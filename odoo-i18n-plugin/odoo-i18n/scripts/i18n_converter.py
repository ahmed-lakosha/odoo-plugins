#!/usr/bin/env python3
"""
Odoo i18n .po File Converter / Utility
========================================
Provides merge, clean, stats, and convert operations on .po translation files.

Actions:
  merge   - Merge new strings from one .po into a base .po, preserving existing translations
  clean   - Remove obsolete entries from a .po file (strings no longer in source)
  stats   - Print statistics about a .po file (translated/untranslated/fuzzy counts)
  convert - Normalize encoding and line endings of a .po file

Usage:
    python i18n_converter.py --action merge --base ar.po --new ar_new.po --output ar_merged.po
    python i18n_converter.py --action clean --po ar.po
    python i18n_converter.py --action stats --po ar.po
    python i18n_converter.py --action convert --po ar.po --output ar_clean.po
"""

import argparse
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PoEntry:
    """A single .po file entry."""
    msgid: str
    msgstr: str
    comments: List[str] = field(default_factory=list)
    extracted_comments: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    is_fuzzy: bool = False
    is_obsolete: bool = False
    is_header: bool = False
    line_start: int = 0

    @property
    def is_translated(self) -> bool:
        return bool(self.msgstr) and not self.is_fuzzy

    def clone_empty(self) -> "PoEntry":
        """Return a copy of this entry with empty msgstr."""
        return PoEntry(
            msgid=self.msgid,
            msgstr="",
            comments=list(self.comments),
            extracted_comments=list(self.extracted_comments),
            locations=list(self.locations),
            flags=[f for f in self.flags if f != "fuzzy"],
            is_fuzzy=False,
            is_obsolete=self.is_obsolete,
            is_header=self.is_header,
        )


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class PoParser:
    """Full-fidelity .po file parser preserving comments and structure."""

    def __init__(self, content: str):
        self.content = content
        self.lines = content.splitlines()
        self._entries: List[PoEntry] = []
        self._errors: List[str] = []

    def parse(self) -> List[PoEntry]:
        entries = []
        current: Optional[PoEntry] = None
        mode: Optional[str] = None

        def flush():
            nonlocal current, mode
            if current is not None:
                if current.is_header or current.msgid:
                    entries.append(current)
                current = None
                mode = None

        for i, raw_line in enumerate(self.lines):
            lineno = i + 1
            line = raw_line.strip()

            if not line:
                flush()
                continue

            # Comments
            if line.startswith("#"):
                if current is None:
                    current = PoEntry(msgid="", msgstr="", line_start=lineno)

                if line.startswith("#,"):
                    flags = [f.strip() for f in line[2:].split(",")]
                    current.flags = flags
                    if "fuzzy" in flags:
                        current.is_fuzzy = True
                elif line.startswith("#:"):
                    current.locations.extend(line[2:].strip().split())
                elif line.startswith("#."):
                    current.extracted_comments.append(line[2:].strip())
                elif line.startswith("#~"):
                    current.is_obsolete = True
                    current.comments.append(line)
                else:
                    current.comments.append(line)
                continue

            if line.startswith("msgid "):
                if current is not None and mode is not None:
                    flush()
                if current is None:
                    current = PoEntry(msgid="", msgstr="", line_start=lineno)
                val = self._parse_string(line[6:])
                current.msgid = val
                if val == "":
                    current.is_header = True
                mode = "msgid"
                continue

            if line.startswith("msgstr "):
                current.msgstr = self._parse_string(line[7:])
                mode = "msgstr"
                continue

            if line.startswith('"') and mode:
                chunk = self._parse_string(line)
                if mode == "msgid":
                    current.msgid += chunk
                    if current.msgid == "":
                        current.is_header = True
                else:
                    current.msgstr += chunk
                continue

        flush()
        self._entries = entries
        return entries

    @staticmethod
    def _parse_string(raw: str) -> str:
        raw = raw.strip()
        if raw.startswith('"') and raw.endswith('"'):
            inner = raw[1:-1]
            inner = inner.replace('\\"', '"')
            inner = inner.replace("\\n", "\n")
            inner = inner.replace("\\t", "\t")
            inner = inner.replace("\\r", "\r")
            inner = inner.replace("\\\\", "\\")
            return inner
        return ""


# ---------------------------------------------------------------------------
# Serializer
# ---------------------------------------------------------------------------

class PoSerializer:
    """Convert PoEntry list back to .po file text."""

    @staticmethod
    def escape(s: str) -> str:
        s = s.replace("\\", "\\\\")
        s = s.replace('"', '\\"')
        s = s.replace("\n", "\\n")
        s = s.replace("\r", "\\r")
        s = s.replace("\t", "\\t")
        return s

    def serialize_entry(self, entry: PoEntry, obsolete: bool = False) -> str:
        parts = []

        # Translator comments
        for c in entry.comments:
            if not c.startswith("#~"):
                parts.append(c)

        # Extracted comments (from source)
        for ec in entry.extracted_comments:
            parts.append(f"#. {ec}")

        # Locations
        if entry.locations:
            # Group locations, max ~76 chars per line
            loc_line = "#:"
            for loc in entry.locations:
                if len(loc_line) + len(loc) + 1 > 76:
                    parts.append(loc_line)
                    loc_line = "#: " + loc
                else:
                    loc_line += " " + loc
            parts.append(loc_line)

        # Flags
        if entry.flags:
            flag_str = ", ".join(entry.flags)
            parts.append(f"#, {flag_str}")

        # msgid
        escaped_id = self.escape(entry.msgid)
        if "\n" in entry.msgid:
            # Multiline
            chunks = escaped_id.split("\\n")
            parts.append('msgid ""')
            for i, chunk in enumerate(chunks):
                suffix = "\\n" if i < len(chunks) - 1 else ""
                parts.append(f'"{chunk}{suffix}"')
        else:
            parts.append(f'msgid "{escaped_id}"')

        # msgstr
        escaped_str = self.escape(entry.msgstr) if entry.msgstr else ""
        if entry.msgstr and "\n" in entry.msgstr:
            chunks = escaped_str.split("\\n")
            parts.append('msgstr ""')
            for i, chunk in enumerate(chunks):
                suffix = "\\n" if i < len(chunks) - 1 else ""
                parts.append(f'"{chunk}{suffix}"')
        else:
            parts.append(f'msgstr "{escaped_str}"')

        return "\n".join(parts)

    def serialize(self, entries: List[PoEntry]) -> str:
        blocks = []
        for entry in entries:
            block = self.serialize_entry(entry)
            blocks.append(block)
        return "\n\n".join(blocks) + "\n"


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

def action_merge(base_path: Path, new_path: Path, output_path: Path) -> int:
    """
    Merge new strings from new_path into base_path.
    - Existing translations in base are preserved
    - New strings from new_po that don't exist in base are added (empty)
    - Strings in base that don't appear in new_po are marked obsolete
    - Returns count of new strings added
    """
    print(f"Merging:")
    print(f"  Base:   {base_path}")
    print(f"  New:    {new_path}")
    print(f"  Output: {output_path}")

    base_content = base_path.read_text(encoding="utf-8", errors="replace")
    new_content = new_path.read_text(encoding="utf-8", errors="replace")

    base_parser = PoParser(base_content)
    base_entries = base_parser.parse()

    new_parser = PoParser(new_content)
    new_entries = new_parser.parse()

    # Build lookup maps (by msgid)
    base_map: Dict[str, PoEntry] = {e.msgid: e for e in base_entries if not e.is_header}
    new_map: Dict[str, PoEntry] = {e.msgid: e for e in new_entries if not e.is_header}

    # Header from base (preserved)
    header = next((e for e in base_entries if e.is_header), None)

    # Update header PO-Revision-Date
    if header:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M+0000")
        header.msgstr = re.sub(
            r'PO-Revision-Date:[^\n]*\\n',
            f'PO-Revision-Date: {now}\\n',
            header.msgstr,
        )

    merged: List[PoEntry] = []
    if header:
        merged.append(header)

    added = 0
    preserved = 0
    marked_obsolete = 0

    # Process all strings that appear in new .po (these are the current source strings)
    for msgid, new_entry in new_map.items():
        if msgid in base_map:
            base_entry = base_map[msgid]
            # Update locations from new (source locations may have changed)
            base_entry.locations = new_entry.locations or base_entry.locations
            # Keep existing translation
            merged.append(base_entry)
            preserved += 1
        else:
            # New string not in base — add as empty
            new_entry_copy = new_entry.clone_empty()
            merged.append(new_entry_copy)
            added += 1

    # Mark strings in base that are no longer in new as obsolete
    for msgid, base_entry in base_map.items():
        if msgid not in new_map:
            base_entry.is_obsolete = True
            base_entry.comments.insert(0, "#~ obsolete")
            merged.append(base_entry)
            marked_obsolete += 1

    # Serialize
    serializer = PoSerializer()
    output_content = serializer.serialize(merged)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_content, encoding="utf-8", newline="\n")

    print(f"\nMerge complete:")
    print(f"  Preserved translations: {preserved}")
    print(f"  New strings added:      {added}")
    print(f"  Marked obsolete:        {marked_obsolete}")
    print(f"  Output written to:      {output_path}")
    return added


def action_clean(po_path: Path, output_path: Optional[Path] = None) -> int:
    """
    Remove obsolete entries (marked with #~ or the is_obsolete flag) from a .po file.
    Returns count of removed entries.
    """
    in_place = output_path is None or output_path == po_path
    if in_place:
        output_path = po_path

    print(f"Cleaning: {po_path}")

    content = po_path.read_text(encoding="utf-8", errors="replace")
    parser = PoParser(content)
    entries = parser.parse()

    original_count = len([e for e in entries if not e.is_header])
    clean_entries = [e for e in entries if not e.is_obsolete]
    removed = original_count - len([e for e in clean_entries if not e.is_header])

    if in_place and removed > 0:
        # Backup original
        backup_path = po_path.with_suffix(".po.bak")
        shutil.copy2(po_path, backup_path)
        print(f"  Backup created: {backup_path}")

    serializer = PoSerializer()
    output_content = serializer.serialize(clean_entries)
    output_path.write_text(output_content, encoding="utf-8", newline="\n")

    print(f"  Removed {removed} obsolete entries")
    print(f"  Remaining entries: {len(clean_entries) - 1}")  # -1 for header
    print(f"  Output: {output_path}")
    return removed


def action_stats(po_path: Path) -> None:
    """Print detailed statistics about a .po file."""
    print(f"Statistics for: {po_path}")
    print("")

    content = po_path.read_text(encoding="utf-8", errors="replace")
    parser = PoParser(content)
    entries = parser.parse()

    non_header = [e for e in entries if not e.is_header]
    total = len(non_header)
    translated = sum(1 for e in non_header if e.msgstr and not e.is_fuzzy and not e.is_obsolete)
    fuzzy = sum(1 for e in non_header if e.is_fuzzy)
    untranslated = sum(1 for e in non_header if not e.msgstr and not e.is_obsolete)
    obsolete = sum(1 for e in non_header if e.is_obsolete)
    active = total - obsolete

    pct = (translated / active * 100) if active > 0 else 0.0

    # Find header info
    header = next((e for e in entries if e.is_header), None)
    lang = "unknown"
    if header:
        lang_match = re.search(r'Language:\s*([^\n\\]+)', header.msgstr)
        if lang_match:
            lang = lang_match.group(1).strip()

    # File size
    size_bytes = po_path.stat().st_size
    size_kb = size_bytes / 1024

    print(f"  File size:         {size_kb:.1f} KB ({size_bytes} bytes)")
    print(f"  Language:          {lang}")
    print(f"  Total entries:     {total}")
    print(f"  Active entries:    {active}")
    print(f"  Translated:        {translated}")
    print(f"  Untranslated:      {untranslated}")
    print(f"  Fuzzy:             {fuzzy}")
    print(f"  Obsolete:          {obsolete}")
    print(f"  Completion:        {pct:.1f}%")
    print("")

    # Progress bar
    bar_width = 40
    filled = int(bar_width * pct / 100)
    bar = "[" + "#" * filled + "." * (bar_width - filled) + "]"
    print(f"  {bar} {pct:.1f}%")
    print("")

    # String length distribution
    if translated > 0:
        lengths = [len(e.msgid) for e in non_header if e.msgstr and not e.is_obsolete]
        avg_len = sum(lengths) / len(lengths)
        max_len = max(lengths)
        print(f"  Avg msgid length:  {avg_len:.0f} chars")
        print(f"  Max msgid length:  {max_len} chars")
        print("")

    # Most common locations
    locations: Dict[str, int] = {}
    for entry in non_header:
        for loc in entry.locations:
            # Extract just the file part (before :line)
            file_part = loc.split(":")[0] if ":" in loc else loc
            locations[file_part] = locations.get(file_part, 0) + 1

    if locations:
        print("  Top source files by string count:")
        for file_part, count in sorted(locations.items(), key=lambda x: -x[1])[:10]:
            print(f"    {count:4d}  {file_part}")
        print("")


def action_convert(po_path: Path, output_path: Path) -> None:
    """
    Normalize a .po file:
    - Ensure UTF-8 encoding (with BOM removal)
    - Normalize line endings to LF
    - Remove trailing whitespace from each line
    - Ensure consistent empty line between entries
    """
    print(f"Converting: {po_path} -> {output_path}")

    # Read raw bytes to handle encoding issues
    raw = po_path.read_bytes()

    # Strip BOM if present
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
        print("  Removed UTF-8 BOM")

    # Try decoding
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1256", "iso-8859-6"):
        try:
            content = raw.decode(encoding)
            if encoding != "utf-8":
                print(f"  Re-encoded from {encoding} to UTF-8")
            break
        except UnicodeDecodeError:
            continue
    else:
        print("  ERROR: Could not decode file with any known encoding", file=sys.stderr)
        sys.exit(1)

    # Normalize line endings and trailing whitespace
    lines = content.splitlines()
    lines = [line.rstrip() for line in lines]

    # Remove consecutive blank lines (max 1 blank line between entries)
    normalized = []
    prev_blank = False
    for line in lines:
        if not line.strip():
            if not prev_blank:
                normalized.append("")
            prev_blank = True
        else:
            normalized.append(line)
            prev_blank = False

    # Ensure file ends with single newline
    while normalized and not normalized[-1]:
        normalized.pop()
    normalized.append("")

    output_content = "\n".join(normalized)

    if output_path != po_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_content, encoding="utf-8", newline="\n")

    original_lines = len(content.splitlines())
    new_lines = len(normalized)
    print(f"  Original lines: {original_lines}")
    print(f"  Normalized lines: {new_lines}")
    print(f"  Output: {output_path}")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert, merge, clean, and analyze Odoo .po translation files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Actions:
  merge   Merge new strings into existing .po, preserving translations
  clean   Remove obsolete entries from .po file
  stats   Show statistics about .po file
  convert Normalize encoding and line endings

Examples:
  python i18n_converter.py --action merge --base ar.po --new ar_new.po --output ar_merged.po
  python i18n_converter.py --action clean --po ar.po
  python i18n_converter.py --action clean --po ar.po --output ar_clean.po
  python i18n_converter.py --action stats --po ar.po
  python i18n_converter.py --action convert --po ar.po --output ar_normalized.po
        """,
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=["merge", "clean", "stats", "convert"],
        help="Action to perform",
    )
    parser.add_argument(
        "--po",
        metavar="FILE",
        help="Path to .po file (for clean, stats, convert actions)",
    )
    parser.add_argument(
        "--base",
        metavar="FILE",
        help="Base .po file (for merge action — the file with existing translations)",
    )
    parser.add_argument(
        "--new",
        metavar="FILE",
        help="New .po file (for merge action — the file with new/updated source strings)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Output file path (default: in-place for clean/convert, required for merge)",
    )
    return parser.parse_args()


def resolve_path(path_str: Optional[str], name: str) -> Path:
    if not path_str:
        print(f"ERROR: --{name} is required for this action", file=sys.stderr)
        sys.exit(1)
    p = Path(path_str).resolve()
    if not p.exists():
        print(f"ERROR: File not found: {path_str}", file=sys.stderr)
        sys.exit(1)
    return p


def main():
    args = parse_args()

    if args.action == "merge":
        base_path = resolve_path(args.base, "base")
        new_path = resolve_path(args.new, "new")
        if not args.output:
            print("ERROR: --output is required for merge action", file=sys.stderr)
            sys.exit(1)
        output_path = Path(args.output).resolve()
        action_merge(base_path, new_path, output_path)

    elif args.action == "clean":
        po_path = resolve_path(args.po, "po")
        output_path = Path(args.output).resolve() if args.output else po_path
        action_clean(po_path, output_path)

    elif args.action == "stats":
        po_path = resolve_path(args.po, "po")
        action_stats(po_path)

    elif args.action == "convert":
        po_path = resolve_path(args.po, "po")
        if args.output:
            output_path = Path(args.output).resolve()
        else:
            # Default: replace in-place (backup created automatically)
            backup = po_path.with_suffix(".po.bak")
            shutil.copy2(po_path, backup)
            print(f"  Backup created: {backup}")
            output_path = po_path
        action_convert(po_path, output_path)


if __name__ == "__main__":
    main()

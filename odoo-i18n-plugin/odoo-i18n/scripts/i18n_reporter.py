#!/usr/bin/env python3
"""
Odoo i18n Translation Reporter
================================
Compares the translatable strings found in a module's source files against
the .po translation file for a given language and produces a detailed
completeness report.

Usage:
    python i18n_reporter.py --module /path/to/my_module --lang ar
    python i18n_reporter.py --module /path/to/my_module --lang ar --format json
    python i18n_reporter.py --module /path/to/my_module --lang ar --missing-only
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Reuse extractor components
sys.path.insert(0, str(Path(__file__).parent))
from i18n_extractor import ModuleScanner, TranslatableString


# ---------------------------------------------------------------------------
# .po reader (lightweight, for reading existing translations)
# ---------------------------------------------------------------------------

def read_po_translations(po_path: Path) -> Dict[str, str]:
    """
    Read a .po file and return a dict of {msgid: msgstr}.
    Empty msgstr values are not included (or included as empty string).
    """
    translations: Dict[str, str] = {}

    if not po_path.exists():
        return translations

    content = po_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    current_msgid = None
    current_msgstr = None
    mode = None
    is_fuzzy = False
    is_header = False

    def flush():
        nonlocal current_msgid, current_msgstr, mode, is_fuzzy, is_header
        if current_msgid is not None:
            if not is_fuzzy and not is_header:
                translations[current_msgid] = current_msgstr or ""
        current_msgid = None
        current_msgstr = None
        mode = None
        is_fuzzy = False
        is_header = False

    def unescape(s: str) -> str:
        s = s.replace('\\"', '"').replace("\\n", "\n").replace("\\t", "\t").replace("\\\\", "\\")
        return s

    def parse_str(raw: str) -> str:
        raw = raw.strip()
        if raw.startswith('"') and raw.endswith('"'):
            return unescape(raw[1:-1])
        return ""

    for line in lines:
        stripped = line.strip()

        if not stripped:
            flush()
            continue

        if stripped.startswith("#,") and "fuzzy" in stripped:
            is_fuzzy = True
            continue

        if stripped.startswith("#"):
            continue

        if stripped.startswith("msgid "):
            if current_msgid is not None:
                flush()
            val = parse_str(stripped[6:])
            current_msgid = val
            if val == "":
                is_header = True
            mode = "msgid"
            continue

        if stripped.startswith("msgstr "):
            current_msgstr = parse_str(stripped[7:])
            mode = "msgstr"
            continue

        if stripped.startswith('"') and mode in ("msgid", "msgstr"):
            chunk = parse_str(stripped)
            if mode == "msgid":
                current_msgid = (current_msgid or "") + chunk
                if current_msgid == "":
                    is_header = True
            elif mode == "msgstr":
                current_msgstr = (current_msgstr or "") + chunk

    flush()
    return translations


# ---------------------------------------------------------------------------
# Report data structures
# ---------------------------------------------------------------------------

@dataclass
class MissingEntry:
    msgid: str
    location: str
    line: int
    source_file_type: str  # 'python', 'xml', 'javascript'

    def to_dict(self):
        return asdict(self)


@dataclass
class TranslationReport:
    module_name: str
    module_path: str
    language: str
    po_file: str
    po_exists: bool

    total_strings: int
    translated_count: int
    missing_count: int
    fuzzy_count: int
    empty_in_po: int
    completion_pct: float

    missing_entries: List[MissingEntry] = field(default_factory=list)

    def to_dict(self):
        d = {
            "module_name": self.module_name,
            "module_path": self.module_path,
            "language": self.language,
            "po_file": self.po_file,
            "po_exists": self.po_exists,
            "statistics": {
                "total_strings": self.total_strings,
                "translated_count": self.translated_count,
                "missing_count": self.missing_count,
                "fuzzy_count": self.fuzzy_count,
                "empty_in_po": self.empty_in_po,
                "completion_pct": round(self.completion_pct, 2),
            },
            "missing_entries": [e.to_dict() for e in self.missing_entries],
        }
        return d


# ---------------------------------------------------------------------------
# Reporter
# ---------------------------------------------------------------------------

class TranslationReporter:
    """Compare module source strings against .po file and build a report."""

    EXTENSION_TYPE = {
        ".py": "python",
        ".xml": "xml",
        ".js": "javascript",
    }

    def __init__(self, module_path: str, lang: str):
        self.module_path = Path(module_path).resolve()
        self.lang = lang
        self.module_name = self.module_path.name

    def run(self) -> TranslationReport:
        """Scan module, read .po file, and build the TranslationReport."""
        # Step 1: Extract source strings
        print(f"Analyzing module: {self.module_name} (language: {self.lang})")
        scanner = ModuleScanner(str(self.module_path))
        source_strings = scanner.scan()

        # Step 2: Read .po file
        po_path = self.module_path / "i18n" / f"{self.lang}.po"
        po_exists = po_path.exists()

        if not po_exists:
            print(f"  WARNING: .po file not found: {po_path}")
            translations = {}
        else:
            translations = read_po_translations(po_path)
            print(f"  Found {len(translations)} entries in {po_path.name}")

        # Step 3: Compare
        missing_entries: List[MissingEntry] = []
        translated_count = 0
        empty_in_po = 0

        for s in source_strings:
            # Determine file type from location
            ext = Path(s.location).suffix.lower()
            file_type = self.EXTENSION_TYPE.get(ext, "other")

            if s.source in translations:
                val = translations[s.source]
                if val:  # Non-empty translation
                    translated_count += 1
                else:
                    empty_in_po += 1
                    missing_entries.append(
                        MissingEntry(
                            msgid=s.source,
                            location=s.location,
                            line=s.line,
                            source_file_type=file_type,
                        )
                    )
            else:
                # Not in .po at all
                missing_entries.append(
                    MissingEntry(
                        msgid=s.source,
                        location=s.location,
                        line=s.line,
                        source_file_type=file_type,
                    )
                )

        total = len(source_strings)
        missing_count = len(missing_entries)
        completion_pct = (translated_count / total * 100) if total > 0 else 0.0

        # Count fuzzy entries in .po
        fuzzy_count = self._count_fuzzy(po_path) if po_exists else 0

        # Sort missing by location for easy editing
        missing_entries.sort(key=lambda e: (e.location, e.line))

        report = TranslationReport(
            module_name=self.module_name,
            module_path=str(self.module_path),
            language=self.lang,
            po_file=str(po_path),
            po_exists=po_exists,
            total_strings=total,
            translated_count=translated_count,
            missing_count=missing_count,
            fuzzy_count=fuzzy_count,
            empty_in_po=empty_in_po,
            completion_pct=completion_pct,
            missing_entries=missing_entries,
        )
        return report

    def _count_fuzzy(self, po_path: Path) -> int:
        """Count fuzzy entries in a .po file."""
        try:
            content = po_path.read_text(encoding="utf-8", errors="replace")
            return content.count("#, fuzzy")
        except OSError:
            return 0


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_text(report: TranslationReport, missing_only: bool = False) -> str:
    """Format report as human-readable text."""
    lines = [
        "=" * 65,
        f"Translation Report: {report.module_name} ({report.language})",
        "=" * 65,
        f"Module:        {report.module_path}",
        f"Language:      {report.language}",
        f"PO File:       {report.po_file}",
        f"PO Exists:     {'Yes' if report.po_exists else 'No — run i18n_extractor.py first'}",
        "",
        "--- Translation Statistics ---",
        f"Total strings:    {report.total_strings}",
        f"Translated:       {report.translated_count} ({report.completion_pct:.1f}%)",
        f"Missing:          {report.missing_count}",
        f"Empty in .po:     {report.empty_in_po}",
        f"Fuzzy:            {report.fuzzy_count}",
        "",
    ]

    # Progress bar
    bar_width = 40
    filled = int(bar_width * report.completion_pct / 100)
    bar = "[" + "=" * filled + "-" * (bar_width - filled) + "]"
    lines.append(f"Progress:      {bar} {report.completion_pct:.1f}%")
    lines.append("")

    if not missing_only:
        # Group missing by file type
        by_type: Dict[str, List[MissingEntry]] = {}
        for entry in report.missing_entries:
            by_type.setdefault(entry.source_file_type, []).append(entry)

        if by_type:
            lines.append("--- Missing by Source Type ---")
            for ftype in ("python", "xml", "javascript", "other"):
                entries = by_type.get(ftype, [])
                if entries:
                    lines.append(f"  {ftype.capitalize()}: {len(entries)}")
            lines.append("")

    if report.missing_entries:
        lines.append("--- Missing Translations ---")
        lines.append(f"(Showing {len(report.missing_entries)} missing entries, sorted by location)")
        lines.append("")

        current_location = None
        for entry in report.missing_entries:
            if entry.location != current_location:
                current_location = entry.location
                lines.append(f"  File: {entry.location}")

            # Truncate long msgids
            msgid_display = entry.msgid.replace("\n", "\\n")
            if len(msgid_display) > 70:
                msgid_display = msgid_display[:67] + "..."

            lines.append(f"    [{entry.line:4d}] {msgid_display!r}")
        lines.append("")
    else:
        lines.append("No missing translations found.")
        lines.append("")

    # Recommendations
    lines.append("--- Recommendations ---")
    if not report.po_exists:
        lines.append("  1. Generate .po file: python i18n_extractor.py --module . --lang " + report.language)
    elif report.missing_count > 0:
        lines.append(f"  1. Translate {report.missing_count} missing strings in: {report.po_file}")
        lines.append("  2. Run i18n_validator.py to check the translated file")
        lines.append("  3. Update module in Odoo to load new translations")
    if report.fuzzy_count > 0:
        lines.append(f"  Review {report.fuzzy_count} fuzzy entries — they need human verification")

    if report.completion_pct == 100.0 and report.fuzzy_count == 0:
        lines.append("  Translations are complete!")

    lines.append("")
    lines.append("=" * 65)

    return "\n".join(lines)


def format_json(report: TranslationReport) -> str:
    """Format report as JSON."""
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)


def format_csv(report: TranslationReport) -> str:
    """Format missing entries as CSV for spreadsheet editing."""
    rows = [
        "location,line,source_type,msgid"
    ]
    for entry in report.missing_entries:
        msgid = entry.msgid.replace('"', '""').replace("\n", "\\n")
        rows.append(f'"{entry.location}",{entry.line},"{entry.source_file_type}","{msgid}"')
    return "\n".join(rows)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a translation completeness report for an Odoo module.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python i18n_reporter.py --module /path/to/my_module --lang ar
  python i18n_reporter.py --module /path/to/my_module --lang ar --format json
  python i18n_reporter.py --module /path/to/my_module --lang fr --missing-only
  python i18n_reporter.py --module /path/to/my_module --lang tr --output report.txt
        """,
    )
    parser.add_argument(
        "--module",
        required=True,
        metavar="PATH",
        help="Path to the Odoo module directory",
    )
    parser.add_argument(
        "--lang",
        required=True,
        metavar="LANG_CODE",
        help="Language code to report on (e.g., ar, fr, tr)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format: text (default), json, or csv (missing entries only)",
    )
    parser.add_argument(
        "--missing-only",
        action="store_true",
        help="Only show missing translations (no group-by-type breakdown)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write report to a file instead of stdout",
    )
    parser.add_argument(
        "--min-pct",
        type=float,
        default=None,
        metavar="PERCENT",
        help="Exit with code 1 if completion is below this threshold (e.g., 80.0)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    module_path = Path(args.module).resolve()
    if not module_path.is_dir():
        print(f"ERROR: Module path does not exist: {args.module}", file=sys.stderr)
        sys.exit(1)

    try:
        reporter = TranslationReporter(str(module_path), args.lang)
        report = reporter.run()
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    # Format output
    if args.format == "json":
        output = format_json(report)
    elif args.format == "csv":
        output = format_csv(report)
    else:
        output = format_text(report, missing_only=args.missing_only)

    # Write or print
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report written to: {args.output}")
    else:
        print(output)

    # Exit code based on threshold
    if args.min_pct is not None and report.completion_pct < args.min_pct:
        print(
            f"\nFAILED: Completion {report.completion_pct:.1f}% is below threshold {args.min_pct:.1f}%",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()

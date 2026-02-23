#!/usr/bin/env python3
"""
Odoo i18n .po File Validator
=============================
Validates a .po file for syntax errors, encoding issues, empty translations,
fuzzy entries, and Arabic-specific RTL/encoding problems.

Usage:
    python i18n_validator.py --po-file /path/to/ar.po
    python i18n_validator.py --po-file /path/to/ar.po --strict
    python i18n_validator.py --po-file /path/to/ar.po --lang ar
"""

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ValidationIssue:
    """A single validation finding."""
    severity: str  # "error", "warning", "info"
    line: int
    message: str
    context: str = ""

    def __str__(self):
        prefix = {"error": "ERROR", "warning": "WARN ", "info": "INFO "}.get(self.severity, "INFO ")
        loc = f"line {self.line:4d}" if self.line > 0 else "header   "
        ctx = f" | {self.context}" if self.context else ""
        return f"  [{prefix}] {loc}: {self.message}{ctx}"


@dataclass
class PoEntry:
    """Represents a single msgid/msgstr pair in a .po file."""
    msgid: str = ""
    msgstr: str = ""
    comments: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    line_start: int = 0
    is_header: bool = False
    is_fuzzy: bool = False
    is_obsolete: bool = False


# ---------------------------------------------------------------------------
# .po Parser
# ---------------------------------------------------------------------------

class PoParser:
    """Simple, line-by-line .po file parser that tracks line numbers."""

    def __init__(self, content: str):
        self.lines = content.splitlines()
        self.entries: List[PoEntry] = []
        self.parse_errors: List[Tuple[int, str]] = []

    def parse(self) -> List[PoEntry]:
        """Parse the .po file into a list of PoEntry objects."""
        entries = []
        current: Optional[PoEntry] = None
        mode = None  # 'msgid' | 'msgstr' | None
        i = 0

        while i < len(self.lines):
            lineno = i + 1
            raw_line = self.lines[i]
            line = raw_line.strip()

            # Empty line — finalize current entry
            if not line:
                if current is not None and (current.msgid or current.is_header):
                    if not current.msgid:
                        current.is_header = True
                    entries.append(current)
                    current = None
                    mode = None
                i += 1
                continue

            # Comment / flag lines
            if line.startswith("#"):
                if current is None:
                    current = PoEntry(line_start=lineno)

                if line.startswith("#,"):
                    flags_str = line[2:].strip()
                    current.flags = [f.strip() for f in flags_str.split(",")]
                    if "fuzzy" in current.flags:
                        current.is_fuzzy = True
                elif line.startswith("#:"):
                    locs = line[2:].strip()
                    current.locations.extend(locs.split())
                elif line.startswith("#~"):
                    current.is_obsolete = True
                    current.comments.append(line)
                else:
                    current.comments.append(line)
                i += 1
                continue

            # msgid
            if line.startswith("msgid "):
                if current is None:
                    current = PoEntry(line_start=lineno)
                mode = "msgid"
                try:
                    current.msgid = self._parse_string(line[6:], lineno)
                    if current.msgid == "":
                        current.is_header = True
                except ValueError as exc:
                    self.parse_errors.append((lineno, str(exc)))
                i += 1
                continue

            # msgstr
            if line.startswith("msgstr "):
                mode = "msgstr"
                try:
                    current.msgstr = self._parse_string(line[7:], lineno)
                except ValueError as exc:
                    self.parse_errors.append((lineno, str(exc)))
                i += 1
                continue

            # Continuation string (starts with ")
            if line.startswith('"') and mode in ("msgid", "msgstr"):
                try:
                    chunk = self._parse_string(line, lineno)
                    if mode == "msgid":
                        current.msgid += chunk
                    else:
                        current.msgstr += chunk
                except ValueError as exc:
                    self.parse_errors.append((lineno, str(exc)))
                i += 1
                continue

            # Unknown line
            self.parse_errors.append((lineno, f"Unexpected content: {raw_line!r}"))
            i += 1

        # Finalize last entry
        if current is not None and (current.msgid or current.is_header):
            if not current.msgid:
                current.is_header = True
            entries.append(current)

        self.entries = entries
        return entries

    @staticmethod
    def _parse_string(raw: str, lineno: int) -> str:
        """Parse a quoted string from a .po line."""
        raw = raw.strip()
        if not raw.startswith('"') or not raw.endswith('"'):
            raise ValueError(f"Malformed string at line {lineno}: {raw!r}")
        inner = raw[1:-1]
        # Unescape
        inner = inner.replace('\\"', '"')
        inner = inner.replace("\\n", "\n")
        inner = inner.replace("\\t", "\t")
        inner = inner.replace("\\r", "\r")
        inner = inner.replace("\\\\", "\\")
        return inner


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

class PoValidator:
    """Run a suite of validation checks on parsed .po entries."""

    # RTL control characters that should not appear randomly in translations
    RTL_MARKS = {
        "\u200f",  # RIGHT-TO-LEFT MARK
        "\u200e",  # LEFT-TO-RIGHT MARK
        "\u202b",  # RIGHT-TO-LEFT EMBEDDING
        "\u202a",  # LEFT-TO-RIGHT EMBEDDING
        "\u202c",  # POP DIRECTIONAL FORMATTING
        "\u202d",  # LEFT-TO-RIGHT OVERRIDE
        "\u202e",  # RIGHT-TO-LEFT OVERRIDE
        "\u2067",  # RIGHT-TO-LEFT ISOLATE
        "\u2066",  # LEFT-TO-RIGHT ISOLATE
        "\u2069",  # POP DIRECTIONAL ISOLATE
    }

    def __init__(self, entries: List[PoEntry], lang: Optional[str] = None, strict: bool = False):
        self.entries = entries
        self.lang = lang or ""
        self.strict = strict
        self.issues: List[ValidationIssue] = []
        self.is_arabic = self.lang.lower().startswith("ar")

    def validate_all(self) -> List[ValidationIssue]:
        """Run all validation checks and return list of issues."""
        if not self.entries:
            self.issues.append(ValidationIssue("error", 0, "No entries found in .po file"))
            return self.issues

        # Find header entry
        header = next((e for e in self.entries if e.is_header), None)
        self._check_header(header)

        # Validate individual entries
        non_header = [e for e in self.entries if not e.is_header]
        for entry in non_header:
            self._check_entry(entry)

        # Global checks
        self._check_duplicate_msgids(non_header)

        return self.issues

    def _add(self, severity: str, line: int, message: str, context: str = ""):
        self.issues.append(ValidationIssue(severity, line, message, context))

    def _check_header(self, header: Optional[PoEntry]):
        """Validate the .po file header."""
        if header is None:
            self._add("error", 0, "Missing .po file header (empty msgid entry with metadata)")
            return

        msgstr = header.msgstr
        required_fields = [
            ("Content-Type", r"Content-Type:\s*text/plain"),
            ("Content-Transfer-Encoding", r"Content-Transfer-Encoding:"),
            ("MIME-Version", r"MIME-Version:"),
            ("Language", r"Language:"),
        ]

        for field_name, pattern in required_fields:
            if not re.search(pattern, msgstr):
                self._add("warning", header.line_start,
                          f"Header missing field: {field_name}")

        # Check charset
        charset_match = re.search(r'charset=([^\s\\]+)', msgstr, re.IGNORECASE)
        if charset_match:
            charset = charset_match.group(1).strip('"').lower()
            if charset not in ("utf-8", "utf8"):
                self._add("error", header.line_start,
                          f"Charset must be UTF-8, found: {charset}")
        else:
            self._add("error", header.line_start, "Header missing charset declaration")

        # Check Plural-Forms for Arabic
        if self.is_arabic:
            if "Plural-Forms" not in msgstr:
                self._add("warning", header.line_start,
                          "Arabic .po file missing Plural-Forms header")
            else:
                plural_match = re.search(r'nplurals=(\d+)', msgstr)
                if plural_match:
                    nplurals = int(plural_match.group(1))
                    if nplurals != 6:
                        self._add("warning", header.line_start,
                                  f"Arabic should have nplurals=6, found nplurals={nplurals}")

    def _check_entry(self, entry: PoEntry):
        """Validate a single msgid/msgstr pair."""
        lineno = entry.line_start

        # Skip obsolete entries (commented out with #~)
        if entry.is_obsolete:
            return

        # Check for fuzzy flag
        if entry.is_fuzzy:
            self._add("warning", lineno, "Fuzzy translation (needs review)",
                      context=entry.msgid[:60])

        # Check for empty translation
        if not entry.msgstr:
            severity = "warning" if not self.strict else "error"
            self._add(severity, lineno, "Empty translation (untranslated string)",
                      context=entry.msgid[:60])
            return

        # Check format specifier consistency
        if "python-format" in entry.flags:
            self._check_format_specifiers(entry, lineno)

        # Check for RTL issues in Arabic translations
        if self.is_arabic and entry.msgstr:
            self._check_arabic_specific(entry, lineno)

        # Check for mixed-direction text issues
        self._check_bidi_issues(entry, lineno)

        # Whitespace consistency
        self._check_whitespace(entry, lineno)

    def _check_format_specifiers(self, entry: PoEntry, lineno: int):
        """Check that format specifiers in msgstr match msgid."""
        # Find all %s, %d, %f, %(name)s style specifiers
        spec_pattern = re.compile(r'%(?:\([^)]+\))?[sdifro%]')

        src_specs = spec_pattern.findall(entry.msgid)
        dst_specs = spec_pattern.findall(entry.msgstr) if entry.msgstr else []

        # For positional specifiers, count must match
        src_positional = [s for s in src_specs if not s.startswith("%(")]
        dst_positional = [s for s in dst_specs if not s.startswith("%(")]

        if len(src_positional) != len(dst_positional):
            self._add("error", lineno,
                      f"Format specifier mismatch: source has {len(src_positional)}, "
                      f"translation has {len(dst_positional)}",
                      context=entry.msgid[:60])

        # For named specifiers, all names must appear in translation
        src_named = {re.search(r'\(([^)]+)\)', s).group(1) for s in src_specs if "(" in s}
        dst_named = {re.search(r'\(([^)]+)\)', s).group(1) for s in dst_specs if "(" in s}
        missing_named = src_named - dst_named
        if missing_named:
            self._add("error", lineno,
                      f"Missing named format specifiers in translation: {missing_named}",
                      context=entry.msgid[:60])

    def _check_arabic_specific(self, entry: PoEntry, lineno: int):
        """Check Arabic-specific issues in translation."""
        msgstr = entry.msgstr

        # Check that Arabic translation actually contains Arabic characters
        has_arabic = any(
            unicodedata.name(ch, "").startswith("ARABIC")
            for ch in msgstr
            if ch.strip()
        )
        if not has_arabic and len(msgstr.strip()) > 2:
            self._add("warning", lineno,
                      "Translation appears to have no Arabic characters",
                      context=msgstr[:60])

        # Check for common Arabic encoding artifacts
        if "Ø" in msgstr or "Ù" in msgstr:
            self._add("error", lineno,
                      "Arabic text appears to be mis-encoded (Mojibake detected). "
                      "Ensure file is saved as UTF-8.",
                      context=msgstr[:60])

        # Check for unnecessary RTL marks
        suspicious_marks = [ch for ch in msgstr if ch in self.RTL_MARKS]
        if suspicious_marks:
            mark_names = [unicodedata.name(m, repr(m)) for m in set(suspicious_marks)]
            self._add("info", lineno,
                      f"Translation contains direction control characters: {mark_names}. "
                      "These are usually not needed in .po files.",
                      context=msgstr[:40])

    def _check_bidi_issues(self, entry: PoEntry, lineno: int):
        """Check for bidirectional text issues."""
        if not entry.msgstr:
            return

        # Check for override characters (potential security/display issue)
        override_chars = [ch for ch in entry.msgstr if ch in {"\u202e", "\u202d"}]
        if override_chars:
            self._add("error", lineno,
                      "Translation contains BIDI override characters — potential security issue")

    def _check_whitespace(self, entry: PoEntry, lineno: int):
        """Check whitespace consistency between msgid and msgstr."""
        if not entry.msgstr:
            return

        # Leading/trailing whitespace should match
        src_leading = len(entry.msgid) - len(entry.msgid.lstrip())
        dst_leading = len(entry.msgstr) - len(entry.msgstr.lstrip())
        if src_leading != dst_leading and (src_leading > 0 or dst_leading > 0):
            self._add("info", lineno,
                      f"Leading whitespace differs: source has {src_leading} space(s), "
                      f"translation has {dst_leading}",
                      context=entry.msgid[:40])

        src_trailing = len(entry.msgid) - len(entry.msgid.rstrip())
        dst_trailing = len(entry.msgstr) - len(entry.msgstr.rstrip())
        if src_trailing != dst_trailing and (src_trailing > 0 or dst_trailing > 0):
            self._add("info", lineno,
                      f"Trailing whitespace differs: source has {src_trailing}, "
                      f"translation has {dst_trailing}",
                      context=entry.msgid[:40])

    def _check_duplicate_msgids(self, entries: List[PoEntry]):
        """Check for duplicate msgid entries (only first wins in gettext)."""
        seen = {}
        for entry in entries:
            key = entry.msgid
            if key in seen:
                self._add("error", entry.line_start,
                          f"Duplicate msgid — first defined at line {seen[key]}",
                          context=entry.msgid[:60])
            else:
                seen[key] = entry.line_start


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    po_path: str,
    entries: List[PoEntry],
    issues: List[ValidationIssue],
    parse_errors: List[Tuple[int, str]],
    lang: Optional[str] = None,
) -> str:
    """Build a human-readable validation report."""
    non_header = [e for e in entries if not e.is_header and not e.is_obsolete]
    total = len(non_header)
    translated = sum(1 for e in non_header if e.msgstr)
    untranslated = total - translated
    fuzzy = sum(1 for e in non_header if e.is_fuzzy)
    obsolete = sum(1 for e in entries if e.is_obsolete)

    pct = (translated / total * 100) if total > 0 else 0

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    infos = [i for i in issues if i.severity == "info"]

    lines = [
        "=" * 60,
        f"Validation Report: {Path(po_path).name}",
        "=" * 60,
        f"Language:         {lang or 'unknown'}",
        f"File:             {po_path}",
        "",
        "--- Translation Statistics ---",
        f"Total entries:    {total}",
        f"Translated:       {translated} ({pct:.1f}%)",
        f"Untranslated:     {untranslated}",
        f"Fuzzy:            {fuzzy}",
        f"Obsolete:         {obsolete}",
        "",
        "--- Validation Summary ---",
        f"Parse errors:     {len(parse_errors)}",
        f"Errors:           {len(errors)}",
        f"Warnings:         {len(warnings)}",
        f"Info notes:       {len(infos)}",
        "",
    ]

    if parse_errors:
        lines.append("--- Parse Errors ---")
        for lineno, msg in parse_errors:
            lines.append(f"  [PARSE ERROR] line {lineno:4d}: {msg}")
        lines.append("")

    if errors:
        lines.append("--- Errors ---")
        for issue in errors:
            lines.append(str(issue))
        lines.append("")

    if warnings:
        lines.append("--- Warnings ---")
        for issue in warnings:
            lines.append(str(issue))
        lines.append("")

    if infos:
        lines.append("--- Info Notes ---")
        for issue in infos:
            lines.append(str(issue))
        lines.append("")

    # Overall result
    if parse_errors or errors:
        status = "FAILED — Fix errors before loading into Odoo"
    elif warnings:
        status = "PASSED WITH WARNINGS — Review warnings recommended"
    else:
        status = "PASSED — File is valid"

    lines.append("=" * 60)
    lines.append(f"Result: {status}")
    lines.append("=" * 60)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate an Odoo .po translation file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python i18n_validator.py --po-file /path/to/ar.po
  python i18n_validator.py --po-file /path/to/ar.po --lang ar
  python i18n_validator.py --po-file /path/to/ar.po --strict
        """,
    )
    parser.add_argument(
        "--po-file",
        required=True,
        metavar="PATH",
        help="Path to the .po file to validate",
    )
    parser.add_argument(
        "--lang",
        metavar="LANG_CODE",
        default=None,
        help="Language code for language-specific checks (e.g., ar, fr, tr). "
             "Auto-detected from filename if not provided.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat untranslated strings as errors instead of warnings",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write validation report to a file instead of stdout",
    )
    return parser.parse_args()


def detect_lang_from_filename(filepath: str) -> Optional[str]:
    """Try to detect language code from .po filename (e.g., ar.po -> ar)."""
    name = Path(filepath).stem  # Remove .po extension
    if re.match(r'^[a-z]{2}(_[A-Z]{2})?$', name):
        return name
    return None


def main():
    args = parse_args()

    po_path = Path(args.po_file).resolve()
    if not po_path.exists():
        print(f"ERROR: File not found: {args.po_file}", file=sys.stderr)
        sys.exit(1)

    if po_path.suffix.lower() != ".po":
        print(f"WARNING: File does not have .po extension: {args.po_file}", file=sys.stderr)

    # Detect language
    lang = args.lang or detect_lang_from_filename(str(po_path))

    # Read and check encoding
    try:
        raw_bytes = po_path.read_bytes()
        # Detect BOM
        if raw_bytes.startswith(b"\xef\xbb\xbf"):
            print("WARNING: File has UTF-8 BOM. Odoo prefers BOM-less UTF-8.")
            content = raw_bytes[3:].decode("utf-8")
        else:
            content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        print(f"ERROR: File is not valid UTF-8: {exc}", file=sys.stderr)
        print("Odoo requires .po files to be UTF-8 encoded.", file=sys.stderr)
        sys.exit(1)

    # Parse
    parser = PoParser(content)
    entries = parser.parse()

    # Validate
    validator = PoValidator(entries, lang=lang, strict=args.strict)
    issues = validator.validate_all()

    # Generate report
    report = generate_report(str(po_path), entries, issues, parser.parse_errors, lang=lang)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report, encoding="utf-8")
        print(f"Report written to: {args.output}")
    else:
        print(report)

    # Exit code: 1 if errors found
    errors = [i for i in issues if i.severity == "error"]
    if parser.parse_errors or errors:
        sys.exit(1)


if __name__ == "__main__":
    main()

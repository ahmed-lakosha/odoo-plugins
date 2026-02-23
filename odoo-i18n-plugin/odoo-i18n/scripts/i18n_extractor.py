#!/usr/bin/env python3
"""
Odoo i18n String Extractor
==========================
Scans an Odoo module for translatable strings in Python, XML, and JavaScript files,
then generates a .pot (template) file and an empty .po file for the target language.

Usage:
    python i18n_extractor.py --module /path/to/module --lang ar
    python i18n_extractor.py --module /path/to/module --lang fr --output /custom/output/
"""

import ast
import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple, Optional

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    import xml.etree.ElementTree as ET
    HAS_LXML = False


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class TranslatableString:
    """Represents a single extracted translatable string."""

    def __init__(
        self,
        source: str,
        location: str,
        line: int,
        context: str = "",
        flags: Optional[List[str]] = None,
        comment: str = "",
    ):
        self.source = source
        self.location = location
        self.line = line
        self.context = context
        self.flags = flags or []
        self.comment = comment

    def __repr__(self):
        return f"<TranslatableString source={self.source!r} location={self.location}:{self.line}>"

    def __eq__(self, other):
        return self.source == other.source

    def __hash__(self):
        return hash(self.source)


# ---------------------------------------------------------------------------
# Python AST extractor
# ---------------------------------------------------------------------------

class PythonExtractor(ast.NodeVisitor):
    """Extract _('...') and _lt('...') calls from Python source via AST."""

    TRANSLATION_FUNCTIONS = {"_", "_lt"}

    def __init__(self, filepath: str, module_root: str):
        self.filepath = filepath
        self.module_root = module_root
        self.strings: List[TranslatableString] = []
        self._relative_path = os.path.relpath(filepath, module_root)

    def extract(self) -> List[TranslatableString]:
        try:
            with open(self.filepath, "r", encoding="utf-8", errors="replace") as fh:
                source = fh.read()
        except OSError as exc:
            print(f"  [WARN] Cannot read {self.filepath}: {exc}", file=sys.stderr)
            return []

        try:
            tree = ast.parse(source, filename=self.filepath)
        except SyntaxError as exc:
            print(f"  [WARN] SyntaxError in {self.filepath}: {exc}", file=sys.stderr)
            return []

        self.visit(tree)
        return self.strings

    def visit_Call(self, node: ast.Call):
        # Match bare _('...') or _lt('...')
        func_name = None
        if isinstance(node.func, ast.Name) and node.func.id in self.TRANSLATION_FUNCTIONS:
            func_name = node.func.id
        elif (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in self.TRANSLATION_FUNCTIONS
        ):
            func_name = node.func.attr

        if func_name and node.args:
            first_arg = node.args[0]
            if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                string_value = first_arg.value
                if string_value.strip():  # Skip empty/whitespace-only strings
                    flags = []
                    # Check if string contains % formatting
                    if re.search(r'%[sdifr(]', string_value):
                        flags.append("python-format")
                    self.strings.append(
                        TranslatableString(
                            source=string_value,
                            location=self._relative_path,
                            line=node.lineno,
                            flags=flags,
                        )
                    )

        # Continue traversal
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# XML extractor
# ---------------------------------------------------------------------------

class XmlExtractor:
    """Extract translatable strings from Odoo XML view/data files."""

    # Attributes that contain translatable text
    TRANSLATABLE_ATTRS = {
        "string", "help", "placeholder", "confirm", "summary",
        "name",  # For menu items and actions
        "title", "alt",
    }

    # Tags where 'name' attribute is NOT a translatable label
    NAME_NOT_TRANSLATABLE_TAGS = {
        "field", "record", "menuitem", "template", "t",
        "function", "delete", "odoo", "data",
    }

    # Tags whose text content is translatable
    TRANSLATABLE_TEXT_TAGS = {
        "p", "span", "h1", "h2", "h3", "h4", "h5", "h6",
        "li", "td", "th", "label", "button", "a", "div",
        "strong", "em", "small", "b", "i",
    }

    def __init__(self, filepath: str, module_root: str):
        self.filepath = filepath
        self.module_root = module_root
        self._relative_path = os.path.relpath(filepath, module_root)
        self.strings: List[TranslatableString] = []

    def extract(self) -> List[TranslatableString]:
        try:
            with open(self.filepath, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except OSError as exc:
            print(f"  [WARN] Cannot read {self.filepath}: {exc}", file=sys.stderr)
            return []

        if HAS_LXML:
            self._extract_lxml(content)
        else:
            self._extract_stdlib(content)

        return self.strings

    def _extract_lxml(self, content: str):
        try:
            parser = etree.XMLParser(recover=True, remove_comments=True)
            root = etree.fromstring(content.encode("utf-8"), parser)
        except Exception as exc:
            print(f"  [WARN] XML parse error in {self.filepath}: {exc}", file=sys.stderr)
            return

        for element in root.iter():
            lineno = getattr(element, "sourceline", 0) or 0
            tag = element.tag.split("}")[-1] if "}" in str(element.tag) else str(element.tag)

            # Check translatable attributes
            for attr, value in element.attrib.items():
                clean_attr = attr.split("}")[-1] if "}" in attr else attr
                if clean_attr in self.TRANSLATABLE_ATTRS and value.strip():
                    # Skip 'name' for technical tags
                    if clean_attr == "name" and tag in self.NAME_NOT_TRANSLATABLE_TAGS:
                        continue
                    self.strings.append(
                        TranslatableString(
                            source=value.strip(),
                            location=self._relative_path,
                            line=lineno,
                            comment=f"attr:{clean_attr}",
                        )
                    )

            # Check text content for common HTML/QWeb tags
            if tag.lower() in self.TRANSLATABLE_TEXT_TAGS:
                text = (element.text or "").strip()
                if text and len(text) > 1:  # Skip single-char texts
                    self.strings.append(
                        TranslatableString(
                            source=text,
                            location=self._relative_path,
                            line=lineno,
                        )
                    )

    def _extract_stdlib(self, content: str):
        """Fallback XML extraction using stdlib (less accurate line numbers)."""
        # Attribute extraction via regex
        attr_pattern = re.compile(
            r'\b(?:string|help|placeholder|confirm|summary)\s*=\s*"([^"]+)"'
        )
        for lineno, line in enumerate(content.splitlines(), start=1):
            for match in attr_pattern.finditer(line):
                value = match.group(1).strip()
                if value:
                    self.strings.append(
                        TranslatableString(
                            source=value,
                            location=self._relative_path,
                            line=lineno,
                        )
                    )


# ---------------------------------------------------------------------------
# JavaScript extractor
# ---------------------------------------------------------------------------

class JsExtractor:
    """Extract _t('...') and _lt('...') calls from JavaScript files via regex."""

    # Matches _t('...') or _t("...") or _lt('...') or _lt("...")
    PATTERN = re.compile(
        r'\b(?:_t|_lt)\s*\(\s*(?P<q>[\'"])(?P<str>(?:(?!(?P=q))(?:\\.|.))*?)(?P=q)\s*\)',
        re.DOTALL,
    )

    def __init__(self, filepath: str, module_root: str):
        self.filepath = filepath
        self.module_root = module_root
        self._relative_path = os.path.relpath(filepath, module_root)
        self.strings: List[TranslatableString] = []

    def extract(self) -> List[TranslatableString]:
        try:
            with open(self.filepath, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except OSError as exc:
            print(f"  [WARN] Cannot read {self.filepath}: {exc}", file=sys.stderr)
            return []

        lines = content.splitlines()
        # Build char-to-line mapping
        char_offsets = []
        offset = 0
        for lineno, line in enumerate(lines, start=1):
            char_offsets.append((offset, lineno))
            offset += len(line) + 1  # +1 for newline

        for match in self.PATTERN.finditer(content):
            string_value = match.group("str")
            # Unescape common sequences
            string_value = string_value.replace("\\'", "'").replace('\\"', '"').replace("\\n", "\n")
            string_value = string_value.strip()

            if not string_value:
                continue

            # Find line number
            pos = match.start()
            lineno = 1
            for char_off, lno in char_offsets:
                if char_off <= pos:
                    lineno = lno
                else:
                    break

            self.strings.append(
                TranslatableString(
                    source=string_value,
                    location=self._relative_path,
                    line=lineno,
                )
            )

        return self.strings


# ---------------------------------------------------------------------------
# Module scanner
# ---------------------------------------------------------------------------

class ModuleScanner:
    """Scan an Odoo module directory and collect all translatable strings."""

    EXCLUDED_DIRS = {
        "__pycache__", ".git", ".hg", "node_modules",
        "static/lib", "static/tests", "tests",
    }

    def __init__(self, module_path: str):
        self.module_path = Path(module_path).resolve()
        if not self.module_path.is_dir():
            raise ValueError(f"Module path is not a directory: {module_path}")

        manifest = self.module_path / "__manifest__.py"
        if not manifest.exists():
            manifest = self.module_path / "__openerp__.py"
        if not manifest.exists():
            raise ValueError(f"Not an Odoo module (no __manifest__.py): {module_path}")

        self.module_name = self.module_path.name
        self.strings: List[TranslatableString] = []

    def scan(self) -> List[TranslatableString]:
        print(f"Scanning module: {self.module_name}")
        self._scan_python()
        self._scan_xml()
        self._scan_javascript()
        # Deduplicate by source string (keep first occurrence)
        seen = {}
        unique = []
        for s in self.strings:
            if s.source not in seen:
                seen[s.source] = True
                unique.append(s)
        self.strings = unique
        print(f"  Found {len(self.strings)} unique translatable strings")
        return self.strings

    def _is_excluded(self, path: Path) -> bool:
        for part in path.relative_to(self.module_path).parts:
            if part in self.EXCLUDED_DIRS:
                return True
        return False

    def _scan_python(self):
        count = 0
        for py_file in self.module_path.rglob("*.py"):
            if self._is_excluded(py_file):
                continue
            extractor = PythonExtractor(str(py_file), str(self.module_path))
            found = extractor.extract()
            self.strings.extend(found)
            count += len(found)
        print(f"  Python files: {count} strings extracted")

    def _scan_xml(self):
        count = 0
        for xml_file in self.module_path.rglob("*.xml"):
            if self._is_excluded(xml_file):
                continue
            extractor = XmlExtractor(str(xml_file), str(self.module_path))
            found = extractor.extract()
            self.strings.extend(found)
            count += len(found)
        print(f"  XML files: {count} strings extracted")

    def _scan_javascript(self):
        count = 0
        for js_file in self.module_path.rglob("*.js"):
            if self._is_excluded(js_file):
                continue
            extractor = JsExtractor(str(js_file), str(self.module_path))
            found = extractor.extract()
            self.strings.extend(found)
            count += len(found)
        print(f"  JavaScript files: {count} strings extracted")


# ---------------------------------------------------------------------------
# .pot / .po file generator
# ---------------------------------------------------------------------------

class PoFileGenerator:
    """Generate .pot (template) and .po (language-specific) files."""

    # Language-specific plural forms
    PLURAL_FORMS = {
        "ar": "nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5;",
        "ar_SA": "nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5;",
        "fr": "nplurals=2; plural=(n > 1);",
        "fr_FR": "nplurals=2; plural=(n > 1);",
        "tr": "nplurals=2; plural=(n != 1);",
        "en": "nplurals=2; plural=(n != 1);",
        "en_US": "nplurals=2; plural=(n != 1);",
        "en_GB": "nplurals=2; plural=(n != 1);",
        "de": "nplurals=2; plural=(n != 1);",
        "es": "nplurals=2; plural=(n != 1);",
        "ru": "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);",
    }

    DEFAULT_PLURAL_FORMS = "nplurals=2; plural=(n != 1);"

    def __init__(self, module_name: str, strings: List[TranslatableString]):
        self.module_name = module_name
        self.strings = strings
        self.now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M+0000")

    def _escape_po_string(self, s: str) -> str:
        """Escape special characters for .po format."""
        s = s.replace("\\", "\\\\")
        s = s.replace('"', '\\"')
        s = s.replace("\n", "\\n")
        s = s.replace("\r", "\\r")
        s = s.replace("\t", "\\t")
        return s

    def _format_msgid(self, s: str) -> str:
        """Format msgid with possible multiline."""
        escaped = self._escape_po_string(s)
        if "\\n" in escaped:
            # Multiline: use empty first line, then continuation
            lines = escaped.split("\\n")
            result = 'msgid ""\n'
            for i, line in enumerate(lines):
                suffix = "\\n" if i < len(lines) - 1 else ""
                result += f'"{line}{suffix}"\n'
            return result
        return f'msgid "{escaped}"\n'

    def generate_pot(self) -> str:
        """Generate the .pot template file content."""
        lines = [
            f"# Translation template for {self.module_name}",
            f"# Copyright (C) {datetime.now().year} TaqaTechno",
            "# This file is distributed under the MIT license.",
            "#",
            'msgid ""',
            'msgstr ""',
            f'"Project-Id-Version: Odoo Module {self.module_name}\\n"',
            '"Report-Msgid-Bugs-To: contact@taqat-techno.com\\n"',
            f'"POT-Creation-Date: {self.now}\\n"',
            '"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"',
            '"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"',
            '"Language-Team: LANGUAGE <LL@li.org>\\n"',
            '"Language: \\n"',
            '"MIME-Version: 1.0\\n"',
            '"Content-Type: text/plain; charset=UTF-8\\n"',
            '"Content-Transfer-Encoding: 8bit\\n"',
            "",
        ]

        for s in self.strings:
            if s.comment:
                lines.append(f"#. {s.comment}")
            lines.append(f"#: {s.location}:{s.line}")
            if s.flags:
                lines.append(f"#, {', '.join(s.flags)}")
            lines.append(self._format_msgid(s.source).rstrip())
            lines.append('msgstr ""')
            lines.append("")

        return "\n".join(lines)

    def generate_po(self, lang: str) -> str:
        """Generate a language-specific .po file with empty translations."""
        plural_forms = self.PLURAL_FORMS.get(lang, self.DEFAULT_PLURAL_FORMS)
        lang_display = lang.replace("_", " ")

        lines = [
            f"# {lang_display} translation of {self.module_name}",
            f"# Copyright (C) {datetime.now().year} TaqaTechno",
            "# This file is distributed under the MIT license.",
            "# Translator: FULL NAME <EMAIL@ADDRESS>, YEAR",
            "#",
            'msgid ""',
            'msgstr ""',
            f'"Project-Id-Version: Odoo Module {self.module_name}\\n"',
            '"Report-Msgid-Bugs-To: contact@taqat-techno.com\\n"',
            f'"POT-Creation-Date: {self.now}\\n"',
            f'"PO-Revision-Date: {self.now}\\n"',
            '"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"',
            f'"Language-Team: {lang_display}\\n"',
            f'"Language: {lang}\\n"',
            '"MIME-Version: 1.0\\n"',
            '"Content-Type: text/plain; charset=UTF-8\\n"',
            '"Content-Transfer-Encoding: 8bit\\n"',
            f'"Plural-Forms: {plural_forms}\\n"',
            "",
        ]

        for s in self.strings:
            if s.comment:
                lines.append(f"#. {s.comment}")
            lines.append(f"#: {s.location}:{s.line}")
            if s.flags:
                lines.append(f"#, {', '.join(s.flags)}")
            lines.append(self._format_msgid(s.source).rstrip())
            lines.append('msgstr ""')
            lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract translatable strings from an Odoo module and generate .pot/.po files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python i18n_extractor.py --module /path/to/my_module --lang ar
  python i18n_extractor.py --module /path/to/my_module --lang fr --output /custom/output/
  python i18n_extractor.py --module /path/to/my_module --lang tr --no-pot
        """,
    )
    parser.add_argument(
        "--module",
        required=True,
        metavar="PATH",
        help="Path to the Odoo module directory (must contain __manifest__.py)",
    )
    parser.add_argument(
        "--lang",
        required=True,
        metavar="LANG_CODE",
        help="Target language code (e.g., ar, fr, tr, en_US)",
    )
    parser.add_argument(
        "--output",
        metavar="DIR",
        default=None,
        help="Output directory for generated files (default: module/i18n/)",
    )
    parser.add_argument(
        "--no-pot",
        action="store_true",
        help="Skip generating .pot template file",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print each extracted string",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Validate module path
    module_path = Path(args.module).resolve()
    if not module_path.is_dir():
        print(f"ERROR: Module path does not exist or is not a directory: {args.module}", file=sys.stderr)
        sys.exit(1)

    # Scan module
    try:
        scanner = ModuleScanner(str(module_path))
        strings = scanner.scan()
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if not strings:
        print("WARNING: No translatable strings found. Check that the module contains Python, XML, or JS files.")
        sys.exit(0)

    if args.verbose:
        print("\nExtracted strings:")
        for s in strings:
            print(f"  [{s.location}:{s.line}] {s.source!r}")

    # Determine output directory
    if args.output:
        output_dir = Path(args.output).resolve()
    else:
        output_dir = module_path / "i18n"

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")

    # Generate files
    generator = PoFileGenerator(scanner.module_name, strings)

    # Generate .pot template
    if not args.no_pot:
        pot_path = output_dir / f"{scanner.module_name}.pot"
        pot_content = generator.generate_pot()
        with open(pot_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(pot_content)
        print(f"  Generated: {pot_path}")

    # Generate .po file for target language
    po_filename = f"{args.lang}.po"
    po_path = output_dir / po_filename

    if po_path.exists():
        # Don't overwrite existing .po — warn user
        backup_path = output_dir / f"{args.lang}.po.bak"
        import shutil
        shutil.copy2(po_path, backup_path)
        print(f"  Existing {po_filename} backed up to {backup_path.name}")

    po_content = generator.generate_po(args.lang)
    with open(po_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(po_content)
    print(f"  Generated: {po_path}")

    print(f"\nExtraction complete!")
    print(f"  Module: {scanner.module_name}")
    print(f"  Total strings: {len(strings)}")
    print(f"  Language: {args.lang}")
    print(f"\nNext steps:")
    print(f"  1. Open {po_path} and fill in the msgstr entries")
    print(f"  2. Run i18n_validator.py to check the completed translations")
    print(f"  3. Load into Odoo: python odoo-bin -c conf.conf -d db -u {scanner.module_name} --stop-after-init")


if __name__ == "__main__":
    main()

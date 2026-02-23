#!/usr/bin/env python3
"""
Comprehensive Syntax Validator for Odoo Modules
Validates Python, XML, JavaScript, and SCSS files for syntax errors
"""

import ast
import os
import re
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import xml.etree.ElementTree as ET
from collections import defaultdict


class SyntaxValidator:
    """Comprehensive syntax validator for Odoo modules"""

    def __init__(self, project_path: str, verbose: bool = False):
        """
        Initialize the syntax validator.

        Args:
            project_path: Path to the Odoo project/module
            verbose: Enable verbose output
        """
        self.project_path = Path(project_path)
        self.verbose = verbose
        self.errors = defaultdict(list)
        self.warnings = defaultdict(list)
        self.stats = {
            'python_files': 0,
            'xml_files': 0,
            'js_files': 0,
            'scss_files': 0,
            'python_errors': 0,
            'xml_errors': 0,
            'js_errors': 0,
            'scss_errors': 0,
            'total_errors': 0,
            'total_warnings': 0
        }

    def validate_python_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate Python file syntax using AST parsing.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            # Check for basic syntax using AST
            try:
                ast.parse(source, filename=str(file_path))
            except SyntaxError as e:
                errors.append(f"Line {e.lineno}: {e.msg}")
                if e.text:
                    errors.append(f"  Problem: {e.text.strip()}")

            # Check for common Odoo-specific issues
            lines = source.split('\n')
            for i, line in enumerate(lines, 1):
                # Check for incorrect API decorators
                if re.match(r'^\s*@api\.\w+\s*$', line):
                    if i < len(lines) and not re.match(r'^\s*def\s+', lines[i]):
                        errors.append(f"Line {i}: API decorator not followed by function definition")

                # Check for deprecated imports
                if 'from openerp' in line:
                    errors.append(f"Line {i}: Deprecated 'openerp' import, use 'odoo' instead")

                # Check for incorrect field definitions
                if 'fields.' in line and '=' in line:
                    if not re.search(r'fields\.\w+\(', line):
                        self.warnings['python'].append(
                            f"{file_path}:{i}: Possible incorrect field definition"
                        )

            return len(errors) == 0, errors

        except Exception as e:
            errors.append(f"Failed to read file: {str(e)}")
            return False, errors

    def validate_xml_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate XML file syntax and Odoo-specific rules.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # First, check for malformed comments
            comment_errors = self._check_xml_comments(content)
            errors.extend(comment_errors)

            # Try to parse the XML
            try:
                # Clean content for parsing (remove potentially problematic comments)
                clean_content = self._clean_xml_for_parsing(content)
                root = ET.fromstring(clean_content)

                # Validate Odoo-specific XML structure
                odoo_errors = self._validate_odoo_xml_structure(root, content)
                errors.extend(odoo_errors)

            except ET.ParseError as e:
                line_num = getattr(e, 'lineno', 'unknown')
                errors.append(f"Line {line_num}: XML parsing error - {str(e)}")

            # Check for common Odoo 19 compatibility issues
            if '<tree' in content and not '<!-- Compatibility:' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if '<tree' in line and not '<!--' in line:
                        self.warnings['xml'].append(
                            f"{file_path}:{i}: <tree> tag should be <list> in Odoo 19"
                        )

            return len(errors) == 0, errors

        except Exception as e:
            errors.append(f"Failed to read file: {str(e)}")
            return False, errors

    def _check_xml_comments(self, content: str) -> List[str]:
        """Check for malformed XML comments."""
        errors = []

        # Check for nested comment starts
        if re.search(r'<!--[^>]*<!--', content):
            errors.append("Nested XML comment start markers detected")

        # Check for nested comment ends
        if re.search(r'-->[^<]*-->', content):
            errors.append("Nested XML comment end markers detected")

        # Check for double hyphens within comments
        comments = re.findall(r'<!--.*?-->', content, re.DOTALL)
        for comment in comments:
            inner = comment[4:-3]  # Extract content between <!-- and -->
            if '--' in inner:
                errors.append("Double hyphens found within XML comment (not allowed)")
                break

        return errors

    def _clean_xml_for_parsing(self, content: str) -> str:
        """Clean XML content for safe parsing."""
        # Fix double hyphens in comments
        def fix_comment_hyphens(match):
            comment = match.group(0)
            inner = comment[4:-3]
            inner = re.sub(r'--+', '- -', inner)
            return f'<!--{inner}-->'

        content = re.sub(r'<!--.*?-->', fix_comment_hyphens, content, flags=re.DOTALL)

        # Wrap content in odoo tags if not present
        if not content.strip().startswith('<odoo'):
            content = f'<odoo>{content}</odoo>'

        return content

    def _validate_odoo_xml_structure(self, root, content: str) -> List[str]:
        """Validate Odoo-specific XML structure."""
        errors = []

        # Check for required attributes in specific tags
        for record in root.findall('.//record'):
            if 'id' not in record.attrib:
                errors.append("Record element missing 'id' attribute")
            if 'model' not in record.attrib:
                errors.append("Record element missing 'model' attribute")

        # Check for template inheritance
        for template in root.findall('.//template'):
            if 'inherit_id' in template.attrib:
                inherit_id = template.attrib['inherit_id']
                if inherit_id == 'website.snippet_options':
                    errors.append("Template inherits from removed 'website.snippet_options'")

        return errors

    def validate_javascript_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate JavaScript file syntax and Odoo module structure.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for Odoo module declaration
            if not content.strip().startswith('/** @odoo-module'):
                self.warnings['js'].append(
                    f"{file_path}:1: Missing '/** @odoo-module **/' declaration"
                )

            # Basic syntax checks
            syntax_errors = self._check_javascript_syntax(content)
            errors.extend(syntax_errors)

            # Check for removed Odoo 19 features
            if '@web/core/network/rpc_service' in content:
                errors.append("Import from removed RPC service module")

            # Check for unbalanced brackets
            bracket_errors = self._check_balanced_brackets(content)
            errors.extend(bracket_errors)

            return len(errors) == 0, errors

        except Exception as e:
            errors.append(f"Failed to read file: {str(e)}")
            return False, errors

    def _check_javascript_syntax(self, content: str) -> List[str]:
        """Basic JavaScript syntax checking."""
        errors = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Check for missing semicolons (simple heuristic)
            if line.strip() and not line.strip().endswith((';', '{', '}', ',', ':', '*/')) \
               and not line.strip().startswith(('//', '/*', '*')):
                # Check if it's a statement that should end with semicolon
                if re.match(r'^\s*(const|let|var|return|import|export)\s+', line):
                    next_line = lines[i] if i < len(lines) else ''
                    if not next_line.strip().startswith(('.', '[')):
                        self.warnings['js'].append(f"Line {i}: Statement might be missing semicolon")

            # Check for console.log statements (should be removed in production)
            if 'console.log(' in line:
                self.warnings['js'].append(f"Line {i}: console.log should be removed in production")

            # Check for async without await
            if 'async' in line and 'function' in line:
                # Check next 10 lines for await
                has_await = False
                for j in range(i, min(i + 10, len(lines))):
                    if 'await' in lines[j]:
                        has_await = True
                        break
                if not has_await:
                    self.warnings['js'].append(f"Line {i}: async function might not contain await")

        return errors

    def _check_balanced_brackets(self, content: str) -> List[str]:
        """Check for balanced brackets in JavaScript."""
        errors = []

        # Remove strings and comments to avoid false positives
        cleaned = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'"[^"]*"', '""', cleaned)
        cleaned = re.sub(r"'[^']*'", "''", cleaned)
        cleaned = re.sub(r'`[^`]*`', '``', cleaned)

        # Check bracket balance
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []

        for i, char in enumerate(cleaned):
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    errors.append(f"Unmatched closing bracket '{char}' at position {i}")
                else:
                    opening = stack.pop()
                    if brackets[opening] != char:
                        errors.append(f"Mismatched brackets: '{opening}' and '{char}'")

        if stack:
            errors.append(f"Unclosed brackets: {stack}")

        return errors

    def validate_scss_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate SCSS file syntax.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for balanced braces
            brace_errors = self._check_scss_braces(content)
            errors.extend(brace_errors)

            # Check for Odoo-specific SCSS variables
            if '$o-' in content or '$theme-' in content:
                # Validate Odoo theme variables
                theme_errors = self._validate_odoo_theme_variables(content)
                errors.extend(theme_errors)

            return len(errors) == 0, errors

        except Exception as e:
            errors.append(f"Failed to read file: {str(e)}")
            return False, errors

    def _check_scss_braces(self, content: str) -> List[str]:
        """Check for balanced braces in SCSS."""
        errors = []

        # Remove comments
        cleaned = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)

        # Count braces
        open_braces = cleaned.count('{')
        close_braces = cleaned.count('}')

        if open_braces != close_braces:
            errors.append(f"Unbalanced braces: {open_braces} opening, {close_braces} closing")

        return errors

    def _validate_odoo_theme_variables(self, content: str) -> List[str]:
        """Validate Odoo theme-specific SCSS variables."""
        errors = []

        # Check for deprecated variable names
        deprecated_vars = {
            '$headings-font-weight': '$o-theme-headings-font-weight',
            '$font-size-base': '$o-theme-font-size-base',
        }

        for old, new in deprecated_vars.items():
            if old in content:
                errors.append(f"Deprecated variable '{old}', use '{new}' instead")

        return errors

    def validate_all(self) -> Dict:
        """
        Validate all files in the project.

        Returns:
            Dictionary with validation results
        """
        print("\n" + "=" * 60)
        print("ODOO MODULE SYNTAX VALIDATION")
        print("=" * 60)
        print(f"Project: {self.project_path}\n")

        # Validate Python files
        print("Validating Python files...")
        py_files = list(self.project_path.glob("**/*.py"))
        self.stats['python_files'] = len(py_files)

        for py_file in py_files:
            if '__pycache__' in str(py_file):
                continue

            is_valid, errors = self.validate_python_file(py_file)
            if not is_valid:
                rel_path = py_file.relative_to(self.project_path)
                for error in errors:
                    self.errors['python'].append(f"{rel_path}: {error}")
                self.stats['python_errors'] += 1

            if self.verbose:
                status = "✓" if is_valid else "✗"
                print(f"  {status} {py_file.name}")

        # Validate XML files
        print("\nValidating XML files...")
        xml_files = list(self.project_path.glob("**/*.xml"))
        self.stats['xml_files'] = len(xml_files)

        for xml_file in xml_files:
            is_valid, errors = self.validate_xml_file(xml_file)
            if not is_valid:
                rel_path = xml_file.relative_to(self.project_path)
                for error in errors:
                    self.errors['xml'].append(f"{rel_path}: {error}")
                self.stats['xml_errors'] += 1

            if self.verbose:
                status = "✓" if is_valid else "✗"
                print(f"  {status} {xml_file.name}")

        # Validate JavaScript files
        print("\nValidating JavaScript files...")
        js_files = list(self.project_path.glob("**/*.js"))
        self.stats['js_files'] = len(js_files)

        for js_file in js_files:
            if 'node_modules' in str(js_file) or '.min.js' in str(js_file):
                continue

            is_valid, errors = self.validate_javascript_file(js_file)
            if not is_valid:
                rel_path = js_file.relative_to(self.project_path)
                for error in errors:
                    self.errors['js'].append(f"{rel_path}: {error}")
                self.stats['js_errors'] += 1

            if self.verbose:
                status = "✓" if is_valid else "✗"
                print(f"  {status} {js_file.name}")

        # Validate SCSS files
        print("\nValidating SCSS files...")
        scss_files = list(self.project_path.glob("**/*.scss"))
        self.stats['scss_files'] = len(scss_files)

        for scss_file in scss_files:
            is_valid, errors = self.validate_scss_file(scss_file)
            if not is_valid:
                rel_path = scss_file.relative_to(self.project_path)
                for error in errors:
                    self.errors['scss'].append(f"{rel_path}: {error}")
                self.stats['scss_errors'] += 1

            if self.verbose:
                status = "✓" if is_valid else "✗"
                print(f"  {status} {scss_file.name}")

        # Calculate totals
        self.stats['total_errors'] = (
            self.stats['python_errors'] +
            self.stats['xml_errors'] +
            self.stats['js_errors'] +
            self.stats['scss_errors']
        )

        self.stats['total_warnings'] = sum(len(warns) for warns in self.warnings.values())

        return {
            'valid': self.stats['total_errors'] == 0,
            'errors': dict(self.errors),
            'warnings': dict(self.warnings),
            'stats': self.stats
        }

    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate a detailed validation report.

        Args:
            output_file: Optional path to save the report

        Returns:
            Report content as string
        """
        report = []
        report.append("# Odoo Module Syntax Validation Report")
        report.append(f"\n**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"**Project**: {self.project_path.name}")
        report.append(f"**Path**: {self.project_path}")

        # Statistics
        report.append("\n## Statistics")
        report.append(f"- Python files: {self.stats['python_files']} "
                     f"(Errors: {self.stats['python_errors']})")
        report.append(f"- XML files: {self.stats['xml_files']} "
                     f"(Errors: {self.stats['xml_errors']})")
        report.append(f"- JavaScript files: {self.stats['js_files']} "
                     f"(Errors: {self.stats['js_errors']})")
        report.append(f"- SCSS files: {self.stats['scss_files']} "
                     f"(Errors: {self.stats['scss_errors']})")
        report.append(f"- **Total Errors**: {self.stats['total_errors']}")
        report.append(f"- **Total Warnings**: {self.stats['total_warnings']}")

        # Errors
        if self.errors:
            report.append("\n## Errors (Must Fix)")

            for file_type, error_list in self.errors.items():
                if error_list:
                    report.append(f"\n### {file_type.upper()} Errors")
                    for error in error_list:
                        report.append(f"- {error}")

        # Warnings
        if self.warnings:
            report.append("\n## Warnings (Should Review)")

            for file_type, warning_list in self.warnings.items():
                if warning_list:
                    report.append(f"\n### {file_type.upper()} Warnings")
                    for warning in warning_list:
                        report.append(f"- {warning}")

        # Summary
        if self.stats['total_errors'] == 0:
            report.append("\n## ✓ Validation Passed")
            report.append("No syntax errors detected. Module is ready for deployment.")
        else:
            report.append("\n## ✗ Validation Failed")
            report.append(f"Found {self.stats['total_errors']} error(s) that must be fixed.")
            report.append("\n### Next Steps:")
            report.append("1. Fix all errors listed above")
            report.append("2. Run validation again: `python syntax_validator.py <project_path>`")
            report.append("3. Consider using auto-fix: `python auto_fix_library.py <project_path>`")

        report_content = '\n'.join(report)

        # Save report if output file specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"\nReport saved to: {output_file}")

        return report_content


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print("Usage: python syntax_validator.py <project_path> [--verbose] [--report <output_file>]")
        print("\nOptions:")
        print("  --verbose    Show detailed output for each file")
        print("  --report     Generate markdown report file")
        print("\nExample:")
        print("  python syntax_validator.py C:\\odoo\\odoo19\\projects\\mymodule --verbose --report validation.md")
        sys.exit(1)

    project_path = sys.argv[1]
    verbose = '--verbose' in sys.argv

    # Check for report option
    report_file = None
    if '--report' in sys.argv:
        report_idx = sys.argv.index('--report')
        if report_idx + 1 < len(sys.argv):
            report_file = sys.argv[report_idx + 1]

    if not os.path.exists(project_path):
        print(f"Error: Path '{project_path}' does not exist")
        sys.exit(1)

    # Run validation
    validator = SyntaxValidator(project_path, verbose=verbose)
    results = validator.validate_all()

    # Generate report
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    if results['valid']:
        print("✓ PASSED - No syntax errors detected")
    else:
        print(f"✗ FAILED - {results['stats']['total_errors']} error(s) found")

    if results['stats']['total_warnings'] > 0:
        print(f"⚠ {results['stats']['total_warnings']} warning(s) to review")

    # Generate detailed report
    if report_file or not results['valid']:
        if not report_file:
            report_file = project_path + "/SYNTAX_VALIDATION_REPORT.md"

        report = validator.generate_report(report_file)

        if not results['valid']:
            print(f"\nDetailed report: {report_file}")
            print("Run with --verbose for more details")

    # Exit with appropriate code
    sys.exit(0 if results['valid'] else 1)


if __name__ == "__main__":
    main()
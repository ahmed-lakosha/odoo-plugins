#!/usr/bin/env python3
"""
Automated Fix Library for Odoo Module Issues
Pattern-based auto-correction system for common syntax and compatibility problems
"""

import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import ast
import shutil


class AutoFixLibrary:
    """Library of automated fixes for common Odoo issues"""

    def __init__(self, project_path: str, backup: bool = True):
        """
        Initialize the auto-fix library.

        Args:
            project_path: Path to the Odoo project/module
            backup: Whether to create backups before fixes
        """
        self.project_path = Path(project_path)
        self.backup = backup
        self.fixes_applied = []
        self.files_modified = set()
        self.backup_path = None

    def create_backup(self) -> Optional[Path]:
        """Create a backup of the project before applying fixes."""
        if not self.backup:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.project_path.name}_autofix_backup_{timestamp}"
        self.backup_path = self.project_path.parent / backup_name

        print(f"Creating backup at: {self.backup_path}")
        shutil.copytree(self.project_path, self.backup_path)
        return self.backup_path

    # ========== Python Fixes ==========

    def fix_python_imports(self) -> int:
        """Fix common Python import issues."""
        fixed_count = 0

        patterns = [
            # Old openerp imports
            (r'from openerp import', 'from odoo import'),
            (r'import openerp', 'import odoo'),

            # Deprecated slug/unslug imports
            (r'from odoo\.addons\.http_routing\.models\.ir_http import slug',
             '''from odoo.http import request

def slug(value):
    """Compatibility wrapper for slug function"""
    return request.env['ir.http']._slug(value)'''),

            # url_for replacement
            (r'from odoo\.addons\.http_routing\.models\.ir_http import url_for',
             '# url_for import removed - use self.env["ir.http"]._url_for() instead'),
        ]

        py_files = list(self.project_path.glob("**/*.py"))
        for py_file in py_files:
            if '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content
                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content)

                if content != original:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.files_modified.add(py_file)
                    fixed_count += 1

            except Exception as e:
                print(f"  Error fixing {py_file}: {e}")

        if fixed_count > 0:
            self.fixes_applied.append(f"Fixed Python imports in {fixed_count} files")

        return fixed_count

    def fix_python_api_decorators(self) -> int:
        """Fix incorrect API decorator usage."""
        fixed_count = 0

        py_files = list(self.project_path.glob("**/*.py"))
        for py_file in py_files:
            if '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                modified = False
                for i in range(len(lines) - 1):
                    # Check for API decorator not followed by def
                    if re.match(r'^\s*@api\.\w+\s*$', lines[i]):
                        next_line = lines[i + 1] if i + 1 < len(lines) else ''
                        if not re.match(r'^\s*def\s+', next_line):
                            # Add a comment to flag the issue
                            lines[i] = lines[i].rstrip() + "  # FIX: Decorator needs function below\n"
                            modified = True

                if modified:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    self.files_modified.add(py_file)
                    fixed_count += 1

            except Exception as e:
                print(f"  Error fixing {py_file}: {e}")

        if fixed_count > 0:
            self.fixes_applied.append(f"Fixed API decorators in {fixed_count} files")

        return fixed_count

    def fix_python_syntax_errors(self) -> int:
        """Attempt to fix common Python syntax errors."""
        fixed_count = 0

        py_files = list(self.project_path.glob("**/*.py"))
        for py_file in py_files:
            if '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Try to parse and identify syntax errors
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    # Attempt automatic fixes based on error type
                    fixed_content = self._attempt_python_syntax_fix(content, e)
                    if fixed_content != content:
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(fixed_content)
                        self.files_modified.add(py_file)
                        fixed_count += 1

            except Exception as e:
                print(f"  Error processing {py_file}: {e}")

        if fixed_count > 0:
            self.fixes_applied.append(f"Fixed Python syntax errors in {fixed_count} files")

        return fixed_count

    def _attempt_python_syntax_fix(self, content: str, error: SyntaxError) -> str:
        """Attempt to fix specific syntax errors."""
        lines = content.split('\n')

        if error.msg == "unexpected EOF while parsing":
            # Add missing closing parenthesis/bracket
            content += "\n)"

        elif "invalid syntax" in error.msg and error.lineno:
            line_idx = error.lineno - 1
            if line_idx < len(lines):
                line = lines[line_idx]

                # Fix missing colons
                if re.match(r'^\s*(if|elif|else|for|while|def|class|try|except|finally|with)\s+.*[^:]$', line):
                    lines[line_idx] = line + ':'

                # Fix incorrect indentation after colon
                elif line.strip().endswith(':') and line_idx + 1 < len(lines):
                    next_line = lines[line_idx + 1]
                    if next_line.strip() and not next_line.startswith(' '):
                        lines[line_idx + 1] = '    ' + next_line

            content = '\n'.join(lines)

        return content

    # ========== XML Fixes ==========

    def fix_xml_comments(self) -> int:
        """Fix malformed XML comments."""
        fixed_count = 0

        xml_files = list(self.project_path.glob("**/*.xml"))
        for xml_file in xml_files:
            try:
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Fix nested comment starts
                while '<!--' in content and '<!--' in content[content.index('<!--') + 4:]:
                    content = re.sub(r'<!--([^>]*)<!--', r'<!-- \1', content)

                # Fix nested comment ends
                while '-->' in content and '-->' in content[content.index('-->') + 3:]:
                    content = re.sub(r'-->([^<]*)-->', r'\1 -->', content)

                # Fix double hyphens within comments
                def fix_comment_hyphens(match):
                    comment = match.group(0)
                    inner = comment[4:-3]
                    inner = re.sub(r'--+', '- -', inner)
                    return f'<!--{inner}-->'

                content = re.sub(r'<!--.*?-->', fix_comment_hyphens, content, flags=re.DOTALL)

                if content != original:
                    with open(xml_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.files_modified.add(xml_file)
                    fixed_count += 1

            except Exception as e:
                print(f"  Error fixing {xml_file}: {e}")

        if fixed_count > 0:
            self.fixes_applied.append(f"Fixed XML comments in {fixed_count} files")

        return fixed_count

    def fix_xml_odoo19_compatibility(self) -> int:
        """Fix Odoo 19 specific XML issues."""
        fixed_count = 0

        xml_files = list(self.project_path.glob("**/*.xml"))
        for xml_file in xml_files:
            try:
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Convert tree to list
                content = re.sub(r'<tree(\s+[^>]*)?>', r'<list\1>', content)
                content = content.replace('</tree>', '</list>')

                # Fix view_mode references
                content = re.sub(r'(<field name="view_mode">)tree', r'\1list', content)
                content = re.sub(r'view_mode["\'][^>]*>tree', r"view_mode'>list", content)

                # Remove group tags from search views
                if '<search' in content:
                    content = self._fix_search_view_groups(content)

                # Fix kanban templates
                content = content.replace('t-name="kanban-box"', 't-name="card"')

                # Remove numbercall from cron
                content = re.sub(r'<field\s+name="numbercall"[^>]*>.*?</field>', '', content, flags=re.DOTALL)
                content = re.sub(r'<field\s+name="numbercall"[^/]*/>', '', content)

                # Fix active_id to id
                content = re.sub(r"context=['\"]([^'\"]*?)active_id([^'\"]*?)['\"]",
                               r"context='\1id\2'", content)

                # Remove edit="1"
                content = re.sub(r'\s+edit=["\']1["\']', '', content)

                # Fix XPath expressions with //tree
                content = re.sub(r'(xpath[^>]*expr=")//tree', r'\1//list', content)
                content = re.sub(r"(xpath[^>]*expr=')//tree", r"\1//list", content)

                # Remove expand attribute from search view groups
                content = re.sub(r'(<group[^>]*)\s+expand=["\'][01]["\']', r'\1', content)
                content = re.sub(r"(<group[^>]*)\s+expand='[01]'", r'\1', content)

                if content != original:
                    with open(xml_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.files_modified.add(xml_file)
                    fixed_count += 1

            except Exception as e:
                print(f"  Error fixing {xml_file}: {e}")

        if fixed_count > 0:
            self.fixes_applied.append(f"Fixed XML Odoo 19 compatibility in {fixed_count} files")

        return fixed_count

    def _fix_search_view_groups(self, content: str) -> str:
        """Remove group tags from search views."""
        pattern = r'(<search[^>]*>)(.*?)(</search>)'

        def remove_groups(match):
            search_start = match.group(1)
            search_content = match.group(2)
            search_end = match.group(3)

            # Remove group tags
            search_content = re.sub(r'<group[^>]*>', '', search_content)
            search_content = search_content.replace('</group>', '')

            # Add separator if needed
            if 'group_by' in search_content and '<separator/>' not in search_content:
                search_content = re.sub(r'(\s*)(<filter[^>]*group_by[^>]*>)',
                                       r'\1<separator/>\1\2', search_content, count=1)

            return search_start + search_content + search_end

        return re.sub(pattern, remove_groups, content, flags=re.DOTALL)

    # ========== JavaScript Fixes ==========

    def fix_javascript_rpc(self) -> int:
        """Fix RPC service usage in JavaScript files."""
        fixed_count = 0

        # JSON-RPC helper method
        jsonrpc_helper = '''
    async _jsonRpc(endpoint, params = {}) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Csrf-Token': document.querySelector('meta[name="csrf-token"]')?.content || '',
                },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: params,
                    id: Math.floor(Math.random() * 1000000)
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error.message || 'RPC call failed');
            }
            return data.result;
        } catch (error) {
            console.error('JSON-RPC call failed:', error);
            throw error;
        }
    }'''

        js_files = list(self.project_path.glob("**/*.js"))
        for js_file in js_files:
            if 'node_modules' in str(js_file) or '.min.js' in str(js_file):
                continue

            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Remove RPC service import
                content = re.sub(r'import\s*{\s*jsonrpc\s*}\s*from\s*["\']@web/core/network/rpc_service["\'];?',
                               '// RPC service removed in Odoo 19', content)

                # Remove useService for RPC
                content = re.sub(r'this\.rpc\s*=\s*useService\(["\']rpc["\']\);?\s*\n?', '', content)

                # Replace this.rpc calls with this._jsonRpc
                if 'this.rpc(' in content:
                    content = content.replace('this.rpc(', 'this._jsonRpc(')

                    # Add helper method if not present
                    if '_jsonRpc(endpoint, params' not in content:
                        # Find setup() method and add after it
                        setup_match = re.search(r'(setup\(\)\s*{[^}]*})', content)
                        if setup_match:
                            insert_pos = setup_match.end()
                            content = content[:insert_pos] + '\n' + jsonrpc_helper + '\n' + content[insert_pos:]

                if content != original:
                    with open(js_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.files_modified.add(js_file)
                    fixed_count += 1

            except Exception as e:
                print(f"  Error fixing {js_file}: {e}")

        if fixed_count > 0:
            self.fixes_applied.append(f"Fixed JavaScript RPC in {fixed_count} files")

        return fixed_count

    def fix_javascript_module_declaration(self) -> int:
        """Add missing @odoo-module declarations."""
        fixed_count = 0

        js_files = list(self.project_path.glob("**/*.js"))
        for js_file in js_files:
            if 'node_modules' in str(js_file) or '.min.js' in str(js_file):
                continue

            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if module declaration is missing
                if content.strip() and not content.strip().startswith('/** @odoo-module'):
                    # Add module declaration
                    content = '/** @odoo-module **/\n\n' + content

                    with open(js_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.files_modified.add(js_file)
                    fixed_count += 1

            except Exception as e:
                print(f"  Error fixing {js_file}: {e}")

        if fixed_count > 0:
            self.fixes_applied.append(f"Added module declarations to {fixed_count} JavaScript files")

        return fixed_count

    def fix_javascript_async_await(self) -> int:
        """Fix async/await patterns in JavaScript."""
        fixed_count = 0

        js_files = list(self.project_path.glob("**/*.js"))
        for js_file in js_files:
            if 'node_modules' in str(js_file) or '.min.js' in str(js_file):
                continue

            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Fix promise chains that should use async/await
                # Look for .then().catch() patterns
                if '.then(' in content and 'async' not in content[:100]:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'function' in line and '.then(' in '\n'.join(lines[i:i+10]):
                            # Add async to function
                            lines[i] = re.sub(r'function(\s+\w+)?\s*\(',
                                            r'async function\1(', lines[i])

                    content = '\n'.join(lines)

                if content != original:
                    with open(js_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.files_modified.add(js_file)
                    fixed_count += 1

            except Exception as e:
                print(f"  Error fixing {js_file}: {e}")

        if fixed_count > 0:
            self.fixes_applied.append(f"Fixed async/await patterns in {fixed_count} files")

        return fixed_count

    # ========== SCSS Fixes ==========

    def fix_scss_variables(self) -> int:
        """Fix SCSS variable naming issues."""
        fixed_count = 0

        # Variable replacements for Odoo 19
        replacements = {
            '$headings-font-weight': '$o-theme-headings-font-weight',
            '$font-size-base': '$o-theme-font-size-base',
            '$body-bg': '$o-theme-body-bg',
            '$text-color': '$o-theme-text-color',
            '$link-color': '$o-theme-link-color',
        }

        scss_files = list(self.project_path.glob("**/*.scss"))
        for scss_file in scss_files:
            try:
                with open(scss_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content
                for old, new in replacements.items():
                    content = content.replace(old, new)

                # Fix color palette definitions
                if 'o-color-palettes' in content and "'menu':" not in content:
                    content = re.sub(
                        r"('o-color-5':\s*[^,]+,?)(\s*\))",
                        r"\1,\2        'menu': 4,\2        'footer': 1,\2        'copyright': 5\2",
                        content
                    )

                if content != original:
                    with open(scss_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.files_modified.add(scss_file)
                    fixed_count += 1

            except Exception as e:
                print(f"  Error fixing {scss_file}: {e}")

        if fixed_count > 0:
            self.fixes_applied.append(f"Fixed SCSS variables in {fixed_count} files")

        return fixed_count

    def fix_scss_syntax(self) -> int:
        """Fix SCSS syntax issues."""
        fixed_count = 0

        scss_files = list(self.project_path.glob("**/*.scss"))
        for scss_file in scss_files:
            try:
                with open(scss_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Fix unclosed braces
                open_count = content.count('{')
                close_count = content.count('}')

                if open_count > close_count:
                    # Add missing closing braces
                    content += '\n' + '}' * (open_count - close_count)
                elif close_count > open_count:
                    # Remove extra closing braces
                    for _ in range(close_count - open_count):
                        content = content[:content.rfind('}')]

                # Fix missing semicolons
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    # Check if line is a property declaration without semicolon
                    if ':' in line and not line.strip().endswith((';', '{', '}')) \
                       and not line.strip().startswith(('/', '*', '@')):
                        lines[i] = line.rstrip() + ';'

                content = '\n'.join(lines)

                if content != original:
                    with open(scss_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.files_modified.add(scss_file)
                    fixed_count += 1

            except Exception as e:
                print(f"  Error fixing {scss_file}: {e}")

        if fixed_count > 0:
            self.fixes_applied.append(f"Fixed SCSS syntax in {fixed_count} files")

        return fixed_count

    def fix_controller_type(self) -> int:
        """Fix Odoo 19: type='json' → type='jsonrpc' in @http.route decorators."""
        fixed_count = 0
        pattern = re.compile(
            r"(@http\.route\([^)]*?)type\s*=\s*['\"]json['\"]([^)]*\))",
            re.DOTALL,
        )

        py_files = list(self.project_path.glob("**/*.py"))
        for py_file in py_files:
            if '__pycache__' in str(py_file):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                new_content = pattern.sub(
                    lambda m: m.group(1) + "type='jsonrpc'" + m.group(2),
                    content,
                )

                if new_content != content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    self.files_modified.add(py_file)
                    fixed_count += 1

            except Exception as e:
                print(f"  Error fixing controller type in {py_file}: {e}")

        if fixed_count > 0:
            self.fixes_applied.append(
                f"Fixed controller type='json' → type='jsonrpc' in {fixed_count} files"
            )
        return fixed_count

    def fix_attrs_to_inline(self) -> int:
        """Fix Odoo 18/19: attrs={'invisible':[...]} → invisible='...' inline expressions in XML."""
        fixed_count = 0

        def _domain_to_expr(domain_str: str) -> str:
            """Convert simple Odoo domain list to Python inline expression."""
            # Match single condition: [('field', '=', 'value')]
            m = re.match(
                r"""\[\s*\(\s*['"](\w+)['"]\s*,\s*['"]([!=<>]{1,2})['"]\s*,\s*['"]?([^'"\)\]]+)['"]?\s*\)\s*\]""",
                domain_str.strip(),
            )
            if m:
                field, op, value = m.group(1), m.group(2), m.group(3).strip()
                # Wrap non-numeric values in quotes
                if not re.match(r'^-?\d+(\.\d+)?$', value) and value not in ('True', 'False', 'None'):
                    value = f"'{value}'"
                return f"{field} {op} {value}"
            # Fallback: return the raw domain (requires manual review)
            return domain_str

        def _convert_attrs(match: re.Match) -> str:
            """Convert a single attrs="..." attribute to individual inline attrs."""
            original = match.group(0)
            attrs_content = match.group(1)

            try:
                # Normalise quotes for safe parsing
                normalised = attrs_content.replace("'", '"')
                import json
                attrs_dict = json.loads(normalised)
            except Exception:
                return original  # Can't parse safely; leave unchanged

            replacements = []
            for attr_name in ('invisible', 'required', 'readonly', 'column_invisible'):
                if attr_name in attrs_dict:
                    expr = _domain_to_expr(str(attrs_dict[attr_name]).replace('"', "'"))
                    replacements.append(f'{attr_name}="{expr}"')

            if not replacements:
                return original
            return ' '.join(replacements)

        attrs_re = re.compile(r"""attrs\s*=\s*["']\{([^}]+)\}["']""", re.DOTALL)

        xml_files = list(self.project_path.glob("**/*.xml"))
        for xml_file in xml_files:
            try:
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                new_content = attrs_re.sub(_convert_attrs, content)

                if new_content != content:
                    with open(xml_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    self.files_modified.add(xml_file)
                    fixed_count += 1

            except Exception as e:
                print(f"  Error fixing attrs in {xml_file}: {e}")

        if fixed_count > 0:
            self.fixes_applied.append(
                f"Converted attrs={{}} to inline expressions in {fixed_count} files"
            )
        return fixed_count

    def fix_owl_lifecycle_hooks(self) -> int:
        """Fix OWL 1.x → OWL 2.0: rename lifecycle hooks in JS files."""
        fixed_count = 0
        renames = [
            (r'\bmounted\s*\(\s*\)\s*\{', 'onMounted() {'),
            (r'\bwillStart\s*\(\s*\)\s*\{', 'onWillStart() {'),
            (r'\bpatched\s*\(\s*\)\s*\{', 'onPatched() {'),
            (r'\bwillUnmount\s*\(\s*\)\s*\{', 'onWillUnmount() {'),
            (r'\bwillUpdateProps\s*\(\s*\)\s*\{', 'onWillUpdateProps() {'),
            # Constructor with parent/props → setup()
            (r'\bconstructor\s*\(\s*parent\s*,\s*props\s*\)\s*\{', 'setup() {'),
        ]

        js_files = list(self.project_path.glob("**/*.js"))
        for js_file in js_files:
            if 'node_modules' in str(js_file) or '.min.js' in str(js_file):
                continue
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Only process files that use OWL (import from @odoo/owl or owl.Component)
                if 'Component' not in content:
                    continue

                new_content = content
                for pattern, replacement in renames:
                    new_content = re.sub(pattern, replacement, new_content)

                if new_content != content:
                    with open(js_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    self.files_modified.add(js_file)
                    fixed_count += 1

            except Exception as e:
                print(f"  Error fixing OWL hooks in {js_file}: {e}")

        if fixed_count > 0:
            self.fixes_applied.append(
                f"Renamed OWL 1.x lifecycle hooks to OWL 2.0 in {fixed_count} files"
            )
        return fixed_count

    # ========== Main Methods ==========

    def apply_all_fixes(self) -> Dict:
        """Apply all available fixes."""
        print("\n" + "=" * 60)
        print("AUTOMATED FIX LIBRARY")
        print("=" * 60)
        print(f"Project: {self.project_path}\n")

        # Create backup
        if self.backup:
            self.create_backup()

        results = {}

        # Python fixes
        print("Applying Python fixes...")
        results['python_imports'] = self.fix_python_imports()
        results['python_decorators'] = self.fix_python_api_decorators()
        results['python_syntax'] = self.fix_python_syntax_errors()

        # XML fixes
        print("\nApplying XML fixes...")
        results['xml_comments'] = self.fix_xml_comments()
        results['xml_odoo19'] = self.fix_xml_odoo19_compatibility()

        # Odoo 19 specific Python fixes
        print("\nApplying Odoo 19 Python fixes...")
        results['controller_type'] = self.fix_controller_type()
        results['attrs_inline'] = self.fix_attrs_to_inline()

        # JavaScript fixes
        print("\nApplying JavaScript fixes...")
        results['js_rpc'] = self.fix_javascript_rpc()
        results['js_modules'] = self.fix_javascript_module_declaration()
        results['js_async'] = self.fix_javascript_async_await()
        results['owl_lifecycle'] = self.fix_owl_lifecycle_hooks()

        # SCSS fixes
        print("\nApplying SCSS fixes...")
        results['scss_variables'] = self.fix_scss_variables()
        results['scss_syntax'] = self.fix_scss_syntax()

        # Summary
        total_fixes = sum(results.values())
        results['total_fixes'] = total_fixes
        results['files_modified'] = len(self.files_modified)
        results['fixes_applied'] = self.fixes_applied

        return results

    def apply_specific_fixes(self, fix_types: List[str]) -> Dict:
        """Apply only specific types of fixes."""
        print("\n" + "=" * 60)
        print("SELECTIVE FIX APPLICATION")
        print("=" * 60)
        print(f"Project: {self.project_path}")
        print(f"Fixes to apply: {', '.join(fix_types)}\n")

        # Create backup
        if self.backup:
            self.create_backup()

        results = {}

        fix_mapping = {
            'python_imports': self.fix_python_imports,
            'python_decorators': self.fix_python_api_decorators,
            'python_syntax': self.fix_python_syntax_errors,
            'xml_comments': self.fix_xml_comments,
            'xml_odoo19': self.fix_xml_odoo19_compatibility,
            'controller_type': self.fix_controller_type,
            'attrs_inline': self.fix_attrs_to_inline,
            'js_rpc': self.fix_javascript_rpc,
            'js_modules': self.fix_javascript_module_declaration,
            'js_async': self.fix_javascript_async_await,
            'owl_lifecycle': self.fix_owl_lifecycle_hooks,
            'scss_variables': self.fix_scss_variables,
            'scss_syntax': self.fix_scss_syntax,
        }

        for fix_type in fix_types:
            if fix_type in fix_mapping:
                print(f"Applying {fix_type}...")
                results[fix_type] = fix_mapping[fix_type]()
            else:
                print(f"Unknown fix type: {fix_type}")

        results['total_fixes'] = sum(v for v in results.values() if isinstance(v, int))
        results['files_modified'] = len(self.files_modified)
        results['fixes_applied'] = self.fixes_applied

        return results

    def generate_report(self) -> str:
        """Generate a report of applied fixes."""
        report = []
        report.append("# Auto-Fix Report")
        report.append(f"\n**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"**Project**: {self.project_path.name}")

        if self.backup_path:
            report.append(f"**Backup**: {self.backup_path}")

        report.append("\n## Fixes Applied")
        if self.fixes_applied:
            for fix in self.fixes_applied:
                report.append(f"- {fix}")
        else:
            report.append("No fixes were applied.")

        report.append(f"\n## Summary")
        report.append(f"- Total files modified: {len(self.files_modified)}")

        if self.files_modified:
            report.append("\n## Modified Files")
            for file in sorted(self.files_modified):
                rel_path = file.relative_to(self.project_path)
                report.append(f"- {rel_path}")

        return '\n'.join(report)


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print("Usage: python auto_fix_library.py <project_path> [options]")
        print("\nOptions:")
        print("  --no-backup     Skip creating backup")
        print("  --specific      Apply only specific fixes (comma-separated)")
        print("  --list-fixes    List available fix types")
        print("\nAvailable fix types:")
        print("  python_imports, python_decorators, python_syntax")
        print("  xml_comments, xml_odoo19")
        print("  js_rpc, js_modules, js_async")
        print("  scss_variables, scss_syntax")
        print("\nExample:")
        print("  python auto_fix_library.py /path/to/module")
        print("  python auto_fix_library.py /path/to/module --specific xml_comments,js_rpc")
        sys.exit(1)

    if '--list-fixes' in sys.argv:
        print("Available fix types:")
        print("  - python_imports: Fix Python import statements")
        print("  - python_decorators: Fix API decorator issues")
        print("  - python_syntax: Attempt to fix Python syntax errors")
        print("  - xml_comments: Fix malformed XML comments")
        print("  - xml_odoo19: Fix Odoo 19 XML compatibility issues")
        print("  - js_rpc: Migrate RPC service to fetch API")
        print("  - js_modules: Add missing @odoo-module declarations")
        print("  - js_async: Fix async/await patterns")
        print("  - scss_variables: Update SCSS variable names")
        print("  - scss_syntax: Fix SCSS syntax issues")
        sys.exit(0)

    project_path = sys.argv[1]
    backup = '--no-backup' not in sys.argv

    if not os.path.exists(project_path):
        print(f"Error: Path '{project_path}' does not exist")
        sys.exit(1)

    # Initialize fixer
    fixer = AutoFixLibrary(project_path, backup=backup)

    # Apply fixes
    if '--specific' in sys.argv:
        specific_idx = sys.argv.index('--specific')
        if specific_idx + 1 < len(sys.argv):
            fix_types = sys.argv[specific_idx + 1].split(',')
            results = fixer.apply_specific_fixes(fix_types)
        else:
            print("Error: --specific requires comma-separated list of fix types")
            sys.exit(1)
    else:
        results = fixer.apply_all_fixes()

    # Generate and display report
    print("\n" + "=" * 60)
    print("FIX SUMMARY")
    print("=" * 60)

    if results['total_fixes'] > 0:
        print(f"✓ Applied {results['total_fixes']} fixes")
        print(f"✓ Modified {results['files_modified']} files")

        # Save report
        report_file = Path(project_path) / "AUTOFIX_REPORT.md"
        report = fixer.generate_report()
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nDetailed report: {report_file}")
    else:
        print("No fixes were needed.")

    print("\nNext steps:")
    print("1. Review the changes made")
    print("2. Run syntax validation: python syntax_validator.py " + project_path)
    print("3. Test module installation in Odoo")

    if fixer.backup_path:
        print(f"\nBackup location: {fixer.backup_path}")
        print("To restore: copy backup contents back to original location")


if __name__ == "__main__":
    main()
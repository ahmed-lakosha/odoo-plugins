#!/usr/bin/env python3
"""
Odoo Test Generator Script
==========================
Generates complete test class skeletons for Odoo models by reading the model's
Python source and producing well-structured test files with CRUD, compute,
constraint, and onchange test methods.

Usage:
    python test_generator.py --model sale.order --module /path/to/module
    python test_generator.py --model my.model --module /c/odoo/odoo17/projects/myproject/my_module
    python test_generator.py --model hr.employee --module /c/odoo/odoo17/projects/hr/my_hr --output /custom/path/test_hr_employee.py
"""

import argparse
import ast
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from textwrap import dedent


# ─── Field Type Mappings ──────────────────────────────────────────────────────

FIELD_TYPE_DEFAULTS = {
    'Char': "'Test Value'",
    'Text': "'Multi-line test content.'",
    'Html': "'<p>Test HTML content</p>'",
    'Integer': '1',
    'Float': '100.0',
    'Monetary': '500.0',
    'Boolean': 'True',
    'Date': 'fields.Date.today()',
    'Datetime': 'fields.Datetime.now()',
    'Selection': None,  # Handled specially
    'Many2one': None,   # Handled specially
    'Many2many': '[]',
    'One2many': '[]',
    'Binary': "b'test'",
    'Reference': None,
}

FIELD_ASSERT_PATTERNS = {
    'Char': "self.assertEqual({record}.{field}, {value})",
    'Text': "self.assertTrue({record}.{field})",
    'Html': "self.assertTrue({record}.{field})",
    'Integer': "self.assertEqual({record}.{field}, {value})",
    'Float': "self.assertAlmostEqual({record}.{field}, {value}, places=2)",
    'Monetary': "self.assertAlmostEqual({record}.{field}, {value}, places=2)",
    'Boolean': "self.assertTrue({record}.{field})" ,
    'Date': "self.assertEqual({record}.{field}, fields.Date.today())",
    'Datetime': "self.assertIsNotNone({record}.{field})",
    'Selection': "self.assertIn({record}.{field}, [v[0] for v in {record}._fields['{field}'].selection])",
    'Many2one': "self.assertEqual({record}.{field}, self.{field_ref})",
    'Many2many': "self.assertGreater(len({record}.{field}), 0)",
    'One2many': "self.assertGreater(len({record}.{field}), 0)",
}


# ─── Model Parser ─────────────────────────────────────────────────────────────

class OdooModelParser:
    """Parses an Odoo model Python file to extract field and method information."""

    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.fields = {}
        self.methods = []
        self.model_name = None
        self.class_name = None
        self.description = None
        self.inherit = None
        self.required_fields = []
        self.compute_fields = []
        self.constrained_fields = []
        self.selection_fields = {}

    def find_model_file(self, model_name: str) -> Path | None:
        """Find the Python file that defines the given model name."""
        model_filename_guess = model_name.replace('.', '_') + '.py'
        models_dir = self.module_path / 'models'

        # Try exact filename match first
        if models_dir.exists():
            exact = models_dir / model_filename_guess
            if exact.exists():
                return exact

            # Search all .py files in models/
            for py_file in models_dir.glob('*.py'):
                if py_file.name == '__init__.py':
                    continue
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if f"_name = '{model_name}'" in content or f'_name = "{model_name}"' in content:
                    return py_file

        # Also check top-level .py files
        for py_file in self.module_path.glob('*.py'):
            if py_file.name in ('__init__.py', '__manifest__.py'):
                continue
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            if f"_name = '{model_name}'" in content or f'_name = "{model_name}"' in content:
                return py_file

        return None

    def parse_file(self, file_path: Path) -> bool:
        """Parse a Python model file using AST analysis."""
        try:
            source = file_path.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(source)
        except SyntaxError as e:
            print(f"[WARN] Could not parse {file_path}: {e}. Using regex fallback.")
            return self._parse_with_regex(file_path)

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            # Check if this class has _name or _inherit attribute
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            if target.id == '_name':
                                self.model_name = ast.literal_eval(item.value) if isinstance(item.value, ast.Constant) else None
                                self.class_name = node.name
                            elif target.id == '_description':
                                self.description = ast.literal_eval(item.value) if isinstance(item.value, ast.Constant) else None
                            elif target.id == '_inherit':
                                if isinstance(item.value, ast.Constant):
                                    self.inherit = ast.literal_eval(item.value)

            if not self.class_name:
                continue

            # Parse fields and methods
            for item in node.body:
                if isinstance(item, ast.Assign):
                    self._extract_field(item)
                elif isinstance(item, ast.FunctionDef):
                    self._extract_method(item)

        return bool(self.model_name or self.inherit)

    def _extract_field(self, node: ast.Assign):
        """Extract field definition from an assignment node."""
        if not isinstance(node.value, ast.Call):
            return
        if not isinstance(node.value.func, ast.Attribute):
            return

        func = node.value.func
        if not (isinstance(func.value, ast.Name) and func.value.id == 'fields'):
            return

        field_type = func.attr
        if field_type not in FIELD_TYPE_DEFAULTS:
            return

        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            field_name = target.id
            if field_name.startswith('_'):
                continue

            field_info = {'type': field_type, 'required': False, 'compute': None, 'selection': None}

            # Parse keyword arguments
            for kw in node.value.keywords:
                if kw.arg == 'required' and isinstance(kw.value, ast.Constant):
                    field_info['required'] = bool(kw.value.value)
                elif kw.arg == 'compute' and isinstance(kw.value, ast.Constant):
                    field_info['compute'] = kw.value.value
                elif kw.arg == 'selection':
                    if isinstance(kw.value, ast.List):
                        try:
                            field_info['selection'] = ast.literal_eval(kw.value)
                        except Exception:
                            field_info['selection'] = [('draft', 'Draft'), ('done', 'Done')]

            self.fields[field_name] = field_info

            if field_info['required']:
                self.required_fields.append(field_name)
            if field_info['compute']:
                self.compute_fields.append(field_name)
            if field_info['selection']:
                self.selection_fields[field_name] = field_info['selection']

    def _extract_method(self, node: ast.FunctionDef):
        """Extract method information from a FunctionDef node."""
        if node.name.startswith('_') and not node.name.startswith('__'):
            return  # Skip private methods
        if node.name.startswith('__'):
            return  # Skip dunder methods

        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Attribute):
                decorators.append(dec.attr)
            elif isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                decorators.append(dec.func.attr)

        self.methods.append({
            'name': node.name,
            'decorators': decorators,
            'args': [arg.arg for arg in node.args.args if arg.arg != 'self'],
        })

    def _parse_with_regex(self, file_path: Path) -> bool:
        """Fallback regex-based parsing when AST fails."""
        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # Extract model name
        match = re.search(r"_name\s*=\s*['\"]([^'\"]+)['\"]", content)
        if match:
            self.model_name = match.group(1)

        # Extract class name
        match = re.search(r'class\s+(\w+)\s*\(', content)
        if match:
            self.class_name = match.group(1)

        # Extract description
        match = re.search(r"_description\s*=\s*['\"]([^'\"]+)['\"]", content)
        if match:
            self.description = match.group(1)

        # Extract fields
        field_pattern = re.compile(
            r"(\w+)\s*=\s*fields\.(\w+)\(([^)]*)\)"
        )
        for fm in field_pattern.finditer(content):
            field_name, field_type, field_args = fm.group(1), fm.group(2), fm.group(3)
            if field_name.startswith('_') or field_type not in FIELD_TYPE_DEFAULTS:
                continue
            required = 'required=True' in field_args
            compute = None
            cm = re.search(r"compute=['\"](\w+)['\"]", field_args)
            if cm:
                compute = cm.group(1)
            self.fields[field_name] = {'type': field_type, 'required': required, 'compute': compute, 'selection': None}
            if required:
                self.required_fields.append(field_name)
            if compute:
                self.compute_fields.append(field_name)

        return bool(self.model_name)


# ─── Test Code Generator ──────────────────────────────────────────────────────

class TestCodeGenerator:
    """Generates Python test code from parsed model information."""

    def __init__(self, parser: OdooModelParser, model_name: str):
        self.parser = parser
        self.model_name = model_name
        self.test_class_name = self._make_test_class_name(model_name)
        self.record_var = 'record'

    def _make_test_class_name(self, model_name: str) -> str:
        """Convert 'my.model' to 'TestMyModel'."""
        parts = model_name.replace('.', '_').split('_')
        return 'Test' + ''.join(p.title() for p in parts)

    def _make_module_name(self, module_path: Path) -> str:
        """Extract module technical name from path."""
        return module_path.name

    def _get_required_vals(self) -> dict:
        """Build the minimal required field values dict for create()."""
        vals = {}
        for field_name in self.parser.required_fields:
            field_info = self.parser.fields.get(field_name, {})
            field_type = field_info.get('type', 'Char')
            if field_type == 'Many2one':
                vals[field_name] = f'self.{field_name}.id  # Replace with actual fixture'
            elif field_type == 'Selection':
                sel = field_info.get('selection')
                if sel and isinstance(sel, list):
                    vals[field_name] = repr(sel[0][0])
                else:
                    vals[field_name] = "'draft'  # Replace with valid selection value"
            else:
                default = FIELD_TYPE_DEFAULTS.get(field_type, "'Test Value'")
                vals[field_name] = default
        # Ensure 'name' is always present if it's a field
        if 'name' in self.parser.fields and 'name' not in vals:
            vals['name'] = "'Test Record'"
        return vals

    def _format_vals_dict(self, vals: dict, indent: int = 12) -> str:
        """Format a dictionary as Python code with proper indentation."""
        if not vals:
            return '{}'
        pad = ' ' * indent
        inner_pad = ' ' * (indent + 4)
        lines = ['{']
        for k, v in vals.items():
            lines.append(f"{inner_pad}'{k}': {v},")
        lines.append(f"{pad}}}")
        return '\n'.join(lines)

    def generate(self) -> str:
        """Generate the complete test file content."""
        model_name = self.model_name
        class_name = self.test_class_name
        description = self.parser.description or f'{model_name} Model'
        required_vals = self._get_required_vals()
        has_compute = bool(self.parser.compute_fields)
        has_selection = bool(self.parser.selection_fields)
        many2one_fields = [
            (fname, finfo) for fname, finfo in self.parser.fields.items()
            if finfo['type'] == 'Many2one'
        ]

        lines = []

        # Header
        lines.append(f'"""\nTests for {model_name} ({description})\nGenerated by odoo-test-plugin on {datetime.now().strftime("%Y-%m-%d")}\n"""')
        lines.append('')
        lines.append('from odoo.tests import TransactionCase, tagged')
        lines.append('from odoo.exceptions import ValidationError, UserError')
        lines.append('from odoo import fields')
        if has_compute:
            lines.append('# import additional dependencies as needed')
        lines.append('')
        lines.append('')

        # Class definition
        lines.append(f"@tagged('post_install', '-at_install')")
        lines.append(f'class {class_name}(TransactionCase):')
        lines.append(f'    """Test suite for {model_name}: {description}."""')
        lines.append('')

        # setUpClass
        lines.append('    @classmethod')
        lines.append('    def setUpClass(cls):')
        lines.append('        """Shared fixtures created once for all tests in this class."""')
        lines.append('        super().setUpClass()')
        lines.append('        # Disable email sending to speed up tests')
        lines.append('        cls.env = cls.env(context={')
        lines.append('            **cls.env.context,')
        lines.append("            'mail_notrack': True,")
        lines.append("            'tracking_disable': True,")
        lines.append("            'no_reset_password': True,")
        lines.append('        })')
        lines.append('')

        # Add Many2one fixtures
        for fname, finfo in many2one_fields[:3]:  # Max 3 to avoid noise
            lines.append(f'        # Fixture for {fname} (Many2one - replace ref with actual)')
        if many2one_fields:
            lines.append(f'        # cls.{many2one_fields[0][0]} = cls.env.ref("base.res_partner_1")')
        lines.append('        cls.company = cls.env.company')
        lines.append('')

        # setUp
        lines.append('    def setUp(self):')
        lines.append('        """Fresh records created before each test (auto-rolled back)."""')
        lines.append('        super().setUp()')

        vals_str = self._format_vals_dict(required_vals, indent=8)
        lines.append(f'        self.{self.record_var} = self.env[{repr(model_name)}].create(')
        lines.append(f'            {vals_str}')
        lines.append('        )')
        lines.append('')

        # ── CREATE TESTS ──────────────────────────────────────────────
        lines.append('    # ── CREATE TESTS ─────────────────────────────────────────────────────────')
        lines.append('')
        lines.append('    def test_create_minimal(self):')
        lines.append(f'        """Test creating {model_name} with only required fields."""')
        lines.append(f'        self.assertTrue(self.{self.record_var}.id, "Record ID must be set after create")')
        if 'name' in self.parser.fields:
            lines.append(f"        self.assertEqual(self.{self.record_var}.name, 'Test Record')")
        lines.append('')

        lines.append('    def test_create_full(self):')
        lines.append(f'        """Test creating {model_name} with all optional fields populated."""')
        lines.append(f'        vals = {self._format_vals_dict(required_vals, indent=8)}')
        lines.append(f'        record = self.env[{repr(model_name)}].create(vals)')
        lines.append('        self.assertTrue(record.id)')
        if 'name' in self.parser.fields:
            lines.append("        self.assertEqual(record.name, vals['name'])")
        lines.append('')

        lines.append('    def test_create_missing_required_field(self):')
        lines.append(f'        """Test that creating {model_name} without required fields raises an error."""')
        if self.parser.required_fields:
            lines.append('        with self.assertRaises(Exception):')
            lines.append(f'            self.env[{repr(model_name)}].create({{}})')
        else:
            lines.append('        # No required fields detected; adjust as necessary')
            lines.append('        pass')
        lines.append('')

        # ── READ/SEARCH TESTS ─────────────────────────────────────────
        lines.append('    # ── READ / SEARCH TESTS ──────────────────────────────────────────────────')
        lines.append('')
        lines.append('    def test_search_returns_created_record(self):')
        lines.append(f'        """Test search returns the record created in setUp."""')
        if 'name' in self.parser.fields:
            lines.append(f"        results = self.env[{repr(model_name)}].search([('name', '=', 'Test Record')])")
            lines.append(f'        self.assertIn(self.{self.record_var}, results)')
        else:
            lines.append(f'        results = self.env[{repr(model_name)}].search([("id", "=", self.{self.record_var}.id)])')
            lines.append(f'        self.assertEqual(len(results), 1)')
        lines.append('')

        lines.append('    def test_display_name(self):')
        lines.append(f'        """Test the display name of a {model_name} record."""')
        lines.append(f'        name = self.{self.record_var}.display_name')
        lines.append('        self.assertTrue(name, "display_name must not be empty")')
        lines.append('')

        # ── WRITE TESTS ───────────────────────────────────────────────
        lines.append('    # ── WRITE TESTS ──────────────────────────────────────────────────────────')
        lines.append('')
        if 'name' in self.parser.fields:
            lines.append('    def test_write_name(self):')
            lines.append('        """Test updating the name field."""')
            lines.append(f"        self.{self.record_var}.write({{'name': 'Updated Name'}})")
            lines.append(f"        self.assertEqual(self.{self.record_var}.name, 'Updated Name')")
            lines.append('')

        # Write test for first non-required, non-compute Char/Float field
        writable = [
            (fname, finfo) for fname, finfo in self.parser.fields.items()
            if fname != 'name'
            and not finfo.get('compute')
            and finfo['type'] in ('Float', 'Integer', 'Monetary', 'Char')
        ]
        if writable:
            fname, finfo = writable[0]
            ftype = finfo['type']
            new_val = '999.99' if ftype in ('Float', 'Monetary') else ('99' if ftype == 'Integer' else "'New Value'")
            assert_method = 'assertAlmostEqual' if ftype in ('Float', 'Monetary') else 'assertEqual'
            extra = ', places=2' if ftype in ('Float', 'Monetary') else ''
            lines.append(f'    def test_write_{fname}(self):')
            lines.append(f'        """Test writing to the {fname} field."""')
            lines.append(f'        self.{self.record_var}.write({{"{fname}": {new_val}}})')
            lines.append(f'        self.{assert_method}(self.{self.record_var}.{fname}, {new_val}{extra})')
            lines.append('')

        # ── DELETE TESTS ──────────────────────────────────────────────
        lines.append('    # ── DELETE TESTS ─────────────────────────────────────────────────────────')
        lines.append('')
        lines.append('    def test_unlink_draft_record(self):')
        lines.append(f'        """Test deleting a record in draft/default state."""')
        lines.append(f'        record_id = self.{self.record_var}.id')
        lines.append(f'        self.{self.record_var}.unlink()')
        lines.append(f'        result = self.env[{repr(model_name)}].search([("id", "=", record_id)])')
        lines.append('        self.assertFalse(result, "Record should have been deleted")')
        lines.append('')

        # ── COMPUTE FIELD TESTS ───────────────────────────────────────
        if has_compute:
            lines.append('    # ── COMPUTE FIELD TESTS ──────────────────────────────────────────────────')
            lines.append('')
            for fname in self.parser.compute_fields[:3]:
                finfo = self.parser.fields.get(fname, {})
                ftype = finfo.get('type', 'Char')
                lines.append(f'    def test_compute_{fname}(self):')
                lines.append(f'        """Test that {fname} is correctly computed."""')
                lines.append(f'        # Verify the computed value is set (not False/None for required logic)')
                if ftype in ('Float', 'Integer', 'Monetary'):
                    lines.append(f'        self.assertIsNotNone(self.{self.record_var}.{fname})')
                elif ftype == 'Boolean':
                    lines.append(f'        # Boolean compute fields may be True or False - verify logic')
                    lines.append(f'        self.assertIsInstance(self.{self.record_var}.{fname}, bool)')
                else:
                    lines.append(f'        # Adjust assertion based on expected computed value')
                    lines.append(f'        self.assertIsNotNone(self.{self.record_var}.{fname})')
                lines.append(f'        # TODO: Modify a dependency field and verify recompute triggers')
                lines.append(f'        # self.{self.record_var}.write({{\'dependency_field\': new_value}})')
                lines.append(f'        # self.{self.record_var}.invalidate_recordset(["{fname}"])')
                lines.append(f'        # self.assertEqual(self.{self.record_var}.{fname}, expected_value)')
                lines.append('')

        # ── SELECTION FIELD TESTS ─────────────────────────────────────
        if has_selection:
            lines.append('    # ── SELECTION FIELD TESTS ────────────────────────────────────────────────')
            lines.append('')
            for fname, selection in list(self.parser.selection_fields.items())[:2]:
                lines.append(f'    def test_{fname}_selection_values(self):')
                lines.append(f'        """Test that {fname} accepts all valid selection values."""')
                valid_keys = [s[0] for s in selection if isinstance(s, (list, tuple)) and len(s) == 2]
                lines.append(f'        valid_values = {repr(valid_keys)}')
                lines.append(f'        for val in valid_values:')
                lines.append(f'            self.{self.record_var}.write({{"{fname}": val}})')
                lines.append(f'            self.assertEqual(self.{self.record_var}.{fname}, val)')
                lines.append('')

        # ── CONSTRAINT TESTS ──────────────────────────────────────────
        lines.append('    # ── CONSTRAINT TESTS ─────────────────────────────────────────────────────')
        lines.append('')
        lines.append('    def test_sql_constraint_example(self):')
        lines.append('        """Test SQL unique constraints prevent duplicate data.')
        lines.append('        Adjust field names to match actual unique constraints in this model.')
        lines.append('        """')
        if 'name' in self.parser.fields:
            lines.append('        # Example: If name has a unique constraint')
            lines.append("        # self.env['" + model_name + "'].create({'name': 'Unique'})")
            lines.append('        # with self.assertRaises(Exception):')
            lines.append('        #     with self.env.cr.savepoint():')
            lines.append("        #         self.env['" + model_name + "'].create({'name': 'Unique'})")
            lines.append('        pass  # Replace with actual constraint test')
        else:
            lines.append('        pass  # Add constraint tests specific to this model')
        lines.append('')

        lines.append('    def test_python_constraint_validation(self):')
        lines.append('        """Test @constrains decorated validation methods.')
        lines.append('        Adjust to match actual constraints in this model.')
        lines.append('        """')
        lines.append('        # Example pattern:')
        lines.append('        # with self.assertRaises(ValidationError):')
        lines.append('        #     self.record.write({"amount": -1})')
        lines.append('        pass  # Add validation constraint tests')
        lines.append('')

        # ── BUSINESS METHOD TESTS ─────────────────────────────────────
        action_methods = [m for m in self.parser.methods if m['name'].startswith('action_')]
        if action_methods:
            lines.append('    # ── BUSINESS METHOD TESTS ────────────────────────────────────────────────')
            lines.append('')
            for method_info in action_methods[:4]:
                mname = method_info['name']
                lines.append(f'    def test_{mname}(self):')
                lines.append(f'        """Test the {mname}() method."""')
                lines.append(f'        result = self.{self.record_var}.{mname}()')
                lines.append(f'        # Verify state change or returned action')
                lines.append(f'        # self.assertEqual(self.{self.record_var}.state, "expected_state")')
                lines.append(f'        # If it returns an action dict:')
                lines.append(f'        # self.assertIn("type", result)')
                lines.append('')

        # ── MULTI-RECORD TESTS ────────────────────────────────────────
        lines.append('    # ── MULTI-RECORD TESTS ───────────────────────────────────────────────────')
        lines.append('')
        lines.append('    def test_create_multiple_records(self):')
        lines.append(f'        """Test batch creating multiple {model_name} records."""')
        lines.append(f'        records = self.env[{repr(model_name)}].create([')
        for i in range(1, 4):
            single_vals = {k: v.replace('Test Record', f'Batch Record {i}') if isinstance(v, str) and 'Test Record' in v else v
                          for k, v in required_vals.items()}
            if 'name' in self.parser.fields:
                single_vals['name'] = f"'Batch Record {i}'"
            lines.append(f'            {self._format_vals_dict(single_vals, indent=12)},')
        lines.append('        ])')
        lines.append('        self.assertEqual(len(records), 3)')
        lines.append('')

        # Footer
        lines.append('')
        lines.append('# ─── Run standalone (for quick debugging) ────────────────────────────────────')
        lines.append('# This file must be run via Odoo test runner, not directly with Python.')
        lines.append('# python -m odoo -c conf/project.conf -d db \\')
        lines.append(f'#     --test-enable --test-tags=/{self._make_module_name(self.parser.module_path)}:{class_name} \\')
        lines.append('#     --stop-after-init')

        return '\n'.join(lines)


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Generate Odoo test class skeleton for a model.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""
        Examples:
          python test_generator.py --model sale.order --module /c/odoo/odoo17/projects/myproject/my_module
          python test_generator.py --model my.model --module ./my_module --output ./tests/test_custom.py
          python test_generator.py --model hr.employee --module /path/to/module --dry-run
        """)
    )
    parser.add_argument('--model', required=True, help='Odoo model name (e.g., sale.order, my.model)')
    parser.add_argument('--module', required=True, help='Path to the Odoo module directory')
    parser.add_argument('--output', help='Output file path (default: module/tests/test_<model>.py)')
    parser.add_argument('--dry-run', action='store_true', help='Print generated code to stdout without writing')
    parser.add_argument('--force', action='store_true', help='Overwrite existing test file')

    args = parser.parse_args()

    module_path = Path(args.module).resolve()
    if not module_path.exists():
        print(f"[ERROR] Module path not found: {module_path}", file=sys.stderr)
        sys.exit(1)

    manifest = module_path / '__manifest__.py'
    if not manifest.exists():
        print(f"[WARN] No __manifest__.py found at {module_path}. Proceeding anyway.")

    print(f"[INFO] Parsing module: {module_path.name}")
    print(f"[INFO] Target model:   {args.model}")

    # Parse the model
    model_parser = OdooModelParser(module_path)
    model_file = model_parser.find_model_file(args.model)

    if model_file:
        print(f"[INFO] Model file:     {model_file.name}")
        model_parser.parse_file(model_file)
        model_parser.module_path = module_path
    else:
        print(f"[WARN] Model file not found for '{args.model}'. Generating generic skeleton.")
        model_parser.model_name = args.model
        model_parser.class_name = 'GenericModel'
        model_parser.module_path = module_path
        # Add a minimal 'name' field so the generated file is useful
        model_parser.fields['name'] = {'type': 'Char', 'required': True, 'compute': None, 'selection': None}
        model_parser.required_fields = ['name']

    # Generate test code
    generator = TestCodeGenerator(model_parser, args.model)
    code = generator.generate()

    if args.dry_run:
        print('\n' + '=' * 60)
        print('GENERATED TEST FILE:')
        print('=' * 60)
        print(code)
        return

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        test_dir = module_path / 'tests'
        model_slug = args.model.replace('.', '_')
        output_path = test_dir / f'test_{model_slug}.py'

    # Create tests/ directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create __init__.py if missing
    init_path = output_path.parent / '__init__.py'
    if not init_path.exists():
        module_slug = args.model.replace('.', '_')
        init_path.write_text(
            f'# Test package for {module_path.name}\n'
            f'from . import test_{module_slug}\n',
            encoding='utf-8'
        )
        print(f"[CREATE] {init_path}")

    # Check if output file already exists
    if output_path.exists() and not args.force:
        print(f"[ERROR] Output file already exists: {output_path}")
        print("        Use --force to overwrite.")
        sys.exit(1)

    output_path.write_text(code, encoding='utf-8')
    print(f"[OK] Test file generated: {output_path}")
    print()
    print("Next steps:")
    print(f"  1. Review and adjust fixtures in setUpClass()")
    print(f"  2. Add model-specific assertions")
    print(f"  3. Run: python -m odoo -c conf/project.conf -d db --test-enable -u {module_path.name} --stop-after-init")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Test Suite for Odoo Upgrade Syntax Validation and Fixes
Tests the validation and auto-fix functionality
"""

import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path
from datetime import datetime

# Import our modules
try:
    from syntax_validator import SyntaxValidator
    from auto_fix_library import AutoFixLibrary
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    print("Error: Required modules not found. Please ensure syntax_validator.py and auto_fix_library.py are available.")


class TestSyntaxValidation(unittest.TestCase):
    """Test suite for syntax validation functionality"""

    def setUp(self):
        """Set up test environment"""
        if not MODULES_AVAILABLE:
            self.skipTest("Required modules not available")

        # Create temporary directory for tests
        self.test_dir = tempfile.mkdtemp(prefix="odoo_test_")
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_test_file(self, filename, content):
        """Helper to create test files"""
        file_path = self.test_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path

    # ========== Python Validation Tests ==========

    def test_python_valid_syntax(self):
        """Test validation of valid Python syntax"""
        content = '''#!/usr/bin/env python3
from odoo import models, fields, api

class TestModel(models.Model):
    _name = 'test.model'
    _description = 'Test Model'

    name = fields.Char(string='Name', required=True)

    @api.depends('name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.name
'''
        self.create_test_file('models/test_model.py', content)

        validator = SyntaxValidator(self.test_path)
        results = validator.validate_all()

        self.assertTrue(results['valid'], "Valid Python should pass validation")
        self.assertEqual(results['stats']['python_errors'], 0)

    def test_python_syntax_error(self):
        """Test detection of Python syntax errors"""
        content = '''from odoo import models, fields

class TestModel(models.Model):
    _name = 'test.model'

    def test_method(self)  # Missing colon
        return True
'''
        self.create_test_file('models/bad_model.py', content)

        validator = SyntaxValidator(self.test_path)
        results = validator.validate_all()

        self.assertFalse(results['valid'], "Invalid Python should fail validation")
        self.assertGreater(results['stats']['python_errors'], 0)

    def test_python_deprecated_import(self):
        """Test detection of deprecated imports"""
        content = '''from openerp import models, fields

class OldModel(models.Model):
    _name = 'old.model'
'''
        file_path = self.create_test_file('models/old_model.py', content)

        validator = SyntaxValidator(self.test_path)
        is_valid, errors = validator.validate_python_file(file_path)

        self.assertFalse(is_valid, "Deprecated imports should be detected")
        self.assertTrue(any('openerp' in str(e) for e in errors))

    # ========== XML Validation Tests ==========

    def test_xml_valid_syntax(self):
        """Test validation of valid XML syntax"""
        content = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_test_form" model="ir.ui.view">
        <field name="name">test.model.form</field>
        <field name="model">test.model</field>
        <field name="arch" type="xml">
            <form string="Test">
                <field name="name"/>
            </form>
        </field>
    </record>
</odoo>
'''
        self.create_test_file('views/test_view.xml', content)

        validator = SyntaxValidator(self.test_path)
        results = validator.validate_all()

        self.assertTrue(results['valid'], "Valid XML should pass validation")
        self.assertEqual(results['stats']['xml_errors'], 0)

    def test_xml_malformed_comments(self):
        """Test detection of malformed XML comments"""
        content = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- This is a comment <!-- with nested comment --> -->
    <record id="test" model="ir.ui.view">
        <field name="name">test</field>
    </record>
</odoo>
'''
        file_path = self.create_test_file('views/bad_comment.xml', content)

        validator = SyntaxValidator(self.test_path)
        is_valid, errors = validator.validate_xml_file(file_path)

        self.assertFalse(is_valid, "Malformed comments should be detected")
        self.assertTrue(any('comment' in str(e).lower() for e in errors))

    def test_xml_odoo19_compatibility(self):
        """Test detection of Odoo 19 compatibility issues"""
        content = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_tree" model="ir.ui.view">
        <field name="arch" type="xml">
            <tree string="Test">
                <field name="name"/>
            </tree>
        </field>
    </record>
</odoo>
'''
        self.create_test_file('views/tree_view.xml', content)

        validator = SyntaxValidator(self.test_path)
        results = validator.validate_all()

        # Should have warnings about tree tags
        self.assertGreater(len(results['warnings'].get('xml', [])), 0)
        self.assertTrue(any('tree' in w and 'list' in w for w in results['warnings'].get('xml', [])))

    # ========== JavaScript Validation Tests ==========

    def test_javascript_valid_syntax(self):
        """Test validation of valid JavaScript syntax"""
        content = '''/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.TestWidget = publicWidget.Widget.extend({
    selector: '.test-widget',

    start: function () {
        this._super.apply(this, arguments);
        console.log('Widget started');
    },
});
'''
        self.create_test_file('static/src/js/test_widget.js', content)

        validator = SyntaxValidator(self.test_path)
        results = validator.validate_all()

        self.assertEqual(results['stats']['js_errors'], 0, "Valid JavaScript should pass")

    def test_javascript_missing_module_declaration(self):
        """Test detection of missing @odoo-module declaration"""
        content = '''import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.TestWidget = publicWidget.Widget.extend({
    selector: '.test-widget',
});
'''
        self.create_test_file('static/src/js/no_module.js', content)

        validator = SyntaxValidator(self.test_path)
        results = validator.validate_all()

        # Should have warning about missing module declaration
        self.assertGreater(len(results['warnings'].get('js', [])), 0)
        self.assertTrue(any('@odoo-module' in w for w in results['warnings'].get('js', [])))

    def test_javascript_unbalanced_brackets(self):
        """Test detection of unbalanced brackets"""
        content = '''/** @odoo-module **/

const testFunction = function() {
    if (true) {
        console.log('test');
    // Missing closing bracket
};
'''
        file_path = self.create_test_file('static/src/js/unbalanced.js', content)

        validator = SyntaxValidator(self.test_path)
        is_valid, errors = validator.validate_javascript_file(file_path)

        self.assertFalse(is_valid, "Unbalanced brackets should be detected")
        self.assertTrue(any('bracket' in str(e).lower() or 'unclosed' in str(e).lower() for e in errors))

    # ========== SCSS Validation Tests ==========

    def test_scss_valid_syntax(self):
        """Test validation of valid SCSS syntax"""
        content = '''.test-class {
    color: $o-color-1;
    font-size: 14px;

    &:hover {
        color: darken($o-color-1, 10%);
    }
}
'''
        self.create_test_file('static/src/scss/test.scss', content)

        validator = SyntaxValidator(self.test_path)
        results = validator.validate_all()

        self.assertEqual(results['stats']['scss_errors'], 0, "Valid SCSS should pass")

    def test_scss_unbalanced_braces(self):
        """Test detection of unbalanced braces in SCSS"""
        content = '''.test-class {
    color: red;
    .nested {
        font-size: 14px;
    /* Missing closing brace */
}
'''
        file_path = self.create_test_file('static/src/scss/bad.scss', content)

        validator = SyntaxValidator(self.test_path)
        is_valid, errors = validator.validate_scss_file(file_path)

        self.assertFalse(is_valid, "Unbalanced braces should be detected")
        self.assertTrue(any('brace' in str(e).lower() for e in errors))


class TestAutoFixes(unittest.TestCase):
    """Test suite for auto-fix functionality"""

    def setUp(self):
        """Set up test environment"""
        if not MODULES_AVAILABLE:
            self.skipTest("Required modules not available")

        self.test_dir = tempfile.mkdtemp(prefix="odoo_fix_test_")
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_test_file(self, filename, content):
        """Helper to create test files"""
        file_path = self.test_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path

    def test_fix_python_imports(self):
        """Test fixing Python imports"""
        content = '''from openerp import models, fields
import openerp.api as api

class TestModel(models.Model):
    _name = 'test.model'
'''
        file_path = self.create_test_file('models/test.py', content)

        fixer = AutoFixLibrary(self.test_path, backup=False)
        fixed_count = fixer.fix_python_imports()

        self.assertGreater(fixed_count, 0, "Should fix openerp imports")

        # Read fixed content
        with open(file_path, 'r') as f:
            fixed_content = f.read()

        self.assertIn('from odoo import', fixed_content)
        self.assertIn('import odoo', fixed_content)
        self.assertNotIn('from openerp', fixed_content)

    def test_fix_xml_comments(self):
        """Test fixing malformed XML comments"""
        content = '''<?xml version="1.0"?>
<odoo>
    <!-- Comment <!-- nested --> -->
    <!-- Comment with -- double hyphens -->
    <record id="test" model="test.model"/>
</odoo>
'''
        file_path = self.create_test_file('views/test.xml', content)

        fixer = AutoFixLibrary(self.test_path, backup=False)
        fixed_count = fixer.fix_xml_comments()

        self.assertGreater(fixed_count, 0, "Should fix XML comments")

        # Validate fixed XML
        validator = SyntaxValidator(self.test_path)
        is_valid, errors = validator.validate_xml_file(file_path)

        self.assertTrue(is_valid, "Fixed XML should be valid")

    def test_fix_xml_odoo19(self):
        """Test fixing Odoo 19 XML issues"""
        content = '''<?xml version="1.0"?>
<odoo>
    <record id="view" model="ir.ui.view">
        <field name="arch" type="xml">
            <tree string="Test" edit="1">
                <field name="name"/>
            </tree>
        </field>
    </record>

    <record id="action" model="ir.actions.act_window">
        <field name="view_mode">tree,form</field>
    </record>
</odoo>
'''
        file_path = self.create_test_file('views/tree.xml', content)

        fixer = AutoFixLibrary(self.test_path, backup=False)
        fixed_count = fixer.fix_xml_odoo19_compatibility()

        self.assertGreater(fixed_count, 0, "Should fix Odoo 19 issues")

        # Read fixed content
        with open(file_path, 'r') as f:
            fixed_content = f.read()

        self.assertIn('<list', fixed_content)
        self.assertIn('</list>', fixed_content)
        self.assertIn('view_mode">list', fixed_content)
        self.assertNotIn('edit="1"', fixed_content)

    def test_fix_javascript_rpc(self):
        """Test fixing JavaScript RPC service"""
        content = '''/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";

export class TestComponent {
    setup() {
        this.rpc = useService("rpc");
    }

    async loadData() {
        const result = await this.rpc("/api/data", {});
        return result;
    }
}
'''
        file_path = self.create_test_file('static/src/js/component.js', content)

        fixer = AutoFixLibrary(self.test_path, backup=False)
        fixed_count = fixer.fix_javascript_rpc()

        # Read fixed content
        with open(file_path, 'r') as f:
            fixed_content = f.read()

        self.assertIn('_jsonRpc', fixed_content, "Should add _jsonRpc method")
        self.assertNotIn('useService("rpc")', fixed_content)

    def test_fix_scss_variables(self):
        """Test fixing SCSS variables"""
        content = '''.test {
    font-weight: $headings-font-weight;
    font-size: $font-size-base;
}
'''
        file_path = self.create_test_file('static/src/scss/test.scss', content)

        fixer = AutoFixLibrary(self.test_path, backup=False)
        fixed_count = fixer.fix_scss_variables()

        self.assertGreater(fixed_count, 0, "Should fix SCSS variables")

        # Read fixed content
        with open(file_path, 'r') as f:
            fixed_content = f.read()

        self.assertIn('$o-theme-headings-font-weight', fixed_content)
        self.assertIn('$o-theme-font-size-base', fixed_content)


class TestIntegration(unittest.TestCase):
    """Integration tests for validation and fixes"""

    def setUp(self):
        """Set up test environment"""
        if not MODULES_AVAILABLE:
            self.skipTest("Required modules not available")

        self.test_dir = tempfile.mkdtemp(prefix="odoo_integration_test_")
        self.test_path = Path(self.test_dir)
        self.create_test_module()

    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_test_module(self):
        """Create a complete test module with various issues"""
        # Create manifest
        manifest_content = '''{
    'name': 'Test Module',
    'version': '17.0.1.0.0',
    'depends': ['base'],
    'data': ['views/test_views.xml'],
}'''
        self.create_test_file('__manifest__.py', manifest_content)

        # Create Python file with issues
        python_content = '''from openerp import models, fields

class TestModel(models.Model):
    _name = 'test.model'

    name = fields.Char()

    @api.depends('name')
    def compute_display(self):
        pass
'''
        self.create_test_file('models/test.py', python_content)

        # Create XML file with issues
        xml_content = '''<?xml version="1.0"?>
<odoo>
    <!-- Comment <!-- nested --> -->
    <record id="view" model="ir.ui.view">
        <field name="arch" type="xml">
            <tree string="Test">
                <field name="name"/>
            </tree>
        </field>
    </record>
</odoo>
'''
        self.create_test_file('views/test_views.xml', xml_content)

        # Create JavaScript file with issues
        js_content = '''import { useService } from "@web/core/utils/hooks";

export class TestWidget {
    setup() {
        this.rpc = useService("rpc");
    }
}
'''
        self.create_test_file('static/src/js/widget.js', js_content)

    def create_test_file(self, filename, content):
        """Helper to create test files"""
        file_path = self.test_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path

    def test_validate_fix_validate_workflow(self):
        """Test the complete workflow: validate -> fix -> validate"""
        # Initial validation
        validator = SyntaxValidator(self.test_path)
        initial_results = validator.validate_all()

        self.assertFalse(initial_results['valid'], "Initial module should have issues")
        initial_errors = initial_results['stats']['total_errors']

        # Apply fixes
        fixer = AutoFixLibrary(self.test_path, backup=False)
        fix_results = fixer.apply_all_fixes()

        self.assertGreater(fix_results['total_fixes'], 0, "Should apply some fixes")

        # Re-validate after fixes
        final_results = validator.validate_all()
        final_errors = final_results['stats']['total_errors']

        # Should have fewer errors after fixes
        self.assertLess(final_errors, initial_errors,
                       "Should have fewer errors after fixes")

    def test_backup_functionality(self):
        """Test backup creation during fixes"""
        fixer = AutoFixLibrary(self.test_path, backup=True)

        # Apply fixes with backup
        fixer.apply_all_fixes()

        # Check that backup was created
        self.assertIsNotNone(fixer.backup_path)
        self.assertTrue(fixer.backup_path.exists())

        # Verify backup contains original files
        backup_manifest = fixer.backup_path / '__manifest__.py'
        self.assertTrue(backup_manifest.exists())


def run_tests(verbose=False):
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSyntaxValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestAutoFixes))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)

    return result.wasSuccessful()


def main():
    """Main entry point"""
    if '--help' in sys.argv:
        print("Odoo Upgrade Syntax Validation Test Suite")
        print("\nUsage: python test_syntax_validation.py [options]")
        print("\nOptions:")
        print("  --verbose    Show detailed test output")
        print("  --help       Show this help message")
        print("\nThis script tests:")
        print("  - Python syntax validation")
        print("  - XML parsing and validation")
        print("  - JavaScript syntax checking")
        print("  - SCSS validation")
        print("  - Auto-fix functionality")
        print("  - Integration workflows")
        sys.exit(0)

    if not MODULES_AVAILABLE:
        print("Error: Required modules not available")
        print("Please ensure syntax_validator.py and auto_fix_library.py are in the same directory")
        sys.exit(1)

    verbose = '--verbose' in sys.argv

    print("=" * 60)
    print("ODOO UPGRADE SYNTAX VALIDATION TEST SUITE")
    print("=" * 60)
    print(f"Running tests...")
    print()

    success = run_tests(verbose)

    print()
    print("=" * 60)
    if success:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
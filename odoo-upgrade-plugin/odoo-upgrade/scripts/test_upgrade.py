#!/usr/bin/env python3
"""
Test script to verify Odoo 19 upgrade plugin functionality
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path


def create_test_project():
    """Create a test project with common Odoo 17/18 patterns"""
    test_dir = Path(tempfile.mkdtemp(prefix="odoo_test_"))

    # Create manifest with version issue
    manifest_dir = test_dir / "test_module"
    manifest_dir.mkdir()

    manifest_content = """
{
    'name': 'Test Module',
    'version': '1.0.0',
    'depends': ['base'],
    'external_dependencies': {
        'python': ['geopy', 'spacy'],
    },
    'data': [
        'views/test_views.xml',
    ],
}
"""
    (manifest_dir / "__manifest__.py").write_text(manifest_content)

    # Create XML with all issues
    views_dir = manifest_dir / "views"
    views_dir.mkdir()

    xml_content = """<?xml version="1.0" encoding="UTF-8" ?>
<odoo>
    <!-- Test tree view -->
    <record id="test_tree" model="ir.ui.view">
        <field name="arch" type="xml">
            <tree string="Test">
                <field name="name"/>
            </tree>
        </field>
    </record>

    <!-- Test search view with group -->
    <record id="test_search" model="ir.ui.view">
        <field name="arch" type="xml">
            <search>
                <field name="name"/>
                <group>
                    <filter name="filter1"/>
                </group>
            </search>
        </field>
    </record>

    <!-- Test kanban -->
    <record id="test_kanban" model="ir.ui.view">
        <field name="arch" type="xml">
            <kanban js_class="crm_kanban">
                <templates>
                    <t t-name="kanban-box">
                        <div>Test</div>
                    </t>
                </templates>
            </kanban>
        </field>
    </record>

    <!-- Test action -->
    <record id="test_action" model="ir.actions.act_window">
        <field name="view_mode">tree,form</field>
    </record>

    <!-- Test cron -->
    <record id="test_cron" model="ir.cron">
        <field name="numbercall">-1</field>
    </record>

    <!-- Test website.snippet_options inheritance -->
    <template id="test_snippet" inherit_id="website.snippet_options">
        <xpath expr="//div" position="inside">
            <we-button title="Test"/>
        </xpath>
    </template>
</odoo>"""

    (views_dir / "test_views.xml").write_text(xml_content)

    # Create Python file with issues
    models_dir = manifest_dir / "models"
    models_dir.mkdir()

    py_content = """
from odoo import models, fields
from odoo.addons.http_routing.models.ir_http import slug, url_for

class TestModel(models.Model):
    _name = 'test.model'

    name = fields.Char()

    def get_slug(self):
        return slug(self)
"""

    (models_dir / "test_model.py").write_text(py_content)

    # Create JavaScript with RPC issue
    js_dir = manifest_dir / "static" / "src" / "js"
    js_dir.mkdir(parents=True)

    js_content = """
/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class TestComponent extends Component {
    setup() {
        this.rpc = useService("rpc");
    }

    async loadData() {
        const data = await this.rpc("/my/endpoint", {param: 1});
    }
}
"""

    (js_dir / "test.js").write_text(js_content)

    print(f"Created test project at: {test_dir}")
    return test_dir


def run_tests():
    """Run upgrade tests"""
    print("=" * 60)
    print("ODOO 19 UPGRADE PLUGIN TEST")
    print("=" * 60)

    # Create test project
    test_dir = create_test_project()

    try:
        # Test pre-check
        print("\n1. Testing pre-check script...")
        precheck_script = Path(__file__).parent / "odoo19_precheck.py"
        if precheck_script.exists():
            os.system(f'python "{precheck_script}" "{test_dir}"')
        else:
            print(f"   [ERROR] Pre-check script not found: {precheck_script}")

        # Test upgrade
        print("\n2. Testing upgrade script...")
        upgrade_script = Path(__file__).parent / "upgrade_to_odoo19.py"
        if upgrade_script.exists():
            os.system(f'python "{upgrade_script}" "{test_dir}"')
        else:
            print(f"   [ERROR] Upgrade script not found: {upgrade_script}")

        # Verify fixes
        print("\n3. Verifying fixes...")

        # Check manifest
        manifest_path = test_dir / "test_module" / "__manifest__.py"
        manifest_content = manifest_path.read_text()

        if "'version': '19.0." in manifest_content:
            print("   ✓ Version updated correctly")
        else:
            print("   ✗ Version not updated")

        if "'license':" in manifest_content:
            print("   ✓ License added")
        else:
            print("   ✗ License not added")

        # Check XML
        xml_path = test_dir / "test_module" / "views" / "test_views.xml"
        xml_content = xml_path.read_text()

        if "<list" in xml_content and "<tree" not in xml_content:
            print("   ✓ Tree views converted to list")
        else:
            print("   ✗ Tree views not converted")

        if "t-name=\"card\"" in xml_content:
            print("   ✓ Kanban template updated")
        else:
            print("   ✗ Kanban template not updated")

        if "js_class=\"crm_kanban\"" not in xml_content:
            print("   ✓ js_class removed")
        else:
            print("   ✗ js_class not removed")

        if "numbercall" not in xml_content:
            print("   ✓ numbercall removed")
        else:
            print("   ✗ numbercall not removed")

        if "<!-- website.snippet_options" in xml_content or "<!--" in xml_content:
            print("   ✓ website.snippet_options commented out")
        else:
            print("   ✗ website.snippet_options not handled")

        # Check Python
        py_path = test_dir / "test_module" / "models" / "test_model.py"
        if py_path.exists():
            py_content = py_path.read_text()

            if "from odoo.addons.http_routing.models.ir_http import slug" not in py_content:
                print("   ✓ Old imports removed")
            else:
                print("   ✗ Old imports not removed")

        # Check JavaScript
        js_path = test_dir / "test_module" / "static" / "src" / "js" / "test.js"
        if js_path.exists():
            js_content = js_path.read_text()

            if "this._jsonRpc" in js_content and "this.rpc = useService" not in js_content:
                print("   ✓ RPC migrated")
            else:
                print("   ✗ RPC not migrated")

        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)

    finally:
        # Cleanup
        print(f"\nCleaning up test directory: {test_dir}")
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    run_tests()
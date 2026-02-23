#!/usr/bin/env python3
"""
Odoo 19 Pre-upgrade Check Script
Scans project for potential Odoo 19 compatibility issues before upgrade
"""

import os
import re
from pathlib import Path
from collections import defaultdict


class Odoo19PreChecker:
    """Pre-check for Odoo 19 compatibility issues"""

    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.issues = defaultdict(list)
        self.stats = {
            'xml_files': 0,
            'py_files': 0,
            'js_files': 0,
            'critical_issues': 0,
            'high_issues': 0,
            'medium_issues': 0,
            'low_issues': 0
        }

    def check_xml_files(self):
        """Check XML files for compatibility issues"""
        xml_files = list(self.project_path.glob("**/*.xml"))
        self.stats['xml_files'] = len(xml_files)

        for xml_file in xml_files:
            try:
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                rel_path = xml_file.relative_to(self.project_path)

                # CRITICAL: Check for tree views
                if '<tree' in content:
                    count = len(re.findall(r'<tree[\s>]', content))
                    self.issues['critical'].append(
                        f"{rel_path}: Found {count} <tree> view tag(s) - must be changed to <list>"
                    )
                    self.stats['critical_issues'] += 1

                # CRITICAL: Check for search view groups
                if re.search(r'<search[^>]*>.*?<group[^>]*>.*?</group>.*?</search>', content, re.DOTALL):
                    self.issues['critical'].append(
                        f"{rel_path}: Found <group> tag inside <search> view - not allowed in Odoo 19"
                    )
                    self.stats['critical_issues'] += 1

                # CRITICAL: Check for tree in view_mode
                if re.search(r'<field\s+name=["\']view_mode["\'][^>]*>.*?tree', content):
                    count = len(re.findall(r'view_mode["\'][^>]*>.*?tree', content))
                    self.issues['critical'].append(
                        f"{rel_path}: Found {count} act_window with 'tree' in view_mode - must be 'list'"
                    )
                    self.stats['critical_issues'] += 1

                # CRITICAL: Check for XPath expressions with //tree
                if re.search(r'xpath[^>]*expr=["\']//tree', content):
                    count = len(re.findall(r'xpath[^>]*expr=["\']//tree', content))
                    self.issues['critical'].append(
                        f"{rel_path}: Found {count} xpath expression(s) with '//tree' - must be '//list' in Odoo 19"
                    )
                    self.stats['critical_issues'] += 1

                # HIGH: Check for group expand attribute in search views
                if re.search(r'<group[^>]*expand=["\'][01]["\']', content):
                    count = len(re.findall(r'<group[^>]*expand=["\'][01]["\']', content))
                    self.issues['high'].append(
                        f"{rel_path}: Found {count} search view group(s) with 'expand' attribute - deprecated in Odoo 19"
                    )
                    self.stats['high_issues'] += 1

                # HIGH: Check for numbercall in cron
                if 'name="numbercall"' in content:
                    self.issues['high'].append(
                        f"{rel_path}: Found 'numbercall' field in cron job - field removed in Odoo 19"
                    )
                    self.stats['high_issues'] += 1

                # HIGH: Check for js_class="crm_kanban"
                if 'js_class="crm_kanban"' in content:
                    self.issues['high'].append(
                        f"{rel_path}: Found js_class='crm_kanban' - not available outside CRM module"
                    )
                    self.stats['high_issues'] += 1

                # CRITICAL: Check for website.snippet_options inheritance
                if 'inherit_id="website.snippet_options"' in content:
                    self.issues['critical'].append(
                        f"{rel_path}: Found inheritance from website.snippet_options - removed in Odoo 19"
                    )
                    self.stats['critical_issues'] += 1

                # HIGH: Check for attrs= attribute (deprecated in Odoo 17, removed in 19)
                if re.search(r'\battrs\s*=\s*["\']', content):
                    count = len(re.findall(r'\battrs\s*=\s*["\']', content))
                    self.issues['high'].append(
                        f"{rel_path}: Found {count} attrs='...' attribute(s) - must be converted to inline invisible/required/readonly in Odoo 17+"
                    )
                    self.stats['high_issues'] += 1

                # MEDIUM: Check for kanban-box template
                if 't-name="kanban-box"' in content:
                    self.issues['medium'].append(
                        f"{rel_path}: Found kanban-box template - should be 't-name=\"card\"' in Odoo 19"
                    )
                    self.stats['medium_issues'] += 1

                # LOW: Check for active_id in context
                if re.search(r'context=.*active_id', content):
                    self.issues['low'].append(
                        f"{rel_path}: Found 'active_id' in context - may need to be changed to 'id'"
                    )
                    self.stats['low_issues'] += 1

                # LOW: Check for edit="1"
                if 'edit="1"' in content:
                    self.issues['low'].append(
                        f"{rel_path}: Found edit='1' attribute - deprecated in newer versions"
                    )
                    self.stats['low_issues'] += 1

                # CRITICAL: Check for malformed XML comments
                if re.search(r'<!--[^>]*<!--', content) or re.search(r'-->[^<]*-->', content):
                    self.issues['critical'].append(
                        f"{rel_path}: Found malformed XML comments (nested/duplicate comment markers)"
                    )
                    self.stats['critical_issues'] += 1

                # CRITICAL: Check for double hyphens within comments
                comments = re.findall(r'<!--.*?-->', content, re.DOTALL)
                for comment in comments:
                    inner = comment[4:-3]  # Extract content between <!-- and -->
                    if '--' in inner:
                        self.issues['critical'].append(
                            f"{rel_path}: Found double hyphens within XML comment - will cause parsing errors"
                        )
                        self.stats['critical_issues'] += 1
                        break

            except Exception as e:
                print(f"Error checking {xml_file}: {e}")

        # Check manifests for cross-module asset references
        manifest_files = list(self.project_path.glob("**/__manifest__.py"))
        for manifest in manifest_files:
            try:
                with open(manifest, 'r', encoding='utf-8') as f:
                    content = f.read()

                rel_path = manifest.relative_to(self.project_path)
                module_name = manifest.parent.name

                # Check for references to other modules' assets
                asset_refs = re.findall(r"'([^'/]+)/static/[^']+'\s*,", content)
                for ref_module in asset_refs:
                    if ref_module != module_name and ref_module != 'web':
                        self.issues['high'].append(
                            f"{rel_path}: References assets from module '{ref_module}' - may cause dependency issues"
                        )
                        self.stats['high_issues'] += 1

            except Exception as e:
                print(f"Error checking {manifest}: {e}")

    def check_python_dependencies(self):
        """Check for Python dependencies in manifests"""
        dependencies = set()
        manifest_files = list(self.project_path.glob("**/__manifest__.py"))

        for manifest in manifest_files:
            try:
                with open(manifest, 'r', encoding='utf-8') as f:
                    content = f.read()

                rel_path = manifest.relative_to(self.project_path)

                # Find external_dependencies section
                match = re.search(r"'external_dependencies'\s*:\s*\{[^}]*'python'\s*:\s*\[([^\]]+)\]", content, re.DOTALL)
                if match:
                    deps_str = match.group(1)
                    # Extract individual dependencies
                    deps = re.findall(r"'([^']+)'", deps_str)
                    dependencies.update(deps)

            except Exception as e:
                print(f"Error checking {manifest}: {e}")

        if dependencies:
            self.issues['high'].append(
                f"Python dependencies required: {', '.join(dependencies)} - Install with: pip install {' '.join(dependencies)}"
            )
            self.stats['high_issues'] += 1

    def check_python_files(self):
        """Check Python files for compatibility issues"""
        py_files = list(self.project_path.glob("**/*.py"))
        self.stats['py_files'] = len(py_files)

        for py_file in py_files:
            if '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                rel_path = py_file.relative_to(self.project_path)

                # HIGH: Check for old slug/unslug imports
                if 'from odoo.addons.http_routing.models.ir_http import' in content:
                    if 'slug' in content or 'unslug' in content:
                        self.issues['high'].append(
                            f"{rel_path}: Found old slug/unslug import - location changed in Odoo 18+"
                        )
                        self.stats['high_issues'] += 1

                # HIGH: Check for url_for import
                if 'from odoo.addons.http_routing.models.ir_http import url_for' in content:
                    self.issues['high'].append(
                        f"{rel_path}: Found url_for import - use self.env['ir.http']._url_for() instead"
                    )
                    self.stats['high_issues'] += 1

                # CRITICAL: Check for view_mode with 'tree' in Python dictionaries
                if re.search(r"['\"]view_mode['\"]:\s*['\"].*?tree", content):
                    count = len(re.findall(r"['\"]view_mode['\"]:\s*['\"].*?tree", content))
                    self.issues['critical'].append(
                        f"{rel_path}: Found {count} Python dictionary/dictionaries with 'view_mode': 'tree' - must be 'list' in Odoo 19"
                    )
                    self.stats['critical_issues'] += 1

                # CRITICAL: Check for type='json' in @http.route (must be 'jsonrpc' in Odoo 19)
                if re.search(r"@http\.route\([^)]*type\s*=\s*['\"]json['\"]", content):
                    count = len(re.findall(r"@http\.route\([^)]*type\s*=\s*['\"]json['\"]", content))
                    self.issues['critical'].append(
                        f"{rel_path}: Found {count} @http.route with type='json' - must be type='jsonrpc' in Odoo 19"
                    )
                    self.stats['critical_issues'] += 1

                # HIGH: Check for OWL 1.x lifecycle hooks
                owl_hooks = ['mounted()', 'willStart()', 'patched()', 'willUnmount()', 'willUpdateProps()']
                for hook in owl_hooks:
                    if hook in content and 'Component' in content:
                        self.issues['high'].append(
                            f"{rel_path}: OWL 1.x lifecycle hook '{hook}' found - rename to 'on{hook[0].upper()}{hook[1:]}' for OWL 2.0"
                        )
                        self.stats['high_issues'] += 1

                # MEDIUM: Check for view_type parameter (deprecated)
                if re.search(r"['\"]view_type['\"]:\s*['\"]tree['\"]", content):
                    self.issues['medium'].append(
                        f"{rel_path}: Found 'view_type': 'tree' - parameter deprecated, use 'view_mode': 'list'"
                    )
                    self.stats['medium_issues'] += 1

                # Check for version in manifest
                if '__manifest__.py' in str(py_file):
                    if not re.search(r"'version':\s*'19\.0", content):
                        self.issues['medium'].append(
                            f"{rel_path}: Manifest version not set to 19.0.x.x.x format"
                        )
                        self.stats['medium_issues'] += 1

                    if "'license'" not in content:
                        self.issues['low'].append(
                            f"{rel_path}: Missing 'license' key in manifest"
                        )
                        self.stats['low_issues'] += 1

            except Exception as e:
                print(f"Error checking {py_file}: {e}")

    def check_javascript_files(self):
        """Check JavaScript files for compatibility issues"""
        js_files = list(self.project_path.glob("**/*.js"))
        self.stats['js_files'] = len(js_files)

        for js_file in js_files:
            if 'node_modules' in str(js_file) or '.min.js' in str(js_file):
                continue

            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                rel_path = js_file.relative_to(self.project_path)

                # CRITICAL: Check for RPC service usage in frontend
                if 'useService("rpc")' in content or "useService('rpc')" in content:
                    self.issues['critical'].append(
                        f"{rel_path}: Found RPC service usage - not available in Odoo 19 frontend"
                    )
                    self.stats['critical_issues'] += 1

                # Check if _jsonRpc helper is missing
                if 'this.rpc(' in content and '_jsonRpc' not in content:
                    self.issues['high'].append(
                        f"{rel_path}: Uses this.rpc() but missing _jsonRpc helper method"
                    )
                    self.stats['high_issues'] += 1

            except Exception as e:
                print(f"Error checking {js_file}: {e}")

    def generate_report(self):
        """Generate pre-check report"""
        print("\n" + "=" * 70)
        print("ODOO 19 COMPATIBILITY PRE-CHECK REPORT")
        print("=" * 70)
        print(f"\nProject: {self.project_path}")
        print(f"Files scanned: {self.stats['xml_files']} XML, {self.stats['py_files']} Python, {self.stats['js_files']} JavaScript")

        print("\n" + "-" * 70)
        print("ISSUE SUMMARY")
        print("-" * 70)

        total_issues = (self.stats['critical_issues'] + self.stats['high_issues'] +
                       self.stats['medium_issues'] + self.stats['low_issues'])

        if total_issues == 0:
            print("[SUCCESS] No compatibility issues found! Project is ready for Odoo 19.")
            return True

        print(f"Total issues found: {total_issues}")
        print(f"  [CRITICAL] {self.stats['critical_issues']} - Will cause installation/runtime failures")
        print(f"  [HIGH]     {self.stats['high_issues']} - Will likely cause errors")
        print(f"  [MEDIUM]   {self.stats['medium_issues']} - Should be fixed for compatibility")
        print(f"  [LOW]      {self.stats['low_issues']} - Minor issues, optional fixes")

        # Detailed issues
        if self.issues['critical']:
            print("\n" + "=" * 70)
            print("[CRITICAL] ISSUES - Must fix before upgrade:")
            print("=" * 70)
            for issue in self.issues['critical']:
                print(f"  - {issue}")

        if self.issues['high']:
            print("\n" + "-" * 70)
            print("[HIGH] ISSUES - Should fix to prevent errors:")
            print("-" * 70)
            for issue in self.issues['high']:
                print(f"  - {issue}")

        if self.issues['medium']:
            print("\n" + "-" * 70)
            print("[MEDIUM] ISSUES - Recommended fixes:")
            print("-" * 70)
            for issue in self.issues['medium'][:5]:  # Show first 5
                print(f"  - {issue}")
            if len(self.issues['medium']) > 5:
                print(f"  ... and {len(self.issues['medium']) - 5} more")

        if self.issues['low']:
            print("\n" + "-" * 70)
            print("[LOW] ISSUES - Optional improvements:")
            print("-" * 70)
            for issue in self.issues['low'][:3]:  # Show first 3
                print(f"  - {issue}")
            if len(self.issues['low']) > 3:
                print(f"  ... and {len(self.issues['low']) - 3} more")

        print("\n" + "=" * 70)
        print("RECOMMENDATIONS")
        print("=" * 70)

        if self.stats['critical_issues'] > 0:
            print("\n[!] CRITICAL issues detected. Run the upgrade script to fix automatically:")
            print("    python upgrade_to_odoo19.py " + str(self.project_path))
        else:
            print("\n[OK] No critical issues. You can proceed with the upgrade.")

        return self.stats['critical_issues'] == 0

    def run(self):
        """Run all checks"""
        print("\nRunning Odoo 19 compatibility pre-check...")
        print("-" * 40)

        print("Checking Python dependencies...")
        self.check_python_dependencies()

        print("Checking XML files...")
        self.check_xml_files()

        print("Checking Python files...")
        self.check_python_files()

        print("Checking JavaScript files...")
        self.check_javascript_files()

        return self.generate_report()


def main():
    """Main entry point"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python odoo19_precheck.py <project_path>")
        print("\nThis script checks for Odoo 19 compatibility issues without modifying files.")
        sys.exit(1)

    project_path = sys.argv[1]

    if not os.path.exists(project_path):
        print(f"Error: Path '{project_path}' does not exist")
        sys.exit(1)

    checker = Odoo19PreChecker(project_path)
    is_ready = checker.run()

    sys.exit(0 if is_ready else 1)


if __name__ == "__main__":
    main()
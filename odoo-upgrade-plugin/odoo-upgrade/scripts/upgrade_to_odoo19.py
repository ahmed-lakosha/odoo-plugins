#!/usr/bin/env python3
"""
Comprehensive Odoo 17/18 to Odoo 19 Upgrade Script
Handles all major compatibility issues automatically
Enhanced with syntax validation and auto-fix capabilities
"""

import os
import re
import sys
import glob
import shutil
from pathlib import Path
from datetime import datetime

# Import our new validation and fix modules
try:
    from syntax_validator import SyntaxValidator
    from auto_fix_library import AutoFixLibrary
    ENHANCED_MODE = True
except ImportError:
    ENHANCED_MODE = False
    print("Warning: Enhanced validation not available. Install syntax_validator.py and auto_fix_library.py")


class Odoo19Upgrader:
    """Main upgrader class for Odoo 19 migration"""

    def __init__(self, project_path, enable_validation=True, auto_fix=False):
        self.project_path = Path(project_path)
        self.backup_path = None
        self.report = []
        self.errors = []
        self.enable_validation = enable_validation and ENHANCED_MODE
        self.auto_fix = auto_fix
        self.pre_validation_results = None
        self.post_validation_results = None

    def create_backup(self):
        """Create backup of the project"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.project_path.name}_backup_{timestamp}"
        self.backup_path = self.project_path.parent / backup_name

        print(f"Creating backup at: {self.backup_path}")
        shutil.copytree(self.project_path, self.backup_path)
        self.report.append(f"[OK] Backup created: {self.backup_path}")
        return self.backup_path

    def update_manifest_files(self):
        """Update all __manifest__.py files for Odoo 19"""
        manifest_files = self.project_path.glob("**/__manifest__.py")
        updated = 0

        for manifest in manifest_files:
            try:
                with open(manifest, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Fix version format - extract numeric version and format properly
                def fix_version(match):
                    version = match.group(1)
                    # Remove any existing 19.0. prefix if duplicated
                    version = re.sub(r'^19\.0\.', '', version)
                    # Extract just the numeric parts
                    parts = re.findall(r'\d+', version)
                    if len(parts) < 3:
                        parts.extend(['0'] * (3 - len(parts)))
                    return f"'version': '19.0.{'.'.join(parts[:3])}'"

                content = re.sub(
                    r"'version'\s*:\s*['\"]([^'\"]+)['\"]",
                    fix_version,
                    content
                )

                # Add license if missing
                if "'license'" not in content:
                    # Add after version
                    content = re.sub(
                        r"('version'\s*:\s*[^,]+,)",
                        r"\1\n    'license': 'LGPL-3',",
                        content
                    )

                if content != original:
                    with open(manifest, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated += 1
                    print(f"  [OK] Updated: {manifest.name}")

            except Exception as e:
                self.errors.append((str(manifest), str(e)))
                print(f"  [ERROR] Error updating {manifest}: {e}")

        self.report.append(f"[OK] Updated {updated} manifest files")
        return updated

    def fix_xml_views(self):
        """Fix all XML view issues for Odoo 19"""
        xml_files = list(self.project_path.glob("**/*.xml"))
        fixed = 0

        for xml_file in xml_files:
            try:
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # First, fix any existing malformed comments (from previous runs)
                content = self._fix_malformed_comments(content)

                # 1. Convert tree to list views
                content = re.sub(r'<tree(\s+[^>]*)?>', r'<list\1>', content)
                content = content.replace('</tree>', '</list>')

                # 2. Fix search views - remove group tags
                content = self._fix_search_views(content)

                # 3. Fix kanban templates
                content = content.replace('t-name="kanban-box"', 't-name="card"')

                # Remove js_class="crm_kanban" as it's not available outside CRM
                content = re.sub(r'\s+js_class=["\']crm_kanban["\']', '', content)

                # 4. Remove numbercall from cron jobs
                content = re.sub(
                    r'\s*<field\s+name="numbercall"[^>]*>.*?</field>',
                    '',
                    content,
                    flags=re.DOTALL
                )
                content = re.sub(
                    r'\s*<field\s+name="numbercall"[^/]*/>',
                    '',
                    content
                )

                # 5. Fix active_id references
                content = re.sub(
                    r"context=['\"]([^'\"]*?)active_id([^'\"]*?)['\"]",
                    r"context='\1id\2'",
                    content
                )

                # 6. Remove edit="1" from views
                content = re.sub(r'\s+edit=["\']1["\']', '', content)

                # 7. Remove website.snippet_options inheritance (doesn't exist in Odoo 19)
                # Comment out instead of removing to preserve the code
                if 'inherit_id="website.snippet_options"' in content:
                    # Find and comment out the entire template
                    pattern = r'(<template[^>]*inherit_id="website\.snippet_options"[^>]*>.*?</template>)'
                    def comment_template(match):
                        template_content = match.group(1)
                        # Escape any existing double hyphens in the content to avoid XML comment errors
                        template_content = template_content.replace('--', '- -')
                        return f'''<!-- website.snippet_options removed in Odoo 19 - The snippet system has been redesigned
       This template has been disabled
  {template_content}
  -->'''
                    content = re.sub(pattern, comment_template, content, flags=re.DOTALL)

                # 8. Fix view_mode in act_window actions
                # Replace standalone 'tree'
                content = re.sub(
                    r'(<field name="view_mode">)tree(</field>)',
                    r'\1list\2',
                    content
                )
                # Replace 'tree,' with 'list,'
                content = re.sub(
                    r'(<field name="view_mode">)tree,',
                    r'\1list,',
                    content
                )
                # Replace ',tree' with ',list'
                content = re.sub(
                    r',tree([,<])',
                    r',list\1',
                    content
                )
                # Fix view_mode in view_ids
                content = re.sub(
                    r"'view_mode':\s*'tree'",
                    r"'view_mode': 'list'",
                    content
                )

                # 9. Fix XPath expressions with //tree
                # Fix xpath with double quotes
                content = re.sub(
                    r'(xpath[^>]*expr=")//tree',
                    r'\1//list',
                    content
                )
                # Fix xpath with single quotes
                content = re.sub(
                    r"(xpath[^>]*expr=')//tree",
                    r"\1//list",
                    content
                )

                # 10. Remove expand attribute from search view groups (deprecated)
                # Remove expand="0"
                content = re.sub(
                    r'(<group[^>]*)\s+expand="0"',
                    r'\1',
                    content
                )
                # Remove expand="1"
                content = re.sub(
                    r'(<group[^>]*)\s+expand="1"',
                    r'\1',
                    content
                )
                # Also handle with single quotes
                content = re.sub(
                    r"(<group[^>]*)\s+expand='[01]'",
                    r'\1',
                    content
                )

                if content != original:
                    with open(xml_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed += 1
                    print(f"  [OK] Fixed: {xml_file.name}")

            except Exception as e:
                self.errors.append((str(xml_file), str(e)))
                print(f"  [ERROR] Error fixing {xml_file}: {e}")

        self.report.append(f"[OK] Fixed {fixed} XML files")
        return fixed

    def _fix_malformed_comments(self, content):
        """Fix malformed XML comments from previous runs"""
        # Fix nested/duplicated comment starts
        pattern = r'<!--[^>]*<!--'
        while re.search(pattern, content):
            content = re.sub(pattern, '<!-- ', content)

        # Fix nested/duplicated comment ends
        pattern = r'-->[^<]*-->'
        while re.search(pattern, content):
            content = re.sub(pattern, ' -->', content)

        # Fix double hyphens within comments (except at boundaries)
        def fix_comment_hyphens(match):
            comment = match.group(0)
            # Replace internal double hyphens
            inner = comment[4:-3]  # Extract content between <!-- and -->
            inner = re.sub(r'--+', '- -', inner)
            return f'<!--{inner}-->'

        content = re.sub(r'<!--.*?-->', fix_comment_hyphens, content, flags=re.DOTALL)

        return content

    def _fix_search_views(self, content):
        """Remove group tags from search views"""
        pattern = r'(<search[^>]*>)(.*?)(</search>)'

        def remove_groups(match):
            search_start = match.group(1)
            search_content = match.group(2)
            search_end = match.group(3)

            # Remove group tags
            search_content = re.sub(r'<group[^>]*>', '', search_content)
            search_content = search_content.replace('</group>', '')

            # Add separator before group_by filters
            if 'group_by' in search_content and '<separator/>' not in search_content:
                search_content = re.sub(
                    r'(\s*)(<filter[^>]*group_by[^>]*>)',
                    r'\1<separator/>\1\2',
                    search_content,
                    count=1
                )

            return search_start + search_content + search_end

        return re.sub(pattern, remove_groups, content, flags=re.DOTALL)

    def update_python_code(self):
        """Update Python code for Odoo 19 compatibility"""
        py_files = list(self.project_path.glob("**/*.py"))
        updated = 0

        for py_file in py_files:
            if '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Remove slug/unslug imports from old location
                content = re.sub(
                    r'from\s+odoo\.addons\.http_routing\.models\.ir_http\s+import\s+[^,\n]*slug[^,\n]*,?\s*[^,\n]*unslug[^,\n]*,?\s*',
                    '',
                    content
                )

                # Replace url_for usage
                content = re.sub(
                    r'from\s+odoo\.addons\.http_routing\.models\.ir_http\s+import\s+url_for',
                    '',
                    content
                )
                content = re.sub(
                    r'\burl_for\(',
                    r"self.env['ir.http']._url_for(",
                    content
                )

                # Fix view_mode with 'tree' in Python dictionaries
                # Fix standalone 'tree'
                content = re.sub(
                    r"(['\"]view_mode['\"]:\s*['\"])tree(['\"])",
                    r"\1list\2",
                    content
                )
                # Fix 'tree,' at start
                content = re.sub(
                    r"(['\"]view_mode['\"]:\s*['\"])tree,",
                    r"\1list,",
                    content
                )
                # Fix ',tree' in middle or end
                content = re.sub(
                    r",tree([,'\"])",
                    r",list\1",
                    content
                )
                # Fix view_type parameter (deprecated but may exist)
                content = re.sub(
                    r"(['\"]view_type['\"]:\s*['\"])tree(['\"])",
                    r"\1list\2",
                    content
                )

                if content != original:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated += 1
                    print(f"  [OK] Updated: {py_file.name}")

            except Exception as e:
                self.errors.append((str(py_file), str(e)))
                print(f"  [ERROR] Error updating {py_file}: {e}")

        self.report.append(f"[OK] Updated {updated} Python files")
        return updated

    def migrate_javascript_rpc(self):
        """Migrate JavaScript RPC service to fetch API"""
        js_files = list(self.project_path.glob("**/*.js"))
        migrated = 0

        json_rpc_method = '''
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

        # Helper function for services that use jsonrpc directly
        jsonrpc_function = '''
// JSON-RPC helper function for Odoo 19 (replaces rpc service)
async function jsonrpc(endpoint, params = {}) {
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

        for js_file in js_files:
            if 'node_modules' in str(js_file) or '.min.js' in str(js_file):
                continue

            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Remove import of jsonrpc from RPC service
                if 'import {jsonrpc} from "@web/core/network/rpc_service"' in content:
                    content = content.replace('import {jsonrpc} from "@web/core/network/rpc_service";', '')
                    # Add the jsonrpc function after imports
                    import_end = content.find('const ')
                    if import_end == -1:
                        import_end = content.find('export ')
                    if import_end > 0:
                        content = content[:import_end] + '\n' + jsonrpc_function + '\n' + content[import_end:]

                # Remove RPC service usage
                content = re.sub(
                    r'this\.rpc\s*=\s*useService\(["\']rpc["\']\);?\s*\n?',
                    '',
                    content
                )

                # Replace this.rpc calls
                content = content.replace('this.rpc(', 'this._jsonRpc(')

                # Add _jsonRpc method if needed for components
                if 'this._jsonRpc(' in content and '_jsonRpc(endpoint, params' not in content:
                    # Check if this is inside a component class setup
                    if 'setup()' in content:
                        # Find the end of setup() method
                        setup_match = re.search(r'setup\(\)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', content)
                        if setup_match:
                            # Add the method as a class method after setup
                            setup_end = setup_match.end()
                            content = content[:setup_end] + '\n' + json_rpc_method + '\n' + content[setup_end:]

                if content != original:
                    with open(js_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    migrated += 1
                    print(f"  [OK] Migrated: {js_file.name}")

            except Exception as e:
                self.errors.append((str(js_file), str(e)))
                print(f"  [ERROR] Error migrating {js_file}: {e}")

        self.report.append(f"[OK] Migrated {migrated} JavaScript files")
        return migrated

    def update_scss_files(self):
        """Update SCSS files for Odoo 19 compatibility"""
        scss_files = list(self.project_path.glob("**/*.scss"))
        updated = 0

        for scss_file in scss_files:
            if 'node_modules' in str(scss_file):
                continue

            try:
                with open(scss_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Fix headings font weight variable
                content = re.sub(
                    r'\$headings-font-weight:',
                    '$o-theme-headings-font-weight:',
                    content
                )

                # Add menu/footer/copyright to color palettes if missing
                if 'o-color-palettes' in content and "'menu':" not in content:
                    content = re.sub(
                        r"('o-color-5':\s*[^,]+,?)(\s*\))",
                        r"\1,\2        'menu': 4,\2        'footer': 1,\2        'copyright': 5,\2",
                        content
                    )

                if content != original:
                    with open(scss_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated += 1
                    print(f"  [OK] Updated: {scss_file.name}")

            except Exception as e:
                self.errors.append((str(scss_file), str(e)))
                print(f"  [ERROR] Error updating {scss_file}: {e}")

        self.report.append(f"[OK] Updated {updated} SCSS files")
        return updated

    def generate_report(self):
        """Generate migration report"""
        report_path = self.project_path / "MIGRATION_REPORT_ODOO19.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Odoo 19 Migration Report\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"**Project**: {self.project_path.name}\n\n")

            f.write("## Summary\n\n")
            for item in self.report:
                f.write(f"- {item}\n")

            if self.errors:
                f.write("\n## Errors\n\n")
                for file, error in self.errors:
                    f.write(f"- **{file}**: {error}\n")

            if self.backup_path:
                f.write(f"\n## Backup\n\nBackup saved at: `{self.backup_path}`\n")

            f.write("\n## Testing Instructions\n\n")
            f.write("```bash\n")
            f.write("# Create test database\n")
            f.write("python -m odoo -d test_db -i base --stop-after-init\n\n")
            f.write("# Install modules\n")
            f.write("python -m odoo -d test_db -i your_module --stop-after-init\n")
            f.write("```\n")

        print(f"\n[OK] Report saved to: {report_path}")
        return report_path

    def check_python_dependencies(self):
        """Check and list Python dependencies from all manifests"""
        dependencies = set()
        manifest_files = self.project_path.glob("**/__manifest__.py")

        for manifest in manifest_files:
            try:
                with open(manifest, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Find external_dependencies section
                match = re.search(r"'external_dependencies'\s*:\s*\{[^}]*'python'\s*:\s*\[([^\]]+)\]", content, re.DOTALL)
                if match:
                    deps_str = match.group(1)
                    # Extract individual dependencies
                    deps = re.findall(r"'([^']+)'", deps_str)
                    dependencies.update(deps)

            except Exception as e:
                print(f"  [WARNING] Could not check dependencies in {manifest}: {e}")

        if dependencies:
            print(f"\n[INFO] Found Python dependencies: {', '.join(dependencies)}")
            print("[TIP] Install them with: pip install " + " ".join(dependencies))
            self.report.append(f"[INFO] Python dependencies found: {', '.join(dependencies)}")

        return dependencies

    def pre_upgrade_validation(self):
        """Run syntax validation before upgrade."""
        if not self.enable_validation:
            return None

        print("\n[Validation] Running pre-upgrade syntax validation...")
        validator = SyntaxValidator(self.project_path, verbose=False)
        results = validator.validate_all()

        if results['valid']:
            print("[OK] Pre-upgrade validation passed")
            self.report.append("[OK] Pre-upgrade syntax validation passed")
        else:
            print(f"[WARNING] Pre-upgrade validation found {results['stats']['total_errors']} errors")
            print(f"  and {results['stats']['total_warnings']} warnings")

            if self.auto_fix:
                print("\n[Auto-fix] Attempting automatic fixes...")
                fixer = AutoFixLibrary(self.project_path, backup=False)
                fix_results = fixer.apply_all_fixes()
                if fix_results['total_fixes'] > 0:
                    print(f"  Applied {fix_results['total_fixes']} automatic fixes")
                    self.report.append(f"[OK] Applied {fix_results['total_fixes']} pre-upgrade fixes")

                    # Re-validate after fixes
                    results = validator.validate_all()

        # Save validation report
        report_path = self.project_path / "PRE_UPGRADE_VALIDATION.md"
        report_content = validator.generate_report(str(report_path))

        return results

    def post_upgrade_validation(self):
        """Run syntax validation after upgrade."""
        if not self.enable_validation:
            return None

        print("\n[Validation] Running post-upgrade syntax validation...")
        validator = SyntaxValidator(self.project_path, verbose=False)
        results = validator.validate_all()

        if results['valid']:
            print("[OK] Post-upgrade validation passed - All syntax is correct!")
            self.report.append("[OK] Post-upgrade syntax validation passed")
        else:
            print(f"[ERROR] Post-upgrade validation found {results['stats']['total_errors']} errors")
            print(f"  and {results['stats']['total_warnings']} warnings")

            if self.auto_fix:
                print("\n[Auto-fix] Attempting automatic fixes...")
                fixer = AutoFixLibrary(self.project_path, backup=False)
                fix_results = fixer.apply_all_fixes()
                if fix_results['total_fixes'] > 0:
                    print(f"  Applied {fix_results['total_fixes']} automatic fixes")
                    self.report.append(f"[OK] Applied {fix_results['total_fixes']} post-upgrade fixes")

                    # Re-validate after fixes
                    results = validator.validate_all()

                    if results['valid']:
                        print("[OK] All syntax errors fixed successfully!")
                    else:
                        print(f"[WARNING] {results['stats']['total_errors']} errors remain after auto-fix")
                        print("  Manual intervention required")

        # Save validation report
        report_path = self.project_path / "POST_UPGRADE_VALIDATION.md"
        report_content = validator.generate_report(str(report_path))

        return results

    def rollback(self):
        """Rollback to backup if validation fails."""
        if not self.backup_path or not self.backup_path.exists():
            print("[ERROR] Cannot rollback - no backup available")
            return False

        print(f"\n[Rollback] Rolling back to backup: {self.backup_path}")

        try:
            # Remove current project contents
            for item in self.project_path.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

            # Restore from backup
            for item in self.backup_path.iterdir():
                if item.is_dir():
                    shutil.copytree(item, self.project_path / item.name)
                else:
                    shutil.copy2(item, self.project_path / item.name)

            print("[OK] Rollback completed successfully")
            self.report.append("[OK] Rolled back to backup due to validation failures")
            return True

        except Exception as e:
            print(f"[ERROR] Rollback failed: {e}")
            self.report.append(f"[ERROR] Rollback failed: {e}")
            return False

    def run(self):
        """Run the complete upgrade process with validation"""
        print("\n>>> Starting Enhanced Odoo 19 Upgrade Process")
        print("=" * 50)

        # Step 1: Backup
        print("\n[Step 1] Creating backup...")
        self.create_backup()

        # Step 2: Pre-upgrade validation
        if self.enable_validation:
            print("\n[Step 2] Pre-upgrade validation...")
            self.pre_validation_results = self.pre_upgrade_validation()

            if self.pre_validation_results and self.pre_validation_results['stats']['total_errors'] > 20:
                print("\n[WARNING] Too many pre-existing errors. Consider fixing them first.")
                response = input("Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    print("Upgrade cancelled. Fix errors first, then retry.")
                    return
        else:
            print("\n[Step 2] Skipping pre-upgrade validation")

        # Step 3: Check Dependencies
        print("\n[Step 3] Checking Python dependencies...")
        self.check_python_dependencies()

        # Step 4: Manifests
        print("\n[Step 4] Updating manifest files...")
        self.update_manifest_files()

        # Step 5: XML Views
        print("\n[Step 5] Fixing XML views...")
        self.fix_xml_views()

        # Step 6: Python Code
        print("\n[Step 6] Updating Python code...")
        self.update_python_code()

        # Step 7: JavaScript
        print("\n[Step 7] Migrating JavaScript RPC...")
        self.migrate_javascript_rpc()

        # Step 8: SCSS
        print("\n[Step 8] Updating SCSS files...")
        self.update_scss_files()

        # Step 9: Post-upgrade validation
        if self.enable_validation:
            print("\n[Step 9] Post-upgrade validation...")
            self.post_validation_results = self.post_upgrade_validation()

            if self.post_validation_results and not self.post_validation_results['valid']:
                print("\n[WARNING] Post-upgrade validation failed!")

                if self.post_validation_results['stats']['total_errors'] > 0:
                    response = input("Would you like to rollback to backup? (y/n): ")
                    if response.lower() == 'y':
                        self.rollback()
                        print("\n[ERROR] Upgrade rolled back due to validation failures")
                        print(f"Backup preserved at: {self.backup_path}")
                        return
        else:
            print("\n[Step 9] Skipping post-upgrade validation")

        # Generate report
        print("\n[Finalizing] Generating migration report...")
        self.generate_report()

        print("\n" + "=" * 50)

        if self.enable_validation and self.post_validation_results:
            if self.post_validation_results['valid']:
                print("[SUCCESS] Odoo 19 Upgrade Complete - All Syntax Valid!")
            else:
                print("[WARNING] Odoo 19 Upgrade Complete - With Warnings")
                print(f"   {self.post_validation_results['stats']['total_errors']} errors need manual fixing")
        else:
            print("[SUCCESS] Odoo 19 Upgrade Complete!")

        if self.errors:
            print(f"\n[WARNING] {len(self.errors)} upgrade errors encountered. Check the report for details.")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python upgrade_to_odoo19.py <project_path> [options]")
        print("\nOptions:")
        print("  --no-validation    Skip syntax validation")
        print("  --auto-fix         Automatically fix detected issues")
        print("  --help             Show this help message")
        print("\nExamples:")
        print("  python upgrade_to_odoo19.py C:\\odoo\\odoo19\\projects\\mymodule")
        print("  python upgrade_to_odoo19.py C:\\odoo\\odoo19\\projects\\mymodule --auto-fix")
        sys.exit(1)

    if '--help' in sys.argv:
        print("Odoo 19 Upgrade Script - Enhanced Version")
        print("\nThis script upgrades Odoo modules to version 19 with:")
        print("  - Automatic backup creation")
        print("  - Pre and post-upgrade syntax validation")
        print("  - Automatic fixes for common issues")
        print("  - Rollback capability on critical failures")
        print("\nFor more information, see the documentation.")
        sys.exit(0)

    project_path = sys.argv[1]

    if not os.path.exists(project_path):
        print(f"Error: Path '{project_path}' does not exist")
        sys.exit(1)

    enable_validation = '--no-validation' not in sys.argv
    auto_fix = '--auto-fix' in sys.argv

    if auto_fix:
        print("Auto-fix mode enabled - will attempt to fix issues automatically")

    upgrader = Odoo19Upgrader(project_path,
                             enable_validation=enable_validation,
                             auto_fix=auto_fix)
    upgrader.run()


if __name__ == "__main__":
    main()

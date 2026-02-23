#!/usr/bin/env python3
"""
Quick Fix Script for Common Odoo 19 Issues
Applies targeted fixes for specific compatibility problems
Enhanced with dry-run mode and validation support
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Import validation module if available
try:
    from syntax_validator import SyntaxValidator
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    print("Note: Syntax validation not available. Install syntax_validator.py for enhanced features")


class QuickFixer:
    """Quick fixes for common Odoo 19 issues"""

    def __init__(self, project_path, dry_run=False, validate=False):
        self.project_path = Path(project_path)
        self.fixes_applied = []
        self.dry_run = dry_run
        self.validate = validate and VALIDATION_AVAILABLE
        self.dry_run_changes = []
        self.validation_results = None

    def fix_tree_views(self):
        """Fix all tree view references"""
        print("\n[1/6] Fixing tree view references...")
        count = 0
        changes = []

        for xml_file in self.project_path.glob("**/*.xml"):
            try:
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Fix tree tags
                content = re.sub(r'<tree(\s+[^>]*)?>', r'<list\1>', content)
                content = content.replace('</tree>', '</list>')

                # Fix view_mode references
                content = re.sub(r'(<field name="view_mode">)tree(</field>)', r'\1list\2', content)
                content = re.sub(r'(<field name="view_mode">)tree,', r'\1list,', content)
                content = re.sub(r',tree([,<])', r',list\1', content)
                content = re.sub(r"'view_mode':\s*'tree'", r"'view_mode': 'list'", content)

                if content != original:
                    if self.dry_run:
                        changes.append(f"Would fix: {xml_file.relative_to(self.project_path)}")
                        self.dry_run_changes.append({
                            'file': str(xml_file.relative_to(self.project_path)),
                            'type': 'tree_views',
                            'changes': self._get_diff_summary(original, content)
                        })
                    else:
                        with open(xml_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                    count += 1

            except Exception as e:
                print(f"  Error processing {xml_file.name}: {e}")

        if self.dry_run:
            self.fixes_applied.append(f"Would fix tree views in {count} files")
        else:
            self.fixes_applied.append(f"Fixed tree views in {count} files")

        print(f"  [{'DRY-RUN' if self.dry_run else 'OK'}] {'Would fix' if self.dry_run else 'Fixed'} {count} files")

    def fix_search_groups(self):
        """Remove group tags from search views"""
        print("\n[2/6] Fixing search view groups...")
        count = 0

        for xml_file in self.project_path.glob("**/*.xml"):
            try:
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Remove group tags from search views
                pattern = r'(<search[^>]*>)(.*?)(</search>)'

                def remove_groups(match):
                    search_start = match.group(1)
                    search_content = match.group(2)
                    search_end = match.group(3)

                    if '<group' in search_content:
                        # Remove group tags
                        search_content = re.sub(r'<group[^>]*>', '', search_content)
                        search_content = search_content.replace('</group>', '')

                        # Add separator if needed
                        if 'group_by' in search_content and '<separator/>' not in search_content:
                            search_content = re.sub(
                                r'(\s*)(<filter[^>]*group_by[^>]*>)',
                                r'\1<separator/>\1\2',
                                search_content,
                                count=1
                            )

                    return search_start + search_content + search_end

                content = re.sub(pattern, remove_groups, content, flags=re.DOTALL)

                if content != original:
                    with open(xml_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    count += 1

            except Exception as e:
                print(f"  Error processing {xml_file.name}: {e}")

        self.fixes_applied.append(f"Fixed search groups in {count} files")
        print(f"  [OK] Fixed {count} files")

    def fix_js_class(self):
        """Remove problematic js_class attributes"""
        print("\n[3/6] Fixing js_class attributes...")
        count = 0

        for xml_file in self.project_path.glob("**/*.xml"):
            try:
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Remove crm_kanban js_class
                content = re.sub(r'\s+js_class=["\']crm_kanban["\']', '', content)

                # Optionally remove all js_class from kanban views if they cause issues
                # content = re.sub(r'\s+js_class=["\'][^"\']*["\']', '', content)

                if content != original:
                    with open(xml_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    count += 1

            except Exception as e:
                print(f"  Error processing {xml_file.name}: {e}")

        self.fixes_applied.append(f"Fixed js_class in {count} files")
        print(f"  [OK] Fixed {count} files")

    def fix_cron_numbercall(self):
        """Remove numbercall from cron jobs"""
        print("\n[4/6] Fixing cron numbercall fields...")
        count = 0

        for xml_file in self.project_path.glob("**/*.xml"):
            try:
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Remove numbercall fields
                content = re.sub(
                    r'\s*<field\s+name="numbercall"[^>]*>.*?</field>',
                    '',
                    content,
                    flags=re.DOTALL
                )
                content = re.sub(r'\s*<field\s+name="numbercall"[^/]*?/>', '', content)

                if content != original:
                    with open(xml_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    count += 1

            except Exception as e:
                print(f"  Error processing {xml_file.name}: {e}")

        self.fixes_applied.append(f"Fixed numbercall in {count} files")
        print(f"  [OK] Fixed {count} files")

    def fix_kanban_templates(self):
        """Fix kanban template names"""
        print("\n[5/6] Fixing kanban templates...")
        count = 0

        for xml_file in self.project_path.glob("**/*.xml"):
            try:
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Fix kanban-box to card
                content = content.replace('t-name="kanban-box"', 't-name="card"')

                if content != original:
                    with open(xml_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    count += 1

            except Exception as e:
                print(f"  Error processing {xml_file.name}: {e}")

        self.fixes_applied.append(f"Fixed kanban templates in {count} files")
        print(f"  [OK] Fixed {count} files")

    def fix_rpc_service(self):
        """Add _jsonRpc helper to files using RPC service"""
        print("\n[6/6] Fixing RPC service usage...")
        count = 0

        json_rpc_helper = '''
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

        for js_file in self.project_path.glob("**/*.js"):
            if 'node_modules' in str(js_file) or '.min.js' in str(js_file):
                continue

            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original = content

                # Remove RPC service
                content = re.sub(r'this\.rpc\s*=\s*useService\(["\']rpc["\']\);?\s*\n?', '', content)

                # Replace this.rpc calls
                if 'this.rpc(' in content:
                    content = content.replace('this.rpc(', 'this._jsonRpc(')

                    # Add helper if not present
                    if '_jsonRpc(endpoint, params' not in content:
                        # Find setup() and add after
                        setup_pattern = r'(setup\(\)\s*\{[^}]*\})'

                        def add_helper(match):
                            return match.group(0) + json_rpc_helper

                        content = re.sub(setup_pattern, add_helper, content, count=1)

                if content != original:
                    with open(js_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    count += 1

            except Exception as e:
                print(f"  Error processing {js_file.name}: {e}")

        self.fixes_applied.append(f"Fixed RPC service in {count} files")
        print(f"  [OK] Fixed {count} files")

    def _get_diff_summary(self, original, modified):
        """Get a summary of changes between original and modified content"""
        changes = []
        if '<tree' in original and '<list' in modified:
            changes.append("tree → list tags")
        if 'view_mode">tree' in original and 'view_mode">list' in modified:
            changes.append("view_mode tree → list")
        if '<group' in original and '<group' not in modified:
            changes.append("removed group tags")
        if 'js_class="crm_kanban"' in original and 'js_class="crm_kanban"' not in modified:
            changes.append("removed js_class")
        if 'numbercall' in original and 'numbercall' not in modified:
            changes.append("removed numbercall")
        if 't-name="kanban-box"' in original and 't-name="card"' in modified:
            changes.append("kanban-box → card")
        if 'this.rpc(' in original and 'this._jsonRpc(' in modified:
            changes.append("RPC migration")
        return ', '.join(changes) if changes else "various fixes"

    def run_validation(self):
        """Run syntax validation on the project"""
        if not self.validate:
            return None

        print("\n🔍 Running syntax validation...")
        validator = SyntaxValidator(self.project_path, verbose=False)
        results = validator.validate_all()

        if results['valid']:
            print("✓ Validation passed - no syntax errors detected")
        else:
            print(f"⚠ Found {results['stats']['total_errors']} error(s)")
            print(f"  and {results['stats']['total_warnings']} warning(s)")

        # Save validation report
        report_path = self.project_path / "QUICKFIX_VALIDATION.md"
        validator.generate_report(str(report_path))
        print(f"  Validation report: {report_path}")

        return results

    def generate_dry_run_report(self):
        """Generate detailed dry-run report"""
        if not self.dry_run or not self.dry_run_changes:
            return

        report_path = self.project_path / f"DRY_RUN_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Quick Fix Dry-Run Report\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"**Project**: {self.project_path.name}\n")
            f.write(f"**Total files to modify**: {len(self.dry_run_changes)}\n\n")

            f.write("## Changes by Type\n\n")

            # Group changes by type
            changes_by_type = {}
            for change in self.dry_run_changes:
                fix_type = change['type']
                if fix_type not in changes_by_type:
                    changes_by_type[fix_type] = []
                changes_by_type[fix_type].append(change)

            for fix_type, changes in changes_by_type.items():
                f.write(f"### {fix_type.replace('_', ' ').title()}\n\n")
                for change in changes:
                    f.write(f"- **{change['file']}**: {change['changes']}\n")
                f.write("\n")

            f.write("## Next Steps\n\n")
            f.write("1. Review the changes above\n")
            f.write("2. Run without --dry-run to apply fixes\n")
            f.write("3. Use --validate to check syntax after fixes\n")

        print(f"\n📄 Dry-run report saved to: {report_path}")

    def generate_summary(self):
        """Generate fix summary"""
        print("\n" + "=" * 60)
        if self.dry_run:
            print("DRY-RUN SUMMARY")
        else:
            print("QUICK FIX SUMMARY")
        print("=" * 60)

        if self.fixes_applied:
            print(f"\n{'Changes that would be made' if self.dry_run else 'Fixes applied'}:")
            for fix in self.fixes_applied:
                print(f"  [{'DRY-RUN' if self.dry_run else 'OK'}] {fix}")
        else:
            print("\nNo fixes were needed.")

        if self.dry_run:
            self.generate_dry_run_report()
            print("\n[INFO] This was a dry-run. No files were modified.")
            print("       Run without --dry-run to apply the fixes.")
        else:
            print("\n[SUCCESS] All quick fixes completed!")

        if self.validation_results:
            print("\n📊 Validation Results:")
            if self.validation_results['valid']:
                print("  ✓ All syntax checks passed")
            else:
                print(f"  ⚠ {self.validation_results['stats']['total_errors']} errors found")
                print(f"  ⚠ {self.validation_results['stats']['total_warnings']} warnings found")

        print("\nNext steps:")
        if not self.dry_run:
            print("1. Test module installation")
            print("2. Run full upgrade script if needed: python upgrade_to_odoo19.py")
            print("3. Check for any remaining issues with: python odoo19_precheck.py")
        else:
            print("1. Review the dry-run report")
            print("2. Run without --dry-run to apply fixes")

    def run(self):
        """Run all quick fixes"""
        print("\n" + "=" * 60)
        print(f"ODOO 19 QUICK FIX UTILITY {'(DRY-RUN)' if self.dry_run else ''}")
        print("=" * 60)
        print(f"Project: {self.project_path}")
        print(f"Mode: {'Dry-run' if self.dry_run else 'Apply fixes'}")
        print(f"Validation: {'Enabled' if self.validate else 'Disabled'}")
        print("\nApplying fixes...")

        # Run validation before fixes if enabled
        if self.validate and not self.dry_run:
            print("\n=== Pre-fix Validation ===")
            pre_validation = self.run_validation()

        self.fix_tree_views()
        self.fix_search_groups()
        self.fix_js_class()
        self.fix_cron_numbercall()
        self.fix_kanban_templates()
        self.fix_rpc_service()

        # Run validation after fixes if enabled
        if self.validate and not self.dry_run:
            print("\n=== Post-fix Validation ===")
            self.validation_results = self.run_validation()

        self.generate_summary()


def main():
    """Main entry point"""
    if len(sys.argv) < 2 or '--help' in sys.argv:
        print("Usage: python quick_fix_odoo19.py <project_path> [options]")
        print("\nOptions:")
        print("  --dry-run      Preview changes without modifying files")
        print("  --validate     Run syntax validation before and after fixes")
        print("  --help         Show this help message")
        print("\nThis script applies quick fixes for common Odoo 19 issues:")
        print("  - Tree to List view conversion")
        print("  - Search view group removal")
        print("  - js_class attribute removal")
        print("  - Cron numbercall field removal")
        print("  - Kanban template fixes")
        print("  - RPC service migration")
        print("\nExamples:")
        print("  # Preview changes without applying")
        print("  python quick_fix_odoo19.py /path/to/module --dry-run")
        print("\n  # Apply fixes with validation")
        print("  python quick_fix_odoo19.py /path/to/module --validate")
        print("\n  # Preview with validation check")
        print("  python quick_fix_odoo19.py /path/to/module --dry-run --validate")
        sys.exit(0 if '--help' in sys.argv else 1)

    project_path = sys.argv[1]

    if not os.path.exists(project_path):
        print(f"Error: Path '{project_path}' does not exist")
        sys.exit(1)

    # Parse options
    dry_run = '--dry-run' in sys.argv
    validate = '--validate' in sys.argv

    if dry_run:
        print("🔍 Running in DRY-RUN mode - no files will be modified")

    if validate and not VALIDATION_AVAILABLE:
        print("⚠ Warning: Validation requested but syntax_validator.py not available")
        validate = False

    fixer = QuickFixer(project_path, dry_run=dry_run, validate=validate)
    fixer.run()


if __name__ == "__main__":
    main()
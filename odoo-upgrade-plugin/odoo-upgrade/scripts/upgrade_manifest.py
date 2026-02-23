#!/usr/bin/env python3
"""
Odoo Manifest Upgrade Script
Automatically updates __manifest__.py files for target Odoo version
"""

import os
import ast
import json
import argparse
from pathlib import Path

class ManifestUpgrader:
    def __init__(self, target_version):
        self.target_version = target_version
        self.version_format = {
            '14': '14.0',
            '15': '15.0',
            '16': '16.0',
            '17': '17.0',
            '18': '18.0',
            '19': '19.0',
        }

    def get_version_string(self, current_version=None):
        """Generate proper version string for target Odoo version"""
        base = self.version_format.get(str(self.target_version), f'{self.target_version}.0')

        # Extract version numbers if current version exists
        if current_version and '.' in str(current_version):
            parts = str(current_version).split('.')
            if len(parts) >= 3:
                # Keep the last three version numbers
                return f"{base}.{parts[-3]}.{parts[-2]}.{parts[-1]}"

        return f"{base}.1.0.0"

    def read_manifest(self, file_path):
        """Read and parse manifest file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to evaluate as Python dict
        try:
            # Replace common patterns
            content = content.replace('True', 'true')
            content = content.replace('False', 'false')
            content = content.replace('None', 'null')

            # Attempt to parse with ast
            manifest = ast.literal_eval(content.replace('true', 'True').replace('false', 'False').replace('null', 'None'))
            return manifest, content
        except:
            # Fallback: manual parsing
            manifest = {}
            lines = content.split('\n')
            for line in lines:
                if ':' in line and not line.strip().startswith('#'):
                    key_part = line.split(':')[0].strip().strip("'\"")
                    if key_part in ['name', 'version', 'license', 'category', 'author']:
                        value_part = line.split(':', 1)[1].strip().rstrip(',').strip("'\"")
                        manifest[key_part] = value_part
            return manifest, content

    def update_manifest(self, manifest, file_path):
        """Update manifest with required fields"""
        changes = []

        # Update version
        old_version = manifest.get('version', '1.0')
        new_version = self.get_version_string(old_version)
        if old_version != new_version:
            manifest['version'] = new_version
            changes.append(f"Version: {old_version} → {new_version}")

        # Add license if missing
        if 'license' not in manifest:
            manifest['license'] = 'LGPL-3'
            changes.append("Added license: LGPL-3")

        # Add installable if missing
        if 'installable' not in manifest:
            manifest['installable'] = True
            changes.append("Added installable: True")

        # Add auto_install if missing and appropriate
        if 'auto_install' not in manifest:
            manifest['auto_install'] = False
            changes.append("Added auto_install: False")

        # Check for external dependencies
        module_path = Path(file_path).parent
        has_external_deps = self.check_external_dependencies(module_path)
        if has_external_deps and 'external_dependencies' not in manifest:
            manifest['external_dependencies'] = {
                'python': has_external_deps
            }
            changes.append(f"Added external dependencies: {has_external_deps}")

        return manifest, changes

    def check_external_dependencies(self, module_path):
        """Scan Python files for external imports"""
        external_deps = set()
        common_externals = {
            'geopy', 'spacy', 'hachoir', 'PIL', 'numpy', 'pandas',
            'matplotlib', 'seaborn', 'requests', 'xlsxwriter', 'xlrd'
        }

        for py_file in module_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Look for import statements
                import_lines = [line for line in content.split('\n') if 'import' in line]
                for line in import_lines:
                    for dep in common_externals:
                        if f'import {dep}' in line or f'from {dep}' in line:
                            external_deps.add(dep)
            except:
                pass

        return list(external_deps)

    def write_manifest(self, manifest, file_path):
        """Write updated manifest back to file"""
        output = "# -*- coding: utf-8 -*-\n"
        output += "{\n"

        # Key order for better readability
        key_order = ['name', 'version', 'summary', 'category', 'author',
                    'website', 'license', 'depends', 'data', 'assets',
                    'external_dependencies', 'installable', 'auto_install',
                    'application']

        # Write ordered keys first
        for key in key_order:
            if key in manifest:
                value = manifest[key]
                output += f"    '{key}': {self.format_value(value)},\n"

        # Write remaining keys
        for key, value in manifest.items():
            if key not in key_order:
                output += f"    '{key}': {self.format_value(value)},\n"

        output += "}\n"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(output)

    def format_value(self, value):
        """Format Python value for manifest"""
        if isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, bool):
            return 'True' if value else 'False'
        elif isinstance(value, list):
            items = [self.format_value(item) for item in value]
            return '[\n        ' + ',\n        '.join(items) + '\n    ]'
        elif isinstance(value, dict):
            items = [f"'{k}': {self.format_value(v)}" for k, v in value.items()]
            return '{\n        ' + ',\n        '.join(items) + '\n    }'
        else:
            return str(value)

    def process_module(self, module_path):
        """Process a single module"""
        manifest_path = os.path.join(module_path, '__manifest__.py')

        if not os.path.exists(manifest_path):
            print(f"✗ No manifest found in {module_path}")
            return False

        print(f"\n📦 Processing: {os.path.basename(module_path)}")

        # Read current manifest
        manifest, original_content = self.read_manifest(manifest_path)

        # Update manifest
        updated_manifest, changes = self.update_manifest(manifest, manifest_path)

        if changes:
            # Backup original
            backup_path = manifest_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)

            # Write updated manifest
            self.write_manifest(updated_manifest, manifest_path)

            print(f"✓ Updated manifest:")
            for change in changes:
                print(f"  - {change}")
        else:
            print("✓ Manifest already up to date")

        return True

def main():
    parser = argparse.ArgumentParser(description='Upgrade Odoo module manifests')
    parser.add_argument('path', help='Path to module or project directory')
    parser.add_argument('-t', '--target', type=int, default=19,
                       choices=[14, 15, 16, 17, 18, 19],
                       help='Target Odoo version (default: 19)')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Process all modules in directory')

    args = parser.parse_args()

    upgrader = ManifestUpgrader(args.target)

    if args.recursive:
        # Find all modules in directory
        modules_found = 0
        for root, dirs, files in os.walk(args.path):
            if '__manifest__.py' in files:
                upgrader.process_module(root)
                modules_found += 1

        print(f"\n✓ Processed {modules_found} modules")
    else:
        # Process single module
        upgrader.process_module(args.path)

if __name__ == '__main__':
    main()
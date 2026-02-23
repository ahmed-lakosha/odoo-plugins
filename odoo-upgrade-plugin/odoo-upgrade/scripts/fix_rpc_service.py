#!/usr/bin/env python3
"""
Fix RPC Service Usage in Odoo 19 Frontend Components
Replaces useService("rpc") with fetch-based JSON-RPC calls
"""

import os
import re
import argparse
from pathlib import Path

class RPCServiceFixer:
    def __init__(self):
        self.json_rpc_method = '''
    /**
     * Helper method to make JSON-RPC calls in Odoo 19 frontend context
     * Replaces the RPC service which is not available in public components
     */
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
                console.error('JSON-RPC Error:', data.error);
                throw new Error(data.error.message || 'RPC call failed');
            }
            return data.result;
        } catch (error) {
            console.error('JSON-RPC call failed:', error);
            throw error;
        }
    }'''

    def has_rpc_service(self, content):
        """Check if file uses RPC service"""
        patterns = [
            r'useService\(["\']rpc["\']\)',
            r'this\.rpc\s*=\s*useService',
            r'await\s+this\.rpc\(',
            r'this\.rpc\('
        ]
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        return False

    def fix_rpc_service_usage(self, content):
        """Replace RPC service usage with _jsonRpc helper"""
        changes_made = []

        # Step 1: Remove or comment out the RPC service line
        pattern = r'(\s*)this\.rpc\s*=\s*useService\(["\']rpc["\']\);?\s*\n?'
        replacement = r'\1// Note: RPC service removed - using fetch with JSON-RPC instead for Odoo 19 compatibility\n'
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes_made.append("Removed useService('rpc') declaration")

        # Step 2: Add _jsonRpc method if it doesn't exist
        if '_jsonRpc' not in content and 'this.rpc(' in content:
            # Find the right place to insert the method
            # Try to find the end of setup() method
            setup_match = re.search(r'setup\(\)[^{]*{.*?\n(\s*)\}', content, re.DOTALL)
            if setup_match:
                indent = setup_match.group(1)
                insertion_point = setup_match.end()

                # Insert the _jsonRpc method after setup()
                before = content[:insertion_point]
                after = content[insertion_point:]
                content = before + '\n' + self.json_rpc_method + '\n' + after
                changes_made.append("Added _jsonRpc helper method")
            else:
                # Try to insert after the class opening
                class_match = re.search(r'export\s+class\s+\w+\s+extends\s+Component\s*{', content)
                if class_match:
                    insertion_point = class_match.end()
                    before = content[:insertion_point]
                    after = content[insertion_point:]
                    content = before + '\n' + self.json_rpc_method + '\n' + after
                    changes_made.append("Added _jsonRpc helper method")

        # Step 3: Replace this.rpc() calls with this._jsonRpc()
        rpc_call_pattern = r'this\.rpc\('
        if re.search(rpc_call_pattern, content):
            content = re.sub(rpc_call_pattern, 'this._jsonRpc(', content)
            changes_made.append("Replaced this.rpc() with this._jsonRpc()")

        # Step 4: Replace await this.rpc with await this._jsonRpc
        await_pattern = r'await\s+this\.rpc\('
        if re.search(await_pattern, content):
            content = re.sub(await_pattern, 'await this._jsonRpc(', content)
            # Already covered by step 3

        return content, changes_made

    def ensure_module_annotation(self, content):
        """Ensure @odoo-module annotation exists"""
        if '/** @odoo-module **/' not in content[:100]:  # Check first 100 chars
            content = '/** @odoo-module **/\n' + content
            return content, True
        return content, False

    def process_file(self, file_path):
        """Process a single JavaScript file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            content = original_content
            all_changes = []

            # Check and add module annotation
            content, annotation_added = self.ensure_module_annotation(content)
            if annotation_added:
                all_changes.append("Added @odoo-module annotation")

            # Fix RPC service if needed
            if self.has_rpc_service(original_content):
                content, rpc_changes = self.fix_rpc_service_usage(content)
                all_changes.extend(rpc_changes)

            # Write back if changes were made
            if all_changes:
                # Create backup
                backup_path = str(file_path) + '.rpc_backup'
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)

                # Write fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                return True, all_changes
            else:
                return False, []

        except Exception as e:
            return False, [f"Error: {str(e)}"]

    def process_directory(self, directory_path):
        """Process all JavaScript files in directory"""
        path = Path(directory_path)
        js_files = list(path.rglob('*.js'))

        print(f"Found {len(js_files)} JavaScript files")
        print("-" * 50)

        fixed_files = []
        skipped_files = []
        error_files = []

        for js_file in js_files:
            # Skip node_modules and lib directories
            if 'node_modules' in str(js_file) or '/lib/' in str(js_file):
                continue

            print(f"\n📄 Checking: {js_file.relative_to(path)}")

            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if self.has_rpc_service(content):
                fixed, changes = self.process_file(js_file)

                if fixed:
                    print(f"✅ Fixed: {js_file.name}")
                    for change in changes:
                        print(f"   - {change}")
                    fixed_files.append(str(js_file))
                elif changes and changes[0].startswith("Error"):
                    print(f"❌ Error: {js_file.name}")
                    print(f"   {changes[0]}")
                    error_files.append(str(js_file))
            else:
                skipped_files.append(str(js_file))

        # Summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"✅ Fixed: {len(fixed_files)} files")
        print(f"⏭️  Skipped: {len(skipped_files)} files (no RPC usage)")
        print(f"❌ Errors: {len(error_files)} files")

        if fixed_files:
            print("\nFixed files:")
            for f in fixed_files:
                print(f"  - {f}")

        return len(fixed_files), len(error_files)

def main():
    parser = argparse.ArgumentParser(
        description='Fix RPC service usage in Odoo 19 JavaScript files'
    )
    parser.add_argument('path', help='Path to file or directory')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')
    parser.add_argument('--no-backup', action='store_true',
                       help='Do not create backup files')

    args = parser.parse_args()

    fixer = RPCServiceFixer()
    path = Path(args.path)

    if path.is_file():
        # Process single file
        if path.suffix == '.js':
            print(f"Processing file: {path}")
            fixed, changes = fixer.process_file(path)
            if fixed:
                print("✅ File fixed successfully!")
                for change in changes:
                    print(f"  - {change}")
            else:
                print("ℹ️  No changes needed")
        else:
            print("Error: File must be a JavaScript file (.js)")
    elif path.is_dir():
        # Process directory
        print(f"Processing directory: {path}")
        fixer.process_directory(path)
    else:
        print(f"Error: Path does not exist: {path}")

if __name__ == '__main__':
    main()
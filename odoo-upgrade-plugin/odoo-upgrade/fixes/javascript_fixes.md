# JavaScript Fix Templates for Odoo 19

## RPC Service Migration

### Complete Component Migration Template

```javascript
/** @odoo-module **/

import {Component, onMounted, useState} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";
import {registry} from "@web/core/registry";

// TEMPLATE FOR MIGRATING A COMPONENT FROM ODOO 17 TO ODOO 19

export class MigratedComponent extends Component {
    setup() {
        // REMOVED: this.rpc = useService("rpc");
        // Services still available in frontend:
        const localization = useService("localization");

        this.state = useState({
            data: [],
            loading: true,
            error: null,
            isAr: (localization?.code || '').startsWith('ar')
        });

        onMounted(async () => {
            await this.loadData();
        });
    }

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
    }

    async loadData() {
        this.state.loading = true;
        try {
            // OLD: const result = await this.rpc("/api/endpoint", {param: value});
            const result = await this._jsonRpc("/api/endpoint", {param: value});
            this.state.data = result;
        } catch (error) {
            this.state.error = error.message;
        } finally {
            this.state.loading = false;
        }
    }

    static template = "module_name.ComponentTemplate";
}

// Register the component
registry.category("public_components").add("module_name.MigratedComponent", MigratedComponent);
```

### Batch RPC Fix Script

```python
import re
import glob

def fix_rpc_service(js_content):
    """Replace RPC service usage with _jsonRpc helper"""

    # Remove useService("rpc") line
    js_content = re.sub(
        r'this\.rpc\s*=\s*useService\(["\']rpc["\']\);?\s*\n?',
        '// Note: RPC service removed - using fetch with JSON-RPC instead for Odoo 19 compatibility\n',
        js_content
    )

    # Check if _jsonRpc method exists
    if '_jsonRpc' not in js_content:
        # Find the last method in setup() and add _jsonRpc after it
        setup_end = js_content.find('    }\n\n', js_content.find('setup()'))
        if setup_end > 0:
            json_rpc_method = '''
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
    }
'''
            js_content = js_content[:setup_end + 6] + json_rpc_method + '\n' + js_content[setup_end + 6:]

    # Replace this.rpc() calls with this._jsonRpc()
    js_content = re.sub(
        r'this\.rpc\(',
        'this._jsonRpc(',
        js_content
    )

    return js_content
```

### Module Annotation Check

```python
def ensure_module_annotation(js_content):
    """Ensure @odoo-module annotation exists"""
    if '/** @odoo-module **/' not in js_content:
        js_content = '/** @odoo-module **/\n' + js_content
    return js_content
```

### publicWidget Migration

```javascript
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.MyWidget = publicWidget.Widget.extend({
    selector: '.my-selector',
    events: {
        'click .button': '_onClick',
    },

    start: function () {
        // Initialize widget
        return this._super.apply(this, arguments);
    },

    _onClick: function (ev) {
        // Handle click
    },

    // For RPC calls in publicWidget
    _rpc: function (params) {
        // Use the built-in _rpc method for widgets
        return this._super(params);
    },
});

export default publicWidget.registry.MyWidget;
```

### Service Registration Changes

```javascript
// OLD (Odoo 17)
import {serviceRegistry} from "@web/core/registry";

const myService = {
    start(env, {rpc}) {
        return {
            async fetchData() {
                return rpc("/api/data");
            }
        };
    }
};

serviceRegistry.add("myService", myService);

// NEW (Odoo 19)
import {registry} from "@web/core/registry";

const myService = {
    start(env) {
        async function fetchData() {
            // Use fetch directly
            const response = await fetch("/api/data", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: {},
                    id: 1
                })
            });
            const data = await response.json();
            return data.result;
        }

        return {fetchData};
    }
};

registry.category("services").add("myService", myService);
```

### Complete File Processor

```python
import os
import glob

def process_js_file(file_path):
    """Apply all JavaScript fixes to a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply fixes
    content = ensure_module_annotation(content)
    content = fix_rpc_service(content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

def fix_all_js_files(project_path):
    """Process all JavaScript files in a project"""
    js_files = glob.glob(os.path.join(project_path, '**/*.js'), recursive=True)

    fixed_count = 0
    rpc_fixes = []

    for js_file in js_files:
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if 'useService("rpc")' in content or "useService('rpc')" in content:
                process_js_file(js_file)
                rpc_fixes.append(js_file)
                print(f"✓ Fixed RPC in: {js_file}")

            fixed_count += 1
        except Exception as e:
            print(f"✗ Error in {js_file}: {e}")

    print(f"\n✓ Processed {fixed_count} files")
    print(f"✓ Fixed RPC service in {len(rpc_fixes)} files")

    return fixed_count, rpc_fixes
```

## Common JavaScript Errors and Fixes

### Error: "Service rpc is not available"
```javascript
// Problem
this.rpc = useService("rpc");

// Solution
// Remove the line and add _jsonRpc helper method
```

### Error: "Cannot find module"
```javascript
// Problem
import {slug} from "@web_editor/js/common/utils";

// Solution
// Create compatibility function
function slug(value) {
    return value.toLowerCase().replace(/\s+/g, '-');
}
```

### Error: "Registry category not found"
```javascript
// Problem
registry.category("custom_category").add("name", Component);

// Solution
// Use standard categories
registry.category("public_components").add("name", Component);
registry.category("actions").add("name", Component);
registry.category("services").add("name", Service);
```

## Testing JavaScript After Migration

```javascript
// Add console logs to verify execution
console.log("Component loaded:", this.constructor.name);
console.log("Data fetched:", result);

// Check for errors in browser console
// F12 -> Console tab

// Verify network requests
// F12 -> Network tab -> Check JSON-RPC calls
```

## Performance Optimization

```javascript
// Cache API responses
const cache = new Map();

async _jsonRpcCached(endpoint, params = {}) {
    const cacheKey = `${endpoint}:${JSON.stringify(params)}`;

    if (cache.has(cacheKey)) {
        return cache.get(cacheKey);
    }

    const result = await this._jsonRpc(endpoint, params);
    cache.set(cacheKey, result);

    // Clear cache after 5 minutes
    setTimeout(() => cache.delete(cacheKey), 300000);

    return result;
}
```
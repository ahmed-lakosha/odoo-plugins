---
name: odoo-upgrade
description: "Comprehensive Odoo ERP upgrade assistant for migrating modules between Odoo versions (14-19). Handles XML views, Python API changes, JavaScript/OWL components, theme SCSS variables, manifest updates, security implementations, and database migrations. Use when user asks to upgrade Odoo modules, fix version compatibility issues, migrate themes between versions, or resolve Odoo 17/18/19 migration errors. Specializes in frontend RPC service migrations, view XML transformations, theme variable restructuring, and portal template XPath fixes."
version: "4.0.0"
author: "TAQAT Techno"
license: "MIT"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
metadata:
  odoo-versions: ["14", "15", "16", "17", "18", "19"]
  transformation-patterns: 150
  auto-fixes: 75
---

# Odoo Upgrade Assistant v4.0

A comprehensive skill for upgrading Odoo modules between versions, with extensive pattern recognition, automated fixes, and deep integration with Odoo's architecture for common migration issues.

## Version Compatibility Matrix

| Odoo Version | Python | PostgreSQL | Bootstrap | Owl | Status |
|--------------|--------|------------|-----------|-----|--------|
| 14.0 | 3.7-3.10 | 13+ | 4.5.0 | experimental | Legacy |
| 15.0 | 3.8-3.11 | 13+ | 5.0.2 | experimental | Legacy |
| 16.0 | 3.9-3.12 | 13+ | 5.1.3 | v1 | Stable |
| 17.0 | 3.10-3.13 | 13+ | 5.1.3 | v1 | Active |
| 18.0 | 3.10-3.13 | 13+ | 5.1.3 | v2 | Active |
| 19.0 | 3.10-3.13 | 13+ | 5.1.3 | v2 | Latest |

## When to Use This Skill

Activate this skill when:
- User requests upgrading Odoo modules between versions (14→19)
- Fixing Odoo version compatibility errors
- Migrating themes or custom modules to newer versions
- Resolving RPC service errors in frontend components
- Converting XML views for newer Odoo versions (tree→list, search groups)
- Updating SCSS variables for Odoo 18/19 themes
- Fixing portal view XPath inheritance errors
- Updating mail template helper functions
- Migrating JavaScript from Owl v1 to v2

## Upgrade Workflow

### 1. Initial Analysis
```bash
# Analyze source module structure
- Check __manifest__.py version
- Identify module dependencies
- List all file types (XML, Python, JS, SCSS)
- Create backup before changes
```

### 2. Manifest Updates

#### Standard Manifest Fields (Odoo 19 TaqaTechno Standard)
```python
{
    'name': 'Module Display Name',
    'version': '19.0.1.0.0',          # Format: ODOO_VERSION.MAJOR.MINOR.PATCH
    'summary': 'Brief description',
    'category': 'Category Name',
    'author': 'TaqaTechno',            # REQUIRED for Odoo 19
    'website': 'https://www.taqatechno.com/',  # REQUIRED
    'support': 'info@taqatechno.com',  # REQUIRED
    'license': 'LGPL-3',               # REQUIRED
    'contributors': [                   # Names only, NO emails
        'Developer Name',
    ],
    'depends': ['base', 'other_module'],
    'data': [
        'security/group_*.xml',        # User groups first
        'security/ir.model.access.csv', # Model access
        'security/rules_*.xml',        # Record rules
        'views/*.xml',                 # UI views
        'data/*.xml',                  # Default data
    ],
    'assets': {
        'web.assets_frontend': [
            'module_name/static/src/js/*.js',
            'module_name/static/src/scss/*.scss',
        ],
        'web._assets_primary_variables': [
            'module_name/static/src/scss/primary_variables.scss',
        ],
        'web._assets_frontend_helpers': [
            'module_name/static/src/scss/bootstrap_overridden.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
```

#### Version String Migration
```python
# Odoo 14: '14.0.1.0.0'
# Odoo 15: '15.0.1.0.0'
# Odoo 16: '16.0.1.0.0'
# Odoo 17: '17.0.1.0.0'
# Odoo 18: '18.0.1.0.0'
# Odoo 19: '19.0.1.0.0'
```

### 3. XML/View Transformations

#### Search Views (Odoo 19)
```xml
<!-- BEFORE (Invalid in Odoo 19) -->
<search>
    <group expand="0" string="Group By">
        <filter name="type" string="Type"/>
    </group>
</search>

<!-- AFTER (Valid in Odoo 19) -->
<search>
    <filter name="type" string="Type"/>
</search>
```

#### Tree to List Views (Comprehensive)
```xml
<!-- 1. View Template Tags -->
<!-- BEFORE -->
<tree string="Title" edit="1" editable="top">
    <field name="name"/>
</tree>

<!-- AFTER -->
<list string="Title" editable="top">
    <field name="name"/>
</list>

<!-- 2. Action Window view_mode -->
<!-- BEFORE -->
<record id="action_my_model" model="ir.actions.act_window">
    <field name="view_mode">tree,form,kanban</field>
</record>

<!-- AFTER -->
<record id="action_my_model" model="ir.actions.act_window">
    <field name="view_mode">list,form,kanban</field>
</record>

<!-- 3. XPath Expressions (CRITICAL for Odoo 18/19) -->
<!-- BEFORE -->
<xpath expr="//tree" position="inside">
    <field name="new_field"/>
</xpath>
<xpath expr="//tree/field[@name='name']" position="after">
    <field name="other_field"/>
</xpath>

<!-- AFTER -->
<xpath expr="//list" position="inside">
    <field name="new_field"/>
</xpath>
<xpath expr="//list/field[@name='name']" position="after">
    <field name="other_field"/>
</xpath>

<!-- 4. Search View Group expand Attribute (Deprecated) -->
<!-- BEFORE -->
<group expand="0" string="Group By">
    <filter name="group_status" context="{'group_by': 'state'}"/>
</group>

<!-- AFTER -->
<group string="Group By">
    <filter name="group_status" context="{'group_by': 'state'}"/>
</group>
```

#### Python view_mode Dictionary (Odoo 18/19)
```python
# BEFORE
def action_view_records(self):
    return {
        'type': 'ir.actions.act_window',
        'res_model': 'my.model',
        'view_mode': 'tree,form',
        'view_type': 'tree',  # Deprecated parameter
    }

# AFTER
def action_view_records(self):
    return {
        'type': 'ir.actions.act_window',
        'res_model': 'my.model',
        'view_mode': 'list,form',
        # view_type parameter removed
    }
```

#### Kanban Templates (Odoo 19)
```xml
<!-- BEFORE -->
<t t-name="kanban-box">

<!-- AFTER -->
<t t-name="card">
```

#### Form View Context (Odoo 19)
```xml
<!-- BEFORE -->
context="{'search_default_type_id': active_id}"

<!-- AFTER -->
context="{'search_default_type_id': id}"
```

#### Cron Jobs (Odoo 19)
Remove `numbercall` field - no longer supported:
```xml
<!-- Remove this line -->
<field name="numbercall">-1</field>
```

### 4. Python API Migrations

#### Slug Function (Odoo 18+)
```python
# Add compatibility wrapper
from odoo.http import request

def slug(value):
    """Compatibility wrapper for slug function"""
    return request.env['ir.http']._slug(value)

def unslug(value):
    """Compatibility wrapper for unslug function"""
    return request.env['ir.http']._unslug(value)
```

#### URL For Function (Odoo 19)
```python
# BEFORE
from odoo.addons.http_routing.models.ir_http import url_for
url = url_for('/path')

# AFTER
url = self.env['ir.http']._url_for('/path')
```

### 5. JavaScript/OWL Frontend Migrations

#### RPC Service Replacement (Odoo 19)
The RPC service is NOT available in Odoo 19 frontend/public components.

```javascript
/** @odoo-module **/

// BEFORE (Odoo 17)
import {useService} from "@web/core/utils/hooks";

export class MyComponent extends Component {
    setup() {
        this.rpc = useService("rpc");
    }

    async fetchData() {
        const data = await this.rpc("/api/endpoint", params);
    }
}

// AFTER (Odoo 19)
export class MyComponent extends Component {
    setup() {
        // RPC service removed - using fetch instead
    }

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
    }

    async fetchData() {
        const data = await this._jsonRpc("/api/endpoint", params);
    }
}
```

#### OWL 1.x → OWL 2.0 Lifecycle Hook Migration (Odoo 18+)

OWL 2.0 (used in Odoo 18+) renames all lifecycle hooks and changes the constructor signature. This is a **breaking change** — old method names simply won't be called.

**Lifecycle Hook Rename Table:**

| OWL 1.x (Odoo 14-17) | OWL 2.0 (Odoo 18-19) | Notes |
|----------------------|----------------------|-------|
| `constructor(parent, props)` | `setup()` | No `super()` needed |
| `willStart()` | `onWillStart(callback)` | Now uses `onWillStart` hook function |
| `mounted()` | `onMounted(callback)` | Now uses `onMounted` hook function |
| `willUpdateProps(nextProps)` | `onWillUpdateProps(callback)` | Callback receives `nextProps` |
| `patched()` | `onPatched(callback)` | Now uses `onPatched` hook function |
| `willUnmount()` | `onWillUnmount(callback)` | Now uses `onWillUnmount` hook function |
| `willPatch()` | `onWillPatch(callback)` | Now uses `onWillPatch` hook function |
| `destroyed()` | `onDestroyed(callback)` | Now uses `onDestroyed` hook function |

**Before (OWL 1.x — Odoo 14-17):**
```javascript
/** @odoo-module **/
import { Component } from "@odoo/owl";

export class MyWidget extends Component {
    constructor(parent, props) {
        super(...arguments);
        this.state = { count: 0 };
    }

    async willStart() {
        this.data = await this._loadData();
    }

    mounted() {
        this._setupListeners();
    }

    patched() {
        this._updateDOM();
    }

    willUnmount() {
        this._cleanupListeners();
    }
}
```

**After (OWL 2.0 — Odoo 18-19):**
```javascript
/** @odoo-module **/
import { Component, onMounted, onPatched, onWillStart, onWillUnmount, useState } from "@odoo/owl";

export class MyWidget extends Component {
    setup() {
        // useState replaces this.state = {}
        this.state = useState({ count: 0 });

        onWillStart(async () => {
            this.data = await this._loadData();
        });

        onMounted(() => {
            this._setupListeners();
        });

        onPatched(() => {
            this._updateDOM();
        });

        onWillUnmount(() => {
            this._cleanupListeners();
        });
    }
}
```

**Key OWL 2.0 Import Changes:**
```javascript
// OLD — OWL 1.x
import { Component } from "@odoo/owl";

// NEW — OWL 2.0 (import hooks explicitly)
import {
    Component,
    useState,
    useRef,
    useEnv,
    onMounted,
    onPatched,
    onWillStart,
    onWillUpdateProps,
    onWillPatch,
    onWillUnmount,
    onDestroyed,
} from "@odoo/owl";
```

**Auto-fix command:**
```bash
python scripts/auto_fix_library.py --fix owl_lifecycle <project_path>
```

**Detection command:**
```bash
python scripts/odoo19_precheck.py <project_path>
# Look for: [HIGH] OWL 1.x lifecycle methods found
```

### 6. Theme SCSS Variables (Odoo 19)

#### Proper Structure
```scss
// ===================================================================
// Theme Name - Primary Variables
// ===================================================================

// Typography Hierarchy
$o-theme-h1-font-size-multiplier: (64 / 16);
$o-theme-headings-font-weight: 700;  // NOT $headings-font-weight

// Website Values Palette
$o-website-values-palettes: (
    (
        'color-palettes-name': 'my_theme',
        'font': 'Inter',
        'headings-font': 'Inter',
        'btn-padding-y': 1rem,  // Use rem not px
        'btn-padding-x': 2rem,
    ),
);

// Color Palette with menu/footer assignments
$o-color-palettes: map-merge($o-color-palettes, (
    'my_theme': (
        'o-color-1': #124F81,
        'o-color-2': #B1025D,
        'o-color-3': #f8fafc,
        'o-color-4': #ffffff,
        'o-color-5': #1e293b,
        'menu': 1,        // IMPORTANT: Specify which color for menu
        'footer': 4,      // IMPORTANT: Specify which color for footer
        'copyright': 5,   // IMPORTANT: Specify which color for copyright
    ),
));

// Font Configuration (use map-merge!)
$o-theme-font-configs: map-merge($o-theme-font-configs, (
    'Inter': (
        'family': ('Inter', sans-serif),
        'url': 'Inter:300,400,500,600,700&display=swap',
        'properties': (  // IMPORTANT: Add properties section
            'base': (
                'font-size-base': 1rem,
                'line-height-base': 1.6,
            ),
        )
    ),
));
```

### 7. Theme Snippet System (Odoo 19)

Remove incompatible `website.snippet_options` inheritance:
```xml
<!-- REMOVE this template - not compatible with Odoo 19 -->
<template id="custom_footer_op" inherit_id="website.snippet_options">
    <!-- Snippet options content -->
</template>
```

## Common Errors and Solutions

### Error: "Service rpc is not available"
- **Cause**: Using `useService("rpc")` in frontend components
- **Solution**: Replace with `_jsonRpc` helper method using fetch API

### Error: "Invalid field 'numbercall' in 'ir.cron'"
- **Cause**: Field removed in Odoo 19
- **Solution**: Remove `<field name="numbercall">` from cron definitions

### Error: "Invalid view definition" (search views)
- **Cause**: `<group>` tags not allowed in search views (Odoo 19)
- **Solution**: Remove `<group>` tags, keep filters at root level

### Error: "Missing 'card' template"
- **Cause**: Kanban template name changed in Odoo 19
- **Solution**: Change `t-name="kanban-box"` to `t-name="card"`

### Error: "cannot import name 'slug'"
- **Cause**: Import location changed in Odoo 18+
- **Solution**: Add compatibility wrapper function

### Error: "External ID not found: website.snippet_options"
- **Cause**: Snippet system changed in Odoo 19
- **Solution**: Remove the incompatible template

### Error: "field 'active_id' does not exist"
- **Cause**: `active_id` not available in form view contexts (Odoo 19)
- **Solution**: Replace `active_id` with `id`

## Testing Checklist

After upgrade, test:
- [ ] Module installation without errors
- [ ] All views load correctly
- [ ] JavaScript components function
- [ ] Theme displays properly
- [ ] API endpoints respond
- [ ] Cron jobs execute
- [ ] Search/filter functionality
- [ ] Form submissions work
- [ ] Reports generate correctly

## Helper Commands

```bash
# Install upgraded module
python -m odoo -d [DB] -i [MODULE] --addons-path=odoo/addons,projects/[PROJECT] --stop-after-init

# Update module after changes
python -m odoo -d [DB] -u [MODULE] --stop-after-init

# Run with development mode for debugging
python -m odoo -d [DB] --dev=xml,css,js

# Install Python dependencies
pip install geopy spacy hachoir
```

## Migration Report Template

Generate comprehensive reports documenting:
- Files modified count
- Lines changed
- Patterns applied
- Manual fixes needed
- External dependencies added
- Testing status
- Known issues
- Rollback instructions

## Advanced Patterns

### Multi-Module Projects
When upgrading projects with multiple interdependent modules:
1. Analyze dependency tree
2. Upgrade in dependency order
3. Test each module individually
4. Test integrated functionality

### Theme Migrations
Special considerations for themes:
1. SCSS variable structure changes
2. Bootstrap version compatibility
3. Snippet system updates
4. Asset bundling changes

### Performance Optimization
After upgrade:
1. Regenerate assets
2. Clear caches
3. Recompile Python files
4. Optimize database indexes

## Version-Specific Notes

### Odoo 14 → 15
- **Bootstrap 4.x → 5.x** (major CSS class changes)
- QWeb syntax: `t-use-call` removed, use `t-call`
- Payment Provider API changes
- Left/Right classes → Start/End for RTL support

### Odoo 15 → 16
- Bootstrap 5.1.3 standardization
- Web framework module reorganization
- Website page template changes
- Payment flow updates
- Owl v1 adoption begins

### Odoo 16 → 17
- OWL framework v1 fully adopted
- Widget system changes
- Asset pipeline updates
- publicWidget API stabilization
- Theme color palette improvements

### Odoo 17 → 18
- Owl v1 → v2 migration starts
- Minor XML changes
- Python API mostly compatible
- JavaScript minor updates
- Snippet group system introduced

### Odoo 18 → 19
- **Major frontend architecture changes**
- RPC service REMOVED from public components
- Snippet system overhaul (groups required)
- Kanban template: `kanban-box` → `card`
- Search view: `<group>` tags NOT allowed
- `<tree>` views → `<list>` views
- XPath expressions: `//tree` → `//list`
- Portal view templates completely restructured
- Mail template helpers: remove `env` parameter
- Cron jobs: `numbercall` field removed

## Security Implementation (Required for All Versions)

### 1. Model Access (ir.model.access.csv)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_admin,my.model.admin,model_my_model,base.group_erp_manager,1,1,1,1
```

### 2. User Groups (security/group_*.xml)
```xml
<record id="group_my_manager" model="res.groups">
    <field name="name">My Manager</field>
    <field name="category_id" ref="base.module_category_services"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### 3. Record Rules (security/rules_*.xml)
```xml
<record id="my_model_rule" model="ir.rule">
    <field name="name">My Model: User own records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

## Portal View XPath Migration (Odoo 19)

### Sale Portal Template Changes

The sale portal templates have been completely restructured in Odoo 19:

#### Table Header XPaths
```xml
<!-- BEFORE (Odoo 17/18) - Positional selectors -->
<xpath expr="//table[@id='sales_order_table']/thead/tr/th[3]" position="attributes">

<!-- AFTER (Odoo 19) - Named element selectors -->
<xpath expr="//table[@id='sales_order_table']/thead/tr/th[@id='product_unit_price_header']" position="attributes">
```

**Available Header IDs:**
- `th[@id='product_qty_header']` - Quantity
- `th[@id='product_unit_price_header']` - Unit Price
- `th[@id='product_discount_header']` - Discount %
- `th[@id='taxes_header']` - Taxes
- `th[@id='subtotal_header']` - Amount/Subtotal

#### Table Body XPaths
```xml
<!-- BEFORE (Odoo 17/18) -->
<xpath expr="//table[@id='sales_order_table']/tbody//t[@t-foreach='lines_to_report']//tr/t[@t-if='not line.display_type']/td[3]" position="attributes">

<!-- AFTER (Odoo 19) -->
<xpath expr="//table[@id='sales_order_table']/tbody//tr[@name='tr_product']/td[@name='td_product_priceunit']" position="attributes">
```

**Available Body Element Names:**
- `tr[@name='tr_product']` - Product row
- `tr[@name='tr_section']` - Section row
- `tr[@name='tr_note']` - Note row
- `td[@name='td_product_name']` - Product name
- `td[@name='td_product_quantity']` - Quantity
- `td[@name='td_product_priceunit']` - Unit price
- `td[@name='td_product_discount']` - Discount %
- `td[@name='td_product_taxes']` - Taxes
- `td[@name='td_product_subtotal']` - Subtotal

## Mail Template Migration (Odoo 19)

### Helper Function Changes
```xml
<!-- BEFORE (Odoo 17/18) - FAILS in Odoo 19 -->
<t t-out="format_datetime(env, object.date_start, dt_format='long')"/>
<t t-out="format_date(env, object.date_start)"/>
<t t-out="format_amount(env, object.amount, object.currency_id)"/>

<!-- AFTER (Odoo 19) - Remove env parameter -->
<t t-out="format_datetime(object.date_start, dt_format='long')"/>
<t t-out="format_date(object.date_start)"/>
<t t-out="format_amount(object.amount, object.currency_id)"/>
```

### XML Entity Encoding
```xml
<!-- BEFORE - HTML entities (FAILS in XML) -->
<p>&copy; 2025 Company Name</p>
<p>Company&nbsp;Name</p>

<!-- AFTER - Numeric character references -->
<p>&#169; 2025 Company Name</p>
<p>Company&#160;Name</p>
```

**Common Character Codes:**
- `©` → `&#169;` (copyright)
- ` ` → `&#160;` (non-breaking space)
- `—` → `&#8212;` (em dash)
- `™` → `&#8482;` (trademark)
- `€` → `&#8364;` (euro)

## Bootstrap 4 → 5 Class Migration

| Bootstrap 4 | Bootstrap 5 | Description |
|-------------|-------------|-------------|
| `ml-*` | `ms-*` | Margin Left → Start |
| `mr-*` | `me-*` | Margin Right → End |
| `pl-*` | `ps-*` | Padding Left → Start |
| `pr-*` | `pe-*` | Padding Right → End |
| `text-left` | `text-start` | Text align left |
| `text-right` | `text-end` | Text align right |
| `float-left` | `float-start` | Float left |
| `float-right` | `float-end` | Float right |
| `form-group` | `mb-3` | Form group spacing |
| `custom-select` | `form-select` | Custom select |
| `close` | `btn-close` | Close button |
| `badge-primary` | `bg-primary` | Primary badge |
| `font-weight-bold` | `fw-bold` | Bold text |
| `sr-only` | `visually-hidden` | Screen reader only |
| `no-gutters` | `g-0` | No gutters in grid |

## Helper Commands

```bash
# Pre-check for compatibility issues
python scripts/odoo19_precheck.py <project_path>

# Quick targeted fixes
python scripts/quick_fix_odoo19.py <project_path>

# Full comprehensive upgrade
python scripts/upgrade_to_odoo19.py <project_path>

# Update manifest versions
python scripts/upgrade_manifest.py <project_path> 19.0

# Fix RPC service migrations
python scripts/fix_rpc_service.py <project_path>

# Install upgraded module
python -m odoo -d [DB] -i [MODULE] --addons-path=odoo/addons,projects/[PROJECT] --stop-after-init

# Update module after changes
python -m odoo -d [DB] -u [MODULE] --stop-after-init

# Run with development mode for debugging
python -m odoo -d [DB] --dev=all
```

## Migration Report Template

Generate comprehensive reports documenting:
- Files modified count
- Lines changed
- Patterns applied
- Manual fixes needed
- External dependencies added
- Testing status
- Known issues
- Rollback instructions

## References

- [Patterns Documentation](./patterns/common_patterns.md)
- [Odoo 18 to 19 Patterns](./patterns/odoo18_to_19.md)
- [JavaScript Fixes](./fixes/javascript_fixes.md)
- [XML Fixes](./fixes/xml_fixes.md)
- [Error Catalog](./reference/error_catalog.md)
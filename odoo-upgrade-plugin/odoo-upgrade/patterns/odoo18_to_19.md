# Odoo 18 to 19 Migration Patterns

## 🔴 CRITICAL Breaking Changes (Must Fix)

### 1. XML View Type Renamed
**Impact**: CRITICAL - Installation will fail
**Error**: `Invalid view type: 'tree'`

#### Issue
- ALL `<tree>` view tags have been renamed to `<list>` in Odoo 19
- Affects all tree view definitions

#### Detection
```bash
grep -r "<tree" --include="*.xml"
grep -r "</tree>" --include="*.xml"
```

#### Fix
```xml
<!-- BEFORE (Odoo 17/18) -->
<tree string="Items" editable="top">
    <field name="name"/>
</tree>

<!-- AFTER (Odoo 19) -->
<list string="Items" editable="top">
    <field name="name"/>
</list>
```

### 2. Search View Group Tags Removed
**Impact**: CRITICAL - Installation will fail
**Error**: `Invalid view definition`

#### Issue
- `<group>` tags are NO LONGER ALLOWED inside `<search>` views
- All filters must be at root level

#### Detection
```bash
grep -A5 -B5 "<group.*Group By" --include="*.xml"
```

#### Fix
```xml
<!-- BEFORE (Odoo 17/18) -->
<search>
    <field name="name"/>
    <group expand="0" string="Group By">
        <filter name="type" string="Type" context="{'group_by': 'type_id'}"/>
    </group>
</search>

<!-- AFTER (Odoo 19) -->
<search>
    <field name="name"/>
    <separator/>
    <filter name="type" string="Group by Type" context="{'group_by': 'type_id'}"/>
</search>
```

### 3. Action Window view_mode References
**Impact**: CRITICAL - Runtime error
**Error**: `View types not defined tree found in act_window`

#### Issue
- Action windows still reference 'tree' in view_mode field
- Must be changed to 'list' for Odoo 19 compatibility

#### Detection
```bash
grep -r "view_mode.*tree" --include="*.xml"
```

#### Fix
```xml
<!-- BEFORE (Odoo 17/18) -->
<field name="view_mode">tree,form</field>
<field name="view_mode">kanban,tree,form</field>

<!-- AFTER (Odoo 19) -->
<field name="view_mode">list,form</field>
<field name="view_mode">kanban,list,form</field>
```

### 4. XPath Expressions with //tree (CRITICAL - NEW)
**Impact**: CRITICAL - View inheritance will fail
**Error**: `Element '<xpath expr="//tree">' cannot be located in parent view`

#### Issue
- XPath expressions in view inheritance still reference `//tree`
- Parent views now use `<list>` tags, so `//tree` no longer exists
- This is a COMMON error missed by developers

#### Detection
```bash
grep -r "xpath.*//tree" --include="*.xml"
grep -r 'xpath.*expr="//tree' --include="*.xml"
```

#### Fix
```xml
<!-- BEFORE (Odoo 17/18) - FAILS in Odoo 19 -->
<record id="view_inherit" model="ir.ui.view">
    <field name="inherit_id" ref="module.view_tree"/>
    <field name="arch" type="xml">
        <xpath expr="//tree" position="inside">
            <field name="new_field"/>
        </xpath>
    </field>
</record>

<!-- AFTER (Odoo 19) - WORKS -->
<record id="view_inherit" model="ir.ui.view">
    <field name="inherit_id" ref="module.view_tree"/>
    <field name="arch" type="xml">
        <xpath expr="//list" position="inside">
            <field name="new_field"/>
        </xpath>
    </field>
</record>

<!-- Also applies to complex xpath expressions -->
<xpath expr="//tree/field[@name='name']" position="after">
<!-- Must become -->
<xpath expr="//list/field[@name='name']" position="after">
```

### 5. Python view_mode Dictionaries (CRITICAL - NEW)
**Impact**: CRITICAL - Runtime error in smart buttons and actions
**Error**: View type 'tree' not found

#### Issue
- Python code returning action dictionaries with `'view_mode': 'tree'`
- Smart button actions, wizard actions, etc. will fail
- NOT detected by standard XML checks

#### Detection
```bash
grep -r "'view_mode'.*'tree" --include="*.py"
grep -r '"view_mode".*"tree' --include="*.py"
```

#### Fix
```python
# BEFORE (Odoo 17/18) - BREAKS in Odoo 19
def action_view_subscriptions(self):
    return {
        'type': 'ir.actions.act_window',
        'res_model': 'disaster.relief.request',
        'view_mode': 'tree,form',  # ❌ BREAKS
        'domain': [('id', 'in', self.subscribed_request_ids.ids)],
    }

# AFTER (Odoo 19) - WORKS
def action_view_subscriptions(self):
    return {
        'type': 'ir.actions.act_window',
        'res_model': 'disaster.relief.request',
        'view_mode': 'list,form',  # ✅ WORKS
        'domain': [('id', 'in', self.subscribed_request_ids.ids)],
    }
```

### 6. Search View Group expand Attribute (HIGH - DEPRECATED)
**Impact**: HIGH - Deprecated attribute
**Error**: Warning in logs

#### Issue
- The `expand` attribute on `<group>` tags in search views is deprecated
- Should be removed even though groups themselves are removed

#### Detection
```bash
grep -r 'expand="[01]"' --include="*.xml"
```

#### Fix
```xml
<!-- BEFORE (Odoo 17/18) -->
<group expand="0" string="Group By">
    <filter name="status" context="{'group_by': 'state'}"/>
</group>

<!-- AFTER (Odoo 19) -->
<group string="Group By">
    <filter name="status" context="{'group_by': 'state'}"/>
</group>

<!-- Or better yet, remove group entirely (per pattern #2) -->
<separator/>
<filter name="status" string="Group by Status" context="{'group_by': 'state'}"/>
```

### 7. Cron Job numbercall Field Removed
**Impact**: HIGH - Installation will fail
**Error**: `Invalid field 'numbercall' in 'ir.cron'`

#### Issue
- The `numbercall` field has been completely removed from cron jobs

#### Detection
```bash
grep -r "numbercall" --include="*.xml"
```

#### Fix
```xml
<!-- BEFORE (Odoo 17/18) -->
<record id="cron_job" model="ir.cron">
    <field name="name">My Cron Job</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field> <!-- REMOVE THIS LINE -->
</record>

<!-- AFTER (Odoo 19) -->
<record id="cron_job" model="ir.cron">
    <field name="name">My Cron Job</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <!-- numbercall field removed -->
</record>
```

## 🟡 Major Changes

### 4. RPC Service Removal in Frontend
**Impact**: HIGH
**Affected**: All public website components using RPC

The `rpc` service is no longer available in frontend/public components in Odoo 19.

#### Detection
```javascript
grep -r "useService.*['\"]rpc['\"]" --include="*.js"
```

#### Solution
Replace with fetch-based JSON-RPC calls. Add this helper to each affected component:

```javascript
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
```

### 5. Kanban Template Name Change
**Impact**: MEDIUM

#### Issue
- Kanban box template name changed from `kanban-box` to `card`

#### Fix
```xml
<!-- BEFORE -->
<t t-name="kanban-box">

<!-- AFTER -->
<t t-name="card">
```

### 6. URL Generation Changes
**Impact**: MEDIUM

#### Issue
- `url_for` import location changed and should use IR.http service

#### Fix
```python
# BEFORE
from odoo.addons.http_routing.models.ir_http import url_for
url = url_for('/path')

# AFTER
url = self.env['ir.http']._url_for('/path')
```

### 7. Context active_id Changes
**Impact**: LOW

#### Issue
- `active_id` not available in some form view contexts

#### Fix
```xml
<!-- BEFORE -->
context="{'default_type_id': active_id}"

<!-- AFTER -->
context="{'default_type_id': id}"
```

## 🟢 Theme/SCSS Changes

### 8. SCSS Variable Updates
**Impact**: LOW

#### Issue
- Some SCSS variables renamed for consistency

#### Fix
```scss
// BEFORE
$headings-font-weight: 700;

// AFTER
$o-theme-headings-font-weight: 700;
```

### 9. Color Palette Menu/Footer
**Impact**: LOW

#### Issue
- Themes need explicit menu/footer color assignments

#### Fix
```scss
$o-color-palettes: (
    'my_theme': (
        'o-color-1': #207AB7,
        'o-color-2': #FB9F54,
        'o-color-3': #F6F4F0,
        'o-color-4': #ffffff,
        'o-color-5': #191A19,
        'menu': 4,        // Add these
        'footer': 1,      // Add these
        'copyright': 5,   // Add these
    ),
);
```

## 🔴 CRITICAL Mail Template Issues (NEW - Must Fix)

### 10. Mail Template Helper Functions - Invalid env Parameter
**Impact**: CRITICAL - Template rendering fails
**Error**: `AttributeError: 'Environment' object has no attribute 'tzinfo'`

#### Issue
- Mail template helper functions changed in Odoo 19
- `format_datetime()`, `format_date()`, `format_amount()` should NOT receive `env` parameter
- The helpers access environment internally - passing it causes attribute errors

#### Detection
```bash
grep -r "format_datetime(env," --include="*.xml"
grep -r "format_date(env," --include="*.xml"
grep -r "format_amount(env," --include="*.xml"
```

#### Fix
```xml
<!-- BEFORE (Odoo 17/18) - FAILS with AttributeError -->
<t t-out="format_datetime(env, object.date_start, dt_format='long')">
    January 15, 2025 at 2:30:00 PM
</t>
<t t-out="format_date(env, object.date_start)">2025-01-15</t>
<t t-out="format_amount(env, object.amount, object.currency_id)">$100.00</t>

<!-- AFTER (Odoo 19) - WORKS -->
<t t-out="format_datetime(object.date_start, dt_format='long')">
    January 15, 2025 at 2:30:00 PM
</t>
<t t-out="format_date(object.date_start)">2025-01-15</t>
<t t-out="format_amount(object.amount, object.currency_id)">$100.00</t>
```

**Common Locations**:
- Email templates in `data/mail_template_*.xml`
- Report templates in `report/*.xml`
- Website templates with dynamic dates/amounts

### 11. XML Entity Encoding Issues
**Impact**: CRITICAL - XML parsing fails
**Error**: `lxml.etree.XMLSyntaxError: Entity 'copy' not defined, line X`

#### Issue
- HTML entities like `&copy;`, `&nbsp;`, `&mdash;` are NOT valid in XML
- Only 5 predefined XML entities exist: `&lt;`, `&gt;`, `&amp;`, `&quot;`, `&apos;`
- All other special characters must use numeric character references

#### Detection
```bash
grep -r "&copy;" --include="*.xml"
grep -r "&nbsp;" --include="*.xml"
grep -r "&mdash;" --include="*.xml"
grep -r "&trade;" --include="*.xml"
```

#### Fix
```xml
<!-- BEFORE - FAILS in XML parsing -->
<p>© 2025 Company Name</p>
<p>Company&nbsp;Name</p>
<p>Price: 100&mdash;200</p>

<!-- AFTER - WORKS -->
<p>&#169; 2025 Company Name</p>
<p>Company&#160;Name</p>
<p>Price: 100&#8212;200</p>
```

**Common Character Codes**:
- `©` → `&#169;` (copyright)
- `nbsp` (non-breaking space) → `&#160;`
- `—` (em dash) → `&#8212;`
- `™` (trademark) → `&#8482;`
- `€` (euro) → `&#8364;`

### 12. XML Domain Method Calls Not Allowed
**Impact**: HIGH - Search filters fail
**Error**: `Invalid domain: closing parenthesis ']' does not match opening '('`

#### Issue
- XML domains are parsed at load time, NOT runtime
- Cannot use Python method calls like `.strftime()`, `.get()`, functions, etc.
- Context variables like `context_today` are available but cannot have methods called on them

#### Detection
```bash
grep -r "context_today()\.strftime" --include="*.xml"
grep -r "\.get(" --include="*.xml" | grep "domain="
```

#### Fix - Use Odoo's Date Filter Widget
```xml
<!-- BEFORE - FAILS with domain parsing error -->
<search>
    <filter name="filter_today" string="Today"
            domain="[('date_field', '>=', context_today().strftime('%Y-%m-%d'))]"/>
    <filter name="filter_this_week" string="This Week"
            domain="[('date_field', '>=', (context_today - datetime.timedelta(days=7)).strftime('%Y-%m-%d'))]"/>
</search>

<!-- AFTER - WORKS with built-in date filter widget -->
<search>
    <separator/>
    <!-- Odoo provides automatic date range dropdown: Today, This Week, This Month, etc. -->
    <filter name="date_field" string="Date" date="date_field"/>
</search>
```

**Date Filter Widget Benefits**:
- Automatic dropdown with: Today, This Week, This Month, Quarter, Year
- Custom date range picker
- No XML domain parsing issues
- Standard Odoo UX
- Better user experience than single "Today" filter

## 🔴 CRITICAL Portal View XPath Changes (NEW - Must Fix)

### 13. Sale Portal Template Structure Changed
**Impact**: CRITICAL - Portal view inheritance fails
**Error**: `Element '<xpath expr="..."/>' cannot be located in parent view`

#### Issue
- Complete restructure of sale portal templates in Odoo 19
- Removed wrapper conditionals: `<t t-if='not line.display_type'>`
- Now uses named elements with `name="tr_product"` and `name="td_product_*"`
- All positional XPath selectors (td[3], th[3]) must be updated
- Sidebar structure changed - no more `data-id` attributes

#### Detection
```bash
# Detect old portal XPath patterns
grep -r "t-if='not line.display_type'" --include="*.xml"
grep -r "data-id='total_amount'" --include="*.xml"
grep -r "sales_order_table.*th\[" --include="*.xml"
```

#### Fix - Table Header XPaths
```xml
<!-- BEFORE (Odoo 17/18) - Positional selectors FAIL -->
<xpath expr="//table[@id='sales_order_table']/thead/tr/th[3]" position="attributes">
    <attribute name="t-if">condition</attribute>
</xpath>

<!-- AFTER (Odoo 19) - Named element selectors WORK -->
<xpath expr="//table[@id='sales_order_table']/thead/tr/th[@id='product_unit_price_header']" position="attributes">
    <attribute name="t-if">condition</attribute>
</xpath>

<!-- Other header IDs -->
th[@id='product_qty_header']        <!-- Quantity -->
th[@id='product_unit_price_header'] <!-- Unit Price -->
th[@id='product_discount_header']   <!-- Discount % -->
th[@id='taxes_header']              <!-- Taxes -->
th[@id='subtotal_header']           <!-- Amount/Subtotal -->
```

#### Fix - Table Body XPaths
```xml
<!-- BEFORE (Odoo 17/18) - Nested conditional wrapper FAILS -->
<xpath expr="//table[@id='sales_order_table']/tbody//t[@t-foreach='lines_to_report']//tr/t[@t-if='not line.display_type']/td[3]"
       position="attributes">
    <attribute name="t-if">condition</attribute>
</xpath>

<!-- AFTER (Odoo 19) - Direct named element selectors WORK -->
<xpath expr="//table[@id='sales_order_table']/tbody//tr[@name='tr_product']/td[@name='td_product_priceunit']"
       position="attributes">
    <attribute name="t-if">condition</attribute>
</xpath>

<!-- Other body element names -->
tr[@name='tr_product']               <!-- Product row -->
tr[@name='tr_section']               <!-- Section row -->
tr[@name='tr_note']                  <!-- Note row -->
tr[@name='tr_combo']                 <!-- Combo product row -->

td[@name='td_product_name']          <!-- Product name -->
td[@name='td_product_quantity']      <!-- Quantity -->
td[@name='td_product_priceunit']     <!-- Unit price -->
td[@name='td_product_discount']      <!-- Discount % -->
td[@name='td_product_taxes']         <!-- Taxes -->
td[@name='td_product_subtotal']      <!-- Subtotal -->
```

#### Fix - Sidebar XPaths
```xml
<!-- BEFORE (Odoo 17/18) - data-id attribute FAILS -->
<xpath expr="//h2[@data-id='total_amount']" position="attributes">
    <attribute name="t-if">condition</attribute>
</xpath>

<!-- AFTER (Odoo 19) - Template variable selector WORKS -->
<xpath expr="//t[@t-set='title']//h2[@t-field='sale_order.amount_total']" position="attributes">
    <attribute name="t-if">condition</attribute>
</xpath>

<!-- For adding content after title -->
<xpath expr="//t[@t-set='title']" position="after">
    <div class="alert alert-info">Custom content</div>
</xpath>
```

#### Fix - Optional Products (REMOVED)
```xml
<!--
IMPORTANT: Optional products portal structure NO LONGER EXISTS in Odoo 19
The sale_management module completely redesigned optional products

If you have XPaths like:
//t[@t-if='sale_order._can_be_edited_on_portal() and any((not option.is_present)...)']

These templates must be COMMENTED OUT or COMPLETELY REWRITTEN for Odoo 19
-->
```

**Complete Replacement Example**:
```xml
<!-- BEFORE (Odoo 17/18) -->
<template id="sale_portal_inherit" inherit_id="sale.sale_order_portal_content">
    <xpath expr="//table[@id='sales_order_table']/tbody//t[@t-foreach='lines_to_report']//tr/t[@t-if='not line.display_type']/td[3]"
           position="attributes">
        <attribute name="t-if">custom_condition</attribute>
    </xpath>
</template>

<!-- AFTER (Odoo 19) -->
<template id="sale_portal_inherit" inherit_id="sale.sale_order_portal_content">
    <xpath expr="//table[@id='sales_order_table']/tbody//tr[@name='tr_product']/td[@name='td_product_priceunit']"
           position="attributes">
        <attribute name="t-if">custom_condition</attribute>
    </xpath>
</template>
```

## Automated Upgrade Script

Use the comprehensive upgrade script:
```bash
python upgrade_to_odoo19.py /path/to/project
```

This script automatically handles:
- ✅ Tree to List view conversion
- ✅ Search view group removal
- ✅ Cron job numbercall removal
- ✅ RPC service migration
- ✅ Manifest version updates
- ✅ Python API updates
- ✅ SCSS variable fixes
- ✅ Controller type='json' → type='jsonrpc'
- ✅ attrs={} → inline invisible/required/readonly
- ✅ OWL 1.x lifecycle hook renames

## Quick Checklist

- [ ] Run upgrade script first
- [ ] Check for any remaining `<tree>` tags
- [ ] Verify no `<group>` in search views
- [ ] Remove all `numbercall` fields
- [ ] Test RPC calls in JavaScript
- [ ] Update manifest versions
- [ ] Test module installation
- [ ] Run tests
- [ ] Verify no `type='json'` in @http.route
- [ ] Verify no `attrs=` attributes in XML views
- [ ] Check OWL components use OWL 2.0 lifecycle hooks

---

## Pattern 14: Controller Type Migration (CRITICAL)

### Problem
Odoo 19 renamed the JSON-RPC controller type from `'json'` to `'jsonrpc'`.
Routes using `type='json'` will return 404 or error silently.

### Detection
```bash
grep -r "type='json'" controllers/ --include="*.py"
grep -r 'type="json"' controllers/ --include="*.py"
```

### Before (Odoo 17/18)
```python
from odoo import http
from odoo.http import request

class MyController(http.Controller):

    @http.route('/api/my/endpoint', type='json', auth='user', methods=['POST'])
    def my_endpoint(self, **kwargs):
        return {'status': 'ok'}

    @http.route('/web/dataset/call_kw', type='json', auth='user')
    def call_kw(self, model, method, args, kwargs):
        pass
```

### After (Odoo 19)
```python
from odoo import http
from odoo.http import request

class MyController(http.Controller):

    @http.route('/api/my/endpoint', type='jsonrpc', auth='user', methods=['POST'])
    def my_endpoint(self, **kwargs):
        return {'status': 'ok'}

    @http.route('/web/dataset/call_kw', type='jsonrpc', auth='user')
    def call_kw(self, model, method, args, kwargs):
        pass
```

### Auto-Fix
```bash
# Auto-fix with the library (replaces ONLY inside @http.route)
python auto_fix_library.py /path/to/module --specific controller_type

# Manual regex (safe - only matches inside @http.route decorators)
grep -rn "type='json'" controllers/ --include="*.py"
# Then replace type='json' with type='jsonrpc' in each file
```

### Notes
- Only affects `@http.route` decorators — do NOT change `type='json'` elsewhere
- Public JSON endpoints (`auth='public'`) also need this change
- Website controllers in `website_*` modules need this change

---

## Pattern 15: attrs={} → Inline Expressions (CRITICAL for Odoo 17+)

### Problem
The `attrs` attribute was deprecated in Odoo 16, partially removed in 17, and fully removed in Odoo 19.
Fields using `attrs="{'invisible': [...]}"` will raise XML parse errors or be silently ignored.

### Detection
```bash
grep -rn "attrs=" views/ --include="*.xml"
grep -rn "attrs=" --include="*.xml" -r .
```

### Before (Odoo 14/15/16)
```xml
<!-- Single condition -->
<field name="discount" attrs="{'invisible': [('order_type', '=', 'service')]}"/>

<!-- Multiple conditions -->
<field name="date_end"
    attrs="{'invisible': [('is_recurring', '=', False)],
            'required': [('is_recurring', '=', True)]}"/>

<!-- Readonly condition -->
<field name="state"
    attrs="{'readonly': [('state', 'not in', ['draft', 'sent'])]}"/>
```

### After (Odoo 17/18/19)
```xml
<!-- Single condition — Python expression directly -->
<field name="discount" invisible="order_type == 'service'"/>

<!-- Multiple conditions — separate attributes -->
<field name="date_end"
    invisible="not is_recurring"
    required="is_recurring"/>

<!-- Readonly condition -->
<field name="state"
    readonly="state not in ('draft', 'sent')"/>
```

### Expression Conversion Rules
| Domain | Inline Expression |
|--------|------------------|
| `[('field', '=', value)]` | `field == value` |
| `[('field', '!=', value)]` | `field != value` |
| `[('field', 'in', [...])]` | `field in (...)` |
| `[('field', 'not in', [...])]` | `field not in (...)` |
| `[('field', '=', False)]` | `not field` |
| `[('field', '=', True)]` | `field` |
| `['|', cond1, cond2]` | `cond1 or cond2` |
| `['&', cond1, cond2]` | `cond1 and cond2` |

### Auto-Fix (simple cases)
```bash
python auto_fix_library.py /path/to/module --specific attrs_inline
```

**Note**: The auto-fix handles simple single-condition cases. Complex nested domains need manual review.

### Manual Review Required When
- Domain uses `'|'` (OR) or `'&'` (AND) operators
- Domain references fields from related models
- Domain uses functions like `context_today()`
- Multiple conditions with mixed AND/OR

---

## Pattern 16: OWL 1.x → OWL 2.0 Lifecycle Hooks (Odoo 18+)

### Problem
Odoo 18 upgraded to OWL 2.0 which renamed all lifecycle methods and changed
the component constructor pattern. OWL 1.x components will fail silently or throw errors.

### Detection
```bash
grep -rn "mounted()\|willStart()\|patched()\|willUnmount()" static/src/js/ --include="*.js"
grep -rn "constructor(parent, props)" static/src/js/ --include="*.js"
```

### Before (OWL 1.x — Odoo 16/17)
```javascript
/** @odoo-module **/
import { Component, useState } from "@odoo/owl";

class MyWidget extends Component {
    constructor(parent, props) {
        super(parent, props);
        this.state = useState({ count: 0 });
    }

    async willStart() {
        await this._loadData();
    }

    mounted() {
        this._setupListeners();
    }

    patched() {
        this._updateView();
    }

    willUnmount() {
        this._cleanup();
    }
}
```

### After (OWL 2.0 — Odoo 18+)
```javascript
/** @odoo-module **/
import { Component, useState, onMounted, onWillStart, onPatched, onWillUnmount } from "@odoo/owl";

class MyWidget extends Component {
    setup() {
        this.state = useState({ count: 0 });

        onWillStart(async () => {
            await this._loadData();
        });

        onMounted(() => {
            this._setupListeners();
        });

        onPatched(() => {
            this._updateView();
        });

        onWillUnmount(() => {
            this._cleanup();
        });
    }
}
```

### Lifecycle Hook Mapping
| OWL 1.x (method) | OWL 2.0 (hook function in setup) |
|-------------------|----------------------------------|
| `constructor(parent, props)` | `setup()` |
| `async willStart()` | `onWillStart(async () => {...})` |
| `mounted()` | `onMounted(() => {...})` |
| `patched()` | `onPatched(() => {...})` |
| `willUnmount()` | `onWillUnmount(() => {...})` |
| `willUpdateProps(nextProps)` | `onWillUpdateProps((nextProps) => {...})` |
| `willPatch()` | `onWillPatch(() => {...})` |

### Import Change
```javascript
// Before (OWL 1.x)
import { Component, useState } from "@odoo/owl";

// After (OWL 2.0) — import lifecycle hooks as functions
import { Component, useState, onMounted, onWillStart, onPatched, onWillUnmount } from "@odoo/owl";
```

### Auto-Fix (basic renames only)
```bash
python auto_fix_library.py /path/to/module --specific owl_lifecycle
```

**Note**: Auto-fix renames the methods but does NOT restructure them into `setup()`.
Full migration to `setup()` requires manual refactoring of the constructor pattern.
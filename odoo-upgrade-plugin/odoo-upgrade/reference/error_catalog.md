# Odoo Upgrade Error Catalog

## Frontend/JavaScript Errors

### 1. Service rpc is not available
**Error Message**: `Error: Service rpc is not available`
**Versions**: Odoo 19
**Cause**: The RPC service is not available in frontend/public components
**Solution**:
```javascript
// Remove
this.rpc = useService("rpc");

// Add helper method
async _jsonRpc(endpoint, params = {}) {
    // See javascript_fixes.md for full implementation
}

// Replace calls
await this._jsonRpc("/api/endpoint", params);
```

### 2. Cannot find module
**Error Message**: `Cannot find module '@web_editor/js/common/utils'`
**Versions**: Odoo 18+
**Cause**: Module location changed
**Solution**: Create local compatibility functions

### 3. Component template not found
**Error Message**: `Template 'module.ComponentName' not found`
**Cause**: Template naming mismatch
**Solution**: Verify template name matches component

### 4. Cannot find key in registry
**Error Message**: `Cannot find key "crm_kanban" in the "views" registry`
**Versions**: Odoo 19
**Cause**: Using js_class that's not available in the context
**Solution**: Remove js_class attribute from kanban views
```xml
<!-- Remove js_class that's not available -->
<kanban js_class="crm_kanban"> <!-- REMOVE js_class -->
<kanban> <!-- CORRECT -->
```

### 5. Component template not found
**Error Message**: `Template 'module.ComponentName' not found`
**Cause**: Template naming mismatch
**Solution**: Verify template name matches component

## XML/View Errors

### 3. External ID not found: website.snippet_options
**Error Message**: `External ID not found in the system: website.snippet_options`
**Versions**: Odoo 19
**Cause**: website.snippet_options was removed in Odoo 19, snippet system redesigned
**Solution**:
```xml
<!-- Comment out or remove templates inheriting website.snippet_options -->
<!-- The snippet options system has been completely redesigned in Odoo 19 -->
```

### 4. Invalid view type: 'tree'
**Error Message**: `Invalid view type: 'tree'. Allowed types are: list, form, graph...`
**Versions**: Odoo 19
**Cause**: Tree view type renamed to 'list' in Odoo 19
**Solution**:
```xml
<!-- Change all <tree> tags to <list> -->
<list string="Items" editable="top">
    <field name="name"/>
</list>
```

### 5. Invalid view definition (Search Views)
**Error Message**: `Invalid view disaster.disaster.search definition`
**Location**: Search views with group tags
**Versions**: Odoo 19
**Cause**: `<group>` tags not allowed in search views
**Solution**:
```xml
<!-- Remove group tags, keep filters at root level -->
<search>
    <field name="name"/>
    <separator/>
    <filter name="group_by_type" string="Group by Type" context="{'group_by': 'type_id'}"/>
</search>
```

### 6. Invalid field in ir.cron
**Error Message**: `Invalid field 'numbercall' in 'ir.cron'`
**Versions**: Odoo 19
**Cause**: Field removed from cron model
**Solution**: Remove the field entirely from XML

### 6. Missing kanban template
**Error Message**: `Missing 'card' template`
**Versions**: Odoo 19
**Cause**: Kanban template name changed
**Solution**: Change `t-name="kanban-box"` to `t-name="card"`

### 7. Mail Template Helper Environment Error (NEW)
**Error Message**: `AttributeError: 'Environment' object has no attribute 'tzinfo'`
**Location**: Mail template `body_html` field
**Versions**: Odoo 19
**Cause**: Passing `env` parameter to `format_datetime()`, `format_date()`, or `format_amount()` helper functions
**Solution**:
```xml
<!-- WRONG - Causes AttributeError -->
<t t-out="format_datetime(env, object.date_start, dt_format='long')"/>

<!-- CORRECT - Remove env parameter -->
<t t-out="format_datetime(object.date_start, dt_format='long')"/>
```
**Detection**:
```bash
grep -r "format_datetime(env," --include="*.xml"
grep -r "format_date(env," --include="*.xml"
grep -r "format_amount(env," --include="*.xml"
```

### 8. XML Entity Not Defined (NEW)
**Error Message**: `lxml.etree.XMLSyntaxError: Entity 'copy' not defined, line X, column Y`
**Location**: XML data files, mail templates
**Versions**: All Odoo versions
**Cause**: Using HTML entities like `&copy;`, `&nbsp;`, `&mdash;` in XML files
**Explanation**: XML only supports 5 predefined entities: `&lt;`, `&gt;`, `&amp;`, `&quot;`, `&apos;`. All other special characters must use numeric character references.
**Solution**:
```xml
<!-- WRONG - XML parsing fails -->
<p>© 2025 Company&nbsp;Name</p>
<p>Price: 100&mdash;200</p>

<!-- CORRECT - Use numeric character references -->
<p>&#169; 2025 Company&#160;Name</p>
<p>Price: 100&#8212;200</p>
```
**Common Replacements**:
- `&copy;` → `&#169;` (©)
- `&nbsp;` → `&#160;` (non-breaking space)
- `&mdash;` → `&#8212;` (—)
- `&trade;` → `&#8482;` (™)
- `&reg;` → `&#174;` (®)
- `&euro;` → `&#8364;` (€)

**Detection**:
```bash
grep -r "&copy;" --include="*.xml"
grep -r "&nbsp;" --include="*.xml"
grep -r "&mdash;" --include="*.xml"
```

### 9. Portal XPath Cannot Be Located (NEW)
**Error Message**: `Element '<xpath expr="//tbody//t[@t-if='not line.display_type']/td[3]">' cannot be located in parent view`
**Location**: Sale portal template inheritance (`sale_portal_templates.xml`)
**Versions**: Odoo 19
**Cause**: Complete restructure of sale portal templates - wrapper conditionals removed, now uses named elements
**Solution**:
```xml
<!-- OLD (Odoo 17/18) - FAILS in Odoo 19 -->
<xpath expr="//table[@id='sales_order_table']/thead/tr/th[3]" position="attributes">

<!-- NEW (Odoo 19) - Uses named element IDs -->
<xpath expr="//table[@id='sales_order_table']/thead/tr/th[@id='product_unit_price_header']" position="attributes">

<!-- OLD body XPath - FAILS -->
<xpath expr="//tbody//t[@t-foreach='lines_to_report']//tr/t[@t-if='not line.display_type']/td[3]">

<!-- NEW body XPath - WORKS -->
<xpath expr="//tbody//tr[@name='tr_product']/td[@name='td_product_priceunit']">

<!-- OLD sidebar XPath - FAILS -->
<xpath expr="//h2[@data-id='total_amount']">

<!-- NEW sidebar XPath - WORKS -->
<xpath expr="//t[@t-set='title']//h2[@t-field='sale_order.amount_total']">
```
**Common Portal Element Names**:
- Headers: `th[@id='product_unit_price_header']`, `th[@id='taxes_header']`, `th[@id='subtotal_header']`
- Body: `tr[@name='tr_product']`, `td[@name='td_product_priceunit']`, `td[@name='td_product_taxes']`, `td[@name='td_product_subtotal']`

**Detection**:
```bash
grep -r "t-if='not line.display_type'" --include="*.xml"
grep -r "data-id='total_amount'" --include="*.xml"
grep -r "sales_order_table.*th\[" --include="*.xml"
```

### 10. XML Domain Invalid Syntax (NEW)
**Error Message**: `Invalid domain: "[('date_field', '>=', context_today().strftime('%Y-%m-%d'))]" - closing parenthesis ']' does not match opening parenthesis '('`
**Location**: Search view filter domains
**Versions**: All Odoo versions
**Cause**: Using Python method calls (`.strftime()`, `.get()`, etc.) in XML domain expressions
**Explanation**: XML domains are parsed at XML load time, not runtime. They cannot contain Python method calls or function invocations.
**Solution**: Use Odoo's built-in date filter widget instead
```xml
<!-- WRONG - Method call in XML domain -->
<search>
    <filter name="filter_today" string="Today"
            domain="[('sent_date', '>=', context_today().strftime('%Y-%m-%d'))]"/>
</search>

<!-- CORRECT - Use Odoo's date filter widget -->
<search>
    <separator/>
    <filter name="sent_date" string="Sent Date" date="sent_date"/>
</search>
```
**Benefits of date filter widget**:
- Automatic dropdown: Today, This Week, This Month, Quarter, Year
- Custom date range picker
- No XML domain parsing issues
- Standard Odoo UX

**Detection**:
```bash
grep -r "context_today()\.strftime" --include="*.xml"
grep -r "datetime\.timedelta" --include="*.xml" | grep "domain="
grep -r "\.get(" --include="*.xml" | grep "domain="
```

### 7. Invalid js_class in kanban
**Error Message**: `Cannot find key 'crm_kanban' in the 'views' registry`
**Versions**: Odoo 19
**Cause**: js_class attribute deprecated
**Solution**: Remove `js_class` attribute from kanban views

### 8. Active ID not found
**Error Message**: `field 'active_id' does not exist in model`
**Versions**: Odoo 19
**Cause**: active_id not available in form view contexts
**Solution**: Replace `active_id` with `id`

### 9. External ID not found
**Error Message**: `External ID not found in the system: website.snippet_options`
**Versions**: Odoo 19
**Cause**: Snippet system completely changed
**Solution**: Remove templates inheriting from website.snippet_options

## Python Import Errors

### 10. Cannot import slug
**Error Message**: `cannot import name 'slug' from 'odoo.addons.http_routing.models.ir_http'`
**Versions**: Odoo 18+
**Solution**:
```python
from odoo.http import request

def slug(value):
    return request.env['ir.http']._slug(value)
```

### 11. Cannot import url_for
**Error Message**: `cannot import name 'url_for' from 'odoo.addons.http_routing.models.ir_http'`
**Versions**: Odoo 19
**Solution**:
```python
# Use
url = self.env['ir.http']._url_for('/path')
```

### 12. Missing Python Dependencies
**Error Message**: `ModuleNotFoundError: No module named 'geopy'`
**Solution**: Add to manifest and install
```python
'external_dependencies': {
    'python': ['geopy', 'spacy', 'hachoir'],
}
```

## Manifest Errors

### 13. Invalid version format
**Warning**: `Invalid version format`
**Solution**: Use proper version format: `19.0.1.0.0`

### 14. Missing license key
**Warning**: `Missing license key in manifest`
**Solution**: Add `'license': 'LGPL-3'` to manifest

### 15. Module not found
**Error**: `Module 'dependency_name' not found`
**Cause**: Missing or renamed dependency
**Solution**: Update depends list in manifest

## Theme/SCSS Errors

### 16. Undefined variable
**Error**: `Undefined variable: $headings-font-weight`
**Cause**: Incorrect variable naming
**Solution**: Use `$o-theme-headings-font-weight`

### 17. Invalid map-merge
**Error**: `map-merge() expecting a map`
**Cause**: Missing or incorrect map structure
**Solution**: Ensure proper map-merge syntax with existing maps

### 18. Font not loading
**Issue**: Google Fonts not loading
**Cause**: Incorrect font configuration
**Solution**: Use proper $o-theme-font-configs structure

## Database/Migration Errors

### 19. Column does not exist
**Error**: `column "numbercall" does not exist`
**Cause**: Database schema mismatch
**Solution**: Remove field references from Python and XML

### 20. Constraint violation
**Error**: `duplicate key value violates unique constraint`
**Cause**: Duplicate XML IDs during migration
**Solution**: Ensure unique XML IDs across modules

## Asset Compilation Errors

### 21. Asset bundle error
**Error**: `Could not get content for /module/static/src/js/file.js`
**Cause**: File path mismatch
**Solution**: Verify file paths in manifest assets section

### 22. SCSS compilation failed
**Error**: `Error in scss compilation`
**Cause**: Invalid SCSS syntax
**Solution**: Check SCSS syntax and variable definitions

## Performance Issues

### 23. Memory limit exceeded
**Error**: `Memory limit exceeded`
**During**: Module installation
**Solution**: Increase memory limits or install modules individually

### 24. Timeout during upgrade
**Error**: `Request timeout`
**Solution**: Run upgrade with --limit-time-real=0

## Testing Errors

### 25. Test failures after upgrade
**Common Issues**:
- DOM selectors changed
- API endpoints modified
- Field names changed

**Solution**: Update test cases for new version

## Quick Diagnosis Commands

```bash
# Find all RPC usage
grep -r "useService.*rpc" --include="*.js"

# Find tree views
grep -r "<tree" --include="*.xml"

# Find active_id usage
grep -r "active_id" --include="*.xml"

# Find numbercall fields
grep -r "numbercall" --include="*.xml"

# Find slug imports
grep -r "from.*slug" --include="*.py"

# Check manifest versions
find . -name "__manifest__.py" -exec grep -H "version" {} \;
```

## Debugging Tips

1. **Enable developer mode**: Add `?debug=1` to URL
2. **Check browser console**: F12 → Console tab
3. **Check network requests**: F12 → Network tab
4. **Enable Odoo logging**: `--log-level=debug`
5. **Test in isolation**: Install modules one by one
6. **Clear cache**: Delete filestore/assets directory
7. **Regenerate assets**: `--dev=xml,css,js`

## XML Syntax Errors

### 26. Malformed XML comments
**Error**: `XMLSyntaxError: Double hyphen within comment`
**Cause**: Nested or duplicate comment markers, double hyphens in comments
**Solution**: Fix comment structure, escape double hyphens
```xml
<!-- Correct comment without double-hyphens -->
<!-- website.snippet_options removed in Odoo 19 -->
```

### 27. Invalid manifest version format
**Error**: `Invalid version '19.0.19.0.1.0.0.0', must have between 2 and 5 parts`
**Cause**: Duplicated version prefix during upgrade
**Solution**: Use proper version format: `19.0.1.0.0`

## Python Dependency Errors

### 28. Missing Python packages
**Error**: `ModuleNotFoundError: No module named 'geopy'`
**Solution**: Install required packages
```bash
pip install geopy spacy hachoir
```

## Common Fix Order

When encountering multiple errors, fix in this order:
1. Install Python dependencies
2. Fix manifest versions
3. Fix malformed XML comments
4. Python import errors
5. XML structure errors (tree → list)
6. JavaScript RPC service
7. SCSS variables
8. Theme-specific issues
9. Test updates

## Prevention

Before upgrading:
1. Create full backup
2. Test in development environment
3. Review official migration guide
4. Check third-party module compatibility
5. Document customizations
6. Plan rollback strategy
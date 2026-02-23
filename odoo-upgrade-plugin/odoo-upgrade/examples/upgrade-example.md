# Odoo Module Upgrade Examples

This document shows practical examples of using the Odoo Module Upgrade skill.

## Example 1: Simple Single-Version Upgrade

### Scenario
Upgrade a custom inventory module from Odoo 17 to Odoo 18.

### User Request
```
"Upgrade custom_inventory module from odoo17 to odoo18"
```

### Skill Workflow

**1. Information Gathering**
```
Module Name: custom_inventory
Project: warehouse_management
Source Version: 17
Target Version: 18
Source Path: C:\odoo\odoo17\projects\warehouse_management\custom_inventory
```

**2. Analysis Results**
```
Files Found:
- 5 Python files (models)
- 8 XML files (views)
- 2 JavaScript files
- 1 SCSS file
- 1 manifest file

Patterns Detected:
- 12 <tree> tags to convert to <list>
- 3 editable="1" to fix
- 2 OWL components to update
```

**3. Changes Applied**
```
Python:
✅ No name_get overrides (v17 migration already done)
✅ Updated 1 check_access_rights() to check_access()

XML:
✅ Converted 12 <tree> tags to <list>
✅ Fixed 3 editable="1" to editable="bottom"
✅ Updated 5 view_mode references

JavaScript:
✅ Updated 2 OWL components for v2 compatibility
```

**4. Testing**
```
✅ Module installed successfully
✅ All views loaded correctly
✅ 15/15 tests passed
```

**5. Output**
```
📁 Upgraded: C:\odoo\odoo18\projects\warehouse_management\custom_inventory
💾 Backup: custom_inventory.backup_from_v17
📄 Report: custom_inventory_UPGRADE_REPORT.md
```

---

## Example 2: Multi-Version Jump

### Scenario
Upgrade a legacy theme from Odoo 14 to Odoo 19.

### User Request
```
"Migrate theme_retail from version 14 to version 19"
```

### Skill Workflow

**1. Upgrade Path Calculated**
```
14 → 15 → 16 → 17 → 18 → 19

Changes per version:
- 14→15: Python 2 cleanup
- 15→16: Bootstrap 5 prep
- 16→17: attrs removal, OWL v1, Settings views
- 17→18: tree→list, OWL v2
- 18→19: Roles system, JSON-RPC 2.0
```

**2. Major Transformations**

**Python (16→17)**:
```python
# Before
def name_get(self):
    result = []
    for record in self:
        result.append((record.id, record.name))
    return result

# After
@api.depends('name')
def _compute_display_name(self):
    for record in self:
        record.display_name = record.name
```

**XML (16→17)**:
```xml
<!-- Before -->
<field name="color" attrs="{'invisible': [('state','=','done')]}"/>

<!-- After -->
<field name="color" invisible="state == 'done'"/>
```

**XML (17→18)**:
```xml
<!-- Before -->
<tree string="Products" editable="1">

<!-- After -->
<list string="Products" editable="bottom">
```

**Bootstrap (15→16)**:
```scss
// Before
.ml-3 { margin-left: 1rem; }
.text-left { text-align: left; }

// After
.ms-3 { margin-start: 1rem; }
.text-start { text-align: start; }
```

**3. Testing Results**
```
✅ Installation: SUCCESS
⚠️  Warnings: 2 deprecation notices
✅ Views: 18/18 loaded
✅ Theme: Renders correctly
⚠️  Manual Review: 3 items (see report)
```

**4. Manual Steps Required**
```
1. Custom jQuery code in cart.js needs OWL conversion
2. Verify color palette matches design system
3. Test checkout workflow thoroughly
```

---

## Example 3: Module with Enterprise Dependencies

### Scenario
Upgrade a custom accounting extension that uses Enterprise features.

### User Request
```
"Upgrade custom_accounting from odoo16 to odoo18"
```

### Skill Notes

**Dependency Check**:
```
✅ account - Available in v18
✅ account_accountant (Enterprise) - Available in v18
⚠️  custom_reports - Not found in v18 (renamed to custom_accounting_reports)
```

**Manual Steps**:
```
1. Update manifest dependency:
   'custom_reports' → 'custom_accounting_reports'

2. Verify Enterprise license for target environment

3. Test with Enterprise modules installed
```

---

## Example 4: Theme with publicWidget

### Scenario
Upgrade a website theme with custom JavaScript widgets.

### User Request
```
"Upgrade theme_ecommerce from odoo16 to odoo19"
```

### JavaScript Transformation

**Before (v16 - Legacy Widget)**:
```javascript
odoo.define('theme_ecommerce.product_carousel', function (require) {
    'use strict';

    var Widget = require('web.Widget');

    var ProductCarousel = Widget.extend({
        template: 'ProductCarousel',
        events: {
            'click .arrow': '_onArrowClick'
        },
        _onArrowClick: function(ev) {
            // Logic
        }
    });

    return ProductCarousel;
});
```

**After (v17+ - publicWidget)**:
```javascript
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ProductCarousel = publicWidget.Widget.extend({
    selector: '.product-carousel',
    events: {
        'click .arrow': '_onArrowClick',
    },

    _onArrowClick: function(ev) {
        // Logic
    },
});
```

---

## Example 5: Handling Errors

### Scenario
Upgrade fails due to missing fields.

### User Request
```
"Upgrade custom_crm from odoo15 to odoo17"
```

### Error Encountered
```
ERROR: Field 'stage_probability' not found on model 'crm.lead'
Location: models/crm_lead.py:45
```

### Skill Response

**Report Generated**:
```markdown
## Critical Issues

### Field Not Found: stage_probability
- **Location**: models/crm_lead.py:45
- **Reason**: Field removed in Odoo 16
- **Solution**: Replace with 'probability' field
- **Action**: Manual code update required

### Recommended Fix:
# Before
stage_probability = fields.Float(related='stage_id.probability')

# After
probability = fields.Float(string='Success Rate')
```

**Recovery Instructions**:
```bash
# Restore from backup
cd C:\odoo\odoo17\projects\crm_custom
rm -rf custom_crm
cp -r custom_crm.backup_from_v15 custom_crm

# Fix the issue
# Edit models/crm_lead.py manually

# Re-run upgrade
"Upgrade custom_crm from odoo15 to odoo17"
```

---

## Example 6: Batch Upgrade (Future Feature)

### Scenario
Upgrade multiple modules in a project.

### User Request
```
"Upgrade all modules in TAQAT project from odoo17 to odoo18"
```

### Expected Workflow (Planned)
```
Modules Found: 12

Processing:
1/12 custom_inventory... ✅
2/12 custom_sales...     ✅
3/12 custom_reports...   ✅
4/12 theme_taqat...      ✅
...

Summary:
✅ Success: 10
⚠️  Warnings: 2
❌ Failed: 0

Reports generated in: odoo18/projects/TAQAT/_UPGRADE_REPORTS/
```

---

## Tips for Successful Upgrades

### Before Upgrading
1. ✅ Backup your database
2. ✅ Test in staging environment
3. ✅ Review Odoo release notes
4. ✅ Check third-party module compatibility
5. ✅ Update documentation

### During Upgrade
1. ✅ Review generated report carefully
2. ✅ Address critical issues first
3. ✅ Test each module incrementally
4. ✅ Keep backup accessible

### After Upgrade
1. ✅ Run full test suite
2. ✅ Perform UAT (User Acceptance Testing)
3. ✅ Monitor logs for warnings
4. ✅ Update deployment documentation
5. ✅ Train users on new features

---

## Common Patterns

### attrs Conversion
```xml
<!-- Pattern 1: Simple condition -->
attrs="{'invisible': [('x','=','y')]}" → invisible="x == 'y'"

<!-- Pattern 2: Multiple conditions (AND) -->
attrs="{'invisible': [('a','=','1'),('b','=','2')]}" → invisible="a == '1' and b == '2'"

<!-- Pattern 3: OR conditions -->
attrs="{'invisible': ['|',('a','=','1'),('b','=','2')]}" → invisible="a == '1' or b == '2'"

<!-- Pattern 4: readonly -->
attrs="{'readonly': [('state','in',['done','cancel'])]}" → readonly="state in ['done','cancel']"
```

### tree to list
```xml
<!-- Actions -->
view_mode="tree,form" → view_mode="list,form"

<!-- Views -->
<tree string="Items"> → <list string="Items">
</tree> → </list>
```

### editable
```xml
<!-- Add new line at bottom -->
editable="1" → editable="bottom"

<!-- Add new line at top -->
editable="top" → editable="top"
```

---

For more examples and patterns, see the [main skill documentation](../odoo-upgrade.md).
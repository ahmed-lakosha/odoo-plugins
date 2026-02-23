---
title: 'Migrate Template'
read_only: false
type: 'command'
description: 'Migrate email template or QWeb report between Odoo versions with automatic syntax updates'
---

# Migrate Template

Migrate email template or QWeb report between Odoo versions with **automatic syntax updates**, **field mapping**, and **compatibility fixes**.

## Usage

```
/migrate-template [source-file] [target-version]
/migrate-template projects/module/data/template.xml 17
/migrate-template --from 14 --to 19 projects/module/data/*.xml
```

### Natural Language

```
"Migrate my templates from Odoo 14 to Odoo 17"
"Upgrade the invoice template to Odoo 19"
"Update all email templates for the new version"
```

## Migration Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                    VERSION MIGRATION MATRIX                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  FROM → TO   │ 14  │ 15  │ 16  │ 17  │ 18  │ 19  │              │
│  ────────────┼─────┼─────┼─────┼─────┼─────┼─────┤              │
│  Odoo 14     │  -  │  M  │  M  │  H  │  H  │  H  │              │
│  Odoo 15     │  L  │  -  │  L  │  M  │  M  │  M  │              │
│  Odoo 16     │  L  │  L  │  -  │  L  │  L  │  M  │              │
│  Odoo 17     │  M  │  L  │  L  │  -  │  L  │  L  │              │
│  Odoo 18     │  M  │  M  │  L  │  L  │  -  │  L  │              │
│  Odoo 19     │  H  │  M  │  M  │  L  │  L  │  -  │              │
│                                                                   │
│  L = Low effort   M = Medium effort   H = High effort            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Migration Transformations

### Odoo 14 → 15+

```xml
<!-- BEFORE (Odoo 14) -->
<t t-esc="object.name"/>
<t t-raw="object.description"/>

<!-- AFTER (Odoo 15+) -->
<t t-out="object.name"/>
<t t-out="object.description"/>  <!-- t-raw removed, use t-out -->
```

### Odoo 14-16 → 17+

```xml
<!-- BEFORE (Odoo 14-16) - Single report -->
<field name="report_template" ref="module.report_action"/>

<!-- AFTER (Odoo 17+) - Multiple reports -->
<field name="report_template_ids" eval="[(4, ref('module.report_action'))]"/>
```

### Any → Odoo 16+

```xml
<!-- ADD (Odoo 16+) - Template category -->
<!-- Only if template has xmlid and description -->
<field name="template_category">base_template</field>
```

### Any → Odoo 19

```xml
<!-- ENHANCE (Odoo 19) - Company branding colors -->
<!-- BEFORE -->
<a style="background-color: #875A7B;">Button</a>

<!-- AFTER -->
<t t-set="btn_bg" t-value="company.email_secondary_color or '#875A7B'"/>
<a t-att-style="'background-color: %s' % btn_bg">Button</a>
```

## Complete Migration Workflow

### Step 1: Analyze Source Template

```
Analyzing: projects/relief_center/data/mail_template.xml

Source version detected: Odoo 14
Target version: Odoo 17

Templates found:
• email_template_disaster_alert (mail.template)
• email_template_volunteer_welcome (mail.template)

Issues to migrate:
• 12 instances of t-esc → t-out
• 2 instances of t-raw → t-out
• 2 report_template → report_template_ids
• 0 deprecated field references
```

### Step 2: Apply Transformations

```
┌─────────────────────────────────────────────────────────────────┐
│                 MIGRATION TRANSFORMATIONS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [1/12] Line 25: t-esc → t-out                                  │
│         <t t-esc="object.name"/>                                 │
│         <t t-out="object.name"/>                                 │
│                                                                   │
│  [2/12] Line 31: t-esc → t-out                                  │
│         <t t-esc="object.partner_id.name"/>                      │
│         <t t-out="object.partner_id.name"/>                      │
│                                                                   │
│  ... (10 more t-esc → t-out)                                     │
│                                                                   │
│  [13/14] Line 8: report_template → report_template_ids           │
│          <field name="report_template" ref="..."/>               │
│          <field name="report_template_ids" eval="[(4, ref(...))]"/>│
│                                                                   │
│  [14/14] Line 52: t-raw → t-out                                  │
│          <t t-raw="object.notes"/>                               │
│          <t t-out="object.notes"/>                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Step 3: Validate Migration

```
Post-migration validation:

✓ XML syntax valid
✓ All QWeb tags properly closed
✓ No deprecated syntax remaining
✓ Field references valid for Odoo 17
✓ Security patterns intact

Migration complete!
```

### Step 4: Generate Backup and Output

```
Files created:
• projects/relief_center/data/mail_template.xml.bak  (backup)
• projects/relief_center/data/mail_template.xml      (migrated)

Migration summary saved to:
• projects/relief_center/data/MIGRATION_LOG.md
```

## Example Flows

### Example 1: Odoo 14 to 17

**User**: "Migrate my Odoo 14 templates to Odoo 17"

**Claude**:
```
Scanning for templates...
Found 5 template files in projects/my_module/data/

Migration plan:
1. mail_template_order.xml
   - 8 t-esc → t-out
   - 1 report_template → report_template_ids

2. mail_template_invoice.xml
   - 6 t-esc → t-out
   - 1 report_template → report_template_ids
   - 2 t-raw → t-out

3. mail_template_notification.xml
   - 4 t-esc → t-out

...

Proceed with migration? (y/n)
```

### Example 2: Single File Migration

**User**: "Migrate invoice template to Odoo 19 with branding colors"

**Claude**:
```
Source: projects/module/data/mail_template_invoice.xml
From: Odoo 16 (detected)
To: Odoo 19

Transformations:
1. report_template → report_template_ids
2. Add company branding color variables
3. Update CTA button with dynamic colors

Generated:
```

```xml
<!-- BEFORE (Odoo 16) -->
<a href="#" style="background-color: #875A7B; color: white;">
    Pay Now
</a>

<!-- AFTER (Odoo 19) -->
<t t-set="btn_bg" t-value="object.company_id.email_secondary_color or '#875A7B'"/>
<t t-set="btn_text" t-value="object.company_id.email_primary_color or '#FFFFFF'"/>
<a href="#" t-att-style="'background-color: %s; color: %s' % (btn_bg, btn_text)">
    Pay Now
</a>
```

### Example 3: Batch Migration

**User**: "Migrate all templates in the project to Odoo 18"

**Claude**:
```
Scanning projects/relief_center/**/*.xml for templates...

Found 12 template files:
• data/mail_template_alert.xml
• data/mail_template_welcome.xml
• data/mail_template_reminder.xml
• reports/report_disaster.xml
• reports/report_volunteer.xml
...

Total transformations needed: 47

Running migration...
[████████████████████████████████████████] 100%

Results:
• 12 files migrated successfully
• 0 files with errors
• 47 transformations applied
• Backups created: data/*.xml.bak
```

## Migration Checklist

```
┌─────────────────────────────────────────────────────────────────┐
│                    MIGRATION CHECKLIST                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  PRE-MIGRATION:                                                  │
│  [ ] Backup all template files                                   │
│  [ ] Note current Odoo version                                   │
│  [ ] Test templates work in current version                      │
│                                                                   │
│  SYNTAX UPDATES:                                                 │
│  [ ] t-esc → t-out (Odoo 15+)                                   │
│  [ ] t-raw → t-out (Odoo 15+)                                   │
│  [ ] render_engine parameter (if needed)                         │
│                                                                   │
│  FIELD UPDATES:                                                  │
│  [ ] report_template → report_template_ids (Odoo 17+)           │
│  [ ] Check deprecated model fields                               │
│  [ ] Update field paths for renamed fields                       │
│                                                                   │
│  ENHANCEMENTS (OPTIONAL):                                        │
│  [ ] Add template_category (Odoo 16+)                           │
│  [ ] Add company branding colors (Odoo 19)                       │
│  [ ] Use new layout variants                                     │
│                                                                   │
│  POST-MIGRATION:                                                 │
│  [ ] Validate XML syntax                                         │
│  [ ] Test template rendering                                     │
│  [ ] Test email sending                                          │
│  [ ] Test report PDF generation                                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Transformation Rules

### Automatic Transformations

| Pattern | From | To | Versions |
|---------|------|-----|----------|
| Output syntax | `t-esc` | `t-out` | 14→15+ |
| Raw output | `t-raw` | `t-out` | 14→15+ |
| Report attachment | `report_template` | `report_template_ids` | 14-16→17+ |
| Button colors | Hardcoded | `company.email_*_color` | Any→19 |

### Manual Review Required

| Pattern | Reason |
|---------|--------|
| Custom render methods | May need context updates |
| Direct SQL in templates | Security review |
| Complex Jinja2 expressions | Version-specific behavior |
| Custom QWeb extensions | May be deprecated |

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│               MIGRATE TEMPLATE QUICK REFERENCE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  USAGE:                                                          │
│  /migrate-template FILE TARGET_VERSION                           │
│  /migrate-template --from 14 --to 17 FILE                        │
│                                                                   │
│  KEY TRANSFORMATIONS:                                            │
│  14→15: t-esc → t-out, t-raw → t-out                            │
│  14-16→17: report_template → report_template_ids                 │
│  Any→19: Add company branding colors                             │
│                                                                   │
│  OPTIONS:                                                        │
│  --dry-run    Show changes without applying                      │
│  --backup     Create .bak files (default: yes)                   │
│  --recursive  Migrate all templates in directory                 │
│  --force      Skip confirmation prompts                          │
│                                                                   │
│  OUTPUT:                                                         │
│  • Migrated template file                                        │
│  • Backup file (.bak)                                            │
│  • Migration log (MIGRATION_LOG.md)                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Related Commands

| Command | Description |
|---------|-------------|
| `/analyze-template` | Check template for issues |
| `/fix-template` | Fix common template issues |
| `/create-email-template` | Create new template |

---

*Part of Odoo Report Plugin v1.0*
*Version Migration & Compatibility*

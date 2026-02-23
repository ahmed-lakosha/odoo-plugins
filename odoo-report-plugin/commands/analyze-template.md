---
title: 'Analyze Template'
read_only: true
type: 'command'
description: 'Analyze an existing email template or QWeb report for issues and improvements'
---

# Analyze Template

Analyze an existing email template or QWeb report for **issues**, **compatibility**, and **improvement opportunities**.

## Usage

```
/analyze-template [template-id-or-file]
/analyze-template sale.email_template_edi_sale
/analyze-template projects/my_module/data/mail_template.xml
/analyze-template --model sale.order
```

### Natural Language

```
"Analyze the sales quotation email template"
"Check the invoice template for issues"
"Review my custom template in relief_center module"
```

## Analysis Categories

### 1. Syntax Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│                     SYNTAX ANALYSIS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  QWeb Syntax:                                                    │
│  [ ] t-out vs t-esc (version compatibility)                      │
│  [ ] Properly closed tags                                        │
│  [ ] Valid t-if/t-elif/t-else structure                         │
│  [ ] t-foreach with t-as                                         │
│  [ ] t-att vs t-attf usage                                       │
│                                                                   │
│  Jinja2 Syntax (inline_template):                                │
│  [ ] Balanced {{ }} brackets                                     │
│  [ ] Valid Python expressions                                    │
│  [ ] Proper field access chains                                  │
│                                                                   │
│  XML Structure:                                                  │
│  [ ] Valid XML (well-formed)                                     │
│  [ ] Proper CDATA/escaping                                       │
│  [ ] Correct record/field structure                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Field Validation

```
┌─────────────────────────────────────────────────────────────────┐
│                     FIELD VALIDATION                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  For each field reference, check:                                │
│  [ ] Field exists on model                                       │
│  [ ] Field is accessible (not deprecated)                        │
│  [ ] Related fields are valid (object.partner_id.name)           │
│  [ ] Computed fields don't cause performance issues              │
│                                                                   │
│  Report potential issues:                                        │
│  ! object.field_name → Field may be None                         │
│  ! object.partner_id.name → Missing null check                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Version Compatibility

```
┌─────────────────────────────────────────────────────────────────┐
│                   VERSION COMPATIBILITY                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Check against target version:                                   │
│                                                                   │
│  Odoo 14:                                                        │
│  [ ] Uses t-esc (not t-out)                                      │
│  [ ] Uses report_template (not report_template_ids)              │
│                                                                   │
│  Odoo 15+:                                                       │
│  [ ] Uses t-out (not t-esc)                                      │
│  [ ] render_engine parameter if needed                           │
│                                                                   │
│  Odoo 16+:                                                       │
│  [ ] template_category field                                     │
│                                                                   │
│  Odoo 17+:                                                       │
│  [ ] report_template_ids (M2M) for attachments                   │
│                                                                   │
│  Odoo 19:                                                        │
│  [ ] Company branding color fields                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Security Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY ANALYSIS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Check for dangerous patterns:                                   │
│  [!] eval() or exec() calls                                      │
│  [!] os module access                                            │
│  [!] File system operations                                      │
│  [!] Arbitrary SQL execution                                     │
│  [!] External network calls                                      │
│                                                                   │
│  Sandbox safety:                                                 │
│  [ ] Only allowed functions used                                 │
│  [ ] No bypassing of sandbox                                     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 5. Performance Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│                   PERFORMANCE ANALYSIS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Check for performance issues:                                   │
│  [!] N+1 query patterns in loops                                 │
│  [!] Large recordset iterations                                  │
│  [!] Expensive computed fields                                   │
│  [!] Heavy image processing                                      │
│  [!] Unnecessary sudo() calls                                    │
│                                                                   │
│  Recommendations:                                                │
│  • Use prefetching for related records                           │
│  • Limit recordset size where possible                           │
│  • Cache expensive computations                                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Analysis Output Format

```
════════════════════════════════════════════════════════════════════
                    TEMPLATE ANALYSIS REPORT
════════════════════════════════════════════════════════════════════

Template: sale.email_template_edi_sale
Model: sale.order
Version Detected: Odoo 17

────────────────────────────────────────────────────────────────────
SUMMARY
────────────────────────────────────────────────────────────────────
Status: WARNINGS (3 issues found)

Errors:    0
Warnings:  3
Info:      5

────────────────────────────────────────────────────────────────────
FINDINGS
────────────────────────────────────────────────────────────────────

[WARNING] Line 15: Missing null check
  Code: {{ object.partner_id.name }}
  Risk: Will fail if partner_id is None
  Fix:  {{ object.partner_id.name or 'Customer' }}

[WARNING] Line 28: Deprecated syntax
  Code: <t t-esc="object.amount"/>
  Risk: t-esc deprecated in Odoo 15+
  Fix:  <t t-out="object.amount"/>

[WARNING] Line 45: Performance concern
  Code: t-foreach="object.order_line.product_id.seller_ids"
  Risk: Potential N+1 query
  Fix:  Prefetch or use with_prefetch()

[INFO] Line 8: Good practice
  Code: {{ (object.user_id.email_formatted or user.email_formatted) }}
  Note: Proper fallback chain for email_from

[INFO] Line 22: Layout usage
  Code: email_layout_xmlid="mail.mail_notification_layout"
  Note: Using standard layout, good for consistency

────────────────────────────────────────────────────────────────────
RECOMMENDATIONS
────────────────────────────────────────────────────────────────────

1. Add null checks for related field access
2. Update t-esc to t-out for Odoo 15+ compatibility
3. Consider prefetching for nested loops
4. Add report_template_ids instead of report_template (Odoo 17+)

════════════════════════════════════════════════════════════════════
```

## Example Flows

### Example 1: Analyze Standard Template

**User**: "Analyze the sales quotation template"

**Claude**:
```
Locating template: sale.email_template_edi_sale
File: odoo17/odoo/addons/sale/data/mail_template_data.xml

Analyzing...
```

### Example 2: Analyze Custom Template

**User**: "Analyze my template in projects/relief_center/data/mail_template.xml"

**Claude**:
```
Reading file: projects/relief_center/data/mail_template.xml

Analyzing template records found:
• email_template_disaster_alert
• email_template_volunteer_welcome

[Full analysis for each template...]
```

### Example 3: Check Version Compatibility

**User**: "Is my template compatible with Odoo 19?"

**Claude**:
```
Current template version: Odoo 17
Target version: Odoo 19

Compatibility check:
✓ t-out syntax (compatible)
✓ report_template_ids (compatible)
⚠ Missing company branding colors (optional enhancement)

Migration effort: LOW
```

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│              ANALYZE TEMPLATE QUICK REFERENCE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  INPUT OPTIONS:                                                  │
│  • Template XML ID: sale.email_template_edi_sale                 │
│  • File path: projects/module/data/template.xml                  │
│  • Model name: --model sale.order (lists all templates)          │
│                                                                   │
│  ANALYSIS TYPES:                                                 │
│  • --syntax     Syntax validation only                           │
│  • --fields     Field existence check                            │
│  • --version    Version compatibility                            │
│  • --security   Security audit                                   │
│  • --perf       Performance analysis                             │
│  • --all        Full analysis (default)                          │
│                                                                   │
│  OUTPUT LEVELS:                                                  │
│  • ERROR   - Must fix before use                                 │
│  • WARNING - Should fix for best practices                       │
│  • INFO    - Informational note                                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Related Commands

| Command | Description |
|---------|-------------|
| `/debug-template` | Debug template rendering |
| `/fix-template` | Auto-fix common issues |
| `/migrate-template` | Migrate to different version |

---

*Part of Odoo Report Plugin v1.0*
*Template Analysis & Validation*

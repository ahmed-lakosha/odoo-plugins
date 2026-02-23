# Version Routing - Odoo Template Version-Specific Decisions

> **Purpose**: This memory helps Claude make version-appropriate decisions when working with Odoo email templates and QWeb reports.

## Version Detection Priority

1. **User-specified**: `--version 17` flag takes precedence
2. **Directory path**: Extract from `odoo14`, `odoo15`, etc.
3. **Manifest version**: Parse `__manifest__.py` version string
4. **Ask user**: If ambiguous, ask for clarification

## Version-Specific Syntax

### Output Tags

| Version | Preferred | Alternative | Deprecated |
|---------|-----------|-------------|------------|
| Odoo 14 | `t-esc` | - | - |
| Odoo 15+ | `t-out` | `t-esc` | `t-raw` |

**Rule**: Always use `t-out` for Odoo 15+ unless maintaining Odoo 14 compatibility.

### Report Attachments

| Version | Field | Syntax |
|---------|-------|--------|
| Odoo 14-16 | `report_template` | `ref="module.report_action"` |
| Odoo 17+ | `report_template_ids` | `eval="[(4, ref('module.report_action'))]"` |

**Rule**: Check version before generating report attachment fields.

### Template Categories (Odoo 16+)

```python
template_category = fields.Selection([
    ('base_template', 'Base Template'),      # Has XML ID + description
    ('hidden_template', 'Hidden Template'),   # Has XML ID, no description
    ('custom_template', 'Custom Template'),   # No XML ID
])
```

**Rule**: Add `template_category` field only for Odoo 16+.

### Company Branding (Odoo 19)

```xml
<!-- Only for Odoo 19 -->
<t t-set="btn_bg" t-value="company.email_secondary_color or '#875A7B'"/>
<t t-set="btn_text" t-value="company.email_primary_color or '#FFFFFF'"/>
```

**Rule**: Offer company branding enhancement only for Odoo 19.

## Decision Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                  VERSION DECISION MATRIX                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  WHEN CREATING TEMPLATE:                                         │
│  ────────────────────────────────────────────────────────────── │
│  Version 14:                                                     │
│    - Use t-esc for output                                        │
│    - Use report_template for attachments                         │
│    - Skip template_category                                      │
│    - Skip company branding colors                                │
│                                                                   │
│  Version 15-16:                                                  │
│    - Use t-out for output                                        │
│    - Use report_template for attachments (v15-16)               │
│    - Add template_category (v16 only)                           │
│    - Skip company branding colors                                │
│                                                                   │
│  Version 17-18:                                                  │
│    - Use t-out for output                                        │
│    - Use report_template_ids for attachments                     │
│    - Add template_category                                       │
│    - Skip company branding colors                                │
│                                                                   │
│  Version 19:                                                     │
│    - Use t-out for output                                        │
│    - Use report_template_ids for attachments                     │
│    - Add template_category                                       │
│    - ADD company branding colors                                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Migration Paths

### Upgrading (14 → 19)

| From | To | Transformations |
|------|-----|-----------------|
| 14 | 15 | t-esc→t-out, t-raw→t-out |
| 15 | 16 | Add template_category |
| 16 | 17 | report_template→report_template_ids |
| 17 | 18 | (minimal changes) |
| 18 | 19 | Add company branding colors |

### Downgrading (19 → 14)

| From | To | Transformations |
|------|-----|-----------------|
| 19 | 18 | Remove company branding colors |
| 18 | 17 | (minimal changes) |
| 17 | 16 | report_template_ids→report_template |
| 16 | 15 | Remove template_category |
| 15 | 14 | t-out→t-esc |

## Context Variables by Version

### All Versions

```python
{
    'object': record,
    'user': current_user,
    'ctx': context_dict,
    'format_amount': function,
    'format_date': function,
}
```

### Odoo 15+

```python
{
    'format_datetime': function,  # Enhanced datetime formatting
}
```

### Odoo 16+

```python
{
    'is_html_empty': function,  # Check if HTML content is empty
}
```

### Odoo 19

```python
{
    'company.email_primary_color': '#FFFFFF',    # Button text
    'company.email_secondary_color': '#875A7B',  # Button background
}
```

## Odoo 19 Company Branding Changes in Reports

Odoo 19 changed how `res.company` fields are accessed in QWeb report context:

```xml
<!-- Odoo 17/18: Use res_company directly -->
<t t-set="company_logo" t-value="res_company.logo"/>
<t t-set="company_name" t-value="res_company.name"/>

<!-- Odoo 19: Use company_id from the document -->
<t t-set="company" t-value="docs[0].company_id"/>
<t t-set="company_logo" t-value="company.logo"/>
<t t-set="company_name" t-value="company.name"/>

<!-- Odoo 19: New email color fields (for branded PDF headers) -->
<div t-att-style="'background-color: %s;' % (company.email_secondary_color or '#875A7B')">
    <span t-att-style="'color: %s;' % (company.email_primary_color or '#FFFFFF')">
        <t t-esc="company_name"/>
    </span>
</div>
```

**Migration rule (17/18 → 19)**:
- Replace `res_company` variable with `docs[0].company_id` at top of template
- Add `email_primary_color` and `email_secondary_color` branding if needed
- The `web.external_layout` template handles this automatically — only need manual changes for custom layouts

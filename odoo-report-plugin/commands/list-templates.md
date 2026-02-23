---
title: 'List Templates'
read_only: true
type: 'command'
description: 'List all email templates and QWeb reports for a model or module'
---

# List Templates

List all email templates and QWeb reports for a **specific model**, **module**, or **project**.

## Usage

```
/list-templates [filter]
/list-templates sale.order
/list-templates --module sale
/list-templates --project relief_center
/list-templates --all
```

### Natural Language

```
"Show me all email templates for sale orders"
"List templates in the invoice module"
"What templates are in my relief_center project?"
```

## Output Format

```
════════════════════════════════════════════════════════════════════
                    EMAIL TEMPLATES & REPORTS
════════════════════════════════════════════════════════════════════

Filter: model=sale.order
Found: 8 templates, 3 reports

────────────────────────────────────────────────────────────────────
EMAIL TEMPLATES (mail.template)
────────────────────────────────────────────────────────────────────

1. sale.email_template_edi_sale
   Name: Sales: Send Quotation / Order
   Model: sale.order
   Subject: {{ object.name }}
   Layout: mail.mail_notification_layout
   Attachments: 1 report
   Location: odoo/addons/sale/data/mail_template_data.xml:15

2. sale.mail_template_sale_confirmation
   Name: Sales: Order Confirmation
   Model: sale.order
   Subject: Order Confirmation {{ object.name }}
   Layout: mail.mail_notification_layout
   Location: odoo/addons/sale/data/mail_template_data.xml:45

3. my_module.email_template_custom_quote
   Name: Custom: Enhanced Quotation
   Model: sale.order
   Subject: Quotation {{ object.name }} - {{ object.company_id.name }}
   Layout: mail.mail_notification_light
   Location: projects/my_module/data/mail_template.xml:10

...

────────────────────────────────────────────────────────────────────
QWEB REPORTS (ir.actions.report)
────────────────────────────────────────────────────────────────────

1. sale.action_report_saleorder
   Name: Quotation / Order
   Model: sale.order
   Type: qweb-pdf
   Template: sale.report_saleorder
   Binding: Print menu
   Location: odoo/addons/sale/report/sale_report.xml:5

2. sale.action_report_saleorder_pro_forma
   Name: Pro-Forma Invoice
   Model: sale.order
   Type: qweb-pdf
   Template: sale.report_saleorder_pro_forma
   Location: odoo/addons/sale/report/sale_report.xml:20

3. my_module.action_report_custom_quote
   Name: Custom Quotation Report
   Model: sale.order
   Type: qweb-pdf
   Template: my_module.report_custom_quote
   Location: projects/my_module/reports/report_actions.xml:5

════════════════════════════════════════════════════════════════════
```

## Filter Options

| Option | Description | Example |
|--------|-------------|---------|
| `MODEL` | Filter by model | `sale.order` |
| `--module` | Filter by module | `--module sale` |
| `--project` | Filter by project | `--project relief_center` |
| `--type email` | Only email templates | `--type email` |
| `--type report` | Only QWeb reports | `--type report` |
| `--custom` | Only custom (non-core) | `--custom` |
| `--all` | List all templates | `--all` |

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                LIST TEMPLATES QUICK REFERENCE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  BY MODEL:      /list-templates sale.order                       │
│  BY MODULE:     /list-templates --module account                 │
│  BY PROJECT:    /list-templates --project relief_center          │
│  CUSTOM ONLY:   /list-templates --custom                         │
│  ALL:           /list-templates --all                            │
│                                                                   │
│  OUTPUT INCLUDES:                                                │
│  • Template XML ID                                               │
│  • Display name                                                  │
│  • Target model                                                  │
│  • Subject/template reference                                    │
│  • File location                                                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Related Commands

| Command | Description |
|---------|-------------|
| `/analyze-template` | Analyze specific template |
| `/create-email-template` | Create new template |
| `/create-qweb-report` | Create new report |

---

*Part of Odoo Report Plugin v1.0*

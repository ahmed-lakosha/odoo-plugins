---
title: 'Preview Template'
read_only: true
type: 'command'
description: 'Generate a preview of template output with sample or real data'
---

# Preview Template

Generate a preview of email template or QWeb report output with **sample data** or **real record data**.

## Usage

```
/preview-template [template-id] [--record ID]
/preview-template sale.email_template_edi_sale --record 42
/preview-template my_module.email_template_custom --sample
```

### Natural Language

```
"Preview the quotation email template"
"Show me what the invoice email looks like"
"Preview report for order SO042"
```

## Preview Output

```
════════════════════════════════════════════════════════════════════
                    TEMPLATE PREVIEW
════════════════════════════════════════════════════════════════════

Template: sale.email_template_edi_sale
Model: sale.order
Record: SO042 (id: 42)

────────────────────────────────────────────────────────────────────
EMAIL HEADERS
────────────────────────────────────────────────────────────────────

From:    John Doe <john@company.com>
To:      customer@email.com
CC:      (none)
Subject: Quotation SO042

────────────────────────────────────────────────────────────────────
EMAIL BODY (rendered HTML)
────────────────────────────────────────────────────────────────────

Dear Valued Customer,

Please find attached your quotation SO042 amounting to $1,234.56.

This offer is valid until 2026-02-15.

Do not hesitate to contact us if you have any questions.

Best regards,
ACME Corporation

────────────────────────────────────────────────────────────────────
ATTACHMENTS
────────────────────────────────────────────────────────────────────

1. Quotation - SO042.pdf (generated from report)
   Size: ~125 KB (estimated)
   Report: sale.action_report_saleorder

════════════════════════════════════════════════════════════════════

Options:
• Save HTML: /preview-template --save-html preview.html
• Save PDF:  /preview-template --save-pdf preview.pdf
• Open in browser: /preview-template --browser
```

## Preview Options

| Option | Description |
|--------|-------------|
| `--record ID` | Use specific record for preview |
| `--sample` | Use sample/demo data |
| `--save-html FILE` | Save rendered HTML |
| `--save-pdf FILE` | Save as PDF (reports only) |
| `--browser` | Open in default browser |
| `--raw` | Show raw HTML without rendering |

## Related Commands

| Command | Description |
|---------|-------------|
| `/debug-template` | Debug rendering issues |
| `/analyze-template` | Analyze template structure |

---

*Part of Odoo Report Plugin v1.0*

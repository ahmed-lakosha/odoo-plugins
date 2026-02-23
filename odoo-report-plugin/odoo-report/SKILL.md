---
name: odoo-report
description: "Professional Odoo Email Templates & QWeb Reports - Complete toolkit for creating, managing, and debugging email templates and PDF reports across Odoo 14-19. Includes wkhtmltopdf setup, Arabic/RTL support, bilingual patterns, and comprehensive validation."
version: "2.0.0"
author: "TaqaTechno"
license: "LGPL-3"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebFetch
metadata:
  mode: "codebase"
  supported-versions: ["14", "15", "16", "17", "18", "19"]
  primary-version: "17"
  template-patterns: "50+"
  qweb-patterns: "30+"
  categories:
    - email-templates
    - qweb-reports
    - pdf-generation
    - mail-template
    - notification-layouts
---

# Odoo Email Templates & QWeb Reports Skill (v2.0)

A comprehensive skill for creating, managing, debugging, and migrating Odoo email templates and QWeb reports across versions 14-19. Features wkhtmltopdf configuration, Arabic/RTL support, bilingual report patterns, and intelligent version-aware syntax.

## Configuration

- **Supported Versions**: Odoo 14, 15, 16, 17, 18, 19
- **Primary Version**: Odoo 17
- **Templates Database**: 400+ templates analyzed
- **Pattern Library**: 50+ email patterns, 30+ QWeb patterns
- **Core Model**: `mail.template`
- **Rendering Engines**: inline_template (Jinja2), QWeb

---

## Quick Reference

### Template Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ODOO EMAIL TEMPLATE ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  mail.template                                                               │
│  ├── Inherits: mail.render.mixin (rendering engine)                          │
│  ├── Inherits: template.reset.mixin (reset - Odoo 16+)                       │
│  │                                                                           │
│  ├── Header Fields (inline_template engine):                                 │
│  │   • subject        • email_from       • email_to                          │
│  │   • email_cc       • reply_to         • partner_to                        │
│  │                                                                           │
│  ├── Content Fields (QWeb engine):                                           │
│  │   • body_html                                                             │
│  │                                                                           │
│  ├── Attachment Fields:                                                      │
│  │   • attachment_ids (static)                                               │
│  │   • report_template (Odoo 14-16) / report_template_ids (Odoo 17+)        │
│  │   • report_name (dynamic filename)                                        │
│  │                                                                           │
│  └── Configuration:                                                          │
│      • email_layout_xmlid   • auto_delete    • mail_server_id               │
│      • use_default_to       • scheduled_date                                 │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Rendering Flow

```
mail.template.send_mail_batch(res_ids)
    │
    ├─► _generate_template(res_ids, render_fields)
    │       │
    │       ├─► _classify_per_lang()        # Group by language
    │       │
    │       ├─► _render_field() for each:
    │       │       • subject (inline_template)
    │       │       • body_html (qweb)
    │       │       • email_from, email_to, etc.
    │       │
    │       ├─► _generate_template_recipients()
    │       │
    │       ├─► _generate_template_attachments()
    │       │       • Static attachments
    │       │       • Report PDF generation
    │       │
    │       └─► Return rendered values dict
    │
    ├─► Create mail.mail records
    │
    ├─► Apply email_layout_xmlid (if set)
    │       └─► ir.qweb._render(layout_xmlid, context)
    │
    └─► Send via mail_server_id or default
```

---

## Two Rendering Engines

### 1. Inline Template Engine (Jinja2-like)

**Used for**: `subject`, `email_from`, `email_to`, `email_cc`, `reply_to`, `partner_to`, `lang`, `scheduled_date`

```python
# Simple field access
{{ object.name }}
{{ object.partner_id.name }}
{{ object.company_id.name }}

# Method calls
{{ object.get_portal_url() }}
{{ object.email_formatted }}

# Conditional expressions (ternary-like)
{{ object.state == 'draft' and 'Quotation' or 'Order' }}

# Or chains (fallback)
{{ (object.user_id.email_formatted or object.company_id.email_formatted or user.email_formatted) }}

# Context access
{{ ctx.get('proforma') and 'Proforma' or '' }}

# String operations
{{ (object.name or '').replace('/', '-') }}
```

### 2. QWeb Engine

**Used for**: `body_html`

**Output Tags**:
```xml
<!-- Escaped output (safe) -->
<t t-out="object.name"/>
<t t-out="object.partner_id.name or 'Unknown'"/>

<!-- Format with helper -->
<t t-out="format_amount(object.amount_total, object.currency_id)"/>
<t t-out="format_date(object.date_order)"/>
<t t-out="format_datetime(object.create_date, tz='UTC', dt_format='long')"/>
```

**Conditional Tags**:
```xml
<t t-if="object.state == 'draft'">
    This is a draft.
</t>
<t t-elif="object.state == 'sent'">
    This has been sent.
</t>
<t t-else="">
    This is confirmed.
</t>
```

**Loop Tags**:
```xml
<t t-foreach="object.order_line" t-as="line">
    <tr>
        <td t-out="line.name"/>
        <td t-out="line.product_uom_qty"/>
        <td t-out="format_amount(line.price_subtotal, object.currency_id)"/>
    </tr>
</t>
```

**Attribute Tags**:
```xml
<!-- Dynamic attribute -->
<a t-att-href="object.get_portal_url()">View</a>

<!-- Formatted attribute (with interpolation) -->
<a t-attf-href="/web/image/product.product/{{ line.product_id.id }}/image_128">
    <img t-attf-src="/web/image/product.product/{{ line.product_id.id }}/image_128"/>
</a>
```

---

## Version Decision Matrix

| Feature | Odoo 14 | Odoo 15 | Odoo 16 | Odoo 17 | Odoo 18 | Odoo 19 |
|---------|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|
| `t-out` syntax | N | **Y** | **Y** | **Y** | **Y** | **Y** |
| `t-esc` (legacy) | **Y** | **Y** | **Y** | **Y** | **Y** | **Y** |
| `render_engine='qweb'` | N | **Y** | **Y** | **Y** | **Y** | **Y** |
| `template_category` | N | N | **Y** | **Y** | **Y** | **Y** |
| `report_template_ids` M2M | N | N | N | **Y** | **Y** | **Y** |
| Company branding colors | N | N | N | N | N | **Y** |
| `email_primary_color` | N | N | N | N | N | **Y** |
| `email_secondary_color` | N | N | N | N | N | **Y** |
| `mail_notification_layout_with_responsible_signature` | N | N | **Y** | **Y** | **Y** | **Y** |
| Enhanced security in sandbox | N | N | **Y** | **Y** | **Y** | **Y** |

---

## Email Layout Templates

### Available Layouts

| Layout | Width | Use Case |
|--------|-------|----------|
| `mail.mail_notification_layout` | 900px | Full notifications with header/footer |
| `mail.mail_notification_light` | 590px | Simple notifications |
| `mail.mail_notification_layout_with_responsible_signature` | 900px | Uses record's `user_id` signature |

### Layout Context Variables

```python
{
    # Message Information
    'message': mail.message,           # Message object with body, record_name
    'subtype': mail.message.subtype,   # Message subtype

    # Display Control
    'has_button_access': Boolean,      # Show action button
    'button_access': {                 # CTA button config
        'url': String,
        'title': String
    },
    'subtitles': List[String],         # Header subtitles

    # Record Information
    'record': record,                  # The document
    'record_name': String,             # Display name
    'model_description': String,       # Human-readable model

    # Tracking
    'tracking_values': [               # Field changes
        (field_name, old_value, new_value),
    ],

    # Signature
    'email_add_signature': Boolean,    # Include signature
    'signature': HTML,                 # User signature

    # Company
    'company': res.company,            # Company object
    'website_url': String,             # Base URL

    # Branding (Odoo 19+)
    'company.email_primary_color': String,    # Button text color
    'company.email_secondary_color': String,  # Button background

    # Utilities
    'is_html_empty': Function,         # Check empty HTML
}
```

---

## Commands Reference

### Template Creation Commands

| Command | Description |
|---------|-------------|
| `/create-email-template` | Create a new email template for any model |
| `/create-qweb-report` | Create a new QWeb PDF report |
| `/create-notification` | Create a notification template with layout |
| `/create-digest-email` | Create a digest/summary email template |

### Template Management Commands

| Command | Description |
|---------|-------------|
| `/list-templates` | List all templates for a model or module |
| `/analyze-template` | Analyze an existing template for issues |
| `/debug-template` | Debug template rendering issues |
| `/preview-template` | Generate preview of template output |

### Migration Commands

| Command | Description |
|---------|-------------|
| `/migrate-template` | Migrate template between Odoo versions |
| `/fix-template` | Fix common template issues |
| `/validate-template` | Validate template syntax and context |

### QWeb Report Commands

| Command | Description |
|---------|-------------|
| `/create-report-action` | Create report action with menu/button |
| `/style-report` | Add CSS styling to QWeb report |
| `/add-header-footer` | Add header/footer to report |

---

## Template Patterns Library

### Pattern 1: Basic Notification Email

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data noupdate="1">
        <record id="email_template_basic_notification" model="mail.template">
            <field name="name">Basic Notification</field>
            <field name="model_id" ref="model_your_model"/>
            <field name="subject">{{ object.name }} - Notification</field>
            <field name="email_from">{{ (object.company_id.email or user.email_formatted) }}</field>
            <field name="email_to">{{ object.partner_id.email }}</field>
            <field name="email_layout_xmlid">mail.mail_notification_layout</field>
            <field name="body_html" type="html">
<div>
    <p>Dear <t t-out="object.partner_id.name"/>,</p>
    <p>This is a notification regarding <strong t-out="object.name"/>.</p>
    <t t-if="object.description">
        <p t-out="object.description"/>
    </t>
    <p>Best regards,<br/><t t-out="object.company_id.name"/></p>
</div>
            </field>
            <field name="auto_delete" eval="True"/>
        </record>
    </data>
</odoo>
```

### Pattern 2: Document Email with Report Attachment

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data noupdate="1">
        <record id="email_template_document" model="mail.template">
            <field name="name">Send Document</field>
            <field name="model_id" ref="model_your_model"/>
            <field name="subject">
                {{ object.state in ('draft', 'sent') and 'Quotation' or 'Order' }} {{ object.name }}
            </field>
            <field name="email_from">{{ (object.user_id.email_formatted or user.email_formatted) }}</field>
            <field name="partner_to">{{ object.partner_id.id }}</field>
            <!-- Odoo 17+ use report_template_ids -->
            <field name="report_template_ids" eval="[(4, ref('module.report_action_id'))]"/>
            <field name="report_name">{{ (object.name or 'Document').replace('/', '-') }}</field>
            <field name="email_layout_xmlid">mail.mail_notification_layout</field>
            <field name="body_html" type="html">
<div>
    <t t-set="doc_name" t-value="'quotation' if object.state in ('draft', 'sent') else 'order'"/>
    <p>Dear <t t-out="object.partner_id.name"/>,</p>
    <p>Please find attached your <t t-out="doc_name"/>
       <strong t-out="object.name"/> amounting to
       <strong t-out="format_amount(object.amount_total, object.currency_id)"/>.</p>
    <p>Do not hesitate to contact us if you have any questions.</p>
</div>
            </field>
        </record>
    </data>
</odoo>
```

### Pattern 3: Order Lines Table

```xml
<table border="0" cellpadding="0" cellspacing="0" width="100%"
       style="border-collapse: collapse;">
    <thead>
        <tr style="background-color: #875A7B; color: white;">
            <th style="padding: 8px;">Product</th>
            <th style="padding: 8px;">Quantity</th>
            <th style="padding: 8px; text-align: right;">Price</th>
        </tr>
    </thead>
    <tbody>
        <t t-foreach="object.order_line" t-as="line">
            <t t-if="line.display_type == 'line_section'">
                <tr>
                    <td colspan="3" style="font-weight: bold; padding: 8px; background-color: #f5f5f5;">
                        <t t-out="line.name"/>
                    </td>
                </tr>
            </t>
            <t t-elif="line.display_type == 'line_note'">
                <tr>
                    <td colspan="3" style="font-style: italic; padding: 8px;">
                        <t t-out="line.name"/>
                    </td>
                </tr>
            </t>
            <t t-else="">
                <tr t-att-style="'background-color: #f9f9f9' if line_index % 2 == 0 else ''">
                    <td style="padding: 8px;">
                        <t t-out="line.product_id.name"/>
                    </td>
                    <td style="padding: 8px; text-align: center;">
                        <t t-out="line.product_uom_qty"/>
                        <t t-out="line.product_uom.name"/>
                    </td>
                    <td style="padding: 8px; text-align: right;">
                        <t t-out="format_amount(line.price_subtotal, object.currency_id)"/>
                    </td>
                </tr>
            </t>
        </t>
    </tbody>
    <tfoot>
        <tr style="font-weight: bold; background-color: #f5f5f5;">
            <td colspan="2" style="padding: 8px; text-align: right;">Total:</td>
            <td style="padding: 8px; text-align: right;">
                <t t-out="format_amount(object.amount_total, object.currency_id)"/>
            </td>
        </tr>
    </tfoot>
</table>
```

### Pattern 4: CTA Button

```xml
<t t-set="button_color" t-value="company.email_secondary_color or '#875A7B'"/>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
    <tr>
        <td align="center" style="padding: 16px;">
            <a t-att-href="object.get_portal_url()"
               t-att-style="'display: inline-block; padding: 10px 20px; color: #ffffff; text-decoration: none; border-radius: 3px; background-color: %s' % button_color">
                View Online
            </a>
        </td>
    </tr>
</table>
```

### Pattern 5: Conditional Content Based on State

```xml
<t t-if="object.state == 'draft'">
    <p style="color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 4px;">
        <strong>Draft:</strong> This document is not yet confirmed.
    </p>
</t>
<t t-elif="object.state == 'sent'">
    <p style="color: #0c5460; background-color: #d1ecf1; padding: 10px; border-radius: 4px;">
        <strong>Awaiting Confirmation:</strong> Please review and confirm.
    </p>
</t>
<t t-elif="object.state == 'done'">
    <p style="color: #155724; background-color: #d4edda; padding: 10px; border-radius: 4px;">
        <strong>Completed:</strong> This document has been processed.
    </p>
</t>
```

### Pattern 6: Payment Information Block

```xml
<t t-if="object.payment_state not in ('paid', 'in_payment')">
    <div style="background-color: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 4px;">
        <h4 style="margin: 0 0 10px 0;">Payment Information</h4>
        <t t-if="object.payment_reference">
            <p><strong>Reference:</strong> <t t-out="object.payment_reference"/></p>
        </t>
        <t t-if="object.partner_bank_id">
            <p><strong>Bank Account:</strong> <t t-out="object.partner_bank_id.acc_number"/></p>
            <t t-if="object.partner_bank_id.bank_id">
                <p><strong>Bank:</strong> <t t-out="object.partner_bank_id.bank_id.name"/></p>
            </t>
        </t>
        <t t-if="object.amount_residual">
            <p><strong>Amount Due:</strong>
               <t t-out="format_amount(object.amount_residual, object.currency_id)"/>
            </p>
        </t>
    </div>
</t>
```

---

## QWeb Report Patterns

### Pattern 1: Basic Report Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- Report Action -->
    <record id="action_report_document" model="ir.actions.report">
        <field name="name">Document Report</field>
        <field name="model">your.model</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">module_name.report_document_template</field>
        <field name="report_file">module_name.report_document_template</field>
        <field name="print_report_name">'Document - %s' % object.name</field>
        <field name="binding_model_id" ref="model_your_model"/>
        <field name="binding_type">report</field>
    </record>

    <!-- Report Template -->
    <template id="report_document_template">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="web.external_layout">
                    <div class="page">
                        <h2><t t-out="doc.name"/></h2>

                        <div class="row">
                            <div class="col-6">
                                <strong>Date:</strong>
                                <span t-field="doc.date"/>
                            </div>
                            <div class="col-6 text-end">
                                <strong>Reference:</strong>
                                <span t-out="doc.reference"/>
                            </div>
                        </div>

                        <!-- Content goes here -->

                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

### Pattern 2: Report with Table

```xml
<table class="table table-sm o_main_table">
    <thead>
        <tr>
            <th class="text-start">Description</th>
            <th class="text-center">Quantity</th>
            <th class="text-end">Unit Price</th>
            <th class="text-end">Amount</th>
        </tr>
    </thead>
    <tbody>
        <t t-foreach="doc.line_ids" t-as="line">
            <tr>
                <td><span t-field="line.name"/></td>
                <td class="text-center"><span t-field="line.quantity"/></td>
                <td class="text-end"><span t-field="line.price_unit"/></td>
                <td class="text-end"><span t-field="line.price_subtotal"/></td>
            </tr>
        </t>
    </tbody>
</table>

<!-- Totals -->
<div class="row justify-content-end">
    <div class="col-4">
        <table class="table table-sm">
            <tr>
                <td><strong>Subtotal</strong></td>
                <td class="text-end"><span t-field="doc.amount_untaxed"/></td>
            </tr>
            <tr>
                <td>Taxes</td>
                <td class="text-end"><span t-field="doc.amount_tax"/></td>
            </tr>
            <tr class="border-top">
                <td><strong>Total</strong></td>
                <td class="text-end"><span t-field="doc.amount_total"/></td>
            </tr>
        </table>
    </div>
</div>
```

### Pattern 3: Page Break Control

```xml
<!-- Force page break before element -->
<div style="page-break-before: always;">
    <h3>New Page Content</h3>
</div>

<!-- Prevent page break inside element -->
<div style="page-break-inside: avoid;">
    <table><!-- Table that should stay together --></table>
</div>

<!-- Force page break after element -->
<div style="page-break-after: always;">
    <p>End of section</p>
</div>
```

---

## Validation Rules

### MANDATORY Pre-Flight Checks

Before creating any template, Claude MUST validate:

```
┌─────────────────────────────────────────────────────────────────┐
│                 TEMPLATE VALIDATION CHECKLIST                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. MODEL VALIDATION                                             │
│     □ Model exists in target Odoo version                        │
│     □ Model has required fields (partner_id, etc.)               │
│     □ Model inherits mail.thread (if notification)               │
│                                                                   │
│  2. FIELD VALIDATION                                             │
│     □ All {{ object.field }} references exist                    │
│     □ All t-out="object.field" references exist                  │
│     □ Related fields are valid (object.partner_id.name)          │
│                                                                   │
│  3. SYNTAX VALIDATION                                            │
│     □ QWeb tags properly closed                                  │
│     □ Jinja2 expressions balanced {{ }}                          │
│     □ No mixing of t-esc (Odoo 14) and t-out (Odoo 15+)         │
│                                                                   │
│  4. VERSION COMPATIBILITY                                        │
│     □ report_template vs report_template_ids (Odoo 17+)          │
│     □ template_category (Odoo 16+)                               │
│     □ Company branding colors (Odoo 19+)                         │
│                                                                   │
│  5. SECURITY VALIDATION                                          │
│     □ No unsafe eval() or exec()                                 │
│     □ No arbitrary file access                                   │
│     □ Sandbox-safe expressions                                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Error Recovery

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `AttributeError: 'NoneType' has no attribute 'name'` | Null field access | Use `object.field_id.name or ''` |
| `QWebException: t-esc is deprecated` | Old syntax in Odoo 15+ | Replace `t-esc` with `t-out` |
| `KeyError: 'format_amount'` | Missing context helper | Ensure `mail.render.mixin` is inherited |
| `ValidationError: Invalid XML` | Malformed QWeb | Check XML structure, close all tags |
| `NameError: name 'object' is not defined` | Wrong rendering context | Use template's model context |

### Debug Template Rendering

```python
# In Odoo shell
template = env['mail.template'].browse(TEMPLATE_ID)
record = env['your.model'].browse(RECORD_ID)

# Render and inspect
rendered = template._render_field(
    'body_html',
    [record.id],
    compute_lang=True
)
print(rendered[record.id])
```

---

## Module-Specific Templates

### Sales Module

| Template ID | Purpose | Model |
|-------------|---------|-------|
| `email_template_edi_sale` | Send quotation/order | sale.order |
| `mail_template_sale_confirmation` | Order confirmation | sale.order |
| `mail_template_sale_payment_executed` | Payment received | sale.order |

### Purchase Module

| Template ID | Purpose | Model |
|-------------|---------|-------|
| `email_template_edi_purchase` | Send RFQ | purchase.order |
| `email_template_edi_purchase_done` | Send PO | purchase.order |
| `email_template_edi_purchase_reminder` | Delivery reminder | purchase.order |

### Accounting Module

| Template ID | Purpose | Model |
|-------------|---------|-------|
| `email_template_edi_invoice` | Send invoice | account.move |
| `email_template_edi_credit_note` | Send credit note | account.move |
| `mail_template_data_payment_receipt` | Payment receipt | account.payment |

### HR Recruitment

| Template ID | Purpose | Model |
|-------------|---------|-------|
| `email_template_data_applicant_employee` | Applicant to employee | hr.employee |
| `email_template_data_applicant_congratulations` | Congratulations | hr.applicant |
| `email_template_data_applicant_refuse` | Refusal notice | hr.applicant |

---

## Best Practices

### 1. Always Use Fallbacks

```xml
<!-- Good -->
<t t-out="object.partner_id.name or 'Valued Customer'"/>

<!-- Bad - will fail if partner_id is None -->
<t t-out="object.partner_id.name"/>
```

### 2. Use Format Helpers

```xml
<!-- Good - consistent formatting -->
<t t-out="format_amount(object.amount_total, object.currency_id)"/>
<t t-out="format_date(object.date_order)"/>

<!-- Bad - manual formatting -->
<t t-out="'$%.2f' % object.amount_total"/>
```

### 3. Respect Translations

```xml
<!-- Good - translatable -->
<p>Dear <t t-out="object.partner_id.name"/>,</p>

<!-- Bad - hardcoded in template, use data records instead -->
```

### 4. Use Layouts for Consistency

```xml
<!-- Good - uses company branding -->
<field name="email_layout_xmlid">mail.mail_notification_layout</field>

<!-- Avoid - custom inline styling for every email -->
```

### 5. Handle Empty HTML

```xml
<t t-if="not is_html_empty(object.description)">
    <div t-out="object.description"/>
</t>
```

### 6. Version-Specific Syntax

```xml
<!-- Odoo 15+ -->
<t t-out="value"/>

<!-- Odoo 14 only -->
<t t-esc="value"/>
```

### 7. Report Attachment Handling

```xml
<!-- Odoo 14-16: Single report -->
<field name="report_template" ref="module.report_action"/>

<!-- Odoo 17+: Multiple reports -->
<field name="report_template_ids" eval="[(4, ref('module.report_action'))]"/>
```

### 8. Dynamic Filenames

```python
# Safe filename generation
<field name="report_name">{{ (object.name or 'Document').replace('/', '-') }}</field>
```

---

## wkhtmltopdf Setup & Configuration

### ⚠️ CRITICAL: wkhtmltopdf is REQUIRED for PDF Reports

Odoo uses wkhtmltopdf to convert QWeb HTML to PDF. Without proper configuration, PDF generation will fail.

### Installation

```bash
# Windows
winget install wkhtmltopdf.wkhtmltox
# OR download from: https://wkhtmltopdf.org/downloads.html

# Ubuntu/Debian
sudo apt-get install wkhtmltopdf

# macOS
brew install wkhtmltopdf
```

### Odoo Configuration (MANDATORY)

Add to your `odoo.conf`:

```ini
[options]
# Windows
bin_path = C:\Program Files\wkhtmltopdf\bin

# Linux
bin_path = /usr/local/bin

# macOS (Homebrew)
bin_path = /opt/homebrew/bin
```

### Verification

After server restart, check logs for:
```
Will use the Wkhtmltopdf binary at C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Unable to find Wkhtmltopdf` | bin_path not configured | Add bin_path to odoo.conf |
| `PDF generation timeout` | Network resources requested | Remove external URLs (fonts, images) |
| `Blank PDF generated` | CSS/SCSS errors | Check browser console, validate SCSS |
| `Exit with code 1` | HTML syntax error | Validate QWeb template XML |

### Key Limitation: OFFLINE Mode

**wkhtmltopdf runs WITHOUT network access**. This means:
- ❌ Google Fonts CDN will NOT load
- ❌ External images will NOT render
- ❌ External CSS will NOT apply
- ✅ Use `web.external_layout` for fonts
- ✅ Embed images as base64 or use Odoo attachments

---

## Arabic/RTL & Multilingual Reports

### ⚠️ CRITICAL: UTF-8 Encoding Requirement

Arabic text displaying as `ÙØ§ØªÙˆØ±Ø©` instead of `فاتورة` indicates UTF-8 → Latin-1 encoding corruption.

### MANDATORY Template Wrapper

**ALWAYS** use this structure for non-Latin text support:

```xml
<template id="report_document">
    <t t-call="web.html_container">        <!-- ✅ Provides UTF-8 meta tag -->
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout"> <!-- ✅ Loads proper fonts -->
                <div class="page">
                    <!-- Your content here -->
                </div>
            </t>
        </t>
    </t>
</template>
```

### ❌ WRONG Patterns (Will Cause Encoding Issues)

```xml
<!-- WRONG: Custom HTML without proper encoding -->
<template id="report_document">
    <html>
        <head><title>Report</title></head>
        <body>
            فاتورة  <!-- Will display as ÙØ§ØªÙˆØ±Ø© -->
        </body>
    </html>
</template>

<!-- WRONG: Missing web.html_container -->
<template id="report_document">
    <t t-foreach="docs" t-as="o">
        <t t-call="web.external_layout">
            <!-- Missing outer container! -->
        </t>
    </t>
</template>
```

### Bilingual Label Pattern

```xml
<!-- Side-by-side: English | Arabic -->
<th style="background: #1a5276; color: white; padding: 12px;">
    Date | التاريخ
</th>

<!-- Stacked: Arabic on top, English below -->
<th style="background: #1a5276; color: white; padding: 12px;">
    <div>التاريخ</div>
    <div style="font-size: 10px; font-weight: normal;">Date</div>
</th>
```

### RTL Text Alignment

```xml
<!-- Force RTL for Arabic paragraphs -->
<div style="direction: rtl; text-align: right;">
    يرجى إرسال حوالاتكم على الحساب المذكور أعلاه
</div>

<!-- Mixed content: Use CSS classes -->
<style>
    .rtl { direction: rtl; text-align: right; }
    .ltr { direction: ltr; text-align: left; }
</style>
```

### Currency Symbol Corruption

If `$` displays as `$Â` or similar:
- **Cause**: Same UTF-8 encoding issue
- **Solution**: Use `web.html_container` wrapper

---

## Paper Format Configuration

### Custom Paper Format Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="paperformat_custom" model="report.paperformat">
        <field name="name">Custom Invoice Format</field>
        <field name="default" eval="False"/>
        <field name="format">A4</field>
        <field name="orientation">Portrait</field>
        <field name="margin_top">20</field>
        <field name="margin_bottom">20</field>
        <field name="margin_left">15</field>
        <field name="margin_right">15</field>
        <field name="header_line" eval="False"/>
        <field name="header_spacing">0</field>
        <field name="dpi">90</field>
    </record>
</odoo>
```

### Linking Paper Format to Report

```xml
<record id="action_report_invoice" model="ir.actions.report">
    <field name="name">Custom Invoice</field>
    <field name="model">account.move</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">module.report_invoice_template</field>
    <field name="paperformat_id" ref="module.paperformat_custom"/>
    <!-- ... other fields ... -->
</record>
```

### Standard Paper Formats

| Format | Dimensions | Use Case |
|--------|------------|----------|
| `A4` | 210 × 297 mm | Standard international |
| `Letter` | 216 × 279 mm | US standard |
| `Legal` | 216 × 356 mm | Legal documents |
| `A5` | 148 × 210 mm | Small documents |
| `Custom` | Set page_width/page_height | Special sizes |

### Orientation Options

- `Portrait` - Vertical (default)
- `Landscape` - Horizontal (wide tables, charts)

---

## Report SCSS Styling

### Correct Asset Bundle

```python
# __manifest__.py
{
    'assets': {
        'web.report_assets_common': [
            'module/static/src/scss/report_styles.scss',
        ],
    },
}
```

### ⚠️ CRITICAL: Google Fonts Pitfall

```scss
// ❌ BROKEN - Semicolons in URL break SCSS parsing
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

// ✅ FIXED - Use weight range syntax
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300..700&display=swap');

// ✅ BEST - Don't use Google Fonts (wkhtmltopdf is offline!)
// Rely on system fonts via web.external_layout
```

### Why External Fonts Fail

1. wkhtmltopdf runs **offline** (no network access)
2. Google Fonts CDN requests timeout
3. Result: Fallback to system fonts

### Recommended Font Stack

```scss
// Safe fonts that work in PDF generation
$report-font-family: 'DejaVu Sans', 'Arial', 'Helvetica', sans-serif;

.page {
    font-family: $report-font-family;
}
```

### Color Scheme Pattern

```scss
// Define colors once
$primary-color: #1a5276;      // Dark blue
$secondary-color: #d5dbdb;    // Light gray
$accent-color: #f39c12;       // Orange/Gold
$border-color: #bdc3c7;
$text-dark: #2c3e50;
$text-muted: #7f8c8d;

// Table header
.table-header, thead tr {
    background-color: $primary-color;
    color: white;
}

// Label cells
.label-cell {
    background-color: $secondary-color;
    color: $primary-color;
    font-weight: bold;
}

// Alternating rows
tbody tr:nth-child(even) {
    background-color: rgba($secondary-color, 0.3);
}
```

### Print-Specific Styles

```scss
@media print {
    // Ensure colors print
    * {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }

    // Page breaks
    .page-break-before { page-break-before: always; }
    .page-break-after { page-break-after: always; }
    .no-break { page-break-inside: avoid; }
}
```

---

## Debug Report Workflow

### Systematic Diagnosis Steps

```
┌─────────────────────────────────────────────────────────────────┐
│                 REPORT DEBUG WORKFLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  STEP 1: Check Infrastructure                                    │
│  ─────────────────────────────                                   │
│  □ wkhtmltopdf installed? → wkhtmltopdf --version               │
│  □ bin_path in odoo.conf?                                        │
│  □ Server restarted after config change?                         │
│  □ Server log shows wkhtmltopdf path?                           │
│                                                                   │
│  STEP 2: Validate Template Structure                             │
│  ────────────────────────────────────                            │
│  □ Uses web.html_container wrapper?                              │
│  □ Uses web.external_layout?                                     │
│  □ Has t-foreach docs loop?                                      │
│  □ Content inside div.page?                                      │
│                                                                   │
│  STEP 3: Check Report Action                                     │
│  ───────────────────────────                                     │
│  □ report_name matches template id?                              │
│  □ report_file matches template id?                              │
│  □ binding_model_id correct?                                     │
│  □ report_type = 'qweb-pdf'?                                     │
│                                                                   │
│  STEP 4: Test Render in Shell                                    │
│  ────────────────────────────                                    │
│  python odoo-bin shell -d DATABASE                               │
│  >>> report = env.ref('module.report_action')                    │
│  >>> pdf, _ = report._render_qweb_pdf([record_id])              │
│  >>> # Check console for errors                                  │
│                                                                   │
│  STEP 5: Browser Cache                                           │
│  ─────────────────────                                           │
│  □ Clear browser cache (Ctrl+Shift+R)                           │
│  □ Clear Odoo asset cache if needed                             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Issue-Specific Debugging

**Encoding Issues (Arabic, Chinese, etc.)**:
```
Symptom: ÙØ§ØªÙˆØ±Ø© instead of فاتورة
Cause: Missing web.html_container
Fix: Add <t t-call="web.html_container"> as outermost wrapper
```

**Blank PDF**:
```
Symptom: PDF generates but is empty
Causes:
  1. CSS syntax error → Check SCSS for semicolons in URLs
  2. Missing template → Verify report_name matches template id
  3. No records → Check docs variable has records
```

**Fonts Not Rendering**:
```
Symptom: Wrong font in PDF
Cause: External font URLs (wkhtmltopdf offline)
Fix: Use web.external_layout or system fonts only
```

**Timeout/Hang**:
```
Symptom: PDF generation hangs or times out
Cause: External resources being fetched
Fix: Remove all external URLs (CDNs, external images)
```

### Clear Asset Cache

```python
# Odoo shell
env['ir.attachment'].search([
    ('url', 'like', '/web/assets/')
]).unlink()
env.cr.commit()
```

---

## Bilingual Invoice Template (Complete Example)

Based on proven sadad_invoice implementation:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Paper Format -->
    <record id="paperformat_bilingual_invoice" model="report.paperformat">
        <field name="name">Bilingual Invoice A4</field>
        <field name="format">A4</field>
        <field name="orientation">Portrait</field>
        <field name="margin_top">25</field>
        <field name="margin_bottom">25</field>
        <field name="margin_left">15</field>
        <field name="margin_right">15</field>
        <field name="dpi">90</field>
    </record>

    <!-- Report Action -->
    <record id="action_report_bilingual_invoice" model="ir.actions.report">
        <field name="name">Bilingual Invoice</field>
        <field name="model">account.move</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">module.report_bilingual_invoice_document</field>
        <field name="report_file">module.report_bilingual_invoice_document</field>
        <field name="paperformat_id" ref="paperformat_bilingual_invoice"/>
        <field name="binding_model_id" ref="account.model_account_move"/>
        <field name="binding_type">report</field>
        <field name="print_report_name">'Invoice - %s' % object.name</field>
    </record>

    <!-- CRITICAL: Proper wrapper structure for UTF-8 -->
    <template id="report_bilingual_invoice_document">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="o">
                <t t-call="web.external_layout">
                    <t t-call="module.report_bilingual_invoice_content"/>
                </t>
            </t>
        </t>
    </template>

    <!-- Content Template -->
    <template id="report_bilingual_invoice_content">
        <div class="page" style="font-family: Arial, sans-serif; font-size: 12px;">

            <!-- Bilingual Header -->
            <div style="text-align: center; margin-bottom: 30px; border-bottom: 3px solid #1a5276; padding-bottom: 15px;">
                <h1 style="color: #1a5276; margin: 0;">
                    Sales Invoice | فاتورة مبيعات
                </h1>
                <h2 style="margin: 10px 0 0 0;" t-field="o.name"/>
            </div>

            <!-- Invoice Info Grid -->
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
                <tr>
                    <td style="width: 25%; border: 1px solid #bdc3c7; padding: 10px; background: #d5dbdb; color: #1a5276; font-weight: bold;">
                        Invoice Date | تاريخ الفاتورة
                    </td>
                    <td style="width: 25%; border: 1px solid #bdc3c7; padding: 10px;">
                        <span t-field="o.invoice_date" t-options='{"widget": "date"}'/>
                    </td>
                    <td style="width: 25%; border: 1px solid #bdc3c7; padding: 10px; background: #d5dbdb; color: #1a5276; font-weight: bold;">
                        Due Date | تاريخ الاستحقاق
                    </td>
                    <td style="width: 25%; border: 1px solid #bdc3c7; padding: 10px;">
                        <span t-field="o.invoice_date_due" t-options='{"widget": "date"}'/>
                    </td>
                </tr>
                <tr>
                    <td style="border: 1px solid #bdc3c7; padding: 10px; background: #d5dbdb; color: #1a5276; font-weight: bold;">
                        Customer | العميل
                    </td>
                    <td colspan="3" style="border: 1px solid #bdc3c7; padding: 10px;">
                        <span t-field="o.partner_id.name"/>
                    </td>
                </tr>
            </table>

            <!-- Invoice Lines Table -->
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
                <thead>
                    <tr style="background: #1a5276; color: white;">
                        <th style="padding: 12px; border: 1px solid #1a5276; text-align: center; width: 5%;">
                            #
                        </th>
                        <th style="padding: 12px; border: 1px solid #1a5276; text-align: left;">
                            <div>الوصف</div>
                            <div style="font-size: 10px; font-weight: normal;">Description</div>
                        </th>
                        <th style="padding: 12px; border: 1px solid #1a5276; text-align: center; width: 10%;">
                            <div>الكمية</div>
                            <div style="font-size: 10px; font-weight: normal;">Qty</div>
                        </th>
                        <th style="padding: 12px; border: 1px solid #1a5276; text-align: right; width: 15%;">
                            <div>السعر</div>
                            <div style="font-size: 10px; font-weight: normal;">Unit Price</div>
                        </th>
                        <th style="padding: 12px; border: 1px solid #1a5276; text-align: right; width: 15%;">
                            <div>الإجمالي</div>
                            <div style="font-size: 10px; font-weight: normal;">Subtotal</div>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <t t-set="line_num" t-value="0"/>
                    <t t-foreach="o.invoice_line_ids.filtered(lambda l: not l.display_type)" t-as="line">
                        <t t-set="line_num" t-value="line_num + 1"/>
                        <tr t-att-style="'background-color: #f9f9f9;' if line_index % 2 == 0 else ''">
                            <td style="border: 1px solid #bdc3c7; padding: 10px; text-align: center;">
                                <t t-out="line_num"/>
                            </td>
                            <td style="border: 1px solid #bdc3c7; padding: 10px;">
                                <t t-out="line.name"/>
                            </td>
                            <td style="border: 1px solid #bdc3c7; padding: 10px; text-align: center;">
                                <span t-field="line.quantity"/>
                                <t t-if="line.product_uom_id">
                                    <span t-field="line.product_uom_id.name"/>
                                </t>
                            </td>
                            <td style="border: 1px solid #bdc3c7; padding: 10px; text-align: right;">
                                <span t-field="line.price_unit" t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
                            </td>
                            <td style="border: 1px solid #bdc3c7; padding: 10px; text-align: right;">
                                <span t-field="line.price_subtotal" t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
                            </td>
                        </tr>
                    </t>
                </tbody>
            </table>

            <!-- Totals Section -->
            <div style="margin-top: 20px;">
                <table style="width: 40%; margin-left: auto; border-collapse: collapse;">
                    <tr>
                        <td style="border: 1px solid #bdc3c7; padding: 10px; background: #d5dbdb; color: #1a5276; font-weight: bold;">
                            Subtotal | المجموع الفرعي
                        </td>
                        <td style="border: 1px solid #bdc3c7; padding: 10px; text-align: right;">
                            <span t-field="o.amount_untaxed" t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
                        </td>
                    </tr>
                    <t t-if="o.amount_tax">
                        <tr>
                            <td style="border: 1px solid #bdc3c7; padding: 10px; background: #d5dbdb; color: #1a5276; font-weight: bold;">
                                Tax | الضريبة
                            </td>
                            <td style="border: 1px solid #bdc3c7; padding: 10px; text-align: right;">
                                <span t-field="o.amount_tax" t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
                            </td>
                        </tr>
                    </t>
                    <tr style="font-size: 14px;">
                        <td style="border: 2px solid #1a5276; padding: 12px; background: #1a5276; color: white; font-weight: bold;">
                            Total | الإجمالي
                        </td>
                        <td style="border: 2px solid #1a5276; padding: 12px; text-align: right; font-weight: bold;">
                            <span t-field="o.amount_total" t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
                        </td>
                    </tr>
                </table>
            </div>

            <!-- Payment Terms (RTL for Arabic) -->
            <t t-if="o.invoice_payment_term_id">
                <div style="margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 4px;">
                    <strong>Payment Terms | شروط الدفع:</strong>
                    <span t-field="o.invoice_payment_term_id.name"/>
                </div>
            </t>

        </div>
    </template>
</odoo>
```

---

## Report Validation Checklist

### Pre-Flight Checks (MANDATORY)

```
┌─────────────────────────────────────────────────────────────────┐
│              QWEB REPORT VALIDATION CHECKLIST                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. INFRASTRUCTURE                                               │
│     □ wkhtmltopdf installed and in PATH                         │
│     □ bin_path configured in odoo.conf                          │
│     □ Server restarted after config change                       │
│     □ Server log confirms wkhtmltopdf path                      │
│                                                                   │
│  2. TEMPLATE STRUCTURE (for non-Latin text)                     │
│     □ web.html_container as OUTERMOST wrapper                   │
│     □ t-foreach docs loop                                        │
│     □ web.external_layout for company header/fonts              │
│     □ Content inside div.page                                    │
│                                                                   │
│  3. ENCODING VERIFICATION                                        │
│     □ NOT using custom <html> tags                               │
│     □ NOT importing external fonts via CDN                      │
│     □ Arabic/Chinese text renders correctly                      │
│     □ Currency symbols display correctly (no $Â)                │
│                                                                   │
│  4. SCSS/CSS VALIDATION                                          │
│     □ Using web.report_assets_common bundle                      │
│     □ No semicolons in @import URLs                             │
│     □ No external CDN resources                                  │
│     □ System fonts only (DejaVu, Arial, etc.)                   │
│                                                                   │
│  5. REPORT ACTION FIELDS                                         │
│     □ report_name = 'module.template_id'                        │
│     □ report_file = 'module.template_id'                        │
│     □ binding_model_id = ref('module.model_xxx')                │
│     □ report_type = 'qweb-pdf'                                  │
│     □ paperformat_id linked (if custom)                         │
│                                                                   │
│  6. MANIFEST FILE                                                │
│     □ depends includes target module (account, sale, etc.)      │
│     □ data files in correct order (paperformat before action)   │
│     □ assets bundle = web.report_assets_common                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Post-Generation Testing

```bash
# 1. Update module
python -m odoo -c conf/project.conf -d database -u module --stop-after-init

# 2. Verify wkhtmltopdf in server log
# Look for: "Will use the Wkhtmltopdf binary at..."

# 3. Generate test PDF
# Navigate to record > Print menu > Select report

# 4. Verify PDF content
# - All text displays correctly (especially non-Latin)
# - Currency symbols correct
# - Layout matches design
# - Page breaks work correctly
```

---

## File Locations Reference

### Core Template Locations

```
odoo/addons/mail/
├── models/
│   ├── mail_template.py           # Main model
│   └── mail_render_mixin.py       # Rendering engine
├── data/
│   └── mail_template_data.xml     # Base templates
└── views/
    └── mail_template_views.xml    # UI views

odoo/addons/sale/
└── data/
    └── mail_template_data.xml     # Sales templates

odoo/addons/purchase/
└── data/
    └── mail_template_data.xml     # Purchase templates

odoo/addons/account/
└── data/
    └── mail_template_data.xml     # Accounting templates
```

---

## Related Documentation

| Document | Path | Purpose |
|----------|------|---------|
| Email Research | `C:\odoo\researches\ODOO_EMAIL_TEMPLATES_COMPLETE_RESEARCH.md` | Full research documentation |
| Odoo 17 CLAUDE.md | `odoo17\CLAUDE.md` | Development commands |
| Design System | `odoo17\DESIGN_SYSTEM_RULES.md` | Theme styling rules |

---

## Changelog

### v2.0.0 - Major Enhancement Release (January 2026)

Based on lessons learned from sadad_invoice_report development.

**NEW SECTIONS:**

- **wkhtmltopdf Setup & Configuration**
  - Installation commands (Windows, Linux, macOS)
  - Odoo `bin_path` configuration (MANDATORY)
  - Common errors and solutions
  - Offline mode limitations explained

- **Arabic/RTL & Multilingual Reports**
  - CRITICAL: UTF-8 encoding requirements
  - `web.html_container` + `web.external_layout` pattern
  - Wrong patterns that cause encoding corruption
  - Bilingual label patterns (side-by-side, stacked)
  - RTL text alignment

- **Paper Format Configuration**
  - Custom paper format template
  - Linking to report actions
  - Standard formats reference (A4, Letter, Legal)

- **Report SCSS Styling**
  - Correct asset bundle (`web.report_assets_common`)
  - Google Fonts pitfall (semicolons break SCSS)
  - Why external fonts fail in wkhtmltopdf
  - Recommended font stack
  - Color scheme patterns
  - Print-specific styles

- **Debug Report Workflow**
  - Systematic 5-step diagnosis
  - Issue-specific debugging guides
  - Asset cache clearing

- **Bilingual Invoice Template**
  - Complete working example based on sadad_invoice
  - Paper format, report action, templates included
  - Proven UTF-8/Arabic support

- **Report Validation Checklist**
  - 6-category pre-flight checks
  - Post-generation testing steps

**ISSUES PREVENTED:**

| Issue | Time Saved |
|-------|------------|
| Arabic text encoding corruption | 2+ hours |
| wkhtmltopdf configuration | 30 min |
| Google Fonts/external resources | 1 hour |
| SCSS semicolon parsing | 1 hour |

### v1.0.0 - Initial Release

- Email template patterns (50+)
- QWeb report patterns (30+)
- Version decision matrix (Odoo 14-19)
- Commands reference
- Validation rules
- Module-specific templates

---

---

## QR Code & Barcode in Reports

### ZATCA/Saudi e-Invoice QR Code (Legally Required)
Saudi Arabia's ZATCA requires a QR code on all B2C invoices. Use Odoo's built-in barcode API:

```xml
<!-- Built-in Odoo barcode route — no extra library needed -->
<img t-att-src="'/report/barcode/QR/%s' % (o.l10n_sa_qr_code_str or '')"
     style="max-width:100px; max-height:100px;"
     t-if="o.l10n_sa_qr_code_str"/>

<!-- Generic QR code from any string -->
<img t-att-src="'/report/barcode/?type=QR&amp;value=%s&amp;width=150&amp;height=150'
     % (o.name or '')"
     style="width:150px; height:150px;"/>

<!-- Product barcode (Code128) -->
<img t-att-src="'/report/barcode/Code128/%s' % (line.product_id.barcode or '')"
     style="height:40px;"
     t-if="line.product_id.barcode"/>
```

### Available Barcode Types
| Type | Use Case |
|------|---------|
| `QR` | QR codes for invoices, payments, URLs |
| `Code128` | Product barcodes (GS1-128) |
| `EAN13` | Retail product codes |
| `EAN8` | Short retail product codes |
| `Code39` | Alphanumeric codes |
| `ITF` | Shipping/logistics |

### Python: Custom QR Code with qrcode Library
```python
# In report model or controller
import qrcode
import base64
from io import BytesIO

def _get_qr_code_base64(self, data: str) -> str:
    """Generate QR code and return as base64 string for embedding in report."""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()
```

```xml
<!-- Use in report template (pass via report values) -->
<img t-att-src="'data:image/png;base64,%s' % o._get_qr_code_base64(o.name)"
     style="width:100px; height:100px;"/>
```

### wkhtmltopdf Barcode Note
> External image URLs (e.g., `https://...`) will NOT render in wkhtmltopdf when using `--disable-external-links`.
> Always use Odoo's internal `/report/barcode/` route which renders server-side.

---

## Report Wizard (User-Configurable Reports)

When a report needs user input (date range, grouping, language selection), use a `TransientModel` wizard:

### 1. Wizard Model
```python
# wizard/report_wizard.py
from odoo import api, fields, models

class MyReportWizard(models.TransientModel):
    _name = 'my.report.wizard'
    _description = 'My Report Wizard'

    date_from = fields.Date(
        string='From Date',
        required=True,
        default=fields.Date.context_today,
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.context_today,
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
        help='Leave empty to include all partners',
    )
    report_type = fields.Selection([
        ('summary', 'Summary'),
        ('detailed', 'Detailed'),
    ], string='Report Type', default='summary', required=True)

    def action_print_report(self):
        """Generate and return the report action."""
        self.ensure_one()
        data = {
            'form': {
                'date_from': str(self.date_from),
                'date_to': str(self.date_to),
                'partner_ids': self.partner_ids.ids,
                'report_type': self.report_type,
            }
        }
        return self.env.ref('my_module.action_my_report').report_action(
            self, data=data
        )
```

### 2. Wizard View
```xml
<!-- views/report_wizard_views.xml -->
<record id="view_my_report_wizard_form" model="ir.ui.view">
    <field name="name">my.report.wizard.form</field>
    <field name="model">my.report.wizard</field>
    <field name="arch" type="xml">
        <form string="Generate Report">
            <group>
                <group string="Date Range">
                    <field name="date_from"/>
                    <field name="date_to"/>
                </group>
                <group string="Filters">
                    <field name="partner_ids" widget="many2many_tags"/>
                    <field name="report_type"/>
                </group>
            </group>
            <footer>
                <button name="action_print_report" type="object"
                        string="Print Report" class="btn-primary"/>
                <button string="Cancel" class="btn-secondary"
                        special="cancel"/>
            </footer>
        </form>
    </field>
</record>

<!-- Menu action to open wizard -->
<record id="action_open_my_report_wizard" model="ir.actions.act_window">
    <field name="name">My Report</field>
    <field name="res_model">my.report.wizard</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>
</record>
```

### 3. Report Template Receiving Wizard Data
```xml
<!-- reports/my_report.xml -->
<template id="report_my_report">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <!-- Access wizard data via 'data' context variable -->
            <t t-set="date_from" t-value="data['form']['date_from']"/>
            <t t-set="date_to" t-value="data['form']['date_to']"/>
            <t t-set="report_type" t-value="data['form']['report_type']"/>

            <t t-call="web.external_layout">
                <div class="page">
                    <h2>
                        Report: <t t-esc="date_from"/> to <t t-esc="date_to"/>
                    </h2>
                    <!-- Conditional content based on wizard selection -->
                    <t t-if="report_type == 'detailed'">
                        <!-- Detailed view -->
                    </t>
                    <t t-else="">
                        <!-- Summary view -->
                    </t>
                </div>
            </t>
        </t>
    </t>
</template>
```

### 4. Report Action (for wizard)
```xml
<record id="action_my_report" model="ir.actions.report">
    <field name="name">My Report</field>
    <field name="model">my.report.wizard</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_my_report</field>
    <field name="report_file">my_module.report_my_report</field>
    <!-- Note: binding_model_id is NOT set for wizard-triggered reports -->
</record>
```

### Manifest Entry for Wizard
```python
'data': [
    'security/ir.model.access.csv',  # Add: access_my_report_wizard,...
    'wizard/report_wizard_views.xml',
    'reports/my_report.xml',
    'views/menus.xml',
],
```

---

*Odoo Report Plugin v2.0*
*TaqaTechno - Professional Email Templates & QWeb Reports*
*Supports Odoo 14-19 | Arabic/RTL Ready*

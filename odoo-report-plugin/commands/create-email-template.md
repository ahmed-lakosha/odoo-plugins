---
title: 'Create Email Template'
read_only: false
type: 'command'
description: 'Create a professional email template for any Odoo model with version-aware syntax'
---

# Create Email Template

Create a professional email template for any Odoo model with **automatic version detection** and **pattern-based generation**.

## Usage

```
/create-email-template [model] [purpose] [--version VERSION]
/create-email-template sale.order quotation
/create-email-template account.move invoice --version 17
/create-email-template hr.applicant welcome
```

### Natural Language

```
"Create an email template for sending quotations"
"Make a notification template for new applicants"
"Generate invoice email template for Odoo 19"
```

## Complete Workflow

### Step 1: Detect Odoo Version

```
┌─────────────────────────────────────────────────────────────────┐
│                  VERSION DETECTION (MANDATORY)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Check for version in these locations (in order):                │
│  1. User-specified --version flag                                │
│  2. Current working directory (odoo14, odoo15, etc.)             │
│  3. __manifest__.py version string                               │
│  4. Ask user if ambiguous                                        │
│                                                                   │
│  Version affects:                                                │
│  • t-out vs t-esc syntax                                         │
│  • report_template vs report_template_ids                        │
│  • template_category field                                       │
│  • Company branding colors                                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Step 2: Validate Model

```python
# Check model exists and has required fields
model_info = {
    "model": "sale.order",
    "has_partner": True,      # For email_to
    "has_user": True,         # For email_from
    "has_company": True,      # For branding
    "inherits_mail_thread": True,  # For notifications
    "common_fields": ["name", "state", "partner_id", "user_id", "company_id"]
}

# If model not found:
# "Model 'sale.orders' not found. Did you mean 'sale.order'?"
```

### Step 3: Select Template Pattern

Based on purpose, select appropriate pattern:

| Purpose | Pattern | Features |
|---------|---------|----------|
| `quotation` | Document Email | PDF attachment, portal link |
| `invoice` | Document Email | Payment info, bank details |
| `notification` | Basic Notification | Layout wrapper, CTA button |
| `confirmation` | Status Change | State-based content |
| `reminder` | Follow-up | Scheduled sending |
| `welcome` | Onboarding | Rich content, links |

### Step 4: Generate Template XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data noupdate="1">
        <record id="email_template_{model}_{purpose}" model="mail.template">
            <field name="name">{Model}: {Purpose}</field>
            <field name="model_id" ref="model_{model_underscore}"/>
            <field name="subject">{{ object.name }} - {Purpose Title}</field>
            <field name="email_from">{{ (object.user_id.email_formatted or user.email_formatted) }}</field>
            <field name="partner_to">{{ object.partner_id.id }}</field>
            <field name="email_layout_xmlid">mail.mail_notification_layout</field>
            <field name="body_html" type="html">
<!-- Generated body based on pattern -->
            </field>
            <field name="auto_delete" eval="True"/>
        </record>
    </data>
</odoo>
```

### Step 5: Create File

```
Output location: projects/{project}/data/mail_template_{purpose}.xml

Add to __manifest__.py:
'data': [
    ...
    'data/mail_template_{purpose}.xml',
],
```

## Example Flows

### Example 1: Sales Quotation Template

**User**: "Create email template for sending quotations in relief_center"

**Claude**:
```
Detected Odoo version: 17 (from odoo17/projects/relief_center)
Model: sale.order
Purpose: quotation
Pattern: Document Email with PDF

Generating template...
```

**Generated File**: `projects/relief_center/data/mail_template_quotation.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data noupdate="1">
        <record id="email_template_sale_quotation" model="mail.template">
            <field name="name">Sales: Send Quotation</field>
            <field name="model_id" ref="sale.model_sale_order"/>
            <field name="subject">
                {{ object.state in ('draft', 'sent') and 'Quotation' or 'Order' }} {{ object.name }}
            </field>
            <field name="email_from">{{ (object.user_id.email_formatted or user.email_formatted) }}</field>
            <field name="partner_to">{{ object.partner_id.id }}</field>
            <field name="report_template_ids" eval="[(4, ref('sale.action_report_saleorder'))]"/>
            <field name="report_name">{{ (object.name or 'Quotation').replace('/', '-') }}</field>
            <field name="email_layout_xmlid">mail.mail_notification_layout</field>
            <field name="body_html" type="html">
<div>
    <t t-set="doc_name" t-value="'quotation' if object.state in ('draft', 'sent') else 'order'"/>

    <p>Dear <t t-out="object.partner_id.name or 'Valued Customer'"/>,</p>

    <p>Please find attached your <t t-out="doc_name"/>
       <strong t-out="object.name"/> amounting to
       <strong t-out="format_amount(object.amount_total, object.currency_id)"/>.</p>

    <t t-if="object.validity_date">
        <p>This offer is valid until <t t-out="format_date(object.validity_date)"/>.</p>
    </t>

    <p>Do not hesitate to contact us if you have any questions.</p>

    <p>Best regards,</p>
</div>
            </field>
            <field name="auto_delete" eval="True"/>
        </record>
    </data>
</odoo>
```

### Example 2: Invoice Template for Odoo 19

**User**: "Create invoice email template for Odoo 19 with company branding"

**Claude**:
```
Detected Odoo version: 19
Model: account.move
Purpose: invoice
Pattern: Document Email with Payment Info
Special: Using Odoo 19 company branding colors
```

**Generated** (with Odoo 19 specific features):

```xml
<field name="body_html" type="html">
<div>
    <p>Dear <t t-out="object.partner_id.name or 'Valued Customer'"/>,</p>

    <p>Please find attached invoice <strong t-out="object.name"/>
       for <strong t-out="format_amount(object.amount_total, object.currency_id)"/>.</p>

    <t t-if="object.payment_state not in ('paid', 'in_payment')">
        <div style="background-color: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 4px;">
            <h4 style="margin: 0 0 10px 0;">Payment Information</h4>
            <t t-if="object.payment_reference">
                <p><strong>Reference:</strong> <t t-out="object.payment_reference"/></p>
            </t>
            <t t-if="object.partner_bank_id">
                <p><strong>Bank Account:</strong> <t t-out="object.partner_bank_id.acc_number"/></p>
            </t>
        </div>

        <!-- Odoo 19: Company branding colors -->
        <t t-set="btn_color" t-value="object.company_id.email_secondary_color or '#875A7B'"/>
        <table border="0" cellpadding="0" cellspacing="0" width="100%">
            <tr>
                <td align="center" style="padding: 16px;">
                    <a t-att-href="object.get_portal_url()"
                       t-att-style="'display: inline-block; padding: 10px 20px; color: #ffffff; text-decoration: none; border-radius: 3px; background-color: %s' % btn_color">
                        View Invoice Online
                    </a>
                </td>
            </tr>
        </table>
    </t>
    <t t-else="">
        <p style="color: #155724; background-color: #d4edda; padding: 10px; border-radius: 4px;">
            This invoice has been paid. Thank you!
        </p>
    </t>
</div>
</field>
```

### Example 3: HR Welcome Template

**User**: "Create welcome email for new employees"

**Claude**:
```
Model: hr.employee
Purpose: welcome
Pattern: Onboarding Email
```

```xml
<record id="email_template_employee_welcome" model="mail.template">
    <field name="name">HR: Welcome New Employee</field>
    <field name="model_id" ref="hr.model_hr_employee"/>
    <field name="subject">Welcome to {{ object.company_id.name }}, {{ object.name }}!</field>
    <field name="email_from">{{ (object.company_id.email or user.email_formatted) }}</field>
    <field name="email_to">{{ object.work_email }}</field>
    <field name="email_layout_xmlid">mail.mail_notification_layout</field>
    <field name="body_html" type="html">
<div>
    <p>Dear <t t-out="object.name"/>,</p>

    <p>Welcome to <strong t-out="object.company_id.name"/>!</p>

    <p>We are excited to have you join our team
       <t t-if="object.department_id">
           in the <t t-out="object.department_id.name"/> department
       </t>.
    </p>

    <t t-if="object.parent_id">
        <p>Your manager is <t t-out="object.parent_id.name"/>
           (<a t-att-href="'mailto:%s' % object.parent_id.work_email"
               t-out="object.parent_id.work_email"/>).</p>
    </t>

    <t t-if="object.job_id">
        <p>Your position: <strong t-out="object.job_id.name"/></p>
    </t>

    <p>If you have any questions, please don't hesitate to reach out.</p>

    <p>Best regards,<br/>
    <t t-out="object.company_id.name"/> HR Team</p>
</div>
    </field>
</record>
```

## Version-Specific Syntax

### Odoo 14

```xml
<!-- Use t-esc instead of t-out -->
<t t-esc="object.name"/>

<!-- Single report attachment -->
<field name="report_template" ref="module.report_action"/>
```

### Odoo 15-16

```xml
<!-- Use t-out (preferred) -->
<t t-out="object.name"/>

<!-- Single report attachment -->
<field name="report_template" ref="module.report_action"/>

<!-- Odoo 16+: template_category -->
<!-- base_template, hidden_template, custom_template -->
```

### Odoo 17-18

```xml
<!-- Use t-out -->
<t t-out="object.name"/>

<!-- Multiple report attachments -->
<field name="report_template_ids" eval="[(4, ref('module.report_action'))]"/>
```

### Odoo 19

```xml
<!-- Use t-out -->
<t t-out="object.name"/>

<!-- Multiple report attachments -->
<field name="report_template_ids" eval="[(4, ref('module.report_action'))]"/>

<!-- Company branding colors -->
<t t-set="btn_bg" t-value="company.email_secondary_color or '#875A7B'"/>
<t t-set="btn_text" t-value="company.email_primary_color or '#FFFFFF'"/>
```

## Validation Checklist

Before generating, Claude validates:

```
MANDATORY CHECKS:
[ ] Model exists in target version
[ ] Required fields available (partner_id, etc.)
[ ] Version-appropriate syntax selected
[ ] XML is well-formed
[ ] No security issues in expressions
[ ] File path is in projects/ not odoo/
```

## Output Structure

```
projects/{project}/
├── __manifest__.py       # Updated with new data file
└── data/
    └── mail_template_{purpose}.xml   # New template
```

## Error Handling

### Model Not Found

```
Model "sale.orders" not found.

Did you mean:
• sale.order
• sale.order.line
• sale.order.template

Use: /create-email-template sale.order quotation
```

### Missing Required Field

```
Model "custom.model" does not have a partner_id field.

Email templates require:
• partner_id (or partner_to expression)
• Some way to get recipient email

Options:
1. Add partner_id to your model
2. Specify custom email_to expression
3. Use partner_to with explicit IDs
```

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│              CREATE EMAIL TEMPLATE QUICK REFERENCE                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  REQUIRED:                                                       │
│  • Model name (sale.order, account.move, etc.)                   │
│  • Purpose (quotation, invoice, notification, etc.)              │
│                                                                   │
│  OPTIONAL:                                                       │
│  • --version (14, 15, 16, 17, 18, 19)                           │
│  • --with-report (attach PDF report)                             │
│  • --layout (mail_notification_layout, etc.)                     │
│                                                                   │
│  OUTPUT:                                                         │
│  • data/mail_template_{purpose}.xml                              │
│  • Updates to __manifest__.py                                    │
│                                                                   │
│  VERSION SYNTAX:                                                 │
│  • Odoo 14: t-esc                                                │
│  • Odoo 15+: t-out                                               │
│  • Odoo 17+: report_template_ids                                 │
│  • Odoo 19: email_primary/secondary_color                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Related Commands

| Command | Description |
|---------|-------------|
| `/create-qweb-report` | Create QWeb PDF report |
| `/analyze-template` | Analyze existing template |
| `/migrate-template` | Migrate template between versions |
| `/debug-template` | Debug template rendering |

---

*Part of Odoo Report Plugin v1.0*
*Version-aware template generation*

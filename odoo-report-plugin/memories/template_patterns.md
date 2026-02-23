# Template Patterns - Common Email & Report Patterns

> **Purpose**: This memory helps Claude select appropriate template patterns based on use case.

## Pattern Selection Guide

### By Purpose

| Purpose | Pattern | Key Features |
|---------|---------|--------------|
| Send document | Document Email | PDF attachment, portal link |
| Notify user | Basic Notification | Layout wrapper, simple message |
| Confirm action | Status Change | State-based content |
| Request info | Request Email | Reply guidance, deadline |
| Welcome user | Onboarding | Rich content, helpful links |
| Remind user | Follow-up | Urgency indicator, action button |
| Summary report | Digest Email | Multiple items, totals |

### By Model

| Model | Recommended Pattern |
|-------|---------------------|
| `sale.order` | Document Email (quotation/order) |
| `purchase.order` | Document Email (RFQ/PO) |
| `account.move` | Document Email (invoice) with payment info |
| `hr.applicant` | Status Change (application stages) |
| `hr.employee` | Onboarding (welcome) |
| `project.task` | Basic Notification |
| `helpdesk.ticket` | Basic Notification with tracking |
| `event.registration` | Confirmation with calendar info |

## Pattern Templates

### Pattern 1: Basic Notification

```xml
<div>
    <p>Dear <t t-out="object.partner_id.name or 'Valued Customer'"/>,</p>
    <p>[Main message content]</p>
    <p>Best regards,<br/><t t-out="object.company_id.name"/></p>
</div>
```

**Use when**: Simple notifications, status updates

### Pattern 2: Document Email

```xml
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
</div>
```

**Use when**: Sending quotations, invoices, orders

### Pattern 3: Status Change

```xml
<div>
    <p>Dear <t t-out="object.partner_id.name or 'User'"/>,</p>

    <t t-if="object.state == 'approved'">
        <p style="color: #155724; background: #d4edda; padding: 10px; border-radius: 4px;">
            Your request has been <strong>approved</strong>!
        </p>
    </t>
    <t t-elif="object.state == 'rejected'">
        <p style="color: #721c24; background: #f8d7da; padding: 10px; border-radius: 4px;">
            Unfortunately, your request has been <strong>declined</strong>.
        </p>
    </t>
    <t t-else="">
        <p>Your request is currently <strong t-out="object.state"/>.</p>
    </t>
</div>
```

**Use when**: Application status, approval workflows

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

**Use when**: Need prominent call-to-action

### Pattern 5: Line Items Table

```xml
<table border="0" cellpadding="0" cellspacing="0" width="100%"
       style="border-collapse: collapse;">
    <thead>
        <tr style="background-color: #875A7B; color: white;">
            <th style="padding: 8px;">Item</th>
            <th style="padding: 8px;">Qty</th>
            <th style="padding: 8px; text-align: right;">Price</th>
        </tr>
    </thead>
    <tbody>
        <t t-foreach="object.order_line" t-as="line">
            <t t-if="not line.display_type">
                <tr t-att-style="'background-color: #f9f9f9' if line_index % 2 == 0 else ''">
                    <td style="padding: 8px;" t-out="line.name"/>
                    <td style="padding: 8px; text-align: center;" t-out="line.product_uom_qty"/>
                    <td style="padding: 8px; text-align: right;"
                        t-out="format_amount(line.price_subtotal, object.currency_id)"/>
                </tr>
            </t>
        </t>
    </tbody>
    <tfoot>
        <tr style="font-weight: bold; background-color: #f5f5f5;">
            <td colspan="2" style="padding: 8px; text-align: right;">Total:</td>
            <td style="padding: 8px; text-align: right;"
                t-out="format_amount(object.amount_total, object.currency_id)"/>
        </tr>
    </tfoot>
</table>
```

**Use when**: Orders, invoices, reports with line items

### Pattern 6: Payment Information

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
        <p><strong>Amount Due:</strong>
           <t t-out="format_amount(object.amount_residual, object.currency_id)"/>
        </p>
    </div>
</t>
```

**Use when**: Invoices requiring payment

## Layout Selection

| Layout | Width | Use Case |
|--------|-------|----------|
| `mail.mail_notification_layout` | 900px | Full emails with header/footer |
| `mail.mail_notification_light` | 590px | Simple notifications |
| `mail.mail_notification_layout_with_responsible_signature` | 900px | Use record's user_id signature |
| None (no layout) | Full | Minimal emails, automated notifications |

## Best Practices Memory

1. **Always use fallbacks**: `object.field or 'Default'`
2. **Use format helpers**: `format_amount()`, `format_date()`
3. **Check null before traverse**: `object.partner_id and object.partner_id.name`
4. **Use layouts for consistency**
5. **Handle empty HTML**: `not is_html_empty(object.field)`

# QWeb Best Practices - Template Rendering Guidelines

> **Purpose**: This memory helps Claude write high-quality, safe, and performant QWeb templates.

## Safety Rules

### Always Use Null Checks

```xml
<!-- BAD - Will fail if partner_id is None -->
<t t-out="object.partner_id.name"/>

<!-- GOOD - Safe with fallback -->
<t t-out="object.partner_id.name or 'Customer'"/>

<!-- GOOD - Conditional rendering -->
<t t-if="object.partner_id">
    <t t-out="object.partner_id.name"/>
</t>
```

### Never Trust User Input

```xml
<!-- BAD - Potential XSS if raw HTML -->
<t t-raw="object.user_comment"/>

<!-- GOOD - Escaped output (t-out sanitizes) -->
<t t-out="object.user_comment"/>
```

### Use Format Helpers

```xml
<!-- BAD - Manual formatting -->
<t t-out="'$%.2f' % object.amount"/>

<!-- GOOD - Localized, currency-aware -->
<t t-out="format_amount(object.amount, object.currency_id)"/>

<!-- BAD - Manual date formatting -->
<t t-out="str(object.date)"/>

<!-- GOOD - Localized date -->
<t t-out="format_date(object.date)"/>
```

## Performance Guidelines

### Avoid N+1 Queries

```xml
<!-- BAD - N+1 query in loop -->
<t t-foreach="object.order_line" t-as="line">
    <t t-foreach="line.product_id.seller_ids" t-as="seller">
        <t t-out="seller.name"/>
    </t>
</t>

<!-- GOOD - Prefetch or restructure -->
<t t-set="all_sellers" t-value="object.order_line.mapped('product_id.seller_ids')"/>
<!-- Use all_sellers -->
```

### Limit Recordset Size

```xml
<!-- BAD - Could be thousands of records -->
<t t-foreach="env['sale.order'].search([])" t-as="order">

<!-- GOOD - Limit and paginate -->
<t t-foreach="object.order_ids[:100]" t-as="order">
```

### Cache Expensive Computations

```xml
<!-- Set computed value once -->
<t t-set="total_qty" t-value="sum(line.qty for line in object.order_line)"/>

<!-- Reuse throughout template -->
<p>Total items: <t t-out="total_qty"/></p>
```

## Common Patterns

### Conditional Styling

```xml
<div t-att-class="'alert alert-success' if object.state == 'done' else 'alert alert-warning'">
    <t t-out="object.message"/>
</div>
```

### Alternating Rows

```xml
<t t-foreach="items" t-as="item">
    <tr t-att-style="'background-color: #f5f5f5' if item_index % 2 == 0 else ''">
        <td t-out="item.name"/>
    </tr>
</t>
```

### Loop with Section Headers

```xml
<t t-foreach="object.line_ids" t-as="line">
    <t t-if="line.display_type == 'line_section'">
        <tr class="section-header">
            <td colspan="4"><strong t-out="line.name"/></td>
        </tr>
    </t>
    <t t-elif="line.display_type == 'line_note'">
        <tr class="note-row">
            <td colspan="4"><em t-out="line.name"/></td>
        </tr>
    </t>
    <t t-else="">
        <tr><!-- Regular line content --></tr>
    </t>
</t>
```

### Dynamic Attributes

```xml
<!-- Single attribute -->
<a t-att-href="object.website_url">Link</a>

<!-- Formatted attribute with interpolation -->
<img t-attf-src="/web/image/product.product/{{ product.id }}/image_128"/>

<!-- Conditional attribute -->
<button t-att-disabled="True if object.state == 'done' else None">
    Submit
</button>
```

## Email-Specific Guidelines

### Use Tables for Layout (Email Compatibility)

```xml
<!-- Email clients prefer tables -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
    <tr>
        <td style="padding: 20px;">
            Content
        </td>
    </tr>
</table>
```

### Inline Styles Required

```xml
<!-- External CSS won't work in most email clients -->
<p style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
    Text content
</p>
```

### Bulletproof Buttons

```xml
<!-- Works in Outlook and web clients -->
<table border="0" cellpadding="0" cellspacing="0">
    <tr>
        <td align="center" bgcolor="#875A7B" style="border-radius: 3px;">
            <a href="#" target="_blank"
               style="display: inline-block; padding: 10px 20px;
                      font-size: 14px; color: #ffffff;
                      text-decoration: none;">
                Click Here
            </a>
        </td>
    </tr>
</table>
```

## Report-Specific Guidelines

### Page Break Control

```xml
<!-- Force page break -->
<div style="page-break-before: always;"/>

<!-- Keep together -->
<div style="page-break-inside: avoid;">
    <table><!-- Important table --></table>
</div>
```

### Use Bootstrap Classes

```xml
<!-- Reports support Bootstrap -->
<div class="row">
    <div class="col-6">Left</div>
    <div class="col-6">Right</div>
</div>
```

### Use t-field for Better Formatting

```xml
<!-- t-field provides widgets and formatting -->
<span t-field="doc.date" t-options='{"widget": "date"}'/>
<span t-field="doc.amount" t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>
```

## Error Prevention Checklist

```
[ ] All t-out values have null fallbacks
[ ] No direct string concatenation in t-out
[ ] Format helpers used for numbers/dates
[ ] No N+1 queries in loops
[ ] No unsafe t-raw usage
[ ] Email uses inline styles
[ ] Tables used for email layout
[ ] Page breaks handled in reports
```

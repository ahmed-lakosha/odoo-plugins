---
title: 'Create QWeb Report'
read_only: false
type: 'command'
description: 'Create a professional QWeb PDF report with action binding and print menu'
---

# Create QWeb Report

Create a professional QWeb PDF report with **report action**, **print menu binding**, and **proper layout**.

## Usage

```
/create-qweb-report [model] [report-name] [--version VERSION]
/create-qweb-report sale.order quotation_custom
/create-qweb-report account.move invoice_detailed --version 17
/create-qweb-report custom.model document_report
```

### Natural Language

```
"Create a PDF report for sale orders"
"Make a printable invoice report"
"Generate custom report for my model"
```

## Complete Workflow

### Step 1: Gather Information

```
┌─────────────────────────────────────────────────────────────────┐
│                  REPORT REQUIREMENTS GATHERING                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  REQUIRED:                                                       │
│  • Model name (e.g., sale.order)                                 │
│  • Report name (e.g., quotation_custom)                          │
│                                                                   │
│  DETECTED:                                                       │
│  • Odoo version (from path or manifest)                          │
│  • Module name (from current directory)                          │
│  • Model fields (for template suggestions)                       │
│                                                                   │
│  OPTIONS:                                                        │
│  • Paper format (A4, Letter, custom)                             │
│  • Orientation (portrait, landscape)                             │
│  • Header/footer (company layout or custom)                      │
│  • Binding type (report menu, action button, both)               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Step 2: Generate Report Action

```xml
<!-- reports/report_actions.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="action_report_{model}_{name}" model="ir.actions.report">
        <field name="name">{Report Display Name}</field>
        <field name="model">{model}</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">{module}.report_{name}_template</field>
        <field name="report_file">{module}.report_{name}_template</field>
        <field name="print_report_name">'{Name} - %s' % object.name</field>
        <field name="binding_model_id" ref="model_{model_underscore}"/>
        <field name="binding_type">report</field>
    </record>
</odoo>
```

### Step 3: Generate Report Template

```xml
<!-- reports/report_{name}_template.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="report_{name}_template">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="web.external_layout">
                    <div class="page">
                        <!-- Report content -->
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

### Step 4: Update Manifest

```python
'data': [
    ...
    'reports/report_actions.xml',
    'reports/report_{name}_template.xml',
],
```

## Example Flows

### Example 1: Sales Order Report

**User**: "Create a detailed quotation report for sale.order"

**Claude**:
```
Model: sale.order
Report name: quotation_detailed
Module: relief_center
Odoo version: 17

Generating files...
```

**Generated**: `reports/report_actions.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="action_report_sale_quotation_detailed" model="ir.actions.report">
        <field name="name">Quotation (Detailed)</field>
        <field name="model">sale.order</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">relief_center.report_quotation_detailed_template</field>
        <field name="report_file">relief_center.report_quotation_detailed_template</field>
        <field name="print_report_name">
            (object.state in ('draft', 'sent') and 'Quotation - %s' or 'Order - %s') % object.name
        </field>
        <field name="binding_model_id" ref="sale.model_sale_order"/>
        <field name="binding_type">report</field>
    </record>
</odoo>
```

**Generated**: `reports/report_quotation_detailed_template.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="report_quotation_detailed_template">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="web.external_layout">
                    <div class="page">
                        <!-- Header -->
                        <div class="row mb-4">
                            <div class="col-6">
                                <h2>
                                    <t t-if="doc.state in ('draft', 'sent')">Quotation</t>
                                    <t t-else="">Sales Order</t>
                                </h2>
                                <h3 class="text-muted" t-field="doc.name"/>
                            </div>
                            <div class="col-6 text-end">
                                <div><strong>Date:</strong> <span t-field="doc.date_order" t-options='{"widget": "date"}'/></div>
                                <t t-if="doc.validity_date">
                                    <div><strong>Valid Until:</strong> <span t-field="doc.validity_date"/></div>
                                </t>
                                <t t-if="doc.client_order_ref">
                                    <div><strong>Your Reference:</strong> <span t-field="doc.client_order_ref"/></div>
                                </t>
                            </div>
                        </div>

                        <!-- Customer Info -->
                        <div class="row mb-4">
                            <div class="col-6">
                                <strong>Customer:</strong>
                                <div t-field="doc.partner_id"
                                     t-options='{"widget": "contact", "fields": ["address", "name", "phone", "email"], "no_marker": True}'/>
                            </div>
                            <t t-if="doc.partner_shipping_id and doc.partner_shipping_id != doc.partner_id">
                                <div class="col-6">
                                    <strong>Shipping Address:</strong>
                                    <div t-field="doc.partner_shipping_id"
                                         t-options='{"widget": "contact", "fields": ["address", "name"], "no_marker": True}'/>
                                </div>
                            </t>
                        </div>

                        <!-- Order Lines Table -->
                        <table class="table table-sm o_main_table">
                            <thead>
                                <tr>
                                    <th class="text-start">Description</th>
                                    <th class="text-center">Quantity</th>
                                    <th class="text-end">Unit Price</th>
                                    <t t-if="doc.order_line.filtered(lambda l: l.discount)">
                                        <th class="text-end">Disc.%</th>
                                    </t>
                                    <th class="text-end">Amount</th>
                                </tr>
                            </thead>
                            <tbody>
                                <t t-foreach="doc.order_line" t-as="line">
                                    <t t-if="line.display_type == 'line_section'">
                                        <tr>
                                            <td colspan="99" class="fw-bold bg-light">
                                                <span t-field="line.name"/>
                                            </td>
                                        </tr>
                                    </t>
                                    <t t-elif="line.display_type == 'line_note'">
                                        <tr>
                                            <td colspan="99" class="fst-italic">
                                                <span t-field="line.name"/>
                                            </td>
                                        </tr>
                                    </t>
                                    <t t-else="">
                                        <tr>
                                            <td>
                                                <span t-field="line.name"/>
                                            </td>
                                            <td class="text-center">
                                                <span t-field="line.product_uom_qty"/>
                                                <span t-field="line.product_uom"/>
                                            </td>
                                            <td class="text-end">
                                                <span t-field="line.price_unit"/>
                                            </td>
                                            <t t-if="doc.order_line.filtered(lambda l: l.discount)">
                                                <td class="text-end">
                                                    <span t-field="line.discount"/>%
                                                </td>
                                            </t>
                                            <td class="text-end">
                                                <span t-field="line.price_subtotal"/>
                                            </td>
                                        </tr>
                                    </t>
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
                                    <t t-foreach="doc.amount_by_group" t-as="amount_by_group">
                                        <tr>
                                            <td><span t-out="amount_by_group[0]"/></td>
                                            <td class="text-end">
                                                <span t-out="amount_by_group[1]"/>
                                            </td>
                                        </tr>
                                    </t>
                                    <tr class="border-top">
                                        <td><strong>Total</strong></td>
                                        <td class="text-end"><span t-field="doc.amount_total"/></td>
                                    </tr>
                                </table>
                            </div>
                        </div>

                        <!-- Terms and Conditions -->
                        <t t-if="doc.note">
                            <div class="mt-4">
                                <strong>Terms &amp; Conditions:</strong>
                                <p t-field="doc.note"/>
                            </div>
                        </t>

                        <!-- Signature -->
                        <div class="row mt-5">
                            <div class="col-6">
                                <div class="border-top pt-2">
                                    <strong>Seller Signature</strong>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="border-top pt-2">
                                    <strong>Customer Signature</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

### Example 2: Custom Model Report

**User**: "Create a report for custom.document model"

**Claude**:
```
Model: custom.document
Report name: document_report
Module: my_module

Analyzing model fields...
Found: name, date, partner_id, line_ids, state, total

Generating report structure...
```

### Example 3: Landscape Report

**User**: "Create a landscape report for inventory with wide table"

**Claude** adds paper format:

```xml
<!-- Paper Format -->
<record id="paperformat_landscape" model="report.paperformat">
    <field name="name">Landscape A4</field>
    <field name="format">A4</field>
    <field name="orientation">Landscape</field>
    <field name="margin_top">25</field>
    <field name="margin_bottom">25</field>
    <field name="margin_left">10</field>
    <field name="margin_right">10</field>
</record>

<!-- Report Action with Paper Format -->
<record id="action_report_inventory" model="ir.actions.report">
    <field name="name">Inventory Report</field>
    <field name="model">stock.inventory</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_inventory_template</field>
    <field name="paperformat_id" ref="paperformat_landscape"/>
    <field name="binding_model_id" ref="stock.model_stock_inventory"/>
    <field name="binding_type">report</field>
</record>
```

## Report Components

### Layout Wrappers

```xml
<!-- Full company header/footer -->
<t t-call="web.external_layout">
    <div class="page">...</div>
</t>

<!-- Minimal container -->
<t t-call="web.html_container">
    <div class="page">...</div>
</t>

<!-- Internal layout (no header/footer) -->
<t t-call="web.internal_layout">
    <div class="page">...</div>
</t>
```

### Field Widgets

```xml
<!-- Date formatting -->
<span t-field="doc.date" t-options='{"widget": "date"}'/>

<!-- DateTime formatting -->
<span t-field="doc.create_date" t-options='{"widget": "datetime", "format": "dd/MM/yyyy HH:mm"}'/>

<!-- Monetary formatting -->
<span t-field="doc.amount_total" t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>

<!-- Contact widget -->
<div t-field="doc.partner_id" t-options='{"widget": "contact", "fields": ["address", "name", "phone"]}'/>

<!-- Image -->
<img t-if="doc.image_128" t-att-src="image_data_uri(doc.image_128)" style="max-height: 50px;"/>
```

### Page Breaks

```xml
<!-- Force page break -->
<div style="page-break-before: always;"/>
<div style="page-break-after: always;"/>

<!-- Prevent break inside -->
<div style="page-break-inside: avoid;">
    <table>...</table>
</div>
```

### CSS Styling

```xml
<!-- Inline styles (recommended for reports) -->
<style type="text/css">
    .o_report_custom {
        font-family: Arial, sans-serif;
    }
    .o_report_custom table {
        border-collapse: collapse;
        width: 100%;
    }
    .o_report_custom th {
        background-color: #875A7B;
        color: white;
        padding: 8px;
    }
    .o_report_custom td {
        padding: 8px;
        border-bottom: 1px solid #ddd;
    }
</style>
```

## Output Structure

```
projects/{module}/
├── __manifest__.py           # Updated
├── reports/
│   ├── __init__.py          # (if needed for Python reports)
│   ├── report_actions.xml    # Report action definitions
│   └── report_{name}_template.xml  # QWeb templates
└── static/src/css/
    └── report_{name}.css     # Optional custom styles
```

## Validation Checklist

```
MANDATORY CHECKS:
[ ] Model exists and has name field
[ ] Report name is unique
[ ] Template ID matches report_name
[ ] binding_model_id reference is correct
[ ] External layout called properly
[ ] Bootstrap classes used for responsive design
[ ] Page breaks handled for multi-page
```

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│               CREATE QWEB REPORT QUICK REFERENCE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  REPORT ACTION FIELDS:                                           │
│  • name: Display name in print menu                              │
│  • model: Target model                                           │
│  • report_type: qweb-pdf (or qweb-html)                         │
│  • report_name: {module}.template_id                             │
│  • report_file: Same as report_name                              │
│  • print_report_name: Dynamic filename expression                │
│  • binding_model_id: ref to model_* for menu binding            │
│  • binding_type: report (shows in Print menu)                    │
│  • paperformat_id: Optional custom paper format                  │
│                                                                   │
│  TEMPLATE STRUCTURE:                                             │
│  1. html_container (outermost)                                   │
│  2. foreach docs as doc (loop through records)                   │
│  3. external_layout (company header/footer)                      │
│  4. div.page (actual content)                                    │
│                                                                   │
│  COMMON WIDGETS:                                                 │
│  • date, datetime                                                │
│  • monetary                                                      │
│  • contact                                                       │
│  • image_data_uri()                                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Related Commands

| Command | Description |
|---------|-------------|
| `/create-email-template` | Create email template |
| `/style-report` | Add CSS to report |
| `/add-header-footer` | Custom header/footer |
| `/debug-report` | Debug report rendering |

---

*Part of Odoo Report Plugin v1.0*
*Professional QWeb PDF Reports*

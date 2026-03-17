---
title: 'Odoo Report'
read_only: false
type: 'command'
description: 'Odoo email templates & QWeb reports — create, migrate, and manage'
argument-hint: '[create-email|create-report|migrate] <model|file> [args...]'
---

# Odoo Report Plugin

Parse `$ARGUMENTS` and route to the appropriate section:

- `create-email` → Jump to **Section A: Create Email Template**
- `create-report` → Jump to **Section B: Create QWeb Report**
- `migrate` → Jump to **Section C: Migrate Template**
- No arguments or `help` → Show **Section 0: Help + Status** below, then STOP

---

## Section 0: Help + Status

### Sub-Commands

| Sub-command | Usage | What it does |
|-------------|-------|--------------|
| `create-email` | `/odoo-report create-email <model> [purpose]` | Generate a version-aware `mail.template` XML |
| `create-report` | `/odoo-report create-report <model> [name]` | Generate QWeb PDF report action + template |
| `migrate` | `/odoo-report migrate <file> <target-version>` | Migrate template/report XML between Odoo versions |

### Natural Language Examples

The skill also handles these requests without explicit sub-commands:

```
"Create an email template for sending quotations"          → create-email
"Make a printable invoice report"                           → create-report
"Migrate my templates from Odoo 14 to 17"                  → migrate
"Analyze this template for issues"                          → skill-driven (analyze)
"Debug why the invoice email is blank"                      → skill-driven (debug)
"Fix the broken QWeb report"                                → skill-driven (fix)
"Validate templates before deployment"                      → skill-driven (validate)
"List all templates for sale.order"                         → skill-driven (list)
"Preview the email template output"                         → skill-driven (preview)
```

### Version Detection

Detect Odoo version automatically (used by all sub-commands):

1. User-specified `--version` flag (highest priority)
2. Current working directory name (`odoo14`, `odoo15`, ..., `odoo19`)
3. `__manifest__.py` version string (e.g. `'version': '17.0.1.0.0'`)
4. Ask user if ambiguous

| Version | Key Differences |
|---------|----------------|
| Odoo 14 | `t-esc` syntax, `report_template` (singular) |
| Odoo 15 | `t-out` replaces `t-esc`/`t-raw`, `render_engine` |
| Odoo 16 | `template_category` field added |
| Odoo 17 | `report_template_ids` M2M replaces singular field |
| Odoo 18 | Layout variants |
| Odoo 19 | Company branding colors (`email_primary_color`, `email_secondary_color`) |

**After displaying help, STOP. Do not proceed to other sections.**

---

## Section A: Create Email Template

Triggered by: `/odoo-report create-email <model> [purpose] [--version VERSION]`

### A1. Detect Version

Run version detection (see Section 0). Version determines syntax choices throughout.

### A2. Validate Model

```python
model_info = {
    "model": "<model>",
    "has_partner": True/False,      # For email_to / partner_to
    "has_user": True/False,         # For email_from
    "has_company": True/False,      # For branding
    "inherits_mail_thread": True/False,
    "common_fields": [...]
}
# If model not found, suggest similar: "Did you mean 'sale.order'?"
```

### A3. Select Pattern

| Purpose | Pattern | Features |
|---------|---------|----------|
| `quotation` | Document Email | PDF attachment, portal link |
| `invoice` | Document Email | Payment info, bank details |
| `notification` | Basic Notification | Layout wrapper, CTA button |
| `confirmation` | Status Change | State-based content |
| `reminder` | Follow-up | Scheduled sending |
| `welcome` | Onboarding | Rich content, links |

### A4. Generate Template XML

Produce a complete `mail.template` record. Skeleton:

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
<!-- Version-aware body content here -->
            </field>
            <field name="auto_delete" eval="True"/>
        </record>
    </data>
</odoo>
```

### A5. Version-Specific Syntax Rules

**Odoo 14** — use `t-esc`:
```xml
<t t-esc="object.name"/>
<field name="report_template" ref="module.report_action"/>
```

**Odoo 15-16** — use `t-out`:
```xml
<t t-out="object.name"/>
<field name="report_template" ref="module.report_action"/>
<!-- Odoo 16+: optionally add template_category -->
```

**Odoo 17-18** — use `t-out`, M2M reports:
```xml
<t t-out="object.name"/>
<field name="report_template_ids" eval="[(4, ref('module.report_action'))]"/>
```

**Odoo 19** — add company branding colors:
```xml
<t t-out="object.name"/>
<field name="report_template_ids" eval="[(4, ref('module.report_action'))]"/>
<!-- CTA buttons use dynamic colors -->
<t t-set="btn_bg" t-value="company.email_secondary_color or '#875A7B'"/>
<t t-set="btn_text" t-value="company.email_primary_color or '#FFFFFF'"/>
```

### A6. Body Content by Pattern

**Document Email (quotation/invoice)** — include:
- Greeting with `object.partner_id.name`
- Document reference (`object.name`) and amount (`format_amount`)
- Validity date (if quotation) or payment info block (if invoice)
- Portal link CTA button (use branding colors on Odoo 19)
- Closing with salesperson name

**Notification / Confirmation** — include:
- Layout wrapper via `email_layout_xmlid`
- State-dependent content using `t-if`
- Single CTA button

**Welcome / Onboarding** — include:
- Company name, department, manager info
- Job position if available
- Multiple informational sections

### A7. Attachment Handling

If purpose implies a PDF attachment (quotation, invoice):
- **Odoo 14-16**: `<field name="report_template" ref="module.report_action"/>`
- **Odoo 17+**: `<field name="report_template_ids" eval="[(4, ref('module.report_action'))]"/>`
- Always add `report_name` with sanitized filename expression.

### A8. Output and Manifest

```
projects/{project}/data/mail_template_{purpose}.xml

Update __manifest__.py 'data' list:
    'data/mail_template_{purpose}.xml',
```

### A9. Validation Checklist

Before writing the file, confirm:
- [ ] Model exists in target version
- [ ] Required fields available (partner_id or custom email_to)
- [ ] Version-appropriate syntax selected
- [ ] XML is well-formed
- [ ] No security issues in expressions
- [ ] File path is in `projects/`, not `odoo/`

### A10. Error Handling

**Model not found**: Suggest similar models (`sale.orders` → `sale.order`, `sale.order.line`).

**No partner_id**: Offer options — add `partner_id` to model, specify custom `email_to`, or use `partner_to` with explicit IDs.

---

## Section B: Create QWeb Report

Triggered by: `/odoo-report create-report <model> [name] [--version VERSION]`

### B1. Gather Information

Detect version, module name, and model fields. Options:
- Paper format: A4 (default), Letter, custom
- Orientation: portrait (default), landscape
- Header/footer: company layout (`web.external_layout`) or custom
- Binding: Print menu (default), action button, or both

### B2. Generate Report Action

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

For landscape reports, add a `report.paperformat` record:
```xml
<record id="paperformat_{name}" model="report.paperformat">
    <field name="name">Landscape A4</field>
    <field name="format">A4</field>
    <field name="orientation">Landscape</field>
    <field name="margin_top">25</field>
    <field name="margin_bottom">25</field>
    <field name="margin_left">10</field>
    <field name="margin_right">10</field>
</record>
```
Then reference it: `<field name="paperformat_id" ref="paperformat_{name}"/>`.

### B3. Generate Report Template

```xml
<!-- reports/report_{name}_template.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="report_{name}_template">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="web.external_layout">
                    <div class="page">
                        <!-- HEADER: document title, reference, dates -->
                        <!-- PARTNER INFO: contact widget -->
                        <!-- LINE ITEMS TABLE: thead/tbody with sections, notes, products -->
                        <!-- TOTALS: subtotal, taxes, total -->
                        <!-- NOTES / T&C -->
                        <!-- SIGNATURES (optional) -->
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

### B4. Template Content Guidelines

**Header area** — two-column row:
- Left: document title (state-aware), reference (`t-field="doc.name"`)
- Right: date, validity, customer reference

**Partner info** — use contact widget:
```xml
<div t-field="doc.partner_id"
     t-options='{"widget": "contact", "fields": ["address", "name", "phone", "email"], "no_marker": True}'/>
```

**Line items table** — handle `display_type`:
- `line_section`: bold, full-width, `bg-light`
- `line_note`: italic, full-width
- Regular lines: product, qty + UoM, unit price, discount (if any), subtotal

**Totals** — right-aligned summary table: subtotal, tax groups, total (bold, border-top).

**Field widgets**:
```xml
<span t-field="doc.date" t-options='{"widget": "date"}'/>
<span t-field="doc.amount" t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>
<img t-if="doc.image_128" t-att-src="image_data_uri(doc.image_128)" style="max-height: 50px;"/>
```

**Page breaks**:
```xml
<div style="page-break-before: always;"/>
<div style="page-break-inside: avoid;">...</div>
```

### B5. Layout Wrappers Reference

| Wrapper | Use case |
|---------|----------|
| `web.external_layout` | Full company header/footer (most common) |
| `web.html_container` | Outermost container (always required) |
| `web.internal_layout` | No header/footer |

### B6. CSS Styling

For custom report styles, create `static/src/css/report_{name}.css` and add to manifest assets under `web.report_assets_common`:
```xml
'assets': {
    'web.report_assets_common': [
        '{module}/static/src/css/report_{name}.css',
    ],
},
```

### B7. Output Structure

```
projects/{module}/
├── __manifest__.py               # Updated with report files + optional assets
├── reports/
│   ├── report_actions.xml        # Report action (binding to print menu)
│   └── report_{name}_template.xml  # QWeb template
└── static/src/css/
    └── report_{name}.css         # Optional custom styles
```

### B8. Validation Checklist

- [ ] Model exists and has `name` field
- [ ] Report name is unique (no collision with existing `ir.actions.report`)
- [ ] Template ID matches `report_name` in the action
- [ ] `binding_model_id` reference is correct
- [ ] `web.external_layout` called inside `web.html_container`
- [ ] Bootstrap classes used for layout (responsive)
- [ ] Page breaks handled for multi-page content

---

## Section C: Migrate Template

Triggered by: `/odoo-report migrate <file> <target-version> [--from VERSION] [--dry-run] [--recursive]`

### C1. Analyze Source

Read the file(s). Detect source version from:
1. `--from` flag
2. Syntax heuristics (`t-esc` = 14, `report_template` singular = 14-16, etc.)
3. Parent directory name

Report what was found:
```
Source: projects/module/data/mail_template.xml
Detected version: Odoo 14
Target version: Odoo 17
Templates found: 3 (mail.template records)
```

### C2. Migration Matrix

```
FROM → TO  | 14  | 15  | 16  | 17  | 18  | 19
-----------+-----+-----+-----+-----+-----+----
Odoo 14    |  -  |  M  |  M  |  H  |  H  |  H
Odoo 15    |  L  |  -  |  L  |  M  |  M  |  M
Odoo 16    |  L  |  L  |  -  |  L  |  L  |  M
Odoo 17    |  M  |  L  |  L  |  -  |  L  |  L
Odoo 18    |  M  |  M  |  L  |  L  |  -  |  L
Odoo 19    |  H  |  M  |  M  |  L  |  L  |  -
L = Low   M = Medium   H = High effort
```

### C3. Automatic Transformations

Apply all applicable rules in order:

**14 → 15+: Output syntax**
```xml
<!-- BEFORE --> <t t-esc="object.name"/>
<!-- AFTER  --> <t t-out="object.name"/>

<!-- BEFORE --> <t t-raw="object.description"/>
<!-- AFTER  --> <t t-out="object.description"/>
```

**14-16 → 17+: Report attachment field**
```xml
<!-- BEFORE --> <field name="report_template" ref="module.report_action"/>
<!-- AFTER  --> <field name="report_template_ids" eval="[(4, ref('module.report_action'))]"/>
```

**Any → 16+: Template category** (optional enhancement)
```xml
<field name="template_category">base_template</field>
```

**Any → 19: Company branding colors**
```xml
<!-- BEFORE --> <a style="background-color: #875A7B;">Button</a>
<!-- AFTER  -->
<t t-set="btn_bg" t-value="object.company_id.email_secondary_color or '#875A7B'"/>
<a t-att-style="'background-color: %s' % btn_bg">Button</a>
```

### C4. Transformation Summary Table

| Pattern | From | To | Versions |
|---------|------|----|----------|
| `t-esc` → `t-out` | `t-esc` | `t-out` | 14 → 15+ |
| `t-raw` → `t-out` | `t-raw` | `t-out` | 14 → 15+ |
| Report field | `report_template` | `report_template_ids` | 14-16 → 17+ |
| Branding colors | Hardcoded hex | `company.email_*_color` | Any → 19 |

### C5. Manual Review Flags

Flag these for human review (do not auto-transform):

| Pattern | Reason |
|---------|--------|
| Custom render methods | May need context updates |
| Direct SQL in templates | Security review required |
| Complex Jinja2 expressions | Version-specific behavior |
| Custom QWeb extensions | May be deprecated |

### C6. Apply and Output

1. Create backup: `{file}.bak`
2. Apply transformations, reporting each change with line number
3. Validate migrated XML (well-formed, no deprecated syntax remaining)
4. Write migrated file
5. Show diff summary:

```
Migration complete:
  12 t-esc → t-out
   2 t-raw → t-out
   2 report_template → report_template_ids
   0 manual review items

Files:
  {file}.bak    (backup)
  {file}        (migrated)
```

### C7. Migration Checklist

**Pre-migration**: Backup files, note current version, verify templates work now.

**Syntax updates**:
- [ ] `t-esc` → `t-out` (15+)
- [ ] `t-raw` → `t-out` (15+)
- [ ] `report_template` → `report_template_ids` (17+)
- [ ] Check deprecated model fields / renamed fields

**Enhancements (optional)**:
- [ ] Add `template_category` (16+)
- [ ] Add company branding colors (19)
- [ ] Use new layout variants (18+)

**Post-migration**:
- [ ] XML syntax valid
- [ ] Template renders correctly
- [ ] Email sending works
- [ ] PDF report generates

---

## Footer: Previously Available Commands

The following 10 commands have been consolidated. The 3 creation/migration commands are now sub-commands of `/odoo-report`. The remaining 6 management commands are handled by the skill automatically when you describe what you need in natural language.

| Old Command | Status |
|-------------|--------|
| `/create-email-template` | Replaced by `/odoo-report create-email` |
| `/create-qweb-report` | Replaced by `/odoo-report create-report` |
| `/migrate-template` | Replaced by `/odoo-report migrate` |
| `/analyze-template` | Skill-driven (just ask: "analyze this template") |
| `/debug-template` | Skill-driven (just ask: "debug the template rendering") |
| `/fix-template` | Skill-driven (just ask: "fix the broken template") |
| `/validate-template` | Skill-driven (just ask: "validate before deployment") |
| `/list-templates` | Skill-driven (just ask: "list templates for sale.order") |
| `/preview-template` | Skill-driven (just ask: "preview the email output") |
| `/style-report` | Skill-driven (just ask: "add CSS styling to the report") |

---

*Odoo Report Plugin v2.0 — TaqaTechno*
*Unified command for email templates & QWeb reports across Odoo 14-19*

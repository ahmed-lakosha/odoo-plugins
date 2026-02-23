# Odoo Report Plugin Enhancement Plan v2.0

**Based on**: Sadad Invoice Report Development Experience
**Date**: January 19, 2026
**Current Version**: 1.0.0
**Target Version**: 2.0.0

---

## Executive Summary

Analysis of the `sadad_invoice_report` module development revealed **critical gaps** in the current odoo-report-plugin that caused significant debugging time. This plan outlines enhancements to prevent these issues for future users.

### Key Issues Discovered

| Issue | Time Lost | Root Cause | Plugin Gap |
|-------|-----------|------------|------------|
| Arabic text corruption (ÙØ§ØªÙˆØ±Ø©) | 2+ hours | UTF-8 → Latin-1 encoding | No RTL/encoding documentation |
| wkhtmltopdf not found | 30 min | Missing `bin_path` config | No wkhtmltopdf setup guide |
| Google Fonts not loading | 1 hour | wkhtmltopdf runs offline | No font guidance |
| CSS not parsing | 1 hour | Semicolons in URL breaking SCSS | No SCSS pitfalls documentation |
| Theme Utils not running | 30 min | Only runs on install, not update | N/A (theme-specific) |

**Total Time Lost**: ~5+ hours on preventable issues

---

## Analysis: Sadad Invoice Module Structure

### Working Module Structure

```
sadad_invoice_report/
├── __init__.py
├── __manifest__.py
├── data/
│   └── report_paperformat.xml       # ← MISSING in plugin templates
├── report/
│   ├── invoice_report_template.xml   # QWeb template
│   └── invoice_report_action.xml     # Report action
└── static/src/scss/
    └── invoice_report.scss           # ← MISSING in plugin guidance
```

### Critical Success Pattern: Template Wrapper

The **ONLY** solution that worked for Arabic/UTF-8:

```xml
<template id="report_document">
    <t t-call="web.html_container">        <!-- CRITICAL: UTF-8 handling -->
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout"> <!-- CRITICAL: Font loading -->
                <t t-call="module.report_content"/>
            </t>
        </t>
    </t>
</template>
```

### Failed Approaches (DO NOT USE)

1. **Google Fonts CDN** - wkhtmltopdf cannot fetch external resources
2. **font-family declarations alone** - Does not fix encoding
3. **unicode-bidi CSS** - Does not fix encoding
4. **Custom @import in SCSS** - Semicolons break SCSS parsing

---

## Enhancement Plan: 8 Major Additions

### 1. NEW SECTION: wkhtmltopdf Setup & Troubleshooting

**Priority**: HIGH
**Files**: `SKILL.md`, `memories/wkhtmltopdf_setup.md`

```markdown
## wkhtmltopdf Configuration

### Installation
```bash
# Windows
winget install wkhtmltopdf.wkhtmltox

# Ubuntu/Debian
sudo apt-get install wkhtmltopdf

# macOS
brew install wkhtmltopdf
```

### Odoo Configuration (REQUIRED)
```ini
# odoo.conf
bin_path = C:\Program Files\wkhtmltopdf\bin  # Windows
# bin_path = /usr/local/bin                   # Linux
```

### Verification
```
Server log should show:
"Will use the Wkhtmltopdf binary at [PATH]\wkhtmltopdf.exe"
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Unable to find Wkhtmltopdf" | bin_path not set | Add bin_path to odoo.conf |
| PDF generation hangs | Network timeout | See offline mode section |
| Blank PDF | CSS errors | Check SCSS syntax |
```

---

### 2. NEW SECTION: Arabic/RTL & Multilingual Reports

**Priority**: CRITICAL
**Files**: `SKILL.md`, `memories/rtl_support.md`, `templates/qweb/bilingual_report.xml`

```markdown
## Arabic/RTL Report Support

### CRITICAL REQUIREMENT
Always use `web.html_container` + `web.external_layout`:

```xml
<!-- CORRECT - UTF-8 encoding works -->
<template id="report_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <t t-call="module.report_content"/>
            </t>
        </t>
    </t>
</template>

<!-- WRONG - Will cause encoding corruption -->
<template id="report_document">
    <html>
        <body>...</body>
    </html>
</template>
```

### Encoding Corruption Symptoms

If Arabic text displays as `ÙØ§ØªÙˆØ±Ø©` instead of `فاتورة`:
- **Cause**: UTF-8 bytes interpreted as Latin-1
- **Solution**: Use `web.html_container` (includes `<meta charset="utf-8"/>`)

### Bilingual Label Pattern

```xml
<!-- English | Arabic format -->
<th style="background: #1a5276; color: white;">
    Date | التاريخ
</th>

<!-- Stacked format -->
<th>
    <div>رمز الصنف</div>
    <div style="font-size: 11px;">Item Code</div>
</th>
```

### RTL Styling

```xml
<div style="direction: rtl; text-align: right;">
    يرجى إرسال حوالاتكم كما يأتي
</div>
```
```

---

### 3. NEW SECTION: Paper Format Configuration

**Priority**: MEDIUM
**Files**: `SKILL.md`, `templates/data/paperformat.xml`

```markdown
## Custom Paper Formats

### Paper Format Template

```xml
<record id="paperformat_custom" model="report.paperformat">
    <field name="name">Custom A4</field>
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
```

### Linking to Report Action

```xml
<record id="action_report" model="ir.actions.report">
    ...
    <field name="paperformat_id" ref="module.paperformat_custom"/>
</record>
```

### Common Paper Formats

| Format | Dimensions | Use Case |
|--------|------------|----------|
| A4 | 210 × 297 mm | Standard documents |
| Letter | 216 × 279 mm | US documents |
| Legal | 216 × 356 mm | Legal documents |
| Custom | Set page_width/height | Special sizes |

### Orientation Options
- `Portrait` (default)
- `Landscape` (wide tables, charts)
```

---

### 4. NEW SECTION: Report SCSS Styling

**Priority**: HIGH
**Files**: `SKILL.md`, `memories/report_scss.md`

```markdown
## Report SCSS Styling

### Asset Bundle for Reports

```python
# __manifest__.py
'assets': {
    'web.report_assets_common': [
        'module/static/src/scss/report_styles.scss',
    ],
},
```

### CRITICAL: Google Fonts Pitfall

```scss
// ❌ BROKEN - Semicolons break SCSS parsing
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

// ✅ FIXED - Use range syntax
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300..700&display=swap');

// ✅ BEST - Don't use Google Fonts at all (wkhtmltopdf is offline)
// Rely on system fonts or web.external_layout's font loading
```

### Why Google Fonts Often Fail

wkhtmltopdf generates PDFs **offline** without network access:
1. Cannot fetch external URLs
2. Google Fonts CDN requests time out
3. Result: Missing fonts, fallback to defaults

### Recommended Font Stack

```scss
.report-content {
    font-family: 'DejaVu Sans', 'Arial', 'Helvetica', sans-serif;
}
```

### Color Scheme Pattern

```scss
// Define once, use everywhere
$primary-color: #1a5276;
$secondary-color: #d5dbdb;
$border-color: #bdc3c7;
$text-dark: #000;
$text-muted: #666;

.report-header {
    color: $primary-color;
}

.table-header {
    background-color: $primary-color;
    color: white;
}

.label-cell {
    background-color: $secondary-color;
    color: $primary-color;
    font-weight: bold;
}
```
```

---

### 5. NEW COMMAND: /debug-report

**Priority**: HIGH
**Files**: `commands/debug-report.md`

```markdown
---
title: 'Debug Report'
description: 'Diagnose and fix PDF report generation issues'
---

# Debug Report

Systematic diagnosis of QWeb report issues.

## Usage

```
/debug-report [issue-type]
/debug-report encoding      # Arabic/UTF-8 issues
/debug-report blank-pdf     # Empty or broken PDF
/debug-report styling       # CSS not applying
/debug-report fonts         # Font rendering issues
```

## Diagnostic Workflow

### Step 1: Check wkhtmltopdf

```bash
# Verify installation
wkhtmltopdf --version

# Check Odoo config
grep bin_path /path/to/odoo.conf
```

### Step 2: Check Template Structure

```
Required wrapping order:
1. web.html_container (UTF-8 meta tag)
2. t-foreach docs as o (record loop)
3. web.external_layout (company header/fonts)
4. div.page (actual content)
```

### Step 3: Test Render

```python
# Odoo shell
report = env.ref('module.action_report')
pdf = report._render_qweb_pdf([record_id])
# Check for errors in console
```

### Common Issues Checklist

- [ ] wkhtmltopdf bin_path configured
- [ ] Using web.html_container wrapper
- [ ] Using web.external_layout
- [ ] No external CDN resources
- [ ] SCSS has no semicolons in URLs
- [ ] Browser cache cleared after fix
```

---

### 6. NEW SECTION: Version-Specific Report Patterns

**Priority**: MEDIUM
**Files**: `SKILL.md`

```markdown
## Version-Specific Report Patterns

### Odoo 14-16 vs 17+

| Feature | Odoo 14-16 | Odoo 17+ |
|---------|------------|----------|
| Output tag | `t-esc` | `t-out` (preferred) |
| report_template | Single M2O | `report_template_ids` M2M |
| binding_model_id | Required | Required |

### Report Action Field Differences

```xml
<!-- Odoo 14-16 -->
<field name="report_template" ref="module.report_action"/>

<!-- Odoo 17+ -->
<field name="report_template_ids" eval="[(4, ref('module.report_action'))]"/>
```

### t-field vs t-out in Reports

```xml
<!-- t-field: Better for reports (includes widgets) -->
<span t-field="doc.date" t-options='{"widget": "date"}'/>
<span t-field="doc.amount" t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>

<!-- t-out: For simple values -->
<t t-out="doc.name"/>
```
```

---

### 7. NEW TEMPLATE: Bilingual Invoice Report

**Priority**: HIGH
**Files**: `templates/qweb/bilingual_invoice.xml`

Complete working template based on sadad_invoice success pattern:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Report Action -->
    <record id="action_report_bilingual_invoice" model="ir.actions.report">
        <field name="name">Bilingual Invoice</field>
        <field name="model">account.move</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">module.report_bilingual_invoice_template</field>
        <field name="report_file">module.report_bilingual_invoice_template</field>
        <field name="paperformat_id" ref="module.paperformat_invoice"/>
        <field name="binding_model_id" ref="account.model_account_move"/>
        <field name="binding_type">report</field>
        <field name="print_report_name">'Invoice - %s' % object.name</field>
    </record>

    <!-- CRITICAL: Use web.html_container + web.external_layout -->
    <template id="report_bilingual_invoice_template">
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
        <div class="page" style="font-family: Arial, sans-serif;">
            <!-- Bilingual Header -->
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #1a5276;">
                    Sales Invoice | فاتورة مبيعات
                </h1>
                <h2 t-field="o.name"/>
            </div>

            <!-- Customer Info with Bilingual Labels -->
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
                <tr>
                    <td style="border: 1px solid #bdc3c7; padding: 10px; background: #d5dbdb; color: #1a5276; font-weight: bold;">
                        Date | التاريخ
                    </td>
                    <td style="border: 1px solid #bdc3c7; padding: 10px;">
                        <span t-field="o.invoice_date" t-options='{"widget": "date"}'/>
                    </td>
                    <td style="border: 1px solid #bdc3c7; padding: 10px; background: #d5dbdb; color: #1a5276; font-weight: bold;">
                        Customer | العميل
                    </td>
                    <td style="border: 1px solid #bdc3c7; padding: 10px;">
                        <span t-field="o.partner_id.name"/>
                    </td>
                </tr>
            </table>

            <!-- Invoice Lines -->
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #1a5276; color: white;">
                        <th style="padding: 12px; border: 1px solid #1a5276;">#</th>
                        <th style="padding: 12px; border: 1px solid #1a5276;">
                            <div>اسم الصنف</div>
                            <div style="font-size: 11px;">Product</div>
                        </th>
                        <th style="padding: 12px; border: 1px solid #1a5276;">
                            <div>الكمية</div>
                            <div style="font-size: 11px;">Qty</div>
                        </th>
                        <th style="padding: 12px; border: 1px solid #1a5276;">
                            <div>السعر</div>
                            <div style="font-size: 11px;">Price</div>
                        </th>
                        <th style="padding: 12px; border: 1px solid #1a5276;">
                            <div>الإجمالي</div>
                            <div style="font-size: 11px;">Total</div>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <t t-set="line_num" t-value="0"/>
                    <t t-foreach="o.invoice_line_ids" t-as="line">
                        <t t-if="line.product_id">
                            <t t-set="line_num" t-value="line_num + 1"/>
                            <tr>
                                <td style="border: 1px solid #bdc3c7; padding: 10px; text-align: center;">
                                    <t t-out="line_num"/>
                                </td>
                                <td style="border: 1px solid #bdc3c7; padding: 10px;">
                                    <t t-out="line.name"/>
                                </td>
                                <td style="border: 1px solid #bdc3c7; padding: 10px; text-align: center;">
                                    <t t-out="line.quantity"/>
                                </td>
                                <td style="border: 1px solid #bdc3c7; padding: 10px; text-align: right;">
                                    <span t-field="line.price_unit" t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
                                </td>
                                <td style="border: 1px solid #bdc3c7; padding: 10px; text-align: right;">
                                    <span t-field="line.price_subtotal" t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
                                </td>
                            </tr>
                        </t>
                    </t>
                </tbody>
            </table>

            <!-- Totals -->
            <div style="margin-top: 25px;">
                <table style="width: 40%; margin-left: auto; border-collapse: collapse;">
                    <tr>
                        <td style="border: 1px solid #bdc3c7; padding: 10px; background: #d5dbdb; color: #1a5276; font-weight: bold;">
                            المجموع | Total
                        </td>
                        <td style="border: 1px solid #bdc3c7; padding: 10px; text-align: right;">
                            <span t-field="o.amount_total" t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
                        </td>
                    </tr>
                </table>
            </div>
        </div>
    </template>
</odoo>
```

---

### 8. ENHANCED: Validation Checklist

**Priority**: HIGH
**Files**: `validators/report_validator.md`

```markdown
## Report Validation Checklist

### Pre-Flight Checks (MANDATORY)

```
┌─────────────────────────────────────────────────────────────────┐
│              QWEB REPORT VALIDATION CHECKLIST                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. INFRASTRUCTURE                                               │
│     □ wkhtmltopdf installed                                      │
│     □ bin_path configured in odoo.conf                          │
│     □ Server restarted after config change                       │
│                                                                   │
│  2. TEMPLATE STRUCTURE                                           │
│     □ Uses web.html_container as outermost wrapper              │
│     □ Uses web.external_layout for UTF-8/fonts                  │
│     □ Has t-foreach docs as doc/o loop                          │
│     □ Content in div.page element                                │
│                                                                   │
│  3. ENCODING (for non-Latin text)                               │
│     □ NOT using custom <html> tag                                │
│     □ NOT relying on Google Fonts CDN                           │
│     □ Arabic text renders correctly in preview                   │
│     □ Currency symbols display correctly                         │
│                                                                   │
│  4. SCSS/CSS                                                     │
│     □ Using web.report_assets_common bundle                      │
│     □ No semicolons in Google Fonts URLs                        │
│     □ No external @import URLs                                   │
│     □ Font stack uses system fonts                               │
│                                                                   │
│  5. REPORT ACTION                                                │
│     □ report_name matches template id                            │
│     □ report_file matches template id                            │
│     □ binding_model_id is correct ref                            │
│     □ paperformat_id linked if custom                            │
│                                                                   │
│  6. MANIFEST                                                     │
│     □ data/ files listed in correct order                        │
│     □ assets bundle correct (report_assets_common)              │
│     □ depends includes 'account' or target module               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Post-Generation Verification

```bash
# 1. Update module
python -m odoo -c conf/project.conf -d project_db -u module --stop-after-init

# 2. Check server log for wkhtmltopdf
# Look for: "Will use the Wkhtmltopdf binary at..."

# 3. Generate test PDF
# Navigate to record > Print menu > Select report

# 4. Verify PDF content
# - Non-Latin text displays correctly
# - Currency symbols correct
# - Layout matches design
```
```

---

## Implementation Roadmap

### Phase 1: Critical Fixes (Week 1)

| Task | Priority | Files |
|------|----------|-------|
| Add wkhtmltopdf setup section | HIGH | SKILL.md |
| Add Arabic/RTL/encoding section | CRITICAL | SKILL.md |
| Add bilingual template | HIGH | templates/qweb/ |
| Update validation checklist | HIGH | validators/ |

### Phase 2: Enhanced Documentation (Week 2)

| Task | Priority | Files |
|------|----------|-------|
| Add paper format section | MEDIUM | SKILL.md |
| Add SCSS styling section | HIGH | SKILL.md, memories/ |
| Create /debug-report command | HIGH | commands/ |
| Version-specific patterns | MEDIUM | SKILL.md |

### Phase 3: Templates & Testing (Week 3)

| Task | Priority | Files |
|------|----------|-------|
| Add more template examples | MEDIUM | templates/ |
| Add error recovery patterns | HIGH | memories/ |
| Update README.md | LOW | README.md |
| Bump version to 2.0.0 | - | plugin.json, SKILL.md |

---

## Version Changelog

### v2.0.0 (Planned)

**MAJOR ENHANCEMENTS**:

1. **NEW: wkhtmltopdf Setup Guide**
   - Installation commands (Windows, Linux, macOS)
   - Odoo configuration (bin_path)
   - Troubleshooting common errors

2. **NEW: Arabic/RTL Support Section**
   - CRITICAL: web.html_container requirement
   - Encoding corruption diagnosis
   - Bilingual label patterns
   - RTL styling guidelines

3. **NEW: Paper Format Documentation**
   - Custom paper format template
   - Standard format reference
   - Linking to report actions

4. **NEW: Report SCSS Styling**
   - Correct asset bundle (web.report_assets_common)
   - Google Fonts pitfalls and solutions
   - Offline font considerations
   - Color scheme patterns

5. **NEW: /debug-report Command**
   - Systematic diagnosis workflow
   - Issue-specific debugging paths
   - Server log verification

6. **NEW: Bilingual Invoice Template**
   - Complete working example
   - Arabic/English labels
   - Proven UTF-8 pattern

7. **ENHANCED: Validation Checklist**
   - Infrastructure checks
   - Template structure verification
   - Encoding validation
   - Post-generation testing

8. **NEW: Error Recovery Patterns**
   - Common issues table
   - Time-saving solutions
   - Real-world debugging tips

---

## Success Metrics

After implementing v2.0.0, the plugin should enable:

- [ ] First-time Arabic PDF report working in < 30 minutes
- [ ] Zero encoding corruption issues
- [ ] Clear wkhtmltopdf setup path
- [ ] Bilingual reports with minimal effort
- [ ] Self-debugging capability via /debug-report

---

*Enhancement Plan compiled from sadad_invoice_report development experience*
*TaqaTechno - Professional Odoo Development*

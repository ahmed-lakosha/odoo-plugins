---
name: odoo-i18n
description: "Comprehensive Odoo i18n toolkit for extracting translatable strings, validating .po files, generating translation reports, managing Arabic/RTL layouts, and handling multilingual deployments across Odoo 14-19."
version: "1.0.0"
author: "TaqaTechno"
license: "MIT"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
metadata:
  mode: "codebase"
  supported-versions: ["14","15","16","17","18","19"]
  primary-languages: ["ar","en","tr","fr"]
  categories: [i18n, translation, rtl, arabic]
---

# Odoo i18n Skill — Complete Internationalization Reference

This skill provides deep expertise in Odoo internationalization (i18n) and localization (l10n). It covers extracting translatable strings, validating .po files, generating translation reports, and handling Arabic/RTL layouts across Odoo versions 14 through 19.

---

## 1. Odoo Translation Architecture

### 1.1 File Types

Odoo uses the GNU gettext standard for translations:

| File | Purpose | Location |
|------|---------|----------|
| `.pot` | Portable Object Template — master template with all source strings | `module/i18n/module.pot` |
| `.po` | Portable Object — translated strings for a specific language | `module/i18n/ar.po` |
| `.mo` | Machine Object — compiled binary, auto-generated from .po | Runtime cache only |

### 1.2 Directory Structure

Every Odoo module that supports translations must have an `i18n/` directory:

```
my_module/
├── __manifest__.py
├── i18n/
│   ├── my_module.pot      ← Template (all source strings, no translations)
│   ├── ar.po              ← Arabic translations
│   ├── ar_SA.po           ← Saudi Arabic variant (optional)
│   ├── fr.po              ← French translations
│   └── tr.po              ← Turkish translations
├── models/
├── views/
└── ...
```

### 1.3 .po File Anatomy

```po
# Arabic translation of my_module
# Copyright (C) 2024 TaqaTechno
# This file is distributed under the same license as the my_module package.
# Translator: Ahmed Al-Rashidi <ahmed@taqat.com>, 2024
#
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 17.0\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2024-01-15 10:30+0300\n"
"PO-Revision-Date: 2024-01-20 14:00+0300\n"
"Last-Translator: Ahmed Al-Rashidi <ahmed@taqat.com>\n"
"Language-Team: Arabic\n"
"Language: ar\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5;\n"

#. module: my_module
#: model:ir.model,name:my_module.model_my_record
msgid "My Record"
msgstr "سجلي"

#. module: my_module
#: model_terms:ir.ui.view,arch_db:my_module.view_my_form
msgid "Save"
msgstr "حفظ"

#. module: my_module
#: code:addons/my_module/models/my_model.py:45
#, python-format
msgid "Record %s not found"
msgstr "السجل %s غير موجود"
```

### 1.4 How Odoo Loads Translations

1. On module install/update: Odoo reads `.po` files from `i18n/` directory
2. On language install: Odoo loads all `.po` files for that language across all installed modules
3. At runtime: translations are cached in memory and applied based on `res.lang` of the user
4. For website: translations are applied based on the URL language prefix (`/ar/`, `/en/`) or session language

### 1.5 Translation Loading Priority

Odoo applies translations in this priority order (highest to lowest):
1. User-specific overrides (from Translations menu)
2. Module `.po` file
3. Base Odoo translations
4. Source string (fallback)

---

## 2. Python Translations

### 2.1 Basic Import and Usage

```python
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    def action_validate(self):
        for rec in self:
            if not rec.name:
                # CORRECT: wrap literal string in _()
                raise UserError(_('Name is required before validation.'))
```

### 2.2 String Interpolation — Critical Rules

```python
# CORRECT: Variable substitution OUTSIDE _()
raise UserError(_('Record "%s" cannot be deleted.') % record.name)
raise UserError(_('Found %d records matching criteria.') % count)

# CORRECT: Named format specifiers (preferred for clarity)
raise UserError(_('Invoice %(number)s is in state %(state)s.') % {
    'number': invoice.name,
    'state': invoice.state,
})

# CORRECT: .format() can work but % is conventional in Odoo
raise UserError(_('Hello {}!').format(partner.name))

# WRONG: f-strings break i18n — the string is evaluated before _() sees it
raise UserError(_(f'Record {record.name} not found'))  # DO NOT USE

# WRONG: String concatenation breaks i18n
raise UserError(_('Record ') + record.name + _(' not found'))  # DO NOT USE

# WRONG: Building string before _() — translator never sees the full context
msg = 'Record not found'
raise UserError(_(msg))  # Technically works but makes extraction hard
```

### 2.3 Lazy Translation with `_lt()`

Use `_lt()` for module-level strings that are defined at class load time, not at call time:

```python
from odoo.tools.translate import _lt

class MyModel(models.Model):
    _name = 'my.model'

    # CORRECT: Use _lt() for class-level string definitions
    state = fields.Selection([
        ('draft', _lt('Draft')),
        ('confirmed', _lt('Confirmed')),
        ('validated', _lt('Validated')),
        ('cancelled', _lt('Cancelled')),
    ], string='Status', default='draft')

    # CORRECT: Class attribute strings
    _description = 'My Model'  # This does NOT need _() — it's not end-user facing

    # WRONG: Using _() at class level causes issues because no request context exists
    # state = fields.Selection([('draft', _('Draft'))], ...)  # Avoid this
```

### 2.4 Field String Attributes

Field `string` parameters are automatically translated by Odoo — do NOT wrap them in `_()`:

```python
class MyModel(models.Model):
    _name = 'my.model'

    # CORRECT: string= is auto-translated by Odoo's i18n system
    name = fields.Char(string='Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer')
    amount_total = fields.Float(string='Total Amount', digits=(16, 2))

    # The help attribute is also auto-translated
    ref = fields.Char(
        string='Reference',
        help='Internal reference number for tracking purposes.'
    )
```

### 2.5 Model Name and Description

```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'  # Auto-translated; do NOT wrap in _()
```

### 2.6 Report Translations in Python

```python
def _get_report_values(self, docids, data=None):
    docs = self.env['my.model'].browse(docids)
    return {
        'doc_ids': docids,
        'doc_model': 'my.model',
        'docs': docs,
        'report_title': _('Monthly Sales Report'),
    }
```

### 2.7 Email Template Translations

In Python-generated emails, wrap strings in `_()`. For XML-based templates, use `<t t-esc>` with Odoo's translation system.

```python
def send_notification(self):
    subject = _('Your order %(ref)s has been confirmed') % {'ref': self.name}
    body = _('Dear %(name)s, your order is ready.') % {'name': self.partner_id.name}
    self.message_post(subject=subject, body=body)
```

---

## 3. XML / QWeb Translations

### 3.1 View Field Translations

Field labels defined in views via `string` attribute are automatically translatable:

```xml
<odoo>
    <record id="view_my_model_form" model="ir.ui.view">
        <field name="name">my.model.form</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <form string="My Record">
                <sheet>
                    <group>
                        <!-- string= attributes in views are auto-translated -->
                        <field name="name" string="Record Name"/>
                        <field name="partner_id" string="Associated Partner"/>
                    </group>
                    <group string="Financial Information">
                        <field name="amount_total" string="Total"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>
</odoo>
```

### 3.2 Static Text in QWeb Templates

```xml
<!-- Website templates -->
<template id="page_home" name="Home Page">
    <t t-call="website.layout">
        <div id="wrap">
            <!-- Text nodes in templates ARE translatable -->
            <h1>Welcome to Our Website</h1>
            <p>We provide excellent services.</p>

            <!-- Attribute translations use special markup -->
            <img src="/static/img/hero.jpg" alt="Our Services"/>

            <!-- Dynamic content with translation -->
            <span t-field="record.name"/>

            <!-- Explicit translation escape -->
            <span t-esc="'Hello World'"/>
        </div>
    </t>
</template>
```

### 3.3 QWeb Report Translations

```xml
<template id="report_my_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <!-- Text nodes are translatable in reports -->
                    <h2>Sales Order</h2>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Unit Price</th>
                                <th>Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-foreach="doc.order_line" t-as="line">
                                <tr>
                                    <td><t t-esc="line.product_id.name"/></td>
                                    <td><t t-esc="line.product_uom_qty"/></td>
                                    <td><t t-esc="line.price_unit"/></td>
                                    <td><t t-esc="line.price_subtotal"/></td>
                                </tr>
                            </t>
                        </tbody>
                    </table>
                </div>
            </t>
        </t>
    </t>
</template>
```

### 3.4 Disabling Translation for Specific Nodes

```xml
<!-- Disable translation for a specific block (e.g., code, technical content) -->
<t t-translation="off">
    <code>SELECT * FROM res_partner WHERE active = true</code>
</t>

<!-- Numbers and codes should not be translated -->
<span t-translation="off" t-esc="doc.reference"/>
```

### 3.5 `t-esc` vs `t-out` in Translation Context

```xml
<!-- t-esc: escapes HTML, used for plain text values -->
<span t-esc="record.name"/>

<!-- t-out: outputs raw HTML, used when value may contain markup -->
<div t-out="record.description"/>  <!-- Odoo 15+ preferred syntax -->

<!-- In translation context, both work but t-field is preferred for model fields -->
<span t-field="record.name"/>  <!-- Best: uses field's widget for formatting -->
```

### 3.6 Menu Item and Action Translations

```xml
<!-- Menu items are auto-translated -->
<menuitem id="menu_my_module" name="My Module" sequence="10"/>
<menuitem id="menu_my_records" name="Records" parent="menu_my_module" sequence="1"/>

<!-- Action names are auto-translated -->
<record id="action_my_records" model="ir.actions.act_window">
    <field name="name">My Records</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">list,form</field>
</record>
```

### 3.7 Website Snippet Translations

```xml
<!-- Snippet options labels are translatable -->
<template id="snippet_options" inherit_id="website.snippet_options">
    <xpath expr="." position="inside">
        <div data-snippet="s_my_snippet" data-name="My Snippet">
            <t t-call="website.snippet_options_color_palette"/>
        </div>
    </xpath>
</template>
```

---

## 4. JavaScript Translations

### 4.1 Odoo 16+ (New Framework — owl-based)

```javascript
/** @odoo-module **/

// Import translation function from new location
import { _t } from "@web/core/l10n/translation";

// Simple translation
const message = _t("Hello World");

// With variables — use template literals carefully, prefer %s pattern
const errorMsg = _t("Record %s not found").replace('%s', recordName);

// In component
import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.title = _t("My Component Title");
    }

    get buttonLabel() {
        return _t("Save Changes");
    }
}
```

### 4.2 Odoo 14/15 (Legacy Framework)

```javascript
/** @odoo-module **/

// Legacy import path
import { _t, _lt } from "web.core";

// Simple translation
const message = _t("Hello World");

// Lazy translation for module-level strings
const STATUS_LABELS = {
    draft: _lt("Draft"),
    confirmed: _lt("Confirmed"),
    done: _lt("Done"),
};
```

### 4.3 publicWidget with Translation

```javascript
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";

publicWidget.registry.MyWidget = publicWidget.Widget.extend({
    selector: '.my-widget',
    disabledInEditableMode: false,

    events: {
        'click .btn-submit': '_onSubmit',
        'click .btn-cancel': '_onCancel',
    },

    start: function () {
        // Translation works in publicWidget context
        this._super.apply(this, arguments);
        if (!this.editableMode) {
            this._initWidget();
        }
    },

    _initWidget: function () {
        const placeholder = _t("Enter your name here...");
        this.$('input.name-field').attr('placeholder', placeholder);
    },

    _onSubmit: function (ev) {
        ev.preventDefault();
        const successMsg = _t("Your form has been submitted successfully.");
        this._showMessage(successMsg, 'success');
    },

    _onCancel: function (ev) {
        ev.preventDefault();
        const confirmMsg = _t("Are you sure you want to cancel?");
        if (window.confirm(confirmMsg)) {
            window.history.back();
        }
    },

    _showMessage: function (msg, type) {
        const $alert = $(`<div class="alert alert-${type}">${msg}</div>`);
        this.$el.prepend($alert);
        setTimeout(() => $alert.fadeOut(() => $alert.remove()), 3000);
    },
});
```

### 4.4 JavaScript Translation Extraction

Odoo's i18n extractor finds `_t('...')` and `_lt('...')` calls in `.js` files. Ensure:
- Strings are literals, not variables
- No dynamic string construction inside `_t()`

```javascript
// CORRECT: Literal strings
const msg1 = _t("Save");
const msg2 = _t("Delete record");

// WRONG: Dynamic strings won't be extracted
const action = 'Save';
const msg = _t(action);  // Extractor can't find this

// WRONG: Template literals don't work with extraction
const name = 'World';
const msg = _t(`Hello ${name}`);  // Don't use this
```

---

## 5. Extracting Translations

### 5.1 Using Odoo CLI

```bash
# Export translations for a single module (creates/updates .po file)
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-export \
    --modules=my_module \
    --language=ar \
    --output=/path/to/ar.po \
    --stop-after-init

# Export without language (creates .pot template)
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-export \
    --modules=my_module \
    --output=/path/to/my_module.pot \
    --stop-after-init

# Export all modules for a language
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-export \
    --language=ar \
    --output=/path/to/all_ar.po \
    --stop-after-init
```

### 5.2 Using the Plugin Extractor Script

```bash
# Extract strings from a module and create .pot/.po files
python odoo-i18n/scripts/i18n_extractor.py \
    --module /path/to/my_module \
    --lang ar

# Extract with custom output directory
python odoo-i18n/scripts/i18n_extractor.py \
    --module /path/to/my_module \
    --lang fr \
    --output /path/to/output/
```

### 5.3 Manual .pot File Generation

The `.pot` file is the master template. Generate it once, derive `.po` files from it:

```bash
# Step 1: Generate .pot
python odoo-bin -c conf/myproject.conf -d mydb \
    --i18n-export --modules=my_module \
    --output=my_module/i18n/my_module.pot \
    --stop-after-init

# Step 2: Copy .pot to .po for each language
cp my_module/i18n/my_module.pot my_module/i18n/ar.po
cp my_module/i18n/my_module.pot my_module/i18n/fr.po
cp my_module/i18n/my_module.pot my_module/i18n/tr.po

# Step 3: Edit each .po file and add translations
# The msgstr entries in the copied .po files will be empty — fill them in
```

### 5.4 What Gets Extracted

Odoo's extraction process scans:

| Source | What is extracted |
|--------|------------------|
| `*.py` | `_('...')` and `_lt('...')` string arguments |
| `*.xml` | Field `string=` attributes, text nodes in views, `name=` in menu items |
| `*.js` | `_t('...')` and `_lt('...')` string arguments |
| Model fields | `string`, `help`, `selection` values |
| `_description` | Model description |
| Action `name` | Action display names |

---

## 6. Loading Translations

### 6.1 Load Language via CLI

```bash
# Install Arabic language pack into a database
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --load-language=ar \
    --stop-after-init

# Install multiple languages at once
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --load-language=ar,fr,tr \
    --stop-after-init
```

### 6.2 Import Specific .po File via CLI

```bash
# Import a .po file into the database
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-import=/path/to/ar.po \
    --language=ar \
    --modules=my_module \
    --stop-after-init

# Import and overwrite existing translations
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-import=/path/to/ar.po \
    --language=ar \
    --modules=my_module \
    --i18n-overwrite \
    --stop-after-init
```

### 6.3 Load via Odoo Shell

```python
# Interactive shell: python odoo-bin shell -d mydb

# Load a language
self.env['res.lang'].with_context(active_test=False).search(
    [('code', '=', 'ar')]
).active = True
self.env['base.language.install'].create({'lang_ids': [
    (6, 0, [self.env['res.lang'].search([('code', '=', 'ar')]).id])
]}).lang_install()
self.env.cr.commit()

# Simpler approach for existing language
self.env['res.lang'].load_lang('ar')
self.env.cr.commit()

# Load translations for a specific module
self.env['ir.translation'].load_module_terms(['my_module'], ['ar'])
self.env.cr.commit()
```

### 6.4 Load via Database Menu

In Odoo backend: Settings > Translations > Languages > Add a language, then select from list.

---

## 7. Arabic / RTL Support

### 7.1 What RTL Means in Odoo Context

Right-to-left (RTL) languages like Arabic, Hebrew, and Farsi require:
- Text flows from right to left
- UI elements mirror horizontally
- Margins/paddings swap sides
- Icons and arrows reverse direction
- Navigation flows right-to-left

### 7.2 Activating RTL in Odoo Website

```xml
<!-- In your theme's primary template -->
<template id="layout" inherit_id="website.layout">
    <xpath expr="//html" position="attributes">
        <!-- Odoo sets dir="rtl" automatically when Arabic is active language -->
        <!-- But you can force it for testing -->
    </xpath>
</template>
```

Odoo automatically adds `dir="rtl"` to the `<html>` element when the active language is RTL (Arabic, Hebrew, Farsi, Urdu). You do NOT need to hardcode this.

### 7.3 Bootstrap RTL CSS

```xml
<!-- In your theme assets, load Bootstrap RTL for RTL languages -->
<template id="assets_frontend" inherit_id="web.assets_frontend">
    <xpath expr="." position="inside">
        <!-- Bootstrap RTL is available in Odoo 16+ -->
        <!-- It's loaded automatically when dir="rtl" is set -->
    </xpath>
</template>
```

Odoo 16+ automatically switches to Bootstrap RTL CSS when the language is RTL. In older versions (14/15), you may need to load it manually.

### 7.4 SCSS RTL Patterns

```scss
// In static/src/scss/rtl.scss or within your main stylesheet

// Global RTL overrides using the [dir="rtl"] selector
[dir="rtl"] {
    // Text alignment
    .text-start { text-align: right !important; }
    .text-end { text-align: left !important; }

    // Navigation
    .nav-item { float: right; }
    .navbar-nav { padding-right: 0; padding-left: inherit; }

    // Breadcrumb separator
    .breadcrumb-item + .breadcrumb-item::before {
        float: right;
        padding-right: 0;
        padding-left: var(--bs-breadcrumb-item-padding-x);
        content: "\\";  // Reverse separator direction
    }

    // Icons that indicate direction
    .fa-chevron-right::before { content: "\f053"; }  // Swap left/right chevrons
    .fa-chevron-left::before { content: "\f054"; }
    .fa-arrow-right::before { content: "\f060"; }
    .fa-arrow-left::before { content: "\f061"; }

    // Form elements
    .input-group > .form-control:not(:last-child) {
        border-radius: 0 var(--bs-border-radius) var(--bs-border-radius) 0;
    }
    .input-group > .form-control:not(:first-child) {
        border-radius: var(--bs-border-radius) 0 0 var(--bs-border-radius);
    }

    // Dropdown
    .dropdown-menu-end {
        right: auto;
        left: 0;
    }

    // Cards with horizontal layout
    .card-horizontal { flex-direction: row-reverse; }

    // Table
    th, td {
        text-align: right;
    }
}
```

### 7.5 CSS Logical Properties (Modern Approach)

Instead of physical `left`/`right`, use logical properties that automatically adapt to RTL:

```scss
// Instead of margin-left, use margin-inline-start
.my-element {
    margin-inline-start: 1rem;    // = margin-left in LTR, margin-right in RTL
    margin-inline-end: 0.5rem;    // = margin-right in LTR, margin-left in RTL
    padding-inline-start: 1.5rem;
    padding-inline-end: 0.75rem;
    border-inline-start: 3px solid var(--primary);  // Left border in LTR, right in RTL
    text-align: start;  // = left in LTR, right in RTL
}
```

### 7.6 Flexbox and Grid with RTL

```scss
// Flexbox naturally mirrors in RTL without extra CSS
.flex-container {
    display: flex;
    flex-direction: row;  // Items flow right-to-left automatically in RTL
    gap: 1rem;
}

// Only override if you specifically need LTR in RTL context
[dir="rtl"] .force-ltr {
    direction: ltr;
    unicode-bidi: isolate;
}
```

### 7.7 RTL Detection in JavaScript

```javascript
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.RTLAwareWidget = publicWidget.Widget.extend({
    selector: '.my-section',

    start: function () {
        // Detect RTL from HTML element attribute
        this.isRtl = document.documentElement.getAttribute('dir') === 'rtl';

        if (this.isRtl) {
            this._initRtlLayout();
        } else {
            this._initLtrLayout();
        }

        return this._super.apply(this, arguments);
    },

    _initRtlLayout: function () {
        // Apply RTL-specific JavaScript behavior
        // e.g., slider direction, animation direction
        this.$('.carousel').attr('data-bs-direction', 'right');
    },

    _initLtrLayout: function () {
        this.$('.carousel').attr('data-bs-direction', 'left');
    },
});
```

---

## 8. RTL Layout Patterns — Detailed

### 8.1 Navigation Menu

```scss
// RTL navigation fixes
[dir="rtl"] {
    .navbar-collapse {
        // On mobile, menu should still flow correctly
        text-align: right;
    }

    .navbar-nav .dropdown-menu {
        // Dropdown should open to the left in RTL
        left: auto;
        right: 0;
    }

    .navbar-nav .nav-link {
        // Padding should be on the right for RTL
        padding-right: 0.5rem;
        padding-left: 0.5rem;
    }
}
```

### 8.2 Form Fields

```scss
[dir="rtl"] {
    // Label alignment
    .form-label {
        text-align: right;
        display: block;
    }

    // Required asterisk position
    .form-label::after {
        // Move asterisk to right of label in RTL
    }

    // Input group buttons (search, etc.)
    .input-group .btn:first-child {
        border-radius: 0 var(--bs-border-radius) var(--bs-border-radius) 0;
    }
    .input-group .btn:last-child {
        border-radius: var(--bs-border-radius) 0 0 var(--bs-border-radius);
    }

    // Checkboxes and radios
    .form-check {
        padding-left: 0;
        padding-right: 1.5em;
    }
    .form-check-input {
        float: right;
        margin-left: 0;
        margin-right: -1.5em;
    }
}
```

### 8.3 Tables

```scss
[dir="rtl"] {
    // Table text alignment
    table {
        text-align: right;
    }

    // Sortable column headers
    .o_list_view .o_column_sortable::after {
        margin-left: 0;
        margin-right: 4px;
    }

    // Fixed first column (for action checkboxes)
    td.o_list_record_selector {
        text-align: center;
    }
}
```

### 8.4 Footer Columns

```scss
[dir="rtl"] {
    // Footer columns should naturally reverse in RTL flex container
    // but may need explicit ordering for some layouts
    .footer .row {
        flex-direction: row-reverse;
    }

    // Or use order property for specific columns
    .footer .col-logo { order: 3; }
    .footer .col-links { order: 2; }
    .footer .col-contact { order: 1; }
}
```

### 8.5 Icons and Visual Indicators

```scss
[dir="rtl"] {
    // Font Awesome directional icons
    .fa-angle-left::before { content: "\f105"; }   // Swap: angle-right
    .fa-angle-right::before { content: "\f104"; }  // Swap: angle-left
    .fa-arrow-left::before { content: "\f061"; }   // Swap: arrow-right
    .fa-arrow-right::before { content: "\f060"; }  // Swap: arrow-left
    .fa-caret-left::before { content: "\f0d7"; }   // Swap
    .fa-caret-right::before { content: "\f0d9"; }  // Swap

    // Bootstrap icons
    .bi-chevron-left::before { content: "\F285"; }  // Swap
    .bi-chevron-right::before { content: "\F284"; } // Swap
}
```

---

## 9. Bilingual Patterns (Arabic + English)

### 9.1 Side-by-Side Layout

```xml
<!-- Side-by-side Arabic/English layout -->
<div class="bilingual-section">
    <div class="row align-items-center">
        <!-- Arabic content (right side) -->
        <div class="col-md-6 text-ar" dir="rtl" lang="ar">
            <h2>مرحباً بكم</h2>
            <p>نحن نقدم خدمات متميزة في مجال التقنية.</p>
        </div>
        <!-- English content (left side) -->
        <div class="col-md-6 text-en" dir="ltr" lang="en">
            <h2>Welcome</h2>
            <p>We provide excellent technology services.</p>
        </div>
    </div>
</div>
```

### 9.2 Dual-Language Field Display

```xml
<!-- In Odoo backend views — show both name and name_ar -->
<form string="Product">
    <sheet>
        <group>
            <group string="English">
                <field name="name" string="Name (EN)"/>
            </group>
            <group string="Arabic" attrs="{'invisible': []}">
                <field name="name_ar" string="Name (AR)"
                       options="{'direction': 'rtl'}"/>
            </group>
        </group>
    </sheet>
</form>
```

### 9.3 Language Switcher Widget

```javascript
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.LanguageSwitcher = publicWidget.Widget.extend({
    selector: '.language-switcher',

    events: {
        'click [data-lang]': '_onLanguageClick',
    },

    start: function () {
        // Highlight current language
        const currentLang = document.documentElement.lang || 'en';
        this.$('[data-lang="' + currentLang + '"]').addClass('active');
        return this._super.apply(this, arguments);
    },

    _onLanguageClick: function (ev) {
        ev.preventDefault();
        const lang = $(ev.currentTarget).data('lang');
        const currentUrl = window.location.href;

        // Let Odoo handle language switching via URL
        window.location.href = '/web/set_lang?lang=' + lang +
            '&next=' + encodeURIComponent(currentUrl);
    },
});
```

### 9.4 Arabic Numeral Display

Arabic uses Eastern Arabic numerals (٠١٢٣٤٥٦٧٨٩) vs Western (0123456789):

```scss
// Force Western numerals in Arabic context (recommended for mixed content)
[dir="rtl"] {
    // Use font-feature-settings to control numeral style
    body {
        font-feature-settings: "lnum" 1;  // Use lining numerals
    }

    // For currency/numbers specifically
    .o_field_float, .o_field_monetary {
        direction: ltr;
        unicode-bidi: embed;
        text-align: left;
    }
}
```

```python
# In Python: format numbers respecting locale
from odoo.tools.misc import formatLang

# In template context:
formatted_amount = formatLang(self.env, amount, currency_obj=currency)
```

---

## 10. Translation Completeness

### 10.1 Using the Reporter Script

```bash
# Check translation completeness for a module
python odoo-i18n/scripts/i18n_reporter.py \
    --module /path/to/my_module \
    --lang ar

# Example output:
# Translation Report: my_module (ar)
# =====================================
# Total translatable strings: 247
# Translated: 198 (80.2%)
# Missing: 49 (19.8%)
# Fuzzy: 3
#
# Missing translations:
# [my_module/models/sale_order.py:45] "Order Confirmation"
# [my_module/views/templates.xml:123] "Track Your Order"
# ...
```

### 10.2 Manual Completeness Check

```bash
# Count total msgid entries in .po file
grep -c '^msgid ' my_module/i18n/ar.po

# Count translated entries (non-empty msgstr)
grep -A1 '^msgid ' my_module/i18n/ar.po | grep -v '^msgid\|^--$' | grep -cv '^msgstr ""$'

# Count fuzzy entries
grep -c '#, fuzzy' my_module/i18n/ar.po
```

### 10.3 Odoo Shell — Check Translation Coverage

```python
# Interactive shell
translations = self.env['ir.translation'].search([
    ('module', '=', 'my_module'),
    ('lang', '=', 'ar'),
])
total = len(translations)
translated = len(translations.filtered(lambda t: t.value))
print(f"Translated: {translated}/{total} ({translated/total*100:.1f}%)")
```

---

## 11. Version Differences (Odoo 14–19)

### 11.1 Odoo 14

- Uses `ir.translation` model for all translations
- `_()` imports from `odoo` — same as later versions
- JavaScript: uses `web.core` import for `_t`
- No native Bootstrap RTL support — manual CSS needed
- Translation extraction: basic .po file generation

### 11.2 Odoo 15

- Same as v14 for i18n core
- Improved translation export performance
- Added support for inline translations in website builder

### 11.3 Odoo 16

- Major change: Bootstrap 5.1.3 with native RTL support
- Bootstrap RTL CSS (`bootstrap.rtl.min.css`) now included
- Improved `_t()` in new Owl framework components
- Translation model consolidation begins
- Website language detection improved

### 11.4 Odoo 17

- `ir.translation` → deprecated/replaced by `ir.model.fields.selection` for selection fields
- Term-based translations (JSON) for improved performance
- New `_t()` import: `from "@web/core/l10n/translation"` in owl components
- Website RTL: automatic `dir="rtl"` on `<html>` based on active language
- Better pluralization support

### 11.5 Odoo 18

- Further consolidation of translation storage
- Improved translation export/import with better conflict resolution
- Enhanced RTL support in kanban/list views
- Better support for RTL in PDF reports (wkhtmltopdf RTL)

### 11.6 Odoo 19

- Modern translation framework with lazy loading
- WebAssembly-based .mo compilation (performance)
- Improved Arabic shaping support in reports
- Native support for mixed-direction content
- REST API endpoints for translation management

---

## 12. Common Pitfalls

### 12.1 String Concatenation

```python
# WRONG: Translator sees two separate strings, loses context
msg = _('Record') + ' ' + record.name + ' ' + _('not found')

# CORRECT: Give translator the full sentence with placeholder
msg = _('Record "%s" not found') % record.name
```

### 12.2 f-Strings Inside `_()`

```python
# WRONG: String is interpolated before _() processes it — translator gets nothing
error = _(f'Invoice {invoice.name} is overdue by {days} days')

# CORRECT: Use % formatting
error = _('Invoice %(name)s is overdue by %(days)d days') % {
    'name': invoice.name,
    'days': days,
}
```

### 12.3 Pluralization

```python
# WRONG: Simple approach that breaks for some languages
if count == 1:
    msg = _('1 record found')
else:
    msg = _('%d records found') % count

# BETTER: Use a single translatable string with ngettext equivalent
# Odoo doesn't have a built-in ngettext, but you can handle it:
if count == 1:
    msg = _('One record found')
else:
    msg = _('%d records found') % count

# For Arabic (6 plural forms), you may need language-specific handling
```

### 12.4 Context in Translations

Sometimes the same word needs different translations based on context. Odoo supports translation context via the `ir.translation` model and the `_()` function's optional comment parameter.

### 12.5 Missing `i18n/` Directory

If the `i18n/` directory doesn't exist, Odoo silently skips translation loading. Always create it even if initially empty.

### 12.6 Wrong File Encoding

.po files MUST be UTF-8. Other encodings cause silent failures:

```bash
# Check encoding
file -i my_module/i18n/ar.po
# Should show: text/plain; charset=utf-8

# Convert if needed
iconv -f ISO-8859-1 -t UTF-8 ar.po > ar_utf8.po
```

### 12.7 Stale Translations in Cache

After updating .po files, Odoo may serve cached translations. Solutions:
- Update the module: `python -m odoo -c conf.conf -d db -u my_module --stop-after-init`
- Restart the server
- Clear browser cache (Ctrl+Shift+R)
- In shell: `self.env['ir.translation'].clear_caches()`

### 12.8 Website Builder Overriding Translations

When using the Odoo website builder, inline edits create database-level translations that override `.po` file translations. To reset:

```python
# Shell: Remove website-level translation overrides for a specific language
self.env['ir.translation'].search([
    ('lang', '=', 'ar'),
    ('module', 'like', 'website'),
    ('src', '=', 'original text'),
]).unlink()
self.env.cr.commit()
```

---

## 13. Lazy Translation — When to Use `_lt()` vs `_()`

### When to Use `_()`

- Inside functions, methods, and request handlers (runtime context)
- When request environment (user, language) is available
- In `@api.constrains`, `@api.onchange`, action methods

```python
def action_confirm(self):
    for rec in self:
        if not rec.partner_id:
            raise UserError(_('Partner is required to confirm.'))
```

### When to Use `_lt()`

- Class-level definitions (executed at module import time)
- Selection field values
- Static error messages defined at class level
- When no request context is available

```python
from odoo.tools.translate import _lt

class PurchaseOrder(models.Model):
    _name = 'purchase.order'

    # _lt() because this is evaluated at class definition time
    state = fields.Selection([
        ('draft', _lt('Draft RFQ')),
        ('sent', _lt('RFQ Sent')),
        ('purchase', _lt('Purchase Order')),
        ('done', _lt('Locked')),
        ('cancel', _lt('Cancelled')),
    ], string='Status', default='draft')

    # Exception messages as class constants — use _lt()
    _LOCK_ERROR = _lt('Purchase Order is locked and cannot be modified.')
```

---

## 14. Module-Specific Patterns

### 14.1 Website Module

```python
# Website controllers — _() works in request context
from odoo import http, _
from odoo.http import request

class WebsiteController(http.Controller):
    @http.route('/shop', auth='public', website=True)
    def shop(self, **kwargs):
        title = _('Our Products')  # Works fine in request context
        return request.render('my_module.shop_template', {
            'title': title,
        })
```

```xml
<!-- Website templates — text is translatable by default -->
<template id="shop_template">
    <t t-call="website.layout">
        <div id="wrap">
            <!-- This text IS extracted and translated -->
            <h1>Our Products</h1>
            <p>Browse our complete catalog below.</p>

            <!-- Dynamic content from controller -->
            <h2 t-esc="title"/>
        </div>
    </t>
</template>
```

### 14.2 Mail Templates

```xml
<!-- Email templates use translation system -->
<record id="email_template_order" model="mail.template">
    <field name="name">Order Confirmation</field>
    <field name="model_id" ref="model_sale_order"/>
    <field name="subject">Order ${object.name} Confirmed</field>
    <!-- Body is translatable via website translation system -->
    <field name="body_html"><![CDATA[
        <div>
            <p>Dear ${object.partner_id.name},</p>
            <p>Your order ${object.name} has been confirmed.</p>
        </div>
    ]]></field>
    <field name="lang">${object.partner_id.lang}</field>
</record>
```

Note the `lang` field — Odoo uses the partner's language to translate the email template, allowing automatic multilingual emails.

### 14.3 QWeb Report Translations

```python
# In report controller
class MyReportController(models.AbstractModel):
    _name = 'report.my_module.my_report'
    _description = 'My Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'docs': self.env['my.model'].browse(docids),
            'doc_model': 'my.model',
            # These strings will be translated in the report context
            'report_labels': {
                'title': _('Sales Report'),
                'date': _('Date'),
                'total': _('Total'),
            }
        }
```

### 14.4 Scheduled Actions (Cron)

```python
@api.model
def _cron_send_reminders(self):
    # In cron jobs, use sudo() and set language context
    for partner in self.env['res.partner'].search([('active', '=', True)]):
        lang = partner.lang or 'en_US'
        # Translate using partner's language
        with self.env.cr.savepoint():
            translated_msg = self.with_context(lang=lang).env[
                'ir.translation'
            ]._get_source('my_module', 'reminder_message', lang)
```

---

## 15. Commands Reference

The plugin provides these slash commands:

| Command | Description |
|---------|-------------|
| `/odoo-i18n` | Main i18n help and overview |
| `/i18n-extract` | Extract translatable strings from a module |
| `/i18n-missing` | Find missing translations |
| `/i18n-validate` | Validate .po file syntax and completeness |
| `/i18n-export` | Export translations using Odoo CLI |

---

## 16. Script Usage Reference

### i18n_extractor.py

```bash
python odoo-i18n/scripts/i18n_extractor.py --module /path/to/module --lang ar
python odoo-i18n/scripts/i18n_extractor.py --module /path/to/module --lang fr --output /custom/output/
```

### i18n_validator.py

```bash
python odoo-i18n/scripts/i18n_validator.py --po-file /path/to/ar.po
python odoo-i18n/scripts/i18n_validator.py --po-file /path/to/ar.po --strict
```

### i18n_reporter.py

```bash
python odoo-i18n/scripts/i18n_reporter.py --module /path/to/module --lang ar
python odoo-i18n/scripts/i18n_reporter.py --module /path/to/module --lang ar --format json
```

### i18n_converter.py

```bash
python odoo-i18n/scripts/i18n_converter.py --action merge --base ar.po --new ar_new.po --output ar_merged.po
python odoo-i18n/scripts/i18n_converter.py --action clean --po ar.po
python odoo-i18n/scripts/i18n_converter.py --action stats --po ar.po
```

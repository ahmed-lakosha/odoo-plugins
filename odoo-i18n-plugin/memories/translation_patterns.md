# Odoo Translation Patterns — Reference Memory

This memory file contains production-ready patterns for implementing internationalization (i18n) in Odoo modules. Refer to this when writing or reviewing code that needs translation support.

---

## Python Translation Patterns

### Standard Import

```python
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _lt  # For class-level strings
```

### Simple String Translation

```python
class MyModel(models.Model):
    _name = 'my.model'

    def action_confirm(self):
        for rec in self:
            if not rec.partner_id:
                # CORRECT: Literal string inside _()
                raise UserError(_('A partner is required to confirm this record.'))
```

### String Interpolation — The Right Way

```python
# CORRECT: Use % with variables OUTSIDE _()
raise UserError(_('Record "%s" cannot be deleted.') % record.name)

# CORRECT: Named placeholders (preferred for readability and RTL clarity)
raise UserError(_('Invoice %(number)s is overdue by %(days)d days.') % {
    'number': invoice.name,
    'days': overdue_days,
})

# CORRECT: Multiple positional
raise UserError(_('Expected %s but got %s.') % (expected, got))

# CORRECT: .format() — acceptable but less common in Odoo
raise UserError(_('Hello {}! You have {} messages.').format(user.name, count))

# WRONG: f-strings break extraction — extractor sees the interpolated value
raise UserError(_(f'Invoice {invoice.name} is overdue'))  # NEVER DO THIS

# WRONG: String concatenation — translator loses sentence context
msg = _('Invoice ') + invoice.name + _(' is overdue')  # NEVER DO THIS

# WRONG: Variable passed to _() — extractor cannot find the string
msg_template = 'Something went wrong'
raise UserError(_(msg_template))  # Technically works but defeats i18n
```

### Lazy Translation for Class-Level Strings

```python
from odoo.tools.translate import _lt

class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _description = 'Purchase Order'  # DO NOT wrap in _() — it's auto-translated

    # CORRECT: Use _lt() for selection values (defined at class load time)
    STATE_SELECTION = [
        ('draft', _lt('Draft RFQ')),
        ('sent', _lt('RFQ Sent')),
        ('to_approve', _lt('To Approve')),
        ('purchase', _lt('Purchase Order')),
        ('done', _lt('Locked')),
        ('cancel', _lt('Cancelled')),
    ]

    state = fields.Selection(
        selection=STATE_SELECTION,
        string='Status',
        default='draft',
    )

    # CORRECT: Use _lt() for class-level constant messages
    _APPROVE_ERROR = _lt('You do not have permission to approve this order.')

    # Field string= and help= are auto-translated — DO NOT wrap in _() or _lt()
    date_order = fields.Date(
        string='Order Date',
        help='The date the purchase order was confirmed.',
    )
```

### Translation in `@api.constrains`

```python
@api.constrains('amount_total', 'currency_id')
def _check_positive_amount(self):
    for rec in self:
        if rec.amount_total < 0:
            # _() works inside methods — request context is available
            raise ValidationError(
                _('Total amount cannot be negative. Current value: %s') % rec.amount_total
            )
```

### Translation in Cron Jobs (No Request Context)

```python
@api.model
def _cron_send_reminders(self):
    # In cron, we may need to use different languages per partner
    partners = self.env['res.partner'].search([('email', '!=', False)])
    for partner in partners:
        # Use partner's language when generating messages
        lang = partner.lang or 'en_US'
        partner_env = self.env(context=dict(self.env.context, lang=lang))
        subject = partner_env['my.model']._get_reminder_subject()
        self._send_email(partner, subject)

@api.model
def _get_reminder_subject(self):
    # This will use whatever lang is in context
    return _('Reminder: Your subscription expires soon')
```

### Translation in Email Templates (Python)

```python
def send_confirmation_email(self):
    for rec in self:
        # Use partner's language for email content
        lang = rec.partner_id.lang or 'en_US'
        with self.env.cr.savepoint():
            env = self.env(context=dict(self.env.context, lang=lang))
            subject = env['my.model'].browse(rec.id)._get_subject()
            body = env['my.model'].browse(rec.id)._get_body()

        rec.message_post(
            subject=subject,
            body=body,
            partner_ids=[rec.partner_id.id],
        )

def _get_subject(self):
    return _('Your order %(ref)s has been confirmed') % {'ref': self.name}

def _get_body(self):
    return _('Dear %(name)s, your order is ready for pickup.') % {
        'name': self.partner_id.name
    }
```

### Model Name Translation

```python
class MyModel(models.Model):
    _name = 'my.model'
    # _description is translated automatically by Odoo — DO NOT add _()
    _description = 'My Model'
    _rec_name = 'name'

    # All these field attributes are auto-translated — DO NOT add _()
    name = fields.Char(
        string='Name',
        required=True,
        help='The display name of this record.',
    )
    state = fields.Selection(
        string='Status',
        selection=[
            ('draft', 'Draft'),        # These get translated via ir.translation
            ('confirmed', 'Confirmed'),
        ],
        default='draft',
    )
    note = fields.Html(
        string='Notes',
        help='Additional notes. Supports formatted text.',
        sanitize=True,
    )
```

---

## XML Translation Patterns

### View Field String Attributes

```xml
<odoo>
    <record id="view_my_model_form" model="ir.ui.view">
        <field name="name">my.model.form</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <!-- string= attributes are AUTOMATICALLY translated -->
            <form string="My Record">
                <sheet>
                    <group string="General Information">
                        <field name="name" string="Name"/>
                        <field name="partner_id" string="Partner"/>
                        <field name="date" string="Date"/>
                    </group>
                    <group string="Financial Details">
                        <field name="amount" string="Amount"/>
                        <field name="currency_id" string="Currency"/>
                    </group>
                </sheet>
                <footer>
                    <!-- Button text is also auto-translated -->
                    <button string="Confirm" type="object" name="action_confirm"/>
                    <button string="Cancel" class="btn-secondary"/>
                </footer>
            </form>
        </field>
    </record>
</odoo>
```

### List View with Headers

```xml
<record id="view_my_model_list" model="ir.ui.view">
    <field name="name">my.model.list</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <list string="My Records">
            <!-- Column headers come from field string= -->
            <field name="name" string="Name"/>
            <field name="partner_id" string="Customer"/>
            <field name="amount" string="Amount" sum="Total"/>
            <field name="state" string="Status"/>
        </list>
    </field>
</record>
```

### QWeb Website Template Text

```xml
<!-- Text nodes in website templates are translatable -->
<template id="page_about" name="About Us">
    <t t-call="website.layout">
        <div id="wrap">
            <section class="hero">
                <!-- These text nodes will appear in .po extraction -->
                <h1>About Our Company</h1>
                <p>We have been serving clients since 2010.</p>
            </section>

            <!-- Use t-field for model data (auto-formatted + translated) -->
            <div class="company-info">
                <span t-field="company.name"/>
                <span t-field="company.website"/>
            </div>

            <!-- t-esc for simple values -->
            <p>Contact: <span t-esc="company.email"/></p>

            <!-- Disable translation for technical content -->
            <pre t-translation="off">
                <t t-esc="technical_code"/>
            </pre>
        </div>
    </t>
</template>
```

### QWeb Report Headers (Translatable)

```xml
<template id="report_invoice">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <!-- Text in reports IS translatable -->
                    <h2>Tax Invoice</h2>
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <!-- Column headers ARE translatable -->
                                <th>Description</th>
                                <th class="text-end">Qty</th>
                                <th class="text-end">Unit Price</th>
                                <th class="text-end">Tax</th>
                                <th class="text-end">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-foreach="doc.invoice_line_ids" t-as="line">
                                <tr>
                                    <td><t t-field="line.name"/></td>
                                    <td class="text-end"><t t-field="line.quantity"/></td>
                                    <td class="text-end"><t t-field="line.price_unit"/></td>
                                    <td class="text-end"><t t-field="line.tax_ids" options="{'widget': 'many2many_tags'}"/></td>
                                    <td class="text-end"><t t-field="line.price_subtotal"/></td>
                                </tr>
                            </t>
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colspan="4" class="text-end fw-bold">Total</td>
                                <td class="text-end fw-bold"><t t-field="doc.amount_total"/></td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </t>
        </t>
    </t>
</template>
```

### Email Template with Partner Language

```xml
<record id="email_template_order_confirm" model="mail.template">
    <field name="name">Order: Confirmation</field>
    <field name="model_id" ref="sale.model_sale_order"/>
    <!-- ${...} expressions are evaluated server-side, not translated here -->
    <field name="subject">Order ${object.name} Confirmed</field>
    <field name="body_html" type="html">
        <div>
            <p>Dear ${object.partner_id.name},</p>
            <!-- Text in email templates IS translatable via ir.translation -->
            <p>Your order has been confirmed and is being processed.</p>
            <p>Order Reference: <strong>${object.name}</strong></p>
            <p>Thank you for your business.</p>
        </div>
    </field>
    <!-- This ensures email is sent in partner's language -->
    <field name="lang">${object.partner_id.lang}</field>
</record>
```

### Menu Items

```xml
<!-- Menu item name= is automatically translated -->
<menuitem
    id="menu_my_module_root"
    name="My Module"
    sequence="10"
    web_icon="my_module,static/description/icon.png"
/>
<menuitem
    id="menu_my_module_records"
    name="Records"
    parent="menu_my_module_root"
    action="action_my_records"
    sequence="1"
/>
```

---

## JavaScript Translation Patterns

### Odoo 16+ / 17 / 18 / 19 (Owl Components)

```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.notification = useService("notification");
        // Static strings CAN be defined in setup() — context is available
        this.labels = {
            save: _t("Save"),
            cancel: _t("Cancel"),
            delete: _t("Delete"),
            confirm: _t("Are you sure?"),
        };
    }

    onSave() {
        // Dynamic translation with variable
        const msg = _t("Record saved successfully.");
        this.notification.add(msg, { type: "success" });
    }

    onError(errorCode) {
        // Use .replace() for variable substitution
        const msg = _t("Error code: %s").replace("%s", errorCode);
        this.notification.add(msg, { type: "danger" });
    }
}
```

### Odoo 14/15 Legacy (publicWidget)

```javascript
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";

publicWidget.registry.MyFormWidget = publicWidget.Widget.extend({
    selector: '.my-form-container',
    disabledInEditableMode: false,

    events: {
        'submit form': '_onFormSubmit',
        'click .btn-reset': '_onReset',
    },

    start: function () {
        this._super.apply(this, arguments);
        if (!this.editableMode) {
            this._setupValidation();
        }
    },

    _setupValidation: function () {
        const requiredMsg = _t("This field is required.");
        const emailMsg = _t("Please enter a valid email address.");

        // Set placeholder translations
        this.$('input[name="name"]').attr('placeholder', _t("Your full name"));
        this.$('input[name="email"]').attr('placeholder', _t("Your email address"));
        this.$('textarea[name="message"]').attr('placeholder', _t("Your message..."));
    },

    _onFormSubmit: function (ev) {
        ev.preventDefault();

        // Validate
        const name = this.$('input[name="name"]').val().trim();
        if (!name) {
            this._showError(_t("Name is required."));
            return;
        }

        // Submit logic...
        this._showSuccess(_t("Your message has been sent successfully."));
    },

    _onReset: function (ev) {
        ev.preventDefault();
        const confirmMsg = _t("Are you sure you want to clear the form?");
        if (window.confirm(confirmMsg)) {
            this.$('form')[0].reset();
        }
    },

    _showError: function (msg) {
        this.$('.form-error').text(msg).removeClass('d-none');
    },

    _showSuccess: function (msg) {
        this.$('.form-success').text(msg).removeClass('d-none');
        this.$('.form-error').addClass('d-none');
    },

    destroy: function () {
        this._super.apply(this, arguments);
    },
});
```

### Strings That CANNOT Be Extracted

```javascript
// WRONG: Variable inside _t() — extractor only finds literals
const key = 'Save';
const translated = _t(key);  // Extractor cannot find 'Save' here

// WRONG: Template literal — f-string equivalent, not extractable
const name = 'Ahmed';
const msg = _t(`Hello ${name}!`);  // NEVER use template literals in _t()

// WRONG: Concatenation inside _t()
const fullMsg = _t('Hello ' + name + '!');  // Never concatenate inside _t()

// CORRECT patterns only:
const msg1 = _t("Hello World");  // Literal — extractable
const msg2 = _t("Hello %s!").replace('%s', name);  // Substitution outside
```

---

## .po File Patterns

### Correct Header

```po
# Arabic translation of my_module
# Copyright (C) 2024 TaqaTechno
# Translator: Ahmed Al-Rashidi <ahmed@taqatechno.com>, 2024
#
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 17.0\n"
"Report-Msgid-Bugs-To: contact@taqatechno.com\n"
"POT-Creation-Date: 2024-01-15 10:00+0300\n"
"PO-Revision-Date: 2024-02-01 14:30+0300\n"
"Last-Translator: Ahmed Al-Rashidi <ahmed@taqatechno.com>\n"
"Language-Team: Arabic <ar@li.org>\n"
"Language: ar\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5;\n"
```

### Entry with Format Specifier

```po
#. module: my_module
#: models/my_model.py:45
#, python-format
msgid "Record \"%s\" not found"
msgstr "السجل \"%s\" غير موجود"
```

### Entry with Named Placeholder

```po
#. module: my_module
#: models/my_model.py:89
#, python-format
msgid "Invoice %(number)s is overdue by %(days)d days"
msgstr "الفاتورة %(number)s متأخرة بـ %(days)d أيام"
```

### Multiline Entry

```po
#: views/templates.xml:23
msgid ""
"Welcome to our online store.\n"
"Browse our products and place your order."
msgstr ""
"مرحباً بكم في متجرنا الإلكتروني.\n"
"تصفح منتجاتنا وقم بطلبك."
```

---

## Critical Rules Summary

1. **NEVER** use f-strings inside `_()` — use `%` formatting instead
2. **NEVER** concatenate strings inside `_()` — give translator the full sentence
3. **ALWAYS** use `_lt()` for class-level string definitions (selection values, etc.)
4. **NEVER** wrap `string=` attributes in `_()` — they are auto-translated
5. **ALWAYS** save `.po` files as UTF-8 without BOM
6. **ALWAYS** update the module after editing `.po` files
7. **ALWAYS** check format specifiers (`%s`, `%(name)s`) match in msgid and msgstr
8. **Arabic** `.po` files must have `nplurals=6` in the Plural-Forms header

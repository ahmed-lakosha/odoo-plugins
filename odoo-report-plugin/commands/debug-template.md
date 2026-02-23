---
title: 'Debug Template'
read_only: true
type: 'command'
description: 'Debug email template or QWeb report rendering issues with detailed diagnostics'
---

# Debug Template

Debug email template or QWeb report rendering issues with **detailed diagnostics**, **context inspection**, and **step-by-step rendering trace**.

## Usage

```
/debug-template [template-id] [record-id]
/debug-template sale.email_template_edi_sale 42
/debug-template --file projects/module/data/template.xml --record 123
```

### Natural Language

```
"Debug why my email template is failing"
"Why isn't the invoice template rendering correctly?"
"Help me fix the template error for order #42"
```

## Debug Process

### Step 1: Identify Template and Record

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEBUG INITIALIZATION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Template: sale.email_template_edi_sale                          │
│  Model: sale.order                                               │
│  Record ID: 42                                                   │
│                                                                   │
│  Checking:                                                       │
│  [ ] Template exists                                             │
│  [ ] Record exists                                               │
│  [ ] Record is accessible (permissions)                          │
│  [ ] Template model matches record model                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Step 2: Context Inspection

```python
# Debug script to run in Odoo shell
template = env['mail.template'].browse(TEMPLATE_ID)
record = env['sale.order'].browse(42)

# Check rendering context
render_context = template._render_eval_context()
print("Available context variables:")
for key in render_context:
    print(f"  - {key}: {type(render_context[key])}")

# Output:
# Available context variables:
#   - object: <class 'sale.order'>
#   - user: <class 'res.users'>
#   - ctx: <class 'dict'>
#   - format_amount: <class 'function'>
#   - format_date: <class 'function'>
#   - format_datetime: <class 'function'>
#   - is_html_empty: <class 'function'>
```

### Step 3: Field-by-Field Rendering

```
┌─────────────────────────────────────────────────────────────────┐
│                  FIELD RENDERING TRACE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Field: subject                                                  │
│  Expression: {{ object.name }} - Quotation                       │
│  Engine: inline_template                                         │
│  Result: "SO042 - Quotation"                                     │
│  Status: OK                                                      │
│                                                                   │
│  ────────────────────────────────────────────────────────────── │
│                                                                   │
│  Field: email_from                                               │
│  Expression: {{ (object.user_id.email or user.email) }}          │
│  Engine: inline_template                                         │
│  Result: "john@company.com"                                      │
│  Status: OK                                                      │
│                                                                   │
│  ────────────────────────────────────────────────────────────── │
│                                                                   │
│  Field: body_html                                                │
│  Engine: qweb                                                    │
│  Status: ERROR at line 15                                        │
│                                                                   │
│  Error: AttributeError: 'NoneType' object has no attribute       │
│         'name'                                                   │
│                                                                   │
│  Problematic code:                                               │
│  Line 15: <t t-out="object.partner_id.contact_id.name"/>         │
│                                                                   │
│  Debug info:                                                     │
│  - object.partner_id = res.partner(123,)                         │
│  - object.partner_id.contact_id = None                           │
│                                                                   │
│  Suggestion:                                                     │
│  Use: object.partner_id.contact_id.name if                       │
│       object.partner_id.contact_id else ''                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Step 4: Common Error Diagnosis

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMMON ERROR PATTERNS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  AttributeError: 'NoneType' has no attribute 'xxx'               │
│  → Missing null check for related field                          │
│  → Fix: Add "or ''" or use t-if guard                           │
│                                                                   │
│  KeyError: 'format_amount'                                       │
│  → Context helper not available                                  │
│  → Fix: Ensure mail.render.mixin is inherited                    │
│                                                                   │
│  QWebException: t-esc is deprecated                              │
│  → Using old syntax in Odoo 15+                                  │
│  → Fix: Replace t-esc with t-out                                 │
│                                                                   │
│  ValidationError: Invalid template                               │
│  → Malformed XML or QWeb                                         │
│  → Fix: Check tag closure, attribute quotes                      │
│                                                                   │
│  NameError: name 'object' is not defined                         │
│  → Wrong rendering context                                       │
│  → Fix: Use correct model reference                              │
│                                                                   │
│  UnicodeDecodeError                                               │
│  → Encoding issues in template                                   │
│  → Fix: Ensure UTF-8 encoding, escape special chars              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Debug Shell Commands

Claude provides shell commands to help debug:

```python
# Odoo Shell Debug Commands

# 1. Get template and record
template = env['mail.template'].search([('name', 'ilike', 'quotation')])[0]
record = env['sale.order'].browse(42)

# 2. Check template fields
print(f"Subject: {template.subject}")
print(f"Email From: {template.email_from}")
print(f"Model: {template.model}")

# 3. Test inline_template rendering (subject, email fields)
from odoo.addons.mail.models.mail_render_mixin import MailRenderMixin
result = template._render_field('subject', [record.id])
print(f"Rendered subject: {result[record.id]}")

# 4. Test body_html rendering
result = template._render_field('body_html', [record.id], compute_lang=True)
print(f"Rendered body preview: {result[record.id][:500]}...")

# 5. Check for errors
try:
    template.send_mail(record.id, raise_exception=True)
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

# 6. Inspect render context
ctx = template._render_eval_context()
print("Context keys:", list(ctx.keys()))

# 7. Test specific expression
from odoo.tools import safe_eval
expr = "object.partner_id.name or 'Unknown'"
result = safe_eval(expr, {'object': record})
print(f"Expression result: {result}")
```

## Example Flows

### Example 1: NoneType Error

**User**: "Debug template error: AttributeError: 'NoneType' object has no attribute 'name'"

**Claude**:
```
Analyzing error pattern: NoneType attribute access

This error occurs when accessing a field on a None value.

Common causes:
1. Related record doesn't exist (partner_id.contact_id is None)
2. Optional field not set (user_id is False)
3. Filtered recordset is empty

Debugging steps:

1. Identify the line causing the error
2. Check each part of the chain:

   object.partner_id         → res.partner(123,) ✓
   object.partner_id.contact_id  → None ✗

3. The fix:

   BEFORE: <t t-out="object.partner_id.contact_id.name"/>

   AFTER:  <t t-if="object.partner_id.contact_id">
               <t t-out="object.partner_id.contact_id.name"/>
           </t>

   OR:     <t t-out="object.partner_id.contact_id.name if object.partner_id.contact_id else ''"/>
```

### Example 2: Format Function Not Found

**User**: "Getting KeyError: 'format_amount' in my template"

**Claude**:
```
Error: format_amount helper function not found in rendering context.

This usually means:
1. Template model doesn't inherit mail.render.mixin
2. Custom template bypassing standard rendering

Solution:

Check your template model inherits the mixin:

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Includes mail.render.mixin

If using custom rendering, add helpers to context:

def _my_render_method(self):
    return self.env['ir.qweb']._render(
        'my.template',
        {
            'object': self,
            'format_amount': lambda amount, currency: formatLang(
                self.env, amount, currency_obj=currency
            ),
            'format_date': lambda date: format_date(self.env, date),
        }
    )
```

### Example 3: XML Parsing Error

**User**: "Template won't load: XMLSyntaxError"

**Claude**:
```
XML Syntax Error detected.

Common XML issues to check:

1. Unclosed tags:
   BAD:  <div><span>text</div>
   GOOD: <div><span>text</span></div>

2. Unescaped special characters:
   BAD:  <p>Price < $100 & tax</p>
   GOOD: <p>Price &lt; $100 &amp; tax</p>

3. Unquoted attributes:
   BAD:  <div class=container>
   GOOD: <div class="container">

4. Invalid XML in body_html:
   BAD:  <field name="body_html"><div>...</field>
   GOOD: <field name="body_html" type="html"><div>...</div></field>

5. Missing XML declaration encoding:
   GOOD: <?xml version="1.0" encoding="UTF-8"?>

Running XML validator on your template...
```

## Debug Output Report

```
════════════════════════════════════════════════════════════════════
                    TEMPLATE DEBUG REPORT
════════════════════════════════════════════════════════════════════

Template: my_module.email_template_custom
Model: sale.order
Record: SO042 (id: 42)
Timestamp: 2026-01-12 10:30:45

────────────────────────────────────────────────────────────────────
RENDERING RESULTS
────────────────────────────────────────────────────────────────────

subject:     SUCCESS  "SO042 - Quotation"
email_from:  SUCCESS  "sales@company.com"
email_to:    SUCCESS  "customer@email.com"
body_html:   FAILED   Line 15

────────────────────────────────────────────────────────────────────
ERROR DETAILS
────────────────────────────────────────────────────────────────────

Type: AttributeError
Message: 'NoneType' object has no attribute 'name'
Location: body_html, line 15

Code context:
   13 | <p>Your salesperson:</p>
   14 | <p>
>> 15 | <t t-out="object.user_id.partner_id.name"/>
   16 | </p>

Variable state at error:
  object.user_id = res.users(2,)
  object.user_id.partner_id = res.partner(,)  ← EMPTY!

────────────────────────────────────────────────────────────────────
SUGGESTED FIX
────────────────────────────────────────────────────────────────────

Replace line 15 with:

<t t-if="object.user_id and object.user_id.partner_id">
    <t t-out="object.user_id.partner_id.name"/>
</t>
<t t-else="">
    <t t-out="object.user_id.name or 'Your Sales Team'"/>
</t>

════════════════════════════════════════════════════════════════════
```

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                DEBUG TEMPLATE QUICK REFERENCE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  SHELL COMMANDS:                                                 │
│  python odoo-bin shell -d DATABASE                               │
│  >>> template = env['mail.template'].browse(ID)                  │
│  >>> record = env['model'].browse(RECORD_ID)                     │
│  >>> template._render_field('body_html', [record.id])            │
│                                                                   │
│  COMMON ERRORS:                                                  │
│  • NoneType → Add null checks                                    │
│  • KeyError → Check context helpers                              │
│  • XMLSyntaxError → Fix XML structure                            │
│  • UnicodeError → Check encoding                                 │
│                                                                   │
│  DEBUG FLAGS:                                                    │
│  --dev=all → Detailed error messages                             │
│  --log-level=debug → Full logging                                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Related Commands

| Command | Description |
|---------|-------------|
| `/analyze-template` | Full template analysis |
| `/fix-template` | Auto-fix common issues |
| `/preview-template` | Preview rendered output |

---

*Part of Odoo Report Plugin v1.0*
*Template Debugging & Diagnostics*

# /odoo-i18n — Odoo Internationalization Help

Provides an overview of the Odoo i18n toolkit and guides you to the right sub-command for your task.

## What This Plugin Does

The `odoo-i18n` plugin is a comprehensive Odoo internationalization (i18n) toolkit. It helps you:

1. **Extract** translatable strings from Python, XML, and JavaScript files into `.pot`/`.po` files
2. **Find missing** translations by comparing source strings against existing `.po` files
3. **Validate** `.po` files for syntax errors, encoding issues, and Arabic-specific problems
4. **Export/import** translations using Odoo's built-in CLI commands
5. **Manage RTL layouts** for Arabic and other right-to-left languages

---

## Available Commands

| Command | Description |
|---------|-------------|
| `/i18n-extract` | Extract all translatable strings from a module and generate `.pot`/`.po` files |
| `/i18n-missing` | Report which strings are missing translations for a given language |
| `/i18n-validate` | Validate a `.po` file for errors, encoding issues, and Arabic-specific problems |
| `/i18n-export` | Export/import translations using Odoo's built-in CLI |
| `/odoo-i18n` | This help page |

---

## Quick Start Guide

### Step 1: Extract strings from your module

```bash
python odoo-i18n/scripts/i18n_extractor.py \
    --module /path/to/my_module \
    --lang ar
```

This creates:
- `my_module/i18n/my_module.pot` — the template with all source strings
- `my_module/i18n/ar.po` — empty Arabic translation file ready to fill in

### Step 2: Translate the strings

Open `my_module/i18n/ar.po` in a text editor or PO editor (Poedit, Virtaal, etc.) and fill in the `msgstr` entries.

### Step 3: Validate your translations

```bash
python odoo-i18n/scripts/i18n_validator.py \
    --po-file /path/to/my_module/i18n/ar.po \
    --lang ar
```

### Step 4: Check coverage

```bash
python odoo-i18n/scripts/i18n_reporter.py \
    --module /path/to/my_module \
    --lang ar
```

### Step 5: Load translations into Odoo

```bash
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    -u my_module \
    --stop-after-init
```

---

## Key Concepts

### .po File Structure

```po
# Arabic translation of my_module
msgid ""
msgstr ""
"Language: ar\n"
"Content-Type: text/plain; charset=UTF-8\n"

#: models/my_model.py:45
#, python-format
msgid "Record %s not found"
msgstr "السجل %s غير موجود"
```

### Translation in Python

```python
from odoo import _

# Simple string
raise UserError(_('Name is required'))

# With variable
raise UserError(_('Record "%s" not found') % record.name)

# Lazy (for class-level strings)
from odoo.tools.translate import _lt
state = fields.Selection([('draft', _lt('Draft'))])
```

### Translation in JavaScript (Odoo 16+)

```javascript
import { _t } from "@web/core/l10n/translation";
const msg = _t("Hello World");
```

### Translation in XML

```xml
<!-- Attribute strings are auto-translated -->
<field name="state" string="Status"/>

<!-- Text in templates is auto-translated -->
<h1>Welcome</h1>
```

---

## Supported Languages

| Code | Language | RTL? |
|------|----------|------|
| `ar` | Arabic | Yes |
| `ar_SA` | Arabic (Saudi Arabia) | Yes |
| `ar_AE` | Arabic (UAE) | Yes |
| `en` / `en_US` | English | No |
| `fr` / `fr_FR` | French | No |
| `tr` | Turkish | No |

---

## Common Issues

**Q: My translations aren't showing up after editing the .po file.**
A: You need to update the module in Odoo: `python -m odoo -c conf.conf -d db -u my_module --stop-after-init`

**Q: The website shows English even when Arabic is active.**
A: Check that (1) the Arabic language is installed in Settings > Languages, (2) the user's language is set to Arabic, (3) the module was updated after adding translations.

**Q: Arabic text appears garbled (mojibake).**
A: The .po file is not saved as UTF-8. Use `/i18n-validate` to detect this, then re-save the file as UTF-8 without BOM.

**Q: My RTL layout is broken.**
A: See the `memories/rtl_patterns.md` file for comprehensive RTL fix patterns, or use `/i18n-validate` which checks for common RTL issues.

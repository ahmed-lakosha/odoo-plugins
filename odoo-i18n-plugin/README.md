# odoo-i18n-plugin

Comprehensive Odoo internationalization (i18n) toolkit for Claude Code. Extract translatable strings, find missing translations, validate `.po` files, and manage Arabic/RTL layouts across Odoo 14 through 19.

**Author**: TaqaTechno
**Version**: 1.0.0
**License**: MIT
**Supported Odoo Versions**: 14, 15, 16, 17, 18, 19
**Primary Languages**: Arabic (ar, ar_SA, ar_AE), English, Turkish, French

---

## What This Plugin Does

| Capability | Description |
|-----------|-------------|
| String Extraction | Scans Python, XML, JS files for `_()`, `string=`, `_t()` calls |
| .po Generation | Creates proper `.pot` templates and language `.po` files |
| Translation Validation | Checks encoding, format specifiers, Arabic-specific issues |
| Coverage Reporting | Shows what % of strings are translated, lists missing ones |
| .po Management | Merge, clean obsolete entries, normalize encoding |
| RTL Guidance | Comprehensive Arabic/RTL layout patterns and fixes |
| Language Reference | Complete table of language codes, formats, timezones |
| CI/CD Integration | Exit codes, JSON output, threshold enforcement |

---

## Installation

### Prerequisites

- Python 3.8+
- Optional: `lxml` for more accurate XML extraction (`pip install lxml`)

### Install the Plugin

```bash
# Copy to your Claude plugins directory
cp -r odoo-i18n-plugin/ ~/.claude/plugins/

# Or install from the Odoo project root
cp -r odoo-i18n-plugin/ /path/to/odoo-project/.claude-plugins/
```

### Verify Installation

```bash
# Test extractor
python odoo-i18n-plugin/odoo-i18n/scripts/i18n_extractor.py --help

# Test validator
python odoo-i18n-plugin/odoo-i18n/scripts/i18n_validator.py --help
```

---

## Quick Start

### 1. Extract translations from a module

```bash
python odoo-i18n/scripts/i18n_extractor.py \
    --module /path/to/my_module \
    --lang ar
```

Creates:
- `my_module/i18n/my_module.pot` — template with all source strings
- `my_module/i18n/ar.po` — empty Arabic translation file

### 2. Translate the strings

Open `my_module/i18n/ar.po` and fill in the `msgstr` entries:

```po
msgid "Save Changes"
msgstr "حفظ التغييرات"

msgid "Record %s not found"
msgstr "السجل %s غير موجود"
```

### 3. Validate the translation file

```bash
python odoo-i18n/scripts/i18n_validator.py \
    --po-file my_module/i18n/ar.po \
    --lang ar
```

### 4. Check coverage

```bash
python odoo-i18n/scripts/i18n_reporter.py \
    --module /path/to/my_module \
    --lang ar
```

### 5. Load into Odoo

```bash
python -m odoo -c conf/myproject.conf \
    -d mydb \
    -u my_module \
    --stop-after-init
```

---

## Available Commands (Slash Commands)

Use these with Claude Code:

| Command | Description |
|---------|-------------|
| `/odoo-i18n` | Overview and help |
| `/i18n-extract` | Extract strings and generate .po files |
| `/i18n-missing` | Report missing translations |
| `/i18n-validate` | Validate a .po file |
| `/i18n-export` | Export/import via Odoo CLI |

---

## Scripts Reference

### i18n_extractor.py

Scans module source files and generates `.pot`/`.po` files.

```bash
# Basic usage
python i18n_extractor.py --module /path/to/module --lang ar

# With custom output directory
python i18n_extractor.py --module /path/to/module --lang fr --output /tmp/

# Without .pot template
python i18n_extractor.py --module /path/to/module --lang tr --no-pot

# Verbose output
python i18n_extractor.py --module /path/to/module --lang ar --verbose
```

**What it extracts:**

| Source | Patterns |
|--------|---------|
| Python | `_('...')`, `_lt('...')` |
| XML | `string="..."`, `help="..."`, `placeholder="..."`, text nodes |
| JavaScript | `_t('...')`, `_lt('...')` |

### i18n_validator.py

Validates a `.po` file for correctness.

```bash
# Basic validation
python i18n_validator.py --po-file ar.po

# With explicit language (enables language-specific checks)
python i18n_validator.py --po-file ar.po --lang ar

# Strict mode (untranslated = error)
python i18n_validator.py --po-file ar.po --strict

# Save report to file
python i18n_validator.py --po-file ar.po --output report.txt
```

**Checks performed:**

| Check | Severity |
|-------|---------|
| UTF-8 encoding | Error |
| Header presence and required fields | Error/Warning |
| Arabic `nplurals=6` | Warning |
| Empty translations | Warning (Error in `--strict`) |
| Fuzzy entries | Warning |
| Format specifier mismatch (`%s`, `%(name)s`) | Error |
| Duplicate msgids | Error |
| Arabic encoding artifacts (mojibake) | Error |
| BIDI override characters | Error |
| Whitespace consistency | Info |

### i18n_reporter.py

Compares source strings against `.po` file and reports coverage.

```bash
# Text report
python i18n_reporter.py --module /path/to/module --lang ar

# JSON report (for CI)
python i18n_reporter.py --module /path/to/module --lang ar --format json

# CSV export of missing strings
python i18n_reporter.py --module /path/to/module --lang ar --format csv --output missing.csv

# Fail if below threshold
python i18n_reporter.py --module /path/to/module --lang ar --min-pct 90.0
```

**Example output:**
```
=================================================================
Translation Report: my_module (ar)
=================================================================
Total strings:    247
Translated:       235 (95.1%)
Missing:          12

Progress:      [========================================] 95.1%

--- Missing Translations ---
  File: models/sale_order.py
    [  45] 'Order Confirmation'
    [ 123] 'Cannot delete'
```

### i18n_converter.py

Merge, clean, analyze, and normalize `.po` files.

```bash
# Merge new strings into existing .po (preserves translations)
python i18n_converter.py --action merge \
    --base ar.po --new ar_new.po --output ar_merged.po

# Remove obsolete entries
python i18n_converter.py --action clean --po ar.po

# View statistics
python i18n_converter.py --action stats --po ar.po

# Normalize encoding and line endings
python i18n_converter.py --action convert --po ar.po --output ar_clean.po
```

---

## Arabic / RTL Support

This plugin has deep Arabic and RTL support. Key patterns are documented in `memories/rtl_patterns.md`.

### Key RTL Principles

1. **Automatic activation**: Odoo sets `dir="rtl"` on `<html>` automatically for Arabic
2. **Bootstrap RTL**: Odoo 16+ auto-loads `bootstrap.rtl.min.css` for RTL languages
3. **CSS logical properties**: Use `margin-inline-start` instead of `margin-left`
4. **Flexbox auto-mirrors**: `flex-direction: row` automatically reverses in RTL
5. **Font Awesome arrows need swapping**: Left/right icon classes must be exchanged

### Quick RTL Setup

```scss
// In your theme's main SCSS file
[dir="rtl"] {
    // Text alignment
    .text-start { text-align: right !important; }
    .text-end { text-align: left !important; }

    // Navigation
    .navbar-nav .dropdown-menu {
        right: 0;
        left: auto;
    }

    // Forms
    .form-label { text-align: right; }
    .form-check {
        padding-left: 0;
        padding-right: 1.5em;
    }
    .form-check-input {
        float: right;
        margin-left: 0;
        margin-right: -1.5em;
    }

    // Directional icons
    .fa-chevron-left::before { content: "\f054"; }
    .fa-chevron-right::before { content: "\f053"; }
    .fa-arrow-left::before { content: "\f061"; }
    .fa-arrow-right::before { content: "\f060"; }
}
```

### RTL Detection in JavaScript

```javascript
/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.MyWidget = publicWidget.Widget.extend({
    selector: '.my-element',
    start: function () {
        // Detect RTL from HTML attribute
        this.isRtl = document.documentElement.getAttribute('dir') === 'rtl';
        if (this.isRtl) {
            this._applyRtlBehavior();
        }
        return this._super.apply(this, arguments);
    },
    _applyRtlBehavior: function () {
        // RTL-specific JS behavior
    },
});
```

---

## Python Translation Quick Reference

```python
from odoo import _
from odoo.tools.translate import _lt

# Simple string
raise UserError(_('Record not found'))

# With variable (CORRECT: % outside _())
raise UserError(_('Record "%s" not found') % record.name)

# Named placeholders (best for RTL — word order may differ)
raise UserError(_('Invoice %(number)s due on %(date)s') % {
    'number': inv.name,
    'date': inv.date,
})

# WRONG: f-string inside _()
raise UserError(_(f'Record {record.name}'))  # NEVER DO THIS

# Lazy translation for class-level strings
state = fields.Selection([
    ('draft', _lt('Draft')),
    ('confirmed', _lt('Confirmed')),
])

# Field strings are auto-translated — no _() needed
name = fields.Char(string='Name', help='Enter the full name.')
```

---

## XML Translation Quick Reference

```xml
<!-- string= attributes are auto-translated -->
<field name="state" string="Status"/>

<!-- Text in website templates is translatable -->
<h1>Welcome to Our Store</h1>
<p>Browse our products below.</p>

<!-- Disable translation for code/technical content -->
<t t-translation="off">
    <code>SELECT * FROM res_partner</code>
</t>

<!-- Dynamic content — t-field uses field widget (best) -->
<span t-field="record.name"/>

<!-- Or t-esc for raw values -->
<span t-esc="record.reference"/>
```

---

## JavaScript Translation Quick Reference

```javascript
/** @odoo-module **/

// Odoo 16+ (Owl framework)
import { _t } from "@web/core/l10n/translation";

// Odoo 14/15 (legacy)
// import { _t } from "web.core";

// Usage
const message = _t("Save Changes");
const error = _t("Record not found: %s").replace('%s', recordName);

// WRONG: never use variables, f-strings, or concatenation inside _t()
const wrong1 = _t(someVariable);        // not extractable
const wrong2 = _t(`Hello ${name}`);     // template literal — broken
const wrong3 = _t('Hello ' + name);     // concatenation — broken
```

---

## Odoo CLI Translation Commands

```bash
# Export translations
python odoo-bin -c conf/myproject.conf -d mydb \
    --i18n-export --modules=my_module --language=ar \
    --output=my_module/i18n/ar.po --stop-after-init

# Import translations
python odoo-bin -c conf/myproject.conf -d mydb \
    --i18n-import=my_module/i18n/ar.po --language=ar \
    --modules=my_module --i18n-overwrite --stop-after-init

# Load language
python odoo-bin -c conf/myproject.conf -d mydb \
    --load-language=ar --stop-after-init

# Update module (reloads translations from .po files)
python -m odoo -c conf/myproject.conf -d mydb \
    -u my_module --stop-after-init
```

---

## CI/CD Integration

```yaml
# GitHub Actions workflow for translation validation
name: Validate Translations

on: [push, pull_request]

jobs:
  validate-i18n:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install lxml

      - name: Validate Arabic translations
        run: |
          python odoo-i18n-plugin/odoo-i18n/scripts/i18n_validator.py \
            --po-file my_module/i18n/ar.po \
            --lang ar \
            --strict

      - name: Check translation coverage (>= 90%)
        run: |
          python odoo-i18n-plugin/odoo-i18n/scripts/i18n_reporter.py \
            --module my_module \
            --lang ar \
            --min-pct 90.0
```

---

## File Structure Reference

```
odoo-i18n-plugin/
├── .claude-plugin/
│   └── plugin.json                    ← Plugin metadata and configuration
├── odoo-i18n/
│   ├── SKILL.md                       ← Main skill documentation (700+ lines)
│   └── scripts/
│       ├── i18n_extractor.py          ← Extract strings → generate .pot/.po
│       ├── i18n_validator.py          ← Validate .po file correctness
│       ├── i18n_reporter.py           ← Translation coverage reports
│       └── i18n_converter.py          ← Merge, clean, stats, convert .po files
├── commands/
│   ├── odoo-i18n.md                   ← /odoo-i18n command
│   ├── i18n-extract.md                ← /i18n-extract command
│   ├── i18n-missing.md                ← /i18n-missing command
│   ├── i18n-validate.md               ← /i18n-validate command
│   └── i18n-export.md                 ← /i18n-export command
├── memories/
│   ├── translation_patterns.md        ← Python/XML/JS translation patterns
│   ├── rtl_patterns.md                ← RTL/Arabic layout patterns
│   └── language_codes.md              ← Language codes, formats, currencies
├── hooks/
│   └── hooks.json                     ← File event triggers
└── README.md                          ← This file
```

---

## Supported Language Highlights

### Arabic (ar, ar_SA, ar_AE)

- RTL layout with automatic Bootstrap RTL in Odoo 16+
- 6 plural forms (required in Plural-Forms header)
- Western numerals recommended for business data
- Common currencies: SAR, AED, KWD, QAR, EGP

### Turkish (tr)

- LTR layout
- Special characters: Ğ, ğ, İ, ı, Ş, ş, Ç, ç, Ö, ö, Ü, ü
- 2 plural forms

### French (fr, fr_FR)

- LTR layout
- Decimal: comma (,), thousands: space
- Currency symbol after amount: `150,00 €`
- 2 plural forms

---

## Common Issues

### Q: Translations not appearing after editing .po file
```bash
# Update the module to reload .po files
python -m odoo -c conf/myproject.conf -d mydb -u my_module --stop-after-init
# Then clear browser cache (Ctrl+Shift+R)
```

### Q: Arabic text appears as "ÙŠÙ†" (garbled)
The file was saved as Latin-1 instead of UTF-8. Fix:
```bash
python i18n_converter.py --action convert --po ar.po --output ar_fixed.po
```

### Q: RTL layout not activating
Check:
1. Arabic language is installed: Settings > Languages
2. User language is set to Arabic
3. Website: Arabic URL used (`/ar/`)
4. Odoo 16+: Bootstrap RTL loads automatically

### Q: .po file has fuzzy entries
Fuzzy entries need human review. Open the .po file, verify the translation, and remove the `#, fuzzy` flag from approved entries.

### Q: Format specifier error in validation
```po
# WRONG:
msgid "Found %s records in %d files"
msgstr "تم العثور على %s سجل"   ← missing second specifier

# CORRECT:
msgstr "تم العثور على %s سجل في %d ملفات"
```

---

## Contributing

This plugin is maintained by TaqaTechno. For issues or contributions:

- Email: contact@taqat-techno.com
- The plugin supports Odoo 14 through 19
- Test scripts with Python 3.8+ before submitting changes
- All contributions must maintain Arabic/RTL support as a first-class feature

---

## License

MIT License — Free to use, modify, and distribute with attribution to TaqaTechno.

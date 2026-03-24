---
name: odoo-i18n
description: |
  Comprehensive Odoo i18n toolkit for extracting translatable strings, validating .po files, generating translation reports, managing Arabic/RTL layouts, and handling multilingual deployments across Odoo 14-19.


  <example>
  Context: User wants to extract translatable strings
  user: "Extract all translatable strings from my Odoo 17 module to a .pot file"
  assistant: "I will use the odoo-i18n skill to scan Python _() calls, XML translate attributes, and field strings, then generate a properly structured .pot template file."
  <commentary>Core trigger - translation extraction workflow.</commentary>
  </example>

  <example>
  Context: User wants Arabic translation
  user: "Generate an Arabic .po file for my Odoo module"
  assistant: "I will use the odoo-i18n skill to create an ar.po file with RTL-aware formatting and placeholder translations for all extractable strings."
  <commentary>Language-specific trigger - Arabic/RTL translation generation.</commentary>
  </example>

  <example>
  Context: User wants to validate a translation file
  user: "Validate my Arabic .po file for errors"
  assistant: "I will use the odoo-i18n skill to check syntax, encoding, empty translations, fuzzy entries, and RTL-specific issues."
  <commentary>Validate trigger - .po file validation.</commentary>
  </example>

  <example>
  Context: User wants to find missing translations
  user: "Find all strings missing Arabic translation in my module"
  assistant: "I will compare the .pot template against ar.po and report all untranslated or fuzzy entries."
  <commentary>Missing trigger - translation gap analysis.</commentary>
  </example>

  <example>
  Context: User wants RTL/SCSS help
  user: "Fix the RTL layout issues in my Odoo theme for Arabic"
  assistant: "I will use the odoo-i18n skill to apply CSS logical properties, [dir='rtl'] overrides, and Font Awesome icon swaps for Arabic support."
  <commentary>RTL trigger - Arabic layout and styling guidance.</commentary>
  </example>

  <example>
  Context: User needs to export/import translations via Odoo CLI
  user: "Export translations for my module using Odoo CLI"
  assistant: "I will use the odoo-i18n skill to run the Odoo export command and generate the .po file."
  <commentary>Export trigger - Odoo CLI translation export.</commentary>
  </example>

  <example>
  Context: User needs to load a language into Odoo
  user: "How do I activate Arabic language in my Odoo database?"
  assistant: "I will use the odoo-i18n skill to load the Arabic language pack and activate it via shell or CLI."
  <commentary>Language activation trigger.</commentary>
  </example>

  <example>
  Context: User has translation issues after deployment
  user: "My translations are not showing after I updated the module"
  assistant: "I will diagnose the issue: check encoding, language activation, module update, and browser cache."
  <commentary>Troubleshooting trigger - translation visibility issues.</commentary>
  </example>
license: "MIT"
metadata:
  mode: "codebase"
  supported-versions: ["14","15","16","17","18","19"]
  primary-languages: ["ar","en","tr","fr"]
  categories: [i18n, translation, rtl, arabic]
  filePattern: ["**/i18n/*.po", "**/i18n/*.pot", "**/*.po", "**/*.pot"]
  bashPattern: ["i18n_extractor", "i18n_validator", "i18n_reporter", "i18n_converter", "i18n-export", "i18n-import", "load-language"]
---

# Odoo i18n Skill

Provides deep expertise in Odoo internationalization (i18n) and localization (l10n) across Odoo 14-19.

## Critical Translation Rules

1. **NEVER** use f-strings inside `_()` -- use `%` formatting: `_('Record %s') % name`
2. **NEVER** concatenate strings inside `_()` -- give the translator the full sentence
3. **Use `_lt()`** for class-level strings (selection values, class attributes)
4. **NEVER wrap** `string=` field attributes in `_()` -- they are auto-translated by Odoo
5. **Save `.po` files as UTF-8** without BOM
6. **Arabic** `.po` files must have `nplurals=6` in Plural-Forms header
7. **Always update the module** after editing `.po` files: `-u module --stop-after-init`

---

## Workflow 1: Extract Translatable Strings

Scans an Odoo module for all translatable strings and generates `.pot` (template) and `.po` (language) files.

### Usage

```bash
python ${CLAUDE_PLUGIN_ROOT}/odoo-i18n/scripts/i18n_extractor.py --module <path> --lang <code> [--output <dir>] [--no-pot] [--verbose]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--module` | Yes | Path to the Odoo module directory |
| `--lang` | Yes | Target language code (e.g., `ar`, `fr`, `tr`) |
| `--output` | No | Custom output directory (default: `module/i18n/`) |
| `--no-pot` | No | Skip generating .pot template |
| `--verbose` | No | Show all extracted strings |

### What Gets Extracted

**Python (`*.py`)** -- `_('...')` and `_lt('...')`:
```python
# Extracted:
raise UserError(_('Record %s not found') % name)
state = fields.Selection([('draft', _lt('Draft'))])
# NOT extracted: _(variable), _(f'Hello {name}')
```

**XML (`*.xml`)** -- `string=`, `help=`, `placeholder=` attributes; `name=` on menus/actions; HTML text:
```xml
<field name="state" string="Status"/>      <!-- extracted -->
<h1>Welcome to our website</h1>            <!-- extracted -->
<record id="view_my_form" model="ir.ui.view">  <!-- NOT extracted -->
```

**JavaScript (`*.js`)** -- `_t('...')` and `_lt('...')`:
```javascript
const msg = _t("Save Changes");   // extracted
const msg = _t(someVariable);     // NOT extracted
```

### Generated File Structure

```po
# Translation template for my_module
msgid ""
msgstr ""
"Project-Id-Version: Odoo Module my_module\n"
"Content-Type: text/plain; charset=UTF-8\n"

#: models/my_model.py:45
#, python-format
msgid "Record %s not found"
msgstr ""
```

### Alternative: Odoo's Built-in Extractor

```bash
python odoo-bin -c conf/myproject.conf -d mydb \
    --i18n-export --modules=my_module --language=ar \
    --output=my_module/i18n/ar.po --stop-after-init
```

The Odoo CLI extractor includes database strings (model names, action names) that the plugin extractor does not. For production, the built-in extractor is more complete.

### After Extraction

1. Open the `.po` file in a translation editor (Poedit, Virtaal, or text editor)
2. Fill in all `msgstr` entries
3. Validate: run `i18n_validator.py --po-file path/to/ar.po`
4. Check coverage: run `i18n_reporter.py --module path/ --lang ar`
5. Load into Odoo: update module or use export/import workflow

---

## Workflow 2: Validate .po Files

Validates a `.po` file for syntax errors, encoding issues, empty translations, fuzzy entries, format specifier mismatches, and Arabic/RTL-specific problems.

### Usage

```bash
python ${CLAUDE_PLUGIN_ROOT}/odoo-i18n/scripts/i18n_validator.py --po-file <path> [--lang <code>] [--strict] [--output <file>]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--po-file` | Yes | Path to the `.po` file to validate |
| `--lang` | No | Language code for language-specific checks (auto-detected from filename) |
| `--strict` | No | Treat untranslated strings as errors instead of warnings |
| `--output` | No | Write report to a file instead of stdout |

### What is Validated

**Syntax:** UTF-8 encoding (no BOM/Latin-1), header with Content-Type/charset/Language/MIME-Version, properly quoted strings, no parse errors.

**Translations:** Empty `msgstr` (untranslated), fuzzy flags needing review, duplicate `msgid`, obsolete (`#~`) entries.

**Format Specifiers:** `%s`/`%d`/`%f` count must match; `%(name)s` named specifiers must all appear:
```po
# WRONG - missing second %s:
msgid "Invoice %s due on %s"
msgstr "fatura %s"
# CORRECT:
msgid "Invoice %s due on %s"
msgstr "fatura %s vadesi %s"
```

**Arabic-Specific (`--lang ar`):** Arabic characters present, encoding artifacts from Latin-1, direction control chars, `nplurals=6` required, BIDI overrides flagged.

### Common Errors and Fixes

**"Charset must be UTF-8":**
```bash
python ${CLAUDE_PLUGIN_ROOT}/odoo-i18n/scripts/i18n_converter.py --action convert --po ar.po --output ar_fixed.po
```

**"Fuzzy translation (needs review)"** -- remove the `fuzzy` flag after verifying:
```po
# Before:                          # After:
#, fuzzy, python-format            #, python-format
msgid "Record %s not found"        msgid "Record %s not found"
msgstr "record not found"          msgstr "record not found"
```

**"Arabic should have nplurals=6":**
```po
"Plural-Forms: nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5;\n"
```

### CI/CD Integration

```yaml
- name: Validate Arabic translations
  run: python odoo-i18n/scripts/i18n_validator.py --po-file my_module/i18n/ar.po --lang ar --strict
```

Exit code `0` = passed (may have warnings), `1` = failed (errors found).

---

## Workflow 3: Find Missing Translations

Compares translatable strings from a module's source files against an existing `.po` file to report what is missing or incomplete.

### Usage

```bash
python ${CLAUDE_PLUGIN_ROOT}/odoo-i18n/scripts/i18n_reporter.py --module <path> --lang <code> [--format text|json|csv] [--output <file>] [--min-pct <N>]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--module` | Yes | Path to the Odoo module directory |
| `--lang` | Yes | Language code to check (e.g., `ar`, `fr`) |
| `--format` | No | Output format: `text` (default), `json`, `csv` |
| `--output` | No | Write report to a file instead of stdout |
| `--min-pct` | No | Exit code 1 if completion below threshold |

### Understanding the Report

- **Missing**: String in source code but NO entry in `.po`
- **Empty in .po**: Entry exists but `msgstr` is `""` (not yet translated)
- **Fuzzy**: Auto-matched, needs human review; NOT shown to users (Odoo falls back to source)
- **Completion %** = Translated / Total Active Strings * 100 (non-empty, non-fuzzy, non-obsolete)

### Workflow: Fixing Missing Translations

1. Run `i18n_reporter.py` to identify gaps
2. Open `.po` in Poedit, Virtaal, or text editor
3. Fill in missing `msgstr` entries
4. If strings are entirely absent from `.po`, run `i18n_extractor.py` first
5. Validate with `i18n_validator.py`
6. Re-run `i18n_reporter.py` to confirm coverage

### Updating .po After Source Changes

```bash
# 1. Re-extract new strings
python ${CLAUDE_PLUGIN_ROOT}/odoo-i18n/scripts/i18n_extractor.py --module /path/ --lang ar --no-pot
# 2. Merge (preserves existing translations)
python ${CLAUDE_PLUGIN_ROOT}/odoo-i18n/scripts/i18n_converter.py \
    --action merge --base /path/i18n/ar.po --new /path/i18n/ar.po --output /path/i18n/ar_merged.po
# 3. Check remaining gaps
python ${CLAUDE_PLUGIN_ROOT}/odoo-i18n/scripts/i18n_reporter.py --module /path/ --lang ar
```

---

## Workflow 4: Export/Import via Odoo CLI

Requires PostgreSQL and a valid database.

### Exporting Translations

```bash
# Single module
python odoo-bin -c conf/myproject.conf -d mydb \
    --i18n-export --modules=my_module --language=ar \
    --output=my_module/i18n/ar.po --stop-after-init

# Export .pot template (no --language = empty msgstr)
python odoo-bin -c conf/myproject.conf -d mydb \
    --i18n-export --modules=my_module \
    --output=my_module/i18n/my_module.pot --stop-after-init

# Multiple modules / all installed
python odoo-bin -c conf/myproject.conf -d mydb \
    --i18n-export --modules=mod1,mod2 --language=ar --output=combined_ar.po --stop-after-init
```

### Importing Translations

```bash
# Import .po
python odoo-bin -c conf/myproject.conf -d mydb \
    --i18n-import=my_module/i18n/ar.po --language=ar --modules=my_module --stop-after-init

# Import and overwrite existing
python odoo-bin -c conf/myproject.conf -d mydb \
    --i18n-import=my_module/i18n/ar.po --language=ar \
    --modules=my_module --i18n-overwrite --stop-after-init

# Multiple languages
for lang in ar fr tr; do
    python odoo-bin -c conf/myproject.conf -d mydb \
        --i18n-import=my_module/i18n/${lang}.po --language=${lang} \
        --modules=my_module --stop-after-init
done
```

### Loading Languages

```bash
python odoo-bin -c conf/myproject.conf -d mydb --load-language=ar --stop-after-init
python odoo-bin -c conf/myproject.conf -d mydb --load-language=ar,fr,tr --stop-after-init
```

Check/activate via shell:
```python
# python odoo-bin shell -d mydb
langs = self.env['res.lang'].with_context(active_test=False).search([])
for lang in langs:
    print(f"[{'ACTIVE' if lang.active else 'inactive'}] {lang.code}: {lang.name}")

# Activate
lang = self.env['res.lang'].with_context(active_test=False).search([('code', '=', 'ar')])
lang.active = True
self.env.cr.commit()
```

### Module Update (Simplest Reload)

```bash
python -m odoo -c conf/myproject.conf -d mydb -u my_module --stop-after-init
```

### Odoo 17+ Specifics

Translations stored as JSON terms internally; export format still `.po`. Clear cache:
```python
# python odoo-bin shell -d mydb
self.env['ir.translation'].clear_caches()
self.env.cr.commit()
```

### Website Translations

```bash
python odoo-bin -c conf/myproject.conf -d mydb \
    --i18n-export --modules=website,my_theme_module --language=ar \
    --output=website_ar.po --stop-after-init
```

### Translation File Locations

```
module/i18n/
  module.pot    <- Template (not loaded by Odoo)
  ar.po         <- Arabic
  ar_SA.po      <- Saudi variant (overrides ar.po entries)
  fr.po         <- French
  tr.po         <- Turkish
```

---

## Utility: Merge and Clean .po Files

```bash
python ${CLAUDE_PLUGIN_ROOT}/odoo-i18n/scripts/i18n_converter.py --action merge --base ar.po --new ar_new.po --output ar_merged.po
python ${CLAUDE_PLUGIN_ROOT}/odoo-i18n/scripts/i18n_converter.py --action clean --po ar.po
python ${CLAUDE_PLUGIN_ROOT}/odoo-i18n/scripts/i18n_converter.py --action stats --po ar.po
python ${CLAUDE_PLUGIN_ROOT}/odoo-i18n/scripts/i18n_converter.py --action convert --po ar.po --output ar_fixed.po
```

---

## Supported Languages Quick Reference

| Code | Language | RTL? | Plural Forms |
|------|----------|------|-------------|
| `ar` / `ar_SA` / `ar_AE` | Arabic (variants) | Yes | 6 |
| `en` / `en_US` | English | No | 2 |
| `fr` / `fr_FR` | French | No | 2 |
| `tr` | Turkish | No | 2 |
| `de` | German | No | 2 |
| `es` | Spanish | No | 2 |

---

## Odoo Version Differences

| Feature | Odoo 14-15 | Odoo 16-17 | Odoo 18-19 |
|---------|-----------|-----------|-----------|
| JS translation import | `import { _t } from "web.core"` | `import { _t } from "@web/core/l10n/translation"` | Same as 16 |
| Bootstrap version | 4.x | 5.1.3 (RTL built-in) | 5.1.3+ |
| Translation storage | `ir.translation` table | JSON terms (internal) | JSON terms |
| View type for lists | `<tree>` | `<tree>` | `<list>` (19 only) |
| Controller type | `type='json'` | `type='json'` | `type='jsonrpc'` (19 only) |
| Visibility attrs | `attrs={'invisible': ...}` | `attrs={'invisible': ...}` | Inline `invisible="expr"` (19 only) |

---

## Common Issues

**Translations not showing**: Update the module with `-u module --stop-after-init`, then clear browser cache.

**Arabic text garbled (mojibake)**: File saved as Latin-1. Run `i18n_converter.py --action convert` to fix encoding.

**Format specifier error**: Ensure `%s`/`%d`/`%(name)s` count matches between msgid and msgstr.

**Website shows English for Arabic users**: Check (1) Arabic language installed, (2) user language set, (3) module updated after adding translations.

**Fuzzy entries**: Open .po, verify translation, remove `#, fuzzy` flag from approved entries.

---

## Configurable Branding

Generated .pot/.po files use configurable author/email. Set environment variables:
```bash
export ODOO_I18N_COPYRIGHT="Your Company"
export ODOO_I18N_BUGS_EMAIL="you@example.com"
```

## Detailed Reference (Memory Files)

For comprehensive patterns beyond this skill summary, the plugin includes memory files:

- **`memories/translation_patterns.md`** -- Python `_()` / `_lt()` patterns, XML attribute translation, JS `_t()` patterns, .po file structure, email template translation
- **`memories/rtl_patterns.md`** -- RTL activation, Bootstrap RTL, CSS logical properties, SCSS overrides, Flexbox in RTL, JS RTL detection, QWeb report RTL, common RTL fixes
- **`memories/language_codes.md`** -- Language codes, date/time formats, number formats, currency display, Hijri calendar notes, timezone reference

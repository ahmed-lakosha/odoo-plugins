---
title: 'Odoo i18n'
read_only: false
type: 'command'
description: 'Odoo internationalization toolkit — extract, validate, missing, export translations'
argument-hint: '[extract|validate|missing|export] [args...]'
---

# /odoo-i18n — Odoo Internationalization Toolkit

Parse `$ARGUMENTS` to determine the subcommand:

- `extract` → Jump to **Section: Extract Strings**
- `validate` → Jump to **Section: Validate .po**
- `missing` → Jump to **Section: Find Missing**
- `export` → Jump to **Section: Export/Import**
- No args or `help` → Jump to **Section: Help & Status**

---

## Section: Help & Status

| Subcommand | Description |
|------------|-------------|
| `/odoo-i18n extract --module <path> --lang <code>` | Extract translatable strings into `.pot`/`.po` files |
| `/odoo-i18n validate --po-file <path>` | Validate `.po` files for errors and language-specific issues |
| `/odoo-i18n missing --module <path> --lang <code>` | Report missing translations vs source strings |
| `/odoo-i18n export` | Export/import translations via Odoo CLI |

### Quick Start

```bash
# 1. Extract strings
python odoo-i18n/scripts/i18n_extractor.py --module /path/to/my_module --lang ar
# 2. Translate the strings in my_module/i18n/ar.po
# 3. Validate
python odoo-i18n/scripts/i18n_validator.py --po-file /path/to/my_module/i18n/ar.po --lang ar
# 4. Check coverage
python odoo-i18n/scripts/i18n_reporter.py --module /path/to/my_module --lang ar
# 5. Load into Odoo
python -m odoo -c conf/myproject.conf -d mydb -u my_module --stop-after-init
```

### Key Concepts

**Translation in Python:** `_('text')` or `_lt('text')` for class-level strings.
**Translation in JS (16+):** `_t("text")` from `@web/core/l10n/translation`.
**Translation in XML:** `string="..."` attributes and HTML text content are auto-translated.

### Supported Languages

| Code | Language | RTL? | Plural Forms |
|------|----------|------|-------------|
| `ar` / `ar_SA` / `ar_AE` | Arabic (variants) | Yes | 6 |
| `en` / `en_US` | English | No | 2 |
| `fr` / `fr_FR` | French | No | 2 |
| `tr` | Turkish | No | 2 |
| `de` | German | No | 2 |
| `es` | Spanish | No | 2 |

### Common Issues

**Translations not showing:** Update the module: `python -m odoo -c conf.conf -d db -u my_module --stop-after-init`

**Website shows English when Arabic active:** Check (1) Arabic language installed in Settings > Languages, (2) user language set to Arabic, (3) module updated after adding translations.

**Arabic text garbled (mojibake):** The .po file is not UTF-8. Use `/odoo-i18n validate` to detect, then re-save as UTF-8 without BOM.

---

## Section: Extract Strings

Scans an Odoo module for all translatable strings and generates `.pot` (template) and `.po` (language) files.

### Usage

```
/odoo-i18n extract --module <path> --lang <code> [--output <dir>] [--no-pot] [--verbose]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--module` | Yes | Path to the Odoo module directory |
| `--lang` | Yes | Target language code (e.g., `ar`, `fr`, `tr`) |
| `--output` | No | Custom output directory (default: `module/i18n/`) |
| `--no-pot` | No | Skip generating .pot template |
| `--verbose` | No | Show all extracted strings |

### What Gets Extracted

**Python (`*.py`)** — `_('...')` and `_lt('...')`:
```python
# Extracted:
raise UserError(_('Record %s not found') % name)
state = fields.Selection([('draft', _lt('Draft'))])
# NOT extracted: _(variable), _(f'Hello {name}')
```

**XML (`*.xml`)** — `string=`, `help=`, `placeholder=` attributes; `name=` on menus/actions; HTML text:
```xml
<field name="state" string="Status"/>      <!-- extracted -->
<h1>Welcome to our website</h1>            <!-- extracted -->
<record id="view_my_form" model="ir.ui.view">  <!-- NOT extracted -->
```

**JavaScript (`*.js`)** — `_t('...')` and `_lt('...')`:
```javascript
const msg = _t("Save Changes");   // extracted
const msg = _t(someVariable);     // NOT extracted
```

### Examples

```bash
# Extract Arabic translations
python odoo-i18n/scripts/i18n_extractor.py --module /path/to/my_module --lang ar

# Custom output, skip .pot, verbose
python odoo-i18n/scripts/i18n_extractor.py \
    --module /path/to/my_module --lang fr --output /tmp/translations/ --no-pot --verbose
```

Output creates `my_module/i18n/my_module.pot` (template) and `my_module/i18n/ar.po` (language file).

### Alternative: Odoo's Built-in Extractor

```bash
python odoo-bin -c conf/myproject.conf -d mydb \
    --i18n-export --modules=my_module --language=ar \
    --output=my_module/i18n/ar.po --stop-after-init
```

The Odoo CLI extractor includes database strings (model names, action names) that the plugin extractor does not. For production, the built-in extractor is more complete.

### Generated .pot Template

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

### Generated .po Language File

```po
# Arabic translation of my_module
msgid ""
msgstr ""
"Language: ar\n"
"Plural-Forms: nplurals=6; plural=...;\n"
"Content-Type: text/plain; charset=UTF-8\n"

#: models/my_model.py:45
#, python-format
msgid "Record %s not found"
msgstr "السجل %s غير موجود"
```

### After Extraction

1. Open the `.po` file in a translation editor (Poedit, Virtaal, or text editor)
2. Fill in all `msgstr` entries
3. Validate: `/odoo-i18n validate --po-file path/to/ar.po`
4. Check coverage: `/odoo-i18n missing --module path/ --lang ar`
5. Load into Odoo: update module or use `/odoo-i18n export` import workflow

---

## Section: Validate .po

Validates a `.po` file for syntax errors, encoding issues, empty translations, fuzzy entries, format specifier mismatches, and Arabic/RTL-specific problems.

### Usage

```
/odoo-i18n validate --po-file <path> [--lang <code>] [--strict] [--output <file>]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--po-file` | Yes | Path to the `.po` file to validate |
| `--lang` | No | Language code for language-specific checks (auto-detected from filename) |
| `--strict` | No | Treat untranslated strings as errors instead of warnings |
| `--output` | No | Write report to a file instead of stdout |

### Examples

```bash
python odoo-i18n/scripts/i18n_validator.py --po-file /path/to/ar.po
python odoo-i18n/scripts/i18n_validator.py --po-file /path/to/ar.po --strict
python odoo-i18n/scripts/i18n_validator.py --po-file /path/to/translations.po --lang ar --output /tmp/report.txt
```

### What is Validated

**Syntax:** UTF-8 encoding (no BOM/Latin-1), header with Content-Type/charset/Language/MIME-Version, properly quoted strings, no parse errors.

**Translations:** Empty `msgstr` (untranslated), fuzzy flags needing review, duplicate `msgid`, obsolete (`#~`) entries.

**Format Specifiers:** `%s`/`%d`/`%f` count must match; `%(name)s` named specifiers must all appear:
```po
# WRONG — missing second %s:
msgid "Invoice %s due on %s"
msgstr "فاتورة %s"
# CORRECT:
msgid "Invoice %s due on %s"
msgstr "فاتورة %s تستحق في %s"
```

**Arabic-Specific (`--lang ar`):** Arabic characters present, encoding artifacts (`Ø`/`Ù` from Latin-1), direction control chars, `nplurals=6` required, BIDI overrides flagged.

**Whitespace:** Leading/trailing whitespace should match between `msgid` and `msgstr`.

### Common Errors and Fixes

**"Charset must be UTF-8":**
```bash
python odoo-i18n/scripts/i18n_converter.py --action convert --po ar.po --output ar_fixed.po
```

**"Fuzzy translation (needs review)"** — remove the `fuzzy` flag after verifying:
```po
# Before:                          # After:
#, fuzzy, python-format            #, python-format
msgid "Record %s not found"        msgid "Record %s not found"
msgstr "السجل %s غير موجود"        msgstr "السجل %s غير موجود"
```

**"Format specifier mismatch"** — ensure placeholder count and order match the source.

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

## Section: Find Missing

Compares translatable strings from a module's source files against an existing `.po` file to report what is missing or incomplete.

### Usage

```
/odoo-i18n missing --module <path> --lang <code> [--format text|json|csv] [--output <file>] [--min-pct <N>]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--module` | Yes | Path to the Odoo module directory |
| `--lang` | Yes | Language code to check (e.g., `ar`, `fr`) |
| `--format` | No | Output format: `text` (default), `json`, `csv` |
| `--output` | No | Write report to a file instead of stdout |
| `--min-pct` | No | Exit code 1 if completion below threshold |

### Examples

```bash
# Basic report
python odoo-i18n/scripts/i18n_reporter.py --module /path/to/my_module --lang ar

# JSON for CI / CSV for spreadsheets
python odoo-i18n/scripts/i18n_reporter.py --module /path/to/my_module --lang ar --format json
python odoo-i18n/scripts/i18n_reporter.py --module /path/to/my_module --lang ar --format csv --output missing.csv

# Enforce minimum 90% coverage
python odoo-i18n/scripts/i18n_reporter.py --module /path/to/my_module --lang ar --min-pct 90.0

# Multiple languages
for lang in ar fr tr; do
    python odoo-i18n/scripts/i18n_reporter.py --module /path/to/my_module --lang $lang
done
```

### Understanding the Report

The report shows total strings, translated count/percentage, missing, empty-in-po, fuzzy, and a progress bar. Missing entries are grouped by source file with line numbers.

- **Missing**: String in source code but NO entry in `.po`
- **Empty in .po**: Entry exists but `msgstr` is `""` (not yet translated)
- **Fuzzy**: Auto-matched, needs human review; NOT shown to users (Odoo falls back to source)
- **Completion %** = Translated / Total Active Strings * 100 (non-empty, non-fuzzy, non-obsolete)

### Workflow: Fixing Missing Translations

1. Run `/odoo-i18n missing` to identify gaps
2. Open `.po` in Poedit, Virtaal, or text editor
3. Fill in missing `msgstr` entries
4. If strings are entirely absent from `.po`, run `/odoo-i18n extract` first
5. Validate with `/odoo-i18n validate`
6. Re-run `/odoo-i18n missing` to confirm coverage

### Updating .po After Source Changes

```bash
# 1. Re-extract new strings
python odoo-i18n/scripts/i18n_extractor.py --module /path/ --lang ar --no-pot
# 2. Merge (preserves existing translations)
python odoo-i18n/scripts/i18n_converter.py \
    --action merge --base /path/i18n/ar.po --new /path/i18n/ar.po --output /path/i18n/ar_merged.po
# 3. Check remaining gaps
python odoo-i18n/scripts/i18n_reporter.py --module /path/ --lang ar
```

---

## Section: Export/Import

Reference for exporting and importing translations using Odoo's built-in CLI. Requires PostgreSQL and a valid database.

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
python odoo-bin -c conf/myproject.conf -d mydb \
    --i18n-export --language=ar --output=all_ar.po --stop-after-init
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

Reset website builder overrides:
```python
# python odoo-bin shell -d mydb
self.env['ir.translation'].search([
    ('lang', '=', 'ar'),
    ('res_id', 'in', self.env['ir.ui.view'].search([('key', 'like', 'my_theme')]).ids),
]).unlink()
self.env.cr.commit()
```

### Translation File Locations

```
module/i18n/
├── module.pot    <- Template (not loaded by Odoo)
├── ar.po         <- Arabic
├── ar_SA.po      <- Saudi variant (overrides ar.po entries)
├── fr.po         <- French
└── tr.po         <- Turkish
```

### Using Poedit (Recommended GUI)

1. Install from https://poedit.net/
2. Open `my_module/i18n/ar.po`, translate, save
3. Import back into Odoo using CLI above

---

> Previously available as separate commands: /i18n-extract, /i18n-validate, /i18n-missing, /i18n-export.
> All functionality is now unified under /odoo-i18n or handled by the skill via natural language.

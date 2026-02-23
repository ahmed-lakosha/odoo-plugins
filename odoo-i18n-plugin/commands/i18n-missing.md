# /i18n-missing — Find Missing Translations

Compares the translatable strings extracted from a module's source files against an existing `.po` file and reports what is missing, incomplete, or needs attention.

## Usage

```
/i18n-missing --module <path> --lang <code>
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--module` | Yes | Path to the Odoo module directory |
| `--lang` | Yes | Language code to check (e.g., `ar`, `fr`) |
| `--format` | No | Output format: `text` (default), `json`, `csv` |
| `--output` | No | Write report to a file instead of stdout |
| `--min-pct` | No | Exit code 1 if completion below threshold |

## Examples

### Basic missing translation report

```bash
python odoo-i18n/scripts/i18n_reporter.py \
    --module /path/to/my_module \
    --lang ar
```

**Example output:**
```
=================================================================
Translation Report: my_module (ar)
=================================================================
Module:        /path/to/my_module
Language:      ar
PO File:       /path/to/my_module/i18n/ar.po
PO Exists:     Yes

--- Translation Statistics ---
Total strings:    247
Translated:       198 (80.2%)
Missing:          49
Empty in .po:     12
Fuzzy:            3

Progress:      [================================--------] 80.2%

--- Missing by Source Type ---
  Python: 18
  Xml: 24
  Javascript: 7

--- Missing Translations ---
(Showing 49 missing entries, sorted by location)

  File: models/sale_order.py
    [  45] 'Order Confirmation'
    [ 123] 'Quotation sent to customer'
    [ 189] 'Cannot delete confirmed order'

  File: views/templates.xml
    [  23] 'Track Your Order'
    [  67] 'Order History'
    ...

--- Recommendations ---
  1. Translate 49 missing strings in: /path/to/my_module/i18n/ar.po
  2. Run i18n_validator.py to check the translated file
  3. Update module in Odoo to load new translations
  Review 3 fuzzy entries — they need human verification
=================================================================
```

### JSON output (for CI integration)

```bash
python odoo-i18n/scripts/i18n_reporter.py \
    --module /path/to/my_module \
    --lang ar \
    --format json
```

### CSV output (for spreadsheet editing)

```bash
python odoo-i18n/scripts/i18n_reporter.py \
    --module /path/to/my_module \
    --lang ar \
    --format csv \
    --output missing_ar.csv
```

### Enforce minimum coverage in CI/CD

```bash
# Exit with code 1 if less than 90% translated
python odoo-i18n/scripts/i18n_reporter.py \
    --module /path/to/my_module \
    --lang ar \
    --min-pct 90.0
```

### Check multiple languages

```bash
for lang in ar fr tr; do
    echo "=== $lang ==="
    python odoo-i18n/scripts/i18n_reporter.py \
        --module /path/to/my_module \
        --lang $lang \
        --format text
done
```

## Understanding the Report

### "Missing" vs "Empty in .po"

- **Missing**: String exists in source code but has NO entry in the `.po` file
- **Empty in .po**: String HAS an entry in `.po` but `msgstr` is `""` (not translated yet)

Both are shown together as "missing" in the count because both result in untranslated text.

### "Fuzzy" Entries

Fuzzy entries in a `.po` file are translations that were automatically matched but need human review. They appear when:
- The source string changed slightly (Odoo's msgmerge marks old translations fuzzy)
- A translator marked them with the `#, fuzzy` flag

Fuzzy translations are NOT shown to users — Odoo falls back to the source string.

### Completion Percentage

```
Completion % = Translated / (Total Active Strings) * 100
```

Where "Translated" means: entry exists in .po AND msgstr is non-empty AND not fuzzy AND not obsolete.

## Workflow: Fixing Missing Translations

1. Run `/i18n-missing` to see what needs translation
2. Open the `.po` file in Poedit, Virtaal, or a text editor
3. Find the missing `msgid` entries and add `msgstr` translations
4. If strings are missing from `.po` entirely, run `/i18n-extract` first to add them
5. Validate with `/i18n-validate`
6. Re-run `/i18n-missing` to confirm 100% coverage

## Updating .po After Source Changes

When you add new strings to your Python/XML/JS code:

```bash
# 1. Extract to get new .pot
python odoo-i18n/scripts/i18n_extractor.py --module /path/ --lang ar --no-pot

# 2. Merge new strings into existing .po (preserves existing translations)
python odoo-i18n/scripts/i18n_converter.py \
    --action merge \
    --base /path/i18n/ar.po \
    --new /path/i18n/ar.po \  # the newly generated file
    --output /path/i18n/ar_merged.po

# 3. Check what's still missing
python odoo-i18n/scripts/i18n_reporter.py --module /path/ --lang ar
```

## Integration with Odoo Module Update Workflow

```bash
# After translating, update the module to load new translations
python -m odoo -c conf/myproject.conf \
    -d mydb \
    -u my_module \
    --stop-after-init

# Or import specific .po file
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-import=/path/to/ar.po \
    --language=ar \
    --modules=my_module \
    --i18n-overwrite \
    --stop-after-init
```

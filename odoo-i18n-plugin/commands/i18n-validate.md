# /i18n-validate — Validate .po Translation Files

Validates a `.po` file for syntax errors, encoding issues, empty translations, fuzzy entries, format specifier mismatches, and Arabic/RTL-specific problems.

## Usage

```
/i18n-validate --po-file <path>
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--po-file` | Yes | Path to the `.po` file to validate |
| `--lang` | No | Language code for language-specific checks (auto-detected from filename) |
| `--strict` | No | Treat untranslated strings as errors instead of warnings |
| `--output` | No | Write report to a file instead of stdout |

## Examples

### Basic validation

```bash
python odoo-i18n/scripts/i18n_validator.py \
    --po-file /path/to/my_module/i18n/ar.po
```

**Example output:**
```
============================================================
Validation Report: ar.po
============================================================
Language:         ar
File:             /path/to/my_module/i18n/ar.po

--- Translation Statistics ---
Total entries:    247
Translated:       235 (95.1%)
Untranslated:     12
Fuzzy:            3
Obsolete:         5

--- Validation Summary ---
Parse errors:     0
Errors:           1
Warnings:         4
Info notes:       2

--- Errors ---
  [ERROR] line  234: Format specifier mismatch: source has 2, translation has 1 | Invoice %s due on %s

--- Warnings ---
  [WARN ] line   45: Fuzzy translation (needs review) | Save Changes
  [WARN ] line   89: Empty translation (untranslated string) | Order Confirmation
  [WARN ] line  156: Arabic should have nplurals=6, found nplurals=2
  [WARN ] line  203: Empty translation (untranslated string) | Cancel

--- Info Notes ---
  [INFO ] line   78: Trailing whitespace differs: source has 1, translation has 0 | Click here
  [INFO ] line  199: Translation contains direction control characters | ...

============================================================
Result: FAILED — Fix errors before loading into Odoo
============================================================
```

### Strict mode (fail on any untranslated string)

```bash
python odoo-i18n/scripts/i18n_validator.py \
    --po-file /path/to/ar.po \
    --strict
```

### Validate with explicit language

```bash
python odoo-i18n/scripts/i18n_validator.py \
    --po-file /path/to/translations.po \
    --lang ar
```

### Save report to file

```bash
python odoo-i18n/scripts/i18n_validator.py \
    --po-file /path/to/ar.po \
    --output /tmp/validation_report.txt
```

## What is Validated

### Syntax Checks

| Check | Description |
|-------|-------------|
| File encoding | Must be UTF-8 (no BOM, no Latin-1) |
| Header presence | Must have empty msgid entry with metadata |
| Required header fields | Content-Type, charset, Language, MIME-Version |
| Quoted strings | All msgid/msgstr must be properly quoted |
| Parse errors | Unexpected content, malformed lines |

### Translation Checks

| Check | Description |
|-------|-------------|
| Empty msgstr | Entries with no translation |
| Fuzzy flags | Entries marked `#, fuzzy` that need review |
| Duplicate msgids | Same source string defined twice |
| Obsolete entries | Entries marked `#~` (removed from source) |

### Format Specifier Checks

| Check | Description |
|-------|-------------|
| `%s`, `%d`, `%f` count | Number of positional specifiers must match |
| `%(name)s` named specifiers | All named specifiers must appear in translation |

**Example error:**
```
msgid "Invoice %s due on %s"
msgstr "فاتورة %s"  ← WRONG: missing second %s
```

**Correct:**
```
msgid "Invoice %s due on %s"
msgstr "فاتورة %s تستحق في %s"
```

### Arabic-Specific Checks (`--lang ar`)

| Check | Description |
|-------|-------------|
| Arabic characters present | Translation should contain Arabic script |
| Encoding artifacts | Detects `Ø`, `Ù` patterns that indicate UTF-8 read as Latin-1 |
| Direction control chars | Warns about RTL/LTR marks in translation strings |
| Plural forms | Arabic requires `nplurals=6` |
| BIDI override characters | Flags potentially dangerous direction override characters |

### Whitespace Consistency

| Check | Description |
|-------|-------------|
| Leading whitespace | Should match between msgid and msgstr |
| Trailing whitespace | Should match between msgid and msgstr |

## Common Errors and Fixes

### Error: "Charset must be UTF-8"

The `.po` file was saved with wrong encoding.

```bash
# Fix using converter
python odoo-i18n/scripts/i18n_converter.py \
    --action convert \
    --po ar.po \
    --output ar_fixed.po
```

### Error: "Arabic text appears to be mis-encoded"

The file is UTF-8 but was previously loaded/saved with Latin-1 encoding.

1. Open the file in a text editor that supports encoding detection
2. Select "Save As" with UTF-8 encoding
3. Or use the `convert` action of `i18n_converter.py`

### Warning: "Fuzzy translation (needs review)"

Open the `.po` file, find the entry with `#, fuzzy`, review the translation, and if correct, remove the `fuzzy` flag:

```po
# Before:
#, fuzzy, python-format
msgid "Record %s not found"
msgstr "السجل %s غير موجود"

# After (fuzzy flag removed — translation approved):
#, python-format
msgid "Record %s not found"
msgstr "السجل %s غير موجود"
```

### Error: "Format specifier mismatch"

The translation has a different number of `%s`/`%d` placeholders than the source.

```po
# Source has 2 placeholders:
msgid "Invoice %s is overdue by %d days"

# WRONG (only 1 placeholder):
msgstr "فاتورة %s متأخرة"

# CORRECT (must have 2 placeholders in same order):
msgstr "فاتورة %s متأخرة بـ %d أيام"
```

### Warning: "Arabic should have nplurals=6"

Fix the Plural-Forms header:

```po
# Wrong:
"Plural-Forms: nplurals=2; plural=(n != 1);\n"

# Correct for Arabic:
"Plural-Forms: nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5;\n"
```

## Using Validation in CI/CD

```yaml
# GitHub Actions example
- name: Validate Arabic translations
  run: |
    python odoo-i18n/scripts/i18n_validator.py \
      --po-file my_module/i18n/ar.po \
      --lang ar \
      --strict
  # Exits with code 1 if any errors found
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Validation passed (may have warnings/info) |
| `1` | Validation failed (parse errors or error-severity issues) |

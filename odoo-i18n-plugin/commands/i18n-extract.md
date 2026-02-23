# /i18n-extract — Extract Translatable Strings

Scans an Odoo module for all translatable strings and generates `.pot` (template) and `.po` (language) files.

## Usage

```
/i18n-extract --module <path> --lang <code>
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--module` | Yes | Path to the Odoo module directory |
| `--lang` | Yes | Target language code (e.g., `ar`, `fr`, `tr`) |
| `--output` | No | Custom output directory (default: `module/i18n/`) |

## What Gets Extracted

The extractor scans these file types:

### Python files (`*.py`)
- `_('...')` — standard translation function
- `_lt('...')` — lazy translation function (class-level strings)

```python
# Extracted:
raise UserError(_('Record not found'))
raise UserError(_('Record %s not found') % name)
state = fields.Selection([('draft', _lt('Draft'))])

# NOT extracted (dynamic strings):
msg = _t(some_variable)  # Variables not extracted
raise UserError(_(f'Hello {name}'))  # f-strings not extracted
```

### XML files (`*.xml`)
- `string="..."` attributes in view fields
- `help="..."` attributes
- `placeholder="..."` attributes
- `name="..."` on menu items and actions
- Text content of HTML elements (`<h1>`, `<p>`, `<span>`, etc.)

```xml
<!-- Extracted: -->
<field name="state" string="Status"/>
<field name="ref" help="Internal reference number"/>
<h1>Welcome to our website</h1>

<!-- NOT extracted: -->
<record id="view_my_form" model="ir.ui.view">  <!-- technical name, not user-facing -->
```

### JavaScript files (`*.js`)
- `_t('...')` — translation function
- `_lt('...')` — lazy translation function

```javascript
// Extracted:
const msg = _t("Save Changes");
const label = _lt("Draft");

// NOT extracted:
const msg = _t(someVariable);  // Variables not extracted
```

## Examples

### Extract Arabic translations for a module

```bash
python odoo-i18n/scripts/i18n_extractor.py \
    --module /path/to/my_module \
    --lang ar
```

**Output:**
```
Scanning module: my_module
  Python files: 47 strings extracted
  XML files: 89 strings extracted
  JavaScript files: 12 strings extracted
  Found 148 unique translatable strings

Output directory: /path/to/my_module/i18n
  Generated: my_module.pot
  Generated: ar.po
```

### Extract with custom output directory

```bash
python odoo-i18n/scripts/i18n_extractor.py \
    --module /path/to/my_module \
    --lang fr \
    --output /tmp/translations/
```

### Extract without generating .pot template

```bash
python odoo-i18n/scripts/i18n_extractor.py \
    --module /path/to/my_module \
    --lang tr \
    --no-pot
```

### Extract with verbose output (see all strings)

```bash
python odoo-i18n/scripts/i18n_extractor.py \
    --module /path/to/my_module \
    --lang ar \
    --verbose
```

## Using Odoo's Built-in Extractor (Alternative)

```bash
# Export using Odoo CLI (requires running database)
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-export \
    --modules=my_module \
    --language=ar \
    --output=my_module/i18n/ar.po \
    --stop-after-init
```

The Odoo CLI extractor includes strings from the database (model names, action names, etc.) that the plugin extractor doesn't cover. For production use, Odoo's built-in extractor is more complete.

## Generated File Structure

### .pot Template File

The `.pot` file is the master template containing all source strings with empty translations:

```po
# Translation template for my_module
msgid ""
msgstr ""
"Project-Id-Version: Odoo Module my_module\n"
"Language: \n"
"Content-Type: text/plain; charset=UTF-8\n"

#: models/my_model.py:45
#, python-format
msgid "Record %s not found"
msgstr ""

#: views/templates.xml:23
msgid "Welcome to our website"
msgstr ""
```

### .po Language File

The `.po` file is a copy of the template with the language header set. Fill in the `msgstr` entries:

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
msgstr "السجل %s غير موجود"          <-- Fill this in
```

## After Extraction

1. Open the generated `.po` file in a translation editor
2. Fill in all `msgstr` entries with translated text
3. Validate: `/i18n-validate --po-file path/to/ar.po`
4. Check coverage: `/i18n-missing --module path/ --lang ar`
5. Load into Odoo: `/i18n-export --action import`

## Supported Language Codes

| Code | Language | Plural Forms |
|------|----------|-------------|
| `ar` | Arabic | 6 forms |
| `ar_SA` | Arabic (Saudi) | 6 forms |
| `fr` | French | 2 forms |
| `tr` | Turkish | 2 forms |
| `en_US` | English (US) | 2 forms |
| `de` | German | 2 forms |
| `es` | Spanish | 2 forms |

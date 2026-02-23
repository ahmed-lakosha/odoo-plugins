# /i18n-export — Export & Import Translations via Odoo CLI

Reference guide for exporting and importing translations using Odoo's built-in command-line interface. Also covers loading languages, overwriting translations, and working with translation databases.

## Odoo CLI Translation Commands

Odoo provides several i18n-related CLI arguments. These require a running PostgreSQL connection and a valid database.

---

## Exporting Translations

### Export a single module's translations

```bash
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-export \
    --modules=my_module \
    --language=ar \
    --output=my_module/i18n/ar.po \
    --stop-after-init
```

### Export to .pot template (no language = all strings, empty msgstr)

```bash
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-export \
    --modules=my_module \
    --output=my_module/i18n/my_module.pot \
    --stop-after-init
```

### Export multiple modules at once

```bash
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-export \
    --modules=module1,module2,module3 \
    --language=ar \
    --output=combined_ar.po \
    --stop-after-init
```

### Export all installed modules

```bash
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-export \
    --language=ar \
    --output=all_modules_ar.po \
    --stop-after-init
```

---

## Importing Translations

### Import a .po file into the database

```bash
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-import=my_module/i18n/ar.po \
    --language=ar \
    --modules=my_module \
    --stop-after-init
```

### Import and overwrite existing translations

```bash
# --i18n-overwrite forces re-loading even if translation exists
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-import=my_module/i18n/ar.po \
    --language=ar \
    --modules=my_module \
    --i18n-overwrite \
    --stop-after-init
```

### Import multiple languages

```bash
# Run for each language
for lang in ar fr tr; do
    python odoo-bin -c conf/myproject.conf \
        -d mydb \
        --i18n-import=my_module/i18n/${lang}.po \
        --language=${lang} \
        --modules=my_module \
        --stop-after-init
done
```

---

## Loading Languages

### Load a language pack

```bash
# Install Arabic language (downloads from Odoo's translation server)
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --load-language=ar \
    --stop-after-init

# Install multiple languages
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --load-language=ar,fr,tr \
    --stop-after-init
```

### Check installed languages via Odoo shell

```python
# python odoo-bin shell -d mydb
langs = self.env['res.lang'].with_context(active_test=False).search([])
for lang in langs:
    status = "ACTIVE" if lang.active else "inactive"
    print(f"[{status}] {lang.code}: {lang.name}")
```

### Activate a language via Odoo shell

```python
# python odoo-bin shell -d mydb
lang = self.env['res.lang'].with_context(active_test=False).search([('code', '=', 'ar')])
lang.active = True
self.env.cr.commit()
```

---

## Module Update (Most Common Workflow)

The simplest way to reload translations after editing `.po` files is to update the module:

```bash
# Update single module (reads all .po files in i18n/)
python -m odoo -c conf/myproject.conf \
    -d mydb \
    -u my_module \
    --stop-after-init

# Update with language context (Odoo 17+)
python -m odoo -c conf/myproject.conf \
    -d mydb \
    -u my_module \
    --stop-after-init
```

---

## Odoo 17+ Specific Commands

### Export with new term-based system

In Odoo 17+, translations are stored as JSON terms internally. The export format is still compatible `.po`:

```bash
# Same command works in Odoo 17+
python odoo-bin -c conf/myproject17.conf \
    -d mydb17 \
    --i18n-export \
    --modules=my_module \
    --language=ar \
    --output=ar.po \
    --stop-after-init
```

### Clearing translation cache (Odoo 17+)

```python
# python odoo-bin shell -d mydb
self.env['ir.translation'].clear_caches()
self.env.cr.commit()
```

---

## Using Poedit (Recommended GUI Tool)

1. Install Poedit from https://poedit.net/
2. Open `my_module/i18n/ar.po`
3. Translate strings in the UI
4. Save — Poedit handles encoding and .mo compilation
5. Import back into Odoo using CLI above

---

## Translation in Website Builder

The Odoo website builder adds inline translations directly to the database. To manage these:

### Export website translations

```bash
# Export website-specific translations
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-export \
    --modules=website,my_theme_module \
    --language=ar \
    --output=website_ar.po \
    --stop-after-init
```

### Reset website builder translations

```python
# python odoo-bin shell -d mydb
# Remove all website-level Arabic overrides for a specific view
self.env['ir.translation'].search([
    ('lang', '=', 'ar'),
    ('res_id', 'in', self.env['ir.ui.view'].search([('key', 'like', 'my_theme')]).ids),
]).unlink()
self.env.cr.commit()
```

---

## Translation File Locations

Odoo searches for `.po` files in this order per module:

```
module/
└── i18n/
    ├── module.pot    ← Template (not loaded)
    ├── ar.po         ← Arabic
    ├── ar_SA.po      ← Saudi Arabic variant (loaded after ar.po)
    ├── fr.po         ← French
    └── tr.po         ← Turkish
```

If both `ar.po` and `ar_SA.po` exist, Odoo loads `ar.po` first, then `ar_SA.po` overrides specific strings for the Saudi variant.

---

## Configuration File Tips

Add the translation path to your configuration if using custom locations:

```ini
[options]
addons_path = odoo/addons,projects/my_project
# Odoo automatically finds i18n/ inside each addon path
```

---

## Batch Operations via Shell Script

```bash
#!/bin/bash
# update_translations.sh — Update translations for all modules in a project

PROJECT_CONF="conf/myproject.conf"
DB="mydb"
MODULES="module1,module2,module3"

echo "Exporting current translations..."
python odoo-bin -c $PROJECT_CONF -d $DB \
    --i18n-export --modules=$MODULES --language=ar \
    --output=/tmp/current_ar.po --stop-after-init

echo "... Edit /tmp/current_ar.po ..."
echo "Press Enter when done editing"
read

echo "Importing updated translations..."
python odoo-bin -c $PROJECT_CONF -d $DB \
    --i18n-import=/tmp/current_ar.po --language=ar \
    --modules=$MODULES --i18n-overwrite --stop-after-init

echo "Done!"
```

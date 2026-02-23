# Odoo Language Codes & Locale Reference

Complete reference for language codes, locale settings, date/time formats, number formats, and currency display in Odoo across all supported versions.

---

## 1. Complete Odoo Language Code Table

### Arabic Variants

| Odoo Code | Language | Country | RTL | Plural Forms | Notes |
|-----------|----------|---------|-----|-------------|-------|
| `ar` | Arabic | Generic | Yes | 6 forms | Default Arabic; used when no country-specific variant |
| `ar_SA` | Arabic (Saudi Arabia) | SA | Yes | 6 forms | Most common for Gulf region |
| `ar_AE` | Arabic (UAE) | AE | Yes | 6 forms | UAE variant |
| `ar_EG` | Arabic (Egypt) | EG | Yes | 6 forms | Egyptian Arabic |
| `ar_MA` | Arabic (Morocco) | MA | Yes | 6 forms | Moroccan Arabic (Darija) |
| `ar_DZ` | Arabic (Algeria) | DZ | Yes | 6 forms | Algerian Arabic |
| `ar_TN` | Arabic (Tunisia) | TN | Yes | 6 forms | Tunisian Arabic |
| `ar_JO` | Arabic (Jordan) | JO | Yes | 6 forms | Jordanian Arabic |
| `ar_IQ` | Arabic (Iraq) | IQ | Yes | 6 forms | Iraqi Arabic |
| `ar_KW` | Arabic (Kuwait) | KW | Yes | 6 forms | Kuwaiti Arabic |
| `ar_LB` | Arabic (Lebanon) | LB | Yes | 6 forms | Lebanese Arabic |

### Arabic Plural Forms Rule

```po
# Arabic requires 6 plural forms:
"Plural-Forms: nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5;\n"

# The 6 forms are:
# 0 → Zero (0 items)
# 1 → One (1 item)
# 2 → Two (2 items, dual)
# 3 → Few (3-10 items per hundred)
# 4 → Many (11-99 items per hundred)
# 5 → Other (100+ items, or exact hundreds)
```

### Primary Supported Languages

| Odoo Code | Language | Country | RTL | Plural Forms |
|-----------|----------|---------|-----|-------------|
| `en_US` | English | United States | No | 2 forms |
| `en_GB` | English | United Kingdom | No | 2 forms |
| `en_AU` | English | Australia | No | 2 forms |
| `en_CA` | English | Canada | No | 2 forms |
| `fr` | French | Generic | No | 2 forms |
| `fr_FR` | French | France | No | 2 forms |
| `fr_BE` | French | Belgium | No | 2 forms |
| `fr_CH` | French | Switzerland | No | 2 forms |
| `fr_CA` | French | Canada | No | 2 forms |
| `tr` | Turkish | Turkey | No | 2 forms |
| `de` | German | Generic | No | 2 forms |
| `de_DE` | German | Germany | No | 2 forms |
| `es` | Spanish | Generic | No | 2 forms |
| `es_ES` | Spanish | Spain | No | 2 forms |
| `es_MX` | Spanish | Mexico | No | 2 forms |
| `pt` | Portuguese | Generic | No | 2 forms |
| `pt_BR` | Portuguese | Brazil | No | 2 forms |
| `pt_PT` | Portuguese | Portugal | No | 2 forms |
| `it` | Italian | Italy | No | 2 forms |
| `nl` | Dutch | Generic | No | 2 forms |
| `pl` | Polish | Poland | No | 3 forms |
| `ru` | Russian | Russia | No | 3 forms |
| `zh_CN` | Chinese | Simplified | No | 1 form |
| `zh_TW` | Chinese | Traditional | No | 1 form |
| `ja` | Japanese | Japan | No | 1 form |
| `ko` | Korean | Korea | No | 1 form |
| `he` | Hebrew | Israel | Yes | 2 forms |
| `fa` | Persian (Farsi) | Iran | Yes | 2 forms |
| `ur` | Urdu | Pakistan | Yes | 2 forms |

---

## 2. Date and Time Formats by Language

### Date Format Strings (Python strftime)

| Language Code | Date Format | Example Output |
|---------------|-------------|----------------|
| `ar` / `ar_SA` | `%d/%m/%Y` | `15/01/2024` |
| `en_US` | `%m/%d/%Y` | `01/15/2024` |
| `en_GB` | `%d/%m/%Y` | `15/01/2024` |
| `fr` / `fr_FR` | `%d/%m/%Y` | `15/01/2024` |
| `de` / `de_DE` | `%d.%m.%Y` | `15.01.2024` |
| `tr` | `%d.%m.%Y` | `15.01.2024` |
| `es` / `es_ES` | `%d/%m/%Y` | `15/01/2024` |
| `ja` | `%Y年%m月%d日` | `2024年01月15日` |
| `zh_CN` | `%Y-%m-%d` | `2024-01-15` |

### Odoo Date Field Format Configuration

```python
# In res.lang model — Odoo stores date/time formats per language
lang = self.env['res.lang'].search([('code', '=', 'ar')])
print(lang.date_format)  # e.g., '%d/%m/%Y'
print(lang.time_format)  # e.g., '%H:%M:%S'
```

### Time Formats

| Language Code | Time Format | 12/24 Hour |
|---------------|-------------|------------|
| `ar` / `ar_SA` | `%H:%M:%S` | 24-hour |
| `en_US` | `%I:%M:%S %p` | 12-hour (AM/PM) |
| `en_GB` | `%H:%M:%S` | 24-hour |
| `fr` | `%H:%M:%S` | 24-hour |
| `de` | `%H:%M:%S` | 24-hour |
| `tr` | `%H:%M:%S` | 24-hour |

### Hijri (Islamic) Calendar Notes

Saudi Arabia and some Gulf countries use the Hijri calendar alongside Gregorian. Odoo uses Gregorian by default. For Hijri date display:

```python
# Odoo does not natively support Hijri calendar in core
# Third-party modules available: l10n_sa_hr_payroll, etc.
# For custom Hijri display, use the 'hijri' PyPI package:
# pip install hijri-converter
from hijri_converter import convert
hijri_date = convert.Gregorian(2024, 1, 15).to_hijri()
# Returns: Hijri(1445, 6, 4)
```

---

## 3. Number Formats by Language

### Decimal and Thousands Separators

| Language | Decimal Sep | Thousands Sep | Example |
|----------|-------------|---------------|---------|
| `ar` / `ar_SA` | `.` | `,` | `1,234,567.89` |
| `en_US` | `.` | `,` | `1,234,567.89` |
| `en_GB` | `.` | `,` | `1,234,567.89` |
| `fr` / `fr_FR` | `,` | ` ` (space) | `1 234 567,89` |
| `de` / `de_DE` | `,` | `.` | `1.234.567,89` |
| `tr` | `,` | `.` | `1.234.567,89` |
| `es` | `,` | `.` | `1.234.567,89` |
| `pt_BR` | `,` | `.` | `1.234.567,89` |

### Odoo Number Field Configuration

```python
# Odoo applies number formatting based on user's language settings
# Stored in res.lang per language

lang = self.env['res.lang'].search([('code', '=', 'fr')])
print(lang.decimal_point)     # ',' for French
print(lang.thousands_sep)     # ' ' (non-breaking space) for French
print(lang.grouping)          # '[3, 0]' — group by 3 digits

# To format a number in Python respecting language:
from odoo.tools.misc import formatLang
amount_str = formatLang(self.env, 1234567.89, digits=2)
# Returns '1,234,567.89' for en_US, '1 234 567,89' for fr
```

---

## 4. Currency Display by Language

### Currency Position (Symbol Before or After Amount)

| Language | Position | Example |
|----------|----------|---------|
| `ar` (SAR) | After | `١٥٠.٠٠ ر.س` or `150.00 SAR` |
| `ar` (AED) | After | `١٥٠.٠٠ د.إ` or `150.00 AED` |
| `en_US` (USD) | Before | `$150.00` |
| `en_GB` (GBP) | Before | `£150.00` |
| `fr` (EUR) | After | `150,00 €` |
| `de` (EUR) | After | `150,00 €` |
| `tr` (TRY) | Before | `₺150,00` |
| `ja` (JPY) | Before | `¥150` |

### Common Arabic Currencies in Odoo

| Currency | ISO Code | Arabic Symbol | Subunit |
|----------|----------|---------------|---------|
| Saudi Riyal | `SAR` | ر.س | هللة (Halala) |
| UAE Dirham | `AED` | د.إ | فلس (Fils) |
| Kuwaiti Dinar | `KWD` | د.ك | فلس (Fils) — 3 decimal places |
| Bahraini Dinar | `BHD` | .ب.د | فلس (Fils) — 3 decimal places |
| Jordanian Dinar | `JOD` | د.أ | فلس (Fils) — 3 decimal places |
| Egyptian Pound | `EGP` | ج.م | قرش (Piastre) |
| Moroccan Dirham | `MAD` | د.م. | سنتيم (Centime) |
| Iraqi Dinar | `IQD` | ع.د | فلس (Fils) — 3 decimal places |
| Qatari Riyal | `QAR` | ر.ق | درهم (Dirham) |
| Omani Rial | `OMR` | ر.ع. | بيسة (Baisa) — 3 decimal places |

---

## 5. Installing Languages in Odoo

### Via CLI

```bash
# Install a single language
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --load-language=ar \
    --stop-after-init

# Install multiple languages at once
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --load-language=ar,fr,tr \
    --stop-after-init

# Install language AND update translations for existing modules
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --load-language=ar \
    -u all \
    --stop-after-init
```

### Via Odoo Shell

```python
# Interactive shell: python odoo-bin shell -d mydb

# Method 1: Simple language load
self.env['res.lang'].load_lang('ar')
self.env.cr.commit()

# Method 2: Using the base.language.install wizard
wizard = self.env['base.language.install'].create({
    'lang_ids': [(6, 0, [
        self.env.ref('base.lang_ar').id
    ])]
})
wizard.lang_install()
self.env.cr.commit()

# Method 3: Manual activation of inactive language
lang = self.env['res.lang'].with_context(active_test=False).search([
    ('code', '=', 'ar')
])
if lang:
    lang.active = True
    self.env.cr.commit()
```

### Via Odoo Backend UI

1. Go to Settings > Technical > Translations > Languages
2. Click "Add a Language"
3. Select from the dropdown (e.g., "Arabic / العربية")
4. Click "Add"
5. Wait for translation download to complete

---

## 6. Setting User Language

### Via Shell

```python
# Set language for a specific user
user = self.env['res.users'].browse(1)  # Or search for specific user
user.lang = 'ar'
self.env.cr.commit()

# Set for partner (affects email translations)
partner = self.env['res.partner'].browse(user.partner_id.id)
partner.lang = 'ar'
self.env.cr.commit()
```

### Via Backend

1. Go to Settings > Users > Users
2. Open the user record
3. Set the "Language" field
4. Save

---

## 7. Language-Specific Formatting in Python

### Using `babel` for Locale-Aware Formatting

```python
# Odoo includes babel — use it for locale-aware formatting
from babel.dates import format_date, format_datetime
from babel.numbers import format_number, format_currency
from datetime import date, datetime

# Date formatting
formatted_date = format_date(date.today(), format='long', locale='ar_SA')
# e.g., '15 يناير 2024'

formatted_date_en = format_date(date.today(), format='long', locale='en_US')
# e.g., 'January 15, 2024'

# Number formatting
formatted_num = format_number(1234567.89, locale='ar_SA')
# e.g., '1,234,567.89' (Arabic uses Western numerals in most business contexts)

# Currency formatting
formatted_currency = format_currency(1500.00, 'SAR', locale='ar_SA')
# e.g., '1,500.00 ر.س.'

formatted_currency_en = format_currency(1500.00, 'USD', locale='en_US')
# e.g., '$1,500.00'
```

### Using Odoo's Built-in Formatters

```python
from odoo.tools.misc import formatLang, format_date

# Format using Odoo's formatLang (respects user's language settings)
env = self.env  # or env with lang context

# Currency amount
formatted = formatLang(env, 1500.00, currency_obj=currency_record)

# Percentage
formatted_pct = formatLang(env, 15.5, digits=1) + '%'

# In report context (language from partner)
partner_env = env(context={'lang': partner.lang})
formatted = formatLang(partner_env, amount, currency_obj=currency)
```

---

## 8. Website Language URLs

### Default Odoo URL Patterns

```
/                    → Default language (depends on website settings)
/en/                 → English
/ar/                 → Arabic (RTL activated automatically)
/fr/                 → French
/tr/                 → Turkish

# Or with language code as query param:
/?lang=ar
/?lang=en_US
```

### Language Switcher URLs

```python
# Generate language-switch URL in Python controller
from odoo import http
from odoo.http import request

class MyController(http.Controller):
    @http.route('/my/page', auth='public', website=True)
    def my_page(self, **kwargs):
        # Get available languages for this website
        langs = request.website.language_ids
        current_lang = request.lang

        return request.render('my_module.my_page', {
            'languages': langs,
            'current_lang': current_lang,
        })
```

```xml
<!-- Language switcher in template -->
<div class="language-switcher">
    <t t-foreach="languages" t-as="lang">
        <a t-att-href="'/web/set_lang?lang=%s&amp;next=%s' % (lang.code, request.httprequest.url)"
           t-att-class="'lang-btn' + (' active' if lang == current_lang else '')">
            <span t-field="lang.name"/>
        </a>
    </t>
</div>
```

---

## 9. Translation Loading Order and Priority

When Odoo loads translations, it follows this priority (highest wins):

1. **User overrides** — Edited via Settings > Technical > Translations > Translated Terms
2. **Module `.po` file** — From `module/i18n/lang.po`
3. **Base module translations** — From `odoo/addons/base/i18n/`
4. **Odoo Community translations** — Downloaded from Transifex during language install
5. **Source string** — Fallback when no translation found

### Forcing Translation Reload

```bash
# Reload translations from .po files (after editing)
python -m odoo -c conf/myproject.conf \
    -d mydb \
    -u my_module \
    --stop-after-init

# Force overwrite (wipes user edits for this module)
python odoo-bin -c conf/myproject.conf \
    -d mydb \
    --i18n-import=my_module/i18n/ar.po \
    --language=ar \
    --modules=my_module \
    --i18n-overwrite \
    --stop-after-init
```

---

## 10. Language Configuration in odoo.conf

```ini
[options]
# Default language for new databases
default_lang = ar

# Supported languages (informational, doesn't restrict)
; No specific config for languages — all are supported via language install

# Timezone affects date display
; timezone = Asia/Riyadh  # For Saudi Arabia
; timezone = Asia/Dubai   # For UAE
; timezone = Europe/Paris # For France
; timezone = Europe/Istanbul # For Turkey
```

### Important Timezones for Arabic Regions

| Country | Timezone |
|---------|----------|
| Saudi Arabia | `Asia/Riyadh` (UTC+3) |
| UAE | `Asia/Dubai` (UTC+4) |
| Kuwait | `Asia/Kuwait` (UTC+3) |
| Qatar | `Asia/Qatar` (UTC+3) |
| Bahrain | `Asia/Bahrain` (UTC+3) |
| Egypt | `Africa/Cairo` (UTC+2, DST varies) |
| Jordan | `Asia/Amman` (UTC+2/3) |
| Lebanon | `Asia/Beirut` (UTC+2/3) |
| Morocco | `Africa/Casablanca` (UTC+0/1) |
| Algeria | `Africa/Algiers` (UTC+1) |
| Turkey | `Europe/Istanbul` (UTC+3) |

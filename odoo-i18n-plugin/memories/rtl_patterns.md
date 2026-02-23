# RTL Layout Patterns — Arabic & Right-to-Left Language Reference

This memory file contains production-ready patterns for implementing RTL (right-to-left) layouts in Odoo website themes and backend views, with a focus on Arabic. These patterns are critical for Arabic-language Odoo deployments.

---

## 1. How RTL Works in Odoo

### Automatic RTL Activation

Odoo automatically adds `dir="rtl"` to the `<html>` tag when the active language is RTL (Arabic, Hebrew, Farsi, Urdu). This triggers:
- Bootstrap RTL CSS loading (Odoo 16+)
- CSS `[dir="rtl"]` selectors to activate
- Logical CSS properties to reverse automatically

**You do NOT need to hardcode `dir="rtl"` in templates** — Odoo sets it based on the active language.

### Verifying RTL Activation

```javascript
// JavaScript: detect RTL at runtime
const isRtl = document.documentElement.getAttribute('dir') === 'rtl';
const lang = document.documentElement.lang;  // e.g., 'ar', 'ar_SA'
```

```python
# Python: check if language is RTL
lang = self.env['res.lang'].search([('code', '=', 'ar')])
is_rtl = lang.direction == 'rtl'
```

---

## 2. HTML Structure for RTL

### Base Layout

```html
<!-- Odoo sets dir and lang automatically on <html> — don't hardcode -->
<!-- The layout below shows what Odoo generates for Arabic users -->
<html lang="ar" dir="rtl">
<head>
    <!-- Bootstrap RTL CSS (Odoo 16+ auto-loads this for RTL languages) -->
    <link rel="stylesheet"
          href="/web/static/lib/bootstrap/css/bootstrap.rtl.min.css"/>
</head>
<body>
    <!-- Content flows right-to-left -->
</body>
</html>
```

### Manual RTL for Sections (in LTR pages)

```html
<!-- When you need an RTL section inside a generally LTR page -->
<div dir="rtl" lang="ar" class="arabic-content">
    <h2>عنوان القسم</h2>
    <p>محتوى النص باللغة العربية</p>
</div>
```

### Bilingual Layout Pattern

```html
<div class="bilingual-section py-5">
    <div class="container">
        <div class="row align-items-center g-4">
            <!-- English side (LTR) -->
            <div class="col-md-6" dir="ltr" lang="en">
                <h2 class="text-start">Welcome</h2>
                <p class="text-start">We provide excellent services.</p>
            </div>
            <!-- Arabic side (RTL) -->
            <div class="col-md-6" dir="rtl" lang="ar">
                <h2 class="text-end">أهلاً وسهلاً</h2>
                <p class="text-end">نقدم خدمات متميزة.</p>
            </div>
        </div>
    </div>
</div>
```

---

## 3. Bootstrap RTL Setup

### Bootstrap 5.1.3 RTL (Odoo 16+)

Odoo 16+ ships with Bootstrap 5.1.3 which has full RTL support. The RTL CSS file is auto-loaded:

```xml
<!-- In your theme's manifest or ir_asset.xml -->
<!-- Odoo handles this automatically — no manual loading needed -->
<!-- But if you need to explicitly load RTL Bootstrap: -->
<record id="asset_bootstrap_rtl" model="ir.asset">
    <field name="name">Bootstrap RTL</field>
    <field name="bundle">web.assets_frontend</field>
    <field name="path">/web/static/lib/bootstrap/css/bootstrap.rtl.min.css</field>
    <field name="directive">append</field>
</record>
```

### Bootstrap RTL Classes That Work Automatically

```html
<!-- These Bootstrap classes automatically mirror in RTL: -->
<div class="text-start">text-start = right in RTL</div>     <!-- Logical start -->
<div class="text-end">text-end = left in RTL</div>          <!-- Logical end -->
<div class="ms-3">ms-3 = margin-inline-start</div>          <!-- Start margin -->
<div class="me-3">me-3 = margin-inline-end</div>            <!-- End margin -->
<div class="ps-3">ps-3 = padding-inline-start</div>         <!-- Start padding -->
<div class="pe-3">pe-3 = padding-inline-end</div>           <!-- End padding -->
<div class="float-start">float-start = right float in RTL</div>
<div class="float-end">float-end = left float in RTL</div>
```

---

## 4. CSS Logical Properties (Modern Approach)

Instead of physical `left`/`right`, use logical properties that automatically adapt:

```scss
// PHYSICAL (old way — requires RTL overrides):
.card {
    margin-left: 1rem;       // Always left, regardless of direction
    padding-right: 1.5rem;   // Always right, regardless of direction
    border-left: 3px solid;  // Always left border
    text-align: left;        // Always left-aligned
}

// LOGICAL (new way — automatically mirrors in RTL):
.card {
    margin-inline-start: 1rem;    // = margin-left LTR | margin-right RTL
    padding-inline-end: 1.5rem;   // = padding-right LTR | padding-left RTL
    border-inline-start: 3px solid; // = border-left LTR | border-right RTL
    text-align: start;            // = left LTR | right RTL
}

// Additional logical properties:
.element {
    margin-block-start: 1rem;     // = margin-top (same in both directions)
    margin-block-end: 0.5rem;     // = margin-bottom (same in both directions)
    padding-inline: 1rem 2rem;    // start end (inline axis)
    padding-block: 0.5rem 1rem;   // top bottom (block axis)
    inset-inline-start: 0;        // = left: 0 LTR | right: 0 RTL
    inset-inline-end: auto;       // = right: auto LTR | left: auto RTL
}
```

---

## 5. SCSS RTL Override Patterns

### Global RTL Override File Structure

```scss
// In static/src/scss/rtl.scss (or include in main stylesheet)

// ============================================================
// NAVIGATION
// ============================================================
[dir="rtl"] {
    .navbar-nav {
        padding-right: 0;
        padding-left: inherit;
    }

    .navbar-collapse {
        text-align: right;
    }

    .navbar-nav .dropdown-menu {
        text-align: right;
        right: 0;
        left: auto;
    }

    .navbar-nav .dropdown-menu-end {
        right: auto;
        left: 0;
    }

    // Hamburger button position
    .navbar-toggler {
        margin-left: auto;
        margin-right: 0;
    }
}

// ============================================================
// BREADCRUMB
// ============================================================
[dir="rtl"] {
    .breadcrumb-item + .breadcrumb-item {
        padding-left: 0;
        padding-right: var(--bs-breadcrumb-item-padding-x);
    }

    .breadcrumb-item + .breadcrumb-item::before {
        float: right;
        padding-right: 0;
        padding-left: var(--bs-breadcrumb-item-padding-x);
        content: "/";  // Or use a reversed arrow
    }
}

// ============================================================
// FORM ELEMENTS
// ============================================================
[dir="rtl"] {
    // Label alignment
    .form-label {
        text-align: right;
        display: block;
    }

    // Required asterisk (if using Bootstrap form validation)
    .form-control {
        text-align: right;
    }

    // Checkboxes and radios
    .form-check {
        padding-left: 0;
        padding-right: 1.5em;
    }

    .form-check-input {
        float: right;
        margin-left: 0;
        margin-right: -1.5em;
    }

    // Input group (search, add-on buttons)
    .input-group:not(.has-validation) > :not(:last-child):not(.dropdown-toggle):not(.dropdown-menu) {
        border-top-right-radius: var(--bs-border-radius) !important;
        border-bottom-right-radius: var(--bs-border-radius) !important;
        border-top-left-radius: 0 !important;
        border-bottom-left-radius: 0 !important;
    }

    .input-group > :not(:first-child):not(.dropdown-menu):not(.valid-tooltip):not(.valid-feedback):not(.invalid-tooltip):not(.invalid-feedback) {
        border-top-left-radius: var(--bs-border-radius) !important;
        border-bottom-left-radius: var(--bs-border-radius) !important;
        border-top-right-radius: 0 !important;
        border-bottom-right-radius: 0 !important;
        margin-left: 0;
        margin-right: -1px;
    }
}

// ============================================================
// TABLES
// ============================================================
[dir="rtl"] {
    table {
        text-align: right;
    }

    th {
        text-align: right;
    }

    // Table action buttons
    td.o_list_record_selector {
        text-align: center;
    }

    // Sortable columns
    .o_column_sortable .o_sort_down,
    .o_column_sortable .o_sort_up {
        margin-left: 0;
        margin-right: 4px;
    }
}

// ============================================================
// CARDS
// ============================================================
[dir="rtl"] {
    .card-header {
        text-align: right;
    }

    .card-body {
        text-align: right;
    }

    // Horizontal card (image + content)
    .card-horizontal {
        flex-direction: row-reverse;
    }
}

// ============================================================
// ICONS — Font Awesome Directional
// ============================================================
[dir="rtl"] {
    // Chevrons
    .fa-chevron-left::before { content: "\f054"; }   // Swap to right
    .fa-chevron-right::before { content: "\f053"; }  // Swap to left
    .fa-angle-left::before { content: "\f105"; }     // Swap to right
    .fa-angle-right::before { content: "\f104"; }    // Swap to left

    // Arrows
    .fa-arrow-left::before { content: "\f061"; }     // Swap to right
    .fa-arrow-right::before { content: "\f060"; }    // Swap to left
    .fa-long-arrow-left::before { content: "\f178"; }
    .fa-long-arrow-right::before { content: "\f177"; }

    // Carets
    .fa-caret-left::before { content: "\f0d7"; }     // Swap
    .fa-caret-right::before { content: "\f0d9"; }    // Swap

    // Reply / Forward
    .fa-reply::before { content: "\f064"; }          // Swap with share
    .fa-share::before { content: "\f112"; }          // Swap with reply
}

// ============================================================
// FOOTER
// ============================================================
[dir="rtl"] {
    footer .footer-links {
        text-align: right;
    }

    footer .social-links {
        justify-content: flex-start;  // In RTL flex, this becomes right
    }

    // Contact info
    footer .contact-item {
        flex-direction: row-reverse;
        text-align: right;
    }

    footer .contact-item .fa {
        margin-right: 0;
        margin-left: 8px;
    }
}

// ============================================================
// PAGINATION
// ============================================================
[dir="rtl"] {
    .pagination {
        flex-direction: row-reverse;
    }

    .page-item:first-child .page-link {
        border-radius: 0 var(--bs-border-radius) var(--bs-border-radius) 0;
    }

    .page-item:last-child .page-link {
        border-radius: var(--bs-border-radius) 0 0 var(--bs-border-radius);
    }
}

// ============================================================
// DROPDOWN MENUS
// ============================================================
[dir="rtl"] {
    .dropdown-menu {
        text-align: right;
    }

    .dropdown-item {
        text-align: right;
    }

    // Dropdown caret/arrow position
    .dropdown-toggle::after {
        margin-left: 0;
        margin-right: 0.255em;
    }
}

// ============================================================
// ALERTS AND TOASTS
// ============================================================
[dir="rtl"] {
    .alert {
        text-align: right;
    }

    .alert-dismissible .btn-close {
        left: 0;
        right: auto;
    }

    .toast-header .btn-close {
        margin-left: -0.375rem;
        margin-right: auto;
    }
}

// ============================================================
// PROGRESS BARS
// ============================================================
[dir="rtl"] {
    .progress-bar {
        // Progress bars naturally fill RTL in some browsers
        // If issues arise, add explicit transform
    }
}
```

---

## 6. Flexbox in RTL

Flexbox automatically mirrors in RTL — items in `flex-direction: row` flow right-to-left:

```scss
// In LTR: [Item 1] [Item 2] [Item 3]
// In RTL: [Item 3] [Item 2] [Item 1]  (automatic)

.my-flex-container {
    display: flex;
    flex-direction: row;  // Items automatically RTL when dir="rtl"
    gap: 1rem;
    justify-content: flex-start;  // = right-side in RTL
}

// If you need to FORCE LTR order in RTL context:
[dir="rtl"] .force-ltr-order {
    flex-direction: row-reverse;  // Counter the automatic RTL reversal
}

// If you need items in a specific RTL order using order:
[dir="rtl"] .col-logo { order: 3; }    // Leftmost in visual RTL
[dir="rtl"] .col-nav { order: 2; }
[dir="rtl"] .col-cta { order: 1; }    // Rightmost in visual RTL
```

---

## 7. JavaScript RTL Detection and Handling

### Detect RTL in publicWidget

```javascript
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.RTLAwareSlider = publicWidget.Widget.extend({
    selector: '.hero-slider',

    start: function () {
        this.isRtl = document.documentElement.getAttribute('dir') === 'rtl';
        this.lang = document.documentElement.lang || 'en';

        this._initSlider();
        return this._super.apply(this, arguments);
    },

    _initSlider: function () {
        const sliderOptions = {
            // Reverse slide direction for RTL
            rtl: this.isRtl,
            // Swipe direction also reverses in RTL
            swipe: true,
        };

        if (this.isRtl) {
            // Additional RTL-specific initializations
            this.$('.slider-prev').addClass('slider-btn-rtl-prev');
            this.$('.slider-next').addClass('slider-btn-rtl-next');
        }

        // Initialize your slider (e.g., Swiper, Slick)
        this._initSwiper(sliderOptions);
    },

    _initSwiper: function (options) {
        // Example with Swiper.js
        if (typeof Swiper !== 'undefined') {
            this._swiper = new Swiper(this.el, {
                ...options,
                loop: true,
                autoplay: { delay: 5000 },
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
            });
        }
    },

    destroy: function () {
        if (this._swiper) {
            this._swiper.destroy();
        }
        this._super.apply(this, arguments);
    },
});
```

### Toggle RTL Class Dynamically

```javascript
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.LanguageSwitcher = publicWidget.Widget.extend({
    selector: '.language-switcher',

    events: {
        'click [data-lang]': '_onLanguageSwitch',
    },

    start: function () {
        this._super.apply(this, arguments);
        this._highlightCurrentLang();
    },

    _highlightCurrentLang: function () {
        const currentLang = document.documentElement.lang || 'en';
        this.$('[data-lang]').removeClass('active');
        this.$('[data-lang="' + currentLang + '"]').addClass('active');
        this.$('[data-lang="' + currentLang.split('_')[0] + '"]').addClass('active');
    },

    _onLanguageSwitch: function (ev) {
        ev.preventDefault();
        const lang = $(ev.currentTarget).data('lang');
        const RTL_LANGUAGES = ['ar', 'ar_SA', 'ar_AE', 'he', 'fa', 'ur'];
        const willBeRtl = RTL_LANGUAGES.some(rtlLang => lang.startsWith(rtlLang.split('_')[0]));

        // Odoo handles the actual language switch via URL/cookie
        // This just updates the UI immediately for smoother UX
        document.documentElement.setAttribute('lang', lang);
        if (willBeRtl) {
            document.documentElement.setAttribute('dir', 'rtl');
        } else {
            document.documentElement.setAttribute('dir', 'ltr');
        }

        // Navigate to language switch URL
        const nextUrl = window.location.href;
        window.location.href = `/web/set_lang?lang=${lang}&next=${encodeURIComponent(nextUrl)}`;
    },
});
```

---

## 8. Arabic Number Handling

### Arabic vs Western Numerals

Arabic uses two numeral systems:
- Western Arabic: 0 1 2 3 4 5 6 7 8 9 (used in most Arabic digital content)
- Eastern Arabic: ٠ ١ ٢ ٣ ٤ ٥ ٦ ٧ ٨ ٩ (traditional Arabic numerals)

For Odoo applications, Western Arabic numerals (0-9) are strongly recommended for:
- Currency amounts
- Order numbers
- Dates (when displayed in Gregorian calendar)
- Phone numbers

```scss
// Force Western numerals in Arabic context
[dir="rtl"] {
    .price, .amount, .quantity, .phone, .order-ref {
        direction: ltr;
        unicode-bidi: embed;
        text-align: left;  // Numbers read left-to-right
    }

    // Odoo backend amount fields
    .o_field_float,
    .o_field_monetary,
    .o_field_integer {
        direction: ltr;
        unicode-bidi: isolate;
        text-align: right;  // Right-align in column but LTR digit order
    }
}
```

```python
# In Python: format amounts respecting locale
from odoo.tools.misc import formatLang
from babel.numbers import format_number

# Odoo's built-in formatter handles locale automatically
formatted = formatLang(self.env, amount, currency_obj=currency)

# Manual locale formatting with Babel
import locale
# For Arabic locale, use 'ar_SA' or 'ar_AE' based on country
formatted = format_number(amount, locale='ar_SA', decimal_quantization=False)
```

---

## 9. RTL in QWeb Reports (PDF)

RTL in PDF reports requires `wkhtmltopdf` with RTL support:

```xml
<!-- In report template -->
<t t-call="web.html_container">
    <div class="article" dir="rtl" lang="ar">
        <!-- Report content in Arabic -->
        <table class="table" style="direction: rtl; text-align: right;">
            <thead>
                <tr>
                    <th style="text-align: right;">الوصف</th>
                    <th style="text-align: right; width: 100px;">الكمية</th>
                    <th style="text-align: right; width: 120px;">السعر</th>
                    <th style="text-align: right; width: 120px;">الإجمالي</th>
                </tr>
            </thead>
        </table>
    </div>
</t>
```

```python
# In report action, set paper format and language
class ReportAction(models.AbstractModel):
    _name = 'report.my_module.my_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['my.model'].browse(docids)
        lang = docs[0].partner_id.lang if docs else 'ar'
        return {
            'docs': docs,
            'lang': lang,
            'is_rtl': lang.startswith('ar'),
        }
```

---

## 10. Common RTL Issues and Fixes

### Issue: Navigation Menu Items Overlapping

```scss
[dir="rtl"] .navbar .navbar-nav {
    flex-direction: row;     // Keep horizontal
    margin-right: auto;      // Push to right side (was margin-left: auto in LTR)
    margin-left: 0;
}
```

### Issue: Dropdown Opens in Wrong Direction

```scss
[dir="rtl"] .navbar-nav .dropdown-menu {
    left: auto !important;
    right: 0 !important;
}

[dir="rtl"] .dropdown-menu-end {
    right: auto !important;
    left: 0 !important;
}
```

### Issue: Search Bar Icon on Wrong Side

```scss
[dir="rtl"] .search-bar .search-icon {
    right: auto;
    left: 10px;   // Move icon to left side in RTL
}

[dir="rtl"] .search-bar input {
    padding-right: 12px;   // Normal left padding
    padding-left: 40px;    // Make room for icon on left
}
```

### Issue: Carousel/Slider Going Wrong Direction

```javascript
// Detect RTL and pass to slider initialization
const isRtl = document.documentElement.dir === 'rtl';
// Pass rtl: isRtl to your slider library
```

### Issue: Text Alignment in Mixed Content

```scss
// For elements that contain BOTH Arabic and English
.mixed-content {
    // Use unicode-bidi: plaintext to let browser auto-detect per paragraph
    unicode-bidi: plaintext;
}

// For purely English content embedded in Arabic page
.english-only {
    direction: ltr;
    unicode-bidi: isolate;
    text-align: left;
}
```

### Issue: Form Validation Error Position

```scss
[dir="rtl"] {
    .invalid-feedback {
        text-align: right;
    }

    .valid-feedback {
        text-align: right;
    }

    // Error icon position
    .form-control.is-invalid {
        background-position: left calc(0.375em + 0.1875rem) center;
        padding-left: calc(1.5em + 0.75rem);
        padding-right: 0.75rem;
    }
}
```

---

## 11. Testing RTL Layouts

### Switching to Arabic in Development

```bash
# Quick switch: set language via URL parameter (Odoo website)
http://localhost:8069/ar/

# Or set language in user preferences:
Settings > Users > User > Language: Arabic
```

### Browser DevTools RTL Testing

```javascript
// In browser console — instant RTL toggle for testing
document.documentElement.setAttribute('dir', 'rtl');
document.documentElement.setAttribute('lang', 'ar');

// Revert:
document.documentElement.setAttribute('dir', 'ltr');
document.documentElement.setAttribute('lang', 'en');
```

### Checklist for RTL Review

- [ ] Navigation: items flow right-to-left
- [ ] Dropdown menus: open to the left
- [ ] Forms: labels right-aligned, inputs right-to-left
- [ ] Tables: headers and data right-aligned
- [ ] Icons/arrows: directional icons reversed
- [ ] Footer: columns in correct visual order
- [ ] Carousel/slider: slides in correct direction
- [ ] Numbers/amounts: Western numerals, left-to-right digit order
- [ ] PDF reports: correct RTL direction in printed output
- [ ] Email templates: correct direction in email clients

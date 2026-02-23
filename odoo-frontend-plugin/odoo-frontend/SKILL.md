---
name: odoo-frontend
description: "Advanced Odoo frontend development with comprehensive theme development, /create-theme command, theme.utils activation system, complete dynamic page reference (headers, footers, shop, blog), design workflow methodology, PWA support, modern JavaScript/TypeScript, testing frameworks, performance optimization, accessibility compliance, and real-time features. Features complete $o-website-values-palettes reference, theme mirror model architecture, publicWidget patterns with editableMode handling, and MCP integration. Supports Odoo 14-19 with auto-detection."
version: "7.0.0"
author: "TAQAT Techno"
license: "MIT"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - WebFetch
metadata:
  odoo-versions: ["14", "15", "16", "17", "18", "19"]
  bootstrap-versions: ["4.x", "5.1.3"]
  javascript-features: ["ES2020+", "TypeScript", "Owl v1/v2", "Web Components", "publicWidget"]
  testing-frameworks: ["Jest", "Cypress", "BackstopJS"]
  performance-tools: ["Core Web Vitals", "Lighthouse", "Vite"]
  accessibility: ["WCAG 2.1 AA", "ARIA", "Screen Readers"]
  real-time: ["WebSockets", "SSE", "Push Notifications"]
  mcp-tools: ["claude-in-chrome", "figma", "chrome-devtools", "filesystem"]
  theme-features: ["o-website-values-palettes", "mirror-models", "snippet-groups", "color-palettes"]
---

# Odoo Frontend Development Skill v6.0

## Overview

This skill provides advanced Odoo frontend development capabilities with:
- **🎨 /create-theme Command**: Generate complete production-ready theme modules with all files
- **🔧 Theme Feature Activation**: `theme.utils` model with `_theme_xxx_post_copy()` for template configuration
- **📋 Complete Dynamic Page Reference**: All 11 headers, 9 footers, shop, product, blog templates with XML IDs
- **🎯 Design Workflow**: Figma → Odoo template matching → configuration → enhancement methodology
- **Theme Development**: Complete `$o-website-values-palettes` reference, color semantics, theme mirror models
- **Auto-detection**: Automatically detect Odoo version and map to correct Bootstrap version
- **publicWidget Framework**: Comprehensive patterns with `editableMode` handling for website builder
- **Progressive Web Apps**: Service Workers, offline support, push notifications
- **Modern JavaScript**: TypeScript, ES2020+, Web Components, Owl v1/v2 patterns
- **Testing Frameworks**: Jest, Cypress, visual regression testing
- **Performance Optimization**: Core Web Vitals, resource hints, critical CSS
- **Accessibility**: WCAG 2.1 AA compliance, ARIA patterns, keyboard navigation
- **Real-time Features**: WebSockets, Server-Sent Events, live collaboration
- **MCP Integration**: Figma design conversion and Chrome DevTools style extraction
- **Theme Scaffolding**: Complete theme module generation with proper structure
- **Version-Aware**: Handle differences between Odoo 14-19 (Bootstrap 4/5, Owl v1/v2, Snippet structures)
- **DevOps Ready**: CI/CD pipelines, Vite builds, automated testing

---

## 🎨 /create-theme Command

**Quick Start**: Generate a complete, production-ready Odoo theme module.

### Usage

```bash
# Interactive mode (recommended)
/create-theme

# Quick mode with arguments
/create-theme <theme_name> <project_path>

# Full arguments
/create-theme <theme_name> <project_path> --version=17 --colors="#207AB7,#FB9F54,#F6F4F0,#FFFFFF,#191A19" --font="IBM Plex Sans"
```

### What Gets Created

```
theme_<name>/
├── __init__.py
├── __manifest__.py
├── security/
│   └── ir.model.access.csv
├── data/
│   ├── assets.xml
│   ├── menu.xml
│   └── pages/                        # Individual page files (BEST PRACTICE!)
│       ├── home_page.xml            # Homepage (inherits website.homepage)
│       ├── aboutus_page.xml         # About Us page
│       ├── contactus_page.xml       # Contact (inherits website.contactus)
│       └── services_page.xml        # Services page
├── views/
│   ├── layout/
│   │   ├── header.xml               # Header customization (OPTIONAL)
│   │   ├── footer.xml               # Footer customization (OPTIONAL)
│   │   └── templates.xml            # Base layout templates
│   └── snippets/
│       └── custom_snippets.xml      # Custom snippet definitions
└── static/src/
    ├── scss/
    │   ├── primary_variables.scss   # Theme variables + fonts
    │   ├── bootstrap_overridden.scss # Bootstrap overrides (OPTIONAL)
    │   └── theme.scss               # Additional custom styles
    ├── js/
    │   ├── theme.js                 # publicWidget implementations
    │   └── snippets_options.js      # Snippet options (if needed)
    └── img/
```

### 💡 Simplified Approach (Recommended)

In MOST cases, you can configure via `$o-website-values-palettes` without custom XML:
- `'header-template'`: `'default'` | `'hamburger'` | `'vertical'` | `'sidebar'`
- `'footer-template'`: `'default'` | `'centered'` | `'minimalist'` | `'links'` | `'descriptive'`

**When to use custom header.xml/footer.xml:**
- Design requires completely custom layout not available in templates
- Need additional HTML elements beyond what templates provide

### Color System (o-color-1 to o-color-5)

| Variable | Semantic Meaning | Default |
|----------|------------------|---------|
| `o-color-1` | Primary brand color | #207AB7 |
| `o-color-2` | Secondary/accent | #FB9F54 |
| `o-color-3` | Light backgrounds | #F6F4F0 |
| `o-color-4` | White/body base | #FFFFFF |
| `o-color-5` | Dark text/headings | #191A19 |

### Version Support

- **Odoo 14-15**: Bootstrap 4.5.0, simple snippets
- **Odoo 16-17**: Bootstrap 5.1.3, modern asset bundles
- **Odoo 18-19**: Bootstrap 5.1.3, snippet groups required

### Run Script Directly

```bash
python scripts/create_theme.py <theme_name> <output_path> --version=17 --colors="#207AB7,#FB9F54,#F6F4F0,#FFFFFF,#191A19"
```

---

## CRITICAL RULES

1. **NEVER edit core Odoo** in `odoo/` or `odoo/addons/` directories
2. **No inline JS/CSS** - Create separate `.js` and `.scss` files
3. **JS modules**: Use `/** @odoo-module **/` annotation
4. **Website themes**: Use `publicWidget` framework ONLY (not Owl or vanilla JS)
5. **Bootstrap**: Use v5.1.3 classes for Odoo 16+ (never Tailwind)
6. **Module naming**: Use `snake_case` convention
7. **Translations**: Wrap static labels in JS arrays/constants with `_t()` AT DEFINITION TIME (not via runtime wrappers). Static XML strings are auto-translated.

## Auto-Detection Workflow

### Step 1: Detect Odoo Version

When starting any frontend task, first detect the Odoo version:

```python
# Use the version detector script
python scripts/version_detector.py <module_path>
```

The version detector will:
1. Look for `__manifest__.py` or `__openerp__.py`
2. Parse the version field
3. If not found, detect from parent directory (e.g., `odoo17/`)
4. Return:
   - Odoo version (e.g., "17.0")
   - Bootstrap version (e.g., "5.1.3")
   - Owl version (e.g., "2.x" or None)
   - Module type (theme, website, custom)

### Step 2: Bootstrap Version Mapping

**Automatic Bootstrap Version Selection:**
- Odoo 14-15: Bootstrap 4.5.0
- Odoo 16-19: Bootstrap 5.1.3

### Step 3: Owl Version Detection

**JavaScript Framework Selection:**
- Odoo 14-15: Owl experimental or jQuery only
- Odoo 16-17: Owl v1
- Odoo 18-19: Owl v2 (with breaking changes)

### Step 4: Snippet Structure Detection

**Snippet Registration Method:**
- Odoo 14-17: Simple snippet insertion without groups
- Odoo 18-19: Snippet groups required (`snippet_structure` with groups)

## Complete Theme Variables Reference

This section provides complete documentation for the three core SCSS variable systems used in Odoo themes.

---

### 📚 1. $o-theme-font-configs - Google Fonts Configuration

`$o-theme-font-configs` defines available fonts for Odoo website themes with automatic Google Fonts import.

#### Structure

```scss
$o-theme-font-configs: (
    '<Font Name>': (
        'family': (<CSS font-family list>),     // Required: Font family with fallbacks
        'url': '<Google Fonts parameter>',       // Required*: Google Fonts query param ONLY
        'properties': (                          // Optional: Per-context CSS overrides
            '<font-alias>': (
                '<website-value-key>': <value>,
            ),
        ),
    ),
);
```

**⚠️ CRITICAL**: The `'url'` key contains **only the query parameter**, NOT the full URL!

```scss
// ✅ CORRECT - Only the font parameter
'url': 'Poppins:300,300i,400,400i,600,600i,700,700i'

// The system generates: https://fonts.googleapis.com/css?family=Poppins:...&display=swap

// ❌ WRONG - Do not include full URL
'url': 'https://fonts.googleapis.com/css?family=Poppins:300,400,700'
```

#### Font Weight Specification

```scss
// Format: FontName:weight1,weight1i,weight2,weight2i,...
//   - Number alone = normal style
//   - Number + 'i' = italic style

'url': 'Poppins:300,300i,400,400i,600,600i,700,700i'
//      Light  Light-i  Regular Regular-i SemiBold ...
```

#### Multiple Word Font Names

```scss
// Replace spaces with +
'url': 'Open+Sans:300,300i,400,400i,700,700i'
'url': 'Source+Sans+Pro:300,300i,400,400i,700,700i'
'url': 'DM+Serif+Display:400,400i'
```

#### Font Aliases (for 'properties' key)

| Alias | Maps To | Usage |
|-------|---------|-------|
| `'base'` | `'font'` | Body text |
| `'headings'` | `'headings-font'` | All headings (H1-H6) |
| `'h2'` - `'h6'` | `'h2-font'` - `'h6-font'` | Individual headings |
| `'navbar'` | `'navbar-font'` | Navigation menu |
| `'buttons'` | `'buttons-font'` | Button text |
| `'display-1'` - `'display-4'` | `'display-1-font'` - `'display-4-font'` | Display text |

#### Complete Example

```scss
// ⚠️ STANDALONE definition - NO map-merge with core variables!
$o-theme-font-configs: (
    'Poppins': (
        'family': ('Poppins', sans-serif),
        'url': 'Poppins:300,300i,400,400i,500,500i,600,600i,700,700i',
        'properties': (
            'base': (
                'font-size-base': (15 / 16) * 1rem,
                'header-font-size': (15 / 16) * 1rem,
            ),
        ),
    ),
    'Playfair Display': (
        'family': ('Playfair Display', serif),
        'url': 'Playfair+Display:400,400i,700,700i',
    ),
    'Inter': (
        'family': ('Inter', sans-serif),
        'url': 'Inter:300,400,500,600,700',
    ),
);
```

#### Arabic/RTL Font Support

```scss
$o-theme-font-configs: (
    'IBM Plex Sans Arabic': (
        'family': ('IBM Plex Sans Arabic', sans-serif),
        'url': 'IBM+Plex+Sans+Arabic:100,200,300,400,500,600,700',
    ),
    'Cairo': (
        'family': ('Cairo', sans-serif),
        'url': 'Cairo:200,300,400,500,600,700,800,900',
    ),
    'Almarai': (
        'family': ('Almarai', sans-serif),
        'url': 'Almarai:300,400,700,800',
    ),
);
```

---

### 📚 2. $o-color-palettes - Color System

`$o-color-palettes` defines all color palettes with 5 core colors plus component assignments.

#### The Five Core Colors

| Color | Semantic Meaning | Typical Usage |
|-------|------------------|---------------|
| `o-color-1` | **Primary/Accent** | Brand color, buttons, links, highlights |
| `o-color-2` | **Secondary** | Complementary accent, secondary buttons |
| `o-color-3` | **Light Background** | Section backgrounds, cards, light areas |
| `o-color-4` | **White/Lightest** | Main content background (usually #FFFFFF) |
| `o-color-5` | **Dark/Text** | Dark backgrounds, text color, footer |

#### Visual Representation

```
┌─────────────────────────────────────────────────────────┐
│  o-color-4 (White Background)                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  o-color-3 (Light Section)                      │   │
│  │    Text: o-color-5 (Dark)                       │   │
│  │    Links: o-color-1 (Primary)                   │   │
│  │    Buttons: o-color-1 (Primary), o-color-2 (Sec)│   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  o-color-5 (Dark Section - Footer)              │   │
│  │    Text: o-color-4 (White)                      │   │
│  │    Links: o-color-3 (Light)                     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

#### Color Combinations (o_cc1 - o_cc5)

Color combinations are **preset color schemes** that automatically set background, text, headings, links, and buttons.

| Class | Background | Typical Usage |
|-------|------------|---------------|
| `o_cc1` | `o-color-4` (White) | Main content areas |
| `o_cc2` | `o-color-3` (Light) | Alternate sections |
| `o_cc3` | `o-color-2` (Secondary) | Accent sections |
| `o_cc4` | `o-color-1` (Primary) | Call-to-action sections |
| `o_cc5` | `o-color-5` (Dark) | Footer, dark sections |

#### Color Palette Structure

```scss
$o-color-palettes: map-merge($o-color-palettes, (
    'my-palette': (
        // Required: The 5 core colors
        'o-color-1': #09294F,      // Primary (Navy blue)
        'o-color-2': #FFA807,      // Secondary (Orange)
        'o-color-3': #F6F4F0,      // Light background
        'o-color-4': #FFFFFF,      // White
        'o-color-5': #1B212C,      // Dark

        // Component color assignments (1-5 → o_cc1-o_cc5)
        'menu': 1,                 // Menu uses o_cc1
        'footer': 5,               // Footer uses o_cc5
        'copyright': 5,            // Copyright uses o_cc5

        // Color combination overrides
        'o-cc1-text': 'o-color-5',
        'o-cc1-headings': 'o-color-5',
        'o-cc5-link': 'o-color-4',
        'o-cc5-btn-primary': 'o-color-2',
    ),
));
```

#### Override Syntax for Color Combinations

```scss
// Override specific colors within a combination
'o-cc{n}-{property}': value

// Available properties:
'o-cc1-text': #333333,           // Text color
'o-cc1-headings': 'o-color-5',   // Headings color
'o-cc1-link': 'o-color-1',       // Link color
'o-cc1-btn-primary': 'o-color-1', // Primary button
'o-cc1-btn-secondary': 'o-color-2', // Secondary button

// Example for dark background (o_cc5)
'o-cc5-text': rgba(#fff, .8),    // Semi-transparent white
'o-cc5-headings': 'o-color-4',   // White headings
'o-cc5-link': 'o-color-4',       // White links
'o-cc5-btn-primary': 'o-color-2', // Orange buttons on dark
```

#### HTML Usage

```xml
<!-- White background section -->
<section class="o_cc o_cc1 pt32 pb32">
    <div class="container"><h2>Content</h2></div>
</section>

<!-- Light background section -->
<section class="o_cc o_cc2 pt32 pb32">...</section>

<!-- Primary color background (CTA) -->
<section class="o_cc o_cc4 pt32 pb32">...</section>

<!-- Dark background (footer style) -->
<section class="o_cc o_cc5 pt32 pb32">...</section>
```

---

### 📚 3. $o-website-values-palettes - Complete Configuration (115+ Keys)

`$o-website-values-palettes` is the **master configuration variable** controlling Bootstrap components, typography, buttons, inputs, header/footer templates, and much more.

#### Quick Reference by Category

| Category | Keys Count | Description |
|----------|------------|-------------|
| Typography & Fonts | 13 | Font family configuration |
| Font Sizes | 13 | Base and heading sizes |
| Line Heights | 11 | Text spacing |
| Margins | 22 | Heading and paragraph margins |
| Buttons | 17 | Button styling |
| Inputs | 12 | Form field styling |
| Header | 13 | Header/navigation config |
| Footer | 3 | Footer config |
| Links | 1 | Link underline behavior |
| Layout | 3 | Page layout |
| Colors & Gradients | 5 | Color palette and gradients |
| Google Fonts | 2 | Additional font loading |
| **Total** | **115+** | |

#### 3.1 Typography & Fonts

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `'font'` | string | First in config | Base font for entire site |
| `'headings-font'` | string | Inherits `font` | Font for H1-H6 headings |
| `'navbar-font'` | string | Inherits `font` | Font for navigation menu |
| `'buttons-font'` | string | Inherits `font` | Font for button text |
| `'h2-font'` - `'h6-font'` | string | Inherits headings | Individual heading fonts |
| `'display-1-font'` - `'display-4-font'` | string | Inherits headings | Display text fonts |

#### 3.2 Font Sizes

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `'font-size-base'` | size | `1rem` | Base font size (16px) |
| `'small-font-size'` | size | `0.875rem` | Small text (14px) |
| `'h1-font-size'` - `'h6-font-size'` | size | Calculated | Heading sizes |
| `'display-1-font-size'` - `'display-6-font-size'` | size | 5rem-2.5rem | Display sizes |

#### 3.3 Line Heights & Margins

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `'body-line-height'` | number | `1.5` | Body text line height |
| `'headings-line-height'` | number | `1.2` | All headings line height |
| `'h2-line-height'` - `'h6-line-height'` | number | Inherits | Individual heading line heights |
| `'paragraph-margin-top'` | size | `0` | Paragraph top margin |
| `'paragraph-margin-bottom'` | size | `16px` | Paragraph bottom margin |
| `'headings-margin-top'` | size | `0` | Headings top margin |
| `'headings-margin-bottom'` | size | `0.5rem` | Headings bottom margin |
| `'h2-margin-top'` - `'h6-margin-top'` | size | Inherits | Individual margins |
| `'h2-margin-bottom'` - `'h6-margin-bottom'` | size | Inherits | Individual margins |

#### 3.4 Buttons (17 Keys)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `'btn-padding-y'` | size | Bootstrap | Vertical padding |
| `'btn-padding-x'` | size | Bootstrap | Horizontal padding |
| `'btn-font-size'` | size | Bootstrap | Font size |
| `'btn-padding-y-sm'` / `'btn-padding-x-sm'` | size | Bootstrap | Small button padding |
| `'btn-padding-y-lg'` / `'btn-padding-x-lg'` | size | Bootstrap | Large button padding |
| `'btn-font-size-sm'` / `'btn-font-size-lg'` | size | Bootstrap | Size variants |
| `'btn-border-width'` | size | Bootstrap | Border thickness |
| `'btn-border-radius'` | size | Bootstrap | Corner radius |
| `'btn-border-radius-sm'` / `'btn-border-radius-lg'` | size | Bootstrap | Size variant radius |
| `'btn-primary-outline'` | boolean | `false` | Primary as outline |
| `'btn-secondary-outline'` | boolean | `false` | Secondary as outline |
| `'btn-primary-flat'` | boolean | `false` | Flat primary style |
| `'btn-secondary-flat'` | boolean | `false` | Flat secondary style |
| `'btn-ripple'` | boolean | `false` | Material Design ripple |

#### 3.5 Inputs & Forms (12 Keys)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `'input-padding-y'` / `'input-padding-x'` | size | Bootstrap | Input padding |
| `'input-font-size'` | size | Bootstrap | Input font size |
| `'input-padding-y-sm'` / `'input-padding-x-sm'` | size | Bootstrap | Small input padding |
| `'input-padding-y-lg'` / `'input-padding-x-lg'` | size | Bootstrap | Large input padding |
| `'input-border-width'` | size | Bootstrap | Border thickness |
| `'input-border-radius'` | size | Bootstrap | Corner radius |
| `'input-border-radius-sm'` / `'input-border-radius-lg'` | size | Bootstrap | Size variant radius |

#### 3.6 Header & Navigation (13 Keys)

| Key | Type | Values | Default | Description |
|-----|------|--------|---------|-------------|
| `'header-template'` | string | See below | `'default'` | Header layout |
| `'header-links-style'` | string | See below | `'default'` | Nav link styling |
| `'header-font-size'` | size | CSS length | Bootstrap | Header text size |
| `'logo-height'` | size | CSS length | Navbar height | Logo height |
| `'fixed-logo-height'` | size | CSS length | Smaller | Logo when fixed |
| `'hamburger-position'` | string | `'left'`/`'center'`/`'right'` | `'left'` | Desktop position |
| `'hamburger-position-mobile'` | string | `'left'`/`'center'`/`'right'` | `'left'` | Mobile position |
| `'menu-border-width'` | size | CSS length | null | Menu border |
| `'menu-border-radius'` | size | CSS length | null | Menu corners |
| `'menu-box-shadow'` | CSS | shadow/none | null | Menu shadow |
| `'sidebar-width'` | size | CSS length | `18.75rem` | Sidebar width |

**Header Template Options:**
- `'default'` - Standard horizontal navbar
- `'hamburger'` - Hamburger menu (collapsed)
- `'vertical'` - Vertical sidebar navigation
- `'sidebar'` - Full sidebar layout

**Header Links Style Options:**
- `'default'` - Standard links
- `'fill'` - Filled background on hover
- `'outline'` - Outline border on hover
- `'pills'` - Rounded pill-shaped links
- `'block'` - Block-style links
- `'border-bottom'` - Underline border on hover

#### 3.7 Footer (3 Keys)

| Key | Type | Values | Default | Description |
|-----|------|--------|---------|-------------|
| `'footer-template'` | string | Template name | `'default'` | Footer layout |
| `'footer-effect'` | string | See below | `null` | Animation effect |
| `'footer-scrolltop'` | boolean | `true`/`false` | `false` | Scroll-to-top button |

**Footer Template Options:**
- `'default'` - Standard footer
- `'centered'` - Center-aligned
- `'minimalist'` - Clean, minimal
- `'links'` - Link-heavy
- `'descriptive'` - Detailed description

**Footer Effects:**
- `null` - No effect (static)
- `'slideout_slide_hover'` - Slide out on hover
- `'slideout_shadow'` - Shadow on scroll

#### 3.8 Links (1 Key)

| Key | Type | Values | Default | Description |
|-----|------|--------|---------|-------------|
| `'link-underline'` | string | `'never'`/`'hover'`/`'always'` | `'hover'` | Underline behavior |

#### 3.9 Layout (3 Keys)

| Key | Type | Values | Default | Description |
|-----|------|--------|---------|-------------|
| `'layout'` | string | `'full'`/`'boxed'` | `'full'` | Page layout |
| `'body-image'` | URL | Image path | `null` | Background image |
| `'body-image-type'` | string | `'image'`/`'pattern'` | `'image'` | Background type |

#### 3.10 Colors & Gradients (5 Keys)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `'color-palettes-name'` | string | null | Active color palette name |
| `'menu-gradient'` | CSS gradient | null | Menu background gradient |
| `'menu-secondary-gradient'` | CSS gradient | null | Secondary menu gradient |
| `'footer-gradient'` | CSS gradient | null | Footer background gradient |
| `'copyright-gradient'` | CSS gradient | null | Copyright gradient |

#### 3.11 Google Fonts (2 Keys)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `'google-fonts'` | list | null | Additional Google fonts to load |
| `'google-local-fonts'` | map | null | Locally hosted fonts |

---

### Complete Example - Modern Corporate Theme

```scss
$o-website-values-palettes: (
    (
        // === REQUIRED ===
        'color-palettes-name': 'my-corporate-palette',

        // === TYPOGRAPHY ===
        'font': 'Inter',
        'headings-font': 'Inter',
        'navbar-font': 'Inter',
        'buttons-font': 'Inter',
        'font-size-base': 1rem,
        'headings-line-height': 1.3,
        'body-line-height': 1.6,

        // === HEADER (NO custom header.xml needed!) ===
        'header-template': 'default',      // or 'hamburger', 'vertical', 'sidebar'
        'header-links-style': 'default',   // or 'pills', 'fill', 'border-bottom'
        'logo-height': 48px,
        'fixed-logo-height': 36px,

        // === BUTTONS ===
        'btn-padding-y': 0.75rem,
        'btn-padding-x': 1.5rem,
        'btn-padding-y-lg': 1rem,
        'btn-padding-x-lg': 2rem,
        'btn-border-radius': 8px,
        'btn-border-radius-lg': 12px,
        'btn-ripple': true,

        // === INPUTS ===
        'input-padding-y': 0.75rem,
        'input-padding-x': 1rem,
        'input-border-radius': 8px,

        // === FOOTER (NO custom footer.xml needed!) ===
        'footer-template': 'default',      // or 'centered', 'minimalist', 'links'
        'footer-scrolltop': true,

        // === LINKS ===
        'link-underline': 'hover',         // or 'never', 'always'

        // === LAYOUT ===
        'layout': 'full',                  // or 'boxed'
    ),
);
```

### ⚠️ CRITICAL: SCSS Load Order in Odoo Themes

**Theme SCSS files load BEFORE core Odoo variables are defined!**

When you use `prepend` in your manifest's asset bundles, your SCSS executes BEFORE Odoo's core `primary_variables.scss`:

```
LOAD ORDER:
1. YOUR theme's primary_variables.scss (via prepend)  ← FIRST
2. Odoo core primary_variables.scss                    ← SECOND
3. Other SCSS files
```

**⛔ CRITICAL LIMITATIONS:**
- **CANNOT use map-merge()** with core variables (they don't exist yet!)
- `$o-color-palettes`, `$o-theme-color-palettes`, `$o-theme-font-configs` are all UNDEFINED when your theme loads

**❌ WRONG (Will cause "Undefined variable" error):**
```scss
$o-color-palettes: map-merge($o-color-palettes, (...));         // ERROR!
$o-theme-font-configs: map-merge($o-theme-font-configs, (...)); // ERROR!
```

**✅ CORRECT (Define as standalone):**
```scss
// Standalone font config (no map-merge!)
$o-theme-font-configs: (
    'Poppins': (
        'family': ('Poppins', sans-serif),
        'url': 'Poppins:300,300i,400,400i,500,500i,600,600i,700,700i',
    ),
);

// Reference existing palette by name
$o-website-values-palettes: (
    (
        'color-palettes-name': 'default-1',  // Use existing palette name!
        'font': 'Poppins',
        // ...other values
    ),
);
```

**❌ WRONG**: Do NOT use `ir.asset` records for Google Fonts in themes - this causes malformed URLs!

---

## Theme Page Creation Standard

### Individual Page Files Pattern (Recommended)

Create individual page files instead of a single `pages.xml`:
```
theme_name/
├── data/
│   ├── home.xml          # Homepage template + page
│   ├── about.xml         # About page template + page
│   ├── contact.xml       # Contact page (inherits website.contactus)
│   ├── services.xml      # Services page template + page
│   └── menu.xml          # Menu configuration
└── views/
    └── templates.xml     # Shared templates and layout
```

### Homepage (Inherits website.homepage)
```xml
<!-- data/home.xml -->
<template id="view_home" inherit_id="website.homepage" name="Home">
    <xpath expr="//div[@id='wrap']" position="replace">
        <div id="wrap" class="oe_structure">
            <!-- Homepage content here -->
        </div>
    </xpath>
</template>
```

### Contact Page (Inherits website.contactus)
```xml
<!-- data/contact.xml -->
<template id="view_contact" inherit_id="website.contactus" name="Contact">
    <xpath expr="//h1" position="replace">
        <h1>Get in Touch</h1>
    </xpath>
</template>
```

### Custom Pages (theme.website.page)
```xml
<!-- data/about.xml -->
<template id="view_about" name="About">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure">
            <section class="s_title pt96 pb48">
                <div class="container">
                    <h1>About Us</h1>
                </div>
            </section>
        </div>
    </t>
</template>

<record id="page_about" model="theme.website.page">
    <field name="view_id" ref="view_about"/>
    <field name="is_published" eval="True"/>
    <field name="url">/about</field>
    <field name="name">About</field>
</record>
```

## Theme Mirror Model Architecture

### How Themes Install to Pages

```
Theme Module XML
    ↓
theme.ir.ui.view (Template View)
    ↓
theme.website.page (Template Page)
    ↓ (Theme Installation)
    ↓
ir.ui.view (Actual View with website_id)
    ↓
website.page (Actual Page with website_id)
```

### Key Points
- Theme modules contain `theme.*` models (templates)
- On installation, these convert to actual models with `website_id`
- Each website gets independent copies, enabling theme reuse
- `website_id` assignment happens at view creation level

## Theme Scaffolding Commands

### Command: Scaffold Complete Theme Module

**Trigger**: User asks to "create theme", "scaffold theme", "generate theme module"

**Workflow**:

1. **Detect Context**
   ```bash
   # Determine current Odoo version
   cd <project_path>
   python -c "import sys; sys.path.insert(0, 'helpers'); from version_detector import detect_version; print(detect_version('.'))"
   ```

2. **Create Module Structure**
   ```
   theme_<name>/
   ├── __init__.py
   ├── __manifest__.py
   ├── security/
   │   └── ir.model.access.csv
   ├── data/
   │   ├── assets.xml
   │   ├── menu.xml
   │   └── pages/
   │       ├── home_page.xml
   │       └── aboutus_page.xml
   ├── views/
   │   ├── layout/
   │   │   ├── header.xml          # Header customization (OPTIONAL)
   │   │   ├── footer.xml          # Footer customization (OPTIONAL)
   │   │   └── templates.xml       # Base layout templates
   │   └── snippets/
   │       └── custom_snippets.xml # Custom snippet definitions
   ├── static/
   │   └── src/
   │       ├── scss/
   │       │   ├── primary_variables.scss
   │       │   ├── bootstrap_overridden.scss
   │       │   └── theme.scss
   │       ├── js/
   │       │   ├── theme.js
   │       │   └── snippets_options.js
   │       └── img/
   └── README.md
   ```

3. **Generate `__manifest__.py`**
   ```python
   {
       'name': 'Theme <Name>',
       'version': '<odoo_version>.1.0.0',
       'category': 'Website/Theme',
       'author': 'TaqaTechno',
       'website': 'https://www.taqatechno.com/',
       'support': 'info@taqatechno.com',
       'license': 'LGPL-3',
       'depends': ['website'],
       'data': [
           'security/ir.model.access.csv',
           'views/layout/templates.xml',
           'views/layout/header.xml',
           'views/layout/footer.xml',
           'views/snippets/custom_snippets.xml',
           'data/menu.xml',
           'data/pages/home_page.xml',
           'data/pages/aboutus_page.xml',
           'data/pages/contactus_page.xml',
       ],
       'assets': {
           'web._assets_primary_variables': [
               ('prepend', 'theme_<name>/static/src/scss/primary_variables.scss'),
           ],
           'web._assets_frontend_helpers': [
               'theme_<name>/static/src/scss/bootstrap_overridden.scss',
           ],
           'web.assets_frontend': [
               'theme_<name>/static/src/scss/theme.scss',
               'theme_<name>/static/src/js/theme.js',
           ],
           'website.assets_wysiwyg': [
               'theme_<name>/static/src/js/snippets_options.js',
           ],
       },
       'installable': True,
       'auto_install': False,
       'application': False,
   }
   ```

4. **Generate `primary_variables.scss`** (COMPLETE v5.0)
   ```scss
   // ===================================================================
   // Theme: <Name>
   // Generated by TAQAT Techno /create-theme command v5.0
   // ===================================================================
   //
   // ⚠️ IMPORTANT: This file is PREPENDED before Odoo core variables!
   // DO NOT use map-merge() with core variables - they don't exist yet!
   // ===================================================================

   // === Font Configuration (STANDALONE - no map-merge!) ===
   $o-theme-font-configs: (
       'Inter': (
           'family': ('Inter', sans-serif),
           'url': 'Inter:300,300i,400,400i,500,500i,600,600i,700,700i',
       ),
   );

   // === Website Values Palette (MASTER CONFIGURATION) ===
   // NO bootstrap_overridden.scss needed - configure everything here!
   $o-website-values-palettes: (
       (
           // Reference existing palette (avoids map-merge issues)
           'color-palettes-name': 'default-1',

           // === Typography ===
           'font': 'Inter',
           'headings-font': 'Inter',
           'navbar-font': 'Inter',
           'buttons-font': 'Inter',

           // === Header (NO custom header.xml needed!) ===
           // Options: 'default' | 'hamburger' | 'vertical' | 'sidebar'
           'header-template': 'default',
           'header-links-style': 'default',
           'logo-height': 3rem,
           'fixed-logo-height': 2rem,

           // === Buttons ===
           'btn-padding-y': 0.45rem,
           'btn-padding-x': 1.35rem,
           'btn-border-radius': 0.25rem,

           // === Inputs ===
           'input-padding-y': 0.45rem,
           'input-border-radius': 0.25rem,

           // === Footer (NO custom footer.xml needed!) ===
           // Options: 'default' | 'centered' | 'minimalist' | 'links' | 'descriptive'
           'footer-template': 'default',
           'footer-scrolltop': true,

           // === Links & Layout ===
           'link-underline': 'hover',
           'layout': 'full',
       )
   );
   ```

5. **Generate Initial Template**
   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <odoo>
       <!-- Base template inheritance -->
       <template id="layout" inherit_id="website.layout">
           <xpath expr="//head" position="inside">
               <meta name="theme-name" content="<Name>"/>
           </xpath>
       </template>
   </odoo>
   ```

### Command: Create Snippet (Version-Aware)

**Trigger**: User asks to "create snippet", "add custom snippet"

**Workflow**:

1. **Detect Odoo Version** (determines registration method)

2. **For Odoo 17 and Earlier:**
   ```xml
   <!-- Snippet Template -->
   <template id="s_<snippet_name>" name="<Snippet Name>">
       <section class="s_<snippet_name>" data-name="<Snippet Name>">
           <div class="container">
               <!-- Content here -->
           </div>
       </section>
   </template>

   <!-- Snippet Registration (Odoo 17) -->
   <template id="s_<snippet_name>_insert" inherit_id="website.snippets">
       <xpath expr="//div[@id='snippet_effect']//t[@t-snippet][last()]" position="after">
           <t t-snippet="theme_<name>.s_<snippet_name>"
              string="<Snippet Name>"
              t-thumbnail="/theme_<name>/static/img/snippets/<snippet_name>.svg"/>
       </xpath>
   </template>
   ```

3. **For Odoo 18/19:**
   ```xml
   <!-- Snippet Template -->
   <template id="s_<snippet_name>" name="<Snippet Name>">
       <section class="s_<snippet_name>" data-name="<Snippet Name>">
           <div class="container">
               <!-- Content here -->
           </div>
       </section>
   </template>

   <!-- Snippet Group (if custom group needed) -->
   <template id="snippet_group_custom" inherit_id="website.snippets">
       <xpath expr="//div[@id='snippet_groups']" position="inside">
           <t snippet-group="custom"
              t-snippet="website.s_snippet_group"
              string="Custom Snippets"/>
       </xpath>
   </template>

   <!-- Snippet Registration (Odoo 18/19) -->
   <template id="s_<snippet_name>_insert" inherit_id="website.snippets">
       <xpath expr="//div[@id='snippet_structure']/*[1]" position="before">
           <t t-snippet="theme_<name>.s_<snippet_name>"
              string="<Snippet Name>"
              group="custom"
              t-thumbnail="/theme_<name>/static/img/snippets/<snippet_name>.svg"/>
       </xpath>
   </template>
   ```

4. **Generate Snippet Options** (if needed)
   ```xml
   <template id="s_<snippet_name>_options" inherit_id="website.snippet_options">
       <xpath expr="." position="inside">
           <div data-selector=".s_<snippet_name>">
               <!-- Layout Options -->
               <we-select string="Layout">
                   <we-button data-select-class="">Default</we-button>
                   <we-button data-select-class="s_<snippet_name>_alt">Alternate</we-button>
               </we-select>

               <!-- Add Item Button -->
               <we-row string="Items">
                   <we-button data-add-item="true"
                              data-no-preview="true"
                              class="o_we_bg_brand_primary">Add Item</we-button>
               </we-row>

               <!-- Color Picker -->
               <we-colorpicker string="Background Color"
                               data-css-property="background-color"/>
           </div>
       </xpath>
   </template>
   ```

5. **Generate JavaScript for Options** (if dynamic behavior needed)
   ```javascript
   /** @odoo-module **/

   import options from "@web_editor/js/editor/snippets.options";

   options.registry.<SnippetName> = options.Class.extend({
       /**
        * Add item to snippet
        */
       addItem: function(previewMode, widgetValue, params) {
           let $lastItem = this.$target.find('.snippet-item').last();
           if ($lastItem.length) {
               $lastItem.clone().appendTo(this.$target.find('.snippet-container'));
           }
       },
   });
   ```

   **Include in manifest assets**:
   ```python
   'assets': {
       'website.assets_wysiwyg': [
           'theme_<name>/static/src/js/snippets_options.js',
       ],
   }
   ```

## Figma Integration Workflow

### Command: Convert Figma Design to Odoo Theme

**Trigger**: User provides Figma URL or asks to "convert Figma to Odoo", "import Figma design"

**Prerequisites**: Figma MCP must be available

**Workflow**:

1. **Use Figma MCP with Version-Specific Prompt**
   ```
   Convert this Figma design to HTML for Odoo <version> website theme with these requirements:
   - Use Bootstrap v<bootstrap_version> classes (not Tailwind)
   - Apply proper Odoo theme structure with sections and containers
   - Include responsive classes (col-sm-*, col-md-*, col-lg-*)
   - Use semantic HTML5 elements (header, nav, main, section, article)
   - Add data attributes for Odoo website builder compatibility
   - Map colors to CSS custom properties for theme variables
   - Include accessibility attributes (aria-labels, alt text)
   ```

2. **Extract Color Palette**
   ```
   Extract the color palette from this Figma design and map to CSS custom properties using the o-color-1 through o-color-5 naming convention for Odoo themes.
   ```

3. **Convert HTML to QWeb Template**
   - Wrap in `<template>` tags
   - Add `t-name` attribute
   - Add data attributes for Odoo editor
   - Convert to section-based structure

4. **Generate SCSS from Figma Colors**
   ```python
   python scripts/figma_converter.py <figma_url> <output_dir> <odoo_version>
   ```

5. **Create Snippet from Figma Component**
   - Use converted HTML as snippet content
   - Add proper Odoo structure
   - Register snippet based on version (17 vs 18/19)
   - Generate options if interactive

### Figma MCP Prompts Reference

**Basic HTML + Bootstrap:**
```
Generate this Figma selection as HTML with Bootstrap v<version> classes instead of React and Tailwind. Use Odoo-compatible structure with proper semantic HTML5 elements.
```

**Color Extraction:**
```
Extract colors as CSS custom properties for Odoo theme
```

**Typography Extraction:**
```
Convert this Figma text styling to Bootstrap v<version> typography classes and CSS custom properties. Map font families to Google Fonts configuration for Odoo theme integration.
```

**Layout Extraction:**
```
Convert this Figma layout to Bootstrap v<version> grid system and utility classes. Use proper container, row, col-* structure with responsive breakpoints.
```

## Chrome DevTools Integration Workflow

### Command: Extract Styles from Live Website

**Trigger**: User provides website URL or asks to "extract from website", "copy styles from site"

**Prerequisites**: Chrome DevTools MCP must be available

**Workflow**:

1. **Connect to DevTools MCP**
   - Open URL in Chrome DevTools MCP
   - Select element(s) to extract

2. **Extract Computed Styles**
   ```python
   python scripts/devtools_extractor.py <url> <output_dir>
   ```

3. **Convert to Odoo SCSS**
   - Map CSS properties to SCSS variables
   - Convert colors to Odoo theme variables (o-color-*)
   - Use Bootstrap variables where applicable

4. **Map to Bootstrap Utilities**
   - Identify equivalent Bootstrap classes
   - Replace custom CSS with utilities where possible
   - Generate suggestions for class-based approach

5. **Convert DOM to QWeb**
   - Extract HTML structure
   - Add Odoo-specific attributes
   - Wrap in proper template structure
   - Add Bootstrap grid structure

6. **Generate Complete Theme Code**
   - SCSS file with extracted styles
   - QWeb template with structure
   - Bootstrap class suggestions
   - Snippet registration XML

## JavaScript Development

### Public Widget Pattern (publicWidget - REQUIRED for Themes)

**IMPORTANT**: For website themes, ALWAYS use publicWidget framework - NOT Owl or vanilla JS.

**Use for**: Website interactions, theme functionality, form handling, animations

**Complete Structure with editableMode**:
```javascript
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.MyWidget = publicWidget.Widget.extend({
    selector: '.my-selector',
    disabledInEditableMode: false,  // Allow in website builder

    events: {
        'click .button': '_onClick',
        'change input': '_onChange',
        'submit form': '_onSubmit',
    },

    /**
     * Lifecycle: Called when widget starts
     * CRITICAL: Check editableMode for website builder compatibility
     */
    start: function () {
        // IMPORTANT: Only run animations/interactions in read mode
        if (!this.editableMode) {
            this._initializeAnimation();
            this._bindExternalEvents();
        }
        return this._super.apply(this, arguments);
    },

    /**
     * Initialize animations (only in read mode)
     */
    _initializeAnimation: function () {
        // Animation code that should NOT run in edit mode
        this.$el.addClass('animated');
    },

    /**
     * Bind events outside the widget element
     */
    _bindExternalEvents: function () {
        $(window).on('scroll.myWidget', this._onScroll.bind(this));
        $(window).on('resize.myWidget', this._onResize.bind(this));
    },

    /**
     * Click handler
     */
    _onClick: function (ev) {
        ev.preventDefault();
        // Don't run in edit mode
        if (this.editableMode) return;
        // Handler logic
    },

    /**
     * Scroll handler
     */
    _onScroll: function () {
        // Throttle scroll events for performance
    },

    /**
     * CRITICAL: Clean up event listeners to prevent memory leaks
     */
    destroy: function () {
        $(window).off('.myWidget');  // Remove namespaced events
        this._super.apply(this, arguments);
    },
});

export default publicWidget.registry.MyWidget;
```

**Key publicWidget Points:**
1. **ALWAYS check `this.editableMode`** before running animations/interactions
2. Use `disabledInEditableMode: false` to make widgets work in website builder
3. **ALWAYS clean up** event listeners in `destroy()` method
4. **NEVER use Owl or vanilla JS** for website themes - publicWidget only
5. Use namespaced events (`.myWidget`) for easy cleanup

**Include in Manifest**:
```python
'assets': {
    'web.assets_frontend': [
        'module_name/static/src/js/my_widget.js',
    ],
}
```

### Owl Component Pattern (Modern, Reactive)

**Use for**: Complex interactive UIs, reactive state management, component composition

**Odoo 17 (Owl v1)**:
```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

class MyComponent extends Component {
    setup() {
        this.state = useState({
            items: [],
            loading: false,
        });
    }

    async willStart() {
        await this.loadData();
    }

    async loadData() {
        this.state.loading = true;
        // Fetch data via RPC
        const data = await this.rpc('/my/route');
        this.state.items = data.items;
        this.state.loading = false;
    }

    onItemClick(item) {
        console.log('Clicked:', item);
    }
}

MyComponent.template = "module_name.MyComponentTemplate";

registry.category("public_components").add("MyComponent", MyComponent);

export default MyComponent;
```

**Odoo 18/19 (Owl v2 - Note differences)**:
```javascript
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

class MyComponent extends Component {
    static template = "module_name.MyComponentTemplate";
    static props = {
        // Define props with validation
        title: { type: String, optional: true },
        items: { type: Array },
    };

    setup() {
        this.state = useState({
            selectedId: null,
        });
    }

    // Owl v2 uses static template property
}

export default MyComponent;
```

**XML Template**:
```xml
<template id="MyComponentTemplate" name="My Component">
    <div class="my-component">
        <h3 t-if="props.title"><t t-esc="props.title"/></h3>
        <ul>
            <li t-foreach="props.items" t-as="item" t-key="item.id">
                <t t-esc="item.name"/>
            </li>
        </ul>
    </div>
</template>
```

### Translation (_t) Best Practices

**CRITICAL RULE**: Use `_t()` at **DEFINITION TIME** for static labels in JavaScript arrays/constants, NOT via runtime wrapper methods. Static strings in XML templates are automatically translated by Odoo.

**Why?**
- Static strings in XML templates (`.xml` files) are automatically extracted by Odoo's translation system
- Using `_t()` in templates for static strings duplicates translation entries and adds unnecessary overhead
- `_t()` MUST wrap strings **at definition time** in JS so Odoo's PO extractor can find them
- Runtime wrapper methods (like `translateLabel(key)`) do NOT work - the strings are never found by the extractor

**CORRECT - Wrap static labels with `_t()` AT DEFINITION TIME:**
```javascript
/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";

// ✅ CORRECT: Wrap each string with _t() at definition time
const MONTHS = [
    {value: 1, short: _t("Jan"), full: _t("January")},
    {value: 2, short: _t("Feb"), full: _t("February")},
    {value: 3, short: _t("Mar"), full: _t("March")},
    {value: 4, short: _t("Apr"), full: _t("April")},
    {value: 5, short: _t("May"), full: _t("May")},
    {value: 6, short: _t("Jun"), full: _t("June")},
    {value: 7, short: _t("Jul"), full: _t("July")},
    {value: 8, short: _t("Aug"), full: _t("August")},
    {value: 9, short: _t("Sep"), full: _t("September")},
    {value: 10, short: _t("Oct"), full: _t("October")},
    {value: 11, short: _t("Nov"), full: _t("November")},
    {value: 12, short: _t("Dec"), full: _t("December")},
];

// ✅ CORRECT: Status labels wrapped at definition
const STATUS_LABELS = {
    draft: _t("Draft"),
    pending: _t("Pending"),
    approved: _t("Approved"),
    rejected: _t("Rejected"),
};

export class DatePicker extends Component {
    setup() {
        this.months = MONTHS;  // Already translated at definition
    }

    get displayLabel() {
        const month = this.months.find(m => m.value === this.selectedMonth);
        // No translateLabel() needed - values are already translated
        return `${month?.short || ""} ${this.selectedYear}`;
    }
}
```

**WRONG - Runtime wrapper methods don't work:**
```javascript
// ❌ WRONG: Strings without _t() at definition will NOT be translated
const MONTHS = [
    {value: 1, label: "Jan", full: "January"},  // NOT FOUND by PO extractor!
    {value: 2, label: "Feb", full: "February"},
];

// ❌ WRONG: This pattern does NOT work for translation
translateLabel(key) {
    return _t(key);  // key is a variable, not a literal - PO extractor can't find it!
}
```

**CORRECT - Template using pre-translated values:**
```xml
<!-- Month values come from JS MONTHS array - already translated at definition -->
<t t-foreach="getAvailableMonths()" t-as="month" t-key="month.value">
    <a href="#" t-on-click.prevent="() => this.selectMonth(month.value)">
        <!-- No wrapper needed - month.full is already translated -->
        <t t-esc="month.full"/>
    </a>
</t>
```

**CORRECT - Static XML strings need NO wrapper:**
```xml
<!-- Static strings in XML are auto-translated by Odoo -->
<span>No data available</span>
<a href="#">Live</a>
<button type="submit">Submit</button>
```

**When to use `_t()` at DEFINITION TIME:**
1. ✅ Static labels in JavaScript arrays (month names, day names, status labels)
2. ✅ Static labels in JavaScript objects/constants
3. ✅ Error messages defined as constants
4. ✅ Any string literal that will be displayed to users from JS

**When NOT to use `_t()`:**
1. ❌ Static text directly in XML templates (auto-translated)
2. ❌ Runtime wrapper methods like `translateLabel(key)` (doesn't work!)
3. ❌ Dynamic variables passed to `_t()` at runtime
4. ❌ Any hardcoded string in `.xml` files

**REMEMBER**: If you define a string in JavaScript that will be shown to users, wrap it with `_t()` **where it's defined**, not where it's used.

## SCSS and Bootstrap Customization

### Primary Variables Override

**File**: `static/src/scss/primary_variables.scss`

**Purpose**: Override Odoo's built-in style variables (colors, fonts, spacing)

**Include in**: `web._assets_primary_variables` bundle

**Structure**:
```scss
// ============================================================
// Theme Primary Variables
// Override Odoo defaults with !default to allow further overriding
// ============================================================

// Color Palette
$o-color-1: #3498db !default;  // Primary
$o-color-2: #2ecc71 !default;  // Success
$o-color-3: #e74c3c !default;  // Danger
$o-color-4: #f39c12 !default;  // Warning
$o-color-5: #9b59b6 !default;  // Info

// Website Values Palette Configuration
$o-website-values-palettes: (
    (
        // Color Configuration
        'color-palettes-name': 'my-theme',

        // Typography
        'font': 'Inter',
        'headings-font': 'Inter',
        'navbar-font': 'Inter',
        'buttons-font': 'Inter',
        'headings-line-height': 1.2,

        // Header & Navigation
        'header-template': 'default',  // or 'centered', 'boxed'
        'header-font-size': 1rem,
        'logo-height': 3rem,
        'fixed-logo-height': 2rem,
        'hamburger-position': 'right',  // Mobile menu

        // Buttons
        'btn-padding-y': 0.45rem,
        'btn-padding-x': 1.35rem,
        'btn-padding-y-sm': 0.3rem,
        'btn-padding-x-sm': 0.9rem,
        'btn-padding-y-lg': 0.6rem,
        'btn-padding-x-lg': 1.8rem,
        'btn-border-radius': 0.25rem,
        'btn-border-width': 1px,
        'btn-font-size': 1rem,

        // Input Fields
        'input-padding-y': 0.45rem,
        'input-border-radius': 0.25rem,

        // Colors (map to palette)
        'color-1': $o-color-1,
        'color-2': $o-color-2,
        'color-3': $o-color-3,
        'color-4': $o-color-4,
        'color-5': $o-color-5,
    )
);

// Google Fonts Configuration (STANDALONE - no map-merge!)
$o-theme-font-configs: (
    'Inter': (
        'family': ('Inter', sans-serif),
        'url': 'Inter:wght@300;400;500;600;700',
    ),
);
```

**⚠️ NEVER use these patterns in themes:**
```scss
// ❌ WRONG - Will cause "Undefined variable" errors
$o-color-palettes: map-merge($o-color-palettes, (...));
$o-theme-color-palettes: map-merge($o-theme-color-palettes, (...));
$o-theme-font-configs: map-merge($o-theme-font-configs, (...));
```

### Bootstrap Overrides

**File**: `static/src/scss/bootstrap_overridden.scss`

**Purpose**: Override Bootstrap variables that Odoo hasn't exposed

**Include in**: `web._assets_frontend_helpers` bundle

**Structure**:
```scss
// ============================================================
// Bootstrap Variable Overrides
// Only override Bootstrap vars not available in Odoo variables
// ============================================================

@import "~bootstrap/scss/functions";
@import "~bootstrap/scss/variables";

// Spacing
$spacer: 1rem !default;

// Grid breakpoints
$grid-breakpoints: (
    xs: 0,
    sm: 576px,
    md: 768px,
    lg: 992px,
    xl: 1200px,
    xxl: 1400px
) !default;

// Container max widths
$container-max-widths: (
    sm: 540px,
    md: 720px,
    lg: 960px,
    xl: 1140px,
    xxl: 1320px
) !default;

// Typography
$font-size-base: 1rem !default;
$line-height-base: 1.5 !default;

// Border radius
$border-radius: 0.25rem !default;
$border-radius-sm: 0.125rem !default;
$border-radius-lg: 0.5rem !default;

// Shadows
$box-shadow-sm: 0 .125rem .25rem rgba(0, 0, 0, .075) !default;
$box-shadow: 0 .5rem 1rem rgba(0, 0, 0, .15) !default;
$box-shadow-lg: 0 1rem 3rem rgba(0, 0, 0, .175) !default;
```

## Version-Specific Considerations

### Odoo 17 Specifics

1. **Owl v1**
   - Use `useState` from `@odoo/owl`
   - Legacy import paths
   - Component template as separate property

2. **Snippet Structure**
   - Simple insertion without groups
   - Use XPath targeting `//div[@id='snippet_effect']`

3. **Public Widgets**
   - Import from `@web/legacy/js/public/public_widget`
   - jQuery fully available

### Odoo 18/19 Specifics

1. **Owl v2**
   - Static template property
   - Props validation required
   - New reactive hooks
   - Breaking changes from v1

2. **Snippet Groups**
   - Required `snippet-group` attribute
   - Organized in categories
   - XPath targets `//div[@id='snippet_structure']`

3. **Bootstrap 5.1.3**
   - All use same Bootstrap version
   - Consistent utility classes

4. **Website Builder Enhancements**
   - Theme browsing in editor
   - Custom font upload via UI
   - Enhanced snippet options

### Bootstrap 4 to 5 Migration (Odoo 14/15 → 16+)

When migrating themes:

1. **Class Replacements**:
   ```python
   python scripts/bootstrap_mapper.py <old_classes>
   ```

   Common replacements:
   - `ml-*` → `ms-*` (margin-left → margin-start)
   - `mr-*` → `me-*` (margin-right → margin-end)
   - `pl-*` → `ps-*` (padding-left → padding-start)
   - `pr-*` → `pe-*` (padding-right → padding-end)
   - `text-left` → `text-start`
   - `text-right` → `text-end`
   - `float-left` → `float-start`
   - `float-right` → `float-end`
   - `form-group` → `mb-3`
   - `custom-select` → `form-select`
   - `close` → `btn-close`
   - `badge-*` → `bg-*` (e.g., `badge-primary` → `bg-primary`)
   - `font-weight-bold` → `fw-bold`
   - `sr-only` → `visually-hidden`
   - `no-gutters` → `g-0`

2. **Removed Classes** (find alternatives):
   - `form-inline` - Use grid/flex utilities
   - `jumbotron` - Recreate with utilities
   - `media` - Use `d-flex` with flex utilities

3. **jQuery Removal**:
   - Bootstrap 5 uses vanilla JavaScript
   - May need to adjust widget initialization

## Frontend Performance Best Practices

1. **Asset Bundling**
   - Always use Odoo's asset bundles
   - Don't link external files individually
   - Leverage minification (enabled in production)

2. **Lazy Loading**
   - Use `loading="lazy"` on images
   - Leverage Odoo's `/website/image` route for auto-resizing
   - Lazy load videos (Odoo 18+ has built-in support)

3. **Optimize Snippets**
   - Batch server calls (one RPC for all data)
   - Use QWeb for efficient rendering
   - Minimize DOM manipulation

4. **CSS Optimization**
   - Use Bootstrap utilities instead of custom CSS
   - Keep HTML structure lean
   - Remove unused CSS/JS from bundles

5. **Caching**
   - Utilize computed fields with `store=True`
   - Cache expensive computations
   - Do heavy work server-side

6. **SEO Considerations**
   - Server-render critical content
   - Use Owl for enhancements, not primary content
   - Ensure fast load times

## Security & Access Control

### Model-Level Access

Always create `security/ir.model.access.csv`:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,model.user,model_model_name,base.group_user,1,1,1,0
access_model_public,model.public,model_model_name,,1,0,0,0
```

### Record-Level Rules

Create `security/rules.xml` for fine-grained control:

```xml
<record id="model_rule" model="ir.rule">
    <field name="name">Model: User own records</field>
    <field name="model_id" ref="model_model_name"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### Controller Security

```python
from odoo import http

class MyController(http.Controller):
    @http.route('/public/route', auth='public')  # No login required
    def public_route(self):
        pass

    @http.route('/user/route', auth='user')  # Login required
    def user_route(self):
        pass
```

### Safe Data Exposure

```python
# Use sudo() carefully
records = request.env['model'].sudo().search([('published', '=', True)])

# Check access rights
if not request.env['model'].check_access_rights('read', raise_exception=False):
    return request.redirect('/access-denied')
```

## Common Workflows

### Create Complete Theme from Figma

1. User provides Figma URL
2. Detect target Odoo version
3. Use Figma MCP to extract design
4. Generate theme module structure
5. Convert colors to SCSS variables
6. Convert components to snippets
7. Create snippet options
8. Test in Odoo Website Builder

### Extend Existing Theme

1. Detect current theme and version
2. Analyze existing structure
3. Create inheriting module
4. Override specific templates
5. Add custom snippets
6. Extend SCSS variables

### Migrate Theme Across Versions

1. Detect source and target versions
2. Convert Bootstrap classes (if 4→5)
3. Update snippet structure (if 17→18/19)
4. Update JavaScript (if Owl v1→v2)
5. Test all functionality
6. Generate migration report

## Testing & Validation

### Theme Installation Test

```bash
# Install theme
python -m odoo -c conf/<config>.conf -d <db> -i theme_<name> --stop-after-init

# Check for errors in log
grep ERROR odoo.log
```

### Snippet Registration Test

1. Install theme
2. Go to Website → Edit
3. Check snippets panel
4. Verify snippet appears in correct category
5. Test drag-and-drop
6. Test snippet options

### Browser Testing

1. Test in multiple browsers (Chrome, Firefox, Safari, Edge)
2. Test responsive breakpoints (sm, md, lg, xl, xxl)
3. Validate accessibility (ARIA labels, keyboard navigation)
4. Check performance (Lighthouse, Page Speed)

## Troubleshooting

### ⚠️ SCSS Compilation Errors (CRITICAL)

**Issue: "Undefined variable: $o-color-palettes" or "$o-theme-font-configs"**

**Cause:** Using `map-merge()` with core Odoo variables in theme SCSS. Theme files load BEFORE core variables are defined.

**Solution:**
1. Remove ALL `map-merge()` calls with core variables
2. Define `$o-theme-font-configs` as standalone (no merge)
3. Use `'color-palettes-name': 'default-1'` to reference existing palettes
4. See "CRITICAL: SCSS Load Order" section above

**Issue: CSS showing 0 rules / Styles not loading**

**Cause:** Silent SCSS compilation failure due to undefined variables.

**Diagnosis:**
```javascript
// In browser console
document.styleSheets[0].cssRules.length  // Should be > 0
// If 0, SCSS compilation failed silently
```

**Solution:**
1. Check browser console for "Style compilation failed" errors
2. Fix undefined variable errors (see above)
3. Clear asset cache:
```python
# Via Odoo shell
>>> self.env['ir.attachment'].search([('url', 'like', '/web/assets/')]).unlink()
>>> self.env.cr.commit()
```

**Issue: Malformed Google Fonts URL**

**Cause:** Using `ir.asset` records for external font URLs causes URL duplication.

**Solution:** Use `$o-theme-font-configs` in SCSS instead of `ir.asset` XML records.

### Snippet Not Appearing

**Causes:**
- Incorrect XPath (version mismatch)
- Missing group attribute (Odoo 18/19)
- Template not found
- Syntax error in XML

**Solutions:**
1. Check Odoo version and use correct insertion method
2. Verify template ID exists
3. Check XML syntax
4. Look for errors in log

### Styles Not Applying

**Causes:**
- SCSS not included in correct bundle
- Variable override not using `!default`
- CSS specificity issues
- Asset not compiled
- **SCSS compilation failed silently** (check console!)

**Solutions:**
1. Verify asset bundle in manifest
2. Clear browser cache
3. Check asset regeneration: `odoo-bin --update theme_<name>`
4. Use browser DevTools to inspect computed styles
5. **Check console for SCSS errors first!**

### JavaScript Not Working

**Causes:**
- Import path incorrect for Odoo version
- Widget not registered
- jQuery conflicts (Bootstrap 5)
- Owl version mismatch

**Solutions:**
1. Check import paths for Odoo version
2. Verify widget/component registration
3. Check console for errors
4. Ensure correct Owl version usage

### XPath Errors in Header/Footer Templates

**Cause:** Complex XPath expressions like `//header//nav` may not match Odoo's actual HTML structure.

**Solution:** Use simple XPath expressions:
```xml
<!-- ✅ CORRECT: Simple XPath -->
<xpath expr="//header" position="attributes">

<!-- ❌ WRONG: Complex XPath may not match -->
<xpath expr="//header//nav" position="attributes">
```

## Expert Tips

1. **Always Use Version Detection First**
   - Don't assume Odoo version
   - Check before generating any code

2. **Prefer Bootstrap Utilities**
   - Less custom CSS = easier maintenance
   - Better performance
   - Editor-compatible

3. **Server-Side Rendering for SEO**
   - Don't rely on client-side JS for content
   - Use Owl for enhancements only

4. **Test in Edit Mode**
   - Ensure Website Builder can handle your code
   - Test snippet options thoroughly

5. **Follow Odoo Patterns**
   - Study core themes (`odoo/addons/theme_*`)
   - Match existing conventions
   - Use same class prefixes (`s_`, `o_`)

6. **Documentation**
   - Comment complex SCSS
   - Document snippet options
   - Provide README for theme

## Progressive Web App (PWA) Implementation

### Command: Setup PWA for Odoo Website

**Trigger**: User asks to "make PWA", "add offline support", "enable push notifications"

**Workflow**:

1. **Generate Service Worker**
   ```javascript
   // static/src/service-worker.js
   const CACHE_NAME = 'odoo-pwa-v1';
   const urlsToCache = ['/', '/web/static/lib/owl/owl.js'];

   self.addEventListener('install', event => {
     event.waitUntil(
       caches.open(CACHE_NAME)
         .then(cache => cache.addAll(urlsToCache))
     );
   });

   self.addEventListener('fetch', event => {
     event.respondWith(
       caches.match(event.request)
         .then(response => response || fetch(event.request))
     );
   });
   ```

2. **Create Web App Manifest**
   ```json
   {
     "name": "Odoo PWA",
     "short_name": "OdooPWA",
     "start_url": "/",
     "display": "standalone",
     "background_color": "#875A7B",
     "theme_color": "#875A7B",
     "icons": [...]
   }
   ```

3. **Register Service Worker**
   ```javascript
   /** @odoo-module **/
   import publicWidget from "@web/legacy/js/public/public_widget";

   publicWidget.registry.ServiceWorkerRegistration = publicWidget.Widget.extend({
     selector: 'body',
     start: function() {
       if ('serviceWorker' in navigator) {
         navigator.serviceWorker.register('/service-worker.js');
       }
       return this._super(...arguments);
     }
   });
   ```

## Modern JavaScript & TypeScript

### Command: Setup TypeScript

**Trigger**: User asks to "use TypeScript", "add type safety", "configure TypeScript"

**Workflow**:

1. **Generate tsconfig.json**
   ```json
   {
     "compilerOptions": {
       "target": "ES2020",
       "module": "ES2020",
       "lib": ["ES2020", "DOM"],
       "strict": true,
       "paths": {
         "@web/*": ["./addons/web/static/src/*"],
         "@owl/*": ["./addons/web/static/lib/owl/*"]
       }
     }
   }
   ```

2. **Create Typed Owl Component**
   ```typescript
   /** @odoo-module **/
   import { Component, useState } from "@odoo/owl";

   interface ProductProps {
     id: number;
     name: string;
     price: number;
   }

   export class ProductComponent extends Component<ProductProps> {
     static template = xml`...`;

     setup() {
       this.state = useState({ loading: false });
     }
   }
   ```

### ES2020+ Patterns

**Use modern JavaScript features**:
```javascript
// Optional chaining
const userName = this.props.user?.profile?.name;

// Nullish coalescing
const displayName = userName ?? 'Guest User';

// Dynamic imports
const module = await import('./HeavyFeatureComponent');

// Private class fields
class SecureWidget {
  #apiKey = null;
  #generateKey() {
    return crypto.randomUUID();
  }
}
```

## Testing Infrastructure

### Command: Setup Testing

**Trigger**: User asks to "add tests", "setup Jest", "configure Cypress"

**Workflow**:

1. **Jest Configuration**
   ```javascript
   // jest.config.js
   module.exports = {
     testEnvironment: 'jsdom',
     moduleNameMapper: {
       '^@web/(.*)$': '<rootDir>/addons/web/static/src/$1',
     },
     collectCoverageFrom: ['static/src/**/*.{js,jsx}']
   };
   ```

2. **Cypress E2E Tests**
   ```javascript
   // cypress/e2e/ecommerce.cy.js
   describe('E-commerce Flow', () => {
     it('should complete purchase', () => {
       cy.visit('/shop');
       cy.get('[data-product-id="1"]').click();
       cy.get('#add_to_cart').click();
       cy.get('.btn-primary').contains('Checkout').click();
     });
   });
   ```

3. **Visual Regression Testing**
   ```javascript
   // backstop.config.js
   module.exports = {
     scenarios: [{
       label: 'Homepage',
       url: 'http://localhost:8069',
       misMatchThreshold: 0.1
     }]
   };
   ```

## Performance Optimization

### Command: Optimize Core Web Vitals

**Trigger**: User asks to "improve performance", "optimize LCP/FID/CLS", "speed up website"

**Workflow**:

1. **Optimize Largest Contentful Paint (LCP)**
   ```javascript
   // Preload critical resources
   const link = document.createElement('link');
   link.rel = 'preload';
   link.as = 'image';
   link.href = '/web/image/website/1/logo';
   document.head.appendChild(link);
   ```

2. **Reduce First Input Delay (FID)**
   ```javascript
   // Break up long tasks
   function optimizeLongTask(items) {
     const chunks = [];
     for (let i = 0; i < items.length; i += 100) {
       chunks.push(items.slice(i, i + 100));
     }
     chunks.forEach(chunk => {
       requestIdleCallback(() => processChunk(chunk));
     });
   }
   ```

3. **Minimize Cumulative Layout Shift (CLS)**
   ```css
   /* Reserve space for dynamic content */
   .product-image-container {
     aspect-ratio: 1/1;
     contain: layout;
   }
   ```

## Accessibility (WCAG Compliance)

### Command: Implement Accessibility

**Trigger**: User asks to "add ARIA", "make accessible", "WCAG compliance"

**Workflow**:

1. **ARIA Implementation**
   ```xml
   <form role="form" aria-label="Contact Form">
     <input type="email"
            aria-labelledby="email-label"
            aria-describedby="email-error"
            aria-required="true"
            aria-invalid="false"/>
     <span id="email-error" role="alert" aria-live="polite"></span>
   </form>
   ```

2. **Keyboard Navigation**
   ```javascript
   class KeyboardNavigationManager {
     handleTab(event) {
       if (event.shiftKey) {
         // Backward navigation
       } else {
         // Forward navigation
       }
     }
     trapFocus() {
       // Trap focus within modal
     }
   }
   ```

3. **Screen Reader Support**
   ```javascript
   class ScreenReaderAnnouncer {
     announce(message, priority = 'polite') {
       this.liveRegion.setAttribute('aria-live', priority);
       this.liveRegion.textContent = message;
     }
   }
   ```

## Real-time Features

### Command: Add WebSocket Support

**Trigger**: User asks to "add real-time", "implement WebSocket", "live updates"

**Workflow**:

1. **WebSocket Manager**
   ```javascript
   /** @odoo-module **/
   export class WebSocketManager {
     constructor(url) {
       this.socket = new WebSocket(url);
       this.setupEventHandlers();
     }

     setupEventHandlers() {
       this.socket.onmessage = (event) => {
         const data = JSON.parse(event.data);
         this.handleMessage(data);
       };
     }

     send(data) {
       if (this.socket.readyState === WebSocket.OPEN) {
         this.socket.send(JSON.stringify(data));
       }
     }
   }
   ```

2. **Server-Sent Events (SSE)**
   ```javascript
   class SSEManager {
     constructor(url) {
       this.eventSource = new EventSource(url);
       this.eventSource.onmessage = (event) => {
         this.handleMessage(event.data);
       };
     }
   }
   ```

## Web Components

### Command: Create Web Component

**Trigger**: User asks to "create web component", "custom element"

**Workflow**:

```javascript
/** @odoo-module **/

export class OdooSearchInput extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['placeholder', 'value'];
  }

  connectedCallback() {
    this.render();
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        input { width: 100%; padding: 0.5rem; }
      </style>
      <input type="text" placeholder="${this.getAttribute('placeholder')}"/>
    `;
  }
}

customElements.define('odoo-search-input', OdooSearchInput);
```

## Advanced Odoo Features

### Tour Manager

**Command**: Create guided tour

```javascript
/** @odoo-module **/
import tour from 'web_tour.tour';

tour.register('product_tour', {
  url: '/shop',
}, [{
  content: 'Click on any product',
  trigger: '.oe_product:first',
  position: 'bottom',
}]);
```

### Custom Field Widgets

```javascript
/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class ColorPickerField extends Component {
  static template = xml`
    <input type="color" t-att-value="props.value" t-on-change="onChange"/>
  `;

  onChange(event) {
    this.props.update(event.target.value);
  }
}

registry.category("fields").add("color_picker", ColorPickerField);
```

### Systray Components

```javascript
/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";

export class NotificationBell extends Component {
  static template = xml`...`;

  setup() {
    this.state = useState({ notifications: [] });
  }
}

registry.category("systray").add("NotificationBell", {
  Component: NotificationBell,
});
```

## Modern Build Tools

### Vite Configuration

**Command**: Setup Vite build

```javascript
// vite.config.js
import { defineConfig } from 'vite';

export default defineConfig({
  base: '/web/static/',
  build: {
    rollupOptions: {
      input: {
        main: 'static/src/main.js',
        website: 'static/src/website.js'
      }
    }
  },
  server: {
    proxy: {
      '/web': 'http://localhost:8069'
    }
  }
});
```

### CI/CD Pipeline

```yaml
# .github/workflows/odoo-frontend.yml
name: Odoo Frontend CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run tests
      run: |
        npm run test:unit
        npm run test:e2e
    - name: Build assets
      run: npm run build
```

## Resources

- **Odoo Documentation**: https://www.odoo.com/documentation/
- **Bootstrap 5 Docs**: https://getbootstrap.com/docs/5.1/
- **Owl Framework**: https://github.com/odoo/owl
- **TypeScript**: https://www.typescriptlang.org/docs/
- **Jest**: https://jestjs.io/docs/
- **Cypress**: https://docs.cypress.io/
- **Web Components**: https://developer.mozilla.org/en-US/docs/Web/Web_Components
- **Community Forums**: https://www.odoo.com/forum/

## Theme Feature Activation System (CRITICAL)

### Overview: The theme.utils Model

When creating a theme, you MUST include a **models/theme_xxx.py** file that implements the `theme.utils` pattern. This allows your theme to:
- Enable/disable header templates
- Enable/disable footer templates
- Activate optional features on theme installation
- Configure the theme's default appearance

### Required File Structure

```
theme_yourtheme/
├── __init__.py                    # Must import models
├── __manifest__.py
├── models/
│   ├── __init__.py               # Must import theme_yourtheme
│   └── theme_yourtheme.py        # theme.utils implementation (REQUIRED!)
├── data/
├── views/
└── static/
```

### models/__init__.py
```python
from . import theme_yourtheme
```

### models/theme_yourtheme.py (REQUIRED PATTERN)
```python
from odoo import models

class ThemeYourTheme(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_yourtheme_post_copy(self, mod):
        """
        Called automatically when theme is installed on a website.
        Use enable_view() and disable_view() to configure templates.

        IMPORTANT: Method name MUST be _theme_{technical_name}_post_copy
        where technical_name matches folder name (underscores, not hyphens).
        """
        # Enable desired header template (mutual exclusivity enforced)
        self.enable_view('website.template_header_sales_two')

        # Enable desired footer template (mutual exclusivity enforced)
        self.enable_view('website.template_footer_contact')

        # Enable optional features
        self.enable_view('website.option_header_brand_logo')

        # Disable unwanted defaults
        self.disable_view('website.header_visibility_standard')
        self.enable_view('website.header_visibility_fixed')
```

### Key Methods Available

| Method | Purpose | Example |
|--------|---------|---------|
| `enable_view(xml_id)` | Activate a template | `self.enable_view('website.template_header_hamburger')` |
| `disable_view(xml_id)` | Deactivate a template | `self.disable_view('website.template_header_default')` |
| `enable_asset(xml_id)` | Activate an asset bundle | `self.enable_asset('website.theme_custom_assets')` |
| `disable_asset(xml_id)` | Deactivate an asset bundle | `self.disable_asset('website.theme_old_assets')` |

### Mutual Exclusivity Rules

**Headers**: Only ONE primary header template can be active at a time. When you `enable_view()` a header, Odoo automatically handles deactivating others.

**Footers**: Only ONE primary footer template can be active at a time. Same automatic handling.

**Header Options**: Alignment variants, visibility effects, and components can be combined with the active header.

### Complete Example: Modern Business Theme

```python
from odoo import models

class ThemeModernBusiness(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_modern_business_post_copy(self, mod):
        """Configure Modern Business theme defaults."""

        # === HEADER CONFIGURATION ===
        # Use hamburger header with centered mobile
        self.enable_view('website.template_header_hamburger')
        self.enable_view('website.template_header_hamburger_mobile_align_center')

        # Fixed header that disappears on scroll
        self.disable_view('website.header_visibility_standard')
        self.enable_view('website.header_visibility_disappears')

        # Show logo, not brand name
        self.enable_view('website.option_header_brand_logo')
        self.disable_view('website.option_header_brand_name')

        # === FOOTER CONFIGURATION ===
        # Use contact footer with call-to-action style
        self.enable_view('website.template_footer_contact')

        # Enable scroll-to-top button
        # (This is configured in $o-website-values-palettes, not via views)

        # === OPTIONAL FEATURES ===
        # Enable search in header
        self.enable_view('website.header_search_box')

        # Enable social links
        self.enable_view('website.header_social_links')
```

---

## Complete Dynamic Page Reference

This section documents ALL available templates in Odoo for dynamic pages. Use this reference when:
1. Comparing a Figma design to find the closest Odoo template
2. Configuring theme defaults via `_theme_xxx_post_copy()`
3. Understanding what features Odoo provides out-of-the-box

---

### 📋 HEADER TEMPLATES (11 Primary + Variants)

All headers inherit from `website.layout`. Only ONE primary header can be active per website.

#### Primary Header Templates

| XML ID | Name | Description | Best For |
|--------|------|-------------|----------|
| `website.template_header_default` | Default | Standard horizontal navbar | Most websites |
| `website.template_header_hamburger` | Hamburger | Collapsed hamburger menu | Minimal designs |
| `website.template_header_stretch` | Stretch | Full-width stretched navbar | Wide layouts |
| `website.template_header_vertical` | Vertical | Vertical sidebar navigation | App-like sites |
| `website.template_header_search` | Search | Header with prominent search | E-commerce, directories |
| `website.template_header_sales_one` | Sales 1 | E-commerce focused header | Online stores |
| `website.template_header_sales_two` | Sales 2 | E-commerce with categories | Large catalogs |
| `website.template_header_sales_three` | Sales 3 | E-commerce alternate | Product-focused |
| `website.template_header_sales_four` | Sales 4 | E-commerce variant | Fashion, retail |
| `website.template_header_sidebar` | Sidebar | Full sidebar layout | Dashboard sites |
| `website.template_header_boxed` | Boxed | Rounded box container | Modern brands |

#### Header Alignment Variants (per header)

Each header supports alignment variants. Example for Default header:
- `website.template_header_default` - Left aligned (default)
- `website.template_header_default_align_center` - Center aligned
- `website.template_header_default_align_right` - Right aligned

**Mobile variants** (append `_mobile_align_center` or `_mobile_align_right`):
- `website.template_header_hamburger_mobile_align_center`
- `website.template_header_hamburger_mobile_align_right`

#### Header Visibility Effects (mutually exclusive)

| XML ID | Effect | Description |
|--------|--------|-------------|
| `website.header_visibility_standard` | Standard | Always visible, scrolls with page |
| `website.header_visibility_fixed` | Fixed | Sticks to top on scroll |
| `website.header_visibility_disappears` | Disappears | Hides on scroll down, shows on scroll up |
| `website.header_visibility_fade_out` | Fade Out | Fades out on scroll |

#### Header Components (can be combined)

| XML ID | Component | Default |
|--------|-----------|---------|
| `website.option_header_brand_logo` | Show logo image | **Active** |
| `website.option_header_brand_name` | Show text "My Website" | Inactive |
| `website.header_call_to_action` | CTA button (Contact Us) | **Active** |
| `website.header_search_box` | Search bar | **Active** |
| `website.header_social_links` | Social media icons | Inactive |
| `website.header_text_element` | Custom text element | **Active** |
| `website.header_language_selector` | Language dropdown | **Active** |

#### Header Visual Reference

```
┌─────────────────────────────────────────────────────────────────┐
│ DEFAULT HEADER                                                   │
│ ┌────────┬────────────────────────────────┬───────────────────┐ │
│ │ LOGO   │  Home  About  Services  Blog   │  Search   CTA BTN │ │
│ └────────┴────────────────────────────────┴───────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ HAMBURGER HEADER                                                 │
│ ┌────────┬───────────────────────────────┬────────────────────┐ │
│ │ ☰ MENU │         LOGO                  │   Search   CTA     │ │
│ └────────┴───────────────────────────────┴────────────────────┘ │
│                    ↓ (expanded menu)                             │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  Home  │  About  │  Services  │  Blog  │  Contact           │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SALES TWO HEADER (E-commerce)                                    │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Top bar: Phone | Email | Currency | Language                 │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ LOGO        [    Search Bar    ]        Account  Cart 🛒    │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ Category 1  │  Category 2  │  Category 3  │  All Products   │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ VERTICAL/SIDEBAR HEADER                                         │
│ ┌──────────────┬──────────────────────────────────────────────┐│
│ │              │                                               ││
│ │    LOGO      │                                               ││
│ │              │                                               ││
│ │  ─────────── │              PAGE CONTENT                     ││
│ │              │                                               ││
│ │   Home       │                                               ││
│ │   About      │                                               ││
│ │   Services   │                                               ││
│ │   Blog       │                                               ││
│ │   Contact    │                                               ││
│ │              │                                               ││
│ │  ─────────── │                                               ││
│ │  [Social]    │                                               ││
│ └──────────────┴──────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────┘
```

---

### 📋 FOOTER TEMPLATES (9 Options)

All footers inherit from `website.layout`. Only ONE primary footer can be active per website.

| XML ID | Name | Description | Best For |
|--------|------|-------------|----------|
| `website.footer_custom` | Default | Customizable default footer | General use |
| `website.template_footer_descriptive` | Descriptive | Detailed company description | Corporate sites |
| `website.template_footer_centered` | Centered | Center-aligned minimal | Landing pages |
| `website.template_footer_links` | Links | Multiple link columns | Large sites |
| `website.template_footer_minimalist` | Minimalist | Ultra-minimal footer | Clean designs |
| `website.template_footer_contact` | Contact | Contact info focused | Service businesses |
| `website.template_footer_call_to_action` | CTA | Newsletter/action focused | Marketing sites |
| `website.template_footer_headline` | Headline | Large headline text | Brand statements |
| `website.template_footer_slideout` | Slideout | Slides out on scroll | Modern/trendy |

#### Footer Options

| XML ID | Option | Description |
|--------|--------|-------------|
| `website.footer_no_copyright` | Remove copyright | Hides copyright line |
| `website.footer_language_selector_inline` | Inline language | Language selector style |

#### Footer Visual Reference

```
┌─────────────────────────────────────────────────────────────────┐
│ DEFAULT FOOTER                                                   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  LOGO                                                        │ │
│ │  Company description text here...                            │ │
│ │                                                              │ │
│ │  Links        Services      Contact                          │ │
│ │  · About      · Web Dev     123 Street                       │ │
│ │  · Blog       · Design      City, Country                    │ │
│ │  · Careers    · Support     +1 234 567 890                   │ │
│ │                                                              │ │
│ │  [Social Icons]                                              │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │  © 2024 Company Name. All rights reserved.                   │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ MINIMALIST FOOTER                                                │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │          © 2024 Company  ·  Privacy  ·  Terms               │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CONTACT FOOTER                                                   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │  ┌──────────────┬───────────────┬────────────────────────┐  │ │
│ │  │  📍 Address  │  📞 Phone     │  ✉️ Email              │  │ │
│ │  │  123 Street  │  +1 234 567   │  hello@company.com     │  │ │
│ │  │  City        │               │                        │  │ │
│ │  └──────────────┴───────────────┴────────────────────────┘  │ │
│ │                        [Social Icons]                        │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CALL-TO-ACTION FOOTER                                            │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │            Subscribe to our newsletter                       │ │
│ │  ┌─────────────────────────────────┬─────────────────────┐  │ │
│ │  │  Enter your email...            │  [Subscribe Now]    │  │ │
│ │  └─────────────────────────────────┴─────────────────────┘  │ │
│ │                                                              │ │
│ │  © 2024 Company  ·  [Social Icons]                          │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

### 📋 SHOP PAGE TEMPLATES (website_sale module)

#### Shop Layout Options

| XML ID | Feature | Default | Description |
|--------|---------|---------|-------------|
| `website_sale.products_design_card` | Card design | Inactive | Card-style product items |
| `website_sale.products_design_thumbs` | Thumbnails | Inactive | Thumbnail layout |
| `website_sale.products_design_grid` | Grid design | Inactive | Grid layout |
| `website_sale.products_thumb_4_3` | 4:3 ratio | Inactive | 4:3 image aspect ratio |
| `website_sale.products_thumb_4_5` | 4:5 ratio | Inactive | 4:5 image aspect ratio |
| `website_sale.products_thumb_2_3` | 2:3 ratio | Inactive | 2:3 image aspect ratio |
| `website_sale.products_thumb_cover` | Cover fill | **Active** | Image fills container |

#### Shop Categories & Filters

| XML ID | Feature | Default | Description |
|--------|---------|---------|-------------|
| `website_sale.products_categories` | Left sidebar categories | Inactive | Categories in left sidebar |
| `website_sale.products_categories_top` | Top categories | **Active** | Categories in top nav |
| `website_sale.products_attributes` | Attribute filters | **Active** | Product attribute filters |
| `website_sale.filter_products_price` | Price filter | Inactive | Price range slider |
| `website_sale.filter_products_tags` | Tags filter | **Active** | Filter by product tags |
| `website_sale.search` | Search box | **Active** | Product search |
| `website_sale.sort` | Sort dropdown | **Active** | Sort products |
| `website_sale.add_grid_or_list_option` | Grid/List toggle | **Active** | View toggle button |

#### Product Item Options

| XML ID | Feature | Default | Description |
|--------|---------|---------|-------------|
| `website_sale.products_description` | Description | Inactive | Show description in listing |
| `website_sale.products_add_to_cart` | Add to Cart | Inactive | Add to cart button in listing |

#### Shop Visual Reference

```
┌─────────────────────────────────────────────────────────────────┐
│ SHOP PAGE (Categories Top - Default)                             │
├─────────────────────────────────────────────────────────────────┤
│  All  │  Category 1  │  Category 2  │  Category 3               │
├─────────────────────────────────────────────────────────────────┤
│  [Search...]          [Sort: Featured ▼]   [☷ Grid] [☰ List]   │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  [IMG]   │  │  [IMG]   │  │  [IMG]   │  │  [IMG]   │        │
│  │          │  │          │  │          │  │          │        │
│  │ Product 1│  │ Product 2│  │ Product 3│  │ Product 4│        │
│  │ $99.00   │  │ $149.00  │  │ $79.00   │  │ $199.00  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  [IMG]   │  │  [IMG]   │  │  [IMG]   │  │  [IMG]   │        │
│  │ ...      │  │ ...      │  │ ...      │  │ ...      │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
├─────────────────────────────────────────────────────────────────┤
│                    [1] [2] [3] ... [Next →]                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SHOP PAGE (Categories Left Sidebar)                              │
├────────────────┬────────────────────────────────────────────────┤
│ CATEGORIES     │  [Search...]     [Sort ▼]    [☷] [☰]          │
│ ─────────────  ├────────────────────────────────────────────────┤
│ □ All          │  ┌────────┐  ┌────────┐  ┌────────┐           │
│ ▸ Category 1   │  │ [IMG]  │  │ [IMG]  │  │ [IMG]  │           │
│   · Sub 1.1    │  │ Prod 1 │  │ Prod 2 │  │ Prod 3 │           │
│   · Sub 1.2    │  │ $99    │  │ $149   │  │ $79    │           │
│ ▸ Category 2   │  └────────┘  └────────┘  └────────┘           │
│ ▸ Category 3   │                                                │
│                │  ┌────────┐  ┌────────┐  ┌────────┐           │
│ PRICE          │  │ ...    │  │ ...    │  │ ...    │           │
│ ─────────────  │  └────────┘  └────────┘  └────────┘           │
│ $0 ─●────── $500│                                               │
│                │                                                │
│ TAGS           │                                                │
│ ─────────────  │                                                │
│ [New] [Sale]   │                                                │
└────────────────┴────────────────────────────────────────────────┘
```

---

### 📋 PRODUCT DETAIL PAGE TEMPLATES

| XML ID | Feature | Default | Description |
|--------|---------|---------|-------------|
| `website_sale.product_tags` | Product tags | **Active** | Display product tags |
| `website_sale.product_comment` | Reviews | Inactive | Discussion/rating section |
| `website_sale.product_custom_text` | Terms block | **Active** | Terms & conditions |
| `website_sale.product_share_buttons` | Share buttons | **Active** | Social share buttons |
| `website_sale.product_quantity` | Quantity selector | **Active** | Qty input field |
| `website_sale.product_buy_now` | Buy Now | Inactive | Quick buy button |
| `website_sale.product_variants` | Variants list | Inactive | List view of variants |
| `website_sale.alternative_products` | Alternatives | **Active** | Alternative products carousel |
| `website_sale.carousel_product_indicators_bottom` | Carousel bottom | **Active** | Image indicators at bottom |
| `website_sale.carousel_product_indicators_left` | Carousel left | Inactive | Image indicators on left |

#### Product Page Visual Reference

```
┌─────────────────────────────────────────────────────────────────┐
│ PRODUCT DETAIL PAGE                                              │
├─────────────────────────────────────────────────────────────────┤
│  Home > Category > Product Name                                  │
├───────────────────────────────┬─────────────────────────────────┤
│                               │                                  │
│  ┌─────────────────────────┐  │  Product Name                    │
│  │                         │  │  ★★★★☆ (24 reviews)             │
│  │      [MAIN IMAGE]       │  │                                  │
│  │                         │  │  $199.00                         │
│  │                         │  │  ̶$̶2̶4̶9̶.̶0̶0̶ -20%                     │
│  └─────────────────────────┘  │                                  │
│  [○] [○] [●] [○]              │  Color: [Blue ▼]                 │
│                               │  Size:  [M ▼]                    │
│  ┌──────┐ ┌──────┐ ┌──────┐  │                                  │
│  │thumb1│ │thumb2│ │thumb3│  │  Qty: [- 1 +]                    │
│  └──────┘ └──────┘ └──────┘  │                                  │
│                               │  [Add to Cart]  [Buy Now]        │
│                               │                                  │
│                               │  [♡ Wishlist] [🔗 Share]         │
│                               │                                  │
│                               │  Tags: [New] [Bestseller]        │
├───────────────────────────────┴─────────────────────────────────┤
│  DESCRIPTION  │  SPECIFICATIONS  │  REVIEWS (24)                 │
├─────────────────────────────────────────────────────────────────┤
│  Full product description text goes here...                      │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  ALTERNATIVE PRODUCTS                                            │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐                │
│  │ Alt 1  │  │ Alt 2  │  │ Alt 3  │  │ Alt 4  │                │
│  └────────┘  └────────┘  └────────┘  └────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

---

### 📋 BLOG PAGE TEMPLATES (website_blog module)

#### Blog Listing Options

| XML ID | Feature | Default | Description |
|--------|---------|---------|-------------|
| `website_blog.opt_blog_cover_post` | Latest post banner | **Active** | Show latest post as banner |
| `website_blog.opt_blog_cover_post_fullwidth_design` | Fullwidth banner | **Active** | Banner spans full width |
| `website_blog.opt_blog_list_view` | List view | Inactive | Posts as list vs grid |
| `website_blog.opt_blog_cards_design` | Cards design | Inactive | Bootstrap card components |
| `website_blog.opt_blog_readable` | Readability | **Active** | Larger, readable text |
| `website_blog.opt_blog_sidebar_show` | Sidebar | Inactive | Show blog sidebar |

#### Blog Sidebar Components (when enabled)

| XML ID | Feature | Default | Description |
|--------|---------|---------|-------------|
| `website_blog.opt_sidebar_blog_index_archives` | Archives | **Active** | Date-based archive |
| `website_blog.opt_sidebar_blog_index_follow_us` | Follow Us | **Active** | Social media links |
| `website_blog.opt_sidebar_blog_index_tags` | Tags | **Active** | Tag cloud |

#### Blog Post Loop Display

| XML ID | Feature | Default | Description |
|--------|---------|---------|-------------|
| `website_blog.opt_posts_loop_show_cover` | Cover image | **Active** | Featured image |
| `website_blog.opt_posts_loop_show_author` | Author | **Active** | Author name/avatar |
| `website_blog.opt_posts_loop_show_stats` | Stats | Inactive | Comment/view counts |
| `website_blog.opt_posts_loop_show_teaser` | Teaser | **Active** | Preview text and tags |

#### Blog Post Detail Options

| XML ID | Feature | Default | Description |
|--------|---------|---------|-------------|
| `website_blog.opt_blog_post_readable` | Readability | **Active** | Larger, readable text |
| `website_blog.opt_blog_post_sidebar` | Sidebar | Inactive | Show post sidebar |
| `website_blog.opt_blog_post_regular_cover` | Regular cover | Inactive | Title above cover |
| `website_blog.opt_blog_post_breadcrumb` | Breadcrumbs | **Active** | Navigation breadcrumbs |
| `website_blog.opt_blog_post_read_next` | Read next | **Active** | Next article banner |
| `website_blog.opt_blog_post_comment` | Comments | Inactive | Enable comments |
| `website_blog.opt_blog_post_select_to_tweet` | Tweet selection | Inactive | Highlight-to-tweet |

#### Blog Visual Reference

```
┌─────────────────────────────────────────────────────────────────┐
│ BLOG LISTING (Grid View - Default)                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐│
│  │             [FEATURED POST BANNER IMAGE]                     ││
│  │                                                              ││
│  │  Latest Article Title                                        ││
│  │  Short teaser text for the featured post...                  ││
│  │                        [Read More →]                         ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  All Posts  │  Category 1  │  Category 2  │  [Search...]        │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │   [IMAGE]      │  │   [IMAGE]      │  │   [IMAGE]      │    │
│  │                │  │                │  │                │    │
│  │ Post Title 1   │  │ Post Title 2   │  │ Post Title 3   │    │
│  │ By Author      │  │ By Author      │  │ By Author      │    │
│  │ Jan 15, 2024   │  │ Jan 10, 2024   │  │ Jan 5, 2024    │    │
│  │                │  │                │  │                │    │
│  │ Teaser text... │  │ Teaser text... │  │ Teaser text... │    │
│  │ [Tag1] [Tag2]  │  │ [Tag1]         │  │ [Tag2] [Tag3]  │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ BLOG POST DETAIL (Fullwidth Cover - Default)                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   [FULL WIDTH COVER IMAGE]                   ││
│  │                                                              ││
│  │           Article Title Goes Here                            ││
│  │           By Author Name  ·  January 15, 2024               ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│     Full article content with readable typography.               │
│                                                                  │
│     Multiple paragraphs of content...                            │
│                                                                  │
│     [Share: Facebook | Twitter | LinkedIn]                       │
│                                                                  │
│     Tags: [Technology] [Tutorial] [Odoo]                         │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  READ NEXT: Next Article Title                               ││
│  │  [Banner Image]                                              ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

### 📋 CART & CHECKOUT TEMPLATES

| XML ID | Feature | Default | Description |
|--------|---------|---------|-------------|
| `website_sale.suggested_products_list` | Suggested products | **Active** | Accessory products in cart |
| `website_sale.reduction_code` | Promo code | **Active** | Coupon code input |
| `website_sale.address_b2b` | B2B fields | Inactive | Business address fields |
| `website_sale.accept_terms_and_conditions` | T&C checkbox | Inactive | Require T&C acceptance |

---

## Design Workflow: Figma to Odoo

### The Methodology

When converting a Figma design to an Odoo theme, follow this workflow:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DESIGN WORKFLOW                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. ANALYZE DESIGN                                               │
│     ↓                                                            │
│     Extract: Colors, Fonts, Layout, Components                   │
│                                                                  │
│  2. COMPARE TO ODOO TEMPLATES                                    │
│     ↓                                                            │
│     Match: Header style, Footer style, Page layouts              │
│                                                                  │
│  3. CHOOSE CLOSEST TEMPLATE                                      │
│     ↓                                                            │
│     Select: Best matching header + footer + features             │
│                                                                  │
│  4. CONFIGURE VIA VARIABLES                                      │
│     ↓                                                            │
│     Set: $o-website-values-palettes configuration                │
│                                                                  │
│  5. ENHANCE WITH CUSTOM CSS                                      │
│     ↓                                                            │
│     Add: Only what templates can't provide                       │
│                                                                  │
│  6. CREATE CUSTOM SNIPPETS (if needed)                           │
│     ↓                                                            │
│     Build: Components not available in Odoo                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Step 1: Analyze the Figma Design

Extract these key elements:

| Element | What to Look For | Maps To |
|---------|------------------|---------|
| **Primary Color** | Main brand color (buttons, links, CTAs) | `o-color-1` |
| **Secondary Color** | Accent color, secondary buttons | `o-color-2` |
| **Light Background** | Section backgrounds, cards | `o-color-3` |
| **White/Base** | Main content background | `o-color-4` |
| **Dark/Text** | Headings, footer, dark sections | `o-color-5` |
| **Font Family** | Body text, headings | `$o-theme-font-configs` |
| **Header Style** | Navigation layout | `'header-template'` |
| **Footer Style** | Footer layout | `'footer-template'` |

### Step 2: Match Header Style

| If Design Has... | Use Template |
|-----------------|--------------|
| Standard horizontal nav | `template_header_default` |
| Hidden menu (hamburger icon) | `template_header_hamburger` |
| Full-width stretched nav | `template_header_stretch` |
| Vertical sidebar navigation | `template_header_vertical` |
| Prominent search bar | `template_header_search` |
| E-commerce with categories | `template_header_sales_two` |
| Top bar + main nav | `template_header_sales_one` |
| Sidebar with content | `template_header_sidebar` |
| Rounded/boxed container | `template_header_boxed` |

### Step 3: Match Footer Style

| If Design Has... | Use Template |
|-----------------|--------------|
| Multi-column with logo | `footer_custom` (default) |
| Detailed company info | `template_footer_descriptive` |
| Center-aligned minimal | `template_footer_centered` |
| Multiple link columns only | `template_footer_links` |
| Ultra-minimal copyright only | `template_footer_minimalist` |
| Contact info focus | `template_footer_contact` |
| Newsletter/CTA focus | `template_footer_call_to_action` |
| Large headline text | `template_footer_headline` |
| Modern slide-out effect | `template_footer_slideout` |

### Step 4: Generate Theme Configuration

Based on analysis, create the configuration:

```scss
// primary_variables.scss - Generated from Figma Analysis

$o-theme-font-configs: (
    'Poppins': (
        'family': ('Poppins', sans-serif),
        'url': 'Poppins:300,400,500,600,700',
    ),
);

$o-website-values-palettes: (
    (
        'color-palettes-name': 'default-1',

        // Typography (from Figma)
        'font': 'Poppins',
        'headings-font': 'Poppins',

        // Header (matched to closest template)
        'header-template': 'hamburger',  // Figma shows hamburger menu
        'header-links-style': 'pills',   // Rounded pill-style links
        'logo-height': 48px,

        // Footer (matched to closest template)
        'footer-template': 'contact',    // Figma shows contact-focused footer
        'footer-scrolltop': true,

        // Buttons (from Figma measurements)
        'btn-padding-y': 0.75rem,
        'btn-padding-x': 1.5rem,
        'btn-border-radius': 8px,

        // Layout
        'link-underline': 'never',
    )
);
```

### Step 5: Create theme.utils Implementation

```python
# models/theme_yourtheme.py

from odoo import models

class ThemeYourTheme(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_yourtheme_post_copy(self, mod):
        # Enable matched header template
        self.enable_view('website.template_header_hamburger')
        self.enable_view('website.template_header_hamburger_mobile_align_center')

        # Enable matched footer template
        self.enable_view('website.template_footer_contact')

        # Enable desired header components
        self.enable_view('website.option_header_brand_logo')
        self.enable_view('website.header_search_box')

        # Configure visibility effect
        self.disable_view('website.header_visibility_standard')
        self.enable_view('website.header_visibility_fixed')
```

### Decision Flowchart: Header Selection

```
START: Analyze header design
    │
    ├─ Is navigation hidden by default?
    │   │
    │   ├─ YES → template_header_hamburger
    │   │
    │   └─ NO → Is there a vertical sidebar?
    │           │
    │           ├─ YES → Is it full-page sidebar?
    │           │   │
    │           │   ├─ YES → template_header_sidebar
    │           │   └─ NO → template_header_vertical
    │           │
    │           └─ NO → Is it e-commerce focused?
    │                   │
    │                   ├─ YES → Does it have category mega-menu?
    │                   │   │
    │                   │   ├─ YES → template_header_sales_two
    │                   │   └─ NO → template_header_sales_one
    │                   │
    │                   └─ NO → Is search prominent?
    │                           │
    │                           ├─ YES → template_header_search
    │                           │
    │                           └─ NO → Is it boxed/contained?
    │                                   │
    │                                   ├─ YES → template_header_boxed
    │                                   │
    │                                   └─ NO → Is it full-width?
    │                                           │
    │                                           ├─ YES → template_header_stretch
    │                                           └─ NO → template_header_default
```

### Decision Flowchart: Footer Selection

```
START: Analyze footer design
    │
    ├─ Is it minimal (just copyright)?
    │   │
    │   ├─ YES → template_footer_minimalist
    │   │
    │   └─ NO → Is it center-aligned?
    │           │
    │           ├─ YES → template_footer_centered
    │           │
    │           └─ NO → Is there a newsletter/CTA?
    │                   │
    │                   ├─ YES → template_footer_call_to_action
    │                   │
    │                   └─ NO → Is it contact info focused?
    │                           │
    │                           ├─ YES → template_footer_contact
    │                           │
    │                           └─ NO → Is it primarily links?
    │                                   │
    │                                   ├─ YES → template_footer_links
    │                                   │
    │                                   └─ NO → Has detailed description?
    │                                           │
    │                                           ├─ YES → template_footer_descriptive
    │                                           │
    │                                           └─ NO → footer_custom (default)
```

---

## Website Snippets Complete Reference

This section documents ALL available snippets in Odoo, how they work, and how to create custom ones. Use this when building website pages, creating custom snippets, or understanding the website builder.

---

### 📚 SNIPPET ARCHITECTURE OVERVIEW

Snippets are reusable building blocks for Odoo website pages, enabling drag-and-drop page construction.

```
┌─────────────────────────────────────────────────────────────────┐
│                     ODOO SNIPPET SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │  STATIC SNIPPETS │    │ DYNAMIC SNIPPETS │                   │
│  ├──────────────────┤    ├──────────────────┤                   │
│  │ • Pre-built HTML │    │ • Data-driven    │                   │
│  │ • 81+ templates  │    │ • ir.filters     │                   │
│  │ • Drag & drop    │    │ • Display temps  │                   │
│  └──────────────────┘    └──────────────────┘                   │
│                              │                                   │
│  ┌───────────────────────────┴────────────────────────────────┐ │
│  │                   SNIPPET OPTIONS SYSTEM                    │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │  we-select | we-button | we-colorpicker | we-input | etc.  │ │
│  │  data-selector | data-select-class | data-js | data-css    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

### 📋 STATIC SNIPPETS INVENTORY (81+ Templates)

Odoo provides **81+ static snippet templates** organized into 6 main categories:

| Category | Count | Purpose |
|----------|-------|---------|
| Structure | 14 | Page sections, layouts |
| Gallery/Media | 3 | Image galleries, carousels |
| Features | 11 | Feature showcases |
| Dynamic Content | 15 | Maps, forms, embeds |
| Inner Content | 16 | Cards, quotes, text blocks |
| Mega Menus | 9 | Navigation menus |

#### Structure Snippets (14)

| Snippet ID | Name | Description | Best For |
|------------|------|-------------|----------|
| `s_banner` | Banner | Hero section with background | Landing pages |
| `s_cover` | Cover | Full-width cover image | Headers |
| `s_text_image` | Text - Image | Two-column: text left, image right | Features |
| `s_image_text` | Image - Text | Two-column: image left, text right | Features |
| `s_title` | Title | Section title with subtitle | Section headers |
| `s_text_block` | Text Block | Multi-column text content | Content |
| `s_numbers` | Numbers | Statistics/counters display | Achievements |
| `s_picture` | Picture | Single large image | Visual focus |
| `s_three_columns` | Columns | Three-column layout | Content grids |
| `s_big_boxes` | Big Boxes | Large feature boxes | Services |
| `s_features` | Features | Feature grid with icons | Benefits |
| `s_masonry_block` | Masonry Block | Masonry-style grid | Galleries |
| `s_image_gallery` | Image Gallery | Multi-image gallery | Portfolios |
| `s_images_wall` | Images Wall | Wall-style display | Media |

#### Features Snippets (11)

| Snippet ID | Name | Description | Best For |
|------------|------|-------------|----------|
| `s_comparisons` | Comparisons | Side-by-side comparison | Product comparison |
| `s_company_team` | Company Team | Team member cards | About pages |
| `s_call_to_action` | Call to Action | CTA section with button | Conversions |
| `s_references` | References | Client logos/references | Social proof |
| `s_accordion` | Accordion | Collapsible content | FAQs |
| `s_features_grid` | Features Grid | Grid of feature icons | Benefits |
| `s_table_of_content` | Table of Content | Scrollspy navigation | Long pages |
| `s_pricelist` | Pricelist | Pricing table | Products |
| `s_product_list` | Product List | Product showcase | E-commerce |
| `s_faq_collapse` | FAQ | Frequently asked questions | Support |
| `s_tabs` | Tabs | Tabbed content | Organization |

#### Dynamic Content Snippets (15)

| Snippet ID | Name | Description | Best For |
|------------|------|-------------|----------|
| `s_google_map` | Google Map | Google Maps embed | Contact pages |
| `s_map` | Map | Leaflet/OpenStreetMap | Locations |
| `s_embed_code` | Embed Code | Custom HTML/embed | Third-party |
| `s_website_form` | Website Form | Contact/custom forms | Lead capture |
| `s_searchbar` | Searchbar | Search functionality | Navigation |
| `s_social_media` | Social Media | Social links | Engagement |
| `s_share` | Share | Share buttons | Content sharing |
| `s_dynamic_snippet` | Dynamic Snippet | Base dynamic content | Data display |
| `s_dynamic_snippet_carousel` | Dynamic Carousel | Dynamic carousel | Featured content |
| `s_chart` | Chart | Data visualization | Reports |
| `s_countdown` | Countdown | Timer/countdown | Events |
| `s_popup` | Popup | Modal popup | Promotions |
| `s_newsletter_block` | Newsletter | Email subscription | Marketing |
| `s_newsletter_popup` | Newsletter Popup | Popup subscription | Lead capture |
| `s_newsletter_subscribe_form` | Newsletter Form | Inline subscription | Footer |

#### Inner Content Snippets (16)

| Snippet ID | Name | Description | Best For |
|------------|------|-------------|----------|
| `s_hr` | Horizontal Rule | Divider line | Section breaks |
| `s_alert` | Alert | Alert/notification box | Notices |
| `s_card` | Card | Content card | Items |
| `s_three_cards` | Three Cards | Three-card layout | Services |
| `s_four_cards` | Four Cards | Four-card layout | Features |
| `s_timeline` | Timeline | Timeline display | History |
| `s_process_steps` | Process Steps | Step-by-step guide | Tutorials |
| `s_quotes_carousel` | Quotes Carousel | Testimonial slider | Social proof |
| `s_quotes_grid` | Quotes Grid | Testimonial grid | Reviews |
| `s_rating` | Rating | Star rating display | Reviews |
| `s_progress_bar` | Progress Bar | Progress indicator | Statistics |
| `s_blockquote` | Blockquote | Styled quote | Emphasis |
| `s_badge` | Badge | Badge/label | Labels |
| `s_button` | Button | Styled button | CTAs |
| `s_separator` | Separator | Section separator | Visual breaks |
| `s_text_highlight` | Text Highlight | Highlighted text box | Emphasis |

#### Mega Menu Snippets (9)

| Snippet ID | Name | Description |
|------------|------|-------------|
| `s_mega_menu_multi_menus` | Multi Menus | Multiple menu columns |
| `s_mega_menu_menu_image_menu` | Menu Image Menu | Three-section with image |
| `s_mega_menu_little_icons` | Little Icons | Icon-based menu |
| `s_mega_menu_images_subtitles` | Images Subtitles | Images with subtitles |
| `s_mega_menu_cards` | Cards | Card-style menu |
| `s_mega_menu_big_icons` | Big Icons | Large icon menu |
| `s_mega_menu_thumbnails` | Thumbnails | Thumbnail gallery menu |
| `s_mega_menu_odoo_menu` | Odoo Menu | Odoo-style menu |
| `s_mega_menu_no_extra_info` | No Extra Info | Simple menu |

---

### 📋 DYNAMIC SNIPPETS SYSTEM

Dynamic snippets fetch data from the database and render using templates.

#### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  DYNAMIC SNIPPET FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐                                           │
│  │   DATA SOURCE    │ ← ir.filters / ir.actions.server          │
│  └────────┬─────────┘                                           │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │ DYNAMIC FILTER   │ ← website.snippet.filter model            │
│  │ (Data Fetcher)   │                                           │
│  └────────┬─────────┘                                           │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │ DISPLAY TEMPLATE │ ← dynamic_filter_template_*               │
│  │   (Renderer)     │                                           │
│  └──────────────────┘                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Product Dynamic Snippets (website_sale)

**Main Snippet**: `s_dynamic_snippet_products`

**Display Templates (15 variants)**:

| Template Key | Name | Style |
|--------------|------|-------|
| `dynamic_filter_template_product_product_add_to_cart` | Add to Cart | With purchase button |
| `dynamic_filter_template_product_product_banner` | Banner | Large banner format |
| `dynamic_filter_template_product_product_borderless_1/2/3` | Borderless | Clean borderless |
| `dynamic_filter_template_product_product_card_style` | Card Style | Card-based |
| `dynamic_filter_template_product_product_centered` | Centered | Center-aligned |
| `dynamic_filter_template_product_product_horizontal_card` | Horizontal Card | Horizontal layout |
| `dynamic_filter_template_product_product_mini` | Mini | Compact display |
| `dynamic_filter_template_product_product_minimalist_1/2/3/4` | Minimalist | Minimal designs |
| `dynamic_filter_template_product_product_picture` | Picture | Image-focused |

**Dynamic Filters (6 data sources)**:

| Filter ID | Name | Logic |
|-----------|------|-------|
| `dynamic_filter_newest_products` | Newest Products | Sorted by create_date desc |
| `dynamic_filter_recently_sold_products` | Recently Sold | Products with recent sales |
| `dynamic_filter_recently_viewed_products` | Recently Viewed | User's browsing history |
| `dynamic_filter_accessories` | Accessories | Related accessories |
| `dynamic_filter_products_sold_with` | Sold With | Frequently bought together |
| `dynamic_filter_alternative_products` | Alternative | Similar products |

#### Blog Dynamic Snippets (website_blog)

**Main Snippet**: `s_blog_posts`

**Display Templates (4 layouts)**:

| Template Key | Name |
|--------------|------|
| `dynamic_filter_template_blog_post_big_picture` | Big Picture |
| `dynamic_filter_template_blog_post_card` | Card |
| `dynamic_filter_template_blog_post_horizontal` | Horizontal |
| `dynamic_filter_template_blog_post_vertical` | Vertical |

**Filters**: `dynamic_filter_latest_posts`, `dynamic_filter_most_read_posts`

#### Event Dynamic Snippets (website_event)

**Main Snippet**: `s_events`

**Display Templates**: `dynamic_filter_template_event_event_card`, `dynamic_filter_template_event_event_list`

**Filter**: `dynamic_filter_upcoming_events`

---

### 📋 SNIPPET OPTIONS SYSTEM

The options system allows users to customize snippets in the website editor.

#### We-* Elements Reference

| Element | Purpose | Key Attributes |
|---------|---------|----------------|
| `we-select` | Dropdown selection | `data-name`, `data-dependencies` |
| `we-button` | Toggle button | `data-select-class`, `data-toggle-class` |
| `we-colorpicker` | Color picker | `data-css-property`, `data-color-prefix` |
| `we-input` | Text/number input | `data-attribute-name`, `data-unit` |
| `we-range` | Slider | `data-min`, `data-max`, `data-step` |
| `we-checkbox` | Checkbox toggle | `data-select-class` |
| `we-button-group` | Grouped buttons | For alignment, etc. |
| `we-row` | Option row | Groups related inputs |
| `we-select-pager` | Paginated selection | For large option sets |

#### Data Attributes Reference

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `data-selector` | Target CSS selector | `data-selector=".s_banner"` |
| `data-select-class` | Toggle CSS class | `data-select-class="shadow-lg"` |
| `data-select-style` | Enable style editing | `data-select-style="true"` |
| `data-css-property` | CSS property to modify | `data-css-property="padding"` |
| `data-js` | JavaScript handler class | `data-js="BackgroundImage"` |
| `data-dependencies` | Show based on other options | `data-dependencies="image_opt"` |
| `data-exclude` | Hide for certain elements | `data-exclude=".no-shadow"` |
| `data-no-preview` | Disable live preview | `data-no-preview="true"` |
| `data-attribute-name` | HTML attribute to set | `data-attribute-name="data-speed"` |

#### Built-in JavaScript Handlers

| Handler | Purpose |
|---------|---------|
| `BackgroundImage` | Background image management |
| `BackgroundPosition` | Image positioning |
| `BackgroundToggler` | Toggle background type |
| `ColoredLevelBackground` | Color palette backgrounds |
| `BackgroundShape` | Decorative shapes |
| `ImageTools` | Image editing |
| `ReplaceMedia` | Media replacement |
| `FontawesomeTools` | Icon management |
| `Carousel` | Carousel controls |
| `DynamicSnippet` | Dynamic content options |

#### Complete Options Template Example

```xml
<template id="s_my_snippet_options" inherit_id="website.snippet_options">
    <xpath expr="." position="inside">
        <div data-js="MySnippetHandler"
             data-selector=".s_my_snippet"
             data-drop-in=".oe_structure"
             data-drop-near="section">

            <!-- Layout Selection -->
            <we-select string="Layout" data-name="layout_opt">
                <we-button data-select-class="layout-grid">Grid</we-button>
                <we-button data-select-class="layout-list">List</we-button>
            </we-select>

            <!-- Color Options -->
            <we-colorpicker string="Background"
                            data-name="bg_color_opt"
                            data-select-style="true"
                            data-css-property="background-color"/>

            <!-- Spacing -->
            <we-range string="Spacing"
                      data-name="spacing_opt"
                      data-select-style="true"
                      data-css-property="gap"
                      data-min="0"
                      data-max="100"
                      data-step="5"
                      data-unit="px"/>

            <!-- Conditional Option -->
            <we-select string="Shadow Size"
                       data-name="shadow_size_opt"
                       data-dependencies="shadow_opt">
                <we-button data-select-class="shadow-sm">Small</we-button>
                <we-button data-select-class="shadow-lg">Large</we-button>
            </we-select>

        </div>
    </xpath>
</template>
```

---

### 📋 CREATING CUSTOM SNIPPETS (VERSION-AWARE)

#### Odoo 14-17: Simple Registration

```xml
<!-- 1. Snippet Template -->
<template id="s_my_snippet" name="My Snippet">
    <section class="s_my_snippet pt48 pb48 o_cc o_cc1">
        <div class="container">
            <div class="row">
                <div class="col-lg-12 text-center">
                    <h2>My Custom Snippet</h2>
                    <p>Content goes here...</p>
                </div>
            </div>
        </div>
    </section>
</template>

<!-- 2. Snippet Registration -->
<template id="s_my_snippet_insert" inherit_id="website.snippets">
    <xpath expr="//div[@id='snippet_structure']//t[@t-snippet][last()]" position="after">
        <t t-snippet="my_module.s_my_snippet"
           t-thumbnail="/my_module/static/src/img/snippets/s_my_snippet.svg">
            <keywords>my, custom, snippet</keywords>
        </t>
    </xpath>
</template>
```

#### Odoo 18-19: With Snippet Groups

```xml
<!-- 1. Snippet Template (same as above) -->

<!-- 2. Optional: Custom Snippet Group -->
<template id="snippet_group_custom" inherit_id="website.snippets">
    <xpath expr="//div[@id='snippet_groups']" position="inside">
        <t snippet-group="custom"
           t-snippet="website.s_snippet_group"
           string="Custom Snippets"/>
    </xpath>
</template>

<!-- 3. Snippet Registration with Group -->
<template id="s_my_snippet_insert" inherit_id="website.snippets">
    <xpath expr="//div[@id='snippet_structure']/*[1]" position="before">
        <t t-snippet="my_module.s_my_snippet"
           string="My Snippet"
           group="custom"
           t-thumbnail="/my_module/static/src/img/snippets/s_my_snippet.svg"/>
    </xpath>
</template>
```

#### Snippet Panel Categories

| Panel ID | Category | XPath Target |
|----------|----------|--------------|
| `snippet_mega_menu` | Mega Menu | `//div[@id='snippet_mega_menu']` |
| `snippet_structure` | Structure | `//div[@id='snippet_structure']` |
| `snippet_media` | Gallery | `//div[@id='snippet_media']` |
| `snippet_feature` | Features | `//div[@id='snippet_feature']` |
| `snippet_dynamic` | Dynamic Content | `//div[@id='snippet_dynamic']` |
| `snippet_inner_content` | Inner Content | `//div[@id='snippet_inner_content']` |

---

### 📋 SNIPPET JAVASCRIPT INTEGRATION

#### publicWidget Pattern for Snippets

```javascript
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.MySnippet = publicWidget.Widget.extend({
    selector: '.s_my_snippet',
    disabledInEditableMode: false,  // Allow in website builder

    events: {
        'click .load-more': '_onLoadMore',
    },

    start: function () {
        // CRITICAL: Check editableMode for builder compatibility
        if (!this.editableMode) {
            this._initializeAnimations();
        }
        return this._super(...arguments);
    },

    _initializeAnimations: function () {
        // Animation code that should NOT run in edit mode
        this.$el.addClass('animated');
    },

    _onLoadMore: function (ev) {
        ev.preventDefault();
        if (this.editableMode) return;  // Don't run in edit mode
        // Handler logic
    },

    destroy: function () {
        // CRITICAL: Clean up event listeners
        $(window).off('.mySnippet');
        this._super(...arguments);
    },
});

export default publicWidget.registry.MySnippet;
```

#### Snippet Options JavaScript Handler

```javascript
/** @odoo-module **/

import options from "@web_editor/js/editor/snippets.options";

options.registry.MySnippetOption = options.Class.extend({
    /**
     * Handle data attribute changes
     */
    selectDataAttribute: function(previewMode, widgetValue, params) {
        this._super(...arguments);
        if (params.attributeName === 'layout') {
            this._applyLayout(widgetValue);
        }
    },

    _applyLayout: function(layout) {
        this.$target.removeClass('layout-grid layout-list');
        this.$target.addClass(`layout-${layout}`);
    },

    /**
     * Compute option visibility
     */
    _computeWidgetVisibility: function(methodName, params) {
        if (methodName === 'showAdvanced') {
            return this.$target.hasClass('advanced-mode');
        }
        return this._super(...arguments);
    },
});
```

---

### 📋 VERSION DIFFERENCES FOR SNIPPETS

| Feature | Odoo 14-15 | Odoo 16-17 | Odoo 18-19 |
|---------|------------|------------|------------|
| **Snippet Count** | ~40 | 81+ | 155+ |
| **Registration** | Simple XPath | Simple XPath | Groups required |
| **Asset System** | Template inherit | ir.asset model | ir.asset model |
| **JavaScript** | `odoo.define()` | ES6 modules | Plugin-based |
| **Bootstrap** | 4.x | 5.1.3 | 5.1.3 |
| **Dynamic Snippets** | Basic | Full | Full + Categories |
| **Editor** | Legacy | Legacy | Plugin architecture |

#### Odoo 19 Plugin Pattern (New)

```javascript
import { Plugin } from "@html_editor/plugin";
import { registry } from "@web/core/registry";

export class MySnippetPlugin extends Plugin {
    static id = "mySnippet";
    static dependencies = ["builderOptions", "builderActions"];

    resources = {
        builder_options: [{
            template: "my_module.MySnippetOption",
            selector: "section",
            applyTo: ".s_my_snippet",
        }],
        builder_actions: {
            MyAction: { /* action definition */ },
        },
    };
}

registry.category("website-plugins").add("mySnippet", MySnippetPlugin);
```

---

### 📋 CREATING DYNAMIC SNIPPETS

#### Step 1: Define the Filter

```xml
<record id="dynamic_filter_my_items" model="website.snippet.filter">
    <field name="name">My Items</field>
    <field name="model_name">my.model</field>
    <field name="limit">12</field>
    <field name="filter_id" ref="ir_filter_my_items"/>
</record>

<record id="ir_filter_my_items" model="ir.filters">
    <field name="name">Latest Items</field>
    <field name="model_id">my.model</field>
    <field name="domain">[('is_published', '=', True)]</field>
    <field name="sort">create_date desc</field>
</record>
```

#### Step 2: Create Display Template

```xml
<template id="dynamic_filter_template_my_model_card" name="My Model Card">
    <t t-foreach="records" t-as="record">
        <div class="col-lg-4 mb-4">
            <div class="card h-100 shadow-sm">
                <img t-att-src="record.image_url" class="card-img-top"/>
                <div class="card-body">
                    <h5 class="card-title" t-esc="record.name"/>
                    <p class="card-text" t-esc="record.description"/>
                </div>
            </div>
        </div>
    </t>
</template>
```

#### Step 3: Create Dynamic Snippet

```xml
<template id="s_dynamic_my_items" name="Dynamic My Items">
    <section class="s_dynamic_snippet s_dynamic_my_items pt48 pb48"
             data-snippet="s_dynamic_my_items"
             data-name="Dynamic My Items"
             data-filter-id="my_module.dynamic_filter_my_items"
             data-template-key="my_module.dynamic_filter_template_my_model_card"
             data-number-of-elements="6"
             data-number-of-elements-small-devices="2">
        <div class="container">
            <div class="row">
                <h2 class="col-12 text-center mb-4">Featured Items</h2>
            </div>
            <div class="dynamic_snippet_template row"/>
        </div>
    </section>
</template>
```

---

## Updated /create-theme Command (v6.0)

The `/create-theme` command now automatically generates the `models/theme_xxx.py` file with template activation.

### What Gets Created (v6.0)

```
theme_<name>/
├── __init__.py                        # Imports models
├── __manifest__.py                    # Updated with models/ import
├── models/
│   ├── __init__.py                   # Imports theme_<name>
│   └── theme_<name>.py               # theme.utils implementation (NEW!)
├── security/
│   └── ir.model.access.csv
├── data/
│   ├── assets.xml
│   ├── menu.xml
│   └── pages/
│       ├── home_page.xml
│       ├── aboutus_page.xml
│       └── contactus_page.xml
├── views/
│   ├── layout/
│   │   └── templates.xml
│   └── snippets/
│       └── custom_snippets.xml
└── static/src/
    ├── scss/
    │   ├── primary_variables.scss
    │   └── theme.scss
    ├── js/
    │   └── theme.js
    └── img/
```

### Generated theme_<name>.py

```python
from odoo import models


class Theme<Name>(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_<name>_post_copy(self, mod):
        """
        Configure theme defaults when installed on a website.

        This method is called automatically when the theme is applied.
        Use enable_view() and disable_view() to configure templates.
        """
        # === HEADER CONFIGURATION ===
        # Enable desired header template (only one can be active)
        self.enable_view('website.template_header_<detected>')

        # Configure header visibility
        self.disable_view('website.header_visibility_standard')
        self.enable_view('website.header_visibility_fixed')

        # Enable header components
        self.enable_view('website.option_header_brand_logo')

        # === FOOTER CONFIGURATION ===
        # Enable desired footer template (only one can be active)
        self.enable_view('website.template_footer_<detected>')
```

---

## Changelog

- **v7.0.0**: Website Snippets Complete Reference (MAJOR)
  - **NEW: Complete Static Snippets Inventory (81+ Templates)**
    - Structure snippets (s_banner, s_cover, s_parallax, etc.)
    - Feature snippets (s_features, s_comparisons, s_image_text, etc.)
    - Dynamic content snippets (s_dynamic_snippet_*, products, blog, events)
    - Inner content snippets (s_hr, s_badge, s_card, s_blockquote, etc.)
    - Mega menu snippets (s_mega_menu_*, multi_menus, odoo_menu)
  - **NEW: Dynamic Snippets System Documentation**
    - website.snippet.filter model architecture
    - 15 product display templates (dynamic_filter_template_*)
    - 6 built-in product snippet filters
    - Blog and event dynamic snippet patterns
  - **NEW: Snippet Options System Reference**
    - Complete we-* elements (we-select, we-button, we-colorpicker, we-input, we-range, we-checkbox)
    - Data attributes reference (data-selector, data-select-class, data-js, data-css-property, data-dependencies)
    - Built-in JavaScript handlers (BackgroundImage, Carousel, ImageTools, etc.)
    - Complete snippet options XML example
  - **NEW: Version-Aware Custom Snippet Creation**
    - Odoo 14-17 simple t-snippet registration
    - Odoo 18-19 snippet groups pattern
    - XPath insertion techniques
  - **NEW: Odoo 19 Plugin Pattern Documentation**
    - @html_editor/plugin based architecture
    - 130+ plugin files reference
    - SnippetOption class pattern
  - **NEW: Creating Dynamic Snippets Guide**
    - Define filter (website.snippet.filter)
    - Create display template (dynamic_filter_template_*)
    - Create dynamic snippet with data-filter-id

- **v6.0.0**: Theme Feature Activation System & Dynamic Page Reference (MAJOR)
  - **NEW: Theme Feature Activation System**
    - Complete `theme.utils` model documentation
    - `_theme_{module}_post_copy()` pattern requirement
    - `enable_view()` and `disable_view()` method reference
    - Mutual exclusivity rules for headers/footers
    - Complete working examples
  - **NEW: Complete Dynamic Page Reference**
    - 11 header templates with XML IDs and visual diagrams
    - 9 footer templates with XML IDs and visual diagrams
    - All shop page templates (categories, filters, layout)
    - All product detail page templates
    - All blog templates (listing, detail, sidebar)
    - Cart and checkout templates
  - **NEW: Design Workflow Methodology**
    - Figma analysis extraction guide
    - Template matching decision flowcharts
    - Configuration generation from design
    - Step-by-step workflow documentation
  - **UPDATED: /create-theme command v6.0**
    - Now generates `models/theme_xxx.py` automatically
    - Template activation based on configuration
    - Complete module structure with all required files

- **v5.1.0**: Comprehensive Variable Reference Enhancement (MAJOR)
  - **Complete $o-theme-font-configs reference**:
    - 'family': CSS font-family list (tuple format)
    - 'url': Google Fonts parameter ONLY (not full URL)
    - 'properties': Per-context CSS overrides (base, headings, navbar, buttons)
    - Font aliases documentation: 'base', 'headings', 'h2'-'h6', 'navbar', 'buttons'
    - Arabic/RTL font support examples
  - **Complete $o-color-palettes reference**:
    - 5 core colors semantic meanings (o-color-1 through o-color-5)
    - Color combinations (o_cc1 - o_cc5) presets and usage
    - Override syntax for color combinations (`'o-cc{n}-{property}'`)
    - Component assignments (menu, footer, copyright)
    - HTML usage examples with color classes
  - **Complete $o-website-values-palettes reference (115+ keys)**:
    - Typography & Fonts (13 keys): font family configuration
    - Font Sizes (13 keys): base and heading sizes
    - Line Heights & Margins (33 keys): spacing configuration
    - Buttons (17 keys): padding, radius, style options
    - Inputs (12 keys): form field styling
    - Header (13 keys): templates, link styles, logo, hamburger
    - Footer (3 keys): templates, effects, scrolltop
    - Links (1 key): underline behavior
    - Layout (3 keys): full/boxed, background
    - Colors & Gradients (5 keys): palette selection, gradients
    - Google Fonts (2 keys): additional fonts
  - **Restored full theme structure**: header.xml, footer.xml, snippets (OPTIONAL but present in hierarchy)
  - **Removed redundant documentation sections**: Cleaned up duplicate content
- **v5.0.0**: Major enhancement based on comprehensive variable system analysis
  - Variables can control header/footer templates without custom XML
  - Configure via `'header-template'` and `'footer-template'` variables
  - Bootstrap control via `$o-website-values-palettes`
- **v4.0.0**: CRITICAL fixes based on real-world theme development issues
  - **⚠️ SCSS Load Order Documentation**: Documented that theme SCSS loads BEFORE core variables
  - **Removed map-merge() patterns**: Fixed examples that used `map-merge()` with core variables (causes "Undefined variable" errors)
  - **Font loading fix**: Use `$o-theme-font-configs` as standalone, NOT via `ir.asset` records
  - **XPath simplification**: Use simple expressions (//header) not complex ones (//header//nav)
  - **Enhanced troubleshooting**: Added SCSS debugging, asset cache clearing, silent compilation failures
  - **Corrected all templates**: `/create-theme` command now generates working code without map-merge issues
- **v3.1.0**: Added `/create-theme` command for complete theme generation based on 40+ real implementations
  - Complete `$o-website-values-palettes` configuration
  - Semantic color system (`o-color-1` to `o-color-5`)
  - Individual page files pattern (best practice)
  - publicWidget patterns with `editableMode` handling
  - Version-specific snippet registration (14-19)
  - Windows console encoding fix for script output
- **v3.0.0**: Enhanced theme system with $o-website-values-palettes reference and mirror model architecture
- **v2.0.0**: Added PWA support, TypeScript, testing frameworks, performance optimization, accessibility, real-time features, and modern build tools
- **v1.0.0**: Initial release with full Odoo 14-19 support, Figma/DevTools MCP integration

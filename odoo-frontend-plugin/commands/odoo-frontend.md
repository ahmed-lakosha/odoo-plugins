---
title: 'Odoo Frontend'
read_only: false
type: 'command'
description: 'Odoo frontend toolkit — theme creation, version detection, and capabilities overview'
argument-hint: '[create-theme] [args...]'
---

# /odoo-frontend

Unified entry point for Odoo frontend development. Routes to sub-commands or shows environment status.

## Routing

Parse `$ARGUMENTS`:

- **`create-theme`** args present --> jump to [Section: Create Theme](#create-theme-pipeline)
- **No args / `status` / `help`** --> jump to [Section: Status and Help](#status-and-help)

---

## Status and Help

### Environment Detection

Detect the current Odoo environment by scanning the working directory:

```
1. Walk up from $CWD looking for odoo-bin or odoo/__init__.py
2. Read the version from odoo/release.py -> version_info
3. Map to Bootstrap version:
   - Odoo 14-15 -> Bootstrap 4.x
   - Odoo 16-19 -> Bootstrap 5.1.3
4. Scan for projects/ directory and list available theme modules (theme_*)
5. Check for active conf files in conf/
```

Display the result:

```
Odoo Frontend Toolkit v4.0
==========================

Environment
  Odoo version : 17.0 (detected from path)
  Bootstrap    : 5.1.3
  Owl          : v2
  Python       : 3.10+

Project
  Path         : projects/my_project
  Config       : conf/my_project17.conf
  Themes found : theme_my_project (installed)

Sub-commands
  /odoo-frontend create-theme   Generate a complete Odoo theme from Figma or manual specs
```

### Sub-commands Table

| Sub-command | Description | Example |
|-------------|-------------|---------|
| `create-theme` | Figma-to-Odoo theme pipeline | `/odoo-frontend create-theme --figma <url>` |
| *(no args)* | Show environment status + help | `/odoo-frontend` |

### Natural Language Examples

Users may phrase requests in natural language. Map them to the right sub-command:

| User says | Route to |
|-----------|----------|
| "Create a theme from this Figma design" | `create-theme --figma <url>` |
| "Scaffold a new Odoo theme" | `create-theme <name> <path>` |
| "Generate theme with these colors" | `create-theme --colors="..."` |
| "What Odoo version am I on?" | status (no args) |
| "Show frontend capabilities" | status (no args) |

### Version Compatibility Matrix

| Odoo | Bootstrap | Owl | JavaScript | CSS Classes |
|------|-----------|-----|------------|-------------|
| 14 | 4.x | - | ES6+ | `ml-*`, `mr-*` |
| 15 | 4.x | v1 | ES6+ | `ml-*`, `mr-*` |
| 16 | 5.1.3 | v1 | ES2020+ | `ms-*`, `me-*` |
| 17 | 5.1.3 | v2 | ES2020+ | `ms-*`, `me-*` |
| 18 | 5.1.3 | v2 | ES2020+ | `ms-*`, `me-*` |
| 19 | 5.1.3 | v2 | ES2020+ | `ms-*`, `me-*` |

### Previously Available Commands

These commands are available as separate entry points in the plugin:

| Command | Description |
|---------|-------------|
| `/theme_web_rec` | Create theme mirror models for multi-website support |

---

## Create Theme Pipeline

**Figma-to-Odoo theme generator.** Extracts design variables from Figma via Chrome browser automation (or accepts manual color/font specs), then scaffolds a complete, installable Odoo theme module.

### Usage

```bash
# Recommended: Interactive with Figma URL
/odoo-frontend create-theme --figma <figma_url>

# Full arguments
/odoo-frontend create-theme <theme_name> <project_path> --figma <figma_url> --version=17

# Manual mode (no Figma)
/odoo-frontend create-theme <theme_name> <project_path> --colors="#207AB7,#FB9F54,#F6F4F0,#FFFFFF,#191A19"
```

### Prerequisites

1. **Chrome browser** with the Claude-in-Chrome MCP extension (for Figma mode)
2. **Figma access** -- logged in via Chrome, with view access to the design file
3. **Odoo project** -- an existing project directory under `projects/`
4. **Supported Figma URLs**:
   - `https://www.figma.com/file/XXXX/Design-Name`
   - `https://www.figma.com/design/XXXX/Design-Name`
   - `https://www.figma.com/proto/XXXX/Design-Name`

### Pipeline Overview

```
Phase 1: Figma Design Extraction
  Open Figma in Chrome -> Navigate to PAGES (not components!)
  -> Extract colors from page elements (header, buttons, backgrounds)
  -> Extract typography from page headings (H1-H6, body, fonts)
        |
        v
Phase 2: Typography Hierarchy Mapping
  Map extracted sizes to Odoo multipliers (base = 16px)
  H1-H6 -> $o-theme-h*-font-size-multiplier
  Sizes > H1 -> Bootstrap display-* classes
  H6 is ALWAYS 16px (1rem) -- this is the fixed base
        |
        v
Phase 3: Color Palette Mapping
  Map Figma colors to Odoo semantic system:
    Primary    -> o-color-1 (buttons, links, headers)
    Secondary  -> o-color-2 (CTAs, highlights)
    Light BG   -> o-color-3 (sections, cards)
    White      -> o-color-4 (body background)
    Dark Text  -> o-color-5 (headings, body text)
  Auto-derive missing colors if only 2 found
        |
        v
Phase 4: Theme File Generation
  Scaffold complete module -> See "Generated Structure" below
  Key file: primary_variables.scss (SCSS load order matters!)
        |
        v
Phase 5: Installation and Testing
  Install theme -> Check for errors -> Auto-fix (up to 3 retries)
  Verify: CSS compiles, no console errors, responsive layout works
```

### Phase 1: Figma Extraction Details

**CRITICAL: Navigate to PAGES, not components.** Always extract design variables from actual pages (Homepage, About, etc.) -- not isolated components. Pages show real-world usage of colors, fonts, and sizes.

**Chrome MCP automation sequence:**

1. Get browser tab context (`tabs_context_mcp`)
2. Create new tab and navigate to Figma URL
3. Wait for design to load, take screenshot
4. Navigate to Homepage/main page in left sidebar (NOT the components panel)
5. Click on page elements to extract values:
   - Header/navbar -> primary color
   - CTA buttons -> secondary/accent color
   - Section backgrounds -> background colors
   - Body text -> text color, font family, base size
   - Page headings (H1-H6) -> heading fonts, sizes, weights
6. Navigate through multiple pages (Home, About, Contact, Footer) for complete extraction

**Pages to check (in order):**
- Homepage -- primary colors, hero typography, main CTA styles
- About/Services -- section backgrounds, content hierarchy
- Contact -- form styles, secondary elements
- Footer area -- dark backgrounds, link colors

### Phase 3: Odoo Color System

```
o-color-1: Primary brand color   (buttons, links, headers)
o-color-2: Secondary/accent      (CTAs, highlights)
o-color-3: Light background       (sections, cards)
o-color-4: White/base             (body background)
o-color-5: Dark text              (headings, body text)

Auto-derivation (when only 2 colors found):
  o-color-3 = lighten(primary, 45%)
  o-color-4 = #FFFFFF
  o-color-5 = darken(primary, 40%) or #191A19
```

### Phase 4: Generated Theme Structure

```
theme_{{name}}/
├── __init__.py
├── __manifest__.py
├── security/
│   └── ir.model.access.csv
├── data/
│   ├── assets.xml                    # Minimal (fonts via SCSS, not ir.asset!)
│   ├── menu.xml
│   └── pages/                        # Individual page files (best practice)
│       ├── home_page.xml             # Inherits website.homepage
│       ├── aboutus_page.xml          # theme.website.page
│       ├── contactus_page.xml        # Inherits website.contactus
│       └── services_page.xml         # theme.website.page
├── views/
│   ├── layout/
│   │   └── templates.xml             # Base layout templates
│   └── snippets/
│       └── custom_snippets.xml
└── static/
    ├── description/
    │   ├── cover.png
    │   └── screenshot.png
    └── src/
        ├── scss/
        │   ├── primary_variables.scss # Theme variables + font configs
        │   ├── bootstrap_overridden.scss  # Bootstrap overrides (OPTIONAL)
        │   └── theme.scss             # Additional custom styles
        ├── js/
        │   ├── theme.js              # publicWidget implementations
        │   └── snippets_options.js    # Snippet options (if needed)
        └── img/
            └── .gitkeep
```

**Header and footer:** Use `$o-website-values-palettes` configuration (`'header-template'`, `'footer-template'`), NOT custom XML. Only create custom header.xml/footer.xml if the design requires a completely custom layout not available in built-in templates.

### SCSS Load Order (Critical)

```
1. Theme's primary_variables.scss  (via 'prepend' directive)
   |
2. Odoo core primary_variables.scss
   (where $o-color-palettes, $o-theme-font-configs are FIRST defined)
   |
3. Other SCSS files

CONSEQUENCE:
  - CANNOT use map-merge() with core variables (they don't exist yet!)
  - MUST define standalone variables
  - Use 'color-palettes-name': 'default-1' to reference existing palettes

WRONG:  $o-color-palettes: map-merge($o-color-palettes, (...));
RIGHT:  $o-website-values-palettes: ( ( 'color-palettes-name': 'default-1' ) );
```

### Key SCSS Patterns

**Font configuration (standalone, no map-merge):**
```scss
$o-theme-font-configs: (
    'FontName': (
        'family': ('FontName', sans-serif),
        'url': 'FontName:300,300i,400,400i,500,500i,600,600i,700,700i',
    ),
);
```

**Typography multipliers (base = 16px):**
```scss
$o-theme-h1-font-size-multiplier: (64 / 16); // 64px
$o-theme-h2-font-size-multiplier: (48 / 16); // 48px
$o-theme-h3-font-size-multiplier: (32 / 16); // 32px
$o-theme-h4-font-size-multiplier: (24 / 16); // 24px
$o-theme-h5-font-size-multiplier: (20 / 16); // 20px
$o-theme-h6-font-size-multiplier: (16 / 16); // 16px (FIXED)
```

**$o-website-values-palettes (master configuration):**

This is the primary way to configure Bootstrap components in Odoo. Over 115 variables are available. Key categories:

| Category | Key Variables |
|----------|---------------|
| **Typography** | `'font'`, `'headings-font'`, `'navbar-font'`, `'buttons-font'` |
| **Header** | `'header-template'` (default/hamburger/vertical/sidebar), `'header-links-style'`, `'logo-height'` |
| **Footer** | `'footer-template'` (default/centered/minimalist/links/descriptive), `'footer-effect'`, `'footer-scrolltop'` |
| **Buttons** | `'btn-padding-y'`, `'btn-padding-x'`, `'btn-border-radius'`, `'btn-font-size'` |
| **Inputs** | `'input-padding-y'`, `'input-padding-x'`, `'input-border-radius'` |
| **Layout** | `'layout'` (full/boxed), `'link-underline'` (never/hover/always) |

**For the complete primary_variables.scss template and all 115+ variables, see the SKILL.md (`odoo-frontend/SKILL.md`).**

### Asset Bundle Configuration

```python
# __manifest__.py
'assets': {
    # Primary variables - PREPENDED (loads before Odoo core)
    'web._assets_primary_variables': [
        ('prepend', 'theme_name/static/src/scss/primary_variables.scss'),
    ],
    # Bootstrap overrides (OPTIONAL)
    'web._assets_frontend_helpers': [
        'theme_name/static/src/scss/bootstrap_overridden.scss',
    ],
    # Main frontend assets
    'web.assets_frontend': [
        'theme_name/static/src/scss/theme.scss',
        'theme_name/static/src/js/theme.js',
    ],
    # Website editor assets (snippet options)
    'website.assets_wysiwyg': [
        'theme_name/static/src/js/snippets_options.js',
    ],
},
```

### Phase 5: Installation and Testing

```bash
# Step 1: Update module list
python -m odoo -c conf/{{PROJECT}}.conf -d {{DATABASE}} --update-list

# Step 2: Install theme
python -m odoo -c conf/{{PROJECT}}.conf -d {{DATABASE}} -i theme_{{NAME}} --stop-after-init

# Step 3: If errors, auto-fix and retry (up to 3 attempts)
```

**Auto-fix patterns:**

| Error Pattern | Fix Action |
|---------------|------------|
| `SyntaxError in SCSS` | Parse error location, fix syntax |
| `Module not found` | Add dependency to manifest |
| `Invalid XML` | Fix XML structure |
| `Asset not found` | Fix asset path in manifest |
| `Template inheritance error` | Fix inherit_id reference |
| `Undefined variable "$o-color-palettes"` | Remove map-merge, use standalone definition |
| `Undefined variable "$o-theme-font-configs"` | Define standalone (no map-merge) |
| `Malformed Google Fonts @import` | Remove ir.asset record, use $o-theme-font-configs |

**Testing checklist (after successful install):**

- [ ] Theme module installs without errors
- [ ] CSS compilation succeeds (`document.styleSheets[n].cssRules.length > 0`)
- [ ] No SCSS/JS errors in browser console
- [ ] Header and footer styling apply correctly
- [ ] Responsive layout works on mobile/tablet/desktop
- [ ] Website builder (edit mode) functions without errors

### Version-Specific Adjustments

| Odoo Version | Notes |
|--------------|-------|
| 14-15 | Bootstrap 4: use `ml-*`/`mr-*`, different asset bundle syntax, no snippet groups |
| 16-17 | Bootstrap 5.1.3: use `ms-*`/`me-*`, modern asset bundles, simple snippet registration |
| 18-19 | Bootstrap 5.1.3 + snippet groups, Owl v2 patterns, enhanced website builder |

### Debugging SCSS Issues

```bash
# 1. Check browser console for "Style compilation failed"
# 2. Verify stylesheets: document.styleSheets[0].cssRules.length (should be > 0)
# 3. If 0 rules -> SCSS compilation failed silently -> check for undefined variables
# 4. Clear asset cache:
python odoo-bin shell -d {{DATABASE}}
>>> self.env['ir.attachment'].search([('url', 'like', '/web/assets/')]).unlink()
>>> self.env.cr.commit()
# 5. Restart server + hard refresh browser (Ctrl+Shift+R)
```

### Quick Example

```
User: /odoo-frontend create-theme --figma https://www.figma.com/file/abc123/MyDesign

1. Opens Figma in Chrome, navigates to Homepage
2. Extracts: colors (#2C5282, #ED8936, #F7FAFC, #FFFFFF, #1A202C)
            fonts (Inter for body, Poppins for headings)
            sizes (H1:64px, H2:48px, H3:36px, H4:28px, H5:24px, H6:16px)
3. Prompts for theme_name and project_path
4. Generates theme_my_design/ with all files
5. Installs and tests -> reports success

User: /odoo-frontend create-theme my_theme projects/client --colors="#207AB7,#FB9F54,#F6F4F0,#FFFFFF,#191A19"

1. Skips Figma extraction
2. Uses provided colors directly
3. Uses default typography (or prompts for font names)
4. Generates and installs theme
```

### Rules (Hard Constraints)

- **NEVER** use `map-merge()` with core Odoo variables in theme SCSS
- **NEVER** use `ir.asset` records for external font URLs -- use `$o-theme-font-configs`
- **ALWAYS** use simple XPath expressions if custom header/footer XML is needed
- **PREFER** `$o-website-values-palettes` over custom header/footer XML
- **H6 is ALWAYS 16px** (1rem) -- the fixed base reference
- **ALWAYS** use `('prepend', ...)` for primary_variables.scss in the asset bundle
- All generated code follows TaqaTechno manifest standards (author, website, support, license)

### Deep Reference

For the complete 115+ variable reference, full SCSS templates, detailed Chrome MCP automation steps, and advanced patterns (display sizes, extended hierarchy, custom snippets), see:
- **SKILL.md** (`odoo-frontend/SKILL.md`) -- 3,900+ lines of deep technical knowledge
- **DESIGN_SYSTEM_RULES.md** (`odoo17/DESIGN_SYSTEM_RULES.md`) -- 2,600+ lines on the Odoo design system

The SKILL.md is automatically loaded when the `odoo-frontend` skill activates. This command triggers and guides the workflow; the skill provides the full expertise.

---

*TAQAT Techno - Odoo Frontend Development v4.0*
*Supports Odoo 14-19 with intelligent version detection*

---
title: 'Create Theme'
read_only: false
type: 'command'
description: 'Create a complete Odoo website theme by extracting design system variables from Figma via Chrome browser automation'
---

# /create-theme - Figma-to-Odoo Theme Generator

Generate a professional, production-ready Odoo website theme by **extracting design system variables directly from Figma** via Chrome browser automation, then creating all theme files, testing installation, and auto-fixing any issues.

## Overview

This command provides an end-to-end workflow:

1. **Open Figma Design** in Chrome browser
2. **Extract Design Variables**:
   - Primary and secondary colors from the design
   - Font family (body and headings)
   - Font sizes for H1-H6 hierarchy
   - Additional display sizes if design has more than 6 levels
3. **Generate Theme Files** following Odoo best practices
4. **Test Installation** in Odoo
5. **Auto-Fix Issues** if installation fails

## Usage

### Interactive Mode with Figma URL (Recommended)
```
/create-theme --figma <figma_url>
```
Opens Figma, extracts design variables, and guides through theme creation.

### Full Arguments
```
/create-theme <theme_name> <project_path> --figma <figma_url> --version=17
```

### Manual Mode (No Figma)
```
/create-theme <theme_name> <project_path> --colors="#207AB7,#FB9F54,#F6F4F0,#FFFFFF,#191A19"
```

## Complete Workflow

### Phase 1: Figma Design Extraction via Chrome

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: FIGMA DESIGN EXTRACTION                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ⚠️ CRITICAL: NAVIGATE TO PAGES, NOT COMPONENTS!                             │
│  ─────────────────────────────────────────────────                           │
│  Always extract design variables from ACTUAL PAGES (Homepage, About, etc.)   │
│  NOT from isolated components. Pages show real-world usage of:               │
│  • Primary colors in headers, buttons, CTAs                                  │
│  • Font sizes in actual heading hierarchies                                  │
│  • Background colors in sections                                             │
│                                                                               │
│  STEP 1: Open Figma and Navigate to Homepage                                 │
│  ─────────────────────────────────────────────                               │
│  Using Claude-in-Chrome MCP tools:                                           │
│  1. Get browser tab context                                                  │
│  2. Create new tab if needed                                                 │
│  3. Navigate to Figma URL                                                    │
│  4. Wait for design to load                                                  │
│  5. NAVIGATE TO HOMEPAGE or main page (NOT components panel!)                │
│  6. If homepage isn't visible, look for page list in left sidebar            │
│                                                                               │
│  STEP 2: Extract Colors FROM PAGES                                           │
│  ──────────────────────────────────                                          │
│  Navigate through pages (Home, About, Contact) and identify:                 │
│  • Primary color: Header background, primary buttons, links                  │
│  • Secondary color: CTAs, accent elements, hover states                      │
│  • Background colors: Section backgrounds, cards (o-color-3)                 │
│  • White/base color: Main content background (o-color-4)                     │
│  • Dark/text color: Body text, headings (o-color-5)                          │
│                                                                               │
│  STEP 3: Extract Typography FROM PAGE HEADINGS                               │
│  ─────────────────────────────────────────────                               │
│  Click on actual page headings to extract:                                   │
│  • Font family (from page body text)                                         │
│  • Font family (from page headings if different)                             │
│  • H1 size (page title/hero heading)                                         │
│  • H2 size (section headings)                                                │
│  • H3 size (subsection headings)                                             │
│  • H4-H6 sizes (smaller headings on page)                                    │
│  • Body text size (paragraph text)                                           │
│                                                                               │
│  PAGES TO CHECK (in order):                                                  │
│  1. Homepage - Primary colors, hero typography, main CTA styles              │
│  2. About/Services - Section backgrounds, content hierarchy                  │
│  3. Contact - Form styles, secondary elements                                │
│  4. Footer area - Dark backgrounds, link colors                              │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Chrome Browser Automation Steps

```javascript
// Step 1: Get tab context
mcp__claude-in-chrome__tabs_context_mcp({ createIfEmpty: true })

// Step 2: Create new tab
mcp__claude-in-chrome__tabs_create_mcp()

// Step 3: Navigate to Figma
mcp__claude-in-chrome__navigate({ url: figmaUrl, tabId: tabId })

// Step 4: Wait for design to load
mcp__claude-in-chrome__computer({ action: "wait", duration: 5, tabId: tabId })

// Step 5: Take screenshot to see current view
mcp__claude-in-chrome__computer({ action: "screenshot", tabId: tabId })

// Step 6: CRITICAL - Navigate to PAGES (not components!)
// Look for page list in left sidebar and click on Homepage/main page
mcp__claude-in-chrome__find({ query: "Homepage", tabId: tabId })
// OR
mcp__claude-in-chrome__find({ query: "Home", tabId: tabId })

// Step 7: Click on the Homepage/main page to view it
mcp__claude-in-chrome__computer({ action: "left_click", coordinate: [x, y], tabId: tabId })

// Step 8: Take screenshot of the actual page design
mcp__claude-in-chrome__computer({ action: "screenshot", tabId: tabId })

// Step 9: Click on elements ON THE PAGE to extract values
// Click on header to get primary color
// Click on heading text to get font-family and size
// Click on body text to get body font
```

#### Figma Page Navigation (CRITICAL)

**⚠️ ALWAYS navigate to actual PAGES to extract variables, NOT components!**

To extract design variables, Claude will:

1. **Navigate to Pages List (Left Sidebar)**:
   - Look for "Pages" section in the left sidebar
   - Find and click on "Homepage", "Home", or main page
   - If no homepage, navigate to the first complete page design

2. **Extract Colors FROM PAGE ELEMENTS**:
   - Click on the header/navbar → Get primary color
   - Click on CTA buttons → Get secondary/accent color
   - Click on section backgrounds → Get background colors
   - Click on body text → Get text color
   - **DO NOT** extract from component library or style guide panels

3. **Extract Typography FROM PAGE HEADINGS**:
   - Click on the main page title (H1) → Get H1 size and font
   - Click on section headings → Get H2, H3 sizes
   - Click on body paragraphs → Get body font and size
   - Record: font-family, font-size, font-weight, line-height

4. **Navigate Through Multiple Pages**:
   - Homepage → Primary colors, hero typography
   - About/Services → Section styles, content hierarchy
   - Contact → Form styles, alternative layouts
   - Footer area → Dark backgrounds, footer typography

### Phase 2: Typography Hierarchy Mapping

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TYPOGRAPHY HIERARCHY MAPPING                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  STANDARD HIERARCHY (H1-H6):                                                 │
│  ───────────────────────────                                                 │
│  From design, extract font sizes and convert to multipliers (base = 16px):  │
│                                                                               │
│  H1: 64px  → (64 / 16) = 4.0    (Hero/Page titles)                          │
│  H2: 48px  → (48 / 16) = 3.0    (Section headers)                           │
│  H3: 32px  → (32 / 16) = 2.0    (Sub-section headers)                       │
│  H4: 24px  → (24 / 16) = 1.5    (Card headers)                              │
│  H5: 20px  → (20 / 16) = 1.25   (Small headers)                             │
│  H6: 16px  → (16 / 16) = 1.0    (Captions) **DEFAULT**                      │
│                                                                               │
│  EXTENDED HIERARCHY (Display Classes):                                       │
│  ─────────────────────────────────────                                       │
│  If design has > 6 heading levels, add Bootstrap display classes:           │
│                                                                               │
│  display-1: 96px → 6.0    (Extra large hero)                                │
│  display-2: 88px → 5.5    (Large hero)                                      │
│  display-3: 80px → 5.0    (Hero)                                            │
│  display-4: 72px → 4.5    (Sub-hero)                                        │
│  display-5: 64px → 4.0    (Same as H1)                                      │
│  display-6: 56px → 3.5    (Between H1 and H2)                               │
│                                                                               │
│  MAPPING RULES:                                                              │
│  ─────────────                                                               │
│  • H6 MUST be 16px (1rem) - This is the base font size                      │
│  • Sizes larger than H1 become display-* classes                            │
│  • Maintain visual hierarchy with consistent ratios                          │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### SCSS Variable Generation

```scss
// === Typography Hierarchy from Figma ===
// Font Family
$o-theme-font-family: '{{FONT_FAMILY}}', sans-serif;
$o-theme-headings-font-family: '{{HEADINGS_FONT}}', sans-serif;

// Heading Size Multipliers (relative to 16px base)
$o-theme-h1-font-size-multiplier: ({{H1_SIZE}} / 16); // {{H1_SIZE}}px
$o-theme-h2-font-size-multiplier: ({{H2_SIZE}} / 16); // {{H2_SIZE}}px
$o-theme-h3-font-size-multiplier: ({{H3_SIZE}} / 16); // {{H3_SIZE}}px
$o-theme-h4-font-size-multiplier: ({{H4_SIZE}} / 16); // {{H4_SIZE}}px
$o-theme-h5-font-size-multiplier: ({{H5_SIZE}} / 16); // {{H5_SIZE}}px
$o-theme-h6-font-size-multiplier: (16 / 16);          // 16px (FIXED)

// Display Sizes (for extended hierarchy)
{{#if HAS_DISPLAY_SIZES}}
$display-font-sizes: (
  1: {{DISPLAY_1_SIZE}}px,
  2: {{DISPLAY_2_SIZE}}px,
  3: {{DISPLAY_3_SIZE}}px,
  4: {{DISPLAY_4_SIZE}}px,
  5: {{DISPLAY_5_SIZE}}px,
  6: {{DISPLAY_6_SIZE}}px,
);
{{/if}}

// Font Weights
$o-theme-headings-font-weight: {{HEADINGS_WEIGHT}};
$o-theme-font-weight-normal: 400;
$o-theme-font-weight-medium: 500;
$o-theme-font-weight-semibold: 600;
$o-theme-font-weight-bold: 700;

// Line Heights
$o-theme-headings-line-height: {{HEADINGS_LINE_HEIGHT}};
$o-theme-line-height-base: {{BODY_LINE_HEIGHT}};
```

### Phase 3: Color Palette Mapping

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COLOR PALETTE MAPPING (Odoo Semantic)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ODOO COLOR SYSTEM:                                                          │
│  ──────────────────                                                          │
│  o-color-1: Primary brand color (buttons, links, headers)                   │
│  o-color-2: Secondary/accent color (CTAs, highlights)                       │
│  o-color-3: Light background (sections, cards)                              │
│  o-color-4: White/base (body background)                                    │
│  o-color-5: Dark text (headings, body text)                                 │
│                                                                               │
│  FROM FIGMA EXTRACTION:                                                      │
│  ──────────────────────                                                      │
│  Primary Color    → o-color-1                                               │
│  Secondary Color  → o-color-2                                               │
│  Light BG         → o-color-3 (or derive from primary at 10% opacity)       │
│  White            → o-color-4 (#FFFFFF)                                     │
│  Dark Text        → o-color-5 (or #191A19 default)                          │
│                                                                               │
│  AUTO-DERIVATION:                                                            │
│  ────────────────                                                            │
│  If only 2 colors found:                                                    │
│  • o-color-3 = lighten(primary, 45%)                                        │
│  • o-color-4 = #FFFFFF                                                      │
│  • o-color-5 = darken(primary, 40%) or #191A19                              │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 4: Theme Generation

After extracting all variables, generate the complete theme structure:

```
theme_{{name}}/
├── __init__.py
├── __manifest__.py
├── security/
│   └── ir.model.access.csv
├── data/
│   ├── assets.xml                       # Minimal - fonts via SCSS
│   ├── menu.xml
│   └── pages/                           # Individual page files
│       ├── home_page.xml               # Inherits website.homepage
│       ├── aboutus_page.xml            # theme.website.page
│       ├── contactus_page.xml          # Inherits website.contactus
│       └── services_page.xml           # theme.website.page
├── views/
│   ├── layout/
│   │   ├── header.xml                  # Header customization (OPTIONAL)
│   │   ├── footer.xml                  # Footer customization (OPTIONAL)
│   │   └── templates.xml               # Base layout templates
│   └── snippets/
│       └── custom_snippets.xml         # Custom snippet definitions
└── static/
    ├── description/
    │   ├── cover.png
    │   └── screenshot.png
    └── src/
        ├── scss/
        │   ├── primary_variables.scss   # Theme variables + fonts
        │   ├── bootstrap_overridden.scss # Bootstrap overrides (OPTIONAL)
        │   └── theme.scss               # Additional custom styles
        ├── js/
        │   ├── theme.js                 # publicWidget implementations
        │   └── snippets_options.js      # Snippet options (if needed)
        └── img/
            └── .gitkeep
```

### 💡 Simplified Approach (Recommended)

In MOST cases, you can configure everything via `$o-website-values-palettes` without creating custom XML:

**Header Templates** (via `'header-template'`):
- `'default'` - Standard horizontal navbar
- `'hamburger'` - Hamburger menu (collapsed)
- `'vertical'` - Vertical sidebar navigation
- `'sidebar'` - Full sidebar layout

**Footer Templates** (via `'footer-template'`):
- `'default'` - Standard footer
- `'centered'` - Center-aligned
- `'minimalist'` - Clean minimal
- `'links'` - Link-heavy footer
- `'descriptive'` - Full description footer

**When to use custom header.xml/footer.xml:**
- Design requires completely custom header layout not available in templates
- Need additional HTML elements beyond what templates provide
- Complex JavaScript-based navigation interactions

**When bootstrap_overridden.scss IS useful:**
- Need Bootstrap variables not exposed in `$o-website-values-palettes`
- Complex responsive breakpoint customizations
- Custom grid configurations

### Phase 5: Installation & Testing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 5: INSTALLATION & TESTING                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  STEP 1: Update Module List                                                  │
│  ─────────────────────────────                                               │
│  python -m odoo -c conf/{{PROJECT}}.conf -d {{DATABASE}} --update-list       │
│                                                                               │
│  STEP 2: Install Theme                                                       │
│  ────────────────────────                                                    │
│  python -m odoo -c conf/{{PROJECT}}.conf -d {{DATABASE}} \                   │
│      -i theme_{{NAME}} --stop-after-init                                     │
│                                                                               │
│  STEP 3: Check for Errors                                                    │
│  ─────────────────────────                                                   │
│  If installation fails, analyze error and auto-fix:                          │
│                                                                               │
│  Common Issues:                                                              │
│  • Missing dependencies → Add to __manifest__.py                             │
│  • Invalid XML syntax → Fix and retry                                        │
│  • Asset bundle errors → Fix asset paths                                     │
│  • SCSS syntax errors → Fix SCSS and retry                                   │
│                                                                               │
│  STEP 4: Verify Theme                                                        │
│  ────────────────────                                                        │
│  If installation succeeds:                                                   │
│  1. Navigate to Website → Configuration → Settings → Theme                   │
│  2. Activate the new theme                                                   │
│  3. Preview website                                                          │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Auto-Fix Patterns

| Error Pattern | Auto-Fix Action |
|---------------|-----------------|
| `SyntaxError in SCSS` | Parse error location, fix syntax |
| `Module not found` | Add dependency to manifest |
| `Invalid XML` | Fix XML structure |
| `Asset not found` | Fix asset path in manifest |
| `Template inheritance error` | Fix inherit_id reference |

## Implementation Details

### Chrome MCP Integration

The command uses Claude-in-Chrome MCP tools for browser automation:

```python
# Required MCP tools
mcp__claude-in-chrome__tabs_context_mcp
mcp__claude-in-chrome__tabs_create_mcp
mcp__claude-in-chrome__navigate
mcp__claude-in-chrome__computer
mcp__claude-in-chrome__read_page
mcp__claude-in-chrome__find
mcp__claude-in-chrome__javascript_tool
```

### Figma URL Patterns

Supported Figma URL formats:
```
https://www.figma.com/file/XXXX/Design-Name
https://www.figma.com/design/XXXX/Design-Name
https://www.figma.com/proto/XXXX/Design-Name
```

### Design Variable Extraction

Claude will visually analyze the Figma design to extract:

1. **Colors**: By taking screenshots and identifying prominent colors
2. **Typography**: By clicking on text elements and reading properties
3. **Spacing**: By analyzing component layouts

## ⚠️ CRITICAL: SCSS Load Order in Odoo

**IMPORTANT**: Theme SCSS files with `prepend` directive load **BEFORE** Odoo core variables are defined!

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SCSS LOAD ORDER (CRITICAL!)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  1. Theme's primary_variables.scss (via prepend)                             │
│     ↓                                                                         │
│  2. Odoo core primary_variables.scss                                         │
│     (where $o-color-palettes, $o-theme-font-configs are FIRST defined)      │
│     ↓                                                                         │
│  3. Other SCSS files                                                         │
│                                                                               │
│  ⚠️ CONSEQUENCE:                                                             │
│  ──────────────                                                              │
│  • CANNOT use map-merge() with core variables (they don't exist yet!)       │
│  • MUST define standalone variables                                          │
│  • Use 'color-palettes-name': 'default-1' to reference existing palettes    │
│                                                                               │
│  ❌ WRONG (will cause "Undefined variable" error):                           │
│     $o-color-palettes: map-merge($o-color-palettes, (...));                 │
│     $o-theme-font-configs: map-merge($o-theme-font-configs, (...));         │
│                                                                               │
│  ✅ CORRECT (standalone definitions):                                        │
│     $o-theme-font-configs: ( 'FontName': (...) );                           │
│     $o-website-values-palettes: ( ( 'color-palettes-name': 'default-1' ) ); │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Complete primary_variables.scss Template (CORRECTED)

```scss
// ===================================================================
// Theme: {{THEME_DISPLAY_NAME}}
// Generated from Figma: {{FIGMA_URL}}
// Generated by TAQAT Techno /create-theme command v5.0
// ===================================================================
//
// ⚠️ IMPORTANT: This file is PREPENDED before Odoo core variables!
// DO NOT use map-merge() with core variables - they don't exist yet!
// ===================================================================

// === Typography from Figma ===
// Base font size: 16px (1rem)

// Heading Size Multipliers
$o-theme-h1-font-size-multiplier: ({{H1_SIZE}} / 16); // {{H1_SIZE}}px - Hero/Page titles
$o-theme-h2-font-size-multiplier: ({{H2_SIZE}} / 16); // {{H2_SIZE}}px - Section headers
$o-theme-h3-font-size-multiplier: ({{H3_SIZE}} / 16); // {{H3_SIZE}}px - Sub-sections
$o-theme-h4-font-size-multiplier: ({{H4_SIZE}} / 16); // {{H4_SIZE}}px - Card headers
$o-theme-h5-font-size-multiplier: ({{H5_SIZE}} / 16); // {{H5_SIZE}}px - Small headers
$o-theme-h6-font-size-multiplier: (16 / 16);          // 16px - Captions (FIXED)

// Font Weights
$o-theme-headings-font-weight: {{HEADINGS_WEIGHT}};
$o-theme-font-weight-normal: 400;
$o-theme-font-weight-medium: 500;
$o-theme-font-weight-semibold: 600;
$o-theme-font-weight-bold: 700;

// Line Heights
$o-theme-headings-line-height: {{HEADINGS_LINE_HEIGHT}};
$o-theme-line-height-base: {{BODY_LINE_HEIGHT}};

{{#if HAS_DISPLAY_SIZES}}
// === Extended Typography (Display Sizes) ===
// For designs with > 6 heading levels
$display-font-sizes: (
  1: {{DISPLAY_1}}rem,  // Extra large hero
  2: {{DISPLAY_2}}rem,  // Large hero
  3: {{DISPLAY_3}}rem,  // Hero
  4: {{DISPLAY_4}}rem,  // Sub-hero
  5: {{DISPLAY_5}}rem,  // Large heading
  6: {{DISPLAY_6}}rem,  // Medium heading
) !default;
{{/if}}

// === Font Configuration (STANDALONE - no map-merge!) ===
// Odoo's built-in font loading handles Google Fonts automatically
$o-theme-font-configs: (
    '{{BODY_FONT}}': (
        'family': ('{{BODY_FONT}}', sans-serif),
        'url': '{{BODY_FONT}}:300,300i,400,400i,500,500i,600,600i,700,700i',
    ),
{{#if HEADINGS_FONT_DIFFERENT}}
    '{{HEADINGS_FONT}}': (
        'family': ('{{HEADINGS_FONT}}', sans-serif),
        'url': '{{HEADINGS_FONT}}:300,300i,400,400i,500,500i,600,600i,700,700i',
    ),
{{/if}}
);

// === Website Values Palette (MASTER CONFIGURATION) ===
// This is the MAIN way to configure Bootstrap components in Odoo!
// NO bootstrap_overridden.scss needed - just define variables here.
//
// Available variables: 115+ options for complete Bootstrap control
// See: O_WEBSITE_VALUES_PALETTES_REPORT.md for full reference
$o-website-values-palettes: (
    (
        // ═══════════════════════════════════════════════════════════════
        // COLOR PALETTE REFERENCE
        // ═══════════════════════════════════════════════════════════════
        // Reference existing Odoo palette (default-1 through default-21)
        // This avoids map-merge issues with $o-color-palettes
        'color-palettes-name': 'default-1',

        // ═══════════════════════════════════════════════════════════════
        // TYPOGRAPHY
        // ═══════════════════════════════════════════════════════════════
        'font': '{{BODY_FONT}}',              // Body text font
        'headings-font': '{{HEADINGS_FONT}}', // H1-H6 font
        'navbar-font': '{{BODY_FONT}}',       // Navigation menu font
        'buttons-font': '{{BODY_FONT}}',      // Button text font

        // Font sizes (optional - can override calculated multipliers)
        'font-size-base': 1rem,               // Base font (16px)
        'small-font-size': 0.875rem,          // Small text (14px)

        // Line heights
        'body-line-height': {{BODY_LINE_HEIGHT}},
        'headings-line-height': {{HEADINGS_LINE_HEIGHT}},

        // Spacing
        'paragraph-margin-bottom': 1rem,
        'headings-margin-bottom': 0.5rem,

        // ═══════════════════════════════════════════════════════════════
        // HEADER & NAVIGATION (NO custom header.xml needed!)
        // ═══════════════════════════════════════════════════════════════
        // Header template options:
        // 'default' | 'hamburger' | 'vertical' | 'sidebar'
        'header-template': 'default',

        // Link style options:
        // 'default' | 'pills' | 'fill' | 'outline' | 'border-bottom' | 'block'
        'header-links-style': 'default',

        // Mobile hamburger position: 'left' | 'center' | 'right'
        'hamburger-position': 'right',

        // Logo sizing
        'logo-height': 3rem,
        'fixed-logo-height': 2rem,

        // Menu styling (optional)
        // 'menu-border-radius': 0.5rem,
        // 'menu-box-shadow': none,

        // ═══════════════════════════════════════════════════════════════
        // BUTTONS (Full Bootstrap control!)
        // ═══════════════════════════════════════════════════════════════
        // Normal size
        'btn-padding-y': {{BTN_PADDING_Y}},
        'btn-padding-x': {{BTN_PADDING_X}},
        'btn-font-size': 1rem,

        // Small size
        'btn-padding-y-sm': {{BTN_PADDING_Y_SM}},
        'btn-padding-x-sm': {{BTN_PADDING_X_SM}},
        'btn-font-size-sm': 0.875rem,

        // Large size
        'btn-padding-y-lg': {{BTN_PADDING_Y_LG}},
        'btn-padding-x-lg': {{BTN_PADDING_X_LG}},
        'btn-font-size-lg': 1.25rem,

        // Border radius
        'btn-border-radius': {{BTN_BORDER_RADIUS}},
        'btn-border-radius-sm': {{BTN_BORDER_RADIUS_SM}},
        'btn-border-radius-lg': {{BTN_BORDER_RADIUS_LG}},

        // Border width
        'btn-border-width': 1px,

        // Button styles (true/false)
        // 'btn-primary-outline': false,     // Outline-only primary buttons
        // 'btn-secondary-outline': false,   // Outline-only secondary buttons
        // 'btn-primary-flat': false,        // Flat primary (no border/shadow)
        // 'btn-secondary-flat': false,      // Flat secondary
        // 'btn-ripple': false,              // Material Design ripple effect

        // ═══════════════════════════════════════════════════════════════
        // INPUTS & FORMS (Full Bootstrap control!)
        // ═══════════════════════════════════════════════════════════════
        // Normal size
        'input-padding-y': {{INPUT_PADDING_Y}},
        'input-padding-x': {{INPUT_PADDING_X}},
        'input-font-size': 1rem,

        // Small size
        'input-padding-y-sm': 0.5rem,
        'input-padding-x-sm': 0.75rem,
        'input-font-size-sm': 0.875rem,

        // Large size
        'input-padding-y-lg': 1rem,
        'input-padding-x-lg': 1.5rem,
        'input-font-size-lg': 1.25rem,

        // Border radius
        'input-border-radius': {{INPUT_BORDER_RADIUS}},
        'input-border-radius-sm': 0.25rem,
        'input-border-radius-lg': 0.5rem,

        // ═══════════════════════════════════════════════════════════════
        // FOOTER (NO custom footer.xml needed!)
        // ═══════════════════════════════════════════════════════════════
        // Footer template options:
        // 'default' | 'centered' | 'minimalist' | 'links' | 'descriptive'
        'footer-template': 'default',

        // Footer effects: null | 'slideout_slide_hover' | 'slideout_shadow'
        'footer-effect': null,

        // Scroll-to-top button
        'footer-scrolltop': true,

        // ═══════════════════════════════════════════════════════════════
        // LINKS
        // ═══════════════════════════════════════════════════════════════
        // Underline options: 'never' | 'hover' | 'always'
        'link-underline': 'hover',

        // ═══════════════════════════════════════════════════════════════
        // LAYOUT
        // ═══════════════════════════════════════════════════════════════
        // Layout options: 'full' | 'boxed'
        'layout': 'full',
    ),
);

// === Theme Colors (Custom Properties) ===
// Define as CSS custom properties for use in theme.scss
// These will be available AFTER Odoo core loads
:root {
    --theme-primary: {{COLOR_1}};
    --theme-secondary: {{COLOR_2}};
    --theme-light-bg: {{COLOR_3}};
    --theme-white: {{COLOR_4}};
    --theme-dark: {{COLOR_5}};
}
```

## __manifest__.py Template

```python
# -*- coding: utf-8 -*-
{
    'name': '{{THEME_DISPLAY_NAME}}',
    'version': '17.0.1.0.0',
    'summary': '{{THEME_SUMMARY}}',
    'description': """
        {{THEME_DESCRIPTION}}

        Features:
        - Custom color palette
        - Google Fonts integration
        - Responsive header/footer configuration
        - Custom page templates
        - Custom snippets
    """,
    'category': 'Theme/Creative',
    'author': 'TaqaTechno',
    'website': 'https://www.taqatechno.com/',
    'support': 'info@taqatechno.com',
    'license': 'LGPL-3',
    'depends': [
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/layout/templates.xml',
        'views/layout/header.xml',
        'views/layout/footer.xml',
        'views/snippets/custom_snippets.xml',
        'data/menu.xml',
        # Individual page files (BEST PRACTICE!)
        'data/pages/home_page.xml',
        'data/pages/aboutus_page.xml',
        'data/pages/contactus_page.xml',
        'data/pages/services_page.xml',
    ],
    'assets': {
        # Primary variables - PREPENDED (loads before Odoo core)
        'web._assets_primary_variables': [
            ('prepend', '{{theme_name}}/static/src/scss/primary_variables.scss'),
        ],
        # Bootstrap overrides (if needed)
        'web._assets_frontend_helpers': [
            '{{theme_name}}/static/src/scss/bootstrap_overridden.scss',
        ],
        # Main frontend assets
        'web.assets_frontend': [
            '{{theme_name}}/static/src/scss/theme.scss',
            '{{theme_name}}/static/src/js/theme.js',
        ],
        # Website editor assets (snippet options)
        'website.assets_wysiwyg': [
            '{{theme_name}}/static/src/js/snippets_options.js',
        ],
    },
    'images': [
        'static/description/cover.png',
        'static/description/screenshot.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
```

## assets.xml Template (CORRECTED)

**⚠️ IMPORTANT**: Do NOT use `ir.asset` records for Google Fonts! Use `$o-theme-font-configs` instead.

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!--
    ⚠️ IMPORTANT: Google Fonts are loaded via $o-theme-font-configs in SCSS
    DO NOT create ir.asset records for external font URLs - this causes malformed URLs!

    ❌ WRONG (causes malformed @import URLs):
    <record id="google_fonts" model="ir.asset">
        <field name="path">https://fonts.googleapis.com/css2?family=...</field>
    </record>

    ✅ CORRECT: Fonts configured in primary_variables.scss via $o-theme-font-configs
    -->
</odoo>
```

## Header & Footer: Use Configuration, NOT Custom Templates!

**⚠️ IMPORTANT**: You do NOT need to create custom header.xml or footer.xml files!

Odoo provides built-in header and footer templates that can be fully configured via `$o-website-values-palettes`:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HEADER & FOOTER CONFIGURATION                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ❌ OLD WAY (DON'T DO THIS):                                                 │
│  ───────────────────────────                                                 │
│  • Create views/layout/header.xml with XPath overrides                      │
│  • Create views/layout/footer.xml with XPath overrides                      │
│  • Complex CSS to style custom header/footer                                │
│                                                                               │
│  ✅ CORRECT WAY (USE THIS):                                                  │
│  ──────────────────────────                                                  │
│  Configure in $o-website-values-palettes:                                   │
│                                                                               │
│  HEADER OPTIONS:                                                             │
│  ├── 'header-template': 'default' | 'hamburger' | 'vertical' | 'sidebar'   │
│  ├── 'header-links-style': 'default' | 'pills' | 'fill' | 'outline' | etc  │
│  ├── 'hamburger-position': 'left' | 'center' | 'right'                     │
│  ├── 'logo-height': 3rem                                                    │
│  └── 'fixed-logo-height': 2rem                                              │
│                                                                               │
│  FOOTER OPTIONS:                                                             │
│  ├── 'footer-template': 'default' | 'centered' | 'minimalist' | 'links'    │
│  ├── 'footer-effect': null | 'slideout_slide_hover' | 'slideout_shadow'    │
│  └── 'footer-scrolltop': true | false                                       │
│                                                                               │
│  BENEFITS:                                                                   │
│  • Simpler theme - fewer files to maintain                                  │
│  • Works with Odoo's website builder                                        │
│  • Users can customize via website settings                                 │
│  • Automatic responsive behavior                                            │
│  • No XPath complexity or version-specific issues                           │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### When Custom Header/Footer IS Needed (RARE)

Only create custom header.xml or footer.xml if you need:
- Completely custom header layout not covered by built-in templates
- Additional HTML elements not supported by configuration
- Complex JavaScript-based navigation interactions

If needed, keep XPath expressions **SIMPLE**:

```xml
<!-- views/layout/header.xml - ONLY IF ABSOLUTELY NECESSARY -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Add theme class to header (simple XPath) -->
    <template id="header_style" inherit_id="website.layout" name="{{THEME_NAME}} Header">
        <xpath expr="//header" position="attributes">
            <attribute name="t-attf-class">o_{{THEME_SLUG}}_header #{header_class or ''}</attribute>
        </xpath>
    </template>
</odoo>
```

## Example Session

### User Request
```
/create-theme --figma https://www.figma.com/file/abc123/MyDesign
```

### Claude Response

```
╔══════════════════════════════════════════════════════════════╗
║           FIGMA DESIGN EXTRACTION                            ║
╠══════════════════════════════════════════════════════════════╣
║ Opening Figma in Chrome...                                   ║
║ URL: https://www.figma.com/file/abc123/MyDesign              ║
╚══════════════════════════════════════════════════════════════╝

Analyzing design...

╔══════════════════════════════════════════════════════════════╗
║           EXTRACTED DESIGN VARIABLES                         ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║ COLORS:                                                      ║
║ ├── Primary:   #2C5282 (Deep Blue)                          ║
║ ├── Secondary: #ED8936 (Orange)                             ║
║ ├── Light BG:  #F7FAFC                                      ║
║ ├── White:     #FFFFFF                                      ║
║ └── Dark Text: #1A202C                                      ║
║                                                              ║
║ TYPOGRAPHY:                                                  ║
║ ├── Font Family: Inter                                       ║
║ ├── Headings Font: Poppins                                   ║
║ ├── H1: 64px (4rem)                                          ║
║ ├── H2: 48px (3rem)                                          ║
║ ├── H3: 36px (2.25rem)                                       ║
║ ├── H4: 28px (1.75rem)                                       ║
║ ├── H5: 24px (1.5rem)                                        ║
║ ├── H6: 16px (1rem) [DEFAULT]                                ║
║ └── Headings Weight: 700                                     ║
║                                                              ║
║ DISPLAY SIZES (Extended):                                    ║
║ ├── Display 1: 96px (6rem) - Found in hero section          ║
║ └── Display 2: 80px (5rem) - Found in banner                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Enter theme name (snake_case): my_awesome_theme
Enter project path: projects/my_project
Target Odoo version [17]: 17

╔══════════════════════════════════════════════════════════════╗
║           GENERATING THEME FILES                             ║
╠══════════════════════════════════════════════════════════════╣
║ ✓ __manifest__.py                                            ║
║ ✓ __init__.py                                                ║
║ ✓ security/ir.model.access.csv                               ║
║ ✓ static/src/scss/primary_variables.scss                     ║
║ ✓ static/src/scss/bootstrap_overridden.scss                  ║
║ ✓ static/src/scss/theme.scss                                 ║
║ ✓ static/src/js/theme.js                                     ║
║ ✓ static/src/js/snippets_options.js                          ║
║ ✓ views/layout/header.xml                                    ║
║ ✓ views/layout/footer.xml                                    ║
║ ✓ views/layout/templates.xml                                 ║
║ ✓ views/snippets/custom_snippets.xml                         ║
║ ✓ data/assets.xml                                            ║
║ ✓ data/menu.xml                                              ║
║ ✓ data/pages/home_page.xml                                   ║
║ ✓ data/pages/aboutus_page.xml                                ║
║ ✓ data/pages/contactus_page.xml                              ║
║ ✓ data/pages/services_page.xml                               ║
╚══════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════╗
║           TESTING INSTALLATION                               ║
╠══════════════════════════════════════════════════════════════╣
║ Running: python -m odoo -c conf/my_project17.conf \          ║
║          -d my_project17 -i theme_my_awesome_theme \         ║
║          --stop-after-init                                   ║
╚══════════════════════════════════════════════════════════════╝

Installation successful!

╔══════════════════════════════════════════════════════════════╗
║           THEME CREATED SUCCESSFULLY!                        ║
╠══════════════════════════════════════════════════════════════╣
║ Theme Name:    theme_my_awesome_theme                        ║
║ Odoo Version:  17.0                                          ║
║ Bootstrap:     5.1.3                                         ║
║ Location:      projects/my_project/theme_my_awesome_theme/   ║
║ Source:        Figma Design (abc123)                         ║
╠══════════════════════════════════════════════════════════════╣
║ NEXT STEPS:                                                  ║
║ 1. Go to Website → Configuration → Settings → Theme          ║
║ 2. Select 'Theme My Awesome Theme'                           ║
║ 3. Preview and customize                                     ║
╚══════════════════════════════════════════════════════════════╝
```

## Version-Specific Adjustments

### Odoo 14-15 (Bootstrap 4)
- Use `ml-*`, `mr-*` classes (not `ms-*`, `me-*`)
- Different asset bundle syntax
- No snippet groups

### Odoo 16-17 (Bootstrap 5.1.3)
- Use `ms-*`, `me-*` classes
- Modern asset bundle syntax
- Simple snippet registration

### Odoo 18-19 (Bootstrap 5.1.3 + Snippet Groups)
- Use snippet groups in registration
- Owl v2 patterns available
- Enhanced website builder integration

## Troubleshooting Guide

### Common Issues and Solutions

Based on extensive production theme development, here are the most common issues and their solutions:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TROUBLESHOOTING GUIDE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ISSUE #1: Undefined variable "$o-color-palettes"                            │
│  ───────────────────────────────────────────────────                        │
│  CAUSE: Using map-merge() with core variable in prepended SCSS              │
│  FIX: Remove map-merge(), use $o-website-values-palettes with               │
│       'color-palettes-name': 'default-1' instead                            │
│                                                                               │
│  ISSUE #2: Undefined variable "$o-theme-font-configs"                        │
│  ─────────────────────────────────────────────────────                      │
│  CAUSE: Same as above - core variable not defined yet                       │
│  FIX: Define $o-theme-font-configs as STANDALONE (no map-merge)             │
│                                                                               │
│  ISSUE #3: Malformed Google Fonts @import URL                                │
│  ──────────────────────────────────────────────                              │
│  CAUSE: Using ir.asset record for external font URL                         │
│  SYMPTOM: @import url("https://...https://...")                              │
│  FIX: Remove ir.asset, use $o-theme-font-configs in SCSS                    │
│                                                                               │
│  ISSUE #4: XPath error "Element cannot be located"                           │
│  ─────────────────────────────────────────────────                          │
│  CAUSE: Complex XPath like //header//nav doesn't match HTML structure       │
│  FIX: Use simple XPath: //header, //footer, //main                          │
│                                                                               │
│  ISSUE #5: CSS showing 0 rules (empty stylesheet)                            │
│  ──────────────────────────────────────────────                              │
│  CAUSE: SCSS compilation failed silently                                     │
│  DIAGNOSIS: Check browser console for "Style compilation failed"            │
│  FIX: Fix SCSS errors, clear asset cache                                    │
│                                                                               │
│  ISSUE #6: Asset cache not clearing                                          │
│  ────────────────────────────────                                            │
│  FIX: Clear via Odoo shell:                                                 │
│       >>> self.env['ir.attachment'].search([                                │
│       ...     ('url', 'like', '/web/assets/')                               │
│       ... ]).unlink()                                                        │
│       >>> self.env.cr.commit()                                              │
│                                                                               │
│  ISSUE #7: KeyError 'website.theme.asset'                                   │
│  ──────────────────────────────────────                                      │
│  CAUSE: Incorrect model name for assets                                     │
│  FIX: Use __manifest__.py assets dict, not ir.asset XML records             │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Debugging SCSS Issues

```bash
# Step 1: Check browser console for compilation errors
# Look for: "Style compilation failed" or SCSS error messages

# Step 2: Verify stylesheets loaded
# In browser console:
document.styleSheets[0].cssRules.length  # Should be > 0

# Step 3: If 0 rules, SCSS compilation failed - check for:
# - Undefined variable errors
# - Syntax errors
# - Invalid map-merge() calls

# Step 4: Clear asset cache after fixing
python odoo-bin shell -d {{DATABASE}}
>>> self.env['ir.attachment'].search([('url', 'like', '/web/assets/')]).unlink()
>>> self.env.cr.commit()

# Step 5: Restart server and hard refresh browser (Ctrl+Shift+R)
```

### Correct Asset Bundle Configuration

```python
# __manifest__.py - CORRECT asset bundle configuration
'assets': {
    # Primary variables - PREPENDED (loads before Odoo core)
    # Contains: $o-theme-font-configs, $o-website-values-palettes
    'web._assets_primary_variables': [
        ('prepend', 'theme_name/static/src/scss/primary_variables.scss'),
    ],
    # Bootstrap overrides - loads after helpers (OPTIONAL but useful)
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

### Testing Checklist

Before considering a theme complete, verify:

- [ ] Fresh database creation works
- [ ] `base` + `website` module installation succeeds
- [ ] Theme module installs without errors
- [ ] Theme activation via website configurator works
- [ ] CSS compilation succeeds (check `document.styleSheets[n].cssRules.length > 0`)
- [ ] No SCSS compilation errors in browser console
- [ ] No JavaScript errors in browser console
- [ ] Header styling applies correctly
- [ ] Footer styling applies correctly
- [ ] Responsive layout works on mobile/tablet/desktop
- [ ] Website builder (edit mode) functions without errors

## Quick Variable Reference

### $o-theme-font-configs (Google Fonts)
```scss
$o-theme-font-configs: (
    'FontName': (
        'family': ('FontName', sans-serif),
        'url': 'FontName:300,400,500,600,700',  // Just the parameter!
    ),
);
```

### $o-website-values-palettes (Component Control)
| Category | Key Variables |
|----------|---------------|
| **Typography** | `'font'`, `'headings-font'`, `'navbar-font'`, `'buttons-font'` |
| **Header** | `'header-template'`, `'header-links-style'`, `'logo-height'` |
| **Footer** | `'footer-template'`, `'footer-effect'`, `'footer-scrolltop'` |
| **Buttons** | `'btn-padding-y'`, `'btn-padding-x'`, `'btn-border-radius'` |
| **Inputs** | `'input-padding-y'`, `'input-padding-x'`, `'input-border-radius'` |
| **Layout** | `'layout'` (full/boxed), `'link-underline'` |

### Header Templates
- `'default'` - Standard horizontal navbar
- `'hamburger'` - Hamburger menu (collapsed)
- `'vertical'` - Vertical sidebar navigation
- `'sidebar'` - Full sidebar layout

### Footer Templates
- `'default'` - Standard footer
- `'centered'` - Center-aligned
- `'minimalist'` - Clean minimal
- `'links'` - Link-heavy footer
- `'descriptive'` - Full description footer

## Notes

- Figma account access required (logged in via Chrome)
- H6 is always fixed at 16px (1rem) as the base reference
- Display classes extend the hierarchy for designs with large hero text
- Auto-fix attempts 3 times before reporting failure
- All generated code follows TaqaTechno standards
- **NEVER use map-merge() with core Odoo variables in theme SCSS**
- **NEVER use ir.asset records for external font URLs**
- **ALWAYS use simple XPath expressions**
- **PREFER $o-website-values-palettes over custom header/footer XML**
- **NO bootstrap_overridden.scss needed - variables control everything**

---

*TAQAT Techno - Figma to Odoo Theme Generator v5.0*
*Supports Odoo 14-19 with intelligent design extraction*
*Updated with comprehensive variable system from production reports*

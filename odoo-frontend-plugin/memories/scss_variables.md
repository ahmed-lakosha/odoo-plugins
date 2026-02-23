# SCSS Variables Reference

## Odoo Color System

### Semantic Colors (o-color-1 to o-color-5)

| Variable | Purpose | Typical Usage |
|----------|---------|---------------|
| `o-color-1` | Primary brand | Buttons, links, headers |
| `o-color-2` | Secondary/accent | CTAs, highlights |
| `o-color-3` | Light background | Sections, cards |
| `o-color-4` | White/base | Body background |
| `o-color-5` | Dark text | Headings, body text |

### $o-color-palettes Structure

```scss
$o-color-palettes: map-merge($o-color-palettes, (
    'my_theme': (
        'o-color-1': #207AB7,  // Primary
        'o-color-2': #FB9F54,  // Secondary
        'o-color-3': #F6F4F0,  // Light BG
        'o-color-4': #FFFFFF,  // White
        'o-color-5': #191A19,  // Dark
        'menu': 1,             // Menu uses o-color-1
        'footer': 1,           // Footer uses o-color-1
        'copyright': 5,        // Copyright uses o-color-5
    ),
));
```

## $o-website-values-palettes

Complete configuration for website appearance:

```scss
$o-website-values-palettes: (
    (
        'color-palettes-name': 'theme_name',

        // Typography
        'font': 'Inter',
        'headings-font': 'Poppins',
        'navbar-font': 'Inter',
        'buttons-font': 'Inter',
        'headings-line-height': 1.2,
        'line-height-base': 1.6,

        // Header
        'header-template': 'default',
        'header-links-style': 'default',
        'hamburger-position': 'right',
        'logo-height': 3rem,
        'fixed-logo-height': 2rem,

        // Buttons
        'btn-padding-y': 0.75rem,
        'btn-padding-x': 2rem,
        'btn-padding-y-sm': 0.5rem,
        'btn-padding-x-sm': 1.5rem,
        'btn-padding-y-lg': 1rem,
        'btn-padding-x-lg': 3rem,
        'btn-border-radius': 0.5rem,
        'btn-border-radius-sm': 0.25rem,
        'btn-border-radius-lg': 0.75rem,
        'btn-font-weight': 500,

        // Inputs
        'input-padding-y': 0.75rem,
        'input-padding-x': 1rem,
        'input-border-radius': 0.5rem,

        // Footer
        'footer-template': 'default',
        'footer-scrolltop': true,

        // Links
        'link-underline': 'never',
    ),
);
```

## Typography Multipliers

### Heading Size Multipliers

```scss
// Base: 16px (1rem)
$o-theme-h1-font-size-multiplier: (64 / 16);  // 64px = 4rem
$o-theme-h2-font-size-multiplier: (48 / 16);  // 48px = 3rem
$o-theme-h3-font-size-multiplier: (32 / 16);  // 32px = 2rem
$o-theme-h4-font-size-multiplier: (24 / 16);  // 24px = 1.5rem
$o-theme-h5-font-size-multiplier: (20 / 16);  // 20px = 1.25rem
$o-theme-h6-font-size-multiplier: (16 / 16);  // 16px = 1rem (FIXED BASE)
```

### Display Sizes (Extended Hierarchy)

For designs with more than 6 heading levels:

```scss
$display-font-sizes: (
  1: 6rem,    // 96px - Extra large hero
  2: 5.5rem,  // 88px - Large hero
  3: 5rem,    // 80px - Hero
  4: 4.5rem,  // 72px - Sub-hero
  5: 4rem,    // 64px - Same as H1
  6: 3.5rem,  // 56px - Between H1 and H2
) !default;
```

## Font Configuration

```scss
$o-theme-font-configs: map-merge($o-theme-font-configs, (
    'Inter': (
        'family': ('Inter', sans-serif),
        'url': 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
        'properties': (
            'base': (
                'font-size-base': 1rem,
                'line-height-base': 1.6,
            ),
        ),
    ),
));
```

## Bootstrap Override Variables

Use `!default` flag when overriding:

```scss
// In bootstrap_overridden.scss
$primary: var(--o-color-1) !default;
$secondary: var(--o-color-2) !default;

// Spacing
$spacer: 1rem !default;

// Border radius
$border-radius: 0.5rem !default;
$border-radius-sm: 0.25rem !default;
$border-radius-lg: 0.75rem !default;

// Transitions
$transition-base: all 0.3s ease-in-out !default;
```

## Version-Specific Variables

### Odoo 14-15
- Different variable names
- Bootstrap 4 syntax

### Odoo 16+
- Modern variable structure
- Bootstrap 5.1.3 syntax
- CSS custom properties support

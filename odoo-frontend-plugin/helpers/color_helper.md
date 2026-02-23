# Color Extraction & Mapping Helper

## Purpose
Helper patterns for extracting colors from designs and mapping to Odoo's semantic color system.

## Color Extraction from Figma

### Visual Identification
1. **Primary Color**: Most prominent brand color
   - Usually in buttons, links, headers
   - Often the logo color

2. **Secondary Color**: Accent/CTA color
   - Used for call-to-action buttons
   - Highlights and special elements

3. **Light Background**: Section backgrounds
   - Often a very light tint of primary
   - Or a neutral gray (#F5F5F5 range)

4. **White/Base**: Body background
   - Usually pure white (#FFFFFF)
   - Sometimes off-white (#FAFAFA)

5. **Dark Text**: Headings and body
   - Near-black (#191919 - #333333)
   - Sometimes uses primary darkened

## Odoo Color Mapping

### Semantic Mapping Rules
```
Figma Design          →    Odoo Variable
─────────────────────────────────────────
Primary Brand Color   →    o-color-1
Accent/CTA Color      →    o-color-2
Light Background      →    o-color-3
White/Base            →    o-color-4
Dark Text             →    o-color-5
```

### SCSS Output Format
```scss
$o-color-palettes: map-merge($o-color-palettes, (
    '{{PALETTE_NAME}}': (
        'o-color-1': {{PRIMARY}},    // Primary brand
        'o-color-2': {{SECONDARY}},  // Accent/CTA
        'o-color-3': {{LIGHT_BG}},   // Light sections
        'o-color-4': {{WHITE}},      // Body base
        'o-color-5': {{DARK}},       // Dark text
        'menu': 1,
        'footer': 1,
        'copyright': 5,
    ),
));
```

## Color Derivation Algorithms

### When Only Primary Available
```python
def derive_from_primary(primary_hex):
    """Derive full palette from single primary color."""
    h, s, l = hex_to_hsl(primary_hex)

    return {
        'o-color-1': primary_hex,
        'o-color-2': hsl_to_hex((h + 30) % 360, s, l),  # Shift hue
        'o-color-3': hsl_to_hex(h, s * 0.3, 0.95),      # Very light
        'o-color-4': '#FFFFFF',
        'o-color-5': hsl_to_hex(h, s * 0.2, 0.15),      # Very dark
    }
```

### When Primary + Secondary Available
```python
def derive_from_pair(primary_hex, secondary_hex):
    """Derive palette from primary and secondary."""
    h1, s1, l1 = hex_to_hsl(primary_hex)

    return {
        'o-color-1': primary_hex,
        'o-color-2': secondary_hex,
        'o-color-3': hsl_to_hex(h1, s1 * 0.3, 0.95),
        'o-color-4': '#FFFFFF',
        'o-color-5': '#191A19',  # Safe default
    }
```

## Color Utility Functions

### Hex to RGB
```python
def hex_to_rgb(hex_color):
    """Convert hex to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
```

### Lighten/Darken
```python
def lighten(hex_color, amount):
    """Lighten a color by percentage (0-1)."""
    h, s, l = hex_to_hsl(hex_color)
    new_l = min(1.0, l + (1 - l) * amount)
    return hsl_to_hex(h, s, new_l)

def darken(hex_color, amount):
    """Darken a color by percentage (0-1)."""
    h, s, l = hex_to_hsl(hex_color)
    new_l = max(0.0, l - l * amount)
    return hsl_to_hex(h, s, new_l)
```

### Contrast Check
```python
def get_contrast_ratio(color1, color2):
    """Calculate WCAG contrast ratio."""
    l1 = get_luminance(color1)
    l2 = get_luminance(color2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def has_sufficient_contrast(bg_color, text_color, level='AA'):
    """Check if contrast meets WCAG requirements."""
    ratio = get_contrast_ratio(bg_color, text_color)
    if level == 'AAA':
        return ratio >= 7.0
    return ratio >= 4.5  # AA level
```

## Common Color Palettes

### Corporate Blue
```
Primary:    #2C5282
Secondary:  #ED8936
Light BG:   #F7FAFC
White:      #FFFFFF
Dark:       #1A202C
```

### Modern Teal
```
Primary:    #0D9488
Secondary:  #F59E0B
Light BG:   #F0FDFA
White:      #FFFFFF
Dark:       #134E4A
```

### Elegant Purple
```
Primary:    #7C3AED
Secondary:  #EC4899
Light BG:   #F5F3FF
White:      #FFFFFF
Dark:       #1F2937
```

# SCSS Validation Patterns

## Purpose
Validate SCSS files for syntax errors and Odoo-specific patterns.

## Validation Rules

### 1. Syntax Validation

```python
def validate_scss_syntax(content):
    """Basic SCSS syntax validation."""
    errors = []

    # Check brace matching
    stack = []
    for i, char in enumerate(content):
        if char == '{':
            stack.append(i)
        elif char == '}':
            if not stack:
                errors.append(f"Unmatched closing brace at position {i}")
            else:
                stack.pop()

    for pos in stack:
        errors.append(f"Unclosed brace starting at position {pos}")

    return errors
```

### 2. Variable Validation

```python
def validate_odoo_variables(content, file_type):
    """Validate Odoo-specific SCSS variables."""
    errors = []
    warnings = []

    if file_type == 'primary_variables':
        # Must have color palette
        if '$o-color-palettes' not in content:
            warnings.append("Missing $o-color-palettes definition")

        # Should have website values
        if '$o-website-values-palettes' not in content:
            warnings.append("Missing $o-website-values-palettes (optional)")

        # Check for !default flag on overrides
        if 're.search(r'\$\w+:\s*[^!]+;', content)':
            warnings.append("Consider using !default flag for variable overrides")

    return errors, warnings
```

### 3. Color Format Validation

```python
def validate_color_values(content):
    """Validate color value formats."""
    errors = []

    # Find all hex colors
    hex_colors = re.findall(r'#([0-9A-Fa-f]{3,8})\b', content)
    for color in hex_colors:
        if len(color) not in [3, 6, 8]:
            errors.append(f"Invalid hex color length: #{color}")

    # Check for invalid color functions
    invalid_patterns = [
        (r'rgba\([^)]*\)', 'Consider using Sass rgba() function'),
        (r'hsl\([^)]*\)', 'Consider using Sass hsl() function'),
    ]

    return errors
```

### 4. Import Validation

```python
def validate_imports(content):
    """Validate SCSS import statements."""
    errors = []
    warnings = []

    # Check for deprecated @import
    if '@import' in content:
        warnings.append("@import is deprecated in Dart Sass, consider @use/@forward")

    # Check import paths
    imports = re.findall(r'@(?:import|use|forward)\s+["\']([^"\']+)["\']', content)
    for imp in imports:
        if imp.startswith('/'):
            errors.append(f"Absolute import path not recommended: {imp}")

    return errors, warnings
```

## Common SCSS Errors

### Missing Semicolons
```scss
// ERROR
$color: #333
$size: 16px

// CORRECT
$color: #333;
$size: 16px;
```

### Unclosed Braces
```scss
// ERROR
.container {
    .inner {
        color: red;
    // Missing closing brace

// CORRECT
.container {
    .inner {
        color: red;
    }
}
```

### Invalid Nesting
```scss
// ERROR - Too deep
.a {
    .b {
        .c {
            .d {
                .e {
                    // Avoid > 4 levels
                }
            }
        }
    }
}

// CORRECT - Flatten
.a .b .c .d .e {
    // ...
}
```

## Odoo-Specific Patterns

### Color Palette Definition
```scss
// CORRECT
$o-color-palettes: map-merge($o-color-palettes, (
    'my_theme': (
        'o-color-1': #207AB7,
        'o-color-2': #FB9F54,
        'o-color-3': #F6F4F0,
        'o-color-4': #FFFFFF,
        'o-color-5': #191A19,
    ),
));

// ERROR - Missing map-merge
$o-color-palettes: (
    'my_theme': (...)
);
```

### Typography Multipliers
```scss
// CORRECT
$o-theme-h1-font-size-multiplier: (64 / 16);

// ERROR - Using rem directly
$o-theme-h1-font-size-multiplier: 4rem;
```

### Bootstrap Overrides
```scss
// CORRECT - with !default
$primary: var(--o-color-1) !default;

// WARNING - without !default
$primary: var(--o-color-1);
```

## Auto-Fix Patterns

### Add Missing Semicolons
```python
def fix_missing_semicolons(content):
    """Add missing semicolons to variable declarations."""
    lines = content.split('\n')
    fixed = []
    for line in lines:
        stripped = line.rstrip()
        if re.match(r'^\s*\$[\w-]+:\s*.+[^;{,]\s*$', stripped):
            stripped += ';'
        fixed.append(stripped)
    return '\n'.join(fixed)
```

### Format Color Palettes
```python
def format_color_palette(colors):
    """Generate properly formatted color palette SCSS."""
    template = """$o-color-palettes: map-merge($o-color-palettes, (
    '{name}': (
        'o-color-1': {c1},
        'o-color-2': {c2},
        'o-color-3': {c3},
        'o-color-4': {c4},
        'o-color-5': {c5},
        'menu': 1,
        'footer': 1,
        'copyright': 5,
    ),
));"""
    return template.format(**colors)
```

## Validation Report

```
╔══════════════════════════════════════════════════════════════╗
║                    SCSS VALIDATION REPORT                     ║
╠══════════════════════════════════════════════════════════════╣
║ File: primary_variables.scss                                  ║
╠══════════════════════════════════════════════════════════════╣
║ SYNTAX: ✓ Valid                                               ║
║ COLORS: ✓ 5 colors defined                                    ║
║ VARIABLES: ⚠ 1 warning                                        ║
║   └── Consider using !default on line 15                      ║
║ IMPORTS: ✓ No issues                                          ║
╠══════════════════════════════════════════════════════════════╣
║ STATUS: PASSED with warnings                                  ║
╚══════════════════════════════════════════════════════════════╝
```

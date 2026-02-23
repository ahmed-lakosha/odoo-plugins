# Theme Generation Helper

## Purpose
Helper patterns for generating Odoo website themes.

## Theme Name Conventions

### Naming Rules
```python
def normalize_theme_name(name):
    """Convert name to valid Odoo module name."""
    # Remove special characters
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Ensure starts with letter
    if name[0].isdigit():
        name = 'theme_' + name
    # Add theme prefix if not present
    if not name.startswith('theme_'):
        name = 'theme_' + name
    return name.lower()
```

### Examples
- "Modern Corp" → `theme_modern_corp`
- "123 Design" → `theme_123_design`
- "my-theme" → `theme_my_theme`

## Directory Creation

```python
def create_theme_structure(theme_name, project_path):
    """Create full theme directory structure."""
    dirs = [
        '',
        'security',
        'data',
        'data/pages',
        'views',
        'views/layout',
        'views/snippets',
        'static',
        'static/description',
        'static/src',
        'static/src/scss',
        'static/src/js',
        'static/src/img',
    ]
    for d in dirs:
        path = os.path.join(project_path, theme_name, d)
        os.makedirs(path, exist_ok=True)
```

## Manifest Generation

### Required Fields
```python
manifest = {
    'name': display_name,
    'version': f'{odoo_version}.0.1.0.0',
    'category': 'Theme/Creative',
    'summary': f'Custom theme for {client_name}',
    'author': 'TaqaTechno',
    'website': 'https://www.taqatechno.com/',
    'support': 'info@taqatechno.com',
    'license': 'LGPL-3',
    'depends': ['website'],
    'data': data_files,
    'assets': assets_dict,
    'images': ['static/description/cover.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
```

### Asset Bundle Configuration
```python
def get_assets_dict(theme_name, version):
    """Generate assets dictionary for manifest."""
    assets = {
        'web._assets_primary_variables': [
            f'{theme_name}/static/src/scss/primary_variables.scss',
        ],
        'web._assets_frontend_helpers': [
            ('prepend', f'{theme_name}/static/src/scss/bootstrap_overridden.scss'),
        ],
        'web.assets_frontend': [
            f'{theme_name}/static/src/scss/theme.scss',
            f'{theme_name}/static/src/js/theme.js',
        ],
    }
    return assets
```

## Color Generation

### Auto-Derive Missing Colors
```python
def derive_colors(primary, secondary=None):
    """Derive full palette from primary (and optional secondary)."""
    from colorsys import rgb_to_hls, hls_to_rgb

    # Parse hex color
    r, g, b = hex_to_rgb(primary)
    h, l, s = rgb_to_hls(r/255, g/255, b/255)

    # Derive colors
    colors = {
        'o-color-1': primary,
        'o-color-2': secondary or shift_hue(primary, 30),
        'o-color-3': lighten(primary, 0.45),
        'o-color-4': '#FFFFFF',
        'o-color-5': darken(primary, 0.40) if l > 0.5 else '#191A19',
    }
    return colors
```

## Typography Calculation

### Multiplier Formula
```python
def calculate_multiplier(font_size_px, base=16):
    """Calculate font size multiplier."""
    return round(font_size_px / base, 2)
```

### Size Mapping
```python
def map_to_heading(font_sizes):
    """Map extracted sizes to H1-H6."""
    sorted_sizes = sorted(set(font_sizes), reverse=True)

    mapping = {}
    for i, size in enumerate(sorted_sizes[:6], 1):
        mapping[f'h{i}'] = size

    # Ensure H6 is 16px
    mapping['h6'] = 16

    return mapping
```

## Validation Helpers

### Check Theme Structure
```python
def validate_theme_structure(theme_path):
    """Validate theme has required files."""
    required = [
        '__init__.py',
        '__manifest__.py',
        'security/ir.model.access.csv',
        'static/src/scss/primary_variables.scss',
    ]
    missing = []
    for f in required:
        if not os.path.exists(os.path.join(theme_path, f)):
            missing.append(f)
    return missing
```

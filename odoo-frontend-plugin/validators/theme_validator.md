# Theme Validation Patterns

## Purpose
Validate generated themes before installation to catch common errors.

## Validation Checklist

### 1. Structure Validation

```python
REQUIRED_FILES = [
    '__init__.py',
    '__manifest__.py',
    'security/ir.model.access.csv',
]

RECOMMENDED_FILES = [
    'static/src/scss/primary_variables.scss',
    'static/src/scss/bootstrap_overridden.scss',
    'static/src/scss/theme.scss',
]

def validate_structure(theme_path):
    """Validate theme has required structure."""
    errors = []
    warnings = []

    for f in REQUIRED_FILES:
        if not os.path.exists(os.path.join(theme_path, f)):
            errors.append(f"Missing required file: {f}")

    for f in RECOMMENDED_FILES:
        if not os.path.exists(os.path.join(theme_path, f)):
            warnings.append(f"Missing recommended file: {f}")

    return errors, warnings
```

### 2. Manifest Validation

```python
REQUIRED_MANIFEST_FIELDS = ['name', 'version', 'depends']
RECOMMENDED_MANIFEST_FIELDS = ['summary', 'author', 'license', 'category']

def validate_manifest(manifest):
    """Validate __manifest__.py contents."""
    errors = []
    warnings = []

    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")

    for field in RECOMMENDED_MANIFEST_FIELDS:
        if field not in manifest:
            warnings.append(f"Missing recommended field: {field}")

    # Version format check
    version = manifest.get('version', '')
    if not re.match(r'^\d+\.\d+\.\d+\.\d+\.\d+$', version):
        errors.append(f"Invalid version format: {version}")

    # Depends check
    depends = manifest.get('depends', [])
    if 'website' not in depends:
        errors.append("Theme must depend on 'website' module")

    return errors, warnings
```

### 3. SCSS Validation

```python
def validate_scss(scss_content, filename):
    """Validate SCSS syntax and patterns."""
    errors = []
    warnings = []

    # Check for unclosed braces
    open_braces = scss_content.count('{')
    close_braces = scss_content.count('}')
    if open_braces != close_braces:
        errors.append(f"Mismatched braces in {filename}: {open_braces} open, {close_braces} close")

    # Check for missing semicolons (basic check)
    lines = scss_content.split('\n')
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if line and not line.endswith(('{', '}', ';', '//', '/*', '*/', ',')):
            if ':' in line and not line.startswith('@') and not line.startswith('//'):
                warnings.append(f"Possible missing semicolon at line {i} in {filename}")

    # Check for o-color-palettes
    if 'primary_variables' in filename:
        if '$o-color-palettes' not in scss_content:
            warnings.append("Missing $o-color-palettes definition")

    return errors, warnings
```

### 4. XML Validation

```python
def validate_xml(xml_content, filename):
    """Validate XML syntax."""
    errors = []

    try:
        from xml.etree import ElementTree
        ElementTree.fromstring(f"<root>{xml_content}</root>")
    except Exception as e:
        errors.append(f"XML syntax error in {filename}: {str(e)}")

    return errors
```

### 5. JavaScript Validation

```python
def validate_js(js_content, filename):
    """Validate JavaScript patterns."""
    errors = []
    warnings = []

    # Check for module annotation
    if '/** @odoo-module **/' not in js_content:
        errors.append(f"Missing @odoo-module annotation in {filename}")

    # Check for proper imports
    if 'publicWidget' in js_content:
        if 'import publicWidget' not in js_content:
            errors.append(f"Using publicWidget without proper import in {filename}")

    # Check for inline event handlers (bad practice)
    if 'onclick=' in js_content or 'onchange=' in js_content:
        warnings.append(f"Inline event handlers detected in {filename}")

    return errors, warnings
```

## Common Error Patterns

### Missing Dependencies
```
Error: Module not found: 'website'
Fix: Add 'website' to depends in __manifest__.py
```

### Invalid XML Syntax
```
Error: ParseError: no element found
Fix: Check for unclosed tags or missing root element
```

### SCSS Syntax Error
```
Error: SassError: expected "{"
Fix: Check for missing braces or semicolons
```

### Asset Path Not Found
```
Error: AssetError: File not found
Fix: Verify asset paths in manifest match actual file locations
```

## Auto-Fix Patterns

### Fix Missing Files
```python
def auto_fix_missing_files(theme_path, missing_files):
    """Create minimal versions of missing files."""
    templates = {
        '__init__.py': '',
        'security/ir.model.access.csv': 'id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n',
    }

    for f in missing_files:
        if f in templates:
            full_path = os.path.join(theme_path, f)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as fh:
                fh.write(templates[f])
```

### Fix Manifest Issues
```python
def auto_fix_manifest(manifest, theme_name):
    """Fix common manifest issues."""
    if 'depends' not in manifest:
        manifest['depends'] = []
    if 'website' not in manifest['depends']:
        manifest['depends'].append('website')

    if 'version' not in manifest:
        manifest['version'] = '17.0.1.0.0'

    return manifest
```

## Validation Report Format

```
╔══════════════════════════════════════════════════════════════╗
║                    THEME VALIDATION REPORT                    ║
╠══════════════════════════════════════════════════════════════╣
║ Theme: theme_my_theme                                         ║
║ Path: projects/client/theme_my_theme                          ║
╠══════════════════════════════════════════════════════════════╣
║ ERRORS (2):                                                   ║
║ ├── Missing required file: __init__.py                        ║
║ └── Missing @odoo-module annotation in theme.js               ║
║                                                               ║
║ WARNINGS (1):                                                 ║
║ └── Missing recommended file: bootstrap_overridden.scss       ║
║                                                               ║
║ STATUS: FAILED - Fix errors before installation               ║
╚══════════════════════════════════════════════════════════════╝
```

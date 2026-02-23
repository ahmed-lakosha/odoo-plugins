# Version Detection Helper

## Purpose
Automatically detect Odoo version and apply appropriate patterns.

## Detection Methods

### 1. From Config File
```python
# Read from conf/*.conf
config_path = "conf/project17.conf"
# Extract version from db_filter or path
```

### 2. From Module Path
```python
# Check path pattern: odoo{VERSION}/projects/...
import re
match = re.search(r'odoo(\d+)', module_path)
if match:
    version = match.group(1)
```

### 3. From Manifest
```python
# Check version field in __manifest__.py
# Format: "17.0.1.0.0" → Odoo 17
version = manifest.get('version', '').split('.')[0]
```

## Version-Specific Patterns

### Bootstrap Classes
```python
def get_margin_class(version, direction):
    """Get margin class for Odoo version."""
    if int(version) < 16:
        return f"m{'l' if direction == 'left' else 'r'}-"
    return f"m{'s' if direction == 'left' else 'e'}-"
```

### Asset Bundle Syntax
```python
def get_asset_syntax(version):
    """Get asset bundle syntax for version."""
    if int(version) < 16:
        return "legacy"  # data attribute based
    return "modern"  # assets dict in manifest
```

### Snippet Registration
```python
def use_snippet_groups(version):
    """Check if version uses snippet groups."""
    return int(version) >= 18
```

## Usage in Commands

```markdown
1. Detect version from project path
2. Load version-specific patterns from data/version_mapping.json
3. Apply patterns during theme generation
4. Validate output against version requirements
```

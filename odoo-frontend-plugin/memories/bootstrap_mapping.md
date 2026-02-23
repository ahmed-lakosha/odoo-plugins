# Odoo to Bootstrap Version Mapping

## Version Matrix

| Odoo Version | Bootstrap Version | Owl Version | JavaScript |
|--------------|------------------|-------------|------------|
| Odoo 14 | Bootstrap 4.x | - | ES6+ |
| Odoo 15 | Bootstrap 4.x | Owl v1 | ES6+ |
| Odoo 16 | Bootstrap 5.1.3 | Owl v1 | ES2020+ |
| Odoo 17 | Bootstrap 5.1.3 | Owl v2 | ES2020+ |
| Odoo 18 | Bootstrap 5.1.3 | Owl v2 | ES2020+ |
| Odoo 19 | Bootstrap 5.1.3 | Owl v2 | ES2020+ |

## Key CSS Class Changes

### Margin/Padding Classes

| Bootstrap 4 | Bootstrap 5 |
|-------------|-------------|
| `ml-*` | `ms-*` |
| `mr-*` | `me-*` |
| `pl-*` | `ps-*` |
| `pr-*` | `pe-*` |

### Float Classes

| Bootstrap 4 | Bootstrap 5 |
|-------------|-------------|
| `float-left` | `float-start` |
| `float-right` | `float-end` |

### Text Alignment

| Bootstrap 4 | Bootstrap 5 |
|-------------|-------------|
| `text-left` | `text-start` |
| `text-right` | `text-end` |

### Form Classes

| Bootstrap 4 | Bootstrap 5 |
|-------------|-------------|
| `form-group` | Removed (use `mb-3`) |
| `form-row` | Removed (use `row g-3`) |
| `custom-control` | `form-check` |
| `custom-checkbox` | `form-check` |

## JavaScript Changes

### jQuery to Vanilla JS

Bootstrap 5 removed jQuery dependency. However, Odoo still uses jQuery:

```javascript
// Odoo 14-15 (jQuery required)
$(document).ready(function() {
    // ...
});

// Odoo 16+ (jQuery still available but optional)
document.addEventListener('DOMContentLoaded', function() {
    // ...
});
```

### Data Attributes

| Bootstrap 4 | Bootstrap 5 |
|-------------|-------------|
| `data-toggle` | `data-bs-toggle` |
| `data-target` | `data-bs-target` |
| `data-dismiss` | `data-bs-dismiss` |
| `data-backdrop` | `data-bs-backdrop` |

## Grid System

Both versions use the same 12-column grid, but Bootstrap 5 added:
- `xxl` breakpoint (1400px+)
- RTL support via `start`/`end` classes
- Vertical alignment utilities

## Detection Script

```python
def detect_bootstrap_version(odoo_version):
    """Return Bootstrap version for Odoo version."""
    if int(odoo_version) < 16:
        return "4.x"
    return "5.1.3"
```

## Migration Patterns

### Odoo 14/15 → 16+

1. Replace `ml-*` with `ms-*`
2. Replace `mr-*` with `me-*`
3. Replace `text-left` with `text-start`
4. Replace `text-right` with `text-end`
5. Update data attributes to `data-bs-*`
6. Replace `float-left/right` with `float-start/end`

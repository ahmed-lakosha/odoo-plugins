# Bootstrap Version Mapping for Odoo

## Version Matrix

| Odoo Version | Bootstrap Version | Owl | Python | Notes |
|--------------|-------------------|-----|--------|-------|
| 14.0 | 4.5.0 | experimental | 3.7-3.10 | Last version with Bootstrap 4 |
| 15.0 | 5.0.2 | experimental | 3.8-3.11 | First version with Bootstrap 5 |
| 16.0 | 5.1.3 | v1 | 3.9-3.12 | Standardized on 5.1.3 |
| 17.0 | 5.1.3 | v1 | 3.10-3.13 | Primary development version |
| 18.0 | 5.1.3 | v2 | 3.10-3.13 | Owl v2 transition |
| 19.0 | 5.1.3 | v2 | 3.10-3.13 | Current version |

## CRITICAL: Version Detection

Always detect the Odoo version before applying any Bootstrap classes:
```bash
# Check manifest version
grep -r "version.*[0-9]\+\.[0-9]\+" __manifest__.py

# Or detect from directory name
# odoo17/ = Odoo 17 = Bootstrap 5.1.3
# odoo14/ = Odoo 14 = Bootstrap 4.5.0
```

## Bootstrap 4 to 5 Migration Guide

### Major Changes

1. **jQuery Dependency Removed**
   - Bootstrap 5 uses vanilla JavaScript
   - No need to load jQuery for Bootstrap components
   - Existing jQuery code still works with Odoo

2. **RTL Support**
   - Left/Right replaced with Start/End for RTL support
   - Better internationalization

3. **Utility API**
   - More powerful utility class generation
   - Better customization options

### Class Mapping Reference

#### Spacing

| Bootstrap 4 | Bootstrap 5 | Description |
|-------------|-------------|-------------|
| `ml-*` | `ms-*` | Margin Left → Margin Start |
| `mr-*` | `me-*` | Margin Right → Margin End |
| `pl-*` | `ps-*` | Padding Left → Padding Start |
| `pr-*` | `pe-*` | Padding Right → Padding End |

#### Text Alignment

| Bootstrap 4 | Bootstrap 5 | Description |
|-------------|-------------|-------------|
| `text-left` | `text-start` | Text align left |
| `text-right` | `text-end` | Text align right |
| `float-left` | `float-start` | Float left |
| `float-right` | `float-end` | Float right |

#### Forms

| Bootstrap 4 | Bootstrap 5 | Description |
|-------------|-------------|-------------|
| `form-group` | `mb-3` | Form group spacing |
| `custom-select` | `form-select` | Custom select |
| `custom-file` | `form-control` | Custom file input |
| `custom-range` | `form-range` | Range input |
| `custom-control` | `form-check` | Custom control |
| `custom-control-input` | `form-check-input` | Custom input |
| `custom-control-label` | `form-check-label` | Custom label |
| `custom-checkbox` | `form-check` | Checkbox |
| `custom-radio` | `form-check` | Radio button |
| `custom-switch` | `form-switch` | Switch toggle |

#### Components

| Bootstrap 4 | Bootstrap 5 | Description |
|-------------|-------------|-------------|
| `close` | `btn-close` | Close button |
| `media` | `d-flex` | Media object |
| `no-gutters` | `g-0` | No gutters in grid |

#### Badges

| Bootstrap 4 | Bootstrap 5 | Description |
|-------------|-------------|-------------|
| `badge-primary` | `bg-primary` | Primary badge |
| `badge-secondary` | `bg-secondary` | Secondary badge |
| `badge-success` | `bg-success` | Success badge |
| `badge-danger` | `bg-danger` | Danger badge |
| `badge-warning` | `bg-warning text-dark` | Warning badge |
| `badge-info` | `bg-info` | Info badge |
| `badge-light` | `bg-light text-dark` | Light badge |
| `badge-dark` | `bg-dark` | Dark badge |

#### Typography

| Bootstrap 4 | Bootstrap 5 | Description |
|-------------|-------------|-------------|
| `font-weight-bold` | `fw-bold` | Bold text |
| `font-weight-bolder` | `fw-bolder` | Bolder text |
| `font-weight-normal` | `fw-normal` | Normal weight |
| `font-weight-light` | `fw-light` | Light weight |
| `font-weight-lighter` | `fw-lighter` | Lighter weight |
| `font-italic` | `fst-italic` | Italic text |

#### Visibility

| Bootstrap 4 | Bootstrap 5 | Description |
|-------------|-------------|-------------|
| `sr-only` | `visually-hidden` | Screen reader only |
| `sr-only-focusable` | `visually-hidden-focusable` | SR only focusable |

### Removed Classes

These classes no longer exist in Bootstrap 5:

- `form-inline` - Use grid/flex utilities instead
- `input-group-append` - Use `input-group-text` directly
- `input-group-prepend` - Use `input-group-text` directly
- `jumbotron` - Recreate using utility classes
- `media` - Use flex utilities (`d-flex`)
- `badge-pill` - Use `rounded-pill` with badge

### New Features in Bootstrap 5

1. **Extended Color Palette**
   - More color utilities
   - Better semantic colors

2. **Improved Grid**
   - New `xxl` breakpoint (1400px+)
   - Better column gutters

3. **Utility API**
   - Generate custom utilities
   - Better SCSS customization

4. **Offcanvas Component**
   - New slide-in panel component
   - Better mobile menus

5. **Accordion Improvements**
   - Always expanded option
   - Better ARIA support

## Odoo-Specific Considerations

### Asset Bundles

Bootstrap is included in Odoo's asset bundles:
- `web.assets_frontend` - Main website bundle
- `web._assets_frontend_helpers` - Bootstrap overrides
- `web._assets_primary_variables` - Theme variables

### Theme Variables

Odoo provides additional variables on top of Bootstrap:
```scss
$o-color-1 through $o-color-5  // Theme colors
$o-website-values-palettes      // Complete theme configuration
```

### Website Builder Compatibility

When using Bootstrap classes:
- Editor recognizes standard Bootstrap utilities
- Custom classes should be prefixed (e.g., `o_`, `s_`)
- Use data attributes for editor features

## Migration Checklist

- [ ] Update all `ml-`, `mr-`, `pl-`, `pr-` classes
- [ ] Replace `text-left/right` with `text-start/end`
- [ ] Replace `float-left/right` with `float-start/end`
- [ ] Update form classes (custom-* to form-*)
- [ ] Replace `.close` with `.btn-close`
- [ ] Update badge classes to background utilities
- [ ] Replace font-weight classes with fw-*
- [ ] Update sr-only to visually-hidden
- [ ] Remove form-inline, use grid
- [ ] Remove jumbotron, recreate with utilities
- [ ] Test all jQuery-dependent code
- [ ] Verify responsive breakpoints (new xxl)
- [ ] Check custom Bootstrap overrides still work

## Automated Migration

Use the helper script for automatic conversion:

```bash
python helpers/bootstrap_mapper.py ml-3 mr-2 text-left form-group
# Output: ms-3 me-2 text-start mb-3
```

For bulk migration, use the Edit tool with regex patterns.

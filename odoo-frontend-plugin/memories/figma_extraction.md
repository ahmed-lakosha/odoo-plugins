# Figma Design Extraction Patterns

## Chrome MCP Tools for Figma

### Required Tools

```javascript
// Tab management
mcp__claude-in-chrome__tabs_context_mcp({ createIfEmpty: true })
mcp__claude-in-chrome__tabs_create_mcp()

// Navigation
mcp__claude-in-chrome__navigate({ url: figmaUrl, tabId: tabId })

// Interaction
mcp__claude-in-chrome__computer({ action: "wait", duration: 5, tabId: tabId })
mcp__claude-in-chrome__computer({ action: "screenshot", tabId: tabId })
mcp__claude-in-chrome__computer({ action: "left_click", coordinate: [x, y], tabId: tabId })

// Reading
mcp__claude-in-chrome__read_page({ tabId: tabId, filter: "all" })
mcp__claude-in-chrome__find({ query: "search term", tabId: tabId })
```

## Supported Figma URL Formats

```
https://www.figma.com/file/XXXX/Design-Name
https://www.figma.com/design/XXXX/Design-Name
https://www.figma.com/proto/XXXX/Design-Name
```

## Color Extraction Workflow

### Step 1: Identify Color Sources
- Look for color style definitions in Figma's right panel
- Identify primary colors from buttons, headers
- Identify secondary colors from CTAs, highlights

### Step 2: Map to Odoo Color System

| Figma Color | Odoo Variable | Purpose |
|-------------|---------------|---------|
| Primary | `o-color-1` | Brand color |
| Secondary | `o-color-2` | Accent color |
| Light BG | `o-color-3` | Section backgrounds |
| White | `o-color-4` | Body background |
| Dark Text | `o-color-5` | Text color |

### Step 3: Auto-Derivation (If Only 2 Colors Found)

```scss
// If only primary and secondary found:
$o-color-3: lighten($primary, 45%);  // Light BG
$o-color-4: #FFFFFF;                   // White
$o-color-5: darken($primary, 40%);     // Or #191A19
```

## Typography Extraction Workflow

### Step 1: Identify Text Styles
Click on heading text elements to inspect:
- Font family
- Font size (px)
- Font weight
- Line height

### Step 2: Build Hierarchy

```
H1: Largest heading (typically 48-72px)
H2: Section headers (typically 36-48px)
H3: Sub-sections (typically 24-36px)
H4: Card headers (typically 20-28px)
H5: Small headers (typically 18-24px)
H6: Captions (FIXED at 16px)
```

### Step 3: Calculate Multipliers

Formula: `multiplier = size_px / 16`

Example:
```scss
$o-theme-h1-font-size-multiplier: (64 / 16);  // 4.0
$o-theme-h2-font-size-multiplier: (48 / 16);  // 3.0
$o-theme-h3-font-size-multiplier: (32 / 16);  // 2.0
$o-theme-h4-font-size-multiplier: (24 / 16);  // 1.5
$o-theme-h5-font-size-multiplier: (20 / 16);  // 1.25
$o-theme-h6-font-size-multiplier: (16 / 16);  // 1.0 (FIXED)
```

## Extended Hierarchy (Display Classes)

If design has more than 6 heading levels (e.g., large hero text):

```scss
$display-font-sizes: (
  1: 6rem,    // 96px
  2: 5.5rem,  // 88px
  3: 5rem,    // 80px
  4: 4.5rem,  // 72px
  5: 4rem,    // 64px
  6: 3.5rem,  // 56px
);
```

## Figma Panel Navigation

### Design Panel (Right Sidebar)
- Click elements to inspect properties
- Look for "Fill" section for colors
- Look for "Text" section for typography

### Styles Panel
- Access via dropdown or Assets panel
- Contains defined color styles
- Contains defined text styles

## Extraction Checklist

- [ ] Primary color (buttons, headers)
- [ ] Secondary color (CTAs, accents)
- [ ] Background colors
- [ ] Text color (dark)
- [ ] Body font family
- [ ] Headings font family (if different)
- [ ] H1 size
- [ ] H2 size
- [ ] H3 size
- [ ] H4 size
- [ ] H5 size
- [ ] H6 size (default 16px)
- [ ] Display sizes (if applicable)
- [ ] Font weights
- [ ] Line heights

## Common Issues

### Issue: Can't Access Design
- Ensure logged into Figma in Chrome
- Check if design is shared/public
- May need view permissions

### Issue: Colors Not Visible
- Click directly on colored elements
- Check Figma's right panel for fill values
- Look for color styles in Assets

### Issue: Typography Not Clear
- Click on text elements directly
- Check Text section in right panel
- May need to inspect multiple elements

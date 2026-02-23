---
title: 'Odoo Frontend'
read_only: true
type: 'command'
description: 'Advanced Odoo frontend development with comprehensive theme development, /create-theme command, PWA support, modern JavaScript/TypeScript, testing frameworks, performance optimization, accessibility compliance, and real-time features. Features complete $o-website-values-palettes reference, theme mirror model architecture, publicWidget patterns with editableMode handling, and MCP integration. Supports Odoo 14-19 with auto-detection.'
---

# Odoo Frontend Plugin

Main entry point for the **Odoo Frontend Development** skill. Provides comprehensive tools for building professional Odoo website themes with modern web technologies.

## Quick Start

```
/odoo-frontend                         # Show help and available commands
/odoo-frontend status                  # Check detected Odoo version
/odoo-frontend version                 # Show plugin version info
```

## Available Commands

| Command | Description |
|---------|-------------|
| `/create-theme` | Generate complete Odoo theme from Figma design |
| `/theme_web_rec` | Create theme mirror models for multi-website support |

## Sub-Commands

### `/odoo-frontend status`
Check the current Odoo environment:
- Detected Odoo version
- Bootstrap version mapping
- Available theme modules

### `/odoo-frontend version`
Show plugin version and capabilities:
- Plugin version: 4.0.0
- Supported Odoo versions: 14-19
- Features enabled

## Theme Development

### Create a Theme from Figma
```
/create-theme --figma https://www.figma.com/file/abc123/MyDesign
```

Extracts:
- Colors (primary, secondary) → `o-color-1` to `o-color-5`
- Typography (H1-H6 with H6 fixed at 16px)
- Extended hierarchy (display-1 to display-6 if needed)

### Create Theme Mirror Models
```
/theme_web_rec <website_module_path> <theme_module_path>
```

Creates theme mirror models following Odoo core patterns for multi-website support.

## Features

### Theme Development
- **Complete Theme Scaffolding**: Generate full theme module structures
- **$o-website-values-palettes**: Complete color and typography configuration
- **Theme Mirror Models**: Multi-website support architecture
- **Bootstrap Version Management**: Auto-detect Bootstrap 4/5

### Modern JavaScript
- **publicWidget Framework**: Patterns with `editableMode` handling
- **TypeScript Support**: Full TypeScript integration
- **Owl Framework**: Support for Owl v1 and v2

### Progressive Web Apps
- **Service Workers**: Offline functionality
- **Push Notifications**: Web push API integration
- **App Manifests**: PWA configuration

### Performance & Accessibility
- **Core Web Vitals**: LCP, FID, CLS optimization
- **WCAG 2.1 AA**: Full accessibility compliance
- **Lighthouse Integration**: Performance auditing

## Version Compatibility

| Odoo | Bootstrap | Owl | JavaScript |
|------|-----------|-----|------------|
| 14 | 4.x | - | ES6+ |
| 15 | 4.x | v1 | ES6+ |
| 16 | 5.1.3 | v1 | ES2020+ |
| 17 | 5.1.3 | v2 | ES2020+ |
| 18 | 5.1.3 | v2 | ES2020+ |
| 19 | 5.1.3 | v2 | ES2020+ |

## Configuration

- **Supported Versions**: Odoo 14, 15, 16, 17, 18, 19
- **Primary Version**: Odoo 17
- **Bootstrap Versions**: 4.x (Odoo 14-15), 5.1.3 (Odoo 16+)
- **Auto-Detection**: Version detected from project path

## Examples

### Quick Theme Creation
```
/create-theme my_theme projects/client --version=17 --colors="#207AB7,#FB9F54,#F6F4F0,#FFFFFF,#191A19"
```

### Theme from Figma
```
/create-theme --figma https://www.figma.com/file/abc123/Design
```

### Mirror Model Generation
```
/theme_web_rec projects/pp/website_portfolio projects/pp/theme_pp
```

---

*TAQAT Techno - Odoo Frontend Development v4.0*
*Supports Odoo 14-19 with intelligent version detection*

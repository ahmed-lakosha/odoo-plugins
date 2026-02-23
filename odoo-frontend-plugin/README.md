# Odoo Frontend Plugin for Claude Code v4.0

Advanced Odoo frontend development plugin with **Figma browser automation**, PWA support, TypeScript, modern testing frameworks, performance optimization, accessibility compliance, and complete theme scaffolding for Odoo 14-19.

## 🎨 NEW: /create-theme with Figma Browser Automation

**Extract design variables directly from Figma and generate production-ready Odoo themes!**

```bash
# Open Figma design in Chrome, extract colors & typography, generate theme
/create-theme --figma https://www.figma.com/file/abc123/MyDesign

# Full arguments
/create-theme my_theme projects/my_project --figma <figma_url> --version=17

# Manual mode (without Figma)
/create-theme modern_corp projects/my_project --version=17 --colors="#207AB7,#FB9F54,#F6F4F0,#FFFFFF,#191A19"
```

### Figma Integration Features:
- 🔄 **Chrome Browser Automation**: Opens Figma via Claude-in-Chrome MCP tools
- 🎨 **Color Extraction**: Primary, secondary → `o-color-1` to `o-color-5` mapping
- 📝 **Typography Extraction**: H1-H6 with H6 fixed at 16px (1rem) base
- 📏 **Extended Hierarchy**: Display classes (display-1 to display-6) for designs with >6 levels
- ⚙️ **Auto-Fix**: Tests installation and automatically fixes common issues

Creates a complete theme module with:
- `$o-website-values-palettes` configuration
- Semantic `o-color-1` to `o-color-5` system
- Individual page files (best practice)
- publicWidget JavaScript with `editableMode`
- Menu configuration and asset bundles
- Version-specific snippet registration

## Overview

The Odoo Frontend Plugin supercharges your Odoo website and theme development with modern web technologies, automated version detection, and comprehensive development patterns. It provides everything needed for building professional, performant, and accessible Odoo frontends.

## Features

### 🎨 Theme Development
- **🆕 /create-theme Command**: Generate complete theme modules with all files
- **Complete Theme Scaffolding**: Generate full theme module structures
- **Theme Mirror Models**: `/theme_web_rec` command for multi-website support
- **Bootstrap Version Management**: Auto-detect and handle Bootstrap 4/5
- **SCSS Variable System**: Proper color palettes and typography
- **Snippet Development**: Modern snippet patterns with Odoo 19 support

### 🚀 Modern JavaScript
- **TypeScript Support**: Full TypeScript integration
- **ES2020+ Features**: Modern JavaScript with proper transpilation
- **Owl Framework**: Support for both Owl v1 and v2
- **Web Components**: Custom elements and shadow DOM
- **RPC Migration**: Automatic RPC service to fetch API conversion

### 📱 Progressive Web Apps
- **Service Workers**: Offline functionality and caching strategies
- **Push Notifications**: Web push API integration
- **App Manifests**: PWA configuration and installation
- **Background Sync**: Queue actions for offline execution

### 🧪 Testing Frameworks
- **Jest**: Unit and integration testing
- **Cypress**: E2E testing with visual regression
- **BackstopJS**: Visual regression testing
- **Coverage Reports**: Code coverage analysis

### ⚡ Performance Optimization
- **Core Web Vitals**: LCP, FID, CLS optimization
- **Lighthouse Integration**: Performance auditing
- **Vite Build System**: Fast HMR and optimized builds
- **Critical CSS**: Inline critical styles
- **Resource Hints**: Preload, prefetch, preconnect

### ♿ Accessibility
- **WCAG 2.1 AA Compliance**: Full accessibility standards
- **ARIA Patterns**: Proper ARIA attributes and roles
- **Screen Reader Support**: Tested with NVDA, JAWS
- **Keyboard Navigation**: Complete keyboard accessibility
- **Focus Management**: Proper focus trapping and restoration

### 🔄 Real-time Features
- **WebSockets**: Real-time communication
- **Server-Sent Events**: Live data streaming
- **Live Collaboration**: Multi-user editing support
- **Push Notifications**: Browser push API

### 🎯 Auto-Detection
- **Version Detection**: Automatically detect Odoo version
- **Bootstrap Mapping**: Map Odoo version to Bootstrap version
- **Framework Detection**: Identify Owl v1 vs v2
- **Module Structure**: Analyze existing module patterns

## Installation

### Via Claude Code CLI
```bash
/plugin install odoo-frontend
```

### Manual Installation
1. Clone this repository to your Claude Code plugins directory
2. Ensure the plugin structure is maintained:
   ```
   odoo-frontend-plugin/
   ├── .claude-plugin/
   │   └── plugin.json
   ├── commands/                    # Slash commands (at plugin root)
   │   ├── create-theme.md
   │   └── theme_web_rec.md
   ├── data/                        # JSON configuration data
   │   ├── color_palettes.json
   │   ├── theme_templates.json
   │   ├── typography_defaults.json
   │   └── version_mapping.json
   ├── helpers/                     # Helper documentation
   │   ├── color_helper.md
   │   ├── theme_helper.md
   │   └── version_helper.md
   ├── hooks/
   │   └── hooks.json
   ├── memories/                    # Best practices & patterns
   │   ├── bootstrap_mapping.md
   │   ├── figma_extraction.md
   │   ├── publicwidget_patterns.md
   │   ├── scss_variables.md
   │   └── theme_development.md
   ├── odoo-frontend/               # Main skill folder
   │   ├── SKILL.md
   │   └── scripts/
   ├── reference/                   # Technical references
   │   ├── bootstrap_versions.md
   │   ├── owl_migration.md
   │   └── ...
   ├── validators/                  # Validation patterns
   │   ├── scss_validator.md
   │   └── theme_validator.md
   └── README.md
   ```

## Commands

### `/odoo-frontend:create-theme` - Figma-to-Odoo Theme Generator (v4.0)

Create complete, production-ready Odoo theme modules with **Figma browser automation**.

#### Usage
```bash
# Figma mode (Recommended) - Opens Figma in Chrome, extracts design variables
/create-theme --figma https://www.figma.com/file/abc123/MyDesign

# Full arguments with Figma
/create-theme my_theme projects/client --figma <url> --version=17

# Manual mode (without Figma)
/create-theme modern_corp projects/client --version=17 --colors="#207AB7,#FB9F54,#F6F4F0,#FFFFFF,#191A19" --font="IBM Plex Sans"
```

#### Figma Extraction Workflow
1. **Opens Figma in Chrome** via Claude-in-Chrome MCP
2. **Extracts Colors**: Primary → `o-color-1`, Secondary → `o-color-2`, etc.
3. **Extracts Typography**: H1-H6 sizes (H6 always 16px as base)
4. **Extended Hierarchy**: Adds `display-1` to `display-6` for >6 heading levels
5. **Generates Theme** with all SCSS variables
6. **Tests Installation** and auto-fixes errors

#### What Gets Created
- `__manifest__.py` with proper asset bundles
- `primary_variables.scss` with `$o-website-values-palettes` (from Figma)
- Semantic color palette (`o-color-1` to `o-color-5`)
- Typography multipliers: `$o-theme-h1-font-size-multiplier` etc.
- Display font sizes (if extended hierarchy detected)
- Individual page files (home, about, contact, services)
- publicWidget JavaScript with `editableMode` handling
- Menu configuration
- Custom snippet templates
- Security rules

### `/odoo-frontend:theme_web_rec` - Theme Mirror Model Generator

Create theme mirror models following Odoo core patterns for multi-website support.

#### Usage
```
/odoo-frontend:theme_web_rec <website_module_path> <theme_module_path> [model_name]
```

#### Example
```
/odoo-frontend:theme_web_rec projects/pp/website_portfolio projects/pp/theme_pp
```

This command:
- Analyzes existing website models
- Creates theme mirror models (theme.website.MODEL)
- Sets up view delegation pattern
- Configures installation hooks
- Updates security rules
- Generates sample templates

## Usage Examples

### Create a New Theme
```
"Create a new Odoo 17 theme with Bootstrap 5.1.3 and modern design"
```

### Add PWA Support
```
"Add PWA functionality to my Odoo website with offline support"
```

### Implement Testing
```
"Set up Jest and Cypress testing for my Odoo frontend module"
```

### Optimize Performance
```
"Optimize my Odoo website for Core Web Vitals"
```

### Ensure Accessibility
```
"Make my Odoo theme WCAG 2.1 AA compliant"
```

## Available Scripts

### Version Detector
```bash
python odoo-frontend/scripts/version_detector.py <module_path>
```
Automatically detect Odoo version and Bootstrap mapping

### Theme Mirror Generator
```bash
python odoo-frontend/scripts/theme_mirror_generator.py <website_path> <theme_path>
```
Create theme mirror models for multi-website support

## Version Compatibility

| Odoo Version | Bootstrap Version | Owl Version | JavaScript |
|--------------|------------------|-------------|------------|
| Odoo 14 | Bootstrap 4.x | - | ES6+ |
| Odoo 15 | Bootstrap 4.x | Owl v1 | ES6+ |
| Odoo 16 | Bootstrap 5.1.3 | Owl v1 | ES2020+ |
| Odoo 17 | Bootstrap 5.1.3 | Owl v2 | ES2020+ |
| Odoo 18 | Bootstrap 5.1.3 | Owl v2 | ES2020+ |
| Odoo 19 | Bootstrap 5.1.3 | Owl v2 | ES2020+ |

## Development Patterns

### PublicWidget Pattern
```javascript
/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.MyWidget = publicWidget.Widget.extend({
    selector: '.my-widget',
    events: {
        'click .button': '_onClick',
    },
    start: function () {
        this._super.apply(this, arguments);
        // Initialize widget
    },
    _onClick: function (ev) {
        // Handle click
    },
});
```

### Owl Component Pattern
```javascript
/** @odoo-module **/
import { Component, useState } from "@odoo/owl";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.state = useState({
            value: 0
        });
    }

    increment() {
        this.state.value++;
    }
}
```

### SCSS Variables (Odoo 19)
```scss
// primary_variables.scss
$o-color-palettes: map-merge($o-color-palettes, (
    'my_theme': (
        'o-color-1': #primary,
        'o-color-2': #secondary,
        'o-color-3': #light,
        'o-color-4': #dark,
        'o-color-5': #info,
        'menu': 1,
        'footer': 4,
    ),
));
```

## MCP Integration

The plugin supports MCP (Model Context Protocol) tools:
- **Claude-in-Chrome**: Browser automation for Figma design extraction
  - `mcp__claude-in-chrome__tabs_context_mcp` - Get browser context
  - `mcp__claude-in-chrome__navigate` - Navigate to Figma URL
  - `mcp__claude-in-chrome__computer` - Screenshots and interactions
  - `mcp__claude-in-chrome__read_page` - Extract design elements
  - `mcp__claude-in-chrome__find` - Locate color/typography elements
- **Figma**: Convert Figma designs to Odoo HTML
- **Chrome DevTools**: Extract styles from websites
- **Filesystem**: Advanced file operations

## Best Practices

### Theme Development
1. Always use theme mirror models for multi-website support
2. Follow Odoo's snippet structure conventions
3. Use proper SCSS variable naming
4. Implement responsive design with Bootstrap utilities

### Performance
1. Minimize JavaScript bundle size
2. Use lazy loading for images and components
3. Implement proper caching strategies
4. Optimize Critical Rendering Path

### Accessibility
1. Use semantic HTML elements
2. Provide proper ARIA labels
3. Ensure keyboard navigation
4. Test with screen readers

### Testing
1. Write unit tests for business logic
2. Create E2E tests for user workflows
3. Implement visual regression testing
4. Maintain >80% code coverage

## Troubleshooting

### Common Issues

#### "Bootstrap version mismatch"
- Use version detector to identify correct Bootstrap version
- Update SCSS imports accordingly

#### "Owl component not rendering"
- Check Owl version (v1 vs v2)
- Verify template XML syntax
- Ensure proper module loading

#### "Theme not applying to website"
- Verify theme installation on specific website
- Check theme_template_id assignment
- Confirm view delegation setup

## Documentation

Comprehensive documentation in:
- `SKILL.md`: Complete skill implementation
- `reference/`: Bootstrap mappings and patterns
- `templates/`: Starter templates
- `commands/`: Command documentation

## Contributing

We welcome contributions! Please:
1. Follow existing code patterns
2. Add tests for new features
3. Update documentation
4. Submit pull requests

## Support

- **Repository**: https://github.com/taqat-techno/plugins
- **Issues**: https://github.com/taqat-techno/plugins/issues
- **Contact**: contact@taqat-techno.com

## License

MIT License - See LICENSE file for details

## Changelog

### Version 4.0.0 (Latest)
- **NEW**: Figma browser automation via Claude-in-Chrome MCP tools
- **NEW**: Automatic color extraction from Figma designs
- **NEW**: Typography extraction (H1-H6 with H6 fixed at 16px)
- **NEW**: Extended hierarchy with display classes for >6 heading levels
- **NEW**: Auto-fix for installation issues
- Chrome MCP integration for design variable extraction
- Complete SCSS template generation from Figma

### Version 3.1.0
- `/create-theme` command for complete theme generation
- Theme generation based on 40+ real-world implementations
- Individual page files pattern (best practice)
- Enhanced `$o-website-values-palettes` support
- publicWidget patterns with `editableMode` handling
- Version-specific snippet registration (14-19)

### Version 3.0.0
- Enhanced theme mirror model architecture
- Complete `$o-website-values-palettes` reference
- Semantic color system documentation
- MCP integration improvements

### Version 2.0.0
- Added PWA support with service workers
- TypeScript integration
- Modern testing frameworks
- Performance optimization tools
- Accessibility compliance features
- Real-time capabilities
- MCP tool integration
- Theme mirror model command

### Version 1.0.0
- Initial release
- Basic theme scaffolding
- Bootstrap version management
- Odoo 14-17 support

## Acknowledgments

Developed by TAQAT Techno for the Claude Code community. Built with extensive experience in Odoo frontend development and modern web technologies.
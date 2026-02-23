# Odoo Upgrade Plugin for Claude Code

A comprehensive Claude Code plugin for migrating Odoo modules between versions (14-19) with automated pattern recognition and fixes.

## Overview

The Odoo Upgrade Plugin provides intelligent assistance for upgrading Odoo ERP modules across different versions. It handles complex migrations including XML views, Python API changes, JavaScript/OWL components, theme SCSS variables, and manifest updates.

## Features

### 🔄 Version Support
- Supports Odoo versions 14, 15, 16, 17, 18, and 19
- Handles migrations: 14→15, 15→16, 16→17, 17→18, 18→19
- Automatic version detection from module manifests

### 🎯 Transformation Capabilities
- **100+ transformation patterns** for automatic code migration
- **50+ auto-fixes** for common compatibility issues
- **XML View Transformations**: tree→list, search view groups, kanban templates
- **Python API Migrations**: slug functions, URL routing, field definitions
- **JavaScript/OWL Updates**: RPC service replacement, component migrations
- **Theme SCSS Variables**: Bootstrap 4→5, color palette updates

### 🛠️ Key Components
- **Pre-check Phase**: Scan for compatibility issues before migration
- **Backup System**: Automatic timestamped backups before changes
- **Pattern Engine**: Regex-based transformations for different file types
- **Validation Phase**: Test module installation after migration
- **Report Generation**: Detailed migration reports with manual steps

## Installation

### Via Claude Code CLI
```bash
/plugin install odoo-upgrade
```

### Manual Installation
1. Clone this repository to your Claude Code plugins directory
2. Ensure the plugin structure is maintained:
   ```
   odoo-upgrade-plugin/
   ├── .claude-plugin/
   │   └── plugin.json
   └── odoo-upgrade/
       ├── SKILL.md
       ├── scripts/
       ├── patterns/
       ├── fixes/
       └── reference/
   ```

## Usage

### Activate the Skill
The skill activates automatically when you:
- Request upgrading Odoo modules between versions
- Fix version compatibility errors
- Migrate themes or custom modules
- Resolve RPC service errors
- Convert XML views for newer versions

### Example Commands

#### Basic Module Upgrade
```
"Upgrade my Odoo module from version 17 to 19"
```

#### Theme Migration
```
"Migrate my theme from Odoo 18 to Odoo 19 with Bootstrap 5 support"
```

#### Fix Specific Issues
```
"Fix RPC service errors in my Odoo 19 frontend components"
```

## Available Scripts

The plugin includes several Python scripts for specific tasks:

### Quick Fix Script
```bash
python odoo-upgrade/scripts/quick_fix_odoo19.py <project_path>
```
Fast targeted fixes for common Odoo 19 issues

### Pre-check Script
```bash
python odoo-upgrade/scripts/odoo19_precheck.py <project_path>
```
Scan for compatibility issues before migration

### Full Upgrade Script
```bash
python odoo-upgrade/scripts/upgrade_to_odoo19.py <project_path> <target_version>
```
Comprehensive upgrade with all transformations

### RPC Service Fix
```bash
python odoo-upgrade/scripts/fix_rpc_service.py <project_path>
```
Specialized fix for RPC service migrations

## Common Migration Patterns

### XML View Updates
- **Tree to List**: `<tree>` → `<list>`
- **Search Groups**: Remove `<group>` tags from search views
- **Kanban Templates**: `t-name="kanban-box"` → `t-name="card"`
- **Cron Jobs**: Remove `numbercall` field

### JavaScript Migrations
- **RPC Service**: Replace with fetch-based JSON-RPC
- **OWL Components**: Update imports and lifecycle methods
- **CSRF Handling**: Add proper token management

### Python API Changes
- **Slug Functions**: Add compatibility wrappers
- **URL Routing**: Update import paths
- **Field Definitions**: Update deprecated field types

## Configuration

The plugin uses the following configuration structure:

```json
{
  "name": "odoo-upgrade",
  "version": "3.0.0",
  "skills": "./odoo-upgrade/",
  "scripts": "./odoo-upgrade/scripts/",
  "metadata": {
    "odoo-versions": ["14", "15", "16", "17", "18", "19"],
    "transformation-patterns": 100,
    "auto-fixes": 50
  }
}
```

## Testing

After upgrading a module, test:
- ✅ Module installation without errors
- ✅ All views load correctly
- ✅ JavaScript components function
- ✅ Theme displays properly
- ✅ API endpoints respond
- ✅ Cron jobs execute
- ✅ Search/filter functionality

## Troubleshooting

### Common Issues

#### "Service rpc is not available"
- **Cause**: Using `useService("rpc")` in frontend components
- **Solution**: Plugin automatically replaces with `_jsonRpc` helper

#### "Invalid field 'numbercall'"
- **Cause**: Field removed in Odoo 19
- **Solution**: Plugin automatically removes from cron definitions

#### "Invalid view definition"
- **Cause**: `<group>` tags in search views
- **Solution**: Plugin automatically restructures search views

## Documentation

Detailed documentation available in:
- `patterns/`: Transformation pattern definitions
- `fixes/`: Specific fix documentation
- `reference/`: Error catalogs and API changes
- `SKILL.md`: Complete skill implementation

## Contributing

Contributions are welcome! Please:
1. Follow the existing pattern structure
2. Add tests for new transformations
3. Update documentation
4. Submit pull requests to the main repository

## Support

- **Repository**: https://github.com/taqat-techno/plugins
- **Issues**: https://github.com/taqat-techno/plugins/issues
- **Contact**: contact@taqat-techno.com

## License

MIT License - See LICENSE file for details

## Changelog

### Version 3.0.0
- Added Odoo 19 support with major frontend changes
- RPC service replacement patterns
- Enhanced theme migration capabilities
- 100+ transformation patterns
- Improved error handling and reporting

### Version 2.0.0
- Added Odoo 18 support
- Slug function compatibility
- Enhanced XML transformations

### Version 1.0.0
- Initial release with Odoo 14-17 support
- Basic transformation patterns
- Manifest updates

## Acknowledgments

Developed by TAQAT Techno for the Claude Code community. Based on extensive experience with Odoo ERP implementations and migrations.
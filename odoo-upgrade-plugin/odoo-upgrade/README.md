# Odoo Module Upgrade Skill

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Odoo](https://img.shields.io/badge/Odoo-14%20|%2015%20|%2016%20|%2017%20|%2018%20|%2019-purple.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Automatically upgrade custom Odoo modules and themes across major versions with intelligent code transformations, testing, and comprehensive reporting.

## 🚀 Features

- ✅ **Multi-Version Support**: Upgrade from Odoo 14/15/16/17/18 to 19
- ✅ **Cumulative Changes**: Handles multi-version jumps (e.g., 14→19)
- ✅ **Automatic Transformations**: Python, XML, JavaScript, SCSS
- ✅ **Safe Migration**: Creates backups before modifications
- ✅ **Testing**: Validates installation in target version
- ✅ **Detailed Reports**: Comprehensive documentation
- ✅ **Theme Support**: Bootstrap 5, SCSS, publicWidget
- ✅ **Tool Integration**: Runs `odoo-bin upgrade_code`

### 🆕 New in v2.0 (Odoo 19 Enhanced)
- **Pre-Check Tool**: Scan for issues before upgrading
- **Quick Fix Utility**: Apply targeted fixes for common problems
- **Enhanced Detection**: All Odoo 19 breaking changes covered
- **Act_window Fixes**: Automatic view_mode tree→list conversion
- **JS Class Cleanup**: Removes incompatible js_class attributes
- **Complete RPC Migration**: Full frontend RPC to fetch API conversion

### 🎉 NEW in v3.0 (Enhanced Validation & Auto-Fix)
- **✅ Comprehensive Syntax Validation**: Python (AST), XML, JavaScript, SCSS
- **🔧 Automated Fix Library**: Pattern-based corrections for 10+ issue types
- **🔄 Pre & Post-Upgrade Validation**: Catch errors before and after upgrade
- **↩️ Automatic Rollback**: Restore from backup if critical errors detected
- **🔍 Dry-Run Mode**: Preview changes before applying
- **📊 Detailed Reports**: Validation and fix reports in Markdown
- **🧪 Test Suite**: Comprehensive unit and integration tests
- **🎯 Unified CLI**: Single command-line interface for all operations

## 📦 Installation

### As Part of Marketplace (Recommended)

```bash
# Clone marketplace to plugins directory
cd ~/.claude/plugins/marketplaces
git clone https://github.com/taqat-techno/plugins.git taqat-techno-plugins

# All skills auto-discovered by Claude Code
```

### As Standalone Skill

```bash
# Copy just this skill
mkdir -p ~/.claude/skills
curl -o ~/.claude/skills/odoo-upgrade.md \
  https://raw.githubusercontent.com/taqat-techno/plugins/main/odoo-development/odoo-upgrade/SKILL.md
```

### Windows Installation

```cmd
REM Marketplace method
cd %USERPROFILE%\.claude\plugins\marketplaces
git clone https://github.com/taqat-techno/plugins.git taqat-techno-plugins

REM Or standalone
curl -o %USERPROFILE%\.claude\skills\odoo-upgrade.md ^
  https://raw.githubusercontent.com/taqat-techno/plugins/main/odoo-development/odoo-upgrade/SKILL.md
```

## 🎯 Usage

### Via Claude Code (Recommended)

Simply ask Claude Code to upgrade your module:

```
"Upgrade custom_inventory module from odoo17 to odoo18"

"Migrate my theme_custom from version 14 to version 19"

"Upgrade the custom_pos module in TAQAT project from v16 to v19"
```

### Via Unified CLI (New!)

Use the command-line interface for direct control:

```bash
# Complete upgrade workflow with auto-fix
python odoo_upgrade_cli.py workflow /path/to/module --auto-fix

# Check for issues before upgrading
python odoo_upgrade_cli.py precheck /path/to/module

# Validate syntax
python odoo_upgrade_cli.py validate /path/to/module --verbose

# Quick fixes (with dry-run)
python odoo_upgrade_cli.py quickfix /path/to/module --dry-run

# Apply specific automatic fixes
python odoo_upgrade_cli.py autofix /path/to/module --specific xml_odoo19,js_rpc

# Full upgrade with validation
python odoo_upgrade_cli.py upgrade /path/to/module --auto-fix

# Run test suite
python odoo_upgrade_cli.py test --verbose
```

### Individual Scripts

Each tool can also be run independently:

```bash
# Syntax validation
python syntax_validator.py /path/to/module --verbose --report validation.md

# Auto-fix library
python auto_fix_library.py /path/to/module
python auto_fix_library.py /path/to/module --specific xml_comments,js_rpc

# Quick fixes
python quick_fix_odoo19.py /path/to/module --dry-run --validate

# Pre-upgrade check
python odoo19_precheck.py /path/to/module

# Full upgrade
python upgrade_to_odoo19.py /path/to/module --auto-fix
```

## 📋 What Gets Upgraded

### Python Code
- `name_get()` → `_compute_display_name()` (v17)
- Hook signatures: `pre_init_hook(env)` instead of `(cr)`
- Context keys: `active_id` → `id`
- Access control methods: `check_access()`, `has_access()`
- ORM changes and deprecated field removals

### XML/Views
- **Critical**: `attrs={}` → direct expressions (v17)
  ```xml
  <!-- Before -->
  <field name="color" attrs="{'invisible': [('state','=','done')]}"/>
  <!-- After -->
  <field name="color" invisible="state == 'done'"/>
  ```
- `<tree>` → `<list>` (v18)
- `states={}` → `invisible=` expressions
- Settings view restructure: `<app>`, `<block>`, `<setting>` tags

### JavaScript
- Legacy widgets → OWL v1/v2 components
- `odoo.define()` → ES6 imports
- Add `/** @odoo-module **/` annotations
- publicWidget framework for themes

### Themes
- Bootstrap 3/4 → Bootstrap 5 classes
- `.less` → `.scss` conversion
- Modern grid and utility classes

## 🔧 Enhanced Tools

### 1. Syntax Validator (`syntax_validator.py`)
Comprehensive syntax checking for all file types:
- **Python**: AST parsing, decorator validation, import checking
- **XML**: Well-formedness, Odoo structure, comment validation
- **JavaScript**: Bracket matching, module declarations, async/await patterns
- **SCSS**: Brace balance, variable validation, Odoo theme compliance

Features:
- Per-file validation with detailed error messages
- Line number references for quick fixes
- Warnings vs. errors classification
- Markdown report generation

### 2. Auto-Fix Library (`auto_fix_library.py`)
Pattern-based automated corrections:
- **Python Fixes**: Import updates, API decorators, syntax corrections
- **XML Fixes**: Comment sanitization, Odoo 19 compatibility, view transformations
- **JavaScript Fixes**: RPC migration, module declarations, async/await
- **SCSS Fixes**: Variable renaming, syntax corrections

Features:
- Automatic backup before changes
- Selective fix application
- Rollback support
- Detailed fix reports

### 3. Enhanced Main Upgrader (`upgrade_to_odoo19.py`)
Now includes:
- Pre-upgrade validation with optional abort
- Post-upgrade validation with auto-fix
- Automatic rollback on critical failures
- Interactive prompts for issue resolution
- Comprehensive validation reports

### 4. Improved Quick Fix (`quick_fix_odoo19.py`)
Enhanced with:
- **Dry-run mode**: Preview changes without modification
- **Validation integration**: Check syntax before/after fixes
- **Detailed reports**: Dry-run and validation reports
- Progress tracking and change summaries

### 5. Unified CLI (`odoo_upgrade_cli.py`)
Single interface for all operations:
```bash
Commands:
  precheck   - Scan for compatibility issues
  validate   - Check syntax of all files
  quickfix   - Apply targeted fixes
  autofix    - Pattern-based corrections
  upgrade    - Full upgrade with validation
  workflow   - Complete automated workflow
  test       - Run test suite
```

## 📚 Documentation

- [Full Skill Documentation](./SKILL.md)
- [Usage Guide](./USAGE.md)
- [Changelog](./CHANGELOG.md)
- [Error Reference](./reference/error_catalog.md)
- [Fix Patterns](./patterns/)
- [Detailed Fixes](./fixes/)

## ⚠️ Limitations

The skill **cannot** automatically:
- Migrate database data (use OpenUpgrade separately)
- Rewrite complex custom business logic
- Fix third-party module compatibility
- Deploy to production

## 🔧 Requirements

- **Claude Code**: Latest version with skills support
- **Odoo Installations**: Multiple versions (e.g., odoo14/, odoo17/, odoo19/)
- **Directory Structure**: Custom modules in `projects/` (NOT `odoo/addons/`)
- **Python**: Version compatible with target Odoo
- **PostgreSQL**: For testing (13+)

## 📝 License

MIT License - See [LICENSE](../../../LICENSE)

---

**Part of**: [TAQAT Techno Plugins Marketplace](https://github.com/taqat-techno/plugins)
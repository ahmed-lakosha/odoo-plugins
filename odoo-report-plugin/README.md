# Odoo Report Plugin

Professional Odoo Email Templates & QWeb Reports toolkit for Claude Code.

## Overview

A comprehensive skill for creating, managing, debugging, and migrating email templates and PDF reports across **Odoo 14-19** with intelligent pattern recognition and version-aware syntax.

## Features

- **Version-Aware**: Automatic syntax selection based on detected Odoo version
- **50+ Email Patterns**: Ready-to-use email template patterns
- **30+ QWeb Patterns**: Ready-to-use report template patterns
- **Smart Validation**: Pre-flight checks for syntax, fields, and security
- **Migration Tools**: Seamless template migration between Odoo versions

## Supported Versions

| Version | Status | Key Features |
|---------|--------|--------------|
| Odoo 14 | Supported | `t-esc` syntax, `report_template` |
| Odoo 15 | Supported | `t-out` syntax, `render_engine` |
| Odoo 16 | Supported | `template_category`, enhanced security |
| Odoo 17 | **Primary** | `report_template_ids` M2M |
| Odoo 18 | Supported | Layout variants |
| Odoo 19 | Supported | Company branding colors |

## Installation

This plugin is automatically available in Claude Code when working in Odoo projects.

## Quick Start

```
# Show help
/odoo-report

# Create email template
/create-email-template sale.order quotation

# Create QWeb report
/create-qweb-report sale.order detailed_quote

# Analyze existing template
/analyze-template sale.email_template_edi_sale

# Migrate to new version
/migrate-template templates.xml 19
```

## Commands

### Template Creation

| Command | Description |
|---------|-------------|
| `/create-email-template` | Create professional email template |
| `/create-qweb-report` | Create QWeb PDF report |

### Template Management

| Command | Description |
|---------|-------------|
| `/list-templates` | List templates by model/module |
| `/analyze-template` | Analyze template for issues |
| `/debug-template` | Debug rendering problems |
| `/preview-template` | Preview template output |
| `/validate-template` | Validate before deployment |

### Template Fixes

| Command | Description |
|---------|-------------|
| `/fix-template` | Auto-fix common issues |
| `/migrate-template` | Migrate between versions |

## Plugin Structure

```
odoo-report-plugin/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── odoo-report/
│   └── SKILL.md              # Main skill definition (2000+ lines)
├── commands/                  # Command definitions
│   ├── create-email-template.md
│   ├── create-qweb-report.md
│   ├── analyze-template.md
│   ├── debug-template.md
│   ├── migrate-template.md
│   ├── list-templates.md
│   ├── preview-template.md
│   ├── fix-template.md
│   ├── validate-template.md
│   └── odoo-report.md
├── memories/                  # Decision-making knowledge
│   ├── version_routing.md
│   ├── template_patterns.md
│   └── qweb_best_practices.md
├── data/                      # Configuration data
│   ├── template_fields.json
│   ├── context_variables.json
│   └── layouts.json
├── validators/
│   └── template_validator.md
├── helpers/
│   └── version_helper.md
├── hooks/
│   └── hooks.json
└── templates/                 # Pattern templates
    ├── email/
    │   ├── basic_notification.xml
    │   └── document_email.xml
    └── qweb/
        ├── basic_report.xml
        └── table_report.xml
```

## Version Migration

The plugin handles automatic migration between versions:

| From | To | Changes Applied |
|------|-----|-----------------|
| 14 | 15+ | `t-esc` → `t-out`, `t-raw` → `t-out` |
| 14-16 | 17+ | `report_template` → `report_template_ids` |
| Any | 16+ | Add `template_category` |
| Any | 19 | Add company branding colors |

## Documentation

- **Full Research**: `C:\odoo\researches\ODOO_EMAIL_TEMPLATES_COMPLETE_RESEARCH.md`
- **SKILL Reference**: `odoo-report/SKILL.md`
- **Pattern Library**: `templates/email/*.xml`, `templates/qweb/*.xml`

## Author

**TaqaTechno**
- Website: https://www.taqatechno.com/
- Email: info@taqatechno.com

## License

LGPL-3.0

# Odoo Report Plugin v2.0.0

Professional Odoo Email Templates & QWeb Reports toolkit for Claude Code.

## Overview

A comprehensive skill for creating, managing, debugging, and migrating email templates and PDF reports across **Odoo 14-19** with intelligent pattern recognition and version-aware syntax.

**v2.0** consolidates 9 separate commands into 1 skill with 3 sub-commands plus natural language capabilities for analysis, debugging, fixing, validation, listing, and previewing.

## Features

- **Version-Aware**: Automatic syntax selection based on detected Odoo version
- **50+ Email Patterns**: Ready-to-use email template patterns
- **30+ QWeb Patterns**: Ready-to-use report template patterns
- **Smart Validation**: Pre-flight checks for syntax, fields, and security
- **Migration Tools**: Seamless template migration between Odoo versions
- **Natural Language**: Analyze, debug, fix, validate, list, and preview via conversation

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
# Create email template
/odoo-report create-email sale.order quotation

# Create QWeb report
/odoo-report create-report sale.order detailed_quote

# Migrate template to new version
/odoo-report migrate templates.xml 19
```

### Natural Language (no command needed)

The skill automatically activates when you ask about template operations:

```
"Analyze this email template for issues and improvements"
"Debug why my email template shows plain text instead of HTML"
"Fix common issues in my email template"
"Validate my QWeb report template before deployment"
"List all email templates for sale.order in my module"
"Preview this email template with sample data"
```

## Commands

| Command | Description |
|---------|-------------|
| `/odoo-report create-email` | Create professional email template |
| `/odoo-report create-report` | Create QWeb PDF report |
| `/odoo-report migrate` | Migrate templates between Odoo versions |

### Natural Language Capabilities

| Capability | Trigger |
|------------|---------|
| **Analyze** | Ask to analyze or review a template for issues and improvements |
| **Debug** | Ask to debug rendering problems, missing fields, or broken output |
| **Fix** | Ask to auto-fix encoding, QWeb expressions, or version-specific syntax |
| **Validate** | Ask to validate a template before deployment |
| **List** | Ask to list or discover templates by model or module |
| **Preview** | Ask to preview template output with sample data |

## Plugin Structure

```
odoo-report-plugin/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── odoo-report/
│   └── SKILL.md              # Main skill definition (1750+ lines)
├── commands/                  # Command definitions
│   ├── create-email.md
│   ├── create-report.md
│   ├── migrate.md
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

> **Migration note**: Use `/odoo-report migrate <file> <target_version>` for automated migration. The skill handles all version-specific syntax transformations including QWeb directives, field references, and report action updates.

## Documentation

- **Full Research**: `C:\TQ-WorkSpace\odoo\researches\ODOO_EMAIL_TEMPLATES_COMPLETE_RESEARCH.md`
- **SKILL Reference**: `odoo-report/SKILL.md`
- **Pattern Library**: `templates/email/*.xml`, `templates/qweb/*.xml`

## Author

**TaqaTechno**
- Website: https://www.taqatechno.com/
- Email: support@example.com

## License

LGPL-3.0

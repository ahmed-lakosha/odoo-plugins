---
title: 'Odoo Report'
read_only: true
type: 'command'
description: 'Main entry point for Odoo Email Templates & QWeb Reports skill'
---

# Odoo Report Plugin

Main entry point for the **Odoo Email Templates & QWeb Reports** skill. Provides comprehensive tools for creating, managing, debugging, and migrating email templates and PDF reports across Odoo 14-19.

## Quick Start

```
/odoo-report                           # Show help and available commands
/odoo-report status                    # Check detected Odoo version
/odoo-report templates sale.order      # List templates for model
```

## Available Commands

### Template Creation

| Command | Description |
|---------|-------------|
| `/create-email-template` | Create professional email template |
| `/create-qweb-report` | Create QWeb PDF report |
| `/create-notification` | Create notification with layout |
| `/create-digest-email` | Create digest/summary email |

### Template Management

| Command | Description |
|---------|-------------|
| `/list-templates` | List templates by model/module |
| `/analyze-template` | Analyze template for issues |
| `/debug-template` | Debug rendering problems |
| `/preview-template` | Preview template output |
| `/validate-template` | Validate before deployment |

### Template Fixes & Migration

| Command | Description |
|---------|-------------|
| `/fix-template` | Auto-fix common issues |
| `/migrate-template` | Migrate between versions |

### QWeb Reports

| Command | Description |
|---------|-------------|
| `/style-report` | Add CSS styling |
| `/add-header-footer` | Custom header/footer |

## Supported Versions

| Version | Status | Key Features |
|---------|--------|--------------|
| Odoo 14 | Supported | t-esc syntax, report_template |
| Odoo 15 | Supported | t-out syntax, render_engine |
| Odoo 16 | Supported | template_category, enhanced security |
| Odoo 17 | Primary | report_template_ids M2M |
| Odoo 18 | Supported | Layout variants |
| Odoo 19 | Supported | Company branding colors |

## Version Detection

The plugin automatically detects Odoo version from:
1. Current working directory (odoo14, odoo15, etc.)
2. `__manifest__.py` version string
3. User-specified `--version` flag

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│              ODOO REPORT PLUGIN - QUICK REFERENCE                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  CREATE:                                                         │
│  /create-email-template MODEL PURPOSE                            │
│  /create-qweb-report MODEL NAME                                  │
│                                                                   │
│  MANAGE:                                                         │
│  /list-templates MODEL                                           │
│  /analyze-template TEMPLATE_ID                                   │
│  /debug-template TEMPLATE_ID RECORD_ID                           │
│                                                                   │
│  FIX:                                                            │
│  /fix-template FILE                                              │
│  /migrate-template FILE VERSION                                  │
│                                                                   │
│  HELP:                                                           │
│  /odoo-report help COMMAND                                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Documentation

- **Full Research**: `C:\odoo\researches\ODOO_EMAIL_TEMPLATES_COMPLETE_RESEARCH.md`
- **Plugin SKILL**: `odoo-report/SKILL.md`
- **Pattern Library**: `templates/email/*.xml`, `templates/qweb/*.xml`

---

*Odoo Report Plugin v1.0*
*TaqaTechno - Professional Email Templates & QWeb Reports*
*Supports Odoo 14-19*

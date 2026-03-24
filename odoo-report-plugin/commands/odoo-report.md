---
title: 'Odoo Reports & Templates'
read_only: false
type: 'command'
description: 'Odoo email templates & QWeb reports - create, validate, migrate, and manage'
argument-hint: '[create|validate|migrate|analyze|preview] [args...]'
---

# /odoo-report - Email Templates & QWeb Reports

Parse `$ARGUMENTS` and route:

| Sub-command | Description |
|-------------|-------------|
| `create` | Create a new email template or QWeb PDF report |
| `validate` | Validate QWeb syntax, context variables, and version compatibility |
| `migrate` | Migrate templates between Odoo versions |
| `analyze` | Analyze existing template for issues and improvements |
| `preview` | Preview template output with sample data |
| *(none)* | Show help and list available templates |

Use the odoo-report skill for:
- Template creation workflows (mail.template, ir.actions.report)
- QWeb syntax validation and best practices
- Version-specific field routing (14-19 differences)
- Arabic/RTL report support
- Context variable reference
- wkhtmltopdf setup and troubleshooting

Templates at `${CLAUDE_PLUGIN_ROOT}/templates/` (email + QWeb examples).
Reference data at `${CLAUDE_PLUGIN_ROOT}/data/` (context_variables, layouts, template_fields).

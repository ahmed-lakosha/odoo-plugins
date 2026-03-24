---
title: 'Odoo i18n'
read_only: false
type: 'command'
description: 'Odoo internationalization toolkit - extract, validate, missing, export translations'
argument-hint: '[extract|validate|missing|export] [args...]'
---

# /odoo-i18n - Odoo Internationalization Toolkit

Parse `$ARGUMENTS` to determine the subcommand and execute using the odoo-i18n skill for workflow guidance and translation rules.

| Subcommand | Script | Description |
|------------|--------|-------------|
| `extract` | `i18n_extractor.py` | Extract translatable strings to .pot/.po |
| `validate` | `i18n_validator.py` | Validate .po file syntax, encoding, specifiers |
| `missing` | `i18n_reporter.py` | Report untranslated strings and coverage % |
| `export` | (Odoo CLI) | Export/import translations via Odoo CLI |
| (none) | | Show this help table |

## Execution

Run the matching script:

```bash
# Extract
python "${CLAUDE_PLUGIN_ROOT}/odoo-i18n/scripts/i18n_extractor.py" --module <path> --lang <code>

# Validate
python "${CLAUDE_PLUGIN_ROOT}/odoo-i18n/scripts/i18n_validator.py" --po-file <path> [--lang <code>] [--strict]

# Missing
python "${CLAUDE_PLUGIN_ROOT}/odoo-i18n/scripts/i18n_reporter.py" --module <path> --lang <code> [--format text|json|csv] [--min-pct <N>]

# Export (Odoo CLI)
python odoo-bin -c <conf> -d <db> --i18n-export --modules=<module> --language=<lang> --output=<path> --stop-after-init
```

Use the odoo-i18n skill for detailed workflow steps, translation rules, version-specific patterns, RTL/Arabic handling, and troubleshooting.

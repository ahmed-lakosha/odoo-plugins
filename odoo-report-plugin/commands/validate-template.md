---
title: 'Validate Template'
read_only: true
type: 'command'
description: 'Validate template syntax, context, and security before deployment'
---

# Validate Template

Validate template **syntax**, **context variables**, and **security** before deployment.

## Usage

```
/validate-template [file-or-template-id] [--version VERSION]
/validate-template projects/module/data/template.xml
/validate-template --strict sale.email_template_edi_sale
```

## Validation Checks

```
┌─────────────────────────────────────────────────────────────────┐
│                    TEMPLATE VALIDATION                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  XML SYNTAX:                                                     │
│  ✓ Well-formed XML                                               │
│  ✓ Valid UTF-8 encoding                                          │
│  ✓ Proper tag closure                                            │
│  ✓ Valid attribute quoting                                       │
│                                                                   │
│  QWEB SYNTAX:                                                    │
│  ✓ Valid t-if/t-elif/t-else structure                           │
│  ✓ t-foreach has t-as                                            │
│  ✓ t-set has t-value                                             │
│  ✓ Version-appropriate output tags                               │
│                                                                   │
│  FIELD REFERENCES:                                               │
│  ✓ object.name exists on model                                   │
│  ✓ object.partner_id.name traversable                            │
│  ⚠ object.custom_field - check exists                           │
│                                                                   │
│  CONTEXT VARIABLES:                                              │
│  ✓ format_amount available                                       │
│  ✓ format_date available                                         │
│  ✓ is_html_empty available                                       │
│                                                                   │
│  SECURITY:                                                       │
│  ✓ No eval/exec calls                                            │
│  ✓ No file system access                                         │
│  ✓ No external network calls                                     │
│  ✓ Sandbox-safe expressions                                      │
│                                                                   │
│  Result: VALID (1 warning)                                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Validation Modes

| Mode | Description |
|------|-------------|
| `--quick` | Syntax only |
| `--standard` | Syntax + fields (default) |
| `--strict` | All checks including security |
| `--security` | Security audit only |

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│               VALIDATE TEMPLATE QUICK REFERENCE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  VALIDATION LEVELS:                                              │
│  • ERROR   - Must fix, template won't work                       │
│  • WARNING - Should fix, may cause issues                        │
│  • INFO    - Informational, best practice                        │
│                                                                   │
│  EXIT CODES:                                                     │
│  • 0 - Valid (no errors)                                         │
│  • 1 - Errors found                                              │
│  • 2 - Validation failed to run                                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Related Commands

| Command | Description |
|---------|-------------|
| `/analyze-template` | Detailed analysis |
| `/fix-template` | Auto-fix issues |
| `/debug-template` | Runtime debugging |

---

*Part of Odoo Report Plugin v1.0*

---
title: 'Fix Template'
read_only: false
type: 'command'
description: 'Auto-fix common template issues with safe transformations'
---

# Fix Template

Auto-fix common template issues with **safe transformations** and **backup creation**.

## Usage

```
/fix-template [file-or-template-id]
/fix-template projects/module/data/template.xml
/fix-template sale.email_template_edi_sale
```

### Natural Language

```
"Fix issues in my email template"
"Auto-fix the template errors"
"Clean up the template syntax"
```

## Fixable Issues

### Automatic Fixes

| Issue | Fix Applied |
|-------|-------------|
| `t-esc` in Odoo 15+ | Replace with `t-out` |
| `t-raw` deprecated | Replace with `t-out` |
| Missing null checks | Add `or ''` fallback |
| Unclosed XML tags | Close tags properly |
| Invalid XML entities | Escape `&`, `<`, `>` |
| Hardcoded button colors | Add company branding variables |

### Manual Review Required

| Issue | Reason |
|-------|--------|
| Complex expressions | May change behavior |
| Custom render methods | Needs context review |
| Security patterns | Requires audit |

## Fix Process

```
┌─────────────────────────────────────────────────────────────────┐
│                       FIX TEMPLATE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Source: projects/module/data/mail_template.xml                  │
│  Backup: projects/module/data/mail_template.xml.bak              │
│                                                                   │
│  Fixes Applied:                                                  │
│                                                                   │
│  [AUTO] Line 15: t-esc → t-out                                  │
│         <t t-esc="object.name"/> →                               │
│         <t t-out="object.name"/>                                 │
│                                                                   │
│  [AUTO] Line 28: Missing null check                              │
│         object.partner_id.name →                                 │
│         object.partner_id.name or ''                             │
│                                                                   │
│  [SKIP] Line 45: Complex expression                              │
│         Requires manual review                                   │
│                                                                   │
│  Summary: 2 auto-fixed, 1 skipped                                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Fix Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Show fixes without applying |
| `--no-backup` | Skip backup creation |
| `--force` | Apply all fixes including risky |
| `--version VERSION` | Target specific Odoo version |

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                 FIX TEMPLATE QUICK REFERENCE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  SAFE AUTO-FIXES:                                                │
│  • t-esc → t-out                                                 │
│  • t-raw → t-out                                                 │
│  • Missing null checks                                           │
│  • XML entity escaping                                           │
│                                                                   │
│  CREATES BACKUP:                                                 │
│  • Original file saved as .bak                                   │
│  • Can restore with: mv file.xml.bak file.xml                    │
│                                                                   │
│  USE WITH:                                                       │
│  /analyze-template → identify issues                             │
│  /fix-template → auto-fix safe issues                            │
│  /debug-template → verify fixes work                             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Related Commands

| Command | Description |
|---------|-------------|
| `/analyze-template` | Identify issues first |
| `/debug-template` | Test after fixing |
| `/migrate-template` | Full version migration |

---

*Part of Odoo Report Plugin v1.0*

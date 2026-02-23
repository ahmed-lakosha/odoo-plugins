---
title: 'Check Access Rules'
read_only: true
type: 'command'
description: 'Check model access rule completeness for an Odoo module — finds models with missing or incomplete ir.model.access.csv entries.'
---

# /check-access <module-path>

Scan an Odoo module for model access rule completeness. This command identifies every model defined in `models/*.py` and verifies it has appropriate entries in `security/ir.model.access.csv`.

## Usage

```
/check-access /path/to/module
/check-access /path/to/module --verbose
/check-access /path/to/module --fix
```

## What It Checks

### 1. Missing Model Access Rules (CRITICAL)
Any model defined with `_name = '...'` that has no entry in `ir.model.access.csv` is immediately accessible to ALL authenticated users. This is the most common Odoo security mistake.

```python
# This model...
class MyModel(models.Model):
    _name = 'my.model'
    name = fields.Char()

# ...requires this CSV entry:
# access_my_model_user,my.model user,model_my_model,group_user,1,1,1,0
```

### 2. Missing Wizard (TransientModel) Access Rules (HIGH)
Transient models are often overlooked. Without access rules, any user can instantiate and execute wizard logic.

```python
# Wizards also need access rules!
class MyWizard(models.TransientModel):
    _name = 'my.wizard'
    # Needs: access_my_wizard_user,my.wizard user,model_my_wizard,[group],1,1,1,1
```

### 3. Empty Group References (HIGH)
CSV entries with an empty `group_id:id` column grant access to ALL authenticated users, regardless of their role.

```csv
# DANGEROUS — grants access to everyone
access_my_model_all,my.model all,model_my_model,,1,1,1,0
```

### 4. Overly Permissive Permissions (MEDIUM)
Non-manager groups with full CRUD including DELETE (`perm_unlink=1`) are flagged as potentially overly permissive.

### 5. Unknown Group References (LOW)
CSV entries referencing groups that aren't defined in the module or known Odoo base modules.

### 6. Missing Record Rules for Company Models (HIGH)
Models with a `company_id = fields.Many2one('res.company')` field but no multi-company record rules.

## Output Format

```
========================================
ACCESS CHECKER REPORT — my_module
========================================
Total issues: 3
  CRITICAL: 1
  HIGH: 1
  MEDIUM: 1

[CRITICAL] models/my_model.py:15
  Model 'my.model' (class MyModel) has no access rules in ir.model.access.csv.
  Expected CSV entry with model_id:id = 'model_my_model'

[HIGH] models/my_wizard.py:8
  Transient (wizard) 'my.wizard' (class MyWizard) has no access rules.
  Expected CSV entry with model_id:id = 'model_my_wizard'

[MEDIUM] security/ir.model.access.csv:5
  Access rule 'access_my_model_user' grants full CRUD including DELETE
  to group 'my_module.group_user' which appears to be a non-manager group.
```

## Auto-Fix Mode

When used with `--fix`, the AI assistant will:

1. Scan all model definitions
2. Check which ones are missing from CSV
3. Generate the correct CSV entries with appropriate permissions
4. Determine the right groups based on module's group definitions
5. Write the updated `security/ir.model.access.csv`

### Generated CSV Example

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink

# my.model — standard CRUD model
access_my_model_user,my.model user,model_my_model,my_module.group_my_module_user,1,1,1,0
access_my_model_manager,my.model manager,model_my_model,my_module.group_my_module_manager,1,1,1,1

# my.wizard — transient model (full CRUD for lifecycle management)
access_my_wizard_user,my.wizard user,model_my_wizard,my_module.group_my_module_user,1,1,1,1
```

## model_id:id Derivation Rules

The `model_id:id` field in the CSV must match the format Odoo uses internally:

| Model `_name` | CSV `model_id:id` |
|--------------|-------------------|
| `my.model` | `model_my_model` |
| `account.move.line` | `model_account_move_line` |
| `res.partner` | `model_res_partner` |
| `sale.order` | `model_sale_order` |

**Rule**: Replace all dots with underscores, prepend `model_`.

## Standard Access Patterns

### Internal Application Model
```csv
access_[model]_user,[model] user,model_[model],[module].group_[module]_user,1,1,1,0
access_[model]_manager,[model] manager,model_[model],[module].group_[module]_manager,1,1,1,1
```

### Read-Only Reference Data
```csv
access_[model]_user,[model] user,model_[model],base.group_user,1,0,0,0
access_[model]_admin,[model] admin,model_[model],base.group_system,1,1,1,1
```

### Portal-Accessible Model
```csv
access_[model]_user,[model] user,model_[model],[module].group_user,1,1,1,0
access_[model]_portal,[model] portal,model_[model],base.group_portal,1,0,0,0
```

### Transient (Wizard) Model
```csv
access_[wizard]_user,[wizard] user,model_[wizard],[module].group_user,1,1,1,1
```

## Running Directly

```bash
python scripts/access_checker.py /path/to/module
python scripts/access_checker.py /path/to/module --json
python scripts/access_checker.py /path/to/module --verbose
```

## Integration

This check is automatically included when running `/odoo-security` or `/security-audit`. Run it standalone when you want focused access control analysis without the full security audit.

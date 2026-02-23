---
title: 'Find sudo() Usage'
read_only: true
type: 'command'
description: 'Find all .sudo() calls in an Odoo module and classify them by security risk and context — privilege escalation, loops, unscoped usage, and safe patterns.'
---

# /find-sudo <module-path>

Scan an Odoo module for all `.sudo()` usage and classify each occurrence by security risk. Not all sudo() calls are dangerous — this command helps you distinguish safe patterns from privilege escalation risks.

## Usage

```
/find-sudo /path/to/module
/find-sudo /path/to/module --verbose
/find-sudo /path/to/module --all
```

## Options

| Option | Description |
|--------|-------------|
| `--verbose` | Show code context (5 lines around each sudo() call) |
| `--all` | Show ALL sudo() calls including safe ones (OK severity) |

## Risk Classification

### CRITICAL — sudo() in Public/None-Auth Controller
The most dangerous pattern. Unauthenticated users can access any record.

```python
# CRITICAL — public route + sudo() = anyone can access any record
@http.route('/orders', auth='public')
def orders(self):
    orders = request.env['sale.order'].sudo().search([])  # ANY order!
    return request.render('template', {'orders': orders})
```

**Fix**: Add domain filter scoped to current user, or change `auth='user'`.

### HIGH — sudo() in Loop
Performance degradation plus unnecessarily repeated privilege escalation.

```python
# HIGH — sudo() called on every iteration
def compute_stats(self):
    for record in self:
        related = self.env['related.model'].sudo().search([  # Called N times!
            ('record_id', '=', record.id)
        ])
        record.total = sum(related.mapped('amount'))

# CORRECT — single sudo() call outside loop
def compute_stats(self):
    related_data = self.env['related.model'].sudo().read_group(
        [('record_id', 'in', self.ids)],
        ['record_id', 'amount:sum'],
        ['record_id']
    )
    totals = {d['record_id'][0]: d['amount'] for d in related_data}
    for record in self:
        record.total = totals.get(record.id, 0.0)
```

### HIGH — sudo() Accessing Sensitive Models
sudo() that reaches into sensitive models (res.users, hr.payslip, account.payment, etc.) without domain restriction.

```python
# HIGH — sudo() on sensitive model without domain filter
def get_user_data(self, user_id):
    user = self.env['res.users'].sudo().browse(user_id)  # Any user!
    return user.read(['name', 'email', 'password'])  # Includes password hash!
```

### MEDIUM — Unscoped sudo() Without Domain
sudo() call that doesn't immediately apply search/browse/domain filtering.

```python
# MEDIUM — what does sudo() give access to? unclear without a filter
def process(self):
    sudo_env = self.env['my.model'].sudo()
    # ... lots of code before any domain filter ...
    return sudo_env.search([])  # Accesses ALL records
```

### MEDIUM — sudo() in Wizard Method
Wizard access depends on which group can open the wizard. If `ir.model.access.csv` is too permissive, sudo() in wizards can be exploited.

### LOW — sudo() for Audit/Config Access
Generally safe but worth documenting.

```python
# LOW — reading a specific config parameter (safe, but document it)
def get_setting(self):
    return self.env['ir.config_parameter'].sudo().get_param('my.setting')
```

### OK — Known Safe Patterns
These are automatically detected and excluded from reports unless `--all` is used:
- Mail/notification sending
- Audit log writing
- Reading specific config parameters with `get_param('known.key')`
- `message_post` / `message_subscribe` calls

## Output Format

```
========================================
SUDO FINDER REPORT — my_module
========================================
Total findings: 4
  CRITICAL: 1
  HIGH: 1
  MEDIUM: 2

[CRITICAL] controllers/main.py:45
  sudo() accessing sensitive model 'sale.order' in public route method 'view_orders'
  in class 'MainController'. Unauthenticated users bypass all access controls.
  FIX: Use _document_check_access() or add domain filter scoped to current user.

[HIGH] models/my_model.py:78
  sudo() inside a loop in method 'compute_totals' (class 'MyModel').
  Each iteration re-elevates privileges unnecessarily.
  FIX: Move sudo() before loop, use read_group() or single search() with all IDs.

[MEDIUM] models/my_model.py:120
  sudo() in method 'get_config' without immediate domain filter.
  Unscoped sudo() grants access to all records without restriction.
  FIX: Add domain filters immediately after sudo() or use with_user(admin).

[MEDIUM] wizard/my_wizard.py:34
  sudo() in wizard method 'action_confirm'. Ensure wizard is only accessible
  to appropriate user groups.
  FIX: Verify ir.model.access.csv restricts wizard to appropriate groups.
```

## Secure Alternatives to sudo()

### Instead of: `self.env['res.users'].sudo().browse(user_id)`
Use: Check if current user has the permission they need directly.
```python
# Grant the permission properly via groups, not sudo()
```

### Instead of: sudo() in portal controller
Use: `_document_check_access()` from `CustomerPortal`
```python
from odoo.addons.portal.controllers.portal import CustomerPortal
try:
    order = self._document_check_access('sale.order', order_id)
except (AccessError, MissingError):
    return request.redirect('/my')
```

### Instead of: sudo() in loop
Use: Batched query before the loop
```python
all_data = self.env['model'].sudo().read_group(
    [('ref_id', 'in', self.ids)],
    ['ref_id', 'amount:sum'],
    ['ref_id']
)
data_map = {d['ref_id'][0]: d['amount'] for d in all_data}
```

### Instead of: full sudo() for single operation
Use: `with_user(specific_user)` for scoped elevation
```python
# Grant only the permissions of a specific user
admin_user = self.env.ref('base.user_admin')
result = self.env['my.model'].with_user(admin_user).search([])
```

## Running Directly

```bash
python scripts/sudo_finder.py /path/to/module
python scripts/sudo_finder.py /path/to/module --verbose
python scripts/sudo_finder.py /path/to/module --all  # Include safe patterns
python scripts/sudo_finder.py /path/to/module --json
```

---
title: 'Odoo Security'
read_only: true
type: 'command'
description: 'Comprehensive Odoo module security audit — access rules, routes, sudo, SQL injection'
argument-hint: '<module> [--severity=critical|high|medium|low] [--layer=access|routes|sudo|all]'
---

# /odoo-security

Unified security audit for Odoo modules. Scans model access rules, HTTP route authentication, sudo() privilege escalation, SQL injection risks, and record rule coverage — all in one command.

## Argument Parsing

Parse `$ARGUMENTS` for:

| Token | Type | Default | Description |
|-------|------|---------|-------------|
| First positional | path/name | _(required)_ | Module path or name |
| `--severity=` | enum | `low` | Minimum severity to report: `critical`, `high`, `medium`, `low` |
| `--layer=` | enum | `all` | Which audit layer to run: `access`, `routes`, `sudo`, `sql`, `all` |
| `--fix` | flag | off | Generate and apply safe remediations after review |
| `--json` | flag | off | Output as machine-readable JSON |

Examples of valid invocations:
```
/odoo-security my_module
/odoo-security /path/to/module --severity=high
/odoo-security my_module --layer=sudo
/odoo-security my_module --layer=access --fix
/odoo-security my_module --severity=critical --layer=routes
```

---

## Help (No Module Provided)

If `$ARGUMENTS` is empty or `--help`, display:

```
Odoo Security — Comprehensive Module Security Audit

USAGE
  /odoo-security <module> [options]

LAYERS (--layer=)
  all       Run every audit layer (default)
  access    Model access rules — ir.model.access.csv completeness
  routes    HTTP route auth, CSRF, data exposure
  sudo      .sudo() usage — privilege escalation, loops, unscoped
  sql       SQL injection — unsafe cr.execute(), string formatting in queries

SEVERITY LEVELS (--severity=)
  critical  Immediate vulnerability — fix before deployment
  high      Significant risk, likely exploitable — fix within sprint
  medium    Security weakness — fix in next release
  low       Minor improvement — fix when convenient (default threshold)

EXAMPLES
  /odoo-security my_module                        Full audit, all layers
  /odoo-security my_module --severity=high        Only HIGH+ issues
  /odoo-security my_module --layer=access --fix   Check access rules, apply fixes
  /odoo-security my_module --layer=sudo           Find risky sudo() calls
  /odoo-security my_module --layer=routes         Audit HTTP route security
  /odoo-security my_module --layer=sql            Scan for SQL injection risks

PREVIOUSLY SEPARATE COMMANDS (now unified here)
  /security-audit   -> /odoo-security --severity=<level>
  /check-access     -> /odoo-security --layer=access
  /check-routes     -> /odoo-security --layer=routes
  /find-sudo        -> /odoo-security --layer=sudo
```

---

## Severity Levels

| Severity | Weight | Meaning | Action |
|----------|--------|---------|--------|
| CRITICAL | 4 | Immediate security vulnerability | Fix before deployment |
| HIGH | 3 | Significant risk, likely exploitable | Fix within sprint |
| MEDIUM | 2 | Security weakness | Fix in next release |
| LOW | 1 | Minor improvement | Fix when convenient |

**Risk Score** (0-100) = sum of (issue_count x weight). Interpretation:
- 80-100: CRITICAL risk — deployment blocked
- 50-79: HIGH risk — immediate attention
- 25-49: MEDIUM risk — schedule fixes
- 1-24: LOW risk — minor improvements
- 0: Clean

---

## Full Audit (`--layer=all`, default)

When no `--layer` is specified, run ALL layers sequentially and produce a unified report.

### Execution Steps

1. **Validate module** — confirm `__manifest__.py` exists at the given path.
2. **Run Access Checker** — scan `models/*.py` vs `security/ir.model.access.csv`.
3. **Run Route Auditor** — scan `controllers/*.py` for `@http.route()` issues.
4. **Run Sudo Finder** — scan all `.py` files for `.sudo()` risk patterns.
5. **Run SQL Injection Scanner** — find `env.cr.execute()` with string formatting.
6. **Aggregate results** — merge issues, compute risk score, sort by severity.
7. **Apply severity filter** — if `--severity` is set, hide issues below threshold.
8. **Present unified report**.

### Report Format

```
======================================================================
  ODOO SECURITY AUDIT REPORT
======================================================================
  Module:     my_module
  Path:       /path/to/my_module
  Date:       2026-03-17 14:30:00
  Risk Score: 65/100 — Significant vulnerabilities present

  SUMMARY
  ----------------------------------------
  CRITICAL      2 issues
  HIGH          1 issue
  MEDIUM        1 issue
  LOW           0 issues
  TOTAL         4 issues

  LAYER STATUS
  ----------------------------------------
  access        3 issues
  routes        0 issues (CLEAN)
  sudo          1 issue

  ISSUES (sorted by severity)
  ======================================================================

  [CRITICAL] models/my_model.py:15
    Model 'my.model' has no access rules in ir.model.access.csv
    FIX: Add entry — access_my_model_user,my.model user,model_my_model,[group],1,1,1,0

  [HIGH] models/my_wizard.py:8
    Transient model 'my.wizard' has no access rules.
    FIX: Add entry — access_my_wizard_user,my.wizard user,model_my_wizard,[group],1,1,1,1

  ...
```

---

## Layer: Access Rules (`--layer=access`)

Scan every model defined in `models/*.py` and verify it has appropriate entries in `security/ir.model.access.csv`.

### What It Checks

**CRITICAL — Missing Model Access Rules**
Any `_name = '...'` model without a CSV entry is accessible to ALL authenticated users.

**HIGH — Missing Wizard Access Rules**
TransientModel classes without access rules allow any user to execute wizard logic.

**HIGH — Empty Group References**
CSV entries with empty `group_id:id` grant access to everyone:
```csv
# DANGEROUS — grants access to all authenticated users
access_my_model_all,my.model all,model_my_model,,1,1,1,0
```

**HIGH — Missing Multi-Company Record Rules**
Models with `company_id = fields.Many2one('res.company')` but no record rules for company isolation.

**MEDIUM — Overly Permissive Permissions**
Non-manager groups with `perm_unlink=1` (DELETE access).

**LOW — Unknown Group References**
CSV entries referencing groups not defined in the module or known Odoo base.

### model_id:id Derivation

| Model `_name` | CSV `model_id:id` |
|--------------|-------------------|
| `my.model` | `model_my_model` |
| `account.move.line` | `model_account_move_line` |

Rule: replace dots with underscores, prepend `model_`.

### Standard Access Patterns

**Internal application model:**
```csv
access_[model]_user,[model] user,model_[model],[module].group_[module]_user,1,1,1,0
access_[model]_manager,[model] manager,model_[model],[module].group_[module]_manager,1,1,1,1
```

**Portal-accessible model:**
```csv
access_[model]_user,[model] user,model_[model],[module].group_user,1,1,1,0
access_[model]_portal,[model] portal,model_[model],base.group_portal,1,0,0,0
```

**Transient (wizard) model:**
```csv
access_[wizard]_user,[wizard] user,model_[wizard],[module].group_user,1,1,1,1
```

### Auto-Fix (`--fix`)

When `--fix` is active, the AI will:
1. Scan all model definitions for missing CSV entries.
2. Generate correct CSV entries with appropriate groups based on module's group definitions.
3. Write the updated `security/ir.model.access.csv`.
4. Create multi-company record rules XML if needed.

---

## Layer: Routes (`--layer=routes`)

Audit all `@http.route()` decorators in `controllers/*.py` for authentication, CSRF, and data exposure.

### What It Checks

**CRITICAL — auth='none' Without API Key Validation**
Completely unauthenticated routes with no HMAC/API key check in the method body.

**HIGH — CSRF Disabled on User Routes**
`csrf=False` on `auth='user'` POST routes leaves users vulnerable to CSRF attacks.

**HIGH — sudo() in Public Routes Accessing Sensitive Models**
Public routes using `.sudo()` on sensitive models bypass all access controls. Sensitive models:
```
res.partner, res.users, hr.employee, hr.payslip, account.move,
account.payment, sale.order, purchase.order, stock.picking,
ir.config_parameter, ir.attachment, ir.rule, ir.model.access,
mail.message, res.partner.bank
```

**HIGH — Missing auth= Parameter**
Implicit `auth=` defaults to `'user'` but being implicit is dangerous and error-prone.

**MEDIUM — CSRF Disabled on Public POST Routes**
`csrf=False` on `auth='public'` routes.

**MEDIUM — Mixed GET/POST Methods**
Routes accepting both GET and POST violate HTTP semantics.

**LOW — Missing CORS on API Routes**
JSON API routes with `auth='none'` without explicit `cors=` configuration.

### Secure Route Patterns

**Internal user route:**
```python
@http.route('/my/data', type='http', auth='user', methods=['GET'])
def my_data(self):
    records = request.env['my.model'].search([])
    return request.render('template', {'records': records})
```

**Webhook with API key auth:**
```python
@http.route('/webhook/events', type='json', auth='none', methods=['POST'], csrf=False)
def webhook(self, **kwargs):
    api_key = request.httprequest.headers.get('X-Api-Key', '')
    if not self._validate_api_key(api_key):
        return {'error': 'Unauthorized', 'code': 401}
    return {'status': 'received'}
```

**Portal route with ownership check:**
```python
@http.route('/my/order/<int:order_id>', type='http', auth='user', website=True)
def portal_order(self, order_id, **kwargs):
    try:
        order = self._document_check_access('sale.order', order_id)
    except (AccessError, MissingError):
        return request.redirect('/my')
    return request.render('portal_template', {'order': order})
```

---

## Layer: Sudo (`--layer=sudo`)

Find all `.sudo()` calls and classify each by security risk context.

### Risk Classification

**CRITICAL — sudo() in Public/None-Auth Controller**
Unauthenticated users can access any record.
```python
@http.route('/orders', auth='public')
def orders(self):
    orders = request.env['sale.order'].sudo().search([])  # ANY order!
```
FIX: Add domain filter scoped to current user, or change `auth='user'`.

**HIGH — sudo() in Loop**
Repeated privilege escalation plus performance degradation.
```python
for record in self:
    related = self.env['related.model'].sudo().search([...])  # N calls!
```
FIX: Move sudo() before loop, use `read_group()` or single `search()` with all IDs.

**HIGH — sudo() on Sensitive Models Without Domain**
Accessing `res.users`, `hr.payslip`, `account.payment`, etc. without restriction.
FIX: Add domain filters or use proper group permissions instead.

**MEDIUM — Unscoped sudo() Without Immediate Domain**
sudo() call followed by unfiltered operations.
FIX: Add domain filters immediately after sudo().

**MEDIUM — sudo() in Wizard Method**
Risk depends on who can open the wizard via `ir.model.access.csv`.
FIX: Verify CSV restricts wizard to appropriate groups.

**LOW — sudo() for Config/Audit Access**
Generally safe (e.g., `ir.config_parameter.sudo().get_param()`).

**OK — Known Safe Patterns** (hidden unless `--all`):
- `message_post` / `message_subscribe` calls
- Mail/notification sending
- Audit log writing
- `get_param('known.key')` calls

### Secure Alternatives

| Instead of | Use |
|------------|-----|
| `env['res.users'].sudo().browse(id)` | Proper group permissions |
| sudo() in portal controller | `_document_check_access()` from CustomerPortal |
| sudo() in loop | Batched `read_group()` before the loop |
| Full sudo() for single op | `with_user(specific_user)` for scoped elevation |

---

## Layer: SQL Injection (`--layer=sql`)

Scans all Python files for unsafe SQL patterns.

### What It Detects

| Risk | Pattern | Example | Fix |
|------|---------|---------|-----|
| CRITICAL | f-string in cr.execute | `cr.execute(f"SELECT * WHERE id={val}")` | Use `cr.execute("SELECT * WHERE id=%s", (val,))` |
| CRITICAL | .format() in cr.execute | `cr.execute("...{}".format(val))` | Use parameterized `%s` |
| HIGH | String concat in cr.execute | `cr.execute("SELECT " + field)` | Whitelist field names |
| HIGH | % formatting in cr.execute | `cr.execute("... %s" % val)` | Use tuple: `(val,)` as second arg |
| MEDIUM | cr.execute without params | `cr.execute(query)` where query is variable | Ensure query is constant or parameterized |
| LOW | _where_calc override | Custom `_where_calc` without `_apply_ir_rules` | Always call `_apply_ir_rules` |

### Safe Patterns (no alert)
- `cr.execute("SELECT ... WHERE id = %s", (record_id,))` -- parameterized
- `cr.execute("SELECT ... WHERE id IN %s", (tuple(ids),))` -- tuple param
- `cr.execute(constant_query)` where query is a module-level string constant

---

## Auto-Fix Capabilities (`--fix`)

When `--fix` is specified, the AI will generate and apply safe remediations.

**Auto-applied (safe):**
- Create missing `ir.model.access.csv` entries
- Fix empty group references
- Add `groups=` to sensitive fields (salary, password, token, etc.)
- Create multi-company record rules
- Rewrite unsafe `env.cr.execute()` with parameterized queries

**Requires manual review (never auto-applied):**
- Changing `auth='public'` to `auth='user'`
- Removing `sudo()` from controllers
- Re-enabling CSRF on routes (may break integrations)

---

## CI/CD Integration

```bash
# Full audit — fail build on any issues
python scripts/security_auditor.py /path/to/module --exit-on-issues

# Only block on critical/high
python scripts/security_auditor.py /path/to/module --min-severity HIGH --exit-on-issues

# JSON report for downstream processing
python scripts/security_auditor.py /path/to/module --json --output security-report.json

# Single layer in CI
python scripts/access_checker.py /path/to/module --json
python scripts/route_auditor.py /path/to/module --json
python scripts/sudo_finder.py /path/to/module --json
```

---

## When to Run

- Before every pull request merge
- After creating a new module
- After adding controllers or models
- After modifying `ir.model.access.csv`
- As part of CI/CD pipeline

---

## AI Integration

When you run `/odoo-security`, the AI assistant will:

1. Execute the appropriate audit layers on the specified module.
2. Analyze findings in context of the Odoo version being used.
3. Prioritize issues by severity and exploitability.
4. Generate specific, production-ready remediation code for each issue.
5. If `--fix` is passed, apply safe remediations after confirmation.

The AI uses knowledge from `odoo-security/SKILL.md` and `memories/` to provide context-aware remediation that respects Odoo version-specific patterns.

---

> **Note:** This command replaces the previously separate `/security-audit`, `/check-access`, `/check-routes`, and `/find-sudo` commands. All functionality is now available through `--layer` and `--severity` flags.

---
name: odoo-security
description: "Comprehensive Odoo security auditor for model access rules, HTTP route authentication, sudo() usage, SQL injection risks, and record rule completeness across Odoo 14-19."
version: "1.0.0"
author: "TaqaTechno"
license: "MIT"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
metadata:
  mode: "codebase"
  supported-versions: ["14","15","16","17","18","19"]
  categories: [security, audit, access-control]
---

# Odoo Security Skill

You are an expert Odoo security auditor with deep knowledge of Odoo's multi-layer security model spanning versions 14 through 19. You understand the complete attack surface of Odoo applications and can identify vulnerabilities, misconfigurations, and insecure coding patterns. You provide actionable remediation with correct, production-ready code.

When invoked, you analyze Odoo module codebases systematically, produce severity-graded reports, and guide developers toward secure-by-default implementations.

---

## 1. Security Architecture — Odoo's 3-Layer Security Model

Odoo implements a defense-in-depth approach using three distinct security layers that work together. Understanding all three layers is mandatory before auditing any module.

### Layer 1: User Groups (Authentication & Authorization)

User groups are the foundation. Every action in Odoo is gated by group membership.

```xml
<!-- security/group_my_module.xml -->
<odoo>
    <data>
        <!-- Base group category -->
        <record id="module_category_my_module" model="ir.module.category">
            <field name="name">My Module</field>
            <field name="sequence">50</field>
        </record>

        <!-- User group (read + limited write) -->
        <record id="group_my_module_user" model="res.groups">
            <field name="name">User</field>
            <field name="category_id" ref="module_category_my_module"/>
            <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
        </record>

        <!-- Manager group (full access, implies user group) -->
        <record id="group_my_module_manager" model="res.groups">
            <field name="name">Manager</field>
            <field name="category_id" ref="module_category_my_module"/>
            <field name="implied_ids" eval="[(4, ref('group_my_module_user'))]"/>
            <field name="users" eval="[(4, ref('base.user_root'))]"/>
        </record>
    </data>
</odoo>
```

**Group Hierarchy Rules:**
- Every group should have a `category_id` for proper UI display in Settings
- `implied_ids` creates transitive inheritance — users in Manager automatically get User permissions
- Groups should follow the pattern: `group_[module]_[role]` (user, manager, admin)
- Never grant permissions directly to `base.group_public` for internal data

### Layer 2: Model-Level Access Control (ir.model.access)

Model access controls define CRUD permissions per group per model. Every model MUST have entries.

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
# Standard user: read, write, create — no delete
access_my_model_user,my.model user,model_my_model,group_my_module_user,1,1,1,0
# Manager: full CRUD
access_my_model_manager,my.model manager,model_my_model,group_my_module_manager,1,1,1,1
# Portal: read-only
access_my_model_portal,my.model portal,model_my_model,base.group_portal,1,0,0,0
```

**Critical Rules:**
- A model with NO access rules is accessible to ALL authenticated users (default allow)
- Transient models (wizards) need access rules too
- Inherited models (`_inherit`) that add sensitive fields need their own rules
- The `model_id:id` uses the technical name converted: `my.model` → `model_my_model`

### Layer 3: Record-Level Security (ir.rule)

Record rules filter which records a user can see/modify within an already-accessible model.

```xml
<!-- Multi-company isolation — MANDATORY for multi-company setups -->
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: Company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">
        ['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]
    </field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>

<!-- User can only see their own records -->
<record id="rule_my_model_user_own" model="ir.rule">
    <field name="name">My Model: Own Records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('group_my_module_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="False"/>
</record>

<!-- Manager sees all records -->
<record id="rule_my_model_manager_all" model="ir.rule">
    <field name="name">My Model: Manager All</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('group_my_module_manager'))]"/>
</record>
```

---

## 2. Model Access Rules — Complete Reference

### ir.model.access.csv Column Definitions

| Column | Description | Values |
|--------|-------------|--------|
| `id` | Unique XML ID for the access rule | `access_[model]_[group]` |
| `name` | Human-readable description | `[model] [group]` |
| `model_id:id` | Reference to `ir.model` | `model_[model_technical_name]` |
| `group_id:id` | Reference to `res.groups` | `module.group_name` or empty for all users |
| `perm_read` | Read permission | `1` (granted) or `0` (denied) |
| `perm_write` | Write/update permission | `1` or `0` |
| `perm_create` | Create permission | `1` or `0` |
| `perm_unlink` | Delete permission | `1` or `0` |

### Deriving model_id:id from _name

```python
# Model _name          → model_id:id
# my.model             → model_my_model
# account.move.line    → model_account_move_line
# res.partner          → model_res_partner

# Rule: replace dots with underscores, prefix with "model_"
```

### Complete Access Pattern Templates

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink

# Pattern 1: Standard internal model
access_my_model_user,my.model user,model_my_model,my_module.group_my_module_user,1,1,1,0
access_my_model_manager,my.model manager,model_my_model,my_module.group_my_module_manager,1,1,1,1

# Pattern 2: Read-only reference data (all users can read, only admin writes)
access_ref_data_user,ref.data user,model_ref_data,base.group_user,1,0,0,0
access_ref_data_manager,ref.data manager,model_ref_data,base.group_system,1,1,1,1

# Pattern 3: Transient model (wizard) — grant to same groups as main model
access_my_wizard_user,my.wizard user,model_my_wizard,my_module.group_my_module_user,1,1,1,1

# Pattern 4: Portal access — read only
access_my_model_portal,my.model portal,model_my_model,base.group_portal,1,0,0,0

# Pattern 5: Multi-company model — requires company record rules too
access_my_model_user,my.model user,model_my_model,my_module.group_my_module_user,1,1,1,0

# Pattern 6: Inherited model with added sensitive fields
# When using _inherit and adding fields that need access control,
# create a NEW model with _name set and add separate access rules
```

### Common Mistakes in Model Access

**Mistake 1: Missing access for transient models**
```python
# models/my_wizard.py
class MyWizard(models.TransientModel):
    _name = 'my.wizard'  # NEEDS entry in ir.model.access.csv!
```

**Mistake 2: Leaving group_id empty (grants access to ALL users)**
```csv
# DANGEROUS — grants access to every logged-in user
access_my_model_all,my.model all,model_my_model,,1,1,1,0
```

**Mistake 3: Wrong model_id derivation**
```csv
# WRONG
access_x,x,my.model,,1,0,0,0
# CORRECT
access_x,x,model_my_model,,1,0,0,0
```

---

## 3. User Groups — Complete Patterns

### Group Hierarchy Best Practices

```xml
<odoo>
    <data>
        <record id="module_category_my_app" model="ir.module.category">
            <field name="name">My Application</field>
            <field name="description">Manage My Application access levels</field>
            <field name="sequence">100</field>
            <field name="exclusive_ids" eval="[
                (4, ref('group_my_app_readonly')),
                (4, ref('group_my_app_user')),
                (4, ref('group_my_app_manager'))
            ]"/>
        </record>

        <!-- Read-only: Can view but not create/edit -->
        <record id="group_my_app_readonly" model="res.groups">
            <field name="name">Read Only</field>
            <field name="category_id" ref="module_category_my_app"/>
            <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
        </record>

        <!-- User: Standard operational access -->
        <record id="group_my_app_user" model="res.groups">
            <field name="name">User</field>
            <field name="category_id" ref="module_category_my_app"/>
            <field name="implied_ids" eval="[
                (4, ref('base.group_user')),
                (4, ref('group_my_app_readonly'))
            ]"/>
        </record>

        <!-- Manager: Administrative access -->
        <record id="group_my_app_manager" model="res.groups">
            <field name="name">Administrator</field>
            <field name="category_id" ref="module_category_my_app"/>
            <field name="implied_ids" eval="[
                (4, ref('group_my_app_user'))
            ]"/>
            <field name="users" eval="[(4, ref('base.user_root'))]"/>
        </record>
    </data>
</odoo>
```

### Field-Level Security with groups= Attribute

```python
class MyModel(models.Model):
    _name = 'my.model'

    # Public field — everyone can see
    name = fields.Char(string='Name', required=True)

    # Sensitive field — only managers can see/edit
    salary = fields.Float(
        string='Salary',
        groups='my_module.group_my_app_manager'
    )

    # Internal note — hidden from portal users
    internal_note = fields.Text(
        string='Internal Note',
        groups='base.group_user'
    )

    # Computed field with group restriction
    margin_percent = fields.Float(
        string='Margin %',
        compute='_compute_margin',
        groups='my_module.group_my_app_manager'
    )
```

---

## 4. Record Rules — Domain-Based Row-Level Security

### Standard Record Rule Patterns

```xml
<odoo>
    <data noupdate="1">

        <!-- Pattern 1: Multi-company isolation (REQUIRED for company_id fields) -->
        <record id="rule_my_model_multi_company" model="ir.rule">
            <field name="name">My Model: Multi-Company</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="global" eval="True"/>
            <field name="domain_force">
                ['|',
                    ('company_id', '=', False),
                    ('company_id', 'in', company_ids)
                ]
            </field>
        </record>

        <!-- Pattern 2: User can only access their own records -->
        <record id="rule_my_model_user_own" model="ir.rule">
            <field name="name">My Model: Own Records Only</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[('create_uid', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('my_module.group_my_app_user'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="False"/>
        </record>

        <!-- Pattern 3: Manager sees everything (override user restriction) -->
        <record id="rule_my_model_manager_all" model="ir.rule">
            <field name="name">My Model: Manager All Access</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[(1, '=', 1)]</field>
            <field name="groups" eval="[(4, ref('my_module.group_my_app_manager'))]"/>
        </record>

        <!-- Pattern 4: Portal users see only published/confirmed records -->
        <record id="rule_my_model_portal" model="ir.rule">
            <field name="name">My Model: Portal Published Only</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">
                [('state', 'in', ['published', 'confirmed'])]
            </field>
            <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="False"/>
            <field name="perm_create" eval="False"/>
            <field name="perm_unlink" eval="False"/>
        </record>

        <!-- Pattern 5: Salesperson sees only their team's records -->
        <record id="rule_my_model_sales_team" model="ir.rule">
            <field name="name">My Model: Sales Team</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">
                [('team_id.member_ids', 'in', [user.id])]
            </field>
            <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
        </record>

    </data>
</odoo>
```

### Record Rule Evaluation Logic

Record rules within the same group are evaluated with **OR** logic (any matching rule grants access). Rules from different groups are evaluated with **AND** logic (all matching rules must pass). This means:

- Multiple rules for the same group = broader access (OR)
- Rules for different groups = narrower access (AND intersection)
- Global rules (`<field name="global" eval="True"/>`) apply to ALL users

### When Record Rules Are Missing (Vulnerability)

A model without record rules but with model access means ANY authenticated user with the group can see ALL records — including data from other companies, other users, or sensitive records. Always add:

1. Multi-company rule if model has `company_id`
2. User-scoping rule if records are user-specific
3. State-filtering rule for portal/public access

---

## 5. HTTP Route Security — Authentication Patterns

### Route Authentication Types

```python
from odoo import http
from odoo.http import request

class MyController(http.Controller):

    # auth='user' — Requires login, redirects to /web/login if not authenticated
    # Use for: Internal backend routes, authenticated user operations
    @http.route('/my/internal/route', type='http', auth='user', methods=['GET'])
    def internal_route(self):
        # request.env.user is the authenticated user
        return request.render('my_module.template', {})

    # auth='public' — Works for both guests and logged-in users
    # Use for: Public website pages, product listings, blog posts
    # WARNING: Never expose sensitive data here
    @http.route('/my/public/route', type='http', auth='public', methods=['GET'])
    def public_route(self):
        # request.env.user = public user if not logged in
        # Check: if request.env.user._is_public(): handle guest case
        if not request.env.user._is_public():
            # Authenticated user
            pass
        return request.render('my_module.public_template', {})

    # auth='none' — No authentication at all, raw HTTP
    # Use for: Webhooks with their own auth, health checks, OAuth callbacks
    # CRITICAL: Must implement own authentication if handling sensitive data
    @http.route('/my/webhook', type='http', auth='none', methods=['POST'])
    def webhook(self, **kwargs):
        # Validate with HMAC signature, API key, or IP whitelist
        api_key = request.httprequest.headers.get('X-API-Key')
        if not self._validate_api_key(api_key):
            return request.make_response('Unauthorized', status=401)
        # Process webhook...
        return request.make_response('OK', status=200)
```

### CSRF Protection

```python
# POST routes that modify state MUST have csrf=False only for APIs/webhooks
# By default, Odoo enforces CSRF for all POST routes (good!)

# DANGEROUS — disables CSRF for a state-modifying route
@http.route('/my/action', type='http', auth='user', methods=['POST'], csrf=False)
def bad_action(self):
    pass  # This is vulnerable to CSRF attacks!

# CORRECT — keep CSRF enabled (default) for web form actions
@http.route('/my/action', type='http', auth='user', methods=['POST'])
def safe_action(self):
    pass

# ACCEPTABLE — disable CSRF only for machine-to-machine API calls with API key auth
@http.route('/api/v1/webhook', type='json', auth='none', methods=['POST'], csrf=False)
def webhook(self, **kwargs):
    # MUST validate API key here
    self._authenticate_request()
```

### JSON API Routes

```python
# For JSON APIs, use type='json' — this handles serialization and error formatting
@http.route('/api/v1/data', type='json', auth='user', methods=['POST'])
def api_data(self, **kwargs):
    # Return dict, Odoo serializes to JSON automatically
    return {'status': 'ok', 'data': []}

# Public API with API key authentication
@http.route('/api/v1/public', type='json', auth='none', methods=['POST'], csrf=False)
def public_api(self, api_key=None, **kwargs):
    if not self._validate_api_key(api_key):
        return {'error': 'Invalid API key', 'code': 401}
    # Safe to process
```

### Sensitive Data in Public Routes

```python
# VULNERABLE — exposes partner email to public
@http.route('/partners', type='http', auth='public')
def partners(self):
    partners = request.env['res.partner'].sudo().search([])
    return request.render('template', {'partners': partners})

# SECURE — only expose non-sensitive fields, respect visibility
@http.route('/partners', type='http', auth='public')
def partners(self):
    # Only published partners, only safe fields
    partners = request.env['res.partner'].sudo().search([
        ('website_published', '=', True)
    ])
    # Never pass raw recordsets with sensitive fields to public templates
    partner_data = partners.read(['name', 'website', 'country_id'])
    return request.render('template', {'partners': partner_data})
```

---

## 6. Sudo() Usage — Safe and Dangerous Patterns

### When sudo() Is Appropriate

```python
# APPROPRIATE 1: Escalating privileges to read configuration data
# User doesn't need access to system params, but the operation is safe
@api.model
def get_public_config(self):
    param = self.env['ir.config_parameter'].sudo().get_param('my.public.setting')
    return param  # Only returning a specific, safe setting

# APPROPRIATE 2: Writing to audit log (user shouldn't control their own log)
def write(self, vals):
    result = super().write(vals)
    # Log change — user shouldn't have access to audit model
    self.env['my.audit.log'].sudo().create({
        'model': self._name,
        'record_id': self.id,
        'user_id': self.env.user.id,
        'changes': str(vals),
    })
    return result

# APPROPRIATE 3: Sending notifications to users the current user can't access
def notify_admin(self):
    admin = self.env.ref('base.user_admin').sudo()
    admin.notify_warning('Alert', 'Something happened')

# APPROPRIATE 4: Computing fields that aggregate data across companies
@api.depends('order_ids')
def _compute_total_orders(self):
    for rec in self:
        rec.order_count = self.env['sale.order'].sudo().search_count([
            ('partner_id', '=', rec.id)
        ])
```

### When sudo() Is DANGEROUS

```python
# DANGEROUS 1: sudo() in a public/portal controller
# Bypasses ALL access controls — user can access any record by ID
@http.route('/order/<int:order_id>', auth='public')
def view_order(self, order_id):
    # VULNERABLE TO IDOR — anyone can access any order ID
    order = request.env['sale.order'].sudo().browse(order_id)
    return request.render('template', {'order': order})

# SECURE VERSION — verify ownership before accessing
@http.route('/order/<int:order_id>', auth='user')
def view_order(self, order_id):
    order = request.env['sale.order'].browse(order_id)
    # ORM access controls apply — user can only see their orders
    if not order.exists():
        raise request.not_found()
    return request.render('template', {'order': order})

# DANGEROUS 2: sudo() in a loop
def process_all(self):
    for record in self.search([]):  # Could be thousands of records
        # sudo() call inside loop = performance issue + security concern
        sensitive = self.env['sensitive.model'].sudo().search([
            ('ref_id', '=', record.id)
        ])
        record.result = len(sensitive)

# SECURE VERSION — batch the sudo() outside the loop
def process_all(self):
    all_records = self.search([])
    # Single sudo() query outside loop
    sensitive_data = self.env['sensitive.model'].sudo().read_group(
        [('ref_id', 'in', all_records.ids)],
        ['ref_id'],
        ['ref_id']
    )
    count_map = {d['ref_id'][0]: d['ref_id_count'] for d in sensitive_data}
    for record in all_records:
        record.result = count_map.get(record.id, 0)

# DANGEROUS 3: Passing sudo env to user-controlled operations
def dangerous_search(self, domain):
    # User provides domain — they could access ANY record
    sudo_env = self.env['my.model'].sudo()
    return sudo_env.search(domain)  # User controls domain!

# SECURE VERSION — always apply fixed safety constraints
def safe_search(self, user_domain):
    # Sanitize and constrain the domain
    safe_domain = [
        ('partner_id', '=', self.env.user.partner_id.id),  # Fixed constraint
    ] + user_domain  # Append user's additional filters
    return self.env['my.model'].search(safe_domain)  # No sudo()

# DANGEROUS 4: sudo() in onchange (exposes data in UI)
@api.onchange('partner_id')
def _onchange_partner_id(self):
    # sudo() in onchange means ANY user can see ALL partner data
    all_orders = self.env['sale.order'].sudo().search([
        ('partner_id', '=', self.partner_id.id)
    ])
    self.order_count = len(all_orders)
```

### Scoped sudo() with Specific User

```python
# Instead of full sudo(), use a specific user's environment
# This gives exactly the permissions of that user, not root

# Get sudo environment for the admin user only
admin_user = self.env.ref('base.user_admin')
admin_env = self.env['my.model'].with_user(admin_user)

# Or use with_context to pass additional context
elevated_env = self.env['my.model'].with_context(
    no_check=True,  # Only if the model respects this context key
    force_company=self.company_id.id
)
```

---

## 7. SQL Injection Prevention

### Parameterized Queries (Always Required)

```python
# VULNERABLE — string concatenation with user input
def vulnerable_search(self, name):
    query = "SELECT id FROM res_partner WHERE name = '%s'" % name
    self.env.cr.execute(query)  # SQL INJECTION RISK!
    return self.env.cr.fetchall()

# SECURE — parameterized query (tuple format)
def safe_search(self, name):
    query = "SELECT id FROM res_partner WHERE name = %s"
    self.env.cr.execute(query, (name,))  # Parameters passed separately
    return self.env.cr.fetchall()

# VULNERABLE — f-string in SQL
def vulnerable_f(self, table, field):
    query = f"SELECT {field} FROM {table}"  # INJECTION RISK!
    self.env.cr.execute(query)

# SECURE — use psycopg2.sql for dynamic identifiers
from psycopg2 import sql

def safe_dynamic(self, field_name):
    # Use sql.Identifier for table/column names (NOT string format)
    query = sql.SQL("SELECT {} FROM res_partner LIMIT 10").format(
        sql.Identifier(field_name)
    )
    self.env.cr.execute(query)
    return self.env.cr.fetchall()

# SECURE — ORM domain for user-provided filters (preferred over raw SQL)
def orm_search(self, partner_name):
    # ORM handles escaping automatically
    return self.env['res.partner'].search([('name', 'ilike', partner_name)])
```

### Safe Raw SQL Patterns

```python
# SECURE — multiple parameters
def get_partner_orders(self, partner_id, state, date_from):
    query = """
        SELECT so.id, so.name, so.amount_total
        FROM sale_order so
        WHERE so.partner_id = %s
          AND so.state = %s
          AND so.date_order >= %s
        ORDER BY so.date_order DESC
        LIMIT 100
    """
    self.env.cr.execute(query, (partner_id, state, date_from))
    return self.env.cr.dictfetchall()

# SECURE — IN clause with list (psycopg2 handles tuple expansion)
def get_orders_by_ids(self, order_ids):
    if not order_ids:
        return []
    query = "SELECT id, name FROM sale_order WHERE id IN %s"
    self.env.cr.execute(query, (tuple(order_ids),))
    return self.env.cr.fetchall()

# SECURE — LIKE pattern with escaping
def search_by_prefix(self, prefix):
    # % must be escaped in parameterized queries using %%
    query = "SELECT id FROM res_partner WHERE name ILIKE %s"
    self.env.cr.execute(query, (prefix + '%',))
    return self.env.cr.fetchall()
```

---

## 8. Field-Level Security

### groups= Attribute on Field Definitions

```python
class Employee(models.Model):
    _inherit = 'hr.employee'

    # Visible to all HR users
    name = fields.Char()

    # Only HR managers can see salary information
    wage = fields.Float(
        groups='hr.group_hr_manager'
    )

    # Only accessible via HR admin (payroll group)
    ssnid = fields.Char(
        string='SSN',
        groups='hr.group_hr_user'  # Still too broad — consider more restrictive
    )

    # Computed field with group restriction
    contract_count = fields.Integer(
        compute='_compute_contract_count',
        groups='hr.group_hr_manager'
    )

    # Multiple groups (OR logic — either group grants access)
    sensitive_field = fields.Text(
        groups='my_module.group_hr_manager,base.group_system'
    )
```

### View-Level Field Hiding

```xml
<!-- Hide field in view for non-managers (defense in depth) -->
<field name="salary" groups="my_module.group_my_app_manager"/>

<!-- Show different fields based on group -->
<field name="public_notes"/>
<field name="private_notes" groups="my_module.group_my_app_manager"/>

<!-- Entire section hidden from non-managers -->
<group string="Financials" groups="account.group_account_manager">
    <field name="revenue"/>
    <field name="cost"/>
    <field name="margin"/>
</group>
```

---

## 9. Portal Security Patterns

### Secure Portal Controller

```python
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError


class MyPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'my_model_count' in counters:
            values['my_model_count'] = request.env['my.model'].search_count(
                self._get_my_model_domain()
            )
        return values

    def _get_my_model_domain(self):
        """Return domain that limits portal access to current user's records only."""
        return [('partner_id', '=', request.env.user.partner_id.id)]

    @http.route(['/my/orders', '/my/orders/page/<int:page>'],
                type='http', auth='user', website=True)
    def portal_my_orders(self, page=1, **kwargs):
        # SECURE — domain always scoped to current user
        domain = self._get_my_model_domain()
        total = request.env['my.model'].search_count(domain)

        pager = portal_pager(
            url='/my/orders',
            total=total,
            page=page,
            step=10
        )

        orders = request.env['my.model'].search(
            domain,
            limit=10,
            offset=pager['offset']
        )

        return request.render('my_module.portal_orders', {
            'orders': orders,
            'pager': pager,
        })

    @http.route('/my/order/<int:order_id>', type='http', auth='user', website=True)
    def portal_order_detail(self, order_id, **kwargs):
        # SECURE — use _document_check_access to verify ownership
        try:
            order = self._document_check_access('my.model', order_id)
        except (AccessError, MissingError):
            return request.redirect('/my/orders')
        return request.render('my_module.portal_order_detail', {'order': order})
```

### _document_check_access Implementation

```python
# This method (from CustomerPortal) verifies:
# 1. Record exists
# 2. Current user has access rights to it
# 3. Optional: token-based access for share links
# Always use this instead of sudo().browse() in portal controllers
```

---

## 10. API Security Patterns

### API Key Authentication

```python
class ApiController(http.Controller):

    def _get_api_key_user(self, api_key):
        """Validate API key and return associated user or None."""
        if not api_key:
            return None
        # Store API keys in a secure model with hashed values
        key_record = request.env['my.api.key'].sudo().search([
            ('key_hash', '=', hashlib.sha256(api_key.encode()).hexdigest()),
            ('active', '=', True),
        ], limit=1)
        if not key_record or key_record.is_expired():
            return None
        return key_record.user_id

    @http.route('/api/v1/resource', type='json', auth='none', csrf=False)
    def api_resource(self, **kwargs):
        api_key = request.httprequest.headers.get('X-Api-Key', '')
        user = self._get_api_key_user(api_key)
        if not user:
            return {'error': 'Unauthorized', 'code': 401}

        # Switch to the API key user's environment (respects their permissions)
        env = request.env(user=user.id)
        records = env['my.model'].search([])
        return {'data': records.read(['name', 'state'])}
```

### Rate Limiting Pattern

```python
import time
from collections import defaultdict

class RateLimiter:
    """Simple in-memory rate limiter — use Redis in production."""
    _requests = defaultdict(list)

    @classmethod
    def is_allowed(cls, key, limit=60, window=60):
        now = time.time()
        cls._requests[key] = [t for t in cls._requests[key] if now - t < window]
        if len(cls._requests[key]) >= limit:
            return False
        cls._requests[key].append(now)
        return True

class ApiController(http.Controller):
    @http.route('/api/v1/data', type='json', auth='none', csrf=False)
    def api_data(self, **kwargs):
        client_ip = request.httprequest.remote_addr
        if not RateLimiter.is_allowed(client_ip, limit=60, window=60):
            return {'error': 'Rate limit exceeded', 'code': 429}
        # Process request...
```

---

## 11. Common Vulnerabilities — Top 10 Odoo Security Mistakes

### 1. Missing ir.model.access.csv (CRITICAL)

**Risk**: Every authenticated user can read/write ALL records of the model.
**Detection**: Run `access_checker.py` — finds models with no access rules.
**Fix**: Create complete `security/ir.model.access.csv` with entries for all defined models.

### 2. auth='none' on Data Routes (CRITICAL)

**Risk**: Unauthenticated access to sensitive business data.
**Detection**: Run `route_auditor.py` — flags `auth='none'` without justification.
**Fix**: Use `auth='user'` for internal routes, implement API key auth for `auth='none'` webhooks.

### 3. IDOR (Insecure Direct Object Reference) (HIGH)

**Risk**: Integer IDs are sequential — attackers enumerate IDs to access other users' records.
**Detection**: Public routes accepting `<int:id>` parameters with sudo() access.
**Fix**: Use `_document_check_access()`, verify `partner_id == request.env.user.partner_id.id`.

### 4. SQL Injection via env.cr.execute() (HIGH)

**Risk**: String concatenation with user input leads to data theft or destruction.
**Detection**: Run grep for `env.cr.execute` + string formatting nearby.
**Fix**: Always use parameterized queries: `self.env.cr.execute(query, (param,))`.

### 5. sudo() Privilege Escalation in Controllers (HIGH)

**Risk**: sudo() in public routes bypasses all access controls.
**Detection**: Run `sudo_finder.py` — finds sudo() in public/portal methods.
**Fix**: Use user-scoped environments, verify ownership before access.

### 6. Missing Multi-Company Record Rules (HIGH)

**Risk**: Users in company A can see/modify data from company B.
**Detection**: Models with `company_id` field but no multi-company record rule.
**Fix**: Add `['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]` rule.

### 7. Missing CSRF on State-Changing Routes (MEDIUM)

**Risk**: Malicious websites can trigger actions as the authenticated user.
**Detection**: POST routes with `csrf=False` that modify data.
**Fix**: Remove `csrf=False` from web routes (only use for machine-to-machine APIs).

### 8. Sensitive Fields Without groups= (MEDIUM)

**Risk**: Salary, SSN, passwords visible to all users who can access the model.
**Detection**: Look for fields named `salary`, `password`, `token`, `ssn`, `secret` without `groups=`.
**Fix**: Add `groups='my_module.group_manager'` to sensitive field definitions.

### 9. sudo() in Loops (MEDIUM)

**Risk**: Performance degradation + security — each iteration re-escalates privileges unnecessarily.
**Detection**: Run `sudo_finder.py` — finds `.sudo()` inside `for` loops.
**Fix**: Move sudo() call before loop, batch the query.

### 10. Overly Permissive Record Rules (LOW)

**Risk**: Users can access records they shouldn't (e.g., other departments' data).
**Detection**: Record rules with `(1, '=', 1)` domain for non-manager groups.
**Fix**: Add appropriate filters — company, user, team, or state constraints.

---

## 12. Audit Commands — How to Use Each Command

### /odoo-security — Full Module Security Audit

```bash
# Run complete security audit on a module
/odoo-security /path/to/odoo17/projects/my_project/my_module

# What it checks:
# - Model access rules completeness
# - HTTP route authentication
# - sudo() usage safety
# - SQL injection risks
# - Record rule coverage
# - Field-level security on sensitive fields

# Output format:
# [CRITICAL] Model 'my.model' has no access rules in ir.model.access.csv
# [HIGH]     Route /api/data uses auth='none' without API key validation
# [HIGH]     sudo() found in public controller method view_order (line 45)
# [MEDIUM]   Field 'salary' has no groups= restriction
# [LOW]      Record rule allows all users to see all records

# Exit codes:
# 0 = No issues found
# 1 = Issues found (check report for details)
```

### /security-audit — Targeted Module Audit

```bash
# Audit specific module with verbose output
/security-audit my_module_name

# Useful for CI/CD integration — fails build on CRITICAL/HIGH issues
```

### /check-access — Model Access Rule Checker

```bash
# Check access rules for all models in a module
/check-access /path/to/module

# Example output:
# Scanning models in: /path/to/module/models/
# Found 5 model definitions:
#   my.model       -> [CRITICAL] NO ACCESS RULES DEFINED
#   my.wizard      -> [HIGH] Wizard has no access rules
#   my.category    -> [OK] 2 rules found
#   my.tag         -> [OK] 2 rules found
#   my.config      -> [MEDIUM] Only admin group, missing user group
```

### /find-sudo — sudo() Usage Scanner

```bash
# Find all sudo() calls and classify by risk
/find-sudo /path/to/module

# Example output:
# controllers/main.py:45  [CRITICAL] sudo() in auth='public' route
# models/my_model.py:123  [HIGH]     sudo() inside for loop
# models/my_model.py:89   [OK]       sudo() for audit log write (safe pattern)
# wizards/my_wizard.py:34 [MEDIUM]   Unscoped sudo() — consider with_user()
```

### /check-routes — HTTP Route Security Scanner

```bash
# Audit all HTTP routes in controllers/
/check-routes /path/to/module

# Example output:
# controllers/main.py:
#   GET  /my/public    auth='public'  [OK]
#   POST /my/action    auth='user'    [OK]
#   POST /api/webhook  auth='none'    [CRITICAL] No API key validation found
#   GET  /data         auth='public'  [HIGH] Reads sensitive model without filtering
```

---

## 13. Remediation Patterns — How to Fix Each Issue

### Fix: Missing Model Access Rules

```bash
# 1. Identify models without access rules
python scripts/access_checker.py /path/to/module

# 2. Create or update security/ir.model.access.csv
```

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model user,model_my_model,my_module.group_my_module_user,1,1,1,0
access_my_model_manager,my.model manager,model_my_model,my_module.group_my_module_manager,1,1,1,1
```

```python
# 3. Add to __manifest__.py data list
'data': [
    'security/group_my_module.xml',
    'security/ir.model.access.csv',  # Must come AFTER group definitions
    'security/rules_my_module.xml',
    ...
]
```

### Fix: Insecure Route Authentication

```python
# BEFORE (CRITICAL)
@http.route('/sensitive/data', type='json', auth='none')
def get_data(self):
    return request.env['sensitive.model'].sudo().search_read([])

# AFTER (SECURE)
@http.route('/sensitive/data', type='json', auth='user')
def get_data(self):
    # Now request.env automatically scoped to authenticated user
    return request.env['sensitive.model'].search_read([])
```

### Fix: IDOR in Portal Routes

```python
# BEFORE (VULNERABLE)
@http.route('/order/<int:order_id>', auth='public')
def view_order(self, order_id):
    order = request.env['sale.order'].sudo().browse(order_id)
    return request.render('template', {'order': order})

# AFTER (SECURE)
@http.route('/order/<int:order_id>', auth='user', website=True)
def view_order(self, order_id):
    from odoo.exceptions import AccessError, MissingError
    try:
        order = self._document_check_access('sale.order', order_id)
    except (AccessError, MissingError):
        return request.redirect('/my/orders')
    return request.render('template', {'order': order})
```

### Fix: SQL Injection

```python
# BEFORE (VULNERABLE)
def search_orders(self, status):
    query = "SELECT id FROM sale_order WHERE state = '%s'" % status
    self.env.cr.execute(query)
    return self.env.cr.fetchall()

# AFTER (SECURE)
def search_orders(self, status):
    query = "SELECT id FROM sale_order WHERE state = %s"
    self.env.cr.execute(query, (status,))  # Tuple with trailing comma!
    return self.env.cr.fetchall()
```

### Fix: sudo() in Public Controller

```python
# BEFORE (CRITICAL)
@http.route('/products', auth='public')
def products(self):
    products = request.env['product.template'].sudo().search([])
    return request.render('template', {'products': products})

# AFTER (SECURE)
@http.route('/products', auth='public')
def products(self):
    # Only show published products, use sudo only for the published filter
    products = request.env['product.template'].sudo().search([
        ('website_published', '=', True),
        ('sale_ok', '=', True),
    ])
    # Restrict fields returned to non-sensitive data
    product_data = products.read(['name', 'description_sale', 'list_price', 'image_128'])
    return request.render('template', {'products': product_data})
```

### Fix: sudo() in Loop

```python
# BEFORE (MEDIUM — performance + security)
def compute_totals(self):
    for record in self:
        related = self.env['related.model'].sudo().search([
            ('record_id', '=', record.id)
        ])
        record.total = sum(related.mapped('amount'))

# AFTER (SECURE + PERFORMANT)
def compute_totals(self):
    # Single sudo() query outside loop
    related_data = self.env['related.model'].sudo().read_group(
        [('record_id', 'in', self.ids)],
        ['record_id', 'amount:sum'],
        ['record_id']
    )
    totals = {d['record_id'][0]: d['amount'] for d in related_data}
    for record in self:
        record.total = totals.get(record.id, 0.0)
```

### Fix: Missing Multi-Company Record Rule

```xml
<!-- BEFORE: No record rule = all users in all companies can see all records -->
<!-- AFTER: Add to security/rules_my_module.xml -->
<record id="rule_my_model_multi_company" model="ir.rule">
    <field name="name">My Model: Multi-Company Access</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="global" eval="True"/>
    <field name="domain_force">
        ['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]
    </field>
</record>
```

### Fix: Sensitive Field Without Group Restriction

```python
# BEFORE (MEDIUM)
class Employee(models.Model):
    _inherit = 'hr.employee'
    salary_override = fields.Float(string='Special Salary')

# AFTER (SECURE)
class Employee(models.Model):
    _inherit = 'hr.employee'
    salary_override = fields.Float(
        string='Special Salary',
        groups='hr.group_hr_manager'  # Only HR managers can see/edit
    )
```

---

## 14. Security Checklist for Code Review

Use this checklist when reviewing any Odoo module pull request:

### Models Checklist
- [ ] Every `_name` definition has entries in `ir.model.access.csv`
- [ ] Transient models (wizards) have access rules
- [ ] Models with `company_id` have multi-company record rules
- [ ] Record rules scope access appropriately (not overly permissive)
- [ ] Sensitive fields have `groups=` restriction
- [ ] `_sql_constraints` used for uniqueness (not just Python constraints)

### Controllers Checklist
- [ ] Every route has explicit `auth=` parameter
- [ ] No `auth='none'` routes without API key/HMAC validation
- [ ] POST routes that modify state have CSRF enabled (no `csrf=False`)
- [ ] Portal routes use `_document_check_access()` for record access
- [ ] Public routes don't expose sensitive model data
- [ ] User-provided IDs are validated against current user's accessible records

### Python Code Checklist
- [ ] No string formatting/f-strings in `env.cr.execute()` calls
- [ ] All raw SQL uses parameterized queries
- [ ] `sudo()` calls have documented justification in comment
- [ ] No `sudo()` inside `for` loops
- [ ] No `sudo()` in public/portal controllers without domain scoping

### Security Files Checklist
- [ ] `security/` directory exists with required files
- [ ] Group XML file defines category and group hierarchy
- [ ] `ir.model.access.csv` has all required access rules
- [ ] Record rules file exists for models needing row-level security
- [ ] All security files listed in `__manifest__.py` data list in correct order

---

## 15. Integration with CI/CD

### GitHub Actions Security Gate

```yaml
# .github/workflows/security-check.yml
name: Odoo Security Audit

on: [push, pull_request]

jobs:
  security-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Run Security Audit
        run: |
          python .claude-plugins/odoo-security/scripts/security_auditor.py \
            ./projects/my_project/my_module \
            --min-severity HIGH \
            --exit-on-issues
        # Exit code 1 = issues found = build fails

      - name: Upload Security Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: security-report.json
```

### Pre-commit Hook Integration

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run security audit on changed modules
CHANGED_MODULES=$(git diff --cached --name-only | grep -E '^projects/' | \
    sed 's|/.*||' | sort -u)

for MODULE in $CHANGED_MODULES; do
    echo "Running security audit on $MODULE..."
    python /path/to/security_auditor.py "$MODULE" --min-severity CRITICAL
    if [ $? -ne 0 ]; then
        echo "CRITICAL security issues found in $MODULE. Commit blocked."
        exit 1
    fi
done

exit 0
```

---

## 16. Odoo Version-Specific Security Notes

### Odoo 14
- `auth_jwt` module not available natively — use custom API key implementation
- `website.http_routing_map` slower — cached routes need security review
- `mail.thread` access rules inherited but worth verifying

### Odoo 15
- Introduction of `website.auth_signup_token` for secure registration links
- Enhanced portal security with stronger token validation
- Multi-website record rules became more important

### Odoo 16
- `ir.http._auth_method_public()` refactored — custom auth methods need updating
- `website.route.security` group added for route-level security
- JSON API routes improved error handling (don't expose stack traces in production)

### Odoo 17
- New `_check_access()` method replaces some manual access checks
- Improved `check_access_rights()` and `check_access_rule()` APIs
- `env.user._is_internal()` / `env.user._is_public()` / `env.user._is_portal()` helpers
- Webhook security improvements with signature verification helpers

### Odoo 18
- OAuth 2.0 integration improvements — verify token validation in custom OAuth routes
- Enhanced attachment security — check `access_token` handling
- Two-factor authentication API expanded

### Odoo 19
- REST API framework introduced — use built-in auth decorators
- Improved rate limiting primitives in core
- Enhanced field-level encryption support for PII data

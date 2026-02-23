# Odoo Security Patterns Memory

This file contains the most important security patterns, ranked by severity, with detection commands and remediation code. Reference this when auditing or reviewing Odoo modules.

---

## CRITICAL: Missing ir.model.access.csv Entry

**Description**: Every Odoo model defined with `_name = 'some.model'` MUST have at least one entry in `security/ir.model.access.csv`. Without it, ALL authenticated users can read, write, create, and delete ALL records of that model — regardless of their role.

**Why Critical**: This is the most common Odoo security mistake. It effectively makes the model's data public to all logged-in users, including portal users in some cases.

**Detection Command**:
```bash
python scripts/access_checker.py /path/to/module
# or search manually:
grep -r "_name\s*=\s*'" models/ | grep -v "inherit"
# Then verify each _name value appears in security/ir.model.access.csv
```

**Detection Pattern**: Model name in Python → derives to CSV model_id
```
my.model          → model_my_model
account.move.line → model_account_move_line
```

**Remediation Code**:
```csv
# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink

# Standard pattern: users can create/edit but not delete
access_my_model_user,my.model user,model_my_model,my_module.group_my_module_user,1,1,1,0

# Managers have full access including delete
access_my_model_manager,my.model manager,model_my_model,my_module.group_my_module_manager,1,1,1,1

# For TransientModel (wizard) — users need full CRUD for wizard lifecycle
access_my_wizard_user,my.wizard user,model_my_wizard,my_module.group_my_module_user,1,1,1,1
```

**Also Required in __manifest__.py**:
```python
'data': [
    'security/group_my_module.xml',  # Must be BEFORE ir.model.access.csv
    'security/ir.model.access.csv',  # Access rules
    'security/rules_my_module.xml',  # Record rules
    'views/my_module_views.xml',
],
```

---

## CRITICAL: auth='none' on Data Route

**Description**: Routes with `auth='none'` receive no authentication from Odoo. If the handler doesn't implement its own authentication (API key, HMAC, etc.), anyone on the internet can access the route — including from bots.

**Why Critical**: Completely bypasses Odoo's authentication layer. Any data returned or action taken is available without credentials.

**Detection Command**:
```bash
python scripts/route_auditor.py /path/to/module
# or search manually:
grep -rn "auth=['\"]none['\"]" controllers/
```

**VULNERABLE Pattern**:
```python
# Anyone can call this — no authentication at all
@http.route('/my/data', type='json', auth='none', csrf=False)
def get_data(self, **kwargs):
    records = request.env['my.model'].sudo().search_read([])
    return {'data': records}
```

**Remediation Code** (API Key Authentication):
```python
import hashlib
import hmac
import time

@http.route('/my/data', type='json', auth='none', csrf=False)
def get_data(self, **kwargs):
    # Validate API key from header
    api_key = request.httprequest.headers.get('X-Api-Key', '').strip()
    if not api_key or not self._validate_api_key(api_key):
        return {'error': 'Unauthorized', 'code': 401}

    # Safe to process — API key is validated
    records = request.env['my.model'].sudo().search_read([
        ('active', '=', True)
    ], fields=['name', 'state'])
    return {'data': records}

def _validate_api_key(self, provided_key):
    """Validate API key against database-stored hash."""
    key_hash = hashlib.sha256(provided_key.encode()).hexdigest()
    valid_key = request.env['my.api.key'].sudo().search([
        ('key_hash', '=', key_hash),
        ('active', '=', True),
    ], limit=1)
    if not valid_key:
        return False
    if valid_key.expiry_date and valid_key.expiry_date < fields.Datetime.now():
        return False
    return True
```

**Alternative** — Change to `auth='user'` if the route is for internal use:
```python
@http.route('/my/data', type='json', auth='user')
def get_data(self, **kwargs):
    # request.env is automatically scoped to authenticated user
    records = request.env['my.model'].search_read([])
    return {'data': records}
```

---

## HIGH: Unsanitized env.cr.execute()

**Description**: Using Python string formatting (%, f-strings, .format()) to build SQL queries with user input is SQL injection. Attackers can read arbitrary data, modify records, or drop tables.

**Why High**: SQL injection can expose ALL data in the database, bypass all access controls, and potentially destroy data.

**Detection Command**:
```bash
python scripts/route_auditor.py /path/to/module  # Detects in controllers
# Manual search:
grep -rn "cr\.execute" models/ controllers/ | grep -v "\.py:#"
# Then review each line for string formatting
```

**VULNERABLE Patterns**:
```python
# INJECTION 1: % operator
query = "SELECT id FROM res_partner WHERE name = '%s'" % user_input
self.env.cr.execute(query)

# INJECTION 2: f-string
query = f"SELECT id FROM res_partner WHERE name = '{user_input}'"
self.env.cr.execute(query)

# INJECTION 3: .format()
query = "SELECT id FROM res_partner WHERE state = '{}'".format(state)
self.env.cr.execute(query)

# INJECTION 4: string concatenation
query = "SELECT id FROM res_partner WHERE name = '" + name + "'"
self.env.cr.execute(query)
```

**Remediation Code** — Parameterized queries (ALWAYS use this):
```python
# SAFE 1: Single parameter
def search_by_name(self, name):
    query = "SELECT id, name FROM res_partner WHERE name = %s"
    self.env.cr.execute(query, (name,))  # Note: tuple with trailing comma!
    return self.env.cr.dictfetchall()

# SAFE 2: Multiple parameters
def get_orders(self, partner_id, state, date_from):
    query = """
        SELECT so.id, so.name, so.amount_total
        FROM sale_order so
        WHERE so.partner_id = %s
          AND so.state = %s
          AND so.date_order >= %s
        ORDER BY so.date_order DESC
    """
    self.env.cr.execute(query, (partner_id, state, date_from))
    return self.env.cr.dictfetchall()

# SAFE 3: IN clause with tuple
def get_by_ids(self, record_ids):
    if not record_ids:
        return []
    query = "SELECT id, name FROM my_model WHERE id IN %s"
    self.env.cr.execute(query, (tuple(record_ids),))
    return self.env.cr.fetchall()

# SAFE 4: Dynamic column/table names (use psycopg2.sql)
from psycopg2 import sql
def get_field(self, field_name):
    query = sql.SQL("SELECT {} FROM res_partner").format(
        sql.Identifier(field_name)
    )
    self.env.cr.execute(query)
    return self.env.cr.fetchall()

# PREFERRED: Use ORM when possible (handles escaping automatically)
def search_by_name_orm(self, name):
    return self.env['res.partner'].search([('name', 'ilike', name)])
```

---

## HIGH: sudo() in Public Controller

**Description**: Using `.sudo()` in a controller route with `auth='public'` or `auth='none'` means unauthenticated users can trigger elevated privilege operations. Combined with a record ID parameter, this is IDOR (Insecure Direct Object Reference).

**Why High**: Bypasses ALL model-level access controls. Attackers can enumerate integer IDs to access any record.

**Detection Command**:
```bash
python scripts/sudo_finder.py /path/to/module
# Manual detection:
grep -rn "\.sudo()" controllers/ | grep -v "\.py:#"
# Then check if surrounding route decorator has auth='public' or auth='none'
```

**VULNERABLE Pattern** — IDOR via sudo + public route:
```python
# Anyone can access ANY order by guessing the integer ID
@http.route('/order/<int:order_id>', type='http', auth='public')
def view_order(self, order_id):
    order = request.env['sale.order'].sudo().browse(order_id)
    return request.render('template', {'order': order})
```

**Remediation Code** — Use _document_check_access:
```python
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal

class MyPortalController(CustomerPortal):
    @http.route('/order/<int:order_id>', type='http', auth='user', website=True)
    def view_order(self, order_id, **kwargs):
        # _document_check_access verifies:
        # 1. Record exists
        # 2. Current user has read access
        # 3. Optionally validates access_token for sharing
        try:
            order = self._document_check_access('sale.order', order_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render('my_module.portal_order', {'order': order})
```

**Alternative** — Domain-scoped sudo for public listing:
```python
@http.route('/products', type='http', auth='public', website=True)
def products(self):
    # sudo() is acceptable here ONLY because:
    # 1. We have a fixed domain filter (website_published=True)
    # 2. We only read non-sensitive data
    # 3. The domain cannot be manipulated by the user
    products = request.env['product.template'].sudo().search([
        ('website_published', '=', True),
        ('sale_ok', '=', True),
    ])
    # Never pass full recordset to template if it contains sensitive fields
    product_data = products.read(['name', 'list_price', 'description_sale'])
    return request.render('template', {'products': product_data})
```

---

## HIGH: No Record Rules for Multi-Company Models

**Description**: Models with a `company_id` field but no multi-company record rules allow users from company A to see and modify records from company B. In multi-company setups, this is a critical data isolation failure.

**Why High**: Can cause data leakage between companies, regulatory compliance failures, and business logic corruption.

**Detection Command**:
```bash
# Find models with company_id but no rules XML
grep -rn "company_id.*Many2one.*res.company" models/
ls security/rules_*.xml  # Should exist if company_id found
python scripts/access_checker.py /path/to/module  # Detects this automatically
```

**Remediation Code** — Multi-company record rules:
```xml
<!-- security/rules_my_module.xml -->
<odoo>
    <data noupdate="1">

        <!-- Global rule — applies to ALL users (no groups= means everyone) -->
        <record id="rule_my_model_company" model="ir.rule">
            <field name="name">My Model: Multi-Company Access</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="global" eval="True"/>
            <!-- '|' means OR: company_id is False (shared) OR in user's companies -->
            <field name="domain_force">
                ['|',
                    ('company_id', '=', False),
                    ('company_id', 'in', company_ids)
                ]
            </field>
        </record>

        <!-- If model has both company_id and user_id, add user scoping for non-managers -->
        <record id="rule_my_model_user" model="ir.rule">
            <field name="name">My Model: User Access</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">
                ['|',
                    ('user_id', '=', False),
                    ('user_id', '=', user.id)
                ]
            </field>
            <field name="groups" eval="[(4, ref('my_module.group_my_module_user'))]"/>
        </record>

        <!-- Manager sees all records within their company -->
        <record id="rule_my_model_manager" model="ir.rule">
            <field name="name">My Model: Manager All Records</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[(1, '=', 1)]</field>
            <field name="groups" eval="[(4, ref('my_module.group_my_module_manager'))]"/>
        </record>

    </data>
</odoo>
```

---

## MEDIUM: Fields Without groups= for Sensitive Data

**Description**: Sensitive fields (salary, password, SSN, tokens, bank details) that don't have a `groups=` attribute are visible to all users who can access the model.

**Why Medium**: Information disclosure. Less severe than access rule gaps but can expose PII, financial data, or credentials.

**Detection Command**:
```bash
# Search for common sensitive field names without groups=
grep -rn "salary\|password\|token\|secret\|ssn\|iban\|bank" models/ \
    | grep "fields\." | grep -v "groups="
```

**Remediation Code**:
```python
class Employee(models.Model):
    _inherit = 'hr.employee'

    # BEFORE (all users can see)
    salary_exception = fields.Float(string='Special Salary')
    api_token = fields.Char(string='API Token')
    ssn = fields.Char(string='Social Security Number')

    # AFTER (restricted to appropriate groups)
    salary_exception = fields.Float(
        string='Special Salary',
        groups='hr.group_hr_manager'
    )
    api_token = fields.Char(
        string='API Token',
        groups='base.group_system'  # Only admin can see
    )
    ssn = fields.Char(
        string='Social Security Number',
        groups='hr.group_hr_manager'  # Only HR managers
    )
```

**Also restrict in views** (defense in depth):
```xml
<field name="salary_exception" groups="hr.group_hr_manager"/>
<field name="api_token" groups="base.group_system"/>
```

---

## MEDIUM: sudo() in Loop

**Description**: Calling `.sudo()` inside a `for` loop creates N database calls and unnecessarily re-elevates privileges on each iteration. This is both a performance issue and a code smell that often indicates access control is being bypassed incorrectly.

**Why Medium**: Performance degradation (N+1 query), plus unnecessary repeated privilege escalation increases attack surface.

**Detection Command**:
```bash
python scripts/sudo_finder.py /path/to/module
# or manually review:
grep -rn "\.sudo()" models/ | while read line; do
    echo "$line"
done
```

**VULNERABLE Pattern**:
```python
def compute_totals(self):
    for record in self:
        # BAD: sudo() called N times, one per record
        related = self.env['related.model'].sudo().search([
            ('record_id', '=', record.id)
        ])
        record.total_amount = sum(related.mapped('amount'))
```

**Remediation Code** — Batch query outside loop:
```python
def compute_totals(self):
    # GOOD: Single sudo() call, batch query for all records
    related_data = self.env['related.model'].sudo().read_group(
        domain=[('record_id', 'in', self.ids)],
        fields=['record_id', 'amount:sum'],
        groupby=['record_id']
    )
    # Map results by record_id for O(1) lookup
    totals_map = {
        item['record_id'][0]: item['amount']
        for item in related_data
    }
    for record in self:
        record.total_amount = totals_map.get(record.id, 0.0)
```

---

## LOW: Overly Permissive Record Rules

**Description**: Record rules with domain `[(1, '=', 1)]` (always True) for non-manager groups mean those users can see/modify all records in the model, including records from other users or departments.

**Why Low**: Typically an oversight rather than a vulnerability, but can lead to data leakage or unauthorized modifications.

**Detection Command**:
```bash
# Find record rules with always-true domain
grep -rn "1, '=', 1\|True.*domain_force" security/rules_*.xml
# Verify: are these for manager groups only? User groups should have tighter domains.
```

**VULNERABLE Pattern**:
```xml
<!-- Users can see ALL records — should be restricted to their own -->
<record id="rule_my_model_user" model="ir.rule">
    <field name="name">My Model: User</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('my_module.group_my_module_user'))]"/>
</record>
```

**Remediation Code** — Scope rule to user's own records:
```xml
<!-- Users see only their own records -->
<record id="rule_my_model_user" model="ir.rule">
    <field name="name">My Model: User Own Records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('my_module.group_my_module_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="False"/>
</record>

<!-- Managers see everything (this is correct for managers) -->
<record id="rule_my_model_manager" model="ir.rule">
    <field name="name">My Model: Manager All</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('my_module.group_my_module_manager'))]"/>
</record>
```

---

## Quick Reference: Severity Decision Tree

```
Is there NO access rule for a model?
  YES → CRITICAL

Is there auth='none' without API key auth?
  YES → CRITICAL

Is sudo() in a public/none auth route with sensitive model access?
  YES → CRITICAL

Is there string formatting in env.cr.execute()?
  YES → HIGH

Is sudo() in a public controller (auth='public')?
  YES → HIGH (or CRITICAL if sensitive model accessed)

Is there a company_id field but no multi-company record rule?
  YES → HIGH

Is csrf=False on a user-facing POST route?
  YES → HIGH

Is sudo() inside a for loop?
  YES → MEDIUM

Is there a sensitive field name without groups=?
  YES → MEDIUM

Is a record rule's domain overly broad for non-manager groups?
  YES → LOW

Is there a missing groups= on a field that should be restricted?
  YES → LOW to MEDIUM depending on sensitivity
```

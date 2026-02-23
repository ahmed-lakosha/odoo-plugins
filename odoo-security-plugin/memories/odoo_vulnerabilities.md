# Odoo Common Vulnerabilities — Reference Memory

Complete reference for known Odoo security vulnerabilities with safe vs. unsafe code examples and remediation code. Use this when security auditing or code reviewing Odoo modules.

---

## 1. SQL Injection via env.cr.execute()

**CVE Category**: CWE-89 (SQL Injection)
**Odoo Severity**: Critical

### Description

Odoo's ORM prevents SQL injection automatically. However, developers sometimes bypass the ORM using `self.env.cr.execute()` for performance. If user-controlled data is inserted into the SQL string using Python formatting, SQL injection is possible.

### Unsafe Examples

```python
# UNSAFE 1: % operator
def search_partners(self, name):
    sql = "SELECT id FROM res_partner WHERE name = '%s'" % name
    self.env.cr.execute(sql)
    # Payload: ' OR '1'='1' --  → returns ALL partners

# UNSAFE 2: f-string
def get_by_state(self, state):
    sql = f"SELECT * FROM sale_order WHERE state = '{state}'"
    self.env.cr.execute(sql)
    # Payload: confirmed'; DROP TABLE sale_order; --

# UNSAFE 3: string concatenation
def search_by_code(self, code):
    sql = "SELECT id FROM product_product WHERE default_code = '" + code + "'"
    self.env.cr.execute(sql)

# UNSAFE 4: .format()
def get_orders(self, customer_id):
    sql = "SELECT * FROM sale_order WHERE partner_id = {}".format(customer_id)
    self.env.cr.execute(sql)
    # customer_id could be: "1 OR 1=1"
```

### Safe Examples

```python
# SAFE 1: Parameterized query (psycopg2 format)
def search_partners(self, name):
    sql = "SELECT id FROM res_partner WHERE name = %s"
    self.env.cr.execute(sql, (name,))  # Tuple — psycopg2 handles escaping
    return self.env.cr.fetchall()

# SAFE 2: Multiple parameters
def get_orders(self, customer_id, state):
    sql = """
        SELECT id, name, amount_total
        FROM sale_order
        WHERE partner_id = %s AND state = %s
        ORDER BY date_order DESC
        LIMIT 100
    """
    self.env.cr.execute(sql, (customer_id, state))
    return self.env.cr.dictfetchall()

# SAFE 3: IN clause
def get_by_ids(self, record_ids):
    if not record_ids:
        return []
    sql = "SELECT id, name FROM res_partner WHERE id IN %s"
    self.env.cr.execute(sql, (tuple(record_ids),))
    return self.env.cr.fetchall()

# SAFE 4: Dynamic identifiers (column/table names) with psycopg2.sql
from psycopg2 import sql as psql
def get_field_value(self, table_name, field_name, record_id):
    query = psql.SQL("SELECT {} FROM {} WHERE id = %s").format(
        psql.Identifier(field_name),
        psql.Identifier(table_name)
    )
    self.env.cr.execute(query, (record_id,))
    return self.env.cr.fetchone()

# PREFERRED: Use ORM (no SQL injection possible)
def search_partners_orm(self, name):
    return self.env['res.partner'].search([('name', 'ilike', name)])
```

---

## 2. IDOR (Insecure Direct Object Reference) via Integer IDs in Public Routes

**CVE Category**: CWE-639 (Authorization Bypass Through User-Controlled Key)
**Odoo Severity**: High

### Description

Odoo uses sequential integer IDs for all records. Public routes that accept an `<int:id>` URL parameter and retrieve records via `sudo().browse(id)` allow attackers to enumerate IDs and access records belonging to other users.

### Unsafe Example

```python
# VULNERABLE: Attacker can change order_id=1 to order_id=2,3,4... to access ANY order
@http.route('/my/order/<int:order_id>', type='http', auth='public')
def view_order(self, order_id, **kwargs):
    order = request.env['sale.order'].sudo().browse(order_id)
    if not order.exists():
        return request.not_found()
    return request.render('my_module.order_template', {'order': order})
```

### Safe Examples

```python
# SAFE 1: Use _document_check_access (requires auth='user')
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal

class MyPortal(CustomerPortal):
    @http.route('/my/order/<int:order_id>', type='http', auth='user', website=True)
    def view_order(self, order_id, **kwargs):
        try:
            # Verifies: record exists AND current user has access
            order = self._document_check_access('sale.order', order_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render('my_module.order_template', {'order': order})

# SAFE 2: Manual ownership check
@http.route('/my/order/<int:order_id>', type='http', auth='user', website=True)
def view_order(self, order_id, **kwargs):
    order = request.env['sale.order'].browse(order_id)
    # ORM access controls apply automatically (user sees only their orders)
    if not order.exists():
        return request.not_found()
    # Extra check: verify partner ownership
    if order.partner_id != request.env.user.partner_id:
        if not order.partner_id.parent_id == request.env.user.partner_id:
            return request.redirect('/my')
    return request.render('my_module.order_template', {'order': order})

# SAFE 3: Access token for shareable links (guest access)
@http.route('/order/<int:order_id>/<string:access_token>',
            type='http', auth='public', website=True)
def view_order_token(self, order_id, access_token, **kwargs):
    try:
        order = self._document_check_access('sale.order', order_id,
                                            access_token=access_token)
    except (AccessError, MissingError):
        return request.not_found()
    return request.render('my_module.order_template', {'order': order})
```

---

## 3. Mass Assignment via Website Forms

**CVE Category**: CWE-915 (Improperly Controlled Modification of Dynamically-Determined Object Attributes)
**Odoo Severity**: High

### Description

Website form submissions that pass arbitrary field names to `write()` or `create()` allow attackers to modify fields they shouldn't be able to set, including system fields like `active`, `group_ids`, `is_company`, etc.

### Unsafe Example

```python
@http.route('/contact/submit', type='http', auth='public', methods=['POST'])
def submit_contact(self, **kwargs):
    # DANGEROUS: Passes ALL form fields directly to create()
    # Attacker can add is_company=True, active=False, etc.
    partner = request.env['res.partner'].sudo().create(kwargs)
    return request.redirect('/contact/thank-you')
```

### Safe Example

```python
@http.route('/contact/submit', type='http', auth='public', methods=['POST'])
def submit_contact(self, **kwargs):
    # SAFE: Explicit whitelist of allowed fields
    ALLOWED_FIELDS = {'name', 'email', 'phone', 'website', 'comment'}
    safe_vals = {
        key: value
        for key, value in kwargs.items()
        if key in ALLOWED_FIELDS
    }

    # Additional validation
    if not safe_vals.get('name') or not safe_vals.get('email'):
        return request.redirect('/contact?error=missing_fields')

    # Validate email format
    import re
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', safe_vals.get('email', '')):
        return request.redirect('/contact?error=invalid_email')

    partner = request.env['res.partner'].sudo().create(safe_vals)
    return request.redirect('/contact/thank-you')
```

---

## 4. Privilege Escalation via sudo()

**CVE Category**: CWE-269 (Improper Privilege Management)
**Odoo Severity**: High

### Description

`sudo()` in Odoo bypasses ALL access controls and runs as the superuser. Using it in public routes or with user-controlled domain parameters allows privilege escalation.

### Unsafe Example

```python
# UNSAFE: User can access ANY data by providing different domain
@http.route('/api/records', type='json', auth='user')
def get_records(self, model, domain=None):
    # User controls both model name AND domain — can access anything
    domain = domain or []
    records = request.env[model].sudo().search_read(domain)
    return records
    # Attacker: model='ir.rule', domain=[] → sees all security rules
    # Attacker: model='res.users', domain=[] → sees all user accounts
```

### Safe Example

```python
# SAFE: Explicit allowlist of accessible models
ALLOWED_MODELS = {'my.model', 'my.category', 'my.tag'}

@http.route('/api/records', type='json', auth='user')
def get_records(self, model, domain=None):
    if model not in ALLOWED_MODELS:
        return {'error': 'Model not accessible', 'code': 403}

    # Validate domain is a list of tuples
    if domain and not isinstance(domain, list):
        return {'error': 'Invalid domain format', 'code': 400}

    # Add mandatory filter: current user's company + active only
    safe_domain = [
        ('company_id', 'in', request.env.user.company_ids.ids),
        ('active', '=', True),
    ] + (domain or [])

    # No sudo() — respect user's actual permissions
    records = request.env[model].search_read(safe_domain, limit=100)
    return {'records': records}
```

---

## 5. Server-Side Template Injection (SSTI) in QWeb

**CVE Category**: CWE-94 (Code Injection)
**Odoo Severity**: High

### Description

QWeb templates allow Python expressions inside `t-if`, `t-att-`, and other directives. If user-controlled data is embedded directly in template expressions (not just values), code injection may be possible.

### Unsafe Example

```xml
<!-- UNSAFE: The 'expression' variable contains user-controlled code -->
<!-- Never dynamically construct XPath or Python expressions from user input -->
<t t-if="eval(record.user_expression)">
    <!-- This is dangerous if user_expression contains malicious code -->
</t>
```

```python
# UNSAFE: Rendering template with user-controlled template name
@http.route('/render', auth='public')
def render_template(self, template_name):
    # User can request any template, including admin ones
    return request.render(template_name, {})
```

### Safe Example

```python
# SAFE: Allowlist of renderable templates
ALLOWED_TEMPLATES = {
    'my_module.homepage',
    'my_module.about',
    'my_module.contact',
}

@http.route('/page/<string:page_name>', auth='public')
def render_page(self, page_name):
    template = f'my_module.page_{page_name}'
    if template not in ALLOWED_TEMPLATES:
        return request.not_found()
    return request.render(template, {})
```

```xml
<!-- SAFE: User data as VALUES, not expressions -->
<span t-esc="record.user_name"/>        <!-- Escaped output -->
<span t-raw="record.trusted_html"/>     <!-- Only for trusted HTML -->
<!-- NEVER use t-raw with user-controlled data -->
```

---

## 6. Insecure Direct Object Reference in Attachments

**CVE Category**: CWE-639 (Authorization Bypass Through User-Controlled Key)
**Odoo Severity**: High

### Description

Odoo's `ir.attachment` model stores files. Without proper access control, users can access attachments belonging to other users' records by guessing or enumerating attachment IDs.

### Unsafe Example

```python
# UNSAFE: Any authenticated user can download any attachment by ID
@http.route('/attachment/<int:att_id>/download', auth='user')
def download_attachment(self, att_id):
    attachment = request.env['ir.attachment'].sudo().browse(att_id)
    if attachment.exists():
        return request.make_response(
            base64.b64decode(attachment.datas),
            headers=[('Content-Type', attachment.mimetype)]
        )
```

### Safe Example

```python
# SAFE: Verify user has access to the attached record
@http.route('/attachment/<int:att_id>/download', auth='user')
def download_attachment(self, att_id):
    attachment = request.env['ir.attachment'].browse(att_id)
    # Without sudo() — ORM access controls check if user can see the attachment
    if not attachment.exists():
        return request.not_found()

    # Additional check: verify access to the linked record
    if attachment.res_model and attachment.res_id:
        try:
            linked_record = request.env[attachment.res_model].browse(attachment.res_id)
            linked_record.check_access_rights('read')
            linked_record.check_access_rule('read')
        except Exception:
            return request.not_found()

    return request.make_response(
        base64.b64decode(attachment.datas),
        headers=[
            ('Content-Type', attachment.mimetype),
            ('Content-Disposition', f'attachment; filename="{attachment.name}"'),
        ]
    )
```

---

## 7. Missing CSRF on State-Changing Routes

**CVE Category**: CWE-352 (Cross-Site Request Forgery)
**Odoo Severity**: Medium

### Description

CSRF attacks trick authenticated users into executing unintended actions. Odoo protects against this with CSRF tokens by default. Disabling CSRF (`csrf=False`) on routes that modify data is dangerous.

### Unsafe Example

```python
# UNSAFE: CSRF disabled on a route that deletes data
@http.route('/record/delete', type='http', auth='user', methods=['POST'], csrf=False)
def delete_record(self, record_id, **kwargs):
    record = request.env['my.model'].browse(int(record_id))
    record.unlink()
    return request.redirect('/records')

# Attacker's malicious website:
# <form action="https://yourapp.com/record/delete" method="POST">
#     <input name="record_id" value="42"/>
# </form>
# <script>document.forms[0].submit();</script>
# Any logged-in user visiting this page will delete record 42!
```

### Safe Example

```python
# SAFE: Keep CSRF enabled (just don't add csrf=False)
@http.route('/record/delete', type='http', auth='user', methods=['POST'])
def delete_record(self, record_id, **kwargs):
    record = request.env['my.model'].browse(int(record_id))
    record.unlink()
    return request.redirect('/records')

# ACCEPTABLE exception: machine-to-machine webhooks with their own auth
@http.route('/webhook/payment', type='json', auth='none', methods=['POST'], csrf=False)
def payment_webhook(self, **kwargs):
    # MUST implement own authentication here
    signature = request.httprequest.headers.get('X-Signature', '')
    if not self._verify_signature(request.httprequest.data, signature):
        return {'error': 'Invalid signature', 'code': 401}
    # Process payment...
```

---

## 8. Information Disclosure via Error Messages

**CVE Category**: CWE-209 (Generation of Error Message Containing Sensitive Information)
**Odoo Severity**: Low-Medium

### Description

Stack traces, database error messages, and internal paths in HTTP responses give attackers information about the system architecture, database schema, and potential vulnerabilities.

### Unsafe Example

```python
@http.route('/api/process', type='json', auth='user')
def process(self, data):
    try:
        result = self._process_data(data)
        return {'result': result}
    except Exception as e:
        # UNSAFE: Exposes internal error details
        return {'error': str(e), 'traceback': traceback.format_exc()}
        # Attacker learns: database table names, model internals, file paths
```

### Safe Example

```python
import logging
_logger = logging.getLogger(__name__)

@http.route('/api/process', type='json', auth='user')
def process(self, data):
    try:
        result = self._process_data(data)
        return {'result': result}
    except ValidationError as e:
        # Safe: Odoo validation errors are meant for users
        return {'error': str(e.args[0]), 'code': 400}
    except AccessError:
        # Safe: Generic access denied message
        return {'error': 'Access denied', 'code': 403}
    except Exception as e:
        # SAFE: Log internally, return generic message to user
        _logger.exception("Unexpected error in /api/process: %s", str(e))
        return {
            'error': 'An internal error occurred. Please contact support.',
            'code': 500
        }
```

**Production Configuration** (conf file):
```ini
; Disable debug mode in production — never show tracebacks to users
dev_mode =
; Use workers for production (process isolation)
workers = 4
; Disable test mode
test_enable = False
```

---

## Quick Reference: Vulnerability Checklist

Before deploying any Odoo module, verify:

### SQL Security
- [ ] No `env.cr.execute()` with `%`, `f""`, `.format()`, or `+` string building
- [ ] All raw SQL uses `(query, (params,))` parameterized form
- [ ] Dynamic column/table names use `psycopg2.sql.Identifier`

### Access Control
- [ ] Every route has explicit `auth=` parameter
- [ ] `auth='none'` routes implement API key or HMAC authentication
- [ ] No `sudo().browse(user_provided_id)` in public routes
- [ ] Form submissions whitelist allowed fields explicitly
- [ ] Attachments verify access to the linked record

### CSRF & State Changes
- [ ] No `csrf=False` on user-facing POST routes
- [ ] State-changing operations use POST method only
- [ ] Machine-to-machine APIs with `csrf=False` implement their own auth

### Information Security
- [ ] Error responses return generic messages in production
- [ ] Exceptions are logged server-side with full details
- [ ] Stack traces never sent to client

### Template Security
- [ ] `t-raw` never used with user-controlled data (use `t-esc` instead)
- [ ] Template names never user-controlled (use allowlist)
- [ ] User data appears as values, never as template expressions

### Model Access
- [ ] Every `_name` model has `ir.model.access.csv` entries
- [ ] Portal users have record rules restricting to their own data
- [ ] Multi-company models have company isolation record rules
- [ ] Sensitive fields have `groups=` restriction

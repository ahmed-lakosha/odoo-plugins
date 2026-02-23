---
title: 'Check HTTP Routes'
read_only: true
type: 'command'
description: 'Audit all HTTP routes in an Odoo module for authentication, CSRF, and data exposure security issues.'
---

# /check-routes <module-path>

Audit all `@http.route()` decorators in an Odoo module's `controllers/` directory for authentication configuration, CSRF protection, sensitive data exposure, and API security.

## Usage

```
/check-routes /path/to/module
/check-routes /path/to/module --verbose
```

## What It Analyzes

### 1. auth= Parameter Validation

Every route MUST have an explicit `auth=` parameter. Odoo supports three values:

| auth value | Meaning | When to Use |
|------------|---------|-------------|
| `'user'` | Requires authenticated user | Internal backend, user-specific operations |
| `'public'` | Works for guests + logged-in users | Public website pages, product listings |
| `'none'` | No authentication at all | Webhooks with own auth, health checks |

**Flags**:
- `auth='none'` without API key / HMAC validation in the function body → CRITICAL
- Missing `auth=` parameter → HIGH (defaults to 'user' but implicit is dangerous)
- `auth='public'` accessing sensitive models with `sudo()` → HIGH

### 2. CSRF Protection Check

Odoo enforces CSRF protection by default on all POST routes. This is a security feature — do not disable it without a good reason.

**Flags**:
- `csrf=False` on `auth='user'` POST routes → HIGH (CSRF vulnerability)
- `csrf=False` on `auth='public'` POST routes → MEDIUM
- `csrf=False` is acceptable ONLY for machine-to-machine APIs with their own auth

```python
# DANGEROUS — CSRF disabled for user-facing action
@http.route('/my/action', type='http', auth='user', methods=['POST'], csrf=False)
def my_action(self):
    pass  # User is vulnerable to CSRF!

# SAFE — CSRF enabled (default, just don't add csrf=False)
@http.route('/my/action', type='http', auth='user', methods=['POST'])
def my_action(self):
    pass  # Protected!

# ACCEPTABLE — machine-to-machine API with API key auth
@http.route('/api/v1/webhook', type='json', auth='none', methods=['POST'], csrf=False)
def webhook(self, **kwargs):
    api_key = request.httprequest.headers.get('X-Api-Key', '')
    if not self._validate_key(api_key):
        return {'error': 'Unauthorized'}
    # Safe to process
```

### 3. Sensitive Model Access in Public Routes

Public routes that access sensitive Odoo models are flagged. Sensitive models include:

```
res.partner, res.users, hr.employee, hr.payslip,
account.move, account.payment, sale.order, purchase.order,
stock.picking, ir.config_parameter, ir.attachment,
ir.rule, ir.model.access, mail.message, res.partner.bank
```

A public route that accesses these with `sudo()` bypasses all access controls.

### 4. GET/POST Mixed Methods

Routes accepting both GET and POST violate HTTP semantics. GET should be read-only; POST should handle state changes.

```python
# MEDIUM — mixed methods
@http.route('/my/route', auth='user', methods=['GET', 'POST'])

# CORRECT — separate routes
@http.route('/my/data', auth='user', methods=['GET'])
def get_data(self): ...

@http.route('/my/action', auth='user', methods=['POST'])
def do_action(self): ...
```

### 5. API Route CORS Configuration

JSON API routes with `auth='none'` should have explicit `cors=` configuration.

```python
# LOW — no CORS configured
@http.route('/api/v1/data', type='json', auth='none', csrf=False)

# BETTER — explicit CORS
@http.route('/api/v1/data', type='json', auth='none', csrf=False, cors='*')
# or restrict to specific origins:
@http.route('/api/v1/data', type='json', auth='none', csrf=False, cors='https://myapp.com')
```

### 6. SQL Injection in Controllers

Scans controller functions for `env.cr.execute()` calls with string formatting.

## Output Format

```
========================================
ROUTE AUDITOR REPORT — my_module
========================================
Total issues: 4

[CRITICAL] controllers/main.py:45
  Route ['/webhook'] uses auth='none' but no API key validation, HMAC signature
  check, or authentication logic detected in method 'webhook'.
  This route is completely unauthenticated.

[HIGH] controllers/main.py:67
  Route ['/orders'] is auth='public' and accesses sensitive model 'sale.order'
  with sudo() in method 'get_orders'. This bypasses all access controls for
  public users. Add domain filters or change auth='user'.

[HIGH] controllers/api.py:23
  Route ['/api/submit'] (methods=['POST']) has csrf=False but auth='user'.
  Disabling CSRF on user-authenticated routes leaves users vulnerable to CSRF.

[MEDIUM] controllers/main.py:89
  Route ['/my/page'] has a sensitive-looking path but uses auth='public'.
  Verify this is intentional and no sensitive data is exposed.
```

## Secure Route Patterns

### Internal User Route
```python
@http.route('/my/data', type='http', auth='user', methods=['GET'])
def my_data(self):
    records = request.env['my.model'].search([])  # Scoped to user
    return request.render('template', {'records': records})
```

### Public Website Route
```python
@http.route('/products', type='http', auth='public', website=True)
def products(self):
    # Only published products, only safe fields
    products = request.env['product.template'].sudo().search([
        ('website_published', '=', True)
    ])
    return request.render('template', {'products': products})
```

### Authenticated API Route
```python
@http.route('/api/v1/resource', type='json', auth='user', methods=['POST'])
def api_resource(self, **kwargs):
    return {'data': request.env['my.model'].search_read([])}
```

### Webhook with API Key Auth
```python
@http.route('/webhook/events', type='json', auth='none', methods=['POST'], csrf=False)
def webhook(self, **kwargs):
    api_key = request.httprequest.headers.get('X-Api-Key', '')
    if not self._validate_api_key(api_key):
        return {'error': 'Unauthorized', 'code': 401}
    # Process event...
    return {'status': 'received'}
```

### Portal Route with Ownership Check
```python
@http.route('/my/order/<int:order_id>', type='http', auth='user', website=True)
def portal_order(self, order_id, **kwargs):
    from odoo.exceptions import AccessError, MissingError
    try:
        order = self._document_check_access('sale.order', order_id)
    except (AccessError, MissingError):
        return request.redirect('/my')
    return request.render('portal_template', {'order': order})
```

## Running Directly

```bash
python scripts/route_auditor.py /path/to/module
python scripts/route_auditor.py /path/to/module --json
python scripts/route_auditor.py /path/to/module --verbose
```

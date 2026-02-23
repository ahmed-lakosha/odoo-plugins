# Odoo Testing Patterns Memory

Reference guide for common Odoo test patterns used across Odoo 14-19.

---

## Core Test Base Classes

### TransactionCase (Most Common)

```python
from odoo.tests import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestMyModel(TransactionCase):
    """
    - Each test method is wrapped in a database SAVEPOINT
    - Savepoint is rolled back after each test method
    - setUpClass() data is rolled back after the entire class
    - Full ORM access via self.env
    - No HTTP server — pure database/ORM testing
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Runs ONCE. Data persists across all test methods.
        cls.partner = cls.env['res.partner'].create({
            'name': 'Shared Fixture',
        })
        # Disable email tracking to speed up tests
        cls.env = cls.env(context={
            **cls.env.context,
            'mail_notrack': True,
            'tracking_disable': True,
            'no_reset_password': True,
        })

    def setUp(self):
        super().setUp()
        # Runs before EACH test. Data rolled back after each test.
        self.record = self.env['my.model'].create({
            'name': 'Per-Test Record',
            'partner_id': self.partner.id,
        })

    def test_example(self):
        # self.partner is from setUpClass (shared)
        # self.record is from setUp (isolated, rolled back after this test)
        self.assertEqual(self.record.partner_id, self.partner)
```

### HttpCase (For Routes and UI)

```python
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestWebsite(HttpCase):
    """
    - Starts a real HTTP server on localhost (random port)
    - Use self.url_open() for HTTP requests
    - Use self.jsonrpc() for JSON-RPC calls
    - Use self.authenticate(login, password) for auth
    - Slower than TransactionCase due to HTTP overhead
    """

    def test_public_page(self):
        res = self.url_open('/shop')
        self.assertEqual(res.status_code, 200)

    def test_authenticated_route(self):
        self.authenticate('admin', 'admin')
        res = self.url_open('/web/dataset/call_kw', data={...})
        self.assertEqual(res.status_code, 200)

    def test_json_rpc(self):
        self.authenticate('admin', 'admin')
        result = self.jsonrpc('/web/dataset/call_kw', method='execute_kw', params={
            'model': 'res.partner',
            'method': 'search_read',
            'args': [[]],
            'kwargs': {'fields': ['name'], 'limit': 5},
        })
        self.assertIsInstance(result, list)
```

### SavepointCase (Odoo 14-15 Only — Removed in 16)

```python
# ONLY for Odoo 14/15 — use TransactionCase in 16+
from odoo.tests.common import SavepointCase

class TestOld(SavepointCase):
    # Class-level setup is preserved across tests (not rolled back per test)
    # Use cls.env.cr.savepoint() for partial rollback control
    pass

# In Odoo 16+, use TransactionCase with manual savepoints:
class TestModern(TransactionCase):
    def test_with_savepoint(self):
        with self.env.cr.savepoint():
            # This block will be rolled back if exception occurs
            self.env['my.model'].create({'invalid': True})
```

---

## @tagged Decorator Reference Table

| Tag | When it runs | Use case |
|-----|-------------|----------|
| `post_install` | After all modules installed | Integration tests (most common) |
| `at_install` | During module install | Basic integrity checks |
| `-at_install` | Excludes at_install | Combined with post_install |
| `-post_install` | Excludes post_install | Run only during install |
| `standard` | Default CI | General unit tests |
| `-standard` | Not in default CI | Manual/special tests |
| `slow` | Explicit request only | Long-running tests |
| `external` | Explicit request only | External API calls |

### Most Common Combinations

```python
# Standard production test (runs in CI, after all modules installed)
@tagged('post_install', '-at_install')

# Installation sanity check
@tagged('at_install', '-post_install')

# Explicit opt-in only (manual testing)
@tagged('-standard', 'manual')

# Module-specific tag (for running just your module's tests)
@tagged('post_install', '-at_install', 'my_module_tag')

# Exclude from automated CI
@tagged('slow', 'post_install', '-at_install', '-standard')
```

### Running by Tag

```bash
# Run post_install tagged tests for a module
python -m odoo -c conf/p17.conf -d db --test-enable -u my_module \
    --test-tags=post_install --stop-after-init

# Run specific test class
python -m odoo -c conf/p17.conf -d db --test-enable -u my_module \
    --test-tags=/my_module:TestMyModel --stop-after-init

# Run specific method
python -m odoo -c conf/p17.conf -d db --test-enable -u my_module \
    --test-tags=/my_module:TestMyModel.test_create --stop-after-init
```

---

## setUp / tearDown Patterns

### Pattern 1: Expensive Setup in setUpClass

```python
@classmethod
def setUpClass(cls):
    super().setUpClass()
    # Create expensive fixtures ONCE
    cls.company = cls.env.ref('base.main_company')
    cls.currency = cls.env.ref('base.USD')
    # Complex product with variants — expensive to create
    cls.product_tmpl = cls.env['product.template'].create({
        'name': 'Complex Product',
        'type': 'product',
        'attribute_line_ids': [(0, 0, {
            'attribute_id': cls.env.ref('product.product_attribute_color').id,
            'value_ids': [(4, cls.env.ref('product.product_attribute_value_red').id)],
        })],
    })
```

### Pattern 2: Fresh Records in setUp

```python
def setUp(self):
    super().setUp()
    # Always fresh, auto-rolled back, cheap to create
    self.record = self.env['my.model'].create({
        'name': 'Test',
        'partner_id': self.partner.id,  # from setUpClass
    })
```

### Pattern 3: Disabling Side Effects

```python
@classmethod
def setUpClass(cls):
    super().setUpClass()
    # Disable mail operations globally for all tests in class
    cls.env = cls.env(context={
        **cls.env.context,
        'mail_notrack': True,           # Disable tracking (chatter)
        'tracking_disable': True,        # Odoo 14+: more comprehensive
        'no_reset_password': True,       # Skip welcome email on user create
        'mail_create_nosubscribe': True, # No followers on record create
    })
```

### Pattern 4: Cleanup in tearDown (Rare)

```python
def tearDown(self):
    super().tearDown()
    # Only needed for external resources (files, API connections)
    # Database is auto-cleaned by savepoint rollback
    if hasattr(self, '_temp_file') and self._temp_file.exists():
        self._temp_file.unlink()
```

---

## Assertion Methods Reference

### Equality and Comparison

```python
self.assertEqual(a, b)              # a == b
self.assertNotEqual(a, b)           # a != b
self.assertAlmostEqual(a, b, places=2)  # Float: round to 2 decimal places
self.assertGreater(a, b)            # a > b
self.assertGreaterEqual(a, b)       # a >= b
self.assertLess(a, b)               # a < b
self.assertLessEqual(a, b)          # a <= b
```

### Identity and None

```python
self.assertIs(a, b)         # a is b (same object)
self.assertIsNot(a, b)      # a is not b
self.assertIsNone(a)        # a is None
self.assertIsNotNone(a)     # a is not None
```

### Boolean

```python
self.assertTrue(x)          # bool(x) is True
self.assertFalse(x)         # bool(x) is False
# Odoo recordsets:
self.assertTrue(record)     # record is non-empty recordset
self.assertFalse(record)    # record is empty recordset
```

### Membership

```python
self.assertIn(a, b)         # a in b (works for lists, sets, dicts, recordsets)
self.assertNotIn(a, b)      # a not in b
# Odoo:
self.assertIn(record, recordset)
self.assertIn('field_name', dir(record))
```

### Exceptions

```python
# Context manager (recommended)
with self.assertRaises(ValidationError):
    record.write({'amount': -1})

# With message check
with self.assertRaises(ValidationError) as ctx:
    record.write({'amount': -1})
self.assertIn('must be positive', str(ctx.exception))

# Lambda form (simple cases)
self.assertRaises(UserError, record.action_confirm)
```

### String

```python
self.assertIn('substring', text)
self.assertRegex(text, r'pattern')
self.assertNotRegex(text, r'pattern')
```

### Collections

```python
self.assertEqual(len(records), 3)
self.assertGreater(len(records), 0)
self.assertListEqual([1, 2, 3], [1, 2, 3])
```

---

## Testing Computed Fields

### Pattern: Verify Initial Computation

```python
def test_compute_total_on_create(self):
    """Computed field is calculated at create time."""
    order = self.env['sale.order'].create({
        'partner_id': self.partner.id,
        'order_line': [(0, 0, {
            'product_id': self.product.id,
            'product_uom_qty': 2,
            'price_unit': 100.0,
        })],
    })
    self.assertAlmostEqual(order.amount_untaxed, 200.0, places=2)
```

### Pattern: Verify Recomputation on Dependency Change

```python
def test_compute_triggers_on_write(self):
    """Modifying a @depends field triggers recompute."""
    record = self.env['my.model'].create({'base': 100.0, 'rate': 0.1})
    self.assertAlmostEqual(record.computed_total, 110.0, places=2)

    record.write({'base': 200.0})
    # For stored fields, value is updated in DB automatically
    self.assertAlmostEqual(record.computed_total, 220.0, places=2)
```

### Pattern: Test Stored vs Non-Stored

```python
def test_stored_compute_in_db(self):
    """Stored computed field persists in the database."""
    record = self.env['my.model'].create({'base': 100.0})
    record_id = record.id

    # Clear ORM cache and re-read from DB
    record.invalidate_recordset()  # Odoo 16+
    # record.invalidate_cache()    # Odoo 14-15

    self.env.cr.execute("SELECT computed_field FROM my_model WHERE id = %s", [record_id])
    row = self.env.cr.fetchone()
    self.assertAlmostEqual(float(row[0]), 100.0, places=2)
```

---

## Testing Constraints

### Python Constraint (@constrains)

```python
def test_amount_must_be_positive(self):
    """@constrains raises ValidationError on invalid data."""
    from odoo.exceptions import ValidationError
    with self.assertRaises(ValidationError):
        self.env['my.model'].create({'name': 'Bad', 'amount': -1.0})

def test_constraint_on_write(self):
    """Constraint fires on write, not just create."""
    record = self.env['my.model'].create({'amount': 100.0})
    from odoo.exceptions import ValidationError
    with self.assertRaises(ValidationError):
        record.write({'amount': -50.0})
```

### SQL Constraint (UNIQUE, CHECK)

```python
def test_unique_code_constraint(self):
    """SQL UNIQUE constraint prevents duplicates."""
    self.env['my.model'].create({'name': 'First', 'code': 'UNIQUE001'})
    from psycopg2 import IntegrityError
    with self.assertRaises(Exception):  # catches IntegrityError or UserError
        with self.env.cr.savepoint():
            self.env['my.model'].create({'name': 'Second', 'code': 'UNIQUE001'})
```

---

## Testing Onchange

```python
def test_onchange_partner_populates_currency(self):
    """Simulate onchange by calling the method directly on a New record."""
    # Use .new() to create an in-memory record (not saved to DB)
    record = self.env['my.model'].new({
        'partner_id': self.partner.id,
    })
    # Call the onchange method
    record._onchange_partner_id()
    # Verify that onchange populated expected fields
    self.assertTrue(record.currency_id, "Currency should be set from partner")
    self.assertEqual(record.currency_id, self.partner.country_id.currency_id)
```

---

## Testing Workflows / State Machines

```python
@tagged('post_install', '-at_install')
class TestOrderWorkflow(TransactionCase):

    def test_draft_to_confirmed(self):
        order = self.env['my.order'].create({'name': 'Order 1'})
        self.assertEqual(order.state, 'draft')
        order.action_confirm()
        self.assertEqual(order.state, 'confirmed')

    def test_confirmed_to_done(self):
        order = self.env['my.order'].create({'name': 'Order 2'})
        order.action_confirm()
        order.action_done()
        self.assertEqual(order.state, 'done')

    def test_cancel_from_draft(self):
        order = self.env['my.order'].create({'name': 'Order 3'})
        order.action_cancel()
        self.assertEqual(order.state, 'cancelled')

    def test_cannot_confirm_cancelled(self):
        from odoo.exceptions import UserError
        order = self.env['my.order'].create({'name': 'Order 4'})
        order.action_cancel()
        with self.assertRaises(UserError):
            order.action_confirm()
```

---

## Version Compatibility Notes

| Feature | 14 | 15 | 16 | 17 | 18 | 19 |
|---------|----|----|----|----|----|----|
| `SavepointCase` | Yes | Yes | Removed | Removed | Removed | Removed |
| `TransactionCase` | Yes | Yes | Yes | Yes | Yes | Yes |
| `invalidate_recordset()` | No | No | Yes | Yes | Yes | Yes |
| `invalidate_cache()` | Yes | Yes | Deprecated | Removed | Removed | Removed |
| `browser_js()` | Yes | Yes | Yes | Deprecated | Removed | Removed |
| Tag `--test-tags` path format | No | No | Yes | Yes | Yes | Yes |

---

## CI Test Runner Patterns

### Running Tests in GitHub Actions (Self-Hosted)

```yaml
# .github/workflows/2-test.yml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
      POSTGRES_DB: postgres
    ports:
      - 5432:5432
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5

steps:
  - name: Install system deps
    run: |
      sudo apt-get update -q
      sudo apt-get install -yq \
        libxml2-dev libxslt1-dev libpq-dev \
        libldap2-dev libsasl2-dev node-less

  - name: Install Python deps
    run: pip install -r requirements.txt coverage

  - name: Create test database
    run: PGPASSWORD=odoo psql -h localhost -U odoo -c "CREATE DATABASE test_mymodule" postgres

  - name: Run tests
    run: |
      python -m odoo \
        --db_host=localhost --db_user=odoo --db_password=odoo \
        -d test_mymodule \
        --addons-path=odoo/addons,projects \
        --test-enable --stop-after-init \
        -i my_module \
        --log-level=test 2>&1 | tee /tmp/test.log
      grep -q "FAILED\|ERROR" /tmp/test.log && exit 1 || true
```

### Running Tests for Changed Modules Only (10x faster than `-u all`)

```bash
# Detect changed modules from git diff
CHANGED=$(git diff --name-only HEAD~1 HEAD \
  | grep "^projects/" \
  | awk -F/ '{print $2}' \
  | sort -u \
  | tr '\n' ',')

# Run only changed modules
python -m odoo -c conf/myproject.conf -d mydb \
  --test-enable --stop-after-init \
  -u "${CHANGED%,}" \
  --test-tags=post_install,standard
```

### Test Tags in CI

```bash
# Standard CI test run (most common)
--test-tags=post_install,standard

# Full test run (slower, for pre-release)
--test-tags=post_install,at_install,standard

# Module-specific only
--test-tags=/my_module

# Specific class
--test-tags=/my_module:TestMyModel

# Skip slow tests in CI
--test-tags=standard,-slow
```

### Odoo.sh Test Configuration (`odoo_tests.cfg`)

When using Odoo.sh (custom addons repo), place at repo root:

```ini
[options]
test_enable = True
test_tags = standard,at_install
# Odoo.sh auto-installs all installable modules and runs tests on every push
```

### Detect Test Failures in CI Log

Odoo writes test results to the log. Check for failures:

```bash
# These patterns indicate test failure
grep -E "FAILED|ERROR|Traceback|AssertionError" /tmp/odoo_test.log

# Odoo 17+ also prints summary
# "Ran X tests in Y.Zs — FAILED (failures=N, errors=M)"
grep -E "FAILED \(failures=" /tmp/odoo_test.log && exit 1

# Check exit code (Odoo returns 0 even on test failures in some versions!)
# Always grep the log for failure patterns
```

### Coverage in CI

```bash
# Run with coverage
coverage run --source=projects/my_module \
  -m odoo -c /tmp/test.conf -d test_mydb \
  --test-enable --stop-after-init -i my_module

# Report
coverage report --include="projects/my_module/**" --fail-under=60

# Upload to GitHub as artifact
coverage html -d /tmp/coverage_report
```

### Python Version × Odoo Version Matrix for CI

| Odoo | Python | PostgreSQL |
|------|--------|-----------|
| 14   | 3.8    | 13        |
| 15   | 3.10   | 13        |
| 16   | 3.10   | 14        |
| 17   | 3.11   | 15        |
| 18   | 3.12   | 15        |
| 19   | 3.12   | 16        |

---

## Testing Approach Comparison

Choose the right tool for what you're testing:

| | TransactionCase | HttpCase | Playwright E2E |
|---|---|---|---|
| **What it tests** | Business logic, ORM, computed fields | HTTP routes, JSON-RPC, portal | Full UI workflows, JS interactions |
| **Browser involved** | No | No | Yes (Chromium/Firefox) |
| **Speed** | Fast (< 1s/test) | Medium (1-5s/test) | Slow (5-30s/test) |
| **Requires live server** | No | Yes (auto-started) | Yes (separate process) |
| **Best for** | Constraints, @api.depends, state machines | Controllers, website pages, auth | UX flows, drag-drop, dynamic UI |
| **Odoo versions** | All (14-19) | All (14-19) | All (14-19) |
| **CI complexity** | Simple (PostgreSQL only) | Medium (Odoo server needed) | High (Node.js + Odoo + browser) |

### When to Use Each

```
New module with business logic?   → TransactionCase (always start here)
REST API / controller endpoint?   → HttpCase + url_open / jsonrpc
Portal page / website route?      → HttpCase + self.authenticate()
Multi-step UI workflow?           → Playwright E2E
JavaScript-heavy feature?         → Playwright E2E
Visual regression?                → Playwright + screenshots
Odoo.sh project QA?               → Playwright against staging URL
```

### Migration: `browser_js()` → Playwright

`browser_js()` was deprecated in Odoo 17 and removed in Odoo 18+.

| Old Odoo 14-16 | New Odoo 17-19 |
|----------------|----------------|
| `self.browser_js('/web', "web.tour.startTour('my_tour')")` | Playwright: `await page.goto('/web'); await page.evaluate("odoo.startTour('my_tour')")` |
| `self.start_tour('/odoo/sales', 'sale_tour')` | Playwright full test file |
| `phantom_js(...)` | Playwright full test file |

**Note**: Odoo's JavaScript tour definitions (`.js` files with `web.tour.register`) still work in Odoo 17+.
Only the Python `browser_js()` / `start_tour()` runner was removed. Tours can still be triggered
via `page.evaluate()` in Playwright.

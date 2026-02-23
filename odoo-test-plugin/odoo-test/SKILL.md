---
name: odoo-test
description: "Comprehensive Odoo testing toolkit for generating test skeletons, running test suites, creating mock data, and analyzing test coverage across Odoo 14-19. Supports TransactionCase, HttpCase, SavepointCase, and integrates with Azure DevOps for CI/CD test result reporting."
version: "1.0.0"
author: "TaqaTechno"
license: "MIT"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebFetch
metadata:
  mode: "codebase"
  supported-versions: ["14", "15", "16", "17", "18", "19"]
  primary-version: "17"
  test-patterns: "80+"
  mock-data-generators: "20+"
  categories:
    - testing
    - unit-tests
    - integration-tests
    - mock-data
    - coverage
---

# Odoo Testing Toolkit Skill (v1.0)

A comprehensive skill for generating, running, and analyzing tests across Odoo 14-19. Covers unit tests, integration tests, HTTP controller tests, mock data creation, and test coverage analysis. Includes CI/CD integration patterns for Azure DevOps pipelines.

## Configuration

- **Supported Versions**: Odoo 14, 15, 16, 17, 18, 19
- **Primary Version**: Odoo 17
- **Test Patterns**: 80+ documented patterns
- **Mock Data Generators**: 20+ field-type-aware generators
- **Core Base Class**: `odoo.tests.common.TransactionCase`
- **Test Runner**: Built-in Odoo test framework + CLI scripts

---

## Quick Reference

### All Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `/odoo-test` | Full testing workflow | `/odoo-test my_module` |
| `/test-generate` | Generate test skeleton | `/test-generate --model my.model --module /path/to/module` |
| `/test-run` | Run test suite | `/test-run my_module --tags post_install` |
| `/test-coverage` | Analyze coverage | `/test-coverage /path/to/module` |
| `/test-data` | Generate mock data | `/test-data --model res.partner --count 10` |

### One-Liner Command Reference

```bash
# Generate test skeleton for a model
python test_generator.py --model sale.order --module /c/odoo/odoo17/projects/myproject/my_module

# Run tests for a module
python -m odoo -c conf/project17.conf -d project17 --test-enable -i my_module --stop-after-init

# Run tests with specific tags
python -m odoo -c conf/project17.conf -d project17 --test-enable --test-tags=post_install --stop-after-init

# Run specific test class
python -m odoo -c conf/project17.conf -d project17 --test-enable --test-tags=/my_module:TestMyModel --stop-after-init

# Analyze coverage
python coverage_reporter.py --module /path/to/my_module

# Generate 10 mock partner records
python mock_data_factory.py --model res.partner --count 10
```

---

## Testing Architecture

### Test Class Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ODOO TEST CLASS HIERARCHY                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  unittest.TestCase (Python standard)                                          │
│  └── odoo.tests.common.BaseCase                                              │
│       ├── TransactionCase          ← MOST COMMON                             │
│       │   • Each test wrapped in transaction rolled back on completion        │
│       │   • Full ORM access via self.env                                      │
│       │   • Database state reset between tests                                │
│       │   • setUpClass() for shared expensive setup                           │
│       │                                                                       │
│       ├── SavepointCase (Odoo 14-15) / TransactionCase with savepoints        │
│       │   • Allows partial rollback within a test                             │
│       │   • Useful for testing exception handling                             │
│       │   • Use self.cr.savepoint() context manager                           │
│       │                                                                       │
│       └── HttpCase                 ← FOR WEBSITE/API                         │
│           • Starts real HTTP server on localhost                              │
│           • Supports phantom_js() / browser_js()                              │
│           • Supports jsonrpc() / url_open()                                   │
│           • Full route testing with authentication                            │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### TransactionCase vs HttpCase vs SavepointCase

| Feature | TransactionCase | SavepointCase | HttpCase |
|---------|----------------|---------------|----------|
| DB Isolation | Per test (rollback) | Per class (savepoints) | Per test (rollback) |
| HTTP server | No | No | Yes (localhost) |
| Speed | Fast | Medium | Slow |
| Best for | ORM/business logic | Exception testing | Routes, UI, JSON |
| Auth control | Direct `self.env` | Direct `self.env` | `self.authenticate()` |
| Access | `env.user` | `env.user` | Via HTTP session |

### When to Use Each

```python
# TransactionCase - Business logic, CRUD, compute, constraints, workflows
class TestSaleOrder(TransactionCase):
    def test_order_confirmation(self):
        order = self.env['sale.order'].create({...})
        order.action_confirm()
        self.assertEqual(order.state, 'sale')

# HttpCase - Website routes, API endpoints, authenticated pages
class TestWebsiteController(HttpCase):
    def test_shop_page(self):
        self.authenticate('admin', 'admin')
        res = self.url_open('/shop')
        self.assertEqual(res.status_code, 200)

# SavepointCase - When you need to test that an exception rolls back properly
class TestConstraints(TransactionCase):
    def test_constraint_rollback(self):
        with self.assertRaises(ValidationError):
            self.env['my.model'].create({'required_field': False})
```

---

## Test Tagging System

### Tag Decorator Reference

```python
from odoo.tests import tagged

# Most common - runs after all modules installed (stable environment)
@tagged('post_install', '-at_install')
class TestMyModel(TransactionCase):
    pass

# Runs during module install (early execution, limited env)
@tagged('at_install', '-post_install')
class TestEarlyLogic(TransactionCase):
    pass

# Standard tests (default, equivalent to post_install)
@tagged('standard')
class TestStandard(TransactionCase):
    pass

# Explicitly exclude from automatic runs
@tagged('-standard', 'manual')
class TestManualOnly(TransactionCase):
    pass

# Multiple tags
@tagged('post_install', '-at_install', 'sale', 'critical')
class TestSaleIntegration(TransactionCase):
    pass
```

### Tag Precedence Rules

```
Tag with '-' prefix = EXCLUSION (remove from selection)
Tag without '-'    = INCLUSION (add to selection)

Default run: --test-tags=standard
Post-install: --test-tags=post_install (most common for production tests)

Examples:
  --test-tags=post_install           → all post_install tagged tests
  --test-tags=my_module              → all tests in module my_module
  --test-tags=/my_module:MyClass     → specific class in module
  --test-tags=/my_module:MyClass.test_method  → specific method
```

### Built-in Odoo Tags

| Tag | When it runs | Use case |
|-----|-------------|----------|
| `standard` | Default CI runs | Unit tests, business logic |
| `at_install` | During install | Basic module integrity |
| `post_install` | After all installs | Integration, full env tests |
| `slow` | Skipped by default | Long-running tests |
| `external` | Skipped by default | External API tests |
| `multi_company` | Special flag | Multi-company scenarios |

---

## Writing Tests

### Complete CRUD Test Pattern

```python
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError, UserError

@tagged('post_install', '-at_install')
class TestMyModel(TransactionCase):
    """Test suite for my.model CRUD operations and business logic."""

    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures shared across all tests in this class.
        Called once before any test method in the class.
        """
        super().setUpClass()
        # Create shared records (not rolled back between tests)
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@example.com',
        })
        cls.currency = cls.env.ref('base.USD')
        cls.company = cls.env.company

    def setUp(self):
        """Set up per-test fixtures. Called before EACH test method."""
        super().setUp()
        # Create fresh records for each test (rolled back after each test)
        self.record = self.env['my.model'].create({
            'name': 'Test Record',
            'partner_id': self.partner.id,
            'amount': 100.0,
        })

    # ─── CREATE TESTS ────────────────────────────────────────────────────────

    def test_create_minimal(self):
        """Test creating a record with only required fields."""
        record = self.env['my.model'].create({'name': 'Minimal'})
        self.assertTrue(record.id, "Record should have been created with an ID")
        self.assertEqual(record.name, 'Minimal')
        self.assertEqual(record.state, 'draft')  # Default state

    def test_create_full(self):
        """Test creating a record with all fields populated."""
        vals = {
            'name': 'Full Record',
            'partner_id': self.partner.id,
            'amount': 1500.50,
            'date': '2024-01-15',
            'notes': 'Test notes',
            'active': True,
        }
        record = self.env['my.model'].create(vals)
        self.assertEqual(record.name, vals['name'])
        self.assertEqual(record.partner_id, self.partner)
        self.assertAlmostEqual(record.amount, 1500.50, places=2)

    def test_create_required_field_missing(self):
        """Test that creating without required fields raises an error."""
        with self.assertRaises(Exception):
            self.env['my.model'].create({})  # Missing 'name' (required)

    # ─── READ/SEARCH TESTS ──────────────────────────────────────────────────

    def test_search_by_name(self):
        """Test searching records by name."""
        results = self.env['my.model'].search([('name', '=', 'Test Record')])
        self.assertIn(self.record, results)

    def test_search_domain(self):
        """Test complex domain search."""
        results = self.env['my.model'].search([
            ('amount', '>=', 50.0),
            ('partner_id', '=', self.partner.id),
        ])
        self.assertGreater(len(results), 0)

    def test_name_get(self):
        """Test the display name of the record."""
        name = self.record.display_name
        self.assertIn('Test Record', name)

    # ─── WRITE TESTS ─────────────────────────────────────────────────────────

    def test_write_name(self):
        """Test updating the record name."""
        self.record.write({'name': 'Updated Name'})
        self.assertEqual(self.record.name, 'Updated Name')

    def test_write_amount(self):
        """Test updating a numeric field."""
        self.record.write({'amount': 999.99})
        self.assertAlmostEqual(self.record.amount, 999.99, places=2)

    def test_write_state_transition(self):
        """Test valid state transition."""
        self.record.action_confirm()
        self.assertEqual(self.record.state, 'confirmed')

    # ─── DELETE TESTS ────────────────────────────────────────────────────────

    def test_unlink(self):
        """Test deleting a record."""
        record_id = self.record.id
        self.record.unlink()
        result = self.env['my.model'].search([('id', '=', record_id)])
        self.assertFalse(result, "Record should have been deleted")

    def test_unlink_confirmed_raises(self):
        """Test that confirmed records cannot be deleted."""
        self.record.action_confirm()
        with self.assertRaises(UserError):
            self.record.unlink()
```

### Compute Field Tests

```python
@tagged('post_install', '-at_install')
class TestComputedFields(TransactionCase):

    def test_amount_total_compute(self):
        """Test that amount_total correctly sums line amounts."""
        order = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
        })
        self.env['sale.order.line'].create([
            {
                'order_id': order.id,
                'product_id': self.env.ref('product.product_product_1').id,
                'product_uom_qty': 2,
                'price_unit': 100.0,
            },
            {
                'order_id': order.id,
                'product_id': self.env.ref('product.product_product_2').id,
                'product_uom_qty': 1,
                'price_unit': 50.0,
            },
        ])
        # Force recompute in case it's not stored
        order.invalidate_recordset()
        self.assertAlmostEqual(order.amount_untaxed, 250.0, places=2)

    def test_compute_depends_triggers(self):
        """Test that modifying a dependency triggers recompute."""
        record = self.env['my.model'].create({'base_amount': 100.0, 'tax_rate': 0.15})
        # Verify initial computed value
        self.assertAlmostEqual(record.total_with_tax, 115.0, places=2)
        # Change a dependency and verify recompute
        record.write({'base_amount': 200.0})
        self.assertAlmostEqual(record.total_with_tax, 230.0, places=2)

    def test_stored_compute_persists(self):
        """Test that stored computed fields are saved to the database."""
        record = self.env['my.model'].create({'name': 'Compute Test', 'value': 42})
        record_id = record.id
        # Clear cache and reload from DB
        self.env.cr.execute("SELECT computed_field FROM my_model WHERE id = %s", [record_id])
        row = self.env.cr.fetchone()
        self.assertIsNotNone(row[0], "Stored computed field should be in DB")

    def test_onchange_simulation(self):
        """Test onchange logic by calling the method directly."""
        record = self.env['my.model'].new({'partner_id': self.env.ref('base.res_partner_1').id})
        record._onchange_partner_id()
        # Verify that onchange populated expected fields
        self.assertTrue(record.currency_id, "Currency should be set from partner country")
```

### Constraint Tests

```python
@tagged('post_install', '-at_install')
class TestConstraints(TransactionCase):

    def test_sql_constraint_unique_name(self):
        """Test SQL unique constraint prevents duplicate names."""
        self.env['my.model'].create({'name': 'Unique Name', 'code': 'UNAME'})
        from psycopg2 import IntegrityError
        with self.assertRaises(IntegrityError):
            # Must be in a separate transaction savepoint
            with self.env.cr.savepoint():
                self.env['my.model'].create({'name': 'Different', 'code': 'UNAME'})

    def test_python_constraint_amount_positive(self):
        """Test Python @constrains decorator validation."""
        from odoo.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.env['my.model'].create({'name': 'Negative', 'amount': -100.0})

    def test_python_constraint_date_range(self):
        """Test date range constraint."""
        from odoo.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.env['my.model'].create({
                'name': 'Bad Dates',
                'date_start': '2024-12-31',
                'date_end': '2024-01-01',  # End before start
            })

    def test_constraint_on_write(self):
        """Test that constraints fire on write, not just create."""
        from odoo.exceptions import ValidationError
        record = self.env['my.model'].create({'name': 'Valid', 'amount': 100.0})
        with self.assertRaises(ValidationError):
            record.write({'amount': -50.0})
```

### Wizard Tests

```python
@tagged('post_install', '-at_install')
class TestWizard(TransactionCase):

    def test_wizard_create_and_confirm(self):
        """Test wizard creation and confirmation."""
        record = self.env['my.model'].create({'name': 'Parent', 'amount': 500.0})
        wizard = self.env['my.wizard'].with_context(
            active_model='my.model',
            active_id=record.id,
            active_ids=[record.id],
        ).create({
            'reason': 'Testing cancellation',
        })
        result = wizard.action_confirm()
        # Verify state changed
        self.assertEqual(record.state, 'cancelled')
        # If wizard returns an action, verify structure
        if result:
            self.assertIn('type', result)

    def test_wizard_onchange(self):
        """Test wizard field dependencies."""
        wizard = self.env['my.wizard'].new({
            'partner_id': self.env.ref('base.res_partner_1').id,
        })
        wizard._onchange_partner_id()
        self.assertTrue(wizard.currency_id)

    def test_wizard_required_fields(self):
        """Test wizard raises UserError when required action fields missing."""
        from odoo.exceptions import UserError
        record = self.env['my.model'].create({'name': 'Test'})
        wizard = self.env['my.wizard'].with_context(
            active_ids=[record.id],
        ).create({})
        with self.assertRaises(UserError):
            wizard.action_confirm()
```

---

## HTTP Controller Tests

### Basic Route Testing

```python
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestWebsiteRoutes(HttpCase):
    """Test HTTP routes and website controllers."""

    def test_public_page_accessible(self):
        """Test that a public page returns 200 without authentication."""
        res = self.url_open('/my-page')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Expected Content', res.text)

    def test_authenticated_page_redirects_unauthenticated(self):
        """Test that protected pages redirect to login."""
        res = self.url_open('/my-account')
        # Should redirect to login (302) or show login (200 with login form)
        self.assertIn(res.status_code, [200, 301, 302])

    def test_authenticated_route(self):
        """Test route that requires authentication."""
        self.authenticate('admin', 'admin')
        res = self.url_open('/my-account')
        self.assertEqual(res.status_code, 200)

    def test_portal_user_access(self):
        """Test portal user can access their own records."""
        portal_user = self.env['res.users'].create({
            'name': 'Portal Test User',
            'login': 'portal_test@example.com',
            'groups_id': [(4, self.env.ref('base.group_portal').id)],
        })
        self.authenticate(portal_user.login, 'portal_test@example.com')
        res = self.url_open('/my/orders')
        self.assertEqual(res.status_code, 200)
```

### JSON RPC Controller Testing

```python
@tagged('post_install', '-at_install')
class TestJsonController(HttpCase):
    """Test JSON-RPC API endpoints."""

    def test_json_endpoint_success(self):
        """Test a JSON endpoint returns correct data."""
        self.authenticate('admin', 'admin')
        result = self.jsonrpc(
            url='/web/dataset/call_kw',
            method='execute_kw',
            params={
                'model': 'res.partner',
                'method': 'search_read',
                'args': [[['name', 'ilike', 'Azure']]],
                'kwargs': {'fields': ['name', 'email'], 'limit': 5},
            }
        )
        self.assertIsInstance(result, list)

    def test_custom_json_route(self):
        """Test a custom JSON controller endpoint."""
        self.authenticate('admin', 'admin')
        result = self.jsonrpc(
            url='/api/my-endpoint',
            method='call',
            params={'record_id': 1, 'action': 'validate'},
        )
        self.assertEqual(result.get('status'), 'ok')

    def test_json_route_validation_error(self):
        """Test JSON endpoint returns error structure on invalid input."""
        self.authenticate('admin', 'admin')
        res = self.url_open(
            '/api/my-endpoint',
            data='{"jsonrpc": "2.0", "method": "call", "params": {"record_id": -999}}',
            headers={'Content-Type': 'application/json'},
        )
        data = res.json()
        self.assertIn('error', data)

    def test_post_form_submission(self):
        """Test a POST form submission via website."""
        res = self.url_open(
            '/contact',
            data={
                'name': 'Test Contact',
                'email': 'test@test.com',
                'message': 'Test message from automated test',
            },
        )
        self.assertIn(res.status_code, [200, 302])
```

---

## Mock Data Creation

### Pattern Overview

```python
@classmethod
def setUpClass(cls):
    super().setUpClass()
    # Using env.ref() for existing XML ID records
    cls.partner_azure = cls.env.ref('base.res_partner_1')
    cls.product_service = cls.env.ref('product.product_product_1')
    cls.currency_usd = cls.env.ref('base.USD')
    cls.company_main = cls.env.ref('base.main_company')
    cls.user_admin = cls.env.ref('base.user_admin')

    # Create fresh test records
    cls.partner_test = cls.env['res.partner'].create({
        'name': 'Automated Test Partner',
        'email': 'autotest@example.com',
        'phone': '+1-555-0100',
        'street': '123 Test Street',
        'city': 'Test City',
        'country_id': cls.env.ref('base.us').id,
        'customer_rank': 1,
    })

    cls.product_test = cls.env['product.product'].create({
        'name': 'Test Product',
        'type': 'service',
        'list_price': 100.0,
        'standard_price': 60.0,
        'uom_id': cls.env.ref('uom.product_uom_unit').id,
    })
```

### Creating Realistic Batch Records

```python
def _create_batch_orders(self, count=5):
    """Helper to create multiple test sale orders."""
    partners = self.env['res.partner'].create([
        {
            'name': f'Test Partner {i}',
            'email': f'partner{i}@test.com',
        }
        for i in range(count)
    ])
    orders = self.env['sale.order'].create([
        {
            'partner_id': partner.id,
            'date_order': fields.Datetime.now(),
        }
        for partner in partners
    ])
    return orders
```

### Model-Specific Mock Data

```python
# res.partner - Customer
partner = env['res.partner'].create({
    'name': 'Acme Corporation',
    'is_company': True,
    'email': 'contact@acme.com',
    'phone': '+1-800-ACME',
    'street': '100 Main St',
    'city': 'Springfield',
    'state_id': env.ref('base.state_us_53').id,
    'country_id': env.ref('base.us').id,
    'zip': '12345',
    'vat': 'US123456789',
    'customer_rank': 5,
    'supplier_rank': 1,
})

# res.users - Internal User
user = env['res.users'].create({
    'name': 'Test Salesperson',
    'login': 'test_salesperson@company.com',
    'email': 'test_salesperson@company.com',
    'groups_id': [(4, env.ref('sales_team.group_sale_salesman').id)],
    'company_id': env.company.id,
    'company_ids': [(4, env.company.id)],
})

# product.product - Storable Product
product = env['product.product'].create({
    'name': 'Office Chair',
    'type': 'product',  # storable
    'list_price': 299.99,
    'standard_price': 150.00,
    'categ_id': env.ref('product.product_category_all').id,
    'uom_id': env.ref('uom.product_uom_unit').id,
    'uom_po_id': env.ref('uom.product_uom_unit').id,
})

# sale.order - Sales Order with Lines
sale_order = env['sale.order'].create({
    'partner_id': partner.id,
    'partner_invoice_id': partner.id,
    'partner_shipping_id': partner.id,
    'date_order': fields.Datetime.now(),
    'validity_date': fields.Date.add(fields.Date.today(), days=30),
    'order_line': [(0, 0, {
        'product_id': product.id,
        'product_uom_qty': 3,
        'price_unit': 299.99,
    })],
})

# account.move - Vendor Bill
bill = env['account.move'].create({
    'move_type': 'in_invoice',
    'partner_id': partner.id,
    'invoice_date': fields.Date.today(),
    'invoice_date_due': fields.Date.add(fields.Date.today(), days=30),
    'currency_id': env.ref('base.USD').id,
    'invoice_line_ids': [(0, 0, {
        'name': 'Services rendered',
        'quantity': 10,
        'price_unit': 200.0,
        'account_id': env['account.account'].search([
            ('account_type', '=', 'expense'),
        ], limit=1).id,
    })],
})

# hr.employee - Employee
employee = env['hr.employee'].create({
    'name': 'John Doe',
    'job_id': env.ref('hr.job_consultant').id,
    'department_id': env.ref('hr.dep_it').id,
    'work_email': 'john.doe@company.com',
    'work_phone': '+1-555-0101',
    'company_id': env.company.id,
    'resource_calendar_id': env.ref('resource.resource_calendar_std').id,
})

# stock.picking - Delivery Order
picking = env['stock.picking'].create({
    'partner_id': partner.id,
    'picking_type_id': env.ref('stock.picking_type_out').id,
    'location_id': env.ref('stock.stock_location_stock').id,
    'location_dest_id': env.ref('stock.stock_location_customers').id,
    'move_ids': [(0, 0, {
        'name': product.name,
        'product_id': product.id,
        'product_uom_qty': 5,
        'product_uom': product.uom_id.id,
        'location_id': env.ref('stock.stock_location_stock').id,
        'location_dest_id': env.ref('stock.stock_location_customers').id,
    })],
})
```

---

## Test Isolation

### Transaction Rollback Mechanism

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     TRANSACTION ISOLATION IN TESTS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Database State:  [module data] [demo data] [setUpClass data]                │
│                                                                               │
│  SAVEPOINT ──────────────────────────────────────────────────────────────── │
│  │  test_one()  → create records → assert → ROLLBACK to savepoint           │
│  │                                                                           │
│  SAVEPOINT ──────────────────────────────────────────────────────────────── │
│  │  test_two()  → create records → assert → ROLLBACK to savepoint           │
│  │                                                                           │
│  SAVEPOINT ──────────────────────────────────────────────────────────────── │
│  │  test_three() → create records → assert → ROLLBACK to savepoint          │
│                                                                               │
│  After ALL tests: ROLLBACK entire setUpClass data                            │
│  Database returns to exactly pre-test state                                  │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### SetUp and TearDown Patterns

```python
@tagged('post_install', '-at_install')
class TestWithSetup(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """Runs ONCE before all tests. Use for expensive operations."""
        super().setUpClass()
        # These records persist across all test methods in this class
        cls.company = cls.env.ref('base.main_company')
        cls.currency = cls.env.ref('base.USD')
        cls.partner = cls.env['res.partner'].create({
            'name': 'Shared Test Partner',
            'email': 'shared@test.com',
        })
        # Disable mail sending during tests
        cls.env = cls.env(context=dict(cls.env.context, no_mail_send=True))

    def setUp(self):
        """Runs BEFORE each test method. Use for per-test state."""
        super().setUp()
        # Fresh record per test, automatically rolled back
        self.record = self.env['my.model'].create({
            'name': 'Per-Test Record',
            'partner_id': self.partner.id,
        })

    @classmethod
    def tearDownClass(cls):
        """Runs ONCE after all tests in class. Clean up class-level resources."""
        # Usually not needed - transaction rollback handles cleanup
        super().tearDownClass()

    def tearDown(self):
        """Runs AFTER each test method."""
        # Usually not needed - savepoint rollback handles cleanup
        super().tearDown()

    def test_example(self):
        # self.partner is available (from setUpClass)
        # self.record is fresh (from setUp)
        self.assertTrue(self.record.id)
```

### Disabling Side Effects in Tests

```python
# Prevent emails from being sent
def setUp(self):
    super().setUp()
    # Method 1: Context flag
    self.env = self.env(context={**self.env.context, 'mail_notrack': True})

    # Method 2: Mock the send method
    def _mock_send(self, *args, **kwargs):
        return True
    self.patch(type(self.env['mail.mail']), '_send', _mock_send)

# Prevent scheduled actions
def setUp(self):
    super().setUp()
    self.env['ir.config_parameter'].sudo().set_param(
        'mail.catchall.domain', 'test.example.com'
    )

# Bypass security for testing business logic only
def test_without_security(self):
    record = self.env['my.model'].sudo().create({'name': 'Test'})
    # Uses sudo() to bypass access rights - focus on business logic
```

---

## Running Tests

### By Module

```bash
# Install and test a module
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable -i my_module --stop-after-init

# Update and test an existing module
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable -u my_module --stop-after-init

# Test multiple modules
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable -u module1,module2 --stop-after-init
```

### By Tags

```bash
# Run only post_install tagged tests
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable --test-tags=post_install --stop-after-init

# Run standard tests only
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable --test-tags=standard --stop-after-init

# Run tests for specific module
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable --test-tags=my_module --stop-after-init
```

### By Class or Method

```bash
# Run a specific test class
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable --test-tags=/my_module:TestMyModel --stop-after-init

# Run a specific test method
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable --test-tags=/my_module:TestMyModel.test_create --stop-after-init

# Exclude a tag and run the rest
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable --test-tags=standard,-slow --stop-after-init
```

### Test Output Interpretation

```
[INFO] odoo.tests.result: STARTING tests
[INFO] odoo.tests: Computed test module list for test runner
[OK] odoo.tests: my_module.tests.test_my_model.TestMyModel.test_create_minimal
[OK] odoo.tests: my_module.tests.test_my_model.TestMyModel.test_create_full
[FAIL] odoo.tests: my_module.tests.test_my_model.TestMyModel.test_constraint_fails
  AssertionError: ValidationError not raised
[ERROR] odoo.tests: my_module.tests.test_my_model.TestMyModel.test_db_access
  psycopg2.OperationalError: database connection closed

[INFO] Ran 3 tests in 4.231s
[ERROR] 1 error, 1 failure
```

### Log Level for Test Debugging

```bash
# Verbose test output
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable -u my_module \
    --log-level=debug --log-handler=odoo.tests:DEBUG \
    --stop-after-init

# Show test SQL queries
python -m odoo -c conf/project17.conf -d project17 \
    --test-enable -u my_module \
    --log-level=debug --log-handler=odoo.sql_db:DEBUG \
    --stop-after-init
```

---

## Coverage Analysis

### Manual Coverage Inspection Pattern

To find untested methods in your module:

1. List all public methods in your model files
2. Cross-reference against test files
3. Calculate coverage percentage

```python
# Example: Find methods without tests using coverage_reporter.py
python coverage_reporter.py \
    --module /c/odoo/odoo17/projects/myproject/my_module \
    --output report.json
```

### Python Coverage with odoo-coverage

```bash
# Install coverage tool
pip install coverage

# Run with coverage measurement
coverage run --source=my_module \
    -m odoo -c conf/project17.conf -d project17 \
    --test-enable -u my_module --stop-after-init

# Generate HTML report
coverage html -d htmlcov/

# Generate terminal report
coverage report --show-missing
```

### Coverage Configuration (.coveragerc)

```ini
[run]
source = my_module
omit =
    my_module/tests/*
    my_module/migrations/*
    my_module/__manifest__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if TYPE_CHECKING:
    @abstractmethod

[html]
directory = htmlcov
title = My Module Test Coverage
```

### Coverage Targets by Code Type

| Code Type | Target Coverage | Rationale |
|-----------|----------------|-----------|
| Business logic methods | 90%+ | Critical paths must be tested |
| Compute fields | 85%+ | Core data integrity |
| Constraints | 100% | Security and data integrity |
| Controllers (HTTP routes) | 80%+ | API contract validation |
| Wizards | 75%+ | User workflow coverage |
| XML views | N/A | Tested via integration |
| `__manifest__.py` | N/A | Not executable logic |

---

## Integration with DevOps

### Azure DevOps Pipeline Integration

```yaml
# azure-pipelines.yml - Odoo Test Stage
stages:
  - stage: OdooTests
    displayName: 'Odoo Module Tests'
    jobs:
      - job: RunTests
        displayName: 'Run Unit and Integration Tests'
        pool:
          vmImage: 'ubuntu-22.04'
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.10'

          - script: |
              pip install -r requirements.txt
            displayName: 'Install Dependencies'

          - script: |
              python -m odoo \
                -c conf/test.conf \
                -d test_db \
                --test-enable \
                -u my_module \
                --stop-after-init \
                --log-level=test \
                2>&1 | tee test_output.log
            displayName: 'Run Odoo Tests'

          - task: PublishTestResults@2
            condition: always()
            inputs:
              testResultsFormat: 'JUnit'
              testResultsFiles: 'test_results.xml'
              testRunTitle: 'Odoo Module Tests'
              failTaskOnFailedTests: true
```

### Generating JUnit XML from Odoo Tests

```python
# test_runner.py handles this - generates JUnit XML compatible output
# Usage:
python test_runner.py \
    --module my_module \
    --config conf/project17.conf \
    --database project17 \
    --output-format junit \
    --output test_results.xml
```

### Posting Results to Azure DevOps API

```python
import requests
import base64

def post_test_results_to_azure(
    organization, project, pat_token,
    test_run_name, results
):
    """Post test results to Azure DevOps Test Plans."""
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(
            f':{pat_token}'.encode()
        ).decode(),
        'Content-Type': 'application/json',
    }
    base_url = f'https://dev.azure.com/{organization}/{project}/_apis'

    # Create test run
    run_response = requests.post(
        f'{base_url}/test/runs?api-version=7.0',
        headers=headers,
        json={
            'name': test_run_name,
            'isAutomated': True,
            'state': 'InProgress',
        }
    )
    run_id = run_response.json()['id']

    # Add test results
    test_results = [
        {
            'testCaseTitle': r['name'],
            'automatedTestName': r['full_name'],
            'outcome': 'Passed' if r['passed'] else 'Failed',
            'durationInMs': r['duration_ms'],
            'errorMessage': r.get('error', ''),
            'stackTrace': r.get('traceback', ''),
        }
        for r in results
    ]
    requests.post(
        f'{base_url}/test/runs/{run_id}/results?api-version=7.0',
        headers=headers,
        json=test_results,
    )

    # Complete test run
    requests.patch(
        f'{base_url}/test/runs/{run_id}?api-version=7.0',
        headers=headers,
        json={'state': 'Completed'},
    )
    return run_id
```

---

## Common Test Patterns by Module Type

### Sales Module Tests

```python
@tagged('post_install', '-at_install')
class TestSaleOrders(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref('base.res_partner_1')
        cls.product = cls.env.ref('product.product_product_5')
        cls.pricelist = cls.env.ref('product.list0')

    def _create_sale_order(self, qty=1, price=100.0):
        """Helper to create a minimal sale order."""
        return self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': qty,
                'price_unit': price,
            })],
        })

    def test_create_sale_order(self):
        """Test creating a sale order in draft state."""
        order = self._create_sale_order()
        self.assertEqual(order.state, 'draft')
        self.assertEqual(len(order.order_line), 1)

    def test_confirm_sale_order(self):
        """Test confirming a sale order changes state to 'sale'."""
        order = self._create_sale_order()
        order.action_confirm()
        self.assertEqual(order.state, 'sale')

    def test_invoice_from_sale_order(self):
        """Test creating an invoice from a confirmed sale order."""
        order = self._create_sale_order(qty=2, price=500.0)
        order.action_confirm()
        # Create invoice
        invoice = order._create_invoices()
        self.assertTrue(invoice)
        self.assertEqual(invoice.move_type, 'out_invoice')
        self.assertEqual(invoice.state, 'draft')
        # Post the invoice
        invoice.action_post()
        self.assertEqual(invoice.state, 'posted')
        self.assertAlmostEqual(invoice.amount_untaxed, 1000.0, places=2)

    def test_cancel_sale_order(self):
        """Test cancelling a draft order."""
        order = self._create_sale_order()
        order.action_cancel()
        self.assertEqual(order.state, 'cancel')

    def test_cancel_confirmed_order_raises(self):
        """Test that cancelling a confirmed order with stock moves raises error."""
        from odoo.exceptions import UserError
        order = self._create_sale_order()
        order.action_confirm()
        # Depending on stock integration, this may raise UserError
        # This test documents expected behavior
```

### HR Module Tests

```python
@tagged('post_install', '-at_install')
class TestHREmployee(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.department = cls.env['hr.department'].create({
            'name': 'Test IT Department',
        })
        cls.job = cls.env['hr.job'].create({
            'name': 'Test Software Engineer',
            'department_id': cls.department.id,
        })

    def _create_employee(self, name='Test Employee'):
        return self.env['hr.employee'].create({
            'name': name,
            'job_id': self.job.id,
            'department_id': self.department.id,
            'work_email': f'{name.lower().replace(" ", ".")}@company.com',
            'company_id': self.env.company.id,
        })

    def test_create_employee(self):
        """Test creating an employee."""
        emp = self._create_employee()
        self.assertTrue(emp.id)
        self.assertEqual(emp.department_id, self.department)

    def test_employee_archive(self):
        """Test archiving an employee."""
        emp = self._create_employee('Archive Me')
        emp.toggle_active()
        self.assertFalse(emp.active)

    def test_attendance_checkin(self):
        """Test employee check-in if hr_attendance is installed."""
        if 'hr.attendance' not in self.env:
            self.skipTest("hr_attendance module not installed")
        emp = self._create_employee()
        attendance = self.env['hr.attendance'].create({
            'employee_id': emp.id,
            'check_in': fields.Datetime.now(),
        })
        self.assertTrue(attendance.id)
```

### Account Module Tests

```python
@tagged('post_install', '-at_install')
class TestAccountMove(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref('base.res_partner_2')
        cls.account_receivable = cls.env['account.account'].search([
            ('account_type', '=', 'asset_receivable'),
            ('company_id', '=', cls.env.company.id),
        ], limit=1)
        cls.account_revenue = cls.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('company_id', '=', cls.env.company.id),
        ], limit=1)

    def _create_invoice(self, amount=100.0):
        return self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': 'Test Service',
                'quantity': 1,
                'price_unit': amount,
                'account_id': self.account_revenue.id,
            })],
        })

    def test_create_draft_invoice(self):
        """Test creating a draft invoice."""
        invoice = self._create_invoice()
        self.assertEqual(invoice.state, 'draft')
        self.assertAlmostEqual(invoice.amount_untaxed, 100.0, places=2)

    def test_post_invoice(self):
        """Test posting (confirming) an invoice."""
        invoice = self._create_invoice(500.0)
        invoice.action_post()
        self.assertEqual(invoice.state, 'posted')
        self.assertTrue(invoice.name)  # Name assigned on posting

    def test_register_payment(self):
        """Test registering a payment against an invoice."""
        invoice = self._create_invoice(200.0)
        invoice.action_post()
        # Register payment
        payment_wizard = self.env['account.payment.register'].with_context(
            active_model='account.move',
            active_ids=invoice.ids,
        ).create({
            'payment_date': fields.Date.today(),
            'amount': 200.0,
        })
        payment_wizard.action_create_payments()
        self.assertEqual(invoice.payment_state, 'paid')
```

### Inventory / Stock Tests

```python
@tagged('post_install', '-at_install')
class TestInventory(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Test Storable',
            'type': 'product',
        })
        cls.warehouse = cls.env.ref('stock.warehouse0')
        cls.location_stock = cls.env.ref('stock.stock_location_stock')
        cls.location_customer = cls.env.ref('stock.stock_location_customers')

    def test_create_picking(self):
        """Test creating a stock picking."""
        picking = self.env['stock.picking'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.location_stock.id,
            'location_dest_id': self.location_customer.id,
            'move_ids': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 5.0,
                'product_uom': self.product.uom_id.id,
                'location_id': self.location_stock.id,
                'location_dest_id': self.location_customer.id,
            })],
        })
        self.assertEqual(picking.state, 'draft')
        self.assertEqual(len(picking.move_ids), 1)

    def test_validate_picking(self):
        """Test validating a picking (immediate transfer)."""
        # First ensure stock is available
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': self.product.id,
            'location_id': self.location_stock.id,
            'quantity': 100.0,
        })
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.location_stock.id,
            'location_dest_id': self.location_customer.id,
            'move_ids': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 5.0,
                'product_uom': self.product.uom_id.id,
                'location_id': self.location_stock.id,
                'location_dest_id': self.location_customer.id,
            })],
        })
        picking.action_confirm()
        picking.action_assign()
        # Set done quantities
        for move_line in picking.move_line_ids:
            move_line.qty_done = move_line.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, 'done')
```

---

## Version Compatibility

### Test Framework Differences Odoo 14-19

| Feature | Odoo 14 | Odoo 15 | Odoo 16 | Odoo 17 | Odoo 18 | Odoo 19 |
|---------|---------|---------|---------|---------|---------|---------|
| `SavepointCase` | Yes | Yes | Deprecated | Removed | Removed | Removed |
| `TransactionCase` | Yes | Yes | Yes | Yes | Yes | Yes |
| `HttpCase` | Yes | Yes | Yes | Yes | Yes | Yes |
| `--test-tags` format | Basic | Basic | Enhanced | Enhanced | Enhanced | Enhanced |
| `setUpClass` | Yes | Yes | Yes | Yes | Yes | Yes |
| `assertRaises` context | Yes | Yes | Yes | Yes | Yes | Yes |
| `browser_js` | Yes | Yes | Yes | Deprecated | Removed | Removed |
| `phantom_js` | Yes | Yes | Yes | Yes | Yes | Yes |
| Mock `patch` in base | Manual | Manual | Built-in | Built-in | Built-in | Built-in |

### Version-Specific Import Changes

```python
# Odoo 14 - SavepointCase still valid
from odoo.tests.common import SavepointCase, TransactionCase, HttpCase

# Odoo 15 - SavepointCase deprecated
from odoo.tests.common import TransactionCase, HttpCase
from odoo.tests import tagged

# Odoo 16-19 - Use TransactionCase with savepoints for rollback control
from odoo.tests import TransactionCase, HttpCase, tagged
# SavepointCase was removed; use TransactionCase with self.cr.savepoint()
```

### Version-Safe Test Template

```python
# Works across Odoo 14-19
try:
    from odoo.tests.common import SavepointCase as TestBase
except ImportError:
    from odoo.tests.common import TransactionCase as TestBase

from odoo.tests import tagged

@tagged('post_install', '-at_install')
class TestCompatible(TestBase):
    """Version-compatible test class."""
    pass
```

### Field API Changes

```python
# Odoo 14-15: fields.Date.from_string('2024-01-01')
# Odoo 16+:   fields.Date.to_date('2024-01-01')  (also works in 14-15)

# Odoo 14-16: self.env['ir.sequence'].next_by_code('my.sequence')
# Odoo 17+:   Same API - no change

# Odoo 14-17: order.write({'state': 'cancel'})
# Odoo 18+:   May require specific action methods depending on model
```

---

## Troubleshooting

### Common Test Failures and Fixes

#### 1. Module Not Found in Test Discovery

```
ERROR: no test found in my_module
```

**Fix**: Ensure `tests/` directory has `__init__.py` and imports test files:

```python
# my_module/tests/__init__.py
from . import test_my_model
from . import test_other
```

Also ensure `__manifest__.py` has:
```python
'installable': True,
# No 'tests' key needed - discovered automatically
```

#### 2. ImportError in Test File

```
ImportError: cannot import name 'SavepointCase' from 'odoo.tests.common'
```

**Fix**: Replace `SavepointCase` with `TransactionCase` (removed in Odoo 16).

#### 3. Access Rights Error

```
AccessError: my_module.my_model: Permission denied
```

**Fix**: Use `.sudo()` for admin-level test setup, or add user to proper group:

```python
def setUp(self):
    super().setUp()
    # Use admin env for setup
    self.record = self.env['my.model'].sudo().create({...})

    # Or add current user to required group
    self.env.user.write({
        'groups_id': [(4, self.env.ref('my_module.group_manager').id)]
    })
```

#### 4. Database Not Reset Between Tests

```
# If setUpClass data is being modified by tests unintentionally:
```

**Fix**: Never mutate `cls.*` attributes in test methods. Use `setUp` for mutable records.

#### 5. Compute Field Not Triggering

```
AssertionError: 0 != 100.0 (computed field returned default)
```

**Fix**: Invalidate cache after dependency changes:

```python
record.write({'base_amount': 200.0})
record.invalidate_recordset(['total_amount'])  # Odoo 16+
# Or
record._compute_total_amount()  # Direct call for stored fields
```

#### 6. Email Sent During Tests (Slows Execution)

**Fix**: Disable mail tracking in context:

```python
@classmethod
def setUpClass(cls):
    super().setUpClass()
    cls.env = cls.env(context={
        **cls.env.context,
        'mail_notrack': True,
        'no_reset_password': True,
        'tracking_disable': True,
    })
```

#### 7. Test Timing Out

```
Test exceeded maximum time limit (300s)
```

**Fix**: Split slow tests, use `@tagged('slow')` to exclude from regular CI:

```python
@tagged('slow', 'post_install', '-at_install', '-standard')
class TestSlowIntegration(TransactionCase):
    pass
```

#### 8. PostgreSQL Integrity Error in Test

```
psycopg2.errors.UniqueViolation: duplicate key value
```

**Fix**: Use savepoints to catch expected DB errors:

```python
def test_unique_constraint(self):
    self.env['my.model'].create({'code': 'UNIQUE'})
    with self.assertRaises(Exception):
        with self.env.cr.savepoint():
            self.env['my.model'].create({'code': 'UNIQUE'})
```

#### 9. HttpCase Authentication Fails

```
AssertionError: Expected 200, got 403
```

**Fix**: Ensure user exists and password is correct:

```python
def test_requires_admin(self):
    # Use built-in admin (always available in tests)
    self.authenticate('admin', 'admin')
    res = self.url_open('/admin-only-route')
    self.assertEqual(res.status_code, 200)
```

#### 10. Field Not Found on Model

```
AttributeError: 'my.model' model has no field 'my_field'
```

**Fix**: Ensure module with the field is in `depends` in `__manifest__.py` and installed in test DB.

---

## Quick Snippets

### Assert Methods Reference

```python
# Equality
self.assertEqual(a, b)          # a == b
self.assertNotEqual(a, b)       # a != b
self.assertAlmostEqual(a, b, places=2)  # float comparison
self.assertIs(a, b)             # a is b (identity)
self.assertIsNone(a)            # a is None
self.assertIsNotNone(a)         # a is not None

# Boolean
self.assertTrue(x)              # bool(x) is True
self.assertFalse(x)             # bool(x) is False

# Membership
self.assertIn(a, b)             # a in b
self.assertNotIn(a, b)          # a not in b
self.assertIn(record, recordset)  # Odoo recordset check

# Collections
self.assertEqual(len(records), 3)  # Count check
self.assertGreater(len(records), 0)

# Exceptions
self.assertRaises(ValidationError, lambda: record.write({...}))
with self.assertRaises(UserError) as ctx:
    record.action_confirm()
self.assertIn('specific message', str(ctx.exception))

# Recordsets (Odoo-specific patterns)
self.assertFalse(empty_recordset)
self.assertTrue(non_empty_recordset)
self.assertEqual(record, expected_record)  # Recordset equality
```

### Useful Test Utilities

```python
# Skip test conditionally
def test_feature(self):
    if not self.env['account.move']._module_installed('account_lock'):
        self.skipTest('account_lock module not installed')
    # ...

# Generate unique names to avoid conflicts
import uuid
unique_name = f'Test_{uuid.uuid4().hex[:8]}'

# Freeze time (Odoo 16+)
from unittest.mock import patch
from datetime import date
with patch('odoo.fields.Date.today', return_value=date(2024, 6, 15)):
    record = self.env['my.model'].create({'date': fields.Date.today()})
    self.assertEqual(record.date, date(2024, 6, 15))

# Access Odoo configuration
param_value = self.env['ir.config_parameter'].sudo().get_param('my.param')

# Run as different user
record_as_user = record.with_user(self.env.ref('base.user_demo'))
```

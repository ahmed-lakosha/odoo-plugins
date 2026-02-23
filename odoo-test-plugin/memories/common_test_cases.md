# Common Odoo Test Cases by Module

Ready-to-adapt test patterns for the most common Odoo module types.

---

## Sales Order Tests (sale module)

```python
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError
from odoo import fields


@tagged('post_install', '-at_install')
class TestSaleOrder(TransactionCase):
    """Complete test suite for sale.order workflow."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context={**cls.env.context, 'mail_notrack': True})
        cls.partner = cls.env.ref('base.res_partner_1')
        cls.product_service = cls.env.ref('product.product_product_1')
        cls.product_storable = cls.env['product.product'].create({
            'name': 'Test Storable',
            'type': 'product',
            'list_price': 100.0,
            'standard_price': 60.0,
        })

    def _create_order(self, qty=1, price=100.0, partner=None):
        """Helper: create a minimal sale order."""
        return self.env['sale.order'].create({
            'partner_id': (partner or self.partner).id,
            'order_line': [(0, 0, {
                'product_id': self.product_service.id,
                'product_uom_qty': qty,
                'price_unit': price,
            })],
        })

    def test_create_in_draft_state(self):
        order = self._create_order()
        self.assertEqual(order.state, 'draft')
        self.assertEqual(len(order.order_line), 1)

    def test_amount_total_calculation(self):
        order = self._create_order(qty=3, price=200.0)
        # Without tax
        self.assertAlmostEqual(order.amount_untaxed, 600.0, places=2)

    def test_confirm_order(self):
        order = self._create_order()
        order.action_confirm()
        self.assertEqual(order.state, 'sale')
        self.assertTrue(order.name)  # Name should be assigned (SO0001, etc.)

    def test_cancel_draft_order(self):
        order = self._create_order()
        order.action_cancel()
        self.assertEqual(order.state, 'cancel')

    def test_create_invoice_from_confirmed_order(self):
        order = self._create_order(qty=2, price=500.0)
        order.action_confirm()
        # Mark as qty_delivered for service products
        order.order_line.write({'qty_delivered': 2.0})
        # Create invoice
        invoices = order._create_invoices()
        self.assertTrue(invoices)
        self.assertEqual(invoices.move_type, 'out_invoice')
        self.assertAlmostEqual(invoices.amount_untaxed, 1000.0, places=2)

    def test_post_invoice(self):
        order = self._create_order(qty=1, price=300.0)
        order.action_confirm()
        order.order_line.write({'qty_delivered': 1.0})
        invoice = order._create_invoices()
        invoice.action_post()
        self.assertEqual(invoice.state, 'posted')

    def test_lock_confirmed_order(self):
        """Confirmed orders can be locked to prevent modification."""
        order = self._create_order()
        order.action_confirm()
        order.action_lock()
        self.assertEqual(order.locked, True)

    def test_multiple_lines(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                (0, 0, {'product_id': self.product_service.id, 'product_uom_qty': 2, 'price_unit': 100}),
                (0, 0, {'product_id': self.product_service.id, 'product_uom_qty': 3, 'price_unit': 50}),
            ],
        })
        self.assertEqual(len(order.order_line), 2)
        self.assertAlmostEqual(order.amount_untaxed, 350.0, places=2)

    def test_copy_order(self):
        """Copying an order creates a new draft order."""
        order = self._create_order()
        order.action_confirm()
        copy = order.copy()
        self.assertEqual(copy.state, 'draft')
        self.assertEqual(len(copy.order_line), len(order.order_line))
```

---

## HR Employee Tests (hr module)

```python
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError
from odoo import fields


@tagged('post_install', '-at_install')
class TestHREmployee(TransactionCase):
    """Tests for hr.employee model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context={**cls.env.context, 'mail_notrack': True})
        cls.department = cls.env['hr.department'].create({
            'name': 'Test Department',
        })
        cls.job_position = cls.env['hr.job'].create({
            'name': 'Test Engineer',
            'department_id': cls.department.id,
            'expected_employees': 5,
        })

    def _create_employee(self, name='Test Employee', **kwargs):
        vals = {
            'name': name,
            'department_id': self.department.id,
            'job_id': self.job_position.id,
            'work_email': f'{name.lower().replace(" ", ".")}@company.com',
            'company_id': self.env.company.id,
        }
        vals.update(kwargs)
        return self.env['hr.employee'].create(vals)

    def test_create_employee(self):
        emp = self._create_employee('John Doe')
        self.assertEqual(emp.name, 'John Doe')
        self.assertEqual(emp.department_id, self.department)
        self.assertTrue(emp.active)

    def test_employee_display_name(self):
        emp = self._create_employee('Jane Smith')
        self.assertIn('Jane Smith', emp.display_name)

    def test_archive_employee(self):
        emp = self._create_employee('Archive Me')
        self.assertTrue(emp.active)
        emp.toggle_active()
        self.assertFalse(emp.active)

    def test_employee_work_email_required(self):
        """Work email format validation (if implemented)."""
        emp = self._create_employee('Valid Email')
        self.assertTrue(emp.work_email)

    def test_department_link(self):
        emp = self._create_employee()
        self.assertEqual(emp.department_id, self.department)
        # Change department
        new_dept = self.env['hr.department'].create({'name': 'New Department'})
        emp.write({'department_id': new_dept.id})
        self.assertEqual(emp.department_id, new_dept)

    def test_employee_contract(self):
        """Test creating a contract for an employee (if hr_contract installed)."""
        if 'hr.contract' not in self.env:
            self.skipTest("hr_contract module not installed")
        emp = self._create_employee()
        contract = self.env['hr.contract'].create({
            'name': f'{emp.name} - Contract',
            'employee_id': emp.id,
            'date_start': fields.Date.today(),
            'wage': 5000.0,
            'state': 'open',
        })
        self.assertEqual(contract.employee_id, emp)
        self.assertAlmostEqual(contract.wage, 5000.0, places=2)

    def test_attendance_checkin(self):
        """Test check-in/check-out (if hr_attendance installed)."""
        if 'hr.attendance' not in self.env:
            self.skipTest("hr_attendance module not installed")
        emp = self._create_employee()
        attendance = self.env['hr.attendance'].create({
            'employee_id': emp.id,
            'check_in': fields.Datetime.now(),
        })
        self.assertTrue(attendance.id)
        attendance.write({
            'check_out': fields.Datetime.add(attendance.check_in, hours=8)
        })
        self.assertAlmostEqual(attendance.worked_hours, 8.0, places=1)
```

---

## Website / Portal Tests (HttpCase)

```python
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestWebsitePages(HttpCase):
    """Tests for website controller routes."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Portal Test Partner',
            'email': 'portal@example.com',
        })
        # Create portal user
        cls.portal_user = cls.env['res.users'].create({
            'name': 'Portal User',
            'login': 'test_portal_user@example.com',
            'email': 'test_portal_user@example.com',
            'partner_id': cls.partner.id,
            'groups_id': [(4, cls.env.ref('base.group_portal').id)],
        })

    def test_homepage_public(self):
        """Homepage accessible without authentication."""
        res = self.url_open('/')
        self.assertEqual(res.status_code, 200)

    def test_shop_public(self):
        """Shop page accessible without authentication (if website_sale)."""
        if 'website.sale' not in self.env:
            self.skipTest("website_sale not installed")
        res = self.url_open('/shop')
        self.assertEqual(res.status_code, 200)

    def test_protected_page_redirects(self):
        """Protected page redirects unauthenticated users."""
        res = self.url_open('/my/home', allow_redirects=False)
        # Should redirect to login
        self.assertIn(res.status_code, [302, 301])

    def test_portal_my_home(self):
        """Portal user can access /my/home."""
        self.authenticate(self.portal_user.login, 'test_portal_user@example.com')
        res = self.url_open('/my/home')
        self.assertEqual(res.status_code, 200)

    def test_admin_backend_access(self):
        """Admin user can access backend."""
        self.authenticate('admin', 'admin')
        res = self.url_open('/web#action=')
        # Web client loads successfully
        self.assertEqual(res.status_code, 200)

    def test_json_rpc_search_read(self):
        """JSON-RPC search_read call works for authenticated users."""
        self.authenticate('admin', 'admin')
        result = self.jsonrpc(
            url='/web/dataset/call_kw',
            method='execute_kw',
            params={
                'model': 'res.partner',
                'method': 'search_read',
                'args': [[['customer_rank', '>', 0]]],
                'kwargs': {'fields': ['name', 'email'], 'limit': 5},
            }
        )
        self.assertIsInstance(result, list)

    def test_custom_json_endpoint(self):
        """Test a custom JSON controller route."""
        self.authenticate('admin', 'admin')
        import json
        res = self.url_open(
            '/api/my-custom-endpoint',
            data=json.dumps({'action': 'ping'}),
            headers={'Content-Type': 'application/json'},
        )
        self.assertIn(res.status_code, [200, 404])  # 404 if route not implemented
```

---

## Account Move Tests (account module)

```python
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError
from odoo import fields


@tagged('post_install', '-at_install')
class TestAccountMove(TransactionCase):
    """Tests for account.move (invoices, bills, journal entries)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context={**cls.env.context, 'mail_notrack': True})
        cls.partner_customer = cls.env.ref('base.res_partner_1')
        cls.partner_vendor = cls.env.ref('base.res_partner_2')
        cls.company = cls.env.company

        cls.account_income = cls.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('company_id', '=', cls.company.id),
        ], limit=1)
        cls.account_expense = cls.env['account.account'].search([
            ('account_type', '=', 'expense'),
            ('company_id', '=', cls.company.id),
        ], limit=1)

    def _create_invoice(self, partner=None, amount=1000.0, move_type='out_invoice'):
        account = self.account_income if move_type == 'out_invoice' else self.account_expense
        return self.env['account.move'].create({
            'move_type': move_type,
            'partner_id': (partner or self.partner_customer).id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': 'Test Line',
                'quantity': 1.0,
                'price_unit': amount,
                'account_id': account.id,
            })],
        })

    def test_create_draft_invoice(self):
        inv = self._create_invoice(amount=500.0)
        self.assertEqual(inv.state, 'draft')
        self.assertAlmostEqual(inv.amount_untaxed, 500.0, places=2)

    def test_post_invoice(self):
        inv = self._create_invoice(amount=750.0)
        inv.action_post()
        self.assertEqual(inv.state, 'posted')
        self.assertTrue(inv.name)  # Sequence number assigned

    def test_create_vendor_bill(self):
        bill = self._create_invoice(
            partner=self.partner_vendor,
            amount=300.0,
            move_type='in_invoice'
        )
        self.assertEqual(bill.move_type, 'in_invoice')
        self.assertEqual(bill.state, 'draft')

    def test_reset_to_draft(self):
        inv = self._create_invoice()
        inv.action_post()
        self.assertEqual(inv.state, 'posted')
        inv.button_draft()
        self.assertEqual(inv.state, 'draft')

    def test_cancel_invoice(self):
        inv = self._create_invoice()
        inv.action_post()
        inv.button_cancel()
        self.assertEqual(inv.state, 'cancel')

    def test_register_payment(self):
        """Test full payment flow using account.payment.register wizard."""
        inv = self._create_invoice(amount=1000.0)
        inv.action_post()
        self.assertEqual(inv.payment_state, 'not_paid')

        payment_wizard = self.env['account.payment.register'].with_context(
            active_model='account.move',
            active_ids=inv.ids,
        ).create({
            'payment_date': fields.Date.today(),
            'amount': 1000.0,
        })
        payment_wizard.action_create_payments()
        self.assertIn(inv.payment_state, ['paid', 'in_payment'])

    def test_credit_note(self):
        """Test creating a credit note from a posted invoice."""
        inv = self._create_invoice(amount=500.0)
        inv.action_post()

        # Create reversal (credit note)
        reversal_wizard = self.env['account.move.reversal'].with_context(
            active_model='account.move',
            active_ids=inv.ids,
        ).create({
            'reason': 'Test credit note',
            'journal_id': inv.journal_id.id,
        })
        result = reversal_wizard.reverse_moves()
        # Verify credit note was created
        credit_note = self.env['account.move'].browse(result.get('res_id'))
        self.assertEqual(credit_note.move_type, 'out_refund')
```

---

## Inventory / Stock Tests (stock module)

```python
from odoo.tests import TransactionCase, tagged
from odoo import fields


@tagged('post_install', '-at_install')
class TestStockPicking(TransactionCase):
    """Tests for stock.picking warehouse operations."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context={**cls.env.context, 'mail_notrack': True})
        cls.warehouse = cls.env.ref('stock.warehouse0')
        cls.location_stock = cls.env.ref('stock.stock_location_stock')
        cls.location_customer = cls.env.ref('stock.stock_location_customers')
        cls.location_supplier = cls.env.ref('stock.stock_location_suppliers')
        cls.partner = cls.env.ref('base.res_partner_1')

        cls.product = cls.env['product.product'].create({
            'name': 'Test Storable Product',
            'type': 'product',
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
        })

    def _ensure_stock(self, product, quantity, location=None):
        """Helper: add stock to a location via inventory adjustment."""
        location = location or self.location_stock
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': product.id,
            'location_id': location.id,
            'quantity': quantity,
        })

    def _create_delivery(self, qty=5):
        """Helper: create a delivery order."""
        return self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.location_stock.id,
            'location_dest_id': self.location_customer.id,
            'move_ids': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': float(qty),
                'product_uom': self.product.uom_id.id,
                'location_id': self.location_stock.id,
                'location_dest_id': self.location_customer.id,
            })],
        })

    def test_create_delivery_draft(self):
        picking = self._create_delivery()
        self.assertEqual(picking.state, 'draft')
        self.assertEqual(picking.picking_type_code, 'outgoing')

    def test_confirm_picking(self):
        picking = self._create_delivery()
        picking.action_confirm()
        self.assertEqual(picking.state, 'confirmed')

    def test_reserve_stock(self):
        self._ensure_stock(self.product, 100.0)
        picking = self._create_delivery(qty=10)
        picking.action_confirm()
        picking.action_assign()  # Reserve availability
        self.assertEqual(picking.state, 'assigned')

    def test_validate_picking(self):
        """Full delivery validation."""
        self._ensure_stock(self.product, 50.0)
        picking = self._create_delivery(qty=5)
        picking.action_confirm()
        picking.action_assign()
        # Set done quantities
        for move_line in picking.move_line_ids:
            move_line.qty_done = move_line.reserved_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, 'done')

    def test_receipt_from_vendor(self):
        """Create and validate an incoming shipment."""
        receipt = self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'location_id': self.location_supplier.id,
            'location_dest_id': self.location_stock.id,
            'move_ids': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 20.0,
                'product_uom': self.product.uom_id.id,
                'location_id': self.location_supplier.id,
                'location_dest_id': self.location_stock.id,
            })],
        })
        receipt.action_confirm()
        # Set done quantities for immediate transfer
        receipt.move_ids.write({'quantity': 20.0})
        receipt.button_validate()
        self.assertEqual(receipt.state, 'done')
        # Verify stock increased
        quant = self.env['stock.quant'].search([
            ('product_id', '=', self.product.id),
            ('location_id', '=', self.location_stock.id),
        ])
        self.assertGreater(quant.quantity, 0)

    def test_backorder_creation(self):
        """Test backorder when partial quantity is done."""
        self._ensure_stock(self.product, 100.0)
        picking = self._create_delivery(qty=10)
        picking.action_confirm()
        picking.action_assign()
        # Only deliver 5 of 10
        for ml in picking.move_line_ids:
            ml.qty_done = 5.0
        # Validate — should create backorder
        result = picking.button_validate()
        # Check if backorder dialog triggered
        if result and result.get('res_model') == 'stock.backorder.confirmation':
            backorder_wizard = self.env['stock.backorder.confirmation'].with_context(
                result.get('context', {})
            ).create({'pick_ids': [(4, picking.id)]})
            backorder_wizard.process()
        self.assertEqual(picking.state, 'done')
```

---

## Checklist: Before Submitting Tests

- [ ] All test methods start with `test_`
- [ ] Class decorated with `@tagged('post_install', '-at_install')`
- [ ] `setUpClass` disables mail tracking (`mail_notrack: True`)
- [ ] No hardcoded record IDs (use `env.ref()` or create fixtures)
- [ ] Assertions are specific (`assertEqual` not just `assertTrue`)
- [ ] Negative tests cover error cases (`assertRaises`)
- [ ] Test file is in `tests/` directory with `__init__.py`
- [ ] `__init__.py` imports the test module
- [ ] Module manifest has `'installable': True`
- [ ] Tests pass: `python -m odoo -c conf/project.conf -d db --test-enable -u module --stop-after-init`

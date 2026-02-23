# Mock Data Reference for Odoo Tests

Realistic test fixture values organized by field type and common model.

---

## Realistic Values by Field Type

### Char Fields

```python
# Name fields
'name': 'Ahmed Al-Rashidi'          # Person name
'name': 'Acme Corporation'           # Company name
'name': 'Office Chair Pro'           # Product name
'name': 'Test Record 001'            # Generic test name

# Email
'email': 'ahmed.alrashidi@company.com'
'email_from': 'support@example.com'
'work_email': 'emp001@company.com'

# Phone
'phone': '+966-11-234-5678'          # Saudi
'mobile': '+971-50-123-4567'         # UAE
'work_phone': '+1-555-234-5678'      # US

# Address
'street': '4532 King Fahd Road'
'street2': 'Building 7, Floor 3'
'city': 'Riyadh'
'zip': '12345'

# Reference codes
'ref': 'CUST-001'
'code': 'PRD-2024-001'
'barcode': '978020137962'

# Notes / descriptions
'note': 'High-value customer. Priority handling required.'
'description': 'Premium service package with 24/7 support.'
'internal_note': 'Internal memo: follow up next quarter.'
```

### Integer Fields

```python
'sequence': 10          # Usually multiples of 10
'priority': 1           # 0=Normal, 1=Low, 2=High, 3=Very High
'qty_on_hand': 50
'product_uom_qty': 3
'worked_hours': 8
'day_count': 30
```

### Float Fields

```python
# Prices and amounts
'price_unit': 299.99
'list_price': 1250.00
'standard_price': 750.00
'amount': 5000.00
'cost': 1200.50

# Quantities
'product_uom_qty': 5.0
'qty_done': 3.0
'weight': 2.5           # kg
'volume': 0.015         # m3

# Rates and ratios
'tax_rate': 15.0        # percentage
'discount': 10.0        # percentage
'interest_rate': 3.5    # percentage
```

### Monetary Fields

```python
# Always pair with currency_id
'amount_total': 1150.00
'price_subtotal': 1000.00
'amount_tax': 150.00
'credit_limit': 50000.00
```

### Boolean Fields

```python
'active': True
'is_company': True          # for legal entities
'is_company': False         # for individuals
'customer_rank': 1          # Makes them a customer (integer but Boolean-like)
'to_invoice': True
'is_published': True        # website pages
```

### Date Fields

```python
from odoo import fields

# Today / relative dates
'date': fields.Date.today()
'date_order': fields.Date.today()
'invoice_date': fields.Date.today()

# Future dates
'validity_date': fields.Date.add(fields.Date.today(), days=30)
'date_deadline': fields.Date.add(fields.Date.today(), days=14)
'invoice_date_due': fields.Date.add(fields.Date.today(), days=30)

# Past dates
'date_start': fields.Date.add(fields.Date.today(), days=-365)
'date_from': fields.Date.add(fields.Date.today(), days=-30)

# Specific date (for reproducible tests)
'date': fields.Date.to_date('2024-06-15')
```

### Datetime Fields

```python
from odoo import fields

'date_order': fields.Datetime.now()
'check_in': fields.Datetime.now()
'check_out': fields.Datetime.add(fields.Datetime.now(), hours=8)
'write_date': fields.Datetime.now()

# Specific datetime
import datetime
'datetime_field': datetime.datetime(2024, 6, 15, 9, 0, 0)
```

### Selection Fields

```python
# Always use the raw key string, not the display label
'state': 'draft'            # Not 'Draft'
'move_type': 'out_invoice'  # Not 'Customer Invoice'
'type': 'product'           # Not 'Storable Product'
'priority': '0'             # Often string '0', '1', '2'
'gender': 'male'
'company_type': 'company'

# How to get valid keys programmatically:
valid_keys = [v[0] for v in record._fields['state'].selection]
```

### Many2one Fields

```python
# Using env.ref() for XML IDs (most reliable)
'partner_id': self.env.ref('base.res_partner_1').id
'company_id': self.env.company.id
'currency_id': self.env.ref('base.USD').id
'currency_id': self.env.ref('base.SAR').id   # Saudi Riyal
'country_id': self.env.ref('base.us').id
'country_id': self.env.ref('base.sa').id     # Saudi Arabia
'state_id': self.env.ref('base.state_us_5').id  # California
'uom_id': self.env.ref('uom.product_uom_unit').id
'uom_id': self.env.ref('uom.product_uom_kgm').id
'categ_id': self.env.ref('product.product_category_all').id
'pricelist_id': self.env.ref('product.list0').id
'journal_id': self.env['account.journal'].search([], limit=1).id
'account_id': self.env['account.account'].search([
    ('account_type', '=', 'income')
], limit=1).id
'warehouse_id': self.env.ref('stock.warehouse0').id
'location_id': self.env.ref('stock.stock_location_stock').id
'picking_type_id': self.env.ref('stock.picking_type_out').id
'user_id': self.env.ref('base.user_admin').id
'user_id': self.env.user.id   # Current test user
'team_id': self.env.ref('sales_team.team_sales_department').id
'department_id': self.env.ref('hr.dep_it').id
```

### Many2many Fields

```python
# Command 4 = link existing, 6 = replace all
'tag_ids': [(4, tag_id)]                    # Link one tag
'tag_ids': [(4, tag1_id), (4, tag2_id)]     # Link multiple
'tag_ids': [(6, 0, [tag1_id, tag2_id])]     # Replace all with list

'groups_id': [(4, self.env.ref('base.group_user').id)]
'category_id': [(4, self.env.ref('base.res_partner_category_0').id)]
```

### One2many Fields (Embedded Records)

```python
# Command 0 = create new linked record
'order_line': [(0, 0, {
    'product_id': self.product.id,
    'product_uom_qty': 2.0,
    'price_unit': 100.0,
})]

'invoice_line_ids': [(0, 0, {
    'name': 'Service Description',
    'quantity': 1.0,
    'price_unit': 500.0,
    'account_id': account_id,
})]

'move_ids': [(0, 0, {
    'name': product.name,
    'product_id': product.id,
    'product_uom_qty': 5.0,
    'product_uom': product.uom_id.id,
    'location_id': location_id,
    'location_dest_id': dest_location_id,
})]
```

---

## Common Model Fixtures

### res.partner (Customer/Vendor)

```python
@classmethod
def setUpClass(cls):
    super().setUpClass()
    # Individual contact
    cls.contact = cls.env['res.partner'].create({
        'name': 'Ahmed Al-Rashidi',
        'is_company': False,
        'email': 'ahmed@example.com',
        'phone': '+966-11-234-5678',
        'mobile': '+966-50-987-6543',
        'street': '1234 Olaya Street',
        'city': 'Riyadh',
        'country_id': cls.env.ref('base.sa').id,
        'customer_rank': 1,
        'supplier_rank': 0,
    })
    # Company
    cls.company_partner = cls.env['res.partner'].create({
        'name': 'Saudi Tech Solutions',
        'is_company': True,
        'email': 'info@saudi-tech.com',
        'phone': '+966-11-555-0000',
        'website': 'https://www.saudi-tech.com',
        'vat': 'SA300000000000003',
        'customer_rank': 5,
        'supplier_rank': 2,
    })
```

### res.users (System User)

```python
# Internal user
cls.user_salesperson = cls.env['res.users'].create({
    'name': 'Test Salesperson',
    'login': 'test_sales@company.com',
    'email': 'test_sales@company.com',
    'groups_id': [(4, cls.env.ref('sales_team.group_sale_salesman').id)],
    'company_id': cls.env.company.id,
    'company_ids': [(4, cls.env.company.id)],
})

# Portal user
cls.user_portal = cls.env['res.users'].create({
    'name': 'Portal Customer',
    'login': 'portal@customer.com',
    'email': 'portal@customer.com',
    'groups_id': [(4, cls.env.ref('base.group_portal').id)],
})
```

### product.product (Product)

```python
# Service product
cls.service_product = cls.env['product.product'].create({
    'name': 'Consulting Services',
    'type': 'service',
    'list_price': 500.00,
    'standard_price': 300.00,
    'uom_id': cls.env.ref('uom.product_uom_hour').id,
    'uom_po_id': cls.env.ref('uom.product_uom_hour').id,
    'invoice_policy': 'order',
})

# Storable product
cls.storable_product = cls.env['product.product'].create({
    'name': 'Office Desk',
    'type': 'product',
    'list_price': 899.99,
    'standard_price': 450.00,
    'uom_id': cls.env.ref('uom.product_uom_unit').id,
    'categ_id': cls.env.ref('product.product_category_all').id,
})
```

### sale.order (Sales Order)

```python
cls.sale_order = cls.env['sale.order'].create({
    'partner_id': cls.partner.id,
    'partner_invoice_id': cls.partner.id,
    'partner_shipping_id': cls.partner.id,
    'date_order': fields.Datetime.now(),
    'validity_date': fields.Date.add(fields.Date.today(), days=30),
    'pricelist_id': cls.env.ref('product.list0').id,
    'order_line': [(0, 0, {
        'product_id': cls.product.id,
        'product_uom_qty': 5.0,
        'price_unit': 100.00,
        'discount': 0.0,
    })],
})
```

### account.move (Invoice / Bill)

```python
# Customer invoice
cls.invoice = cls.env['account.move'].create({
    'move_type': 'out_invoice',
    'partner_id': cls.partner.id,
    'invoice_date': fields.Date.today(),
    'invoice_date_due': fields.Date.add(fields.Date.today(), days=30),
    'currency_id': cls.env.ref('base.USD').id,
    'invoice_line_ids': [(0, 0, {
        'name': 'Professional Services',
        'quantity': 10.0,
        'price_unit': 200.0,
        'account_id': cls.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('company_id', '=', cls.env.company.id),
        ], limit=1).id,
    })],
})

# Vendor bill
cls.vendor_bill = cls.env['account.move'].create({
    'move_type': 'in_invoice',
    'partner_id': cls.vendor.id,
    'invoice_date': fields.Date.today(),
    'invoice_line_ids': [(0, 0, {
        'name': 'Office Supplies',
        'quantity': 5.0,
        'price_unit': 150.0,
        'account_id': cls.env['account.account'].search([
            ('account_type', '=', 'expense'),
        ], limit=1).id,
    })],
})
```

### hr.employee (Employee)

```python
cls.employee = cls.env['hr.employee'].create({
    'name': 'John Smith',
    'job_id': cls.env.ref('hr.job_consultant').id,
    'job_title': 'Senior Consultant',
    'department_id': cls.env.ref('hr.dep_it').id,
    'work_email': 'john.smith@company.com',
    'work_phone': '+1-555-234-5678',
    'company_id': cls.env.company.id,
    'resource_calendar_id': cls.env.ref('resource.resource_calendar_std').id,
    'active': True,
})
```

---

## Using env.ref() Safely

```python
# Always use try/except when ref might not exist
try:
    ref_record = cls.env.ref('module.xml_id')
except Exception:
    ref_record = cls.env['model.name'].search([], limit=1)

# Fallback pattern for optional modules
if 'hr.attendance' in cls.env:
    cls.attendance = cls.env['hr.attendance'].create({...})
else:
    cls.skipTest("hr_attendance not installed")
```

---

## Creating Minimal vs Full Records

### Minimal (Required Fields Only)

```python
# Good for testing create() itself or business logic that doesn't need full data
record = self.env['my.model'].create({
    'name': 'Minimal',  # only required field
})
```

### Full (All Fields for Integration Tests)

```python
# Good for testing workflows, reports, or features that access many fields
record = self.env['my.model'].create({
    'name': 'Full Record',
    'partner_id': self.partner.id,
    'date': fields.Date.today(),
    'amount': 1000.0,
    'currency_id': self.env.ref('base.USD').id,
    'state': 'draft',
    'note': 'Integration test record with all fields populated.',
    'active': True,
    'user_id': self.env.user.id,
    'company_id': self.env.company.id,
})
```

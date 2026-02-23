---
title: 'Generate Mock Test Data'
read_only: false
type: 'command'
description: 'Generate realistic mock data Python code for Odoo models - field-type-aware value generation for test setUp methods'
---

# /test-data --model <model> --count <n> [options]

Generate production-quality mock data Python code for Odoo models. Detects field types from model source files and produces realistic values (names, emails, amounts, dates) suitable for use in `setUpClass()` or `setUp()` test methods. Supports well-known Odoo models with pre-built templates and custom model parsing.

## Usage

```
/test-data --model res.partner --count 5
/test-data --model sale.order --count 3
/test-data --model my.model --count 10 --module /path/to/module
/test-data --model hr.employee --count 2 --format setup_method
/test-data --model my.model --count 5 --format create_list --output setup_data.py
```

## Natural Language Triggers

```
"Generate mock data for res.partner"
"Create 10 test partners"
"Generate realistic sales order data for tests"
"Create employee fixtures for my tests"
"Make test setup data for my.model"
"Generate 20 product records for testing"
```

## Implementation

```python
import sys
import subprocess
from pathlib import Path

args_str = "${ARGS}".strip()
args_parts = args_str.split()

if not args_parts or '--model' not in args_parts:
    print("Usage: /test-data --model <model.name> --count <n> [options]")
    print()
    print("Examples:")
    print("  /test-data --model res.partner --count 5")
    print("  /test-data --model sale.order --count 3")
    print("  /test-data --model my.model --count 10 --module /path/to/module")
    print("  /test-data --model hr.employee --count 2 --format setup_method")
    sys.exit(1)

script = Path(r"${PLUGIN_DIR}/odoo-test/scripts/mock_data_factory.py")
cmd = [sys.executable, str(script)] + args_parts

print(f"Generating mock data...")
print()

result = subprocess.run(cmd, capture_output=False, text=True)
sys.exit(result.returncode)
```

## Output Formats

### Individual Records (Default)

```bash
/test-data --model res.partner --count 3
```

Output:
```python
# Mock data for res.partner (3 records)
from odoo import fields

record_1 = self.env['res.partner'].create({
    'name': 'Acme Corporation',
    'is_company': True,
    'email': 'acme.corporation@business.com',
    'phone': '+1-800-ACME',
    'street': '4532 King Fahd Road',
    'city': 'Riyadh',
    'country_id': self.env.ref('base.us').id,
    'customer_rank': 3,
    'supplier_rank': 1,
})

record_2 = self.env['res.partner'].create({...})
record_3 = self.env['res.partner'].create({...})
```

### Create List (Batch)

```bash
/test-data --model res.partner --count 5 --format create_list
```

Output:
```python
records = self.env['res.partner'].create([
    {'name': 'Ahmed Smith', 'email': 'ahmed.smith@company.com', ...},
    {'name': 'Emma Johnson', 'email': 'emma.johnson@tech.io', ...},
    ...
])
```

### Loop Format (Large Counts)

```bash
/test-data --model res.partner --count 50 --format loop
```

Output:
```python
records = []
for i in range(1, 51):
    record = self.env['res.partner'].create({
        'name': f'Test Partner {i:03d}',
        'email': f'partner{i:03d}@company.com',
        ...
    })
    records.append(record)
```

### Setup Method (Full setUpClass Snippet)

```bash
/test-data --model my.model --count 3 --module /path/to/module --format setup_method
```

Output:
```python
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures - runs once for all tests in this class."""
        super().setUpClass()
        # Disable mail tracking to speed up tests
        cls.env = cls.env(context={
            **cls.env.context,
            'mail_notrack': True,
            'tracking_disable': True,
        })
        cls.my_model_records = cls.env['my.model'].create([
            {'name': 'Test Record 1', 'amount': 1234.56, ...},
            {'name': 'Test Record 2', 'amount': 5678.90, ...},
            {'name': 'Test Record 3', 'amount': 9012.34, ...},
        ])
```

## Pre-Built Templates for Common Models

The following models have optimized, realistic data templates:

| Model | Generated Values |
|-------|-----------------|
| `res.partner` | Realistic names, emails, addresses, phone numbers |
| `res.users` | Login emails, group assignments, company setup |
| `product.product` | Product names, prices, UoM references |
| `hr.employee` | Full names, job titles, work contact info |
| `sale.order` | With order lines, quantities, unit prices |
| `account.move` | Invoice type, line items, account references |

## Realistic Value Examples by Field Type

| Field Type | Example Generated Values |
|-----------|------------------------|
| `Char` (name) | 'Ahmed Al-Rashidi', 'Emma Williams' |
| `Char` (email) | 'ahmed.alrashidi@company.com' |
| `Char` (phone) | '+1-555-234-5678' |
| `Char` (city) | 'Riyadh', 'Dubai', 'London' |
| `Float` (price) | 1247.83, 5982.10 |
| `Float` (quantity) | 3.0, 15.5 |
| `Integer` (count) | 7, 42 |
| `Date` (start) | `fields.Date.add(fields.Date.today(), days=-14)` |
| `Date` (end/due) | `fields.Date.add(fields.Date.today(), days=30)` |
| `Datetime` | `fields.Datetime.now()` |
| `Boolean` | `True` or `False` (random) |
| `Selection` | First valid key from selection list |
| `Many2one` (partner) | `self.env.ref('base.res_partner_1').id` |
| `Many2one` (currency) | `self.env.ref('base.USD').id` |

## Options Reference

| Option | Description | Default |
|--------|-------------|---------|
| `--model` | Odoo model name (required) | - |
| `--count` | Number of records to generate | 3 |
| `--module` | Module path for field type detection | - |
| `--format` | `individual`, `create_list`, `loop`, `setup_method` | `individual` |
| `--output` | Write output to file | stdout |

---

*Part of odoo-test-plugin v1.0*

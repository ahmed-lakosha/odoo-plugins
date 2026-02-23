#!/usr/bin/env python3
"""
Odoo Mock Data Factory
======================
Generates realistic test fixture Python code for Odoo models. Detects field
types from model source files and produces sensible values per field type.
Output is Python code suitable for use in test setUp() or setUpClass() methods.

Usage:
    python mock_data_factory.py --model res.partner --count 5
    python mock_data_factory.py --model sale.order --count 3 --module /path/to/module
    python mock_data_factory.py --model my.model --count 10 --output setup_data.py
    python mock_data_factory.py --model hr.employee --count 2 --format create_list
"""

import argparse
import ast
import random
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from textwrap import dedent, indent


# ─── Realistic Value Generators ───────────────────────────────────────────────

# First names and last names for realistic partner names
FIRST_NAMES = [
    'Ahmed', 'Mohammed', 'Sarah', 'Emma', 'Liam', 'Olivia', 'Noah', 'Ava',
    'Oliver', 'Isabella', 'William', 'Sophia', 'James', 'Charlotte', 'Benjamin',
    'Mia', 'Lucas', 'Amelia', 'Mason', 'Harper', 'Ethan', 'Evelyn', 'Alexander',
    'Abigail', 'Henry', 'Emily', 'Sebastian', 'Elizabeth', 'Jack', 'Layla',
]
LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
    'Davis', 'Wilson', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White',
    'Harris', 'Martin', 'Thompson', 'Young', 'Martinez', 'Robinson',
    'Al-Rashidi', 'Al-Mansouri', 'Al-Otaibi', 'Al-Harbi', 'Al-Qahtani',
]
COMPANY_NAMES = [
    'Acme Corp', 'TechSolutions Ltd', 'Global Industries', 'Innovation Hub',
    'Digital Works', 'Smart Systems', 'Future Tech', 'Alpha Dynamics',
    'Nexus Group', 'Apex Solutions', 'Vertex Technologies', 'Quantum Labs',
    'Stellar Enterprises', 'Peak Performance', 'Horizon Consulting',
]
CITIES = [
    'Riyadh', 'Jeddah', 'Dammam', 'Medina', 'Khobar',
    'Dubai', 'Abu Dhabi', 'Kuwait City', 'Doha', 'Muscat',
    'Cairo', 'Amman', 'Beirut', 'Istanbul', 'London',
    'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
]
STREETS = [
    'King Fahd Road', 'Olaya Street', 'Tahlia Street', 'Prince Sultan Road',
    'Main Street', 'Business Park Ave', 'Innovation Blvd', 'Commerce Drive',
    '5th Avenue', 'Market Street', 'Harbor View Road', 'Tech Park Lane',
]
PRODUCT_NAMES = [
    'Office Chair', 'Standing Desk', 'Monitor 27"', 'Keyboard Pro',
    'USB Hub', 'Webcam HD', 'Headset Wireless', 'Laptop Stand',
    'Printer Cartridge', 'Cable Management Kit', 'Mouse Ergonomic',
    'Notebook Set', 'Whiteboard 4x6', 'Projector Screen', 'Document Tray',
]
JOB_TITLES = [
    'Software Engineer', 'Product Manager', 'Data Analyst', 'DevOps Engineer',
    'UX Designer', 'Sales Representative', 'Marketing Specialist',
    'Financial Analyst', 'HR Manager', 'Operations Lead', 'QA Engineer',
    'Business Analyst', 'Account Executive', 'Customer Success Manager',
]
NOTES = [
    'Preferred customer with long-term relationship.',
    'High-value account requiring priority service.',
    'New lead from marketing campaign Q1 2024.',
    'Requires special billing terms - net 60.',
    'International shipping restrictions apply.',
    'Loyalty discount program member.',
    'Referred by partner program.',
    'VIP client - escalate issues immediately.',
]


def _rand_name() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def _rand_company() -> str:
    return random.choice(COMPANY_NAMES)

def _rand_email(name: str = None) -> str:
    if not name:
        name = _rand_name()
    slug = name.lower().replace(' ', '.').replace('-', '').replace("'", '')
    domain = random.choice(['gmail.com', 'company.com', 'business.org', 'enterprise.net', 'tech.io'])
    return f"{slug}@{domain}"

def _rand_phone() -> str:
    area = random.randint(200, 999)
    mid  = random.randint(100, 999)
    end  = random.randint(1000, 9999)
    return f"+1-{area}-{mid}-{end}"

def _rand_date(days_offset_range=(-365, 365)) -> str:
    offset = random.randint(*days_offset_range)
    d = date.today() + timedelta(days=offset)
    return d.strftime('%Y-%m-%d')

def _rand_amount(min_val=10.0, max_val=10000.0, precision=2) -> float:
    return round(random.uniform(min_val, max_val), precision)

def _rand_int(min_val=1, max_val=100) -> int:
    return random.randint(min_val, max_val)

def _rand_street() -> str:
    num = random.randint(1, 9999)
    return f"{num} {random.choice(STREETS)}"


# ─── Field Value Resolver ──────────────────────────────────────────────────────

KNOWN_MODEL_FIXTURES = {
    'res.partner': {
        'template': """self.env['res.partner'].create({{
            'name': {name!r},
            'is_company': {is_company},
            'email': {email!r},
            'phone': {phone!r},
            'street': {street!r},
            'city': {city!r},
            'country_id': self.env.ref('base.us').id,
            'customer_rank': {customer_rank},
            'supplier_rank': {supplier_rank},
        }})""",
        'generator': lambda i: {
            'name': _rand_company() if i % 3 == 0 else _rand_name(),
            'is_company': 'True' if i % 3 == 0 else 'False',
            'email': _rand_email(),
            'phone': _rand_phone(),
            'street': _rand_street(),
            'city': random.choice(CITIES),
            'customer_rank': random.randint(0, 5),
            'supplier_rank': random.randint(0, 2),
        }
    },
    'res.users': {
        'template': """self.env['res.users'].create({{
            'name': {name!r},
            'login': {login!r},
            'email': {email!r},
            'groups_id': [(4, self.env.ref('base.group_user').id)],
            'company_id': self.env.company.id,
        }})""",
        'generator': lambda i: {
            'name': _rand_name(),
            'login': f'test_user_{i:03d}@company.com',
            'email': f'test_user_{i:03d}@company.com',
        }
    },
    'product.product': {
        'template': """self.env['product.product'].create({{
            'name': {name!r},
            'type': {ptype!r},
            'list_price': {list_price},
            'standard_price': {standard_price},
            'uom_id': self.env.ref('uom.product_uom_unit').id,
        }})""",
        'generator': lambda i: {
            'name': random.choice(PRODUCT_NAMES) + f' #{i}',
            'ptype': random.choice(['service', 'product', 'consu']),
            'list_price': _rand_amount(10, 2000),
            'standard_price': _rand_amount(5, 1000),
        }
    },
    'hr.employee': {
        'template': """self.env['hr.employee'].create({{
            'name': {name!r},
            'work_email': {work_email!r},
            'work_phone': {work_phone!r},
            'job_title': {job_title!r},
            'company_id': self.env.company.id,
        }})""",
        'generator': lambda i: {
            'name': _rand_name(),
            'work_email': f'emp_{i:03d}@company.com',
            'work_phone': _rand_phone(),
            'job_title': random.choice(JOB_TITLES),
        }
    },
    'sale.order': {
        'template': """self.env['sale.order'].create({{
            'partner_id': self.env.ref('base.res_partner_1').id,  # Replace with fixture
            'date_order': fields.Datetime.now(),
            'order_line': [(0, 0, {{
                'product_id': self.env.ref('product.product_product_1').id,  # Replace with fixture
                'product_uom_qty': {qty},
                'price_unit': {price},
            }})],
        }})""",
        'generator': lambda i: {
            'qty': random.randint(1, 20),
            'price': _rand_amount(50, 5000),
        }
    },
    'account.move': {
        'template': """self.env['account.move'].create({{
            'move_type': {move_type!r},
            'partner_id': self.env.ref('base.res_partner_2').id,  # Replace with fixture
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {{
                'name': {line_name!r},
                'quantity': {qty},
                'price_unit': {price},
                'account_id': self.env['account.account'].search([
                    ('account_type', '=', 'income')
                ], limit=1).id,
            }})],
        }})""",
        'generator': lambda i: {
            'move_type': random.choice(['out_invoice', 'in_invoice']),
            'line_name': f'Service Line {i}',
            'qty': random.randint(1, 10),
            'price': _rand_amount(100, 5000),
        }
    },
}


class FieldValueGenerator:
    """Generates realistic mock values for Odoo field types."""

    def __init__(self, field_name: str, field_info: dict, index: int):
        self.field_name = field_name
        self.field_info = field_info
        self.field_type = field_info.get('type', 'Char')
        self.index = index

    def generate(self) -> str:
        """Return a Python literal string for this field's value."""
        ft = self.field_type
        fn = self.field_name

        # Name-based heuristics first
        if fn == 'name':
            return repr(_rand_name())
        if fn in ('email', 'email_from', 'work_email'):
            return repr(_rand_email())
        if fn in ('phone', 'mobile', 'work_phone'):
            return repr(_rand_phone())
        if fn in ('street', 'street2'):
            return repr(_rand_street())
        if fn == 'city':
            return repr(random.choice(CITIES))
        if fn in ('zip', 'zip_code'):
            return repr(f'{random.randint(10000, 99999)}')
        if fn in ('note', 'notes', 'description', 'comment', 'internal_note'):
            return repr(random.choice(NOTES))
        if fn in ('ref', 'code', 'reference'):
            return repr(f'REF-{self.index:04d}')
        if fn == 'sequence':
            return repr(self.index * 10)

        # Type-based generators
        generators = {
            'Char':     self._gen_char,
            'Text':     self._gen_text,
            'Html':     self._gen_html,
            'Integer':  self._gen_integer,
            'Float':    self._gen_float,
            'Monetary': self._gen_monetary,
            'Boolean':  self._gen_boolean,
            'Date':     self._gen_date,
            'Datetime': self._gen_datetime,
            'Selection':self._gen_selection,
            'Many2one': self._gen_many2one,
            'Many2many':self._gen_many2many,
            'One2many': self._gen_one2many,
        }
        gen_fn = generators.get(ft, self._gen_char)
        return gen_fn()

    def _gen_char(self):
        return repr(f'Test {self.field_name.replace("_", " ").title()} {self.index}')

    def _gen_text(self):
        return repr(f'Detailed text for {self.field_name} record #{self.index}. {random.choice(NOTES)}')

    def _gen_html(self):
        return repr(f'<p>HTML content for {self.field_name} #{self.index}.</p>')

    def _gen_integer(self):
        # Amount-like field names get higher values
        if any(k in self.field_name for k in ('qty', 'quantity', 'count', 'num')):
            return str(random.randint(1, 50))
        if any(k in self.field_name for k in ('sequence', 'priority', 'order')):
            return str(self.index * 10)
        return str(_rand_int(1, 100))

    def _gen_float(self):
        if any(k in self.field_name for k in ('price', 'amount', 'cost', 'total', 'subtotal')):
            return str(_rand_amount(50.0, 5000.0))
        if any(k in self.field_name for k in ('qty', 'quantity', 'hours')):
            return str(round(random.uniform(1.0, 50.0), 2))
        if any(k in self.field_name for k in ('rate', 'percent', 'ratio')):
            return str(round(random.uniform(0.0, 100.0), 2))
        if any(k in self.field_name for k in ('weight', 'volume', 'length')):
            return str(round(random.uniform(0.1, 100.0), 3))
        return str(_rand_amount(1.0, 1000.0))

    def _gen_monetary(self):
        return str(_rand_amount(100.0, 50000.0))

    def _gen_boolean(self):
        return random.choice(['True', 'False'])

    def _gen_date(self):
        # Date field name heuristics
        if 'start' in self.field_name or 'from' in self.field_name or 'begin' in self.field_name:
            return f"fields.Date.add(fields.Date.today(), days=-{random.randint(0, 30)})"
        if 'end' in self.field_name or 'to' in self.field_name or 'due' in self.field_name:
            return f"fields.Date.add(fields.Date.today(), days={random.randint(1, 60)})"
        return "fields.Date.today()"

    def _gen_datetime(self):
        if 'start' in self.field_name or 'begin' in self.field_name:
            return "fields.Datetime.now()"
        if 'end' in self.field_name or 'stop' in self.field_name:
            return f"fields.Datetime.add(fields.Datetime.now(), hours={random.randint(1, 48)})"
        return "fields.Datetime.now()"

    def _gen_selection(self):
        selection = self.field_info.get('selection', [])
        if selection and isinstance(selection, list) and len(selection) > 0:
            keys = [s[0] for s in selection if isinstance(s, (list, tuple)) and len(s) == 2]
            if keys:
                return repr(random.choice(keys))
        # Default state values
        if 'state' in self.field_name:
            return repr('draft')
        return repr('option_1')

    def _gen_many2one(self):
        # Heuristic: common relational field names
        m2o_refs = {
            'partner_id': "self.env.ref('base.res_partner_1').id",
            'partner_invoice_id': "self.env.ref('base.res_partner_1').id",
            'partner_shipping_id': "self.env.ref('base.res_partner_1').id",
            'company_id': "self.env.company.id",
            'currency_id': "self.env.ref('base.USD').id",
            'user_id': "self.env.ref('base.user_admin').id",
            'country_id': "self.env.ref('base.us').id",
            'product_id': "self.env.ref('product.product_product_1').id",
            'uom_id': "self.env.ref('uom.product_uom_unit').id",
            'categ_id': "self.env.ref('product.product_category_all').id",
            'pricelist_id': "self.env.ref('product.list0').id",
            'warehouse_id': "self.env.ref('stock.warehouse0').id",
            'location_id': "self.env.ref('stock.stock_location_stock').id",
            'journal_id': "self.env['account.journal'].search([], limit=1).id",
            'account_id': "self.env['account.account'].search([], limit=1).id",
            'department_id': "self.env.ref('hr.dep_it').id",
            'job_id': "self.env.ref('hr.job_consultant').id",
            'team_id': "self.env.ref('sales_team.team_sales_department').id",
            'picking_type_id': "self.env.ref('stock.picking_type_out').id",
        }
        if self.field_name in m2o_refs:
            return m2o_refs[self.field_name]
        # Generic fallback
        return f"None  # TODO: Provide a valid {self.field_name} ID"

    def _gen_many2many(self):
        return '[]  # TODO: Add IDs, e.g., [(4, ref_id)]'

    def _gen_one2many(self):
        return '[]  # TODO: Add embedded records, e.g., [(0, 0, {{...}})]'


# ─── Model Field Parser ───────────────────────────────────────────────────────

def parse_fields_from_file(file_path: Path) -> dict:
    """Extract field definitions from a Python model file."""
    fields = {}
    try:
        source = file_path.read_text(encoding='utf-8', errors='ignore')
        tree = ast.parse(source)
    except (SyntaxError, FileNotFoundError):
        # Regex fallback
        source = file_path.read_text(encoding='utf-8', errors='ignore')
        field_pattern = re.compile(r'(\w+)\s*=\s*fields\.(\w+)\(([^)]*)\)')
        for m in field_pattern.finditer(source):
            fname, ftype, fargs = m.group(1), m.group(2), m.group(3)
            if not fname.startswith('_'):
                required = 'required=True' in fargs
                compute = bool(re.search(r"compute=['\"]", fargs))
                related = bool(re.search(r"related=['\"]", fargs))
                sel_match = re.search(r"selection=\[([^\]]+)\]", fargs)
                selection = None
                if sel_match:
                    try:
                        selection = ast.literal_eval(f"[{sel_match.group(1)}]")
                    except Exception:
                        pass
                fields[fname] = {
                    'type': ftype, 'required': required,
                    'compute': compute, 'related': related,
                    'selection': selection,
                }
        return fields

    FIELD_TYPES = {
        'Char', 'Text', 'Html', 'Integer', 'Float', 'Monetary', 'Boolean',
        'Date', 'Datetime', 'Selection', 'Many2one', 'Many2many', 'One2many',
        'Binary', 'Reference',
    }

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if not isinstance(item, ast.Assign):
                continue
            if not isinstance(item.value, ast.Call):
                continue
            func = item.value.func
            if not isinstance(func, ast.Attribute):
                continue
            if not (isinstance(func.value, ast.Name) and func.value.id == 'fields'):
                continue
            if func.attr not in FIELD_TYPES:
                continue
            for target in item.targets:
                if not isinstance(target, ast.Name) or target.id.startswith('_'):
                    continue
                kws = {kw.arg: kw for kw in item.value.keywords}
                required = False
                if 'required' in kws and isinstance(kws['required'].value, ast.Constant):
                    required = bool(kws['required'].value.value)
                compute = 'compute' in kws
                related = 'related' in kws
                selection = None
                if 'selection' in kws and isinstance(kws['selection'].value, ast.List):
                    try:
                        selection = ast.literal_eval(kws['selection'].value)
                    except Exception:
                        pass
                fields[target.id] = {
                    'type': func.attr,
                    'required': required,
                    'compute': compute,
                    'related': related,
                    'selection': selection,
                }
    return fields


def find_model_files(module_path: Path, model_name: str) -> list[Path]:
    """Find Python files that define the given model."""
    candidates = []
    models_dir = module_path / 'models'
    search_dirs = [models_dir, module_path] if models_dir.exists() else [module_path]

    for search_dir in search_dirs:
        for py_file in search_dir.glob('*.py'):
            if py_file.name in ('__init__.py', '__manifest__.py'):
                continue
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            if f"_name = '{model_name}'" in content or f'_name = "{model_name}"' in content:
                candidates.append(py_file)
    return candidates


# ─── Code Generators ──────────────────────────────────────────────────────────

def generate_known_model_code(model_name: str, count: int) -> str:
    """Generate code for well-known Odoo models using predefined templates."""
    fixture = KNOWN_MODEL_FIXTURES.get(model_name)
    if not fixture:
        return None

    lines = [
        f"# Mock data for {model_name} ({count} records)",
        "from odoo import fields",
        "",
    ]

    if count == 1:
        vals = fixture['generator'](1)
        record_code = fixture['template'].format(**vals)
        lines.append(f"record = {record_code}")
    else:
        lines.append(f"records = []")
        lines.append(f"for i in range(1, {count + 1}):")
        lines.append(f"    # Create each {model_name} record")
        # Show single-record creation in loop
        vals = fixture['generator'](1)
        # Replace concrete values with loop variable references
        template_lines = fixture['template'].format(**vals).splitlines()
        for tl in template_lines:
            lines.append(f"    {tl}")
        lines.append(f"    records.append(record)")

    return '\n'.join(lines)


def generate_generic_code(model_name: str, count: int, fields: dict, output_format: str) -> str:
    """Generate mock data code for any model based on parsed fields."""
    writable_fields = {
        fname: finfo for fname, finfo in fields.items()
        if not finfo.get('compute') and not finfo.get('related')
        and finfo['type'] not in ('One2many',)
    }

    lines = [
        f"# Mock data for {model_name} ({count} records)",
        f"# Generated by odoo-test-plugin mock_data_factory.py",
        "from odoo import fields",
        "",
    ]

    if output_format == 'create_list':
        # Generate single create() call with list of vals dicts
        lines.append(f"records = self.env[{repr(model_name)}].create([")
        for i in range(1, count + 1):
            lines.append("    {")
            for fname, finfo in writable_fields.items():
                gen = FieldValueGenerator(fname, finfo, i)
                value = gen.generate()
                lines.append(f"        {repr(fname)}: {value},")
            lines.append("    },")
        lines.append("])")

    elif output_format == 'loop':
        # Generate a loop
        lines.append(f"records = []")
        lines.append(f"for i in range(1, {count + 1}):")
        lines.append(f"    record = self.env[{repr(model_name)}].create({{")
        for fname, finfo in writable_fields.items():
            gen = FieldValueGenerator(fname, finfo, 1)
            value = gen.generate()
            # Replace hardcoded index with loop variable where possible
            value = value.replace("'001'", "f'{i:03d}'").replace('"001"', "f'{i:03d}'")
            lines.append(f"        {repr(fname)}: {value},")
        lines.append("    })")
        lines.append("    records.append(record)")

    else:  # individual - one create per record
        for i in range(1, count + 1):
            var_name = 'record' if count == 1 else f'record_{i}'
            lines.append(f"{var_name} = self.env[{repr(model_name)}].create({{")
            for fname, finfo in writable_fields.items():
                gen = FieldValueGenerator(fname, finfo, i)
                value = gen.generate()
                lines.append(f"    {repr(fname)}: {value},")
            lines.append("})")
            if i < count:
                lines.append("")

    return '\n'.join(lines)


def generate_setup_method(model_name: str, count: int, fields: dict) -> str:
    """Generate a complete setUpClass snippet."""
    writable = {
        fname: finfo for fname, finfo in fields.items()
        if not finfo.get('compute') and not finfo.get('related')
    }

    var_name = model_name.replace('.', '_')
    lines = [
        "    @classmethod",
        "    def setUpClass(cls):",
        '        """Set up test fixtures - runs once for all tests in this class."""',
        "        super().setUpClass()",
        "        # Disable mail tracking to speed up tests",
        "        cls.env = cls.env(context={",
        "            **cls.env.context,",
        "            'mail_notrack': True,",
        "            'tracking_disable': True,",
        "        })",
        "",
    ]

    if count == 1:
        lines.append(f"        cls.{var_name} = cls.env[{repr(model_name)}].create({{")
        for fname, finfo in writable.items():
            gen = FieldValueGenerator(fname, finfo, 1)
            value = gen.generate()
            lines.append(f"            {repr(fname)}: {value},")
        lines.append("        })")
    else:
        lines.append(f"        cls.{var_name}_records = cls.env[{repr(model_name)}].create([")
        for i in range(1, count + 1):
            lines.append("            {")
            for fname, finfo in writable.items():
                gen = FieldValueGenerator(fname, finfo, i)
                value = gen.generate()
                lines.append(f"                {repr(fname)}: {value},")
            lines.append("            },")
        lines.append("        ])")

    return '\n'.join(lines)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Generate realistic mock data code for Odoo models.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""
        Examples:
          # Generate 5 res.partner records
          python mock_data_factory.py --model res.partner --count 5

          # Generate setup code for a custom model
          python mock_data_factory.py --model my.model --count 3 --module /path/to/module

          # Generate as a loop (useful for large counts)
          python mock_data_factory.py --model sale.order --count 20 --format loop

          # Generate a full setUpClass method
          python mock_data_factory.py --model my.model --count 5 --format setup_method

          # Save output to file
          python mock_data_factory.py --model hr.employee --count 10 --output setup_data.py
        """)
    )
    parser.add_argument('--model', required=True, help='Odoo model name (e.g., res.partner, sale.order)')
    parser.add_argument('--count', type=int, default=3, help='Number of records to generate (default: 3)')
    parser.add_argument('--module', help='Path to module directory (for field type detection)')
    parser.add_argument('--format', choices=['individual', 'create_list', 'loop', 'setup_method'],
                        default='individual', help='Output code format (default: individual)')
    parser.add_argument('--output', help='Write output to file (default: print to stdout)')

    args = parser.parse_args()
    random.seed(42 + args.count)  # Reproducible output

    print(f"# Generating {args.count} {args.model} record(s)...", file=sys.stderr)

    code = None

    # Try known model templates first
    if args.model in KNOWN_MODEL_FIXTURES and args.format not in ('setup_method',):
        code = generate_known_model_code(args.model, args.count)

    # Parse custom module fields
    if not code and args.module:
        module_path = Path(args.module).resolve()
        model_files = find_model_files(module_path, args.model)
        if model_files:
            print(f"# Parsing fields from: {model_files[0].name}", file=sys.stderr)
            fields = parse_fields_from_file(model_files[0])
        else:
            print(f"# No model file found for {args.model}; using minimal defaults", file=sys.stderr)
            fields = {
                'name': {'type': 'Char', 'required': True, 'compute': False, 'related': False, 'selection': None},
            }

        if args.format == 'setup_method':
            code = generate_setup_method(args.model, args.count, fields)
        else:
            code = generate_generic_code(args.model, args.count, fields, args.format)

    # Fall back to minimal code
    if not code:
        fields = {
            'name': {'type': 'Char', 'required': True, 'compute': False, 'related': False, 'selection': None},
        }
        code = generate_generic_code(args.model, args.count, fields, args.format)

    if args.output:
        Path(args.output).write_text(code + '\n', encoding='utf-8')
        print(f"# Written to {args.output}", file=sys.stderr)
    else:
        print(code)


if __name__ == '__main__':
    main()

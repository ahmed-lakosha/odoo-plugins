# Template Validator

> **Purpose**: Validation rules for email templates and QWeb reports before creation or modification.

## Pre-Flight Validation Checklist

```
┌─────────────────────────────────────────────────────────────────┐
│                 TEMPLATE VALIDATION CHECKLIST                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  PHASE 1: MODEL VALIDATION                                       │
│  ────────────────────────────────────────────────────────────── │
│  [ ] Model exists in target Odoo version                         │
│  [ ] Model name is correctly formatted (module.model)            │
│  [ ] Model has required fields for template type:                │
│      - Email: partner_id or email field                          │
│      - Notification: inherits mail.thread                        │
│      - Report: name field for print_report_name                  │
│                                                                   │
│  PHASE 2: FIELD VALIDATION                                       │
│  ────────────────────────────────────────────────────────────── │
│  [ ] All object.field references exist on model                  │
│  [ ] Related fields are valid (object.partner_id.name)           │
│  [ ] No deprecated field references                              │
│  [ ] Computed fields don't cause circular dependencies           │
│                                                                   │
│  PHASE 3: SYNTAX VALIDATION                                      │
│  ────────────────────────────────────────────────────────────── │
│  [ ] Valid XML structure                                         │
│  [ ] QWeb tags properly structured:                              │
│      - t-if/t-elif/t-else sequences                              │
│      - t-foreach has t-as                                        │
│      - t-set has t-value                                         │
│  [ ] Jinja2 expressions balanced {{ }}                           │
│  [ ] Version-appropriate syntax (t-out vs t-esc)                 │
│                                                                   │
│  PHASE 4: SECURITY VALIDATION                                    │
│  ────────────────────────────────────────────────────────────── │
│  [ ] No eval() or exec() calls                                   │
│  [ ] No os module access                                         │
│  [ ] No file system operations                                   │
│  [ ] No arbitrary SQL execution                                  │
│  [ ] Sandbox-safe expressions only                               │
│                                                                   │
│  PHASE 5: VERSION COMPATIBILITY                                  │
│  ────────────────────────────────────────────────────────────── │
│  [ ] report_template vs report_template_ids (Odoo 17+)          │
│  [ ] template_category field (Odoo 16+)                         │
│  [ ] Company branding colors (Odoo 19)                          │
│  [ ] t-out syntax (Odoo 15+)                                    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Validation Rules

### XML Syntax Rules

```python
# Rule 1: Well-formed XML
def validate_xml(content):
    try:
        etree.fromstring(content.encode())
        return True
    except etree.XMLSyntaxError as e:
        return f"XML Error at line {e.lineno}: {e.msg}"

# Rule 2: Proper tag closure
SELF_CLOSING_TAGS = ['t', 'br', 'hr', 'img', 'input', 'meta', 'link']
# Check all non-self-closing tags have matching close tags

# Rule 3: Valid attribute quoting
# All attributes must use double quotes: attr="value"
```

### QWeb Syntax Rules

```python
# Rule 1: t-if/t-elif/t-else structure
# t-elif must follow t-if or another t-elif
# t-else must follow t-if or t-elif
# No orphaned t-elif or t-else

# Rule 2: t-foreach requires t-as
# <t t-foreach="items" t-as="item">  ← REQUIRED

# Rule 3: t-set requires t-value (or body content)
# <t t-set="var" t-value="expression"/>  ← OK
# <t t-set="var">content</t>  ← OK

# Rule 4: Version-appropriate output
# Odoo 14: t-esc
# Odoo 15+: t-out (preferred), t-esc (deprecated warning)
```

### Field Reference Rules

```python
# Rule 1: Direct field access
# object.field_name → Check field exists on model

# Rule 2: Related field access
# object.partner_id.name → Check:
#   - partner_id exists on model
#   - partner_id is relational (Many2one, Many2many, One2many)
#   - name exists on related model

# Rule 3: Method access
# object.get_portal_url() → Check method exists on model

# Rule 4: Null safety
# WARN: object.partner_id.name without null check
# SUGGEST: object.partner_id.name or 'Default'
```

### Security Rules

```python
# BLOCKED expressions:
BLOCKED_PATTERNS = [
    r'\beval\s*\(',           # eval() calls
    r'\bexec\s*\(',           # exec() calls
    r'\bcompile\s*\(',        # compile() calls
    r'\b__import__\s*\(',     # Dynamic imports
    r'\bopen\s*\(',           # File operations
    r'\bos\.',                # OS module
    r'\bsubprocess\.',        # Subprocess
    r'\.execute\s*\(',        # SQL execute
]

# ALLOWED context functions:
ALLOWED_FUNCTIONS = [
    'format_amount',
    'format_date',
    'format_datetime',
    'is_html_empty',
    'len',
    'str',
    'int',
    'float',
    'bool',
    'list',
    'dict',
    'sum',
    'min',
    'max',
    'sorted',
    'enumerate',
    'zip',
]
```

## Validation Responses

### Pass Response

```
✓ VALIDATION PASSED

Template: my_module.email_template_custom
Model: sale.order
Version: Odoo 17

All checks passed:
- XML syntax: Valid
- QWeb structure: Valid
- Field references: 15/15 valid
- Security: No issues
- Version compatibility: Compatible

Ready for deployment.
```

### Warning Response

```
⚠ VALIDATION PASSED WITH WARNINGS

Template: my_module.email_template_custom
Model: sale.order
Version: Odoo 17

Warnings (3):
1. Line 15: Missing null check on object.partner_id.contact_id.name
   Suggestion: Use 'or' fallback or t-if guard

2. Line 28: Using t-esc instead of t-out (deprecated in 15+)
   Suggestion: Replace with t-out

3. Line 45: Potential N+1 query in nested loop
   Suggestion: Consider prefetching

Template will work but consider addressing warnings.
```

### Fail Response

```
✗ VALIDATION FAILED

Template: my_module.email_template_custom
Model: sale.order
Version: Odoo 17

Errors (2):
1. Line 10: Field 'invalid_field' does not exist on sale.order
   Code: {{ object.invalid_field }}

2. Line 25: Invalid XML - unclosed tag
   Code: <div><span>text</div>

Template cannot be deployed. Fix errors first.
```

## Integration with Commands

```
/create-email-template → validate_template()
/fix-template → validate_template() before and after
/migrate-template → validate_template() for target version
/validate-template → Full validation report
```

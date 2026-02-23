# Odoo Access Rules — Complete Reference Memory

This file contains comprehensive reference material for Odoo's access control system. Use this when creating, reviewing, or fixing access control configurations in Odoo modules.

---

## ir.model.access.csv — Complete Format

### Column Definitions

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `id` | Yes | Unique XML ID for this rule | `access_my_model_user` |
| `name` | Yes | Human-readable description | `my.model user` |
| `model_id:id` | Yes | Reference to `ir.model` record | `model_my_model` |
| `group_id:id` | No | Reference to `res.groups` record. Empty = ALL users | `my_module.group_my_module_user` |
| `perm_read` | Yes | Allow read/search | `1` = yes, `0` = no |
| `perm_write` | Yes | Allow write/update | `1` = yes, `0` = no |
| `perm_create` | Yes | Allow create | `1` = yes, `0` = no |
| `perm_unlink` | Yes | Allow delete | `1` = yes, `0` = no |

### model_id:id Derivation

The `model_id:id` value is derived from the model's `_name` attribute by:
1. Replacing all dots (`.`) with underscores (`_`)
2. Prefixing with `model_`

Examples:
```
_name                    → model_id:id
'my.model'              → model_my_model
'account.move'          → model_account_move
'account.move.line'     → model_account_move_line
'res.partner'           → model_res_partner
'my.wizard'             → model_my_wizard
'hr.employee.public'    → model_hr_employee_public
```

### group_id:id Format

The `group_id:id` is the XML ID of the group in format `module.group_id`:
```
base.group_user              → Internal users (all employees)
base.group_system            → Technical / Settings access
base.group_erp_manager       → ERP manager (broad access)
base.group_portal            → Portal users (external)
base.group_public            → Public users (unauthenticated)
my_module.group_my_module_user    → Custom user group
my_module.group_my_module_manager → Custom manager group
```

**DANGER**: Empty `group_id:id` grants access to ALL authenticated users.

---

## Standard Access Patterns

### Pattern 1: Standard Internal Model (Most Common)

Appropriate for models used internally by employees. Users can create and modify, only managers can delete.

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model user,model_my_model,my_module.group_my_module_user,1,1,1,0
access_my_model_manager,my.model manager,model_my_model,my_module.group_my_module_manager,1,1,1,1
```

### Pattern 2: Read-Only Reference/Configuration Data

For lookup tables, categories, or configuration that users need to read but only admins should modify.

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_category_user,my.category user,model_my_category,base.group_user,1,0,0,0
access_my_category_manager,my.category manager,model_my_category,my_module.group_my_module_manager,1,1,1,1
```

### Pattern 3: Portal-Accessible Model

For data that portal (customer) users can view but not modify.

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model user,model_my_model,my_module.group_my_module_user,1,1,1,0
access_my_model_manager,my.model manager,model_my_model,my_module.group_my_module_manager,1,1,1,1
access_my_model_portal,my.model portal,model_my_model,base.group_portal,1,0,0,0
```

### Pattern 4: Transient Model (Wizard)

Wizards need full CRUD including unlink because Odoo manages their lifecycle (creates on open, deletes after submit).

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_wizard_user,my.wizard user,model_my_wizard,my_module.group_my_module_user,1,1,1,1
```

### Pattern 5: Multi-Company Isolated Model

For models with `company_id` in a multi-company setup. Access rules control CRUD; record rules handle company isolation.

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model user,model_my_model,my_module.group_my_module_user,1,1,1,0
access_my_model_manager,my.model manager,model_my_model,my_module.group_my_module_manager,1,1,1,1
```

(Pair with multi-company record rules in `security/rules_*.xml`)

### Pattern 6: System-Only Model

For models that only the admin/system should access (e.g., internal configuration, audit logs).

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_config_admin,my.config admin,model_my_config,base.group_system,1,1,1,1
```

### Pattern 7: Public Data (No Authentication)

For models that even unauthenticated users can read (rarely needed, use carefully).

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_public_data_public,public.data public,model_public_data,base.group_public,1,0,0,0
access_public_data_user,public.data user,model_public_data,base.group_user,1,1,1,0
```

### Pattern 8: Inherited Model with Sensitive Extension

When using `_inherit` to add fields to an existing model, you generally DON'T need separate access rules — access is inherited from the parent model's rules. However, if you create a NEW model (set `_name` as well), you need separate rules.

```python
# Case 1: Pure extension — NO separate access rules needed
class ResPartnerExtension(models.Model):
    _inherit = 'res.partner'
    my_custom_field = fields.Char()
    # res.partner access rules already cover this

# Case 2: New model with name — NEEDS separate access rules
class MyCustomModel(models.Model):
    _name = 'my.custom.model'    # New model!
    _inherit = 'res.partner'     # Inherits partner fields
    # This model NEEDS its own ir.model.access.csv entries
```

---

## Group Hierarchy and Inheritance

### Understanding implied_ids

When group B has `implied_ids = [(4, ref('group_A'))]`, users in group B automatically also have the permissions of group A.

```xml
<!-- group_user: base level -->
<record id="group_my_module_user" model="res.groups">
    <field name="name">User</field>
    <field name="category_id" ref="module_category_my_module"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>

<!-- group_manager: includes all user permissions + more -->
<record id="group_my_module_manager" model="res.groups">
    <field name="name">Manager</field>
    <field name="category_id" ref="module_category_my_module"/>
    <field name="implied_ids" eval="[(4, ref('group_my_module_user'))]"/>
    <!-- Manager automatically has all User permissions via inheritance -->
</record>
```

### Multiple Groups in Access Rules

If you have 3 groups (readonly, user, manager), you typically need 3 CSV rows per model:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
# Read-only: can only search and read
access_my_model_readonly,my.model readonly,model_my_model,my_module.group_my_module_readonly,1,0,0,0
# User: can create and modify but not delete
access_my_model_user,my.model user,model_my_model,my_module.group_my_module_user,1,1,1,0
# Manager: full access
access_my_model_manager,my.model manager,model_my_model,my_module.group_my_module_manager,1,1,1,1
```

---

## Record Rules — Row-Level Security

Record rules filter WHICH records a user can see within a model they already have model-level access to.

### Record Rule XML Structure

```xml
<record id="rule_id" model="ir.rule">
    <field name="name">Human-readable name</field>
    <field name="model_id" ref="model_my_model"/>

    <!-- domain_force: Python domain expression evaluated per user -->
    <!-- Available variables: user (res.users record), company_ids (list of company IDs) -->
    <field name="domain_force">[('user_id', '=', user.id)]</field>

    <!-- groups: which groups this rule applies to (no groups = global rule) -->
    <field name="groups" eval="[(4, ref('my_module.group_my_module_user'))]"/>

    <!-- Which operations this rule restricts (default: all) -->
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="False"/>

    <!-- global=True means rule applies to ALL users regardless of groups -->
    <!-- <field name="global" eval="True"/> -->
</record>
```

### Record Rule Domain Variables

```python
# Available in domain_force expressions:
user           # Current res.users record
user.id        # Current user ID
user.partner_id.id  # Current user's partner ID
company_ids    # List of IDs of companies user belongs to
time           # Python time module

# Examples:
[('user_id', '=', user.id)]                          # Own records only
[('company_id', 'in', company_ids)]                   # Within user's companies
[('state', 'in', ['draft', 'confirmed'])]             # By record state
[('partner_id', '=', user.partner_id.id)]             # By partner
[('team_id.member_ids', 'in', [user.id])]             # By sales team
[(1, '=', 1)]                                         # All records (no filter)
['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]  # Multi-company
```

### Rule Evaluation Logic

- Rules for the **same group** are combined with **OR** (any matching rule = access granted)
- Rules for **different groups** are combined with **AND** (all matching rules must pass)
- **Global rules** (`global=True`) always apply in addition to group-based rules
- A record is accessible if it passes ALL applicable rules

### Standard Record Rule Patterns

**Multi-Company Isolation** (required for any model with company_id):
```xml
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: Multi-Company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="global" eval="True"/>
    <field name="domain_force">
        ['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]
    </field>
</record>
```

**User's Own Records**:
```xml
<record id="rule_my_model_user_own" model="ir.rule">
    <field name="name">My Model: Own Records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('my_module.group_my_module_user'))]"/>
</record>
```

**Portal View of Published Records**:
```xml
<record id="rule_my_model_portal" model="ir.rule">
    <field name="name">My Model: Portal Published</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('website_published', '=', True)]</field>
    <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="False"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

---

## Access Rules for Inherited Models

### When _inherit Creates a New Model
```python
class MyExtension(models.Model):
    _name = 'my.extension'   # Creates new model
    _inherit = 'res.partner' # Inherits partner fields
    extra_field = fields.Char()
```
**Action needed**: Create ir.model.access.csv entries for `model_my_extension`.

### When _inherit Extends an Existing Model (No _name)
```python
class ResPartnerExtension(models.Model):
    _inherit = 'res.partner'  # Extends existing model, NO new model created
    extra_field = fields.Char()
```
**Action needed**: None — res.partner's access rules cover this.

### Computed Fields on Extended Models
If adding sensitive computed fields to an extended model, use `groups=` on the field:
```python
class AccountMoveExtension(models.Model):
    _inherit = 'account.move'
    profit_margin = fields.Float(
        compute='_compute_profit_margin',
        groups='account.group_account_manager'  # Restrict visibility
    )
```

---

## Portal User Access Patterns

Portal users (`base.group_portal`) are external users (customers, suppliers) with restricted access.

### Giving Portal Users Read Access to a Model
```csv
# In ir.model.access.csv
access_my_model_portal,my.model portal,model_my_model,base.group_portal,1,0,0,0
```

### Restricting Portal to Own Records (Record Rule)
```xml
<record id="rule_my_model_portal_own" model="ir.rule">
    <field name="name">My Model: Portal Own</field>
    <field name="model_id" ref="model_my_model"/>
    <!-- Portal users can only see records linked to their partner -->
    <field name="domain_force">[('partner_id', '=', user.partner_id.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="False"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

### Portal Access via Access Token (Secure Sharing)
For sharing individual records with non-logged-in users, use Odoo's built-in token system:
```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['portal.mixin']  # Adds access_token field automatically

    def _get_report_base_filename(self):
        return f"my-model-{self.name}"
```

---

## Public User Access (base.group_public)

Public users are completely unauthenticated visitors. Granting them access should be extremely limited.

```csv
# Only grant read access, never write/create/delete
access_my_public_data_public,my.public.data public,model_my_public_data,base.group_public,1,0,0,0
```

Always pair with record rules to limit WHICH records are visible:
```xml
<record id="rule_my_public_data_public" model="ir.rule">
    <field name="name">My Public Data: Published Only</field>
    <field name="model_id" ref="model_my_public_data"/>
    <field name="domain_force">[('is_published', '=', True)]</field>
    <field name="groups" eval="[(4, ref('base.group_public'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="False"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

---

## Common Mistakes Checklist

Before finalizing access rules, verify:

- [ ] Every `_name` model in `models/*.py` has CSV entries
- [ ] Every `TransientModel` (wizard) has CSV entries with `perm_unlink=1`
- [ ] No empty `group_id:id` column (would grant access to all users)
- [ ] `model_id:id` uses correct format: `model_my_model` (dots → underscores)
- [ ] Group XML files are listed BEFORE `ir.model.access.csv` in `__manifest__.py`
- [ ] `security/` files are listed in correct order in `data` array:
  1. `security/group_[module].xml`
  2. `security/ir.model.access.csv`
  3. `security/rules_[module].xml`
- [ ] Models with `company_id` have multi-company record rules
- [ ] Portal-accessible models have read-only access with ownership record rules
- [ ] Sensitive fields have `groups=` restriction
- [ ] Record rules don't have `(1,'=',1)` domain for non-manager groups

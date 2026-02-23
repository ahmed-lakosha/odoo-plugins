# XML Fix Templates

## Automated XML Fixes for Odoo 19

### 1. Tree to List Conversion
```python
# Fix pattern
old_string = '<tree'
new_string = '<list'

old_string = '</tree>'
new_string = '</list>'
```

### 2. Search View Group Removal (Odoo 19)
```python
import re

def fix_search_views(xml_content):
    """Remove group tags from search views - not allowed in Odoo 19"""
    # Pattern to match search views with group tags
    pattern = r'(<search[^>]*>)(.*?)(</search>)'

    def remove_groups(match):
        search_start = match.group(1)
        content = match.group(2)
        search_end = match.group(3)

        # Remove <group> opening tags with all attributes
        content = re.sub(r'<group[^>]*>', '', content)
        # Remove </group> closing tags
        content = content.replace('</group>', '')

        # Add separator before group by filters if needed
        if 'group_by' in content and '<separator/>' not in content:
            # Add separator before first group_by filter
            content = re.sub(
                r'(\s*)(<filter[^>]*group_by[^>]*>)',
                r'\1<separator/>\1\2',
                content,
                count=1
            )

        return search_start + content + search_end

    return re.sub(pattern, remove_groups, xml_content, flags=re.DOTALL)
```

### 3. Active ID Replacement
```python
def fix_active_id(xml_content):
    # Replace active_id with id in contexts
    pattern = r'context="([^"]*?)active_id([^"]*?)"'
    replacement = r'context="\1id\2"'
    return re.sub(pattern, replacement, xml_content)
```

### 4. Kanban Template Fix
```python
def fix_kanban_templates(xml_content):
    # Fix template names
    xml_content = xml_content.replace('t-name="kanban-box"', 't-name="card"')

    # Remove js_class attributes that may not be available
    # Remove crm_kanban specifically (not available outside CRM)
    pattern = r'\s+js_class=["\']crm_kanban["\']'
    xml_content = re.sub(pattern, '', xml_content)

    # Remove any other problematic js_class if needed
    # pattern = r'<kanban([^>]*?)\s+js_class="[^"]*"([^>]*?)>'
    # replacement = r'<kanban\1\2>'
    # xml_content = re.sub(pattern, replacement, xml_content)

    return xml_content
```

### 5. Cron Job Fix
```python
def fix_cron_jobs(xml_content):
    # Remove numbercall field
    pattern = r'<field name="numbercall"[^>]*>.*?</field>\s*'
    xml_content = re.sub(pattern, '', xml_content, flags=re.DOTALL)

    # Also handle self-closing tags
    pattern = r'<field name="numbercall"[^/]*?/>\s*'
    xml_content = re.sub(pattern, '', xml_content)

    return xml_content
```

### 6. T-if Expression Fix
```python
def fix_t_if_expressions(xml_content):
    # Fix not operator usage
    pattern = r't-if="not\s+(\w+)"'
    replacement = r't-if="\1 == False"'
    return re.sub(pattern, replacement, xml_content)
```

### 7. Mail Template Helper Functions Fix (NEW - Odoo 19)
```python
def fix_mail_template_helpers(xml_content):
    """Remove env parameter from mail template helper functions

    In Odoo 19, format_datetime/format_date/format_amount should NOT receive 'env' parameter.
    The helpers access the environment internally.

    Common error: AttributeError: 'Environment' object has no attribute 'tzinfo'
    """
    import re

    # Fix format_datetime(env, ...) -> format_datetime(...)
    xml_content = re.sub(
        r'format_datetime\(\s*env\s*,\s*',
        'format_datetime(',
        xml_content
    )

    # Fix format_date(env, ...) -> format_date(...)
    xml_content = re.sub(
        r'format_date\(\s*env\s*,\s*',
        'format_date(',
        xml_content
    )

    # Fix format_amount(env, ...) -> format_amount(...)
    xml_content = re.sub(
        r'format_amount\(\s*env\s*,\s*',
        'format_amount(',
        xml_content
    )

    return xml_content
```

### 8. XML Entity Encoding Fix (NEW - Odoo 19)
```python
def fix_xml_entities(xml_content):
    """Replace HTML entities with numeric character references

    XML only supports 5 predefined entities: &lt; &gt; &amp; &quot; &apos;
    All other special characters must use numeric references.

    Common error: lxml.etree.XMLSyntaxError: Entity 'copy' not defined
    """
    # Map of common HTML entities to numeric character references
    entity_map = {
        '&copy;': '&#169;',      # Copyright ©
        '&nbsp;': '&#160;',      # Non-breaking space
        '&mdash;': '&#8212;',    # Em dash —
        '&ndash;': '&#8211;',    # En dash –
        '&trade;': '&#8482;',    # Trademark ™
        '&reg;': '&#174;',       # Registered ®
        '&euro;': '&#8364;',     # Euro €
        '&pound;': '&#163;',     # Pound £
        '&yen;': '&#165;',       # Yen ¥
        '&cent;': '&#162;',      # Cent ¢
        '&bull;': '&#8226;',     # Bullet •
        '&hellip;': '&#8230;',   # Ellipsis …
        '&laquo;': '&#171;',     # Left angle quote «
        '&raquo;': '&#187;',     # Right angle quote »
        '&times;': '&#215;',     # Multiplication ×
        '&divide;': '&#247;',    # Division ÷
    }

    for entity, numeric_ref in entity_map.items():
        xml_content = xml_content.replace(entity, numeric_ref)

    return xml_content
```

### 9. Portal XPath Migration (NEW - Odoo 19)
```python
def fix_portal_xpaths(xml_content):
    """Update sale portal XPath expressions for Odoo 19 structure changes

    Odoo 19 changed the sale portal template structure:
    - Removed wrapper: <t t-if='not line.display_type'>
    - Uses named elements: tr[@name='tr_product'], td[@name='td_product_*']
    - Positional selectors (th[3], td[3]) no longer work

    Common error: Element '<xpath expr="..."/>' cannot be located in parent view
    """
    import re

    # Fix table header positional selectors
    header_replacements = {
        r"thead/tr/th\[3\]": "thead/tr/th[@id='product_unit_price_header']",
        r"thead/tr/th\[4\]": "thead/tr/th[@id='product_discount_header']",
        r"thead/tr/th\[@id='taxes'\]": "thead/tr/th[@id='taxes_header']",
        r"thead/tr/th\[@id='subtotal'\]": "thead/tr/th[@id='subtotal_header']",
    }

    for old_pattern, new_pattern in header_replacements.items():
        xml_content = re.sub(old_pattern, new_pattern, xml_content)

    # Fix table body nested conditional wrappers
    # Old: //tbody//t[@t-foreach='lines_to_report']//tr/t[@t-if='not line.display_type']/td[3]
    # New: //tbody//tr[@name='tr_product']/td[@name='td_product_priceunit']

    body_cell_map = {
        r"//tr/t\[@t-if='not line\.display_type'\]/td\[3\]":
            "//tr[@name='tr_product']/td[@name='td_product_priceunit']",
        r"//tr/t\[@t-if='not line\.display_type'\]/td\[@id='taxes'\]":
            "//tr[@name='tr_product']/td[@name='td_product_taxes']",
        r"//tr/t\[@t-if='not line\.display_type'\]/td\[@id='subtotal'\]":
            "//tr[@name='tr_product']/td[@name='td_product_subtotal']",
    }

    for old_xpath, new_xpath in body_cell_map.items():
        xml_content = re.sub(old_xpath, new_xpath, xml_content)

    # Fix sidebar data-id attributes
    xml_content = re.sub(
        r"//h2\[@data-id='total_amount'\]",
        "//t[@t-set='title']//h2[@t-field='sale_order.amount_total']",
        xml_content
    )

    return xml_content
```

### 10. Complete XML Processor (UPDATED)
```python
def process_xml_file(file_path):
    """Apply all XML fixes to a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply all fixes
    content = content.replace('<tree', '<list')
    content = content.replace('</tree>', '</list>')
    content = content.replace('edit="1"', '')
    content = fix_search_views(content)
    content = fix_active_id(content)
    content = fix_kanban_templates(content)
    content = fix_cron_jobs(content)
    content = fix_t_if_expressions(content)

    # NEW Odoo 19 fixes
    content = fix_mail_template_helpers(content)
    content = fix_xml_entities(content)
    content = fix_portal_xpaths(content)

    # Remove website.snippet_options inheritance
    pattern = r'<template[^>]*inherit_id="website\.snippet_options"[^>]*>.*?</template>\s*'
    content = re.sub(pattern, '', content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True
```

## Batch Processing Script
```python
import os
import glob

def fix_all_xml_files(project_path):
    """Process all XML files in a project"""
    xml_files = glob.glob(os.path.join(project_path, '**/*.xml'), recursive=True)

    fixed_count = 0
    errors = []

    for xml_file in xml_files:
        try:
            process_xml_file(xml_file)
            fixed_count += 1
            print(f"✓ Fixed: {xml_file}")
        except Exception as e:
            errors.append((xml_file, str(e)))
            print(f"✗ Error in {xml_file}: {e}")

    print(f"\n✓ Fixed {fixed_count} files")
    if errors:
        print(f"✗ {len(errors)} errors encountered")

    return fixed_count, errors
```

## View-Specific Fixes

### Form Views
```xml
<!-- Before -->
<form string="Title" edit="1">
    <button context="{'default_type_id': active_id}"/>
</form>

<!-- After -->
<form string="Title">
    <button context="{'default_type_id': id}"/>
</form>
```

### List Views
```xml
<!-- Before -->
<tree string="Items" edit="1" editable="top">
    <field name="name"/>
</tree>

<!-- After -->
<list string="Items" editable="top">
    <field name="name"/>
</list>
```

### Kanban Views
```xml
<!-- Before -->
<kanban js_class="custom_kanban">
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_card">
                <!-- content -->
            </div>
        </t>
    </templates>
</kanban>

<!-- After -->
<kanban>
    <templates>
        <t t-name="card">
            <div class="oe_kanban_card">
                <!-- content -->
            </div>
        </t>
    </templates>
</kanban>
```

### Search Views
```xml
<!-- Before -->
<search>
    <field name="name"/>
    <group expand="0" string="Group By">
        <filter name="type" string="Type" context="{'group_by': 'type_id'}"/>
    </group>
    <group expand="0" string="Filters">
        <filter name="active" string="Active" domain="[('active', '=', True)]"/>
    </group>
</search>

<!-- After -->
<search>
    <field name="name"/>
    <filter name="type" string="Type" context="{'group_by': 'type_id'}"/>
    <filter name="active" string="Active" domain="[('active', '=', True)]"/>
</search>
```

## Validation

After applying fixes, validate XML:
```python
from lxml import etree

def validate_xml(file_path):
    """Validate XML syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            etree.parse(f)
        return True, "Valid"
    except etree.XMLSyntaxError as e:
        return False, str(e)
```
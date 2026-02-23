# Version Helper

> **Purpose**: Helper functions for detecting and working with Odoo versions.

## Version Detection

### Detection Priority

1. **User-specified flag**: `--version 17`
2. **Directory path**: Extract from `odoo14`, `odoo15`, `odoo17`, etc.
3. **Manifest version**: Parse `__manifest__.py` version string
4. **Config file**: Check Odoo configuration file
5. **Ask user**: If ambiguous

### Detection Logic

```python
def detect_odoo_version(context):
    """
    Detect Odoo version from context.

    Priority:
    1. User flag
    2. Directory path
    3. Manifest
    4. Config file
    """

    # 1. Check user flag
    if context.get('version_flag'):
        return int(context['version_flag'])

    # 2. Check directory path
    cwd = context.get('cwd', os.getcwd())
    match = re.search(r'odoo(\d{2})', cwd)
    if match:
        return int(match.group(1))

    # 3. Check manifest
    manifest_path = find_manifest(cwd)
    if manifest_path:
        version = parse_manifest_version(manifest_path)
        if version:
            return version

    # 4. Unable to detect
    return None


def parse_manifest_version(manifest_path):
    """
    Parse version from __manifest__.py

    Version format: "X.Y.Z.W.V" where X is Odoo version
    Examples: "17.0.1.0.0" → 17
              "16.0.2.1.0" → 16
    """
    with open(manifest_path) as f:
        content = f.read()

    # Find version string
    match = re.search(r"['\"]version['\"]\s*:\s*['\"](\d+)\.", content)
    if match:
        return int(match.group(1))

    return None
```

## Version-Specific Features

```python
VERSION_FEATURES = {
    14: {
        'output_tag': 't-esc',
        'report_attachment': 'report_template',
        'has_template_category': False,
        'has_company_branding': False,
    },
    15: {
        'output_tag': 't-out',
        'report_attachment': 'report_template',
        'has_template_category': False,
        'has_company_branding': False,
        'has_format_datetime': True,
    },
    16: {
        'output_tag': 't-out',
        'report_attachment': 'report_template',
        'has_template_category': True,
        'has_company_branding': False,
        'has_format_datetime': True,
        'has_is_html_empty': True,
    },
    17: {
        'output_tag': 't-out',
        'report_attachment': 'report_template_ids',
        'has_template_category': True,
        'has_company_branding': False,
        'has_format_datetime': True,
        'has_is_html_empty': True,
    },
    18: {
        'output_tag': 't-out',
        'report_attachment': 'report_template_ids',
        'has_template_category': True,
        'has_company_branding': False,
        'has_format_datetime': True,
        'has_is_html_empty': True,
    },
    19: {
        'output_tag': 't-out',
        'report_attachment': 'report_template_ids',
        'has_template_category': True,
        'has_company_branding': True,
        'has_format_datetime': True,
        'has_is_html_empty': True,
    },
}


def get_output_tag(version):
    """Get appropriate output tag for version."""
    return VERSION_FEATURES.get(version, {}).get('output_tag', 't-out')


def get_report_attachment_field(version):
    """Get appropriate report attachment field for version."""
    return VERSION_FEATURES.get(version, {}).get('report_attachment', 'report_template_ids')


def has_feature(version, feature):
    """Check if version has a specific feature."""
    return VERSION_FEATURES.get(version, {}).get(feature, False)
```

## Version Comparison

```python
def is_version_at_least(current, minimum):
    """Check if current version is at least minimum."""
    return current >= minimum


def is_version_between(current, min_ver, max_ver):
    """Check if current version is in range [min, max]."""
    return min_ver <= current <= max_ver


def requires_migration(from_ver, to_ver):
    """Determine what migrations are needed."""
    migrations = []

    if from_ver < 15 <= to_ver:
        migrations.append('t-esc to t-out')

    if from_ver < 16 <= to_ver:
        migrations.append('add template_category')

    if from_ver < 17 <= to_ver:
        migrations.append('report_template to report_template_ids')

    if from_ver < 19 <= to_ver:
        migrations.append('add company branding colors')

    return migrations
```

## Usage in Commands

```python
# In create-email-template command:
version = detect_odoo_version(context)
output_tag = get_output_tag(version)
attachment_field = get_report_attachment_field(version)

# Generate appropriate syntax
if version >= 17:
    attachment_xml = f'<field name="report_template_ids" eval="[(4, ref(\'{report_ref}\'))]"/>'
else:
    attachment_xml = f'<field name="report_template" ref="{report_ref}"/>'
```

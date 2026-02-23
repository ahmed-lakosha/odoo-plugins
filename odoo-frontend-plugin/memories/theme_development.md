# Theme Development Best Practices

## Theme Module Structure

```
theme_name/
├── __init__.py
├── __manifest__.py
├── security/
│   └── ir.model.access.csv
├── data/
│   ├── assets.xml
│   ├── menu.xml
│   └── pages/
│       ├── home_page.xml        # Individual page files (best practice)
│       ├── aboutus_page.xml
│       ├── contactus_page.xml
│       └── services_page.xml
├── views/
│   ├── layout/
│   │   ├── header.xml
│   │   ├── footer.xml
│   │   └── templates.xml
│   └── snippets/
│       └── custom_snippets.xml
└── static/
    ├── description/
    │   └── icon.png
    └── src/
        ├── scss/
        │   ├── primary_variables.scss
        │   ├── bootstrap_overridden.scss
        │   └── theme.scss
        ├── js/
        │   ├── theme.js
        │   └── snippets_options.js
        └── img/
```

## Key Patterns

### 1. Individual Page Files (Best Practice)
Create separate files for each page instead of a single pages.xml:
- `data/pages/home_page.xml`
- `data/pages/aboutus_page.xml`
- `data/pages/contactus_page.xml`

### 2. Theme Mirror Models
Use `theme.website.page` for multi-website support:
```xml
<record id="page_home" model="theme.website.page">
    <field name="view_id" ref="view_home"/>
    <field name="url">/</field>
    <field name="is_published" eval="True"/>
</record>
```

### 3. View Inheritance
For homepage, inherit from website.homepage:
```xml
<template id="homepage_inherit" inherit_id="website.homepage" name="Theme Homepage">
    <!-- Custom content -->
</template>
```

### 4. Asset Bundle Registration
```python
'assets': {
    'web._assets_primary_variables': [
        'theme_name/static/src/scss/primary_variables.scss',
    ],
    'web._assets_frontend_helpers': [
        ('prepend', 'theme_name/static/src/scss/bootstrap_overridden.scss'),
    ],
    'web.assets_frontend': [
        'theme_name/static/src/scss/theme.scss',
        'theme_name/static/src/js/theme.js',
    ],
},
```

## Version-Specific Patterns

### Odoo 14-15 (Bootstrap 4)
- Use `ml-*`, `mr-*` margin classes
- Different asset bundle syntax

### Odoo 16-17 (Bootstrap 5.1.3)
- Use `ms-*`, `me-*` margin classes
- Modern asset bundle syntax

### Odoo 18-19 (Bootstrap 5.1.3 + Snippet Groups)
- Use snippet groups for registration
- Enhanced website builder integration

---
title: 'Theme Web Rec'
read_only: false
type: 'command'
description: 'Create theme mirror models following Odoo core patterns for website themes'
---

# Theme Website Record Command

You are implementing the `/odoo-frontend:theme_web_rec` command that creates theme mirror models following Odoo core patterns from `website.page`/`theme.website.page` architecture.

## Functionality

This command helps developers create proper theme mirror models for Odoo website themes, automating the complex process of setting up the mirror model architecture required for multi-website support in Odoo.

## What This Command Does

1. **Analyzes existing website model** structure to understand fields and inheritance
2. **Updates website model** with view delegation pattern (following website.page pattern)
3. **Creates theme mirror models** (theme.website.MODEL_NAME)
4. **Sets up installation hooks** (ir.module.module extensions)
5. **Updates security rules** for new models
6. **Creates theme data** with sample templates
7. **Updates manifests** with proper dependencies

## Usage Examples

### Basic Usage
- **Command**: `/theme_web_rec <website_module_path> <theme_module_path>`
- **Example**: `/theme_web_rec projects/pearlpixels/website_portfolio projects/pearlpixels/theme_pearlpixels`

### With Model Name (if auto-detection fails)
- **Command**: `/theme_web_rec <website_module_path> <theme_module_path> <model_name>`
- **Example**: `/theme_web_rec projects/pp/website_portfolio projects/pp/theme_pp portfolio`

## Implementation Details

When the user invokes this command, you should:

1. **Parse the command arguments** to extract:
   - Website module path (required)
   - Theme module path (required)
   - Model name (optional - can auto-detect)

2. **Use the theme mirror generator script** located at:
   ```
   plugins/odoo-frontend-plugin/odoo-frontend/scripts/theme_mirror_generator.py
   ```

3. **Execute the script** with the provided arguments:
   ```bash
   python plugins/odoo-frontend-plugin/odoo-frontend/scripts/theme_mirror_generator.py <website_path> <theme_path> [model_name]
   ```

4. **Show progress** as the script runs, displaying:
   - Model analysis results
   - Files being created/updated
   - Success/failure for each step

5. **Provide clear next steps** after completion:
   - How to update the website module
   - How to install the theme
   - How to verify the setup

## Key Features

### Smart Mixin Detection
- Detects `website.published.multi.mixin` and skips URL field duplication
- Recognizes `website.seo.metadata` for SEO fields

### Correct Field Types
- Uses `arch = fields.Text` (not Html)
- Proper view delegation with `_inherits`

### Proper File Generation
- Creates theme_models.py following Odoo core patterns
- Extends ir.module.module for theme installation
- Updates security CSV with correct formatting

### Template Structure
- Generates professional, creative, and minimal templates
- Uses proper `<template>` syntax with wrapper views

## Error Handling

If errors occur, provide clear messages about:
- Missing module paths
- Unable to detect model name
- File permission issues
- Invalid module structure

## Success Indicators

After successful execution, confirm that:
- All files were created/updated
- Theme mirror models are properly configured
- Security rules are in place
- Manifests have correct dependencies

## Reference Documentation

This command implements the Odoo theme mirror model pattern from:
- `odoo/addons/website/models/theme_models.py`
- `odoo/addons/website/models/ir_module_module.py`
- `odoo/addons/website/models/website_page.py`

## Notes

- This command is specifically designed for Odoo 14-19
- It follows Odoo's multi-website architecture
- Creates proper theme isolation per website
- Enables theme reusability across multiple sites
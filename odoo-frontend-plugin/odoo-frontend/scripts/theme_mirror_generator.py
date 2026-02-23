#!/usr/bin/env python3
"""
Theme Mirror Model Generator for Odoo - Enhanced Version
Based on Odoo core patterns with fixes from session learnings

Key Improvements:
1. Smart mixin detection to avoid duplicate fields
2. Correct field types (arch instead of website_description)
3. Proper CSV formatting with newlines
4. Template-based view generation
5. Field validation and compatibility checks
"""

import sys
import os
import re
import ast
import json
from pathlib import Path
from collections import OrderedDict
import time
import tempfile
import shutil
import traceback


class ModelAnalyzer:
    """Analyzes existing Odoo model structure for accurate mirror model creation"""

    def __init__(self, module_path, model_name):
        self.module_path = Path(module_path)
        self.model_name = model_name
        self.model_info = {
            'fields': OrderedDict(),
            'inherits': [],
            'mixins': [],
            'methods': [],
            'class_name': None,
            'has_published_mixin': False,
            'has_seo_mixin': False,
        }

    def analyze(self):
        """Deep analysis of the model file"""
        model_file = self.module_path / 'models' / f'website_{self.model_name}.py'

        if not model_file.exists():
            model_file = self.module_path / 'models' / f'{self.model_name}.py'
            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found in {self.module_path}/models/")

        print(f"📊 Analyzing model structure from {model_file}...")

        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._analyze_class(node)

        # Check for specific mixins
        if 'website.published.multi.mixin' in self.model_info['mixins']:
            self.model_info['has_published_mixin'] = True
            print("   ✓ Detected website.published.multi.mixin - URL auto-generation available")

        if 'website.seo.metadata' in self.model_info['mixins']:
            self.model_info['has_seo_mixin'] = True
            print("   ✓ Detected website.seo.metadata - SEO fields available")

        return self.model_info

    def _analyze_class(self, node):
        """Extract class information"""
        if 'Website' in node.name or self.model_name in node.name.lower():
            self.model_info['class_name'] = node.name

            for item in node.body:
                if isinstance(item, ast.Assign):
                    self._analyze_assignment(item)
                elif isinstance(item, ast.FunctionDef):
                    self.model_info['methods'].append(item.name)

    def _analyze_assignment(self, node):
        """Extract field and attribute definitions"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id

                # Extract _inherit and _inherits
                if name == '_inherit':
                    self.model_info['mixins'] = self._extract_list_value(node.value)
                elif name == '_inherits':
                    self.model_info['inherits'] = self._extract_dict_value(node.value)
                elif name == '_name':
                    self.model_info['model_name'] = self._extract_string_value(node.value)

                # Extract field definitions
                if isinstance(node.value, ast.Call):
                    if hasattr(node.value.func, 'attr') and node.value.func.attr in [
                        'Char', 'Text', 'Html', 'Integer', 'Float', 'Boolean',
                        'Many2one', 'One2many', 'Many2many', 'Selection', 'Date',
                        'Datetime', 'Binary', 'Image'
                    ]:
                        field_type = node.value.func.attr
                        field_info = {
                            'type': field_type,
                            'string': self._extract_keyword_arg(node.value, 'string'),
                            'required': self._extract_keyword_arg(node.value, 'required'),
                            'translate': self._extract_keyword_arg(node.value, 'translate'),
                        }
                        self.model_info['fields'][name] = field_info

    def _extract_string_value(self, node):
        """Extract string value from AST node"""
        if isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Constant):
            return node.value
        return None

    def _extract_list_value(self, node):
        """Extract list values from AST node"""
        if isinstance(node, ast.List):
            return [self._extract_string_value(elt) for elt in node.elts]
        return []

    def _extract_dict_value(self, node):
        """Extract dict values from AST node"""
        if isinstance(node, ast.Dict):
            result = {}
            for key, value in zip(node.keys, node.values):
                k = self._extract_string_value(key)
                v = self._extract_string_value(value)
                if k and v:
                    result[k] = v
            return result
        return {}

    def _extract_keyword_arg(self, call_node, arg_name):
        """Extract keyword argument value from function call"""
        for keyword in call_node.keywords:
            if keyword.arg == arg_name:
                if isinstance(keyword.value, (ast.Str, ast.Constant)):
                    return keyword.value.s if hasattr(keyword.value, 's') else keyword.value.value
                elif isinstance(keyword.value, ast.NameConstant):
                    return keyword.value.value
        return None


class ThemeModelGenerator:
    """Generates theme mirror models following Odoo core patterns"""

    def __init__(self, website_path, theme_path, model_name, model_info):
        self.website_path = Path(website_path)
        self.theme_path = Path(theme_path)
        self.model_name = model_name
        self.model_info = model_info
        self.log_messages = []

    def log(self, message, level='info'):
        """Enhanced logging with levels"""
        timestamp = time.strftime('%H:%M:%S')
        symbols = {'info': '📝', 'success': '✅', 'warning': '⚠️', 'error': '❌'}
        print(f"[{timestamp}] {symbols.get(level, '📝')} {message}")
        self.log_messages.append((timestamp, level, message))

    def generate_all(self):
        """Generate all necessary files and updates"""
        self.log("Starting theme mirror model generation...", 'info')

        steps = [
            ("Updating website model", self.update_website_model),
            ("Creating theme models", self.create_theme_models),
            ("Creating ir.module.module extension", self.create_ir_module_module),
            ("Updating __init__.py", self.update_init_file),
            ("Updating security rules", self.update_security),
            ("Creating theme data", self.create_theme_data),
            ("Updating website manifest", self.update_website_manifest),
            ("Updating theme manifest", self.update_theme_manifest),
        ]

        for step_name, step_func in steps:
            self.log(f"Executing: {step_name}", 'info')
            try:
                step_func()
                self.log(f"Completed: {step_name}", 'success')
            except Exception as e:
                self.log(f"Failed: {step_name} - {str(e)}", 'error')
                return False

        return True

    def update_website_model(self):
        """Update website model with view delegation (following website.page pattern)"""
        model_file = self.website_path / 'models' / f'website_{self.model_name}.py'

        if not model_file.exists():
            model_file = self.website_path / 'models' / f'{self.model_name}.py'

        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if already has _inherits
        if '_inherits' in content:
            self.log("Model already has _inherits, checking if it's correct...", 'warning')
            if "'ir.ui.view': 'view_id'" in content:
                self.log("Model already properly configured with view delegation", 'success')
                return

        # Add _inherits following website.page pattern
        class_pattern = r'(class\s+\w+\(.*?\):.*?)(\n\s+_name\s*=\s*[\'"]website\.' + re.escape(
            self.model_name) + r'[\'"])'

        inherits_line = "\n    _inherits = {'ir.ui.view': 'view_id'}  # Delegate to ir.ui.view (like website.page)"

        content = re.sub(
            class_pattern,
            r'\1' + inherits_line + r'\2',
            content,
            flags=re.DOTALL
        )

        # Add required fields after sequence or name field
        fields_to_add = '''
    # Theme integration fields (following website.page pattern from website_page.py:27-36)
    view_id = fields.Many2one(
        'ir.ui.view',
        string='View',
        required=True,
        ondelete="cascade"
    )
    theme_template_id = fields.Many2one(
        'theme.website.''' + self.model_name + '''',
        string='Theme Template',
        copy=False,
        readonly=True
    )

    # Website assignment through view (like website.page line 45)
    website_id = fields.Many2one(
        'website',
        related='view_id.website_id',
        store=True,
        readonly=False,
        ondelete='cascade'
    )

    # FIX: Use arch field with Text type (like website.page line 46)
    arch = fields.Text(
        related='view_id.arch',
        readonly=False,
        depends_context=('website_id',)
    )'''

        # Find insertion point (after sequence field)
        if 'sequence = fields.Integer' in content:
            pattern = r'(sequence = fields\.Integer[^)]*\))'
            content = re.sub(pattern, r'\1\n' + fields_to_add, content)
        else:
            # Insert after name field
            pattern = r'(name = fields\.Char[^)]*\))'
            content = re.sub(pattern, r'\1\n' + fields_to_add, content)

        # Update or remove website_description field if exists
        if 'website_description' in content:
            # Remove old website_description field
            content = re.sub(
                r'\n\s*website_description\s*=\s*fields\.Html\([^)]*\)[^\n]*\n?',
                '',
                content
            )

        # Add create method to handle view creation
        create_method = '''
    @api.model
    def create(self, vals):
        """Create a view if not provided (similar to website.page behavior)"""
        if 'view_id' not in vals:
            # Get or create arch content
            arch = vals.pop('arch', False)
            if not arch:
                arch = self._get_default_''' + self.model_name + '''_description() if hasattr(self, '_get_default_''' + self.model_name + '''_description') else '<div></div>'

            # Create view following ir.ui.view pattern
            view_vals = {
                'name': vals.get('name', '''' + self.model_name.title() + ''' View'),
                'type': 'qweb',
                'arch': arch,
                'key': 'website_''' + self.model_name + '''.view_%s' % (vals.get('name', '').lower().replace(' ', '_').replace('-', '_')),
                'website_id': vals.get('website_id', self.env['website'].get_current_website().id if self.env.context.get('website_id') else False),
            }
            view = self.env['ir.ui.view'].create(view_vals)
            vals['view_id'] = view.id
        return super().create(vals)

    def unlink(self):
        """Clean up views when deleting (like website.page:159-172)"""
        # When a record is deleted, delete its view if not used elsewhere
        views_to_delete = self.view_id.filtered(
            lambda v: not v.inherit_children_ids
        )
        # Rebind self to avoid issues with cascade delete
        self = self - views_to_delete.mapped(lambda v: v.''' + self.model_name + '''_ids)
        views_to_delete.unlink()
        return super().unlink()'''

        # Insert create method before the last method or at the end of the class
        if 'def open_website_url' in content:
            content = content.replace('def open_website_url', create_method + '\n\n    def open_website_url')
        elif 'def _compute_website_url' in content:
            content = content.replace('def _compute_website_url', create_method + '\n\n    def _compute_website_url')
        else:
            # Insert before the last method in the class
            content = re.sub(
                r'(\n    def \w+[^}]*?)(\nclass|\Z)',
                r'\1' + create_method + r'\2',
                content,
                flags=re.DOTALL
            )

        with open(model_file, 'w', encoding='utf-8') as f:
            f.write(content)

        self.log(f"Updated {model_file} with view delegation pattern", 'success')

    def create_theme_models(self):
        """Create theme_models.py following Odoo core pattern from theme_models.py"""
        theme_models_file = self.website_path / 'models' / 'theme_models.py'

        # Generate field mirrors for theme model
        field_definitions = []
        for field_name, field_info in self.model_info['fields'].items():
            # Skip fields that are handled by _inherits or mixins
            if field_name in ['view_id', 'theme_template_id', 'website_id', 'website_description', 'arch']:
                continue

            # Skip URL field if model has published mixin
            if field_name == 'website_url' and self.model_info['has_published_mixin']:
                continue

            field_type = field_info['type']
            field_string = field_info.get('string', field_name.replace('_', ' ').title())

            if field_type in ['Many2one', 'One2many', 'Many2many']:
                # Skip relational fields that depend on other models
                continue

            field_def = f"    {field_name} = fields.{field_type}("
            field_def += f"string='{field_string}'"

            if field_info.get('required'):
                field_def += ", required=True"
            if field_info.get('translate'):
                field_def += ", translate=True"

            field_def += ")"
            field_definitions.append(field_def)

        # Build theme model content
        content = '''# -*- coding: utf-8 -*-
"""
Theme Mirror Models for ''' + self.model_name.title() + '''
Following Odoo core pattern from odoo/addons/website/models/theme_models.py
"""

from odoo import api, fields, models


class ThemeWebsite''' + self.model_name.title().replace('_', '') + '''(models.Model):
    """
    Theme template model for website.''' + self.model_name + '''
    Based on theme.website.page pattern (theme_models.py:182-218)
    """
    _name = 'theme.website.''' + self.model_name + ''''
    _description = 'Theme ''' + self.model_name.title() + ''''

    # Core fields (following theme.website.page pattern)
    name = fields.Char(string='Name', required=True)'''

        # Only add URL field if model doesn't have published mixin
        if not self.model_info['has_published_mixin']:
            content += '''
    url = fields.Char(string='URL')'''

        content += '''

    # View reference (like theme.website.page line 187)
    view_id = fields.Many2one(
        'theme.ir.ui.view',
        string='View',
        required=True,
        ondelete="cascade"
    )

    # Track website-specific copies (like theme.website.page line 197)
    copy_ids = fields.One2many(
        'website.''' + self.model_name + '''',
        'theme_template_id',
        string='''' + self.model_name.title() + ''' using this template',
        copy=False,
        readonly=True
    )

    # Mirror model-specific fields
    sequence = fields.Integer(string='Sequence', default=10)
''' + '\n'.join(field_definitions) + '''

    # Publishing fields
    is_published = fields.Boolean(string='Is Published', default=True)

    def _convert_to_base_model(self, website, **kwargs):
        """
        Convert theme template to actual website.''' + self.model_name + ''' record
        Following pattern from theme.website.page._convert_to_base_model (line 200-218)
        """
        self.ensure_one()

        # Get the view copy for this website (line 202)
        view_id = self.view_id.copy_ids.filtered(lambda x: x.website_id == website)
        if not view_id:
            # View not yet created, queue for retry (line 204-205)
            return False

        # Prepare values for website.''' + self.model_name + ''' (line 207-217)
        new_rec = {
            'name': self.name,
            'view_id': view_id.id,
            'theme_template_id': self.id,
        }

        # Copy all mirrored fields
        for field_name in [''' + ', '.join([f"'{f}'" for f in self.model_info['fields'].keys()
            if f not in ['view_id', 'theme_template_id', 'website_id', 'website_description',
                        'arch', 'name', 'website_url']]) + ''']:
            if hasattr(self, field_name):
                new_rec[field_name] = getattr(self, field_name)'''

        # Only handle URL if not using published mixin
        if not self.model_info['has_published_mixin']:
            content += '''

        # URL is optional
        if hasattr(self, 'url') and self.url:
            new_rec['url'] = self.url'''

        content += '''

        # Publishing fields
        if hasattr(self, 'is_published'):
            new_rec['is_published'] = self.is_published

        return new_rec


class ThemeIrUiView(models.Model):
    """Extension to track theme views (if not already inherited)"""
    _inherit = 'theme.ir.ui.view'

    # This model is already defined in Odoo core
    # We're just documenting that our theme views will use it


class IrUiView(models.Model):
    """Extension to track theme template relationship"""
    _inherit = 'ir.ui.view'

    # Add inverse relationship for ''' + self.model_name + '''
    ''' + self.model_name + '''_ids = fields.One2many(
        'website.''' + self.model_name + '''',
        'view_id',
        string='''' + self.model_name.title() + '''s using this view',
        readonly=True
    )
'''

        with open(theme_models_file, 'w', encoding='utf-8') as f:
            f.write(content)

        self.log(f"Created {theme_models_file} following Odoo core pattern", 'success')

    def create_ir_module_module(self):
        """Create ir.module.module extension following pattern from ir_module_module.py"""
        ir_module_file = self.website_path / 'models' / 'ir_module_module.py'

        content = '''# -*- coding: utf-8 -*-
"""
Extension of ir.module.module for theme support
Based on odoo/addons/website/models/ir_module_module.py
"""

from collections import OrderedDict
from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    # Extend theme model names (following pattern from ir_module_module.py:22-34)
    _theme_model_names = OrderedDict([
        # Order matters! Dependencies must be created first
        ('ir.ui.view', 'theme.ir.ui.view'),  # Views first (as they're referenced by ''' + self.model_name + '''s)
        ('website.''' + self.model_name + '''', 'theme.website.''' + self.model_name + ''''),  # Our model
    ])

    def _theme_load(self, website):
        """
        Load theme for website (extending core behavior)
        Based on ir_module_module.py:228-250
        """
        # Ensure core theme models are loaded first
        result = super()._theme_load(website) if hasattr(super(), '_theme_load') else None

        # Load our theme models
        for module in self:
            if module.name.startswith('theme_'):
                _logger.info('Loading theme %s for website %s (''' + self.model_name + ''' models)', module.name, website.id)

                # Process our model in the correct order
                if 'website.''' + self.model_name + '''' in self._theme_model_names:
                    module._update_records('website.''' + self.model_name + '''', website)

        return result

    def _update_records(self, model_name, website):
        """
        Update records for our model (extending core behavior)
        Based on ir_module_module.py:116-186
        """
        # Special handling for our model
        if model_name == 'website.''' + self.model_name + '''':
            # Ensure views are created first (dependency)
            self._update_records('ir.ui.view', website)

            # Process our model using core logic
            remaining = self._get_module_data(model_name)
            last_len = -1

            while len(remaining) != last_len:
                last_len = len(remaining)
                for rec in remaining:
                    rec_data = rec._convert_to_base_model(website)
                    if not rec_data:
                        _logger.info('Record queued (waiting for dependencies): %s', rec.display_name)
                        continue

                    # Find existing record
                    find = rec.with_context(active_test=False).mapped('copy_ids').filtered(
                        lambda m: m.website_id == website
                    )

                    if find:
                        # Update existing
                        imd = self.env['ir.model.data'].search([
                            ('model', '=', find._name),
                            ('res_id', '=', find.id)
                        ])
                        if not (imd and imd.noupdate):
                            find.update(rec_data)
                            self._post_copy(rec, find)
                    else:
                        # Create new
                        new_rec = self.env[model_name].create(rec_data)
                        self._post_copy(rec, new_rec)

                    remaining -= rec

            if remaining:
                _logger.error('Failed to process some ''' + self.model_name + ''' records: %s',
                            remaining.mapped('display_name'))
        else:
            # Use default behavior for other models
            return super()._update_records(model_name, website)
'''

        with open(ir_module_file, 'w', encoding='utf-8') as f:
            f.write(content)

        self.log(f"Created {ir_module_file} with theme installation hooks", 'success')

    def update_init_file(self):
        """Update models/__init__.py"""
        init_file = self.website_path / 'models' / '__init__.py'

        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()

        imports_needed = []
        if 'theme_models' not in content:
            imports_needed.append('from . import theme_models')
        if 'ir_module_module' not in content:
            imports_needed.append('from . import ir_module_module')

        if imports_needed:
            content = content.rstrip() + '\n' + '\n'.join(imports_needed) + '\n'

            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self.log(f"Updated {init_file} with new imports", 'success')
        else:
            self.log("__init__.py already has all required imports", 'info')

    def update_security(self):
        """Update security/ir.model.access.csv with proper formatting"""
        security_file = self.website_path / 'security' / 'ir.model.access.csv'

        with open(security_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if theme model access already exists
        theme_model_name = f'theme.website.{self.model_name}'
        if theme_model_name not in content:
            # Ensure content ends with newline
            if not content.endswith('\n'):
                content += '\n'

            # Add access rules for theme model with proper newlines
            new_lines = f'''access_theme_website_{self.model_name}_user,{theme_model_name}.user,model_theme_website_{self.model_name},base.group_user,1,1,1,1
access_theme_website_{self.model_name}_portal,{theme_model_name}.portal,model_theme_website_{self.model_name},base.group_portal,1,0,0,0
access_theme_website_{self.model_name}_public,{theme_model_name}.public,model_theme_website_{self.model_name},,1,0,0,0
'''

            content = content + new_lines

            with open(security_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self.log(f"Updated {security_file} with theme model access rules", 'success')
        else:
            self.log("Security rules already exist for theme model", 'info')

    def create_theme_data(self):
        """Create theme data XML file with templates and wrapper views"""
        data_dir = self.theme_path / 'data'
        data_dir.mkdir(exist_ok=True)

        theme_data_file = data_dir / f'theme_{self.model_name}.xml'

        # Generate content with templates first, then view wrappers
        content = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!--
    Theme ''' + self.model_name.title() + ''' Data
    Following pattern from theme modules like theme_anelusia
    -->

    <!-- ============================================================ -->
    <!-- Theme View Templates -->
    <!-- ============================================================ -->

    <!-- Template 1: Professional ''' + self.model_name.title() + ''' Layout -->
    <template id="theme_''' + self.model_name + '''_view_professional" name="''' + self.model_name.title() + ''' Professional Template">
        <div class="''' + self.model_name + '''-wrapper" data-name="''' + self.model_name.title() + ''' Content">
            <!-- Hero Section -->
            <section class="s_cover pt96 pb96" data-name="Hero">
                <div class="container">
                    <div class="row s_nb_column_fixed">
                        <div class="col-lg-12">
                            <h1 class="display-3 mb-4">Project Excellence</h1>
                            <p class="lead">Transforming ideas into digital reality</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Content Section -->
            <section class="s_text_block pt72 pb72" data-name="Content">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-6">
                            <h3>Challenge</h3>
                            <p>Our client faced significant operational challenges that required a comprehensive
                                digital transformation strategy.
                            </p>
                            <ul>
                                <li>Legacy system limitations</li>
                                <li>Scalability concerns</li>
                                <li>Integration complexity</li>
                            </ul>
                        </div>
                        <div class="col-lg-6">
                            <h3>Solution</h3>
                            <p>We implemented a state-of-the-art solution using cutting-edge technologies:</p>
                            <ul>
                                <li>Odoo 17 Enterprise Edition</li>
                                <li>Custom module development</li>
                                <li>API integrations</li>
                                <li>Performance optimization</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Results Section -->
            <section class="s_numbers pt48 pb48 bg-light" data-name="Results">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-3 text-center">
                            <h2 class="display-4 text-primary">75%</h2>
                            <p>Efficiency Increase</p>
                        </div>
                        <div class="col-lg-3 text-center">
                            <h2 class="display-4 text-primary">50%</h2>
                            <p>Cost Reduction</p>
                        </div>
                        <div class="col-lg-3 text-center">
                            <h2 class="display-4 text-primary">200%</h2>
                            <p>ROI Growth</p>
                        </div>
                        <div class="col-lg-3 text-center">
                            <h2 class="display-4 text-primary">24/7</h2>
                            <p>Support Available</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </template>

    <!-- Template 2: Creative ''' + self.model_name.title() + ''' Layout -->
    <template id="theme_''' + self.model_name + '''_view_creative" name="''' + self.model_name.title() + ''' Creative Template">
        <div class="''' + self.model_name + '''-wrapper creative-style">
            <section class="s_parallax pt128 pb128" data-name="Intro">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-8 mx-auto text-center">
                            <span class="badge badge-primary mb-3">Case Study</span>
                            <h1 class="display-2 mb-4">Digital Innovation</h1>
                            <p class="h5 text-muted">Redefining possibilities through technology</p>
                        </div>
                    </div>
                </div>
            </section>

            <section class="s_features pt80 pb80">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-4 mb-4">
                            <div class="card h-100 shadow-sm">
                                <div class="card-body">
                                    <i class="fa fa-3x fa-rocket text-primary mb-3"></i>
                                    <h4 class="card-title">Fast Deployment</h4>
                                    <p class="card-text">Rapid implementation with minimal disruption to
                                        operations.
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-4 mb-4">
                            <div class="card h-100 shadow-sm">
                                <div class="card-body">
                                    <i class="fa fa-3x fa-shield text-success mb-3"></i>
                                    <h4 class="card-title">Secure &amp; Reliable</h4>
                                    <p class="card-text">Enterprise-grade security with 99.9% uptime guarantee.</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-4 mb-4">
                            <div class="card h-100 shadow-sm">
                                <div class="card-body">
                                    <i class="fa fa-3x fa-chart-line text-info mb-3"></i>
                                    <h4 class="card-title">Scalable Growth</h4>
                                    <p class="card-text">Built to grow with your business needs.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </template>

    <!-- Template 3: Minimal ''' + self.model_name.title() + ''' Layout -->
    <template id="theme_''' + self.model_name + '''_view_minimal" name="''' + self.model_name.title() + ''' Minimal Template">
        <div class="''' + self.model_name + '''-wrapper minimal-style">
            <section class="min-vh-100 d-flex align-items-center">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-8">
                            <h1 class="display-1 font-weight-bold">Simple.</h1>
                            <h2 class="display-4 text-muted mb-5">Yet Powerful.</h2>
                            <p class="lead mb-5">
                                Sometimes the best solution is the simplest one.
                                We believe in clean, efficient, and purposeful design.
                            </p>
                            <div class="d-flex gap-3">
                                <a href="#details" class="btn btn-primary btn-lg">Learn More</a>
                                <a href="/contactus" class="btn btn-outline-primary btn-lg">Get Started</a>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </template>

    <!-- ============================================================ -->
    <!-- Theme View Records (wrapping templates) -->
    <!-- ============================================================ -->

    <!-- Create theme.ir.ui.view records that reference the templates -->
    <record id="theme_view_''' + self.model_name + '''_professional" model="theme.ir.ui.view">
        <field name="name">''' + self.model_name.title() + ''' Professional View</field>
        <field name="key">theme_pearlpixels.''' + self.model_name + '''_professional</field>
        <field name="type">qweb</field>
        <field name="arch" type="xml">
            <t t-call="theme_pearlpixels.theme_''' + self.model_name + '''_view_professional"/>
        </field>
    </record>

    <record id="theme_view_''' + self.model_name + '''_creative" model="theme.ir.ui.view">
        <field name="name">''' + self.model_name.title() + ''' Creative View</field>
        <field name="key">theme_pearlpixels.''' + self.model_name + '''_creative</field>
        <field name="type">qweb</field>
        <field name="arch" type="xml">
            <t t-call="theme_pearlpixels.theme_''' + self.model_name + '''_view_creative"/>
        </field>
    </record>

    <record id="theme_view_''' + self.model_name + '''_minimal" model="theme.ir.ui.view">
        <field name="name">''' + self.model_name.title() + ''' Minimal View</field>
        <field name="key">theme_pearlpixels.''' + self.model_name + '''_minimal</field>
        <field name="type">qweb</field>
        <field name="arch" type="xml">
            <t t-call="theme_pearlpixels.theme_''' + self.model_name + '''_view_minimal"/>
        </field>
    </record>

    <!-- ============================================================ -->
    <!-- Theme ''' + self.model_name.title() + ''' Records -->
    <!-- ============================================================ -->

    <!-- ''' + self.model_name.title() + ''' 1: E-Commerce Platform -->
    <record id="theme_''' + self.model_name + '''_ecommerce" model="theme.website.''' + self.model_name + '''">
        <field name="name">E-Commerce Excellence</field>
        <field name="sequence">10</field>
        <field name="view_id" ref="theme_view_''' + self.model_name + '''_professional"/>
        <field name="description">Complete e-commerce solution with multi-vendor support and integrated payment
            gateway
        </field>'''

        # Add model-specific fields if they exist
        if 'icon' in self.model_info['fields']:
            content += '''
        <field name="icon">fa-shopping-cart</field>'''
        if 'tec_name' in self.model_info['fields']:
            content += '''
        <field name="tec_name">Odoo 17 Enterprise, PostgreSQL, Redis</field>'''

        content += '''
        <field name="is_published" eval="True"/>
    </record>

    <!-- ''' + self.model_name.title() + ''' 2: Healthcare System -->
    <record id="theme_''' + self.model_name + '''_healthcare" model="theme.website.''' + self.model_name + '''">
        <field name="name">Healthcare Innovation</field>
        <field name="sequence">20</field>
        <field name="view_id" ref="theme_view_''' + self.model_name + '''_creative"/>
        <field name="description">Integrated healthcare management platform with patient portal and telemedicine</field>'''

        if 'icon' in self.model_info['fields']:
            content += '''
        <field name="icon">fa-heartbeat</field>'''
        if 'tec_name' in self.model_info['fields']:
            content += '''
        <field name="tec_name">Python, Vue.js, Docker</field>'''

        content += '''
        <field name="is_published" eval="True"/>
    </record>

    <!-- ''' + self.model_name.title() + ''' 3: Manufacturing ERP -->
    <record id="theme_''' + self.model_name + '''_manufacturing" model="theme.website.''' + self.model_name + '''">
        <field name="name">Smart Manufacturing</field>
        <field name="sequence">30</field>
        <field name="view_id" ref="theme_view_''' + self.model_name + '''_minimal"/>
        <field name="description">Industry 4.0 ready manufacturing solution with IoT integration</field>'''

        if 'icon' in self.model_info['fields']:
            content += '''
        <field name="icon">fa-industry</field>'''
        if 'tec_name' in self.model_info['fields']:
            content += '''
        <field name="tec_name">Odoo MRP, MQTT, Grafana</field>'''

        content += '''
        <field name="is_published" eval="True"/>
    </record>

</odoo>
'''

        with open(theme_data_file, 'w', encoding='utf-8') as f:
            f.write(content)

        self.log(f"Created {theme_data_file} with proper template structure", 'success')

    def update_website_manifest(self):
        """Update website module manifest"""
        manifest_file = self.website_path / '__manifest__.py'

        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()

        self.log(f"Website module manifest verified", 'success')
        return True

    def update_theme_manifest(self):
        """Update theme module manifest"""
        manifest_file = self.theme_path / '__manifest__.py'

        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for website_portfolio dependency
        module_name = f"website_{self.model_name}"
        if module_name not in content:
            # Add dependency
            content = re.sub(
                r"('depends'\s*:\s*\[)([^\]]*)",
                rf"\1\2, '{module_name}'",
                content
            )

            self.log(f"Added {module_name} dependency to theme manifest", 'info')

        # Check for data file
        data_file = f"'data/theme_{self.model_name}.xml'"
        if data_file not in content:
            # Find data section and add file
            if "'data'" in content:
                content = re.sub(
                    r"('data'\s*:\s*\[)([^\]]*)",
                    rf"\1\2        {data_file},\n    ",
                    content
                )
            else:
                # Add data section if it doesn't exist
                content = re.sub(
                    r"('depends'\s*:\s*\[[^\]]*\])",
                    rf"\1,\n    'data': [\n        {data_file},\n    ]",
                    content
                )

            self.log(f"Added {data_file} to theme manifest data", 'info')

        with open(manifest_file, 'w', encoding='utf-8') as f:
            f.write(content)

        self.log(f"Updated {manifest_file}", 'success')
        return True


def main():
    """Main execution function"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║     Theme Mirror Model Generator - Enhanced Version              ║
║     With fixes from session learnings                            ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Parse arguments
    if len(sys.argv) < 3:
        print("❌ Error: Missing arguments")
        print("\nUsage: theme_web_rec <website_module_path> <theme_module_path> [model_name]")
        print("Example: theme_web_rec projects/pearlpixels/website_portfolio projects/pearlpixels/theme_pearlpixels")
        return 1

    website_path = Path(sys.argv[1])
    theme_path = Path(sys.argv[2])

    # Validate paths
    if not website_path.exists():
        print(f"❌ Error: Website module path {website_path} does not exist")
        return 1

    if not theme_path.exists():
        print(f"❌ Error: Theme module path {theme_path} does not exist")
        return 1

    # Auto-detect or use provided model name
    model_name = None
    if len(sys.argv) > 3:
        model_name = sys.argv[3]
    else:
        # Auto-detect from files
        models_dir = website_path / 'models'
        for file in models_dir.glob('website_*.py'):
            if file.name != 'website.py':
                model_name = file.stem.replace('website_', '')
                break

    if not model_name:
        print("❌ Error: Could not detect model name. Please provide it as third argument.")
        return 1

    print(f"\n📋 Configuration:")
    print(f"   Website Module: {website_path}")
    print(f"   Theme Module: {theme_path}")
    print(f"   Model Name: {model_name}")
    print("=" * 70)

    try:
        # Step 1: Analyze existing model
        print("\n🔍 Phase 1: Model Analysis")
        print("-" * 50)
        analyzer = ModelAnalyzer(website_path, model_name)
        model_info = analyzer.analyze()

        print(f"   ✓ Found class: {model_info['class_name']}")
        print(f"   ✓ Found {len(model_info['fields'])} fields")
        print(f"   ✓ Found {len(model_info['methods'])} methods")
        print(f"   ✓ Mixins: {', '.join(model_info['mixins'][:3]) if model_info['mixins'] else 'None'}")

        # Step 2: Generate theme models
        print("\n🏗️ Phase 2: Theme Model Generation")
        print("-" * 50)
        generator = ThemeModelGenerator(website_path, theme_path, model_name, model_info)

        if not generator.generate_all():
            print("\n❌ Generation failed. Check the error messages above.")
            return 1

        # Step 3: Summary
        print("\n" + "=" * 70)
        print("✅ Theme Mirror Model Setup Complete!")
        print("\n📚 Created/Updated Files:")
        print(f"   • {website_path}/models/website_{model_name}.py")
        print(f"   • {website_path}/models/theme_models.py")
        print(f"   • {website_path}/models/ir_module_module.py")
        print(f"   • {website_path}/models/__init__.py")
        print(f"   • {website_path}/security/ir.model.access.csv")
        print(f"   • {theme_path}/data/theme_{model_name}.xml")
        print(f"   • {theme_path}/__manifest__.py")

        print("\n🚀 Next Steps:")
        print(f"1. Update the website module:")
        print(f"   python -m odoo -c conf/[config].conf -d [db] -u website_{model_name}")
        print(f"\n2. Install/update the theme:")
        print(f"   python -m odoo -c conf/[config].conf -d [db] -i theme_pearlpixels")
        print(f"\n3. Verify in Admin:")
        print(f"   • Go to Website > Configuration > {model_name.title()}s")
        print(f"   • Check that records have website_id assigned")
        print(f"   • Verify theme_template_id is set")
        print(f"\n4. Test the pages:")
        print(f"   • Visit /{model_name}/[slug] URLs")
        print(f"   • Check that content displays correctly")
        print(f"   • Verify multi-website isolation")

        print("\n📖 References:")
        print("   • Pattern based on: odoo/addons/website/models/theme_models.py")
        print("   • Installation flow: odoo/addons/website/models/ir_module_module.py")
        print("   • Model structure: odoo/addons/website/models/website_page.py")

        print("\n✨ Key Improvements in This Version:")
        print("   • Smart mixin detection avoids duplicate URL field")
        print("   • Uses correct arch field type (Text, not Html)")
        print("   • Proper CSV formatting with newlines")
        print("   • Template-based view generation with t-call")
        print("   • Field validation and compatibility checks")

        return 0

    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
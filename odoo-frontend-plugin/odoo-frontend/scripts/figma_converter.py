#!/usr/bin/env python3
"""
Figma to Odoo Converter
Interfaces with Figma MCP to convert designs to Odoo-compatible HTML/SCSS
"""

from typing import Dict, List, Optional
import json


class FigmaConverter:
    """Converts Figma designs to Odoo theme components"""

    # MCP prompts for Figma conversion
    FIGMA_PROMPTS = {
        'basic_html': """Generate this Figma selection as HTML with Bootstrap v{bootstrap_version} classes instead of React and Tailwind. Use Odoo-compatible structure with proper semantic HTML5 elements.""",

        'odoo_component': """Convert this Figma design to HTML for Odoo {odoo_version} website theme with these requirements:
- Use Bootstrap v{bootstrap_version} classes (not Tailwind)
- Apply proper Odoo theme structure with sections and containers
- Include responsive classes (col-sm-*, col-md-*, col-lg-*)
- Use semantic HTML5 elements (header, nav, main, section, article)
- Add data attributes for Odoo website builder compatibility
- Map colors to CSS custom properties for theme variables
- Include accessibility attributes (aria-labels, alt text)""",

        'page_template': """Convert this Figma page layout to complete Odoo theme template with:
- Bootstrap v{bootstrap_version} framework (compatible with Odoo {odoo_version})
- Proper XML template structure for inheritance
- Bootstrap grid system throughout (container, row, col-*)
- Odoo snippet-compatible sections
- CSS custom properties for theme color variables
- Responsive viewport and accessibility best practices""",

        'color_extraction': """Extract the color palette from this Figma design and map to CSS custom properties using the o-color-1 through o-color-5 naming convention for Odoo themes.""",

        'typography_extraction': """Convert this Figma text styling to Bootstrap v{bootstrap_version} typography classes and CSS custom properties. Map font families to Google Fonts configuration for Odoo theme integration.""",

        'layout_extraction': """Convert this Figma layout to Bootstrap v{bootstrap_version} grid system and utility classes. Use proper container, row, col-* structure with responsive breakpoints. Map Figma spacing to Bootstrap spacing scale (0-5).""",
    }

    def __init__(self, odoo_version: str = '17.0', bootstrap_version: str = '5.1.3'):
        self.odoo_version = odoo_version
        self.bootstrap_version = bootstrap_version

    def get_prompt(self, prompt_type: str) -> str:
        """Get MCP prompt for Figma conversion"""
        if prompt_type not in self.FIGMA_PROMPTS:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        return self.FIGMA_PROMPTS[prompt_type].format(
            odoo_version=self.odoo_version,
            bootstrap_version=self.bootstrap_version
        )

    def convert_colors_to_scss(self, figma_colors: Dict[str, str]) -> str:
        """Convert Figma color palette to Odoo SCSS variables"""
        scss = "// Odoo Theme Color Variables (extracted from Figma)\n\n"

        # Map to o-color-1 through o-color-5
        color_vars = []
        for i, (name, value) in enumerate(figma_colors.items(), start=1):
            if i <= 5:
                color_vars.append(f"$o-color-{i}: {value}; // {name}")

        scss += '\n'.join(color_vars)
        scss += "\n\n// Color palette configuration\n"
        scss += "$o-website-values-palettes: (\n    (\n"
        scss += "        'color-palettes-name': 'figma-palette',\n"

        for i in range(1, len(color_vars) + 1):
            scss += f"        'color-{i}': $o-color-{i},\n"

        scss += "    )\n);\n"

        return scss

    def convert_typography_to_scss(self, figma_fonts: Dict[str, Dict]) -> str:
        """Convert Figma typography to Odoo SCSS configuration"""
        scss = "// Typography Configuration (extracted from Figma)\n\n"

        font_config = {
            'font': figma_fonts.get('body', {}).get('family', 'Inter'),
            'headings-font': figma_fonts.get('heading', {}).get('family', 'Inter'),
            'navbar-font': figma_fonts.get('nav', {}).get('family', 'Inter'),
            'buttons-font': figma_fonts.get('button', {}).get('family', 'Inter'),
        }

        scss += "$o-theme-font-configs: (\n"
        for key, value in font_config.items():
            scss += f"    '{key}': '{value}',\n"
        scss += ");\n\n"

        # Font size configuration
        if 'sizes' in figma_fonts:
            scss += "// Font sizes\n"
            for name, size in figma_fonts['sizes'].items():
                scss += f"$font-size-{name}: {size};\n"

        return scss

    def generate_snippet_xml(self, html_content: str, snippet_id: str, snippet_name: str,
                              odoo_version_num: int = 17) -> str:
        """Generate Odoo snippet XML from HTML content"""

        # Template definition
        xml = f"""<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Snippet Template -->
    <template id="{snippet_id}" name="{snippet_name}">
        {html_content}
    </template>

"""

        # Snippet registration (version-specific)
        if odoo_version_num >= 18:
            # Odoo 18/19 with snippet groups
            xml += f"""    <!-- Snippet Registration (Odoo 18/19) -->
    <template id="{snippet_id}_insert" inherit_id="website.snippets">
        <xpath expr="//div[@id='snippet_structure']/*[1]" position="before">
            <t t-snippet="{snippet_id}"
               string="{snippet_name}"
               group="custom"
               t-thumbnail="/theme_name/static/img/snippets/{snippet_id}.svg"/>
        </xpath>
    </template>
"""
        else:
            # Odoo 17 and earlier
            xml += f"""    <!-- Snippet Registration (Odoo 17) -->
    <template id="{snippet_id}_insert" inherit_id="website.snippets">
        <xpath expr="//div[@id='snippet_effect']//t[@t-snippet][last()]" position="after">
            <t t-snippet="{snippet_id}"
               string="{snippet_name}"
               t-thumbnail="/theme_name/static/img/snippets/{snippet_id}.svg"/>
        </xpath>
    </template>
"""

        xml += "</odoo>\n"
        return xml

    def generate_snippet_options(self, snippet_id: str, options: List[Dict]) -> str:
        """Generate snippet options XML"""
        xml = f"""<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="{snippet_id}_options" inherit_id="website.snippet_options">
        <xpath expr="." position="inside">
            <div data-selector=".{snippet_id}">
"""

        for option in options:
            option_type = option.get('type', 'select')

            if option_type == 'select':
                xml += f"""                <we-select string="{option['label']}">
"""
                for choice in option.get('choices', []):
                    xml += f"""                    <we-button data-select-class="{choice.get('class', '')}">{choice.get('label', '')}</we-button>
"""
                xml += """                </we-select>
"""

            elif option_type == 'colorpicker':
                xml += f"""                <we-colorpicker string="{option['label']}" data-css-property="background-color"/>
"""

            elif option_type == 'add_item':
                xml += f"""                <we-row string="{option['label']}">
                    <we-button data-add-item="true" data-no-preview="true" class="o_we_bg_brand_primary">Add Item</we-button>
                </we-row>
"""

        xml += """            </div>
        </xpath>
    </template>
</odoo>
"""
        return xml

    def extract_figma_data(self, figma_response: Dict) -> Dict:
        """Extract structured data from Figma MCP response"""
        # This would be implemented based on actual Figma MCP response structure
        return {
            'html': figma_response.get('html', ''),
            'colors': figma_response.get('colors', {}),
            'fonts': figma_response.get('typography', {}),
            'spacing': figma_response.get('spacing', {}),
            'components': figma_response.get('components', []),
        }


def convert_figma_to_odoo(figma_url: str, output_dir: str, odoo_version: str = '17.0'):
    """
    Main conversion function - interfaces with Figma MCP

    This function would be called by Claude Code with MCP access to:
    1. Fetch Figma design via MCP
    2. Convert to HTML/CSS using appropriate prompts
    3. Generate Odoo-compatible files

    Args:
        figma_url: Figma file or frame URL
        output_dir: Where to save generated files
        odoo_version: Target Odoo version
    """
    converter = FigmaConverter(odoo_version=odoo_version)

    print(f"Converting Figma design from: {figma_url}")
    print(f"Target Odoo version: {odoo_version}")
    print(f"Output directory: {output_dir}")

    # Instructions for Claude Code to execute with MCP
    instructions = f"""
To convert this Figma design:

1. Use Figma MCP with this prompt:
   {converter.get_prompt('odoo_component')}

2. Extract colors using:
   {converter.get_prompt('color_extraction')}

3. Extract typography using:
   {converter.get_prompt('typography_extraction')}

4. Save generated files to: {output_dir}
   - HTML content → snippet template XML
   - Colors → primary_variables.scss
   - Typography → primary_variables.scss
   - Generate snippet options if needed
"""

    print(instructions)
    return instructions


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        figma_url = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else './output'
        odoo_version = sys.argv[3] if len(sys.argv) > 3 else '17.0'

        convert_figma_to_odoo(figma_url, output_dir, odoo_version)
    else:
        print("Usage: python figma_converter.py <figma_url> [output_dir] [odoo_version]")
        print("\nAvailable prompts:")
        converter = FigmaConverter()
        for prompt_name in converter.FIGMA_PROMPTS.keys():
            print(f"  - {prompt_name}")

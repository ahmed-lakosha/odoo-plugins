#!/usr/bin/env python3
"""
Chrome DevTools Style Extractor
Interfaces with Chrome DevTools MCP to extract styles from live websites
"""

from typing import Dict, List, Optional
import re


class DevToolsExtractor:
    """Extracts and converts styles from Chrome DevTools to Odoo SCSS"""

    def __init__(self, bootstrap_version: str = '5.1.3'):
        self.bootstrap_version = bootstrap_version

    def extract_computed_styles(self, element_styles: Dict) -> Dict[str, str]:
        """Extract relevant computed styles from DevTools"""
        # Common CSS properties that should be extracted
        relevant_properties = [
            'color', 'background-color', 'background', 'background-image',
            'font-family', 'font-size', 'font-weight', 'line-height', 'letter-spacing',
            'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
            'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
            'border', 'border-radius', 'box-shadow',
            'width', 'height', 'max-width', 'min-height',
            'display', 'flex-direction', 'justify-content', 'align-items',
            'position', 'top', 'right', 'bottom', 'left',
            'z-index', 'opacity', 'transform', 'transition',
        ]

        extracted = {}
        for prop in relevant_properties:
            if prop in element_styles:
                extracted[prop] = element_styles[prop]

        return extracted

    def convert_to_scss(self, element_styles: Dict[str, str], class_name: str) -> str:
        """Convert extracted styles to SCSS"""
        scss = f".{class_name} {{\n"

        for prop, value in element_styles.items():
            scss += f"    {prop}: {value};\n"

        scss += "}\n"
        return scss

    def map_to_bootstrap_utilities(self, styles: Dict[str, str]) -> List[str]:
        """Map CSS styles to Bootstrap utility classes"""
        bootstrap_classes = []

        # Spacing mapping
        spacing_map = {
            '0': '0', '0.25rem': '1', '0.5rem': '2',
            '1rem': '3', '1.5rem': '4', '3rem': '5'
        }

        # Map margins
        for direction, suffix in [('top', 't'), ('right', 'e'), ('bottom', 'b'), ('left', 's')]:
            margin_key = f'margin-{direction}'
            if margin_key in styles:
                value = styles[margin_key]
                if value in spacing_map:
                    bootstrap_classes.append(f"m{suffix}-{spacing_map[value]}")

        # Map paddings
        for direction, suffix in [('top', 't'), ('right', 'e'), ('bottom', 'b'), ('left', 's')]:
            padding_key = f'padding-{direction}'
            if padding_key in styles:
                value = styles[padding_key]
                if value in spacing_map:
                    bootstrap_classes.append(f"p{suffix}-{spacing_map[value]}")

        # Map display
        if 'display' in styles:
            display = styles['display']
            if display in ['block', 'inline', 'inline-block', 'flex', 'grid', 'none']:
                bootstrap_classes.append(f"d-{display}")

        # Map text alignment
        if 'text-align' in styles:
            align = styles['text-align']
            if align in ['start', 'center', 'end']:
                bootstrap_classes.append(f"text-{align}")
            elif align == 'left':
                bootstrap_classes.append('text-start')
            elif align == 'right':
                bootstrap_classes.append('text-end')

        # Map flex properties
        if styles.get('display') == 'flex':
            if 'justify-content' in styles:
                justify = styles['justify-content']
                if justify in ['start', 'end', 'center', 'between', 'around', 'evenly']:
                    bootstrap_classes.append(f"justify-content-{justify}")

            if 'align-items' in styles:
                align = styles['align-items']
                if align in ['start', 'end', 'center', 'baseline', 'stretch']:
                    bootstrap_classes.append(f"align-items-{align}")

        # Map colors to Odoo theme variables
        if 'color' in styles:
            bootstrap_classes.append('/* color: var(--o-color-text) */')

        if 'background-color' in styles:
            bootstrap_classes.append('/* background-color: var(--o-color-bg) */')

        return bootstrap_classes

    def convert_dom_to_qweb(self, html: str, add_odoo_attributes: bool = True) -> str:
        """Convert HTML DOM to Odoo QWeb template"""
        # Add QWeb structure
        qweb = f"""<template id="snippet_extracted" name="Extracted Snippet">
    <section class="s_extracted_snippet">
        <div class="container">
            {html}
        </div>
    </section>
</template>
"""

        if add_odoo_attributes:
            # Add data attributes for Odoo editor
            qweb = qweb.replace('<section', '<section data-name="Extracted Section"')

        return qweb

    def generate_scss_from_styles(self, styles_dict: Dict[str, Dict[str, str]]) -> str:
        """Generate complete SCSS file from multiple element styles"""
        scss = "// Extracted Styles from DevTools\n"
        scss += "// Generated for Odoo Website Theme\n\n"

        # Add import statements
        scss += "@import 'odoo/addons/web/static/src/scss/bootstrap_overridden';\n\n"

        # Convert each element's styles
        for selector, styles in styles_dict.items():
            scss += self.convert_to_scss(styles, selector)
            scss += "\n"

        # Add Bootstrap utility class suggestions
        scss += "// Bootstrap Utility Class Suggestions:\n"
        for selector, styles in styles_dict.items():
            bootstrap_classes = self.map_to_bootstrap_utilities(styles)
            if bootstrap_classes:
                scss += f"// .{selector} could use: {' '.join(bootstrap_classes)}\n"

        return scss

    def extract_layout_grid(self, dom_structure: List[Dict]) -> str:
        """Analyze DOM structure and convert to Bootstrap grid"""
        grid_html = "<div class=\"container\">\n"
        grid_html += "    <div class=\"row\">\n"

        # Analyze structure for columns
        for element in dom_structure:
            width = element.get('width', 'auto')

            # Estimate column size
            col_size = 12  # Default full width
            if 'flex' in element.get('display', ''):
                # If flex container, children become columns
                children_count = len(element.get('children', []))
                if children_count > 0:
                    col_size = 12 // children_count

            grid_html += f"        <div class=\"col-lg-{col_size}\">\n"
            grid_html += f"            <!-- Content from {element.get('selector', 'element')} -->\n"
            grid_html += "        </div>\n"

        grid_html += "    </div>\n"
        grid_html += "</div>\n"

        return grid_html

    def generate_instructions_for_mcp(self, url: str) -> str:
        """Generate instructions for using Chrome DevTools MCP"""
        instructions = f"""
Instructions for extracting styles from {url} using Chrome DevTools MCP:

1. Open the page in Chrome DevTools MCP
2. Select the element(s) you want to extract
3. Get computed styles for each element
4. Copy the DOM structure

Then use this tool to:
- Convert styles to SCSS
- Map to Bootstrap utility classes
- Generate QWeb template structure
- Create Odoo-compatible theme code

Example DevTools extraction:
{{
    "selector": ".hero-section",
    "styles": {{
        "background-color": "#f8f9fa",
        "padding-top": "5rem",
        "padding-bottom": "5rem"
    }},
    "html": "<div class='hero-section'><h1>Title</h1><p>Content</p></div>"
}}

This will be converted to:
- SCSS with Odoo variables
- Bootstrap utility classes (bg-light, pt-5, pb-5)
- QWeb template with proper structure
"""
        return instructions


def extract_from_devtools(url: str, output_dir: str):
    """
    Main extraction function - interfaces with Chrome DevTools MCP

    This function would be called by Claude Code with MCP access to:
    1. Connect to Chrome DevTools via MCP
    2. Extract computed styles and DOM
    3. Convert to Odoo-compatible SCSS and templates

    Args:
        url: URL of the website to extract from
        output_dir: Where to save generated files
    """
    extractor = DevToolsExtractor()

    print(f"Extracting styles from: {url}")
    print(f"Output directory: {output_dir}")

    instructions = extractor.generate_instructions_for_mcp(url)
    print(instructions)

    return instructions


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        url = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else './output'

        extract_from_devtools(url, output_dir)
    else:
        print("Usage: python devtools_extractor.py <url> [output_dir]")
        print("\nThis tool extracts styles from live websites using Chrome DevTools MCP")
        print("and converts them to Odoo-compatible SCSS and QWeb templates")

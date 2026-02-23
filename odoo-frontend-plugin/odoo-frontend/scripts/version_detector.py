#!/usr/bin/env python3
"""
Odoo Version Detection Utility
Automatically detects Odoo version from manifest files and maps to correct Bootstrap version
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, Optional, Tuple


class OdooVersionDetector:
    """Detects Odoo version from module manifests and provides version-specific information"""

    # Bootstrap version mapping
    BOOTSTRAP_VERSION_MAP = {
        '14.0': '4.5.0',
        '15.0': '5.0.2',
        '16.0': '5.1.3',
        '17.0': '5.1.3',
        '18.0': '5.1.3',
        '19.0': '5.1.3',
    }

    # Owl version mapping
    OWL_VERSION_MAP = {
        '14.0': None,  # Experimental
        '15.0': None,  # Experimental
        '16.0': '1.x',
        '17.0': '1.x',
        '18.0': '2.x',
        '19.0': '2.x',
    }

    def __init__(self, module_path: str):
        self.module_path = Path(module_path)
        self.version_info = self._detect_version()

    def _detect_version(self) -> Dict[str, any]:
        """Detect Odoo version from manifest file"""
        manifest_file = self._find_manifest()

        if not manifest_file:
            return self._detect_from_parent()

        version = self._parse_manifest_version(manifest_file)

        return {
            'odoo_version': version,
            'bootstrap_version': self.BOOTSTRAP_VERSION_MAP.get(version, '5.1.3'),
            'owl_version': self.OWL_VERSION_MAP.get(version),
            'manifest_file': str(manifest_file),
            'module_type': self._detect_module_type(manifest_file),
        }

    def _find_manifest(self) -> Optional[Path]:
        """Find __manifest__.py or __openerp__.py in module directory"""
        manifest_files = ['__manifest__.py', '__openerp__.py']

        for manifest_name in manifest_files:
            manifest_path = self.module_path / manifest_name
            if manifest_path.exists():
                return manifest_path

        return None

    def _parse_manifest_version(self, manifest_file: Path) -> str:
        """Parse version from manifest file"""
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try to parse as Python dict
            manifest_dict = ast.literal_eval(content)

            if 'version' in manifest_dict:
                version_str = manifest_dict['version']
                # Extract major.minor (e.g., "17.0.1.0.0" -> "17.0")
                match = re.match(r'(\d+\.\d+)', version_str)
                if match:
                    return match.group(1)

            # Fallback: search for version pattern in file
            version_match = re.search(r"['\"]version['\"]:\s*['\"](\d+\.\d+)", content)
            if version_match:
                return version_match.group(1)

        except Exception as e:
            print(f"Error parsing manifest: {e}")

        return '17.0'  # Default to latest

    def _detect_from_parent(self) -> Dict[str, any]:
        """Detect version from parent directory structure (e.g., odoo17/)"""
        current_path = self.module_path

        for parent in current_path.parents:
            match = re.match(r'odoo(\d+)', parent.name)
            if match:
                version_num = match.group(1)
                version = f"{version_num}.0"
                return {
                    'odoo_version': version,
                    'bootstrap_version': self.BOOTSTRAP_VERSION_MAP.get(version, '5.1.3'),
                    'owl_version': self.OWL_VERSION_MAP.get(version),
                    'manifest_file': None,
                    'module_type': 'unknown',
                }

        # Default fallback
        return {
            'odoo_version': '17.0',
            'bootstrap_version': '5.1.3',
            'owl_version': '1.x',
            'manifest_file': None,
            'module_type': 'unknown',
        }

    def _detect_module_type(self, manifest_file: Path) -> str:
        """Detect if module is a theme, website module, or custom module"""
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                content = f.read()

            manifest_dict = ast.literal_eval(content)

            # Check category
            category = manifest_dict.get('category', '').lower()
            if 'theme' in category:
                return 'theme'
            elif 'website' in category:
                return 'website'

            # Check name
            name = manifest_dict.get('name', '').lower()
            if name.startswith('theme_'):
                return 'theme'
            elif 'website' in name:
                return 'website'

            # Check dependencies
            depends = manifest_dict.get('depends', [])
            if 'website' in depends:
                return 'website'

            return 'custom'

        except Exception:
            return 'unknown'

    def get_version_info(self) -> Dict[str, any]:
        """Get complete version information"""
        return self.version_info

    def get_odoo_version(self) -> str:
        """Get Odoo version (e.g., '17.0')"""
        return self.version_info['odoo_version']

    def get_bootstrap_version(self) -> str:
        """Get Bootstrap version (e.g., '5.1.3')"""
        return self.version_info['bootstrap_version']

    def get_owl_version(self) -> Optional[str]:
        """Get Owl version (e.g., '2.x' or None)"""
        return self.version_info['owl_version']

    def is_theme_module(self) -> bool:
        """Check if module is a theme"""
        return self.version_info['module_type'] == 'theme'

    def is_website_module(self) -> bool:
        """Check if module is a website module"""
        return self.version_info['module_type'] in ['theme', 'website']

    def supports_snippet_groups(self) -> bool:
        """Check if Odoo version supports snippet groups (18+)"""
        version = float(self.get_odoo_version().split('.')[0])
        return version >= 18

    def uses_owl_v2(self) -> bool:
        """Check if Odoo version uses Owl v2 (18+)"""
        return self.get_owl_version() == '2.x'


def detect_version(module_path: str) -> Dict[str, any]:
    """Convenience function to detect version"""
    detector = OdooVersionDetector(module_path)
    return detector.get_version_info()


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python version_detector.py <module_path>")
        sys.exit(1)

    path = sys.argv[1]
    detector = OdooVersionDetector(path)
    info = detector.get_version_info()

    print(f"Odoo Version: {info['odoo_version']}")
    print(f"Bootstrap Version: {info['bootstrap_version']}")
    print(f"Owl Version: {info['owl_version'] or 'Not available'}")
    print(f"Module Type: {info['module_type']}")
    print(f"Manifest File: {info['manifest_file'] or 'Not found'}")
    print(f"Supports Snippet Groups: {detector.supports_snippet_groups()}")
    print(f"Uses Owl v2: {detector.uses_owl_v2()}")

#!/usr/bin/env python3
"""
Bootstrap Version Mapper
Maps Bootstrap 4 classes to Bootstrap 5 and provides version-specific references
"""

from typing import Dict, List, Tuple


class BootstrapMapper:
    """Maps Bootstrap classes between versions and provides references"""

    # Bootstrap 4 → Bootstrap 5 class mappings
    CLASS_MAPPINGS = {
        # Utility classes
        'ml-': 'ms-',  # margin-left → margin-start
        'mr-': 'me-',  # margin-right → margin-end
        'pl-': 'ps-',  # padding-left → padding-start
        'pr-': 'pe-',  # padding-right → padding-end
        'left-': 'start-',
        'right-': 'end-',

        # Form classes
        'form-group': 'mb-3',
        'form-row': 'row',
        'input-group-append': 'input-group-text',
        'input-group-prepend': 'input-group-text',
        'custom-select': 'form-select',
        'custom-file': 'form-control',
        'custom-range': 'form-range',
        'custom-control': 'form-check',
        'custom-control-input': 'form-check-input',
        'custom-control-label': 'form-check-label',
        'custom-checkbox': 'form-check',
        'custom-radio': 'form-check',
        'custom-switch': 'form-switch',

        # Components
        'media': 'd-flex',
        'close': 'btn-close',
        'text-left': 'text-start',
        'text-right': 'text-end',
        'float-left': 'float-start',
        'float-right': 'float-end',
        'border-left': 'border-start',
        'border-right': 'border-end',
        'rounded-left': 'rounded-start',
        'rounded-right': 'rounded-end',

        # Grid classes
        'no-gutters': 'g-0',

        # Badge classes
        'badge-primary': 'bg-primary',
        'badge-secondary': 'bg-secondary',
        'badge-success': 'bg-success',
        'badge-danger': 'bg-danger',
        'badge-warning': 'bg-warning text-dark',
        'badge-info': 'bg-info',
        'badge-light': 'bg-light text-dark',
        'badge-dark': 'bg-dark',

        # Typography
        'font-weight-bold': 'fw-bold',
        'font-weight-bolder': 'fw-bolder',
        'font-weight-normal': 'fw-normal',
        'font-weight-light': 'fw-light',
        'font-weight-lighter': 'fw-lighter',
        'font-italic': 'fst-italic',

        # Display
        'sr-only': 'visually-hidden',
        'sr-only-focusable': 'visually-hidden-focusable',
    }

    # Deprecated/removed classes in Bootstrap 5
    REMOVED_CLASSES = [
        'form-inline',
        'input-group-append',
        'input-group-prepend',
        'jumbotron',
        'media',
        'badge-pill',  # Use rounded-pill instead
    ]

    # Bootstrap 5.1.3 utility classes (Odoo 16-19)
    BOOTSTRAP_5_UTILITIES = {
        'spacing': ['m-', 'mt-', 'mb-', 'ms-', 'me-', 'mx-', 'my-', 'p-', 'pt-', 'pb-', 'ps-', 'pe-', 'px-', 'py-'],
        'sizing': ['w-', 'h-', 'mw-', 'mh-', 'vw-', 'vh-'],
        'display': ['d-', 'd-none', 'd-inline', 'd-inline-block', 'd-block', 'd-flex', 'd-grid'],
        'flex': ['flex-', 'flex-row', 'flex-column', 'flex-wrap', 'flex-nowrap', 'justify-content-', 'align-items-', 'align-self-'],
        'text': ['text-', 'text-start', 'text-end', 'text-center', 'text-wrap', 'text-nowrap', 'text-break', 'text-truncate'],
        'colors': ['text-primary', 'text-secondary', 'text-success', 'text-danger', 'text-warning', 'text-info', 'text-light', 'text-dark', 'text-muted', 'text-white'],
        'background': ['bg-primary', 'bg-secondary', 'bg-success', 'bg-danger', 'bg-warning', 'bg-info', 'bg-light', 'bg-dark', 'bg-white', 'bg-transparent'],
        'borders': ['border', 'border-', 'border-top', 'border-end', 'border-bottom', 'border-start', 'border-0', 'rounded', 'rounded-'],
        'position': ['position-static', 'position-relative', 'position-absolute', 'position-fixed', 'position-sticky', 'top-', 'bottom-', 'start-', 'end-'],
        'shadows': ['shadow', 'shadow-sm', 'shadow-lg', 'shadow-none'],
        'visibility': ['visible', 'invisible', 'visually-hidden'],
    }

    # Bootstrap 4 utility classes (Odoo 14-15)
    BOOTSTRAP_4_UTILITIES = {
        'spacing': ['m-', 'mt-', 'mb-', 'ml-', 'mr-', 'mx-', 'my-', 'p-', 'pt-', 'pb-', 'pl-', 'pr-', 'px-', 'py-'],
        'text': ['text-', 'text-left', 'text-right', 'text-center'],
        'float': ['float-left', 'float-right', 'float-none'],
    }

    def __init__(self, source_version: str = '4', target_version: str = '5'):
        self.source_version = source_version
        self.target_version = target_version

    def convert_class(self, class_name: str) -> str:
        """Convert a single Bootstrap class from v4 to v5"""
        if self.source_version == '4' and self.target_version == '5':
            # Check for exact matches first
            if class_name in self.CLASS_MAPPINGS:
                return self.CLASS_MAPPINGS[class_name]

            # Check for prefix matches (e.g., ml-3 → ms-3)
            for old_prefix, new_prefix in self.CLASS_MAPPINGS.items():
                if class_name.startswith(old_prefix):
                    return class_name.replace(old_prefix, new_prefix, 1)

            # Check if class is removed
            if class_name in self.REMOVED_CLASSES:
                return f"/* REMOVED: {class_name} - find alternative */"

        return class_name

    def convert_classes(self, classes: str) -> str:
        """Convert a space-separated string of classes"""
        class_list = classes.split()
        converted = [self.convert_class(cls) for cls in class_list]
        return ' '.join(converted)

    def get_spacing_scale(self, version: str = '5') -> Dict[str, str]:
        """Get spacing scale for Bootstrap version"""
        if version == '5':
            return {
                '0': '0',
                '1': '0.25rem',
                '2': '0.5rem',
                '3': '1rem',
                '4': '1.5rem',
                '5': '3rem',
            }
        else:  # Bootstrap 4
            return {
                '0': '0',
                '1': '0.25rem',
                '2': '0.5rem',
                '3': '1rem',
                '4': '1.5rem',
                '5': '3rem',
            }

    def get_color_utilities(self, version: str = '5') -> List[str]:
        """Get available color utility classes"""
        return self.BOOTSTRAP_5_UTILITIES['colors'] if version == '5' else []

    def validate_class(self, class_name: str, version: str = '5') -> Tuple[bool, str]:
        """Validate if a class exists in the specified Bootstrap version"""
        utilities = self.BOOTSTRAP_5_UTILITIES if version == '5' else self.BOOTSTRAP_4_UTILITIES

        # Check if it's a standard utility
        for category, prefixes in utilities.items():
            for prefix in prefixes:
                if class_name.startswith(prefix) or class_name == prefix:
                    return True, f"Valid {category} utility"

        # Check if it's a component class (common ones)
        common_components = [
            'btn', 'btn-primary', 'btn-secondary', 'btn-success', 'btn-danger', 'btn-warning', 'btn-info',
            'alert', 'alert-primary', 'alert-secondary', 'alert-success', 'alert-danger', 'alert-warning', 'alert-info',
            'card', 'card-body', 'card-header', 'card-footer',
            'navbar', 'nav', 'nav-item', 'nav-link',
            'dropdown', 'dropdown-menu', 'dropdown-item',
            'modal', 'modal-dialog', 'modal-content', 'modal-header', 'modal-body', 'modal-footer',
            'form-control', 'form-label', 'form-check', 'form-select',
            'table', 'table-striped', 'table-bordered', 'table-hover',
            'badge', 'accordion', 'carousel', 'collapse', 'offcanvas', 'pagination', 'progress', 'spinner', 'toast'
        ]

        for component in common_components:
            if class_name.startswith(component):
                return True, "Valid component class"

        return False, f"Unknown class (may be custom or Odoo-specific)"

    def get_migration_notes(self) -> List[str]:
        """Get important migration notes from Bootstrap 4 to 5"""
        return [
            "jQuery is no longer required - Bootstrap 5 uses vanilla JavaScript",
            "Replace .ml- and .mr- with .ms- and .me- (start/end instead of left/right)",
            "Replace .pl- and .pr- with .ps- and .pe-",
            ".form-group is removed - use .mb-3 instead for spacing",
            ".form-inline is removed - use grid/flex utilities",
            ".jumbotron is removed - recreate using utilities",
            ".media is removed - use flex utilities",
            "Custom form controls renamed: .custom-select → .form-select",
            ".close button replaced with .btn-close",
            ".text-left/.text-right replaced with .text-start/.text-end",
            ".float-left/.float-right replaced with .float-start/.float-end",
            "Badge colors use background utilities: .badge-primary → .bg-primary",
            ".sr-only replaced with .visually-hidden",
            "Font weight classes renamed: .font-weight-* → .fw-*",
            ".no-gutters replaced with .g-0",
        ]


if __name__ == '__main__':
    import sys

    mapper = BootstrapMapper(source_version='4', target_version='5')

    if len(sys.argv) > 1:
        classes = ' '.join(sys.argv[1:])
        converted = mapper.convert_classes(classes)
        print(f"Original: {classes}")
        print(f"Converted: {converted}")
    else:
        print("Bootstrap 4 → 5 Migration Notes:")
        for note in mapper.get_migration_notes():
            print(f"  • {note}")

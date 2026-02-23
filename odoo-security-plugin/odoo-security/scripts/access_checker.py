#!/usr/bin/env python3
"""
Odoo Model Access Rule Checker
===============================
Scans an Odoo module for all model definitions and cross-references them
against the security/ir.model.access.csv file to find missing or incomplete
access control rules.

Usage:
    python access_checker.py <module_path> [options]

Options:
    --json     Output results as JSON (used by security_auditor.py orchestrator)
    --verbose  Show detailed per-model information

Exit codes:
    0 = No issues found
    1 = Issues found
    2 = Usage error
"""

import sys
import os
import re
import ast
import csv
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple


# Known Odoo abstract base classes that don't need access rules
ABSTRACT_BASES = {
    'models.AbstractModel',
    'models.TransientModel',  # Transient models DO need rules but are tracked separately
    'Model',
    'AbstractModel',
}

# Common model _name patterns that indicate the model is abstract
ABSTRACT_NAME_PATTERNS = [
    r'^base\.',
    r'^mail\.thread',
    r'^mail\.activity',
]

SEVERITY_ORDER = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']


def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in a directory, excluding tests."""
    files = []
    for py_file in directory.rglob('*.py'):
        # Skip test files
        if 'test' in py_file.parts:
            continue
        if py_file.name.startswith('test_'):
            continue
        files.append(py_file)
    return sorted(files)


def extract_models_from_file(file_path: Path) -> List[Dict]:
    """
    Extract all Odoo model definitions from a Python file.

    Returns list of dicts with:
        - name: model technical name (_name value)
        - inherit: inherited model name (_inherit value) if no _name set
        - is_transient: True if TransientModel
        - is_abstract: True if AbstractModel
        - line: line number of the class definition
        - class_name: Python class name
    """
    models = []

    try:
        source = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        # Fall back to regex parsing for malformed files
        return extract_models_regex(source, file_path)

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # Check if class inherits from Odoo model base classes
        base_names = []
        for base in node.bases:
            if isinstance(base, ast.Attribute):
                base_names.append(f"{base.value.id if isinstance(base.value, ast.Name) else '?'}.{base.attr}")
            elif isinstance(base, ast.Name):
                base_names.append(base.name)

        is_odoo_model = any(
            'Model' in b or 'model' in b.lower()
            for b in base_names
        )
        if not is_odoo_model and not any('models.' in b for b in base_names):
            continue

        is_transient = any('Transient' in b for b in base_names)
        is_abstract = any('Abstract' in b for b in base_names)

        # Extract _name and _inherit
        model_name = None
        inherit = None

        for item in ast.walk(node):
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if target.id == '_name' and isinstance(item.value, ast.Constant):
                            model_name = item.value.value
                        elif target.id == '_inherit':
                            if isinstance(item.value, ast.Constant):
                                inherit = item.value.value
                            elif isinstance(item.value, ast.List):
                                inherit = [
                                    elt.value for elt in item.value.elts
                                    if isinstance(elt, ast.Constant)
                                ]

        # Skip classes that don't define or inherit a model
        if not model_name and not inherit:
            continue

        # Skip abstract models
        if is_abstract:
            continue

        models.append({
            'name': model_name,
            'inherit': inherit,
            'is_transient': is_transient,
            'is_abstract': is_abstract,
            'line': node.lineno,
            'class_name': node.name,
            'file': str(file_path),
        })

    return models


def extract_models_regex(source: str, file_path: Path) -> List[Dict]:
    """
    Fallback regex-based model extraction for files that can't be AST-parsed.
    Less accurate but handles syntax errors.
    """
    models = []

    # Find _name = 'something' assignments
    name_pattern = re.compile(r"_name\s*=\s*['\"]([^'\"]+)['\"]")
    inherit_pattern = re.compile(r"_inherit\s*=\s*['\"]([^'\"]+)['\"]")
    transient_pattern = re.compile(r'class\s+\w+\s*\(.*TransientModel.*\)')
    abstract_pattern = re.compile(r'class\s+\w+\s*\(.*AbstractModel.*\)')

    lines = source.split('\n')
    for i, line in enumerate(lines, 1):
        name_match = name_pattern.search(line)
        if name_match:
            model_name = name_match.group(1)
            # Look back a few lines for the class definition
            is_transient = any(
                transient_pattern.search(lines[max(0, i-10):i])
                for _ in range(1)  # just to use loop
            )
            is_abstract = any(
                abstract_pattern.search(lines[max(0, i-10):i])
                for _ in range(1)
            )
            if not is_abstract:
                models.append({
                    'name': model_name,
                    'inherit': None,
                    'is_transient': bool(is_transient),
                    'is_abstract': False,
                    'line': i,
                    'class_name': 'unknown',
                    'file': str(file_path),
                })

    return models


def model_name_to_csv_id(model_name: str) -> str:
    """
    Convert an Odoo model _name to its ir.model.access.csv model_id:id format.

    Example: 'my.model' -> 'model_my_model'
    """
    return 'model_' + model_name.replace('.', '_')


def parse_access_csv(csv_path: Path) -> Tuple[List[Dict], List[str]]:
    """
    Parse ir.model.access.csv file.

    Returns:
        (rows, errors) where rows is list of parsed access rule dicts
    """
    if not csv_path.exists():
        return [], []

    rows = []
    errors = []

    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            expected_cols = {'id', 'name', 'model_id:id', 'group_id:id',
                             'perm_read', 'perm_write', 'perm_create', 'perm_unlink'}

            if reader.fieldnames:
                missing_cols = expected_cols - set(reader.fieldnames)
                if missing_cols:
                    errors.append(f"Missing CSV columns: {', '.join(sorted(missing_cols))}")

            for line_num, row in enumerate(reader, start=2):  # 2 because row 1 is header
                if not any(row.values()):
                    continue  # Skip empty rows

                # Validate required fields
                model_id = row.get('model_id:id', '').strip()
                if not model_id:
                    errors.append(f"Line {line_num}: Empty model_id:id")
                    continue

                rows.append({
                    'id': row.get('id', '').strip(),
                    'name': row.get('name', '').strip(),
                    'model_id': model_id,
                    'group_id': row.get('group_id:id', '').strip(),
                    'perm_read': row.get('perm_read', '0').strip() == '1',
                    'perm_write': row.get('perm_write', '0').strip() == '1',
                    'perm_create': row.get('perm_create', '0').strip() == '1',
                    'perm_unlink': row.get('perm_unlink', '0').strip() == '1',
                    'line': line_num,
                })
    except Exception as e:
        errors.append(f"Error reading CSV: {e}")

    return rows, errors


def find_defined_groups(module_path: Path) -> set:
    """Scan security XML files to find all defined group XML IDs."""
    group_ids = set()
    security_dir = module_path / 'security'

    if not security_dir.exists():
        return group_ids

    # Also check all XML files in the module
    xml_files = list(module_path.rglob('*.xml'))

    group_pattern = re.compile(r'<record\s[^>]*id=["\']([^"\']+)["\'][^>]*model=["\']res\.groups["\']')
    id_pattern = re.compile(r'<record[^>]+id=["\']([^"\']+)["\']')

    for xml_file in xml_files:
        try:
            content = xml_file.read_text(encoding='utf-8', errors='replace')
            # Find group definitions
            for match in group_pattern.finditer(content):
                group_ids.add(match.group(1))
                module_name = module_path.name
                group_ids.add(f"{module_name}.{match.group(1)}")
        except (OSError, IOError):
            continue

    # Add known Odoo base group IDs
    known_base_groups = {
        'base.group_user', 'base.group_system', 'base.group_erp_manager',
        'base.group_portal', 'base.group_public', 'base.group_no_one',
        'base.group_sanitize_override', 'base.group_private_addresses',
        'base.group_multi_company', 'base.group_multi_currency',
        'account.group_account_user', 'account.group_account_manager',
        'account.group_account_invoice', 'account.group_account_readonly',
        'hr.group_hr_user', 'hr.group_hr_manager',
        'sales_team.group_sale_salesman', 'sales_team.group_sale_salesman_all_leads',
        'sales_team.group_sale_manager',
        'purchase.group_purchase_user', 'purchase.group_purchase_manager',
        'stock.group_stock_user', 'stock.group_stock_manager',
        'mrp.group_mrp_user', 'mrp.group_mrp_manager',
        'project.group_project_user', 'project.group_project_manager',
    }
    group_ids.update(known_base_groups)

    return group_ids


def check_access_rules(module_path: Path) -> List[Dict]:
    """
    Main analysis function. Returns list of security issues.
    """
    issues = []
    module_path = Path(module_path)
    module_name = module_path.name

    # Find models directory
    models_dir = module_path / 'models'
    if not models_dir.exists():
        # Try looking in the root (some modules put models at root)
        models_dir = module_path

    # Find all Python files
    py_files = find_python_files(models_dir)
    if models_dir == module_path:
        # Filter to only keep model-like files when searching root
        py_files = [f for f in py_files if f.name not in {'__manifest__.py', 'setup.py'}]

    # Extract all model definitions
    all_models = []
    for py_file in py_files:
        file_models = extract_models_from_file(py_file)
        all_models.extend(file_models)

    if not all_models:
        issues.append({
            'severity': 'LOW',
            'type': 'no_models_found',
            'file': str(models_dir),
            'line': None,
            'message': 'No model definitions found in models/ directory.',
        })
        return issues

    # Find ir.model.access.csv
    csv_candidates = [
        module_path / 'security' / 'ir.model.access.csv',
        module_path / 'ir.model.access.csv',
    ]
    csv_path = next((p for p in csv_candidates if p.exists()), None)

    # Parse existing access rules
    access_rows = []
    csv_errors = []
    if csv_path:
        access_rows, csv_errors = parse_access_csv(csv_path)
    else:
        issues.append({
            'severity': 'CRITICAL',
            'type': 'missing_access_csv',
            'file': str(module_path / 'security'),
            'line': None,
            'message': (
                f"No ir.model.access.csv found. "
                f"All {len([m for m in all_models if m.get('name')])} models are unprotected."
            ),
        })

    # Build set of models that have access rules
    # model_id format in CSV is either 'model_my_model' or 'module.model_my_model'
    covered_model_ids = set()
    for row in access_rows:
        model_id = row['model_id']
        # Strip module prefix if present
        if '.' in model_id:
            covered_model_ids.add(model_id.split('.')[-1])
        covered_model_ids.add(model_id)

    # Report CSV parsing errors
    for error in csv_errors:
        issues.append({
            'severity': 'MEDIUM',
            'type': 'csv_parse_error',
            'file': str(csv_path) if csv_path else str(module_path / 'security'),
            'line': None,
            'message': f"CSV parse error: {error}",
        })

    # Find defined groups
    defined_groups = find_defined_groups(module_path)

    # Check each model
    new_models = [m for m in all_models if m.get('name') and not m.get('is_abstract')]
    inherited_only = [m for m in all_models if not m.get('name') and m.get('inherit')]

    for model in new_models:
        model_name = model['name']
        expected_csv_id = model_name_to_csv_id(model_name)
        file_rel = Path(model['file']).relative_to(module_path) if module_path in Path(model['file']).parents else model['file']

        # Check if any access rule exists for this model
        has_rule = (
            expected_csv_id in covered_model_ids or
            f"{module_name}.{expected_csv_id}" in covered_model_ids
        )

        if not has_rule:
            severity = 'CRITICAL' if not model['is_transient'] else 'HIGH'
            model_type = 'Transient (wizard)' if model['is_transient'] else 'Model'
            issues.append({
                'severity': severity,
                'type': 'missing_access_rule',
                'file': str(file_rel),
                'line': model['line'],
                'message': (
                    f"{model_type} '{model_name}' (class {model['class_name']}) "
                    f"has no access rules in ir.model.access.csv. "
                    f"Expected CSV entry with model_id:id = '{expected_csv_id}'"
                ),
            })
        else:
            # Model has rules — check if they are complete
            model_rules = [
                r for r in access_rows
                if r['model_id'] == expected_csv_id or
                r['model_id'].endswith('.' + expected_csv_id)
            ]

            # Check for rules with empty group (grants access to ALL users)
            for rule in model_rules:
                if not rule['group_id']:
                    issues.append({
                        'severity': 'HIGH',
                        'type': 'empty_group_access',
                        'file': str(csv_path.relative_to(module_path)) if csv_path else 'security/ir.model.access.csv',
                        'line': rule['line'],
                        'message': (
                            f"Access rule '{rule['id']}' for model '{model_name}' "
                            f"has no group_id — grants access to ALL authenticated users."
                        ),
                    })

            # Check for suspicious permissions on non-transient models
            for rule in model_rules:
                if rule['perm_read'] and rule['perm_write'] and rule['perm_unlink']:
                    group_id = rule.get('group_id', '')
                    # Full CRUD for non-manager groups is suspicious
                    if group_id and 'manager' not in group_id.lower() and 'admin' not in group_id.lower() and 'system' not in group_id.lower():
                        issues.append({
                            'severity': 'MEDIUM',
                            'type': 'overly_permissive_access',
                            'file': str(csv_path.relative_to(module_path)) if csv_path else 'security/ir.model.access.csv',
                            'line': rule['line'],
                            'message': (
                                f"Access rule '{rule['id']}' grants full CRUD including DELETE "
                                f"to group '{group_id}' which appears to be a non-manager group. "
                                f"Consider restricting perm_unlink to manager groups."
                            ),
                        })

            # Validate group references exist
            for rule in model_rules:
                group_id = rule.get('group_id', '').strip()
                if group_id and group_id not in defined_groups:
                    # Group might be from an external module — warn but don't error
                    if '.' in group_id:
                        issues.append({
                            'severity': 'LOW',
                            'type': 'unknown_group_reference',
                            'file': str(csv_path.relative_to(module_path)) if csv_path else 'security/ir.model.access.csv',
                            'line': rule['line'],
                            'message': (
                                f"Access rule '{rule['id']}' references group '{group_id}' "
                                f"which was not found in this module's XML. "
                                f"Ensure the group is defined in a dependency module."
                            ),
                        })

    # Check for models that use _inherit (extension) but add new _name (new model)
    # These are additional models that might be missed
    new_model_names = {m['name'] for m in new_models}

    # Check if ir.model.access.csv references non-existent models (dead rules)
    for rule in access_rows:
        model_id = rule['model_id']
        # Strip module prefix
        bare_model_id = model_id.split('.')[-1] if '.' in model_id else model_id
        # Try to find a matching model
        matching_model_name = bare_model_id.replace('model_', '', 1).replace('_', '.')
        # This is a best-effort check since we'd need the full Odoo model registry
        # to be certain. We skip this for now to avoid false positives.

    # Check if company-aware models are missing multi-company rules
    # Heuristic: check if models have company_id in Python files but no rules XML
    rules_xml_path = module_path / 'security'
    has_rules_xml = any(rules_xml_path.glob('rules_*.xml')) if rules_xml_path.exists() else False

    company_pattern = re.compile(r"company_id\s*=\s*fields\.(Many2one|Integer)\s*\(\s*['\"]res\.company['\"]")
    for py_file in py_files:
        try:
            content = py_file.read_text(encoding='utf-8', errors='replace')
            if company_pattern.search(content):
                if not has_rules_xml:
                    issues.append({
                        'severity': 'HIGH',
                        'type': 'missing_record_rule',
                        'file': str(py_file.relative_to(module_path)),
                        'line': None,
                        'message': (
                            f"File '{py_file.name}' defines a model with company_id field, "
                            f"but no record rules XML file (security/rules_*.xml) was found. "
                            f"Multi-company isolation record rules may be missing."
                        ),
                    })
                    break  # Only report once per module
        except (OSError, IOError):
            continue

    return issues


def format_text_report(issues: List[Dict], module_path: Path) -> str:
    """Format issues as a human-readable text report."""
    lines = []
    module_name = module_path.name

    counts = {s: 0 for s in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']}
    for issue in issues:
        sev = issue.get('severity', 'LOW')
        if sev in counts:
            counts[sev] += 1

    lines.append(f"\n{'='*60}")
    lines.append(f"ACCESS CHECKER REPORT — {module_name}")
    lines.append(f"{'='*60}")
    lines.append(f"Total issues: {len(issues)}")
    for sev, count in counts.items():
        if count:
            lines.append(f"  {sev}: {count}")
    lines.append("")

    for issue in sorted(issues, key=lambda x: -(
        {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}.get(x.get('severity', 'LOW'), 1)
    )):
        severity = issue.get('severity', 'LOW')
        file_info = issue.get('file', '')
        line = issue.get('line', '')
        loc = f"{file_info}:{line}" if line else file_info
        lines.append(f"[{severity}] {loc}")
        lines.append(f"  {issue.get('message', '')}")
        lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Check Odoo module model access rules completeness'
    )
    parser.add_argument('module_path', help='Path to the Odoo module')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()
    module_path = Path(args.module_path).resolve()

    if not module_path.exists():
        print(json.dumps({'error': f'Path not found: {module_path}', 'issues': []}))
        sys.exit(2)

    issues = check_access_rules(module_path)

    counts = {s: 0 for s in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']}
    for issue in issues:
        sev = issue.get('severity', 'LOW')
        if sev in counts:
            counts[sev] += 1

    if args.json:
        output = {
            'auditor': 'access_checker',
            'module': module_path.name,
            'module_path': str(module_path),
            'summary': {'total': len(issues), 'by_severity': counts},
            'issues': issues,
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print(format_text_report(issues, module_path))

    sys.exit(1 if issues else 0)


if __name__ == '__main__':
    main()

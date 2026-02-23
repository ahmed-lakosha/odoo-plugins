#!/usr/bin/env python3
"""
Odoo HTTP Route Security Auditor
==================================
Scans all controllers in an Odoo module for HTTP route security issues:
- Missing or unsafe auth= parameters
- CSRF protection status
- Sensitive data exposure on public routes
- API routes missing authentication
- CORS configuration issues

Usage:
    python route_auditor.py <module_path> [options]

Options:
    --json     Output results as JSON (used by security_auditor.py orchestrator)
    --verbose  Show detailed route information

Exit codes:
    0 = No issues found
    1 = Issues found
    2 = Usage error
"""

import sys
import re
import ast
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple


# Models considered sensitive — accessing them without proper auth is a risk
SENSITIVE_MODELS = {
    'res.partner', 'res.users', 'hr.employee', 'hr.payslip',
    'account.move', 'account.payment', 'sale.order', 'purchase.order',
    'stock.picking', 'stock.move', 'ir.config_parameter',
    'ir.attachment', 'base.automation', 'ir.rule', 'ir.model.access',
    'mail.message', 'mail.thread', 'res.bank', 'res.partner.bank',
}

# Route path patterns that suggest sensitive operations
SENSITIVE_PATH_PATTERNS = [
    r'/admin', r'/settings', r'/config', r'/user', r'/employee',
    r'/payment', r'/invoice', r'/order', r'/report', r'/export',
    r'/download', r'/attachment', r'/file', r'/upload',
    r'/api/v\d', r'/webhook',
]

# Methods that indicate state changes (must have CSRF or API key auth)
STATE_CHANGING_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}

# Indicators of proper API key authentication in function body
API_AUTH_INDICATORS = [
    r'api.?key', r'api_key', r'x.api.key', r'authorization',
    r'_authenticate', r'_validate.*key', r'_check.*token',
    r'hmac', r'signature', r'bearer', r'token',
]


def find_controller_files(module_path: Path) -> List[Path]:
    """Find all Python files in the controllers directory."""
    controllers_dir = module_path / 'controllers'
    if not controllers_dir.exists():
        return []

    files = []
    for py_file in controllers_dir.rglob('*.py'):
        if py_file.name.startswith('test_'):
            continue
        if py_file.name == '__init__.py':
            continue
        files.append(py_file)
    return sorted(files)


def parse_route_decorator(decorator_node: ast.Call) -> Optional[Dict]:
    """
    Parse an @http.route() or @route() decorator AST node.

    Returns dict with route attributes or None if not a route decorator.
    """
    if not isinstance(decorator_node, ast.Call):
        return None

    # Check if it's http.route or route
    func = decorator_node.func
    is_route = False

    if isinstance(func, ast.Attribute) and func.attr == 'route':
        is_route = True
    elif isinstance(func, ast.Name) and func.id == 'route':
        is_route = True

    if not is_route:
        return None

    route_info = {
        'paths': [],
        'methods': [],
        'auth': None,
        'csrf': True,  # Default is True
        'type': 'http',  # Default type
        'cors': None,
        'website': False,
    }

    # Parse positional args (path or list of paths)
    for arg in decorator_node.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            route_info['paths'].append(arg.value)
        elif isinstance(arg, ast.List):
            for elt in arg.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    route_info['paths'].append(elt.value)

    # Parse keyword args
    for kw in decorator_node.keywords:
        key = kw.arg
        value = kw.value

        if key == 'auth':
            if isinstance(value, ast.Constant):
                route_info['auth'] = value.value
        elif key == 'methods':
            if isinstance(value, ast.List):
                route_info['methods'] = [
                    elt.value for elt in value.elts
                    if isinstance(elt, ast.Constant)
                ]
        elif key == 'csrf':
            if isinstance(value, ast.Constant):
                route_info['csrf'] = bool(value.value)
            elif isinstance(value, (ast.NameConstant,)):
                route_info['csrf'] = value.value
        elif key == 'type':
            if isinstance(value, ast.Constant):
                route_info['type'] = value.value
        elif key == 'cors':
            if isinstance(value, ast.Constant):
                route_info['cors'] = value.value
        elif key == 'website':
            if isinstance(value, ast.Constant):
                route_info['website'] = bool(value.value)

    return route_info


def extract_function_body_text(func_node: ast.FunctionDef, source_lines: List[str]) -> str:
    """Extract the text of a function body for pattern searching."""
    if not func_node.body:
        return ''
    start = func_node.body[0].lineno - 1
    end = func_node.end_lineno if hasattr(func_node, 'end_lineno') else start + 50
    return '\n'.join(source_lines[start:end])


def has_api_auth_in_body(body_text: str) -> bool:
    """Check if a function body contains API authentication code."""
    body_lower = body_text.lower()
    return any(re.search(pattern, body_lower) for pattern in API_AUTH_INDICATORS)


def has_sensitive_model_access(body_text: str) -> Tuple[bool, Optional[str]]:
    """
    Check if function body accesses sensitive models.
    Returns (found, model_name).
    """
    for model in SENSITIVE_MODELS:
        if f"'{model}'" in body_text or f'"{model}"' in body_text:
            return True, model
    return False, None


def is_sensitive_path(path: str) -> bool:
    """Check if a route path suggests sensitive operations."""
    return any(re.search(pattern, path, re.IGNORECASE) for pattern in SENSITIVE_PATH_PATTERNS)


def analyze_controller_file(file_path: Path, module_path: Path) -> List[Dict]:
    """
    Analyze a controller file for route security issues.
    Returns list of issue dicts.
    """
    issues = []
    rel_path = file_path.relative_to(module_path) if module_path in file_path.parents else file_path

    try:
        source = file_path.read_text(encoding='utf-8', errors='replace')
        source_lines = source.split('\n')
    except (OSError, IOError) as e:
        return [{
            'severity': 'LOW',
            'type': 'file_read_error',
            'file': str(rel_path),
            'line': None,
            'message': f"Could not read file: {e}",
        }]

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        # Fall back to regex analysis
        return analyze_routes_regex(source, file_path, module_path)

    # Walk through all class and function definitions
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        # Find route decorators
        for decorator in node.decorator_list:
            route_info = parse_route_decorator(decorator)
            if route_info is None:
                continue

            # We found a route — analyze it
            func_name = node.name
            line = node.lineno
            paths = route_info['paths'] or [f'/{func_name}']
            auth = route_info['auth']
            methods = route_info['methods'] or ['GET']
            csrf = route_info['csrf']
            route_type = route_info['type']

            # Get function body for analysis
            body_text = extract_function_body_text(node, source_lines)
            has_sudo = '.sudo()' in body_text

            # Check 1: auth='none' without API authentication
            if auth == 'none':
                has_auth = has_api_auth_in_body(body_text)
                if not has_auth:
                    issues.append({
                        'severity': 'CRITICAL',
                        'type': 'auth_none_route',
                        'file': str(rel_path),
                        'line': line,
                        'message': (
                            f"Route {paths} uses auth='none' but no API key validation, "
                            f"HMAC signature check, or authentication logic detected "
                            f"in method '{func_name}'. This route is completely unauthenticated."
                        ),
                    })
                else:
                    # Has auth code — check if it properly rejects unauthorized requests
                    if not re.search(r'return.*401|make_response.*401|status.*401|Unauthorized|403|Forbidden', body_text):
                        issues.append({
                            'severity': 'HIGH',
                            'type': 'auth_none_incomplete',
                            'file': str(rel_path),
                            'line': line,
                            'message': (
                                f"Route {paths} uses auth='none' with API key check in '{func_name}', "
                                f"but no 401/403 response found for invalid keys. "
                                f"Ensure unauthorized requests are properly rejected."
                            ),
                        })

            # Check 2: auth='public' accessing sensitive models
            if auth == 'public':
                found_sensitive, sensitive_model = has_sensitive_model_access(body_text)
                if found_sensitive and has_sudo:
                    issues.append({
                        'severity': 'HIGH',
                        'type': 'auth_public_sensitive',
                        'file': str(rel_path),
                        'line': line,
                        'message': (
                            f"Route {paths} is auth='public' and accesses sensitive model "
                            f"'{sensitive_model}' with sudo() in method '{func_name}'. "
                            f"This bypasses all access controls for public users. "
                            f"Add domain filters or change auth='user'."
                        ),
                    })
                elif found_sensitive:
                    issues.append({
                        'severity': 'MEDIUM',
                        'type': 'auth_public_model_access',
                        'file': str(rel_path),
                        'line': line,
                        'message': (
                            f"Route {paths} is auth='public' and accesses sensitive model "
                            f"'{sensitive_model}' in method '{func_name}'. "
                            f"Verify that only non-sensitive data is returned."
                        ),
                    })
                elif is_sensitive_path(paths[0] if paths else ''):
                    issues.append({
                        'severity': 'LOW',
                        'type': 'auth_public_sensitive_path',
                        'file': str(rel_path),
                        'line': line,
                        'message': (
                            f"Route {paths} has a sensitive-looking path but uses auth='public'. "
                            f"Verify this is intentional and no sensitive data is exposed."
                        ),
                    })

            # Check 3: Missing auth parameter
            if auth is None:
                issues.append({
                    'severity': 'HIGH',
                    'type': 'missing_auth_param',
                    'file': str(rel_path),
                    'line': line,
                    'message': (
                        f"Route {paths} in method '{func_name}' has no explicit auth= parameter. "
                        f"Odoo defaults to auth='user' but always specify explicitly for clarity."
                    ),
                })

            # Check 4: CSRF disabled on state-changing routes
            state_changing = bool(STATE_CHANGING_METHODS.intersection(set(methods)))
            if state_changing and not csrf and auth not in ('none',):
                issues.append({
                    'severity': 'HIGH' if auth == 'user' else 'MEDIUM',
                    'type': 'csrf_disabled',
                    'file': str(rel_path),
                    'line': line,
                    'message': (
                        f"Route {paths} (methods={methods}) has csrf=False but auth='{auth}'. "
                        f"Disabling CSRF on user-authenticated routes leaves users vulnerable "
                        f"to Cross-Site Request Forgery attacks. "
                        f"Remove csrf=False unless this is a machine-to-machine API with its own auth."
                    ),
                })

            # Check 5: GET routes that also accept POST (state-change via GET)
            if 'GET' in methods and 'POST' in methods:
                issues.append({
                    'severity': 'MEDIUM',
                    'type': 'get_post_mixed',
                    'file': str(rel_path),
                    'line': line,
                    'message': (
                        f"Route {paths} accepts both GET and POST methods. "
                        f"State-changing operations should use POST only. "
                        f"GET requests should be read-only (HTTP semantics)."
                    ),
                })

            # Check 6: API routes without CORS configuration
            if route_type == 'json' and auth == 'none' and not route_info.get('cors'):
                if re.search(r'/api/', paths[0] if paths else ''):
                    issues.append({
                        'severity': 'LOW',
                        'type': 'api_no_cors',
                        'file': str(rel_path),
                        'line': line,
                        'message': (
                            f"API route {paths} has no cors= configuration. "
                            f"Consider setting cors='*' or a specific origin to control "
                            f"cross-origin access explicitly."
                        ),
                    })

            # Check 7: sudo() in public/none authenticated routes
            if auth in ('public', 'none') and has_sudo:
                # Check if sudo is scoped properly (has domain filter after)
                sudo_line_idx = None
                for i, line_text in enumerate(source_lines):
                    if '.sudo()' in line_text and func_name in '\n'.join(source_lines[max(0, i-20):i+1]):
                        sudo_line_idx = i + 1

                issues.append({
                    'severity': 'HIGH' if auth == 'none' else 'MEDIUM',
                    'type': 'sudo_in_public',
                    'file': str(rel_path),
                    'line': sudo_line_idx or line,
                    'message': (
                        f"sudo() found in route method '{func_name}' with auth='{auth}'. "
                        f"This bypasses all model-level access controls. "
                        f"Ensure sudo() results are filtered to only expose appropriate data."
                    ),
                })

    return issues


def analyze_routes_regex(source: str, file_path: Path, module_path: Path) -> List[Dict]:
    """
    Regex-based fallback analysis for files that can't be AST-parsed.
    Less precise but handles syntax errors.
    """
    issues = []
    rel_path = file_path.relative_to(module_path) if module_path in file_path.parents else file_path

    # Find @http.route decorators with auth='none'
    auth_none_pattern = re.compile(r"@(?:http\.)?route\([^)]*auth=['\"]none['\"][^)]*\)")
    for match in auth_none_pattern.finditer(source):
        line = source[:match.start()].count('\n') + 1
        issues.append({
            'severity': 'CRITICAL',
            'type': 'auth_none_route',
            'file': str(rel_path),
            'line': line,
            'message': "Route with auth='none' found (regex analysis — verify API auth is present).",
        })

    # Find routes with csrf=False
    csrf_false_pattern = re.compile(r"@(?:http\.)?route\([^)]*csrf\s*=\s*False[^)]*\)")
    for match in csrf_false_pattern.finditer(source):
        line = source[:match.start()].count('\n') + 1
        issues.append({
            'severity': 'MEDIUM',
            'type': 'csrf_disabled',
            'file': str(rel_path),
            'line': line,
            'message': "Route with csrf=False found (regex analysis — verify this is an API route with auth).",
        })

    return issues


def audit_routes(module_path: Path) -> List[Dict]:
    """
    Main analysis function for route security.
    Returns list of security issues.
    """
    issues = []
    module_path = Path(module_path)

    controller_files = find_controller_files(module_path)

    if not controller_files:
        # No controllers — not an issue, just note it
        return []

    for controller_file in controller_files:
        file_issues = analyze_controller_file(controller_file, module_path)
        issues.extend(file_issues)

    # Check for inherited controllers from common modules
    # Look for website controller patterns in all Python files
    for py_file in module_path.rglob('*.py'):
        if 'controllers' not in str(py_file) and 'wizard' not in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding='utf-8', errors='replace')
            # Check for request.env.cr.execute with string formatting (SQL injection in controllers)
            sqli_pattern = re.compile(
                r"(?:request\.)?env\.cr\.execute\s*\(\s*(?:['\"].*%[^s]|f['\"]|.*%\s*\()",
                re.MULTILINE
            )
            for match in sqli_pattern.finditer(content):
                line = content[:match.start()].count('\n') + 1
                rel_path = py_file.relative_to(module_path) if module_path in py_file.parents else py_file
                issues.append({
                    'severity': 'HIGH',
                    'type': 'sql_injection',
                    'file': str(rel_path),
                    'line': line,
                    'message': (
                        f"Potential SQL injection in controller: env.cr.execute() with "
                        f"string formatting detected. Use parameterized queries: "
                        f"self.env.cr.execute('SELECT ... WHERE x = %s', (value,))"
                    ),
                })
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
    lines.append(f"ROUTE AUDITOR REPORT — {module_name}")
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
        description='Audit Odoo module HTTP routes for security issues'
    )
    parser.add_argument('module_path', help='Path to the Odoo module')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()
    module_path = Path(args.module_path).resolve()

    if not module_path.exists():
        print(json.dumps({'error': f'Path not found: {module_path}', 'issues': []}))
        sys.exit(2)

    issues = audit_routes(module_path)

    counts = {s: 0 for s in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']}
    for issue in issues:
        sev = issue.get('severity', 'LOW')
        if sev in counts:
            counts[sev] += 1

    if args.json:
        output = {
            'auditor': 'route_auditor',
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

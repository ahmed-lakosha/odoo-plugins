#!/usr/bin/env python3
"""
Odoo sudo() Usage Finder and Risk Classifier
=============================================
Scans all Python files in an Odoo module for .sudo() usage and classifies
each occurrence by context and risk level.

Classification:
    CRITICAL - sudo() in public/none auth controller (privilege escalation)
    HIGH     - sudo() in loop (performance + security), or unscoped sudo in portal
    MEDIUM   - sudo() without env scoping or in wizard public methods
    LOW      - sudo() that appears safe (audit logs, config reads, etc.)
    OK       - sudo() in known safe patterns (mail notifications, audit logs)

Usage:
    python sudo_finder.py <module_path> [options]

Options:
    --json     Output results as JSON (used by security_auditor.py orchestrator)
    --verbose  Show code context around each occurrence
    --all      Show ALL sudo() calls including safe ones

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


# Patterns that indicate a sudo() call is in a SAFE context (OK severity)
SAFE_CONTEXT_PATTERNS = [
    # Audit log writing
    r'audit.*log|log.*audit',
    # Mail/notification sending
    r'mail.*send|send.*mail|notify|notification',
    # Config parameter reading (specific, not broad)
    r'ir\.config_parameter.*get_param\([\'"][\w\.]+[\'"]\)',
    r'get_param\([\'"][\w\.]+[\'"]\)',
    # Superuser for specific system operations
    r'env\.ref\(',
    # Creating chatter messages
    r'message_post|message_subscribe',
]

# Patterns that indicate a method is in a PUBLIC or PORTAL context
PUBLIC_CONTEXT_PATTERNS = [
    r"auth=['\"]public['\"]",
    r"auth=['\"]none['\"]",
    r'portal.*controller|CustomerPortal',
    r'website.*controller',
    r'auth_public',
    r'_is_public',
]

# Patterns that suggest sudo() is in a loop
LOOP_INDICATORS = ['for ', 'while ', 'map(', 'filter(', 'list(']

# Models that should NEVER be accessed via sudo() in public contexts
DANGEROUS_SUDO_MODELS = {
    'res.users', 'res.partner', 'hr.employee', 'hr.payslip',
    'account.move', 'account.payment', 'ir.config_parameter',
    'ir.rule', 'ir.model.access', 'base.automation',
    'mail.message', 'res.partner.bank',
}

# Alternative approaches to suggest instead of sudo()
SUDO_ALTERNATIVES = {
    'in_loop': "Use read_group() or a single search() outside the loop, then map results by ID.",
    'in_public': "Use _document_check_access(), verify partner ownership, or add domain filters.",
    'sensitive_model': "Use with_user(specific_user) to scope access instead of full sudo().",
    'unscoped': "Add domain filters immediately after sudo() or use with_user(admin) instead.",
    'portal': "Verify record ownership with partner_id == request.env.user.partner_id.id before sudo().",
}


def find_python_files(module_path: Path) -> List[Path]:
    """Find all Python files in the module, excluding tests."""
    files = []
    for py_file in module_path.rglob('*.py'):
        if 'test' in py_file.parts:
            continue
        if py_file.name.startswith('test_'):
            continue
        files.append(py_file)
    return sorted(files)


def get_context_lines(source_lines: List[str], line_num: int, context: int = 5) -> str:
    """Get surrounding source lines for context display."""
    start = max(0, line_num - context - 1)
    end = min(len(source_lines), line_num + context)
    result = []
    for i, line in enumerate(source_lines[start:end], start=start + 1):
        prefix = '-->' if i == line_num else '   '
        result.append(f"{prefix} {i:4}: {line}")
    return '\n'.join(result)


def classify_sudo_in_loop(source_lines: List[str], sudo_line_num: int) -> bool:
    """
    Check if a sudo() call appears to be inside a loop.
    Looks back up to 20 lines for loop indicators.
    """
    check_start = max(0, sudo_line_num - 20)
    preceding = source_lines[check_start:sudo_line_num - 1]

    # Count indentation of sudo line
    sudo_line = source_lines[sudo_line_num - 1]
    sudo_indent = len(sudo_line) - len(sudo_line.lstrip())

    for line in reversed(preceding):
        stripped = line.strip()
        if not stripped:
            continue

        line_indent = len(line) - len(line.lstrip())

        # If we find a less-indented line, we've left the inner block
        if line_indent < sudo_indent and stripped:
            # Check if this less-indented line is a loop
            if stripped.startswith(('for ', 'while ')):
                return True
            # If it's something else (def, class, if), we've left the loop context
            if stripped.startswith(('def ', 'class ', 'return ', 'with ')):
                break

    # Also check for list comprehensions or generator expressions on same/nearby lines
    sudo_context = '\n'.join(source_lines[max(0, sudo_line_num - 5):sudo_line_num + 2])
    if re.search(r'for\s+\w+\s+in\s+.*\.sudo\(\)', sudo_context):
        return True

    return False


def get_enclosing_function(tree: ast.AST, line_num: int) -> Optional[ast.FunctionDef]:
    """Find the function definition that contains the given line number."""
    best_match = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno <= line_num:
                end = getattr(node, 'end_lineno', node.lineno + 1000)
                if line_num <= end:
                    if best_match is None or node.lineno > best_match.lineno:
                        best_match = node
    return best_match


def get_enclosing_class(tree: ast.AST, line_num: int) -> Optional[ast.ClassDef]:
    """Find the class definition that contains the given line number."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.lineno <= line_num:
                end = getattr(node, 'end_lineno', node.lineno + 10000)
                if line_num <= end:
                    return node
    return None


def is_safe_sudo_context(source: str, line_num: int, source_lines: List[str]) -> Tuple[bool, str]:
    """
    Check if a sudo() call is in a known safe pattern.
    Returns (is_safe, reason).
    """
    context = '\n'.join(source_lines[max(0, line_num - 3):line_num + 2]).lower()

    for pattern in SAFE_CONTEXT_PATTERNS:
        if re.search(pattern, context, re.IGNORECASE):
            return True, f"Safe pattern detected: {pattern}"

    return False, ''


def is_in_public_context(func_node: Optional[ast.FunctionDef], source: str) -> Tuple[bool, str]:
    """
    Check if a function is in a public/portal context.
    Returns (is_public, context_type).
    """
    if func_node is None:
        return False, ''

    # Check function decorators for route decorators
    func_start = func_node.lineno
    func_end = getattr(func_node, 'end_lineno', func_start + 100)

    # Look at the lines before the function for decorators
    source_lines = source.split('\n')
    decorator_region = '\n'.join(source_lines[max(0, func_start - 10):func_start])

    for pattern in PUBLIC_CONTEXT_PATTERNS:
        if re.search(pattern, decorator_region, re.IGNORECASE):
            return True, 'public/portal route'

    # Check function name for portal hints
    if func_node.name:
        if any(keyword in func_node.name.lower() for keyword in ['portal', 'public', 'website', 'shop']):
            return True, 'portal/public method name'

    return False, ''


def find_sudo_calls(source: str, file_path: Path, module_path: Path) -> List[Dict]:
    """
    Find all .sudo() calls in a Python file and classify them.
    Returns list of issue dicts.
    """
    findings = []
    source_lines = source.split('\n')
    rel_path = file_path.relative_to(module_path) if module_path in file_path.parents else file_path

    # Determine file context (controller vs model vs wizard)
    file_context = 'model'
    if 'controllers' in str(file_path):
        file_context = 'controller'
    elif 'wizard' in str(file_path) or 'wizards' in str(file_path):
        file_context = 'wizard'

    # Parse AST for structural analysis
    tree = None
    try:
        tree = ast.parse(source)
    except SyntaxError:
        pass

    # Find all sudo() occurrences using regex (handles all cases)
    sudo_pattern = re.compile(r'\.sudo\(\)')
    matches = list(sudo_pattern.finditer(source))

    for match in matches:
        line_num = source[:match.start()].count('\n') + 1
        line_text = source_lines[line_num - 1].strip()

        # Skip commented lines
        stripped_for_comment = source_lines[line_num - 1].lstrip()
        if stripped_for_comment.startswith('#'):
            continue

        # Skip string literals (common in docstrings)
        if line_text.startswith(('"', "'")):
            continue

        # Get enclosing function and class
        enclosing_func = get_enclosing_function(tree, line_num) if tree else None
        enclosing_class = get_enclosing_class(tree, line_num) if tree else None

        func_name = enclosing_func.name if enclosing_func else 'module-level'
        class_name = enclosing_class.name if enclosing_class else ''

        # Check if in loop
        in_loop = classify_sudo_in_loop(source_lines, line_num)

        # Check if in public context
        is_public, public_reason = is_in_public_context(enclosing_func, source)

        # Check if safe pattern
        is_safe, safe_reason = is_safe_sudo_context(source, line_num, source_lines)

        # Check what model is being accessed
        context_window = '\n'.join(source_lines[max(0, line_num - 5):line_num + 3])
        accessed_model = None
        for model in DANGEROUS_SUDO_MODELS:
            if f"'{model}'" in context_window or f'"{model}"' in context_window:
                accessed_model = model
                break

        # Check if sudo() has no domain filter after it
        post_sudo = '\n'.join(source_lines[line_num:min(len(source_lines), line_num + 3)])
        has_domain = bool(re.search(r'search\(|browse\(|read\(|with_context\(', post_sudo))
        unscoped = not has_domain and not re.search(r'search|browse|read|_compute|_get', context_window.lower())

        # Classify severity
        if file_context == 'controller' and (is_public or True):
            # Check the actual controller's auth level
            controller_context = '\n'.join(source_lines[max(0, line_num - 50):line_num])
            has_public_auth = re.search(r"auth=['\"](?:public|none)['\"]", controller_context)
            has_sudo_with_danger = accessed_model is not None

            if has_public_auth and has_sudo_with_danger:
                severity = 'CRITICAL'
                issue_type = 'sudo_in_public'
                message = (
                    f"sudo() accessing sensitive model '{accessed_model}' in "
                    f"public/unauthenticated route method '{func_name}' in class '{class_name}'. "
                    f"This allows unauthenticated users to bypass all access controls."
                )
                suggestion = SUDO_ALTERNATIVES['in_public']
            elif has_public_auth:
                severity = 'HIGH'
                issue_type = 'sudo_in_public'
                message = (
                    f"sudo() in public/portal route method '{func_name}' in class '{class_name}'. "
                    f"Ensure results are filtered to only expose data appropriate for public users."
                )
                suggestion = SUDO_ALTERNATIVES['portal']
            elif in_loop:
                severity = 'MEDIUM'
                issue_type = 'sudo_in_loop'
                message = (
                    f"sudo() inside a loop in method '{func_name}' (controller). "
                    f"Each iteration re-elevates privileges unnecessarily — use a single batched query."
                )
                suggestion = SUDO_ALTERNATIVES['in_loop']
            elif is_safe:
                severity = 'OK'
                issue_type = 'sudo_safe'
                message = f"sudo() in '{func_name}' — appears safe ({safe_reason})."
                suggestion = ''
            else:
                severity = 'LOW'
                issue_type = 'sudo_controller'
                message = (
                    f"sudo() in controller method '{func_name}'. "
                    f"Verify this is intentional and results are properly filtered."
                )
                suggestion = 'Review that sudo() results are scoped appropriately.'

        elif in_loop:
            severity = 'MEDIUM'
            issue_type = 'sudo_in_loop'
            message = (
                f"sudo() inside a loop in method '{func_name}' (class '{class_name}'). "
                f"Performance risk: privileges re-elevated on every iteration. "
                f"Move sudo() before the loop and batch the query."
            )
            suggestion = SUDO_ALTERNATIVES['in_loop']

        elif is_safe:
            severity = 'OK'
            issue_type = 'sudo_safe'
            message = f"sudo() in '{func_name}' — safe pattern ({safe_reason})."
            suggestion = ''

        elif accessed_model in DANGEROUS_SUDO_MODELS:
            severity = 'HIGH'
            issue_type = 'sudo_sensitive_model'
            message = (
                f"sudo() accessing sensitive model '{accessed_model}' in method '{func_name}'. "
                f"Verify this elevated access is necessary and results are filtered."
            )
            suggestion = SUDO_ALTERNATIVES['sensitive_model']

        elif file_context == 'wizard':
            severity = 'LOW'
            issue_type = 'sudo_in_wizard'
            message = (
                f"sudo() in wizard method '{func_name}'. "
                f"Ensure wizard is only accessible to appropriate user groups."
            )
            suggestion = 'Verify wizard access rules restrict to appropriate groups.'

        elif unscoped and enclosing_func:
            severity = 'MEDIUM'
            issue_type = 'sudo_unscoped'
            message = (
                f"sudo() in method '{func_name}' without immediate domain filtering. "
                f"Unscoped sudo() grants access to all records without restriction."
            )
            suggestion = SUDO_ALTERNATIVES['unscoped']

        else:
            severity = 'LOW'
            issue_type = 'sudo_review'
            message = (
                f"sudo() in method '{func_name}'. "
                f"Review to ensure elevated privileges are justified and minimal."
            )
            suggestion = 'Document why sudo() is needed with an inline comment.'

        findings.append({
            'severity': severity,
            'type': issue_type,
            'file': str(rel_path),
            'line': line_num,
            'message': message,
            'suggestion': suggestion,
            'context': {
                'function': func_name,
                'class': class_name,
                'file_context': file_context,
                'in_loop': in_loop,
                'is_public_route': is_public,
                'accessed_model': accessed_model,
            },
            'code_snippet': line_text,
        })

    return findings


def scan_for_sudo(module_path: Path, include_ok: bool = False) -> List[Dict]:
    """
    Main analysis function. Returns list of sudo() findings.
    """
    all_findings = []
    module_path = Path(module_path)

    py_files = find_python_files(module_path)

    for py_file in py_files:
        try:
            source = py_file.read_text(encoding='utf-8', errors='replace')
        except (OSError, IOError):
            continue

        # Quick pre-check — skip files without sudo()
        if '.sudo()' not in source:
            continue

        file_findings = find_sudo_calls(source, py_file, module_path)
        all_findings.extend(file_findings)

    # Filter out OK findings unless --all is requested
    if not include_ok:
        all_findings = [f for f in all_findings if f['severity'] != 'OK']

    return all_findings


def format_text_report(findings: List[Dict], module_path: Path, verbose: bool = False) -> str:
    """Format findings as a human-readable text report."""
    lines = []
    module_name = module_path.name

    counts = {s: 0 for s in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'OK']}
    for finding in findings:
        sev = finding.get('severity', 'LOW')
        if sev in counts:
            counts[sev] += 1

    lines.append(f"\n{'='*60}")
    lines.append(f"SUDO FINDER REPORT — {module_name}")
    lines.append(f"{'='*60}")
    lines.append(f"Total findings: {len(findings)}")
    for sev, count in counts.items():
        if count:
            lines.append(f"  {sev}: {count}")
    lines.append("")

    for finding in sorted(findings, key=lambda x: -(
        {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'OK': 0}.get(x.get('severity', 'LOW'), 1)
    )):
        severity = finding.get('severity', 'LOW')
        file_info = finding.get('file', '')
        line = finding.get('line', '')
        loc = f"{file_info}:{line}" if line else file_info

        lines.append(f"[{severity}] {loc}")
        lines.append(f"  {finding.get('message', '')}")

        if verbose:
            ctx = finding.get('context', {})
            lines.append(f"  Context: function={ctx.get('function')}, class={ctx.get('class')}, "
                         f"file_type={ctx.get('file_context')}")
            if finding.get('code_snippet'):
                lines.append(f"  Code: {finding['code_snippet']}")

        suggestion = finding.get('suggestion', '')
        if suggestion:
            lines.append(f"  FIX: {suggestion}")
        lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Find and classify sudo() usage in Odoo modules'
    )
    parser.add_argument('module_path', help='Path to the Odoo module')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', action='store_true', help='Show code context')
    parser.add_argument('--all', action='store_true', help='Show all sudo() calls including safe ones')

    args = parser.parse_args()
    module_path = Path(args.module_path).resolve()

    if not module_path.exists():
        print(json.dumps({'error': f'Path not found: {module_path}', 'issues': []}))
        sys.exit(2)

    findings = scan_for_sudo(module_path, include_ok=args.all)

    # Rename 'findings' key to 'issues' for consistency with other auditors
    issues = findings

    counts = {s: 0 for s in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']}
    for issue in issues:
        sev = issue.get('severity', 'LOW')
        if sev in counts:
            counts[sev] += 1

    if args.json:
        output = {
            'auditor': 'sudo_finder',
            'module': module_path.name,
            'module_path': str(module_path),
            'summary': {'total': len(issues), 'by_severity': counts},
            'issues': issues,
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print(format_text_report(findings, module_path, verbose=args.verbose))

    # Exit 1 only if there are non-OK issues
    has_real_issues = any(
        i.get('severity', 'LOW') not in ('OK', 'LOW')
        for i in issues
    )
    sys.exit(1 if has_real_issues else 0)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Odoo Security Auditor — Master Orchestration Script
====================================================
Runs all sub-auditors (access_checker, route_auditor, sudo_finder) and
produces a unified severity-graded security report.

Usage:
    python security_auditor.py <module_path> [options]

Options:
    --min-severity {CRITICAL,HIGH,MEDIUM,LOW}  Minimum severity to report (default: LOW)
    --exit-on-issues                           Exit with code 1 if any issues found
    --json                                     Output report as JSON
    --output <file>                            Write report to file instead of stdout

Exit codes:
    0 = No issues found at or above min-severity
    1 = Issues found at or above min-severity
    2 = Usage/configuration error
"""

import sys
import os
import json
import argparse
import subprocess
import textwrap
from pathlib import Path
from datetime import datetime

# ANSI color codes for terminal output
COLORS = {
    'CRITICAL': '\033[91m',  # Red
    'HIGH':     '\033[93m',  # Yellow
    'MEDIUM':   '\033[94m',  # Blue
    'LOW':      '\033[96m',  # Cyan
    'OK':       '\033[92m',  # Green
    'RESET':    '\033[0m',
    'BOLD':     '\033[1m',
    'DIM':      '\033[2m',
}

SEVERITY_ORDER = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']

SEVERITY_WEIGHTS = {
    'CRITICAL': 4,
    'HIGH': 3,
    'MEDIUM': 2,
    'LOW': 1,
}

SCRIPTS_DIR = Path(__file__).parent


def colorize(text, color_key):
    """Wrap text in ANSI color codes."""
    if not sys.stdout.isatty():
        return text
    return f"{COLORS.get(color_key, '')}{text}{COLORS['RESET']}"


def bold(text):
    """Bold text for terminals."""
    if not sys.stdout.isatty():
        return text
    return f"{COLORS['BOLD']}{text}{COLORS['RESET']}"


def dim(text):
    """Dim text for terminals."""
    if not sys.stdout.isatty():
        return text
    return f"{COLORS['DIM']}{text}{COLORS['RESET']}"


def severity_badge(severity):
    """Return a colored severity label."""
    return colorize(f"[{severity:<8}]", severity)


def run_sub_auditor(script_name, module_path, extra_args=None):
    """
    Run a sub-auditor script and return its JSON output.

    Returns:
        dict with keys: 'issues', 'summary', 'error' (if failed)
    """
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return {
            'issues': [],
            'summary': {},
            'error': f"Script not found: {script_path}"
        }

    cmd = [sys.executable, str(script_path), str(module_path), '--json']
    if extra_args:
        cmd.extend(extra_args)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.stdout:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {
                    'issues': [],
                    'summary': {},
                    'error': f"Invalid JSON from {script_name}: {result.stdout[:200]}"
                }
        return {
            'issues': [],
            'summary': {},
            'error': result.stderr[:500] if result.stderr else 'No output'
        }
    except subprocess.TimeoutExpired:
        return {
            'issues': [],
            'summary': {},
            'error': f"Timeout running {script_name}"
        }
    except Exception as e:
        return {
            'issues': [],
            'summary': {},
            'error': str(e)
        }


def validate_module_path(module_path):
    """
    Validate that the given path looks like an Odoo module.

    Returns:
        (is_valid, warnings) tuple
    """
    path = Path(module_path)
    warnings = []

    if not path.exists():
        return False, [f"Path does not exist: {module_path}"]

    if not path.is_dir():
        return False, [f"Path is not a directory: {module_path}"]

    # Check for __manifest__.py (Odoo 10+) or __openerp__.py (Odoo 8/9)
    has_manifest = (path / '__manifest__.py').exists() or (path / '__openerp__.py').exists()
    if not has_manifest:
        warnings.append("No __manifest__.py found — may not be a valid Odoo module")

    # Check for models directory
    if not (path / 'models').exists():
        warnings.append("No models/ directory found — may be a theme or data module")

    # Check for security directory
    if not (path / 'security').exists():
        warnings.append("No security/ directory found — access control may be missing")

    return True, warnings


def compute_risk_score(issues):
    """Compute an overall risk score from 0-100."""
    if not issues:
        return 0
    score = sum(SEVERITY_WEIGHTS.get(i.get('severity', 'LOW'), 1) for i in issues)
    # Normalize: 10 CRITICAL = 100, more issues = higher score, capped at 100
    return min(100, int(score * 2.5))


def get_risk_label(score):
    """Return a risk label based on score."""
    if score >= 80:
        return ('CRITICAL', 'Immediate action required')
    elif score >= 50:
        return ('HIGH', 'Significant vulnerabilities present')
    elif score >= 25:
        return ('MEDIUM', 'Some issues to address')
    elif score > 0:
        return ('LOW', 'Minor improvements recommended')
    else:
        return ('OK', 'No issues detected')


def filter_issues_by_severity(issues, min_severity):
    """Filter issues to only include those at or above min_severity."""
    min_weight = SEVERITY_WEIGHTS.get(min_severity, 1)
    return [i for i in issues if SEVERITY_WEIGHTS.get(i.get('severity', 'LOW'), 1) >= min_weight]


def generate_remediation(issue):
    """Generate a remediation suggestion for a given issue."""
    issue_type = issue.get('type', '')
    severity = issue.get('severity', 'LOW')

    remediations = {
        'missing_access_rule': (
            "Add an entry to security/ir.model.access.csv for this model. "
            "At minimum: access_[model]_user,[model] user,model_[model],[group],1,1,1,0"
        ),
        'auth_none_route': (
            "Change auth='none' to auth='user' for internal routes, or implement "
            "API key/HMAC signature validation before processing the request."
        ),
        'auth_public_sensitive': (
            "Verify this route only returns publicly safe data. If it accesses "
            "sensitive models, change to auth='user' or add explicit field filtering."
        ),
        'csrf_disabled': (
            "Remove csrf=False from non-API routes. For machine-to-machine APIs, "
            "ensure API key authentication is implemented as a replacement."
        ),
        'sudo_in_public': (
            "Remove sudo() from public/portal controllers. Use _document_check_access() "
            "for record verification, or add domain filters to scope results to current user."
        ),
        'sudo_in_loop': (
            "Move sudo() call outside the loop. Use read_group() or a single search() "
            "with all record IDs, then map results by ID in Python."
        ),
        'sql_injection': (
            "Replace string formatting with parameterized queries: "
            "self.env.cr.execute('SELECT ... WHERE x = %s', (value,)) — note the tuple."
        ),
        'missing_record_rule': (
            "Add record rules to security/rules_[module].xml. For multi-company models, "
            "add a company_id domain rule. For user-specific models, add user_id scoping."
        ),
        'sensitive_field_no_group': (
            "Add groups='[module].[group]' to the field definition to restrict visibility. "
            "Example: salary = fields.Float(groups='hr.group_hr_manager')"
        ),
        'missing_company_rule': (
            "Add a multi-company record rule: domain_force = "
            "['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]"
        ),
    }

    default = (
        f"Review this {severity} issue and apply security best practices. "
        "Consult the SKILL.md remediation section for detailed fix patterns."
    )

    return remediations.get(issue_type, default)


def print_report(module_path, all_issues, sub_results, min_severity, options):
    """Print a formatted security report to stdout."""
    module_name = Path(module_path).name
    filtered_issues = filter_issues_by_severity(all_issues, min_severity)
    risk_score = compute_risk_score(all_issues)
    risk_label, risk_desc = get_risk_label(risk_score)

    # Count by severity
    counts = {s: 0 for s in SEVERITY_ORDER}
    for issue in all_issues:
        sev = issue.get('severity', 'LOW')
        if sev in counts:
            counts[sev] += 1

    print()
    print(bold("=" * 70))
    print(bold(f"  ODOO SECURITY AUDIT REPORT"))
    print(bold("=" * 70))
    print(f"  Module:    {bold(module_name)}")
    print(f"  Path:      {dim(str(module_path))}")
    print(f"  Date:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Risk Score: {colorize(str(risk_score) + '/100', risk_label)} — {risk_desc}")
    print()

    # Summary table
    print(bold("  SUMMARY"))
    print("  " + "-" * 40)
    for sev in SEVERITY_ORDER:
        count = counts[sev]
        indicator = colorize(f"{count:>4} issue{'s' if count != 1 else ' '}", sev if count > 0 else 'OK')
        print(f"  {sev:<12} {indicator}")
    print(f"  {'TOTAL':<12} {len(all_issues):>4} issue{'s' if len(all_issues) != 1 else ' '}")
    print()

    # Sub-auditor results
    print(bold("  AUDITOR STATUS"))
    print("  " + "-" * 40)
    for auditor_name, result in sub_results.items():
        if result.get('error'):
            status = colorize("ERROR", 'HIGH')
            print(f"  {auditor_name:<20} {status}: {result['error'][:60]}")
        else:
            issue_count = len(result.get('issues', []))
            status = colorize(f"{issue_count} issues", 'HIGH' if issue_count else 'OK')
            print(f"  {auditor_name:<20} {status}")
    print()

    if not filtered_issues:
        print(colorize(
            f"  No issues found at or above {min_severity} severity. Great job!",
            'OK'
        ))
        print()
        return

    # Detailed issues
    print(bold(f"  ISSUES (showing {min_severity}+, {len(filtered_issues)} total)"))
    print("  " + "=" * 68)

    current_file = None
    for issue in sorted(filtered_issues, key=lambda x: -SEVERITY_WEIGHTS.get(x.get('severity', 'LOW'), 1)):
        file_path = issue.get('file', 'unknown')
        line = issue.get('line', '')
        severity = issue.get('severity', 'LOW')
        message = issue.get('message', 'No description')
        issue_type = issue.get('type', '')

        # File header
        if file_path != current_file:
            print()
            print(f"  {bold(dim(file_path))}")
            current_file = file_path

        # Issue line
        location = f":{line}" if line else ""
        print(f"  {severity_badge(severity)} {file_path}{location}")
        print(f"    {message}")

        # Remediation
        remediation = generate_remediation(issue)
        wrapped = textwrap.fill(remediation, width=65, initial_indent="    FIX: ", subsequent_indent="         ")
        print(dim(wrapped))
        print()

    print(bold("=" * 70))
    print()


def generate_json_report(module_path, all_issues, sub_results, options):
    """Generate a structured JSON report."""
    module_name = Path(module_path).name
    risk_score = compute_risk_score(all_issues)
    risk_label, risk_desc = get_risk_label(risk_score)

    counts = {s: 0 for s in SEVERITY_ORDER}
    for issue in all_issues:
        sev = issue.get('severity', 'LOW')
        if sev in counts:
            counts[sev] += 1

    # Enrich issues with remediation
    enriched_issues = []
    for issue in all_issues:
        enriched = dict(issue)
        enriched['remediation'] = generate_remediation(issue)
        enriched_issues.append(enriched)

    return {
        'module': module_name,
        'module_path': str(module_path),
        'audit_date': datetime.now().isoformat(),
        'risk_score': risk_score,
        'risk_label': risk_label,
        'risk_description': risk_desc,
        'summary': {
            'total': len(all_issues),
            'by_severity': counts,
        },
        'auditors': {
            name: {
                'issues': result.get('issues', []),
                'error': result.get('error'),
            }
            for name, result in sub_results.items()
        },
        'issues': enriched_issues,
    }


def main():
    parser = argparse.ArgumentParser(
        description='Odoo Security Auditor — comprehensive module security analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python security_auditor.py /path/to/my_module
          python security_auditor.py /path/to/my_module --min-severity HIGH
          python security_auditor.py /path/to/my_module --json --output report.json
          python security_auditor.py /path/to/my_module --min-severity CRITICAL --exit-on-issues
        """)
    )
    parser.add_argument('module_path', help='Path to the Odoo module to audit')
    parser.add_argument(
        '--min-severity',
        choices=SEVERITY_ORDER,
        default='LOW',
        help='Minimum severity level to report (default: LOW)'
    )
    parser.add_argument(
        '--exit-on-issues',
        action='store_true',
        help='Exit with code 1 if issues found at min-severity or above'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output report in JSON format'
    )
    parser.add_argument(
        '--output',
        metavar='FILE',
        help='Write report to file instead of stdout'
    )
    parser.add_argument(
        '--skip-auditor',
        action='append',
        choices=['access', 'routes', 'sudo'],
        default=[],
        metavar='AUDITOR',
        help='Skip a specific auditor (can be used multiple times)'
    )

    args = parser.parse_args()
    module_path = Path(args.module_path).resolve()

    # Validate module path
    is_valid, validation_warnings = validate_module_path(module_path)
    if not is_valid:
        for warning in validation_warnings:
            print(colorize(f"ERROR: {warning}", 'CRITICAL'), file=sys.stderr)
        sys.exit(2)

    if validation_warnings and not args.json:
        for warning in validation_warnings:
            print(colorize(f"WARNING: {warning}", 'MEDIUM'), file=sys.stderr)

    # Run sub-auditors
    sub_results = {}
    all_issues = []

    auditors = [
        ('access_checker', 'access_checker.py', 'access' not in args.skip_auditor),
        ('route_auditor', 'route_auditor.py', 'routes' not in args.skip_auditor),
        ('sudo_finder', 'sudo_finder.py', 'sudo' not in args.skip_auditor),
    ]

    if not args.json:
        print(f"\nRunning security audit on: {bold(str(module_path))}")

    for auditor_name, script_name, should_run in auditors:
        if not should_run:
            if not args.json:
                print(f"  Skipping {auditor_name}...")
            continue

        if not args.json:
            print(f"  Running {auditor_name}...", end=' ', flush=True)

        result = run_sub_auditor(script_name, module_path)
        sub_results[auditor_name] = result

        issues = result.get('issues', [])
        all_issues.extend(issues)

        if not args.json:
            if result.get('error'):
                print(colorize('ERROR', 'HIGH'))
            else:
                count = len(issues)
                if count == 0:
                    print(colorize('CLEAN', 'OK'))
                else:
                    # Count criticals/highs
                    critical = sum(1 for i in issues if i.get('severity') == 'CRITICAL')
                    high = sum(1 for i in issues if i.get('severity') == 'HIGH')
                    summary_parts = []
                    if critical:
                        summary_parts.append(colorize(f"{critical} CRITICAL", 'CRITICAL'))
                    if high:
                        summary_parts.append(colorize(f"{high} HIGH", 'HIGH'))
                    other = count - critical - high
                    if other:
                        summary_parts.append(f"{other} other")
                    print(', '.join(summary_parts) if summary_parts else str(count) + ' issues')

    # Generate output
    filtered_issues = filter_issues_by_severity(all_issues, args.min_severity)

    if args.json:
        report = generate_json_report(module_path, all_issues, sub_results, args)
        output_text = json.dumps(report, indent=2, default=str)
    else:
        # Capture print_report output if writing to file
        import io
        if args.output:
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()

        print_report(module_path, all_issues, sub_results, args.min_severity, args)

        if args.output:
            output_text = sys.stdout.getvalue()
            sys.stdout = old_stdout
            print(output_text)
        else:
            output_text = None

    # Write to file if requested
    if args.output and output_text:
        output_path = Path(args.output)
        output_path.write_text(output_text, encoding='utf-8')
        if not args.json:
            print(f"Report written to: {args.output}")

    # Exit code
    if args.exit_on_issues and filtered_issues:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()

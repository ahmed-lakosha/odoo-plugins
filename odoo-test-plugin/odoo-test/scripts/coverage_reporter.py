#!/usr/bin/env python3
"""
Odoo Test Coverage Reporter
============================
Scans an Odoo module's Python source files to identify all public methods,
cross-references them with test files to determine coverage, and produces a
detailed report with a coverage percentage per model and overall.

Usage:
    python coverage_reporter.py --module /path/to/my_module
    python coverage_reporter.py --module /path/to/my_module --output report.json
    python coverage_reporter.py --module /path/to/my_module --format html --output coverage.html
    python coverage_reporter.py --module /path/to/my_module --threshold 80
"""

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from textwrap import dedent


# ─── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class MethodInfo:
    name: str
    file: str
    line: int
    class_name: str
    decorator: list = field(default_factory=list)
    is_tested: bool = False
    test_methods: list = field(default_factory=list)
    is_private: bool = False
    is_compute: bool = False
    is_constraint: bool = False
    is_onchange: bool = False
    is_action: bool = False

@dataclass
class ModelCoverage:
    model_name: str
    class_name: str
    file: str
    methods: list = field(default_factory=list)

    @property
    def total_testable(self) -> int:
        return sum(1 for m in self.methods if not m.is_private)

    @property
    def tested_count(self) -> int:
        return sum(1 for m in self.methods if not m.is_private and m.is_tested)

    @property
    def coverage_pct(self) -> float:
        if self.total_testable == 0:
            return 100.0
        return round(self.tested_count / self.total_testable * 100, 1)

    @property
    def untested_methods(self) -> list:
        return [m for m in self.methods if not m.is_private and not m.is_tested]

    @property
    def tested_methods(self) -> list:
        return [m for m in self.methods if not m.is_private and m.is_tested]


@dataclass
class CoverageReport:
    module_name: str
    module_path: str
    models: list = field(default_factory=list)
    test_methods_found: list = field(default_factory=list)

    @property
    def total_methods(self) -> int:
        return sum(m.total_testable for m in self.models)

    @property
    def tested_methods(self) -> int:
        return sum(m.tested_count for m in self.models)

    @property
    def overall_coverage(self) -> float:
        if self.total_methods == 0:
            return 100.0
        return round(self.tested_methods / self.total_methods * 100, 1)

    @property
    def uncovered_models(self) -> list:
        return [m for m in self.models if m.coverage_pct < 50.0]

    @property
    def well_covered_models(self) -> list:
        return [m for m in self.models if m.coverage_pct >= 80.0]


# ─── Source Analyser ──────────────────────────────────────────────────────────

ODOO_DECORATORS = {
    'depends':    'compute',
    'constrains': 'constraint',
    'onchange':   'onchange',
    'model':      'model',
    'model_create_multi': 'model',
}

SKIP_METHODS = frozenset({
    'setUp', 'setUpClass', 'tearDown', 'tearDownClass',
    '__init__', '__repr__', '__str__', '__eq__', '__hash__',
    'create', 'write', 'unlink', 'read', 'search', 'copy',
    'default_get', 'fields_get',
    'name_get', 'name_search',
})


class ModuleAnalyser:
    """Analyses Odoo module source to extract method inventory."""

    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.models: list[ModelCoverage] = []

    def analyse(self):
        """Walk the module directory and analyse all Python model files."""
        model_dirs = [
            self.module_path / 'models',
            self.module_path,
        ]
        # Exclude test files and __init__ / __manifest__
        for model_dir in model_dirs:
            if not model_dir.exists():
                continue
            for py_file in sorted(model_dir.glob('*.py')):
                if py_file.name in ('__init__.py', '__manifest__.py'):
                    continue
                if 'test' in py_file.name.lower():
                    continue
                self._analyse_file(py_file)

    def _analyse_file(self, file_path: Path):
        """Extract model classes and their methods from a Python file."""
        try:
            source = file_path.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(source)
        except SyntaxError:
            return

        rel_path = str(file_path.relative_to(self.module_path))

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            # Find _name or _inherit to identify Odoo models
            model_name = None
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == '_name':
                            if isinstance(item.value, ast.Constant):
                                model_name = item.value.value

            if not model_name:
                # Check for _inherit only
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == '_inherit':
                                if isinstance(item.value, ast.Constant):
                                    model_name = f"{item.value.value} (inherited)"

            if not model_name:
                continue

            coverage = ModelCoverage(
                model_name=model_name,
                class_name=node.name,
                file=rel_path,
            )

            for item in node.body:
                if not isinstance(item, ast.FunctionDef):
                    continue

                method_name = item.name
                is_private = method_name.startswith('_')
                is_dunder  = method_name.startswith('__') and method_name.endswith('__')

                if is_dunder or method_name in SKIP_METHODS:
                    continue

                # Extract decorators
                decs = []
                for dec in item.decorator_list:
                    if isinstance(dec, ast.Attribute):
                        decs.append(dec.attr)
                    elif isinstance(dec, ast.Name):
                        decs.append(dec.id)
                    elif isinstance(dec, ast.Call):
                        if isinstance(dec.func, ast.Attribute):
                            decs.append(dec.func.attr)
                        elif isinstance(dec, ast.Name):
                            decs.append(dec.func.id)

                is_compute    = 'depends' in decs
                is_constraint = 'constrains' in decs
                is_onchange   = 'onchange' in decs
                is_action     = method_name.startswith('action_')

                minfo = MethodInfo(
                    name=method_name,
                    file=rel_path,
                    line=item.lineno,
                    class_name=node.name,
                    decorator=decs,
                    is_private=is_private,
                    is_compute=is_compute,
                    is_constraint=is_constraint,
                    is_onchange=is_onchange,
                    is_action=is_action,
                )
                coverage.methods.append(minfo)

            if coverage.methods:
                self.models.append(coverage)


# ─── Test File Analyser ───────────────────────────────────────────────────────

class TestAnalyser:
    """Analyses test files to build a set of tested method names."""

    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.test_method_calls: set[str] = set()  # method names referenced in tests
        self.test_methods: list[str] = []          # test method names (test_*)

    def analyse(self):
        """Scan tests/ directory for all test methods and their content."""
        test_dir = self.module_path / 'tests'
        if not test_dir.exists():
            return

        for py_file in test_dir.glob('**/*.py'):
            if py_file.name == '__init__.py':
                continue
            self._analyse_test_file(py_file)

    def _analyse_test_file(self, file_path: Path):
        """Extract test method names and method calls from a test file."""
        try:
            source = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return

        # Find all test method names
        for m in re.finditer(r'def (test_\w+)', source):
            self.test_methods.append(m.group(1))

        # Find all method call references (e.g., record.action_confirm() → action_confirm)
        # This covers: self.record.method_name(), record.method_name(), obj.method_name()
        for m in re.finditer(r'\.(\w+)\s*\(', source):
            method_ref = m.group(1)
            if not method_ref.startswith('assert') and not method_ref.startswith('_'):
                self.test_method_calls.add(method_ref)

        # Also extract from test method names: test_action_confirm → action_confirm
        for test_name in self.test_methods:
            # Strip test_ prefix and try to match
            stripped = test_name[5:]  # Remove 'test_'
            self.test_method_calls.add(stripped)
            # Also try common prefixes
            for prefix in ('action_', 'compute_', 'onchange_', 'constraint_', 'check_', 'get_'):
                if stripped.startswith(prefix.replace('_', '')):
                    self.test_method_calls.add(prefix + stripped[len(prefix.replace('_', '')):])


# ─── Report Formatter ─────────────────────────────────────────────────────────

USE_COLOR = sys.stdout.isatty() and not os.environ.get('NO_COLOR')

class TermColor:
    RESET   = '\033[0m' if USE_COLOR else ''
    BOLD    = '\033[1m' if USE_COLOR else ''
    GREEN   = '\033[92m' if USE_COLOR else ''
    RED     = '\033[91m' if USE_COLOR else ''
    YELLOW  = '\033[93m' if USE_COLOR else ''
    CYAN    = '\033[96m' if USE_COLOR else ''
    BLUE    = '\033[94m' if USE_COLOR else ''
    DIM     = '\033[2m'  if USE_COLOR else ''

def _coverage_color(pct: float) -> str:
    if pct >= 80:
        return TermColor.GREEN
    elif pct >= 50:
        return TermColor.YELLOW
    else:
        return TermColor.RED

def _coverage_bar(pct: float, width: int = 20) -> str:
    filled = int(pct / 100 * width)
    bar = '█' * filled + '░' * (width - filled)
    return f"{_coverage_color(pct)}[{bar}]{TermColor.RESET}"


def format_terminal_report(report: CoverageReport) -> str:
    lines = []
    sep = '─' * 72

    lines.append(f"\n{TermColor.BLUE}{TermColor.BOLD}{'═' * 72}{TermColor.RESET}")
    lines.append(f"{TermColor.BLUE}{TermColor.BOLD}  ODOO TEST COVERAGE REPORT — {report.module_name}{TermColor.RESET}")
    lines.append(f"{TermColor.BLUE}{TermColor.BOLD}{'═' * 72}{TermColor.RESET}")
    lines.append(f"  Module path: {report.module_path}")
    lines.append(f"  Models analysed: {len(report.models)}")
    lines.append(f"  Test methods found: {len(report.test_methods_found)}")
    lines.append('')

    # Per-model table
    lines.append(f"  {TermColor.BOLD}{'Model':<35} {'File':<25} {'Methods':>7} {'Tested':>7} {'Coverage':>9}{TermColor.RESET}")
    lines.append(f"  {sep}")

    for model in sorted(report.models, key=lambda m: m.coverage_pct):
        color = _coverage_color(model.coverage_pct)
        file_short = model.file[:24]
        lines.append(
            f"  {model.model_name:<35} {file_short:<25} "
            f"{model.total_testable:>7} {model.tested_count:>7} "
            f"{color}{model.coverage_pct:>8.1f}%{TermColor.RESET}"
        )

    lines.append(f"  {sep}")
    overall_color = _coverage_color(report.overall_coverage)
    lines.append(
        f"  {'TOTAL':<35} {'':<25} "
        f"{report.total_methods:>7} {report.tested_methods:>7} "
        f"{overall_color}{TermColor.BOLD}{report.overall_coverage:>8.1f}%{TermColor.RESET}"
    )

    # Coverage bar
    lines.append('')
    lines.append(f"  Overall Coverage: {_coverage_bar(report.overall_coverage)} {overall_color}{report.overall_coverage:.1f}%{TermColor.RESET}")
    lines.append('')

    # Untested methods
    all_untested = [
        (model.model_name, m)
        for model in report.models
        for m in model.untested_methods
    ]

    if all_untested:
        lines.append(f"  {TermColor.RED}{TermColor.BOLD}Untested Methods ({len(all_untested)} total):{TermColor.RESET}")
        for model_name, method in sorted(all_untested, key=lambda x: x[0]):
            kind = ''
            if method.is_action:
                kind = ' [ACTION]'
            elif method.is_compute:
                kind = ' [COMPUTE]'
            elif method.is_constraint:
                kind = ' [CONSTRAINT]'
            elif method.is_onchange:
                kind = ' [ONCHANGE]'
            lines.append(
                f"    {TermColor.DIM}{model_name}{TermColor.RESET}.{TermColor.RED}{method.name}{TermColor.RESET}"
                f"{TermColor.YELLOW}{kind}{TermColor.RESET}  (line {method.line})"
            )
    else:
        lines.append(f"  {TermColor.GREEN}{TermColor.BOLD}All public methods are covered!{TermColor.RESET}")

    lines.append('')

    # Recommendations
    lines.append(f"  {TermColor.CYAN}{TermColor.BOLD}Recommendations:{TermColor.RESET}")
    if report.overall_coverage < 50:
        lines.append(f"  {TermColor.RED}• Critical: Coverage is below 50%. Add tests immediately.{TermColor.RESET}")
    elif report.overall_coverage < 80:
        lines.append(f"  {TermColor.YELLOW}• Coverage is below 80% target. Focus on untested action_ methods.{TermColor.RESET}")
    else:
        lines.append(f"  {TermColor.GREEN}• Good coverage! Consider adding edge case tests.{TermColor.RESET}")

    constraint_untested = [m for _, m in all_untested if m.is_constraint]
    if constraint_untested:
        lines.append(f"  {TermColor.RED}• {len(constraint_untested)} constraint method(s) untested! These are high-priority.{TermColor.RESET}")

    action_untested = [m for _, m in all_untested if m.is_action]
    if action_untested:
        lines.append(f"  {TermColor.YELLOW}• {len(action_untested)} action method(s) untested. Add workflow tests.{TermColor.RESET}")

    lines.append(f"  • Use /test-generate to create test skeletons for untested models.")
    lines.append(f"  • Run: python coverage_reporter.py --module . --threshold 80 (for CI gate)")
    lines.append('')

    return '\n'.join(lines)


def format_json_report(report: CoverageReport) -> str:
    data = {
        'module_name': report.module_name,
        'module_path': report.module_path,
        'overall_coverage': report.overall_coverage,
        'total_methods': report.total_methods,
        'tested_methods': report.tested_methods,
        'test_methods_count': len(report.test_methods_found),
        'models': [
            {
                'model_name': m.model_name,
                'class_name': m.class_name,
                'file': m.file,
                'coverage_pct': m.coverage_pct,
                'total_testable': m.total_testable,
                'tested_count': m.tested_count,
                'tested_methods': [mi.name for mi in m.tested_methods],
                'untested_methods': [
                    {
                        'name': mi.name,
                        'line': mi.line,
                        'is_action': mi.is_action,
                        'is_compute': mi.is_compute,
                        'is_constraint': mi.is_constraint,
                        'is_onchange': mi.is_onchange,
                    }
                    for mi in m.untested_methods
                ],
            }
            for m in report.models
        ],
    }
    return json.dumps(data, indent=2)


def format_html_report(report: CoverageReport) -> str:
    def coverage_class(pct: float) -> str:
        if pct >= 80:
            return 'good'
        elif pct >= 50:
            return 'warn'
        return 'bad'

    rows = ''
    for model in sorted(report.models, key=lambda m: m.coverage_pct):
        cc = coverage_class(model.coverage_pct)
        rows += f"""
        <tr>
            <td>{model.model_name}</td>
            <td><code>{model.file}</code></td>
            <td>{model.total_testable}</td>
            <td>{model.tested_count}</td>
            <td class="{cc}">{model.coverage_pct:.1f}%</td>
        </tr>"""
        for m in model.untested_methods:
            kind = 'ACTION' if m.is_action else ('COMPUTE' if m.is_compute else ('CONSTRAINT' if m.is_constraint else 'METHOD'))
            rows += f"""
        <tr class="untested">
            <td colspan="3">&nbsp;&nbsp;↳ <code>{m.name}()</code> <span class="badge">{kind}</span></td>
            <td>Line {m.line}</td>
            <td class="bad">Not tested</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Coverage Report — {report.module_name}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 2rem; background: #f8f9fa; color: #212529; }}
  h1 {{ color: #495057; }}
  .summary {{ display: flex; gap: 2rem; margin: 1rem 0 2rem; }}
  .metric {{ background: white; padding: 1rem 2rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,.1); }}
  .metric h3 {{ margin: 0 0 0.5rem; font-size: 0.9rem; color: #6c757d; text-transform: uppercase; }}
  .metric span {{ font-size: 2rem; font-weight: bold; }}
  .good {{ color: #28a745; }} .warn {{ color: #ffc107; }} .bad {{ color: #dc3545; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.1); }}
  th {{ background: #495057; color: white; padding: 0.75rem 1rem; text-align: left; font-size: 0.85rem; text-transform: uppercase; }}
  td {{ padding: 0.5rem 1rem; border-bottom: 1px solid #dee2e6; font-size: 0.9rem; }}
  tr.untested td {{ background: #fff5f5; color: #666; }}
  .badge {{ background: #6c757d; color: white; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.75rem; }}
  tr:hover td {{ background: #f1f3f5; }}
</style>
</head>
<body>
<h1>Test Coverage Report — {report.module_name}</h1>
<div class="summary">
  <div class="metric"><h3>Overall Coverage</h3><span class="{coverage_class(report.overall_coverage)}">{report.overall_coverage:.1f}%</span></div>
  <div class="metric"><h3>Total Methods</h3><span>{report.total_methods}</span></div>
  <div class="metric"><h3>Tested</h3><span class="good">{report.tested_methods}</span></div>
  <div class="metric"><h3>Untested</h3><span class="bad">{report.total_methods - report.tested_methods}</span></div>
  <div class="metric"><h3>Test Methods</h3><span>{len(report.test_methods_found)}</span></div>
</div>
<table>
  <thead><tr><th>Model</th><th>File</th><th>Methods</th><th>Tested</th><th>Coverage</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
<p style="color:#aaa;font-size:0.8rem;margin-top:2rem">Generated by odoo-test-plugin coverage_reporter.py</p>
</body>
</html>"""


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Analyse test coverage for an Odoo module.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""
        Examples:
          python coverage_reporter.py --module /c/odoo/odoo17/projects/myproject/my_module
          python coverage_reporter.py --module . --output report.json --format json
          python coverage_reporter.py --module . --output coverage.html --format html
          python coverage_reporter.py --module . --threshold 80  # Exit code 1 if below threshold
        """)
    )
    parser.add_argument('--module', required=True, help='Path to the Odoo module directory')
    parser.add_argument('--output', help='Output file path for the report')
    parser.add_argument('--format', choices=['terminal', 'json', 'html'], default='terminal',
                        help='Report format (default: terminal)')
    parser.add_argument('--threshold', type=float, default=0,
                        help='Minimum coverage percentage (exit code 1 if below)')

    args = parser.parse_args()

    module_path = Path(args.module).resolve()
    if not module_path.exists():
        print(f"[ERROR] Module path not found: {module_path}", file=sys.stderr)
        sys.exit(2)

    module_name = module_path.name

    # Analyse source
    source_analyser = ModuleAnalyser(module_path)
    source_analyser.analyse()

    if not source_analyser.models:
        print(f"[WARN] No Odoo model classes found in {module_path}", file=sys.stderr)
        print("       Ensure the module has models/ directory with Python files.")
        sys.exit(0)

    # Analyse tests
    test_analyser = TestAnalyser(module_path)
    test_analyser.analyse()

    # Cross-reference: mark methods as tested
    for model in source_analyser.models:
        for method in model.methods:
            if method.is_private:
                continue
            # Check if method name appears in test method calls
            if method.name in test_analyser.test_method_calls:
                method.is_tested = True
            # Check test method names: test_<method_name> pattern
            expected_test_names = [
                f'test_{method.name}',
                f'test_{method.name}_',
                f'test_create',      # Common: test_create covers model.create()
                f'test_write',
                f'test_unlink',
            ]
            for test_name in test_analyser.test_methods:
                if any(test_name == e or test_name.startswith(e) for e in expected_test_names):
                    method.is_tested = True
                    method.test_methods.append(test_name)

    # Build report
    report = CoverageReport(
        module_name=module_name,
        module_path=str(module_path),
        models=source_analyser.models,
        test_methods_found=test_analyser.test_methods,
    )

    # Format output
    if args.format == 'json':
        output_text = format_json_report(report)
    elif args.format == 'html':
        output_text = format_html_report(report)
    else:
        output_text = format_terminal_report(report)

    if args.output:
        Path(args.output).write_text(output_text, encoding='utf-8')
        print(f"[OK] Report written to: {args.output}")
    else:
        print(output_text)

    # Check threshold
    if args.threshold > 0 and report.overall_coverage < args.threshold:
        print(
            f"\n[FAIL] Coverage {report.overall_coverage:.1f}% is below threshold {args.threshold:.1f}%",
            file=sys.stderr
        )
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()

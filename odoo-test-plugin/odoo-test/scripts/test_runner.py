#!/usr/bin/env python3
"""
Odoo Test Runner Script
=======================
Wraps the Odoo test framework with colored output, structured logging,
progress tracking, and optional JUnit XML output for CI/CD pipelines.

Usage:
    python test_runner.py --module my_module --config conf/project17.conf --database project17
    python test_runner.py --module my_module --config conf/project17.conf --database project17 --tags post_install
    python test_runner.py --module my_module --config conf/project17.conf --database project17 --show-logs
    python test_runner.py --module my_module --config conf/project17.conf --database project17 --output-format junit --output results.xml
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from textwrap import dedent

# ─── Color Support ────────────────────────────────────────────────────────────

def supports_color() -> bool:
    """Check if the terminal supports ANSI color codes."""
    if os.environ.get('NO_COLOR'):
        return False
    if sys.platform == 'win32':
        try:
            import colorama
            colorama.init()
            return True
        except ImportError:
            return os.environ.get('TERM') is not None
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

USE_COLOR = supports_color()

class Color:
    RESET   = '\033[0m' if USE_COLOR else ''
    BOLD    = '\033[1m' if USE_COLOR else ''
    GREEN   = '\033[92m' if USE_COLOR else ''
    RED     = '\033[91m' if USE_COLOR else ''
    YELLOW  = '\033[93m' if USE_COLOR else ''
    CYAN    = '\033[96m' if USE_COLOR else ''
    BLUE    = '\033[94m' if USE_COLOR else ''
    MAGENTA = '\033[95m' if USE_COLOR else ''
    WHITE   = '\033[97m' if USE_COLOR else ''
    DIM     = '\033[2m'  if USE_COLOR else ''

def fmt_pass(text: str) -> str:
    return f"{Color.GREEN}{Color.BOLD}PASS{Color.RESET} {text}"

def fmt_fail(text: str) -> str:
    return f"{Color.RED}{Color.BOLD}FAIL{Color.RESET} {text}"

def fmt_error(text: str) -> str:
    return f"{Color.RED}{Color.BOLD}ERROR{Color.RESET} {text}"

def fmt_skip(text: str) -> str:
    return f"{Color.YELLOW}{Color.BOLD}SKIP{Color.RESET} {text}"

def fmt_info(text: str) -> str:
    return f"{Color.CYAN}[INFO]{Color.RESET} {text}"

def fmt_section(text: str) -> str:
    return f"\n{Color.BLUE}{Color.BOLD}{'─' * 60}{Color.RESET}\n{Color.BLUE}{Color.BOLD}{text}{Color.RESET}\n{'─' * 60}"

def fmt_summary_line(label: str, value: str, color: str = '') -> str:
    return f"  {Color.BOLD}{label:<20}{Color.RESET}{color}{value}{Color.RESET}"


# ─── Log Parser ───────────────────────────────────────────────────────────────

class OdooTestLogParser:
    """Parses Odoo test runner stdout/stderr and extracts structured results."""

    # Log line patterns
    PASS_PATTERN  = re.compile(r'\[OK\]\s+odoo\.tests[:\.](.+)')
    FAIL_PATTERN  = re.compile(r'(?:FAIL|FAILED)\s+odoo\.tests[:\.](.+)')
    ERROR_PATTERN = re.compile(r'ERROR\s+odoo\.tests[:\.](.+)')
    SKIP_PATTERN  = re.compile(r'SKIP\s+odoo\.tests[:\.](.+)')
    RAN_PATTERN   = re.compile(r'Ran (\d+) test[s]? in ([\d.]+)s')
    FAIL_MSG_PATTERN  = re.compile(r'AssertionError|ValidationError|UserError|psycopg2')
    TRACEBACK_START   = re.compile(r'^Traceback \(most recent call last\):')
    LOG_PREFIX        = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ \d+ (?:INFO|DEBUG|WARNING|ERROR) ')

    def __init__(self):
        self.results = []
        self.current_fail = None
        self.in_traceback = False
        self.total_ran = 0
        self.total_time = 0.0
        self.raw_lines = []

    def feed(self, line: str):
        """Process a single log line."""
        self.raw_lines.append(line)
        line_stripped = line.strip()

        # Strip Odoo log prefix to get the actual message
        clean = re.sub(self.LOG_PREFIX, '', line_stripped)

        m = self.PASS_PATTERN.search(clean)
        if m:
            self.results.append({
                'status': 'pass',
                'name': m.group(1).strip(),
                'message': '',
                'duration_ms': 0,
            })
            self.in_traceback = False
            return

        m = self.FAIL_PATTERN.search(clean)
        if m:
            self.current_fail = {
                'status': 'fail',
                'name': m.group(1).strip(),
                'message': '',
                'traceback': [],
                'duration_ms': 0,
            }
            self.results.append(self.current_fail)
            self.in_traceback = False
            return

        m = self.ERROR_PATTERN.search(clean)
        if m:
            self.current_fail = {
                'status': 'error',
                'name': m.group(1).strip(),
                'message': '',
                'traceback': [],
                'duration_ms': 0,
            }
            self.results.append(self.current_fail)
            self.in_traceback = False
            return

        m = self.SKIP_PATTERN.search(clean)
        if m:
            self.results.append({
                'status': 'skip',
                'name': m.group(1).strip(),
                'message': '',
                'duration_ms': 0,
            })
            return

        m = self.RAN_PATTERN.search(clean)
        if m:
            self.total_ran = int(m.group(1))
            self.total_time = float(m.group(2))
            return

        # Accumulate traceback/error message for current failure
        if self.TRACEBACK_START.match(clean):
            self.in_traceback = True

        if self.in_traceback and self.current_fail:
            self.current_fail.setdefault('traceback', []).append(clean)
            if self.FAIL_MSG_PATTERN.search(clean):
                self.current_fail['message'] = clean

    def get_summary(self) -> dict:
        passed = sum(1 for r in self.results if r['status'] == 'pass')
        failed = sum(1 for r in self.results if r['status'] == 'fail')
        errors = sum(1 for r in self.results if r['status'] == 'error')
        skipped = sum(1 for r in self.results if r['status'] == 'skip')
        return {
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'skipped': skipped,
            'total': len(self.results),
            'total_ran': self.total_ran or len(self.results),
            'duration_s': self.total_time,
            'success': failed == 0 and errors == 0,
        }


# ─── Command Builder ──────────────────────────────────────────────────────────

def build_odoo_command(
    config: str,
    database: str,
    module: str,
    tags: str | None = None,
    class_name: str | None = None,
    method_name: str | None = None,
    install: bool = False,
    log_level: str = 'test',
    extra_args: list | None = None,
) -> list[str]:
    """Build the Odoo test runner command."""

    # Detect odoo entry point
    odoo_bin = Path(config).parent.parent / 'odoo-bin'
    if odoo_bin.exists():
        cmd = [sys.executable, str(odoo_bin)]
    else:
        cmd = [sys.executable, '-m', 'odoo']

    cmd += ['-c', config, '-d', database]

    if install:
        cmd += ['-i', module]
    else:
        cmd += ['-u', module]

    cmd += ['--test-enable']

    # Build --test-tags
    if tags or class_name or method_name:
        tag_parts = []
        if tags:
            tag_parts.append(tags)
        if class_name:
            selector = f'/{module}:{class_name}'
            if method_name:
                selector += f'.{method_name}'
            tag_parts.append(selector)
        cmd += [f'--test-tags={",".join(tag_parts)}']

    cmd += [f'--log-level={log_level}']
    cmd += ['--stop-after-init']

    if extra_args:
        cmd += extra_args

    return cmd


# ─── JUnit XML Writer ─────────────────────────────────────────────────────────

def write_junit_xml(results: list[dict], summary: dict, output_path: str, suite_name: str = 'OdooTests'):
    """Write test results in JUnit XML format for Azure DevOps / Jenkins."""
    root = ET.Element('testsuites')
    suite = ET.SubElement(root, 'testsuite')
    suite.set('name', suite_name)
    suite.set('tests', str(summary['total']))
    suite.set('failures', str(summary['failed']))
    suite.set('errors', str(summary['errors']))
    suite.set('skipped', str(summary['skipped']))
    suite.set('time', str(round(summary['duration_s'], 3)))
    suite.set('timestamp', datetime.now().isoformat())

    for result in results:
        name_parts = result['name'].rsplit('.', 1)
        classname = name_parts[0] if len(name_parts) > 1 else result['name']
        testname  = name_parts[1] if len(name_parts) > 1 else result['name']

        tc = ET.SubElement(suite, 'testcase')
        tc.set('classname', classname)
        tc.set('name', testname)
        tc.set('time', str(round(result.get('duration_ms', 0) / 1000, 3)))

        if result['status'] == 'fail':
            failure = ET.SubElement(tc, 'failure')
            failure.set('message', result.get('message', 'Test failed'))
            failure.text = '\n'.join(result.get('traceback', []))
        elif result['status'] == 'error':
            error = ET.SubElement(tc, 'error')
            error.set('message', result.get('message', 'Test error'))
            error.text = '\n'.join(result.get('traceback', []))
        elif result['status'] == 'skip':
            ET.SubElement(tc, 'skipped')

    tree = ET.ElementTree(root)
    ET.indent(tree, space='  ')
    tree.write(output_path, encoding='unicode', xml_declaration=True)


# ─── Main Runner ──────────────────────────────────────────────────────────────

def run_tests(args: argparse.Namespace) -> int:
    """Execute Odoo tests and process results."""

    # Build command
    cmd = build_odoo_command(
        config=args.config,
        database=args.database,
        module=args.module,
        tags=args.tags if args.tags else None,
        class_name=args.test_class,
        method_name=args.test_method,
        install=args.install,
        log_level='debug' if args.show_logs else 'test',
    )

    print(fmt_section(f'Odoo Test Runner - {args.module}'))
    print(fmt_info(f'Config:   {args.config}'))
    print(fmt_info(f'Database: {args.database}'))
    print(fmt_info(f'Module:   {args.module}'))
    if args.tags:
        print(fmt_info(f'Tags:     {args.tags}'))
    if args.test_class:
        print(fmt_info(f'Class:    {args.test_class}'))
    if args.test_method:
        print(fmt_info(f'Method:   {args.test_method}'))
    print()
    print(fmt_info(f'Command: {" ".join(cmd)}'))
    print()

    # Execute
    start_time = time.time()
    log_parser = OdooTestLogParser()

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
        )

        for line in proc.stdout:
            log_parser.feed(line)

            # Real-time output
            line_clean = line.rstrip()
            if args.show_logs:
                print(line_clean)
            else:
                # Only show test results lines
                if any(marker in line for marker in ['[OK]', 'FAIL', 'ERROR', 'SKIP', 'Ran ']):
                    if log_parser.results:
                        last = log_parser.results[-1]
                        if last['status'] == 'pass':
                            print(fmt_pass(last['name']))
                        elif last['status'] == 'fail':
                            print(fmt_fail(last['name']))
                        elif last['status'] == 'error':
                            print(fmt_error(last['name']))
                        elif last['status'] == 'skip':
                            print(fmt_skip(last['name']))

        proc.wait()
        return_code = proc.returncode

    except FileNotFoundError as e:
        print(f"{Color.RED}[ERROR]{Color.RESET} Could not start Odoo: {e}", file=sys.stderr)
        print("Ensure Python and Odoo are properly installed.")
        return 2
    except KeyboardInterrupt:
        proc.terminate()
        print(f"\n{Color.YELLOW}[INTERRUPTED]{Color.RESET} Test run cancelled by user.")
        return 130

    elapsed = time.time() - start_time
    summary = log_parser.get_summary()
    if not summary['duration_s']:
        summary['duration_s'] = round(elapsed, 2)

    # ── Print Summary ─────────────────────────────────────────────────────────
    print(fmt_section('Test Results Summary'))

    status_color = Color.GREEN if summary['success'] else Color.RED
    overall = 'ALL PASSED' if summary['success'] else 'TESTS FAILED'
    print(f"  {status_color}{Color.BOLD}{overall}{Color.RESET}\n")

    print(fmt_summary_line('Total Tests:', str(summary['total_ran'])))
    print(fmt_summary_line('Passed:', str(summary['passed']), Color.GREEN))
    print(fmt_summary_line('Failed:', str(summary['failed']), Color.RED if summary['failed'] else ''))
    print(fmt_summary_line('Errors:', str(summary['errors']), Color.RED if summary['errors'] else ''))
    print(fmt_summary_line('Skipped:', str(summary['skipped']), Color.YELLOW if summary['skipped'] else ''))
    print(fmt_summary_line('Duration:', f"{summary['duration_s']:.2f}s"))

    # Print failure details
    failures = [r for r in log_parser.results if r['status'] in ('fail', 'error')]
    if failures:
        print(f"\n{Color.RED}{Color.BOLD}Failed Tests:{Color.RESET}")
        for f in failures:
            print(f"  {Color.RED}✗{Color.RESET} {f['name']}")
            if f.get('message'):
                print(f"    {Color.DIM}{f['message'][:120]}{Color.RESET}")

    # ── Output formats ────────────────────────────────────────────────────────
    if args.output:
        fmt = (args.output_format or 'junit').lower()
        if fmt == 'junit':
            write_junit_xml(
                log_parser.results, summary,
                args.output,
                suite_name=f'{args.module}-tests',
            )
            print(f"\n{fmt_info(f'JUnit XML written to: {args.output}')}")
        elif fmt == 'json':
            data = {
                'summary': summary,
                'results': log_parser.results,
                'command': cmd,
                'timestamp': datetime.now().isoformat(),
            }
            Path(args.output).write_text(json.dumps(data, indent=2), encoding='utf-8')
            print(f"\n{fmt_info(f'JSON report written to: {args.output}')}")

    print()
    return 0 if summary['success'] else 1


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Run Odoo module tests with colored output and structured reports.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""
        Examples:
          # Run all tests in a module
          python test_runner.py --module my_module --config conf/project17.conf --database project17

          # Run with specific tags
          python test_runner.py --module my_module --config conf/project17.conf --database project17 --tags post_install

          # Run a specific test class
          python test_runner.py --module my_module --config conf/project17.conf --database project17 --test-class TestMyModel

          # Run a specific method
          python test_runner.py --module my_module --config conf/project17.conf --database project17 --test-class TestMyModel --test-method test_create

          # Show all Odoo log output
          python test_runner.py --module my_module --config conf/project17.conf --database project17 --show-logs

          # Generate JUnit XML for Azure DevOps
          python test_runner.py --module my_module --config conf/project17.conf --database project17 --output-format junit --output test_results.xml
        """)
    )
    parser.add_argument('--module', required=True, help='Odoo module technical name')
    parser.add_argument('--config', required=True, help='Path to Odoo config file (e.g., conf/project17.conf)')
    parser.add_argument('--database', required=True, help='Database name for tests')
    parser.add_argument('--tags', help='Test tags to filter (e.g., post_install, standard)')
    parser.add_argument('--test-class', help='Specific test class to run (e.g., TestMyModel)')
    parser.add_argument('--test-method', help='Specific test method to run (requires --test-class)')
    parser.add_argument('--install', action='store_true', help='Use -i (install) instead of -u (update)')
    parser.add_argument('--show-logs', action='store_true', help='Show full Odoo log output during run')
    parser.add_argument('--output', help='Output file path for test report')
    parser.add_argument('--output-format', choices=['junit', 'json'], default='junit',
                        help='Output format: junit (JUnit XML) or json (default: junit)')

    args = parser.parse_args()

    if args.test_method and not args.test_class:
        parser.error("--test-method requires --test-class")

    sys.exit(run_tests(args))


if __name__ == '__main__':
    main()

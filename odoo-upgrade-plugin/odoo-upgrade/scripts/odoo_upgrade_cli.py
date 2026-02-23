#!/usr/bin/env python3
"""
Unified CLI Interface for Odoo Upgrade Tools
Single entry point for all upgrade operations with comprehensive command structure
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Import upgrade modules
try:
    from syntax_validator import SyntaxValidator
    SYNTAX_VALIDATOR_AVAILABLE = True
except ImportError:
    SYNTAX_VALIDATOR_AVAILABLE = False

try:
    from auto_fix_library import AutoFixLibrary
    AUTO_FIX_AVAILABLE = True
except ImportError:
    AUTO_FIX_AVAILABLE = False

try:
    from upgrade_to_odoo19 import Odoo19Upgrader
    UPGRADER_AVAILABLE = True
except ImportError:
    UPGRADER_AVAILABLE = False

try:
    from quick_fix_odoo19 import QuickFixer
    QUICK_FIX_AVAILABLE = True
except ImportError:
    QUICK_FIX_AVAILABLE = False

try:
    from odoo19_precheck import Odoo19PreChecker
    PRECHECK_AVAILABLE = True
except ImportError:
    PRECHECK_AVAILABLE = False


class OdooUpgradeCLI:
    """Unified CLI for Odoo upgrade operations"""

    def __init__(self):
        self.parser = self.create_parser()

    def create_parser(self):
        """Create argument parser with subcommands"""
        parser = argparse.ArgumentParser(
            description='Odoo Upgrade CLI - Comprehensive upgrade toolkit for Odoo modules',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
Examples:
  # Check for compatibility issues
  %(prog)s precheck /path/to/module

  # Validate syntax
  %(prog)s validate /path/to/module --verbose

  # Quick fixes for common issues
  %(prog)s quickfix /path/to/module --dry-run

  # Auto-fix specific issues
  %(prog)s autofix /path/to/module --specific xml_odoo19,js_rpc

  # Full upgrade to Odoo 19
  %(prog)s upgrade /path/to/module --auto-fix

  # Complete workflow
  %(prog)s workflow /path/to/module

For more information on each command, use:
  %(prog)s <command> --help
            '''
        )

        parser.add_argument('--version', action='version', version='Odoo Upgrade CLI v1.0.0')

        # Create subparsers for different commands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Precheck command
        self.add_precheck_parser(subparsers)

        # Validate command
        self.add_validate_parser(subparsers)

        # Quick fix command
        self.add_quickfix_parser(subparsers)

        # Auto-fix command
        self.add_autofix_parser(subparsers)

        # Upgrade command
        self.add_upgrade_parser(subparsers)

        # Workflow command (combined operations)
        self.add_workflow_parser(subparsers)

        # Test command
        self.add_test_parser(subparsers)

        return parser

    def add_precheck_parser(self, subparsers):
        """Add precheck command parser"""
        parser = subparsers.add_parser(
            'precheck',
            help='Check for Odoo 19 compatibility issues before upgrade',
            description='Scan project for potential compatibility issues without making changes'
        )
        parser.add_argument('path', help='Path to Odoo module or project')
        parser.add_argument('--report', help='Save report to file', metavar='FILE')
        parser.add_argument('--critical-only', action='store_true',
                          help='Show only critical issues')

    def add_validate_parser(self, subparsers):
        """Add validate command parser"""
        parser = subparsers.add_parser(
            'validate',
            help='Validate syntax of Python, XML, JavaScript, and SCSS files',
            description='Comprehensive syntax validation for all file types'
        )
        parser.add_argument('path', help='Path to Odoo module or project')
        parser.add_argument('--verbose', action='store_true',
                          help='Show detailed output for each file')
        parser.add_argument('--report', help='Save validation report to file', metavar='FILE')

    def add_quickfix_parser(self, subparsers):
        """Add quickfix command parser"""
        parser = subparsers.add_parser(
            'quickfix',
            help='Apply quick fixes for common Odoo 19 issues',
            description='Fast targeted fixes for known compatibility issues'
        )
        parser.add_argument('path', help='Path to Odoo module or project')
        parser.add_argument('--dry-run', action='store_true',
                          help='Preview changes without modifying files')
        parser.add_argument('--validate', action='store_true',
                          help='Run validation before and after fixes')

    def add_autofix_parser(self, subparsers):
        """Add autofix command parser"""
        parser = subparsers.add_parser(
            'autofix',
            help='Automatically fix detected issues using pattern library',
            description='Pattern-based automatic corrections for various issue types'
        )
        parser.add_argument('path', help='Path to Odoo module or project')
        parser.add_argument('--no-backup', action='store_true',
                          help='Skip creating backup before fixes')
        parser.add_argument('--specific', help='Apply only specific fix types (comma-separated)',
                          metavar='TYPES')
        parser.add_argument('--list-fixes', action='store_true',
                          help='List available fix types')

    def add_upgrade_parser(self, subparsers):
        """Add upgrade command parser"""
        parser = subparsers.add_parser(
            'upgrade',
            help='Full upgrade to Odoo 19 with all transformations',
            description='Comprehensive upgrade including manifests, XML, Python, JS, and SCSS'
        )
        parser.add_argument('path', help='Path to Odoo module or project')
        parser.add_argument('--no-validation', action='store_true',
                          help='Skip syntax validation steps')
        parser.add_argument('--auto-fix', action='store_true',
                          help='Automatically fix detected issues')
        parser.add_argument('--target-version', default='19.0',
                          help='Target Odoo version (default: 19.0)')

    def add_workflow_parser(self, subparsers):
        """Add workflow command parser"""
        parser = subparsers.add_parser(
            'workflow',
            help='Execute complete upgrade workflow (precheck → upgrade → validate)',
            description='Automated workflow combining all upgrade steps with validation'
        )
        parser.add_argument('path', help='Path to Odoo module or project')
        parser.add_argument('--auto-fix', action='store_true',
                          help='Enable automatic fixes throughout workflow')
        parser.add_argument('--skip-precheck', action='store_true',
                          help='Skip initial precheck step')
        parser.add_argument('--interactive', action='store_true',
                          help='Prompt for confirmation at each step')

    def add_test_parser(self, subparsers):
        """Add test command parser"""
        parser = subparsers.add_parser(
            'test',
            help='Run test suite for validation and fix functionality',
            description='Execute unit and integration tests'
        )
        parser.add_argument('--verbose', action='store_true',
                          help='Show detailed test output')

    def check_module_availability(self, required_modules):
        """Check if required modules are available"""
        missing = []
        module_map = {
            'syntax_validator': SYNTAX_VALIDATOR_AVAILABLE,
            'auto_fix': AUTO_FIX_AVAILABLE,
            'upgrader': UPGRADER_AVAILABLE,
            'quick_fix': QUICK_FIX_AVAILABLE,
            'precheck': PRECHECK_AVAILABLE,
        }

        for module in required_modules:
            if not module_map.get(module, False):
                missing.append(module)

        if missing:
            print(f"Error: Required modules not available: {', '.join(missing)}")
            print("\nPlease ensure all upgrade scripts are in the same directory:")
            print("  - syntax_validator.py")
            print("  - auto_fix_library.py")
            print("  - upgrade_to_odoo19.py")
            print("  - quick_fix_odoo19.py")
            print("  - odoo19_precheck.py")
            return False

        return True

    def cmd_precheck(self, args):
        """Execute precheck command"""
        if not self.check_module_availability(['precheck']):
            return 1

        if not os.path.exists(args.path):
            print(f"Error: Path '{args.path}' does not exist")
            return 1

        print("\n" + "=" * 60)
        print("ODOO 19 PRE-UPGRADE CHECK")
        print("=" * 60)

        checker = Odoo19PreChecker(args.path)
        checker.check_xml_files()
        checker.check_python_files()
        checker.check_javascript_files()
        checker.check_scss_files()

        if args.report:
            checker.generate_report(args.report)

        checker.print_summary()
        return 0

    def cmd_validate(self, args):
        """Execute validate command"""
        if not self.check_module_availability(['syntax_validator']):
            return 1

        if not os.path.exists(args.path):
            print(f"Error: Path '{args.path}' does not exist")
            return 1

        validator = SyntaxValidator(args.path, verbose=args.verbose)
        results = validator.validate_all()

        # Generate report
        report_file = args.report if args.report else None
        if not report_file and not results['valid']:
            report_file = os.path.join(args.path, "VALIDATION_REPORT.md")

        if report_file:
            validator.generate_report(report_file)

        return 0 if results['valid'] else 1

    def cmd_quickfix(self, args):
        """Execute quickfix command"""
        if not self.check_module_availability(['quick_fix']):
            return 1

        if not os.path.exists(args.path):
            print(f"Error: Path '{args.path}' does not exist")
            return 1

        fixer = QuickFixer(args.path, dry_run=args.dry_run, validate=args.validate)
        fixer.run()
        return 0

    def cmd_autofix(self, args):
        """Execute autofix command"""
        if not self.check_module_availability(['auto_fix']):
            return 1

        if args.list_fixes:
            print("Available fix types:")
            print("  - python_imports: Fix Python import statements")
            print("  - python_decorators: Fix API decorator issues")
            print("  - python_syntax: Attempt to fix Python syntax errors")
            print("  - xml_comments: Fix malformed XML comments")
            print("  - xml_odoo19: Fix Odoo 19 XML compatibility issues")
            print("  - js_rpc: Migrate RPC service to fetch API")
            print("  - js_modules: Add missing @odoo-module declarations")
            print("  - js_async: Fix async/await patterns")
            print("  - scss_variables: Update SCSS variable names")
            print("  - scss_syntax: Fix SCSS syntax issues")
            return 0

        if not os.path.exists(args.path):
            print(f"Error: Path '{args.path}' does not exist")
            return 1

        fixer = AutoFixLibrary(args.path, backup=not args.no_backup)

        if args.specific:
            fix_types = args.specific.split(',')
            results = fixer.apply_specific_fixes(fix_types)
        else:
            results = fixer.apply_all_fixes()

        # Generate report
        report = fixer.generate_report()
        print(report)

        return 0

    def cmd_upgrade(self, args):
        """Execute upgrade command"""
        if not self.check_module_availability(['upgrader']):
            return 1

        if not os.path.exists(args.path):
            print(f"Error: Path '{args.path}' does not exist")
            return 1

        upgrader = Odoo19Upgrader(
            args.path,
            enable_validation=not args.no_validation,
            auto_fix=args.auto_fix
        )
        upgrader.run()
        return 0

    def cmd_workflow(self, args):
        """Execute complete workflow"""
        print("\n" + "=" * 60)
        print("ODOO 19 UPGRADE WORKFLOW")
        print("=" * 60)
        print(f"Project: {args.path}")
        print(f"Auto-fix: {'Enabled' if args.auto_fix else 'Disabled'}")
        print(f"Interactive: {'Yes' if args.interactive else 'No'}")
        print()

        # Step 1: Precheck
        if not args.skip_precheck:
            print("\n>>> Step 1: Pre-upgrade Check <<<")
            if args.interactive:
                input("Press Enter to continue...")

            if not self.check_module_availability(['precheck']):
                return 1

            checker = Odoo19PreChecker(args.path)
            checker.check_xml_files()
            checker.check_python_files()
            checker.check_javascript_files()
            checker.check_scss_files()
            checker.print_summary()

            if args.interactive:
                response = input("\nContinue with upgrade? (y/n): ")
                if response.lower() != 'y':
                    print("Workflow cancelled.")
                    return 1

        # Step 2: Full Upgrade
        print("\n>>> Step 2: Full Upgrade <<<")
        if args.interactive:
            input("Press Enter to continue...")

        if not self.check_module_availability(['upgrader']):
            return 1

        upgrader = Odoo19Upgrader(
            args.path,
            enable_validation=True,
            auto_fix=args.auto_fix
        )
        upgrader.run()

        # Step 3: Final Validation
        print("\n>>> Step 3: Final Validation <<<")
        if args.interactive:
            input("Press Enter to continue...")

        if not self.check_module_availability(['syntax_validator']):
            return 1

        validator = SyntaxValidator(args.path, verbose=False)
        results = validator.validate_all()

        # Generate final report
        report_file = os.path.join(args.path, f"WORKFLOW_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        validator.generate_report(report_file)

        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETE")
        print("=" * 60)
        print(f"Final report: {report_file}")

        if results['valid']:
            print("✓ All validation checks passed")
            return 0
        else:
            print(f"⚠ {results['stats']['total_errors']} errors require manual fixing")
            return 1

    def cmd_test(self, args):
        """Execute test suite"""
        try:
            from test_syntax_validation import run_tests
        except ImportError:
            print("Error: test_syntax_validation.py not found")
            return 1

        print("\n" + "=" * 60)
        print("RUNNING TEST SUITE")
        print("=" * 60)

        success = run_tests(verbose=args.verbose)
        return 0 if success else 1

    def run(self, argv=None):
        """Run the CLI"""
        args = self.parser.parse_args(argv)

        if not args.command:
            self.parser.print_help()
            return 1

        # Dispatch to command handler
        command_map = {
            'precheck': self.cmd_precheck,
            'validate': self.cmd_validate,
            'quickfix': self.cmd_quickfix,
            'autofix': self.cmd_autofix,
            'upgrade': self.cmd_upgrade,
            'workflow': self.cmd_workflow,
            'test': self.cmd_test,
        }

        handler = command_map.get(args.command)
        if handler:
            try:
                return handler(args)
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user")
                return 130
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
                return 1
        else:
            print(f"Unknown command: {args.command}")
            return 1


def main():
    """Main entry point"""
    cli = OdooUpgradeCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
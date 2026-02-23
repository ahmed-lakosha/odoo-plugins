#!/usr/bin/env python3
"""
Claude Code Plugin Validator (Simple Version)
Validates plugins against the Claude Code Plugin Development Guide requirements
"""

import json
import os
import sys
from pathlib import Path
import re
from typing import Dict, List, Tuple, Optional
import argparse


class PluginValidator:
    """Validates Claude Code plugins for compliance with development guide"""

    def __init__(self, plugin_path: str):
        self.plugin_path = Path(plugin_path)
        self.errors = []
        self.warnings = []
        self.suggestions = []

    def validate(self) -> bool:
        """Run all validation checks"""
        print(f"Validating plugin at: {self.plugin_path}")
        print("=" * 60)

        # Run validation checks
        checks = [
            self.check_plugin_structure,
            self.check_manifest,
            self.check_commands,
            self.check_skills,
            self.check_hooks,
            self.check_documentation,
            self.check_naming_conventions,
        ]

        all_passed = True
        for check in checks:
            if not check():
                all_passed = False

        # Print results
        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)

        if self.errors:
            print(f"\n[ERRORS] ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")

        if self.warnings:
            print(f"\n[WARNINGS] ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")

        if self.suggestions:
            print(f"\n[SUGGESTIONS] ({len(self.suggestions)}):")
            for suggestion in self.suggestions:
                print(f"   - {suggestion}")

        if not self.errors and not self.warnings:
            print("\n[SUCCESS] Plugin passes all validation checks!")

        return len(self.errors) == 0

    def check_plugin_structure(self) -> bool:
        """Check required plugin structure"""
        print("\nChecking plugin structure...")

        # Check for .claude-plugin directory
        claude_plugin_dir = self.plugin_path / ".claude-plugin"
        if not claude_plugin_dir.exists():
            self.errors.append("Missing required .claude-plugin directory")
            return False

        # Check for plugin.json
        manifest_path = claude_plugin_dir / "plugin.json"
        if not manifest_path.exists():
            self.errors.append("Missing required .claude-plugin/plugin.json")
            return False

        print("   [OK] Plugin structure is valid")
        return True

    def check_manifest(self) -> bool:
        """Validate plugin.json manifest"""
        print("\nChecking manifest (plugin.json)...")

        manifest_path = self.plugin_path / ".claude-plugin" / "plugin.json"
        if not manifest_path.exists():
            return False

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in plugin.json: {e}")
            return False

        # Check required fields
        required_fields = ["name", "version", "description"]
        for field in required_fields:
            if field not in manifest:
                self.errors.append(f"Missing required field '{field}' in plugin.json")

        # Validate name format (kebab-case)
        if "name" in manifest:
            name = manifest["name"]
            if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
                self.warnings.append(f"Plugin name '{name}' should use kebab-case")

        # Validate version (semantic versioning)
        if "version" in manifest:
            version = manifest["version"]
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                self.errors.append(f"Version '{version}' must follow semantic versioning (X.Y.Z)")

        # Check author format
        if "author" in manifest:
            author = manifest["author"]
            if isinstance(author, dict) and "name" not in author:
                self.errors.append("Author object must have 'name' field")

        # Check optional fields
        optional_fields = ["homepage", "repository", "license", "keywords"]
        for field in optional_fields:
            if field not in manifest:
                self.suggestions.append(f"Consider adding '{field}' to plugin.json")

        # Check component paths
        components = ["commands", "agents", "skills", "hooks", "scripts"]
        for component in components:
            if component in manifest:
                path = Path(self.plugin_path) / manifest[component]
                if not path.exists():
                    self.warnings.append(f"Referenced {component} path does not exist: {manifest[component]}")

        print("   [OK] Manifest validation complete")
        return len([e for e in self.errors if "plugin.json" in e]) == 0

    def check_commands(self) -> bool:
        """Validate command definitions"""
        print("\nChecking commands...")

        # Look for commands directory
        commands_dirs = list(self.plugin_path.rglob("commands"))
        if not commands_dirs:
            print("   [INFO] No commands directory found")
            return True

        command_count = 0
        for commands_dir in commands_dirs:
            for cmd_file in commands_dir.glob("*.md"):
                command_count += 1
                self._validate_command_file(cmd_file)

        if command_count > 0:
            print(f"   [OK] Validated {command_count} command(s)")
        return True

    def _validate_command_file(self, file_path: Path):
        """Validate individual command file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for frontmatter
        if not content.startswith("---"):
            self.errors.append(f"Command {file_path.name} missing YAML frontmatter")
            return

        # Basic frontmatter validation without yaml module
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            self.errors.append(f"Invalid frontmatter in {file_path.name}")
            return

        # Basic parsing
        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        # Check required frontmatter fields
        required_fields = ["description", "author", "version"]
        for field in required_fields:
            if field not in frontmatter:
                self.warnings.append(f"Command {file_path.name} missing '{field}' in frontmatter")

    def check_skills(self) -> bool:
        """Validate skill definitions"""
        print("\nChecking skills...")

        # Look for SKILL.md files
        skill_files = list(self.plugin_path.rglob("SKILL.md"))
        if not skill_files:
            print("   [INFO] No SKILL.md files found")
            return True

        for skill_file in skill_files:
            self._validate_skill_file(skill_file)

        print(f"   [OK] Validated {len(skill_files)} skill(s)")
        return True

    def _validate_skill_file(self, file_path: Path):
        """Validate individual skill file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for frontmatter
        if not content.startswith("---"):
            self.errors.append(f"Skill {file_path} missing YAML frontmatter")
            return

        # Basic frontmatter validation
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            self.errors.append(f"Invalid frontmatter in {file_path}")
            return

        # Basic parsing
        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line and not line.strip().startswith('#'):
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        # Check required fields for skills
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in frontmatter:
                self.errors.append(f"Skill {file_path.name} missing required '{field}' field")

    def check_hooks(self) -> bool:
        """Validate hooks configuration"""
        print("\nChecking hooks...")

        # Look for hooks.json files
        hooks_files = list(self.plugin_path.rglob("hooks.json"))
        if not hooks_files:
            print("   [INFO] No hooks.json files found")
            self.suggestions.append("Consider adding hooks for automation")
            return True

        for hooks_file in hooks_files:
            self._validate_hooks_file(hooks_file)

        print(f"   [OK] Validated {len(hooks_files)} hooks file(s)")
        return True

    def _validate_hooks_file(self, file_path: Path):
        """Validate hooks.json file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                hooks = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in {file_path}: {e}")
            return

        # Check hook structure
        valid_events = ["PostToolUse", "PreCommit", "PostCommit", "OnError"]
        for event in hooks.keys():
            if event not in valid_events:
                self.warnings.append(f"Unknown hook event '{event}' in {file_path.name}")

    def check_documentation(self) -> bool:
        """Check for documentation files"""
        print("\nChecking documentation...")

        # Check for README.md
        readme_path = self.plugin_path / "README.md"
        if not readme_path.exists():
            self.warnings.append("Missing README.md file")
        else:
            print("   [OK] README.md found")

        # Check for LICENSE
        license_path = self.plugin_path / "LICENSE"
        if not license_path.exists():
            self.suggestions.append("Consider adding a LICENSE file")

        # Check for CHANGELOG
        changelog_path = self.plugin_path / "CHANGELOG.md"
        if not changelog_path.exists():
            self.suggestions.append("Consider adding a CHANGELOG.md file")

        return True

    def check_naming_conventions(self) -> bool:
        """Check naming conventions"""
        print("\nChecking naming conventions...")

        # Check plugin directory name (should be kebab-case)
        plugin_name = self.plugin_path.name
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', plugin_name):
            self.warnings.append(f"Plugin directory name '{plugin_name}' should use kebab-case")

        print("   [OK] Naming convention check complete")
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate Claude Code plugins for compliance"
    )
    parser.add_argument(
        "plugin_path",
        nargs="?",
        default=".",
        help="Path to plugin directory (default: current directory)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )

    args = parser.parse_args()

    # Validate plugin path
    plugin_path = Path(args.plugin_path)
    if not plugin_path.exists():
        print(f"[ERROR] Plugin path does not exist: {plugin_path}")
        sys.exit(1)

    # Run validation
    validator = PluginValidator(plugin_path)
    is_valid = validator.validate()

    # Exit code
    if not is_valid:
        sys.exit(1)
    elif args.strict and validator.warnings:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
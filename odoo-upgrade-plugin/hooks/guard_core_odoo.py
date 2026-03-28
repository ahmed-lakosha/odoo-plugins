#!/usr/bin/env python
"""
PreToolUse hook: Block writes to core Odoo framework files.

Reads tool input JSON from stdin. If the target file is inside a core
Odoo directory, exits with code 2 to block the action. Otherwise exits 0.

Core path patterns are loaded from odoo-upgrade.config.json (configurable).
"""

import json
import re
import sys
import os

# Import shared config loader (same directory)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import load_config


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_input = data.get('tool_input', {})
    file_path = tool_input.get('file_path', '') or tool_input.get('path', '')

    if not file_path:
        sys.exit(0)

    normalized = file_path.replace('\\', '/')

    config = load_config()
    core_patterns = config.get('core_path_patterns', [])

    for pattern in core_patterns:
        try:
            if re.search(pattern, normalized):
                msg = (
                    f"BLOCKED: Cannot modify core Odoo file: {file_path}\n"
                    "Core framework files (odoo/addons/, odoo/*.py) must not be edited.\n"
                    "Use model/view inheritance in projects/ instead."
                )
                print(msg, file=sys.stderr)
                sys.exit(2)
        except re.error:
            continue  # Skip malformed user-provided patterns

    sys.exit(0)


if __name__ == '__main__':
    main()

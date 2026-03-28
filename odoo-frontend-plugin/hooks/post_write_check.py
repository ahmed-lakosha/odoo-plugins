#!/usr/bin/env python
"""PostToolUse hook: prints advisory reminders after Write/Edit operations.

Receives JSON on stdin with tool_input containing file_path and content.
Always exits 0. Outputs reminders to stdout.
"""
import json
import os
import re
import sys

# Bootstrap 4 classes that should be Bootstrap 5 in Odoo 16+
BS4_PATTERN = re.compile(
    r"\b(ml-|mr-|pl-|pr-|text-left|text-right|float-left|float-right"
    r"|font-weight-bold|sr-only)\b"
)

BS4_REPLACEMENTS = (
    "ml-*->ms-*, mr-*->me-*, pl-*->ps-*, pr-*->pe-*, "
    "text-left->text-start, text-right->text-end, "
    "float-left->float-start, float-right->float-end, "
    "font-weight-bold->fw-bold, sr-only->visually-hidden"
)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "") or tool_input.get("new_string", "")

    if not file_path:
        sys.exit(0)

    basename = os.path.basename(file_path).lower()
    ext = os.path.splitext(file_path)[1].lower()
    reminders = []

    # --- SCSS/SASS checks ---
    if ext in (".scss", ".sass"):
        reminders.append(
            "SCSS modified. Regenerate assets: "
            "python -m odoo -d [DB] -u [MODULE] --stop-after-init "
            "or restart with --dev=css"
        )
        if "primary_variables" in basename:
            reminders.append(
                "Primary variables changed. Ensure o-color-1..5 follow semantic meanings: "
                "1=primary brand, 2=secondary/accent, 3=light bg, 4=white/body, 5=dark text."
            )

    # --- JavaScript checks ---
    if ext == ".js" and content:
        if "@odoo-module" not in content:
            reminders.append(
                "JS file should start with /** @odoo-module **/ annotation."
            )
        if "publicWidget" in content and ("Widget.extend" in content or "registry" in content):
            reminders.append(
                "publicWidget detected. Check 'this.editableMode' in start() "
                "for website builder compatibility."
            )

    # --- Theme XML checks ---
    if ext == ".xml" and "theme_" in file_path.replace("\\", "/").lower():
        reminders.append(
            "Theme data modified. Update theme: "
            "python -m odoo -d [DB] -u [theme_module] --stop-after-init"
        )

    # --- Bootstrap 4 class detection ---
    if ext in (".xml", ".html", ".scss") and content:
        if BS4_PATTERN.search(content):
            reminders.append(
                f"Bootstrap 4 classes detected. For Odoo 16+, use Bootstrap 5: {BS4_REPLACEMENTS}"
            )

    if reminders:
        print("\n".join(reminders))

    sys.exit(0)


if __name__ == "__main__":
    main()

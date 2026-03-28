#!/usr/bin/env python
"""PreToolUse hook: blocks Write/Edit of XML files containing inline JavaScript.

Receives JSON on stdin with tool_input containing file_path and content.
Exit 0 = allow, Exit 2 = block (message on stderr).
"""
import json
import re
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "") or tool_input.get("new_string", "")

    if not file_path or not content:
        sys.exit(0)

    # Only check XML files
    if not file_path.lower().endswith(".xml"):
        sys.exit(0)

    # Check for inline <script> tags with non-empty body
    if re.search(r"<script[^>]*>[^<]+</script>", content, re.DOTALL):
        print(
            "Inline JavaScript detected in XML template. "
            "Create a separate .js file in static/src/js/ instead.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
Shared configuration loader for odoo-upgrade plugin hooks.

Loads odoo-upgrade.config.json from (first match wins):
1. $CLAUDE_PROJECT_ROOT/odoo-upgrade.config.json  (user override)
2. $CLAUDE_PLUGIN_ROOT/odoo-upgrade.config.json   (plugin default)
3. Hardcoded fallback (zero-dependency safety net)
"""

import json
import os
import re
from pathlib import Path
from typing import Optional


DEFAULT_CONFIG = {
    "core_path_patterns": [
        r"odoo\d{2}/odoo/addons/",
        r"odoo\d{2}/odoo/[^/]+\.py$",
        r"odoo\d{2}/odoo/tools/",
        r"odoo\d{2}/odoo/modules/",
        r"odoo\d{2}/odoo/cli/",
        r"odoo\d{2}/odoo/service/",
        r"odoo-\d+\.\d+/odoo/addons/",
        r"odoo-\d+\.\d+/odoo/[^/]+\.py$",
        r"odoo-\d+\.\d+/odoo/tools/",
        r"odoo-\d+\.\d+/odoo/modules/",
        r"/odoo/odoo/addons/",
        r"/odoo/addons/[^/]+/(?!projects/)",
    ],
    "target_version_path_patterns": {
        "19": [r"odoo19[/\\]", r"odoo-19", r"[/\\]v19[/\\]", r"19\.0"],
        "18": [r"odoo18[/\\]", r"odoo-18", r"[/\\]v18[/\\]", r"18\.0"],
        "17": [r"odoo17[/\\]", r"odoo-17", r"[/\\]v17[/\\]", r"17\.0"],
        "16": [r"odoo16[/\\]", r"odoo-16", r"[/\\]v16[/\\]", r"16\.0"],
        "15": [r"odoo15[/\\]", r"odoo-15", r"[/\\]v15[/\\]", r"15\.0"],
        "14": [r"odoo14[/\\]", r"odoo-14", r"[/\\]v14[/\\]", r"14\.0"],
    },
    "default_target_version": 19,
}


def load_config() -> dict:
    """Load plugin configuration from file or return defaults."""
    search_paths = []

    project_root = os.environ.get("CLAUDE_PROJECT_ROOT", "")
    if project_root:
        search_paths.append(Path(project_root) / "odoo-upgrade.config.json")

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if plugin_root:
        search_paths.append(Path(plugin_root) / "odoo-upgrade.config.json")

    for config_path in search_paths:
        if config_path.exists():
            try:
                data = json.loads(config_path.read_text(encoding="utf-8"))
                # Merge with defaults so missing keys don't break anything
                merged = {**DEFAULT_CONFIG, **data}
                return merged
            except (json.JSONDecodeError, OSError):
                continue

    return DEFAULT_CONFIG


def detect_target_version(file_path: str, config: dict) -> Optional[int]:
    """
    Detect the Odoo target version from a file path.

    Checks path against target_version_path_patterns in config.
    Returns the version number (e.g. 19) or None if no pattern matches
    and default_target_version is None/not set.
    """
    normalized = file_path.replace("\\", "/")
    patterns = config.get("target_version_path_patterns", {})

    # Check highest version first (most likely during upgrades)
    for ver_str in sorted(patterns.keys(), key=int, reverse=True):
        for pattern in patterns[ver_str]:
            if re.search(pattern, normalized, re.IGNORECASE):
                return int(ver_str)

    default = config.get("default_target_version")
    return int(default) if default is not None else None

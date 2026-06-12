"""Catalog loading helpers for auto-mir."""

from __future__ import annotations

import sys
from pathlib import Path


def load_catalog(catalog_path: Path, workspace_root: Path) -> dict:
    """Load catalog.yaml and return the parsed structure.

    The host CLI depends on YAML parsing, so emit a precise error if PyYAML is
    missing rather than failing later during analysis.
    """
    try:
        import yaml
    except ImportError:
        print(
            "auto-mir requires PyYAML on the host. Install it with: sudo apt install python3-yaml",
            file=sys.stderr,
        )
        raise SystemExit(1)

    with catalog_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)

    return loaded


def summarize_catalog(loaded: dict) -> dict:
    """Return lightweight counts that are useful in evidence and debug output."""
    checks = loaded.get("checks", [])
    section_counts = {}
    for check in checks:
        section = check.get("section", "unknown")
        section_counts[section] = section_counts.get(section, 0) + 1

    return {
        "check_count": len(checks),
        "security_trigger_count": len(loaded.get("security_triggers", [])),
        "sections": section_counts,
    }

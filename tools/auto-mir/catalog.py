"""Catalog loading helpers for auto-mir."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


def load_catalog(catalog_path: Path, workspace_root: Path) -> dict:
    """Load catalog.yaml and attach policy file hashes.

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

    metadata = loaded.setdefault("metadata", {})
    policy_hashes = {}
    for policy_file in metadata.get("policy_files", []):
        rel_path = policy_file.get("path")
        if not rel_path:
            continue

        file_path = workspace_root / rel_path
        if file_path.exists():
            policy_hashes[rel_path] = _sha256_file(file_path)
        else:
            policy_hashes[rel_path] = None

    metadata["policy_hashes"] = policy_hashes
    return loaded


def summarize_catalog(loaded: dict) -> dict:
    """Return lightweight counts that are useful in evidence and debug output."""
    checks = loaded.get("checks", [])
    section_counts = {}
    for check in checks:
        section = check.get("section", "unknown")
        section_counts[section] = section_counts.get(section, 0) + 1

    return {
        "schema_version": loaded.get("metadata", {}).get("schema_version"),
        "check_count": len(checks),
        "security_trigger_count": len(loaded.get("security_triggers", [])),
        "sections": section_counts,
    }


def _sha256_file(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


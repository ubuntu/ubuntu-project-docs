"""Pure shaping helpers over evidence-adapter payloads.

Lives in utils (import-side-effect free) so both the reviewer checks and the
reporter evaluators can share it without import cycles.
"""

from __future__ import annotations


def built_using_entries(deb_metadata: dict) -> list[str]:
    """Every Built-Using and Static-Built-Using entry across built packages.

    Shared by the reviewer checks (ESL-3 toolchain-only acceptance, ESL-10
    Rust vendoring) and the reporter Built-Using surface item; both roles
    therefore read the same shape from the deb-metadata payload.
    """
    entries: set[str] = set()
    for pkg in deb_metadata.get("deb_packages", []):
        entries.update(pkg.get("built_using", []))
        entries.update(pkg.get("static_built_using", []))
    return sorted(entries)

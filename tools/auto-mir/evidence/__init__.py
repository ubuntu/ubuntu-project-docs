"""Evidence collection adapters for auto-mir.

These collectors run inside the provisioned LXD container via lxd_runner.exec_in
and store structured outputs under ctx.evidence[adapter_id].

Host-side adapters (lp-*-api, ubuntu-cve-tracker, autopkgtest-db) do NOT use the
container; they call Launchpad / HTTP APIs directly from the tool host and are safe
to run before or after container operations.
"""

from __future__ import annotations

import logging

# Import adapter implementations from submodules
from evidence.host_adapters import (
    AdapterError,
    collect_autopkgtest,
    collect_lp_bug_api,
    collect_lp_package_api,
    collect_lp_team_membership_api,
    collect_ubuntu_cve_tracker,
)
from evidence.container_adapters import (
    collect_component_mismatches,
    collect_dep_analysis,
    collect_packaging_source,
    collect_sbuild,
)

log = logging.getLogger("auto_mir.evidence")


def collect_from_catalog(ctx) -> None:
    """Collect evidence for all adapters referenced by the catalog."""
    supported = {
        # Host-side (no container needed)
        "lp-bug-api": collect_lp_bug_api,
        "lp-team-membership-api": collect_lp_team_membership_api,
        "lp-package-api": collect_lp_package_api,
        "ubuntu-cve-tracker": collect_ubuntu_cve_tracker,
        "autopkgtest-db": collect_autopkgtest,
        # In-container
        "packaging-source": collect_packaging_source,
        "dep-analysis": collect_dep_analysis,
        "component-mismatches": collect_component_mismatches,
        "sbuild": collect_sbuild,
    }
    adapter_deps: dict[str, list[str]] = {
        "dep-analysis": ["packaging-source"],
        "sbuild": ["packaging-source"],
    }

    checks = ctx.catalog.get("checks", [])
    required: set[str] = set()
    for check in checks:
        for adapter_id in check.get("adapters_required", []):
            required.add(adapter_id)

    ctx.evidence.setdefault("adapters", {})

    ordered_required = _order_adapters(required, adapter_deps)

    for adapter_id in ordered_required:
        collector = supported.get(adapter_id)
        if collector is None:
            ctx.evidence["adapters"][adapter_id] = {
                "status": "pending",
                "message": "Adapter collector not implemented yet",
            }
            continue

        try:
            log.info("Collecting adapter: %s", adapter_id)
            ctx.evidence["adapters"][adapter_id] = collector(ctx)
        except Exception as exc:
            log.warning("Adapter %s failed: %s", adapter_id, exc)
            ctx.evidence["adapters"][adapter_id] = {
                "status": "error",
                "message": str(exc),
            }


def _order_adapters(required: set[str], adapter_deps: dict[str, list[str]]) -> list[str]:
    """Return adapters in dependency-safe order with stable fallback."""
    remaining = set(required)
    ordered: list[str] = []

    while remaining:
        progressed = False
        for adapter_id in sorted(remaining):
            deps = adapter_deps.get(adapter_id, [])
            if all(dep in ordered or dep not in required for dep in deps):
                ordered.append(adapter_id)
                remaining.remove(adapter_id)
                progressed = True
                break

        if not progressed:
            # Break cycles/fallback by appending sorted remainder.
            ordered.extend(sorted(remaining))
            break

    return ordered

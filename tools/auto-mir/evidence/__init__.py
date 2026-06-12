"""Evidence collection adapters for auto-mir.

These collectors run inside the provisioned LXD container via lxd_runner.exec_in
and store structured outputs under ctx.evidence[adapter_id].

Host-side adapters (lp-*-api, ubuntu-cve-tracker, autopkgtest-db) do NOT use the
container; they call Launchpad / HTTP APIs directly from the tool host and are safe
to run before or after container operations.
"""

from __future__ import annotations

import logging

from catalog_enums import AdapterID

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
        AdapterID.LP_BUG_API: collect_lp_bug_api,
        AdapterID.LP_TEAM_MEMBERSHIP_API: collect_lp_team_membership_api,
        AdapterID.LP_PACKAGE_API: collect_lp_package_api,
        AdapterID.UBUNTU_CVE_TRACKER: collect_ubuntu_cve_tracker,
        AdapterID.AUTOPKGTEST_DB: collect_autopkgtest,
        # In-container
        AdapterID.PACKAGING_SOURCE: collect_packaging_source,
        AdapterID.DEP_ANALYSIS: collect_dep_analysis,
        AdapterID.COMPONENT_MISMATCHES: collect_component_mismatches,
        AdapterID.SBUILD: collect_sbuild,
    }
    adapter_deps: dict[str, list[str]] = {
        str(AdapterID.DEP_ANALYSIS): [str(AdapterID.PACKAGING_SOURCE)],
        str(AdapterID.SBUILD): [str(AdapterID.PACKAGING_SOURCE)],
    }

    checks = ctx.catalog.get("checks", [])
    required: set[str] = set()
    for check in checks:
        for adapter_id in check.get("adapters_required", []):
            required.add(adapter_id)

    ctx.evidence.setdefault("adapters", {})

    ordered_required = _order_adapters(required, adapter_deps)

    for adapter_id_str in ordered_required:
        # Convert string to enum for lookup
        try:
            adapter_id = AdapterID(adapter_id_str)
        except ValueError:
            log.warning("Unknown adapter ID in catalog: %s", adapter_id_str)
            ctx.evidence["adapters"][adapter_id_str] = {
                "status": "pending",
                "message": f"Unknown adapter: {adapter_id_str}",
            }
            continue
        
        collector = supported.get(adapter_id)
        if collector is None:
            ctx.evidence["adapters"][adapter_id_str] = {
                "status": "pending",
                "message": "Adapter collector not implemented yet",
            }
            continue

        try:
            log.info("Collecting adapter: %s", adapter_id_str)
            ctx.evidence["adapters"][adapter_id_str] = collector(ctx)
        except Exception as exc:
            log.warning("Adapter %s failed: %s", adapter_id_str, exc)
            ctx.evidence["adapters"][adapter_id_str] = {
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

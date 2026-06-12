"""Evidence collection adapters for auto-mir.

These collectors run inside the provisioned LXD container via lxd_runner.exec_in
and store structured outputs under ctx.evidence[adapter_id].

Host-side adapters (lp-*-api, ubuntu-cve-tracker, autopkgtest-db) do NOT use the
container; they call Launchpad / HTTP APIs directly from the tool host and are safe
to run before or after container operations.
"""

from __future__ import annotations

import logging
import graphlib

from catalog_enums import AdapterID
from evidence.registry import ADAPTER_REGISTRY

# Import adapter implementations from submodules so they register
import evidence.host_adapters
import evidence.container_adapters
import evidence.team_mapping_adapter

log = logging.getLogger("auto_mir.evidence")
from evidence.host_adapters import AdapterError

def collect_from_catalog(ctx) -> None:
    """Collect evidence for all adapters referenced by the catalog."""
    checks = ctx.catalog.get("checks", [])
    required: set[str] = set()
    for check in checks:
        for adapter_id in check.get("adapters_required", []):
            required.add(adapter_id)

    ctx.evidence.setdefault("adapters", {})

    ordered_required = _order_adapters(required)

    # Track missing dependencies to skip downstream adapters
    failed_adapters: set[str] = set()

    for adapter_id_str in ordered_required:
        if adapter_id_str not in ADAPTER_REGISTRY:
            log.warning("Unknown adapter ID in catalog: %s", adapter_id_str)
            ctx.evidence["adapters"][adapter_id_str] = {
                "status": "pending",
                "message": f"Unknown adapter: {adapter_id_str}",
            }
            failed_adapters.add(adapter_id_str)
            continue
        
        collector, deps = ADAPTER_REGISTRY[adapter_id_str]
        
        # Check if deps failed
        failed_deps = [dep for dep in deps if dep in failed_adapters]
        if failed_deps:
            log.warning(
                "Skipping adapter %s due to failed dependencies: %s",
                adapter_id_str,
                ", ".join(failed_deps),
            )
            ctx.evidence["adapters"][adapter_id_str] = {
                "status": "error",
                "message": f"upstream dependency failed: {', '.join(failed_deps)}",
            }
            failed_adapters.add(adapter_id_str)
            continue

        try:
            log.info("Collecting adapter: %s", adapter_id_str)
            ctx.evidence["adapters"][adapter_id_str] = collector(ctx)
            if ctx.evidence["adapters"][adapter_id_str].get("status") == "error":
                 failed_adapters.add(adapter_id_str)
                 log.warning(
                     "Adapter %s returned error status: %s",
                     adapter_id_str,
                     ctx.evidence["adapters"][adapter_id_str].get("message", "unknown"),
                 )
        except Exception as exc:
            log.warning("Adapter %s failed: %s", adapter_id_str, exc)
            ctx.evidence["adapters"][adapter_id_str] = {
                "status": "error",
                "message": str(exc),
            }
            failed_adapters.add(adapter_id_str)
            log.warning(
                "Adapter %s returned error status: %s",
                adapter_id_str,
                ctx.evidence["adapters"][adapter_id_str].get("message", "unknown"),
            )
        except Exception as exc:
            log.warning("Adapter %s failed: %s", adapter_id_str, exc)
            ctx.evidence["adapters"][adapter_id_str] = {
                "status": "error",
                "message": str(exc),
            }
            failed_adapters.add(adapter_id_str)

def _order_adapters(required: set[str], adapter_deps: dict[str, list[str]] | None = None) -> list[str]:
    """Return adapters in dependency-safe order using graphlib."""
    graph = {}
    for adapter_id in required:
        if adapter_deps is not None:
            deps = adapter_deps.get(adapter_id, [])
        elif adapter_id in ADAPTER_REGISTRY:
            _, deps = ADAPTER_REGISTRY[adapter_id]
        else:
            deps = []
        # topological_sorter expects {node: [predecessors]}
        # Only track dependencies that are also in required set to avoid trying to resolve unneeded adapters
        graph[adapter_id] = [d for d in deps if d in required]
            
    sorter = graphlib.TopologicalSorter(graph)
    try:
        return list(sorter.static_order())
    except graphlib.CycleError as e:
        log.error("Cycle detected in adapter dependencies: %s", e)
        # Fallback to sorted list if cycle occurs
        return sorted(list(required))

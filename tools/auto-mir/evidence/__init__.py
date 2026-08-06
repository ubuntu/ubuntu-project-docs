"""Evidence collection adapters for auto-mir.

These collectors run inside the provisioned LXD guest via lxd_runner.exec_in
and store structured outputs under ctx.evidence[adapter_id].

Host-side adapters (lp-*-api, ubuntu-cve-tracker, autopkgtest-db) do NOT use the
LXD guest; they call Launchpad / HTTP APIs directly from the tool host and are safe
to run before or after guest operations.
"""

from __future__ import annotations

import graphlib
import importlib
import logging

from contracts import EvidenceContext
from evidence.host_adapters import AdapterError as AdapterError
from evidence.host_adapters import cleanup_cached_autopkgtest_db
from evidence.registry import ADAPTER_REGISTRY

log = logging.getLogger("auto_mir.evidence")


def _ensure_adapters_registered() -> None:
    """Import adapter modules for their registry side effects."""
    importlib.import_module("evidence.host_adapters")
    importlib.import_module("evidence.guest_adapters")
    importlib.import_module("evidence.team_mapping_adapter")
    importlib.import_module("evidence.lto_disabled_adapter")


def _summarize_result(result: dict) -> str:
    """Return a concise human-readable summary of an adapter result dict."""
    parts = []
    for k, v in result.items():
        if isinstance(v, str):
            if len(v) > 80:
                parts.append(f"{k}=<{len(v)} chars>")
            else:
                parts.append(f"{k}={v!r}")
        elif isinstance(v, (list, dict)):
            parts.append(f"{k}=[{len(v)} items]")
        else:
            parts.append(f"{k}={v!r}")
    return ", ".join(parts)


def collect_from_catalog(ctx: EvidenceContext) -> int:
    """Collect evidence for all adapters referenced by the catalog.

    Returns:
        0 if all adapters succeeded, 1 if any adapter failed.
    """
    _ensure_adapters_registered()

    checks = ctx.catalog.get("checks", ctx.catalog.get("items", []))
    required: set[str] = set()
    optional: set[str] = set()
    for check in checks:
        for adapter_id in check.get("adapters_required", []):
            required.add(adapter_id)
        for adapter_id in check.get("adapters_optional", []):
            optional.add(adapter_id)

    # Optional adapters are collected best-effort: they enrich checks (e.g.
    # git-ubuntu-delta for PRF-1) but their failure must not fail the run or be
    # reported as a hard adapter failure. Anything that is also required stays
    # required.
    optional -= required
    adapter_deps = _catalog_adapter_dependencies(ctx.catalog)
    required = _expand_adapter_dependencies(required, adapter_deps)
    optional = _expand_adapter_dependencies(optional, adapter_deps) - required

    ctx.evidence.setdefault("adapters", {})

    ordered = _order_adapters(required | optional, adapter_deps)

    # Track missing dependencies to skip downstream adapters
    failed_adapters: set[str] = set()
    # Failures of purely-optional adapters are tracked separately so they do
    # not flip the overall return status.
    failed_required: set[str] = set()

    try:
        for adapter_id_str in ordered:
            is_optional = adapter_id_str in optional
            if adapter_id_str not in ADAPTER_REGISTRY:
                log.warning("Unknown adapter ID in catalog: %s", adapter_id_str)
                ctx.evidence["adapters"][adapter_id_str] = {
                    "status": "pending",
                    "message": f"Unknown adapter: {adapter_id_str}",
                }
                failed_adapters.add(adapter_id_str)
                if not is_optional:
                    failed_required.add(adapter_id_str)
                continue

            collector = ADAPTER_REGISTRY[adapter_id_str]
            deps = adapter_deps.get(adapter_id_str, [])

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
                if not is_optional:
                    failed_required.add(adapter_id_str)
                continue

            try:
                suffix = " (optional)" if is_optional else ""
                log.info("Collecting adapter: %s%s", adapter_id_str, suffix)
                ctx.evidence["adapters"][adapter_id_str] = collector(ctx)
                if ctx.collect_only:
                    log.debug(
                        "Adapter %s found: %s",
                        adapter_id_str,
                        _summarize_result(ctx.evidence["adapters"][adapter_id_str]),
                    )
                if ctx.evidence["adapters"][adapter_id_str].get("status") == "error":
                    failed_adapters.add(adapter_id_str)
                    if not is_optional:
                        failed_required.add(adapter_id_str)
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
                if not is_optional:
                    failed_required.add(adapter_id_str)
                log.warning(
                    "Adapter %s returned error status: %s",
                    adapter_id_str,
                    ctx.evidence["adapters"][adapter_id_str].get("message", "unknown"),
                )
    finally:
        # The autopkgtest DB is a large temp file cached on ctx and shared by
        # several adapters; always remove it once collection is done.
        cleanup_cached_autopkgtest_db(ctx)

    return 0 if not failed_required else 1


def _catalog_adapter_dependencies(catalog: dict) -> dict[str, list[str]]:
    """Return the catalog-authoritative adapter dependency graph."""
    graph: dict[str, list[str]] = {}
    for adapter_definition in catalog.get("evidence_adapters", []):
        if not isinstance(adapter_definition, dict) or not adapter_definition.get("id"):
            continue
        dependencies = adapter_definition.get("depends_on", [])
        graph[str(adapter_definition["id"])] = (
            [str(dependency) for dependency in dependencies]
            if isinstance(dependencies, list)
            else []
        )
    return graph


def _expand_adapter_dependencies(
    adapter_ids: set[str], adapter_deps: dict[str, list[str]]
) -> set[str]:
    """Add every transitive dependency needed by the selected adapters."""
    expanded = set(adapter_ids)
    pending = list(adapter_ids)
    while pending:
        adapter_id = pending.pop()
        for dependency in adapter_deps.get(adapter_id, []):
            if dependency not in expanded:
                expanded.add(dependency)
                pending.append(dependency)
    return expanded


def _order_adapters(required: set[str], adapter_deps: dict[str, list[str]]) -> list[str]:
    """Return adapters in dependency-safe order using graphlib."""
    graph = {}
    for adapter_id in required:
        deps = adapter_deps.get(adapter_id, [])
        # topological_sorter expects {node: [predecessors]}.
        # Only keep dependencies that are required in this run.
        graph[adapter_id] = [d for d in deps if d in required]

    sorter = graphlib.TopologicalSorter(graph)
    try:
        return list(sorter.static_order())
    except graphlib.CycleError as e:
        log.error("Cycle detected in adapter dependencies: %s", e)
        # Fallback to sorted list if cycle occurs
        return sorted(list(required))

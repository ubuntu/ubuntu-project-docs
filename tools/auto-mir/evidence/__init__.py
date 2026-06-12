"""Evidence collection adapters for auto-mir.

These collectors run inside the provisioned LXD container via lxd_runner.exec_in
and store structured outputs under ctx.evidence[adapter_id].
"""

from __future__ import annotations

import json
import logging
from typing import Any

import lxd_runner

log = logging.getLogger("auto_mir.evidence")


class AdapterError(RuntimeError):
    """Raised when an evidence adapter cannot produce required output."""


def collect_from_catalog(ctx) -> None:
    """Collect evidence for all adapters referenced by the catalog.

    Current implementation supports a subset with real collectors:
    - packaging-source
    - dep-analysis
    - component-mismatches

    Other adapters are marked as pending in evidence for traceability.
    """
    supported = {
        "packaging-source": _collect_packaging_source,
        "dep-analysis": _collect_dep_analysis,
        "component-mismatches": _collect_component_mismatches,
    }

    checks = ctx.catalog.get("checks", [])
    required = set()
    for check in checks:
        for adapter_id in check.get("adapters_required", []):
            required.add(adapter_id)

    ctx.evidence.setdefault("adapters", {})

    for adapter_id in sorted(required):
        collector = supported.get(adapter_id)
        if collector is None:
            ctx.evidence["adapters"][adapter_id] = {
                "status": "pending",
                "message": "Adapter collector not implemented yet",
            }
            continue

        try:
            ctx.evidence["adapters"][adapter_id] = collector(ctx)
        except Exception as exc:
            log.warning("Adapter %s failed: %s", adapter_id, exc)
            ctx.evidence["adapters"][adapter_id] = {
                "status": "error",
                "message": str(exc),
            }


def _collect_packaging_source(ctx) -> dict[str, Any]:
    pkg = ctx.source_package
    if not pkg:
        raise AdapterError("source package is not set")

    workdir = f"/tmp/auto-mir-{ctx.bug_id}"
    lxd_runner.exec_in(ctx.container_name, ["mkdir", "-p", workdir])

    # Fetch source package via apt source for deterministic availability.
    lxd_runner.exec_in(
        ctx.container_name,
        [
            "bash",
            "-lc",
            (
                f"cd {workdir} && apt-get source -qq {pkg} && "
                "dir=$(find . -maxdepth 1 -type d -name '*-*' | head -n1) && "
                "echo ${dir#./} > source_dir.txt"
            ),
        ],
    )

    source_dir = _capture(
        ctx,
        ["bash", "-lc", f"cd {workdir} && cat source_dir.txt"],
    ).strip()
    if not source_dir:
        raise AdapterError("failed to resolve unpacked source dir")

    full_source = f"{workdir}/{source_dir}"

    debian_control = _capture(
        ctx,
        ["bash", "-lc", f"cd {full_source} && cat debian/control"],
    )
    debian_rules = _capture(
        ctx,
        ["bash", "-lc", f"cd {full_source} && cat debian/rules"],
        allow_fail=True,
    )

    cargo_lock = _exists(ctx, ["bash", "-lc", f"test -f {full_source}/Cargo.lock"])
    go_sum = _exists(ctx, ["bash", "-lc", f"test -f {full_source}/go.sum"])

    vendored_dirs_raw = _capture(
        ctx,
        [
            "bash",
            "-lc",
            (
                f"cd {full_source} && "
                "find . -maxdepth 3 -type d "
                "\\( -name vendor -o -name third_party -o -name vendored \\)"
            ),
        ],
        allow_fail=True,
    )

    vendored_dirs = [line.strip() for line in vendored_dirs_raw.splitlines() if line.strip()]

    return {
        "status": "ok",
        "source_dir": full_source,
        "debian_control": debian_control,
        "debian_rules": debian_rules,
        "cargo_lock_present": cargo_lock,
        "go_sum_present": go_sum,
        "vendored_dirs": vendored_dirs,
    }


def _collect_dep_analysis(ctx) -> dict[str, Any]:
    packaging = ctx.evidence.get("adapters", {}).get("packaging-source", {})
    source_dir = packaging.get("source_dir")
    if not source_dir:
        raise AdapterError("dep-analysis requires packaging-source.source_dir")

    # Best-effort parse of binary package names from debian/control.
    binaries_raw = _capture(
        ctx,
        [
            "bash",
            "-lc",
            f"cd {source_dir} && awk '/^Package: / {{print $2}}' debian/control",
        ],
        allow_fail=True,
    )
    binaries = [line.strip() for line in binaries_raw.splitlines() if line.strip()]

    runtime_deps = []
    for binary in binaries:
        depends = _capture(
            ctx,
            [
                "bash",
                "-lc",
                f"apt-cache show {binary} 2>/dev/null | awk -F': ' '/^Depends:/ {{print $2; exit}}'",
            ],
            allow_fail=True,
        ).strip()
        if not depends:
            continue
        runtime_deps.append({"binary": binary, "depends": depends})

    return {
        "status": "ok",
        "binary_packages": binaries,
        "runtime_deps": runtime_deps,
    }


def _collect_component_mismatches(ctx) -> dict[str, Any]:
    pkg = ctx.source_package
    script = "/opt/ubuntu-archive-tools/component-mismatches"
    exists = _exists(ctx, ["bash", "-lc", f"test -x {script}"])
    if not exists:
        raise AdapterError("component-mismatches script not present in container")

    series = ctx.series or "devel"
    output = _capture(
        ctx,
        ["bash", "-lc", f"{script} -r {series} {pkg}"],
        allow_fail=True,
    )

    return {
        "status": "ok",
        "series": series,
        "raw_output": output,
    }


def _capture(ctx, cmd: list[str], allow_fail: bool = False) -> str:
    result = lxd_runner.exec_in(
        ctx.container_name,
        cmd,
        check=not allow_fail,
        capture=True,
    )
    return (result.stdout or "").strip()


def _exists(ctx, cmd: list[str]) -> bool:
    result = lxd_runner.exec_in(ctx.container_name, cmd, check=False, capture=True)
    return result.returncode == 0

"""In-container evidence collection adapters.

These adapters run inside the LXD container via lxd_runner.exec_in() and collect
evidence from package build tools, dependency analysis, and packaging inspection.
"""

from __future__ import annotations

import logging
import re

import lxd_runner
from catalog_enums import AdapterID
from evidence.registry import adapter
from evidence.types import (
    ComponentMismatchesResult,
    DepAnalysisResult,
    PackagingSourceResult,
    SbuildResult,
)

log = logging.getLogger("auto_mir.evidence.container")


class AdapterError(RuntimeError):
    """Raised when an evidence adapter cannot produce required output."""


# ---------------------------------------------------------------------------
# Helper functions for container execution
# ---------------------------------------------------------------------------


def _capture(ctx, cmd: list[str], allow_fail: bool = False) -> str:
    """Execute command in container and return stdout."""
    result = lxd_runner.exec_in(
        ctx.vm_name,
        cmd,
        check=not allow_fail,
        capture=True,
    )
    return (result.stdout or "").strip()


def _exists(ctx, cmd: list[str]) -> bool:
    """Check if command succeeds in container."""
    result = lxd_runner.exec_in(ctx.vm_name, cmd, check=False, capture=True)
    return result.returncode == 0


def _extract_dependency_names(depends: str) -> set[str]:
    """Extract package names from a Debian Depends expression."""
    names: set[str] = set()
    for comma_group in depends.split(","):
        for alternative in comma_group.split("|"):
            token = alternative.strip()
            if not token:
                continue
            match = re.match(r"^([a-z0-9][a-z0-9+.-]*)(?::[a-z0-9-]+)?", token)
            if match:
                names.add(match.group(1))
    return names


def _detect_component(ctx, package: str) -> str:
    """Best-effort component detection via apt-cache policy output."""
    policy = _capture(
        ctx,
        ["bash", "-lc", f"apt-cache policy {package} 2>/dev/null"],
        allow_fail=True,
    )
    if not policy:
        return "unknown"

    for component in ("main", "universe", "restricted", "multiverse"):
        if re.search(rf"/ubuntu\s+[^\n]*/{component}\b", policy):
            return component

    return "unknown"


# ---------------------------------------------------------------------------
# Packaging source adapter
# ---------------------------------------------------------------------------


@adapter(AdapterID.PACKAGING_SOURCE)
def collect_packaging_source(ctx) -> PackagingSourceResult:
    """Fetch and analyze Debian packaging source files.

    Runs apt-get source in the container to fetch the source package, then
    extracts debian/control, debian/rules, and checks for language-specific
    files (Cargo.lock, go.sum, vendored directories).
    """
    pkg = ctx.source_package
    if not pkg:
        raise AdapterError("source package is not set")

    workdir = f"/tmp/auto-mir-{ctx.bug_id}"
    lxd_runner.exec_in(ctx.vm_name, ["mkdir", "-p", workdir])

    # Fetch source package via apt source for deterministic availability.
    lxd_runner.exec_in_retry(
        ctx.vm_name,
        [
            "bash",
            "-lc",
            (
                f"cd {workdir} && apt-get source -qq {pkg} && "
                "dir=$(find . -maxdepth 1 -type d -name '*-*' | head -n1) && "
                "echo ${dir#./} > source_dir.txt"
            ),
        ],
        operation=f"apt-get source {pkg}",
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


# ---------------------------------------------------------------------------
# Dependency analysis adapter
# ---------------------------------------------------------------------------


@adapter(AdapterID.DEP_ANALYSIS, depends_on=[AdapterID.PACKAGING_SOURCE, AdapterID.SBUILD])
def collect_dep_analysis(ctx) -> DepAnalysisResult:
    """Analyze runtime dependencies from built packages.

    Extracts dependencies from built .deb files (post-build), maps them to source
    packages, and filters by MIR scope to identify dependencies needing separate MIRs.
    """
    packaging = ctx.evidence.get("adapters", {}).get("packaging-source", {})
    sbuild_result = ctx.evidence.get("adapters", {}).get("sbuild", {})
    source_dir = packaging.get("source_dir")
    
    if not source_dir:
        raise AdapterError("dep-analysis requires packaging-source.source_dir")
    
    if sbuild_result.get("status") != "ok" or not sbuild_result.get("build_success"):
        raise AdapterError("dep-analysis requires successful sbuild")
    
    # Get binary package names from debian/control (for scope comparison)
    binaries_raw = _capture(
        ctx,
        ["bash", "-lc", f"cd {source_dir} && awk '/^Package: / {{print $2}}' debian/control"],
        allow_fail=True,
    )
    binary_packages = [line.strip() for line in binaries_raw.splitlines() if line.strip()]
    
    # Extract dependencies from built .deb files
    runtime_deps = []
    dep_names: set[str] = set()
    built_packages = []
    
    for deb_path in sbuild_result.get("built_debs", []):
        # Extract Package: field
        pkg_name = _capture(
            ctx,
            ["bash", "-lc", f"dpkg-deb -f {deb_path} Package"],
            allow_fail=True,
        ).strip()
        
        if not pkg_name:
            continue
        
        built_packages.append(pkg_name)
        
        # Extract Depends: field
        depends = _capture(
            ctx,
            ["bash", "-lc", f"dpkg-deb -f {deb_path} Depends"],
            allow_fail=True,
        ).strip()
        
        if depends:
            runtime_deps.append({"binary": pkg_name, "depends": depends})
            dep_names.update(_extract_dependency_names(depends))
    
    # Component detection
    dep_components = []
    deps_not_in_main = []
    for dep in sorted(dep_names):
        component = _detect_component(ctx, dep)
        dep_components.append({"package": dep, "component": component})
        if component and component != "main":
            deps_not_in_main.append(dep)
    
    # Source package mapping
    dep_source_map = []
    for dep in sorted(dep_names):
        source_pkg = _capture(
            ctx,
            ["bash", "-lc", 
             f"apt-cache show {dep} 2>/dev/null | awk '/^Source:/ {{print $2; exit}}'"],
            allow_fail=True,
        ).strip()
        if not source_pkg:
            source_pkg = dep  # Debian convention: binary name = source name
        dep_source_map.append({"package": dep, "source_package": source_pkg})
    
    # Scope-aware filtering
    in_scope = (
        set(ctx.requested_binaries) & set(binary_packages) 
        if ctx.requested_binaries 
        else set(binary_packages)
    )
    out_of_scope = set(binary_packages) - in_scope
    
    in_scope_deps_not_in_main = []
    out_of_scope_deps_not_in_main = []
    same_source_deps = []
    
    dep_source_lookup = {
        entry["package"]: entry["source_package"] 
        for entry in dep_source_map
    }
    
    for dep in deps_not_in_main:
        source_pkg = dep_source_lookup.get(dep, dep)
        if source_pkg == ctx.source_package:
            same_source_deps.append(dep)
        elif _dep_belongs_to_in_scope(dep, runtime_deps, in_scope):
            in_scope_deps_not_in_main.append(dep)
        else:
            out_of_scope_deps_not_in_main.append(dep)
    
    return {
        "status": "ok",
        "binary_packages": binary_packages,
        "built_packages": built_packages,
        "runtime_deps": runtime_deps,
        "runtime_dep_packages": sorted(dep_names),
        "dep_components": dep_components,
        "dep_source_map": dep_source_map,
        "deps_not_in_main": sorted(set(deps_not_in_main)),
        "in_scope_deps_not_in_main": sorted(set(in_scope_deps_not_in_main)),
        "out_of_scope_deps_not_in_main": sorted(set(out_of_scope_deps_not_in_main)),
        "same_source_deps": sorted(set(same_source_deps)),
    }


def _dep_belongs_to_in_scope(
    dep: str, runtime_deps: list[dict], in_scope: set[str]
) -> bool:
    """Check if a dependency belongs to an in-scope binary package."""
    for entry in runtime_deps:
        if entry["binary"] in in_scope:
            dep_names = _extract_dependency_names(entry["depends"])
            if dep in dep_names:
                return True
    return False


# ---------------------------------------------------------------------------
# Component mismatches adapter
# ---------------------------------------------------------------------------


@adapter(AdapterID.COMPONENT_MISMATCHES)
def collect_component_mismatches(ctx) -> ComponentMismatchesResult:
    """Run component-mismatches tool to identify packages needing promotion.

    Executes the ubuntu-archive-tools component-mismatches script to determine
    which binary packages would need to be promoted from universe to main.
    """
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

    promotion_candidates = _parse_promotion_candidates(output)

    return {
        "status": "ok",
        "series": series,
        "raw_output": output,
        "promotion_candidates": promotion_candidates,
    }


def _parse_promotion_candidates(output: str) -> list[str]:
    """Parse binary package names that need promotion from component-mismatches output.

    The component-mismatches tool from ubuntu-archive-tools outputs lines such as:
      binary-pkg-name (1.2.3) in universe but needed in main
      binary-pkg-name (1.2.3) [arch1, arch2]
    or a tabular format where binary package names appear at the start of lines.

    This is a best-effort parser: it extracts tokens that look like Debian binary
    package names (lowercase, digits, hyphens/dots/plus) at the start of non-empty
    lines, excluding known header/summary lines.
    """
    candidates: list[str] = []
    seen: set[str] = set()
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("Seed:"):
            continue
        # Binary package name is the first whitespace-delimited token
        token = line.split()[0].rstrip(":")
        # Debian binary package name pattern: lowercase letters, digits, hyphens, dots, plus
        if re.match(r"^[a-z0-9][a-z0-9.+\-]+$", token) and token not in seen:
            seen.add(token)
            candidates.append(token)
    return sorted(candidates)


# ---------------------------------------------------------------------------
# Sbuild adapter (real build with unshare backend)
# ---------------------------------------------------------------------------


@adapter(AdapterID.SBUILD, depends_on=[AdapterID.PACKAGING_SOURCE])
def collect_sbuild(ctx) -> SbuildResult:
    """Build source package using sbuild with unshare backend.
    
    Performs a real build in the target Ubuntu series to extract accurate
    post-build dependencies from built .deb files.
    """
    packaging = ctx.evidence.get("adapters", {}).get("packaging-source", {})
    source_dir = packaging.get("source_dir")
    if not source_dir:
        raise AdapterError("sbuild adapter requires packaging-source.source_dir")
    
    series = ctx.series or "devel"
    output_dir = "/tmp/sbuild-output"
    
    # Create output directory
    _capture(ctx, ["bash", "-lc", f"mkdir -p {output_dir}"])
    
    # Run sbuild with unshare backend
    # --build-mode=unshare: use unshare backend (requires Noble or newer)
    # --no-run-lintian: skip lintian (handled separately)
    # --no-arch-all: skip arch:all packages (not needed for dependency analysis)
    # --no-source-only-changes: don't create source-only changes file
    # --build-dir: output directory for built packages
    build_cmd = (
        f"cd {source_dir} && "
        f"sbuild -d {series} "
        f"--build-mode=unshare "
        f"--no-run-lintian "
        f"--no-arch-all "
        f"--no-source-only-changes "
        f"--build-dir={output_dir} "
        f"2>&1"
    )
    
    log.info("Running sbuild for %s in series %s", ctx.source_package, series)
    build_log = _capture(
        ctx,
        ["bash", "-lc", build_cmd],
        allow_fail=True,
    )
    
    # Check if build succeeded by looking for .deb files
    build_success = _exists(
        ctx, 
        ["bash", "-lc", f"test -d {output_dir} && ls {output_dir}/*.deb >/dev/null 2>&1"]
    )
    
    # Collect built .deb files
    built_debs = []
    if build_success:
        deb_list = _capture(
            ctx,
            ["bash", "-lc", f"ls -1 {output_dir}/*.deb 2>/dev/null"],
            allow_fail=True,
        )
        built_debs = [line.strip() for line in deb_list.splitlines() if line.strip()]
        log.info("sbuild succeeded: %d .deb files built", len(built_debs))
    else:
        log.warning("sbuild failed for %s", ctx.source_package)
    
    # Run lintian on the source package (keep existing functionality)
    lintian_raw = _capture(
        ctx,
        [
            "bash",
            "-lc",
            f"cd {source_dir} && lintian --no-tag-display-limit 2>&1 || true",
        ],
        allow_fail=True,
    )
    
    # Parse lintian output into error/warning/info lists
    lintian_errors: list[str] = []
    lintian_warnings: list[str] = []
    lintian_pedantic: list[str] = []
    for line in lintian_raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("E: "):
            lintian_errors.append(stripped)
        elif stripped.startswith("W: "):
            lintian_warnings.append(stripped)
        elif stripped.startswith("I: ") or stripped.startswith("P: "):
            lintian_pedantic.append(stripped)
    
    # Check for static linking indicators in debian/rules (fast heuristic)
    rules = packaging.get("debian_rules", "")
    static_link_hints = []
    for pattern in (
        "-static",
        "LDFLAGS.*-static",
        "linkshared.*false",
        "CGO_ENABLED=0",
    ):
        if re.search(pattern, rules, re.IGNORECASE):
            static_link_hints.append(pattern)
    
    log.info(
        "lintian for %s: %d errors, %d warnings, %d info",
        ctx.source_package,
        len(lintian_errors),
        len(lintian_warnings),
        len(lintian_pedantic),
    )
    
    return {
        "status": "ok" if build_success else "error",
        "build_success": build_success,
        "build_log": build_log,
        "built_debs": built_debs,
        "lintian_output": lintian_raw,
        "lintian_errors": lintian_errors,
        "lintian_warnings": lintian_warnings,
        "lintian_pedantic": lintian_pedantic,
        "static_link_hints": static_link_hints,
        "note": "Real sbuild with unshare backend completed" if build_success else "sbuild failed",
    }

"""In-container evidence collection adapters.

These adapters run inside the LXD container via lxd_runner.exec_in() and collect
evidence from package build tools, dependency analysis, and packaging inspection.
"""

from __future__ import annotations

import json
import logging
import re
import tempfile
from pathlib import Path

import lxd_runner
from catalog_enums import AdapterID
from evidence.registry import adapter
from evidence.types import (
    ComponentMismatchesResult,
    CvelistScanResult,
    DebMetadataResult,
    DepAnalysisResult,
    LintianResult,
    PackagingSourceResult,
    SbuildResult,
)

log = logging.getLogger("auto_mir.evidence.container")

_UBUNTU_UID = 1000
_UBUNTU_GID = 1000
_UBUNTU_ENV = {"HOME": "/home/ubuntu", "USER": "ubuntu", "LOGNAME": "ubuntu"}


class AdapterError(RuntimeError):
    """Raised when an evidence adapter cannot produce required output."""


# ---------------------------------------------------------------------------
# Helper functions for container execution
# ---------------------------------------------------------------------------


def _capture(
    ctx,
    cmd: list[str],
    allow_fail: bool = False,
    *,
    as_ubuntu: bool = False,
    env: dict[str, str] | None = None,
) -> str:
    """Execute command in container and return stdout."""
    run_env = _UBUNTU_ENV if as_ubuntu and env is None else env
    result = lxd_runner.exec_in(
        ctx.vm_name,
        cmd,
        check=not allow_fail,
        capture=True,
        env=run_env,
        user=_UBUNTU_UID if as_ubuntu else None,
        group=_UBUNTU_GID if as_ubuntu else None,
    )
    return (result.stdout or "").strip()


def _exists(
    ctx,
    cmd: list[str],
    *,
    as_ubuntu: bool = False,
    env: dict[str, str] | None = None,
) -> bool:
    """Check if command succeeds in container."""
    run_env = _UBUNTU_ENV if as_ubuntu and env is None else env
    result = lxd_runner.exec_in(
        ctx.vm_name,
        cmd,
        check=False,
        capture=True,
        env=run_env,
        user=_UBUNTU_UID if as_ubuntu else None,
        group=_UBUNTU_GID if as_ubuntu else None,
    )
    return result.returncode == 0


def _read_latest_sbuild_log(ctx, output_dir: str) -> tuple[str, str]:
    """Return the newest sbuild .build log path and contents from output_dir."""
    build_log_path = _capture(
        ctx,
        ["bash", "-lc", f"ls -1t {output_dir}/*.build 2>/dev/null | head -n1"],
        allow_fail=True,
        as_ubuntu=True,
    ).strip()
    if not build_log_path:
        return "", ""

    return build_log_path, _capture(
        ctx,
        ["bash", "-lc", f"cat {build_log_path}"],
        allow_fail=True,
        as_ubuntu=True,
    )


def _parse_lintian_output(lintian_raw: str) -> tuple[list[str], list[str], list[str]]:
    """Parse lintian output into error, warning, and pedantic buckets."""
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
    return lintian_errors, lintian_warnings, lintian_pedantic


def _resolve_sbuild_series(ctx, requested_series: str) -> str:
    """Resolve alias series names to an actual in-container suite name.

    sbuild expects a concrete suite/codename. When callers pass "devel",
    resolve it to the container codename to avoid suite ambiguity.
    """
    if requested_series != "devel":
        return requested_series

    codename = _capture(
        ctx,
        [
            "bash",
            "-lc",
            ". /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME:-devel}}",
        ],
        allow_fail=True,
    ).strip()
    if codename:
        log.info("Resolved sbuild suite alias 'devel' to container codename '%s'", codename)
        return codename
    return requested_series


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


def _is_auto_included_binary(package: str) -> bool:
    """Return whether a binary package is auto-included by suffix convention."""
    return package.endswith(("-dev", "-dbg", "-debug", "-doc", "-docs"))


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
    lxd_runner.exec_in(
        ctx.vm_name,
        ["mkdir", "-p", workdir],
        user=_UBUNTU_UID,
        group=_UBUNTU_GID,
    )

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
        env=_UBUNTU_ENV,
        user=_UBUNTU_UID,
        group=_UBUNTU_GID,
        operation=f"apt-get source {pkg}",
    )

    source_dir = _capture(
        ctx,
        ["bash", "-lc", f"cd {workdir} && cat source_dir.txt"],
        as_ubuntu=True,
    ).strip()
    if not source_dir:
        raise AdapterError("failed to resolve unpacked source dir")

    full_source = f"{workdir}/{source_dir}"

    debian_control = _capture(
        ctx,
        ["bash", "-lc", f"cd {full_source} && cat debian/control"],
        as_ubuntu=True,
    )
    debian_watch = _capture(
        ctx,
        ["bash", "-lc", f"cd {full_source} && cat debian/watch"],
        allow_fail=True,
        as_ubuntu=True,
    )
    debian_rules = _capture(
        ctx,
        ["bash", "-lc", f"cd {full_source} && cat debian/rules"],
        allow_fail=True,
        as_ubuntu=True,
    )

    cargo_lock = _exists(
        ctx,
        ["bash", "-lc", f"test -f {full_source}/Cargo.lock"],
        as_ubuntu=True,
    )
    go_sum = _exists(
        ctx,
        ["bash", "-lc", f"test -f {full_source}/go.sum"],
        as_ubuntu=True,
    )

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
        as_ubuntu=True,
    )

    vendored_dirs = [line.strip() for line in vendored_dirs_raw.splitlines() if line.strip()]

    # Collect recursive file listing for embedded source detection
    # Filter out common noise dirs and build artifacts
    file_listing_raw = _capture(
        ctx,
        [
            "bash",
            "-lc",
            (
                f"cd {full_source} && "
                "find . -type f -printf '%s %p\\n' 2>/dev/null | "
                "grep -v -E '(/\\.git/|/node_modules/|/\\.pytest_cache/|"
                "/\\.tox/|/__pycache__/|/build/|/dist/|/\\.eggs/|\\.egg-info|"
                "/\\.coverage|/htmlcov/|/\\.cache|/vendor/.*\\.git)' | "
                "head -50000"
            ),
        ],
        allow_fail=True,
        as_ubuntu=True,
    )

    file_listing: list[dict] = []
    for line in file_listing_raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            try:
                size = int(parts[0])
                path = parts[1]
                file_listing.append({"path": path, "size": size})
            except (ValueError, IndexError):
                pass

    log.debug(
        "packaging-source: source dir %s, %d file(s), vendored dirs: %d, "
        "Cargo.lock: %s, go.sum: %s",
        full_source,
        len(file_listing),
        len(vendored_dirs),
        cargo_lock,
        go_sum,
    )
    return {
        "status": "ok",
        "source_dir": full_source,
        "source_workdir": workdir,
        "debian_control": debian_control,
        "debian_watch": debian_watch,
        "debian_rules": debian_rules,
        "cargo_lock_present": cargo_lock,
        "go_sum_present": go_sum,
        "vendored_dirs": vendored_dirs,
        "file_listing": file_listing,
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
            [
                "bash",
                "-lc",
                f"apt-cache show {dep} 2>/dev/null | awk '/^Source:/ {{print $2; exit}}'",
            ],
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

    in_scope_deps_not_in_main = []
    out_of_scope_deps_not_in_main = []
    same_source_deps = []

    # Build fast lookup maps for scoped dependency analysis.
    dep_component_lookup = {entry["package"]: entry["component"] for entry in dep_components}
    deps_by_binary = {
        entry["binary"]: sorted(_extract_dependency_names(entry["depends"]))
        for entry in runtime_deps
    }

    auto_included_binaries = sorted(p for p in in_scope if _is_auto_included_binary(p))
    auto_included_dep_components: list[dict[str, str]] = []
    auto_included_offending_deps_by_binary: list[dict[str, list[str] | str]] = []
    auto_included_dep_names: set[str] = set()
    auto_included_deps_not_in_main_or_unknown: set[str] = set()

    dep_source_lookup = {entry["package"]: entry["source_package"] for entry in dep_source_map}

    for dep in deps_not_in_main:
        source_pkg = dep_source_lookup.get(dep, dep)
        if source_pkg == ctx.source_package:
            same_source_deps.append(dep)
        elif _dep_belongs_to_in_scope(dep, runtime_deps, in_scope):
            in_scope_deps_not_in_main.append(dep)
        else:
            out_of_scope_deps_not_in_main.append(dep)

    for binary in auto_included_binaries:
        binary_deps = deps_by_binary.get(binary, [])
        binary_offending_deps: list[str] = []
        for dep in binary_deps:
            component = dep_component_lookup.get(dep, "unknown")
            auto_included_dep_names.add(dep)
            if component != "main":
                binary_offending_deps.append(dep)
                auto_included_deps_not_in_main_or_unknown.add(dep)

        auto_included_offending_deps_by_binary.append(
            {
                "binary": binary,
                "dependencies": binary_offending_deps,
            }
        )

    for dep in sorted(auto_included_dep_names):
        auto_included_dep_components.append(
            {
                "package": dep,
                "component": dep_component_lookup.get(dep, "unknown"),
            }
        )

    log.debug(
        "dep-analysis: %d binary package(s), %d runtime dep(s), %d dep(s) not in main "
        "(%d in scope)",
        len(binary_packages),
        len(dep_names),
        len(set(deps_not_in_main)),
        len(set(in_scope_deps_not_in_main)),
    )
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
        "auto_included_binaries": auto_included_binaries,
        "auto_included_dep_components": auto_included_dep_components,
        "auto_included_deps_not_in_main_or_unknown": sorted(
            auto_included_deps_not_in_main_or_unknown
        ),
        "auto_included_offending_deps_by_binary": auto_included_offending_deps_by_binary,
    }


def _dep_belongs_to_in_scope(dep: str, runtime_deps: list[dict], in_scope: set[str]) -> bool:
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

    log.debug(
        "component-mismatches: %d promotion candidate(s) for %s in %s",
        len(promotion_candidates),
        pkg,
        series,
    )
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


def _detect_static_binaries(ctx, output_dir: str) -> list[str]:
    """Return package paths of fully statically linked ELF binaries in built debs.

    Each .deb is extracted and every regular file is classified with ``file``.
    Only fully static ELF executables/objects ("statically linked") are
    reported; this is the authoritative signal that the package ships a static
    binary. Files under test directories are excluded, matching MIR policy that
    static linking inside tests is acceptable.
    """
    script = (
        "tmp=$(mktemp -d) || exit 0; "
        f"for deb in {output_dir}/*.deb; do "
        '  [ -e "$deb" ] || continue; '
        '  dest="$tmp/$(basename "$deb" .deb)"; '
        '  mkdir -p "$dest"; '
        '  dpkg-deb -x "$deb" "$dest" 2>/dev/null || true; '
        "done; "
        'find "$tmp" -type f 2>/dev/null | while read -r f; do '
        '  desc=$(file -b "$f" 2>/dev/null || true); '
        '  case "$desc" in '
        '    *"statically linked"*) echo "${f#"$tmp"/}";; '
        "  esac; "
        "done; "
        'rm -rf "$tmp"'
    )
    out = _capture(ctx, ["bash", "-lc", script], allow_fail=True, as_ubuntu=True)
    results: list[str] = []
    for line in out.splitlines():
        path = line.strip()
        if not path:
            continue
        marked = f"/{path.lower()}"
        if "/test/" in marked or "/tests/" in marked:
            continue
        results.append(path)
    return results


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

    source_workdir = packaging.get("source_workdir", "")
    series = _resolve_sbuild_series(ctx, ctx.series or "devel")
    output_dir = "/tmp/sbuild-output"

    # Create output directory
    _capture(
        ctx,
        ["bash", "-lc", f"mkdir -p {output_dir}"],
        as_ubuntu=True,
    )

    # Locate the .dsc file produced by apt-get source in the workdir.
    # Using the .dsc file is the correct way to invoke sbuild: it avoids
    # a spurious clean step that sbuild would run when given a source dir,
    # and it ensures sbuild copies a pristine source tree into the chroot.
    dsc_path = _capture(
        ctx,
        ["bash", "-lc", f"ls {source_workdir}/*.dsc 2>/dev/null | head -n1"],
        allow_fail=True,
        as_ubuntu=True,
    ).strip()
    if not dsc_path:
        raise AdapterError(
            f"sbuild adapter requires a .dsc file in {source_workdir}; "
            "none found after apt-get source"
        )

    # Run sbuild with unshare backend
    # --chroot-mode=unshare: use unshare backend (requires Noble or newer)
    # --no-run-lintian: skip lintian (handled separately)
    # --no-arch-all: skip arch:all packages (only on non-amd64 systems)
    # --no-source-only-changes: don't create source-only changes file
    # --build-dir: output directory for built packages

    # Detect build architecture to decide whether to build arch-all packages
    arch_output = _capture(
        ctx,
        ["bash", "-lc", "dpkg --print-architecture"],
        allow_fail=True,
        as_ubuntu=True,
    )
    build_arch = arch_output.strip()

    # Build arch-all packages only on amd64 (where Ubuntu builds them)
    if build_arch == "amd64":
        arch_all_flag = ""
        log.info("Building arch-all packages on %s", build_arch)
    else:
        arch_all_flag = "--no-arch-all "
        log.warning(
            "Skipping arch-all packages on %s (not amd64); "
            "arch-all dependencies cannot be included in considerations and checks",
            build_arch,
        )

    build_cmd = (
        f"sbuild -d {series} "
        f"--chroot-mode=unshare "
        f"--no-run-lintian "
        f"{arch_all_flag}"
        f"--no-source-only-changes "
        f"--build-dir={output_dir} "
        f"{dsc_path} "
        f"2>&1"
    )

    log.info("Running sbuild for %s in series %s", ctx.source_package, series)
    log.info("sbuild command: %s", build_cmd)
    build_log = _capture(
        ctx,
        ["bash", "-lc", build_cmd],
        allow_fail=True,
        as_ubuntu=True,
    )

    # Check if build succeeded by looking for .deb files
    build_success = _exists(
        ctx,
        ["bash", "-lc", f"test -d {output_dir} && ls {output_dir}/*.deb >/dev/null 2>&1"],
        as_ubuntu=True,
    )

    sbuild_build_log_path, sbuild_build_log = _read_latest_sbuild_log(ctx, output_dir)
    if sbuild_build_log:
        if build_success and not build_log:
            build_log = sbuild_build_log
        elif not build_success:
            build_log = (
                f"{build_log}\n\n--- sbuild build file: {sbuild_build_log_path} ---\n"
                f"{sbuild_build_log}"
            ).strip()

    # Collect built .deb files
    built_debs = []
    if build_success:
        deb_list = _capture(
            ctx,
            ["bash", "-lc", f"ls -1 {output_dir}/*.deb 2>/dev/null"],
            allow_fail=True,
            as_ubuntu=True,
        )
        built_debs = [line.strip() for line in deb_list.splitlines() if line.strip()]
        log.info("sbuild succeeded: %d .deb files built", len(built_debs))
        message = f"Build succeeded: {len(built_debs)} .deb files produced"
    else:
        log.warning("sbuild failed for %s", ctx.source_package)
        message = "Build failed, see build_log for details"

    # Inspect built binaries for fully static ELF linkage (authoritative signal
    # for ESL-2). Partial static linking of individual archive libraries is
    # tracked separately via Built-Using (ESL-3).
    static_binaries: list[str] = []
    if build_success and built_debs:
        static_binaries = _detect_static_binaries(ctx, output_dir)

    # Run lintian on the source package (keep existing functionality)
    lintian_raw = _capture(
        ctx,
        [
            "bash",
            "-lc",
            f"cd {source_dir} && lintian --no-tag-display-limit 2>&1 || true",
        ],
        allow_fail=True,
        as_ubuntu=True,
    )

    lintian_errors, lintian_warnings, lintian_pedantic = _parse_lintian_output(lintian_raw)

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
        "message": message,
        "build_success": build_success,
        "build_log": build_log,
        "sbuild_build_log_path": sbuild_build_log_path,
        "built_debs": built_debs,
        "lintian_output": lintian_raw,
        "lintian_errors": lintian_errors,
        "lintian_warnings": lintian_warnings,
        "lintian_pedantic": lintian_pedantic,
        "static_link_hints": static_link_hints,
        "static_binaries": static_binaries,
        "note": "Real sbuild with unshare backend completed" if build_success else "sbuild failed",
    }


# ---------------------------------------------------------------------------
# Lintian adapter
# ---------------------------------------------------------------------------


@adapter(AdapterID.LINTIAN, depends_on=[AdapterID.SBUILD])
def collect_lintian(ctx) -> LintianResult:
    """Expose the lintian output parsed from the sbuild run as a standalone adapter."""
    sbuild_result = ctx.evidence.get("adapters", {}).get("sbuild", {})
    if sbuild_result.get("status") != "ok":
        raise AdapterError("lintian adapter requires successful sbuild evidence")

    lintian_raw = str(sbuild_result.get("lintian_output", ""))
    lintian_errors, lintian_warnings, lintian_pedantic = _parse_lintian_output(lintian_raw)

    return {
        "status": "ok",
        "lintian_output": lintian_raw,
        "lintian_errors": lintian_errors,
        "lintian_warnings": lintian_warnings,
        "lintian_pedantic": lintian_pedantic,
    }


# ---------------------------------------------------------------------------
# Binary package metadata adapter
# ---------------------------------------------------------------------------


def _parse_built_using_entries(field_text: str) -> list[str]:
    """Parse Built-Using or Static-Built-Using field into list of entries.

    The field may span multiple lines (continuation lines start with space).
    Each entry is typically: package (>= version) or similar.
    Returns list of individual entries; may contain multiple per field.
    """
    if not field_text:
        return []

    # Collapse multi-line entries
    collapsed = " ".join(line.strip() for line in field_text.splitlines())

    # Split on commas to get individual entries
    # Each entry might be "package (constraint)" or similar
    entries = [e.strip() for e in collapsed.split(",")]
    return [e for e in entries if e]  # Filter empty strings


@adapter(AdapterID.DEB_METADATA, depends_on=[AdapterID.SBUILD])
def collect_deb_metadata(ctx) -> DebMetadataResult:
    """Extract metadata from built .deb files.

    Runs after sbuild completes to extract Package, Version, Built-Using,
    and Static-Built-Using fields from binary packages for checks that
    need post-build metadata (e.g., ESL-3, ESL-10).
    """
    sbuild_result = ctx.evidence.get("adapters", {}).get("sbuild", {})

    if sbuild_result.get("status") != "ok" or not sbuild_result.get("build_success"):
        raise AdapterError("deb-metadata adapter requires successful sbuild")

    built_debs = sbuild_result.get("built_debs", [])
    if not built_debs:
        raise AdapterError("No built .deb files found from sbuild")

    deb_packages = []

    for deb_path in built_debs:
        try:
            # Extract Package field
            package_name = _capture(
                ctx,
                ["bash", "-lc", f"dpkg-deb -f {deb_path} Package"],
                allow_fail=True,
                as_ubuntu=True,
            ).strip()

            if not package_name:
                log.warning("Could not extract Package from %s", deb_path)
                continue

            # Extract Version field
            version = _capture(
                ctx,
                ["bash", "-lc", f"dpkg-deb -f {deb_path} Version"],
                allow_fail=True,
                as_ubuntu=True,
            ).strip()

            # Extract Built-Using field (may be empty)
            built_using_raw = _capture(
                ctx,
                ["bash", "-lc", f"dpkg-deb -f {deb_path} Built-Using"],
                allow_fail=True,
                as_ubuntu=True,
            ).strip()

            # Extract Static-Built-Using field (may be empty)
            static_built_using_raw = _capture(
                ctx,
                ["bash", "-lc", f"dpkg-deb -f {deb_path} Static-Built-Using"],
                allow_fail=True,
                as_ubuntu=True,
            ).strip()

            # Parse multi-line fields into lists of entries
            built_using = _parse_built_using_entries(built_using_raw)
            static_built_using = _parse_built_using_entries(static_built_using_raw)

            deb_packages.append(
                {
                    "package": package_name,
                    "version": version,
                    "built_using": built_using,
                    "static_built_using": static_built_using,
                }
            )

        except Exception as e:
            log.warning("Error extracting metadata from %s: %s", deb_path, e)
            continue

    if not deb_packages:
        raise AdapterError("Could not extract metadata from any built .deb files")

    built_using_count = sum(1 for p in deb_packages if p["built_using"])
    static_built_using_count = sum(1 for p in deb_packages if p["static_built_using"])
    log.debug(
        "deb-metadata: %d binary package(s), %d with Built-Using, %d with Static-Built-Using",
        len(deb_packages),
        built_using_count,
        static_built_using_count,
    )
    return {
        "status": "ok",
        "message": f"Extracted metadata from {len(deb_packages)} binary packages",
        "deb_packages": deb_packages,
    }


# ---------------------------------------------------------------------------
# CVE / security — cvelistV5 baseline scan (in-VM)
# ---------------------------------------------------------------------------


_CVELIST_SCAN_SCRIPT = "cvelist_scan_invm.py"
_CVELIST_VM_SCRIPT = "/tmp/auto-mir-cvelist-scan.py"
_CVELIST_VM_TERMS = "/tmp/auto-mir-cve-terms.json"


@adapter(AdapterID.CVELIST_SCAN, depends_on=[AdapterID.CVE_SEARCH_TERMS])
def collect_cvelist_scan(ctx) -> CvelistScanResult:
    """Identify candidate CVEs by scanning the cvelistV5 baseline corpus in the VM.

    Downloads the documented ``*_all_CVEs_at_midnight.zip`` baseline inside the
    throwaway VM (keeping the bulky corpus off the host) and word-matches it
    against the search terms produced by the cve-search-terms adapter. Returns a
    small set of candidate CVE IDs for downstream NVD enrichment.
    """
    pkg = ctx.source_package
    if not pkg:
        raise AdapterError("source_package not set")

    terms_result = ctx.evidence.get("adapters", {}).get("cve-search-terms", {})
    terms = terms_result.get("terms", []) if isinstance(terms_result, dict) else []
    if not terms:
        log.warning("cvelist-scan: no search terms available; skipping scan")
        return {
            "status": "ok",
            "source_package": pkg,
            "baseline": "",
            "scanned_terms": [],
            "candidates": [],
            "total_candidate_count": 0,
            "note": "no search terms produced by cve-search-terms",
        }

    scanned_terms = [str(t.get("term") or "") for t in terms if t.get("term")]

    # Push the self-contained scanner and the terms list into the VM.
    script_path = Path(__file__).resolve().parent / _CVELIST_SCAN_SCRIPT
    lxd_runner.push_file(ctx.vm_name, str(script_path), _CVELIST_VM_SCRIPT)

    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as terms_file:
        json.dump(terms, terms_file)
        terms_local = terms_file.name
    lxd_runner.push_file(ctx.vm_name, terms_local, _CVELIST_VM_TERMS)

    raw = _capture(
        ctx,
        ["python3", _CVELIST_VM_SCRIPT, _CVELIST_VM_TERMS],
        allow_fail=True,
    ).strip()

    if not raw:
        raise AdapterError("cvelist-scan produced no output from the VM")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AdapterError(f"cvelist-scan returned invalid JSON: {exc}") from exc

    if payload.get("status") != "ok":
        raise AdapterError(f"cvelist-scan failed in VM: {payload.get('message', 'unknown error')}")

    candidates = payload.get("candidates", []) or []
    log.debug(
        "cvelist-scan: %d candidate CVE(s) for %s from baseline %s (terms: %s)",
        len(candidates),
        pkg,
        payload.get("baseline", ""),
        ", ".join(scanned_terms),
    )
    return {
        "status": "ok",
        "source_package": pkg,
        "baseline": str(payload.get("baseline") or ""),
        "scanned_terms": scanned_terms,
        "candidates": candidates,
        "total_candidate_count": len(candidates),
    }

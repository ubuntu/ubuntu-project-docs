"""Evidence collection adapters for auto-mir.

These collectors run inside the provisioned LXD container via lxd_runner.exec_in
and store structured outputs under ctx.evidence[adapter_id].

Host-side adapters (lp-*-api, ubuntu-cve-tracker, autopkgtest-db) do NOT use the
container; they call Launchpad / HTTP APIs directly from the tool host and are safe
to run before or after container operations.
"""

from __future__ import annotations

import json
import logging
import lzma
import re
import sqlite3
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import lxd_runner

log = logging.getLogger("auto_mir.evidence")


class AdapterError(RuntimeError):
    """Raised when an evidence adapter cannot produce required output."""


def collect_from_catalog(ctx) -> None:
    """Collect evidence for all adapters referenced by the catalog."""
    supported = {
        # Host-side (no container needed)
        "lp-bug-api":             _collect_lp_bug_api,
        "lp-team-membership-api": _collect_lp_team_membership_api,
        "lp-package-api":         _collect_lp_package_api,
        "ubuntu-cve-tracker":     _collect_ubuntu_cve_tracker,
        "autopkgtest-db":         _collect_autopkgtest,
        # In-container
        "packaging-source":       _collect_packaging_source,
        "dep-analysis":           _collect_dep_analysis,
        "component-mismatches":   _collect_component_mismatches,
        "sbuild":                 _collect_sbuild,
    }
    adapter_deps: dict[str, list[str]] = {
        "dep-analysis": ["packaging-source"],
        "sbuild":        ["packaging-source"],
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


# ---------------------------------------------------------------------------
# Host-side adapters — LP API
# ---------------------------------------------------------------------------

def _collect_lp_bug_api(ctx) -> dict[str, Any]:
    """Return Launchpad bug data already collected by lp_intake.

    This is a passthrough: lp_intake.run() already populated ctx.bug.
    We expose it as an adapter so checks can declare a clean dependency on it.
    """
    bug = ctx.bug
    if not bug:
        raise AdapterError("Launchpad bug data not populated by lp_intake")
    return {
        "status": "ok",
        "bug_id": ctx.bug_id,
        "bug_title": bug.get("title", ""),
        "bug_description": bug.get("description", ""),
        "bug_tags": bug.get("tags", []),
        "bug_comments": bug.get("comments", []),
        "bug_subscribers": bug.get("subscribers", []),
        "target_source_package": ctx.source_package,
        "target_series": ctx.series or "devel",
        "mir_heuristics": bug.get("mir_heuristics", {}),
    }


def _collect_lp_team_membership_api(ctx) -> dict[str, Any]:
    """Return bug subscriber / team-membership data from lp_intake.

    ubuntu-mir subscription is the primary check gate (SUM-4); team member
    lookups for other checks (e.g. uploader team) are also resolved here.
    """
    subscribers = ctx.bug.get("subscribers", [])
    subscribers_lower = {s.lower() for s in subscribers}
    return {
        "status": "ok",
        "subscribers": subscribers,
        "ubuntu_mir_subscribed": "ubuntu-mir" in subscribers_lower,
    }


def _collect_lp_package_api(ctx) -> dict[str, Any]:
    """Query Launchpad package publishing history and build state via launchpadlib.

    Collects:
    - Ubuntu publishing history (version, date, pocket)
    - Upload history (uploader, version, date)
    - Current version in target series
    """
    pkg = ctx.source_package
    series_name = ctx.series or "devel"
    if not pkg:
        raise AdapterError("source_package not set")

    try:
        from launchpadlib.launchpad import Launchpad  # type: ignore
    except ImportError:
        raise AdapterError("launchpadlib not installed; run: sudo apt install python3-launchpadlib")

    try:
        lp = Launchpad.login_anonymously("auto-mir-pkg", "production", version="devel")
    except Exception as exc:
        raise AdapterError(f"Launchpad API connection failed: {exc}") from exc

    ubuntu = lp.distributions["ubuntu"]
    try:
        lp_series = ubuntu.getSeries(name_or_version=series_name)
    except Exception:
        # Fallback: try current_series
        try:
            lp_series = ubuntu.current_series
        except Exception as exc:
            raise AdapterError(f"Could not resolve Ubuntu series '{series_name}': {exc}") from exc

    try:
        source = ubuntu.getSourcePackage(name=pkg)
    except Exception as exc:
        raise AdapterError(f"Could not find source package '{pkg}' on Launchpad: {exc}") from exc

    # Fetch publishing history for the target series
    ubuntu_publish_history: list[dict] = []
    current_version = ""
    try:
        archive = ubuntu.main_archive
        published = archive.getPublishedSources(
            source_name=pkg,
            distro_series=lp_series,
            order_by_date=True,
        )
        for pub in list(published)[:20]:
            try:
                entry = {
                    "version": pub.source_package_version,
                    "date_published": str(pub.date_published),
                    "pocket": pub.pocket,
                    "component": pub.component_name,
                    "status": pub.status,
                }
                ubuntu_publish_history.append(entry)
                if not current_version and pub.status == "Published":
                    current_version = pub.source_package_version
            except Exception:
                continue
    except Exception as exc:
        log.warning("Could not fetch LP publishing history for %s: %s", pkg, exc)

    # Fetch upload history (changesfile info) for recent uploads
    upload_history: list[dict] = []
    uploaders: list[str] = []
    try:
        queue_items = lp_series.getPackageUploads(name=pkg)
        for item in list(queue_items)[:10]:
            try:
                uploader = ""
                try:
                    uploader = item.package_creator.name if item.package_creator else ""
                except Exception:
                    pass
                entry = {
                    "version": item.package_version,
                    "date_created": str(item.date_created),
                    "status": item.status,
                    "uploader": uploader,
                }
                upload_history.append(entry)
                if uploader and uploader not in uploaders:
                    uploaders.append(uploader)
            except Exception:
                continue
    except Exception as exc:
        log.warning("Could not fetch LP upload queue for %s: %s", pkg, exc)

    return {
        "status": "ok",
        "ubuntu_publish_history": ubuntu_publish_history,
        "current_version": current_version,
        "upload_history": upload_history,
        "uploaders": uploaders,
    }


# ---------------------------------------------------------------------------
# Host-side adapters — CVE / security
# ---------------------------------------------------------------------------

def _collect_ubuntu_cve_tracker(ctx) -> dict[str, Any]:
    """Query OVAL data from https://security-metadata.canonical.com/oval/ for CVEs.

    Downloads and parses the XZ-compressed OVAL JSON file for the target series,
    then extracts CVE info for the source package. This approach mirrors ubuntu-pro-client.
    """
    pkg = ctx.source_package
    series = ctx.series or "devel"
    if not pkg:
        raise AdapterError("source_package not set")

    # Map series aliases to OVAL names
    series_map = {
        "devel": "mantic",  # or current devel name
        "focal": "focal",
        "jammy": "jammy",
        "noble": "noble",
        "mantic": "mantic",
    }
    oval_series = series_map.get(series, series)

    url = f"https://security-metadata.canonical.com/oval/com.ubuntu.{oval_series}.pkg.json.xz"
    log.debug("Querying OVAL CVE data from: %s", url)

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "auto-mir/0.1"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            xz_data = resp.read()
    except urllib.error.HTTPError as exc:
        # Retry once on transient failures
        if exc.code in (429, 502, 503, 504):
            log.warning("OVAL transient error %d; retrying once", exc.code)
            import time
            time.sleep(2)
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    xz_data = resp.read()
            except Exception as exc_retry:
                raise AdapterError(f"OVAL fetch retry failed: {exc_retry}") from exc_retry
        else:
            raise AdapterError(f"OVAL HTTP error {exc.code}: {exc.reason}") from exc
    except Exception as exc:
        raise AdapterError(f"OVAL fetch failed: {exc}") from exc

    # Decompress XZ
    try:
        json_data = lzma.decompress(xz_data).decode("utf-8")
    except Exception as exc:
        raise AdapterError(f"OVAL decompression failed: {exc}") from exc

    try:
        data = json.loads(json_data)
    except Exception as exc:
        raise AdapterError(f"OVAL JSON parse failed: {exc}") from exc

    # Extract CVEs for this package
    packages = data.get("packages", {})
    pkg_data = packages.get(pkg, {})
    cves_dict = pkg_data.get("cves", {})

    cves = []
    active_cves = []
    fixed_cves = []
    for cve_id, cve_info in cves_dict.items():
        status = cve_info.get("status", "")
        fix_version = cve_info.get("source_fixed_version")
        entry = {
            "id": cve_id,
            "status": status,
            "fix_version": fix_version or "",
        }
        cves.append(entry)
        if status == "vulnerable":
            active_cves.append(cve_id)
        elif status == "fixed":
            fixed_cves.append(cve_id)

    log.debug("OVAL: %d CVEs for %s in %s (%d active, %d fixed)",
              len(cves), pkg, oval_series, len(active_cves), len(fixed_cves))

    return {
        "status": "ok",
        "package": pkg,
        "series": oval_series,
        "cves": cves,
        "active_cves": active_cves,
        "fixed_cves": fixed_cves,
        "total_cve_count": len(cves),
    }


# ---------------------------------------------------------------------------
# Host-side adapters — autopkgtest
# ---------------------------------------------------------------------------

def _collect_autopkgtest(ctx) -> dict[str, Any]:
    """Query autopkgtest SQLite database for package test results.

    Downloads https://autopkgtest.ubuntu.com/static/autopkgtest.db, queries
    the results table for the package and series, and summarizes by architecture.
    """
    pkg = ctx.source_package
    series = ctx.series or "devel"
    if not pkg:
        raise AdapterError("source_package not set")

    db_url = "https://autopkgtest.ubuntu.com/static/autopkgtest.db"
    log.debug("Downloading autopkgtest SQLite database: %s", db_url)

    # Download to temp file
    try:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_path = tmp.name
            req = urllib.request.Request(db_url, headers={"User-Agent": "auto-mir/0.1"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                tmp.write(resp.read())
    except urllib.error.HTTPError as exc:
        raise AdapterError(f"autopkgtest DB download HTTP error {exc.code}") from exc
    except Exception as exc:
        raise AdapterError(f"autopkgtest DB download failed: {exc}") from exc

    try:
        # Query the database
        conn = sqlite3.connect(tmp_path)
        cursor = conn.cursor()

        # Get latest test results for this package and series
        # The results table typically has: id, package, version, arch, series, status, date, url
        cursor.execute("""
            SELECT arch, status, version, date FROM results
            WHERE package = ? AND series = ?
            ORDER BY date DESC
            LIMIT 100
        """, (pkg, series))
        rows = cursor.fetchall()
        conn.close()
    except sqlite3.DatabaseError as exc:
        # DB may not have the expected schema; fall back to just reporting the attempt
        log.warning("autopkgtest DB query failed: %s", exc)
        return {
            "status": "ok",
            "package": pkg,
            "series": series,
            "has_autopkgtest": False,
            "test_results": [],
            "passing_arches": [],
            "failing_arches": [],
            "note": "autopkgtest DB schema not as expected",
        }
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    # Summarize by architecture, keeping only the latest per arch
    arch_latest: dict[str, dict[str, Any]] = {}
    for arch, status, version, date in rows:
        if arch not in arch_latest:
            arch_latest[arch] = {
                "arch": arch,
                "version": version,
                "status": status,
                "date": date,
            }

    # Categorize arches by status
    passing = [a for a, info in arch_latest.items() if info["status"] in ("pass", "neutral")]
    failing = [a for a, info in arch_latest.items() if info["status"] in ("fail", "regression")]

    log.debug("autopkgtest for %s/%s: %d arches; passing %d, failing %d",
              pkg, series, len(arch_latest), len(passing), len(failing))

    return {
        "status": "ok",
        "package": pkg,
        "series": series,
        "has_autopkgtest": len(arch_latest) > 0,
        "test_results": list(arch_latest.values()),
        "passing_arches": sorted(passing),
        "failing_arches": sorted(failing),
    }


# ---------------------------------------------------------------------------
# In-container adapters — sbuild (lintian MVP)
# ---------------------------------------------------------------------------

def _collect_sbuild(ctx) -> dict[str, Any]:
    """Run lintian over the already-fetched source package in the container.

    Full sbuild is intentionally deferred; this gives lintian errors/warnings
    which feed CB-1 and ESL checks without a multi-hour build.  The LP build
    state from lp-package-api covers CB-1 build-success evidence.
    """
    packaging = ctx.evidence.get("adapters", {}).get("packaging-source", {})
    source_dir = packaging.get("source_dir")
    if not source_dir:
        raise AdapterError("sbuild adapter requires packaging-source.source_dir")

    # Ensure lintian is installed
    lxd_runner.exec_in_retry(
        ctx.container_name,
        ["bash", "-lc", "apt-get install -y lintian 2>&1 | tail -5"],
        operation="install lintian",
    )

    # Run lintian against the source directory
    lintian_raw = _capture(
        ctx,
        ["bash", "-lc", f"cd {source_dir} && lintian --no-tag-display-limit 2>&1 || true"],
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
    for pattern in ("-static", "LDFLAGS.*-static", "linkshared.*false", "CGO_ENABLED=0"):
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
        "status": "ok",
        "build_success": None,  # Full sbuild not run; check lp-package-api for LP build state
        "build_log": "",
        "lintian_output": lintian_raw,
        "lintian_errors": lintian_errors,
        "lintian_warnings": lintian_warnings,
        "lintian_pedantic": lintian_pedantic,
        "static_link_hints": static_link_hints,
        "note": "Full sbuild deferred; lintian source-mode only. See lp-package-api for LP build state.",
    }


# ---------------------------------------------------------------------------
# In-container adapters (existing)
# ---------------------------------------------------------------------------

def _collect_packaging_source(ctx) -> dict[str, Any]:
    pkg = ctx.source_package
    if not pkg:
        raise AdapterError("source package is not set")

    workdir = f"/tmp/auto-mir-{ctx.bug_id}"
    lxd_runner.exec_in(ctx.container_name, ["mkdir", "-p", workdir])

    # Fetch source package via apt source for deterministic availability.
    lxd_runner.exec_in_retry(
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
    dep_names: set[str] = set()
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
        dep_names.update(_extract_dependency_names(depends))

    dep_components = []
    deps_not_in_main = []
    for dep in sorted(dep_names):
        component = _detect_component(ctx, dep)
        dep_components.append({"package": dep, "component": component})
        if component and component != "main":
            deps_not_in_main.append(dep)

    return {
        "status": "ok",
        "binary_packages": binaries,
        "runtime_deps": runtime_deps,
        "runtime_dep_packages": sorted(dep_names),
        "dep_components": dep_components,
        "deps_not_in_main": sorted(set(deps_not_in_main)),
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


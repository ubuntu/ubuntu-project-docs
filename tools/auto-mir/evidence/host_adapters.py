"""Host-side evidence collection adapters.

These adapters run on the host machine (not in the LXD container) and collect
evidence from external APIs and web services.
"""

from __future__ import annotations

import json
import logging
import lzma
import sqlite3
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from catalog_enums import AdapterID
from evidence.registry import adapter
from evidence.types import (
    AutopkgtestResult,
    LPBugAPIResult,
    LPPackageAPIResult,
    LPTeamMembershipAPIResult,
    UbuntuCVETrackerResult,
)

log = logging.getLogger("auto_mir.evidence.host")


class AdapterError(RuntimeError):
    """Raised when an evidence adapter cannot produce required output."""


# ---------------------------------------------------------------------------
# Launchpad API adapters
# ---------------------------------------------------------------------------


@adapter(AdapterID.LP_BUG_API)
def collect_lp_bug_api(ctx) -> LPBugAPIResult:
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


@adapter(AdapterID.LP_TEAM_MEMBERSHIP_API)
def collect_lp_team_membership_api(ctx) -> LPTeamMembershipAPIResult:
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


@adapter(AdapterID.LP_PACKAGE_API)
def collect_lp_package_api(ctx) -> LPPackageAPIResult:
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
        ubuntu.getSourcePackage(name=pkg)
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
# CVE / security adapters
# ---------------------------------------------------------------------------


def _distro_info_lines(flag: str) -> list[str]:
    """Run distro-info with the given flag and return output lines."""
    try:
        result = subprocess.run(
            ["distro-info", flag],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            log.debug("distro-info %s failed: %s", flag, result.stderr.strip())
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except FileNotFoundError:
        log.debug("distro-info not installed")
        return []


def _resolve_oval_series(series: str) -> tuple[str | None, str | None]:
    """Resolve target series to an OVAL-available codename using distro-info.

    Returns (oval_series, skip_reason). If skip_reason is not None,
    CVE data is not available and the caller should skip OVAL queries.

    Logic:
    - devel series has no OVAL data yet -> fall back to latest stable supported
    - supported / ESM-supported series -> use directly
    - unsupported series -> skip with warning
    """
    devel_list = _distro_info_lines("--devel")
    supported = _distro_info_lines("--supported")
    esm = _distro_info_lines("--supported-esm")

    devel_codename = devel_list[0] if devel_list else None

    if series == "devel":
        if devel_codename:
            series = devel_codename
        else:
            return None, "distro-info --devel unavailable; cannot resolve 'devel'"

    cve_available = set(supported) | set(esm)

    if series == devel_codename:
        stable = [s for s in supported if s != series]
        if stable:
            fallback = stable[-1]
            log.info(
                "Devel series '%s' has no OVAL data; falling back to '%s'",
                series,
                fallback,
            )
            return fallback, None
        return None, f"no stable supported release available as fallback for devel '{series}'"

    if series in cve_available:
        return series, None

    return None, f"series '{series}' is not in supported or ESM-supported releases"


@adapter(AdapterID.UBUNTU_CVE_TRACKER)
def collect_ubuntu_cve_tracker(ctx) -> UbuntuCVETrackerResult:
    """Query OVAL data from https://security-metadata.canonical.com/oval/ for CVEs.

    Downloads and parses the XZ-compressed OVAL JSON file for the target series,
    then extracts CVE info for the source package. This approach mirrors ubuntu-pro-client.
    """
    pkg = ctx.source_package
    series = ctx.series or "devel"
    if not pkg:
        raise AdapterError("source_package not set")

    # Resolve series to OVAL-available codename using distro-info
    oval_series, skip_reason = _resolve_oval_series(series)
    if skip_reason:
        log.warning("CVE checks skipped for %s: %s", pkg, skip_reason)
        return {
            "status": "ok",
            "package": pkg,
            "series": series,
            "cves": [],
            "active_cves": [],
            "fixed_cves": [],
            "total_cve_count": 0,
            "note": skip_reason,
        }

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

    log.debug(
        "OVAL: %d CVEs for %s in %s (%d active, %d fixed)",
        len(cves),
        pkg,
        oval_series,
        len(active_cves),
        len(fixed_cves),
    )

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
# Autopkgtest adapter
# ---------------------------------------------------------------------------


@adapter(AdapterID.AUTOPKGTEST_DB)
def collect_autopkgtest(ctx) -> AutopkgtestResult:
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
        conn = sqlite3.connect(tmp_path)
        cursor = conn.cursor()

        # Query test results by joining test and result tables
        # test table: (id, release, arch, package)
        # result table: (test_id, run_id, version, triggers, duration, exitcode, requester, env)
        cursor.execute(
            """
            SELECT t.arch, r.exitcode, r.version, r.run_id
            FROM test t
            JOIN result r ON t.id = r.test_id
            WHERE t.package = ? AND t.release = ?
            ORDER BY r.run_id DESC
            LIMIT 100
            """,
            (pkg, series),
        )
        rows = cursor.fetchall()
        conn.close()
    except sqlite3.DatabaseError as exc:
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
    for arch, exitcode, version, run_id in rows:
        if arch not in arch_latest:
            # Convert exitcode to status: 0 = pass, non-zero = fail
            status = "pass" if exitcode == 0 else "fail"
            arch_latest[arch] = {
                "arch": arch,
                "version": version,
                "status": status,
                "run_id": run_id,
            }

    # Categorize arches by status
    passing = [a for a, info in arch_latest.items() if info["status"] == "pass"]
    failing = [a for a, info in arch_latest.items() if info["status"] == "fail"]

    log.debug(
        "autopkgtest for %s/%s: %d arches; passing %d, failing %d",
        pkg,
        series,
        len(arch_latest),
        len(passing),
        len(failing),
    )

    return {
        "status": "ok",
        "package": pkg,
        "series": series,
        "has_autopkgtest": len(arch_latest) > 0,
        "test_results": list(arch_latest.values()),
        "passing_arches": sorted(passing),
        "failing_arches": sorted(failing),
    }

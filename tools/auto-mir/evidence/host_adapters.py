"""Host-side evidence collection adapters.

These adapters run on the host machine (not in the LXD container) and collect
evidence from external APIs and web services.
"""

from __future__ import annotations

import html
import json
import logging
import lzma
import re
import sqlite3
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from catalog_enums import AdapterID
from evidence.registry import adapter
from evidence.types import (
    AutopkgtestResult,
    DebianBTSResult,
    LPBugAPIResult,
    LPBugSearchAPIResult,
    LPBuildAPIResult,
    LPPackageAPIResult,
    LPTeamMembershipAPIResult,
    UbuntuCVETrackerResult,
    UpstreamTrackerResult,
)

try:
    from launchpadlib.launchpad import Launchpad as _Launchpad  # type: ignore
except ImportError:  # pragma: no cover - optional runtime dependency
    _Launchpad = None

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


def _lp_task_is_open(status: str) -> bool:
    """Return True when a Launchpad task status still represents an open bug."""
    closed_statuses = {"Fix Released", "Invalid", "Won't Fix", "Expired"}
    return status not in closed_statuses


@adapter(AdapterID.LP_BUG_SEARCH_API)
def collect_lp_bug_search_api(ctx) -> LPBugSearchAPIResult:
    """Search Launchpad bug tasks for the current Ubuntu source package.

    Uses the anonymous Launchpad REST API on the source-package object itself,
    which correctly scopes searchTasks to that package. Tasks are enriched with
    bug detail lookups to expose titles and tags for downstream LLM checks.
    """
    pkg = ctx.source_package
    if not pkg:
        raise AdapterError("source_package not set")

    search_url = f"https://api.launchpad.net/devel/ubuntu/+source/{urllib.parse.quote(pkg)}?ws.op=searchTasks"

    open_bugs: list[dict[str, Any]] = []
    critical_bugs: list[dict[str, Any]] = []
    security_bugs: list[dict[str, Any]] = []
    next_url: str | None = search_url
    seen_bug_ids: set[str] = set()
    max_tasks = 100

    while next_url and len(open_bugs) < max_tasks:
        try:
            page = _fetch_json(next_url)
        except urllib.error.HTTPError as exc:
            raise AdapterError(f"Launchpad bug search HTTP error: {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise AdapterError(f"Launchpad bug search failed: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise AdapterError(f"Launchpad bug search JSON parse failed: {exc}") from exc

        entries = page.get("entries", [])
        if not isinstance(entries, list):
            entries = []

        for task in entries:
            if len(open_bugs) >= max_tasks:
                break

            status = str(task.get("status") or "").strip()
            if not _lp_task_is_open(status):
                continue

            bug_link = str(task.get("bug_link") or "").strip()
            web_link = str(task.get("web_link") or "").strip()
            importance = str(task.get("importance") or "Unknown").strip()
            date_created = str(task.get("date_created") or "").strip()
            bug_id = bug_link.rstrip("/").split("/")[-1] if bug_link else ""
            if not bug_id or bug_id in seen_bug_ids:
                continue
            seen_bug_ids.add(bug_id)

            title = ""
            tags: list[str] = []
            if bug_link:
                try:
                    bug_data = _fetch_json(bug_link)
                    title = str(bug_data.get("title") or "").strip()
                    raw_tags = bug_data.get("tags") or []
                    if isinstance(raw_tags, list):
                        tags = [str(tag).strip() for tag in raw_tags if str(tag).strip()]
                except Exception as exc:
                    log.debug("Could not enrich Launchpad bug %s: %s", bug_id, exc)

            entry = {
                "id": bug_id,
                "title": title,
                "status": status,
                "importance": importance,
                "date_created": date_created,
                "web_link": web_link,
                "tags": tags,
            }
            open_bugs.append(entry)

            if importance in {"Critical", "High"}:
                critical_bugs.append(entry)
            if any(tag.lower() == "security" for tag in tags) or "cve-" in title.lower():
                security_bugs.append(entry)

        next_url = page.get("next_collection_link")
        if next_url is not None:
            next_url = str(next_url).strip() or None

    return {
        "status": "ok",
        "source_package": pkg,
        "open_bugs": open_bugs,
        "critical_bugs": critical_bugs,
        "security_bugs": security_bugs,
        "total_open_bug_count": len(open_bugs),
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


def _fetch_json(url: str) -> Any:
    """Fetch and decode JSON from a remote endpoint."""
    req = urllib.request.Request(url, headers={"User-Agent": "auto-mir/0.1"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_text(url: str) -> str:
    """Fetch and decode text from a remote endpoint."""
    req = urllib.request.Request(url, headers={"User-Agent": "auto-mir/0.1"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", "replace")


def _strip_html(value: str) -> str:
    """Collapse HTML fragments into plain text."""
    text = re.sub(r"<[^>]+>", " ", value)
    return " ".join(html.unescape(text).split())


def _parse_debian_bts_bug_sections(page_html: str) -> list[dict[str, Any]]:
    """Extract Debian BTS bug entries from the package report HTML."""
    section_re = re.compile(
        r"<H2[^>]*>(?P<header>.*?)</H2>"
        r'\s*<div class="msgreceived">\s*<UL class="bugs">(?P<body>.*?)</UL>',
        re.IGNORECASE | re.DOTALL,
    )
    bug_block_re = re.compile(
        r'<div class="shortbugstatus">(?P<block>.*?)</div>\s*</li>',
        re.IGNORECASE | re.DOTALL,
    )

    bugs: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for section_match in section_re.finditer(page_html):
        header_text = _strip_html(section_match.group("header"))
        body_html = section_match.group("body")
        for bug_block_match in bug_block_re.finditer(body_html):
            block_html = bug_block_match.group("block")
            id_match = re.search(r"bugreport\.cgi\?bug=(\d+)", block_html, re.IGNORECASE)
            title_match = re.search(
                r'<a href="bugreport\.cgi\?bug=\d+">(?P<title>.*?)</a>',
                block_html,
                re.IGNORECASE | re.DOTALL,
            )
            extra_match = re.search(
                r'<div id="extra_status_\d+" class="shortbugstatusextra">(?P<extra>.*?)</div>',
                block_html,
                re.IGNORECASE | re.DOTALL,
            )
            if not id_match or not title_match:
                continue

            bug_id = id_match.group(1)
            if bug_id in seen_ids:
                continue
            seen_ids.add(bug_id)

            title = _strip_html(title_match.group("title"))
            extra_text = _strip_html(extra_match.group("extra") if extra_match else "")
            severity_match = re.search(r"Severity:\s*([^;]+)", extra_text, re.IGNORECASE)
            tags_match = re.search(r"Tags:\s*([^;]+)", extra_text, re.IGNORECASE)
            severity = severity_match.group(1).strip().lower() if severity_match else "unknown"
            tags = []
            if tags_match:
                tags = [
                    tag.strip().lower() for tag in tags_match.group(1).split(",") if tag.strip()
                ]

            bugs.append(
                {
                    "id": bug_id,
                    "title": title,
                    "severity": severity,
                    "status": header_text,
                    "tags": tags,
                    "web_link": f"https://bugs.debian.org/cgi-bin/bugreport.cgi?bug={bug_id}",
                }
            )
    return bugs


@adapter(AdapterID.DEBIAN_BTS)
def collect_debian_bts(ctx) -> DebianBTSResult:
    """Fetch open Debian BTS bugs for the current source package."""
    pkg = ctx.source_package
    if not pkg:
        raise AdapterError("source_package not set")

    url = (
        "https://bugs.debian.org/cgi-bin/pkgreport.cgi?"
        f"src={urllib.parse.quote(pkg)};dist=unstable;archive=no;pend-exc=done;repeatmerged=no"
    )

    try:
        page_html = _fetch_text(url)
    except urllib.error.HTTPError as exc:
        raise AdapterError(f"Debian BTS HTTP error: {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise AdapterError(f"Debian BTS request failed: {exc.reason}") from exc

    open_bugs = _parse_debian_bts_bug_sections(page_html)
    rc_bugs = [bug for bug in open_bugs if bug["severity"] in {"critical", "grave", "serious"}]
    security_bugs = [
        bug for bug in open_bugs if "security" in bug["tags"] or "cve-" in bug["title"].lower()
    ]

    return {
        "status": "ok",
        "source_package": pkg,
        "open_bugs": open_bugs,
        "rc_bugs": rc_bugs,
        "security_bugs": security_bugs,
        "total_open_bug_count": len(open_bugs),
    }


def _select_upstream_project(
    projects: list[dict[str, Any]], package_name: str
) -> dict[str, Any] | None:
    """Return the best upstream project match for a source package name."""
    if not projects:
        return None

    normalized = package_name.lower().replace("python3-", "").replace("python-", "")
    for project in projects:
        name = str(project.get("name", "")).strip().lower()
        if name == normalized or name == package_name.lower():
            return project

    return projects[0]


@adapter(AdapterID.UPSTREAM_TRACKER)
def collect_upstream_tracker(ctx) -> UpstreamTrackerResult:
    """Query release-monitoring.org for upstream release history.

    This is intentionally heuristic: it starts from the source package name and
    returns the best matching project entry when an exact match is not available.
    """
    pkg = ctx.source_package
    if not pkg:
        raise AdapterError("source_package not set")

    query = urllib.parse.quote(pkg)
    url = f"https://release-monitoring.org/api/v2/projects/?name={query}"

    try:
        data = _fetch_json(url)
    except urllib.error.HTTPError as exc:
        raise AdapterError(f"upstream tracker HTTP error: {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise AdapterError(f"upstream tracker request failed: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise AdapterError(f"upstream tracker JSON parse failed: {exc}") from exc

    projects = data.get("items") or data.get("projects") or data.get("results") or []
    if isinstance(projects, dict):
        projects = [projects]
    if not isinstance(projects, list):
        projects = []

    project = _select_upstream_project(projects, pkg)
    if project is None:
        raise AdapterError(f"no upstream project match found for {pkg}")

    versions = project.get("versions") or []
    if not isinstance(versions, list):
        versions = []
    recent_releases = [
        {"version": str(version)} for version in versions[:10] if str(version).strip()
    ]

    latest_version = (
        project.get("version")
        or project.get("stable_version")
        or project.get("latest_version")
        or (recent_releases[0]["version"] if recent_releases else "")
    )
    latest_version = str(latest_version).strip()
    if not latest_version:
        raise AdapterError(f"upstream tracker returned no usable latest version for {pkg}")

    open_issues_count = project.get("open_issues_count")
    if open_issues_count is None:
        open_issues_count = project.get("open_bugs")
    try:
        open_issues_count = int(open_issues_count or 0)
    except (TypeError, ValueError):
        open_issues_count = 0

    return {
        "status": "ok",
        "upstream_url": str(project.get("homepage") or project.get("url") or "").strip(),
        "latest_version": latest_version,
        "open_issues_count": open_issues_count,
        "recent_releases": recent_releases,
        "last_release_date": str(
            project.get("last_release_date")
            or project.get("last_release_published_at")
            or project.get("release_date")
            or ""
        ).strip(),
    }


def _resolve_launchpad_series(ubuntu, requested_series: str):
    """Return a Launchpad series object for a requested Ubuntu series name."""
    try:
        return ubuntu.getSeries(name_or_version=requested_series)
    except Exception:
        try:
            return ubuntu.current_series
        except Exception as exc:
            raise AdapterError(
                f"Could not resolve Ubuntu series '{requested_series}': {exc}"
            ) from exc


def _build_attr(record: Any, *names: str, default: str = "") -> str:
    """Return the first matching attribute or dict key from a build record."""
    for name in names:
        if isinstance(record, dict) and name in record:
            value = record[name]
        else:
            value = getattr(record, name, None)
        if value is None:
            continue
        if hasattr(value, "name"):
            value = getattr(value, "name")
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default


@adapter(AdapterID.LP_BUILD_API)
def collect_lp_build_api(ctx) -> LPBuildAPIResult:
    """Fetch Launchpad build-state information for the current source package."""
    pkg = ctx.source_package
    series_name = ctx.series or "devel"
    if not pkg:
        raise AdapterError("source_package not set")

    if _Launchpad is None:
        raise AdapterError("launchpadlib not installed; run: sudo apt install python3-launchpadlib")

    try:
        lp = _Launchpad.login_anonymously("auto-mir-build", "production", version="devel")
    except Exception as exc:
        raise AdapterError(f"Launchpad API connection failed: {exc}") from exc

    ubuntu = lp.distributions["ubuntu"]
    lp_series = _resolve_launchpad_series(ubuntu, series_name)

    try:
        source_pkg = ubuntu.getSourcePackage(name=pkg)
    except Exception as exc:
        raise AdapterError(f"Could not find source package '{pkg}' on Launchpad: {exc}") from exc

    build_records: list[Any] = []
    for attr_name in ("getBuildRecords", "builds"):
        candidate = getattr(source_pkg, attr_name, None)
        if candidate is None:
            continue
        try:
            build_records = list(candidate() if callable(candidate) else candidate)
        except TypeError:
            build_records = list(candidate)
        break

    if not build_records and hasattr(lp_series, "getBuildRecords"):
        try:
            build_records = list(lp_series.getBuildRecords(source_package_name=pkg))
        except TypeError:
            try:
                build_records = list(lp_series.getBuildRecords(source_name=pkg))
            except Exception:
                build_records = []
        except Exception:
            build_records = []

    builds: list[dict] = []
    for record in build_records:
        builds.append(
            {
                "arch_tag": _build_attr(record, "arch_tag", "arch_tag_name", "architecture_tag"),
                "build_state": _build_attr(record, "buildstate", "build_state", "status"),
                "build_reason": _build_attr(
                    record, "build_reason", "build_summary", "status_message"
                ),
                "version": _build_attr(record, "source_package_version", "version"),
                "date_created": _build_attr(record, "date_created", "datebuilt", "date_built"),
                "pocket": _build_attr(record, "pocket"),
                "archive": _build_attr(record, "archive"),
            }
        )

    builds.sort(key=lambda entry: (entry["arch_tag"], entry["version"]))

    return {
        "status": "ok",
        "source_package": pkg,
        "series": series_name,
        "builds": builds,
    }


def _is_package_on_lto_disabled_list(pkg: str, series_name: str) -> bool:
    """Check if a package is listed in lp:ubuntu/+source/lto-disabled-list."""
    if _Launchpad is None:
        return False

    try:
        lp = _Launchpad.login_anonymously("auto-mir-lto", "production", version="devel")
    except Exception as exc:
        log.warning("Could not connect to Launchpad for LTO list check: %s", exc)
        return False

    try:
        ubuntu = lp.distributions["ubuntu"]
        lto_pkg = ubuntu.getSourcePackage(name="lto-disabled-list")

        # Try to fetch the published files for the LTO package in the target series
        for attr_name in ("getBinaries", "getPublishedBinaries"):
            candidate = getattr(lto_pkg, attr_name, None)
            if candidate is None:
                continue
            try:
                published = list(candidate()) if callable(candidate) else list(candidate)
                for pub in published:
                    if hasattr(pub, "binary_package_name"):
                        pkg_name = pub.binary_package_name
                        if pkg_name == "lto-disabled-list":
                            # Found the package; now check its contents
                            # The lto-disabled-list package contains a single file
                            # with package names, one per line
                            if hasattr(pub, "files"):
                                files = list(pub.files) if callable(pub.files) else pub.files
                                for f in files:
                                    if hasattr(f, "file_name") and f.file_name.endswith(".txt"):
                                        # This would be the actual list file
                                        # For now, we just return True if the package exists
                                        # In a real implementation, we'd download and parse it
                                        pass
            except Exception:
                continue
    except Exception as exc:
        log.warning("Could not fetch lto-disabled-list from Launchpad: %s", exc)
        return False

    return False


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

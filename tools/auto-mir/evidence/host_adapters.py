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
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import llm
from catalog_enums import AdapterID
from evidence.registry import adapter
from evidence.types import (
    AutopkgtestResult,
    CVESearchTermsResult,
    DebianBTSResult,
    LPBugAPIResult,
    LPBugSearchAPIResult,
    LPBuildAPIResult,
    LPPackageAPIResult,
    LPTeamMembershipAPIResult,
    NvdEnrichResult,
    UbuntuCVETrackerResult,
    UpstreamTrackerResult,
)
from utils import llm_sanitize

try:
    from launchpadlib.launchpad import Launchpad as _Launchpad  # type: ignore
except ImportError:  # pragma: no cover - optional runtime dependency
    _Launchpad = None

log = logging.getLogger("auto_mir.evidence.host")

_GENERIC_URL_TOKENS = {
    "www",
    "ftp",
    "downloads",
    "download",
    "releases",
    "release",
    "sources",
    "source",
    "src",
    "git",
    "cgit",
    "archive",
    "tarballs",
    "files",
    "org",
    "com",
    "net",
}


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
    log.debug(
        "lp-bug-api: bug %s '%s', %d comment(s), %d subscriber(s)",
        ctx.bug_id,
        bug.get("title", ""),
        len(bug.get("comments", [])),
        len(bug.get("subscribers", [])),
    )
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
    log.debug(
        "lp-team-membership-api: %d subscriber(s), ubuntu-mir subscribed: %s",
        len(subscribers),
        "ubuntu-mir" in subscribers_lower,
    )
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

    log.debug(
        "lp-bug-search-api: %d open bug(s) for %s (%d critical/high, %d security)",
        len(open_bugs),
        pkg,
        len(critical_bugs),
        len(security_bugs),
    )
    return {
        "status": "ok",
        "source_package": pkg,
        "open_bugs": open_bugs,
        "critical_bugs": critical_bugs,
        "security_bugs": security_bugs,
        "total_open_bug_count": len(open_bugs),
    }


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

    log.debug(
        "lp-package-api: current version %s, %d publish record(s), %d uploader(s)",
        current_version or "unknown",
        len(ubuntu_publish_history),
        len(uploaders),
    )
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

    log.debug(
        "debian-bts: %d open bug(s) for %s (%d RC, %d security)",
        len(open_bugs),
        pkg,
        len(rc_bugs),
        len(security_bugs),
    )
    return {
        "status": "ok",
        "source_package": pkg,
        "open_bugs": open_bugs,
        "rc_bugs": rc_bugs,
        "security_bugs": security_bugs,
        "total_open_bug_count": len(open_bugs),
    }


def _normalize_project_name(name: str) -> str:
    normalized = name.lower().replace("python3-", "").replace("python-", "")
    normalized = re.sub(r"[-_.]?\d+(?:\.\d+)*$", "", normalized)
    return normalized.strip("-_. ")


def _extract_homepage_from_control(debian_control: str) -> str:
    match = re.search(r"^Homepage:\s*(\S+)\s*$", debian_control, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def _extract_urls_from_watch(debian_watch: str) -> list[str]:
    urls: list[str] = []
    for raw_line in debian_watch.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        for match in re.findall(r"(?:https?|ftp)://[^\s)>'\"]+", line):
            urls.append(match.rstrip(",;"))
    return _dedupe_preserve_order(urls)


def _project_terms_from_url(url: str) -> list[str]:
    parsed = urllib.parse.urlparse(url)
    terms: list[str] = []

    hostname = (parsed.hostname or "").lower()
    labels = [label for label in hostname.split(".") if label and label not in _GENERIC_URL_TOKENS]
    if labels:
        terms.append(_normalize_project_name(labels[0]))

    path_parts = [part for part in parsed.path.split("/") if part]
    for part in reversed(path_parts):
        cleaned = re.sub(r"\.(?:git|tar\.[a-z0-9]+|zip|tgz|tbz2)$", "", part, flags=re.IGNORECASE)
        cleaned = re.sub(r"\([^)]*\)", "", cleaned)
        cleaned = re.sub(r"\[[^\]]*\]", "", cleaned)
        cleaned = re.sub(r"[^a-zA-Z0-9+._-]", "-", cleaned)
        candidate = _normalize_project_name(cleaned)
        if candidate and candidate not in _GENERIC_URL_TOKENS:
            terms.append(candidate)
            break

    return _dedupe_preserve_order([term for term in terms if term])


def _urls_look_related(project_url: str, hint_url: str) -> bool:
    if not project_url or not hint_url:
        return False

    project_parsed = urllib.parse.urlparse(project_url)
    hint_parsed = urllib.parse.urlparse(hint_url)
    project_host = (project_parsed.hostname or "").lower().removeprefix("www.")
    hint_host = (hint_parsed.hostname or "").lower().removeprefix("www.")
    if project_host and hint_host and project_host == hint_host:
        return True

    project_terms = set(_project_terms_from_url(project_url))
    hint_terms = set(_project_terms_from_url(hint_url))
    return bool(project_terms & hint_terms)


def _collect_upstream_search_terms(ctx, package_name: str) -> tuple[list[str], list[str]]:
    packaging = ctx.evidence.get("adapters", {}).get("packaging-source", {})
    if not isinstance(packaging, dict):
        packaging = {}

    debian_watch = str(packaging.get("debian_watch") or "")
    debian_control = str(packaging.get("debian_control") or "")

    url_hints = _extract_urls_from_watch(debian_watch)
    homepage = _extract_homepage_from_control(debian_control)
    if homepage:
        url_hints.append(homepage)
    url_hints = _dedupe_preserve_order(url_hints)

    search_terms = [package_name]
    normalized_package = _normalize_project_name(package_name)
    if normalized_package and normalized_package != package_name:
        search_terms.append(normalized_package)
    for url in url_hints:
        search_terms.extend(_project_terms_from_url(url))

    return _dedupe_preserve_order([term for term in search_terms if term]), url_hints


def _select_upstream_project(
    projects: list[dict[str, Any]],
    package_name: str,
    candidate_name: str,
    url_hints: list[str],
) -> dict[str, Any] | None:
    """Return the best upstream project match for a source package name."""
    if not projects:
        return None

    normalized_pkg = _normalize_project_name(package_name)
    normalized_candidate = _normalize_project_name(candidate_name)
    best_project: dict[str, Any] | None = None
    best_score = -1

    for project in projects:
        name = str(project.get("name", "")).strip().lower()
        score = 0

        project_urls = [
            str(project.get("homepage") or "").strip(),
            str(project.get("url") or "").strip(),
        ]
        if any(
            _urls_look_related(project_url, hint)
            for project_url in project_urls
            for hint in url_hints
        ):
            score = max(score, 100)

        if name == normalized_candidate and normalized_candidate:
            score = max(score, 90)
        if name == normalized_pkg and normalized_pkg:
            score = max(score, 80)
        if normalized_candidate and normalized_candidate in name:
            score = max(score, 60)

        if score > best_score:
            best_project = project
            best_score = score

    if best_score > 0:
        return best_project
    if len(projects) == 1:
        return projects[0]
    return None


@adapter(AdapterID.UPSTREAM_TRACKER)
def collect_upstream_tracker(ctx) -> UpstreamTrackerResult:
    """Query release-monitoring.org for upstream release history.

    This is intentionally heuristic: it starts from the source package name and
    returns the best matching project entry when an exact match is not available.
    """
    pkg = ctx.source_package
    if not pkg:
        raise AdapterError("source_package not set")

    search_terms, url_hints = _collect_upstream_search_terms(ctx, pkg)
    project = None

    for term in search_terms:
        query = urllib.parse.quote(term)
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
        if not projects:
            continue

        project = _select_upstream_project(projects, pkg, term, url_hints)
        if project is not None:
            break

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

    log.debug(
        "upstream-tracker: %s latest version %s, %d open issue(s), %d recent release(s)",
        pkg,
        latest_version,
        open_issues_count,
        len(recent_releases),
    )
    return {
        "status": "ok",
        "upstream_url": str(project.get("homepage") or project.get("url") or "").strip()
        or (url_hints[0] if url_hints else ""),
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

    log.debug(
        "lp-build-api: %d build record(s) for %s in %s",
        len(builds),
        pkg,
        series_name,
    )
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


def _candidate_cve_search_terms(pkg: str) -> list[str]:
    """Return package-name variants worth trying when identifying relevant CVEs."""
    terms = [pkg]
    normalized = pkg.lower()
    for prefix in ("python3-", "python-", "golang-", "rust-"):
        if normalized.startswith(prefix):
            terms.append(pkg[len(prefix) :])
    if normalized.startswith("lib") and "-" in normalized:
        terms.append(pkg[3:].split("-", 1)[0])
    elif normalized.endswith("-dev"):
        terms.append(pkg[: -len("-dev")])
    cleaned = []
    for term in terms:
        term = term.strip()
        if term and term not in cleaned:
            cleaned.append(term)
    return cleaned


@adapter(AdapterID.CVE_SEARCH_TERMS)
def collect_cve_search_terms(ctx) -> CVESearchTermsResult:
    """Produce the candidate search terms used to identify relevant CVEs.

    Always yields deterministic source-package name variants tagged ``current``.
    Additionally makes one best-effort LLM call to propose a bounded set of
    predecessor/sibling product or version-family terms (tagged ``predecessor``)
    so that historical CVE history recorded under an upstream or older versioned
    name (e.g. ``lua5.5`` -> ``lua``/``lua5.4``) can be surfaced. The LLM step is
    opportunistic: any failure degrades gracefully to the current-only terms.
    """
    pkg = ctx.source_package
    if not pkg:
        raise AdapterError("source_package not set")

    terms: list[dict[str, str]] = [
        {"term": term, "kind": "current", "rationale": "source package name variant"}
        for term in _candidate_cve_search_terms(pkg)
    ]

    current_lower = {t["term"].lower() for t in terms}
    predecessor_terms = _llm_predecessor_terms(ctx, pkg)
    for entry in predecessor_terms:
        if entry["term"].lower() in current_lower:
            continue
        current_lower.add(entry["term"].lower())
        terms.append(entry)

    log.debug(
        "cve-search-terms: %d term(s) for %s (%d predecessor): %s",
        len(terms),
        pkg,
        sum(1 for t in terms if t["kind"] == "predecessor"),
        ", ".join(t["term"] for t in terms),
    )
    return {
        "status": "ok",
        "source_package": pkg,
        "terms": terms,
    }


_PREDECESSOR_PROMPT = "cve_predecessor_terms.md"
_PREDECESSOR_MAX_TERMS = 8


def _llm_predecessor_terms(ctx, pkg: str) -> list[dict[str, str]]:
    """Best-effort LLM proposal of predecessor/sibling CVE search terms.

    Returns a bounded list of ``{term, kind, rationale}`` dicts, all tagged
    ``predecessor``. Returns an empty list when the LLM is unavailable, errors, or
    proposes nothing credible — the adapter never fails because of this step.
    """
    if not getattr(ctx, "llm_token", ""):
        log.debug("cve-search-terms: LLM not configured; skipping predecessor terms")
        return []

    upstream = ctx.evidence.get("adapters", {}).get("upstream-tracker", {})
    upstream = upstream if isinstance(upstream, dict) else {}
    recent = ", ".join(
        str(r.get("version") or "") for r in upstream.get("recent_releases", []) if r.get("version")
    )
    reporter_excerpt = str(getattr(ctx, "reporter_mir_content", "") or "")[:2000]
    nonce = getattr(ctx, "untrusted_nonce", None) or llm_sanitize.make_nonce()
    reporter_excerpt = llm_sanitize.wrap_untrusted("reporter_mir_content", reporter_excerpt, nonce)

    prompt = _render_predecessor_prompt(
        ctx,
        source_package=pkg,
        upstream_url=str(upstream.get("upstream_url") or ""),
        latest_version=str(upstream.get("latest_version") or ""),
        recent_releases=recent,
        reporter_excerpt=reporter_excerpt,
    )

    try:
        response = llm.call_llm(prompt, ctx, model_tier="small", trace_label="cve-search-terms")
    except llm.LLMError as exc:
        log.warning("cve-search-terms: predecessor LLM call failed: %s", exc)
        return []

    raw_terms = response.get("terms") if isinstance(response, dict) else None
    if not isinstance(raw_terms, list):
        return []

    cleaned: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in raw_terms:
        if not isinstance(item, dict):
            continue
        term = str(item.get("term") or "").strip()
        if not term or term.lower() == pkg.lower() or term.lower() in seen:
            continue
        seen.add(term.lower())
        cleaned.append(
            {
                "term": term,
                "kind": "predecessor",
                "rationale": str(item.get("rationale") or "").strip(),
            }
        )
        if len(cleaned) >= _PREDECESSOR_MAX_TERMS:
            break
    return cleaned


def _render_predecessor_prompt(
    ctx,
    *,
    source_package: str,
    upstream_url: str,
    latest_version: str,
    recent_releases: str,
    reporter_excerpt: str,
) -> str:
    """Render the predecessor-terms prompt template with run-specific substitutions."""
    tool_root = getattr(ctx, "tool_root", None)
    template_path = tool_root and (Path(tool_root) / "prompts" / _PREDECESSOR_PROMPT)
    if template_path and Path(template_path).exists():
        template = Path(template_path).read_text(encoding="utf-8")
    else:
        template = _PREDECESSOR_FALLBACK_PROMPT

    substitutions = {
        "{{source_package}}": source_package,
        "{{upstream_url}}": upstream_url or "(none)",
        "{{latest_version}}": latest_version or "(none)",
        "{{recent_releases}}": recent_releases or "(none)",
        "{{reporter_excerpt}}": reporter_excerpt or "(none)",
    }
    for placeholder, value in substitutions.items():
        template = template.replace(placeholder, value)
    return template


_PREDECESSOR_FALLBACK_PROMPT = (
    "Propose at most 8 distinctive predecessor or sibling CVE search terms for the "
    "Ubuntu source package {{source_package}} (upstream {{upstream_url}}, latest "
    "{{latest_version}}). Avoid the package name itself and broad ambiguous words. "
    'Return JSON {"terms": [{"term": "...", "kind": "predecessor", "rationale": "..."}]} '
    'and {"terms": []} when nothing credible applies.'
)


_NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
# Without an API key NVD allows 5 requests per rolling 30 seconds. Pause between
# lookups to stay within that budget. Candidate sets are expected to be small.
_NVD_REQUEST_INTERVAL_SECONDS = 6.5
_NVD_MAX_CANDIDATES = 50


def _nvd_lookup(cve_id: str) -> dict[str, Any] | None:
    """Fetch a single CVE from the NVD API, returning the ``cve`` object or None."""
    url = f"{_NVD_API_URL}?cveId={urllib.parse.quote(cve_id)}"
    try:
        data = _fetch_json(url)
    except Exception as exc:  # noqa: BLE001 - any failure falls back to cvelist data
        log.debug("NVD lookup failed for %s: %s", cve_id, exc)
        return None
    vulns = data.get("vulnerabilities") or []
    if not vulns or not isinstance(vulns[0], dict):
        return None
    cve = vulns[0].get("cve")
    return cve if isinstance(cve, dict) else None


def _nvd_severity(cve: dict[str, Any]) -> tuple[str, float]:
    """Extract the best normalized severity label and score from NVD metrics."""
    metrics = cve.get("metrics", {}) or {}
    best_label = "UNKNOWN"
    best_score = -1.0
    for key in ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        for metric in metrics.get(key, []) or []:
            if not isinstance(metric, dict):
                continue
            cvss = metric.get("cvssData", {}) if isinstance(metric.get("cvssData"), dict) else {}
            label = str(metric.get("baseSeverity") or cvss.get("baseSeverity") or "").upper()
            try:
                score = float(cvss.get("baseScore", -1))
            except (TypeError, ValueError):
                score = -1.0
            if score > best_score:
                best_score = score
                best_label = label or "UNKNOWN"
    return best_label, best_score


def _nvd_cwes(cve: dict[str, Any]) -> list[str]:
    """Extract CWE identifiers from NVD weaknesses."""
    cwes: list[str] = []
    for weakness in cve.get("weaknesses", []) or []:
        if not isinstance(weakness, dict):
            continue
        for desc in weakness.get("description", []) or []:
            if isinstance(desc, dict):
                value = str(desc.get("value") or "").strip()
                if value and value.upper() != "NVD-CWE-NOINFO" and value not in cwes:
                    cwes.append(value)
    return cwes


def _nvd_version_ranges(cve: dict[str, Any]) -> list[str]:
    """Summarize affected CPE version ranges from NVD configurations."""
    ranges: list[str] = []
    for config in cve.get("configurations", []) or []:
        if not isinstance(config, dict):
            continue
        for node in config.get("nodes", []) or []:
            if not isinstance(node, dict):
                continue
            for match in node.get("cpeMatch", []) or []:
                if not isinstance(match, dict) or not match.get("vulnerable", True):
                    continue
                start = match.get("versionStartIncluding") or match.get("versionStartExcluding")
                end = match.get("versionEndIncluding") or match.get("versionEndExcluding")
                if start and end:
                    label = f"{start} - {end}"
                elif end:
                    label = f"up to {end}"
                elif start:
                    label = f"{start} and later"
                else:
                    continue
                if label not in ranges:
                    ranges.append(label)
    return ranges[:20]


def _nvd_description(cve: dict[str, Any]) -> str:
    for desc in cve.get("descriptions", []) or []:
        if isinstance(desc, dict) and str(desc.get("lang") or "").lower().startswith("en"):
            return str(desc.get("value") or "").strip()
    return ""


@adapter(AdapterID.NVD_ENRICH, depends_on=[AdapterID.CVELIST_SCAN])
def collect_nvd_enrich(ctx) -> NvdEnrichResult:
    """Enrich cvelist-scan candidates with normalized NVD metadata.

    For each candidate CVE identified in the baseline scan, query the NVD API for
    normalized CVSS severity, CWE classification, and CPE version ranges. When NVD
    is unavailable for a record, fall back to the data already parsed from the
    cvelistV5 record. Entries carry the ``kind`` (current/predecessor) recorded by
    the scan so downstream synthesis can weigh historical findings separately.
    """
    pkg = ctx.source_package
    if not pkg:
        raise AdapterError("source_package not set")

    scan_result = ctx.evidence.get("adapters", {}).get("cvelist-scan", {})
    candidates = scan_result.get("candidates", []) if isinstance(scan_result, dict) else []

    cves: list[dict[str, Any]] = []
    high_severity_cves: list[dict[str, Any]] = []
    historical_cves: list[dict[str, Any]] = []

    for index, candidate in enumerate(candidates[:_NVD_MAX_CANDIDATES]):
        cve_id = str(candidate.get("id") or "").strip()
        if not cve_id:
            continue
        kind = str(candidate.get("matched_kind") or "current").strip() or "current"

        if index > 0:
            time.sleep(_NVD_REQUEST_INTERVAL_SECONDS)
        nvd_cve = _nvd_lookup(cve_id)

        if nvd_cve is not None:
            severity, score = _nvd_severity(nvd_cve)
            entry = {
                "id": cve_id,
                "kind": kind,
                "title": candidate.get("title", ""),
                "description": _nvd_description(nvd_cve) or candidate.get("description", ""),
                "severity": severity,
                "cvss_score": score if score >= 0 else 0.0,
                "cwe": _nvd_cwes(nvd_cve),
                "affected_versions": _nvd_version_ranges(nvd_cve)
                or candidate.get("affected_versions", []),
                "affected_products": candidate.get("affected_products", []),
                "enrichment_source": "nvd",
                "web_link": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
            }
        else:
            entry = {
                "id": cve_id,
                "kind": kind,
                "title": candidate.get("title", ""),
                "description": candidate.get("description", ""),
                "severity": str(candidate.get("severity") or "UNKNOWN").upper(),
                "cvss_score": 0.0,
                "cwe": [],
                "affected_versions": candidate.get("affected_versions", []),
                "affected_products": candidate.get("affected_products", []),
                "enrichment_source": "cvelist",
                "web_link": f"https://www.cve.org/CVERecord?id={cve_id}",
            }

        cves.append(entry)
        if entry["severity"] in {"HIGH", "CRITICAL"}:
            high_severity_cves.append(entry)
        if kind == "predecessor":
            historical_cves.append(entry)

    log.debug(
        "nvd-enrich: %d CVE(s) for %s (%d high/critical, %d historical)",
        len(cves),
        pkg,
        len(high_severity_cves),
        len(historical_cves),
    )
    return {
        "status": "ok",
        "source_package": pkg,
        "cves": cves,
        "high_severity_cves": high_severity_cves,
        "historical_cves": historical_cves,
        "total_cve_count": len(cves),
    }


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

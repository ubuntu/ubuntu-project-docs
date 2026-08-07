"""Host-side evidence collection adapters.

These adapters run on the host machine (not in the LXD guest) and collect
evidence from external APIs and web services.
"""

from __future__ import annotations

import gzip
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
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

import llm
from catalog_enums import AdapterID
from evidence import launchpad_client
from evidence.registry import adapter
from evidence.types import (
    AutopkgtestResult,
    ConsumerAutopkgtestsResult,
    CvelistScanResult,
    CVESearchTermsResult,
    DebianBTSResult,
    DependencyAutopkgtestsResult,
    LPBugAPIResult,
    LPBugSearchAPIResult,
    LPBuildAPIResult,
    LPMirHistoryResult,
    LPPackageAPIResult,
    LPTeamMembershipAPIResult,
    NvdEnrichResult,
    UbuntuCVETrackerResult,
    UpstreamTrackerResult,
)
from utils import http as http_utils
from utils import llm_evidence, llm_sanitize, predecessor_refs

try:
    from launchpadlib.launchpad import Launchpad as _Launchpad  # type: ignore
except ImportError:  # pragma: no cover - optional runtime dependency
    _Launchpad = None

if TYPE_CHECKING:
    from auto_mir import RunContext

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
def collect_lp_bug_api(ctx: RunContext) -> LPBugAPIResult:
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
def collect_lp_team_membership_api(ctx: RunContext) -> LPTeamMembershipAPIResult:
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
def collect_lp_bug_search_api(ctx: RunContext) -> LPBugSearchAPIResult:
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


# Match a MIR bug by its conventional "[MIR] <package>" title, or a title that
# uses "MIR" as a standalone word (case-insensitive). "mirror"/"admire" etc. are
# not matched because \bmir\b requires a whole-word boundary.
_MIR_TITLE_RE = re.compile(r"\[mir\]|\bmir\b", re.IGNORECASE)

# Bound the best-effort search so a review run never fans out into dozens of
# Launchpad round-trips: at most this many candidate source names, and at most
# this many MIR-matching tasks enriched per candidate.
_MIR_HISTORY_MAX_CANDIDATES = 6
_MIR_HISTORY_MAX_TASKS_PER_NAME = 10
# At most this many explicit "LP: #NNNN" references from bug text are fetched
# directly (each is one API call). The number of such references in a real MIR
# bug is small; the bound keeps a pathological bug from fanning out.
_MIR_HISTORY_MAX_EXPLICIT_REFS = 5

# Parse the source name from a "[MIR] <name>" bug title. Used to derive the
# predecessor source name from a directly-fetched prior-MIR bug title.
_MIR_TITLE_NAME_CAPTURE_RE = re.compile(r"^\[mir\]\s+(.+?)\s*$", re.IGNORECASE)


def _mir_history_bug_text(ctx: RunContext) -> str:
    """Return the combined bug text to scan for predecessor references.

    Mirrors review_type._reporter_text(): title, description, comments, and
    reporter MIR content. Kept local to avoid an evidence -> review_type import
    (review_type is a downstream consumer of this adapter's output, not a
    dependency of evidence collection).
    """
    parts: list[str] = []
    parts.append(str(getattr(ctx, "reporter_mir_content", "") or ""))
    bug = getattr(ctx, "bug", None)
    if isinstance(bug, dict):
        parts.append(str(bug.get("title", "") or ""))
        parts.append(str(bug.get("description", "") or ""))
        for comment in bug.get("comments", []) or []:
            parts.append(str(comment or ""))
    return "\n".join(p for p in parts if p)


def _mir_history_predecessor_refs(ctx: RunContext) -> list[predecessor_refs.PredecessorRef]:
    """Extract rename/predecessor references from the bug text.

    Best-effort and dependency-free: returns an empty list when bug text is
    empty or contains no predecessor references.
    """
    pkg = str(getattr(ctx, "source_package", "") or "")
    text = _mir_history_bug_text(ctx)
    return predecessor_refs.extract_predecessor_refs(text, pkg)


def _mir_history_candidate_names(ctx: RunContext) -> list[str]:
    """Return distinct candidate source names to probe for a prior MIR bug.

    The current source package is always first. Predecessor/sibling names from
    the cve-search-terms adapter, archive-neighbour names from dup-search, and
    rename/predecessor names extracted directly from the bug text (e.g.
    "mysql-9.7 to replace mysql-8.4") are added when available, so a renamed
    or split source can be linked back to the name it was reviewed under. All
    lookups are read defensively; missing or failed adapters simply contribute
    nothing.
    """
    names: list[str] = []
    seen: set[str] = set()

    def _add(raw: object) -> None:
        name = str(raw or "").strip()
        key = name.lower()
        if name and key not in seen:
            seen.add(key)
            names.append(name)

    _add(getattr(ctx, "source_package", ""))

    adapters = {}
    evidence = getattr(ctx, "evidence", None)
    if isinstance(evidence, dict):
        adapters = evidence.get("adapters", {}) or {}

    cve_terms = adapters.get("cve-search-terms", {})
    if isinstance(cve_terms, dict):
        for term in cve_terms.get("terms", []) or []:
            if isinstance(term, dict) and term.get("kind") == "predecessor":
                _add(term.get("term"))

    dup_search = adapters.get("dup-search", {})
    if isinstance(dup_search, dict):
        for cand in dup_search.get("candidates", []) or []:
            if isinstance(cand, dict):
                _add(cand.get("name"))

    # Predecessor names extracted directly from the bug text. These are the
    # strongest signal for a rename (the reporter says "replace mysql-8.4")
    # and are not available from the cve-search-terms or dup-search adapters.
    for ref in _mir_history_predecessor_refs(ctx):
        if ref.name:
            _add(ref.name)

    return names[:_MIR_HISTORY_MAX_CANDIDATES]


@adapter(AdapterID.LP_MIR_HISTORY)
def collect_lp_mir_history(ctx: RunContext) -> LPMirHistoryResult:
    """Search Launchpad for prior MIR bugs on this source or a predecessor name.

    Best-effort: probes each candidate source name's bug tasks with a server-side
    ``search_text=MIR`` filter and keeps tasks whose (enriched) title looks like
    a Main Inclusion Review bug. Used by review-type detection to recognise a
    source that was renamed or reorganised from something already in main. A
    missing package (404) or transient API hiccup for one candidate is skipped
    rather than failing the adapter.

    Explicit ``LP: #NNNN`` cross-references in the bug text (e.g. "MIR for
    mysql-8.4 - LP: #2089720") are fetched directly and title-confirmed, so a
    renamed source's prior MIR bug is recognised from the reporter's own words
    even when the predecessor name was not probed via searchTasks.
    """
    pkg = getattr(ctx, "source_package", "")
    if not pkg:
        raise AdapterError("source_package not set")

    candidate_names = _mir_history_candidate_names(ctx)
    prior_mir_bugs: list[dict[str, Any]] = []
    seen_bug_ids: set[str] = set()

    for name in candidate_names:
        search_url = (
            f"https://api.launchpad.net/devel/ubuntu/+source/{urllib.parse.quote(name)}"
            "?ws.op=searchTasks&search_text=MIR"
        )
        try:
            page = _fetch_json(search_url)
        except urllib.error.HTTPError as exc:
            # 404 = no such source under this name; anything else = transient.
            log.debug("lp-mir-history: search for %s failed (HTTP %s)", name, exc.code)
            continue
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            log.debug("lp-mir-history: search for %s failed: %s", name, exc)
            continue

        entries = page.get("entries", [])
        if not isinstance(entries, list):
            continue

        enriched = 0
        for task in entries:
            if enriched >= _MIR_HISTORY_MAX_TASKS_PER_NAME:
                break
            bug_link = str(task.get("bug_link") or "").strip()
            web_link = str(task.get("web_link") or "").strip()
            bug_id = bug_link.rstrip("/").split("/")[-1] if bug_link else ""
            if not bug_id or bug_id in seen_bug_ids:
                continue

            title = ""
            status = str(task.get("status") or "").strip()
            if bug_link:
                try:
                    bug_data = _fetch_json(bug_link)
                    title = str(bug_data.get("title") or "").strip()
                except Exception as exc:
                    log.debug("lp-mir-history: could not enrich bug %s: %s", bug_id, exc)
            enriched += 1

            if not _MIR_TITLE_RE.search(title):
                continue

            seen_bug_ids.add(bug_id)
            prior_mir_bugs.append(
                {
                    "id": bug_id,
                    "title": title,
                    "status": status,
                    "web_link": web_link,
                    "matched_name": name,
                }
            )

    # --- explicit "LP: #NNNN" cross-references from the bug text -------------
    # A reporter almost always links the prior MIR bug explicitly (e.g.
    # "MIR for mysql-8.4 - LP: #2089720"). Fetch those directly and
    # title-confirm them, so the predecessor is recognised even when the
    # predecessor name was not probed via searchTasks (e.g. because it was not
    # a cve-search-terms predecessor and not a dup-search candidate).
    text_refs = _mir_history_predecessor_refs(ctx)
    explicit_refs = predecessor_refs.explicit_bug_ids(text_refs)
    # Index refs by bug_id for O(1) name fallback lookup below.
    ref_name_by_bug_id: dict[str, str] = {}
    for ref in text_refs:
        if ref.bug_id and ref.name and ref.bug_id not in ref_name_by_bug_id:
            ref_name_by_bug_id[ref.bug_id] = ref.name

    for bug_id in explicit_refs[:_MIR_HISTORY_MAX_EXPLICIT_REFS]:
        if bug_id in seen_bug_ids:
            continue
        bug_url = f"https://api.launchpad.net/devel/bugs/{bug_id}"
        try:
            bug_data = _fetch_json(bug_url)
        except urllib.error.HTTPError as exc:
            log.debug("lp-mir-history: direct fetch of bug %s failed (HTTP %s)", bug_id, exc.code)
            continue
        except (urllib.error.URLError, json.JSONDecodeError) as exc:
            log.debug("lp-mir-history: direct fetch of bug %s failed: %s", bug_id, exc)
            continue

        title = str(bug_data.get("title") or "").strip()
        if not _MIR_TITLE_RE.search(title):
            continue

        # Derive the predecessor source name from a "[MIR] <name>" title.
        matched_name = ""
        name_match = _MIR_TITLE_NAME_CAPTURE_RE.match(title)
        if name_match:
            candidate = name_match.group(1).strip()
            if candidate.lower() != pkg.lower():
                matched_name = candidate
        # Fall back to the name paired with this bug id in the bug text, if any.
        if not matched_name:
            matched_name = ref_name_by_bug_id.get(bug_id, "")

        seen_bug_ids.add(bug_id)
        prior_mir_bugs.append(
            {
                "id": bug_id,
                "title": title,
                "status": "",
                "web_link": f"https://bugs.launchpad.net/bugs/{bug_id}",
                "matched_name": matched_name or pkg,
                "provenance": "bug-text-ref",
            }
        )

    log.debug(
        "lp-mir-history: %d prior MIR bug(s) across %d candidate name(s) for %s",
        len(prior_mir_bugs),
        len(candidate_names),
        pkg,
    )
    return {
        "status": "ok",
        "source_package": pkg,
        "candidate_names": candidate_names,
        "prior_mir_bugs": prior_mir_bugs,
    }


def _parse_lp_date(value: object) -> datetime | None:
    """Parse a Launchpad date string into a tz-naive UTC datetime, or None."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "none":
        return None
    text = text.replace("Z", "+00:00")
    for candidate in (text, text.split(".")[0], text.split(" ")[0]):
        try:
            parsed = datetime.fromisoformat(candidate)
        except ValueError:
            continue
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    return None


def summarise_release_cadence(history: list[dict]) -> dict:
    """Characterise distro publishing cadence from publish-history entries.

    Each history item carries ``version`` and ``date_published``. The earliest
    publication date per distinct source version is taken, the dates are sorted,
    and the average interval is classified (thresholds are deliberately soft):

      good      >= ~1 upload per 6 months (average interval <= 183 days)
      slow      ~ 1 upload per year (average interval <= 400 days)
      sporadic  less frequent than that
      unknown   fewer than 2 dated versions to compare
    """
    by_version: dict[str, datetime] = {}
    for entry in history:
        version = str(entry.get("version") or "").strip()
        parsed = _parse_lp_date(entry.get("date_published"))
        if not version or parsed is None:
            continue
        if version not in by_version or parsed < by_version[version]:
            by_version[version] = parsed

    dates = sorted(by_version.values())
    if len(dates) < 2:
        return {"releases": len(dates), "descriptor": "unknown"}

    intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    avg_interval = sum(intervals) / len(intervals)
    if avg_interval <= 183:
        descriptor = "good"
    elif avg_interval <= 400:
        descriptor = "slow"
    else:
        descriptor = "sporadic"

    return {
        "releases": len(dates),
        "span_days": (dates[-1] - dates[0]).days,
        "avg_interval_days": round(avg_interval, 1),
        "first": dates[0].date().isoformat(),
        "last": dates[-1].date().isoformat(),
        "descriptor": descriptor,
    }


@adapter(AdapterID.LP_PACKAGE_API)
def collect_lp_package_api(ctx: RunContext) -> LPPackageAPIResult:
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
        lp = launchpad_client.login_anonymously("auto-mir-pkg")
        ubuntu = lp.distributions["ubuntu"]
        lp_series = launchpad_client.resolve_series(ubuntu, series_name)
    except launchpad_client.LaunchpadUnavailableError as exc:
        raise AdapterError(str(exc)) from exc

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

    current_component = _resolve_current_component(ubuntu_publish_history)

    # Fetch the cross-series publishing history (all Ubuntu series) so the
    # update cadence can be characterised over a meaningful time span rather
    # than just the development series (which often holds only a few records).
    all_publish_history: list[dict] = []
    try:
        archive = ubuntu.main_archive
        published_all = archive.getPublishedSources(
            source_name=pkg,
            exact_match=True,
            order_by_date=True,
        )
        for pub in list(published_all)[:100]:
            try:
                all_publish_history.append(
                    {
                        "version": pub.source_package_version,
                        "date_published": str(pub.date_published),
                        "pocket": pub.pocket,
                        "status": pub.status,
                    }
                )
            except Exception:
                continue
    except Exception as exc:
        log.warning("Could not fetch cross-series LP history for %s: %s", pkg, exc)

    release_cadence = summarise_release_cadence(all_publish_history or ubuntu_publish_history)

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
        "lp-package-api: current version %s, %d publish record(s), "
        "%d cross-series record(s), cadence=%s, %d uploader(s), component=%s",
        current_version or "unknown",
        len(ubuntu_publish_history),
        len(all_publish_history),
        release_cadence.get("descriptor", "unknown"),
        len(uploaders),
        current_component,
    )
    return {
        "status": "ok",
        "ubuntu_publish_history": ubuntu_publish_history,
        "all_publish_history": all_publish_history,
        "release_cadence": release_cadence,
        "current_version": current_version,
        "current_component": current_component,
        "upload_history": upload_history,
        "uploaders": uploaders,
        "source_url": f"https://launchpad.net/ubuntu/+source/{pkg}",
    }


def _resolve_current_component(ubuntu_publish_history: list[dict]) -> str:
    """Return the archive component (main/universe/...) currently governing this source.

    ``ubuntu_publish_history`` is ordered newest-first (``order_by_date=True``)
    and covers every pocket in the target series, mirroring what ``rmadison``
    shows for that series. The newest ``Published`` record is authoritative;
    if none has that status (e.g. only a still-processing upload is known),
    fall back to the newest record of any status. Returns "unknown" when no
    record or component data is available, so callers never mistake an
    unresolved lookup for a real "main" or "universe" answer.
    """
    for entry in ubuntu_publish_history:
        if entry.get("status") == "Published" and entry.get("component"):
            return str(entry["component"])
    for entry in ubuntu_publish_history:
        if entry.get("component"):
            return str(entry["component"])
    return "unknown"


def _fetch_json(url: str) -> Any:
    """Fetch and decode JSON from a remote endpoint."""
    return http_utils.get_json(url)


def _fetch_text(url: str) -> str:
    """Fetch and decode text from a remote endpoint."""
    return http_utils.get_text(url)


def _download_oval_xz(url: str) -> bytes:
    """Download an OVAL XZ payload with resilient retry/backoff."""
    return http_utils.get_bytes(url)


def _download_autopkgtest_db(url: str, tmp_path: str) -> None:
    """Download autopkgtest DB to a local file path with resilient retry/backoff."""
    http_utils.download_to_file(url, tmp_path)


# The autopkgtest SQLite database is large (hundreds of MB). Several adapters
# need to query it (the package itself and each reverse-dep consumer), so it is
# downloaded once per run and cached on the context. The cached temp file is
# removed by ``cleanup_cached_autopkgtest_db`` at the end of evidence collection.
_AUTOPKGTEST_DB_URL = "https://autopkgtest.ubuntu.com/static/autopkgtest.db"
_AUTOPKGTEST_DB_CACHE_ATTR = "_autopkgtest_db_path"


def _get_cached_autopkgtest_db(ctx: RunContext) -> str:
    """Return a local path to the autopkgtest DB, downloading it once per run.

    The path is cached on ``ctx`` so repeated lookups (package + consumers)
    reuse a single download. Raises AdapterError on download failure.
    """
    cached = getattr(ctx, _AUTOPKGTEST_DB_CACHE_ATTR, None)
    if isinstance(cached, str) and cached and Path(cached).exists():
        return cached

    log.debug("Downloading autopkgtest SQLite database: %s", _AUTOPKGTEST_DB_URL)
    try:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_path = tmp.name
        _download_autopkgtest_db(_AUTOPKGTEST_DB_URL, tmp_path)
    except urllib.error.HTTPError as exc:
        Path(tmp_path).unlink(missing_ok=True)
        raise AdapterError(f"autopkgtest DB download HTTP error {exc.code}") from exc
    except Exception as exc:
        Path(tmp_path).unlink(missing_ok=True)
        raise AdapterError(f"autopkgtest DB download failed: {exc}") from exc

    try:
        setattr(ctx, _AUTOPKGTEST_DB_CACHE_ATTR, tmp_path)
    except (AttributeError, TypeError):
        # Some minimal contexts do not accept new attributes; the caller then
        # simply re-downloads on the next lookup and cleanup is a no-op.
        pass
    return tmp_path


def cleanup_cached_autopkgtest_db(ctx: RunContext) -> None:
    """Remove the cached autopkgtest DB temp file, if any, at end of a run."""
    cached = getattr(ctx, _AUTOPKGTEST_DB_CACHE_ATTR, None)
    if not isinstance(cached, str) or not cached:
        return
    try:
        Path(cached).unlink(missing_ok=True)
        log.debug("Removed cached autopkgtest DB: %s", cached)
    except OSError as exc:
        log.warning("Could not remove cached autopkgtest DB %s: %s", cached, exc)
    finally:
        try:
            setattr(ctx, _AUTOPKGTEST_DB_CACHE_ATTR, None)
        except (AttributeError, TypeError):
            pass


def _query_autopkgtest_for_package(
    db_path: str, package: str, candidates: list[str]
) -> tuple[list[Any], str]:
    """Query the autopkgtest DB for a package across candidate releases.

    Returns the latest result rows and the release they came from. Rows are
    ``(arch, exitcode, version, run_id)`` tuples. The first candidate release
    with any results wins; if none match, empty rows are returned for the first
    candidate. Raises sqlite3.DatabaseError on a malformed database.
    """
    query = """
        SELECT t.arch, r.exitcode, r.version, r.run_id
        FROM test t
        JOIN result r ON t.id = r.test_id
        WHERE t.package = ? AND t.release = ?
        ORDER BY r.run_id DESC
        LIMIT 100
        """
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        rows: list[Any] = []
        resolved_release = candidates[0] if candidates else ""
        for release in candidates:
            cursor.execute(query, (package, release))
            fetched = cursor.fetchall()
            if fetched:
                return fetched, release
        return rows, resolved_release
    finally:
        conn.close()


def _summarize_autopkgtest_rows(rows: list[Any]) -> dict[str, list]:
    """Summarize per-arch autopkgtest rows into passing/failing/results."""
    arch_latest: dict[str, dict[str, Any]] = {}
    for arch, exitcode, version, run_id in rows:
        if arch not in arch_latest:
            status = "pass" if exitcode == 0 else "fail"
            arch_latest[arch] = {
                "arch": arch,
                "version": version,
                "status": status,
                "run_id": run_id,
            }
    passing = sorted(a for a, info in arch_latest.items() if info["status"] == "pass")
    failing = sorted(a for a, info in arch_latest.items() if info["status"] == "fail")
    return {
        "test_results": list(arch_latest.values()),
        "passing_arches": passing,
        "failing_arches": failing,
    }


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
def collect_debian_bts(ctx: RunContext) -> DebianBTSResult:
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


def _collect_upstream_search_terms(
    ctx: RunContext, package_name: str
) -> tuple[list[str], str, list[str]]:
    """Return search terms plus the Homepage hint and other (watch) hints.

    debian/control's ``Homepage:`` field is kept distinct from debian/watch
    URLs: it is usually the project's own authoritative page, while
    debian/watch typically points at a download/tarball location that can
    live on an entirely different domain (e.g. an author's personal site
    hosting release tarballs). Keeping them separate lets
    ``_select_upstream_project`` weight a Homepage match higher without
    diluting it into one flat, unordered hint list.
    """
    packaging = ctx.evidence.get("adapters", {}).get("packaging-source", {})
    if not isinstance(packaging, dict):
        packaging = {}

    debian_watch = str(packaging.get("debian_watch") or "")
    debian_control = str(packaging.get("debian_control") or "")

    homepage_hint = _extract_homepage_from_control(debian_control)
    watch_url_hints = [
        url for url in _extract_urls_from_watch(debian_watch) if url != homepage_hint
    ]
    all_hints = _dedupe_preserve_order(([homepage_hint] if homepage_hint else []) + watch_url_hints)

    search_terms = [package_name]
    normalized_package = _normalize_project_name(package_name)
    if normalized_package and normalized_package != package_name:
        search_terms.append(normalized_package)
    for url in all_hints:
        search_terms.extend(_project_terms_from_url(url))

    return (
        _dedupe_preserve_order([term for term in search_terms if term]),
        homepage_hint,
        watch_url_hints,
    )


def _select_upstream_project(
    projects: list[dict[str, Any]],
    package_name: str,
    candidate_name: str,
    homepage_hint: str,
    watch_url_hints: list[str],
) -> dict[str, Any] | None:
    """Return the best upstream project match for a source package name.

    Scoring tiers (highest wins, ties broken by first-seen): a
    release-monitoring.org project whose own homepage/url corresponds to
    debian/control's Homepage hint (100) outranks an exact candidate-name
    match (90), which outranks an exact package-name match (80), which
    outranks a project matching only a debian/watch-derived hint (70, since
    that URL is often just a download location, not the project's real
    home), which outranks a partial name match (60). This keeps Homepage as
    the practical default winner while still leaving it a normal, scorable
    (and thus outscoreable) signal rather than a hard override.
    """
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
        if homepage_hint and any(
            _urls_look_related(project_url, homepage_hint) for project_url in project_urls
        ):
            score = max(score, 100)

        if name == normalized_candidate and normalized_candidate:
            score = max(score, 90)
        if name == normalized_pkg and normalized_pkg:
            score = max(score, 80)

        if any(
            _urls_look_related(project_url, hint)
            for project_url in project_urls
            for hint in watch_url_hints
        ):
            score = max(score, 70)

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


def _verified_upstream_url(candidates: list[str]) -> str:
    """Return the first candidate URL that actually resolves, else "".

    URLs suggested to a reporter should be verified to exist first: a stale
    or wrong upstream URL (e.g. a domain that used to host the project but
    no longer does) is worse than no URL at all, since the reporter is
    likely to trust a tool-provided value. Tries candidates in the given
    preference order (already Homepage-first where applicable) and falls
    through to the next one on a verification failure, rather than giving up
    after the first candidate -- this is still bounded (at most a handful of
    fast, timeout-capped checks) and lets a genuinely good URL (e.g. the
    verified Homepage) win even when a higher-preference candidate (e.g. a
    release-monitoring.org project's own homepage) turns out to be stale.
    """
    for candidate in _dedupe_preserve_order([url for url in candidates if url]):
        if http_utils.check_url_exists(candidate):
            return candidate
    return ""


@adapter(AdapterID.UPSTREAM_TRACKER)
def collect_upstream_tracker(ctx: RunContext) -> UpstreamTrackerResult:
    """Query release-monitoring.org for upstream release history.

    This is intentionally heuristic: it starts from the source package name and
    returns the best matching project entry when an exact match is not available.
    Finding no release-monitoring.org match is a normal, expected outcome for
    many packages, not an adapter failure: when the package's own
    debian/control Homepage or debian/watch already names an upstream URL,
    that URL is used directly rather than discarded. Only genuine
    transport/parse errors raise ``AdapterError``. Whatever URL is finally
    chosen is verified to actually resolve (see ``_verified_upstream_url``)
    before being returned; an unverified URL is dropped rather than
    presented to the reporter as if it were confidently detected.
    """
    pkg = ctx.source_package
    if not pkg:
        raise AdapterError("source_package not set")

    search_terms, homepage_hint, watch_url_hints = _collect_upstream_search_terms(ctx, pkg)
    hint_candidates = _dedupe_preserve_order(
        ([homepage_hint] if homepage_hint else []) + watch_url_hints
    )
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

        project = _select_upstream_project(projects, pkg, term, homepage_hint, watch_url_hints)
        if project is not None:
            break

    if project is None:
        if hint_candidates:
            log.debug(
                "upstream-tracker: no release-monitoring.org match for %s; "
                "using debian/control or debian/watch URL hint instead",
                pkg,
            )
        else:
            log.debug("upstream-tracker: no upstream project match found for %s", pkg)
        upstream_url = _verified_upstream_url(hint_candidates)
        if hint_candidates and not upstream_url:
            log.debug(
                "upstream-tracker: candidate URL(s) for %s did not resolve, "
                "treating upstream project as undetected",
                pkg,
            )
        return {
            "status": "ok",
            "upstream_url": upstream_url,
            "upstream_name": "",
            "latest_version": "",
            "open_issues_count": 0,
            "recent_releases": [],
            "last_release_date": "",
        }

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
    project_url = str(project.get("homepage") or project.get("url") or "").strip()
    upstream_url = _verified_upstream_url([project_url, *hint_candidates])
    if not upstream_url and (project_url or hint_candidates):
        log.debug(
            "upstream-tracker: candidate URL(s) for %s did not resolve, omitting upstream_url",
            pkg,
        )
    return {
        "status": "ok",
        "upstream_url": upstream_url,
        "upstream_name": str(project.get("name") or "").strip(),
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


def _builds_from_newest_publication(archive, lp_series, pkg: str) -> list[Any]:
    """Return build records for the newest published source in the target series.

    Fallback path used only when packaging-source could not pin an exact
    analysed version (e.g. no publish history at all in the target pocket).
    Uses ``archive.getPublishedSources`` to find the most recent publication
    of ``pkg`` in ``lp_series`` and returns its per-architecture builds via
    ``getBuilds()``. Returns an empty list (never raises) so the caller can
    fall back to the older getBuildRecords path when this yields nothing.
    """
    for kwargs in (
        {"source_name": pkg, "distro_series": lp_series, "exact_match": True},
        {"source_name": pkg, "exact_match": True},
    ):
        try:
            pubs = list(archive.getPublishedSources(**kwargs))
        except Exception:
            continue
        if not pubs:
            continue
        # getPublishedSources returns newest first; use the most recent
        # publication that can enumerate builds.
        for pub in pubs:
            builds = launchpad_client.builds_for_publication(pub)
            if builds:
                return builds
    return []


@adapter(AdapterID.LP_BUILD_API)
def collect_lp_build_api(ctx: RunContext) -> LPBuildAPIResult:
    """Fetch Launchpad build-state information for the exact analysed version.

    Pinned to version-resolution's ``resolved_version``/``resolved_pocket`` so
    the per-architecture build state reported here always matches the exact
    source (and, for the local architecture, the binaries fetch-build later
    downloads) that the rest of the evidence was collected against - not
    just "whichever publication happens to have any builds", which could
    silently be a different version than the one actually analysed.

    Reuses the same build/binary classification as version-resolution (see
    ``evidence.launchpad_client.summarize_build_completeness``): an
    architecture with a published binary but no distinct Build record (e.g. a
    package carried over unchanged into a newly-opened devel series, where
    binaries are copied across without a fresh per-series build) is reported
    as built here too, instead of silently vanishing from this list - which
    previously left CB-1 unable to confirm the package does not FTBFS even
    though it plainly is available and working.
    """
    pkg = ctx.source_package
    series_name = ctx.series or "devel"
    if not pkg:
        raise AdapterError("source_package not set")

    version_resolution = ctx.evidence.get("adapters", {}).get("version-resolution", {})
    analyzed_version = (
        str(version_resolution.get("resolved_version", "") or "").strip()
        if isinstance(version_resolution, dict)
        else ""
    )
    analyzed_pocket = (
        str(version_resolution.get("resolved_pocket", "") or "").strip()
        if isinstance(version_resolution, dict)
        else ""
    )

    try:
        lp = launchpad_client.login_anonymously("auto-mir-build")
        ubuntu = lp.distributions["ubuntu"]
        lp_series = launchpad_client.resolve_series(ubuntu, series_name)
    except launchpad_client.LaunchpadUnavailableError as exc:
        raise AdapterError(str(exc)) from exc

    try:
        archive = ubuntu.main_archive
    except Exception as exc:
        raise AdapterError(f"Could not resolve the Ubuntu primary archive: {exc}") from exc

    build_records: list[Any] = []
    binary_records: list[Any] = []
    if analyzed_version:
        pub = launchpad_client.find_source_publication(archive, lp_series, pkg, analyzed_version)
        if pub is not None:
            build_records = launchpad_client.builds_for_publication(pub)
            binary_records = launchpad_client.binaries_for_publication(pub)
        if not build_records and not binary_records:
            log.warning(
                "lp-build-api: no Launchpad build or published-binary records found "
                "for the exact analysed version %s of %s (%s pocket); the publication "
                "may not carry build records (e.g. a pure metadata/override change)",
                analyzed_version,
                pkg,
                analyzed_pocket or "unknown",
            )
    else:
        # version-resolution could not pin a version (e.g. no publish history
        # at all in the target pocket); fall back to the newest publication
        # that has any build records.
        build_records = _builds_from_newest_publication(archive, lp_series, pkg)

    if not build_records and not binary_records:
        try:
            source_pkg = ubuntu.getSourcePackage(name=pkg)
        except Exception as exc:
            raise AdapterError(
                f"Could not find source package '{pkg}' on Launchpad: {exc}"
            ) from exc
        for attr_name in ("getBuildRecords", "builds"):
            candidate = getattr(source_pkg, attr_name, None)
            if candidate is None:
                continue
            try:
                build_records = list(candidate() if callable(candidate) else candidate)
            except TypeError:
                build_records = list(candidate)
            break

    if not build_records and not binary_records and hasattr(lp_series, "getBuildRecords"):
        try:
            build_records = list(lp_series.getBuildRecords(source_package_name=pkg))
        except TypeError:
            try:
                build_records = list(lp_series.getBuildRecords(source_name=pkg))
            except Exception:
                build_records = []
        except Exception:
            build_records = []

    completeness = launchpad_client.summarize_build_completeness(build_records, binary_records)

    builds: list[dict] = []
    seen_arches: set[str] = set()
    for record in build_records:
        arch_tag = launchpad_client.build_attr(
            record, "arch_tag", "arch_tag_name", "architecture_tag"
        )
        seen_arches.add(arch_tag)
        builds.append(
            {
                "arch_tag": arch_tag,
                "build_state": launchpad_client.build_attr(
                    record, "buildstate", "build_state", "status"
                ),
                "build_reason": launchpad_client.build_attr(
                    record, "build_reason", "build_summary", "status_message"
                ),
                "version": launchpad_client.build_attr(record, "source_package_version", "version"),
                "date_created": launchpad_client.build_attr(
                    record, "date_created", "datebuilt", "date_built"
                ),
                "pocket": launchpad_client.build_attr(record, "pocket"),
                "archive": launchpad_client.build_attr(record, "archive"),
                "web_link": launchpad_client.build_attr(record, "web_link", "self_link"),
                # Needed by fetch-build to download the local architecture's
                # official build artifacts instead of building locally.
                "build_log_url": launchpad_client.build_attr(record, "build_log_url"),
                "changesfile_url": launchpad_client.build_attr(record, "changesfile_url"),
                "buildinfo_url": launchpad_client.build_attr(record, "buildinfo_url"),
            }
        )

    # Architectures with a published binary but no distinct Build record (see
    # summarize_build_completeness's "carried_over" fallback) are added too,
    # so this list never silently under-reports an architecture that is
    # plainly available in the archive. The published binary itself still
    # references the real build that produced it (possibly in an older
    # series' publication), so that real build's log/changes/buildinfo URLs
    # are resolved from there instead of being left empty - otherwise a
    # carried-over package (e.g. copied unchanged into a newly-opened devel
    # series) would always report "no build log available" even though a
    # real, working log exists under its original series.
    for entry in completeness["entries"]:
        if entry["arch_tag"] in seen_arches:
            continue
        original_build = launchpad_client.original_build_for_arch(binary_records, entry["arch_tag"])
        builds.append(
            {
                "arch_tag": entry["arch_tag"],
                "build_state": "Successfully built",
                "build_reason": entry["build_state"],
                "version": launchpad_client.build_attr(
                    original_build,
                    "source_package_version",
                    "version",
                    default=analyzed_version,
                ),
                "date_created": launchpad_client.build_attr(
                    original_build, "date_created", "datebuilt", "date_built"
                ),
                "pocket": launchpad_client.build_attr(
                    original_build, "pocket", default=analyzed_pocket
                ),
                "archive": launchpad_client.build_attr(original_build, "archive"),
                "web_link": launchpad_client.build_attr(original_build, "web_link", "self_link"),
                "build_log_url": launchpad_client.build_attr(original_build, "build_log_url"),
                "changesfile_url": launchpad_client.build_attr(original_build, "changesfile_url"),
                "buildinfo_url": launchpad_client.build_attr(original_build, "buildinfo_url"),
            }
        )

    builds.sort(key=lambda entry: (entry["arch_tag"], entry["version"]))

    log.debug(
        "lp-build-api: %d build record(s) for %s %s in %s",
        len(builds),
        pkg,
        analyzed_version or "(unpinned)",
        series_name,
    )
    return {
        "status": "ok",
        "source_package": pkg,
        "series": series_name,
        "builds": builds,
        "source_url": f"https://launchpad.net/ubuntu/+source/{pkg}",
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
def collect_cve_search_terms(ctx: RunContext) -> CVESearchTermsResult:
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


def _llm_predecessor_terms(ctx: RunContext, pkg: str) -> list[dict[str, str]]:
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
    ctx: RunContext,
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

_CVELIST_RELEASES_API = "https://api.github.com/repos/CVEProject/cvelistV5/releases?per_page=40"
# Marker substring identifying the daily "all CVEs" baseline asset. Matched with
# `in` + a ".zip" suffix check rather than an exact suffix: upstream has at times
# uploaded this asset as "<date>_all_CVEs_at_midnight.zip.zip" (a doubled
# extension, apparently a quirk of their release automation) instead of a single
# ".zip". Matching loosely keeps discovery working across that kind of naming
# drift without needing a code change every time upstream's naming shifts.
_CVELIST_BASELINE_MARKER = "_all_CVEs_at_midnight"


def _cvelist_discover_baseline(url: str = _CVELIST_RELEASES_API) -> tuple[str, str]:
    """Return (asset_name, download_url) of the newest midnight baseline zip."""
    releases = _fetch_json(url)
    if not isinstance(releases, list):
        raise AdapterError("unexpected releases payload from GitHub API")
    for release in releases:
        assets = release.get("assets", []) if isinstance(release, dict) else []
        for asset in assets:
            if not isinstance(asset, dict):
                continue
            name = str(asset.get("name") or "")
            if _CVELIST_BASELINE_MARKER not in name or not name.endswith(".zip"):
                continue
            download_url = str(asset.get("browser_download_url") or "")
            if download_url:
                return name, download_url
    raise AdapterError("no '*_all_CVEs_at_midnight.zip' asset found in recent releases")


@adapter(AdapterID.CVELIST_SCAN)
def collect_cvelist_scan(ctx: RunContext) -> CvelistScanResult:
    """Identify candidate CVEs by scanning cvelistV5 baseline corpus on the host."""
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

    try:
        from evidence.cvelist_scan_invm import scan_zip

        baseline_name, download_url = _cvelist_discover_baseline()
        baseline_path = ""
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            baseline_path = tmp.name
        try:
            http_utils.download_to_file(download_url, baseline_path)
            candidates = scan_zip(baseline_path, terms)
        finally:
            if baseline_path:
                Path(baseline_path).unlink(missing_ok=True)
    except urllib.error.HTTPError as exc:
        raise AdapterError(f"cvelist-scan HTTP error {exc.code}: {exc.reason}") from exc
    except Exception as exc:
        raise AdapterError(f"cvelist-scan failed on host: {exc}") from exc

    log.debug(
        "cvelist-scan: %d candidate CVE(s) for %s from baseline %s (terms: %s)",
        len(candidates),
        pkg,
        baseline_name,
        ", ".join(scanned_terms),
    )
    return {
        "status": "ok",
        "source_package": pkg,
        "baseline": baseline_name,
        "scanned_terms": scanned_terms,
        "candidates": candidates,
        "total_candidate_count": len(candidates),
    }


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


@adapter(AdapterID.NVD_ENRICH)
def collect_nvd_enrich(ctx: RunContext) -> NvdEnrichResult:
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
def collect_ubuntu_cve_tracker(ctx: RunContext) -> UbuntuCVETrackerResult:
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
        xz_data = _download_oval_xz(url)
    except urllib.error.HTTPError as exc:
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
def collect_autopkgtest(ctx: RunContext) -> AutopkgtestResult:
    """Query autopkgtest SQLite database for package test results.

    Downloads https://autopkgtest.ubuntu.com/static/autopkgtest.db (once per
    run, cached on ctx), queries the results table for the package and series,
    and summarizes by architecture.
    """
    pkg = ctx.source_package
    series = ctx.series or "devel"
    if not pkg:
        raise AdapterError("source_package not set")

    db_path = _get_cached_autopkgtest_db(ctx)

    # The DB is keyed by concrete release codename, not by the alias "devel".
    # Resolve candidates (devel codename first, then latest supported stable as a
    # fallback for a fresh cycle with no results yet) so a real test suite is not
    # missed just because the series was passed as "devel".
    candidates = _autopkgtest_release_candidates(series)

    try:
        rows, resolved_release = _query_autopkgtest_for_package(db_path, pkg, candidates)
    except sqlite3.DatabaseError as exc:
        log.warning("autopkgtest DB query failed: %s", exc)
        return {
            "status": "ok",
            "package": pkg,
            "series": series,
            "requested_series": series,
            "has_autopkgtest": False,
            "test_results": [],
            "passing_arches": [],
            "failing_arches": [],
            "note": "autopkgtest DB schema not as expected",
        }

    note = ""
    if resolved_release != series:
        note = (
            f"results are from '{resolved_release}' "
            f"(requested series '{series}' resolved/fell back to it)"
        )

    summary = _summarize_autopkgtest_rows(rows)

    log.debug(
        "autopkgtest for %s/%s: %d arches; passing %d, failing %d",
        pkg,
        resolved_release,
        len(summary["test_results"]),
        len(summary["passing_arches"]),
        len(summary["failing_arches"]),
    )

    return {
        "status": "ok",
        "package": pkg,
        "series": resolved_release,
        "requested_series": series,
        "note": note,
        "has_autopkgtest": len(summary["test_results"]) > 0,
        "test_results": summary["test_results"],
        "passing_arches": summary["passing_arches"],
        "failing_arches": summary["failing_arches"],
    }


_AUTOPKGTEST_LOG_URL_TEMPLATE = (
    "https://autopkgtest.ubuntu.com/results/autopkgtest-{series}/{series}/"
    "{arch}/{prefix}/{package}/{run_id}/log.gz"
)


def _autopkgtest_archive_pool_prefix(package: str) -> str:
    """Debian/Ubuntu archive pool-style directory prefix for a package name.

    ``lib``-prefixed packages use their first four characters (e.g.
    ``libgit2`` -> ``libg``); everything else uses just the first character.
    Matches the autopkgtest.ubuntu.com results bucket layout.
    """
    if package.startswith("lib") and len(package) > 3:
        return package[:4]
    return package[:1]


def fetch_autopkgtest_log_excerpt(package: str, series: str, arch: str, run_id: str) -> dict | None:
    """Best-effort fetch of one real autopkgtest execution log, summarised.

    Used as a bounded, opt-in fallback for reporter items that need more than
    the debian/tests/control test definitions to judge test adequacy (see
    REP-QA-TEST-004's ``autopkgtest_log_followup``). Returns ``None`` on any
    failure (network, decompression, decoding, or an unexpected shape) so
    callers can proceed without it rather than fail the run; this is
    genuinely best-effort, not a required evidence source.
    """
    if not package or not series or not arch or not run_id:
        return None
    prefix = _autopkgtest_archive_pool_prefix(package)
    url = _AUTOPKGTEST_LOG_URL_TEMPLATE.format(
        series=series, arch=arch, prefix=prefix, package=package, run_id=run_id
    )
    try:
        compressed = http_utils.get_bytes(url)
        text = gzip.decompress(compressed).decode("utf-8", errors="replace")
    except (OSError, ValueError) as exc:
        log.debug("autopkgtest log fetch failed for %s/%s (%s): %s", package, arch, run_id, exc)
        return None
    return llm_evidence.summarise_build_log(text)


@adapter(AdapterID.CONSUMER_AUTOPKGTESTS)
def collect_consumer_autopkgtests(ctx: RunContext) -> ConsumerAutopkgtestsResult:
    """Look up autopkgtest status for the source's reverse-dependency consumers.

    Reads the consumer source packages discovered by the reverse-deps adapter
    and queries the (already cached) autopkgtest DB for each one. This provides
    the E2E-via-consumers evidence CB-6 needs: whether key consumers of a simple
    library have non-trivial tests that exercise it indirectly.
    """
    series = ctx.series or "devel"
    reverse_deps = ctx.evidence.get("adapters", {}).get("reverse-deps", {})
    consumer_entries = reverse_deps.get("consumers", []) or []

    if not consumer_entries:
        return {
            "status": "ok",
            "series": series,
            "requested_series": series,
            "consumers": [],
            "note": "no reverse-dependency consumers found",
        }

    try:
        db_path = _get_cached_autopkgtest_db(ctx)
    except AdapterError as exc:
        # Best-effort: without the DB we cannot report consumer tests, but the
        # reverse-dep list itself is still useful context for the reviewer.
        return {
            "status": "ok",
            "series": series,
            "requested_series": series,
            "consumers": [],
            "note": f"autopkgtest DB unavailable: {exc}",
        }

    candidates = _autopkgtest_release_candidates(series)
    consumers: list[dict[str, Any]] = []
    for entry in consumer_entries:
        consumer_source = str(entry.get("source", "")).strip()
        if not consumer_source:
            continue
        kind = str(entry.get("kind", ""))
        try:
            rows, resolved = _query_autopkgtest_for_package(db_path, consumer_source, candidates)
        except sqlite3.DatabaseError as exc:
            log.warning("autopkgtest DB query failed for %s: %s", consumer_source, exc)
            consumers.append(
                {
                    "source": consumer_source,
                    "kind": kind,
                    "has_autopkgtest": False,
                    "passing_arches": [],
                    "failing_arches": [],
                    "note": "autopkgtest DB schema not as expected",
                }
            )
            continue
        summary = _summarize_autopkgtest_rows(rows)
        note = ""
        if resolved and resolved != series:
            note = f"results from '{resolved}'"
        consumers.append(
            {
                "source": consumer_source,
                "kind": kind,
                "has_autopkgtest": len(summary["test_results"]) > 0,
                "passing_arches": summary["passing_arches"],
                "failing_arches": summary["failing_arches"],
                "note": note,
            }
        )

    log.debug(
        "consumer-autopkgtests: %d consumer(s), %d with tests",
        len(consumers),
        sum(1 for c in consumers if c["has_autopkgtest"]),
    )
    return {
        "status": "ok",
        "series": series,
        "requested_series": series,
        "consumers": consumers,
    }


@adapter(AdapterID.DEPENDENCY_AUTOPKGTESTS)
def collect_dependency_autopkgtests(ctx: RunContext) -> DependencyAutopkgtestsResult:
    """Look up autopkgtest status for each in-main runtime dependency's source.

    Reads the in-main runtime dependencies discovered by the dep-analysis
    adapter (dependencies that are already in main and so need no MIR of
    their own) and queries the (already cached) autopkgtest DB for each one's
    source package. This gives DEP-4 grounded per-dependency test coverage
    evidence instead of requiring the reviewer/LLM to cross-reference
    dep-analysis and autopkgtest-db by hand.
    """
    series = ctx.series or "devel"
    dep_analysis = ctx.evidence.get("adapters", {}).get("dep-analysis", {})
    deps_in_main = dep_analysis.get("runtime_deps_in_main", []) or []

    if not deps_in_main:
        return {
            "status": "ok",
            "series": series,
            "requested_series": series,
            "dependency_coverage": [],
            "note": "no in-main runtime dependencies found",
        }

    dep_source_lookup = {
        entry.get("package"): entry.get("source_package")
        for entry in dep_analysis.get("dep_source_map", []) or []
    }

    try:
        db_path = _get_cached_autopkgtest_db(ctx)
    except AdapterError as exc:
        # Best-effort: without the DB we cannot report per-dependency test
        # coverage, but the in-main dependency list itself is still useful
        # context for the reviewer.
        return {
            "status": "ok",
            "series": series,
            "requested_series": series,
            "dependency_coverage": [],
            "note": f"autopkgtest DB unavailable: {exc}",
        }

    candidates = _autopkgtest_release_candidates(series)
    dependency_coverage: list[dict[str, Any]] = []
    queried_sources: dict[str, dict[str, Any]] = {}
    for dep_name in deps_in_main:
        source_pkg = dep_source_lookup.get(dep_name) or dep_name
        if source_pkg not in queried_sources:
            try:
                rows, resolved = _query_autopkgtest_for_package(db_path, source_pkg, candidates)
            except sqlite3.DatabaseError as exc:
                log.warning("autopkgtest DB query failed for %s: %s", source_pkg, exc)
                queried_sources[source_pkg] = {
                    "has_autopkgtest": False,
                    "passing_arches": [],
                    "failing_arches": [],
                    "note": "autopkgtest DB schema not as expected",
                }
            else:
                summary = _summarize_autopkgtest_rows(rows)
                note = ""
                if resolved and resolved != series:
                    note = f"results from '{resolved}'"
                queried_sources[source_pkg] = {
                    "has_autopkgtest": len(summary["test_results"]) > 0,
                    "passing_arches": summary["passing_arches"],
                    "failing_arches": summary["failing_arches"],
                    "note": note,
                }
        result = queried_sources[source_pkg]
        dependency_coverage.append(
            {
                "package": dep_name,
                "source": source_pkg,
                "has_autopkgtest": result["has_autopkgtest"],
                "passing_arches": result["passing_arches"],
                "failing_arches": result["failing_arches"],
                "note": result["note"],
            }
        )

    log.debug(
        "dependency-autopkgtests: %d in-main dependency(ies), %d with tests",
        len(dependency_coverage),
        sum(1 for c in dependency_coverage if c["has_autopkgtest"]),
    )
    return {
        "status": "ok",
        "series": series,
        "requested_series": series,
        "dependency_coverage": dependency_coverage,
    }


def _autopkgtest_release_candidates(series: str) -> list[str]:
    """Return release codenames to query in preference order for autopkgtest.

    The autopkgtest DB is keyed by codename. For the "devel" alias we try the
    current development codename first, then the newest supported stable release
    as a fallback (a freshly opened devel cycle may have no results yet). For an
    explicit series we try it first, then the newest supported stable as a
    fallback when it differs.
    """
    devel = _distro_info_lines("--devel")
    devel_codename = devel[0] if devel else None
    supported = _distro_info_lines("--supported")
    newest_stable = next((s for s in reversed(supported) if s != devel_codename), None)

    candidates: list[str] = []
    if series == "devel":
        if devel_codename:
            candidates.append(devel_codename)
    else:
        candidates.append(series)

    if newest_stable and newest_stable not in candidates:
        candidates.append(newest_stable)

    return candidates or [series]

"""Shared Launchpad API session and build-state helpers.

Both host-side adapters (``evidence/host_adapters.py``: lp-package-api,
lp-build-api) and in-guest adapters (``evidence/guest_adapters.py``: the
build-aware version resolution in packaging-source, and the fetch-build
adapter) need to talk to Launchpad's API. This module is the single place
that owns the launchpadlib session and the low-level per-publication build
lookups, so both callers stay consistent and share the same mocking surface
in tests instead of re-implementing login/series/build-record handling.
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from launchpadlib.launchpad import Launchpad as _Launchpad  # type: ignore
except ImportError:  # pragma: no cover - optional runtime dependency
    _Launchpad = None

log = logging.getLogger("auto_mir.evidence.launchpad")


class LaunchpadUnavailableError(RuntimeError):
    """Raised when launchpadlib is missing or the Launchpad API is unreachable."""


# Launchpad IBuild.buildstate values, classified for our purposes. Anything
# not listed here is treated as "unknown" (still surfaced verbatim to the
# user, but counted as neither a pass nor an outright failure).
_BUILD_STATE_SUCCESSFUL = {"successfully built"}
_BUILD_STATE_IN_PROGRESS = {
    "needs building",
    "currently building",
    "uploading build",
    "gathering build output",
}
_BUILD_STATE_FAILED = {
    "failed to build",
    "chroot problem",
    "failed to upload",
    "cancelled build",
    "cancelling build",
    "dependency wait",
    "build for superseded source",
}


def login_anonymously(consumer_name: str) -> Any:
    """Return an anonymous launchpadlib session, or raise LaunchpadUnavailableError."""
    if _Launchpad is None:
        raise LaunchpadUnavailableError(
            "launchpadlib not installed; run: sudo apt install python3-launchpadlib"
        )
    try:
        return _Launchpad.login_anonymously(consumer_name, "production", version="devel")
    except Exception as exc:
        raise LaunchpadUnavailableError(f"Launchpad API connection failed: {exc}") from exc


def resolve_series(ubuntu: Any, requested_series: str) -> Any:
    """Return a Launchpad distro series object for a requested Ubuntu series name."""
    try:
        return ubuntu.getSeries(name_or_version=requested_series)
    except Exception:
        try:
            return ubuntu.current_series
        except Exception as exc:
            raise LaunchpadUnavailableError(
                f"Could not resolve Ubuntu series '{requested_series}': {exc}"
            ) from exc


def build_attr(record: Any, *names: str, default: str = "") -> str:
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


def classify_build_state(raw_state: str) -> str:
    """Classify a raw Launchpad buildstate string.

    Returns one of ``"successful"``, ``"in_progress"``, ``"failed"``,
    ``"unknown"``.
    """
    state = raw_state.strip().lower()
    if state in _BUILD_STATE_SUCCESSFUL:
        return "successful"
    if state in _BUILD_STATE_IN_PROGRESS:
        return "in_progress"
    if state in _BUILD_STATE_FAILED:
        return "failed"
    return "unknown"


def builds_for_publication(pub: Any) -> list[Any]:
    """Return the per-architecture build records for one source publication.

    Never raises: a publication that cannot enumerate builds (e.g. a
    launchpadlib/network hiccup) is treated the same as "no builds yet".
    """
    try:
        return list(pub.getBuilds())
    except Exception:
        return []


def find_source_publication(archive: Any, lp_series: Any, pkg: str, version: str) -> Any | None:
    """Return the ISourcePackagePublishingHistory for an exact source/version, or None."""
    try:
        pubs = list(
            archive.getPublishedSources(
                source_name=pkg,
                version=version,
                distro_series=lp_series,
                exact_match=True,
            )
        )
    except Exception:
        return None
    return pubs[0] if pubs else None


def summarize_build_completeness(builds: list[Any]) -> dict[str, Any]:
    """Summarise a list of raw build records into a completeness verdict.

    Returns a dict with:
      - ``complete``: True only when there is at least one build record and
        every one of them classifies as "successful".
      - ``overall_state``: ``"no_builds"`` | ``"successful"`` |
        ``"in_progress"`` | ``"failed"`` | ``"mixed"`` (some failed/pending,
        some successful).
      - ``entries``: list of ``{"arch_tag", "build_state", "classification"}``.
    """
    entries = []
    classifications: set[str] = set()
    for record in builds:
        arch_tag = build_attr(record, "arch_tag", "arch_tag_name", "architecture_tag")
        raw_state = build_attr(record, "buildstate", "build_state", "status")
        classification = classify_build_state(raw_state)
        classifications.add(classification)
        entries.append(
            {
                "arch_tag": arch_tag or "unknown-arch",
                "build_state": raw_state or "unknown",
                "classification": classification,
            }
        )

    if not entries:
        overall_state = "no_builds"
    elif classifications == {"successful"}:
        overall_state = "successful"
    elif classifications == {"failed"}:
        overall_state = "failed"
    elif "failed" not in classifications and "unknown" not in classifications:
        overall_state = "in_progress"
    else:
        overall_state = "mixed"

    return {
        "complete": overall_state == "successful",
        "overall_state": overall_state,
        "entries": entries,
    }


class BuildCandidate:
    """One (version, pocket) candidate considered while resolving a buildable version."""

    def __init__(self, version: str, pocket: str, completeness: dict[str, Any]):
        self.version = version
        self.pocket = pocket
        self.completeness = completeness

    @property
    def complete(self) -> bool:
        return bool(self.completeness["complete"])

    @property
    def overall_state(self) -> str:
        return str(self.completeness["overall_state"])

    @property
    def label(self) -> str:
        """Human-readable one-line summary, e.g. for interactive prompts/logs."""
        state = self.overall_state
        if state == "successful":
            arches = ", ".join(e["arch_tag"] for e in self.completeness["entries"])
            return f"{self.version} - built on {arches or 'no architectures'}"
        if state == "no_builds":
            return f"{self.version} - not yet built"
        if state == "failed":
            return f"{self.version} - failed to build"
        if state == "in_progress":
            return f"{self.version} - currently building"
        return f"{self.version} - partially built"


def find_buildable_version(
    archive: Any,
    lp_series: Any,
    pkg: str,
    candidates: list[tuple[str, str]],
    *,
    max_candidates: int = 5,
) -> list[BuildCandidate]:
    """Probe Launchpad build completeness for up to ``max_candidates`` versions.

    ``candidates`` is an ordered (newest-first) list of ``(version, pocket)``
    pairs to consider (typically derived from lp-package-api's publish
    history for the desired pocket(s)). Returns the probed candidates in the
    same order, each annotated with its build completeness, so the caller
    can pick the first "successful" one or offer the reviewer/reporter a
    choice among them. Never raises: an unresolvable candidate is recorded
    with a "no_builds" verdict rather than aborting the walk. Stops probing
    as soon as a fully-built candidate is found.
    """
    results: list[BuildCandidate] = []
    for version, pocket in candidates[:max_candidates]:
        pub = find_source_publication(archive, lp_series, pkg, version)
        builds = builds_for_publication(pub) if pub is not None else []
        completeness = summarize_build_completeness(builds)
        candidate = BuildCandidate(version, pocket, completeness)
        results.append(candidate)
        if candidate.complete:
            break
    return results

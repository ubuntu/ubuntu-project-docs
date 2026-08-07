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
_BUILD_STATE_QUEUED = {"needs building"}
_BUILD_STATE_IN_PROGRESS = {
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

    Returns one of ``"successful"``, ``"queued"`` (not started yet),
    ``"in_progress"`` (actively building/uploading), ``"failed"``,
    ``"unknown"``.
    """
    state = raw_state.strip().lower()
    if state in _BUILD_STATE_SUCCESSFUL:
        return "successful"
    if state in _BUILD_STATE_QUEUED:
        return "queued"
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


def binaries_for_publication(pub: Any) -> list[Any]:
    """Return the published binary records for one source publication.

    Never raises: a publication that cannot enumerate binaries (e.g. a
    launchpadlib/network hiccup) is treated the same as "no binaries yet".

    This is the ground truth for a scenario ``getBuilds()`` alone gets wrong:
    when a brand-new Ubuntu devel series opens, the whole archive (including
    already-built packages) is copied across from the previous series without
    creating fresh ``Build`` rows for the new series - the binaries are
    copied straight across, referencing the *original* series' build. A
    source publication can therefore have zero ``Build`` records yet be
    fully available (published binaries for every architecture). See
    ``summarize_build_completeness`` for how this is folded in.
    """
    try:
        return list(pub.getPublishedBinaries())
    except Exception:
        return []


def _binary_arch_tag(record: Any) -> str:
    """Return the architecture tag for a published binary record.

    Test fixtures may supply a plain ``arch_tag`` key/attribute directly;
    real launchpadlib records expose it one level down, via
    ``distro_arch_series.architecture_tag``.
    """
    direct = build_attr(record, "arch_tag", "arch_tag_name")
    if direct:
        return direct
    das = record.get("distro_arch_series") if isinstance(record, dict) else None
    if das is None:
        das = getattr(record, "distro_arch_series", None)
    if das is None:
        return ""
    return build_attr(das, "architecture_tag", "architecturetag", "arch_tag")


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


def summarize_build_completeness(
    builds: list[Any], binaries: list[Any] | None = None
) -> dict[str, Any]:
    """Summarise build (and, as a fallback, published-binary) records.

    Returns a dict with:
      - ``complete``: True only when there is at least one entry and every
        one of them classifies as "successful".
      - ``overall_state``: ``"no_builds"`` | ``"successful"`` |
        ``"in_progress"`` | ``"failed"`` | ``"mixed"`` (some failed/pending,
        some successful).
      - ``entries``: list of ``{"arch_tag", "build_state", "classification"}``.
      - ``carried_over``: True when at least one architecture's evidence came
        from a published binary rather than a distinct Build record (see
        ``binaries_for_publication``).

    ``binaries`` supplies published-binary records for the same publication.
    An architecture with a Build record is always classified from that record
    (authoritative); an architecture with NO Build record but a Published
    binary is treated as "successful" too - the binary being there and
    published is itself proof the package is available for that
    architecture, regardless of whether Launchpad recorded a distinct Build
    row for this particular series.
    """
    entries = []
    classifications: set[str] = set()
    seen_arches: set[str] = set()
    for record in builds:
        arch_tag = build_attr(record, "arch_tag", "arch_tag_name", "architecture_tag")
        arch_tag = arch_tag or "unknown-arch"
        raw_state = build_attr(record, "buildstate", "build_state", "status")
        classification = classify_build_state(raw_state)
        classifications.add(classification)
        seen_arches.add(arch_tag)
        entries.append(
            {
                "arch_tag": arch_tag,
                "build_state": raw_state or "unknown",
                "classification": classification,
            }
        )

    carried_over = False
    for record in binaries or []:
        arch_tag = _binary_arch_tag(record) or "unknown-arch"
        if arch_tag in seen_arches:
            continue  # a Build record for this arch already exists and is authoritative
        status = build_attr(record, "status").strip().lower()
        if status != "published":
            continue
        seen_arches.add(arch_tag)
        classifications.add("successful")
        carried_over = True
        entries.append(
            {
                "arch_tag": arch_tag,
                "build_state": (
                    "binaries published (no distinct build record for this series - "
                    "likely carried over unchanged from a previous series)"
                ),
                "classification": "successful",
            }
        )

    if not entries:
        overall_state = "no_builds"
    elif classifications == {"successful"}:
        overall_state = "successful"
    elif classifications == {"failed"}:
        overall_state = "failed"
    elif classifications == {"queued"}:
        overall_state = "queued"
    elif classifications <= {"queued", "in_progress"}:
        overall_state = "in_progress"
    else:
        overall_state = "mixed"

    return {
        "complete": overall_state == "successful",
        "overall_state": overall_state,
        "entries": entries,
        "carried_over": carried_over,
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
    def has_available_arch(self) -> bool:
        """True when at least one architecture is built/available.

        Unlike ``complete`` (which requires *every* probed architecture to be
        successful), this is True for a "mixed" candidate too - a version
        that built fine on some architectures but not others is still worth
        offering to the reviewer/reporter as a real option, not silently
        discarded in favour of an older, fully-built version.
        """
        return self.overall_state in ("successful", "mixed")

    @property
    def overall_state(self) -> str:
        return str(self.completeness["overall_state"])

    @property
    def label(self) -> str:
        """Human-readable one-line summary, e.g. for interactive prompts/logs."""
        entries = self.completeness["entries"]
        state = self.overall_state
        if state == "successful":
            arches = ", ".join(e["arch_tag"] for e in entries)
            return f"{self.version} - built on {arches or 'no architectures'}"
        if state in ("no_builds", "queued"):
            return f"{self.version} - not yet built"
        if state == "failed":
            return f"{self.version} - failed to build"
        if state == "in_progress":
            return f"{self.version} - currently building"
        # "mixed": some architectures are available, some are not - spell out
        # both sides so the reviewer/reporter can make an informed choice.
        passing = ", ".join(e["arch_tag"] for e in entries if e["classification"] == "successful")
        other = ", ".join(e["arch_tag"] for e in entries if e["classification"] != "successful")
        return f"{self.version} - built on {passing or 'no architectures'}; not on {other}"


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
    same order, each annotated with its build completeness. Every candidate
    in the (bounded) window is probed - the walk does not stop at the first
    fully-built one - so a caller can offer the reviewer/reporter a genuine
    choice among *all* buildable candidates found, not just the newest one.
    Never raises: an unresolvable candidate is recorded with a "no_builds"
    verdict rather than aborting the walk.
    """
    results: list[BuildCandidate] = []
    for version, pocket in candidates[:max_candidates]:
        pub = find_source_publication(archive, lp_series, pkg, version)
        builds = builds_for_publication(pub) if pub is not None else []
        binaries = binaries_for_publication(pub) if pub is not None else []
        completeness = summarize_build_completeness(builds, binaries)
        results.append(BuildCandidate(version, pocket, completeness))
    return results

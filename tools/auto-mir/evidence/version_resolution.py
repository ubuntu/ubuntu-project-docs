"""Single source of truth for "which source version/pocket to analyse".

Several adapters need to talk about the *exact same* Launchpad publication -
packaging-source fetches its source, lp-build-api reports its per-architecture
build state, fetch-build downloads its binaries. Previously packaging-source
derived this decision itself (including a build-completeness check and an
interactive/headless fallback among older versions) and everything else
either re-derived it independently or read packaging-source's already-decided
``analyzed_version``. This module makes that decision exactly once, so every
consumer's statements about the package agree with each other.

Runs on the host (a pure Launchpad API lookup, no guest/lxd_runner needed).
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

from evidence import launchpad_client
from evidence.host_adapters import AdapterError
from evidence.types import VersionResolutionResult

if TYPE_CHECKING:
    from auto_mir import RunContext

log = logging.getLogger("auto_mir.evidence.version_resolution")

# Bounded lookback when the newest published version in the target pocket is
# not (yet) fully built on Launchpad: how many older versions of the same
# pocket to probe for build completeness before giving up.
_MAX_BUILD_CANDIDATES = 5


def _latest_published_in_pocket(history: list, pocket: str) -> str:
    """Return the most recent Published version in the given pocket, or ''.

    ``history`` is the lp-package-api ``ubuntu_publish_history`` (ordered newest
    first). Matching is case-insensitive on the pocket name (e.g. "Proposed").
    """
    pocket_lc = pocket.lower()
    for entry in history:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("pocket", "")).lower() != pocket_lc:
            continue
        if str(entry.get("status", "")).lower() != "published":
            continue
        version = str(entry.get("version", "")).strip()
        if version:
            return version
    return ""


def _candidate_versions_in_pocket(history: list, pocket: str, max_candidates: int) -> list[str]:
    """Return up to ``max_candidates`` distinct version strings for a pocket.

    ``history`` is already ordered newest-first (lp-package-api's
    ``ubuntu_publish_history``). Includes every publish status (Published,
    Superseded, Deleted, Obsolete): walking backwards from the newest upload,
    older entries are expected to show as Superseded, and we deliberately
    still want to offer them as fallback candidates when the newest one is
    not (yet) fully built on Launchpad.
    """
    pocket_lc = pocket.lower()
    versions: list[str] = []
    seen: set[str] = set()
    for entry in history:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("pocket", "")).lower() != pocket_lc:
            continue
        version = str(entry.get("version", "")).strip()
        if not version or version in seen:
            continue
        seen.add(version)
        versions.append(version)
        if len(versions) >= max_candidates:
            break
    return versions


def _headline_for_candidate(candidate: "launchpad_client.BuildCandidate") -> str:
    """Differentiated "not built yet" vs "failed to build" headline for a candidate."""
    state = candidate.overall_state
    if state == "failed":
        return f"The most recent build version {candidate.version} has failed to build."
    if state in ("no_builds", "queued"):
        return f"The most recent build version {candidate.version} has not yet built."
    if state == "in_progress":
        return f"The most recent build version {candidate.version} is currently building."
    return f"The most recent build version {candidate.version} is only partially built."


def _ask_buildable_candidate(
    headline: str, candidates: list["launchpad_client.BuildCandidate"]
) -> "launchpad_client.BuildCandidate":
    """Interactively offer buildable alternatives when the newest isn't fully ready.

    Mirrors the TTY-prompt convention used by auto_mir._ask_requested_binaries:
    a numbered list, free-text index selection, blank/EOF defaults to the
    first (newest) offered candidate.
    """
    print(f"\n{headline}")
    print("Do you want to instead analyze one of these versions?")
    for idx, candidate in enumerate(candidates, start=1):
        print(f"  {idx}. {candidate.label}")
    try:
        response = input(f"> [1-{len(candidates)}, default 1]: ").strip()
    except EOFError:
        return candidates[0]
    if not response:
        return candidates[0]
    try:
        index = int(response)
    except ValueError:
        print("Not a valid choice, defaulting to option 1.")
        return candidates[0]
    if 1 <= index <= len(candidates):
        return candidates[index - 1]
    print("Not a valid choice, defaulting to option 1.")
    return candidates[0]


def _resolve_buildable_candidate(
    ctx: RunContext, candidate_versions: list[str], lp_pocket: str
) -> tuple[str, str, str]:
    """Pick which candidate version to analyse, preferring the newest available.

    ``candidate_versions`` is newest-first within ``lp_pocket`` (e.g.
    "Release" or "Proposed"). "Available" means at least one architecture is
    built or has a published binary (see ``evidence.launchpad_client`` for the
    build/binary-completeness classification) - a version that only built on
    *some* architectures ("mixed") is still offered/used, not discarded in
    favour of an older fully-built one.

    Returns ``(version, pocket_label, note)``. ``note`` is empty when the
    newest candidate was used unmodified and fully built; otherwise it
    records why an older version was substituted, or why the newest one is
    being used despite only partial architecture coverage (surfaced to the
    reviewer/reporter for transparency).

    Raises AdapterError when none of the probed candidates have any
    available architecture anywhere in the lookback window (no polling/
    waiting: the caller should re-run once Launchpad has a successful build).
    """
    pocket_label = lp_pocket.lower()
    try:
        lp = launchpad_client.login_anonymously("auto-mir-version-resolution")
        ubuntu = lp.distributions["ubuntu"]
        archive = ubuntu.main_archive
        lp_series = launchpad_client.resolve_series(ubuntu, ctx.series or "devel")
    except launchpad_client.LaunchpadUnavailableError as exc:
        log.warning(
            "Could not verify Launchpad build completeness (%s); analysing "
            "the newest %s version %s without a build-state check",
            exc,
            pocket_label,
            candidate_versions[0],
        )
        return candidate_versions[0], pocket_label, ""

    candidates = [(version, lp_pocket) for version in candidate_versions]
    results = launchpad_client.find_buildable_version(
        archive, lp_series, ctx.source_package, candidates
    )

    newest = results[0]
    if newest.complete:
        return newest.version, pocket_label, ""

    available_candidates = [c for c in results if c.has_available_arch]
    headline = _headline_for_candidate(newest)

    if not available_candidates:
        raise AdapterError(
            f"{headline} No buildable {pocket_label} candidate (built on any "
            f"architecture) was found in the last {len(results)} published "
            f"version(s) of {ctx.source_package}; re-run once Launchpad has a "
            "successful build."
        )

    if sys.stdin.isatty() and sys.stdout.isatty():
        chosen = _ask_buildable_candidate(headline, available_candidates)
    else:
        # Headless: always prefer the newest candidate that has any built
        # architecture at all (even if only partially built), rather than an
        # older, fully-built one - the reviewer/reporter can see exactly
        # which architectures are missing via the note/label.
        chosen = available_candidates[0]
        log.warning(
            "%s No interactive terminal available; analysing %s instead "
            "(newest buildable candidate found in the last %d published version(s)).",
            headline,
            chosen.label,
            len(results),
        )

    if chosen is newest:
        note = f"{headline} Proceeding with {chosen.version} ({chosen.label})."
    else:
        note = f"{headline} Substituted with {chosen.version} ({chosen.label})."
    return chosen.version, pocket_label, note


def _resolve_source_pocket_version(ctx: RunContext) -> tuple[str, str, str]:
    """Resolve which source version/pocket every consumer should analyse.

    Returns ``(version, pocket_label, resolution_note)``.
    ``pocket_label`` is one of "release" or "proposed". The returned version
    is always pinned to a specific upload (never left for apt/callers to
    pick), because it must be the exact version fetch-build later downloads
    build artifacts for - source and binaries must never drift apart.
    ``resolution_note`` is empty unless an older version had to be
    substituted, or the newest one is being used despite only partial
    architecture coverage (see ``_resolve_buildable_candidate``).

    Honours ``ctx.source_pocket``:
      - "release":  always the release pocket.
      - "proposed": the published -proposed version; falls back to release
                    with a warning when none is published.
      - "auto":     prefer -proposed when published, else release.

    Within the chosen pocket, prefers the newest version that Launchpad has
    fully built. If the newest version is not (yet) fully built, walks up to
    ``_MAX_BUILD_CANDIDATES`` older versions in the same pocket and offers a
    choice (interactively on a TTY, automatically otherwise) among the ones
    that have at least one available architecture.
    """
    requested_pocket = getattr(ctx, "source_pocket", "auto")

    lp = ctx.evidence.get("adapters", {}).get("lp-package-api", {})
    history = lp.get("ubuntu_publish_history", []) if isinstance(lp, dict) else []

    if requested_pocket == "release":
        lp_pocket = "Release"
    else:
        proposed_version = _latest_published_in_pocket(history, "Proposed")
        if proposed_version:
            lp_pocket = "Proposed"
        else:
            if requested_pocket == "proposed":
                log.warning(
                    "source-pocket=proposed requested but no published -proposed "
                    "version found; falling back to the release pocket"
                )
            lp_pocket = "Release"

    candidate_versions = _candidate_versions_in_pocket(history, lp_pocket, _MAX_BUILD_CANDIDATES)
    if not candidate_versions:
        return "", lp_pocket.lower(), ""

    version, pocket_label, note = _resolve_buildable_candidate(ctx, candidate_versions, lp_pocket)
    log.info(
        "Analysing %s source version %s (source-pocket=%s)", pocket_label, version, requested_pocket
    )
    return version, pocket_label, note


def collect_version_resolution(ctx: RunContext) -> VersionResolutionResult:
    """Resolve, once, which source version/pocket every other adapter uses.

    Reads lp-package-api's publish history (already scoped to the target
    series) and decides the pocket + exact version to analyse, probing
    Launchpad build/binary completeness with a fallback among older versions
    when the newest one is not (yet) fully built anywhere. See
    ``_resolve_source_pocket_version`` for the full policy.
    """
    version, pocket, note = _resolve_source_pocket_version(ctx)
    log.debug(
        "version-resolution: %s resolved to version=%s pocket=%s%s",
        ctx.source_package,
        version or "(unpinned)",
        pocket,
        " (note: see resolution_note)" if note else "",
    )
    return {
        "status": "ok",
        "resolved_version": version,
        "resolved_pocket": pocket,
        "resolution_note": note,
    }

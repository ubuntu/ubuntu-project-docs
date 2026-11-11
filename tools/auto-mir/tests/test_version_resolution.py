"""Unit tests for evidence/version_resolution.py.

This is the single source of truth for "which source version/pocket should
this run analyse" - packaging-source and lp-build-api both consume its
result instead of independently re-deriving the decision (see decisions.md).
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evidence import launchpad_client  # noqa: E402
from evidence.version_resolution import (  # noqa: E402  # noqa: E402
    _candidate_versions_in_pocket,
    _headline_for_candidate,
    _latest_published_in_pocket,
    _resolve_source_pocket_version,
    collect_version_resolution,
)


class _PocketCtx:
    def __init__(self, source_pocket, publish_history, source_package="testpkg", series="noble"):
        self.source_pocket = source_pocket
        self.source_package = source_package
        self.series = series
        self.evidence = {
            "adapters": {
                "lp-package-api": {
                    "status": "ok",
                    "ubuntu_publish_history": publish_history,
                }
            }
        }


_PROPOSED = {"version": "0.20.0-2ubuntu1", "pocket": "Proposed", "status": "Published"}
_RELEASE = {"version": "0.20.0-2build1", "pocket": "Release", "status": "Published"}

# Launchpad lookups are mocked to raise LaunchpadUnavailableError in the
# "plain" pocket-resolution tests below so they exercise the same
# unmodified-pin behaviour regardless of build-completeness (that is
# covered separately further down).


def _unavailable_login(*_args, **_kwargs):
    raise launchpad_client.LaunchpadUnavailableError("no network in unit tests")


def test_latest_published_in_pocket_matches_case_insensitively():
    assert _latest_published_in_pocket([_RELEASE, _PROPOSED], "proposed") == "0.20.0-2ubuntu1"
    assert _latest_published_in_pocket([_RELEASE], "Proposed") == ""


def test_latest_published_ignores_non_published():
    history = [
        {"version": "9.9", "pocket": "Proposed", "status": "Pending"},
        _PROPOSED,
    ]
    assert _latest_published_in_pocket(history, "Proposed") == "0.20.0-2ubuntu1"


def test_resolve_auto_prefers_proposed_when_present():
    ctx = _PocketCtx("auto", [_RELEASE, _PROPOSED])
    with patch("evidence.launchpad_client.login_anonymously", side_effect=_unavailable_login):
        assert _resolve_source_pocket_version(ctx) == ("0.20.0-2ubuntu1", "proposed", "")


def test_resolve_auto_falls_back_to_release_without_proposed():
    ctx = _PocketCtx("auto", [_RELEASE])
    with patch("evidence.launchpad_client.login_anonymously", side_effect=_unavailable_login):
        assert _resolve_source_pocket_version(ctx) == ("0.20.0-2build1", "release", "")


def test_resolve_release_never_pins_proposed():
    ctx = _PocketCtx("release", [_RELEASE, _PROPOSED])
    with patch("evidence.launchpad_client.login_anonymously", side_effect=_unavailable_login):
        assert _resolve_source_pocket_version(ctx) == ("0.20.0-2build1", "release", "")


def test_resolve_proposed_requested_but_missing_falls_back():
    ctx = _PocketCtx("proposed", [_RELEASE])
    with patch("evidence.launchpad_client.login_anonymously", side_effect=_unavailable_login):
        assert _resolve_source_pocket_version(ctx) == ("0.20.0-2build1", "release", "")


def test_resolve_empty_history_lets_apt_pick():
    ctx = _PocketCtx("release", [])
    with patch("evidence.launchpad_client.login_anonymously", side_effect=_unavailable_login):
        assert _resolve_source_pocket_version(ctx) == ("", "release", "")


# ---------------------------------------------------------------------------
# Build-aware version resolution: the newest candidate in the pocket is
# preferred, but an older or only-partially-built candidate is offered/
# substituted per policy when Launchpad has not (yet) fully built the newest.
# ---------------------------------------------------------------------------

_MULTI_PROPOSED_HISTORY = [
    {"version": "2.0-1", "pocket": "Proposed", "status": "Published"},
    {"version": "1.0-1", "pocket": "Proposed", "status": "Superseded"},
    {"version": "0.9-1", "pocket": "Proposed", "status": "Superseded"},
]


def _fake_lp_session(builds_by_version: dict, binaries_by_version: dict | None = None) -> Mock:
    """Return a fake launchpadlib session for the given per-version builds/binaries.

    ``builds_by_version``/``binaries_by_version`` map version string -> list
    of build/binary dicts. A version absent from a mapping (or mapped to an
    empty list) resolves to "nothing there" for that source.
    """
    binaries_by_version = binaries_by_version or {}
    lp = Mock()
    ubuntu = Mock()
    archive = Mock()
    lp.distributions = {"ubuntu": ubuntu}
    ubuntu.main_archive = archive
    ubuntu.getSeries.return_value = Mock(name="lp_series")

    def fake_get_published_sources(*, source_name, version, distro_series, exact_match):
        pub = Mock()
        pub.getBuilds.return_value = builds_by_version.get(version, [])
        pub.getPublishedBinaries.return_value = binaries_by_version.get(version, [])
        return [pub]

    archive.getPublishedSources.side_effect = fake_get_published_sources
    return lp


def test_resolve_buildable_candidate_uses_newest_when_fully_built():
    ctx = _PocketCtx("auto", _MULTI_PROPOSED_HISTORY)
    lp = _fake_lp_session({"2.0-1": [{"arch_tag": "amd64", "buildstate": "Successfully built"}]})
    with patch("evidence.launchpad_client.login_anonymously", return_value=lp):
        assert _resolve_source_pocket_version(ctx) == ("2.0-1", "proposed", "")


def test_resolve_buildable_candidate_falls_back_headless_when_newest_not_built():
    ctx = _PocketCtx("auto", _MULTI_PROPOSED_HISTORY)
    lp = _fake_lp_session(
        {
            "2.0-1": [{"arch_tag": "amd64", "buildstate": "Needs building"}],
            "1.0-1": [{"arch_tag": "amd64", "buildstate": "Successfully built"}],
            "0.9-1": [{"arch_tag": "amd64", "buildstate": "Successfully built"}],
        }
    )
    with (
        patch("evidence.launchpad_client.login_anonymously", return_value=lp),
        patch("sys.stdin.isatty", return_value=False),
    ):
        version, pocket, note = _resolve_source_pocket_version(ctx)
    assert (version, pocket) == ("1.0-1", "proposed")
    assert "no successful builds yet" in note
    assert "1.0-1" in note


def test_resolve_buildable_candidate_prompts_interactively():
    ctx = _PocketCtx("auto", _MULTI_PROPOSED_HISTORY)
    lp = _fake_lp_session(
        {
            "2.0-1": [{"arch_tag": "amd64", "buildstate": "Failed to build"}],
            "1.0-1": [{"arch_tag": "amd64", "buildstate": "Successfully built"}],
            "0.9-1": [{"arch_tag": "amd64", "buildstate": "Successfully built"}],
        }
    )
    with (
        patch("evidence.launchpad_client.login_anonymously", return_value=lp),
        patch("sys.stdin.isatty", return_value=True),
        patch("sys.stdout.isatty", return_value=True),
        patch("builtins.input", return_value="2"),
    ):
        version, pocket, note = _resolve_source_pocket_version(ctx)
    assert (version, pocket) == ("0.9-1", "proposed")
    assert "failed to build" in note


def test_resolve_buildable_candidate_interactive_default_on_blank_input():
    ctx = _PocketCtx("auto", _MULTI_PROPOSED_HISTORY)
    lp = _fake_lp_session(
        {
            "2.0-1": [{"arch_tag": "amd64", "buildstate": "Failed to build"}],
            "1.0-1": [{"arch_tag": "amd64", "buildstate": "Successfully built"}],
        }
    )
    with (
        patch("evidence.launchpad_client.login_anonymously", return_value=lp),
        patch("sys.stdin.isatty", return_value=True),
        patch("sys.stdout.isatty", return_value=True),
        patch("builtins.input", return_value=""),
    ):
        version, _pocket, _note = _resolve_source_pocket_version(ctx)
    assert version == "1.0-1"


def test_resolve_buildable_candidate_raises_when_none_buildable():
    ctx = _PocketCtx("auto", _MULTI_PROPOSED_HISTORY)
    lp = _fake_lp_session({})
    with patch("evidence.launchpad_client.login_anonymously", return_value=lp):
        with pytest.raises(RuntimeError, match="No buildable"):
            _resolve_source_pocket_version(ctx)


def test_resolve_buildable_candidate_degrades_gracefully_without_launchpad():
    """When Launchpad itself is unreachable, pin the newest candidate unmodified."""
    ctx = _PocketCtx("auto", _MULTI_PROPOSED_HISTORY)
    with patch("evidence.launchpad_client.login_anonymously", side_effect=_unavailable_login):
        assert _resolve_source_pocket_version(ctx) == ("2.0-1", "proposed", "")


# ---------------------------------------------------------------------------
# Broadened "mixed"/carried-over-binaries handling. Root cause of the
# jitterentropy-library false positive: a package carried over unchanged into
# a newly-opened devel series has zero Build records for that series (the
# whole archive, binaries included, is copied across without a fresh
# per-series build) - getBuilds() alone wrongly reports "not yet built" even
# though the binaries are Published and fully available. See decisions.md.
# ---------------------------------------------------------------------------


def test_resolve_prefers_newest_mixed_candidate_headlessly():
    """A newest version that only built on SOME arches is still preferred headlessly."""
    ctx = _PocketCtx("auto", _MULTI_PROPOSED_HISTORY)
    lp = _fake_lp_session(
        {
            "2.0-1": [
                {"arch_tag": "amd64", "buildstate": "Successfully built"},
                {"arch_tag": "arm64", "buildstate": "Failed to build"},
            ],
            "1.0-1": [{"arch_tag": "amd64", "buildstate": "Successfully built"}],
        }
    )
    with (
        patch("evidence.launchpad_client.login_anonymously", return_value=lp),
        patch("sys.stdin.isatty", return_value=False),
    ):
        version, pocket, note = _resolve_source_pocket_version(ctx)
    assert (version, pocket) == ("2.0-1", "proposed")
    assert "built on amd64" in note
    assert "not on arm64" in note


def test_resolve_offers_mixed_newest_as_first_interactive_choice():
    ctx = _PocketCtx("auto", _MULTI_PROPOSED_HISTORY)
    lp = _fake_lp_session(
        {
            "2.0-1": [
                {"arch_tag": "amd64", "buildstate": "Successfully built"},
                {"arch_tag": "arm64", "buildstate": "Failed to build"},
            ],
            "1.0-1": [{"arch_tag": "amd64", "buildstate": "Successfully built"}],
        }
    )
    with (
        patch("evidence.launchpad_client.login_anonymously", return_value=lp),
        patch("sys.stdin.isatty", return_value=True),
        patch("sys.stdout.isatty", return_value=True),
        patch("builtins.input", return_value=""),
    ):
        version, _pocket, _note = _resolve_source_pocket_version(ctx)
    # Blank input defaults to choice #1, which must be the newest (mixed) one.
    assert version == "2.0-1"


def test_resolve_treats_published_binaries_as_built_when_no_build_record():
    """Regression test for the jitterentropy-library false positive.

    A package carried over unchanged into a newly-opened devel series has
    zero Build records for that series, but its binaries were copied across
    and are Published for every architecture. This must resolve as fully
    built, not raise.
    """
    ctx = _PocketCtx("release", [_RELEASE])
    lp = _fake_lp_session(
        builds_by_version={"0.20.0-2build1": []},
        binaries_by_version={
            "0.20.0-2build1": [
                {"arch_tag": "amd64", "status": "Published"},
                {"arch_tag": "arm64", "status": "Published"},
            ]
        },
    )
    with patch("evidence.launchpad_client.login_anonymously", return_value=lp):
        version, pocket, note = _resolve_source_pocket_version(ctx)
    assert (version, pocket) == ("0.20.0-2build1", "release")
    assert note == ""


def test_collect_version_resolution_adapter_shape():
    ctx = _PocketCtx("auto", [_RELEASE])
    with patch("evidence.launchpad_client.login_anonymously", side_effect=_unavailable_login):
        result = collect_version_resolution(ctx)
    assert result == {
        "status": "ok",
        "resolved_version": "0.20.0-2build1",
        "resolved_pocket": "release",
        "resolution_note": "",
    }


def test_candidate_versions_excludes_removed_and_pending_uploads():
    """Deleted/Removed/Pending uploads are archive content a review must not
    offer: rmadison does not show them, and a removed upload would otherwise
    keep being probed and headlined forever. Superseded versions stay - the
    rmadison view keeps them analyzable as walk-back fallbacks.
    Regression shape from the user test (rust-sequoia-sq 2121154): the
    1.4.0-1ubuntu2 upload appeared in Release as Published while also being
    Deleted in Proposed; a later archive removal left only the stale entries.
    """
    history = [
        {"version": "1.4.0-1ubuntu2", "pocket": "Release", "status": "Deleted"},
        {"version": "1.4.0-1ubuntu1", "pocket": "Release", "status": "Superseded"},
        {"version": "1.4.0-1ubuntu1", "pocket": "Proposed", "status": "Pending"},
        {"version": "1.4.0-1ubuntu0", "pocket": "Release", "status": "Obsolete"},
        {"version": "1.3.1-10ubuntu1", "pocket": "Release", "status": "Published"},
        {"version": "1.3.1-10ubuntu1", "pocket": "Proposed", "status": "Published"},
        {"version": "1.3.1-6", "pocket": "Release", "status": "Superseded"},
    ]

    candidates = _candidate_versions_in_pocket(history, "Release", 5)

    assert candidates == ["1.4.0-1ubuntu1", "1.3.1-10ubuntu1", "1.3.1-6"]


def test_single_buildable_fallback_skips_the_interactive_prompt():
    """A one-option prompt is not a choice: when exactly one buildable
    fallback exists, proceed with the substitution note instead of asking."""
    history = [
        {"version": "1.4.0-1ubuntu2", "pocket": "Release", "status": "Published"},
        {"version": "1.3.1-10ubuntu1", "pocket": "Release", "status": "Published"},
    ]
    ctx = _PocketCtx("release", history)
    lp = _fake_lp_session(
        {
            "1.4.0-1ubuntu2": [],
            "1.3.1-10ubuntu1": [{"arch_tag": "amd64", "buildstate": "Successfully built"}],
        }
    )
    with (
        patch("evidence.launchpad_client.login_anonymously", return_value=lp),
        patch("sys.stdin.isatty", return_value=True),
        patch("builtins.input", side_effect=AssertionError("must not prompt")),
    ):
        version, pocket, note = _resolve_source_pocket_version(ctx)

    assert (version, pocket) == ("1.3.1-10ubuntu1", "release")
    assert "no successful builds yet" in note
    assert "Substituted with 1.3.1-10ubuntu1" in note


def test_two_buildable_fallbacks_still_prompt_interactively():
    history = [
        {"version": "2.0-1", "pocket": "Proposed", "status": "Published"},
        {"version": "1.0-1", "pocket": "Proposed", "status": "Superseded"},
        {"version": "0.9-1", "pocket": "Proposed", "status": "Superseded"},
    ]
    ctx = _PocketCtx("auto", history)
    lp = _fake_lp_session(
        {
            "2.0-1": [],
            "1.0-1": [{"arch_tag": "amd64", "buildstate": "Successfully built"}],
            "0.9-1": [{"arch_tag": "arm64", "buildstate": "Successfully built"}],
        }
    )
    with (
        patch("evidence.launchpad_client.login_anonymously", return_value=lp),
        patch("sys.stdin.isatty", return_value=True),
        patch("sys.stdout.isatty", return_value=True),
        patch("builtins.input", return_value="2"),
    ):
        version, _pocket, _note = _resolve_source_pocket_version(ctx)

    assert version == "0.9-1"


def test_headline_names_the_pocket():
    """The headline must say where the unbuilt version came from so a
    reviewer cross-checking rmadison is not left guessing."""
    candidate = launchpad_client.BuildCandidate(
        "1.4.0-1ubuntu2", "Release", launchpad_client.summarize_build_completeness([])
    )

    headline = _headline_for_candidate(candidate, "release")

    assert "release pocket" in headline
    assert "1.4.0-1ubuntu2" in headline

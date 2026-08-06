"""Unit tests for evidence/launchpad_client.py."""

from unittest.mock import Mock, patch

import pytest

from evidence import launchpad_client


def test_login_anonymously_raises_when_launchpadlib_missing():
    with patch("evidence.launchpad_client._Launchpad", None):
        with pytest.raises(launchpad_client.LaunchpadUnavailableError, match="not installed"):
            launchpad_client.login_anonymously("auto-mir-test")


def test_login_anonymously_wraps_connection_errors():
    fake_launchpad = Mock()
    fake_launchpad.login_anonymously.side_effect = RuntimeError("network down")
    with patch("evidence.launchpad_client._Launchpad", fake_launchpad):
        with pytest.raises(launchpad_client.LaunchpadUnavailableError, match="connection failed"):
            launchpad_client.login_anonymously("auto-mir-test")


def test_login_anonymously_returns_session():
    fake_session = Mock()
    fake_launchpad = Mock()
    fake_launchpad.login_anonymously.return_value = fake_session
    with patch("evidence.launchpad_client._Launchpad", fake_launchpad):
        result = launchpad_client.login_anonymously("auto-mir-test")
    assert result is fake_session
    fake_launchpad.login_anonymously.assert_called_once_with(
        "auto-mir-test", "production", version="devel"
    )


def test_resolve_series_uses_get_series():
    ubuntu = Mock()
    ubuntu.getSeries.return_value = "stonking-series"
    assert launchpad_client.resolve_series(ubuntu, "stonking") == "stonking-series"


def test_resolve_series_falls_back_to_current_series():
    ubuntu = Mock()
    ubuntu.getSeries.side_effect = RuntimeError("no such series")
    ubuntu.current_series = "devel-series"
    assert launchpad_client.resolve_series(ubuntu, "devel") == "devel-series"


def test_resolve_series_raises_when_nothing_resolves():
    ubuntu = Mock()
    ubuntu.getSeries.side_effect = RuntimeError("no such series")
    type(ubuntu).current_series = property(lambda self: (_ for _ in ()).throw(RuntimeError("no")))
    with pytest.raises(launchpad_client.LaunchpadUnavailableError):
        launchpad_client.resolve_series(ubuntu, "bogus")


def test_build_attr_prefers_first_present_name():
    record = Mock(spec=["arch_tag"])
    record.arch_tag = "amd64"
    assert launchpad_client.build_attr(record, "arch_tag_name", "arch_tag") == "amd64"


def test_build_attr_unwraps_name_attribute():
    inner = Mock()
    inner.name = "primary"
    record = Mock(spec=["archive"])
    record.archive = inner
    assert launchpad_client.build_attr(record, "archive") == "primary"


def test_build_attr_returns_default_when_missing():
    record = Mock(spec=[])
    assert launchpad_client.build_attr(record, "arch_tag", default="unknown") == "unknown"


def test_build_attr_reads_dict_records():
    record = {"arch_tag": "s390x"}
    assert launchpad_client.build_attr(record, "arch_tag") == "s390x"


@pytest.mark.parametrize(
    ("raw_state", "expected"),
    [
        ("Successfully built", "successful"),
        ("Needs building", "queued"),
        ("Currently building", "in_progress"),
        ("Uploading build", "in_progress"),
        ("Failed to build", "failed"),
        ("Dependency wait", "failed"),
        ("Chroot problem", "failed"),
        ("Something Else Entirely", "unknown"),
    ],
)
def test_classify_build_state(raw_state, expected):
    assert launchpad_client.classify_build_state(raw_state) == expected


def test_builds_for_publication_returns_list():
    pub = Mock()
    pub.getBuilds.return_value = ["build1", "build2"]
    assert launchpad_client.builds_for_publication(pub) == ["build1", "build2"]


def test_builds_for_publication_never_raises():
    pub = Mock()
    pub.getBuilds.side_effect = RuntimeError("boom")
    assert launchpad_client.builds_for_publication(pub) == []


def test_find_source_publication_returns_first_match():
    archive = Mock()
    pub = Mock()
    archive.getPublishedSources.return_value = [pub]
    lp_series = Mock()
    result = launchpad_client.find_source_publication(archive, lp_series, "testpkg", "1.0-1")
    assert result is pub
    archive.getPublishedSources.assert_called_once_with(
        source_name="testpkg", version="1.0-1", distro_series=lp_series, exact_match=True
    )


def test_find_source_publication_returns_none_when_absent():
    archive = Mock()
    archive.getPublishedSources.return_value = []
    result = launchpad_client.find_source_publication(archive, Mock(), "testpkg", "1.0-1")
    assert result is None


def test_find_source_publication_never_raises():
    archive = Mock()
    archive.getPublishedSources.side_effect = RuntimeError("boom")
    result = launchpad_client.find_source_publication(archive, Mock(), "testpkg", "1.0-1")
    assert result is None


def _build(arch_tag: str, state: str) -> dict:
    return {"arch_tag": arch_tag, "buildstate": state}


def test_summarize_build_completeness_all_successful():
    builds = [_build("amd64", "Successfully built"), _build("arm64", "Successfully built")]
    summary = launchpad_client.summarize_build_completeness(builds)
    assert summary["complete"] is True
    assert summary["overall_state"] == "successful"
    assert len(summary["entries"]) == 2


def test_summarize_build_completeness_no_builds():
    summary = launchpad_client.summarize_build_completeness([])
    assert summary["complete"] is False
    assert summary["overall_state"] == "no_builds"
    assert summary["entries"] == []


def test_summarize_build_completeness_all_failed():
    builds = [_build("amd64", "Failed to build"), _build("arm64", "Dependency wait")]
    summary = launchpad_client.summarize_build_completeness(builds)
    assert summary["complete"] is False
    assert summary["overall_state"] == "failed"


def test_summarize_build_completeness_queued():
    builds = [_build("amd64", "Needs building"), _build("arm64", "Needs building")]
    summary = launchpad_client.summarize_build_completeness(builds)
    assert summary["complete"] is False
    assert summary["overall_state"] == "queued"


def test_summarize_build_completeness_in_progress():
    builds = [_build("amd64", "Needs building"), _build("arm64", "Currently building")]
    summary = launchpad_client.summarize_build_completeness(builds)
    assert summary["complete"] is False
    assert summary["overall_state"] == "in_progress"


def test_summarize_build_completeness_mixed():
    builds = [_build("amd64", "Successfully built"), _build("arm64", "Failed to build")]
    summary = launchpad_client.summarize_build_completeness(builds)
    assert summary["complete"] is False
    assert summary["overall_state"] == "mixed"


def test_build_candidate_label_variants():
    successful = launchpad_client.BuildCandidate(
        "1.0-1",
        "Release",
        launchpad_client.summarize_build_completeness([_build("amd64", "Successfully built")]),
    )
    assert successful.label == "1.0-1 - built on amd64"
    assert successful.complete is True

    not_built = launchpad_client.BuildCandidate(
        "0.9-1", "Release", launchpad_client.summarize_build_completeness([])
    )
    assert not_built.label == "0.9-1 - not yet built"
    assert not_built.complete is False

    failed = launchpad_client.BuildCandidate(
        "0.8-1",
        "Release",
        launchpad_client.summarize_build_completeness([_build("amd64", "Failed to build")]),
    )
    assert failed.label == "0.8-1 - failed to build"

    in_progress = launchpad_client.BuildCandidate(
        "0.7-1",
        "Release",
        launchpad_client.summarize_build_completeness([_build("amd64", "Currently building")]),
    )
    assert in_progress.label == "0.7-1 - currently building"

    mixed = launchpad_client.BuildCandidate(
        "0.6-1",
        "Release",
        launchpad_client.summarize_build_completeness(
            [_build("amd64", "Successfully built"), _build("arm64", "Failed to build")]
        ),
    )
    assert mixed.label == "0.6-1 - partially built"


def test_find_buildable_version_probes_every_candidate_in_window():
    archive = Mock()
    lp_series = Mock()

    pub_newest = Mock()
    pub_newest.getBuilds.return_value = [_build("amd64", "Needs building")]
    pub_older = Mock()
    pub_older.getBuilds.return_value = [_build("amd64", "Successfully built")]
    pub_oldest = Mock()
    pub_oldest.getBuilds.return_value = [_build("amd64", "Successfully built")]

    def fake_get_published_sources(*, source_name, version, distro_series, exact_match):
        return {"2.0-1": [pub_newest], "1.0-1": [pub_older], "0.9-1": [pub_oldest]}[version]

    archive.getPublishedSources.side_effect = fake_get_published_sources

    candidates = [("2.0-1", "Proposed"), ("1.0-1", "Release"), ("0.9-1", "Release")]
    results = launchpad_client.find_buildable_version(archive, lp_series, "testpkg", candidates)

    # Every candidate in the window is probed - the walk does not stop early
    # - so callers can offer a full choice of buildable alternatives.
    assert [c.version for c in results] == ["2.0-1", "1.0-1", "0.9-1"]
    assert results[0].complete is False
    assert results[1].complete is True
    assert results[2].complete is True


def test_find_buildable_version_respects_max_candidates():
    archive = Mock()
    archive.getPublishedSources.return_value = []
    candidates = [(f"{i}.0-1", "Release") for i in range(10)]
    results = launchpad_client.find_buildable_version(
        archive, Mock(), "testpkg", candidates, max_candidates=3
    )
    assert len(results) == 3


def test_find_buildable_version_handles_unresolvable_candidate():
    archive = Mock()
    archive.getPublishedSources.return_value = []
    results = launchpad_client.find_buildable_version(
        archive, Mock(), "testpkg", [("1.0-1", "Release")]
    )
    assert len(results) == 1
    assert results[0].overall_state == "no_builds"

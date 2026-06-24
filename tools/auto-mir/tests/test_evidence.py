"""Integration tests for evidence collection orchestration."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evidence import AdapterError, _order_adapters, collect_from_catalog

# ---------------------------------------------------------------------------
# Adapter dependency ordering
# ---------------------------------------------------------------------------


def test_order_adapters_no_deps():
    """Adapters without dependencies should all be returned."""
    required = {"lp-bug-api", "ubuntu-cve-tracker", "autopkgtest-db"}
    ordered = _order_adapters(required, {})
    assert set(ordered) == required
    assert len(ordered) == len(required)


def test_order_adapters_with_deps():
    """Adapters with dependencies should be ordered after their dependencies."""
    required = {"dep-analysis", "packaging-source", "lp-bug-api"}
    deps = {"dep-analysis": ["packaging-source"]}
    ordered = _order_adapters(required, deps)

    # packaging-source must come before dep-analysis
    assert ordered.index("packaging-source") < ordered.index("dep-analysis")
    # lp-bug-api has no deps, can be anywhere
    assert "lp-bug-api" in ordered


def test_order_adapters_chain_deps():
    """Adapters with chained dependencies should be ordered correctly."""
    required = {"sbuild", "dep-analysis", "packaging-source"}
    deps = {
        "dep-analysis": ["packaging-source"],
        "sbuild": ["packaging-source"],
    }
    ordered = _order_adapters(required, deps)

    # packaging-source must come first
    assert ordered[0] == "packaging-source"
    # dep-analysis and sbuild can be in any order after packaging-source
    assert "dep-analysis" in ordered[1:]
    assert "sbuild" in ordered[1:]


def test_order_adapters_cycle_breaking():
    """Cyclic dependencies should be broken by appending remainder alphabetically."""
    required = {"a", "b", "c"}
    deps = {
        "a": ["b"],
        "b": ["c"],
        "c": ["a"],  # Cycle: a -> b -> c -> a
    }
    ordered = _order_adapters(required, deps)

    # Should not hang; should return all adapters
    assert len(ordered) == 3
    assert set(ordered) == required


# ---------------------------------------------------------------------------
# Evidence collection orchestration
# ---------------------------------------------------------------------------


def test_collect_from_catalog_skips_unreferenced_adapters():
    """Only adapters referenced by checks should be collected."""
    ctx = Mock()
    ctx.catalog = {
        "checks": [
            {"id": "SUM-1", "adapters_required": ["lp-bug-api"]},
        ]
    }
    ctx.evidence = {}

    mock_lp = Mock(return_value={"status": "ok"})
    mock_cve = Mock(return_value={"status": "ok"})

    with patch.dict(
        "evidence.ADAPTER_REGISTRY",
        {"lp-bug-api": (mock_lp, []), "ubuntu-cve-tracker": (mock_cve, [])},
        clear=True,
    ):
        collect_from_catalog(ctx)

        # lp-bug-api should be called
        assert mock_lp.called
        # ubuntu-cve-tracker should NOT be called (not referenced)
        assert not mock_cve.called


def test_collect_from_catalog_respects_dependency_order():
    """Adapters should be collected in dependency order."""
    ctx = Mock()
    ctx.catalog = {
        "checks": [
            {"id": "DEP-1", "adapters_required": ["dep-analysis", "packaging-source"]},
        ]
    }
    ctx.evidence = {}

    call_order = []

    def mock_packaging(ctx):
        call_order.append("packaging-source")
        return {"status": "ok", "source_dir": "/tmp/test"}

    def mock_dep(ctx):
        call_order.append("dep-analysis")
        return {"status": "ok"}

    m_pack = Mock(side_effect=mock_packaging)
    m_dep = Mock(side_effect=mock_dep)

    with patch.dict(
        "evidence.ADAPTER_REGISTRY",
        {"packaging-source": (m_pack, []), "dep-analysis": (m_dep, ["packaging-source"])},
        clear=True,
    ):
        collect_from_catalog(ctx)

        # packaging-source must be collected before dep-analysis
        assert call_order == ["packaging-source", "dep-analysis"]


def test_collect_from_catalog_handles_adapter_failure():
    """Failed adapters should be marked as error and not block other adapters."""
    ctx = Mock()
    ctx.catalog = {
        "checks": [
            {"id": "SUM-1", "adapters_required": ["lp-bug-api", "ubuntu-cve-tracker"]},
        ]
    }
    ctx.evidence = {}

    mock_lp = Mock(side_effect=AdapterError("LP API unavailable"))
    mock_cve = Mock(return_value={"status": "ok"})

    with patch.dict(
        "evidence.ADAPTER_REGISTRY",
        {"lp-bug-api": (mock_lp, []), "ubuntu-cve-tracker": (mock_cve, [])},
        clear=True,
    ):
        collect_from_catalog(ctx)

        # lp-bug-api should be marked as error
        assert ctx.evidence["adapters"]["lp-bug-api"]["status"] == "error"
        assert "LP API unavailable" in ctx.evidence["adapters"]["lp-bug-api"]["message"]

        # ubuntu-cve-tracker should still be collected
        assert ctx.evidence["adapters"]["ubuntu-cve-tracker"]["status"] == "ok"


def test_collect_from_catalog_marks_unimplemented_adapters():
    """Adapters without collectors should be marked as pending."""
    ctx = Mock()
    ctx.catalog = {
        "checks": [
            {"id": "NEW-1", "adapters_required": ["new-adapter"]},
        ]
    }
    ctx.evidence = {}

    with patch.dict("evidence.ADAPTER_REGISTRY", {}, clear=True):
        collect_from_catalog(ctx)

        # new-adapter should be marked as pending
        assert ctx.evidence["adapters"]["new-adapter"]["status"] == "pending"
        assert "Unknown adapter" in ctx.evidence["adapters"]["new-adapter"]["message"]


# ---------------------------------------------------------------------------
# Adapter output structure validation
# ---------------------------------------------------------------------------


def test_lp_bug_api_output_structure():
    """lp-bug-api adapter should return expected structure."""
    ctx = Mock()
    ctx.bug_id = "1234567"
    ctx.bug = {
        "title": "MIR for testpkg",
        "description": "Test description",
        "tags": ["mir"],
        "comments": ["Comment 1"],
        "subscribers": ["ubuntu-mir"],
    }
    ctx.source_package = "testpkg"
    ctx.series = "noble"

    from evidence.host_adapters import collect_lp_bug_api

    result = collect_lp_bug_api(ctx)

    assert result["status"] == "ok"
    assert result["bug_id"] == "1234567"
    assert result["target_source_package"] == "testpkg"
    assert "bug_title" in result
    assert "bug_description" in result
    assert "bug_tags" in result
    assert "bug_comments" in result
    assert "bug_subscribers" in result


def test_lp_build_api_output_structure():
    """lp-build-api adapter should return normalized build records."""
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.series = "noble"

    fake_record = Mock()
    fake_record.arch_tag = "amd64"
    fake_record.buildstate = "Successfully built"
    fake_record.build_reason = ""
    fake_record.source_package_version = "1.0"
    fake_record.date_created = "2026-06-23"
    fake_record.pocket = "Release"
    fake_record.archive = Mock(name="ubuntu")

    fake_source_pkg = Mock()
    fake_source_pkg.getBuildRecords.return_value = [fake_record]

    fake_series = Mock()

    fake_ubuntu = Mock()
    fake_ubuntu.getSeries.return_value = fake_series
    fake_ubuntu.getSourcePackage.return_value = fake_source_pkg

    fake_lp = Mock()
    fake_lp.distributions = {"ubuntu": fake_ubuntu}

    with patch("evidence.host_adapters._Launchpad") as mock_launchpad:
        mock_launchpad.login_anonymously.return_value = fake_lp

        from evidence.host_adapters import collect_lp_build_api

        result = collect_lp_build_api(ctx)

    assert result["status"] == "ok"
    assert result["source_package"] == "testpkg"
    assert result["series"] == "noble"
    assert result["builds"][0]["arch_tag"] == "amd64"
    assert result["builds"][0]["build_state"] == "Successfully built"


def test_upstream_tracker_output_structure():
    """upstream-tracker adapter should return latest version and release history."""
    ctx = Mock()
    ctx.source_package = "testpkg"

    payload = {
        "items": [
            {
                "name": "testpkg",
                "homepage": "https://example.invalid/testpkg",
                "version": "2.4.1",
                "open_bugs": 3,
                "versions": ["2.4.1", "2.4.0", "2.3.9"],
                "last_release_date": "2026-06-01",
            }
        ]
    }

    with patch("evidence.host_adapters._fetch_json", return_value=payload):
        from evidence.host_adapters import collect_upstream_tracker

        result = collect_upstream_tracker(ctx)

    assert result["status"] == "ok"
    assert result["latest_version"] == "2.4.1"
    assert result["recent_releases"][0]["version"] == "2.4.1"
    assert result["upstream_url"] == "https://example.invalid/testpkg"


def test_dep_analysis_output_structure():
    """dep-analysis adapter should return expected structure."""
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.requested_binaries = []
    ctx.evidence = {
        "adapters": {
            "packaging-source": {
                "status": "ok",
                "source_dir": "/tmp/test",
            },
            "sbuild": {
                "status": "ok",
                "build_success": True,
                "built_debs": [
                    "/tmp/sbuild-output/testpkg_1.0_amd64.deb",
                    "/tmp/sbuild-output/testpkg-dev_1.0_amd64.deb",
                ],
            },
        }
    }

    # Mock the container execution functions
    with patch("evidence.container_adapters._capture") as mock_capture:
        with patch("evidence.container_adapters._detect_component") as mock_component:
            mock_capture.side_effect = [
                "testpkg\ntestpkg-dev",  # binaries_raw from debian/control
                "testpkg",  # Package field for deb1
                "libc6, libssl3",  # Depends for deb1
                "testpkg-dev",  # Package field for deb2
                "libc6",  # Depends for deb2
                "",  # apt-cache show libc6 (empty -> source_pkg = dep name)
                "",  # apt-cache show libssl3
            ]
            mock_component.return_value = "main"

            from evidence.container_adapters import collect_dep_analysis

            result = collect_dep_analysis(ctx)

            assert result["status"] == "ok"
            assert "binary_packages" in result
            assert "runtime_deps" in result
            assert "runtime_dep_packages" in result
            assert "dep_components" in result
            assert "deps_not_in_main" in result


def test_lintian_output_structure():
    """lintian adapter should expose parsed sbuild lintian output."""
    ctx = Mock()
    ctx.evidence = {
        "adapters": {
            "sbuild": {
                "status": "ok",
                "lintian_output": (
                    "W: testpkg: description-synopsis-starts-with-article\n"
                    "E: testpkg: unknown-field"
                ),
            }
        }
    }

    from evidence.container_adapters import collect_lintian

    result = collect_lintian(ctx)

    assert result["status"] == "ok"
    assert result["lintian_errors"] == ["E: testpkg: unknown-field"]
    assert result["lintian_warnings"] == ["W: testpkg: description-synopsis-starts-with-article"]

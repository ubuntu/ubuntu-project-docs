"""Integration tests for evidence collection orchestration."""

import json
import sys
import urllib.error
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evidence import (
    AdapterError,
    _ensure_adapters_registered,
    _order_adapters,
    collect_from_catalog,
)

# Register all adapters into the real registry up front. Several tests below use
# patch.dict("evidence.ADAPTER_REGISTRY", ..., clear=True); if the lazy first
# import of the guest/team adapter modules happened inside such a cleared
# context, their decorator registrations would be discarded on patch exit and
# lost for the rest of the session (modules are cached, so they never re-run).
_ensure_adapters_registered()

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


def test_collect_from_catalog_propagates_failed_dependency_to_downstream_adapter():
    """Downstream adapters should be marked as failed when an upstream dependency fails."""
    ctx = Mock()
    ctx.catalog = {
        "checks": [
            {"id": "DEP-1", "adapters_required": ["packaging-source", "dep-analysis"]},
        ]
    }
    ctx.evidence = {}
    ctx.collect_only = False

    mock_packaging = Mock(side_effect=AdapterError("cannot fetch packaging source"))
    mock_dep = Mock(return_value={"status": "ok"})

    with patch.dict(
        "evidence.ADAPTER_REGISTRY",
        {
            "packaging-source": (mock_packaging, []),
            "dep-analysis": (mock_dep, ["packaging-source"]),
        },
        clear=True,
    ):
        result = collect_from_catalog(ctx)

    assert result == 1
    assert ctx.evidence["adapters"]["packaging-source"]["status"] == "error"
    assert ctx.evidence["adapters"]["dep-analysis"]["status"] == "error"
    assert (
        "upstream dependency failed: packaging-source"
        in ctx.evidence["adapters"]["dep-analysis"]["message"]
    )
    assert mock_packaging.called
    assert not mock_dep.called


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


def test_all_catalog_adapters_are_registered():
    """Every adapter referenced by the catalog must have a registered collector.

    Guards against a collector function losing (or never gaining) its @adapter
    decorator, which silently drops it from ADAPTER_REGISTRY and turns every
    dependent check into an "Unknown adapter" TODO at runtime.
    """
    import catalog
    from evidence.registry import ADAPTER_REGISTRY

    catalog_path = Path(__file__).resolve().parent.parent / "catalog.yaml"
    workspace_root = Path(__file__).resolve().parent.parent.parent.parent
    catalog_data = catalog.load_catalog(catalog_path, workspace_root)

    referenced: set[str] = set()
    for check in catalog_data.get("checks", []):
        referenced.update(check.get("adapters_required", []))
        referenced.update(check.get("adapters_optional", []))

    _ensure_adapters_registered()
    missing = sorted(referenced - set(ADAPTER_REGISTRY))
    assert not missing, f"Catalog references unregistered adapters: {missing}"


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


def test_lp_bug_search_api_output_structure():
    """lp-bug-search-api should return open, critical, and security bug slices."""
    ctx = Mock()
    ctx.source_package = "testpkg"

    task_page = {
        "entries": [
            {
                "bug_link": "https://api.launchpad.net/devel/bugs/111",
                "web_link": "https://bugs.launchpad.net/bugs/111",
                "status": "New",
                "importance": "Critical",
                "date_created": "2026-06-01T00:00:00+00:00",
            },
            {
                "bug_link": "https://api.launchpad.net/devel/bugs/222",
                "web_link": "https://bugs.launchpad.net/bugs/222",
                "status": "Confirmed",
                "importance": "Medium",
                "date_created": "2026-06-02T00:00:00+00:00",
            },
            {
                "bug_link": "https://api.launchpad.net/devel/bugs/333",
                "web_link": "https://bugs.launchpad.net/bugs/333",
                "status": "Fix Released",
                "importance": "High",
                "date_created": "2026-06-03T00:00:00+00:00",
            },
        ],
        "next_collection_link": None,
    }
    bug_111 = {
        "title": "CVE-2026-0001 testpkg privilege escalation",
        "tags": ["security", "patch"],
    }
    bug_222 = {
        "title": "testpkg cosmetic regression",
        "tags": ["ui"],
    }

    def fake_fetch(url: str):
        if "ws.op=searchTasks" in url:
            return task_page
        if url.endswith("/111"):
            return bug_111
        if url.endswith("/222"):
            return bug_222
        raise AssertionError(f"unexpected url: {url}")

    with patch("evidence.host_adapters._fetch_json", side_effect=fake_fetch):
        from evidence.host_adapters import collect_lp_bug_search_api

        result = collect_lp_bug_search_api(ctx)

    assert result["status"] == "ok"
    assert result["source_package"] == "testpkg"
    assert result["total_open_bug_count"] == 2
    assert [bug["id"] for bug in result["open_bugs"]] == ["111", "222"]
    assert [bug["id"] for bug in result["critical_bugs"]] == ["111"]
    assert [bug["id"] for bug in result["security_bugs"]] == ["111"]
    assert result["open_bugs"][0]["title"] == "CVE-2026-0001 testpkg privilege escalation"


def test_lp_mir_history_matches_prior_mir_bug_under_predecessor_name():
    """lp-mir-history keeps only MIR-titled bugs and records the matched name."""
    ctx = Mock()
    ctx.source_package = "libfoo2"
    ctx.evidence = {
        "adapters": {
            "cve-search-terms": {
                "terms": [
                    {"term": "libfoo", "kind": "predecessor", "rationale": "old name"},
                    {"term": "libfoo2", "kind": "current", "rationale": "self"},
                ]
            }
        }
    }

    # Two tasks: one is a real "[MIR] libfoo" bug, the other mentions 'mirror'
    # and must be filtered out by the whole-word MIR title match.
    task_page = {
        "entries": [
            {
                "bug_link": "https://api.launchpad.net/devel/bugs/900",
                "web_link": "https://bugs.launchpad.net/bugs/900",
                "status": "Fix Released",
            },
            {
                "bug_link": "https://api.launchpad.net/devel/bugs/901",
                "web_link": "https://bugs.launchpad.net/bugs/901",
                "status": "New",
            },
        ],
    }
    bug_900 = {"title": "[MIR] libfoo"}
    bug_901 = {"title": "libfoo mirror selection is wrong"}

    def fake_fetch(url: str):
        if "+source/libfoo2" in url:
            # No MIR bugs filed under the current name.
            return {"entries": []}
        if "+source/libfoo" in url:
            return task_page
        if url.endswith("/900"):
            return bug_900
        if url.endswith("/901"):
            return bug_901
        raise AssertionError(f"unexpected url: {url}")

    with patch("evidence.host_adapters._fetch_json", side_effect=fake_fetch):
        from evidence.host_adapters import collect_lp_mir_history

        result = collect_lp_mir_history(ctx)

    assert result["status"] == "ok"
    assert result["source_package"] == "libfoo2"
    assert "libfoo" in result["candidate_names"]
    prior = result["prior_mir_bugs"]
    assert len(prior) == 1
    assert prior[0]["id"] == "900"
    assert prior[0]["matched_name"] == "libfoo"
    assert prior[0]["title"] == "[MIR] libfoo"


def test_lp_mir_history_skips_missing_source_names_gracefully():
    """A 404 for one candidate name is skipped, not fatal."""
    import urllib.error

    ctx = Mock()
    ctx.source_package = "libfoo"
    ctx.evidence = {"adapters": {}}

    def fake_fetch(url: str):
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)

    with patch("evidence.host_adapters._fetch_json", side_effect=fake_fetch):
        from evidence.host_adapters import collect_lp_mir_history

        result = collect_lp_mir_history(ctx)

    assert result["status"] == "ok"
    assert result["prior_mir_bugs"] == []


def test_debian_bts_output_structure():
    """debian-bts adapter should classify RC and security bugs from BTS HTML."""
    ctx = Mock()
    ctx.source_package = "testpkg"

    page_html = """
    <H2 CLASS="outstanding"><a name="_0_3_2"></a>
    Outstanding bugs -- Important bugs; Patch Available (1 bug)</H2>
    <div class="msgreceived">
    <UL class="bugs">
    <li><div class="shortbugstatus">
      <a href="bugreport.cgi?bug=111">#111</a>
      [<font face="fixed"><span class="link"><abbr title="important">i</abbr>
      |<abbr title="security">S</abbr></span></font>]
      [<a class="submitter" href="pkgreport.cgi?package=testpkg">testpkg</a>]
      <a href="bugreport.cgi?bug=111">testpkg: CVE-2026-0001 privilege escalation</a>
      <div id="extra_status_111" class="shortbugstatusextra">
      <span>Severity: important;</span>
      <span>Tags: patch, security, upstream;</span>
      </div>
    </div></li>
    </UL>
    </div>
    <H2 CLASS="outstanding"><a name="_0_1_4"></a>
    Outstanding bugs -- Critical bugs; Unclassified (1 bug)</H2>
    <div class="msgreceived">
    <UL class="bugs">
    <li><div class="shortbugstatus">
      <a href="bugreport.cgi?bug=222">#222</a>
      [<a class="submitter" href="pkgreport.cgi?package=testpkg">testpkg</a>]
      <a href="bugreport.cgi?bug=222">testpkg: release-blocking crash</a>
      <div id="extra_status_222" class="shortbugstatusextra">
      <span>Severity: critical;</span>
      <span>Tags: patch;</span>
      </div>
    </div></li>
    </UL>
    </div>
    """

    with patch("evidence.host_adapters._fetch_text", return_value=page_html):
        from evidence.host_adapters import collect_debian_bts

        result = collect_debian_bts(ctx)

    assert result["status"] == "ok"
    assert result["source_package"] == "testpkg"
    assert result["total_open_bug_count"] == 2
    assert [bug["id"] for bug in result["security_bugs"]] == ["111"]
    assert [bug["id"] for bug in result["rc_bugs"]] == ["222"]
    assert result["open_bugs"][0]["web_link"].startswith("https://bugs.debian.org/")


def test_cve_search_terms_output_structure():
    """cve-search-terms adapter should emit deterministic current-package term variants."""
    ctx = Mock()
    ctx.source_package = "python3-foo"
    ctx.llm_token = ""  # disable the predecessor LLM step
    ctx.evidence = {"adapters": {}}

    from evidence.host_adapters import collect_cve_search_terms

    result = collect_cve_search_terms(ctx)

    assert result["status"] == "ok"
    assert result["source_package"] == "python3-foo"
    term_values = [t["term"] for t in result["terms"]]
    assert "python3-foo" in term_values
    assert "foo" in term_values
    assert all(t["kind"] == "current" for t in result["terms"])


def test_cve_search_terms_adds_predecessor_terms():
    """cve-search-terms should append LLM-proposed predecessor terms, tagged and bounded."""
    ctx = Mock()
    ctx.source_package = "lua5.5"
    ctx.llm_token = "token"
    ctx.tool_root = None  # force fallback prompt template
    ctx.reporter_mir_content = "lua 5.5 interpreter"
    ctx.evidence = {
        "adapters": {
            "upstream-tracker": {
                "upstream_url": "https://www.lua.org",
                "latest_version": "5.5.0",
                "recent_releases": [{"version": "5.5.0"}, {"version": "5.4.7"}],
            }
        }
    }

    llm_response = {
        "terms": [
            {"term": "lua", "kind": "predecessor", "rationale": "upstream project"},
            {"term": "lua5.4", "kind": "predecessor", "rationale": "sibling version"},
            # duplicate of current term should be dropped
            {"term": "lua5.5", "kind": "predecessor", "rationale": "self"},
        ]
    }

    with patch("evidence.host_adapters.llm.call_llm", return_value=llm_response) as mock_llm:
        from evidence.host_adapters import collect_cve_search_terms

        result = collect_cve_search_terms(ctx)

    mock_llm.assert_called_once()
    by_kind = {t["term"]: t["kind"] for t in result["terms"]}
    assert by_kind["lua5.5"] == "current"
    assert by_kind["lua"] == "predecessor"
    assert by_kind["lua5.4"] == "predecessor"
    # The predecessor variant duplicating the current term must not be re-added.
    assert sum(1 for t in result["terms"] if t["term"] == "lua5.5") == 1


def test_cve_search_terms_degrades_on_llm_error():
    """cve-search-terms must fall back to current-only terms when the LLM fails."""
    from evidence.host_adapters import collect_cve_search_terms
    from llm import LLMError

    ctx = Mock()
    ctx.source_package = "lua5.5"
    ctx.llm_token = "token"
    ctx.tool_root = None
    ctx.reporter_mir_content = ""
    ctx.evidence = {"adapters": {}}

    with patch("evidence.host_adapters.llm.call_llm", side_effect=LLMError("boom")):
        result = collect_cve_search_terms(ctx)

    assert result["status"] == "ok"
    assert all(t["kind"] == "current" for t in result["terms"])


def test_cvelist_scan_output_structure():
    """cvelist-scan adapter should run on host and return expected structure."""
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.evidence = {
        "adapters": {
            "cve-search-terms": {
                "status": "ok",
                "terms": [{"term": "testpkg", "kind": "current", "rationale": "name"}],
            }
        }
    }

    import evidence.host_adapters as host_adapters

    candidates = [
        {
            "id": "CVE-2026-0001",
            "matched_term": "testpkg",
            "matched_kind": "current",
            "title": "testpkg flaw",
            "description": "Flaw in testpkg",
            "affected_products": ["testpkg"],
            "affected_versions": ["1.0"],
            "references": [],
            "severity": "HIGH",
            "published_date": "2026-06-01T00:00:00Z",
        }
    ]

    with patch.object(
        host_adapters,
        "_cvelist_discover_baseline",
        return_value=("2026-06-25_all_CVEs_at_midnight.zip", "https://example.invalid/base.zip"),
    ):
        with patch.object(host_adapters.http_utils, "download_to_file"):
            with patch("evidence.cvelist_scan_invm.scan_zip", return_value=candidates):
                result = host_adapters.collect_cvelist_scan(ctx)

    assert result["status"] == "ok"
    assert result["source_package"] == "testpkg"
    assert result["baseline"] == "2026-06-25_all_CVEs_at_midnight.zip"
    assert result["scanned_terms"] == ["testpkg"]
    assert result["total_candidate_count"] == 1
    assert result["candidates"][0]["id"] == "CVE-2026-0001"


def test_cvelist_scan_skips_without_terms():
    """cvelist-scan adapter should no-op cleanly when no search terms are present."""
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.evidence = {"adapters": {"cve-search-terms": {"status": "ok", "terms": []}}}

    import evidence.host_adapters as host_adapters

    with patch.object(host_adapters.http_utils, "download_to_file") as mock_download:
        result = host_adapters.collect_cvelist_scan(ctx)

    mock_download.assert_not_called()
    assert result["status"] == "ok"
    assert result["candidates"] == []
    assert result["total_candidate_count"] == 0


def test_cvelist_scan_reports_discovery_failure():
    """cvelist-scan should raise AdapterError when baseline discovery fails."""
    import evidence.host_adapters as host_adapters

    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.evidence = {
        "adapters": {
            "cve-search-terms": {
                "status": "ok",
                "terms": [{"term": "testpkg", "kind": "current", "rationale": "name"}],
            }
        }
    }

    with patch.object(
        host_adapters, "_cvelist_discover_baseline", side_effect=RuntimeError("boom")
    ):
        try:
            host_adapters.collect_cvelist_scan(ctx)
            assert False, "collect_cvelist_scan should raise AdapterError on discovery failures"
        except host_adapters.AdapterError as exc:
            assert "cvelist-scan failed on host" in str(exc)


def test_nvd_enrich_output_structure():
    """nvd-enrich adapter should enrich candidates and tag historical predecessors."""
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.evidence = {
        "adapters": {
            "cvelist-scan": {
                "status": "ok",
                "candidates": [
                    {
                        "id": "CVE-2026-0001",
                        "matched_kind": "current",
                        "title": "testpkg flaw",
                        "description": "cvelist description",
                        "affected_products": ["testpkg"],
                        "affected_versions": ["1.0"],
                        "severity": "MEDIUM",
                    },
                    {
                        "id": "CVE-2020-0002",
                        "matched_kind": "predecessor",
                        "title": "legacy flaw",
                        "description": "cvelist legacy description",
                        "affected_products": ["oldpkg"],
                        "affected_versions": ["0.9"],
                        "severity": "LOW",
                    },
                ],
            }
        }
    }

    nvd_records = {
        "CVE-2026-0001": {
            "id": "CVE-2026-0001",
            "descriptions": [{"lang": "en", "value": "NVD description"}],
            "metrics": {
                "cvssMetricV31": [
                    {"baseSeverity": "HIGH", "cvssData": {"baseScore": 8.8, "baseSeverity": "HIGH"}}
                ]
            },
            "weaknesses": [
                {"description": [{"value": "CWE-79"}]},
            ],
            "configurations": [],
        }
    }

    def fake_lookup(cve_id):
        return nvd_records.get(cve_id)

    with patch("evidence.host_adapters._nvd_lookup", side_effect=fake_lookup):
        with patch("evidence.host_adapters.time.sleep"):
            from evidence.host_adapters import collect_nvd_enrich

            result = collect_nvd_enrich(ctx)

    assert result["status"] == "ok"
    assert result["source_package"] == "testpkg"
    assert result["total_cve_count"] == 2

    by_id = {c["id"]: c for c in result["cves"]}
    enriched = by_id["CVE-2026-0001"]
    assert enriched["enrichment_source"] == "nvd"
    assert enriched["severity"] == "HIGH"
    assert enriched["cwe"] == ["CWE-79"]
    assert enriched["description"] == "NVD description"

    # Fallback to cvelist data when NVD has no record.
    fallback = by_id["CVE-2020-0002"]
    assert fallback["enrichment_source"] == "cvelist"
    assert fallback["severity"] == "LOW"

    assert [c["id"] for c in result["high_severity_cves"]] == ["CVE-2026-0001"]
    assert [c["id"] for c in result["historical_cves"]] == ["CVE-2020-0002"]


def test_scan_zip_identifies_candidates(tmp_path):
    """scan_zip should word-match CVE records and dedupe by ID."""
    import zipfile

    from evidence.cvelist_scan_invm import scan_zip

    matching = {
        "cveMetadata": {"cveId": "CVE-2026-1234", "datePublished": "2026-06-01T00:00:00Z"},
        "containers": {
            "cna": {
                "title": "testpkg buffer overflow",
                "descriptions": [{"lang": "en", "value": "Overflow in testpkg parser"}],
                "affected": [{"vendor": "Example", "product": "testpkg"}],
                "metrics": [{"cvssV3_1": {"baseScore": 7.5, "baseSeverity": "HIGH"}}],
            }
        },
    }
    noise = {
        "cveMetadata": {"cveId": "CVE-2026-9999", "datePublished": "2026-06-02T00:00:00Z"},
        "containers": {
            "cna": {
                "title": "unrelated issue",
                "descriptions": [{"lang": "en", "value": "Something about testpkgextra only"}],
                "affected": [{"vendor": "Other", "product": "otherpkg"}],
                "metrics": [],
            }
        },
    }

    zip_path = tmp_path / "baseline.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("cves/2026/CVE-2026-1234.json", json.dumps(matching))
        zf.writestr("cves/2026/CVE-2026-9999.json", json.dumps(noise))
        zf.writestr("README.md", "not a cve")

    candidates = scan_zip(str(zip_path), [{"term": "testpkg", "kind": "current"}])

    assert [c["id"] for c in candidates] == ["CVE-2026-1234"]
    assert candidates[0]["matched_kind"] == "current"
    assert candidates[0]["affected_products"] == ["testpkg", "Example"]
    assert candidates[0]["severity"] == "HIGH"


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


def test_upstream_tracker_uses_watch_and_homepage_hints_for_search():
    """upstream-tracker should fall back to upstream hints when package name misses."""
    ctx = Mock()
    ctx.source_package = "lua5.5"
    ctx.evidence = {
        "adapters": {
            "packaging-source": {
                "status": "ok",
                "debian_watch": "version=4\nhttps://www.lua.org/ftp/lua-(\\d.*)\\.tar\\.gz\n",
                "debian_control": "Source: lua5.5\nHomepage: https://www.lua.org/\nVcs-Git: https://salsa.debian.org/lua-team/lua5.5.git\n",
            }
        }
    }

    def _fake_fetch(url):
        if "name=lua5.5" in url:
            return {"items": []}
        if "name=lua" in url:
            return {
                "items": [
                    {
                        "name": "lua",
                        "homepage": "https://www.lua.org/",
                        "version": "5.5.0",
                        "open_bugs": 1,
                        "versions": ["5.5.0", "5.4.8"],
                        "last_release_date": "2026-06-01",
                    }
                ]
            }
        raise AssertionError(f"unexpected URL: {url}")

    with patch("evidence.host_adapters._fetch_json", side_effect=_fake_fetch) as mock_fetch:
        from evidence.host_adapters import collect_upstream_tracker

        result = collect_upstream_tracker(ctx)

    assert result["status"] == "ok"
    assert result["latest_version"] == "5.5.0"
    assert result["upstream_url"] == "https://www.lua.org/"
    queried_urls = [call.args[0] for call in mock_fetch.call_args_list]
    assert any("name=lua5.5" in url for url in queried_urls)
    assert any("name=lua" in url for url in queried_urls)
    assert not any("salsa" in url for url in queried_urls)


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

    # Mock the in-guest execution functions
    with patch("evidence.guest_adapters._capture") as mock_capture:
        with patch("evidence.guest_adapters._detect_component") as mock_component:
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

            from evidence.guest_adapters import collect_dep_analysis

            result = collect_dep_analysis(ctx)

            assert result["status"] == "ok"
            assert "binary_packages" in result
            assert "runtime_deps" in result
            assert "runtime_dep_packages" in result
            assert "dep_components" in result
            assert "deps_not_in_main" in result


def test_dep_analysis_same_source_auto_included_dep_not_offending():
    """An auto-included dep built by the same source is part of this MIR request.

    libebur128-dev auto-includes libebur128-1 which is currently in universe but
    is being promoted by this very request. It must land in the same-source
    bucket, not the offending bucket.
    """
    ctx = Mock()
    ctx.source_package = "libebur128"
    ctx.requested_binaries = []
    ctx.evidence = {
        "adapters": {
            "packaging-source": {"status": "ok", "source_dir": "/tmp/test"},
            "sbuild": {
                "status": "ok",
                "build_success": True,
                "built_debs": [
                    "/tmp/out/libebur128-1_1.0_amd64.deb",
                    "/tmp/out/libebur128-dev_1.0_amd64.deb",
                ],
            },
        }
    }

    with patch("evidence.guest_adapters._capture") as mock_capture:
        with patch("evidence.guest_adapters._detect_component") as mock_component:
            mock_capture.side_effect = [
                "libebur128-1\nlibebur128-dev",  # binaries from debian/control
                "libebur128-1",  # deb1 Package
                "libc6",  # deb1 Depends
                "libebur128-dev",  # deb2 Package
                "libebur128-1",  # deb2 Depends
                "",  # apt-cache show libc6 -> source = libc6
                "libebur128",  # apt-cache show libebur128-1 -> source = libebur128
            ]
            mock_component.side_effect = lambda _ctx, pkg: (
                "universe" if pkg == "libebur128-1" else "main"
            )

            from evidence.guest_adapters import collect_dep_analysis

            result = collect_dep_analysis(ctx)

    assert result["status"] == "ok"
    assert result["auto_included_binaries"] == ["libebur128-dev"]
    assert result["auto_included_deps_not_in_main_or_unknown"] == []
    assert result["auto_included_deps_same_source"] == ["libebur128-1"]
    assert result["auto_included_same_source_deps_by_binary"] == [
        {"binary": "libebur128-dev", "dependencies": ["libebur128-1"]}
    ]
    assert result["auto_included_offending_deps_by_binary"] == [
        {"binary": "libebur128-dev", "dependencies": []}
    ]


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

    from evidence.guest_adapters import collect_lintian

    result = collect_lintian(ctx)

    assert result["status"] == "ok"
    assert result["lintian_errors"] == ["E: testpkg: unknown-field"]
    assert result["lintian_warnings"] == ["W: testpkg: description-synopsis-starts-with-article"]


# ---------------------------------------------------------------------------
# lto-disabled-list adapter
# ---------------------------------------------------------------------------

_LTO_LIST_SAMPLE = """\
# list of source packages not to build with link time optimization (LTO).
#
# packages in main:
abinit any
abiword arm64
# packages not in main:
llvm arm64 s390x
zfs-fuse amd64 ppc64el
"""


def test_parse_lto_disabled_list_skips_comments_and_blanks():
    """Parser keeps source->arches mappings and ignores comments/blank lines."""
    from evidence.lto_disabled_adapter import _parse_lto_disabled_list

    mapping = _parse_lto_disabled_list(_LTO_LIST_SAMPLE)

    assert mapping == {
        "abinit": ["any"],
        "abiword": ["arm64"],
        "llvm": ["arm64", "s390x"],
        "zfs-fuse": ["amd64", "ppc64el"],
    }


def test_collect_lto_disabled_list_on_list():
    """Adapter reports on_list with the architectures for a listed package."""
    from evidence import lto_disabled_adapter

    ctx = Mock()
    ctx.source_package = "llvm"

    with patch.object(lto_disabled_adapter.http_utils, "get_text", return_value=_LTO_LIST_SAMPLE):
        result = lto_disabled_adapter.collect_lto_disabled_list(ctx)

    assert result["status"] == "ok"
    assert result["on_list"] is True
    assert result["disabled_arches"] == ["arm64", "s390x"]


def test_collect_lto_disabled_list_not_on_list():
    """Adapter reports on_list False for an unlisted package."""
    from evidence import lto_disabled_adapter

    ctx = Mock()
    ctx.source_package = "testpkg"

    with patch.object(lto_disabled_adapter.http_utils, "get_text", return_value=_LTO_LIST_SAMPLE):
        result = lto_disabled_adapter.collect_lto_disabled_list(ctx)

    assert result["status"] == "ok"
    assert result["on_list"] is False
    assert result["disabled_arches"] == []


def test_collect_lto_disabled_list_fetch_error():
    """Adapter returns error status when the list cannot be fetched."""
    from evidence import lto_disabled_adapter

    ctx = Mock()
    ctx.source_package = "testpkg"

    with patch.object(
        lto_disabled_adapter.http_utils, "get_text", side_effect=OSError("network unreachable")
    ):
        result = lto_disabled_adapter.collect_lto_disabled_list(ctx)

    assert result["status"] == "error"
    assert "network unreachable" in result["error"]


# ---------------------------------------------------------------------------
# team-mapping adapter
# ---------------------------------------------------------------------------


def test_collect_team_mapping_filters_non_subscriber_teams():
    """Team mapping adapter should filter non-subscriber/display-only teams."""
    from evidence import team_mapping_adapter

    ctx = Mock()
    ctx.source_package = "mypkg"

    payload = {
        "ubuntu-server": ["mypkg"],
        "kubuntu-bugs": ["mypkg"],
        "unsubscribed": ["mypkg"],
    }

    with patch.object(team_mapping_adapter.http_utils, "get_json", return_value=payload):
        result = team_mapping_adapter.collect_team_mapping(ctx)

    assert result["status"] == "ok"
    assert result["subscribed_teams"] == ["ubuntu-server"]
    assert "kubuntu-bugs" not in result["team_mapping"]
    assert "unsubscribed" not in result["team_mapping"]


def test_collect_team_mapping_fetch_error():
    """Team mapping adapter should return error status when fetch fails."""
    from evidence import team_mapping_adapter

    ctx = Mock()
    ctx.source_package = "mypkg"

    with patch.object(
        team_mapping_adapter.http_utils, "get_json", side_effect=OSError("network unreachable")
    ):
        result = team_mapping_adapter.collect_team_mapping(ctx)

    assert result["status"] == "error"
    assert "network unreachable" in result["error"]


# ---------------------------------------------------------------------------
# adapter HTTP error propagation
# ---------------------------------------------------------------------------


def test_collect_autopkgtest_reports_http_error_code():
    """autopkgtest adapter should preserve HTTP status context in AdapterError."""
    import evidence.host_adapters as ha

    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.series = "noble"

    http_error = urllib.error.HTTPError(
        "https://autopkgtest.ubuntu.com/static/autopkgtest.db",
        429,
        "Too Many Requests",
        None,
        None,
    )

    with patch.object(ha, "_download_autopkgtest_db", side_effect=http_error):
        try:
            ha.collect_autopkgtest(ctx)
            assert False, "collect_autopkgtest should raise AdapterError on HTTP errors"
        except ha.AdapterError as exc:
            assert "autopkgtest DB download HTTP error 429" in str(exc)


def test_collect_ubuntu_cve_tracker_reports_http_error_code():
    """OVAL adapter should preserve HTTP status context in AdapterError."""
    import evidence.host_adapters as ha

    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.series = "noble"

    http_error = urllib.error.HTTPError(
        "https://security-metadata.canonical.com/oval/com.ubuntu.noble.pkg.json.xz",
        429,
        "Too Many Requests",
        None,
        None,
    )

    with patch.object(ha, "_resolve_oval_series", return_value=("noble", None)):
        with patch.object(ha, "_download_oval_xz", side_effect=http_error):
            try:
                ha.collect_ubuntu_cve_tracker(ctx)
                assert False, "collect_ubuntu_cve_tracker should raise AdapterError on HTTP errors"
            except ha.AdapterError as exc:
                assert "OVAL HTTP error 429" in str(exc)


# ---------------------------------------------------------------------------
# Release cadence summarisation (lp-package-api)
# ---------------------------------------------------------------------------


def test_release_cadence_unknown_with_few_dates():
    from evidence.host_adapters import summarise_release_cadence

    assert summarise_release_cadence([])["descriptor"] == "unknown"
    one = [{"version": "1.0-1", "date_published": "2024-01-01 00:00:00+00:00"}]
    assert summarise_release_cadence(one)["descriptor"] == "unknown"


def test_release_cadence_good_when_frequent():
    from evidence.host_adapters import summarise_release_cadence

    history = [
        {"version": "1.0-1", "date_published": "2024-01-01 00:00:00+00:00"},
        {"version": "1.0-2", "date_published": "2024-03-01 00:00:00+00:00"},
        {"version": "1.0-3", "date_published": "2024-05-01 00:00:00+00:00"},
    ]
    result = summarise_release_cadence(history)
    assert result["descriptor"] == "good"
    assert result["releases"] == 3


def test_release_cadence_sporadic_when_rare():
    from evidence.host_adapters import summarise_release_cadence

    history = [
        {"version": "1.0-1", "date_published": "2018-01-01 00:00:00+00:00"},
        {"version": "2.0-1", "date_published": "2024-01-01 00:00:00+00:00"},
    ]
    assert summarise_release_cadence(history)["descriptor"] == "sporadic"


def test_release_cadence_deduplicates_versions():
    from evidence.host_adapters import summarise_release_cadence

    # Same version published to multiple pockets/series must count once.
    history = [
        {"version": "1.0-1", "date_published": "2024-01-01 00:00:00+00:00"},
        {"version": "1.0-1", "date_published": "2024-01-05 00:00:00+00:00"},
    ]
    assert summarise_release_cadence(history)["descriptor"] == "unknown"


# ---------------------------------------------------------------------------
# ubuntu-upload-permission parsing
# ---------------------------------------------------------------------------


def test_parse_upload_permission_motu_only():
    from evidence.guest_adapters import _parse_upload_permission

    output = (
        "All upload permissions for lua5.5:\n"
        "\n"
        "Component (universe)\n"
        "====================\n"
        "* MOTU (motu) [team]\n"
        "\n"
        "You can upload lua5.5 to stonking.\n"
    )
    components, teams, individuals = _parse_upload_permission(output)
    assert components == ["universe"]
    assert teams == [{"name": "MOTU (motu)", "component": "universe"}]
    assert individuals == []


def test_parse_upload_permission_individual_uploader():
    from evidence.guest_adapters import _parse_upload_permission

    output = (
        "All upload permissions for foo:\n"
        "\n"
        "Component (main)\n"
        "================\n"
        "* Jane Developer (jane)\n"
        "* Some Team (some-team) [team]\n"
    )
    components, teams, individuals = _parse_upload_permission(output)
    assert components == ["main"]
    assert {"name": "Jane Developer (jane)", "component": "main"} in individuals
    assert {"name": "Some Team (some-team)", "component": "main"} in teams


# ---------------------------------------------------------------------------
# git-ubuntu delta classification
# ---------------------------------------------------------------------------


def test_classify_ubuntu_delta_kinds():
    from evidence.guest_adapters import classify_ubuntu_delta

    assert classify_ubuntu_delta("5.5.0-4") == "sync"
    assert classify_ubuntu_delta("5.5.0-4ubuntu1") == "ubuntu_delta"
    assert classify_ubuntu_delta("1.2.3") == "native"
    assert classify_ubuntu_delta("") == "unknown"
    assert classify_ubuntu_delta("2:1.0-1ubuntu2") == "ubuntu_delta"


# ---------------------------------------------------------------------------
# git-ubuntu delta categorisation (tests-only detection)
# ---------------------------------------------------------------------------


def test_classify_delta_category_tests_only():
    from evidence.guest_adapters import _classify_delta_category

    diffstat = (
        " debian/tests/control | 5 +++++\n"
        " debian/tests/smoke   | 20 ++++++++++++++++++++\n"
        " 2 files changed, 25 insertions(+)"
    )
    assert _classify_delta_category(diffstat) == "tests-only"


def test_classify_delta_category_general():
    from evidence.guest_adapters import _classify_delta_category

    diffstat = (
        " src/foo.c        | 30 ++++++++++++++++++------\n"
        " debian/tests/x   | 4 ++++\n"
        " 2 files changed, 34 insertions(+)"
    )
    assert _classify_delta_category(diffstat) == "general"


def test_classify_delta_category_empty_is_general():
    from evidence.guest_adapters import _classify_delta_category

    assert _classify_delta_category("") == "general"


# ---------------------------------------------------------------------------
# shipped vs test-only vendoring classification
# ---------------------------------------------------------------------------


def test_classify_shipped_vendored_dirs_excludes_test_only():
    from evidence.guest_adapters import _classify_shipped_vendored_dirs

    # tests/third_party is test-only; a top-level vendor dir is shipped.
    dirs = ["./tests/third_party", "./third_party", "./vendor"]
    shipped = _classify_shipped_vendored_dirs(dirs)
    assert "./tests/third_party" not in shipped
    assert "./third_party" in shipped
    assert "./vendor" in shipped


def test_classify_shipped_vendored_dirs_all_test_only():
    from evidence.guest_adapters import _classify_shipped_vendored_dirs

    assert _classify_shipped_vendored_dirs(["./tests/third_party"]) == []


# ---------------------------------------------------------------------------
# binary Section parsing (UI signal for URF-8/URF-9)
# ---------------------------------------------------------------------------


def test_parse_binary_sections():
    from evidence.guest_adapters import _parse_binary_sections

    control = (
        "Source: libgav1\n"
        "Section: libs\n"
        "\n"
        "Package: libgav1-2\n"
        "Section: libs\n"
        "\n"
        "Package: libgav1-dev\n"
        "Section: libdevel\n"
    )
    sections = _parse_binary_sections(control)
    assert sections == ["libs", "libdevel"]


# ---------------------------------------------------------------------------
# autopkgtest release candidate resolution
# ---------------------------------------------------------------------------


def test_autopkgtest_release_candidates_devel(monkeypatch):
    import evidence.host_adapters as ha

    def fake_distro_info(flag):
        return {"--devel": ["stonking"], "--supported": ["jammy", "noble", "resolute"]}.get(
            flag, []
        )

    monkeypatch.setattr(ha, "_distro_info_lines", fake_distro_info)
    candidates = ha._autopkgtest_release_candidates("devel")
    # devel codename first, then newest supported stable as fallback
    assert candidates[0] == "stonking"
    assert "resolute" in candidates


def test_autopkgtest_release_candidates_explicit(monkeypatch):
    import evidence.host_adapters as ha

    def fake_distro_info(flag):
        return {"--devel": ["stonking"], "--supported": ["jammy", "noble", "resolute"]}.get(
            flag, []
        )

    monkeypatch.setattr(ha, "_distro_info_lines", fake_distro_info)
    candidates = ha._autopkgtest_release_candidates("noble")
    assert candidates[0] == "noble"


# ---------------------------------------------------------------------------
# adapters_optional are collected best-effort
# ---------------------------------------------------------------------------


def test_collect_from_catalog_collects_optional_adapters():
    from unittest.mock import Mock

    from evidence import collect_from_catalog

    ctx = Mock()
    ctx.catalog = {
        "checks": [
            {
                "id": "PRF-1",
                "adapters_required": ["packaging-source"],
                "adapters_optional": ["git-ubuntu-delta"],
            },
        ]
    }
    ctx.evidence = {}
    ctx.collect_only = False

    m_pack = Mock(return_value={"status": "ok", "source_dir": "/tmp/x"})
    m_delta = Mock(return_value={"status": "ok", "delta_kind": "sync"})

    with patch.dict(
        "evidence.ADAPTER_REGISTRY",
        {
            "packaging-source": (m_pack, []),
            "git-ubuntu-delta": (m_delta, ["packaging-source"]),
        },
        clear=True,
    ):
        collect_from_catalog(ctx)

    assert m_delta.called
    assert ctx.evidence["adapters"]["git-ubuntu-delta"]["status"] == "ok"


def test_collect_from_catalog_optional_failure_does_not_fail_run():
    from unittest.mock import Mock

    from evidence import collect_from_catalog

    ctx = Mock()
    ctx.catalog = {
        "checks": [
            {
                "id": "PRF-1",
                "adapters_required": ["packaging-source"],
                "adapters_optional": ["git-ubuntu-delta"],
            },
        ]
    }
    ctx.evidence = {}
    ctx.collect_only = False

    m_pack = Mock(return_value={"status": "ok", "source_dir": "/tmp/x"})
    m_delta = Mock(side_effect=AdapterError("git-ubuntu unavailable"))

    with patch.dict(
        "evidence.ADAPTER_REGISTRY",
        {
            "packaging-source": (m_pack, []),
            "git-ubuntu-delta": (m_delta, ["packaging-source"]),
        },
        clear=True,
    ):
        rc = collect_from_catalog(ctx)

    # Optional adapter failure must not flip the overall return status.
    assert rc == 0
    assert ctx.evidence["adapters"]["git-ubuntu-delta"]["status"] == "error"


# ---------------------------------------------------------------------------
# Proposed-pocket source selection (feedback #7)
# ---------------------------------------------------------------------------

from evidence.guest_adapters import (  # noqa: E402
    _latest_published_in_pocket,
    _resolve_source_pocket_version,
)
from lxd_runner import _build_proposed_stanza  # noqa: E402


class _PocketCtx:
    def __init__(self, source_pocket, publish_history):
        self.source_pocket = source_pocket
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
    assert _resolve_source_pocket_version(ctx) == ("0.20.0-2ubuntu1", "proposed")


def test_resolve_auto_falls_back_to_release_without_proposed():
    ctx = _PocketCtx("auto", [_RELEASE])
    assert _resolve_source_pocket_version(ctx) == ("", "release")


def test_resolve_release_never_pins_proposed():
    ctx = _PocketCtx("release", [_RELEASE, _PROPOSED])
    assert _resolve_source_pocket_version(ctx) == ("", "release")


def test_resolve_proposed_requested_but_missing_falls_back():
    ctx = _PocketCtx("proposed", [_RELEASE])
    assert _resolve_source_pocket_version(ctx) == ("", "release")


def test_build_proposed_stanza_derives_from_primary():
    ubuntu_sources = (
        "Types: deb\n"
        "URIs: http://archive.ubuntu.com/ubuntu\n"
        "Suites: stonking stonking-updates stonking-backports\n"
        "Components: main restricted universe multiverse\n"
        "Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg\n"
        "\n"
        "Types: deb\n"
        "URIs: http://security.ubuntu.com/ubuntu\n"
        "Suites: stonking-security\n"
        "Components: main restricted universe multiverse\n"
        "Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg\n"
    )
    stanza = _build_proposed_stanza(ubuntu_sources, "stonking")
    assert "Types: deb deb-src" in stanza
    assert "Suites: stonking-proposed" in stanza
    assert "http://archive.ubuntu.com/ubuntu" in stanza
    # Must not pick the security stanza's URI.
    assert "security.ubuntu.com" not in stanza


def test_build_proposed_stanza_returns_none_without_primary():
    ubuntu_sources = (
        "Types: deb\n"
        "URIs: http://security.ubuntu.com/ubuntu\n"
        "Suites: stonking-security\n"
        "Components: main\n"
    )
    assert _build_proposed_stanza(ubuntu_sources, "stonking") is None


# ---------------------------------------------------------------------------
# dup-search adapter + RDO-1 fallback (feedback #6)
# ---------------------------------------------------------------------------

from types import SimpleNamespace  # noqa: E402

from evidence import guest_adapters  # noqa: E402


def test_extract_binary_descriptions_and_names():
    control = (
        "Source: libgav1\n\n"
        "Package: libgav1-2\n"
        "Description: AV1 decoder developed by Google -- runtime library\n\n"
        "Package: libgav1-dev\n"
        "Description: AV1 decoder -- development files\n"
    )
    assert guest_adapters._extract_binary_descriptions(control) == [
        "AV1 decoder developed by Google -- runtime library",
        "AV1 decoder -- development files",
    ]
    assert guest_adapters._binary_package_names(control) == ["libgav1-2", "libgav1-dev"]


def test_apt_package_component_classifies_universe_and_main():
    calls = []

    def fake_capture(ctx, cmd, allow_fail=False, **kwargs):
        calls.append(cmd)
        # Simulate Section output: universe/libs for libdav1d7, libs for libaom3.
        joined = " ".join(cmd)
        if "libdav1d7" in joined:
            return "universe/libs"
        if "libaom3" in joined:
            return "libs"
        return ""

    with patch.object(guest_adapters, "_capture", side_effect=fake_capture):
        ctx = SimpleNamespace(guest_name="vm")
        assert guest_adapters._apt_package_component(ctx, "libdav1d7") == "universe"
        assert guest_adapters._apt_package_component(ctx, "libaom3") == "main"
        assert guest_adapters._apt_package_component(ctx, "unknownpkg") == "unknown"


def test_collect_dup_search_probes_terms_and_tags_components():
    ctx = SimpleNamespace(
        source_package="libgav1",
        guest_name="vm",
        llm_token="tok",
        untrusted_nonce="N",
        evidence={
            "adapters": {
                "packaging-source": {
                    "status": "ok",
                    "debian_control": (
                        "Source: libgav1\n\n"
                        "Package: libgav1-2\n"
                        "Description: AV1 decoder developed by Google -- runtime library\n"
                    ),
                }
            }
        },
    )

    def fake_capture(ctx_arg, cmd, allow_fail=False, **kwargs):
        joined = " ".join(cmd)
        if cmd[:2] == ["apt-cache", "search"]:
            return "libaom3 - AV1 Video Codec Library\nlibgav1-2 - own package\n"
        if "Section:" in joined and "libaom3" in joined:
            return "libs"
        return ""

    with (
        patch.object(guest_adapters, "_capture", side_effect=fake_capture),
        patch.object(guest_adapters, "_llm_dup_search_terms", return_value=["AV1 decoder"]),
    ):
        result = guest_adapters.collect_dup_search(ctx)

    names = [c["name"] for c in result["candidates"]]
    assert "libaom3" in names
    # The package's own binary must be excluded from candidates.
    assert "libgav1-2" not in names
    assert result["candidates"][0]["component"] == "main"


def test_rdo1_fallback_rationale_lists_dup_candidates():
    import checks.llm_eval as llm_eval

    check = {"id": "RDO-1"}
    ctx = SimpleNamespace(
        evidence={
            "adapters": {
                "dup-search": {
                    "status": "ok",
                    "candidates": [
                        {"name": "libaom3", "synopsis": "AV1", "component": "main"},
                        {"name": "libdav1d7", "synopsis": "AV1", "component": "universe"},
                    ],
                }
            }
        }
    )
    rationale = llm_eval._fallback_rationale_for_check(check, ctx)
    assert "libaom3 (main)" in rationale
    assert "libdav1d7 (universe)" in rationale


def test_fallback_rationale_empty_for_other_checks():
    import checks.llm_eval as llm_eval

    ctx = SimpleNamespace(evidence={"adapters": {}})
    assert llm_eval._fallback_rationale_for_check({"id": "SEC-5"}, ctx) == ""

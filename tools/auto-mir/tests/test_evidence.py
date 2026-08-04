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


def test_catalog_adapter_dependencies_match_registrations():
    import catalog
    from evidence import _catalog_adapter_dependencies
    from evidence.registry import ADAPTER_REGISTRY

    tool_root = Path(__file__).resolve().parent.parent
    workspace_root = tool_root.parent.parent
    catalog_data = catalog.load_catalog(tool_root / "catalog.yaml", workspace_root)
    _ensure_adapters_registered()

    catalog_dependencies = _catalog_adapter_dependencies(catalog_data)
    registered_dependencies = {
        adapter_id: dependencies
        for adapter_id, (_collector, dependencies) in ADAPTER_REGISTRY.items()
    }
    mismatches = {
        adapter_id: (catalog_dependencies.get(adapter_id, []), dependencies)
        for adapter_id, dependencies in registered_dependencies.items()
        if catalog_dependencies.get(adapter_id, []) != dependencies
    }
    assert not mismatches, f"Catalog/registration dependency drift: {mismatches}"


def test_inspect_built_debs_parses_all_binary_surface_sections(monkeypatch):
    from evidence import guest_adapters

    output = """=== STATIC ===
pkg/usr/bin/static-tool
=== SETUIDGID ===
pkg/usr/bin/helper
=== NOBODY ===
pkg/var/lib/data
=== SBIN ===
pkg/usr/sbin/daemon
=== SYSTEMD ===
pkg/usr/lib/systemd/system/daemon.service
=== CRON ===
pkg/etc/cron.daily/daemon
=== APPARMOR ===
pkg/etc/apparmor.d/usr.sbin.daemon
=== DESKTOP ===
pkg/usr/share/applications/daemon.desktop
=== TRANSLATIONS ===
pkg/usr/share/locale/de/LC_MESSAGES/daemon.mo
=== PLUGINS ===
pkg/usr/lib/daemon/plugins/filter.so
=== MAINTSCRIPTS ===
pkg/DEBIAN/postinst
"""
    monkeypatch.setattr(guest_adapters, "_capture", lambda *_args, **_kwargs: output)

    result = guest_adapters._inspect_built_debs(Mock(), "/tmp/output")

    assert result["static_binaries"] == ["pkg/usr/bin/static-tool"]
    assert result["setuid_setgid_binaries"] == ["pkg/usr/bin/helper"]
    assert result["sbin_executables"] == ["pkg/usr/sbin/daemon"]
    assert result["systemd_units"] == ["pkg/usr/lib/systemd/system/daemon.service"]
    assert result["cron_jobs"] == ["pkg/etc/cron.daily/daemon"]
    assert result["apparmor_profiles"] == ["pkg/etc/apparmor.d/usr.sbin.daemon"]
    assert result["desktop_files"] == ["pkg/usr/share/applications/daemon.desktop"]
    assert result["translation_files"] == ["pkg/usr/share/locale/de/LC_MESSAGES/daemon.mo"]
    assert result["plugin_candidates"] == ["pkg/usr/lib/daemon/plugins/filter.so"]
    assert result["maintainer_scripts"] == ["pkg/DEBIAN/postinst"]


def test_binary_package_inspection_projects_sbuild_scan_without_reextracting():
    from evidence.guest_adapters import collect_binary_package_inspection

    ctx = Mock()
    ctx.evidence = {
        "adapters": {
            "sbuild": {
                "status": "ok",
                "static_binaries": [],
                "setuid_setgid_binaries": ["pkg/usr/bin/helper"],
                "nobody_owned_binaries": [],
                "sbin_executables": ["pkg/usr/sbin/daemon"],
                "systemd_units": ["pkg/usr/lib/systemd/system/daemon.service"],
                "cron_jobs": [],
                "apparmor_profiles": [],
                "desktop_files": [],
                "translation_files": [],
                "plugin_candidates": [],
                "maintainer_scripts": ["pkg/DEBIAN/postinst"],
            }
        }
    }

    result = collect_binary_package_inspection(ctx)

    assert result["status"] == "ok"
    assert result["setuid_setgid_binaries"] == ["pkg/usr/bin/helper"]
    assert result["maintainer_scripts"] == ["pkg/DEBIAN/postinst"]


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


def test_lp_mir_history_direct_fetches_explicit_lp_ref_from_bug_text():
    """An explicit 'LP: #NNNN' in the bug text is fetched and title-confirmed."""
    ctx = Mock()
    ctx.source_package = "mysql-9.7"
    ctx.reporter_mir_content = ""
    ctx.bug = {
        "title": "[MIR] mysql-9.7",
        "description": (
            "This MIR will allow mysql-9.7 to replace mysql-8.4 as the provider "
            "of libmysqlclient24.\n\nMIR for mysql-8.4 - LP: #2089720"
        ),
        "comments": [],
    }
    ctx.evidence = {"adapters": {}}

    def fake_fetch(url: str):
        # searchTasks for the current source and the extracted predecessor name
        # return nothing — the prior bug is only reachable via the explicit ref.
        if "searchTasks" in url:
            return {"entries": []}
        # Direct bug fetch for the explicit LP: #2089720 reference.
        if url == "https://api.launchpad.net/devel/bugs/2089720":
            return {"title": "[MIR] mysql-8.4"}
        raise AssertionError(f"unexpected url: {url}")

    with patch("evidence.host_adapters._fetch_json", side_effect=fake_fetch):
        from evidence.host_adapters import collect_lp_mir_history

        result = collect_lp_mir_history(ctx)

    assert result["status"] == "ok"
    prior = result["prior_mir_bugs"]
    assert len(prior) == 1
    assert prior[0]["id"] == "2089720"
    assert prior[0]["matched_name"] == "mysql-8.4"
    assert prior[0]["title"] == "[MIR] mysql-8.4"
    assert prior[0]["web_link"] == "https://bugs.launchpad.net/bugs/2089720"
    assert prior[0]["provenance"] == "bug-text-ref"
    # The predecessor name extracted from the bug text is also a candidate.
    assert "mysql-8.4" in result["candidate_names"]


def test_lp_mir_history_direct_fetch_404_is_skipped():
    """A 404 on the direct fetch of an explicit LP ref is skipped, not fatal."""
    ctx = Mock()
    ctx.source_package = "mysql-9.7"
    ctx.reporter_mir_content = ""
    ctx.bug = {
        "title": "[MIR] mysql-9.7",
        "description": "Prior review: LP: #9999999",
        "comments": [],
    }
    ctx.evidence = {"adapters": {}}

    def fake_fetch(url: str):
        if "searchTasks" in url:
            return {"entries": []}
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)

    with patch("evidence.host_adapters._fetch_json", side_effect=fake_fetch):
        from evidence.host_adapters import collect_lp_mir_history

        result = collect_lp_mir_history(ctx)

    assert result["status"] == "ok"
    assert result["prior_mir_bugs"] == []


def test_lp_mir_history_bare_name_ref_probed_via_searchtasks():
    """A bare predecessor name (no LP ref) is added to the candidate pool."""
    ctx = Mock()
    ctx.source_package = "libfoo2"
    ctx.reporter_mir_content = ""
    ctx.bug = {
        "title": "[MIR] libfoo2",
        "description": "libfoo2 to replace libfoo as the provider.",
        "comments": [],
    }
    ctx.evidence = {"adapters": {}}

    task_page = {
        "entries": [
            {
                "bug_link": "https://api.launchpad.net/devel/bugs/800",
                "web_link": "https://bugs.launchpad.net/bugs/800",
                "status": "Fix Released",
            },
        ],
    }
    bug_800 = {"title": "[MIR] libfoo"}

    def fake_fetch(url: str):
        if "+source/libfoo2" in url and "searchTasks" in url:
            return {"entries": []}
        if "+source/libfoo" in url and "searchTasks" in url:
            return task_page
        if url.endswith("/bugs/800"):
            return bug_800
        raise AssertionError(f"unexpected url: {url}")

    with patch("evidence.host_adapters._fetch_json", side_effect=fake_fetch):
        from evidence.host_adapters import collect_lp_mir_history

        result = collect_lp_mir_history(ctx)

    assert result["status"] == "ok"
    assert "libfoo" in result["candidate_names"]
    prior = result["prior_mir_bugs"]
    assert len(prior) == 1
    assert prior[0]["id"] == "800"
    assert prior[0]["matched_name"] == "libfoo"
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
    assert result["upstream_name"] == "testpkg"


def test_upstream_tracker_no_match_falls_back_to_control_homepage():
    """No release-monitoring.org match should still surface the package's own
    debian/control Homepage or debian/watch URL, not fail the adapter."""
    ctx = Mock()
    ctx.source_package = "rust-ntpd"
    ctx.evidence = {
        "adapters": {
            "packaging-source": {
                "status": "ok",
                "debian_watch": "",
                "debian_control": (
                    "Source: rust-ntpd\nHomepage: https://github.com/pendulum-project/ntpd-rs\n"
                ),
            }
        }
    }

    with patch("evidence.host_adapters._fetch_json", return_value={"items": []}):
        from evidence.host_adapters import collect_upstream_tracker

        result = collect_upstream_tracker(ctx)

    assert result["status"] == "ok"
    assert result["upstream_url"] == "https://github.com/pendulum-project/ntpd-rs"
    assert result["upstream_name"] == ""
    assert result["latest_version"] == ""


def test_upstream_tracker_no_match_and_no_hints_is_still_ok():
    """A genuinely undetectable upstream project is a normal empty result, not an error."""
    ctx = Mock()
    ctx.source_package = "obscure-pkg"
    ctx.evidence = {"adapters": {}}

    with patch("evidence.host_adapters._fetch_json", return_value={"items": []}):
        from evidence.host_adapters import collect_upstream_tracker

        result = collect_upstream_tracker(ctx)

    assert result["status"] == "ok"
    assert result["upstream_url"] == ""
    assert result["upstream_name"] == ""


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


def test_dep_analysis_runtime_deps_in_main_scoped_to_requested_binaries():
    """runtime_deps_in_main lists only in-scope binaries' deps already in main.

    testpkg-dev is not requested, so its dependency (libfoo, universe) must not
    leak into runtime_deps_in_main, and libssl3 (universe, from the in-scope
    binary) must also be excluded — only libc6 (main) qualifies.
    """
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.requested_binaries = ["testpkg"]
    ctx.evidence = {
        "adapters": {
            "packaging-source": {"status": "ok", "source_dir": "/tmp/test"},
            "sbuild": {
                "status": "ok",
                "build_success": True,
                "built_debs": [
                    "/tmp/out/testpkg_1.0_amd64.deb",
                    "/tmp/out/testpkg-dev_1.0_amd64.deb",
                ],
            },
        }
    }

    with patch("evidence.guest_adapters._capture") as mock_capture:
        with patch("evidence.guest_adapters._detect_component") as mock_component:
            mock_capture.side_effect = [
                "testpkg\ntestpkg-dev",  # binaries from debian/control
                "testpkg",  # deb1 Package
                "libc6, libssl3",  # deb1 Depends (in-scope)
                "testpkg-dev",  # deb2 Package
                "libfoo",  # deb2 Depends (out of scope)
                "",  # apt-cache show libc6 -> source = libc6
                "",  # apt-cache show libssl3 -> source = libssl3
                "",  # apt-cache show libfoo -> source = libfoo
            ]
            mock_component.side_effect = lambda _ctx, pkg: {
                "libc6": "main",
                "libssl3": "universe",
                "libfoo": "main",
            }[pkg]

            from evidence.guest_adapters import collect_dep_analysis

            result = collect_dep_analysis(ctx)

    assert result["runtime_deps_in_main"] == ["libc6"]


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


def test_reverse_deps_parses_consumers_and_maps_sources():
    """reverse-deps should parse bullet output and map binaries to sources."""
    ctx = Mock()
    ctx.source_package = "libebur128"
    ctx.series = "plucky"

    def fake_capture(_ctx, cmd, allow_fail=False, **kwargs):
        script = cmd[-1]
        if "--build-depends" in script:
            return ""  # no build reverse-deps
        if "reverse-depends --release plucky-proposed" in script:
            return "Reverse-Depends\n===============\n* pipewire\n* gst-plugins-bad  [amd64]\n"
        if script.startswith("apt-cache show pipewire"):
            return "pipewire"
        if script.startswith("apt-cache show gst-plugins-bad"):
            return "gst-plugins-bad1.0"
        return ""

    from evidence import guest_adapters

    with patch.object(guest_adapters, "_exists", return_value=True):
        with patch.object(guest_adapters, "_capture", side_effect=fake_capture):
            result = guest_adapters.collect_reverse_deps(ctx)

    assert result["status"] == "ok"
    assert result["release"] == "plucky-proposed"
    assert result["consumer_sources"] == ["gst-plugins-bad1.0", "pipewire"]
    assert {"source": "pipewire", "kind": "runtime"} in result["consumers"]
    assert {"source": "gst-plugins-bad1.0", "kind": "runtime"} in result["consumers"]


def test_reverse_deps_excludes_own_source():
    """A reverse-dep binary from the same source is not a consumer."""
    ctx = Mock()
    ctx.source_package = "libebur128"
    ctx.series = "plucky"

    def fake_capture(_ctx, cmd, allow_fail=False, **kwargs):
        script = cmd[-1]
        if "--build-depends" in script:
            return ""
        if "reverse-depends --release plucky-proposed" in script:
            return "* libebur128-1\n* pipewire\n"
        if script.startswith("apt-cache show libebur128-1"):
            return "libebur128"
        if script.startswith("apt-cache show pipewire"):
            return "pipewire"
        return ""

    from evidence import guest_adapters

    with patch.object(guest_adapters, "_exists", return_value=True):
        with patch.object(guest_adapters, "_capture", side_effect=fake_capture):
            result = guest_adapters.collect_reverse_deps(ctx)

    assert result["consumer_sources"] == ["pipewire"]


def test_reverse_deps_missing_tool_raises():
    """Absence of reverse-depends surfaces as an AdapterError (best-effort fallback)."""
    ctx = Mock()
    ctx.source_package = "libebur128"
    ctx.series = "plucky"

    from evidence import guest_adapters

    with patch.object(guest_adapters, "_exists", return_value=False):
        try:
            guest_adapters.collect_reverse_deps(ctx)
            assert False, "expected AdapterError when reverse-depends is absent"
        except guest_adapters.AdapterError:
            pass


def test_consumer_autopkgtests_looks_up_each_consumer():
    """consumer-autopkgtests should query the shared DB per consumer source."""
    import evidence.host_adapters as ha

    ctx = Mock()
    ctx.series = "plucky"
    ctx.evidence = {
        "adapters": {
            "reverse-deps": {
                "status": "ok",
                "consumers": [
                    {"source": "pipewire", "kind": "runtime"},
                    {"source": "quietapp", "kind": "build"},
                ],
            }
        }
    }

    def fake_query(_db, package, _candidates):
        if package == "pipewire":
            return [("amd64", 0, "1.0", 5), ("arm64", 0, "1.0", 4)], "plucky"
        return [], "plucky"

    with patch.object(ha, "_get_cached_autopkgtest_db", return_value="/tmp/fake.db"):
        with patch.object(ha, "_query_autopkgtest_for_package", side_effect=fake_query):
            result = ha.collect_consumer_autopkgtests(ctx)

    assert result["status"] == "ok"
    by_source = {c["source"]: c for c in result["consumers"]}
    assert by_source["pipewire"]["has_autopkgtest"] is True
    assert by_source["pipewire"]["passing_arches"] == ["amd64", "arm64"]
    assert by_source["quietapp"]["has_autopkgtest"] is False


def test_consumer_autopkgtests_no_consumers_returns_empty():
    """With no reverse-dep consumers, the adapter returns an empty, ok result."""
    import evidence.host_adapters as ha

    ctx = Mock()
    ctx.series = "plucky"
    ctx.evidence = {"adapters": {"reverse-deps": {"status": "ok", "consumers": []}}}

    result = ha.collect_consumer_autopkgtests(ctx)

    assert result["status"] == "ok"
    assert result["consumers"] == []


def test_dependency_autopkgtests_looks_up_each_in_main_dependency():
    """dependency-autopkgtests should query the shared DB per in-main dependency source."""
    import evidence.host_adapters as ha

    ctx = Mock()
    ctx.series = "plucky"
    ctx.evidence = {
        "adapters": {
            "dep-analysis": {
                "status": "ok",
                "runtime_deps_in_main": ["libc6", "libssl3"],
                "dep_source_map": [
                    {"package": "libc6", "source_package": "glibc"},
                    {"package": "libssl3", "source_package": "openssl"},
                ],
            }
        }
    }

    def fake_query(_db, source, _candidates):
        if source == "glibc":
            return [("amd64", 0, "1.0", 5), ("arm64", 0, "1.0", 4)], "plucky"
        return [], "plucky"

    with patch.object(ha, "_get_cached_autopkgtest_db", return_value="/tmp/fake.db"):
        with patch.object(ha, "_query_autopkgtest_for_package", side_effect=fake_query):
            result = ha.collect_dependency_autopkgtests(ctx)

    assert result["status"] == "ok"
    by_package = {c["package"]: c for c in result["dependency_coverage"]}
    assert by_package["libc6"]["source"] == "glibc"
    assert by_package["libc6"]["has_autopkgtest"] is True
    assert by_package["libc6"]["passing_arches"] == ["amd64", "arm64"]
    assert by_package["libssl3"]["source"] == "openssl"
    assert by_package["libssl3"]["has_autopkgtest"] is False


def test_dependency_autopkgtests_no_in_main_deps_returns_empty():
    """With no in-main runtime dependencies, the adapter returns an empty, ok result."""
    import evidence.host_adapters as ha

    ctx = Mock()
    ctx.series = "plucky"
    ctx.evidence = {"adapters": {"dep-analysis": {"status": "ok", "runtime_deps_in_main": []}}}

    result = ha.collect_dependency_autopkgtests(ctx)

    assert result["status"] == "ok"
    assert result["dependency_coverage"] == []


def test_autopkgtest_db_downloaded_once_and_cleaned_up():
    """The large autopkgtest DB is downloaded once per run and removed afterwards."""
    import evidence.host_adapters as ha

    class _Ctx:
        pass

    ctx = _Ctx()
    ctx._autopkgtest_db_path = None

    downloads: list[str] = []

    def fake_download(_url, tmp_path):
        downloads.append(tmp_path)
        Path(tmp_path).write_bytes(b"db")

    with patch.object(ha, "_download_autopkgtest_db", side_effect=fake_download):
        first = ha._get_cached_autopkgtest_db(ctx)
        second = ha._get_cached_autopkgtest_db(ctx)

    assert first == second
    assert len(downloads) == 1
    assert Path(first).exists()

    ha.cleanup_cached_autopkgtest_db(ctx)

    assert not Path(first).exists()
    assert ctx._autopkgtest_db_path is None


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


def test_autopkgtest_archive_pool_prefix_matches_debian_pool_convention():
    import evidence.host_adapters as ha

    assert ha._autopkgtest_archive_pool_prefix("python-invoke") == "p"
    assert ha._autopkgtest_archive_pool_prefix("libgit2") == "libg"
    assert ha._autopkgtest_archive_pool_prefix("libvirt") == "libv"


def test_fetch_autopkgtest_log_excerpt_returns_summary_on_success():
    import gzip

    import evidence.host_adapters as ha

    log_text = "\n".join([f"line {i}" for i in range(5)] + ["error: something failed"])
    compressed = gzip.compress(log_text.encode("utf-8"))

    with patch.object(ha.http_utils, "get_bytes", return_value=compressed) as mock_get:
        result = ha.fetch_autopkgtest_log_excerpt(
            "python-invoke", "stonking", "amd64", "20260723_004254_70601@"
        )

    assert result is not None
    assert result["line_count"] == 6
    assert any("error" in entry["text"] for entry in result["highlighted_lines"])
    requested_url = mock_get.call_args.args[0]
    assert requested_url == (
        "https://autopkgtest.ubuntu.com/results/autopkgtest-stonking/stonking/"
        "amd64/p/python-invoke/20260723_004254_70601@/log.gz"
    )


def test_fetch_autopkgtest_log_excerpt_returns_none_on_fetch_failure():
    import evidence.host_adapters as ha

    with patch.object(ha.http_utils, "get_bytes", side_effect=OSError("network unreachable")):
        result = ha.fetch_autopkgtest_log_excerpt(
            "python-invoke", "stonking", "amd64", "20260723_004254_70601@"
        )

    assert result is None


def test_fetch_autopkgtest_log_excerpt_returns_none_on_bad_gzip():
    import evidence.host_adapters as ha

    with patch.object(ha.http_utils, "get_bytes", return_value=b"not actually gzip"):
        result = ha.fetch_autopkgtest_log_excerpt(
            "python-invoke", "stonking", "amd64", "20260723_004254_70601@"
        )

    assert result is None


def test_fetch_autopkgtest_log_excerpt_returns_none_for_missing_arguments():
    import evidence.host_adapters as ha

    assert ha.fetch_autopkgtest_log_excerpt("", "stonking", "amd64", "run1") is None
    assert ha.fetch_autopkgtest_log_excerpt("pkg", "", "amd64", "run1") is None
    assert ha.fetch_autopkgtest_log_excerpt("pkg", "stonking", "", "run1") is None
    assert ha.fetch_autopkgtest_log_excerpt("pkg", "stonking", "amd64", "") is None


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


def test_is_library_package_true_for_library_sections():
    from evidence.guest_adapters import _is_library_package

    assert _is_library_package(["libs", "libdevel"]) is True
    assert _is_library_package(["oldlibs"]) is True


def test_is_library_package_false_for_non_library_sections():
    from evidence.guest_adapters import _is_library_package

    assert _is_library_package(["utils", "net"]) is False
    assert _is_library_package([]) is False


def test_parse_source_control_fields_handles_continuations():
    from evidence.guest_adapters import _parse_source_control_fields

    control = """Source: libfoo
Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
Homepage: https://example.test/libfoo
Description: useful library
 with additional context

Package: libfoo1
Architecture: any
"""

    fields = _parse_source_control_fields(control)

    assert fields["maintainer"].startswith("Ubuntu Developers")
    assert fields["homepage"] == "https://example.test/libfoo"
    assert fields["description"] == "useful library with additional context"


def test_parse_debconf_templates_extracts_declared_metadata():
    from evidence.guest_adapters import _parse_debconf_templates

    content = """Template: libfoo/enable
Type: boolean
Priority: high
Description: Enable foo?
 This is a continuation.

Template: libfoo/name
Type: string
Description: Name
"""

    assert _parse_debconf_templates(content) == [
        {"template": "libfoo/enable", "type": "boolean", "priority": "high"},
        {"template": "libfoo/name", "type": "string", "priority": ""},
    ]


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

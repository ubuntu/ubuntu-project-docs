"""Unit tests for check evaluators in checks.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import checks.deterministic
import checks.language_gates
import checks.llm_eval
from models import Finding

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_finding(check_id="TST-1", title="Test check", mode="deterministic"):
    return Finding(
        id=check_id,
        section="Test",
        title=title,
        mode=mode,
    )


class _Ctx:
    """Minimal RunContext stub for check evaluator tests."""

    def __init__(self, *, source_package="testpkg", reporter_content="content"):
        self.source_package = source_package
        self.reporter_mir_content = reporter_content
        self.requested_binaries = []
        self.bug = {"subscribers": []}
        self.catalog = {
            "checks": [
                {
                    "id": "SUM-1",
                    "messages": {
                        "ok_message": "Review for Source Package: {source_package}",
                        "not_ok_message": "Source package could not be determined",
                        "not_ok_todo": "TODO: Clarify which source package this review is for",
                    },
                },
                {
                    "id": "SUM-2",
                    "messages": {
                        "ok_message": "Reporter MIR content found and used as context.",
                        "nack_message": "Reporter MIR template content not found (hard stop)",
                        "nack_todo": "TODO: - Reporter must post their completed MIR template",
                    },
                },
                {
                    "id": "SUM-4",
                    "messages": {
                        "unknown_message": "Could not check team subscription (team-mapping adapter failed)",
                        "unknown_todo": "TODO: - Manually verify package has a team subscriber",
                        "ok_message": "Package has team subscriber(s): {subscribed_teams}",
                        "not_ok_message": "Package does not have a team subscriber",
                        "not_ok_todo": "TODO: - The package should get a team bug subscriber on this bug before being promoted",
                    },
                },
                {
                    "id": "DEP-1",
                    "messages": {
                        "unknown_adapter_message": "Could not analyse runtime dependencies",
                        "unknown_adapter_todo": "TODO: - Verify no runtime dependencies in universe need MIR",
                        "not_ok_message": "Runtime dependencies from other source packages outside main: {deps}",
                        "not_ok_todo": "TODO: - File MIR for runtime dependencies from other source packages: {deps}",
                        "unknown_component_message": "Could not determine component for some runtime dependencies: {deps}",
                        "unknown_component_todo": "TODO: - Verify Ubuntu component for runtime dependencies: {deps}",
                        "ok_same_source_message": "no external runtime dependencies needing MIR (same-source deps promoted together: {same_source})",
                        "ok_message": "no runtime dependencies outside main needing MIR",
                    },
                },
                {
                    "id": "ESL-1",
                    "messages": {
                        "unknown_message": "Could not collect packaging source",
                        "unknown_todo": "TODO: - Check for embedded source (packaging-source collection failed)",
                        "not_ok_message": "Vendored directories found: {vendored_dirs}",
                        "not_ok_todo": "TODO: - Embedded source found — either remove and use archive packages, or get security team sign-off. Vendored dirs: {vendored_dirs}",
                        "ok_built_using_message": "no embedded source present (Built-Using present; see ESL-3 for review)",
                        "ok_message": "no embedded source present",
                    },
                },
                {
                    "id": "ESL-3",
                    "messages": {
                        "unknown_message": "Could not collect debian/control",
                        "unknown_todo": "TODO: - Check for unexpected Built-Using entries",
                        "ok_message": "does not have unexpected Built-Using entries",
                        "ok_toolchain_message": "Built-Using entries present but appear to be standard toolchain entries: {entries}",
                        "not_ok_message": "Unexpected Built-Using entries that may indicate untracked embedded source: {entries}",
                        "not_ok_todo": "TODO: - Review Built-Using entries — possible untracked embedded source: {entries}",
                    },
                },
                {
                    "id": "SEC-3",
                    "messages": {
                        "ok_message": "does not use webkit1,2",
                        "unknown_message": "Could not analyse webkit dependencies",
                        "blocker_message": "webkit1/2 dependency found — hard blocker",
                        "blocker_todo": "TODO: - webkit1/2 dependency must be removed before main inclusion",
                    },
                },
                {
                    "id": "SEC-4",
                    "messages": {
                        "ok_message": "does not use lib*v8 directly",
                        "unknown_message": "Could not analyse v8 dependencies",
                        "blocker_message": "lib*v8 dependency found — hard blocker",
                        "blocker_todo": "TODO: - direct lib*v8 dependency must be removed before main inclusion",
                    },
                },
                {
                    "id": "CB-7",
                    "messages": {
                        "ok_message": "no new python2 dependency",
                        "unknown_message": "Could not analyse Python2 dependencies",
                        "blocker_message": "Python2 dependency found — hard blocker",
                        "blocker_todo": "TODO: - python2 dependency must be removed or ported before main inclusion",
                    },
                },
                {
                    "id": "DEP-3",
                    "messages": {
                        "unknown_packaging_message": "Could not analyse binary packages",
                        "unknown_packaging_todo": "TODO: - Check whether -dev/-debug/-doc packages need exclusion",
                        "unknown_dep_analysis_message": "Could not analyse auto-included binary dependencies",
                        "unknown_dep_analysis_todo": "TODO: - Check whether auto-included -dev/-debug/-doc packages need exclusion",
                        "ok_no_auto_included_message": "no -dev/-debug/-doc packages that need exclusion",
                        "not_ok_offending_message": "Auto-included binaries ({auto_included}) pull dependencies outside main or with unknown component: {offending_deps}",
                        "not_ok_offending_todo": "TODO: - Consider adding extra-excludes for auto-included binaries with offending dependencies ({details}); otherwise MIR may also be needed for: {offending_deps}",
                        "ok_safe_message": "Auto-included binaries ({auto_included}) will be auto-included, and have no dependencies outside main",
                    },
                }
            ]
        }
        self.evidence = {"adapters": {}}


def _dep_analysis_ok(**kwargs):
    base = {
        "status": "ok",
        "runtime_deps": [],
        "deps_not_in_main": [],
        "dep_components": [],
        "runtime_dep_packages": [],
        "binary_packages": [],
        "dev_debug_doc_packages": [],
        "dep_source_map": [],
        "in_scope_deps_not_in_main": [],
        "out_of_scope_deps_not_in_main": [],
        "same_source_deps": [],
        "auto_included_binaries": [],
        "auto_included_dep_components": [],
        "auto_included_deps_not_in_main_or_unknown": [],
        "auto_included_offending_deps_by_binary": [],
    }
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# SUM-4: team subscriber in package-team-mapping
# ---------------------------------------------------------------------------


def test_sum_1_ok():
    ctx = _Ctx(source_package="libfoo")
    finding = checks.deterministic._check_sum_1(ctx, _make_finding("SUM-1"))
    assert finding.status == "ok"
    assert finding.confidence == "high"
    assert "libfoo" in finding.message


def test_sum_1_missing_package():
    ctx = _Ctx(source_package="")
    finding = checks.deterministic._check_sum_1(ctx, _make_finding("SUM-1"))
    assert finding.status == "not-ok"
    assert finding.severity == "required"


# ---------------------------------------------------------------------------
# SUM-2: Reporter MIR content present
# ---------------------------------------------------------------------------


def test_sum_2_ok():
    ctx = _Ctx(reporter_content="has content")
    finding = checks.deterministic._check_sum_2(ctx, _make_finding("SUM-2"))
    assert finding.status == "ok"


def test_sum_2_missing():
    ctx = _Ctx(reporter_content="")
    finding = checks.deterministic._check_sum_2(ctx, _make_finding("SUM-2"))
    assert finding.status == "not-ok"
    assert finding.severity == "nack"


# ---------------------------------------------------------------------------
# DEP-1: No unresolved runtime dependencies
# ---------------------------------------------------------------------------


def test_dep_1_all_in_main():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        dep_components=[{"package": "libz", "component": "main"}],
    )
    finding = checks.deterministic._check_dep_1(ctx, _make_finding("DEP-1"))
    assert finding.status == "ok"
    assert finding.confidence == "high"


def test_dep_1_in_scope_deps_outside_main():
    """In-scope dependencies from other source packages should block MIR."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        in_scope_deps_not_in_main=["libfancyuniverse"],
        dep_components=[{"package": "libfancyuniverse", "component": "universe"}],
    )
    finding = checks.deterministic._check_dep_1(ctx, _make_finding("DEP-1"))
    assert finding.status == "not-ok"
    assert finding.severity == "required"
    assert "libfancyuniverse" in finding.message


def test_dep_1_same_source_deps_ok():
    """Same-source dependencies should not block MIR."""
    ctx = _Ctx(source_package="dav1d")
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        same_source_deps=["libdav1d7"],
        dep_components=[{"package": "libdav1d7", "component": "universe"}],
    )
    finding = checks.deterministic._check_dep_1(ctx, _make_finding("DEP-1"))
    assert finding.status == "ok"
    assert finding.confidence == "high"


def test_dep_1_out_of_scope_deps_ok():
    """Out-of-scope dependencies should not block MIR."""
    ctx = _Ctx()
    ctx.requested_binaries = ["foo"]
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        out_of_scope_deps_not_in_main=["libbar-universe"],
        dep_components=[{"package": "libbar-universe", "component": "universe"}],
    )
    finding = checks.deterministic._check_dep_1(ctx, _make_finding("DEP-1"))
    assert finding.status == "ok"
    assert finding.confidence == "high"


def test_dep_1_adapter_missing():
    ctx = _Ctx()
    # No dep-analysis adapter at all
    finding = checks.deterministic._check_dep_1(ctx, _make_finding("DEP-1"))
    assert finding.status == "unknown"
    assert finding.confidence == "low"


# ---------------------------------------------------------------------------
# DEP-3: No -dev/-debug/-doc packages needing exclusion
# ---------------------------------------------------------------------------


def test_dep_3_no_auto_included_binaries():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {"status": "ok"}
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        binary_packages=["mypkg", "libmypkg1"],
        auto_included_binaries=[],
    )

    finding = checks.deterministic._check_dep_3(ctx, _make_finding("DEP-3"))

    assert finding.status == "ok"
    assert finding.confidence == "high"
    assert "no -dev/-debug/-doc packages" in finding.message


def test_dep_3_auto_included_binaries_safe():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {"status": "ok"}
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        binary_packages=["mypkg", "libmypkg-dev"],
        auto_included_binaries=["libmypkg-dev"],
        auto_included_deps_not_in_main_or_unknown=[],
    )

    finding = checks.deterministic._check_dep_3(ctx, _make_finding("DEP-3"))

    assert finding.status == "ok"
    assert finding.confidence == "high"
    assert "will be auto-included" in finding.message


def test_dep_3_auto_included_binaries_with_offending_deps():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {"status": "ok"}
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        binary_packages=["mypkg", "libmypkg-dev"],
        auto_included_binaries=["libmypkg-dev"],
        auto_included_deps_not_in_main_or_unknown=["libuniverse1", "libunknown1"],
        auto_included_offending_deps_by_binary=[
            {"binary": "libmypkg-dev", "dependencies": ["libunknown1", "libuniverse1"]}
        ],
    )

    finding = checks.deterministic._check_dep_3(ctx, _make_finding("DEP-3"))

    assert finding.status == "not-ok"
    assert finding.severity == "recommended"
    assert finding.confidence == "high"
    assert "libuniverse1" in finding.message
    assert "libunknown1" in finding.todo
    assert "libmypkg-dev" in finding.todo


def test_dep_3_ignores_global_non_main_for_non_auto_included_binaries():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {"status": "ok"}
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        binary_packages=["mypkg", "libmypkg-dev"],
        deps_not_in_main=["libuniverse-from-mainpkg"],
        auto_included_binaries=["libmypkg-dev"],
        auto_included_deps_not_in_main_or_unknown=[],
    )

    finding = checks.deterministic._check_dep_3(ctx, _make_finding("DEP-3"))

    assert finding.status == "ok"
    assert "have no dependencies outside main" in finding.message


# ---------------------------------------------------------------------------
# SEC-3: Does not use webkit
# ---------------------------------------------------------------------------


def test_sec_3_clean():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        runtime_deps=[{"binary": "libfoo", "depends": "libc6"}],
    )
    finding = checks.deterministic._check_sec_3(ctx, _make_finding("SEC-3"))
    assert finding.status == "ok"


def test_sec_3_webkit_found():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        runtime_deps=[{"binary": "myapp", "depends": "libwebkit2gtk-4.0"}],
    )
    finding = checks.deterministic._check_sec_3(ctx, _make_finding("SEC-3"))
    assert finding.status == "not-ok"
    assert finding.severity == "required"
    assert finding.confidence == "high"


# ---------------------------------------------------------------------------
# SEC-4: Does not use lib*v8
# ---------------------------------------------------------------------------


def test_sec_4_clean():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        runtime_deps=[{"binary": "myapp", "depends": "libssl3"}],
    )
    finding = checks.deterministic._check_sec_4(ctx, _make_finding("SEC-4"))
    assert finding.status == "ok"


def test_sec_4_libv8_found():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        runtime_deps=[{"binary": "myapp", "depends": "libv8-dev"}],
    )
    finding = checks.deterministic._check_sec_4(ctx, _make_finding("SEC-4"))
    assert finding.status == "not-ok"
    assert finding.severity == "required"


# ---------------------------------------------------------------------------
# CB-7: No Python2 dependency
# ---------------------------------------------------------------------------


def test_cb_7_clean():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        runtime_deps=[{"binary": "myapp", "depends": "python3"}],
    )
    finding = checks.deterministic._check_cb_7(ctx, _make_finding("CB-7"))
    assert finding.status == "ok"


def test_cb_7_python2_found():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        runtime_deps=[{"binary": "myapp", "depends": "python2.7"}],
    )
    finding = checks.deterministic._check_cb_7(ctx, _make_finding("CB-7"))
    assert finding.status == "not-ok"
    assert finding.severity == "required"


# ---------------------------------------------------------------------------
# SUM-4: team subscriber in package-team-mapping
# ---------------------------------------------------------------------------


def test_sum_4_subscribed():
    ctx = _Ctx(source_package="bash")
    ctx.evidence["adapters"]["team-mapping"] = {
        "status": "ok",
        "team_mapping": {
            "ubuntu-foundations": ["bash", "coreutils"],
            "ubuntu-server": ["nginx", "apache2"],
        },
        "subscribed_teams": ["ubuntu-foundations"],
        "source_package": "bash",
    }
    finding = checks.deterministic._check_sum_4(ctx, _make_finding("SUM-4"))
    assert finding.status == "ok"
    assert "ubuntu-foundations" in finding.message


def test_sum_4_not_subscribed():
    ctx = _Ctx(source_package="some-package")
    ctx.evidence["adapters"]["team-mapping"] = {
        "status": "ok",
        "team_mapping": {},
        "subscribed_teams": [],
        "source_package": "some-package",
    }
    finding = checks.deterministic._check_sum_4(ctx, _make_finding("SUM-4"))
    assert finding.status == "not-ok"
    assert finding.severity == "recommended"


def test_sum_4_adapter_failed():
    ctx = _Ctx(source_package="bash")
    ctx.evidence["adapters"]["team-mapping"] = {
        "status": "error",
        "error": "Launchpad API error",
    }
    finding = checks.deterministic._check_sum_4(ctx, _make_finding("SUM-4"))
    assert finding.status == "unknown"
    assert finding.confidence == "low"


# ---------------------------------------------------------------------------
# Language gate helpers
# ---------------------------------------------------------------------------


def test_language_gate_go_inactive():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "go_sum_present": False,
    }
    assert checks.language_gates._language_gate_active("go", ctx) is False


def test_language_gate_go_active_via_flag():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@ --with golang",
        "go_sum_present": False,
    }
    assert checks.language_gates._language_gate_active("go", ctx) is True


def test_language_gate_go_active_via_go_sum():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "go_sum_present": True,
    }
    assert checks.language_gates._language_gate_active("go", ctx) is True


def test_language_gate_rust_inactive():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "cargo_lock_present": False,
    }
    assert checks.language_gates._language_gate_active("rust", ctx) is False


def test_language_gate_unknown_defaults_active():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
    }
    # Unknown gate type should conservatively return True
    assert checks.language_gates._language_gate_active("cobol", ctx) is True


def test_language_gate_adapter_missing_defaults_active():
    ctx = _Ctx()
    # No packaging-source adapter — conservative fallback
    assert checks.language_gates._language_gate_active("go", ctx) is True

"""Unit tests for check evaluators in checks.py."""

import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import checks.deterministic
import checks.language_gates
import checks.llm_eval
import llm
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
        self.bug_id = "123456"
        self.series = "devel"
        self.source_package = source_package
        self.reporter_mir_content = reporter_content
        self.requested_binaries = []
        self.bug = {"subscribers": []}
        self.findings = []
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
                        "unknown_message": "Could not collect packaging source and sbuild output",
                        "unknown_todo": "TODO: - Check for embedded source (evidence collection failed)",
                        "not_ok_message": "Embedded source present and used in build: {embedded_dirs}",
                        "not_ok_todo": "TODO: - Embedded source found and used in build — either remove and use archive packages, or get security team sign-off. Dirs: {embedded_dirs}",
                        "ok_message": "no embedded source present or not used in build",
                    },
                },
                {
                    "id": "ESL-3",
                    "messages": {
                        "unknown_message": "Could not collect binary package metadata (deb-metadata collection failed)",
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
                },
                {
                    "id": "ESL-4",
                    "messages": {
                        "unknown_message": "Could not determine language (packaging-source failed)",
                        "unknown_todo": "TODO: - Determine if this is a Go package",
                        "ok_go_message": "Go Package — Debian Go packaging guidelines apply (see ESL-5/6/7)",
                        "ok_not_go_message": "not a go package, no extra constraints to consider in that regard",
                    },
                },
                {
                    "id": "ESL-7",
                    "messages": {
                        "unknown_message": "Could not determine Go build type (packaging-source failed)",
                        "unknown_todo": "TODO: - Determine Go build type (shared vs static)",
                        "ok_not_go_message": "not a go package, no extra constraints to consider in that regard",
                        "ok_shared_message": "golang: shared builds",
                        "recommended_message": "Go package uses dh-golang; build mode not confirmed as shared",
                        "recommended_todo": "TODO: - Confirm Go build mode — if static, team must confirm commitment to additional maintenance responsibilities implied by static builds",
                        "unknown_build_mode_message": "Go package but build mode could not be determined from debian/rules",
                        "unknown_build_mode_todo": "TODO: - Determine Go build type (shared vs static)",
                    },
                },
                {
                    "id": "ESL-8",
                    "messages": {
                        "unknown_message": "Could not determine language (packaging-source failed)",
                        "unknown_todo": "TODO: - Determine if this is a Rust package",
                        "ok_rust_message": "Rust Package — Rust-specific constraints apply (see ESL-9/10)",
                        "ok_not_rust_message": "not a rust package, no extra constraints to consider in that regard",
                    },
                },
                {
                    "id": "ESL-9",
                    "messages": {
                        "unknown_message": "Could not check debian/rules (packaging-source failed)",
                        "unknown_todo": "TODO: - Verify Rust package uses dh_cargo",
                        "ok_not_rust_message": "not a rust package, dh_cargo gate not applicable",
                        "ok_message": "rust package using dh_cargo (dh ... --buildsystem cargo)",
                        "not_ok_message": "Rust package detected but dh_cargo / --buildsystem cargo not found in debian/rules",
                        "not_ok_todo": "TODO: - Rust packages must use dh_cargo (dh ... --buildsystem cargo)",
                    },
                },
                {
                    "id": "ESL-10",
                    "messages": {
                        "unknown_message": "Could not collect packaging source",
                        "unknown_todo": "TODO: - Verify Rust vendored deps / Cargo.lock / Built-Using",
                        "ok_not_rust_message": "not a rust package, ESL-10 constraints not applicable",
                        "not_ok_message": "Rust package has issues: {problems}",
                        "not_ok_todo": "TODO: - Fix Rust package issues: {problems}",
                        "ok_message": "Rust package that has all dependencies vendored. It does neither have *Built-Using (after build). Nor does the build log indicate built-in sources missed as Built-Using.",
                    },
                },
                {
                    "id": "CB-1",
                },
                {
                    "id": "PRF-6",
                    "messages": {
                        "ok_message": "the current release is packaged",
                        "unknown_message": "Could not determine package version information",
                        "unknown_todo": "TODO: - Verify packaged version against latest upstream release",
                    },
                },
                {
                    "id": "PRF-8",
                },
                {
                    "id": "URF-1",
                    "messages": {
                        "ok_message": "no Errors/warnings during the build",
                        "unknown_todo": "TODO: - Check build log for errors and warnings",
                    },
                },
                {
                    "id": "PRF-10",
                    "messages": {
                        "ok_message": "It is not on the lto-disabled list",
                        "unknown_todo": "TODO: - Check if package is on lto-disabled list",
                    },
                },
                {
                    "id": "CB-8",
                    "messages": {
                        "ok_message": "Python package, but using dh_python",
                        "not_ok_message": "Python package not using dh_python",
                        "not_ok_todo": "TODO: - Python packages must use dh_python",
                        "unknown_todo": "TODO: - Check debian/rules for dh_python",
                    },
                },
                {
                    "id": "ESL-2",
                    "messages": {
                        "ok_message": "no static linking",
                        "unknown_todo": "TODO: - Check build log for static linking",
                    },
                },
                {
                    "id": "PRF-2",
                    "messages": {
                        "ok_message": "symbols tracking is in place",
                        "unknown_todo": "TODO: - Check for symbols file",
                    },
                },
                {
                    "id": "PRF-3",
                    "messages": {
                        "ok_message": "debian/watch is present and looks ok",
                        "unknown_todo": "TODO: - Check for debian/watch file",
                    },
                },
                {
                    "id": "SEC-2",
                    "messages": {
                        "ok_message": "does not run a daemon as root",
                        "unknown_todo": "TODO: - Check for daemon running as root",
                    },
                },
                {
                    "id": "URF-3",
                    "messages": {
                        "ok_message": "no use of sudo, gksu, pkexec, or LD_LIBRARY_PATH (usage is OK inside tests)",
                        "unknown_todo": "TODO: - Check for privilege escalation outside tests",
                    },
                },
                {
                    "id": "URF-4",
                    "messages": {
                        "ok_message": "no use of user 'nobody' outside of tests",
                        "unknown_todo": "TODO: - Check for 'nobody' user usage",
                    },
                },
                {
                    "id": "URF-5",
                    "messages": {
                        "ok_message": "no use of setuid / setgid",
                        "unknown_todo": "TODO: - Check for setuid/setgid binaries",
                    },
                },
                {
                    "id": "URF-7",
                    "messages": {
                        "ok_message": "no dependency on webkit, qtwebkit or libseed",
                        "unknown_todo": "TODO: - Check for old webkit dependencies",
                    },
                },
                {
                    "id": "SEC-8",
                    "messages": {
                        "ok_message": "does not use centralized online accounts",
                        "unknown_todo": "TODO: - Check for centralized accounts APIs",
                    },
                },
                {
                    "id": "SEC-10",
                    "messages": {
                        "ok_message": "does not deal with system authentication (eg, pam), etc)",
                        "unknown_todo": "TODO: - Check for PAM/system auth",
                    },
                },
                {
                    "id": "URF-8",
                    "messages": {
                        "ok_message": "UI/desktop file check",
                        "unknown_todo": "TODO: - Check for .desktop files",
                    },
                },
                {
                    "id": "URF-9",
                    "messages": {
                        "ok_message": "translation coverage check",
                        "unknown_todo": "TODO: - Check for translation coverage",
                    },
                },
                {
                    "id": "CB-7",
                    "messages": {
                        "ok_message": "no new python2 dependency",
                        "unknown_todo": "TODO: - Check for Python 2 dependencies",
                    },
                },
                {
                    "id": "SEC-3",
                    "messages": {
                        "ok_message": "does not use webkit1,2",
                        "unknown_todo": "TODO: - Check for webkit dependencies",
                    },
                },
                {
                    "id": "SEC-4",
                    "messages": {
                        "ok_message": "does not use lib*v8 directly",
                        "unknown_todo": "TODO: - Check for V8 dependencies",
                    },
                },
                {
                    "id": "ESL-4",
                    "messages": {
                        "ok_message": "Go language detection",
                        "unknown_todo": "TODO: - Detect Go packages",
                    },
                },
                {
                    "id": "ESL-8",
                    "messages": {
                        "ok_message": "Rust language detection",
                        "unknown_todo": "TODO: - Detect Rust packages",
                    },
                },
                {
                    "id": "DEP-1",
                    "messages": {
                        "ok_message": "no other runtime Dependencies to MIR due to this",
                        "unknown_todo": "TODO: - Verify no runtime dependencies need MIR",
                    },
                },
                {
                    "id": "ESL-9",
                    "messages": {
                        "ok_message": "rust package using dh_cargo",
                        "unknown_todo": "TODO: - Check for dh_cargo",
                    },
                },
                {
                    "id": "PRF-8",
                    "messages": {
                        "ok_message": "no excessive lintian warnings",
                        "unknown_todo": "TODO: - Check lintian output",
                    },
                },
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


def test_language_gate_go_active_via_source_tree_files():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "go_sum_present": False,
        "file_listing": [{"path": "./cmd/tool/main.go", "size": 321}],
    }
    assert checks.language_gates._language_gate_active("go", ctx) is True


def test_language_gate_go_ignores_vendor_tree_files():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "go_sum_present": False,
        "file_listing": [{"path": "./vendor/example/lib.go", "size": 321}],
    }
    assert checks.language_gates._language_gate_active("go", ctx) is False


def test_language_gate_rust_inactive():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "cargo_lock_present": False,
    }
    assert checks.language_gates._language_gate_active("rust", ctx) is False


def test_language_gate_rust_active_via_source_tree_files():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "cargo_lock_present": False,
        "file_listing": [{"path": "./src/main.rs", "size": 456}],
    }
    assert checks.language_gates._language_gate_active("rust", ctx) is True


def test_language_gate_rust_ignores_vendor_tree_files():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "cargo_lock_present": False,
        "file_listing": [{"path": "./third_party/rust/lib.rs", "size": 456}],
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


def test_language_gate_combined_go_rust_active_with_go():
    """Test combined gate 'go|rust' returns True when go package detected."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh-golang",
        "go_sum_present": False,
        "cargo_lock_present": False,
    }
    assert checks.language_gates._language_gate_active("go|rust", ctx) is True


def test_language_gate_combined_go_rust_active_with_rust():
    """Test combined gate 'go|rust' returns True when rust package detected."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "go_sum_present": False,
        "cargo_lock_present": True,
    }
    assert checks.language_gates._language_gate_active("go|rust", ctx) is True


def test_language_gate_combined_go_rust_inactive():
    """Test combined gate 'go|rust' returns False when neither go nor rust present."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "go_sum_present": False,
        "cargo_lock_present": False,
    }
    assert checks.language_gates._language_gate_active("go|rust", ctx) is False


def test_extract_build_hints_no_vendor_references():
    """Test _extract_build_hints returns empty results when no vendor paths present."""
    build_log = """
    gcc -Wall -O2 -c main.c
    gcc -o myapp main.o
    """
    hints = checks.llm_eval._extract_build_hints(build_log)
    assert hints["static_flags"] == []
    assert hints["vendor_compile_invocations"] == []
    assert hints["vendor_archive_ops"] == []


def test_extract_build_hints_static_linking():
    """Test _extract_build_hints detects static linking flags."""
    build_log = """
    gcc -static -Wall -c main.c
    gcc -Wl,--whole-archive -o myapp main.o
    """
    hints = checks.llm_eval._extract_build_hints(build_log)
    assert any("-static" in line for line in hints["static_flags"])
    assert any("--whole-archive" in line for line in hints["static_flags"])


def test_extract_build_hints_vendor_compile():
    """Test _extract_build_hints detects vendor paths in compiler invocations."""
    build_log = """
    gcc -I./vendor/zlib -c main.c
    clang -L./third_party/libs -lmylib main.o
    """
    hints = checks.llm_eval._extract_build_hints(build_log)
    assert any("vendor" in line and "gcc" in line for line in hints["vendor_compile_invocations"])
    assert any(
        "third_party" in line and "clang" in line for line in hints["vendor_compile_invocations"]
    )


def test_extract_build_hints_vendor_archive():
    """Test _extract_build_hints detects archive operations on vendor libraries."""
    build_log = """
    ar rcs ./vendor/libmylib.a obj1.o obj2.o
    ranlib ./third_party/libs/libfoo.a
    """
    hints = checks.llm_eval._extract_build_hints(build_log)
    assert any("ar" in line and "vendor" in line for line in hints["vendor_archive_ops"])
    assert any("ranlib" in line and "third_party" in line for line in hints["vendor_archive_ops"])


def test_parse_built_using_entries_empty():
    """Test _parse_built_using_entries with empty input."""
    import evidence.container_adapters as adapters

    assert adapters._parse_built_using_entries("") == []
    assert adapters._parse_built_using_entries(None) == []


def test_parse_built_using_entries_single_line():
    """Test _parse_built_using_entries with single-line field."""
    import evidence.container_adapters as adapters

    field = "golang-1.20 (>= 1.20~), golang-1.20 (<< 1.21~)"
    result = adapters._parse_built_using_entries(field)
    assert "golang-1.20 (>= 1.20~)" in result
    assert "golang-1.20 (<< 1.21~)" in result


def test_parse_built_using_entries_multi_line():
    """Test _parse_built_using_entries with multi-line field (continuation lines)."""
    import evidence.container_adapters as adapters

    field = """golang-1.20 (>= 1.20~),
 golang-1.20 (<< 1.21~)"""
    result = adapters._parse_built_using_entries(field)
    assert "golang-1.20 (>= 1.20~)" in result
    assert "golang-1.20 (<< 1.21~)" in result


def test_esl_3_no_built_using():
    """Test ESL-3 with no Built-Using entries."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["deb-metadata"] = {
        "status": "ok",
        "message": "OK",
        "deb_packages": [
            {"package": "mypkg", "version": "1.0", "built_using": [], "static_built_using": []},
        ],
    }
    finding = _make_finding("ESL-3", mode="deterministic")
    result = checks.deterministic._check_esl_3(ctx, finding)
    assert result.status == "ok"
    assert "Built-Using" not in result.message.lower() or "not" in result.message.lower()


def test_esl_3_toolchain_built_using():
    """Test ESL-3 with toolchain-only Built-Using entries."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["deb-metadata"] = {
        "status": "ok",
        "message": "OK",
        "deb_packages": [
            {
                "package": "mypkg",
                "version": "1.0",
                "built_using": ["golang-1.20 (>= 1.20~)"],
                "static_built_using": [],
            },
        ],
    }
    finding = _make_finding("ESL-3", mode="deterministic")
    result = checks.deterministic._check_esl_3(ctx, finding)
    assert result.status == "ok"
    assert "toolchain" in result.message.lower()


def test_select_ev_to_ai_model_tier_small_for_short_prompt_and_payload():
    tier = checks.llm_eval._select_ev_to_ai_model_tier(
        "short prompt",
        {"adapter": "small"},
    )
    assert tier == "small"


def test_select_ev_to_ai_model_tier_large_for_long_prompt():
    prompt = "x" * (checks.llm_eval._PROMPT_LARGE_THRESHOLD_CHARS + 1)
    tier = checks.llm_eval._select_ev_to_ai_model_tier(
        prompt,
        {"adapter": "small"},
    )
    assert tier == "large"


def test_eval_ai_graceful_on_large_tier_llm_error():
    ctx = _Ctx()
    check = {
        "id": "SUM-5",
        "title": "Summary verdict",
        "section": "Summary",
        "todo_refs": [],
    }
    finding = _make_finding("SUM-5", mode="ai")

    with mock.patch("llm.call_llm", side_effect=llm.LLMError("large model unavailable")):
        result = checks.llm_eval._eval_ai(check, ctx, finding)

    assert result.status == "unknown"
    assert result.confidence == "low"


def test_eval_ev_to_ai_graceful_on_small_tier_llm_error():
    ctx = _Ctx()
    check = {
        "id": "SEC-1",
        "title": "Security synthesis",
        "section": "Security",
        "todo_refs": ["TODO: - Manual security review"],
        "adapters_required": [],
        "adapters_optional": [],
    }
    finding = _make_finding("SEC-1", mode="ev_to_ai")

    with mock.patch("checks.llm_eval._select_ev_to_ai_model_tier", return_value="small"):
        with mock.patch("llm.call_llm", side_effect=llm.LLMError("small model transient issue")):
            result = checks.llm_eval._eval_ev_to_ai(check, ctx, finding)

    assert result.status == "unknown"
    assert result.confidence == "low"


def test_eval_ev_to_ai_graceful_on_large_tier_llm_error():
    ctx = _Ctx()
    check = {
        "id": "SEC-1",
        "title": "Security synthesis",
        "section": "Security",
        "todo_refs": ["TODO: - Manual security review"],
        "adapters_required": [],
        "adapters_optional": [],
    }
    finding = _make_finding("SEC-1", mode="ev_to_ai")

    with mock.patch("checks.llm_eval._select_ev_to_ai_model_tier", return_value="large"):
        with mock.patch("llm.call_llm", side_effect=llm.LLMError("large model unavailable")):
            result = checks.llm_eval._eval_ev_to_ai(check, ctx, finding)

    assert result.status == "unknown"
    assert result.confidence == "low"


def test_reduce_file_listing_strips_common_prefix_without_reducing_small_list():
    listing = [
        {"path": "./src/pkg/a.py", "size": 10},
        {"path": "./src/pkg/b.py", "size": 11},
    ]

    reduced = checks.llm_eval._reduce_file_listing(listing)

    assert isinstance(reduced, list)
    assert reduced[0]["path"] == "a.py"
    assert reduced[1]["path"] == "b.py"


def test_reduce_file_listing_reduces_above_threshold():
    listing = [{"path": f"./tree/dir/file-{i}.txt", "size": i} for i in range(1005)]

    reduced = checks.llm_eval._reduce_file_listing(listing)

    assert isinstance(reduced, dict)
    assert reduced["total_paths"] == 1005
    assert reduced["shown_paths"] == checks.llm_eval._FILE_LISTING_REDUCTION_THRESHOLD
    assert reduced["truncated"] is True
    assert reduced["paths"][0]["path"] == "file-0.txt"


def test_eval_ev_to_ai_performs_followup_when_model_requests_more_evidence():
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "build_log": "\n".join([f"line {i}" for i in range(1, 501)]),
    }
    check = {
        "id": "SEC-6",
        "title": "Endpoint exposure",
        "section": "Security",
        "todo_refs": ["TODO: - Manual review"],
        "adapters_required": ["sbuild"],
        "adapters_optional": [],
    }
    finding = _make_finding("SEC-6", mode="ev_to_ai")

    first_response = {
        "status": "unknown",
        "severity": "required",
        "confidence": "low",
        "message": "Need more context",
        "todo": "TODO: - request details",
        "rationale": "Insufficient context",
        "human_confirmation_required": True,
        "evidence_refs": [],
        "risk_flags": [],
        "additional_evidence_requests": [{"type": "line_range", "start": 300, "end": 320}],
    }
    second_response = {
        "status": "ok",
        "severity": "ok",
        "confidence": "medium",
        "message": "No endpoint exposure detected",
        "todo": "",
        "rationale": "Reviewed requested lines",
        "human_confirmation_required": True,
        "evidence_refs": ["sbuild:build_log"],
        "risk_flags": [],
    }

    with mock.patch("checks.llm_eval._select_ev_to_ai_model_tier", return_value="small"):
        with mock.patch("llm.call_llm", side_effect=[first_response, second_response]) as mocked:
            result = checks.llm_eval._eval_ev_to_ai(check, ctx, finding)

    assert mocked.call_count == 2
    second_prompt = mocked.call_args_list[1].args[0]
    assert "additional_evidence_requested" in second_prompt
    assert '"line": 300' in second_prompt
    assert result.status == "ok"


def test_cb_1_ok_when_sbuild_and_lp_builds_pass():
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {"status": "ok", "build_success": True}
    ctx.evidence["adapters"]["lp-build-api"] = {
        "status": "ok",
        "builds": [
            {"arch_tag": "amd64", "build_state": "Successfully built"},
            {"arch_tag": "arm64", "build_state": "Successfully built"},
        ],
    }

    finding = _make_finding("CB-1", mode="deterministic")
    result = checks.deterministic._check_cb_1(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "Launchpad build records pass" in result.message


def test_cb_1_not_ok_when_lp_build_state_fails():
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {"status": "ok", "build_success": True}
    ctx.evidence["adapters"]["lp-build-api"] = {
        "status": "ok",
        "builds": [
            {"arch_tag": "amd64", "build_state": "Successfully built"},
            {"arch_tag": "arm64", "build_state": "Failed to build"},
        ],
    }

    finding = _make_finding("CB-1", mode="deterministic")
    result = checks.deterministic._check_cb_1(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "arm64" in result.message


def test_esl_3_unexpected_built_using():
    """Test ESL-3 with unexpected Built-Using entries."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["deb-metadata"] = {
        "status": "ok",
        "message": "OK",
        "deb_packages": [
            {
                "package": "mypkg",
                "version": "1.0",
                "built_using": ["libfoo (>= 1.0)"],
                "static_built_using": [],
            },
        ],
    }
    finding = _make_finding("ESL-3", mode="deterministic")
    result = checks.deterministic._check_esl_3(ctx, finding)
    assert result.status == "not-ok"
    assert result.severity == "required"


def test_esl_3_missing_adapter():
    """Test ESL-3 when deb-metadata adapter is missing."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["deb-metadata"] = {"status": "error"}
    finding = _make_finding("ESL-3", mode="deterministic")
    result = checks.deterministic._check_esl_3(ctx, finding)
    assert result.status == "unknown"


def test_urf_1_clean_build_log():
    """Test URF-1 with clean build log."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "build_log": "dh_auto_configure\ndh_auto_build\ndh_auto_test\ndh_auto_install",
        "build_success": True,
    }

    finding = _make_finding("URF-1", mode="deterministic")
    result = checks.deterministic._check_urf_1(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "Errors/warnings" in result.message


def test_urf_1_build_warnings():
    """Test URF-1 with build warnings detected."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "build_log": "gcc -Wall test.c\ntest.c:5: warning: unused variable 'x'",
        "build_success": True,
    }

    finding = _make_finding("URF-1", mode="deterministic")
    result = checks.deterministic._check_urf_1(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"
    assert "warning" in result.message.lower()


def test_urf_1_build_errors():
    """Test URF-1 with build errors detected."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "build_log": "gcc -Wall test.c\ntest.c:3: error: undefined reference to 'foo'",
        "build_success": True,
    }

    finding = _make_finding("URF-1", mode="deterministic")
    result = checks.deterministic._check_urf_1(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "error" in result.message.lower()


def test_urf_1_security_warning():
    """Test URF-1 with security warning detected."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "build_log": "gcc -Wall test.c\ntest.c:10: warning: format string vulnerability",
        "build_success": True,
    }

    finding = _make_finding("URF-1", mode="deterministic")
    result = checks.deterministic._check_urf_1(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"
    assert "warning" in result.message.lower()


def test_prf_10_not_on_list():
    """Test PRF-10 when package is not on lto-disabled list."""
    ctx = _Ctx(source_package="testpkg")
    ctx.evidence["adapters"]["lp-package-api"] = {
        "status": "ok",
    }

    finding = _make_finding("PRF-10", mode="deterministic")
    result = checks.deterministic._check_prf_10(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "lto-disabled list" in result.message.lower()


def test_prf_10_on_list():
    """Test PRF-10 when package is on lto-disabled list (edge case)."""
    ctx = _Ctx(source_package="llvm")
    ctx.evidence["adapters"]["lp-package-api"] = {
        "status": "ok",
    }

    finding = _make_finding("PRF-10", mode="deterministic")
    result = checks.deterministic._check_prf_10(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "lto-disabled list" in result.message.lower()


def test_cb_8_not_python():
    """Test CB-8 when package is not Python."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("CB-8", mode="deterministic")
    result = checks.deterministic._check_cb_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not a Python package" in result.message


def test_cb_8_python_with_dh_python():
    """Test CB-8 when Python package uses dh_python."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_python3 build",
        "file_listing": [{"path": "setup.py", "size": 100}],
    }

    finding = _make_finding("CB-8", mode="deterministic")
    result = checks.deterministic._check_cb_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "using dh_python" in result.message


def test_cb_8_python_without_dh_python():
    """Test CB-8 when Python package does not use dh_python."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "file_listing": [{"path": "setup.py", "size": 100}],
    }

    finding = _make_finding("CB-8", mode="deterministic")
    result = checks.deterministic._check_cb_8(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "dh_python" in result.message.lower()


def test_esl_2_no_static_linking():
    """Test ESL-2 with clean build log (no static linking)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "build_log": "dh_auto_configure\ndh_auto_build\ndh_auto_test",
        "static_link_hints": [],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure",
        "file_listing": [],
    }

    finding = _make_finding("ESL-2", mode="deterministic")
    result = checks.deterministic._check_esl_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "static linking" in result.message


def test_esl_2_static_linking_detected():
    """Test ESL-2 when static linking is detected."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "build_log": "gcc -static -o myapp main.c",
        "static_link_hints": ["myapp"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure",
        "file_listing": [],
    }

    finding = _make_finding("ESL-2", mode="deterministic")
    result = checks.deterministic._check_esl_2(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "static linking" in result.message.lower()


def test_esl_2_static_linking_justified():
    """Test ESL-2 when static linking is justified."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "build_log": "gcc -static -o scanner security_scanner.c  # integrity checker",
        "static_link_hints": ["scanner"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure",
        "file_listing": [],
    }

    finding = _make_finding("ESL-2", mode="deterministic")
    result = checks.deterministic._check_esl_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "justified" in result.message.lower()


def test_prf_2_not_library():
    """Test PRF-2 when package is not a library."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp\nDescription: Command line tool",
        "debian_rules": "dh_auto_configure",
        "file_listing": [],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not applicable" in result.message.lower()


def test_prf_2_python_library():
    """Test PRF-2 when library is Python (symbols not applicable)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: libpython-mylib\nDescription: Python library",
        "debian_rules": "dh_auto_configure\ndh_python3 build",
        "file_listing": [{"path": "setup.py", "size": 100}],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "language" in result.message.lower()


def test_prf_2_cpp_library_with_symbols():
    """Test PRF-2 when C++ library has symbols file."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: libmyapp1\nLibrary package with .so and .symbols",
        "debian_rules": "dh_makeshlibs",
        "file_listing": [{"path": "debian/libmyapp1.symbols", "size": 500}],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "symbols tracking is in place" in result.message


def test_prf_3_watch_present():
    """Test PRF-3 when debian/watch is present."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "file_listing": [
            {"path": "debian/watch", "size": 200},
            {"path": "debian/control", "size": 500},
        ],
    }

    finding = _make_finding("PRF-3", mode="deterministic")
    result = checks.deterministic._check_prf_3(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "debian/watch" in result.message


def test_prf_3_native_package():
    """Test PRF-3 when package is native (watch not needed)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "debian/source/format: 3.0 (native)",
        "file_listing": [{"path": "debian/control", "size": 500}],
    }

    finding = _make_finding("PRF-3", mode="deterministic")
    result = checks.deterministic._check_prf_3(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not needed" in result.message.lower()


def test_prf_3_non_native_no_watch():
    """Test PRF-3 when non-native package lacks debian/watch."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: upstream-tool\nVersion: 1.2.3-1",
        "file_listing": [
            {"path": "debian/control", "size": 500},
            {"path": "debian/changelog", "size": 300},
        ],
    }

    finding = _make_finding("PRF-3", mode="deterministic")
    result = checks.deterministic._check_prf_3(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"
    assert "debian/watch" in result.message


def test_sec_2_non_root():
    """Test SEC-2 when daemon does not run as root."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "[Unit]\nUser=myuser\nDynamicUser=yes",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("SEC-2", mode="deterministic")
    result = checks.deterministic._check_sec_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "root" in result.message.lower()


def test_sec_2_root_with_mitigations():
    """Test SEC-2 when daemon runs as root but has mitigations."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "User=root\nSeccomp=strict\nAppArmor=profile",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("SEC-2", mode="deterministic")
    result = checks.deterministic._check_sec_2(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"
    assert "mitigations" in result.message.lower()


def test_sec_2_root_no_mitigations():
    """Test SEC-2 when daemon runs as root with no mitigations."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "User=root",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("SEC-2", mode="deterministic")
    result = checks.deterministic._check_sec_2(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_urf_3_no_escalation():
    """Test URF-3 when no privilege escalation found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-3", mode="deterministic")
    result = checks.deterministic._check_urf_3(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_urf_3_escalation_outside_tests():
    """Test URF-3 when privilege escalation found outside tests."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "sudo apt-get install foo",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-3", mode="deterministic")
    result = checks.deterministic._check_urf_3(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_urf_3_test_marker_elsewhere_does_not_bypass():
    """Test URF-3 when escalation exists outside test-context lines."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "# tests run in autopkgtest\nsudo apt-get install foo",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-3", mode="deterministic")
    result = checks.deterministic._check_urf_3(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_urf_4_no_nobody():
    """Test URF-4 when no 'nobody' user found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "User=myapp",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_urf_4_nobody_found():
    """Test URF-4 when 'nobody' user found outside tests."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "User=nobody",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_urf_4_test_marker_elsewhere_does_not_bypass():
    """Test URF-4 when nobody exists outside test-context lines."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "# tests use fake users\nUser=nobody",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_urf_5_no_setuid():
    """Test URF-5 when no setuid/setgid found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-5", mode="deterministic")
    result = checks.deterministic._check_urf_5(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_urf_5_setuid_with_systemd():
    """Test URF-5 when setuid present but using systemd."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "chmod 4755 myapp\n# Using systemd service permissions",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-5", mode="deterministic")
    result = checks.deterministic._check_urf_5(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"


def test_urf_5_setuid_no_justification():
    """Test URF-5 when setuid present without justification."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "chmod 4755 myapp",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-5", mode="deterministic")
    result = checks.deterministic._check_urf_5(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_urf_7_no_old_webkit():
    """Test URF-7 when no old webkit dependencies found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libglib2.0", "libgtk-3-0"],
    }

    finding = _make_finding("URF-7", mode="deterministic")
    result = checks.deterministic._check_urf_7(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_urf_7_webkit_found():
    """Test URF-7 when webkit dependency found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libwebkit2gtk-4.0", "libgtk-3-0"],
    }

    finding = _make_finding("URF-7", mode="deterministic")
    result = checks.deterministic._check_urf_7(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "webkit" in result.message.lower()


def test_sec_8_no_accounts():
    """Test SEC-8 when no centralized accounts found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libglib2.0", "libgtk-3-0"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("SEC-8", mode="deterministic")
    result = checks.deterministic._check_sec_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_sec_8_accounts_found():
    """Test SEC-8 when centralized accounts dependency found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "gnome-online-accounts", "libgtk-3-0"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("SEC-8", mode="deterministic")
    result = checks.deterministic._check_sec_8(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "account" in result.message.lower()


def test_sec_10_no_pam():
    """Test SEC-10 when no PAM dependencies found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libglib2.0", "libgtk-3-0"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("SEC-10", mode="deterministic")
    result = checks.deterministic._check_sec_10(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_sec_10_pam_found():
    """Test SEC-10 when PAM dependency found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libpam0g", "libgtk-3-0"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("SEC-10", mode="deterministic")
    result = checks.deterministic._check_sec_10(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "pam" in result.message.lower()


def test_urf_8_not_ui_package():
    """Test URF-8 when not a UI package (gate N/A; check passes)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: libfoo-dev",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("URF-8", mode="deterministic")
    result = checks.deterministic._check_urf_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not part of the ui" in result.message.lower()


def test_urf_8_ui_with_desktop():
    """Test URF-8 when UI package with a valid .desktop file (check passes)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: gnome-calculator",
        "debian_rules": "dh_auto_build",
        "file_listing": [
            {"path": "usr/share/applications/gnome-calculator.desktop", "size": 500},
        ],
    }

    finding = _make_finding("URF-8", mode="deterministic")
    result = checks.deterministic._check_urf_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "part of the ui" in result.message.lower()


def test_urf_9_not_user_visible():
    """Test URF-9 when package is not user-visible (gate N/A; check passes)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: libfoo-dev",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("URF-9", mode="deterministic")
    result = checks.deterministic._check_urf_9(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not user-visible" in result.message.lower()


def test_urf_9_user_visible_with_translations():
    """Test URF-9 when user-visible package has translations (check passes)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: gnome-calculator",
        "debian_rules": "dh_auto_build",
        "file_listing": [
            {"path": "usr/share/locale/de/LC_MESSAGES/gnome-calculator.mo", "size": 500},
        ],
    }

    finding = _make_finding("URF-9", mode="deterministic")
    result = checks.deterministic._check_urf_9(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "translation present" in result.message.lower()


def test_cb_7_no_py2():
    """Test CB-7 when no Python 2 dependencies found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["python3", "libc6", "libglib2.0"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("CB-7", mode="deterministic")
    result = checks.deterministic._check_cb_7(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_cb_7_py2_found():
    """Test CB-7 when Python 2 dependency found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["python2", "libc6", "libglib2.0"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("CB-7", mode="deterministic")
    result = checks.deterministic._check_cb_7(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "python2" in result.message.lower()


def test_sec_3_no_webkit():
    """Test SEC-3 when no webkit dependencies found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libgtk-3-0", "libglib2.0"],
    }

    finding = _make_finding("SEC-3", mode="deterministic")
    result = checks.deterministic._check_sec_3(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_sec_3_webkit_found():
    """Test SEC-3 when webkit dependency found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libwebkit2gtk-4.0", "libgtk-3-0"],
    }

    finding = _make_finding("SEC-3", mode="deterministic")
    result = checks.deterministic._check_sec_3(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "webkit" in result.message.lower()


def test_sec_4_no_v8():
    """Test SEC-4 when no V8 dependencies found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libnode", "libglib2.0"],
    }

    finding = _make_finding("SEC-4", mode="deterministic")
    result = checks.deterministic._check_sec_4(ctx, finding)

    # libnode matches v8_patterns, so should fail
    assert result.status == "not-ok"
    assert result.severity == "required"


def test_sec_4_v8_not_found():
    """Test SEC-4 when V8 not in dependencies."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libgtk-3-0", "libglib2.0"],
    }

    finding = _make_finding("SEC-4", mode="deterministic")
    result = checks.deterministic._check_sec_4(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_esl_4_not_go():
    """Test ESL-4 when package is not Go (gate N/A; check passes)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "go_sum_present": False,
        "cargo_lock_present": False,
    }

    finding = _make_finding("ESL-4", mode="deterministic")
    result = checks.deterministic._check_esl_4(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not" in result.message.lower() and "go" in result.message.lower()


def test_esl_4_is_go():
    """Test ESL-4 when package is Go (gate active; check still passes)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure --buildsystem golang",
        "debian_control": "Package: myapp\nBuild-Depends: golang-go",
        "file_listing": [{"path": "main.go", "size": 100}],
        "go_sum_present": False,
        "cargo_lock_present": False,
    }

    finding = _make_finding("ESL-4", mode="deterministic")
    result = checks.deterministic._check_esl_4(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "go" in result.message.lower()


def test_esl_8_not_rust():
    """Test ESL-8 when package is not Rust (gate N/A; check passes)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "go_sum_present": False,
        "cargo_lock_present": False,
    }

    finding = _make_finding("ESL-8", mode="deterministic")
    result = checks.deterministic._check_esl_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not" in result.message.lower() and "rust" in result.message.lower()


def test_esl_8_is_rust():
    """Test ESL-8 when package is Rust (gate active; check still passes)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure --buildsystem cargo",
        "debian_control": "Package: myapp\nBuild-Depends: cargo, rustc",
        "file_listing": [{"path": "src/main.rs", "size": 100}],
        "go_sum_present": False,
        "cargo_lock_present": False,
    }

    finding = _make_finding("ESL-8", mode="deterministic")
    result = checks.deterministic._check_esl_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "rust" in result.message.lower()


def test_dep_1_no_unresolved():
    """Test DEP-1 when no unresolved runtime dependencies."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "in_scope_deps_not_in_main": [],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("DEP-1", mode="deterministic")
    result = checks.deterministic._check_dep_1(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_dep_1_unresolved_dep():
    """Test DEP-1 when unresolved dependency found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "in_scope_deps_not_in_main": ["myuniversepkg"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("DEP-1", mode="deterministic")
    result = checks.deterministic._check_dep_1(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_esl_9_not_rust():
    """Test ESL-9 when package is not Rust."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("ESL-9", mode="deterministic")
    result = checks.deterministic._check_esl_9(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_esl_9_rust_with_dh_cargo():
    """Test ESL-9 when Rust package uses dh_cargo."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure --buildsystem cargo\ndh_auto_build",
        "debian_control": "Package: myapp\nBuild-Depends: cargo, rustc",
        "file_listing": [{"path": "src/main.rs", "size": 100}],
    }

    finding = _make_finding("ESL-9", mode="deterministic")
    result = checks.deterministic._check_esl_9(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_esl_9_rust_without_dh_cargo():
    """Test ESL-9 when Rust package doesn't use dh_cargo."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp\nBuild-Depends: cargo, rustc",
        "file_listing": [{"path": "src/main.rs", "size": 100}],
    }

    finding = _make_finding("ESL-9", mode="deterministic")
    result = checks.deterministic._check_esl_9(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_prf_8_no_warnings():
    """Test PRF-8 when no lintian warnings."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_warnings": [],
        "lintian_errors": [],
    }

    finding = _make_finding("PRF-8", mode="deterministic")
    result = checks.deterministic._check_prf_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_prf_8_few_warnings():
    """Test PRF-8 when few lintian warnings."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_warnings": ["W1", "W2"],
        "lintian_errors": [],
    }

    finding = _make_finding("PRF-8", mode="deterministic")
    result = checks.deterministic._check_prf_8(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "ok"


def test_prf_8_excessive_warnings():
    """Test PRF-8 when excessive lintian warnings."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_warnings": ["W1", "W2", "W3", "W4", "W5", "W6"],
        "lintian_errors": [],
    }

    finding = _make_finding("PRF-8", mode="deterministic")
    result = checks.deterministic._check_prf_8(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"


def test_prf_8_errors():
    """Test PRF-8 when lintian errors found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_warnings": [],
        "lintian_errors": ["E1", "E2"],
    }

    finding = _make_finding("PRF-8", mode="deterministic")
    result = checks.deterministic._check_prf_8(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


# ---------------------------------------------------------------------------
# PRF-6: Current release packaged
# ---------------------------------------------------------------------------


def test_prf_6_current_version():
    """Test PRF-6 when archive version is current with upstream."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lp-package-api"] = {
        "status": "ok",
        "current_version": "1.2.3-0ubuntu1",
    }
    ctx.evidence["adapters"]["upstream-tracker"] = {
        "status": "ok",
        "latest_version": "1.2.3",
    }

    finding = _make_finding("PRF-6", mode="deterministic")
    result = checks.deterministic._check_prf_6(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "current" in result.message.lower() or "packaged" in result.message.lower()


def test_prf_6_behind_upstream():
    """Test PRF-6 when archive version is somewhat behind upstream."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lp-package-api"] = {
        "status": "ok",
        "current_version": "1.1.0-2ubuntu1",
    }
    ctx.evidence["adapters"]["upstream-tracker"] = {
        "status": "ok",
        "latest_version": "1.3.0",
    }

    finding = _make_finding("PRF-6", mode="deterministic")
    result = checks.deterministic._check_prf_6(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"


def test_prf_6_very_old_version():
    """Test PRF-6 when archive version is very old compared to upstream."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lp-package-api"] = {
        "status": "ok",
        "current_version": "1:0.9.0-0ubuntu1",
    }
    ctx.evidence["adapters"]["upstream-tracker"] = {
        "status": "ok",
        "latest_version": "2.0.0",
    }

    finding = _make_finding("PRF-6", mode="deterministic")
    result = checks.deterministic._check_prf_6(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_prf_6_adapter_missing():
    """Test PRF-6 when lp-package-api adapter is missing."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lp-package-api"] = {
        "status": "error",
    }

    finding = _make_finding("PRF-6", mode="deterministic")
    result = checks.deterministic._check_prf_6(ctx, finding)

    assert result.status == "unknown"


def test_prf_6_current_version_with_epoch_and_ubuntu_revision():
    """PRF-6 should ignore epoch and Ubuntu revision when matching upstream."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lp-package-api"] = {
        "status": "ok",
        "current_version": "2:3.4.5-1ubuntu2",
    }
    ctx.evidence["adapters"]["upstream-tracker"] = {
        "status": "ok",
        "latest_version": "3.4.5",
    }

    finding = _make_finding("PRF-6", mode="deterministic")
    result = checks.deterministic._check_prf_6(ctx, finding)

    assert result.status == "ok"


def test_versions_compatible_strips_debian_revision():
    """PRF-6 version comparison should use the upstream portion of package versions."""
    is_compatible, _ = checks.deterministic._versions_compatible(
        "1:2.3.4-0ubuntu1",
        "2.3.4",
    )

    assert is_compatible is True

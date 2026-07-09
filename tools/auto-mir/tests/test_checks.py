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
                        "blocker_message": "webkit1/2 dependency found ({dep}) — hard blocker",
                        "blocker_todo": "TODO: - webkit1/2 dependency must be removed before main inclusion",
                    },
                },
                {
                    "id": "SEC-4",
                    "messages": {
                        "ok_message": "does not use lib*v8 directly",
                        "unknown_message": "Could not analyse v8 dependencies",
                        "blocker_message": "lib*v8 dependency found ({dep}) — hard blocker",
                        "blocker_todo": "TODO: - direct lib*v8 dependency must be removed before main inclusion",
                    },
                },
                {
                    "id": "CB-7",
                    "messages": {
                        "ok_message": "no new python2 dependency",
                        "unknown_message": "Could not analyse Python2 dependencies",
                        "blocker_message": "Python2 dependency found ({dep}) — hard blocker",
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
                    "messages": {
                        "hint_local_ok": "local sbuild build succeeded",
                        "hint_local_failed": "local sbuild build FAILED (see build log)",
                        "hint_local_unavailable": "local sbuild result unavailable",
                        "unknown_no_lp_message": "Could not confirm Launchpad build state ({local_hint})",
                        "unknown_no_lp_todo": "TODO: - does not FTBFS currently ({local_hint}; verify recent Launchpad build records)",
                        "unknown_no_builds_message": "No Launchpad build records were found ({local_hint})",
                        "unknown_no_builds_todo": "TODO: - does not FTBFS currently ({local_hint}; no Launchpad build records to confirm)",
                        "not_ok_message": "Launchpad build state shows failures: {failed_builds}",
                        "not_ok_todo": "TODO: - does not FTBFS currently",
                        "ok_message": "does not FTBFS currently; Launchpad build records pass for arches: {passing_arches}",
                        "ok_local_suffix": "; local sbuild build also succeeded",
                    },
                },
                {
                    "id": "PRF-6",
                    "messages": {
                        "unknown_message": "Could not determine package version information",
                        "unknown_todo": "TODO: - Verify packaged version against latest upstream release",
                        "ok_message": "the current release is packaged",
                        "very_behind_message": "Package is very behind upstream: {archive} vs {upstream}",
                        "somewhat_behind_message": "Package is somewhat behind upstream: {archive} vs {upstream}",
                        "behind_todo": "TODO: - Consider updating to a more recent upstream release",
                        "version_lag_message": "Package version lag detected: {archive} vs {upstream}",
                        "unknown_lag_message": "Could not determine version lag",
                        "version_lag_todo": "TODO: - Verify upstream version availability",
                    },
                },
                {
                    "id": "PRF-8",
                    "messages": {
                        "unknown_message": "Could not run lintian (lintian adapter failed)",
                        "not_ok_errors_message": "Lintian errors detected: {errors}",
                        "not_ok_errors_todo": "TODO: - no excessive lintian warnings",
                        "not_ok_many_message": "Lintian found {count} warnings - review and fix if possible",
                        "not_ok_many_todo": "TODO: - Review and fix lintian warnings",
                        "minor_message": "Lintian found {count} minor warnings - acceptable",
                        "minor_todo": "TODO: - {count} minor lintian warnings documented",
                        "ok_message": "no excessive lintian warnings",
                    },
                },
                {
                    "id": "URF-1",
                    "messages": {
                        "unknown_message": "Could not inspect build log",
                        "unknown_todo": "TODO: - Check build log for errors and warnings",
                        "not_ok_errors_message": "Build log contains errors: {errors}",
                        "not_ok_errors_todo": "TODO: - no Errors/warnings during the build",
                        "warnings_message": "Build log contains {count} toolchain warning(s); first: {sample}",
                        "warnings_todo": "TODO: - no Errors/warnings during the build",
                        "warnings_rationale": "review {count} build warning(s) and decide if acceptable: {sample}",
                        "ok_message": "no Errors/warnings during the build",
                    },
                    "negated_statement": "Concerning Errors/warnings during the build",
                },
                {
                    "id": "PRF-10",
                    "messages": {
                        "ok_message": "It is not on the lto-disabled list",
                        "not_ok_message": "Package is on the lto-disabled list (architectures: {arches}); LTO must be fixed or disabled in the package before promotion",
                        "not_ok_todo": "TODO: - Package is on the lto-disabled list ({arches}); ensure the LTO fix or in-package workaround is present before promotion",
                        "unknown_message": "Could not retrieve the lto-disabled-list (adapter failed)",
                        "unknown_todo": "TODO: - Manually verify the package is not on lp:ubuntu/+source/lto-disabled-list",
                    },
                },
                {
                    "id": "CB-8",
                    "messages": {
                        "unknown_message": "Could not inspect debian/rules (packaging-source failed)",
                        "unknown_todo": "TODO: - Check debian/rules for dh_python",
                        "ok_not_python_message": "not a Python package; Python packaging constraints do not apply",
                        "ok_message": "Python package, but using dh_python",
                        "not_ok_message": "Python package detected but dh_python/dh_python3 not found in debian/rules",
                        "not_ok_todo": "TODO: - Python packages must use dh_python",
                    },
                },
                {
                    "id": "ESL-2",
                    "messages": {
                        "unknown_message": "Could not inspect build log for static linking",
                        "unknown_todo": "TODO: - Check build log for static linking",
                        "ok_message": "no static linking",
                        "ok_justified_message": "static linking present but appears to be justified (e.g., scanner/bootloader)",
                        "not_ok_detail_binaries": "statically linked binaries: {binaries}",
                        "not_ok_detail_hints": "debian/rules hints: {hints}",
                        "not_ok_message": "Static linking detected without clear justification; review needed{detail}",
                        "not_ok_todo": "TODO: - no static linking",
                    },
                },
                {
                    "id": "PRF-2",
                    "messages": {
                        "unknown_message": "Could not inspect packaging (packaging-source failed)",
                        "unknown_todo": "TODO: - Check for symbols file",
                        "ok_message": "symbols tracking is in place",
                        "ok_no_shared_message": "symbols tracking not applicable for this kind of code",
                        "not_ok_message": "Shared library is shipped but no debian/*.symbols file was found",
                        "not_ok_todo": "TODO: - symbols tracking isn't in place; add a debian/*.symbols file (or, for C++ libraries, document why tracking is impractical)",
                    },
                },
                {
                    "id": "PRF-3",
                    "messages": {
                        "unknown_message": "Could not inspect packaging (packaging-source failed)",
                        "unknown_todo": "TODO: - Check for debian/watch file",
                        "ok_message": "debian/watch is present and looks ok",
                        "ok_native_message": "debian/watch is not present but also not needed (native package)",
                        "not_ok_message": "Non-native package but debian/watch not found",
                        "not_ok_todo": "TODO: - Add debian/watch to track upstream releases",
                    },
                },
                {
                    "id": "SEC-2",
                    "messages": {
                        "unknown_message": "Could not inspect packaging source",
                        "unknown_todo": "TODO: - Check for daemon running as root",
                        "mitigated_message": "Package runs as root but has security mitigations",
                        "mitigated_todo": "TODO: - Note root execution and mitigations",
                        "not_ok_message": "Package runs daemon as root without security mitigations",
                        "not_ok_todo": "TODO: - does not run a daemon as root",
                        "ok_message": "does not run a daemon as root",
                    },
                },
                {
                    "id": "URF-3",
                    "messages": {
                        "unknown_message": "Could not inspect packaging source",
                        "unknown_todo": "TODO: - Check for privilege escalation outside tests",
                        "not_ok_message": "Potential sudo/gksu/pkexec/LD_LIBRARY_PATH usage found outside tests",
                        "not_ok_todo": "TODO: - no use of sudo, gksu, pkexec, or LD_LIBRARY_PATH (usage is OK inside tests)",
                        "ok_message": "no use of sudo, gksu, pkexec, or LD_LIBRARY_PATH (usage is OK inside tests)",
                    },
                },
                {
                    "id": "URF-4",
                    "messages": {
                        "unknown_message": "Could not inspect packaging source",
                        "unknown_todo": "TODO: - Check for 'nobody' user usage",
                        "not_ok_message": "User 'nobody' found outside test context: {hits}",
                        "not_ok_todo": "TODO: - no use of user 'nobody' outside of tests",
                        "ok_message": "no use of user 'nobody' outside of tests",
                    },
                },
                {
                    "id": "URF-5",
                    "messages": {
                        "unknown_message": "Could not inspect packaging source",
                        "unknown_todo": "TODO: - Check for setuid/setgid binaries",
                        "source_binaries": "built binaries: {files}",
                        "source_lintian": "lintian output",
                        "source_tree": "source tree: {hits}",
                        "source_rules": "debian/rules",
                        "systemd_message": "setuid/setgid present ({source}) but using systemd service permissions",
                        "systemd_todo": "TODO: - use of setuid, but ok because systemd is used",
                        "not_ok_message": "setuid/setgid detected in {source}",
                        "not_ok_todo": "TODO: - no use of setuid / setgid",
                        "ok_message": "no use of setuid / setgid",
                    },
                },
                {
                    "id": "URF-7",
                    "messages": {
                        "unknown_message": "Could not analyse webkit/qtwebkit/libseed dependencies",
                        "unknown_todo": "TODO: - Check for old webkit dependencies",
                        "not_ok_message": "Old web engine dependency found: {dep}",
                        "not_ok_todo": "TODO: - no dependency on webkit, qtwebkit or libseed",
                        "ok_message": "no dependency on webkit, qtwebkit or libseed",
                    },
                },
                {
                    "id": "SEC-8",
                    "messages": {
                        "unknown_message": "Could not analyse online-accounts usage",
                        "unknown_todo": "TODO: - does not use centralized online accounts",
                        "not_ok_dep_message": "Centralized accounts dependency found: {dep}",
                        "not_ok_source_message": "Online accounts pattern found: {pattern}",
                        "not_ok_todo": "TODO: - does not use centralized online accounts",
                        "ok_message": "does not use centralized online accounts",
                    },
                },
                {
                    "id": "SEC-10",
                    "messages": {
                        "unknown_message": "Could not analyse PAM/authentication usage",
                        "unknown_todo": "TODO: - does not deal with system authentication (eg, pam), etc)",
                        "not_ok_dev_message": "Direct PAM development dependency found: {dep}",
                        "not_ok_runtime_message": "PAM runtime library dependency found: {dep} — verify it does not handle auth",
                        "not_ok_todo": "TODO: - does not deal with system authentication (eg, pam), etc)",
                        "ok_message": "does not deal with system authentication (eg, pam), etc)",
                    },
                },
                {
                    "id": "URF-8",
                    "messages": {
                        "unknown_message": "Could not inspect packaging (packaging-source failed)",
                        "unknown_todo": "TODO: - Check for .desktop files",
                        "ok_not_ui_message": "not part of the UI for extra checks",
                        "ok_not_ui_todo": "TODO-A: - not part of the UI for extra checks",
                        "ok_desktop_message": "part of the UI, desktop file is ok",
                        "ok_desktop_todo": "TODO-B: - part of the UI, desktop file is ok",
                        "not_ok_message": "UI package without valid .desktop file",
                        "not_ok_todo": "TODO: - part of the UI, desktop file is ok",
                    },
                },
                {
                    "id": "URF-9",
                    "messages": {
                        "unknown_message": "Could not inspect packaging (packaging-source failed)",
                        "unknown_todo": "TODO: - Check for translation coverage",
                        "ok_not_visible_message": "not user-visible, translations not needed",
                        "ok_not_visible_todo": "TODO-A: - no translation present, but none needed for this case (not user visible)",
                        "ok_translated_message": "user-visible with translation present",
                        "ok_translated_todo": "TODO-B: - translation present",
                        "not_ok_message": "User-visible package without translations",
                        "not_ok_todo": "TODO: - translation present",
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


def test_is_python_package_ignores_stray_py_file():
    """A stray .py helper/test script must not classify a C/C++ package as Python."""
    packaging = {
        "status": "ok",
        "debian_control": "Source: libgav1\n\nPackage: libgav1-2\nBuild-Depends: cmake",
        "debian_rules": "%:\n\tdh $@",
        "file_listing": [{"path": "tests/helper.py", "size": 80}],
    }
    assert checks.language_gates._is_python_package(packaging) is False


def test_is_python_package_detects_real_signals():
    """Genuine Python packaging signals are still detected."""
    dh_python = {
        "debian_control": "Package: python3-x\nBuild-Depends: dh-python, python3-all",
        "debian_rules": "%:\n\tdh $@ --with python3 --buildsystem=pybuild",
        "file_listing": [],
    }
    assert checks.language_gates._is_python_package(dh_python) is True

    metadata = {
        "debian_control": "Package: python3-y",
        "debian_rules": "dh $@",
        "file_listing": [{"path": "pyproject.toml", "size": 40}],
    }
    assert checks.language_gates._is_python_package(metadata) is True


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


def test_render_ev_to_ai_prompt_uses_disk_fallback_when_tool_root_missing():
    """When prompts/ev_to_ai.md cannot be resolved, the on-disk fallback is used."""
    ctx = _Ctx()
    ctx.tool_root = None  # force the fallback path
    check = {
        "id": "URF-2",
        "title": "Memory safety",
        "section": "Upstream red flags",
        "todo_refs": ["TODO: - check"],
    }

    prompt = checks.llm_eval._render_ev_to_ai_prompt(check, {"adapter": "x"}, "policy text", ctx)

    # Placeholders are substituted and the fallback body is present.
    assert "URF-2" in prompt
    assert "{{check_id}}" not in prompt
    assert "human MIR reviewer" in prompt


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


def test_cb_1_todo_with_local_build_hint_when_lp_missing():
    """When Launchpad records are missing, stay TODO but hint the local build worked."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {"status": "ok", "build_success": True}
    ctx.evidence["adapters"]["lp-build-api"] = {"status": "ok", "builds": []}

    finding = _make_finding("CB-1", mode="deterministic")
    result = checks.deterministic._check_cb_1(ctx, finding)

    assert result.status == "unknown"
    assert "local sbuild build succeeded" in result.message
    assert "local sbuild build succeeded" in result.todo


def test_cb_1_todo_hints_local_build_failure():
    """A failed local build is surfaced in the hint when Launchpad data is absent."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {"status": "ok", "build_success": False}
    ctx.evidence["adapters"]["lp-build-api"] = {"status": "error"}

    finding = _make_finding("CB-1", mode="deterministic")
    result = checks.deterministic._check_cb_1(ctx, finding)

    assert result.status == "unknown"
    assert "FAILED" in result.message


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
    """Genuine build warnings are routed to reviewer judgement (Left to decide)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "build_log": "gcc -Wall test.c\ntest.c:5: warning: unused variable 'x'",
        "build_success": True,
    }

    finding = _make_finding("URF-1", mode="deterministic")
    result = checks.deterministic._check_urf_1(ctx, finding)

    assert result.status == "unknown"
    assert result.severity == "recommended"
    assert "warning" in result.message.lower()


def test_urf_1_ignores_dpkg_noise():
    """dpkg-source/dpkg-buildflags noise must not be reported as build warnings."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "build_log": (
            "dpkg-source: warning: cannot verify inline signature for ./foo.dsc: "
            "no acceptable signature found\n"
            "dpkg-buildflags: warning: debian/changelog not found. Not setting "
            "ELF package metadata parameter.\n"
            "gcc -O2 -c foo.c\n"
        ),
        "build_success": True,
    }

    finding = _make_finding("URF-1", mode="deterministic")
    result = checks.deterministic._check_urf_1(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "Errors/warnings" in result.message


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
    """Test URF-1 with security warning detected (reviewer judgement)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "build_log": "gcc -Wall test.c\ntest.c:10: warning: format string vulnerability",
        "build_success": True,
    }

    finding = _make_finding("URF-1", mode="deterministic")
    result = checks.deterministic._check_urf_1(ctx, finding)

    assert result.status == "unknown"
    assert result.severity == "recommended"
    assert "warning" in result.message.lower()


def test_prf_10_not_on_list():
    """Test PRF-10 when package is not on lto-disabled list."""
    ctx = _Ctx(source_package="testpkg")
    ctx.evidence["adapters"]["lto-disabled-list"] = {
        "status": "ok",
        "on_list": False,
        "disabled_arches": [],
    }

    finding = _make_finding("PRF-10", mode="deterministic")
    result = checks.deterministic._check_prf_10(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "lto-disabled list" in result.message.lower()


def test_prf_10_on_list():
    """Test PRF-10 when package is on lto-disabled list (any architecture)."""
    ctx = _Ctx(source_package="llvm")
    ctx.evidence["adapters"]["lto-disabled-list"] = {
        "status": "ok",
        "on_list": True,
        "disabled_arches": ["arm64", "s390x"],
    }

    finding = _make_finding("PRF-10", mode="deterministic")
    result = checks.deterministic._check_prf_10(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "lto-disabled list" in result.message.lower()
    # Affected architectures are surfaced to the reviewer.
    assert "arm64" in result.message
    assert "s390x" in result.message


def test_prf_10_adapter_error_degrades_to_unknown():
    """Test PRF-10 degrades to unknown (left for reviewer) when fetch fails."""
    ctx = _Ctx(source_package="testpkg")
    ctx.evidence["adapters"]["lto-disabled-list"] = {
        "status": "error",
        "error": "network unreachable",
    }

    finding = _make_finding("PRF-10", mode="deterministic")
    result = checks.deterministic._check_prf_10(ctx, finding)

    assert result.status == "unknown"
    assert result.confidence == "low"
    assert result.todo.startswith("TODO:")
    assert "lto-disabled" in result.message.lower()


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


def test_esl_2_ignores_configure_static_probe():
    """A configure feature probe for -static must not be treated as static linking."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "build_log": (
            "checking if gcc static flag -static works... yes\n"
            "checking if g++ static flag -static works... yes\n"
            "libtool --mode=link gcc -Wl,-Bsymbolic-functions -o liblua.so lua.o\n"
        ),
        "static_link_hints": [],
        "static_binaries": [],
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
    assert result.message == "no static linking"


def test_esl_2_static_binary_in_built_deb_flagged():
    """A fully static ELF binary shipped in a built deb is flagged."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "build_log": "dh_auto_build\n",
        "static_link_hints": [],
        "static_binaries": ["mytool/usr/bin/mytool"],
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
    assert "mytool" in result.message


def test_esl_2_ignores_static_libgcc_helper_flag():
    """A build log with only helper flags / no static binaries reports no static linking."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "build_log": "gcc -static-libgcc -static-libstdc++ -o app app.c\n",
        "static_link_hints": [],
        "static_binaries": [],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure",
        "file_listing": [],
    }

    finding = _make_finding("ESL-2", mode="deterministic")
    result = checks.deterministic._check_esl_2(ctx, finding)

    assert result.status == "ok"
    assert result.message == "no static linking"


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
    """A pure-Python library (no shared object) needs no symbols tracking."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: python3-mylib\nDescription: Python library",
        "debian_rules": "dh_auto_configure\ndh_python3 build",
        "file_listing": [{"path": "setup.py", "size": 100}],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not applicable" in result.message.lower()


def test_prf_2_python_package_shipping_shared_lib_still_tracked():
    """A package that ships BOTH Python code and a .so is still responsible for
    symbols tracking of that shared library (language does not exempt it)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": (
            "Source: mymix\n\n"
            "Package: python3-mymix\nDepends: ${python3:Depends}\n\n"
            "Package: libmymix1\nDepends: ${shlibs:Depends}\n"
        ),
        "debian_rules": "dh_python3 build",
        "file_listing": [{"path": "setup.py", "size": 100}],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"
    assert "libmymix1" in result.rationale


def test_prf_2_cpp_library_with_helper_py_and_symbols():
    """Feedback #8: a C++ library that ships a helper .py and a .symbols file is
    credited with tracking in place (not mis-gated as Python/not-applicable)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Source: libgav1\n\nPackage: libgav1-2\nDepends: ${shlibs:Depends}",
        "debian_rules": "%:\n\tdh $@",
        "file_listing": [
            {"path": "debian/libgav1-2.symbols", "size": 500},
            {"path": "tests/helper.py", "size": 80},
        ],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "symbols tracking is in place" in result.message
    assert "libgav1-2.symbols" in result.rationale


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


def test_prf_2_shared_library_with_symbols_file():
    """A C shared library that ships debian/<pkg>.symbols reports tracking in place."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": (
            "Source: lua5.5\n\n"
            "Package: liblua5.5-0\nArchitecture: any\n\n"
            "Package: liblua5.5-dev\nArchitecture: any\n"
        ),
        "debian_rules": "dh_makeshlibs",
        "file_listing": [
            {"path": "./debian/liblua5.5-0.symbols", "size": 500},
            {"path": "./debian/control", "size": 500},
        ],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert result.message == "symbols tracking is in place"


def test_prf_2_shared_library_without_symbols_file():
    """A shared library with no symbols file is flagged as a recommendation."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Source: foo\n\nPackage: libfoo1\nArchitecture: any\n",
        "debian_rules": "dh_auto_configure",
        "file_listing": [{"path": "./debian/control", "size": 500}],
    }
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "built_debs": ["/tmp/out/libfoo1_1.0-1_amd64.deb"],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"
    assert "symbols" in result.message.lower()


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


def test_sec_2_root_in_comment_no_trigger():
    """Test SEC-2 when 'User=root' appears only in a comment line."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "# Do not set User=root\nUser=daemon",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("SEC-2", mode="deterministic")
    result = checks.deterministic._check_sec_2(ctx, finding)

    # comment line must not trigger the root check; User=daemon satisfies non-root
    assert result.status == "ok"
    assert result.severity == "ok"


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
    """Test URF-5 when no setuid/setgid found in rules or lintian."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_errors": [],
        "lintian_warnings": [],
        "lintian_pedantic": [],
    }

    finding = _make_finding("URF-5", mode="deterministic")
    result = checks.deterministic._check_urf_5(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_urf_5_setuid_with_systemd():
    """Test URF-5 when setuid present but using systemd (mitigated)."""
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
    """Test URF-5 when setuid present in rules without justification."""
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


def test_urf_5_lintian_setuid_tag():
    """Test URF-5 when lintian reports a setuid-binary tag on the built artifact."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_errors": [],
        "lintian_warnings": ["W: myapp: setuid-binary usr/bin/myapp 4755 root/root"],
        "lintian_pedantic": [],
    }

    finding = _make_finding("URF-5", mode="deterministic")
    result = checks.deterministic._check_urf_5(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "lintian" in result.message.lower()


def test_urf_4_nobody_found_in_source_tree():
    """URF-4 detects 'nobody' in the broader source tree, not just debian/."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "nobody_source_hits": ['src/daemon.c:42:    setuser("nobody");'],
        "nobody_source_files": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "nobody" in result.message.lower()


def test_urf_4_nobody_in_tests_is_ignored():
    """A 'nobody' hit under a test path does not trip URF-4."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "nobody_source_hits": ['tests/test_user.c:5:    run_as("nobody");'],
        "nobody_source_files": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "ok"


def test_urf_5_setgid_binary_in_built_deb():
    """URF-5 flags a setuid/setgid binary found in the built artifacts."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "setuid_setgid_source_hits": [],
        "setuid_setgid_source_files": [],
    }
    ctx.evidence["adapters"]["sbuild"] = {
        "status": "ok",
        "setuid_setgid_binaries": ["myapp/usr/bin/myhelper"],
    }
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_errors": [],
        "lintian_warnings": [],
        "lintian_pedantic": [],
    }

    finding = _make_finding("URF-5", mode="deterministic")
    result = checks.deterministic._check_urf_5(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert result.confidence == "high"
    assert "myhelper" in result.message


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
    """Test SEC-10 when direct PAM runtime library found (libpam0g)."""
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


def test_sec_10_pam_dev_triggers():
    """Test SEC-10 when libpam-dev found (direct PAM development dep)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libpam-dev"],
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
    assert result.confidence == "high"


def test_sec_10_pam_runtime_meta_no_trigger():
    """Test SEC-10 when only system PAM meta-packages present (no direct auth usage)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libpam-runtime", "libpam-modules"],
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


def test_canonical_ok_statement_used_for_single_statement_ev_to_ai():
    """A single-statement ev_to_ai OK finding uses the template wording + rationale."""
    check = {
        "id": "SEC-1",
        "section": "Security",
        "mode": "ev_to_ai",
        "todo_refs": ["TODO: - history of CVEs does not look concerning"],
    }
    finding = _make_finding("SEC-1", mode="ev_to_ai")
    response = {
        "status": "ok",
        "message": "no CVEs anywhere",
        "rationale": "Both trackers report zero CVEs for the package.",
    }
    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "ok"
    assert result.message.startswith("history of CVEs does not look concerning")
    assert "Both trackers report zero CVEs" in result.rationale
    assert result.todo == ""


def test_canonical_ok_statement_skipped_for_placeholder_todo():
    """A placeholder (TBD) template statement falls back to the model message."""
    check = {
        "id": "SUM-3",
        "section": "Summary",
        "mode": "ev_to_ai",
        "todo_refs": ["TODO: List of binary packages to be promoted: TBD"],
    }
    finding = _make_finding("SUM-3", mode="ev_to_ai")
    response = {
        "status": "ok",
        "message": "libgav1-2 is the sole promotion candidate",
        "rationale": "The reporter lists only libgav1-2.",
    }
    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "ok"
    # Summary section is excluded from canonical substitution.
    assert result.message.startswith("libgav1-2 is the sole promotion candidate")


def test_selected_option_ok_sets_template_statement():
    """An ev_to_ai option with outcome ok renders its canonical statement, no TODO."""
    check = {
        "id": "PRF-1",
        "section": "Packaging red flags",
        "mode": "ev_to_ai",
        "options": [
            {
                "id": "PRF-1-B",
                "todo_ref": "TODO-B",
                "render": "- Ubuntu does carry a delta, but it is reasonable and maintenance under control",
                "outcome": "ok",
            },
        ],
    }
    finding = _make_finding("PRF-1", mode="ev_to_ai")
    response = {
        "status": "ok",
        "selected_option": "PRF-1-B",
        "rationale": "The delta only adds autopkgtests (debian/tests).",
    }
    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert result.message.startswith(
        "Ubuntu does carry a delta, but it is reasonable and maintenance under control"
    )
    assert "only adds autopkgtests" in result.rationale
    assert result.todo == ""


def test_selected_option_matches_by_todo_ref():
    """The model may name an option by its todo_ref instead of its id."""
    check = {
        "id": "ESL-11",
        "section": "Embedded sources and static linking",
        "mode": "ev_to_ai",
        "options": [
            {
                "id": "ESL-11-B",
                "todo_ref": "TODO-B",
                "render": "- Does not include vendored code",
                "outcome": "ok",
            },
        ],
    }
    finding = _make_finding("ESL-11", mode="ev_to_ai")
    response = {"status": "ok", "selected_option": "TODO-B", "rationale": "Only test-only dirs."}
    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "ok"
    assert result.message.startswith("Does not include vendored code")


def test_urf_8_option_not_ui_renders_template_statement():
    """URF-8 (ev_to_ai): selecting the not-UI option yields the template line."""
    check = {
        "id": "URF-8",
        "section": "Upstream red flags",
        "mode": "ev_to_ai",
        "options": [
            {
                "id": "URF-8-A",
                "todo_ref": "TODO-A",
                "render": "- not part of the UI for extra checks",
                "outcome": "ok",
            },
            {
                "id": "URF-8-C",
                "todo_ref": "TODO-B",
                "render": "- part of the UI but no valid .desktop file is shipped",
                "outcome": "required",
            },
        ],
    }
    finding = _make_finding("URF-8", mode="ev_to_ai")
    response = {
        "status": "ok",
        "selected_option": "URF-8-A",
        "rationale": "libgav1 is a codec library with a CLI helper, not a desktop program.",
    }
    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert result.message.startswith("not part of the UI for extra checks")
    assert result.todo == ""


def test_urf_8_option_missing_desktop_is_required():
    """URF-8: a desktop program without a .desktop file is a required TODO."""
    check = {
        "id": "URF-8",
        "section": "Upstream red flags",
        "mode": "ev_to_ai",
        "options": [
            {
                "id": "URF-8-B",
                "todo_ref": "TODO-B",
                "render": "- part of the UI, desktop file is ok",
                "outcome": "ok",
            },
            {
                "id": "URF-8-C",
                "todo_ref": "TODO-B",
                "render": "- part of the UI but no valid .desktop file is shipped",
                "outcome": "required",
            },
        ],
    }
    finding = _make_finding("URF-8", mode="ev_to_ai")
    response = {
        "status": "not-ok",
        "selected_option": "URF-8-C",
        "rationale": "GTK app but ships no .desktop file.",
    }
    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert result.todo.startswith("TODO:")
    assert "no valid .desktop" in result.todo


def test_urf_9_option_not_user_visible_needs_no_translation():
    """URF-9 (ev_to_ai): not-user-visible option resolves ok without a TODO."""
    check = {
        "id": "URF-9",
        "section": "Upstream red flags",
        "mode": "ev_to_ai",
        "options": [
            {
                "id": "URF-9-A",
                "todo_ref": "TODO-A",
                "render": "- no translation present, but none needed for this case (not user visible)",
                "outcome": "ok",
            },
            {
                "id": "URF-9-C",
                "todo_ref": "TODO-B",
                "render": "- user-visible but no translations are present",
                "outcome": "recommended",
            },
        ],
    }
    finding = _make_finding("URF-9", mode="ev_to_ai")
    response = {
        "status": "ok",
        "selected_option": "URF-9-A",
        "rationale": "A shared library exposes no user-facing strings.",
    }
    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not user visible" in result.message.lower()
    assert result.todo == ""


def _cb5_ctx_with_cb4(cb4_status):
    """Build a ctx whose findings already contain a CB-4 result."""
    ctx = _Ctx()
    ctx.catalog["checks"].append(
        {
            "id": "CB-5",
            "section": "Common blockers",
            "title": "Special hardware compromise accepted",
            "mode": "deterministic",
            "messages": {
                "ok_message": "no special hardware needed, so there is no compromise to accept",
                "human_only_message": "Human review required",
                "human_only_todo": "TODO: - {title} - reviewer judgment needed",
            },
        }
    )
    ctx.findings = [
        Finding(
            id="CB-4",
            section="Common blockers",
            title="Special hardware: requirement and coverage plan",
            mode="ev_to_ai",
            status=cb4_status,
            severity="ok" if cb4_status == "ok" else "recommended",
            confidence="medium",
            message="",
        )
    ]
    return ctx


def test_cb_5_ok_when_cb4_needs_no_special_hw():
    """CB-5 resolves ok (no TODO) when CB-4 concluded no special hardware is needed."""
    ctx = _cb5_ctx_with_cb4("ok")
    finding = _make_finding("CB-5", mode="deterministic")
    result = checks.deterministic._check_cb_5(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert result.todo == ""


def test_cb_5_needs_judgment_when_cb4_not_ok():
    """CB-5 asks for reviewer judgment only when CB-4 did not clear special HW."""
    ctx = _cb5_ctx_with_cb4("not-ok")
    finding = _make_finding("CB-5", mode="deterministic")
    result = checks.deterministic._check_cb_5(ctx, finding)

    assert result.status == "unknown"
    assert result.todo.startswith("TODO:")
    assert "reviewer judgment needed" in result.todo


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


def test_synthesis_checks_evaluated_last(monkeypatch):
    """Synthesis checks run after all others and see the accumulated findings.

    The returned list still preserves catalog order so rendering/Summary
    placement is unaffected.
    """
    from types import SimpleNamespace

    order = []
    synthesis_seen = {}

    def normal_eval(check, ctx, finding):
        order.append(check["id"])
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = f"msg {check['id']}"
        return finding

    def synth_eval(check, ctx, finding):
        order.append(check["id"])
        synthesis_seen[check["id"]] = [f.id for f in ctx.findings]
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "synthesis"
        return finding

    monkeypatch.setattr(checks, "_ensure_evaluators_registered", lambda: None)
    monkeypatch.setitem(checks.EVALUATORS, "tnorm", normal_eval)
    monkeypatch.setitem(checks.EVALUATORS, "tsyn", synth_eval)

    ctx = SimpleNamespace(
        catalog={
            "checks": [
                {"id": "A-1", "mode": "tnorm", "section": "Summary"},
                {"id": "SUM-X", "mode": "tsyn", "section": "Summary", "synthesis": True},
                {"id": "B-1", "mode": "tnorm", "section": "Dependencies"},
            ]
        },
        evidence={},
        findings=[],
    )

    result = checks.evaluate_checks(ctx)

    # Synthesis check evaluated last, after both non-synthesis checks.
    assert order == ["A-1", "B-1", "SUM-X"]
    # Returned list preserves catalog order.
    assert [f.id for f in result] == ["A-1", "SUM-X", "B-1"]
    # Synthesis check saw the accumulated non-synthesis findings via ctx.findings.
    assert synthesis_seen["SUM-X"] == ["A-1", "B-1"]


def test_summarise_findings_so_far_respects_message_cap():
    """The per-finding message cap is honoured and overridable for synthesis."""
    from types import SimpleNamespace

    ctx = SimpleNamespace(
        findings=[
            Finding(
                id="X-1",
                section="Summary",
                title="t",
                mode="deterministic",
                status="not-ok",
                severity="required",
                message="y" * 5000,
            )
        ]
    )

    default = checks.llm_eval._summarise_findings_so_far(ctx)
    assert len(default[0]["message"]) == checks.llm_eval._DEFAULT_FINDING_MESSAGE_CHARS

    synth = checks.llm_eval._summarise_findings_so_far(
        ctx, max_message_len=checks.llm_eval._SYNTHESIS_FINDING_MESSAGE_CHARS
    )
    assert len(synth[0]["message"]) == checks.llm_eval._SYNTHESIS_FINDING_MESSAGE_CHARS


def test_combined_language_gate_suppresses_umbrella_message():
    """A combined 'go|rust' gate must not emit a redundant umbrella OK line."""
    from types import SimpleNamespace

    import checks

    ctx = SimpleNamespace(
        evidence={"adapters": {"packaging-source": {"status": "ok"}}},
    )
    check = {
        "id": "ESL-1",
        "section": "Embedded sources and static linking",
        "title": "No embedded source present",
        "mode": "ev_to_ai",
        "language_gate": "go|rust",
    }

    finding = checks._evaluate_single_check(check, ctx)

    assert finding.status == "ok"
    assert finding.message == ""


def test_single_language_gate_still_emits_message():
    """A single-language gate keeps its specific 'not a <lang> package' line."""
    from types import SimpleNamespace

    import checks

    ctx = SimpleNamespace(
        evidence={"adapters": {"packaging-source": {"status": "ok"}}},
    )
    check = {
        "id": "ESL-4",
        "section": "Embedded sources and static linking",
        "title": "Go gate",
        "mode": "ev_to_ai",
        "language_gate": "go",
    }

    finding = checks._evaluate_single_check(check, ctx)

    assert finding.status == "ok"
    assert finding.message == "not a go package, no extra constraints to consider in that regard"


def test_extract_build_test_hints_detects_wiring():
    hints = checks.llm_eval._extract_build_test_hints(
        "override_dh_auto_test:\n\tmake check\n",
        "Running tests\n5 passed\n",
    )
    assert hints["rules_has_test_wiring"] is True
    assert "make check" in hints["rules_test_runners"]
    assert hints["build_log_runs_tests"] is True
    assert hints["build_log_has_pass_fail"] is True
    assert hints["failures_possibly_ignored"] is False


def test_extract_build_test_hints_no_tests():
    hints = checks.llm_eval._extract_build_test_hints(
        "%:\n\tdh $@\n",
        "dh_auto_build\n",
    )
    assert hints["rules_has_test_wiring"] is False
    assert hints["rules_test_runners"] == []


def test_extract_build_test_hints_failures_ignored():
    hints = checks.llm_eval._extract_build_test_hints(
        "override_dh_auto_test:\n\tmake check || true\n",
        "",
    )
    assert hints["failures_possibly_ignored"] is True


# ---------------------------------------------------------------------------
# CB-3 autopkgtest detection: both evidence sources reach the model (feedback #1)
# ---------------------------------------------------------------------------


class _EvCtx:
    """Minimal ctx for exercising _build_evidence_payload."""

    def __init__(self, adapters):
        self.source_package = "libgav1"
        self.bug_id = "2158712"
        self.series = "devel"
        self.bug = {"title": "[MIR] libgav1"}
        self.reporter_mir_content = ""
        self.findings = []
        self.untrusted_nonce = "NONCE"
        self.evidence = {"adapters": adapters}


def test_cb3_payload_includes_autopkgtest_and_tests_control():
    """CB-3 must receive the autopkgtest DB result AND the full debian/tests/control
    so the model can credit a passing autopkgtest even though it judges non-triviality."""
    control = "Tests: decode\nDepends: libgav1-bin\nRestrictions: allow-stderr\n"
    ctx = _EvCtx(
        {
            "packaging-source": {
                "status": "ok",
                "debian_tests_control": control,
                "debian_control": "Source: libgav1",
                "file_listing": [],
            },
            "autopkgtest-db": {
                "status": "ok",
                "has_autopkgtest": True,
                "passing_arches": ["amd64", "arm64", "armhf", "ppc64el", "s390x"],
                "failing_arches": [],
            },
        }
    )
    check = {
        "id": "CB-3",
        "section": "Common blockers",
        "mode": "ev_to_ai",
        "adapters_required": ["packaging-source", "autopkgtest-db"],
    }
    payload = checks.llm_eval._build_evidence_payload(check, ctx)

    # debian/tests/control is kept verbatim (declares the functional 'decode' test).
    assert payload["packaging-source"]["debian_tests_control"] == control
    # The authoritative pass/fail signal is present.
    assert payload["autopkgtest-db"]["has_autopkgtest"] is True
    assert "s390x" in payload["autopkgtest-db"]["passing_arches"]
    assert payload["autopkgtest-db"]["failing_arches"] == []

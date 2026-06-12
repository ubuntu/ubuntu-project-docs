"""Type definitions for evidence adapter return values.

These TypedDict definitions document the expected structure of data returned
by each evidence adapter. They serve as contracts between adapters (producers)
and check evaluators (consumers).

Usage:
    from evidence.types import DepAnalysisResult, PackagingSourceResult

    def _collect_dep_analysis(ctx) -> DepAnalysisResult:
        ...
"""

from __future__ import annotations

from typing import Any, TypedDict


# ---------------------------------------------------------------------------
# Host-side adapters — LP API
# ---------------------------------------------------------------------------


class LPBugAPIResult(TypedDict):
    """Return structure for lp-bug-api adapter."""

    status: str  # "ok" | "error" | "pending"
    bug_id: str
    bug_title: str
    bug_description: str
    bug_tags: list[str]
    bug_comments: list[str]
    bug_subscribers: list[str]
    target_source_package: str
    target_series: str
    mir_heuristics: dict[str, bool]


class LPTeamMembershipAPIResult(TypedDict):
    """Return structure for lp-team-membership-api adapter."""

    status: str
    subscribers: list[str]
    ubuntu_mir_subscribed: bool


class PublishHistoryEntry(TypedDict):
    """Single entry in Ubuntu publishing history."""

    version: str
    date_published: str
    pocket: str
    component: str
    status: str


class UploadHistoryEntry(TypedDict):
    """Single entry in upload history."""

    version: str
    date_created: str
    status: str
    uploader: str


class LPPackageAPIResult(TypedDict):
    """Return structure for lp-package-api adapter."""

    status: str
    ubuntu_publish_history: list[PublishHistoryEntry]
    current_version: str
    upload_history: list[UploadHistoryEntry]
    uploaders: list[str]


# ---------------------------------------------------------------------------
# Host-side adapters — CVE / security
# ---------------------------------------------------------------------------


class CVEEntry(TypedDict):
    """Single CVE entry."""

    id: str
    status: str
    fix_version: str


class UbuntuCVETrackerResult(TypedDict):
    """Return structure for ubuntu-cve-tracker adapter."""

    status: str
    package: str
    series: str
    cves: list[CVEEntry]
    active_cves: list[str]
    fixed_cves: list[str]
    total_cve_count: int


# ---------------------------------------------------------------------------
# Host-side adapters — autopkgtest
# ---------------------------------------------------------------------------


class TestResultEntry(TypedDict):
    """Single autopkgtest result entry."""

    arch: str
    version: str
    status: str
    date: str


class AutopkgtestResult(TypedDict):
    """Return structure for autopkgtest-db adapter."""

    status: str
    package: str
    series: str
    has_autopkgtest: bool
    test_results: list[TestResultEntry]
    passing_arches: list[str]
    failing_arches: list[str]


# ---------------------------------------------------------------------------
# In-container adapters — packaging source
# ---------------------------------------------------------------------------


class PackagingSourceResult(TypedDict):
    """Return structure for packaging-source adapter."""

    status: str
    source_dir: str
    debian_control: str
    debian_rules: str
    cargo_lock_present: bool
    go_sum_present: bool
    vendored_dirs: list[str]


# ---------------------------------------------------------------------------
# In-container adapters — dependency analysis
# ---------------------------------------------------------------------------


class RuntimeDepEntry(TypedDict):
    """Single runtime dependency entry."""

    binary: str
    depends: str


class DepComponentEntry(TypedDict):
    """Dependency component classification."""

    package: str
    component: str  # "main" | "universe" | "restricted" | "multiverse" | "unknown"


class DepSourceEntry(TypedDict):
    """Dependency source package mapping."""

    package: str
    source_package: str


class DepSourceEntry(TypedDict):
    """Dependency source package mapping."""

    package: str
    source_package: str


class DepAnalysisResult(TypedDict):
    """Return structure for dep-analysis adapter."""

    status: str
    binary_packages: list[str]
    built_packages: list[str]
    runtime_deps: list[RuntimeDepEntry]
    runtime_dep_packages: list[str]
    dep_components: list[DepComponentEntry]
    dep_source_map: list[DepSourceEntry]
    deps_not_in_main: list[str]
    in_scope_deps_not_in_main: list[str]
    out_of_scope_deps_not_in_main: list[str]
    same_source_deps: list[str]
    in_scope_deps_not_in_main: list[str]
    out_of_scope_deps_not_in_main: list[str]
    same_source_deps: list[str]


# ---------------------------------------------------------------------------
# In-container adapters — component mismatches
# ---------------------------------------------------------------------------


class ComponentMismatchesResult(TypedDict):
    """Return structure for component-mismatches adapter."""

    status: str
    series: str
    raw_output: str
    promotion_candidates: list[str]


# ---------------------------------------------------------------------------
# In-container adapters — sbuild
# ---------------------------------------------------------------------------


class SbuildResult(TypedDict):
    """Return structure for sbuild adapter (real build with unshare backend)."""

    status: str
    message: str
    build_success: bool
    build_log: str
    built_debs: list[str]
    lintian_output: str
    lintian_errors: list[str]
    lintian_warnings: list[str]
    lintian_pedantic: list[str]
    static_link_hints: list[str]
    note: str

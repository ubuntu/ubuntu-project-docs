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

from typing import TypedDict

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


class LPBugSearchEntry(TypedDict):
    """Single Launchpad package bug entry."""

    id: str
    title: str
    status: str
    importance: str
    date_created: str
    web_link: str
    tags: list[str]


class LPBugSearchAPIResult(TypedDict):
    """Return structure for lp-bug-search-api adapter."""

    status: str
    source_package: str
    open_bugs: list[LPBugSearchEntry]
    critical_bugs: list[LPBugSearchEntry]
    security_bugs: list[LPBugSearchEntry]
    total_open_bug_count: int


class DebianBTSBugEntry(TypedDict):
    """Single Debian BTS bug entry."""

    id: str
    title: str
    severity: str
    status: str
    tags: list[str]
    web_link: str


class DebianBTSResult(TypedDict):
    """Return structure for debian-bts adapter."""

    status: str
    source_package: str
    open_bugs: list[DebianBTSBugEntry]
    rc_bugs: list[DebianBTSBugEntry]
    security_bugs: list[DebianBTSBugEntry]
    total_open_bug_count: int


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
    all_publish_history: list[PublishHistoryEntry]
    release_cadence: dict
    current_version: str
    upload_history: list[UploadHistoryEntry]
    uploaders: list[str]


class LPBuildEntry(TypedDict):
    """Single Launchpad build-state entry."""

    arch_tag: str
    build_state: str
    build_reason: str
    version: str
    date_created: str
    pocket: str
    archive: str


class LPBuildAPIResult(TypedDict):
    """Return structure for lp-build-api adapter."""

    status: str
    source_package: str
    series: str
    builds: list[LPBuildEntry]


class UpstreamReleaseEntry(TypedDict):
    """Single upstream release entry."""

    version: str


class UpstreamTrackerResult(TypedDict):
    """Return structure for upstream-tracker adapter."""

    status: str
    upstream_url: str
    latest_version: str
    open_issues_count: int
    recent_releases: list[UpstreamReleaseEntry]
    last_release_date: str


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


class CVESearchTerm(TypedDict):
    """A single candidate search term for CVE lookups.

    kind distinguishes the current package/project ("current") from historical
    predecessors or sibling versions worth checking ("predecessor").
    """

    term: str
    kind: str
    rationale: str


class CVESearchTermsResult(TypedDict):
    """Return structure for cve-search-terms adapter."""

    status: str
    source_package: str
    terms: list[CVESearchTerm]


class CvelistCandidate(TypedDict):
    """A candidate CVE identified by scanning the cvelistV5 baseline corpus."""

    id: str
    matched_term: str
    matched_kind: str
    title: str
    description: str
    affected_products: list[str]
    affected_versions: list[str]
    references: list[str]
    severity: str
    published_date: str


class CvelistScanResult(TypedDict):
    """Return structure for cvelist-scan adapter (runs inside the VM)."""

    status: str
    source_package: str
    baseline: str
    scanned_terms: list[str]
    candidates: list[CvelistCandidate]
    total_candidate_count: int


class NvdEnrichedCVE(TypedDict):
    """A CVE enriched with NVD metadata (or cvelist fallback data)."""

    id: str
    kind: str
    title: str
    description: str
    severity: str
    cvss_score: float
    cwe: list[str]
    affected_versions: list[str]
    affected_products: list[str]
    enrichment_source: str
    web_link: str


class NvdEnrichResult(TypedDict):
    """Return structure for nvd-enrich adapter."""

    status: str
    source_package: str
    cves: list[NvdEnrichedCVE]
    high_severity_cves: list[NvdEnrichedCVE]
    historical_cves: list[NvdEnrichedCVE]
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


class FileListingEntry(TypedDict):
    """Single file entry from source tree listing."""

    path: str
    size: int


class PackagingSourceResult(TypedDict):
    """Return structure for packaging-source adapter."""

    status: str
    source_dir: str
    source_workdir: str
    debian_control: str
    debian_watch: str
    debian_rules: str
    cargo_lock_present: bool
    go_sum_present: bool
    vendored_dirs: list[str]
    file_listing: list[FileListingEntry]
    nobody_source_hits: list[str]
    setuid_setgid_source_hits: list[str]
    nobody_source_files: list[str]
    setuid_setgid_source_files: list[str]


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


class AutoIncludedDepByBinaryEntry(TypedDict):
    """Offending dependencies for an auto-included binary package."""

    binary: str
    dependencies: list[str]


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
    auto_included_binaries: list[str]
    auto_included_dep_components: list[DepComponentEntry]
    auto_included_deps_not_in_main_or_unknown: list[str]
    auto_included_offending_deps_by_binary: list[AutoIncludedDepByBinaryEntry]


# ---------------------------------------------------------------------------
# In-container adapters — component mismatches
# ---------------------------------------------------------------------------


class ComponentMismatchesResult(TypedDict):
    """Return structure for component-mismatches adapter."""

    status: str
    series: str
    raw_output: str
    promotion_candidates: list[str]


class UbuntuUploadPermissionResult(TypedDict):
    """Return structure for ubuntu-upload-permission adapter."""

    status: str
    raw_output: str
    components: list[str]
    team_uploaders: list[dict]
    individual_uploaders: list[dict]


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
    static_binaries: list[str]
    setuid_setgid_binaries: list[str]
    nobody_owned_binaries: list[str]
    note: str


class LintianResult(TypedDict):
    """Return structure for lintian adapter."""

    status: str
    lintian_output: str
    lintian_errors: list[str]
    lintian_warnings: list[str]
    lintian_pedantic: list[str]


class DebMetadataEntry(TypedDict):
    """Metadata extracted from a single binary .deb package."""

    package: str
    version: str
    built_using: list[str]  # Parsed Built-Using entries (multi-line collapsed)
    static_built_using: list[str]  # Parsed Static-Built-Using entries


class DebMetadataResult(TypedDict):
    """Return structure for deb-metadata adapter.

    Extracts metadata from built .deb files after sbuild completes.
    Provides structured access to Built-Using, Static-Built-Using, etc.
    """

    status: str
    message: str
    deb_packages: list[DebMetadataEntry]

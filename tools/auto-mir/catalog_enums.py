"""Enum definitions for catalog identifiers.

These enums provide type safety for adapter and check IDs, catching typos
at development time rather than runtime.
"""

from enum import StrEnum


class AdapterID(StrEnum):
    """Evidence adapter identifiers.

    These must match the adapter IDs defined in catalog.yaml.
    """

    # Host-side adapters
    LP_BUG_API = "lp-bug-api"
    LP_BUG_SEARCH_API = "lp-bug-search-api"
    LP_TEAM_MEMBERSHIP_API = "lp-team-membership-api"
    LP_PACKAGE_API = "lp-package-api"
    LP_BUILD_API = "lp-build-api"
    UPSTREAM_TRACKER = "upstream-tracker"
    UBUNTU_CVE_TRACKER = "ubuntu-cve-tracker"
    AUTOPKGTEST_DB = "autopkgtest-db"
    TEAM_MAPPING = "team-mapping"
    DEBIAN_BTS = "debian-bts"
    CVE_SEARCH_TERMS = "cve-search-terms"
    NVD_ENRICH = "nvd-enrich"
    LTO_DISABLED_LIST = "lto-disabled-list"

    # In-container adapters
    PACKAGING_SOURCE = "packaging-source"
    DEP_ANALYSIS = "dep-analysis"
    COMPONENT_MISMATCHES = "component-mismatches"
    SBUILD = "sbuild"
    LINTIAN = "lintian"
    DEB_METADATA = "deb-metadata"
    CVELIST_SCAN = "cvelist-scan"
    UBUNTU_UPLOAD_PERMISSION = "ubuntu-upload-permission"
    GIT_UBUNTU_DELTA = "git-ubuntu-delta"


class CheckID(StrEnum):
    """Check identifiers.

    These must match the check IDs defined in catalog.yaml.
    Note: This is a partial list of the most commonly referenced checks.
    """

    # Summary checks
    SUM_1 = "SUM-1"
    SUM_2 = "SUM-2"
    SUM_3 = "SUM-3"
    SUM_4 = "SUM-4"
    SUM_5 = "SUM-5"
    SUM_6 = "SUM-6"

    # Rationale, Duplication, Ownership checks
    RDO_1 = "RDO-1"
    RDO_2 = "RDO-2"
    RDO_3 = "RDO-3"

    # Dependencies checks
    DEP_1 = "DEP-1"
    DEP_2 = "DEP-2"
    DEP_3 = "DEP-3"
    DEP_4 = "DEP-4"

    # Embedded sources and static linking checks
    ESL_1 = "ESL-1"
    ESL_2 = "ESL-2"
    ESL_3 = "ESL-3"
    ESL_4 = "ESL-4"
    ESL_5 = "ESL-5"
    ESL_6 = "ESL-6"
    ESL_7 = "ESL-7"
    ESL_8 = "ESL-8"
    ESL_9 = "ESL-9"
    ESL_10 = "ESL-10"
    ESL_11 = "ESL-11"

    # Security checks
    SEC_1 = "SEC-1"
    SEC_2 = "SEC-2"
    SEC_3 = "SEC-3"
    SEC_4 = "SEC-4"
    SEC_5 = "SEC-5"
    SEC_6 = "SEC-6"
    SEC_7 = "SEC-7"
    SEC_8 = "SEC-8"
    SEC_9 = "SEC-9"
    SEC_10 = "SEC-10"
    SEC_11 = "SEC-11"

    # Common blockers checks
    CB_1 = "CB-1"
    CB_2 = "CB-2"
    CB_3 = "CB-3"
    CB_4 = "CB-4"
    CB_5 = "CB-5"
    CB_6 = "CB-6"
    CB_7 = "CB-7"
    CB_8 = "CB-8"
    CB_9 = "CB-9"

    # Packaging red flags checks
    PRF_1 = "PRF-1"
    PRF_2 = "PRF-2"
    PRF_3 = "PRF-3"
    PRF_4 = "PRF-4"
    PRF_5 = "PRF-5"
    PRF_6 = "PRF-6"
    PRF_7 = "PRF-7"
    PRF_8 = "PRF-8"
    PRF_9 = "PRF-9"
    PRF_10 = "PRF-10"

    # Upstream red flags checks
    URF_1 = "URF-1"
    URF_2 = "URF-2"
    URF_3 = "URF-3"
    URF_4 = "URF-4"
    URF_5 = "URF-5"
    URF_6 = "URF-6"
    URF_7 = "URF-7"
    URF_8 = "URF-8"
    URF_9 = "URF-9"

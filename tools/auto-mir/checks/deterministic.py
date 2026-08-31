"""Deterministic check evaluators for auto-mir.

Contains all check functions that evaluate evidence without LLM calls,
the dispatch table, and the _eval_deterministic entry point.
"""

from __future__ import annotations

import logging
import re
import subprocess
from typing import TYPE_CHECKING, Callable

from checks.language_gates import _is_go_package, _is_python_package, _is_rust_package
from checks.messages import render_check_message
from models import Finding

if TYPE_CHECKING:
    from auto_mir import RunContext

log = logging.getLogger("auto_mir.checks.deterministic")


def _get_check_definition(ctx: RunContext, check_id: str) -> dict:
    """Return check definition by id or raise a clear error."""
    check = next((c for c in ctx.catalog.get("checks", []) if c.get("id") == check_id), None)
    if check is None:
        raise ValueError(f"{check_id} check definition not found in catalog")
    return check


def _set_unknown_from_adapter(
    finding: Finding,
    check: dict,
    *,
    message_key: str = "unknown_message",
    todo_key: str | None = None,
    severity: str = "ok",
    evidence_refs: list[str] | None = None,
) -> Finding:
    """Set finding to unknown with consistent confidence and optional TODO/evidence."""
    message = render_check_message(check, message_key)
    finding.mark_unknown(
        message=message,
        todo=render_check_message(check, todo_key) if todo_key else "",
        severity=severity,
        confidence="low",
    )
    if evidence_refs is not None:
        finding.evidence_refs = evidence_refs
    return finding


def _get_packaging_source_or_unknown(
    ctx: RunContext,
    finding: Finding,
    check_id: str,
    *,
    with_unknown_todo: bool = True,
) -> tuple[dict, dict] | None:
    """Return (check, packaging-source) or set finding unknown and return None."""
    check = _get_check_definition(ctx, check_id)
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})
    if packaging.get("status") != "ok":
        _set_unknown_from_adapter(
            finding,
            check,
            todo_key="unknown_todo" if with_unknown_todo else None,
        )
        return None
    return check, packaging


_TEST_CONTEXT_MARKERS = (
    "test",
    "tests/",
    "autopkgtest",
    "pytest",
    "unittest",
    "debian/tests",
)


def _line_is_test_context(line: str) -> bool:
    """Return True when a source line clearly belongs to test context."""
    lowered = line.lower()
    return any(marker in lowered for marker in _TEST_CONTEXT_MARKERS)


def _path_is_test_context(path: str) -> bool:
    """Return True when a file path lives under a test directory."""
    marked = f"/{str(path).lower().lstrip('./')}"
    return "/test/" in marked or "/tests/" in marked or "/debian/tests/" in marked


# Documentation / plain-text file extensions. A grep match for a privilege
# keyword inside one of these is prose or sample output (e.g. an example of what
# console output looks like), not active code, so it carries no security risk.
_NONEXECUTABLE_DOC_EXTENSIONS = (
    ".txt",
    ".md",
    ".markdown",
    ".rst",
    ".rdoc",
    ".html",
    ".htm",
    ".pod",
    ".adoc",
    ".asciidoc",
    ".texi",
    ".tex",
    ".org",
    ".rtf",
)
# Extensionless conventional documentation files found at the top of source
# trees. Matched by exact basename only so code such as ``license_check.py`` is
# never misclassified.
_NONEXECUTABLE_DOC_BASENAMES = (
    "readme",
    "news",
    "changelog",
    "changes",
    "authors",
    "contributors",
    "copying",
    "license",
    "licence",
    "notice",
    "thanks",
    "todo",
    "install",
)
# Manpage (roff) sources: section digit 1-9, optionally with a locale/suffix
# (e.g. ``.3pm``, ``.1p``). These are documentation, not executables.
_MANPAGE_SUFFIX_RE = re.compile(r"\.[1-9][a-z]*$")

# Code/script extensions. When the last extension of a basename is in this set,
# the file is executable code and is never classified as a doc, even if a
# dot-separated component happens to match a doc basename (e.g. ``install.sh``).
_CODE_EXTENSIONS = frozenset(
    {
        ".py",
        ".sh",
        ".bash",
        ".pl",
        ".rb",
        ".js",
        ".ts",
        ".c",
        ".cc",
        ".cpp",
        ".cxx",
        ".h",
        ".hpp",
        ".go",
        ".rs",
        ".java",
        ".lua",
        ".php",
        ".tcl",
        ".awk",
        ".sed",
        ".vala",
        ".swift",
        ".kt",
        ".scala",
        ".r",
        ".jl",
        ".ex",
        ".exs",
        ".erl",
        ".hs",
        ".ml",
        ".nim",
        ".cr",
        ".d",
        ".zig",
        ".pas",
        ".pp",
        ".f",
        ".f90",
        ".f95",
        ".for",
        ".asm",
        ".s",
        ".S",
    }
)


def _grep_hit_path(hit: str) -> str:
    """Return the file-path portion of a ``path:lineno:content`` grep hit."""
    match = re.match(r"^(?P<path>.+?):\d+:", hit)
    if match:
        return match.group("path")
    return hit.split(":", 1)[0]


def _path_is_nonexecutable_doc(path: str) -> bool:
    """Return True when a path is a non-executable documentation/text file.

    The classification is by file type, not directory: a plain-text or
    documentation file can *mention* privilege keywords (in prose or sample
    output) without shipping active code, whereas a script or source file named
    ``foo_example.py`` is still executable code and is not matched here.
    """
    name = str(path).strip().lstrip("./").rsplit("/", 1)[-1].lower()
    if not name:
        return False
    if "." not in name:
        return name in _NONEXECUTABLE_DOC_BASENAMES
    if _MANPAGE_SUFFIX_RE.search(name):
        return True
    ext = "." + name.rsplit(".", 1)[-1]
    if ext in _NONEXECUTABLE_DOC_EXTENSIONS:
        return True
    # Debian ships conventional documentation as compound basenames such as
    # ``mysql-server.README.Debian`` or ``README.source``. The last extension
    # (``.Debian`` / ``.source``) is not in the doc-extensions list, but a
    # dot-separated component (``readme``) is a known doc basename. Matching any
    # component catches these without misclassifying code: a file like
    # ``install.sh`` whose last extension is a code/script extension is never
    # softened, even though ``install`` is a doc basename.
    if ext in _CODE_EXTENSIONS:
        return False
    components = name.split(".")
    if len(components) > 1 and any(c in _NONEXECUTABLE_DOC_BASENAMES for c in components):
        return True
    return False


# Pattern that identifies a genuine reference to the Unix user 'nobody' in
# source code, as opposed to the English pronoun "nobody" used in comments or
# prose. Real references always appear in a code context: quoted strings,
# assignments, chown-style expressions, privilege-dropping function calls, or
# CLI flags. The bare word "nobody" in a comment ("nobody else can read") never
# matches because it lacks these markers.
_NOBODY_USER_REF_RE = re.compile(
    r'["\']nobody["\']'  # "nobody" / 'nobody' (quoted string literal)
    r"|nobody\s*:\s*\w"  # nobody:group (chown-style colon syntax)
    r"|\buser\s*[:=]\s*nobody\b"  # user=nobody, User=nobody (assignment)
    r"|\b(?:chown|chuid|su|runuser)\b[^;]*\bnobody\b"  # chown/chuid/su/runuser ... nobody
    r"|\b(?:setuid|setgid|setuser|getpwnam|initgroups)\b[^;]*\bnobody\b"
    r"|--user\s+nobody\b"  # --user nobody (CLI flag)
    r"|-u\s+nobody\b",  # -u nobody (CLI flag shorthand)
    re.IGNORECASE,
)


def _line_references_nobody_user(line: str) -> bool:
    """Return True when a grep hit references the Unix user 'nobody'.

    Filters out the English pronoun "nobody" in comments and prose (e.g.
    "nobody else can read", "nobody was asleep at that moment"), which is the
    dominant source of false positives in large C/C++ source trees. A genuine
    user reference always appears in a code context: a quoted string literal,
    an assignment, a chown-style expression, a privilege-dropping function call,
    or a CLI flag.
    """
    return bool(_NOBODY_USER_REF_RE.search(line))


# Soname-versioned shared-library runtime package names end in a digit
# (e.g. liblua5.5-0, libfoo1). -dev/-doc/-dbg packages are excluded.
_SHARED_LIB_PKG_RE = re.compile(r"^lib.+\d$")


def _binary_package_names(debian_control: str) -> list[str]:
    """Return the binary package names declared in a debian/control file."""
    names: list[str] = []
    for line in debian_control.splitlines():
        if line.startswith("Package:"):
            names.append(line.split(":", 1)[1].strip())
    return names


def _is_shared_lib_pkg_name(name: str) -> bool:
    """Return True when a binary package name looks like a shared-library package."""
    base = name.strip().lower()
    if base.endswith(("-dev", "-doc", "-dbg", "-dbgsym")):
        return False
    return bool(_SHARED_LIB_PKG_RE.match(base))


def _shared_library_package_names(debian_control: str, built_debs: list[str]) -> list[str]:
    """Return the soname-versioned shared-library package names for a source.

    Combines the binary package names declared in debian/control with the names
    of any built .deb files (more reliable when control packages are generated).
    """
    names: list[str] = []
    for name in _binary_package_names(debian_control):
        if _is_shared_lib_pkg_name(name) and name not in names:
            names.append(name)
    for deb in built_debs:
        deb_name = str(deb).rsplit("/", 1)[-1].split("_", 1)[0]
        if _is_shared_lib_pkg_name(deb_name) and deb_name not in names:
            names.append(deb_name)
    return names


def _check_sum_1(ctx: RunContext, finding: Finding) -> Finding:
    """SUM-1: Source package identified."""
    check = _get_check_definition(ctx, "SUM-1")
    if ctx.source_package:
        finding.succeed(
            render_check_message(check, "ok_message", source_package=ctx.source_package)
        )
        finding.evidence_refs = ["lp-bug-api:source_package"]
    else:
        finding.fail(
            render_check_message(check, "not_ok_message"),
            render_check_message(check, "not_ok_todo"),
            severity="required",
        )
    return finding


def _check_sum_2(ctx: RunContext, finding: Finding) -> Finding:
    """SUM-2: Reporter MIR content present."""
    check = _get_check_definition(ctx, "SUM-2")
    if ctx.reporter_mir_content:
        finding.succeed(render_check_message(check, "ok_message"))
        finding.evidence_refs = ["lp-bug-api:reporter_content"]
    elif str(getattr(ctx, "review_type", "fresh")) in ("rereview", "reorg"):
        finding.succeed(render_check_message(check, "rereview_ok_message"))
    else:
        finding.fail(
            render_check_message(check, "nack_message"),
            render_check_message(check, "nack_todo"),
            severity="nack",
        )
    return finding


def _check_cb_1(ctx: RunContext, finding: Finding) -> Finding:
    """CB-1: Package does not FTBFS currently.

    Purely a Launchpad per-architecture build-state check. fetch-build only
    downloads the local architecture's already-built artifacts for later
    checks (dep-analysis, lintian, ...) - it is not an independent build
    signal, so it plays no part in this verdict.
    """
    adapters = ctx.evidence.get("adapters", {})

    check = _get_check_definition(ctx, "CB-1")
    lp_build_result = adapters.get("lp-build-api", {})

    # Launchpad build records are required to confirm all architectures build.
    if lp_build_result.get("status") != "ok":
        finding.fail(
            render_check_message(check, "unknown_no_lp_message"),
            render_check_message(check, "unknown_no_lp_todo"),
            severity="recommended",
            confidence="low",
            status="unknown",
        )
        finding.evidence_refs = ["lp-build-api:error"]
        return finding

    builds = lp_build_result.get("builds", [])
    if not builds:
        finding.fail(
            render_check_message(check, "unknown_no_builds_message"),
            render_check_message(check, "unknown_no_builds_todo"),
            severity="recommended",
            confidence="low",
            status="unknown",
        )
        finding.evidence_refs = ["lp-build-api:builds"]
        return finding

    failed_builds = []
    passing_arches = []
    for build in builds:
        arch = str(build.get("arch_tag", "")).strip() or "unknown-arch"
        state = str(build.get("build_state", "")).strip().lower()
        if any(token in state for token in ("successful", "succeeded", "built")):
            passing_arches.append(arch)
        else:
            failed_builds.append(f"{arch}: {build.get('build_state', 'unknown')}")

    if failed_builds:
        finding.fail(
            render_check_message(check, "not_ok_message", failed_builds="; ".join(failed_builds)),
            render_check_message(check, "not_ok_todo"),
            severity="required",
            confidence="high",
        )
        finding.evidence_refs = ["lp-build-api:builds"]
        return finding

    success_message = render_check_message(
        check, "ok_message", passing_arches=", ".join(passing_arches)
    )
    finding.succeed(success_message, confidence="high")
    finding.evidence_refs = ["lp-build-api:builds"]
    return finding


def _check_sum_4(ctx: RunContext, finding: Finding) -> Finding:
    """SUM-4: Package has a team subscriber in package-team-mapping."""
    check = _get_check_definition(ctx, "SUM-4")
    adapters = ctx.evidence.get("adapters", {})
    team_mapping_adapter = adapters.get("team-mapping", {})

    if team_mapping_adapter.get("status") != "ok":
        return _set_unknown_from_adapter(
            finding,
            check,
            todo_key="unknown_todo",
            evidence_refs=["team-mapping:error"],
        )

    subscribed_teams = team_mapping_adapter.get("subscribed_teams", [])

    if subscribed_teams:
        finding.succeed(
            render_check_message(check, "ok_message", subscribed_teams=", ".join(subscribed_teams))
        )
    else:
        finding.fail(
            render_check_message(check, "not_ok_message"),
            render_check_message(check, "not_ok_todo"),
            severity="recommended",
        )

    finding.evidence_refs = ["team-mapping:subscribed_teams"]
    return finding


def _check_dep_3(ctx: RunContext, finding: Finding) -> Finding:
    """DEP-3: No -dev/-debug/-doc packages needing exclusion."""
    adapters = ctx.evidence.get("adapters", {})
    check = _get_check_definition(ctx, "DEP-3")

    packaging = adapters.get("packaging-source", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if packaging.get("status") != "ok":
        return _set_unknown_from_adapter(
            finding,
            check,
            message_key="unknown_packaging_message",
            todo_key="unknown_packaging_todo",
        )

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(
            finding,
            check,
            message_key="unknown_dep_analysis_message",
            todo_key="unknown_dep_analysis_todo",
            evidence_refs=["dep-analysis:error"],
        )

    binary_packages = dep_analysis.get("binary_packages", [])

    # Filter to in-scope binaries only
    if ctx.requested_binaries:
        in_scope = [p for p in binary_packages if p in ctx.requested_binaries]
    else:
        in_scope = binary_packages

    auto_included = dep_analysis.get("auto_included_binaries")
    if auto_included is None:
        auto_included = [
            p
            for p in in_scope
            if any(p.endswith(s) for s in ("-dev", "-dbg", "-debug", "-doc", "-docs"))
        ]

    auto_included = sorted(auto_included)
    if not auto_included:
        finding.succeed(render_check_message(check, "ok_no_auto_included_message"))
        finding.evidence_refs = [
            "packaging-source:debian_control",
            "dep-analysis:binary_packages",
        ]
        return finding

    offending_deps = sorted(dep_analysis.get("auto_included_deps_not_in_main_or_unknown", []))
    offending_by_binary = dep_analysis.get("auto_included_offending_deps_by_binary", [])
    offending_by_binary = sorted(
        [
            {
                "binary": str(entry.get("binary", "")),
                "dependencies": sorted(str(d) for d in entry.get("dependencies", [])),
            }
            for entry in offending_by_binary
            if entry.get("binary")
        ],
        key=lambda e: e["binary"],
    )

    same_source_deps = sorted(dep_analysis.get("auto_included_deps_same_source", []))

    if offending_deps:
        details = "; ".join(
            f"{entry['binary']}: {', '.join(entry['dependencies'])}"
            for entry in offending_by_binary
            if entry["dependencies"]
        )
        finding.fail(
            render_check_message(
                check,
                "not_ok_offending_message",
                auto_included=", ".join(auto_included),
                offending_deps=", ".join(offending_deps),
            ),
            render_check_message(
                check,
                "not_ok_offending_todo",
                details=details,
                offending_deps=", ".join(offending_deps),
            ),
            severity="recommended",
        )
    elif same_source_deps:
        # The only "outside main" dependencies of the auto-included binaries are
        # built by this very source package, so they are being promoted by this
        # MIR request too. That is not an offending component mismatch.
        finding.succeed(
            render_check_message(
                check,
                "ok_same_request_message",
                auto_included=", ".join(auto_included),
                same_request_deps=", ".join(same_source_deps),
            )
        )
    else:
        finding.succeed(
            render_check_message(
                check,
                "ok_safe_message",
                auto_included=", ".join(auto_included),
            )
        )

    finding.evidence_refs = [
        "packaging-source:debian_control",
        "dep-analysis:auto_included_binaries",
        "dep-analysis:auto_included_dep_components",
        "dep-analysis:auto_included_deps_not_in_main_or_unknown",
        "dep-analysis:auto_included_offending_deps_by_binary",
        "dep-analysis:auto_included_deps_same_source",
    ]
    return finding


def _check_esl_3(ctx: RunContext, finding: Finding) -> Finding:
    """ESL-3: No unexpected Built-Using entries.

    Checks Built-Using and Static-Built-Using metadata from built .deb files
    (not source debian/control, which doesn't have these fields).
    """
    check = _get_check_definition(ctx, "ESL-3")

    adapters = ctx.evidence.get("adapters", {})
    deb_metadata = adapters.get("deb-metadata", {})

    if deb_metadata.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check, todo_key="unknown_todo")

    deb_packages = deb_metadata.get("deb_packages", [])

    # Collect all Built-Using and Static-Built-Using entries from all packages
    all_built_using = []
    all_static_built_using = []

    for pkg in deb_packages:
        all_built_using.extend(pkg.get("built_using", []))
        all_static_built_using.extend(pkg.get("static_built_using", []))

    # Combine and deduplicate for analysis
    all_entries = sorted(set(all_built_using + all_static_built_using))

    if not all_entries:
        finding.succeed(render_check_message(check, "ok_message"))
        finding.evidence_refs = ["deb-metadata:deb_packages"]
        return finding

    # Check for toolchain-only pattern (acceptable) vs. other entries
    all_entries_text = " ".join(all_entries).lower()
    # Toolchain-only Built-Using (golang, rust, cgo) are expected.
    # Anything else (especially ${misc:Built-Using} with explicit pkg list) needs attention.
    entries_joined = "; ".join(all_entries)
    if (
        "golang" in all_entries_text
        or "rust" in all_entries_text
        or "${misc:built-using}" in all_entries_text
    ):
        finding.succeed(
            render_check_message(check, "ok_toolchain_message", entries=entries_joined),
            confidence="medium",
        )
    else:
        finding.fail(
            render_check_message(check, "not_ok_message", entries=entries_joined),
            render_check_message(check, "not_ok_todo", entries=entries_joined),
            severity="required",
            confidence="medium",
        )
    finding.evidence_refs = ["deb-metadata:deb_packages"]
    return finding


def _check_esl_4(ctx: RunContext, finding: Finding) -> Finding:
    """ESL-4: Go language detection gate."""
    resolved = _get_packaging_source_or_unknown(ctx, finding, "ESL-4")
    if resolved is None:
        return finding
    check, packaging = resolved

    if _is_go_package(packaging):
        # ESL-4 itself is just the gate; it's ok to confirm it's Go.
        # The actual compliance checks are ESL-5, ESL-6, ESL-7.
        finding.succeed(render_check_message(check, "ok_go_message"))
    else:
        finding.succeed(render_check_message(check, "ok_not_go_message"))
    finding.evidence_refs = [
        "packaging-source:go_sum_present",
        "packaging-source:debian_rules",
    ]
    return finding


def _check_esl_7(ctx: RunContext, finding: Finding) -> Finding:
    """ESL-7: Go build type (shared vs static)."""
    resolved = _get_packaging_source_or_unknown(ctx, finding, "ESL-7")
    if resolved is None:
        return finding
    check, packaging = resolved

    if not _is_go_package(packaging):
        finding.succeed(render_check_message(check, "ok_not_go_message"))
        finding.evidence_refs = []
        return finding

    # Detect build mode
    debian_rules = packaging.get("debian_rules", "")
    if "-buildmode=shared" in debian_rules or "linkshared" in debian_rules:
        finding.succeed(render_check_message(check, "ok_shared_message"))
    elif "DH_GOLANG_BUILDPKG" in debian_rules or "dh_golang" in debian_rules:
        # dh-golang without explicit shared mode defaults to static in modern versions.
        # This needs human confirmation.
        finding.fail(
            render_check_message(check, "recommended_message"),
            render_check_message(check, "recommended_todo"),
            severity="recommended",
            confidence="medium",
        )
    else:
        _set_unknown_from_adapter(
            finding,
            check,
            message_key="unknown_build_mode_message",
            todo_key="unknown_build_mode_todo",
        )
    finding.evidence_refs = ["packaging-source:debian_rules"]
    return finding


def _check_esl_8(ctx: RunContext, finding: Finding) -> Finding:
    """ESL-8: Rust language detection gate."""
    resolved = _get_packaging_source_or_unknown(ctx, finding, "ESL-8")
    if resolved is None:
        return finding
    check, packaging = resolved

    if _is_rust_package(packaging):
        finding.succeed(render_check_message(check, "ok_rust_message"))
    else:
        finding.succeed(render_check_message(check, "ok_not_rust_message"))
    finding.evidence_refs = [
        "packaging-source:cargo_lock_present",
        "packaging-source:debian_rules",
    ]
    return finding


def _check_esl_9(ctx: RunContext, finding: Finding) -> Finding:
    """ESL-9: Rust package uses dh_cargo."""
    resolved = _get_packaging_source_or_unknown(ctx, finding, "ESL-9")
    if resolved is None:
        return finding
    check, packaging = resolved

    if not _is_rust_package(packaging):
        # Not a Rust package; gate doesn't apply.
        finding.succeed(render_check_message(check, "ok_not_rust_message"))
        finding.evidence_refs = []
        return finding

    debian_rules = packaging.get("debian_rules", "")
    uses_dh_cargo = "--buildsystem cargo" in debian_rules or "dh_cargo" in debian_rules
    if uses_dh_cargo:
        finding.succeed(render_check_message(check, "ok_message"))
    else:
        finding.fail(
            render_check_message(check, "not_ok_message"),
            render_check_message(check, "not_ok_todo"),
            severity="required",
        )
    finding.evidence_refs = [
        "packaging-source:debian_rules",
        "packaging-source:cargo_lock_present",
    ]
    return finding


def _check_esl_10(ctx: RunContext, finding: Finding) -> Finding:
    """ESL-10: Rust: vendored deps, no unexpected Built-Using, Cargo.lock present."""
    resolved = _get_packaging_source_or_unknown(ctx, finding, "ESL-10")
    if resolved is None:
        return finding
    check, packaging = resolved
    adapters = ctx.evidence.get("adapters", {})

    if not _is_rust_package(packaging):
        finding.succeed(render_check_message(check, "ok_not_rust_message"))
        finding.evidence_refs = []
        return finding

    problems = []
    if not packaging.get("cargo_lock_present", False):
        problems.append("Cargo.lock not found")

    # Check for unexpected Built-Using from binary packages (not source debian/control)
    deb_metadata = adapters.get("deb-metadata", {})
    if deb_metadata.get("status") == "ok":
        deb_packages = deb_metadata.get("deb_packages", [])
        all_built_using = []
        for pkg in deb_packages:
            all_built_using.extend(pkg.get("built_using", []))
            # Note: Static-Built-Using for Rust should also be toolchain-only
            all_built_using.extend(pkg.get("static_built_using", []))

        # Filter out expected entries (rust, cargo, cgo, standard toolchain)
        unexpected_bu = [
            e
            for e in all_built_using
            if not any(
                keyword in e.lower()
                for keyword in ["rust", "cargo", "cgo", "golang", "${misc:built-using}"]
            )
        ]
        if unexpected_bu:
            problems.append("Unexpected Built-Using entries: " + "; ".join(unexpected_bu))

    if problems:
        problems_str = "; ".join(problems)
        finding.fail(
            render_check_message(check, "not_ok_message", problems=problems_str),
            render_check_message(check, "not_ok_todo", problems=problems_str),
            severity="required",
        )
    else:
        finding.succeed(render_check_message(check, "ok_message"))

    evidence_refs = ["packaging-source:cargo_lock_present"]
    if deb_metadata.get("status") == "ok":
        evidence_refs.append("deb-metadata:deb_packages")
    finding.evidence_refs = evidence_refs
    return finding


# Generic packaging diagnostics that appear on virtually every build and carry
# no signal about the quality of the upstream code. They must not be reported as
# build warnings/errors (they are pure noise for an MIR reviewer).
_BUILD_LOG_NOISE_MARKERS = (
    "dpkg-source: warning:",
    "dpkg-buildflags: warning:",
    "dpkg-genbuildinfo: warning:",
    "dpkg-gencontrol: warning:",
    "dpkg-genchanges: warning:",
    "dpkg-deb: warning:",
    "dpkg-architecture: warning:",
    "debian/changelog not found",
    "cannot verify inline signature",
    "no acceptable signature found",
)


def _is_build_log_noise(line_lower: str) -> bool:
    """Return True for generic packaging diagnostics that are not code issues."""
    return any(marker in line_lower for marker in _BUILD_LOG_NOISE_MARKERS)


# Per-test output emitted by test runners (ctest verbose prefixes each test's
# stdout/stderr with "N: "; meson uses a similar convention). Such lines are the
# program's OWN logging during the test phase (e.g. a decoder emitting
# "ERROR ... Failed to parse FrameHeader" while decoding a deliberately-broken
# fixture) and must never be mistaken for build/toolchain errors.
_TEST_OUTPUT_PREFIX_RE = re.compile(r"^\s*\d+:\s")

# Genuine build failures are compiler/linker/build-tool diagnostics, not
# free-form "error"/"failed to" substrings that also occur in program output.
_BUILD_ERROR_RE = re.compile(
    r":\d+:\d+:\s*(?:fatal\s+)?error:"  # gcc/clang: file:line:col: error:
    r"|:\d+:\s*(?:fatal\s+)?error:"  # file:line: error:
    r"|(?:^|\s)fatal error:"  # preprocessor fatal error
    r"|undefined reference to"  # linker
    r"|\bld:\s*(?:error|cannot)"  # linker
    r"|\bcollect2:\s*error"  # linker driver
    r"|\bdh_[a-z_]+:\s*error"  # debhelper
    r"|make(?:\[\d+\])?:\s*\*\*\*"  # make failure marker
    r"|dpkg-buildpackage:\s*error",
    re.IGNORECASE,
)

# Compiler warnings use a lowercase "warning:" token (optionally with a
# file:line: prefix). Matched case-sensitively so uppercase runtime log levels
# (e.g. glog "WARNING") are not swept in.
_BUILD_WARNING_RE = re.compile(r"(?::\d+:\d*:\s*)?warning:")


def _parse_build_log_issues(build_log: str) -> tuple[list[str], list[str]]:
    """Parse build log to extract real error and warning lines.

    Generic packaging noise that appears on essentially every build (dpkg-source
    signature notes, dpkg-buildflags changelog notes, etc.) is filtered out, and
    per-test runner output is skipped, so only genuine toolchain diagnostics
    remain.

    Returns:
        (errors, warnings) tuple where each is a list of relevant log lines
    """
    errors = []
    warnings = []
    security_warning_keywords = [
        "format string",
        "buffer overflow",
        "stack overflow",
        "integer overflow",
        "use after free",
        "out of bounds",
    ]

    for line in build_log.split("\n"):
        line_lower = line.lower()
        if _is_build_log_noise(line_lower):
            continue
        # Skip the program's own output during the test phase (see regex note).
        if _TEST_OUTPUT_PREFIX_RE.match(line):
            continue
        # Genuine build errors: compiler/linker/build-tool diagnostics only.
        if _BUILD_ERROR_RE.search(line):
            errors.append(line.strip())
        # Security-relevant warnings anywhere in the log.
        elif any(token in line_lower for token in security_warning_keywords):
            warnings.append(line.strip())
        # Compiler/build warnings (lowercase "warning:" or deprecation notes).
        elif _BUILD_WARNING_RE.search(line) or any(
            token in line_lower for token in [" -w ", "deprecated"]
        ):
            warnings.append(line.strip())

    return errors, warnings


def _check_urf_1(ctx: RunContext, finding: Finding) -> Finding:
    """URF-1: No build errors or warnings."""
    check = _get_check_definition(ctx, "URF-1")
    adapters = ctx.evidence.get("adapters", {})
    fetch_build_result = adapters.get("fetch-build", {})

    if fetch_build_result.get("status") != "ok":
        finding.fail(
            render_check_message(check, "unknown_message"),
            render_check_message(check, "unknown_todo"),
            severity="recommended",
            confidence="low",
            status="unknown",
        )
        finding.evidence_refs = ["fetch-build:error"]
        return finding

    build_log = fetch_build_result.get("build_log", "")
    errors, warnings = _parse_build_log_issues(build_log)

    if errors:
        finding.fail(
            render_check_message(check, "not_ok_errors_message", errors="; ".join(errors[:3])),
            render_check_message(check, "not_ok_errors_todo"),
            severity="required",
            confidence="high",
        )
        finding.evidence_refs = ["fetch-build:build_log"]
        return finding

    if warnings:
        # Genuine toolchain warnings are surfaced for reviewer judgement rather
        # than auto-classified as a confirmed problem: whether they matter is a
        # human call. Routed to "Left to decide" via the unknown status. The
        # TODO keeps the original affirmative template statement so the reviewer
        # can resolve it in place; the warning detail is carried as the rationale
        # ("Can't decide: …") so the original statement is not lost.
        sample = "; ".join(warnings[:3])
        finding.fail(
            render_check_message(check, "warnings_message", count=len(warnings), sample=sample),
            render_check_message(check, "warnings_todo"),
            severity="recommended",
            confidence="medium",
            status="unknown",
            rationale=render_check_message(
                check, "warnings_rationale", count=len(warnings), sample=sample
            ),
        )
        finding.evidence_refs = ["fetch-build:build_log"]
        return finding

    finding.succeed(
        render_check_message(check, "ok_message"),
        confidence="high",
    )
    finding.evidence_refs = ["fetch-build:build_log"]
    return finding


def _check_prf_10(ctx: RunContext, finding: Finding) -> Finding:
    """PRF-10: Not on lto-disabled list."""
    check = _get_check_definition(ctx, "PRF-10")
    adapters = ctx.evidence.get("adapters", {})
    lto = adapters.get("lto-disabled-list", {})

    # If the list could not be fetched, leave the decision to the reviewer
    # rather than emitting a false pass.
    if lto.get("status") != "ok":
        _set_unknown_from_adapter(
            finding,
            check,
            todo_key="unknown_todo",
            severity="recommended",
            evidence_refs=["lto-disabled-list:status"],
        )
        return finding

    if lto.get("on_list"):
        arches = lto.get("disabled_arches") or []
        arch_str = ", ".join(arches) if arches else "unknown"
        finding.fail(
            render_check_message(check, "not_ok_message", arches=arch_str),
            render_check_message(check, "not_ok_todo", arches=arch_str),
            severity="required",
            confidence="high",
        )
        finding.evidence_refs = ["lto-disabled-list:disabled_arches"]
        return finding

    finding.succeed(
        render_check_message(check, "ok_message"),
        confidence="high",
    )
    finding.evidence_refs = ["lto-disabled-list:on_list"]
    return finding


# The canonical Maintainer value `update-maintainer` (ubuntu-dev-tools) sets whenever
# a package carries an Ubuntu delta - see LP: #1951988. A package with no Ubuntu
# delta keeps its Debian-original Maintainer unchanged, which is equally correct.
_PRF_11_UBUNTU_DEVELOPERS_MAINTAINER = "Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>"


def _check_prf_11(ctx: RunContext, finding: Finding) -> Finding:
    """PRF-11: debian/control Maintainer field correctness.

    Uses packaging-source.delta_kind (cheap version-string classification,
    no git-ubuntu diffstat needed) plus source_maintainer. Ok whenever there
    is no Ubuntu delta, or a delta is present and Maintainer was already
    updated via update-maintainer. Flags the remaining case - a delta
    present without that update - for the reviewer to judge directly.
    """
    result = _get_packaging_source_or_unknown(ctx, finding, "PRF-11")
    if result is None:
        return finding
    check, packaging = result

    delta_kind = str(packaging.get("delta_kind", "")).strip()
    maintainer = str(packaging.get("source_maintainer", "")).strip()

    if not delta_kind or delta_kind == "unknown":
        _set_unknown_from_adapter(
            finding,
            check,
            todo_key="unknown_todo",
            severity="recommended",
            evidence_refs=["packaging-source:delta_kind"],
        )
        return finding

    if delta_kind != "ubuntu_delta" or maintainer == _PRF_11_UBUNTU_DEVELOPERS_MAINTAINER:
        finding.succeed(render_check_message(check, "ok_message"), confidence="high")
        finding.evidence_refs = [
            "packaging-source:delta_kind",
            "packaging-source:source_maintainer",
        ]
        return finding

    version = str(packaging.get("analyzed_version", "")).strip() or "unknown"
    finding.fail(
        render_check_message(
            check, "not_ok_message", version=version, maintainer=maintainer or "missing"
        ),
        render_check_message(check, "not_ok_todo"),
        severity="required",
        confidence="high",
    )
    finding.evidence_refs = ["packaging-source:delta_kind", "packaging-source:source_maintainer"]
    return finding


def _check_cb_8(ctx: RunContext, finding: Finding) -> Finding:
    """CB-8: Python packages use dh_python."""
    check = _get_check_definition(ctx, "CB-8")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.fail(
            render_check_message(check, "unknown_message"),
            render_check_message(check, "unknown_todo"),
            severity="recommended",
            confidence="low",
            status="unknown",
        )
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    is_python = _is_python_package(packaging)
    rules = packaging.get("debian_rules", "")
    control = packaging.get("debian_control", "")
    # Modern packaging declares dh-sequence-python3 in debian/control
    # Build-Depends instead of an explicit dh_python3 override in
    # debian/rules; the sequence add-on auto-invokes dh_python3, so
    # debian/rules never contains that substring for such packages.
    uses_dh_python = (
        "dh_python" in rules or "dh_python3" in rules or "dh-sequence-python3" in control
    )

    if not is_python:
        # Not a Python package; gate doesn't apply
        finding.succeed(
            render_check_message(check, "ok_not_python_message"),
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:debian_rules"]
        return finding

    if uses_dh_python:
        finding.succeed(
            render_check_message(check, "ok_message"),
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:debian_rules", "packaging-source:debian_control"]
        return finding

    # Python package not using dh_python
    finding.fail(
        render_check_message(check, "not_ok_message"),
        render_check_message(check, "not_ok_todo"),
        severity="required",
        confidence="high",
    )
    finding.evidence_refs = ["packaging-source:debian_rules", "packaging-source:debian_control"]
    return finding


def _check_esl_2(ctx: RunContext, finding: Finding) -> Finding:
    """ESL-2: No unexpected static linking."""
    check = _get_check_definition(ctx, "ESL-2")
    adapters = ctx.evidence.get("adapters", {})
    fetch_build_result = adapters.get("fetch-build", {})
    packaging = adapters.get("packaging-source", {})

    if fetch_build_result.get("status") != "ok" or packaging.get("status") != "ok":
        finding.fail(
            render_check_message(check, "unknown_message"),
            render_check_message(check, "unknown_todo"),
            severity="recommended",
            confidence="low",
            status="unknown",
        )
        finding.evidence_refs = ["fetch-build:build_log"]
        return finding

    build_log = fetch_build_result.get("build_log", "")
    static_link_hints = fetch_build_result.get("static_link_hints", [])
    static_binaries = fetch_build_result.get("static_binaries", [])

    # The authoritative signal for unwanted static linking is a fully static
    # ELF binary shipped in a built deb (static_binaries). Raw "-static" tokens
    # in the build log are NOT used: libtool emits "-static <pkg>.la" to link a
    # package's own convenience library into its own binary (acceptable
    # intra-package linking), and configure probes ("checking if gcc static
    # flag -static works... yes") are not links at all. Cross-source-package
    # static linking of individual archive libraries is tracked via Built-Using
    # (ESL-3). debian/rules hints capture deliberate -static in LDFLAGS.

    # Common patterns for justifiable static linking
    justifiable_patterns = [
        "integrity checker",
        "security scanner",
        "initramfs",
        "bootloader",
        "firmware",
        "kernel module",
    ]
    is_justifiable = any(pattern.lower() in build_log.lower() for pattern in justifiable_patterns)

    if not static_binaries and not static_link_hints:
        finding.succeed(
            render_check_message(check, "ok_message"),
            confidence="high",
        )
        finding.evidence_refs = ["fetch-build:static_binaries", "fetch-build:build_log"]
        return finding

    if is_justifiable:
        finding.succeed(
            render_check_message(check, "ok_justified_message"),
            confidence="medium",
        )
        finding.evidence_refs = ["fetch-build:static_binaries", "fetch-build:build_log"]
        return finding

    # Static linking without clear justification
    detail_parts: list[str] = []
    if static_binaries:
        detail_parts.append(
            render_check_message(
                check, "not_ok_detail_binaries", binaries=", ".join(static_binaries[:5])
            )
        )
    if static_link_hints:
        detail_parts.append(
            render_check_message(check, "not_ok_detail_hints", hints=", ".join(static_link_hints))
        )
    detail = f" ({'; '.join(detail_parts)})" if detail_parts else ""
    finding.fail(
        render_check_message(check, "not_ok_message", detail=detail),
        render_check_message(check, "not_ok_todo"),
        severity="required",
        confidence="medium",
    )
    finding.evidence_refs = ["fetch-build:static_binaries", "fetch-build:build_log"]
    return finding


def _check_prf_2(ctx: RunContext, finding: Finding) -> Finding:
    """PRF-2: Symbols tracking for shared libraries.

    Whether symbols tracking is *needed* is governed solely by whether the
    package ships a shared library (a ``.so``): the programming language is
    irrelevant. A package that also ships Python code is still responsible for
    tracking the symbols of any shared library it ships; only the absence of a
    shared library removes the obligation. The ``.symbols`` file is therefore
    the first, authoritative signal, checked before anything else.
    """
    check = _get_check_definition(ctx, "PRF-2")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.fail(
            render_check_message(check, "unknown_message"),
            render_check_message(check, "unknown_todo"),
            severity="recommended",
            confidence="low",
            status="unknown",
        )
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    debian_control = packaging.get("debian_control", "")
    file_listing = packaging.get("file_listing", [])

    # A debian/*.symbols file is authoritative: it proves the maintainer tracks
    # the shared library's symbols. This is checked first and independently of
    # the language, so a C++ library that ships a helper .py script (which used
    # to be misdetected as "Python, not applicable") is still credited here.
    symbols_files = [
        str(entry.get("path", "")).strip()
        for entry in file_listing
        if str(entry.get("path", "")).rstrip("/").endswith(".symbols")
    ]
    if symbols_files:
        finding.succeed(
            render_check_message(check, "ok_message"),
            confidence="high",
            rationale=f"a symbols file is shipped: {', '.join(sorted(symbols_files))}",
        )
        finding.evidence_refs = ["packaging-source:file_listing"]
        return finding

    # No symbols file: the obligation depends purely on whether a shared library
    # is shipped. Shared-library runtime packages are soname-versioned
    # (e.g. liblua5.5-0); check debian/control and the built .deb names.
    fetch_build = adapters.get("fetch-build", {})
    built_debs = fetch_build.get("built_debs", []) if fetch_build.get("status") == "ok" else []
    shared_lib_pkgs = _shared_library_package_names(debian_control, built_debs)

    if not shared_lib_pkgs:
        finding.succeed(
            render_check_message(check, "ok_no_shared_message"),
            confidence="high",
            rationale="the package ships no shared library (.so), so ABI symbol tracking "
            "does not apply",
        )
        finding.evidence_refs = ["packaging-source:debian_control"]
        return finding

    # Ships a shared library but has no symbols file. This applies regardless of
    # language (e.g. a package that ships both Python code and a .so is still
    # responsible for that .so). C++ ABI tracking is hard, so it is a
    # recommendation rather than a hard requirement.
    finding.fail(
        render_check_message(check, "not_ok_message"),
        render_check_message(check, "not_ok_todo"),
        severity="recommended",
        confidence="medium",
        rationale=(
            f"shared library package(s) {', '.join(sorted(shared_lib_pkgs))} ship a .so but no "
            "debian/*.symbols file; for C++ libraries where tracking is impractical, document "
            "why (or use abigail/abi-compliance-check in CI, or bump SOVER on every update)"
        ),
    )
    finding.evidence_refs = ["packaging-source:debian_control"]
    return finding


def _check_prf_3(ctx: RunContext, finding: Finding) -> Finding:
    """PRF-3: debian/watch present."""
    check = _get_check_definition(ctx, "PRF-3")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.fail(
            render_check_message(check, "unknown_message"),
            render_check_message(check, "unknown_todo"),
            severity="recommended",
            confidence="low",
            status="unknown",
        )
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    debian_control = packaging.get("debian_control", "")
    file_listing = packaging.get("file_listing", [])

    # Check if debian/watch is present
    has_watch_file = any(f.get("path", "").endswith("debian/watch") for f in file_listing)

    # Check if it's a native package (Version ends with ~)
    is_native = "debian/source/format: 3.0 (native)" in debian_control

    if has_watch_file:
        finding.succeed(
            render_check_message(check, "ok_message"),
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:file_listing"]
        return finding

    if is_native:
        finding.succeed(
            render_check_message(check, "ok_native_message"),
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:debian_control"]
        return finding

    # Non-native package without watch file
    finding.fail(
        render_check_message(check, "not_ok_message"),
        render_check_message(check, "not_ok_todo"),
        severity="recommended",
        confidence="medium",
    )
    finding.evidence_refs = ["packaging-source:file_listing"]
    return finding


def _check_sec_2(ctx: RunContext, finding: Finding) -> Finding:
    """SEC-2: Does not run daemon as root."""
    check = _get_check_definition(ctx, "SEC-2")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.fail(
            render_check_message(check, "unknown_message"),
            render_check_message(check, "unknown_todo"),
            severity="recommended",
            confidence="low",
            status="unknown",
        )
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    debian_rules = packaging.get("debian_rules", "")
    debian_control = packaging.get("debian_control", "")

    # Scan non-comment lines only — a comment like '# Do not use User=root' must
    # not trigger a false positive.
    def _non_comment_lines(text: str) -> list[str]:
        return [ln for ln in text.splitlines() if not ln.lstrip().startswith("#")]

    active_lines = "\n".join(
        _non_comment_lines(debian_rules) + _non_comment_lines(debian_control)
    ).lower()

    # First priority: check for explicit root execution (exact match)
    if "user=root" in active_lines:
        # Has root execution; check for mitigations
        mitigations = ["seccomp", "apparmor", "selinux", "capabilities"]
        has_mitigations = any(m.lower() in active_lines for m in mitigations)

        if has_mitigations:
            finding.fail(
                render_check_message(check, "mitigated_message"),
                render_check_message(check, "mitigated_todo"),
                severity="recommended",
                confidence="medium",
            )
            finding.evidence_refs = ["packaging-source:debian_rules"]
            return finding
        else:
            finding.fail(
                render_check_message(check, "not_ok_message"),
                render_check_message(check, "not_ok_todo"),
                severity="required",
                confidence="medium",
            )
            finding.evidence_refs = ["packaging-source:debian_rules"]
            return finding

    # Second: check for non-root indicators
    non_root_indicators = ["user=", "dynamicuser=yes", "droppriv", "drop_privileges"]
    has_non_root = any(ind.lower() in active_lines for ind in non_root_indicators)
    has_nobody = "nobody" in active_lines

    if has_non_root or has_nobody:
        finding.succeed(
            render_check_message(check, "ok_message"),
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:debian_control"]
        return finding

    # No explicit indicators found; assume safe
    finding.succeed(
        render_check_message(check, "ok_message"),
        confidence="medium",
    )
    finding.evidence_refs = ["packaging-source:debian_rules"]
    return finding


def _check_urf_3(ctx: RunContext, finding: Finding) -> Finding:
    """URF-3: No sudo/gksu/pkexec/LD_LIBRARY_PATH outside tests."""
    check = _get_check_definition(ctx, "URF-3")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.fail(
            render_check_message(check, "unknown_message"),
            render_check_message(check, "unknown_todo"),
            severity="recommended",
            confidence="low",
            status="unknown",
        )
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    debian_rules = packaging.get("debian_rules", "")
    debian_control = packaging.get("debian_control", "")

    # Search for privilege escalation patterns and ignore only explicit test-context lines.
    escalation_keywords = ["sudo", "gksu", "pkexec", "ld_library_path"]
    combined_lines = [
        *(line for line in debian_rules.splitlines()),
        *(line for line in debian_control.splitlines()),
    ]

    for line in combined_lines:
        lowered = line.lower()
        if any(keyword in lowered for keyword in escalation_keywords) and not _line_is_test_context(
            line
        ):
            finding.fail(
                render_check_message(check, "not_ok_message"),
                render_check_message(check, "not_ok_todo"),
                severity="required",
                confidence="medium",
            )
            finding.evidence_refs = ["packaging-source:debian_rules"]
            return finding

    finding.succeed(
        render_check_message(check, "ok_message"),
        confidence="high",
    )
    finding.evidence_refs = ["packaging-source:debian_rules"]
    return finding


def _check_urf_4(ctx: RunContext, finding: Finding) -> Finding:
    """URF-4: No use of user 'nobody' outside tests."""
    check = _get_check_definition(ctx, "URF-4")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.fail(
            render_check_message(check, "unknown_message"),
            render_check_message(check, "unknown_todo"),
            severity="recommended",
            confidence="low",
            status="unknown",
        )
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    debian_rules = packaging.get("debian_rules", "")
    debian_control = packaging.get("debian_control", "")

    # Combine the classic debian/{rules,control} text scan with the full
    # source-tree grep (grep -RIn nobody) and the find -user nobody results from
    # both the source tree and the built binaries. Test-context hits are ignored.
    hits: list[str] = []
    for line in (*debian_rules.splitlines(), *debian_control.splitlines()):
        if "nobody" in line.lower() and not _line_is_test_context(line):
            hits.append(line.strip())
    for line in packaging.get("nobody_source_hits", []):
        # A text mention in a non-executable doc/text file (e.g. sample console
        # output) is not active code; skip it. Ownership facts below are kept.
        if _line_is_test_context(line) or _path_is_nonexecutable_doc(_grep_hit_path(line)):
            continue
        # The English pronoun "nobody" in comments/prose (e.g. "nobody else can
        # read") is not a user reference; only flag genuine code-context
        # references (quoted strings, assignments, chown-style, privilege-dropping
        # functions, CLI flags).
        if not _line_references_nobody_user(line):
            continue
        hits.append(line)
    for path in packaging.get("nobody_source_files", []):
        if not _path_is_test_context(path):
            hits.append(f"file owned by nobody (source): {path}")
    fetch_build = adapters.get("fetch-build", {})
    for path in fetch_build.get("nobody_owned_binaries", []):
        if not _path_is_test_context(path):
            hits.append(f"file owned by nobody (built binary): {path}")

    if hits:
        finding.fail(
            render_check_message(check, "not_ok_message", hits="; ".join(hits[:3])),
            render_check_message(check, "not_ok_todo"),
            severity="required",
            confidence="medium",
        )
        finding.evidence_refs = [
            "packaging-source:nobody_source_hits",
            "fetch-build:nobody_owned_binaries",
        ]
        return finding

    finding.succeed(
        render_check_message(check, "ok_message"),
        confidence="high",
    )
    finding.evidence_refs = [
        "packaging-source:nobody_source_hits",
        "fetch-build:nobody_owned_binaries",
    ]
    return finding


def _check_urf_5(ctx: RunContext, finding: Finding) -> Finding:
    """URF-5: No setuid/setgid binaries."""
    check = _get_check_definition(ctx, "URF-5")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})
    lintian = adapters.get("lintian", {})

    if packaging.get("status") != "ok":
        finding.fail(
            render_check_message(check, "unknown_message"),
            render_check_message(check, "unknown_todo"),
            severity="recommended",
            confidence="low",
            status="unknown",
        )
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    # Check lintian output for setuid/setgid tags (covers built binary artefacts).
    _LINTIAN_SETUID_TAGS = ("setuid-binary", "setgid-binary", "set-uid", "set-gid")
    lintian_triggered = False
    if lintian.get("status") == "ok":
        all_lintian = " ".join(
            lintian.get("lintian_errors", [])
            + lintian.get("lintian_warnings", [])
            + lintian.get("lintian_pedantic", [])
        ).lower()
        lintian_triggered = any(tag in all_lintian for tag in _LINTIAN_SETUID_TAGS)

    # Also check debian/rules text for explicit setuid/setgid patterns.
    debian_rules = packaging.get("debian_rules", "").lower()
    setuid_patterns = ["chmod 4", "chmod 2", "perm -4000", "perm -2000", "setuid", "setgid"]
    rules_triggered = any(p in debian_rules for p in setuid_patterns)

    # Full source-tree grep (grep -RIn setuid/setgid) and find -perm results from
    # both the source tree and the built binaries. Test-context hits are ignored,
    # as are text mentions inside non-executable doc/text files (prose or sample
    # output rather than active code).
    source_hits = [
        line
        for line in packaging.get("setuid_setgid_source_hits", [])
        if not _line_is_test_context(line) and not _path_is_nonexecutable_doc(_grep_hit_path(line))
    ]
    source_perm_files = [
        path
        for path in packaging.get("setuid_setgid_source_files", [])
        if not _path_is_test_context(path)
    ]
    fetch_build = adapters.get("fetch-build", {})
    binary_perm_files = [
        path
        for path in fetch_build.get("setuid_setgid_binaries", [])
        if not _path_is_test_context(path)
    ]
    source_triggered = bool(source_hits or source_perm_files)
    binary_triggered = bool(binary_perm_files)

    if lintian_triggered or rules_triggered or source_triggered or binary_triggered:
        if binary_triggered:
            source = render_check_message(
                check, "source_binaries", files=", ".join(binary_perm_files[:3])
            )
        elif lintian_triggered:
            source = render_check_message(check, "source_lintian")
        elif source_triggered:
            sample = (source_hits + source_perm_files)[:3]
            source = render_check_message(check, "source_tree", hits="; ".join(sample))
        else:
            source = render_check_message(check, "source_rules")
        # Check for documented justification (prefer systemd)
        if "systemd" in debian_rules:
            finding.fail(
                render_check_message(check, "systemd_message", source=source),
                render_check_message(check, "systemd_todo"),
                severity="recommended",
                confidence="medium",
            )
            finding.evidence_refs = ["packaging-source:debian_rules", "lintian:lintian_warnings"]
            return finding

        # A confirmed setuid/setgid binary in the built artefacts is high
        # confidence; source-only or rules-only hints are lower confidence.
        confidence = "high" if (lintian_triggered or binary_triggered) else "low"
        finding.fail(
            render_check_message(check, "not_ok_message", source=source),
            render_check_message(check, "not_ok_todo"),
            severity="required",
            confidence=confidence,
        )
        finding.evidence_refs = [
            "packaging-source:setuid_setgid_source_hits",
            "fetch-build:setuid_setgid_binaries",
            "lintian:lintian_warnings",
        ]
        return finding

    finding.succeed(
        render_check_message(check, "ok_message"),
        confidence="high" if lintian.get("status") == "ok" else "medium",
    )
    finding.evidence_refs = [
        "packaging-source:setuid_setgid_source_hits",
        "fetch-build:setuid_setgid_binaries",
    ]
    if lintian.get("status") == "ok":
        finding.evidence_refs.append("lintian:lintian_warnings")
    return finding


def _check_urf_7(ctx: RunContext, finding: Finding) -> Finding:
    """URF-7: No webkit/qtwebkit/libseed dependency."""
    check = _get_check_definition(ctx, "URF-7")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(
            finding, check, todo_key="unknown_todo", evidence_refs=["dep-analysis:error"]
        )

    dependencies = dep_analysis.get("runtime_dep_packages", [])
    old_webkit = ["webkit", "qtwebkit", "libseed"]

    for dep in dependencies:
        if any(web in dep.lower() for web in old_webkit):
            finding.fail(
                render_check_message(check, "not_ok_message", dep=dep),
                render_check_message(check, "not_ok_todo"),
                severity="required",
                confidence="high",
            )
            finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
            return finding

    finding.succeed(
        render_check_message(check, "ok_message"),
        confidence="high",
    )
    finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
    return finding


def _check_sec_8(ctx: RunContext, finding: Finding) -> Finding:
    """SEC-8: Does not use centralized online accounts."""
    check = _get_check_definition(ctx, "SEC-8")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})
    packaging = adapters.get("packaging-source", {})

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(
            finding, check, todo_key="unknown_todo", evidence_refs=["dep-analysis:error"]
        )

    if packaging.get("status") != "ok":
        return _set_unknown_from_adapter(
            finding, check, todo_key="unknown_todo", evidence_refs=["packaging-source:error"]
        )

    dependencies = dep_analysis.get("runtime_dep_packages", [])
    debian_control = packaging.get("debian_control", "")

    # Check for centralized accounts/online service APIs
    online_account_patterns = [
        "evolution-data-server",
        "gnome-online-accounts",
        "account-plugin",
        "accountsservice",
        "telepathy",
    ]

    # Also check source code for API patterns
    source_patterns = [
        "oauth",
        "oauth2",
        "google-api",
        "facebook-sdk",
        "twitter-api",
        "accounts_manager",
    ]

    for dep in dependencies:
        if any(p in dep.lower() for p in online_account_patterns):
            finding.fail(
                render_check_message(check, "not_ok_dep_message", dep=dep),
                render_check_message(check, "not_ok_todo"),
                severity="required",
                confidence="high",
            )
            finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
            return finding

    debian_control_lower = debian_control.lower()
    for pattern in source_patterns:
        if pattern.lower() in debian_control_lower:
            finding.fail(
                render_check_message(check, "not_ok_source_message", pattern=pattern),
                render_check_message(check, "not_ok_todo"),
                severity="required",
                confidence="medium",
            )
            finding.evidence_refs = ["packaging-source:debian_control"]
            return finding

    finding.succeed(
        render_check_message(check, "ok_message"),
        confidence="high",
    )
    finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
    return finding


def _check_sec_10(ctx: RunContext, finding: Finding) -> Finding:
    """SEC-10: Does not handle system authentication (PAM)."""
    check = _get_check_definition(ctx, "SEC-10")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})
    packaging = adapters.get("packaging-source", {})

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(
            finding, check, todo_key="unknown_todo", evidence_refs=["dep-analysis:error"]
        )

    if packaging.get("status") != "ok":
        return _set_unknown_from_adapter(
            finding, check, todo_key="unknown_todo", evidence_refs=["packaging-source:error"]
        )

    dependencies = dep_analysis.get("runtime_dep_packages", [])

    # Tier-1: direct PAM development deps — definitively indicates PAM implementation.
    _PAM_DEV_PATTERNS = ("libpam-dev", "libpam0g-dev", "libpam-abi")
    # Tier-2: direct PAM runtime library — likely PAM usage (medium confidence).
    _PAM_RUNTIME_DIRECT = ("libpam0g",)
    # Tier-0: system-level PAM meta-packages that nearly every service depends on
    # transitively — NOT a signal of direct PAM usage.
    _PAM_SYSTEM_META = ("libpam-runtime", "libpam-modules", "libpam-modules-bin")

    for dep in dependencies:
        dep_lower = dep.lower()
        if any(dep_lower == meta for meta in _PAM_SYSTEM_META):
            continue
        if any(pat in dep_lower for pat in _PAM_DEV_PATTERNS):
            finding.fail(
                render_check_message(check, "not_ok_dev_message", dep=dep),
                render_check_message(check, "not_ok_todo"),
                severity="required",
                confidence="high",
            )
            finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
            return finding
        if any(dep_lower == pat for pat in _PAM_RUNTIME_DIRECT):
            finding.fail(
                render_check_message(check, "not_ok_runtime_message", dep=dep),
                render_check_message(check, "not_ok_todo"),
                severity="required",
                confidence="medium",
            )
            finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
            return finding

    finding.succeed(
        render_check_message(check, "ok_message"),
        confidence="high",
    )
    finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
    return finding


# URF-8 (UI/desktop) is evaluated as an ev_to_ai check (see catalog-mir-
# review.yaml): whether a package is a user-facing desktop program is a
# judgement best made from Section, GUI-toolkit dependencies, the description
# and general knowledge — not from crude substring matching on debian/control.
# The .desktop file fact is surfaced by packaging-source for verification
# only, not for classification.
# URF-9 (translations) is deterministic: it reuses URF-8's already-made
# end-user-facing judgement (see _check_urf_9 below) instead of asking the
# model to independently re-classify the same package a second time, which
# risked the two checks disagreeing with each other.


def _check_urf_9(ctx: RunContext, finding: Finding) -> Finding:
    """URF-9: Translation coverage.

    Gated on URF-8's end-user-facing judgement (read via ``ctx.findings``,
    the same cross-check pattern CB-5 uses for CB-4) rather than asking the
    model to re-judge "is this package user-facing?" a second time. Once
    URF-8 has classified the package, only the has_translation_files FACT
    (deterministic, from packaging-source) remains to check.
    """
    check = _get_check_definition(ctx, "URF-9")
    urf8 = next((f for f in ctx.findings if f.id == "URF-8"), None)

    if urf8 is None or urf8.status == "unknown":
        _set_unknown_from_adapter(
            finding,
            check,
            message_key="urf8_unknown_message",
            todo_key="urf8_unknown_todo",
        )
        finding.evidence_refs = ["URF-8:status"]
        return finding

    if urf8.selected_option == "URF-8-A":
        # URF-8 judged the package not end-user facing; translations are not
        # needed regardless of whether any happen to be present.
        finding.succeed(render_check_message(check, "ok_not_visible_message"), confidence="high")
        finding.evidence_refs = ["URF-8:selected_option"]
        return finding

    # URF-8 judged the package end-user facing (URF-8-B or URF-8-C); only the
    # translation-file fact remains to check.
    resolved = _get_packaging_source_or_unknown(ctx, finding, "URF-9")
    if resolved is None:
        return finding
    _, packaging = resolved

    if packaging.get("has_translation_files"):
        finding.succeed(render_check_message(check, "ok_translated_message"), confidence="high")
    else:
        finding.fail(
            render_check_message(check, "not_ok_message"),
            render_check_message(check, "not_ok_todo"),
            severity="recommended",
            confidence="high",
        )
    finding.evidence_refs = ["URF-8:selected_option", "packaging-source:has_translation_files"]
    return finding


def _check_cb_7(ctx: RunContext, finding: Finding) -> Finding:
    """CB-7: No new Python 2 dependency."""
    check = _get_check_definition(ctx, "CB-7")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})
    packaging = adapters.get("packaging-source", {})

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    if packaging.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    dependencies = dep_analysis.get("runtime_dep_packages", [])

    # Python 2 patterns
    py2_patterns = ["python2", "python-", "py2-", "libpython2"]

    for dep in dependencies:
        if any(p in dep.lower() for p in py2_patterns):
            finding.fail(
                render_check_message(check, "blocker_message", dep=dep),
                render_check_message(check, "blocker_todo"),
                severity="required",
                confidence="high",
            )
            finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
            return finding

    finding.succeed(
        render_check_message(check, "ok_message"),
        confidence="high",
    )
    finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
    return finding


def _check_cb_5(ctx: RunContext, finding: Finding) -> Finding:
    """CB-5: Special hardware compromise accepted.

    This is only a genuine human judgment call when special hardware is actually
    required. It is gated on CB-4: when CB-4 concluded no special hardware is
    needed, there is no compromise to accept and the check resolves ok. When
    CB-4 indicates (or could not rule out) a special-hardware need, the reviewer
    must decide whether the compromise is acceptable, so it is left to decide.
    """
    check = _get_check_definition(ctx, "CB-5")
    cb4 = next((f for f in ctx.findings if f.id == "CB-4"), None)

    if cb4 is not None and cb4.status == "ok":
        finding.succeed(render_check_message(check, "ok_message"), confidence="high")
        finding.evidence_refs = ["CB-4:status"]
        return finding

    finding.fail(
        render_check_message(check, "human_only_message"),
        render_check_message(check, "human_only_todo", title=finding.title),
        severity="recommended",
        confidence="low",
        status="unknown",
    )
    finding.evidence_refs = ["CB-4:status"]
    return finding


def _check_sec_3(ctx: RunContext, finding: Finding) -> Finding:
    """SEC-3: Does not use webkit1/2."""
    check = _get_check_definition(ctx, "SEC-3")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    dependencies = dep_analysis.get("runtime_dep_packages", [])

    # Webkit patterns
    webkit_patterns = ["webkit", "webkit1", "webkit2", "libwebkit"]

    for dep in dependencies:
        if any(p in dep.lower() for p in webkit_patterns):
            finding.fail(
                render_check_message(check, "blocker_message", dep=dep),
                render_check_message(check, "blocker_todo"),
                severity="required",
                confidence="high",
            )
            finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
            return finding

    finding.succeed(
        render_check_message(check, "ok_message"),
        confidence="high",
    )
    finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
    return finding


def _check_sec_4(ctx: RunContext, finding: Finding) -> Finding:
    """SEC-4: Does not use lib*v8 directly."""
    check = _get_check_definition(ctx, "SEC-4")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    dependencies = dep_analysis.get("runtime_dep_packages", [])

    # V8 patterns
    v8_patterns = ["libv8", "v8", "libnode"]

    for dep in dependencies:
        if any(p in dep.lower() for p in v8_patterns):
            finding.fail(
                render_check_message(check, "blocker_message", dep=dep),
                render_check_message(check, "blocker_todo"),
                severity="required",
                confidence="high",
            )
            finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
            return finding

    finding.succeed(
        render_check_message(check, "ok_message"),
        confidence="high",
    )
    finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
    return finding


def _check_dep_1(ctx: RunContext, finding: Finding) -> Finding:
    """DEP-1: No unresolved runtime dependencies needing MIR."""
    check = _get_check_definition(ctx, "DEP-1")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})
    packaging = adapters.get("packaging-source", {})

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(
            finding,
            check,
            message_key="unknown_adapter_message",
            todo_key="unknown_adapter_todo",
            evidence_refs=["dep-analysis:error"],
        )

    if packaging.get("status") != "ok":
        return _set_unknown_from_adapter(
            finding,
            check,
            message_key="unknown_adapter_message",
            todo_key="unknown_adapter_todo",
            evidence_refs=["packaging-source:error"],
        )

    unresolved_deps = dep_analysis.get("in_scope_deps_not_in_main", [])

    if unresolved_deps:
        deps_str = ", ".join(unresolved_deps[:3])  # Show first 3
        finding.fail(
            render_check_message(check, "not_ok_message", deps=deps_str),
            render_check_message(check, "not_ok_todo", deps=deps_str),
            severity="required",
            confidence="medium",
        )
        finding.evidence_refs = ["dep-analysis:in_scope_deps_not_in_main"]
        return finding

    finding.succeed(
        render_check_message(check, "ok_message"),
        confidence="high",
    )
    finding.evidence_refs = ["dep-analysis:in_scope_deps_not_in_main"]
    return finding


def _check_prf_8(ctx: RunContext, finding: Finding) -> Finding:
    """PRF-8: No excessive lintian warnings."""
    check = _get_check_definition(ctx, "PRF-8")
    adapters = ctx.evidence.get("adapters", {})
    lintian = adapters.get("lintian", {})

    if lintian.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    # Get lintian output
    warnings = lintian.get("lintian_warnings", [])
    errors = lintian.get("lintian_errors", [])

    # Hard failures on errors
    if errors:
        error_str = ", ".join(errors[:3])
        finding.fail(
            render_check_message(check, "not_ok_errors_message", errors=error_str),
            render_check_message(check, "not_ok_errors_todo"),
            severity="required",
            confidence="high",
        )
        finding.evidence_refs = ["lintian:lintian_errors"]
        return finding

    # Check for excessive warnings (more than a few)
    if len(warnings) > 5:
        finding.fail(
            render_check_message(check, "not_ok_many_message", count=len(warnings)),
            render_check_message(check, "not_ok_many_todo"),
            severity="recommended",
            confidence="medium",
        )
        finding.evidence_refs = ["lintian:lintian_warnings"]
        return finding

    # Some warnings are OK, but document them
    if warnings:
        finding.fail(
            render_check_message(check, "minor_message", count=len(warnings)),
            render_check_message(check, "minor_todo", count=len(warnings)),
            severity="ok",
            confidence="high",
        )
        finding.evidence_refs = ["lintian:lintian_warnings"]
        return finding

    # No warnings/errors
    finding.succeed(
        render_check_message(check, "ok_message"),
        confidence="high",
    )
    finding.evidence_refs = ["lintian:warnings"]
    return finding


def _split_debian_version(version_str: str) -> tuple[int, str, str]:
    """Split a Debian/Ubuntu package version into epoch, upstream, revision."""
    if not version_str:
        return (0, "", "")

    epoch = 0
    remainder = version_str
    if ":" in version_str:
        epoch_str, _, tail = version_str.partition(":")
        if epoch_str.isdigit():
            epoch = int(epoch_str)
            remainder = tail

    if "-" in remainder:
        upstream_version, _, debian_revision = remainder.rpartition("-")
    else:
        upstream_version = remainder
        debian_revision = ""

    return (epoch, upstream_version, debian_revision)


def _normalize_upstream_version(version_str: str) -> str:
    """Normalize a version string to the upstream version part used for PRF-6."""
    _, upstream_version, _ = _split_debian_version(version_str)
    normalized = upstream_version or version_str
    if normalized.startswith("v") and len(normalized) > 1 and normalized[1].isdigit():
        normalized = normalized[1:]
    return normalized


def _parse_version_tuple(version_str: str) -> tuple:
    """Parse the normalized upstream version into a coarse semantic tuple."""
    normalized = _normalize_upstream_version(version_str)
    if not normalized:
        return ()

    tokens = re.findall(r"\d+|[A-Za-z]+|~", normalized)
    parsed: list[int | str] = []
    for token in tokens:
        if token.isdigit():
            parsed.append(int(token))
        else:
            parsed.append(token.lower())
    return tuple(parsed)


def _compare_versions(left: str, right: str) -> int:
    """Compare two Debian-style versions using dpkg semantics."""
    comparisons = (("lt", -1), ("gt", 1), ("eq", 0))
    for operator, result in comparisons:
        completed = subprocess.run(
            ["dpkg", "--compare-versions", left, operator, right],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode == 0:
            return result
    raise RuntimeError(f"Could not compare versions: {left!r} vs {right!r}")


def _versions_compatible(archive_version: str, upstream_version: str) -> tuple[bool, str]:
    """Check if the packaged upstream version is up-to-date with upstream."""
    if not archive_version or not upstream_version:
        return (True, "Could not determine versions")

    packaged_upstream = _normalize_upstream_version(archive_version)
    latest_upstream = _normalize_upstream_version(upstream_version)
    if not packaged_upstream or not latest_upstream:
        return (True, "Could not parse versions")

    comparison = _compare_versions(packaged_upstream, latest_upstream)
    if comparison >= 0:
        return (True, "Packaged upstream version meets or exceeds latest upstream")

    return (
        False,
        f"Packaged upstream version behind upstream: {packaged_upstream} < {latest_upstream}",
    )


def _check_prf_6(ctx: RunContext, finding: Finding) -> Finding:
    """PRF-6: Current release packaged."""
    check = _get_check_definition(ctx, "PRF-6")
    adapters = ctx.evidence.get("adapters", {})

    # Get package info
    lp_package = adapters.get("lp-package-api", {})
    if lp_package.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    upstream_tracker = adapters.get("upstream-tracker", {})
    if upstream_tracker.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    archive_version = lp_package.get("current_version", "")
    upstream_version = upstream_tracker.get("latest_version", "")

    if not archive_version or not upstream_version:
        return _set_unknown_from_adapter(finding, check)

    # Check version compatibility
    is_compatible, reason = _versions_compatible(archive_version, upstream_version)

    if is_compatible:
        finding.succeed(render_check_message(check, "ok_message"))
    else:
        # Archive is behind - determine if "somewhat behind" or "very old"
        archive_parts = _parse_version_tuple(archive_version)
        upstream_parts = _parse_version_tuple(upstream_version)
        archive_norm = _normalize_upstream_version(archive_version)
        upstream_norm = _normalize_upstream_version(upstream_version)

        if archive_parts and upstream_parts:
            # Compare major versions
            archive_major = archive_parts[0] if isinstance(archive_parts[0], int) else 0
            upstream_major = upstream_parts[0] if isinstance(upstream_parts[0], int) else 0

            # If major version is 2+ behind, it's very old
            if isinstance(archive_major, int) and isinstance(upstream_major, int):
                major_gap = upstream_major - archive_major

                if major_gap >= 2:
                    # Very old
                    finding.fail(
                        render_check_message(
                            check,
                            "very_behind_message",
                            archive=archive_norm,
                            upstream=upstream_norm,
                        ),
                        render_check_message(check, "behind_todo"),
                        severity="required",
                        confidence="high",
                    )
                else:
                    # Somewhat behind (1 major version or minor version differences)
                    finding.fail(
                        render_check_message(
                            check,
                            "somewhat_behind_message",
                            archive=archive_norm,
                            upstream=upstream_norm,
                        ),
                        render_check_message(check, "behind_todo"),
                        severity="recommended",
                        confidence="high",
                    )
            else:
                # Can't determine major - mark as recommended
                finding.fail(
                    render_check_message(
                        check, "version_lag_message", archive=archive_norm, upstream=upstream_norm
                    ),
                    render_check_message(check, "version_lag_todo"),
                    severity="recommended",
                    confidence="medium",
                )
        else:
            finding.fail(
                render_check_message(check, "unknown_lag_message"),
                render_check_message(check, "version_lag_todo"),
                severity="recommended",
                confidence="medium",
            )

    finding.evidence_refs = ["lp-package-api:current_version", "upstream-tracker:latest_version"]
    return finding


# ---------------------------------------------------------------------------
# Deterministic dispatch table
# Must be defined after all _check_* functions it references.
# ---------------------------------------------------------------------------


def _eval_deterministic(check: dict, ctx: RunContext, finding: Finding) -> Finding:
    """Evaluate checks with deterministic logic only."""
    check_id = check["id"]
    evaluator_func = DETERMINISTIC_CHECKS.get(check_id)
    if evaluator_func:
        return evaluator_func(ctx, finding)
    else:
        finding.fail(
            "Deterministic check evaluator not implemented", finding.title, status="unknown"
        )
        return finding


# Check id -> evaluator function. A plain mapping replaces the old decorator
# registry (checks.registry): the check set is static, so import-time
# registration indirection had no payoff beyond ordering fragility.
DETERMINISTIC_CHECKS: dict[str, Callable[[RunContext, Finding], Finding]] = {
    "SUM-1": _check_sum_1,
    "SUM-2": _check_sum_2,
    "CB-1": _check_cb_1,
    "SUM-4": _check_sum_4,
    "DEP-3": _check_dep_3,
    "ESL-3": _check_esl_3,
    "ESL-4": _check_esl_4,
    "ESL-7": _check_esl_7,
    "ESL-8": _check_esl_8,
    "ESL-9": _check_esl_9,
    "ESL-10": _check_esl_10,
    "URF-1": _check_urf_1,
    "PRF-10": _check_prf_10,
    "PRF-11": _check_prf_11,
    "CB-8": _check_cb_8,
    "ESL-2": _check_esl_2,
    "PRF-2": _check_prf_2,
    "PRF-3": _check_prf_3,
    "SEC-2": _check_sec_2,
    "URF-3": _check_urf_3,
    "URF-4": _check_urf_4,
    "URF-5": _check_urf_5,
    "URF-7": _check_urf_7,
    "SEC-8": _check_sec_8,
    "SEC-10": _check_sec_10,
    "URF-9": _check_urf_9,
    "CB-7": _check_cb_7,
    "CB-5": _check_cb_5,
    "SEC-3": _check_sec_3,
    "SEC-4": _check_sec_4,
    "DEP-1": _check_dep_1,
    "PRF-8": _check_prf_8,
    "PRF-6": _check_prf_6,
}

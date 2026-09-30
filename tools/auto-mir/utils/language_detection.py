"""Shared language and vendor-tree detection over packaging evidence.

Single source of truth for "is this package written in language X" and
"which directories hold vendored third-party code". Both the evidence
adapters (``packaging-source`` marker collection) and the checks
subsystem (language gates, ESL/CB checks) consume this module, so the
two can never drift apart. It deliberately depends on nothing but the
standard library and the packaging-source payload dict.
"""

from __future__ import annotations

import re

# Directory names conventionally used for vendored third-party code.
# ``rust-vendor`` is the documented Debian cargo vendoring convention
# (dh-cargo/debcargo helper layout); the rest are the generic upstream
# conventions. Rules-declared names (e.g. CARGO_VENDOR_DIR) are merged
# into this set per package by derive_vendor_dir_names().
STANDARD_VENDOR_DIR_NAMES = (
    "vendor",
    "vendored",
    "third_party",
    "3rdparty",
    "node_modules",
    "rust-vendor",
)

# Path segments that mark a directory as build/test-time only. Used both
# to classify vendored dirs as test-only (shipped_vendored_dirs) and to
# keep test fixtures (which frequently embed foreign-language mock
# files) out of language tree hints.
TEST_ONLY_PATH_SEGMENTS = (
    "test",
    "tests",
    "testing",
    "example",
    "examples",
    "doc",
    "docs",
    "benchmark",
    "benchmarks",
    "fixture",
    "fixtures",
)

# CARGO_VENDOR_DIR = <name> assignments in debian/rules (also matches
# ``export CARGO_VENDOR_DIR=...`` and the ``?=``/``+=`` variants). The
# captured name is restricted to a single safe path component; anything
# else is ignored rather than interpolated into a guest shell command.
_CARGO_VENDOR_DIR_PATTERN = re.compile(
    r"(?m)^\s*(?:export\s+)?CARGO_VENDOR_DIR\s*[?:+]?=\s*([A-Za-z0-9][A-Za-z0-9._+-]*)"
)


def derive_vendor_dir_names(debian_rules: str) -> list[str]:
    """Return the vendor directory names to recognize for this package.

    The standard convention names plus every ``CARGO_VENDOR_DIR``
    assignment found in debian/rules (the Debian cargo packaging
    convention stores vendored crates in a top-level directory whose
    name the rules file declares, e.g. ``rust-vendor``).
    """
    names = set(STANDARD_VENDOR_DIR_NAMES)
    for match in _CARGO_VENDOR_DIR_PATTERN.finditer(debian_rules or ""):
        names.add(match.group(1))
    return sorted(names)


def vendor_dir_markers(packaging: dict) -> tuple[str, ...]:
    """Return ``/<name>/`` marker substrings for this package's vendor trees.

    Uses the adapter-collected ``vendor_dir_names`` when present (rules
    derived) and falls back to the standard convention names for older
    evidence payloads that predate the field.
    """
    names = set(STANDARD_VENDOR_DIR_NAMES)
    extra = packaging.get("vendor_dir_names")
    if isinstance(extra, (list, tuple)):
        names.update(name for name in extra if isinstance(name, str) and name)
    return tuple(f"/{name}/" for name in sorted(names))


def iter_non_vendor_paths(packaging: dict):
    """Yield normalized source-tree file paths, excluding vendored trees.

    Paths are lowercased with a leading ``./`` stripped (so ``./src/a.rs``
    yields ``src/a.rs``). Vendored directories - the standard names plus
    whatever ``vendor_dir_names`` the adapter derived from debian/rules -
    and ``.git`` trees never yield, because foreign-language files inside
    them (test mocks, vendored crate sources) must not classify the
    package's own language.
    """
    for entry in packaging.get("file_listing", []):
        raw_path = str(entry.get("path", "") or "")
        if not raw_path:
            continue
        normalized = raw_path.lower().replace("\\", "/")
        if normalized.startswith("./"):
            normalized = normalized[1:]
        marked = normalized if normalized.startswith("/") else f"/{normalized}"
        if "/.git/" in marked:
            continue
        if any(marker in marked for marker in vendor_dir_markers(packaging)):
            continue
        yield normalized


def _is_test_only_path(path: str) -> bool:
    """True when any parent segment marks the file as build/test-time only."""
    segments = path.split("/")[:-1]
    return any(segment in TEST_ONLY_PATH_SEGMENTS for segment in segments)


def _tree_hint_paths(packaging: dict, suffixes: tuple[str, ...], basenames: tuple[str, ...]):
    """Collect the package's own (non-vendored, non-test-tree) source paths
    whose name or suffix indicates the language."""
    hints: list[str] = []
    for path in iter_non_vendor_paths(packaging):
        if _is_test_only_path(path):
            continue
        base = path.rsplit("/", 1)[-1]
        if base in basenames:
            hints.append(path)
        elif base.endswith(suffixes):
            hints.append(path)
    return hints


def go_tree_hint_paths(packaging: dict) -> list[str]:
    """Source-tree paths hinting at Go (own .go files, go.mod, go.work)."""
    return _tree_hint_paths(packaging, (".go",), ("go.mod", "go.work"))


def rust_tree_hint_paths(packaging: dict) -> list[str]:
    """Source-tree paths hinting at Rust (own .rs files, Cargo.toml)."""
    return _tree_hint_paths(packaging, (".rs",), ("cargo.toml",))


def _is_python_package(packaging: dict) -> bool:
    """Return True when the packaging evidence indicates a Python package.

    Detection requires a genuine Python *packaging* signal rather than the mere
    presence of a ``.py`` file, because C/C++ (and other) source trees routinely
    ship helper or test scripts written in Python. A single stray ``.py`` must
    not classify such a package as Python (this previously mis-gated e.g. a C++
    library that ships a helper script).

    Heuristics (any one sufficient):
    - a Python build system in debian/rules (dh_python(3)/dh-python/pybuild, or
      distutils/setuptools/flit);
    - a python3 / dh-python / pybuild build dependency, or an X[S]-Python*
      field, in debian/control;
    - a Python packaging metadata file (setup.py, setup.cfg, pyproject.toml) in
      the source tree (excluding vendored/third-party trees).
    """
    rules = packaging.get("debian_rules", "")
    rules_lower = rules.lower()
    if any(sig in rules for sig in ("dh_python", "dh_python3")):
        return True
    if any(
        sig in rules_lower for sig in ("dh-python", "pybuild", "distutils", "setuptools", "flit")
    ):
        return True

    # debian/control: python3 build-deps or X[S]-Python* fields.
    debian_control = packaging.get("debian_control", "")
    for raw_line in debian_control.splitlines():
        low = raw_line.lower()
        if low.startswith(("build-depends", "build-depends-indep")) and (
            "python3" in low or "dh-python" in low or "pybuild" in low
        ):
            return True
        if low.startswith(("x-python3-version", "xs-python-version", "x-python-version")):
            return True

    # Python packaging metadata files anywhere in the (non-vendored) tree.
    for path in iter_non_vendor_paths(packaging):
        base = path.rsplit("/", 1)[-1]
        if base in ("setup.py", "setup.cfg", "pyproject.toml"):
            return True

    return False


def detect_language_signals(packaging: dict) -> dict:
    """Detect Go/Rust/Python signals from packaging evidence, tiered.

    Declared signals are authoritative packaging statements: buildsystem
    declarations in debian/rules, build-dependency sequences in
    debian/control, and the ecosystem lockfiles (go.sum, Cargo.lock).
    Tree hints are mere file-name evidence from the package's own
    (non-vendored, non-test) tree; a declared signal of one language
    outranks tree hints of another, so vendored test mocks of a foreign
    language can never misclassify a package.

    Returns ``{"go": {"declared_evidence": [...], "tree_hint_paths": [...]},
    "rust": {...}, "python": {...}}`` with human-readable evidence strings.
    """
    rules = str(packaging.get("debian_rules", "") or "")
    rules_lower = rules.lower()
    control = str(packaging.get("debian_control", "") or "")

    go_declared: list[str] = []
    if packaging.get("go_sum_present"):
        go_declared.append("go.sum present")
    if "dh-golang" in rules:
        go_declared.append("dh-golang in debian/rules")
    if "--with golang" in rules_lower or "--buildsystem golang" in rules_lower:
        go_declared.append("golang buildsystem in debian/rules")
    if "dh-sequence-golang" in control:
        go_declared.append("dh-sequence-golang in debian/control Build-Depends")

    rust_declared: list[str] = []
    if packaging.get("cargo_lock_present"):
        rust_declared.append("Cargo.lock present")
    if "--buildsystem cargo" in rules:
        rust_declared.append("--buildsystem cargo in debian/rules")
    if "dh_cargo" in rules:
        rust_declared.append("dh_cargo in debian/rules")
    if "dh-sequence-cargo" in control:
        rust_declared.append("dh-sequence-cargo in debian/control Build-Depends")

    python_declared: list[str] = (
        ["Python packaging signals in debian/rules/control"]
        if (_is_python_package(packaging))
        else []
    )

    return {
        "go": {
            "declared_evidence": go_declared,
            "tree_hint_paths": go_tree_hint_paths(packaging),
        },
        "rust": {
            "declared_evidence": rust_declared,
            "tree_hint_paths": rust_tree_hint_paths(packaging),
        },
        "python": {
            "declared_evidence": python_declared,
            "tree_hint_paths": [],
        },
    }


def _hint_paths_counted(paths: list[str]) -> str:
    """Summarize hint paths for a message: up to 3 paths plus a count."""
    if len(paths) <= 3:
        return ", ".join(paths)
    return f"{len(paths)} files, e.g. {', '.join(paths[:3])}"


def _is_go_package(packaging: dict) -> bool:
    """Return True when the packaging evidence indicates a Go package.

    A declared Go signal (buildsystem, go.sum, build-dependency sequence)
    always classifies the package as Go. Mere tree hints only do when no
    other language is declared - a rust/python buildsystem outranks Go
    files in the tree, which in practice are vendored or auxiliary.
    """
    signals = detect_language_signals(packaging)
    if signals["go"]["declared_evidence"]:
        return True
    if not signals["go"]["tree_hint_paths"]:
        return False
    return not _other_language_declared(signals, "go")


def _is_rust_package(packaging: dict) -> bool:
    """Return True when the packaging evidence indicates a Rust package.

    Same declared-wins rule as ``_is_go_package``: declared Rust packaging
    (buildsystem, Cargo.lock, dh-sequence-cargo) always classifies; tree
    hints only when no go/python packaging is declared.
    """
    signals = detect_language_signals(packaging)
    if signals["rust"]["declared_evidence"]:
        return True
    if not signals["rust"]["tree_hint_paths"]:
        return False
    return not _other_language_declared(signals, "rust")


def _other_language_declared(signals: dict, language: str) -> bool:
    """True when any language other than ``language`` has declared signals."""
    return any(
        bool(entry["declared_evidence"]) for name, entry in signals.items() if name != language
    )


def _declared_language_names(signals: dict, language: str) -> str:
    """Comma-joined names of the languages (other than ``language``) whose
    packaging is declared - used to state which buildsystem outranked a
    tree hint."""
    declared = sorted(
        name for name, entry in signals.items() if name != language and entry["declared_evidence"]
    )
    return ", ".join(declared)


def language_detection_summary(packaging: dict, language: str) -> str:
    """Human-readable trigger summary for one language's gate decision.

    Used by ESL-4/ESL-8 so the draft states *why* a language was asserted
    (or why a tree hint was outranked by a declared buildsystem).
    """
    signals = detect_language_signals(packaging)
    entry = signals[language]
    if entry["declared_evidence"]:
        return "; ".join(entry["declared_evidence"])
    hints = entry["tree_hint_paths"]
    if hints and _other_language_declared(signals, language):
        declared_langs = sorted(
            name
            for name, other in signals.items()
            if name != language and other["declared_evidence"]
        )
        return (
            f"{_hint_paths_counted(hints)} found, but "
            f"{', '.join(declared_langs)} packaging is declared"
        )
    if hints:
        return _hint_paths_counted(hints)
    return "no signal"

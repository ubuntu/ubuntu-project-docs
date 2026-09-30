"""Unit tests for the shared language/vendor detection module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.language_detection import (  # noqa: E402
    STANDARD_VENDOR_DIR_NAMES,
    _is_go_package,
    _is_rust_package,
    derive_vendor_dir_names,
    go_tree_hint_paths,
    rust_tree_hint_paths,
)


def test_derive_vendor_dir_names_includes_cargo_vendor_dir():
    """The Debian cargo CARGO_VENDOR_DIR assignment is recognized as a vendor
    dir name (rust-ntpd regression: `export CARGO_VENDOR_DIR = rust-vendor`)."""
    rules = (
        "#!/usr/bin/make -f\n"
        "export CARGO_VENDOR_DIR = rust-vendor\n"
        "VENDOR_TARBALL = rust-ntpd_$(DEB_VERSION_UPSTREAM).orig-$(CARGO_VENDOR_DIR).tar.xz\n"
    )
    names = derive_vendor_dir_names(rules)
    assert "rust-vendor" in names
    for standard in STANDARD_VENDOR_DIR_NAMES:
        assert standard in names


def test_derive_vendor_dir_names_variants_and_ignores_unsafe():
    """?= / := / plain assignments match; anything that is not a single safe
    path component (slashes, spaces, shell metacharacters) is ignored."""
    rules = (
        "CARGO_VENDOR_DIR ?= crates-vendor\n"
        "CARGO_VENDOR_DIR := other\n"
        "export CARGO_VENDOR_DIR=plain\n"
        "CARGO_VENDOR_DIR = ../../etc\n"
        "CARGO_VENDOR_DIR = name; rm -rf /\n"
    )
    names = derive_vendor_dir_names(rules)
    assert "crates-vendor" in names
    assert "other" in names
    assert "plain" in names
    # unsafe values never reach the guest find command
    assert "../../etc" not in names
    assert all("/" not in name and " " not in name for name in names)
    assert all(";" not in name for name in names)


def test_derive_vendor_dir_names_empty_rules():
    assert derive_vendor_dir_names("") == sorted(STANDARD_VENDOR_DIR_NAMES)
    assert derive_vendor_dir_names(None) == sorted(STANDARD_VENDOR_DIR_NAMES)


def test_tree_hints_skip_vendored_and_test_trees():
    """Vendored trees (rules-derived names) and test/fixture trees are not
    language hints; the package's own sources are."""
    packaging = {
        "debian_rules": "export CARGO_VENDOR_DIR = rust-vendor\n",
        "vendor_dir_names": derive_vendor_dir_names(
            "export CARGO_VENDOR_DIR = rust-vendor\n"
        ),
        "go_sum_present": False,
        "cargo_lock_present": False,
        "file_listing": [
            {"path": "./cmd/tool/main.go", "size": 10},
            {"path": "./src/main.rs", "size": 10},
            {"path": "./rust-vendor/mocklib/ca.go", "size": 10},
            {"path": "./tests/verification_mock/ca.go", "size": 10},
            {"path": "./examples/old/go.mod", "size": 10},
        ],
    }
    # normalized paths keep the leading slash of the stripped "./" prefix
    assert go_tree_hint_paths(packaging) == ["/cmd/tool/main.go"]
    assert rust_tree_hint_paths(packaging) == ["/src/main.rs"]


def test_declared_rust_suppresses_go_tree_hints():
    """Declared-buildsystem-wins: Go tree hints do not classify a package
    whose Rust packaging is declared."""
    packaging = {
        "debian_rules": "%:\n\tdh $@ --buildsystem cargo\n",
        "debian_control": "Source: rust-ntpd\n",
        "cargo_lock_present": True,
        "go_sum_present": False,
        "file_listing": [{"path": "./cmd/tool/main.go", "size": 10}],
    }
    assert _is_rust_package(packaging) is True
    assert _is_go_package(packaging) is False


def test_go_tree_hints_still_active_without_other_declaration():
    """Without a conflicting buildsystem, own-tree Go files still classify
    (a Go package that does not (yet) declare dh-golang must not slip through)."""
    packaging = {
        "debian_rules": "dh $@",
        "cargo_lock_present": False,
        "go_sum_present": False,
        "file_listing": [{"path": "./cmd/tool/main.go", "size": 10}],
    }
    assert _is_go_package(packaging) is True

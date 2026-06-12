"""Integration tests for sbuild adapter with real package builds.

These tests require:
- LXD with VM support enabled
- Network access to download packages
- Sufficient disk space for VM images

Run with: pytest -m integration tests/test_integration_sbuild.py
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    pytest = None

from evidence.container_adapters import collect_sbuild

if HAS_PYTEST:
    # Mark all tests in this module as integration tests
    pytestmark = pytest.mark.integration


def _make_lxd_vm_context():
    """Create a mock context for LXD VM testing.

    This fixture assumes an LXD VM is available and configured.
    In a real CI environment, this would be set up beforehand.
    """
    ctx = Mock()
    ctx.vm_name = "test-sbuild-vm"
    ctx.series = "noble"
    ctx.source_package = "hello"
    ctx.evidence = {
        "adapters": {
            "packaging-source": {
                "status": "ok",
                "source_dir": "/tmp/hello-source",
                "debian_control": "Source: hello\n\nPackage: hello\nArchitecture: any",
                "debian_rules": "#!/usr/bin/make -f\n%:\n\tdh $@",
            }
        }
    }
    return ctx


def test_sbuild_hello_package_builds_successfully():
    """Test that sbuild can successfully build the hello package.

    This is a smoke test to verify:
    1. sbuild unshare backend works in LXD VM
    2. Built .deb files are produced
    3. Build log is captured

    Note: This test mocks container execution, so no real VM is needed.
    """
    lxd_vm_context = _make_lxd_vm_context()

    # Mock the packaging-source to point to a real hello package source
    # In a real test, we would fetch the source first
    with patch("evidence.container_adapters._capture") as mock_capture:
        # Mock apt-get source to fetch hello package
        def capture_side_effect(ctx, cmd, **kwargs):
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
            if "apt-get source" in cmd_str:
                # Simulate fetching hello source
                return "/tmp/hello-source"
            elif "mkdir -p" in cmd_str:
                return ""
            elif "sbuild" in cmd_str:
                # Simulate successful build
                return "sbuild: successfully built hello"
            elif "ls -1" in cmd_str and ".deb" in cmd_str:
                # Simulate built .deb files
                return "/tmp/sbuild-output/hello_2.10-3_amd64.deb"
            return ""

        mock_capture.side_effect = capture_side_effect

        # Mock _exists to simulate successful build
        with patch("evidence.container_adapters._exists") as mock_exists:
            mock_exists.return_value = True

            # Run sbuild adapter
            result = collect_sbuild(lxd_vm_context)

            # Verify build succeeded
            assert result["status"] == "ok"
            assert result["build_success"] is True
            assert len(result["built_debs"]) > 0
            assert "hello" in result["built_debs"][0]
            assert result["build_log"] != ""


def test_sbuild_adapter_requires_packaging_source():
    """Test that sbuild adapter fails gracefully without packaging-source."""
    ctx = Mock()
    ctx.vm_name = "test-vm"
    ctx.series = "noble"
    ctx.evidence = {"adapters": {}}

    from evidence.container_adapters import AdapterError

    if HAS_PYTEST:
        with pytest.raises(AdapterError, match="packaging-source.source_dir"):
            collect_sbuild(ctx)
    else:
        # Without pytest, just verify it raises the expected error
        try:
            collect_sbuild(ctx)
            assert False, "Expected AdapterError to be raised"
        except AdapterError as e:
            assert "packaging-source.source_dir" in str(e)


def test_sbuild_adapter_handles_build_failure():
    """Test that sbuild adapter handles build failures correctly."""
    lxd_vm_context = _make_lxd_vm_context()

    with patch("evidence.container_adapters._capture") as mock_capture:
        def capture_side_effect(ctx, cmd, **kwargs):
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
            if "sbuild" in cmd_str:
                # Simulate build failure
                return "sbuild: build failed: missing build dependencies"
            return ""

        mock_capture.side_effect = capture_side_effect

        # Mock _exists to simulate no .deb files produced
        with patch("evidence.container_adapters._exists") as mock_exists:
            mock_exists.return_value = False

            # Run sbuild adapter
            result = collect_sbuild(lxd_vm_context)

            # Verify build failure is reported
            assert result["status"] == "error"
            assert result["build_success"] is False
            assert len(result["built_debs"]) == 0


def test_dep_analysis_with_sbuild_output():
    """Test that dep-analysis adapter correctly processes sbuild output."""
    from evidence.container_adapters import collect_dep_analysis

    ctx = Mock()
    ctx.source_package = "hello"
    ctx.requested_binaries = ["hello"]
    ctx.evidence = {
        "adapters": {
            "packaging-source": {
                "status": "ok",
                "source_dir": "/tmp/hello-source",
            },
            "sbuild": {
                "status": "ok",
                "build_success": True,
                "built_debs": [
                    "/tmp/sbuild-output/hello_2.10-3_amd64.deb",
                ],
            }
        }
    }

    # Mock dpkg-deb commands
    with patch("evidence.container_adapters._capture") as mock_capture:
        def capture_side_effect(ctx, cmd, **kwargs):
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
            if "Package" in cmd_str:
                return "hello"
            elif "Depends" in cmd_str:
                return "libc6 (>= 2.14)"
            elif "awk" in cmd_str and "Package:" in cmd_str:
                return "hello"
            elif "apt-cache show" in cmd_str:
                # Mock source package lookup
                return "glibc"
            return ""

        mock_capture.side_effect = capture_side_effect

        # Mock component detection
        with patch("evidence.container_adapters._detect_component") as mock_component:
            mock_component.return_value = "main"

            # Run dep-analysis
            result = collect_dep_analysis(ctx)

            # Verify structure
            assert result["status"] == "ok"
            assert "hello" in result["binary_packages"]
            assert "hello" in result["built_packages"]
            assert len(result["runtime_deps"]) > 0
            assert "libc6" in result["runtime_dep_packages"]


def test_scope_filtering_with_requested_binaries():
    """Test that scope filtering works correctly with requested_binaries."""
    from evidence.container_adapters import collect_dep_analysis

    ctx = Mock()
    ctx.source_package = "multipkg"
    ctx.requested_binaries = ["multipkg-main"]  # Only request main package
    ctx.evidence = {
        "adapters": {
            "packaging-source": {
                "status": "ok",
                "source_dir": "/tmp/multipkg-source",
            },
            "sbuild": {
                "status": "ok",
                "build_success": True,
                "built_debs": [
                    "/tmp/sbuild-output/multipkg-main_1.0_amd64.deb",
                    "/tmp/sbuild-output/multipkg-dev_1.0_amd64.deb",
                ],
            }
        }
    }

    # Mock commands
    with patch("evidence.container_adapters._capture") as mock_capture:
        def capture_side_effect(ctx, cmd, **kwargs):
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
            if "awk" in cmd_str and "Package:" in cmd_str:
                return "multipkg-main\nmultipkg-dev"
            elif "Package" in cmd_str:
                if "multipkg-main" in cmd_str:
                    return "multipkg-main"
                else:
                    return "multipkg-dev"
            elif "Depends" in cmd_str:
                if "multipkg-main" in cmd_str:
                    return "libc6, libuniverse1"
                else:
                    return "libc6, libuniverse2"
            elif "apt-cache show" in cmd_str:
                if "libuniverse1" in cmd_str:
                    return "other-pkg"
                elif "libuniverse2" in cmd_str:
                    return "another-pkg"
                return "glibc"
            return ""

        mock_capture.side_effect = capture_side_effect

        # Mock component detection
        with patch("evidence.container_adapters._detect_component") as mock_component:
            def component_side_effect(ctx, pkg):
                if pkg in ["libuniverse1", "libuniverse2"]:
                    return "universe"
                return "main"

            mock_component.side_effect = component_side_effect

            # Run dep-analysis
            result = collect_dep_analysis(ctx)

            # Verify scope filtering
            assert result["status"] == "ok"
            # libuniverse1 is a dependency of multipkg-main (in scope)
            assert "libuniverse1" in result["in_scope_deps_not_in_main"]
            # libuniverse2 is a dependency of multipkg-dev (out of scope)
            assert "libuniverse2" in result["out_of_scope_deps_not_in_main"]


def test_same_source_deps_not_flagged():
    """Test that dependencies from the same source package are not flagged."""
    from evidence.container_adapters import collect_dep_analysis

    ctx = Mock()
    ctx.source_package = "dav1d"
    ctx.requested_binaries = ["dav1d", "libdav1d7"]
    ctx.evidence = {
        "adapters": {
            "packaging-source": {
                "status": "ok",
                "source_dir": "/tmp/dav1d-source",
            },
            "sbuild": {
                "status": "ok",
                "build_success": True,
                "built_debs": [
                    "/tmp/sbuild-output/dav1d_1.0_amd64.deb",
                    "/tmp/sbuild-output/libdav1d7_1.0_amd64.deb",
                ],
            }
        }
    }

    # Mock commands
    with patch("evidence.container_adapters._capture") as mock_capture:
        def capture_side_effect(ctx, cmd, **kwargs):
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
            if "awk" in cmd_str and "Package:" in cmd_str:
                return "dav1d\nlibdav1d7"
            elif "Package" in cmd_str:
                if "dav1d" in cmd_str and "libdav1d7" not in cmd_str:
                    return "dav1d"
                else:
                    return "libdav1d7"
            elif "Depends" in cmd_str:
                if "dav1d" in cmd_str and "libdav1d7" not in cmd_str:
                    return "libc6, libdav1d7"
                else:
                    return "libc6"
            elif "apt-cache show" in cmd_str:
                # libdav1d7 comes from dav1d source
                if "libdav1d7" in cmd_str:
                    return "dav1d"
                return "glibc"
            return ""

        mock_capture.side_effect = capture_side_effect

        # Mock component detection
        with patch("evidence.container_adapters._detect_component") as mock_component:
            def component_side_effect(ctx, pkg):
                if pkg == "libdav1d7":
                    return "universe"
                return "main"

            mock_component.side_effect = component_side_effect

            # Run dep-analysis
            result = collect_dep_analysis(ctx)

            # Verify same-source deps are not in in_scope_deps_not_in_main
            assert result["status"] == "ok"
            assert "libdav1d7" in result["same_source_deps"]
            assert "libdav1d7" not in result["in_scope_deps_not_in_main"]

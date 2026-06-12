"""Integration tests for sbuild adapter with real package builds.

These tests require:
- LXD with VM support enabled
- Network access to download packages
- Sufficient disk space for VM images

Run with: pytest -m integration tests/test_integration_sbuild.py
"""

import os
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

import lxd_runner
from evidence.container_adapters import collect_sbuild

_UBUNTU_ENV = {"HOME": "/home/ubuntu", "USER": "ubuntu", "LOGNAME": "ubuntu"}

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
                "source_workdir": "/tmp/hello-source-workdir",
                "debian_control": "Source: hello\n\nPackage: hello\nArchitecture: any",
                "debian_rules": "#!/usr/bin/make -f\n%:\n\tdh $@",
            }
        }
    }
    return ctx


def _require_vm_name() -> str:
    """Return integration VM name or skip when not configured.

    This keeps the test as a real integration check while remaining optional
    for environments without a prepared VM.
    """
    vm_name = os.environ.get("AUTO_MIR_TEST_VM")
    if not vm_name:
        if HAS_PYTEST:
            pytest.skip("Set AUTO_MIR_TEST_VM to a running provisioned VM for sbuild integration")
        return ""
    return vm_name


def _prepare_packaging_source_in_vm(vm_name: str, source_pkg: str = "hello") -> dict:
    """Fetch source package inside VM and return packaging-source adapter payload."""
    workdir = f"/tmp/auto-mir-int-{source_pkg}"
    lxd_runner.exec_in_retry(
        vm_name,
        [
            "bash",
            "-lc",
            (
                f"work={workdir} && "
                'rm -rf "$work" && mkdir -p "$work" && cd "$work" && '
                f"apt-get source -qq {source_pkg} && "
                "dir=$(find . -maxdepth 1 -type d -name '*-*' | head -n1) && "
                "echo ${dir#./} > source_dir.txt"
            ),
        ],
        env=_UBUNTU_ENV,
        user=1000,
        group=1000,
        operation=f"prepare source package {source_pkg}",
    )

    source_dir_name = lxd_runner.exec_in(
        vm_name,
        ["bash", "-lc", f"cd {workdir} && cat source_dir.txt"],
        capture=True,
        env=_UBUNTU_ENV,
        user=1000,
        group=1000,
    ).stdout.strip()
    source_dir = f"{workdir}/{source_dir_name}"

    dsc_path = lxd_runner.exec_in(
        vm_name,
        ["bash", "-lc", f"ls {workdir}/*.dsc 2>/dev/null | head -n1"],
        capture=True,
        check=False,
        env=_UBUNTU_ENV,
        user=1000,
        group=1000,
    ).stdout.strip()
    if not dsc_path:
        raise AssertionError(f"Expected a .dsc file in {workdir} after apt-get source")

    debian_control = lxd_runner.exec_in(
        vm_name,
        ["bash", "-lc", f"cd {source_dir} && cat debian/control"],
        capture=True,
        check=False,
        env=_UBUNTU_ENV,
        user=1000,
        group=1000,
    ).stdout
    debian_rules = lxd_runner.exec_in(
        vm_name,
        ["bash", "-lc", f"cd {source_dir} && cat debian/rules"],
        capture=True,
        check=False,
        env=_UBUNTU_ENV,
        user=1000,
        group=1000,
    ).stdout

    return {
        "status": "ok",
        "source_dir": source_dir,
        "source_workdir": workdir,
        "debian_control": debian_control,
        "debian_rules": debian_rules,
    }


def test_sbuild_hello_package_builds_successfully():
    """Test that sbuild can successfully build the hello package.

    This is a smoke test to verify:
    1. sbuild unshare backend works in LXD VM
    2. Built .deb files are produced
    3. Build log is captured

    This test exercises the real adapter code path in a real VM.
    """
    vm_name = _require_vm_name()
    if not vm_name:
        return

    ctx = Mock()
    ctx.vm_name = vm_name
    ctx.series = "devel"
    ctx.source_package = "hello"
    ctx.requested_binaries = []
    ctx.evidence = {
        "adapters": {
            "packaging-source": _prepare_packaging_source_in_vm(vm_name, "hello"),
        }
    }

    result = collect_sbuild(ctx)

    if result["status"] != "ok":
        details = (
            "sbuild smoke test failed unexpectedly\n"
            f"status={result.get('status')} build_success={result.get('build_success')}\n"
            f"message={result.get('message', '')}\n"
            f"built_debs={result.get('built_debs', [])}\n"
            f"lintian_errors={result.get('lintian_errors', [])}\n"
            f"lintian_warnings={result.get('lintian_warnings', [])}\n"
            "--- build_log ---\n"
            f"{result.get('build_log', '')}\n"
            "--- lintian_output ---\n"
            f"{result.get('lintian_output', '')}\n"
        )
        if HAS_PYTEST:
            pytest.fail(details)
        assert False, details

    assert result["build_success"] is True
    assert len(result["built_debs"]) > 0
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
    """Test that sbuild adapter reports errors for invalid source directories."""
    vm_name = _require_vm_name()
    if not vm_name:
        return

    ctx = Mock()
    ctx.vm_name = vm_name
    ctx.series = "devel"
    ctx.source_package = "hello"
    ctx.requested_binaries = []
    ctx.evidence = {
        "adapters": {
            "packaging-source": {
                "status": "ok",
                "source_dir": "/tmp/does-not-exist-auto-mir-sbuild/hello-0.0",
                "source_workdir": "/tmp/does-not-exist-auto-mir-sbuild",
                "debian_control": "",
                "debian_rules": "",
            }
        }
    }

    # With no .dsc in the (nonexistent) workdir the adapter raises AdapterError.
    from evidence.container_adapters import AdapterError

    if HAS_PYTEST:
        with pytest.raises(AdapterError, match=".dsc"):
            collect_sbuild(ctx)
    else:
        try:
            collect_sbuild(ctx)
            assert False, "Expected AdapterError to be raised"
        except AdapterError as e:
            assert ".dsc" in str(e)


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
            },
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
            },
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
            },
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

"""Integration tests for the fetch-build adapter with real Launchpad downloads.

These tests require:
- LXD with VM support enabled
- Network access to Launchpad (build state/binaries) and the archive
- Sufficient disk space for VM images

Run with: pytest -m integration tests/test_integration_fetch_build.py
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
from evidence.guest_adapters import collect_fetch_build
from evidence.host_adapters import collect_lp_build_api

_UBUNTU_ENV = {"HOME": "/home/ubuntu", "USER": "ubuntu", "LOGNAME": "ubuntu"}

if HAS_PYTEST:
    # Mark all tests in this module as integration tests
    pytestmark = pytest.mark.integration


def _require_vm_name() -> str:
    """Return integration VM name or skip when not configured.

    This keeps the test as a real integration check while remaining optional
    for environments without a prepared VM.
    """
    vm_name = os.environ.get("AUTO_MIR_TEST_VM")
    if not vm_name:
        if HAS_PYTEST:
            pytest.skip(
                "Set AUTO_MIR_TEST_VM to a running provisioned VM for fetch-build integration"
            )
        return ""
    return vm_name


def _prepare_packaging_source_in_vm(vm_name: str, source_pkg: str = "hello") -> dict:
    """Fetch source package inside VM and return packaging-source adapter payload.

    "hello" is used throughout this module because it is a small, always
    successfully built Ubuntu main package - a stable reference for
    exercising fetch-build's real Launchpad download path.
    """
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
    analyzed_version = lxd_runner.exec_in(
        vm_name,
        ["bash", "-lc", f"cd {source_dir} && dpkg-parsechangelog -S Version 2>/dev/null"],
        capture=True,
        check=False,
        env=_UBUNTU_ENV,
        user=1000,
        group=1000,
    ).stdout.strip()

    return {
        "status": "ok",
        "source_dir": source_dir,
        "source_workdir": workdir,
        "analyzed_version": analyzed_version,
        "analyzed_pocket": "release",
        "debian_control": debian_control,
        "debian_rules": debian_rules,
    }


def test_fetch_build_hello_package_downloads_successfully():
    """Smoke test: fetch-build downloads the official Launchpad build for hello.

    Exercises the real adapter code path in a real VM: a real lp-build-api
    lookup, fetch-build's own Launchpad binary lookup/download, pushing
    files into the guest, and running lintian there.
    """
    vm_name = _require_vm_name()
    if not vm_name:
        return

    packaging = _prepare_packaging_source_in_vm(vm_name, "hello")

    ctx = Mock()
    ctx.guest_name = vm_name
    ctx.series = "devel"
    ctx.source_package = "hello"
    ctx.requested_binaries = []
    ctx.evidence = {"adapters": {"packaging-source": packaging}}

    lp_build_result = collect_lp_build_api(ctx)
    assert lp_build_result["status"] == "ok", lp_build_result
    ctx.evidence["adapters"]["lp-build-api"] = lp_build_result

    result = collect_fetch_build(ctx)

    if result["status"] != "ok":
        details = (
            "fetch-build smoke test failed unexpectedly\n"
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


def test_fetch_build_requires_packaging_source():
    """fetch-build adapter fails gracefully without packaging-source."""
    ctx = Mock()
    ctx.guest_name = "test-vm"
    ctx.series = "noble"
    ctx.evidence = {"adapters": {}}

    from evidence.guest_adapters import AdapterError

    if HAS_PYTEST:
        with pytest.raises(AdapterError, match="packaging-source.source_dir"):
            collect_fetch_build(ctx)
    else:
        try:
            collect_fetch_build(ctx)
            assert False, "Expected AdapterError to be raised"
        except AdapterError as e:
            assert "packaging-source.source_dir" in str(e)


def test_fetch_build_requires_lp_build_api():
    """fetch-build adapter fails gracefully without successful lp-build-api evidence."""
    ctx = Mock()
    ctx.guest_name = "test-vm"
    ctx.series = "noble"
    ctx.evidence = {
        "adapters": {
            "packaging-source": {"status": "ok", "source_dir": "/tmp/hello-2.10"},
        }
    }

    from evidence.guest_adapters import AdapterError

    if HAS_PYTEST:
        with pytest.raises(AdapterError, match="lp-build-api"):
            collect_fetch_build(ctx)
    else:
        try:
            collect_fetch_build(ctx)
            assert False, "Expected AdapterError to be raised"
        except AdapterError as e:
            assert "lp-build-api" in str(e)


def test_fetch_build_requires_build_record_for_local_arch():
    """fetch-build adapter fails gracefully when no build exists for the guest arch."""
    ctx = Mock()
    ctx.guest_name = "test-vm"
    ctx.series = "noble"
    ctx.source_package = "hello"
    ctx.evidence = {
        "adapters": {
            "packaging-source": {
                "status": "ok",
                "source_dir": "/tmp/hello-2.10",
                "analyzed_version": "2.10-3",
            },
            "lp-build-api": {
                "status": "ok",
                "builds": [
                    {"arch_tag": "arm64", "build_state": "Successfully built"},
                    {"arch_tag": "riscv64", "build_state": "Successfully built"},
                ],
            },
        }
    }

    from evidence.guest_adapters import AdapterError

    with patch("evidence.guest_adapters._capture", return_value="amd64"):
        if HAS_PYTEST:
            with pytest.raises(AdapterError, match="amd64"):
                collect_fetch_build(ctx)
        else:
            try:
                collect_fetch_build(ctx)
                assert False, "Expected AdapterError to be raised"
            except AdapterError as e:
                assert "amd64" in str(e)


def test_dep_analysis_with_fetch_build_output():
    """Test that dep-analysis adapter correctly processes fetch-build output."""
    from evidence.guest_adapters import collect_dep_analysis

    ctx = Mock()
    ctx.source_package = "hello"
    ctx.requested_binaries = ["hello"]
    ctx.evidence = {
        "adapters": {
            "packaging-source": {
                "status": "ok",
                "source_dir": "/tmp/hello-source",
            },
            "fetch-build": {
                "status": "ok",
                "build_success": True,
                "built_debs": [
                    "/tmp/fetch-build-output/hello_2.10-3_amd64.deb",
                ],
            },
        }
    }

    # Mock dpkg-deb commands
    with patch("evidence.guest_adapters._capture") as mock_capture:

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
        with patch("evidence.guest_adapters._detect_component") as mock_component:
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
    from evidence.guest_adapters import collect_dep_analysis

    ctx = Mock()
    ctx.source_package = "multipkg"
    ctx.requested_binaries = ["multipkg-main"]  # Only request main package
    ctx.evidence = {
        "adapters": {
            "packaging-source": {
                "status": "ok",
                "source_dir": "/tmp/multipkg-source",
            },
            "fetch-build": {
                "status": "ok",
                "build_success": True,
                "built_debs": [
                    "/tmp/fetch-build-output/multipkg-main_1.0_amd64.deb",
                    "/tmp/fetch-build-output/multipkg-dev_1.0_amd64.deb",
                ],
            },
        }
    }

    # Mock commands
    with patch("evidence.guest_adapters._capture") as mock_capture:

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
        with patch("evidence.guest_adapters._detect_component") as mock_component:

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
    from evidence.guest_adapters import collect_dep_analysis

    ctx = Mock()
    ctx.source_package = "dav1d"
    ctx.requested_binaries = ["dav1d", "libdav1d7"]
    ctx.evidence = {
        "adapters": {
            "packaging-source": {
                "status": "ok",
                "source_dir": "/tmp/dav1d-source",
            },
            "fetch-build": {
                "status": "ok",
                "build_success": True,
                "built_debs": [
                    "/tmp/fetch-build-output/dav1d_1.0_amd64.deb",
                    "/tmp/fetch-build-output/libdav1d7_1.0_amd64.deb",
                ],
            },
        }
    }

    # Mock commands
    with patch("evidence.guest_adapters._capture") as mock_capture:

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
        with patch("evidence.guest_adapters._detect_component") as mock_component:

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


def test_auto_included_dep_classification_scoped_to_requested_binaries():
    """Auto-included dependency classification should use in-scope binaries only."""
    from evidence.guest_adapters import collect_dep_analysis

    ctx = Mock()
    ctx.source_package = "multipkg"
    ctx.requested_binaries = ["multipkg-main", "multipkg-dev"]
    ctx.evidence = {
        "adapters": {
            "packaging-source": {
                "status": "ok",
                "source_dir": "/tmp/multipkg-source",
            },
            "fetch-build": {
                "status": "ok",
                "build_success": True,
                "built_debs": [
                    "/tmp/fetch-build-output/multipkg-main_1.0_amd64.deb",
                    "/tmp/fetch-build-output/multipkg-dev_1.0_amd64.deb",
                    "/tmp/fetch-build-output/multipkg-doc_1.0_all.deb",
                ],
            },
        }
    }

    with patch("evidence.guest_adapters._capture") as mock_capture:

        def capture_side_effect(ctx, cmd, **kwargs):
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
            if "awk" in cmd_str and "Package:" in cmd_str:
                return "multipkg-main\nmultipkg-dev\nmultipkg-doc"
            elif "Package" in cmd_str:
                if "multipkg-main" in cmd_str:
                    return "multipkg-main"
                if "multipkg-dev" in cmd_str:
                    return "multipkg-dev"
                return "multipkg-doc"
            elif "Depends" in cmd_str:
                if "multipkg-main" in cmd_str:
                    return "libc6, libmain-only"
                if "multipkg-dev" in cmd_str:
                    return "libc6, libuniverse-dev, libunknown-dev"
                return "libc6, libdoc-extra"
            elif "apt-cache show" in cmd_str:
                if "libuniverse-dev" in cmd_str:
                    return "other-src"
                if "libunknown-dev" in cmd_str:
                    return "unknown-src"
                if "libdoc-extra" in cmd_str:
                    return "doc-src"
                return "glibc"
            return ""

        mock_capture.side_effect = capture_side_effect

        with patch("evidence.guest_adapters._detect_component") as mock_component:

            def component_side_effect(ctx, pkg):
                if pkg == "libuniverse-dev":
                    return "universe"
                if pkg == "libunknown-dev":
                    return "unknown"
                return "main"

            mock_component.side_effect = component_side_effect

            result = collect_dep_analysis(ctx)

            assert result["status"] == "ok"
            assert result["auto_included_binaries"] == ["multipkg-dev"]
            assert result["auto_included_deps_not_in_main_or_unknown"] == [
                "libuniverse-dev",
                "libunknown-dev",
            ]
            assert result["auto_included_offending_deps_by_binary"] == [
                {
                    "binary": "multipkg-dev",
                    "dependencies": ["libuniverse-dev", "libunknown-dev"],
                }
            ]

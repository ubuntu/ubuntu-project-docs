#!/usr/bin/env python3
"""Integration test runner for auto-mir.

Provisions a fresh LXD VM, runs the full pytest suite with AUTO_MIR_TEST_VM
set (so integration-gated tests execute), then destroys the VM regardless of
the test outcome.

Usage::

    python3 tests/run_integration.py
    make integration

The runner performs a fast lint check before creating the VM so that obvious
style mistakes are caught without paying the provisioning cost.
"""

import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_ROOT))

import lxd_runner  # noqa: E402

_VM_NAME_PREFIX = "auto-mir-int"

logging.basicConfig(
    format="%(levelname)-8s %(name)s %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("integration")


class _Ctx:
    """Minimal context object satisfying lxd_runner.spawn / destroy."""

    def __init__(self, vm_name: str) -> None:
        self.run_name = vm_name
        self.vm_name = ""  # populated by lxd_runner.spawn
        self.series = None  # resolve to current devel series automatically
        self.lxd_image = None
        self.lxd_options = "--vm -c limits.cpu=4 -c limits.memory=8GiB"
        self.pin_uat_tooling = None
        self.container_env: dict[str, str] = {}


def _run(cmd: list[str], env: dict | None = None) -> int:
    """Run a command in TOOL_ROOT and return its exit code."""
    return subprocess.run(cmd, cwd=str(TOOL_ROOT), env=env).returncode


def main() -> int:
    # Fast lint/format check before paying the cost of VM provisioning.
    log.info("Running lint checks before provisioning VM…")
    for lint_cmd in (
        ["uv", "tool", "run", "ruff", "format", "--check", "."],
        ["uv", "tool", "run", "ruff", "check", "."],
    ):
        rc = _run(lint_cmd)
        if rc != 0:
            log.error("Lint check failed; fix issues before running integration tests.")
            return rc

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    vm_name = f"{_VM_NAME_PREFIX}-{ts}"
    ctx = _Ctx(vm_name)

    log.info("Provisioning integration VM: %s", vm_name)
    try:
        lxd_runner.spawn(ctx)
        log.info("VM ready: %s", ctx.vm_name)

        env = os.environ.copy()
        env["AUTO_MIR_TEST_VM"] = ctx.vm_name
        rc = _run(["pytest", "tests/", "-v"], env=env)
        return rc

    except Exception as exc:
        log.error("Integration run failed: %s", exc)
        return 1

    finally:
        if ctx.vm_name:
            log.info("Tearing down VM: %s", ctx.vm_name)
            try:
                lxd_runner.destroy(ctx)
                log.info("VM destroyed.")
            except Exception as exc:
                log.warning(
                    "VM teardown failed — manual cleanup may be needed: lxc delete --force %s (%s)",
                    ctx.vm_name,
                    exc,
                )


if __name__ == "__main__":
    sys.exit(main())

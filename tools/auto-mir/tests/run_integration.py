#!/usr/bin/env python3
"""VM lifecycle helper for the make integration target.

Subcommands
-----------
setup    — Provision a fresh LXD VM and write its name to .int-vm-name.
teardown — Read .int-vm-name, destroy the VM, and remove the file.

This script is called exclusively by the Makefile integration target.
Lint and test execution are handled by the Makefile lint / unit targets so
there is no duplication; changing the ruff invocation in the Makefile is the
single source of truth.
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_ROOT))

import lxd_runner  # noqa: E402

_VM_NAME_PREFIX = "auto-mir-int"
_VM_NAME_FILE = TOOL_ROOT / ".int-vm-name"

logging.basicConfig(
    format="%(levelname)-8s %(name)s %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("integration")


class _Ctx:
    """Minimal context object satisfying lxd_runner.spawn / destroy."""

    def __init__(self, vm_name: str) -> None:
        self.run_name = vm_name
        self.guest_name = ""  # populated by lxd_runner.spawn
        self.series = None  # resolve to current devel series automatically
        self.lxd_image = None
        self.lxd_options = "--vm -c limits.cpu=4 -c limits.memory=8GiB -d root,size=20GiB"
        self.pin_uat_tooling = None
        self.guest_env: dict[str, str] = {}


def _setup() -> int:
    """Provision a fresh VM and record its name for subsequent make targets."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    vm_name = f"{_VM_NAME_PREFIX}-{ts}"
    ctx = _Ctx(vm_name)
    log.info("Provisioning integration VM: %s", vm_name)
    try:
        lxd_runner.spawn(ctx)
        _VM_NAME_FILE.write_text(ctx.guest_name)
        log.info("VM ready: %s (name recorded in %s)", ctx.guest_name, _VM_NAME_FILE.name)
        return 0
    except Exception as exc:
        log.error("VM provisioning failed: %s", exc)
        if ctx.guest_name:
            try:
                lxd_runner.destroy(ctx)
            except Exception:
                log.warning(
                    "Could not destroy partial VM %s — manual cleanup may be needed: "
                    "lxc delete --force %s",
                    ctx.guest_name,
                    ctx.guest_name,
                )
        return 1


def _teardown() -> int:
    """Destroy the VM recorded in .int-vm-name and remove the file."""
    if not _VM_NAME_FILE.exists():
        log.info("No %s found; nothing to tear down.", _VM_NAME_FILE.name)
        return 0
    vm_name = _VM_NAME_FILE.read_text().strip()
    if not vm_name:
        _VM_NAME_FILE.unlink(missing_ok=True)
        return 0
    ctx = _Ctx(vm_name)
    ctx.guest_name = vm_name  # already known — skip spawn, go straight to destroy
    log.info("Tearing down integration VM: %s", vm_name)
    try:
        lxd_runner.destroy(ctx)
        log.info("VM %s destroyed.", vm_name)
    except Exception as exc:
        log.warning(
            "VM teardown failed — manual cleanup may be needed: lxc delete --force %s (%s)",
            vm_name,
            exc,
        )
    finally:
        _VM_NAME_FILE.unlink(missing_ok=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Integration VM lifecycle helper (called by Makefile).",
    )
    parser.add_argument("command", choices=["setup", "teardown"])
    args = parser.parse_args()
    if args.command == "setup":
        return _setup()
    return _teardown()


if __name__ == "__main__":
    sys.exit(main())

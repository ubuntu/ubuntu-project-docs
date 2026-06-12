#!/usr/bin/env python3
"""integration_smoke.py - container isolation smoke test for auto-mir.

This script verifies that command execution happens inside an isolated LXD
Ubuntu devel container and captures runtime facts relevant to integration tests.

Usage:
    /usr/bin/python tools/auto-mir/integration_smoke.py [--lxd-image IMAGE] [--keep-container]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

import lxd_runner


class SmokeContext:
    def __init__(self, lxd_image: str | None, keep_container: bool | None):
        self.bug_id = "smoke"
        self.pin_uat_tooling = None
        self.lxd_image = lxd_image
        self.keep_container = keep_container
        self.lxd_options = "--vm -c limits.cpu=4 -c limits.memory=8GiB"
        self.vm_name = ""


def _parse_bool_arg(value: str) -> bool:
    if value.lower() in ("true", "yes", "1"):
        return True
    if value.lower() in ("false", "no", "0"):
        return False
    raise argparse.ArgumentTypeError(f"Expected true or false, got: {value!r}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="auto-mir LXD isolation smoke test")
    p.add_argument(
        "--lxd-image",
        default=None,
        help="Optional explicit LXD image alias (default: first available Ubuntu devel alias)",
    )
    p.add_argument(
        "--keep-container",
        dest="keep_container",
        nargs="?",
        const=True,
        default=None,
        type=_parse_bool_arg,
        metavar="true|false",
        help=(
            "Control smoke-test container cleanup (tri-state). "
            "Not specified: destroy on success, preserve on failure. "
            "--keep-container or --keep-container=true: always preserve. "
            "--keep-container=false: always destroy."
        ),
    )
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose logs")
    return p


def main() -> int:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s  %(name)s  %(message)s",
    )

    ctx = SmokeContext(args.lxd_image, args.keep_container)

    exit_code = 0
    try:
        lxd_runner.spawn(ctx)
        facts = lxd_runner.collect_runtime_facts(ctx)

        apt_policy_pkg = lxd_runner.exec_in(
            ctx.vm_name,
            ["bash", "-lc", "apt-cache policy bash"],
            capture=True,
            check=False,
        ).stdout.strip()

        result = {
            "runtime_isolation": facts,
            "apt_policy_bash_excerpt": "\n".join(apt_policy_pkg.splitlines()[:20]),
            "vm_exec_ok": bool(apt_policy_pkg),
        }
        print(json.dumps(result, indent=2, sort_keys=True))
    except Exception:
        exit_code = 1
        raise
    finally:
        if ctx.vm_name:
            if ctx.keep_container is True:
                should_keep = True
            elif ctx.keep_container is False:
                should_keep = False
            else:
                should_keep = exit_code != 0
            if not should_keep:
                lxd_runner.destroy(ctx)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

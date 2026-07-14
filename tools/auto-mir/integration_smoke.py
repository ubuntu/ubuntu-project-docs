#!/usr/bin/env python3
"""integration_smoke.py - LXD guest isolation smoke test for auto-mir.

This script verifies that command execution happens inside an isolated LXD
Ubuntu devel guest and captures runtime facts relevant to integration tests.

Usage:
    /usr/bin/python tools/auto-mir/integration_smoke.py [--lxd-image IMAGE] [--keep-guest]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

import lxd_runner
from utils.cli import parse_bool_arg


class SmokeContext:
    def __init__(self, lxd_image: str | None, keep_guest: bool | None):
        self.bug_id = "smoke"
        self.lxd_image = lxd_image
        self.keep_guest = keep_guest
        self.lxd_options = "--vm -c limits.cpu=4 -c limits.memory=8GiB -d root,size=20GiB"
        self.guest_name = ""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="auto-mir LXD isolation smoke test")
    p.add_argument(
        "--lxd-image",
        default=None,
        help="Optional explicit LXD image alias (default: first available Ubuntu devel alias)",
    )
    p.add_argument(
        "--keep-guest",
        dest="keep_guest",
        nargs="?",
        const=True,
        default=None,
        type=parse_bool_arg,
        metavar="true|false",
        help=(
            "Control smoke-test guest cleanup (tri-state). "
            "Not specified: destroy on success, preserve on failure. "
            "--keep-guest or --keep-guest=true: always preserve. "
            "--keep-guest=false: always destroy."
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

    ctx = SmokeContext(args.lxd_image, args.keep_guest)

    exit_code = 0
    try:
        lxd_runner.spawn(ctx)
        facts = lxd_runner.collect_runtime_facts(ctx)

        apt_policy_pkg = lxd_runner.exec_in(
            ctx.guest_name,
            ["bash", "-lc", "apt-cache policy bash"],
            capture=True,
            check=False,
        ).stdout.strip()

        result = {
            "runtime_isolation": facts,
            "apt_policy_bash_excerpt": "\n".join(apt_policy_pkg.splitlines()[:20]),
            "guest_exec_ok": bool(apt_policy_pkg),
        }
        print(json.dumps(result, indent=2, sort_keys=True))
    except Exception:
        exit_code = 1
        raise
    finally:
        if ctx.guest_name:
            if ctx.keep_guest is True:
                should_keep = True
            elif ctx.keep_guest is False:
                should_keep = False
            else:
                should_keep = exit_code != 0
            if not should_keep:
                lxd_runner.destroy(ctx)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

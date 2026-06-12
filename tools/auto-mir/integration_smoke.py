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
    def __init__(self, lxd_image: str | None, keep_container: bool):
        self.bug_id = "smoke"
        self.pin_tooling = None
        self.lxd_image = lxd_image
        self.keep_container = keep_container
        self.container_name = ""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="auto-mir LXD isolation smoke test")
    p.add_argument(
        "--lxd-image",
        default=None,
        help="Optional explicit LXD image alias (default: first available Ubuntu devel alias)",
    )
    p.add_argument(
        "--keep-container",
        action="store_true",
        default=False,
        help="Keep the smoke-test container for debugging",
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

    try:
        lxd_runner.spawn(ctx)
        facts = lxd_runner.collect_runtime_facts(ctx)

        apt_policy_pkg = lxd_runner.exec_in(
            ctx.container_name,
            ["bash", "-lc", "apt-cache policy bash"],
            capture=True,
            check=False,
        ).stdout.strip()

        result = {
            "runtime_isolation": facts,
            "apt_policy_bash_excerpt": "\n".join(apt_policy_pkg.splitlines()[:20]),
            "container_exec_ok": bool(apt_policy_pkg),
        }
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        if ctx.container_name and not ctx.keep_container:
            lxd_runner.destroy(ctx)

    return 0


if __name__ == "__main__":
    sys.exit(main())

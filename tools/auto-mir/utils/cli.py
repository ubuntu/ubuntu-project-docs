"""CLI parsing helpers shared across auto-mir entrypoints."""

from __future__ import annotations

import argparse


def parse_bool_arg(value: str) -> bool:
    """Parse common true/false command-line values.

    Accepted true values: true, yes, 1
    Accepted false values: false, no, 0
    """
    lowered = value.lower()
    if lowered in ("true", "yes", "1"):
        return True
    if lowered in ("false", "no", "0"):
        return False
    raise argparse.ArgumentTypeError(f"Expected true or false, got: {value!r}")

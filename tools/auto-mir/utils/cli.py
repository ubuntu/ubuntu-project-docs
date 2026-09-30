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


def ask_yes_no(prompt: str, *, default: bool | None = None, alerter=None) -> bool:
    """Ask a y/n question.

    ``default=None`` retries until a y/n answer; a boolean default is
    returned on empty input or EOF. ``alerter`` is the optional
    ``utils.attention.AttentionAlerter``: the idle bell/notification is
    armed around the blocking read and cancelled on answer.
    """
    suffix = "[y/n]" if default is None else ("[Y/n]" if default else "[y/N]")

    def _read_answer() -> str:
        if alerter is None:
            return input(f"{prompt} {suffix} ").strip().lower()
        handle = alerter.start(prompt)
        try:
            return input(f"{prompt} {suffix} ").strip().lower()
        finally:
            alerter.cancel(handle)

    while True:
        try:
            raw = _read_answer()
        except EOFError:
            return bool(default)
        if not raw and default is not None:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        if default is None:
            print("Please answer y or n.")


def ask_single_choice(prompt: str, options: list[tuple[str, str]]) -> str:
    """Ask the user to pick one option from a numbered list.

    ``options`` is a list of ``(label, value)`` pairs; the labels are printed
    numbered 1..N and the chosen option's ``value`` is returned. Invalid or
    out-of-range input re-prompts. EOF propagates as ``EOFError`` — callers
    gate on an interactive terminal before asking.
    """
    for index, (label, _value) in enumerate(options, start=1):
        print(f"  {index}. {label}")
    while True:
        try:
            raw = input(f"{prompt} [1-{len(options)}] ").strip()
        except EOFError:
            raise
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1][1]
        print(f"Please enter a number between 1 and {len(options)}.")

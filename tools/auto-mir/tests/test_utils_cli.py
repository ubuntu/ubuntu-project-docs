"""Unit tests for CLI helper utilities."""

import argparse
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.cli import parse_bool_arg


def test_parse_bool_arg_true_values():
    assert parse_bool_arg("true") is True
    assert parse_bool_arg("yes") is True
    assert parse_bool_arg("1") is True
    assert parse_bool_arg("TRUE") is True


def test_parse_bool_arg_false_values():
    assert parse_bool_arg("false") is False
    assert parse_bool_arg("no") is False
    assert parse_bool_arg("0") is False
    assert parse_bool_arg("FALSE") is False


def test_parse_bool_arg_invalid_value():
    with pytest.raises(argparse.ArgumentTypeError):
        parse_bool_arg("maybe")


def test_ask_yes_no_arms_and_cancels_the_idle_alert(monkeypatch):
    from utils.cli import ask_yes_no

    class RecordingAlerter:
        def __init__(self):
            self.started = []
            self.cancelled = []

        def start(self, message):
            handle = object()
            self.started.append((handle, message))
            return handle

        def cancel(self, handle):
            self.cancelled.append(handle)

    monkeypatch.setattr("builtins.input", lambda _prompt: "yes")
    alerter = RecordingAlerter()

    assert ask_yes_no("Keep the guest?", alerter=alerter) is True

    assert len(alerter.started) == 1
    assert alerter.started[0][1] == "Keep the guest?"
    assert alerter.cancelled == [alerter.started[0][0]]

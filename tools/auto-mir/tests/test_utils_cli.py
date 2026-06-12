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

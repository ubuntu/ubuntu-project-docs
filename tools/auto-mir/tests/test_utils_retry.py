"""Unit tests for retry utility helpers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.retry import is_transient_command_failure


def test_is_transient_command_failure_true_for_503():
    assert is_transient_command_failure("", "HTTP 503 Service Unavailable") is True


def test_is_transient_command_failure_true_for_dns_error():
    assert (
        is_transient_command_failure("", "Temporary failure resolving archive.ubuntu.com") is True
    )


def test_is_transient_command_failure_false_for_generic_error():
    assert is_transient_command_failure("", "dpkg: error processing package") is False

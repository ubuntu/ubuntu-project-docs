"""Unit tests for retry utility helpers."""

import sys
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.retry import (
    _is_network_url_error,
    is_transient_command_failure,
    retry_rate_limited,
)


def test_is_transient_command_failure_true_for_503():
    assert is_transient_command_failure("", "HTTP 503 Service Unavailable") is True


def test_is_transient_command_failure_true_for_dns_error():
    assert (
        is_transient_command_failure("", "Temporary failure resolving archive.ubuntu.com") is True
    )


def test_is_transient_command_failure_false_for_generic_error():
    assert is_transient_command_failure("", "dpkg: error processing package") is False


# ---------------------------------------------------------------------------
# _is_network_url_error: HTTPError must never be treated as a plain URLError,
# even though urllib.error.HTTPError subclasses urllib.error.URLError.
# ---------------------------------------------------------------------------


def test_is_network_url_error_true_for_plain_url_error():
    assert _is_network_url_error(urllib.error.URLError("Name or service not known")) is True


def test_is_network_url_error_false_for_http_error():
    http_error = urllib.error.HTTPError("http://x", 404, "Not Found", None, None)
    assert _is_network_url_error(http_error) is False


def test_is_network_url_error_false_for_unrelated_exception():
    assert _is_network_url_error(ValueError("nope")) is False


# ---------------------------------------------------------------------------
# retry_rate_limited: HTTPError(404) must fail fast
# (single call, no retries), while 5xx/429 and genuine URLErrors are retried.
# A bogus/expected-404 candidate lookup (e.g. lp-mir-history probing a name
# that was never a real Ubuntu source package) previously cost ~12.5 minutes
# of pointless retries (30/60/120/240/300s backoff) before this fix.
# ---------------------------------------------------------------------------


def _counting_failure(calls: list[int], exc: BaseException):
    def _fn():
        calls.append(1)
        raise exc

    return _fn


@pytest.mark.parametrize("decorator", [retry_rate_limited])
def test_retry_decorators_do_not_retry_on_404(decorator):
    calls: list[int] = []
    http_404 = urllib.error.HTTPError("http://x", 404, "Not Found", None, None)
    fn = decorator(max_attempts=4, base_delay=0.001, max_delay=0.001)(
        _counting_failure(calls, http_404)
    )

    with pytest.raises(urllib.error.HTTPError) as excinfo:
        fn()

    assert excinfo.value.code == 404
    assert len(calls) == 1


@pytest.mark.parametrize(
    "decorator,code",
    [
        (retry_rate_limited, 503),
        (retry_rate_limited, 429),
        (retry_rate_limited, 429),
    ],
)
def test_retry_decorators_retry_on_retryable_status_codes(decorator, code):
    calls: list[int] = []
    http_error = urllib.error.HTTPError("http://x", code, "error", None, None)
    fn = decorator(max_attempts=3, base_delay=0.001, max_delay=0.001)(
        _counting_failure(calls, http_error)
    )

    with pytest.raises(urllib.error.HTTPError) as excinfo:
        fn()

    assert excinfo.value.code == code
    assert len(calls) == 3


@pytest.mark.parametrize("decorator", [retry_rate_limited])
def test_retry_decorators_retry_on_genuine_url_error(decorator):
    calls: list[int] = []
    url_error = urllib.error.URLError("Temporary failure in name resolution")
    fn = decorator(max_attempts=3, base_delay=0.001, max_delay=0.001)(
        _counting_failure(calls, url_error)
    )

    with pytest.raises(urllib.error.URLError):
        fn()

    assert len(calls) == 3


def test_retry_rate_limited_wait_honors_retry_after():
    """When a 429 carries Retry-After, the wait strategy uses it (capped)."""
    from utils.retry import _retry_after_or_exponential

    wait = _retry_after_or_exponential(base_delay=8.0, max_delay=60.0)
    http_error = urllib.error.HTTPError("http://x", 429, "Too Many Requests", None, None)
    http_error.headers = {"Retry-After": "7"}

    class _Outcome:
        def exception(self):
            return http_error

    class _State:
        outcome = _Outcome()

    assert wait(_State()) == 9.0  # 7 + extract_retry_after's 2s buffer

    http_error.headers = {"Retry-After": "120"}
    assert wait(_State()) == 60.0  # capped at max_delay


def test_retry_rate_limited_wait_falls_back_to_exponential_without_retry_after():
    from utils.retry import _retry_after_or_exponential

    wait = _retry_after_or_exponential(base_delay=8.0, max_delay=60.0)

    class _Outcome:
        def exception(self):
            return None

    class _State:
        outcome = _Outcome()
        attempt_number = 1

    assert wait(_State()) == 8.0  # exponential first wait: multiplier * 2^0

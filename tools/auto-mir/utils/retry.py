"""Retry utilities using tenacity.

Provides standardized retry decorators for handling transient failures
in network operations and LXD-guest commands.
"""

from __future__ import annotations

import logging
from typing import Callable

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)

log = logging.getLogger("auto_mir.utils.retry")


TRANSIENT_COMMAND_FAILURE_MARKERS = (
    " 503",
    "http 503",
    "requested url returned error: 503",
    "temporary failure resolving",
    "could not resolve",
    "failed to fetch",
    "connection timed out",
    "connection reset",
    "tls handshake timeout",
    "service unavailable",
    "network is unreachable",
)


# ---------------------------------------------------------------------------
# Retry strategies
# ---------------------------------------------------------------------------


def retry_transient_network(
    max_attempts: int = 4,
    base_delay: float = 2.0,
    max_delay: float = 30.0,
) -> Callable:
    """Decorator for retrying on transient network failures.

    Retries on:
    - ConnectionError
    - TimeoutError
    - urllib.error.URLError
    - urllib.error.HTTPError with 5xx status codes

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        max_delay: Maximum delay in seconds between retries

    Returns:
        Decorated function with retry behavior
    """
    import urllib.error

    def is_transient_http(exc: BaseException) -> bool:
        """Check if exception is a transient HTTP error (5xx)."""
        if isinstance(exc, urllib.error.HTTPError):
            return exc.code >= 500
        return False

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=base_delay, max=max_delay),
        retry=(
            retry_if_exception_type((ConnectionError, TimeoutError, urllib.error.URLError))
            | retry_if_exception(is_transient_http)
        ),
        before_sleep=before_sleep_log(log, logging.WARNING),
        reraise=True,
    )


def retry_rate_limited(
    max_attempts: int = 4,
    base_delay: float = 8.0,
    max_delay: float = 60.0,
) -> Callable:
    """Decorator for retrying with rate limit awareness.

    Specifically designed for API calls that may return 429 (rate limit)
    or 5xx errors. Uses longer delays to respect rate limits.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        max_delay: Maximum delay in seconds between retries

    Returns:
        Decorated function with retry behavior
    """
    import urllib.error

    def is_retryable_http(exc: BaseException) -> bool:
        """Check if exception is a retryable HTTP error (429 or 5xx)."""
        if isinstance(exc, urllib.error.HTTPError):
            return exc.code in (429, 500, 502, 503, 504)
        return False

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=base_delay, max=max_delay),
        retry=(
            retry_if_exception_type((ConnectionError, TimeoutError, urllib.error.URLError))
            | retry_if_exception(is_retryable_http)
        ),
        before_sleep=before_sleep_log(log, logging.WARNING),
        reraise=True,
    )


def retry_guest_command(
    max_attempts: int = 4,
    base_delay: float = 6.0,
    max_delay: float = 60.0,
) -> Callable:
    """Decorator for retrying LXD-guest commands on transient failures.

    Retries when command output indicates transient infrastructure issues
    (503 errors, DNS failures, connection timeouts, etc.).

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        max_delay: Maximum delay in seconds between retries

    Returns:
        Decorated function with retry behavior
    """
    import subprocess

    def is_transient_failure(result: subprocess.CompletedProcess) -> bool:
        """Check if command result indicates transient failure."""
        if result.returncode == 0:
            return False
        return is_transient_command_failure(result.stdout, result.stderr)

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=base_delay, max=max_delay),
        retry=retry_if_result(is_transient_failure),
        before_sleep=before_sleep_log(log, logging.WARNING),
    )


def is_transient_command_failure(stdout: str | None, stderr: str | None) -> bool:
    """Return True when command output matches known transient infra failures."""
    text = f"{stdout or ''}\n{stderr or ''}".lower()
    return any(marker in text for marker in TRANSIENT_COMMAND_FAILURE_MARKERS)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def extract_retry_after(exc: BaseException) -> float | None:
    """Extract Retry-After delay from HTTP exception if present.

    Args:
        exc: Exception that may contain Retry-After header

    Returns:
        Delay in seconds, or None if not found
    """
    import re
    import urllib.error

    if not isinstance(exc, urllib.error.HTTPError):
        return None

    # Check Retry-After header
    try:
        retry_after = exc.headers.get("Retry-After") or exc.headers.get("retry-after")
        if retry_after:
            return float(retry_after) + 2.0  # Add buffer
    except (ValueError, AttributeError):
        pass

    # Check response body for "please wait N seconds"
    try:
        body = exc.read().decode(errors="replace")
        match = re.search(r"please wait (\d+) seconds", body, re.IGNORECASE)
        if match:
            return float(match.group(1)) + 2.0
    except Exception:
        pass

    return None

"""Retry utilities using tenacity.

Provides standardized retry decorators for handling transient failures
in network operations and LXD-guest commands.
"""

from __future__ import annotations

import logging
import urllib.error
from typing import Callable

from tenacity import (
    retry,
    retry_if_exception,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)

log = logging.getLogger("auto_mir.utils.retry")

# Cap how much of a retried URL / error text appears in one log line: these
# messages exist to tell the user *which* fetch is stuck and *where* in the
# retry budget it is, not to duplicate whole URLs or error bodies.
_TARGET_URL_LIMIT = 100
_ERROR_TEXT_LIMIT = 200


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


def _is_network_url_error(exc: BaseException) -> bool:
    """Check if exception is a genuine network-level URLError (DNS, connection).

    ``urllib.error.HTTPError`` is a subclass of ``URLError``, so a plain
    ``isinstance(exc, URLError)`` check also matches every HTTPError regardless
    of status code - silently retrying on 4xx client errors (401/403/404/...)
    that a caller's own status-code predicate deliberately excludes. This
    predicate returns True only for URLErrors that are *not* HTTPErrors (e.g.
    DNS failures, connection refused), so HTTP status-code gating stays the
    sole authority over whether an HTTP response is retried.
    """
    return isinstance(exc, urllib.error.URLError) and not isinstance(exc, urllib.error.HTTPError)


# ---------------------------------------------------------------------------
# Retry strategies
# ---------------------------------------------------------------------------


def _retry_after_or_exponential(base_delay: float, max_delay: float) -> Callable:
    """Tenacity wait strategy: honor Retry-After when present, else back off.

    This is the single retry scheme for rate-limited HTTP calls: the
    provider's Retry-After header (or a "please wait N seconds" body hint,
    via extract_retry_after) wins over the exponential schedule, capped at
    max_delay.
    """
    exponential = wait_exponential(multiplier=base_delay, max=max_delay)

    def wait(retry_state):
        outcome = retry_state.outcome
        exc = outcome.exception() if outcome is not None else None
        if exc is not None:
            retry_after = extract_retry_after(exc)
            if retry_after:
                return min(retry_after, max_delay)
        return exponential(retry_state)

    return wait


def _retry_target_name(retry_state) -> str:
    """Describe what is being retried: function name plus URL when visible.

    Only a ``str`` first argument that starts with ``http`` is included -
    HTTP evidence-fetch URLs are public service endpoints, while the LLM
    path's first argument is the prompt, which must never be echoed into
    the log. Internal ``*_impl`` helpers (the per-call retry pattern, see
    ``llm._call_openai_compatible`` and ``utils.http``) are displayed by
    their public wrapper's name.
    """
    fn = retry_state.fn
    name = getattr(fn, "__name__", str(fn))
    if name.endswith("_impl"):
        name = name[: -len("_impl")]
    name = name.lstrip("_")
    args = retry_state.args or ()
    if args and isinstance(args[0], str) and args[0].startswith("http"):
        url = args[0]
        if len(url) > _TARGET_URL_LIMIT:
            url = url[: _TARGET_URL_LIMIT - 3] + "..."
        return f"{name} ({url})"
    return name


def _short_error(exc: BaseException | None) -> str:
    text = f"{type(exc).__name__}: {exc}" if exc is not None else "unknown error"
    if len(text) > _ERROR_TEXT_LIMIT:
        text = text[: _ERROR_TEXT_LIMIT - 3] + "..."
    return text


def _retry_reason(retry_state) -> str:
    """Why the attempt is being retried: exception or result description.

    Exception-driven strategies (HTTP/LLM) carry the error; result-driven
    strategies (guest commands retrying on transient output) carry the
    failing command result instead.
    """
    outcome = retry_state.outcome
    if outcome is None:
        return "unknown error"
    exc = outcome.exception()
    if exc is not None:
        return _short_error(exc)
    text = f"transient command failure: {outcome.result()!r}"
    if len(text) > _ERROR_TEXT_LIMIT:
        text = text[: _ERROR_TEXT_LIMIT - 3] + "..."
    return text


def _progress_before_sleep(logger, max_attempts: int) -> Callable:
    """Tenacity ``before_sleep`` logging each wait with its retry budget.

    A bare "Retrying fn in N seconds" line (tenacity's default) tells the
    user neither which fetch is stuck nor how close the budget is to
    exhaustion - which is exactly what a reporter watching a service outage
    needs to decide whether to keep waiting.
    """

    def before_sleep(retry_state) -> None:
        delay = getattr(retry_state.next_action, "sleep", 0.0)
        # ponytail: attempt counts assume exception-driven retries; result-
        # based strategies (retry_guest_command) keep the same shape but their
        # give-up is logged by the caller, not here.
        total_retries = max(1, max_attempts - 1)
        logger.warning(
            "Retrying %s [retry %d/%d] in %.1f seconds: %s",
            _retry_target_name(retry_state),
            retry_state.attempt_number,
            total_retries,
            delay,
            _retry_reason(retry_state),
        )

    return before_sleep


def _give_up_after(logger, max_attempts: int) -> Callable:
    """Tenacity ``after`` logging one explicit line when the budget is spent.

    Without it, the transition from "still retrying" to "gave up" only
    exists implicitly: the next log entry is the caller's adapter error.
    """

    def after(retry_state) -> None:
        outcome = retry_state.outcome
        if outcome is not None and outcome.failed and retry_state.attempt_number >= max_attempts:
            logger.warning(
                "Giving up on %s after %d attempts: %s",
                _retry_target_name(retry_state),
                max_attempts,
                _short_error(outcome.exception()),
            )

    return after


def retry_rate_limited(
    max_attempts: int = 4,
    base_delay: float = 8.0,
    max_delay: float = 60.0,
) -> Callable:
    """Decorator for retrying with rate limit awareness.

    Specifically designed for API calls that may return 429 (rate limit)
    or 5xx errors. Honors the provider's Retry-After when present and
    otherwise uses longer exponential delays to respect rate limits. Each
    wait is logged with its retry budget (``[retry k/N]``), and exhausting
    the attempts is logged as an explicit "giving up" line before the
    exception is reraised.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        max_delay: Maximum delay in seconds between retries

    Returns:
        Decorated function with retry behavior
    """

    def is_retryable_http(exc: BaseException) -> bool:
        """Check if exception is a retryable HTTP error (429 or 5xx)."""
        if isinstance(exc, urllib.error.HTTPError):
            return exc.code in (429, 500, 502, 503, 504)
        return False

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=_retry_after_or_exponential(base_delay, max_delay),
        retry=(
            retry_if_exception_type((ConnectionError, TimeoutError))
            | retry_if_exception(_is_network_url_error)
            | retry_if_exception(is_retryable_http)
        ),
        before_sleep=_progress_before_sleep(log, max_attempts),
        after=_give_up_after(log, max_attempts),
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
        before_sleep=_progress_before_sleep(log, max_attempts),
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

"""Shared HTTP helpers with resilient retry behavior."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from utils.retry import retry_rate_limited

# The ``ubuntu/`` prefix identifies this as Ubuntu project tooling; some
# services (e.g. autopkgtest) grant ``ubuntu/*`` clients more generous rate
# limits than an anonymous agent.
_DEFAULT_USER_AGENT = "ubuntu/auto-mir/0.1"
_DEFAULT_TIMEOUT_SECONDS = 300

# Every HTTP evidence fetch retries with exponential backoff (honoring the
# server's Retry-After) on 429/5xx and network errors; these are the
# defaults. A run overrides them via configure_http_retries() from the
# --http-retry-* CLI options, which is why the retry policy is built per
# call rather than at import time (same pattern as the LLM path's
# --llm-retry-base-delay). With the defaults, a persistently failing fetch
# waits 30+60+120+240+300 = 750 seconds (~13 minutes) across 6 attempts
# before giving up - visible in the log as [retry k/5] lines.
_HTTP_RETRY_CONFIG: dict[str, float] = {
    "attempts": 6,
    "base_delay": 30.0,
    "max_delay": 300.0,
}


def configure_http_retries(
    *, attempts: int | None = None, base_delay: float | None = None, max_delay: float | None = None
) -> None:
    """Override the HTTP retry defaults for the rest of the process.

    Called once from ``auto_mir.main`` with the parsed ``--http-retry-*``
    options, before any evidence collection runs. ``None`` leaves a value
    unchanged; an attempt count below 1 is rejected (a fetch must always be
    tried at least once).
    """
    if attempts is not None:
        if attempts < 1:
            raise ValueError("http retry attempts must be at least 1")
        _HTTP_RETRY_CONFIG["attempts"] = int(attempts)
    if base_delay is not None:
        _HTTP_RETRY_CONFIG["base_delay"] = float(base_delay)
    if max_delay is not None:
        _HTTP_RETRY_CONFIG["max_delay"] = float(max_delay)


def _retry_with_current_config(fetch):
    """Apply the current retry policy to one undecorated fetch function."""
    return retry_rate_limited(
        max_attempts=_HTTP_RETRY_CONFIG["attempts"],
        base_delay=_HTTP_RETRY_CONFIG["base_delay"],
        max_delay=_HTTP_RETRY_CONFIG["max_delay"],
    )(fetch)


def _get_bytes_impl(url: str, *, timeout: int = _DEFAULT_TIMEOUT_SECONDS) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _DEFAULT_USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def get_bytes(url: str, *, timeout: int = _DEFAULT_TIMEOUT_SECONDS) -> bytes:
    """Fetch raw bytes from a URL with uniform retry/backoff policy."""
    retried = _retry_with_current_config(_get_bytes_impl)
    return retried(url, timeout=timeout)


# Existence checks are a best-effort sanity check on a URL the tool is about
# to *suggest* to a human, not a critical data fetch -- deliberately NOT
# wrapped in the retry policy (which can take up to ~6 attempts over several
# minutes). A single slow/unreachable link should fail fast so the caller can
# fall back to asking the reporter, not stall the run.
_URL_EXISTS_TIMEOUT_SECONDS = 10.0


def get_text(
    url: str,
    *,
    timeout: int = _DEFAULT_TIMEOUT_SECONDS,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> str:
    """Fetch and decode text from a URL with uniform retry/backoff policy."""
    return get_bytes(url, timeout=timeout).decode(encoding, errors)


def get_json(url: str, *, timeout: int = _DEFAULT_TIMEOUT_SECONDS) -> Any:
    """Fetch and decode JSON from a URL with uniform retry/backoff policy."""
    return json.loads(get_text(url, timeout=timeout))


def _download_to_file_impl(
    url: str, dest_path: str | Path, *, timeout: int = _DEFAULT_TIMEOUT_SECONDS
) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": _DEFAULT_USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        Path(dest_path).write_bytes(resp.read())


def download_to_file(
    url: str, dest_path: str | Path, *, timeout: int = _DEFAULT_TIMEOUT_SECONDS
) -> None:
    """Download URL content and write it directly to a file path."""
    retried = _retry_with_current_config(_download_to_file_impl)
    retried(url, dest_path, timeout=timeout)


def check_url_exists(url: str, *, timeout: float = _URL_EXISTS_TIMEOUT_SECONDS) -> bool:
    """Best-effort check that ``url`` actually resolves before it is suggested.

    Tries a HEAD request first (cheapest: no response body). Some servers
    reject HEAD (405/501) even though the resource exists, so those two
    codes fall back to a single GET. Any other outcome -- a real 404/4xx/5xx,
    a connection failure, or a timeout -- is treated as "does not exist"
    rather than retried: this is a quick sanity check on a URL about to be
    shown to a human, not a critical fetch, so failing fast and letting the
    caller fall back to asking the reporter is preferable to a multi-minute
    retry storm on one broken link.
    """
    if not url:
        return False
    request = urllib.request.Request(url, headers={"User-Agent": _DEFAULT_USER_AGENT})
    request.get_method = lambda: "HEAD"
    try:
        with urllib.request.urlopen(request, timeout=timeout):
            return True
    except urllib.error.HTTPError as exc:
        if exc.code not in (405, 501):
            return False
    except (urllib.error.URLError, TimeoutError, OSError):
        return False

    get_request = urllib.request.Request(url, headers={"User-Agent": _DEFAULT_USER_AGENT})
    try:
        with urllib.request.urlopen(get_request, timeout=timeout):
            return True
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
        return False

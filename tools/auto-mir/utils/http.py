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
_RETRY_ATTEMPTS = 6
_RETRY_BASE_DELAY = 30.0
_RETRY_MAX_DELAY = 300.0

# Existence checks are a best-effort sanity check on a URL the tool is about
# to *suggest* to a human, not a critical data fetch -- deliberately NOT
# wrapped in @retry_rate_limited (which can take up to ~self._RETRY_ATTEMPTS
# attempts over several minutes). A single slow/unreachable link should fail
# fast so the caller can fall back to asking the reporter, not stall the run.
_URL_EXISTS_TIMEOUT_SECONDS = 10.0


@retry_rate_limited(
    max_attempts=_RETRY_ATTEMPTS,
    base_delay=_RETRY_BASE_DELAY,
    max_delay=_RETRY_MAX_DELAY,
)
def get_bytes(url: str, *, timeout: int = _DEFAULT_TIMEOUT_SECONDS) -> bytes:
    """Fetch raw bytes from a URL with uniform retry/backoff policy."""
    req = urllib.request.Request(url, headers={"User-Agent": _DEFAULT_USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


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


@retry_rate_limited(
    max_attempts=_RETRY_ATTEMPTS,
    base_delay=_RETRY_BASE_DELAY,
    max_delay=_RETRY_MAX_DELAY,
)
def download_to_file(
    url: str, dest_path: str | Path, *, timeout: int = _DEFAULT_TIMEOUT_SECONDS
) -> None:
    """Download URL content and write it directly to a file path."""
    req = urllib.request.Request(url, headers={"User-Agent": _DEFAULT_USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        Path(dest_path).write_bytes(resp.read())


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

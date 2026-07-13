"""Shared HTTP helpers with resilient retry behavior."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any

from utils.retry import retry_rate_limited

_DEFAULT_USER_AGENT = "auto-mir/0.1"
_DEFAULT_TIMEOUT_SECONDS = 300
_RETRY_ATTEMPTS = 6
_RETRY_BASE_DELAY = 30.0
_RETRY_MAX_DELAY = 300.0


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

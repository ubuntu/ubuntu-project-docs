"""LLM adapter for auto-mir.

Provides a single call_llm() entry point that dispatches to the configured
provider.  Currently only the 'copilot' provider is implemented, using the
GitHub Copilot chat-completions API.

Design constraints:
- No streaming; we want a complete JSON response before proceeding.
- Caller is always responsible for interpreting the response; this module
  only handles HTTP, auth, retries, and JSON extraction.
- Never logs token values.
- Returns a parsed dict on success or raises LLMError on failure.
"""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from typing import Any

log = logging.getLogger("auto_mir.llm")

# GitHub Copilot chat-completions endpoint
class LLMError(RuntimeError):
    """Raised when the LLM call cannot produce a usable response."""


# GitHub Models inference endpoint — works with a standard GitHub PAT that has
# been granted access to GitHub Models (https://github.com/marketplace/models).
_COPILOT_API_URL = "https://models.inference.ai.azure.com/chat/completions"

# gpt-4o-mini: 15 req/min rate limit (vs 10 for gpt-4o); sufficient for JSON tasks.
_COPILOT_MODEL = "gpt-4o-mini"
# Hard cap on response tokens — JSON responses for MIR checks are compact.
_MAX_TOKENS = 1024
# Retry attempts on transient HTTP errors (429, 5xx).
_MAX_RETRIES = 4
# Base delay between retries; actual delay is taken from 429 body when available.
_RETRY_DELAY_S = 8
# Minimum gap between consecutive LLM calls to stay under 15/min rate limit.
_MIN_CALL_INTERVAL_S = 4.5
# Module-level timestamp of the last successful call for rate-limit pacing.
_last_call_time: float = 0.0

def call_llm(prompt: str, ctx) -> dict[str, Any]:
    """Call the configured LLM provider and return the parsed JSON response.

    Args:
        prompt:  The fully-rendered prompt string to send as the user message.
        ctx:     RunContext — used to determine provider and retrieve token.

    Returns:
        Parsed JSON dict from the LLM response content.

    Raises:
        LLMError: on auth failure, HTTP error, or invalid JSON in response.
    """
    provider = getattr(ctx, "llm_provider", "copilot").lower()
    if provider == "copilot":
        return _call_copilot(prompt, ctx)
    raise LLMError(f"Unknown LLM provider: {provider!r}")


# ---------------------------------------------------------------------------
# Copilot provider
# ---------------------------------------------------------------------------

def _call_copilot(prompt: str, ctx) -> dict[str, Any]:
    """Call GitHub Copilot chat-completions and return parsed JSON."""
    token = _get_copilot_token(ctx)
    if not token:
        raise LLMError(
            "No GitHub token available for Copilot calls. "
            "Ensure COPILOT_GITHUB_TOKEN / GH_TOKEN / GITHUB_TOKEN is set "
            "or that `gh auth status` succeeds."
        )

    payload = {
        "model": _COPILOT_MODEL,
        "max_tokens": _MAX_TOKENS,
        "temperature": 0.0,   # Determinism — same evidence should yield same assessment
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert Ubuntu package reviewer assisting with MIR "
                    "(Main Inclusion Review) checks. "
                    "Return only valid JSON matching the exact schema provided in the prompt. "
                    "Do not include markdown fences, explanations, or extra keys."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }

    body = json.dumps(payload).encode()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    import time
    global _last_call_time
    last_err: Exception | None = None
    # Pace calls to stay under the per-minute rate limit.
    elapsed = time.time() - _last_call_time
    if elapsed < _MIN_CALL_INTERVAL_S:
        time.sleep(_MIN_CALL_INTERVAL_S - elapsed)

    for attempt in range(1, _MAX_RETRIES + 1):
        req = urllib.request.Request(
            _COPILOT_API_URL,
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode()
            _last_call_time = time.time()
            return _extract_json(raw)
        except urllib.error.HTTPError as exc:
            status = exc.code
            err_body = exc.read().decode(errors="replace")
            log.debug("Copilot HTTP %d on attempt %d: %s", status, attempt, err_body[:200])
            if status in (429, 500, 502, 503, 504) and attempt < _MAX_RETRIES:
                wait = _parse_retry_after(err_body) or _RETRY_DELAY_S
                log.warning(
                    "Copilot returned %d (attempt %d/%d), retrying in %ds",
                    status, attempt, _MAX_RETRIES, wait,
                )
                time.sleep(wait)
                last_err = exc
                continue
            raise LLMError(
                f"Copilot API returned HTTP {status}: {err_body[:400]}"
            ) from exc
        except urllib.error.URLError as exc:
            raise LLMError(f"Copilot API network error: {exc}") from exc

    raise LLMError(
        f"Copilot API failed after {_MAX_RETRIES} retries"
    ) from last_err


def _get_copilot_token(ctx) -> str:
    """Retrieve GitHub token from context container_env or host environment."""
    import os
    # ctx.container_env is populated by stage_auth with the resolved token.
    for key in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        value = (getattr(ctx, "container_env", {}) or {}).get(key)
        if value:
            return value
        value = os.environ.get(key)
        if value:
            return value
    return ""


def _extract_json(raw_response: str) -> dict[str, Any]:
    """Extract the JSON content from a chat-completions API response.

    The response is the full OpenAI-compatible response envelope; we extract
    choices[0].message.content and parse that as JSON (the model's actual reply).
    """
    try:
        envelope = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise LLMError(f"Copilot API response is not valid JSON: {exc}") from exc

    try:
        content = envelope["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError(
            f"Unexpected Copilot API response shape: {exc}\n"
            f"Envelope keys: {list(envelope.keys())}"
        ) from exc

    # Strip any accidental markdown fences the model may have added
    content = _strip_fences(content)

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise LLMError(
            f"Model response is not valid JSON: {exc}\nContent: {content[:400]}"
        ) from exc


def _strip_fences(text: str) -> str:
    """Remove ```json ... ``` fences from model output if present."""
    text = text.strip()
    # Match optional language tag after opening fence
    match = re.match(r"^```(?:json)?\s*([\s\S]*?)```\s*$", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


def _parse_retry_after(body: str) -> int | None:
    """Parse the recommended wait time in seconds from a 429 error body.

    GitHub Models returns messages like:
    "Rate limit of 10 per 60s exceeded ... Please wait 27 seconds before retrying."
    """
    match = re.search(r"please wait (\d+) seconds", body, re.IGNORECASE)
    if match:
        return int(match.group(1)) + 2  # small buffer
    return None

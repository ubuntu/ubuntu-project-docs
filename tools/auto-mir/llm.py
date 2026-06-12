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
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

log = logging.getLogger("auto_mir.llm")

# GitHub Copilot chat-completions endpoint
class LLMError(RuntimeError):
    """Raised when the LLM call cannot produce a usable response."""


# GitHub Models inference endpoint — works with a standard GitHub PAT that has
# been granted access to GitHub Models (https://github.com/marketplace/models).
_COPILOT_API_URL = "https://models.inference.ai.azure.com/chat/completions"

# Concrete default model for the GitHub Models endpoint.
_DEFAULT_COPILOT_MODEL = "gpt-4o-mini"
# Hard cap on response tokens — JSON responses for MIR checks are compact.
_MAX_TOKENS = 1024
# Retry attempts on transient HTTP errors (429, 5xx).
_MAX_RETRIES = 4
# Base delay between retries; actual delay is taken from 429 body when available.
_RETRY_DELAY_S = 8
# Conservative defaults until we learn real values from API responses.
_DEFAULT_LIMIT_PER_WINDOW = 10
_DEFAULT_WINDOW_SECONDS = 60
_RATE_SAFETY_FACTOR = 1.10
_WAIT_BUFFER_SECONDS = 2


@dataclass
class _RateLimitState:
    limit: int = _DEFAULT_LIMIT_PER_WINDOW
    window_s: int = _DEFAULT_WINDOW_SECONDS
    min_interval_s: float = (_DEFAULT_WINDOW_SECONDS / _DEFAULT_LIMIT_PER_WINDOW) * _RATE_SAFETY_FACTOR
    next_allowed_at: float = 0.0


# Per-model adaptive limiter state.
_rate_limit_by_model: dict[str, _RateLimitState] = {}

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
    return _call_copilot(prompt, ctx)


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

    model = _selected_model(ctx)
    limiter = _get_rate_limiter(model)

    payload = {
        "model": model,
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

    last_err: Exception | None = None

    for attempt in range(1, _MAX_RETRIES + 1):
        _wait_for_slot(limiter)
        req = urllib.request.Request(
            _COPILOT_API_URL,
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode()
                _learn_from_headers(limiter, resp.headers)
                limiter.next_allowed_at = max(
                    limiter.next_allowed_at,
                    time.time() + limiter.min_interval_s,
                )
            return _extract_json(raw)
        except urllib.error.HTTPError as exc:
            status = exc.code
            err_body = exc.read().decode(errors="replace")
            log.debug("Copilot HTTP %d on attempt %d: %s", status, attempt, err_body[:200])
            _learn_from_headers(limiter, exc.headers)

            if status in (429, 500, 502, 503, 504) and attempt < _MAX_RETRIES:
                if status == 429:
                    learned = _parse_rate_limit_hint(err_body)
                    if learned:
                        limiter.limit, limiter.window_s = learned
                        limiter.min_interval_s = (limiter.window_s / limiter.limit) * _RATE_SAFETY_FACTOR
                        log.info(
                            "Learned rate limit for model %s: %d per %ds (min interval %.2fs)",
                            model,
                            limiter.limit,
                            limiter.window_s,
                            limiter.min_interval_s,
                        )

                wait = _parse_retry_after(err_body, exc.headers) or _RETRY_DELAY_S
                limiter.next_allowed_at = max(limiter.next_allowed_at, time.time() + wait)
                log.warning(
                    "Copilot model=%s returned %d (attempt %d/%d), retrying in %ds",
                    model,
                    status,
                    attempt,
                    _MAX_RETRIES,
                    wait,
                )
                log.debug(
                    "Rate-limit backoff sleep engaged for model %s: sleeping %.2fs",
                    model,
                    float(wait),
                )
                time.sleep(wait)
                last_err = exc
                continue
            raise LLMError(
                f"Copilot API model={model} returned HTTP {status}: {err_body[:400]}"
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


def _selected_model(ctx) -> str:
    """Return the configured model name for this run.

    Priority:
    1) ctx.llm_model (from --llm-model)
    2) provider default
    """
    explicit = (getattr(ctx, "llm_model", "") or "").strip()
    if explicit:
        return explicit

    return _DEFAULT_COPILOT_MODEL


def _get_rate_limiter(model: str) -> _RateLimitState:
    state = _rate_limit_by_model.get(model)
    if state is None:
        state = _RateLimitState()
        _rate_limit_by_model[model] = state
    return state


def _wait_for_slot(limiter: _RateLimitState) -> None:
    """Sleep until we are allowed to send the next request for this model."""
    now = time.time()
    if limiter.next_allowed_at > now:
        sleep_s = limiter.next_allowed_at - now
        log.debug("Rate-limit pacing sleep engaged: sleeping %.2fs", sleep_s)
        time.sleep(sleep_s)


def _learn_from_headers(limiter: _RateLimitState, headers) -> None:
    """Best-effort learning from rate-limit response headers.

    Some providers expose x-ratelimit-limit / x-ratelimit-reset headers. If
    present, we use them. Missing headers are fine.
    """
    if not headers:
        return

    try:
        limit_val = headers.get("x-ratelimit-limit") or headers.get("X-RateLimit-Limit")
        reset_val = headers.get("x-ratelimit-reset") or headers.get("X-RateLimit-Reset")
    except Exception:
        return

    if limit_val:
        try:
            parsed_limit = int(limit_val)
            # Guardrail: request-per-window limits are expected to be modest.
            # Large values (e.g. 60000) are typically token quotas, not request rates.
            if 0 < parsed_limit <= 500:
                limiter.limit = parsed_limit
        except ValueError:
            pass

    if reset_val:
        # Reset can be epoch seconds or duration. We only use it as a hint for
        # future pacing when it clearly looks like a duration.
        try:
            parsed_reset = int(reset_val)
            if 0 < parsed_reset <= 3600:
                limiter.window_s = parsed_reset
        except ValueError:
            pass

    limiter.min_interval_s = (limiter.window_s / limiter.limit) * _RATE_SAFETY_FACTOR


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


def _parse_retry_after(body: str, headers=None) -> int | None:
    """Parse retry delay from headers or body.

    Preference order:
    1) Retry-After header
    2) Message text: "Please wait N seconds before retrying"
    """
    if headers:
        try:
            retry_after = headers.get("Retry-After") or headers.get("retry-after")
        except Exception:
            retry_after = None
        if retry_after:
            try:
                return int(retry_after) + _WAIT_BUFFER_SECONDS
            except ValueError:
                pass

    match = re.search(r"please wait (\d+) seconds", body, re.IGNORECASE)
    if match:
        return int(match.group(1)) + _WAIT_BUFFER_SECONDS
    return None


def _parse_rate_limit_hint(body: str) -> tuple[int, int] | None:
    """Parse limit/window from a 429 message.

    Example:
      "Rate limit of 10 per 60s exceeded for UserByModelByMinute..."
    Returns:
      (10, 60)
    """
    match = re.search(r"rate limit of\s+(\d+)\s+per\s+(\d+)s", body, re.IGNORECASE)
    if not match:
        return None
    limit = int(match.group(1))
    window_s = int(match.group(2))
    # Guardrails: request-rate hints are expected to be modest. Very large
    # values are usually token quotas and should not drive request pacing.
    if limit <= 0 or window_s <= 0 or limit > 500 or window_s > 3600:
        return None
    return limit, window_s

"""LLM adapter for auto-mir.

Provides a single call_llm() entry point using an OpenAI-compatible
chat-completions API.

Provider
--------
openai-compatible
        Any OpenAI-compatible endpoint, including OpenRouter.
        Auth: OPENAI_API_KEY.
        Base URL: OPENAI_API_BASE (default: https://api.openai.com/v1).
        Default models: small=z-ai/glm-4.7, large=z-ai/glm-5.2
        (OpenRouter names; override via --llm-model-small / --llm-model-large).

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
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from utils.retry import extract_retry_after, retry_rate_limited

log = logging.getLogger("auto_mir.llm")

# OpenAI-compatible (OpenRouter and others) defaults.
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_OPENAI_COMPAT_SMALL_MODEL = "z-ai/glm-4.7"
DEFAULT_OPENAI_COMPAT_LARGE_MODEL = "z-ai/glm-5.2"

DEFAULT_TIMEOUT_SECONDS = 60


class LLMError(RuntimeError):
    """Raised when the LLM call cannot produce a usable response."""


# Hard cap on response tokens — JSON responses for MIR checks are compact.
_MAX_TOKENS = 1024
# Conservative defaults until we learn real values from API responses.
_DEFAULT_LIMIT_PER_WINDOW = 10
_DEFAULT_WINDOW_SECONDS = 60
_RATE_SAFETY_FACTOR = 1.10


@dataclass
class _RateLimitState:
    limit: int = _DEFAULT_LIMIT_PER_WINDOW
    window_s: int = _DEFAULT_WINDOW_SECONDS
    min_interval_s: float = (
        _DEFAULT_WINDOW_SECONDS / _DEFAULT_LIMIT_PER_WINDOW
    ) * _RATE_SAFETY_FACTOR
    next_allowed_at: float = 0.0


# Per-model adaptive limiter state.
_rate_limit_by_model: dict[str, _RateLimitState] = {}


def call_llm(prompt: str, ctx, model_tier: str = "small") -> dict[str, Any]:
    """Call the configured LLM provider and return the parsed JSON response.

    Args:
        prompt:  The fully-rendered prompt string to send as the user message.
        ctx:     RunContext — used to determine provider, URL, and token.
                 ctx.llm_provider, ctx.llm_api_url, ctx.llm_token must be
                 populated by stage_auth before calling this function.

    Returns:
        Parsed JSON dict from the LLM response content.

    Raises:
        LLMError: on auth failure, HTTP error, or invalid JSON in response.
    """
    try:
        response_dict = _call_openai_compatible(prompt, ctx, model_tier=model_tier)
    except urllib.error.HTTPError as exc:
        # Retries exhausted, convert to LLMError
        status = exc.code
        err_body = _http_error_body(exc)
        model = _selected_model(ctx, model_tier)
        provider = getattr(ctx, "llm_provider", "unknown")
        raise LLMError(
            f"LLM provider={provider} model={model} returned HTTP {status}: {err_body[:400]}"
        ) from exc
    except urllib.error.URLError as exc:
        provider = getattr(ctx, "llm_provider", "unknown")
        raise LLMError(f"LLM provider={provider} network error: {exc}") from exc

    # Track LLM usage for cost/efficiency reporting
    model = _selected_model(ctx, model_tier)
    if not hasattr(ctx, "llm_calls_by_model"):
        ctx.llm_calls_by_model = {}
        ctx.llm_estimated_tokens = {}
    ctx.llm_calls_by_model[model] = ctx.llm_calls_by_model.get(model, 0) + 1
    # Rough estimate: prompt words + response tokens
    estimated_total = len(prompt.split()) + _MAX_TOKENS
    ctx.llm_estimated_tokens[model] = ctx.llm_estimated_tokens.get(model, 0) + estimated_total

    return response_dict


def _http_error_body(exc: urllib.error.HTTPError) -> str:
    """Read HTTPError body safely without leaking exceptions to callers."""
    try:
        return exc.read().decode(errors="replace")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Shared OpenAI-compatible provider
# ---------------------------------------------------------------------------


@retry_rate_limited(max_attempts=4, base_delay=8.0, max_delay=60.0)
def _call_openai_compatible(prompt: str, ctx, model_tier: str) -> dict[str, Any]:
    """Call an OpenAI-compatible chat-completions endpoint and return parsed JSON.

    Reads ctx.llm_api_url and ctx.llm_token, both populated by stage_auth.

    Raises:
        LLMError: On non-retryable errors (auth failure, non-5xx HTTP errors)
        urllib.error.HTTPError: On retryable HTTP errors (429, 5xx) - will trigger retry
    """
    token = getattr(ctx, "llm_token", "") or ""
    api_url = getattr(ctx, "llm_api_url", "") or f"{DEFAULT_OPENAI_BASE_URL}/chat/completions"
    provider = getattr(ctx, "llm_provider", "openai-compatible")

    if not token:
        raise LLMError(
            f"No authentication token found for LLM provider '{provider}'. Set OPENAI_API_KEY."
        )

    model = _selected_model(ctx, model_tier)
    limiter = _get_rate_limiter(model)

    payload = {
        "model": model,
        "max_tokens": _MAX_TOKENS,
        "temperature": 0.0,  # Determinism — same evidence should yield same assessment
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

    _wait_for_slot(limiter)
    req = urllib.request.Request(
        api_url,
        data=body,
        headers=headers,
        method="POST",
    )

    try:
        timeout = getattr(ctx, "llm_timeout", DEFAULT_TIMEOUT_SECONDS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
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
        log.debug("LLM HTTP %d: %s", status, err_body[:200])
        _learn_from_headers(limiter, exc.headers)

        # Update rate limiter based on 429 response
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

            # Extract Retry-After if present
            retry_after = extract_retry_after(exc)
            if retry_after:
                limiter.next_allowed_at = max(limiter.next_allowed_at, time.time() + retry_after)

        # Re-raise for tenacity to handle (will retry on 429/5xx)
        raise


def _selected_model(ctx, model_tier: str = "small") -> str:
    """Return the configured model name for the selected tier.

    Priority:
    1) Tier-specific CLI override (ctx.llm_model_small / ctx.llm_model_large)
    2) OpenAI-compatible defaults:
        - small: z-ai/glm-4.7
        - large: z-ai/glm-5.2
    """
    if model_tier not in {"small", "large"}:
        raise LLMError(f"Invalid model tier: {model_tier}")

    if model_tier == "small":
        explicit = (getattr(ctx, "llm_model_small", "") or "").strip()
        if explicit:
            return explicit
        return DEFAULT_OPENAI_COMPAT_SMALL_MODEL

    explicit = (getattr(ctx, "llm_model_large", "") or "").strip()
    if explicit:
        return explicit
    return DEFAULT_OPENAI_COMPAT_LARGE_MODEL


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
        raise LLMError(f"LLM API response is not valid JSON: {exc}") from exc

    try:
        content = envelope["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError(
            f"Unexpected LLM API response shape: {exc}\nEnvelope keys: {list(envelope.keys())}"
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


# ---------------------------------------------------------------------------
# Auth resolution
# ---------------------------------------------------------------------------


def resolve_auth() -> tuple[str, str | None, str, str]:
    """Resolve LLM provider, token, source label, and API URL.

    Returns:
        (provider, token, source, api_url)

        provider  — "openai-compatible"
        token     — auth token string, or None if none found
        source    — human-readable source label for logging
        api_url   — full chat-completions endpoint URL

    Returns token=None when OPENAI_API_KEY is unavailable; caller handles hard-fail.
    """

    def _openai_token_from_env() -> tuple[str | None, str, str]:
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            return None, "", ""
        base = os.environ.get("OPENAI_API_BASE", DEFAULT_OPENAI_BASE_URL).rstrip("/")
        api_url = f"{base}/chat/completions"
        return key, "host-env:OPENAI_API_KEY", api_url

    token, source, api_url = _openai_token_from_env()
    return "openai-compatible", token, source, api_url

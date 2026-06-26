"""Tests for LLM model tier selection and response parsing behavior."""

import json
import logging
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import llm
from auto_mir import build_parser


def test_build_parser_accepts_new_model_flags():
    parser = build_parser()
    args = parser.parse_args(["123", "--llm-model-small", "foo", "--llm-model-large", "bar"])

    assert args.llm_model_small == "foo"
    assert args.llm_model_large == "bar"


def test_build_parser_rejects_removed_single_model_flag():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["123", "--llm-model", "gpt-4.1-mini"])


def test_selected_model_defaults_for_openai_compatible():
    ctx = SimpleNamespace(llm_model_small=None, llm_model_large=None)
    assert llm._selected_model(ctx, "small") == llm.DEFAULT_OPENAI_COMPAT_SMALL_MODEL
    assert llm._selected_model(ctx, "large") == llm.DEFAULT_OPENAI_COMPAT_LARGE_MODEL


def test_selected_model_prefers_explicit_overrides():
    ctx = SimpleNamespace(
        llm_model_small="openai/custom-small",
        llm_model_large="openai/custom-large",
    )

    assert llm._selected_model(ctx, "small") == "openai/custom-small"
    assert llm._selected_model(ctx, "large") == "openai/custom-large"


def test_selected_model_invalid_tier_raises():
    ctx = SimpleNamespace(llm_model_small=None, llm_model_large=None)

    with pytest.raises(llm.LLMError):
        llm._selected_model(ctx, "invalid")


def test_parse_chat_response_rejects_null_message_content():
    raw = json.dumps({"choices": [{"message": {"content": None}}]})

    with pytest.raises(llm.LLMError, match="content is null"):
        llm._parse_chat_response(raw, llm._MAX_TOKENS_BY_TIER["small"])


def test_parse_chat_response_accepts_list_message_content_parts():
    raw = json.dumps(
        {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"type": "text", "text": '{"status":"ok",'},
                            {"type": "text", "text": '"message":"fine"}'},
                        ]
                    }
                }
            ]
        }
    )

    parsed, _meta = llm._parse_chat_response(raw, llm._MAX_TOKENS_BY_TIER["small"])

    assert parsed == {"status": "ok", "message": "fine"}


def test_parse_chat_response_logs_parse_hint_only_in_debug(monkeypatch):
    raw = json.dumps({"choices": [{"message": {"content": None}}], "model": "demo"})
    debug_messages = []

    monkeypatch.setattr(llm.log, "isEnabledFor", lambda level: level == logging.DEBUG)
    monkeypatch.setattr(
        llm.log,
        "debug",
        lambda message, *args: debug_messages.append(message % args),
    )

    with pytest.raises(llm.LLMError, match="content is null"):
        llm._parse_chat_response(raw, llm._MAX_TOKENS_BY_TIER["small"])

    assert debug_messages == [
        "LLM parse hint: envelope_keys=['choices', 'model'] content_type=NoneType"
    ]


def test_parse_chat_response_skips_parse_hint_when_debug_disabled(monkeypatch):
    raw = json.dumps({"choices": [{"message": {"content": None}}], "model": "demo"})
    debug_messages = []

    monkeypatch.setattr(llm.log, "isEnabledFor", lambda level: False)
    monkeypatch.setattr(
        llm.log,
        "debug",
        lambda message, *args: debug_messages.append(message % args),
    )

    with pytest.raises(llm.LLMError, match="content is null"):
        llm._parse_chat_response(raw, llm._MAX_TOKENS_BY_TIER["small"])

    assert debug_messages == []


def test_max_tokens_for_tier_defaults_and_override():
    assert llm._max_tokens_for_tier("small") == llm._MAX_TOKENS_BY_TIER["small"]
    assert llm._max_tokens_for_tier("large") == llm._MAX_TOKENS_BY_TIER["large"]
    # Unknown tier falls back to the small budget.
    assert llm._max_tokens_for_tier("weird") == llm._MAX_TOKENS_BY_TIER["small"]
    # Explicit override wins.
    assert llm._max_tokens_for_tier("small", override=123) == 123


def test_parse_chat_response_falls_back_to_reasoning_when_content_null():
    raw = json.dumps(
        {
            "choices": [
                {
                    "message": {
                        "content": None,
                        "reasoning": '```json\n{"status": "ok", "message": "from reasoning"}\n```',
                    }
                }
            ]
        }
    )

    parsed, _meta = llm._parse_chat_response(raw, llm._MAX_TOKENS_BY_TIER["small"])

    assert parsed == {"status": "ok", "message": "from reasoning"}


def test_parse_chat_response_uses_reasoning_details_parts():
    raw = json.dumps(
        {
            "choices": [
                {
                    "message": {
                        "content": "",
                        "reasoning_details": [
                            {"type": "reasoning.text", "text": '{"status":"ok",'},
                            {"type": "reasoning.text", "text": '"message":"ok"}'},
                        ],
                    }
                }
            ]
        }
    )

    parsed, _meta = llm._parse_chat_response(raw, llm._MAX_TOKENS_BY_TIER["small"])

    assert parsed == {"status": "ok", "message": "ok"}


def test_parse_chat_response_raises_truncation_on_length_finish_reason():
    raw = json.dumps(
        {
            "choices": [
                {
                    "finish_reason": "length",
                    "message": {"content": '{"status": "ok"'},
                }
            ]
        }
    )

    with pytest.raises(llm.LLMTruncationError):
        llm._parse_chat_response(raw, max_tokens=8192)


def test_strip_fences_handles_unterminated_leading_fence():
    text = '```json\n{"status": "ok", "message": "fine"}'
    assert llm._strip_fences(text) == '{"status": "ok", "message": "fine"}'


def test_text_to_json_repairs_trailing_comma():
    assert llm._text_to_json('{"status": "ok", "message": "fine",}') == {
        "status": "ok",
        "message": "fine",
    }


def test_repair_json_trims_trailing_garbage_after_object():
    assert llm._repair_json('{"status": "ok"} trailing junk') == {"status": "ok"}


def test_call_llm_retries_once_with_larger_budget(monkeypatch):
    ctx = SimpleNamespace(llm_model_small=None, llm_model_large=None)
    budgets = []

    def fake_call(prompt, ctx_arg, model_tier, max_tokens):
        budgets.append(max_tokens)
        if len(budgets) == 1:
            raise llm.LLMTruncationError("truncated")
        return {"status": "ok"}, {"reasoning": "", "finish_reason": "stop"}

    monkeypatch.setattr(llm, "_call_openai_compatible", fake_call)

    result = llm.call_llm("prompt", ctx, model_tier="small", trace_label="X-1")

    assert result == {"status": "ok"}
    assert budgets == [
        llm._MAX_TOKENS_BY_TIER["small"],
        min(llm._MAX_TOKENS_BY_TIER["small"] * 2, llm._MAX_TOKENS_HARD_CAP),
    ]


def test_call_llm_records_reasoning_trace(monkeypatch):
    ctx = SimpleNamespace(llm_model_small=None, llm_model_large=None)

    def fake_call(prompt, ctx_arg, model_tier, max_tokens):
        return {"status": "ok"}, {"reasoning": "because reasons", "finish_reason": "stop"}

    monkeypatch.setattr(llm, "_call_openai_compatible", fake_call)

    llm.call_llm("prompt", ctx, model_tier="small", trace_label="SEC-12")

    traces = ctx.llm_reasoning_traces
    assert len(traces) == 1
    assert traces[0]["label"] == "SEC-12"
    assert traces[0]["reasoning"] == "because reasons"
    assert traces[0]["finish_reason"] == "stop"


def test_fresh_rate_limiter_does_not_pace_proactively():
    """A new limiter must not sleep before the first call (no learned limit yet)."""
    limiter = llm._RateLimitState()
    assert limiter.min_interval_s == 0.0

    slept = []
    original_sleep = llm.time.sleep
    llm.time.sleep = lambda s: slept.append(s)
    try:
        llm._wait_for_slot(limiter)
    finally:
        llm.time.sleep = original_sleep

    assert slept == []


def test_learn_from_headers_without_usable_headers_keeps_no_pacing():
    """Token-quota / missing headers must not trigger proactive pacing."""
    limiter = llm._RateLimitState()

    # Large value is treated as a token quota, not a request rate -> ignored.
    llm._learn_from_headers(limiter, {"x-ratelimit-limit": "60000"})
    assert limiter.min_interval_s == 0.0

    # No rate-limit headers at all.
    llm._learn_from_headers(limiter, {"content-type": "application/json"})
    assert limiter.min_interval_s == 0.0


def test_learn_from_headers_with_real_limit_starts_pacing():
    """A modest request-rate limit header starts proactive pacing."""
    limiter = llm._RateLimitState()

    llm._learn_from_headers(limiter, {"x-ratelimit-limit": "60", "x-ratelimit-reset": "60"})

    assert limiter.limit == 60
    assert limiter.window_s == 60
    expected = (60 / 60) * llm._RATE_SAFETY_FACTOR
    assert limiter.min_interval_s == pytest.approx(expected)

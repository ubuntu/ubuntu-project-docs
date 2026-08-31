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
    args = parser.parse_args(
        ["review", "123", "--llm-model-small", "foo", "--llm-model-large", "bar"]
    )

    assert args.llm_model_small == "foo"
    assert args.llm_model_large == "bar"


def test_build_parser_rejects_removed_single_model_flag():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["123", "--llm-model", "gpt-4.1-mini"])


def test_lxd_default_options_request_larger_disk():
    import lxd_runner

    # LXD VMs default to a 10GB root disk, which is too small for large builds.
    assert "root,size=20GiB" in " ".join(lxd_runner._DEFAULT_LXD_OPTIONS)
    assert "--vm" in lxd_runner._DEFAULT_LXD_OPTIONS


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


def test_resolve_auth_defaults_to_openrouter(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-token")
    monkeypatch.delenv("OPENAI_API_BASE", raising=False)

    provider, token, source, api_url = llm.resolve_auth()

    assert provider == "openai-compatible"
    assert token == "test-token"
    assert source == "host-env:OPENAI_API_KEY"
    assert api_url == "https://openrouter.ai/api/v1/chat/completions"


def test_resolve_auth_honors_compatible_base_override(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-token")
    monkeypatch.setenv("OPENAI_API_BASE", "https://llm.example/v1/")

    _provider, _token, _source, api_url = llm.resolve_auth()

    assert api_url == "https://llm.example/v1/chat/completions"


def test_resolve_auth_without_key_falls_back_to_placeholder_token(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_BASE", raising=False)

    provider, token, source, api_url = llm.resolve_auth()

    assert provider == "openai-compatible"
    assert token == llm.FALLBACK_TOKEN
    assert source.startswith(llm.FALLBACK_AUTH_SOURCE_PREFIX)
    assert api_url == "https://openrouter.ai/api/v1/chat/completions"


def test_resolve_auth_without_key_honors_compatible_base_override(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_BASE", "https://llm.example/v1/")

    _provider, token, source, api_url = llm.resolve_auth()

    assert token == llm.FALLBACK_TOKEN
    assert source.startswith(llm.FALLBACK_AUTH_SOURCE_PREFIX)
    assert api_url == "https://llm.example/v1/chat/completions"


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


def test_default_token_budgets_leave_room_for_doubling_retry():
    # Generous first-call ceilings avoid truncation for reasoning models.
    assert llm._MAX_TOKENS_BY_TIER["small"] == 32768
    assert llm._MAX_TOKENS_BY_TIER["large"] == 49152
    # The hard cap must not clip the "twice the base budget" retry for any tier.
    assert llm._MAX_TOKENS_HARD_CAP >= 2 * llm._MAX_TOKENS_BY_TIER["large"]


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


def test_parse_chat_response_recovers_complete_answer_despite_length_finish_reason(caplog):
    """A reasoning model can finish a complete JSON answer and then keep
    rambling until it hits the token budget - finish_reason=="length" must
    not be treated as fatal when the answer itself already parses cleanly
    (recovered via the existing trim-to-last-balanced-brace repair)."""
    raw = json.dumps(
        {
            "choices": [
                {
                    "finish_reason": "length",
                    "message": {
                        "content": (
                            '{"status": "ok", "message": "fine"}\n\n'
                            "Further unrelated reasoning that never closes anything"
                        )
                    },
                }
            ]
        }
    )

    with caplog.at_level("INFO", logger="auto_mir.llm"):
        parsed, meta = llm._parse_chat_response(raw, max_tokens=8192, trace_label="RDO-3")

    assert parsed == {"status": "ok", "message": "fine"}
    assert meta["finish_reason"] == "length"
    assert any(
        "Recovered a complete JSON answer despite finish_reason=length" in record.getMessage()
        and "RDO-3" in record.getMessage()
        for record in caplog.records
    )


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


def test_build_parser_accepts_llm_retry_and_timeout_flags():
    parser = build_parser()
    args = parser.parse_args(
        ["review", "123", "--llm-retry-base-delay", "30", "--llm-timeout", "120"]
    )

    assert args.llm_retry_base_delay == 30.0
    assert args.llm_timeout == 120.0


def test_build_parser_defaults_llm_retry_and_timeout_flags():
    parser = build_parser()
    args = parser.parse_args(["review", "123"])

    assert args.llm_retry_base_delay == 8.0
    assert args.llm_timeout == 60.0


def test_call_openai_compatible_honours_ctx_retry_base_delay(monkeypatch):
    captured = {}
    real_retry_rate_limited = llm.retry_rate_limited

    def spy_retry_rate_limited(*, max_attempts, base_delay, max_delay):
        captured["max_attempts"] = max_attempts
        captured["base_delay"] = base_delay
        captured["max_delay"] = max_delay
        return real_retry_rate_limited(
            max_attempts=max_attempts, base_delay=base_delay, max_delay=max_delay
        )

    monkeypatch.setattr(llm, "retry_rate_limited", spy_retry_rate_limited)
    monkeypatch.setattr(llm, "_call_openai_compatible_impl", lambda *a, **k: ({"ok": True}, {}))

    ctx = SimpleNamespace(llm_retry_base_delay=90.0)
    result = llm._call_openai_compatible("prompt", ctx, "small", 100)

    assert result == ({"ok": True}, {})
    assert captured["max_attempts"] == 4
    assert captured["base_delay"] == 90.0
    # max_delay never shrinks below the configured base delay.
    assert captured["max_delay"] == 90.0


def test_call_openai_compatible_default_retry_delay_unchanged(monkeypatch):
    captured = {}
    real_retry_rate_limited = llm.retry_rate_limited

    def spy_retry_rate_limited(*, max_attempts, base_delay, max_delay):
        captured["base_delay"] = base_delay
        captured["max_delay"] = max_delay
        return real_retry_rate_limited(
            max_attempts=max_attempts, base_delay=base_delay, max_delay=max_delay
        )

    monkeypatch.setattr(llm, "retry_rate_limited", spy_retry_rate_limited)
    monkeypatch.setattr(llm, "_call_openai_compatible_impl", lambda *a, **k: ({"ok": True}, {}))

    # No llm_retry_base_delay attribute at all: must match the previous
    # hardcoded static-decorator defaults exactly (8.0 / 60.0).
    ctx = SimpleNamespace()
    llm._call_openai_compatible("prompt", ctx, "small", 100)

    assert captured["base_delay"] == 8.0
    assert captured["max_delay"] == 60.0


def test_call_llm_retries_once_with_larger_budget(monkeypatch):
    ctx = SimpleNamespace(llm_model_small=None, llm_model_large=None)
    budgets = []

    def fake_call(prompt, ctx_arg, model_tier, max_tokens, trace_label=""):
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


def test_call_llm_large_tier_retry_doubles_within_hard_cap(monkeypatch):
    ctx = SimpleNamespace(llm_model_small=None, llm_model_large=None)
    budgets = []

    def fake_call(prompt, ctx_arg, model_tier, max_tokens, trace_label=""):
        budgets.append(max_tokens)
        if len(budgets) == 1:
            raise llm.LLMTruncationError("truncated")
        return {"status": "ok"}, {"reasoning": "", "finish_reason": "stop"}

    monkeypatch.setattr(llm, "_call_openai_compatible", fake_call)

    result = llm.call_llm("prompt", ctx, model_tier="large", trace_label="URF-6")

    assert result == {"status": "ok"}
    # The large-tier retry must reach exactly twice the base budget, not a
    # value clipped by the hard cap.
    assert budgets == [
        llm._MAX_TOKENS_BY_TIER["large"],
        llm._MAX_TOKENS_BY_TIER["large"] * 2,
    ]


def test_call_llm_retries_on_invalid_envelope_and_reinstructs_json(monkeypatch):
    """A malformed HTTP envelope is transient: retry once with a strict-JSON prompt."""
    ctx = SimpleNamespace(llm_model_small=None, llm_model_large=None)
    prompts = []

    def fake_call(prompt, ctx_arg, model_tier, max_tokens, trace_label=""):
        prompts.append(prompt)
        if len(prompts) == 1:
            raise llm.LLMEnvelopeError("LLM API response is not valid JSON: Expecting value")
        return {"status": "ok"}, {"reasoning": "", "finish_reason": "stop"}

    monkeypatch.setattr(llm, "_call_openai_compatible", fake_call)

    result = llm.call_llm("original prompt", ctx, model_tier="small", trace_label="RDO-1")

    assert result == {"status": "ok"}
    assert len(prompts) == 2
    # First attempt uses the bare prompt; the retry appends the strict-JSON steer.
    assert prompts[0] == "original prompt"
    assert "ONLY a single valid JSON object" in prompts[1]


def test_parse_envelope_raises_retryable_error_on_invalid_json():
    import pytest

    with pytest.raises(llm.LLMEnvelopeError):
        llm._parse_envelope("this is not json")
    # It remains an LLMError subclass so existing callers still catch it.
    assert issubclass(llm.LLMEnvelopeError, llm.LLMError)


def test_call_llm_records_reasoning_trace(monkeypatch):
    ctx = SimpleNamespace(llm_model_small=None, llm_model_large=None)

    def fake_call(prompt, ctx_arg, model_tier, max_tokens, trace_label=""):
        return {"status": "ok"}, {"reasoning": "because reasons", "finish_reason": "stop"}

    monkeypatch.setattr(llm, "_call_openai_compatible", fake_call)

    llm.call_llm("prompt", ctx, model_tier="small", trace_label="SEC-12")

    traces = ctx.llm_reasoning_traces
    assert len(traces) == 1
    assert traces[0]["label"] == "SEC-12"
    assert traces[0]["reasoning"] == "because reasons"
    assert traces[0]["finish_reason"] == "stop"


def test_call_openai_compatible_impl_logs_attempt_start_and_elapsed(caplog, monkeypatch):
    """Each individual HTTP attempt logs its own start (model/budget/timeout)
    and completion (elapsed seconds), so a long wait is directly visible in
    the log instead of only inferable from unrelated log-line timestamps."""
    import io

    class _FakeResponse(io.BytesIO):
        headers = {}

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def _fake_urlopen(req, timeout=None):
        body = json.dumps(
            {
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": '{"status": "ok"}'},
                    }
                ]
            }
        ).encode()
        return _FakeResponse(body)

    monkeypatch.setattr(llm.urllib.request, "urlopen", _fake_urlopen)
    ctx = SimpleNamespace(llm_token="tok", llm_api_url="https://example.test/v1/chat/completions")

    with caplog.at_level("INFO", logger="auto_mir.llm"):
        parsed, _meta = llm._call_openai_compatible_impl(
            "prompt", ctx, model_tier="small", max_tokens=1234, trace_label="SEC-1"
        )

    assert parsed == {"status": "ok"}
    messages = [record.getMessage() for record in caplog.records]
    assert any(
        "LLM request starting for SEC-1" in message and "1234" in message for message in messages
    )
    assert any("LLM request for SEC-1 finished in" in message for message in messages)


def test_call_llm_surfaces_auth_rejection_as_llm_error_not_a_crash(monkeypatch):
    """A local/self-hosted endpoint that rejects the optional-auth fallback
    token's format (HTTP 401) must surface through the normal LLMError path,
    not propagate as a raw, uncaught urllib.error.HTTPError."""
    import io
    import urllib.error

    def _fake_urlopen(req, timeout=None):
        raise urllib.error.HTTPError(
            url="https://example.test/v1/chat/completions",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=io.BytesIO(b'{"error": "invalid api key format"}'),
        )

    monkeypatch.setattr(llm.urllib.request, "urlopen", _fake_urlopen)
    ctx = SimpleNamespace(
        llm_token=llm.FALLBACK_TOKEN,
        llm_provider="openai-compatible",
        llm_api_url="https://example.test/v1/chat/completions",
        llm_retry_base_delay=0.001,
    )

    with pytest.raises(llm.LLMError, match="HTTP 401"):
        llm.call_llm("prompt", ctx, model_tier="small", trace_label="SEC-1")

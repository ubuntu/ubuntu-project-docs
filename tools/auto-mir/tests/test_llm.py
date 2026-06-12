"""Tests for LLM model tier selection and CLI model flags."""

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


def test_selected_model_defaults_for_copilot():
    ctx = SimpleNamespace(llm_provider="copilot", llm_model_small=None, llm_model_large=None)

    assert llm._selected_model(ctx, "small") == llm.DEFAULT_COPILOT_SMALL_MODEL
    assert llm._selected_model(ctx, "large") == llm.DEFAULT_COPILOT_LARGE_MODEL


def test_selected_model_defaults_for_openai_compatible():
    ctx = SimpleNamespace(
        llm_provider="openai-compatible",
        llm_model_small=None,
        llm_model_large=None,
    )

    assert llm._selected_model(ctx, "small") == llm.DEFAULT_OPENAI_COMPAT_SMALL_MODEL
    assert llm._selected_model(ctx, "large") == llm.DEFAULT_OPENAI_COMPAT_LARGE_MODEL


def test_selected_model_prefers_explicit_overrides():
    ctx = SimpleNamespace(
        llm_provider="openai-compatible",
        llm_model_small="openai/custom-small",
        llm_model_large="openai/custom-large",
    )

    assert llm._selected_model(ctx, "small") == "openai/custom-small"
    assert llm._selected_model(ctx, "large") == "openai/custom-large"


def test_selected_model_invalid_tier_raises():
    ctx = SimpleNamespace(llm_provider="copilot", llm_model_small=None, llm_model_large=None)

    with pytest.raises(llm.LLMError):
        llm._selected_model(ctx, "invalid")

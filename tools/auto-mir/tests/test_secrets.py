"""Tests for credential-safe logging and shareable artifacts."""

import io
import json
import logging
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pythonjsonlogger import jsonlogger

import auto_mir
import checks
import llm
import lxd_runner
import render
from models import Finding
from utils.secrets import RedactingFormatter, SecretRedactor, ensure_secret_redactor

_SENTINEL = "arbitrary-provider-credential-SENTINEL-42"


def test_redactor_uses_registered_exact_values_only():
    redactor = SecretRedactor()
    redactor.register(_SENTINEL)

    value = {
        "nested": [f"prefix-{_SENTINEL}-suffix", {"secret": _SENTINEL}],
        "public": "sk-looking-but-not-registered",
    }

    assert redactor.sanitize(value) == {
        "nested": ["prefix-[REDACTED]-suffix", {"secret": "[REDACTED]"}],
        "public": "sk-looking-but-not-registered",
    }
    assert value["nested"][1]["secret"] == _SENTINEL


def test_ensure_secret_redactor_creates_and_binds_fallback_when_missing():
    ctx = SimpleNamespace()

    redactor = ensure_secret_redactor(ctx)

    assert isinstance(redactor, SecretRedactor)
    assert ctx.secret_redactor is redactor


def test_stage_auth_registers_host_secret_without_guest_export(monkeypatch):
    ctx = SimpleNamespace(evidence={}, secret_redactor=SecretRedactor())
    monkeypatch.setattr(
        llm,
        "resolve_auth",
        lambda: (
            "openai-compatible",
            _SENTINEL,
            "host-env:OPENAI_API_KEY",
            "https://example.test/v1/chat/completions",
        ),
    )

    auto_mir.stage_auth(ctx)

    assert ctx.secret_redactor.redact_text(_SENTINEL) == "[REDACTED]"
    assert not hasattr(ctx, "guest_env")


def test_stage_auth_warns_and_proceeds_without_openai_api_key(monkeypatch, caplog):
    ctx = SimpleNamespace(evidence={}, secret_redactor=SecretRedactor())
    monkeypatch.setattr(
        llm,
        "resolve_auth",
        lambda: (
            "openai-compatible",
            llm.FALLBACK_TOKEN,
            "fallback:no-openai-api-key",
            "https://example.test/v1/chat/completions",
        ),
    )

    with caplog.at_level(logging.WARNING, logger="auto_mir"):
        auto_mir.stage_auth(ctx)  # must not raise SystemExit

    assert ctx.llm_token == llm.FALLBACK_TOKEN
    assert any("OPENAI_API_KEY" in record.message for record in caplog.records)
    # The placeholder token is not a real secret, so it should not be registered.
    assert ctx.secret_redactor.redact_text(llm.FALLBACK_TOKEN) == llm.FALLBACK_TOKEN
    assert ctx.evidence["auth"]["api_url"] == "https://example.test/v1/chat/completions"


def test_redacting_formatter_covers_arguments_and_tracebacks():
    redactor = SecretRedactor()
    redactor.register(_SENTINEL)
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(
        RedactingFormatter(logging.Formatter("%(levelname)s %(message)s"), redactor)
    )
    logger = logging.getLogger("test.secret.console")
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    try:
        raise RuntimeError(f"request rejected for {_SENTINEL}")
    except RuntimeError:
        logger.exception("credential argument: %s", _SENTINEL)

    output = stream.getvalue()
    assert _SENTINEL not in output
    assert output.count("[REDACTED]") == 2


def test_json_log_redacts_subprocess_command_and_output(monkeypatch, tmp_path):
    redactor = SecretRedactor()
    redactor.register(_SENTINEL)
    log_path = tmp_path / "auto-mir.log"
    handler = logging.FileHandler(log_path)
    handler.setFormatter(
        RedactingFormatter(jsonlogger.JsonFormatter("%(levelname)s %(name)s %(message)s"), redactor)
    )
    logger = logging.getLogger("auto_mir.lxd_runner")
    previous_handlers = logger.handlers[:]
    previous_propagate = logger.propagate
    previous_level = logger.level
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    monkeypatch.setattr(
        lxd_runner.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args[0], 1, stdout=f"out {_SENTINEL}", stderr=f"err {_SENTINEL}"
        ),
    )
    try:
        try:
            lxd_runner.run_command(["tool", f"--credential={_SENTINEL}"], "host", capture=True)
        except subprocess.CalledProcessError:
            pass
    finally:
        handler.close()
        logger.handlers = previous_handlers
        logger.propagate = previous_propagate
        logger.setLevel(previous_level)

    output = log_path.read_text()
    assert _SENTINEL not in output
    assert "[REDACTED]" in output
    for line in output.splitlines():
        json.loads(line)


def _run_context(tmp_path: Path) -> auto_mir.RunContext:
    args = auto_mir.build_parser().parse_args(["12345", "--output-dir", str(tmp_path)])
    ctx = auto_mir.RunContext(args)
    ctx.secret_redactor.register(_SENTINEL)
    ctx.source_package = f"package-{_SENTINEL}"
    ctx.reporter_mir_content = f"reporter {_SENTINEL}"
    ctx.bug = {"description": f"bug {_SENTINEL}"}
    ctx.evidence = {
        "adapters": {
            "fetch-build": {
                "build_success": False,
                "build_log": f"build failed with {_SENTINEL}",
            }
        },
        "analysis_summary": {"detail": _SENTINEL},
    }
    ctx.findings = [
        Finding(
            id="TEST-1",
            section="Summary",
            title="Credential boundary",
            mode="deterministic",
            status="ok",
            severity="ok",
            confidence="high",
            message=f"finding {_SENTINEL}",
        )
    ]
    return ctx


def test_all_shareable_artifact_writers_redact_registered_secrets(monkeypatch, tmp_path, capsys):
    ctx = _run_context(tmp_path)
    ctx.llm_calls_by_model = {_SENTINEL: 1}
    ctx.llm_estimated_tokens = {_SENTINEL: 10}

    ctx.save_evidence()
    render.write_outputs(ctx)

    ctx.catalog = {"checks": []}
    monkeypatch.setattr(checks, "evaluate_checks", lambda _ctx: ctx.findings)
    auto_mir._save_test_artifacts(ctx)
    auto_mir._print_complete_banner(ctx)

    files = [path for path in tmp_path.iterdir() if path.is_file()]
    assert {path.name for path in files} >= {
        "build_log.txt",
        "context.json",
        "deterministic_findings.json",
        "evidence.json",
        "meta.json",
        "report.json",
        "review-draft.txt",
    }
    for path in files:
        assert _SENTINEL not in path.read_text(), path.name
    assert _SENTINEL not in capsys.readouterr().out


def test_render_outputs_do_not_fail_when_context_misses_secret_redactor(tmp_path):
    ctx = _run_context(tmp_path)
    del ctx.secret_redactor

    render.write_outputs(ctx)

    assert ctx.report_path and ctx.report_path.exists()
    assert ctx.review_draft_path and ctx.review_draft_path.exists()


def test_runtime_facts_do_not_probe_or_report_auth(monkeypatch):
    commands: list[list[str]] = []

    def fake_exec(_name, command, **_kwargs):
        commands.append(command)
        return SimpleNamespace(stdout="value\n", returncode=0)

    monkeypatch.setattr(lxd_runner, "exec_in", fake_exec)
    facts = lxd_runner.collect_runtime_facts(SimpleNamespace(guest_name="guest", lxd_image="image"))

    assert "auth_env_present" not in facts
    assert all("OPENAI_API" not in " ".join(command) for command in commands)

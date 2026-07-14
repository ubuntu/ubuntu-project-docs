# Auto-MIR Design

## Purpose

Auto-MIR turns a Launchpad MIR bug into a structured, reviewer-facing draft by:

1. collecting deterministic evidence,
2. evaluating catalog-defined checks,
3. using LLM analysis only where policy allows,
4. rendering results into reviewer-template-aligned output.

The tool is host-orchestrated and executes build/evidence-sensitive work in an
LXD VM for reproducibility and isolation.

## Scope and boundaries

- Architecture and operating model are defined here.
- Development process rules are defined in:
  `.github/instructions/tools-development.instructions.md`.
- Rationale/history is defined in `decisions.md`.
- Prompt content is defined in `prompts/` and is out of scope for this document.

## End-to-end stage flow

`auto_mir.main()` executes these stages:

Bootstrap and host preflight (before Stage 0):
- Parse command-line arguments using standard-library-only imports, so
  `--help` works on an unprepared host.
- Require Python 3.12 or newer and discover every direct Python runtime
  dependency before creating output state or starting network/LXD work.
- Report all missing dependencies together as Ubuntu binary packages. The
  mapping between project distributions, import modules, and Ubuntu packages
  lives in `utils/dependencies.py` and is checked against `pyproject.toml`.

1. Stage 0: auth (`stage_auth`)
- Resolve provider/token/API base for LLM usage.
- Register the token with the run's exact-value redactor.
- Keep credentials host-only; they are never stored in LXD guest configuration.
- Skipped in `--collect-only` mode.

2. Stage 1: intake (`stage_intake`)
- Pull Launchpad bug metadata and reporter MIR content.
- Resolve source package and series context.

3. Stage 2: isolation setup (`stage_spawn_guest`)
- Create/provision LXD VM and tooling.

4. Stage 3: evidence (`stage_collect_evidence`)
- Load catalog and collect required + optional adapters.
- Store adapter payloads under `ctx.evidence["adapters"]`.

5. Stage 4: analysis (`stage_analyse`)
- Resolve the review type (`review_type.detect_review_type`): fresh, or a
  softened fast-path (rereview / reorg) forced via `--review-type` or detected
  from the bug text and evidence (incl. the best-effort `lp-mir-history`
  adapter). Fast-paths downgrade blocking findings to recommendations.
- Evaluate checks with deterministic and LLM evaluators.
- Produce `Finding` objects with severity/confidence.

6. Stage 5: rendering (`stage_render`)
- Write review draft and structured report.

Always-run tail logic:
- log artifact locations,
- teardown/preserve VM based on tri-state keep policy,
- print completion banner.

## Credential boundary

LLM requests run on the host. Authentication values are therefore neither
needed nor persisted in the LXD guest. A per-run redactor registers resolved
secret values and sanitizes fully formatted console/JSON logs and every
shareable artifact writer. Redaction matches exact registered values rather
than provider-specific prefixes or heuristic token patterns, so another
OpenAI-compatible provider does not require a new masking rule and public MIR
evidence remains intact.

The output directory is credential-safe to share after a completed run. It is
not anonymized: public Launchpad content, package data, guest names, versions,
and diagnostic paths remain present.

## Core data contracts

### RunContext (operational state)

`RunContext` is the runtime envelope passed across stages and subsystems.
Important partitions:

- Inputs/config: bug id, models, LXD options, source pocket.
- Runtime/auth: resolved provider/token/API URL.
- Evidence: adapter outputs, collection summaries.
- Findings: check outputs from `checks.evaluate_checks()`.
- Output: rendered report and draft paths.

### Finding (evaluation result contract)

`models.Finding` is the canonical check-output model with enforced invariants:

- `status == "ok"` implies `severity == "ok"`.
- statuses and severities are enum-validated.
- helper methods (`succeed`, `fail`, factories) are preferred to manual field mutation.

Rendering semantics are driven by `status + confidence + mode`:

- deterministic non-ok or high-confidence non-ok -> `Problems`.
- low/medium-confidence non-ok -> `Left to decide`.

## Checks subsystem model

`checks/__init__.py` orchestrates evaluation in two passes:

- Pass 1: non-synthesis checks.
- Pass 2: synthesis checks (`synthesis: true`) after pass-1 findings exist.

Dispatch is mode-driven through the registry:

- `deterministic`
- `ev_to_ai`
- `ai`
- `human_only`

Language applicability is gated before evaluator routing.

## Evidence subsystem model

`evidence/__init__.py` computes required/optional adapters from the catalog,
orders execution by dependencies, and executes collectors.

Key rules:

- required adapter failures contribute to non-zero collection status,
- optional adapter failures are best-effort and do not fail the run,
- dependency failures propagate to downstream adapters as explicit error status.

The reverse-dependency chain feeds CB-6 (E2E coverage via consumers):

- `reverse-deps` (guest) lists reverse-dependency consumer source packages via
  `reverse-depends` (runtime and build) against the target release,
- `consumer-autopkgtests` (host, depends on `reverse-deps`) reports each
  consumer's autopkgtest status.

The large `autopkgtest.db` is downloaded once per run and cached on the context
(shared by `autopkgtest-db` and `consumer-autopkgtests`), then removed at the
end of evidence collection (`cleanup_cached_autopkgtest_db`).

## LLM usage model

`checks/llm_eval.py` controls AI paths with guardrails:

- explicit prompt rendering,
- bounded payload truncation/summarization,
- confidence cap for AI outcomes,
- deterministic fallback behavior when LLM calls fail.

Model tiering:

- `ai` synthesis uses large tier,
- `ev_to_ai` selects tier heuristically.

## Rendering model

`render/__init__.py` converts findings into:

- reviewer draft text,
- structured machine-readable report.

The renderer enforces section/order conventions and lint-style consistency checks.

## Repository layout (current)

```
tools/auto-mir/
  auto_mir.py
  lxd_runner.py
  lp_intake.py
  llm.py
  models.py
  contracts.py
  catalog.yaml
  catalog.py
  CATALOG.md
  checks/
  evidence/
  render/
  prompts/
  tests/
  testing.md
  decisions.md
  design.md
```

## Verification model

Baseline local gate from `tools/auto-mir`:

- `make lint`
- `make test`
- `make parity-contract` (advisory until baseline fixtures are populated)

Integration gate (when execution/evidence boundaries change):

- `make integration`

## Current refactor posture

The 2026 phased structural refactor is complete. The codebase now operates with:

- characterization and contract tests in place,
- simplified helper-driven state transitions and wrapper boundaries,
- documentation aligned to the current runtime architecture,
- steady-state advisory parity checks to monitor baseline drift.

See `decisions.md` phase ledger entries for per-batch status and validation.

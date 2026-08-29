# Auto-MIR Design

## Purpose

Auto-MIR supports two role-specific workflows:

- `review BUG` turns a Launchpad MIR bug into a structured reviewer draft.
- `report SOURCE` turns source-package evidence and terminal answers into a
  structured reporter draft.

Both workflows operate by:

1. collecting deterministic evidence,
2. evaluating catalog-defined checks,
3. using LLM analysis only where policy allows,
4. rendering results into the applicable role template.

The tool is host-orchestrated and executes build/evidence-sensitive work in an
LXD VM for reproducibility and isolation.

## Scope and boundaries

- Architecture and operating model are defined here.
- Development process rules are defined in:
  `.github/instructions/tools-development.instructions.md`.
- Rationale/history is defined in `decisions.md`.
- Prompt content is defined in `prompts/` and is out of scope for this document.

## End-to-end stage flow

`auto_mir.main()` executes a shared bootstrap followed by a role pipeline.

Bootstrap and host preflight (before Stage 0):
- Parse command-line arguments using standard-library-only imports, so
  `--help` works on an unprepared host.
- Require Python 3.12 or newer and discover every direct Python runtime
  dependency before creating output state or starting network/LXD work.
- Report all missing dependencies together as Ubuntu binary packages. The
  mapping between project distributions, import modules, and Ubuntu packages
  lives in `utils/dependencies.py` and is checked against `pyproject.toml`.
  This tool intentionally runs against Ubuntu system/apt-installed packages
  rather than a project-local virtualenv (it orchestrates `lxc`/`apt-get` and
  expects a host's system Python); `pyproject.toml`'s `dependencies` list
  exists only for packaging/dev tooling and is never what gets installed at
  runtime - a test asserts the two lists never drift apart.

1. Stage 0: auth (`stage_auth`)
- Resolve provider/token/API base for LLM usage.
- Register the token with the run's exact-value redactor.
- Keep credentials host-only; they are never stored in LXD guest configuration.
- Skipped in `--collect-only` mode.

Reviewer Stage 1: intake (`stage_intake`)
- Pull Launchpad bug metadata and reporter MIR content.
- Resolve source package and series context.
- Run early review-type pre-detection
  (`review_type.pre_detect_review_type`): if bug text or `--review-type`
  indicates a re-review/reorg, the reporter template requirement is skipped
  (per MIR policy, it is not required for these fast-paths). The authoritative
  detection runs in Stage 4.

3. Stage 2: isolation setup (`stage_spawn_guest`)
- Create/provision LXD VM and tooling.

4. Stage 3: evidence (`stage_collect_evidence`)
- Load catalog and collect required + optional adapters.
- Store adapter payloads under `ctx.evidence["adapters"]`.

5. Stage 4: analysis (`stage_analyse`)
- Resolve the review type (`review_type.detect_review_type`): fresh, or a
  softened fast-path (rereview / reorg) forced via `--review-type` or detected
  from the bug text and the `lp-mir-history` adapter (which probes Launchpad
  for prior MIR bugs under the current or a predecessor name, including
  predecessor names extracted directly from bug text). Fast-paths downgrade
  blocking findings to recommendations.
- Evaluate checks with deterministic and LLM evaluators.
- Produce `Finding` objects with severity/confidence.

6. Stage 5: rendering (`stage_render`)
- Write review draft and structured report.

Reporter stages:

1. Optional auth: use configured LLM credentials when present; never require
  them for deterministic collection or terminal questions.
2. Source intake: validate the source name and collect the target series.
3. Isolation setup and catalog-selected evidence: reuse the LXD and adapter
  subsystems without Launchpad bug intake.
4. Statement evaluation: resolve deterministic report items and ask only the
  human-owned questions through the terminal wizard.
5. Rendering: write `reporter-draft.txt`, `report.json`, and `evidence.json`.
  Pipeline success and MIR readiness are represented separately.

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

### StatementResult (reporter result contract)

Reporter results deliberately do not use reviewer severity or ACK/NACK
semantics. They record resolution state, readiness effect, statement
provenance, evidence references, answer references, and explicit human
confirmation. Human declarations are never inferred from package evidence.

## Catalog composition

- `catalog.yaml` holds only the sections shared by both roles:
  `global_policies` (confidence model) and `evidence_adapters` (data
  collection interfaces).
- `catalog-mir-review.yaml` owns all reviewer-only content directly: `role:
  review`, `metadata` (reviewer-template blueprint), `checks`,
  `security_triggers`, `render_policy`, `fallback_policy`.
- `catalog-mir-report.yaml` owns all reporter-only content directly: `role:
  report`, `metadata` (reporter-template blueprint), `items` (questions,
  readiness effects, terminal templates).
- `catalog.load_catalog_for_role(tool_root, workspace_root, role)` composes
  the runtime view for either role the same way: load `catalog.yaml`'s shared
  sections, load the role's own file, reject either side overriding the
  other's keys, then validate the composed dict as a whole
  (`validate_catalog` for review, `validate_report_catalog` for report).

Both compositions reject shared-section overrides and validate every check /
item, adapter reference, and blueprint reference on the assembled result.

### RULE-clause coverage (catalog-to-template mapping contract)

A blueprint `RULE:` line may opt in to individual coverage tracking via
`RULE[<slug>]: <text>` (a following plain `RULE:` line continues attaching to
that clause, same as any other multi-line RULE block - tagging never changes
rendered output). Items/checks declare which slug(s) they resolve via an
optional `covers_rule_clauses: [...]` list. `catalog._validate_rule_clause_
coverage()` (called from both `validate_report_catalog()` and
`validate_catalog()`) fails catalog loading on a duplicate slug, a reference
to an undeclared slug, or a declared slug with zero covering items. This is
the structural guarantee that the catalog's authored policy actually reaches
the rendered reporter/reviewer templates, without pinning to a frozen
snapshot of the pre-migration human templates - tagging is opt-in and grows
incrementally as specific clauses are identified worth guaranteeing.

The report catalog currently defines 53 stable logical items. Its runtime
supports catalog options, multi-select choices, safe applicability conditions,
deterministic evaluators, bounded evidence-to-AI suggestions with explicit
confirmation, direct human fallback, and one final issue-finding consistency
pass followed by deterministic readiness validation.

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

The dependency chain feeds DEP-4 (in-main dependencies not only superficially
tested):

- `dep-analysis` (guest) computes `runtime_deps_in_main`: runtime dependencies
  of in-scope binaries that are already in main (so need no MIR of their own),
- `dependency-autopkgtests` (host, depends on `dep-analysis`) resolves each to
  its source via `dep_source_map` and reports per-dependency
  `dependency_coverage` (has_autopkgtest, passing/failing arches) from the
  shared autopkgtest DB.

The large `autopkgtest.db` is downloaded once per run and cached on the context
(shared by `autopkgtest-db`, `consumer-autopkgtests`, and
`dependency-autopkgtests`), then removed at the end of evidence collection
(`cleanup_cached_autopkgtest_db`).

## LLM usage model

`checks/llm_eval.py` controls AI paths with guardrails:

- explicit prompt rendering,
- bounded payload truncation/summarization,
- explicit human-confirmation metadata for every AI outcome,
- deterministic fallback behavior when LLM calls fail.

AI evaluators accept `low`, `medium`, or `high` confidence. A high-confidence
AI failure may therefore render as a confirmed problem, but it remains marked
as requiring human confirmation. This is the current behavior established by
the 2026-07-09 outcome-model decision; older medium-cap descriptions are
superseded.

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
  catalog-mir-review.yaml
  catalog-mir-report.yaml
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

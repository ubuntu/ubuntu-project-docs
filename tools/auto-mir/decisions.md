# Auto-MIR Decisions Log

Choices and reasoning recorded during development. Grouped by topic.

## Promotion tagging convention

Use this log as the source for deciding what should be promoted into
`.github/instructions/tools-development.instructions.md`.

- Promote only stable, repeated contributor workflow rules.
- Keep one-off tradeoffs and historical context in this file.
- When adding a decision that should become instruction-level guidance, include
  `Promotion: yes` in that decision entry.
- For decisions that should stay local rationale, include `Promotion: no`.

## 2026-07-14 — Strict catalog YAML loading

- Promotion: no
- Context: reporter support will compose several policy catalogs. PyYAML's
  default safe loader silently accepts duplicate mapping keys and keeps the
  final value; the existing review catalog already contained one duplicate
  `notes` key. Silent shadowing would make composed policy difficult to audit.
- Decision: load catalogs with a SafeLoader-derived mapping constructor that
  rejects duplicate or unhashable keys and rejects a non-mapping document
  root. Report the YAML source location and fail before catalog validation or
  runtime work.
- Consequences:
  - Duplicate policy/configuration keys are now hard errors rather than silent
    last-value-wins behavior.
  - The duplicate sbuild `notes` key was collapsed without changing its value.
  - Validation from `tools/auto-mir`: `make test` PASS (430 passed, 3 skipped).

## 2026-07-14 — Pre-reporter contract documentation reconciliation

- Promotion: no
- Context: design work for a reporter workflow exposed stale descriptions of
  existing reviewer behavior. In particular, documentation still described an
  AI medium-confidence cap that was intentionally relaxed on 2026-07-09,
  described catalog adapter dependencies as runtime wiring although decorators
  currently own execution order, and described cvelist scanning as guest-side
  after the 2026-07-13 host migration.
- Decision: align architecture, catalog, model, evidence and user-guide text to
  the code and latest explicit decisions before introducing role behavior. Do
  not change reviewer evaluation or rendering semantics in this task.
- Consequences:
  - High-confidence AI outcomes remain permitted and continue to require human
    confirmation.
  - The temporary adapter dependency duplication is explicit, ready for a
    later catalog-authority migration under parity tests.
  - Cvelist documentation now identifies normal host execution accurately.

## 2026-07-14 — Role-based CLI foundation

- Promotion: no
- Context: reviewer runs start from a Launchpad bug, while reporter runs must
  start from a source package. A single positional value plus a mode flag would
  make validation ambiguous and keep reviewer assumptions in the reporter
  path.
- Decision:
  - Introduce explicit `review BUG` and `report SOURCE` commands.
  - Preserve the historical bare numeric bug form by normalizing it to
    `review BUG` before dependency preflight and emit a deprecation warning on
    actual runs.
  - Never infer a bare non-numeric value as a source package; reporter use must
    be explicit.
  - Record the role and role-specific subject on `RunContext` and use either
    value for collision-safe run naming.
  - Require an interactive terminal for `report` before dependency checks,
    output creation, network access, or LXD work. Keep reporter execution
    gated until its dedicated pipeline is connected rather than accidentally
    sending a source package through reviewer Launchpad intake.
- Consequences:
  - Existing scripts using a numeric bug ID continue to parse and run.
  - `--help` remains standard-library-only and now exposes both roles.
  - `report SOURCE` is a recognized but deliberately gated command at this
    foundation stage.

## 2026-07-14 — Separate reporter results and terminal wizard

- Promotion: no
- Context: reviewer `Finding` objects encode severity, ACK/NACK implications,
  summary aggregation, and `Problems` versus `Left to decide` rendering. A
  reporter instead supplies declarations and evidence-backed statements whose
  readiness and provenance must remain explicit.
- Decision:
  - Add reporter-only question, answer, statement-state, readiness, and
    provenance models rather than extending `Finding`.
  - Treat AI text as resolved only with `ai-confirmed` provenance and explicit
    human confirmation.
  - Implement a dependency-free terminal wizard supporting text, multiline,
    yes/no, single-choice, and multi-choice input.
  - End multiline input with a line containing only `.`, and accept `\.` as a
    literal dot. `:cancel` and EOF abort required questions; optional questions
    may be skipped.
  - Keep answers process-local. This layer performs no persistence, network,
    evidence, package, or LLM work.
- Consequences:
  - Reporter interaction is testable independently from catalog and runtime
    orchestration.
  - Human commitments cannot accidentally inherit reviewer severity semantics
    or become authoritative merely because a model generated prose.
  - Validation from `tools/auto-mir`: `make test` PASS (450 passed, 3 skipped).

## 2026-07-14 — Declarative reporter applicability conditions

- Promotion: no
- Context: reporter questions have nested applicability rules, especially test
  coverage and hardware-plan alternatives. Hardcoded per-ID branches would be
  difficult to audit, while evaluating arbitrary catalog expressions would
  create a code-execution and maintenance risk.
- Decision: support a small condition tree containing only `all`, `any`, `not`,
  item references, evidence paths, and `equals`/`in`/`truthy` comparisons.
  Validate every node, reject unknown keys, collect references for catalog
  validation, and reject cycles in item-to-item applicability dependencies.
- Consequences:
  - Complex A-H/X reporter flows can remain catalog-defined without an `eval`
    path or item-specific orchestration code.
  - Missing evidence paths evaluate as absent rather than raising.
  - Diagnostics and traversal order are deterministic for tests and users.
  - Validation from `tools/auto-mir`: `make test` PASS (465 passed, 3 skipped).

## 2026-07-15 — Composed reporter catalog and review compatibility contract

- Promotion: no
- Context: the initial reporter foundation had no reporter policy catalog and
  therefore could not select evidence, drive questions, or generate a template.
  Moving the full established reviewer catalog in the same change would add a
  large, behavior-sensitive file relocation before reporter runtime existed.
- Decision:
  - Add an explicit shared composition contract naming the global policy and
    adapter sections currently inherited from the established catalog.
  - Add an explicit review role contract documenting the reviewer-owned
    sections, while preserving `catalog.yaml` as their single compatibility
    authority during migration.
  - Add `catalog-mir-report.yaml` as the sole authority for reporter items,
    questions, readiness effects, and reporter-template blueprint.
  - Compose a fixed report view with no shared-section overrides and strict
    item, adapter-reference, and blueprint-coverage validation.
  - Let evidence discovery consume either reviewer `checks` or reporter
    `items`.
- Consequences:
  - Reporter policy is now concrete and machine-validated rather than planned
    only.
  - Reviewer loading remains byte-for-byte equivalent to direct legacy catalog
    loading.
  - Physical extraction of shared/review sections remains a later migration;
    the compatibility contracts make ownership explicit without duplicating
    the 48 reviewer checks.
  - The first reporter catalog is intentionally a user-test schema covering all
    12 sections with grouped questions. Fine-grained parity with every legacy
    TODO variant remains required before production readiness.
  - Validation from `tools/auto-mir`: `make test` PASS (470 passed, 3 skipped).

## 2026-07-15 — Connected reporter user-test pipeline

- Promotion: no
- Context: `report SOURCE` previously parsed but stopped unconditionally. The
  reporter catalog and wizard could not be exercised end to end, and the
  documentation reporter template remained a hand-maintained second source.
- Decision:
  - Connect reporter source/series intake, optional authentication, shared LXD
    evidence collection, catalog-driven deterministic/human item evaluation,
    readiness calculation, and draft/JSON rendering.
  - Keep reviewer Launchpad intake, review checks, and renderer on their
    existing path.
  - Use run identity rather than bug ID for source work directories.
  - Preserve unavailable deterministic facts as visible TODO statements and
    distinguish pipeline completion from submission readiness.
  - Generate the reporter documentation include strictly from
    `catalog-mir-report.yaml` during local and Read the Docs builds; the Markdown
    page is now a literalinclude wrapper.
- Consequences:
  - `./auto_mir.py report SOURCE` is runnable for interactive user testing and
    writes `reporter-draft.txt`, `report.json`, and `evidence.json` without any
    Launchpad write operation.
  - The user-test catalog covers all 12 sections using grouped questions. It is
    not yet a production replacement for every fine-grained TODO/RULE variant
    in the former reporter template; that parity remains explicit follow-up.
  - Reporter AI confirmation and full-report consistency primitives remain
    designed but are not activated by this deterministic/human user-test
    catalog.
  - Validation from `tools/auto-mir`: `make test` PASS (478 passed, 3 skipped).
    `make -C docs html` PASS with both role includes generated strictly.

## 2026-07-15 — Single-extraction binary package inspection

- Promotion: no
- Context: reporter security, service, UI, and maintenance questions need facts
  from installed binary package contents. The reviewer sbuild adapter already
  extracted every built deb once for static/setuid/nobody checks; a separate
  extractor would duplicate expensive work and risk inconsistent results.
- Decision:
  - Extend the existing single extraction to inspect sbin executables, systemd
    units, cron jobs, AppArmor profiles, desktop files, translations,
    plugin/extension candidates, and maintainer scripts.
  - Expose those cached sbuild facts through a dedicated
    `binary-package-inspection` adapter depending on sbuild. The adapter performs
    no extraction itself.
  - Preserve the existing sbuild compatibility fields consumed by reviewer
    checks.
- Consequences:
  - Reporter and reviewer logic share one factual binary substrate.
  - The report catalog can make conclusive absence claims only when this adapter
    succeeds; failure remains an explicit unavailable/TODO outcome.
  - Validation from `tools/auto-mir`: `make test` PASS (480 passed, 3 skipped).

## 2026-07-15 — Reporter source packaging evidence enrichment

- Promotion: no
- Decision: extend `packaging-source` with bounded README.source and copyright
  content, source format, source Maintainer/Homepage/description fields,
  structured debconf templates, debian/rules override names, and source service
  and AppArmor paths. Parse these facts deterministically and expose reporter
  statements for packaging metadata and vendored-source refresh/copyright gaps.
- Boundaries: license compatibility, override acceptability, ownership, and
  maintenance commitments remain human decisions; the adapter only reports
  observable source facts. Large text fields are bounded before leaving the
  guest.
- Validation from `tools/auto-mir`: `make test` PASS (482 passed, 3 skipped).

## 2026-07-15 — Confirm-before-use reporter AI and bounded consistency pass

- Promotion: no
- Decision:
  - Add catalog-declared `ev_to_ai` reporter assessments for alternatives,
    security exposure, maintenance health, test adequacy, packaging complexity,
    and UI applicability.
  - Wrap all evidence and completed statements as untrusted data, restrict AI
    responses to small JSON schemas, and discard evidence references outside an
    item's declared adapters.
  - Require explicit terminal confirmation before model text receives
    `ai-confirmed` provenance. Rejection, missing credentials, `--no-llm`, or an
    LLM error routes directly to the human fallback question.
  - Run one final bounded issue-finding pass. It may reference only known item
    IDs and three issue categories, cannot rewrite the draft, and can only ask a
    targeted follow-up which the reporter answers. Deterministic readiness is
    rerun after corrections.
- Consequences: model output cannot satisfy intent, ownership, legal, or
  commitment questions autonomously; all accepted AI text is auditable by
  provenance and evidence references.
- Validation from `tools/auto-mir`: `make test` PASS (489 passed, 3 skipped).

## 2026-07-15 — Catalog-driven reporter choices and applicability

- Promotion: no
- Decision: activate the safe condition engine in reporter evaluation, persist
  stable selected option IDs, and render catalog-owned canonical statements for
  single/multi-choice answers. Add conditional rationale/deadline, post-install,
  exotic-hardware, dependency-routing, and full A-H/X non-automated-testing
  flows. Validate option IDs/statements and all condition references/cycles at
  catalog load time.
- Also derive reviewer intake's reporter-template detection markers from the
  report catalog and enrich Launchpad evidence with canonical source/build URLs.
- Consequences: conditional questions are no longer hardcoded or always asked;
  nested test-plan alternatives remain machine-auditable and structured output
  records the exact choices used.
- Validation from `tools/auto-mir`: `make test` PASS (490 passed, 3 skipped).

## 2026-07-15 — Complete logical reporter-item inventory

- Promotion: no
- Decision: complete the approved 53-item logical reporter inventory across all
  12 sections. Add explicit prior-MIR history, optional deprecated-crypto hint,
  failing-test explanation, micro-library solution testing, obsolete dependency
  detection, recent-build evidence, and cross-team impact coordination. Keep
  option variants nested under stable parent IDs; the non-automated testing
  group exposes all A-H and X alternatives.
- Consequences: every planned logical question has a catalog identity, mode,
  readiness effect, blueprint position, and deterministic or human/AI handling
  path. Exact line-for-line preservation of the former prose/RULE body remains
  a separate documentation-parity concern rather than an untracked question
  gap.
- Validation from `tools/auto-mir`: `make test` PASS (491 passed, 3 skipped).

## 2026-07-15 — Catalog-authoritative adapter topology

- Promotion: no
- Decision: use `evidence_adapters[].depends_on` as the production dependency
  graph, expand the complete transitive closure before execution, and use the
  same graph for ordering and failed-dependency propagation. Registration
  dependencies remain temporarily present for decorator compatibility and are
  checked for exact equality; only minimal catalogs with no adapter metadata
  fall back to registrations.
- Consequences: adapter selection no longer depends on every transitive adapter
  being repeated by checks/items, and catalog/runtime dependency drift fails
  the unit suite.
- Validation from `tools/auto-mir`: `make test` PASS (492 passed, 3 skipped).

## 2026-07-15 — Reporter rule guidance restored to catalog generation

- Promotion: no
- Decision: store the semantic MIR policy guidance for every reporter section
  as catalog blueprint `RULE:` lines. The offline documentation renderer emits
  them, while the runtime draft deliberately removes them after the terminal
  workflow has processed the corresponding questions.
- Consequences: generated reporter documentation again explains demand,
  security lifetime/exposure, maintenance, testing/hardware, packaging,
  standards/licensing, ownership, static/vendored obligations, and background
  requirements without duplicating policy in the Markdown wrapper. The catalog
  remains authoritative for both guidance and questions.

## 2026-07-15 — Consistency-aware final readiness

- Promotion: no
- Decision: merge deterministic/final consistency errors into both the human
  reporter draft readiness summary and structured report readiness. A pipeline
  that completed successfully must never display `Ready for submission: yes`
  while the consistency pass still reports a blocker.
- Validation from `tools/auto-mir`: `make test` PASS (493 passed, 3 skipped).

## 2026-07-15 — Reporter series defaults to devel

- Promotion: no
- Context: reporter mode prompted for a series even though the intended default
  is the current development release and pressing Enter selected `devel`.
- Decision: when `report SOURCE` has no `--series`, select `devel` immediately
  without a terminal question. Preserve reviewer behavior, where omission means
  detecting the series from Launchpad bug tasks. Explain both behaviors in
  `--help` and the end-user guide.
- Validation from `tools/auto-mir`: `make test` PASS (495 passed, 3 skipped).

## 2026-07-15 — Reporter template uses logical policy parity

- Promotion: no
- Context: preserving the former reporter body byte-for-byte would also freeze
  historical typos, obsolete wording, and URLs, and would duplicate a large
  prose snapshot alongside structured production items. The reporter catalog
  now carries every planned logical question, choice family, A-H/X alternative,
  section, and semantic RULE requirement.
- Decision: use strict logical policy parity rather than byte parity. Keep the
  catalog as the only editable source for generated guidance and templates;
  validate 53 unique logical items, all section markers, option statements,
  conditions, blueprint coverage, and key rule families. Intentional wording
  corrections remain normal catalog changes.
- Also make `catalog-mir-review.yaml` the real role-aware loading and template
  generation entry point. Its compatibility reference preserves the established
  reviewer data and exact reviewer output while completing role separation at
  the public catalog boundary.
- Validation from `tools/auto-mir`: `make test` PASS (496 passed, 3 skipped).
  Strict reporter generation covers 53 items, all 12 sections, every option
  statement, conditions/cardinality, A-H/X, and all historical policy families.

## Refactor phase ledger template (2026-07)

Use this template for each refactor PR batch under `tools/auto-mir`.
The goal is to keep intent, boundaries, and parity outcomes explicit so later
phases do not drift.

```md
### Phase Ledger Entry: <PR-ID / batch name>

- Date: YYYY-MM-DD
- Promotion: no
- Intent: <single architectural intent for this PR>
- Scope boundaries touched:
  - <module/file group 1>
  - <module/file group 2>
- Explicit non-goals:
  - <what was intentionally not changed>
- Invariants preserved:
  - <behavior or contract 1>
  - <behavior or contract 2>
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS/FAIL
  - `make test`: PASS/FAIL
  - `make parity-contract` (advisory): PASS/WARN/FAIL
  - `python3 integration_smoke.py` (if applicable): PASS/FAIL/SKIP
- Parity result summary:
  - <byte-level parity status against baseline artifacts>
- Follow-up impacts:
  - <next PR dependency or cleanup>
```

### Phase Ledger Entry: PR-00 Baseline contract and governance rails

- Date: 2026-07-10
- Promotion: no
- Intent: Establish explicit refactor guardrail mechanics and command-surface governance.
- Scope boundaries touched:
  - `tools/auto-mir/Makefile`
  - `tools/auto-mir/testing.md`
  - `tools/auto-mir/tests/check_parity_baseline.py`
  - `tools/auto-mir/tests/parity_baseline.json`
- Explicit non-goals:
  - No production runtime behavior changes.
  - No check logic or adapter logic changes.
- Invariants preserved:
  - `make test` remains the fast validation gate.
  - Existing test suite behavior is unchanged.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: WARN (advisory mode; baseline fixtures absent)
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Baseline manifest and checker are in place; strict parity is not yet enforceable until fixtures are populated.
- Follow-up impacts:
  - PR-01 can rely on a stable test and phase-gate command surface.

### Phase Ledger Entry: PR-01 Characterization tests for orchestration and adapter graph

- Date: 2026-07-10
- Promotion: no
- Intent: Add explicit characterization tests for stage sequencing, collect-only routing, dependency failure propagation, and Finding invariants.
- Scope boundaries touched:
  - `tools/auto-mir/tests/test_auto_mir.py`
  - `tools/auto-mir/tests/test_evidence.py`
  - `tools/auto-mir/tests/test_models.py`
- Explicit non-goals:
  - No changes to stage orchestration implementation semantics.
  - No changes to adapter execution logic.
- Invariants preserved:
  - Stage order in `auto_mir.main` remains auth -> intake -> spawn -> collect -> analyse -> render (with collect-only exceptions).
  - Downstream adapters are not executed when required upstream dependency fails.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: WARN (advisory mode; baseline fixtures absent)
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Test-only changes; runtime parity unaffected.
- Follow-up impacts:
  - PR-02 can safely extend evaluator-routing characterization with stronger guardrails.

### Phase Ledger Entry: PR-02 Characterization tests for evaluator and rendering contracts

- Date: 2026-07-10
- Promotion: no
- Intent: Strengthen evaluator routing and fallback contract tests, including adapter error-cause mapping and unknown-mode normalization.
- Scope boundaries touched:
  - `tools/auto-mir/tests/test_checks.py`
- Explicit non-goals:
  - No modifications to evaluator implementations.
  - No rendering logic changes.
- Invariants preserved:
  - Low-confidence unresolved findings map failed adapter causes deterministically.
  - Unknown-mode fallback remains normalized to `TODO:`-prefixed manual action.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: WARN (advisory mode; baseline fixtures absent)
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Test-only changes; runtime parity unaffected.
- Follow-up impacts:
  - PR-10+ refactors now have stronger evaluator contract protection.

### Phase Ledger Entry: PR-10 Context and boundary typing pass

- Date: 2026-07-10
- Promotion: no
- Intent: Introduce explicit protocol contracts for checks/evidence orchestration boundaries without runtime behavior changes.
- Scope boundaries touched:
  - `tools/auto-mir/contracts.py`
  - `tools/auto-mir/checks/__init__.py`
  - `tools/auto-mir/evidence/__init__.py`
- Explicit non-goals:
  - No refactor of orchestration flow.
  - No adapter/check implementation changes.
- Invariants preserved:
  - `evaluate_checks` and `collect_from_catalog` behavior remains unchanged.
  - Existing call sites continue to pass `RunContext` objects.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: WARN (advisory mode; baseline fixtures absent)
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Type annotation and protocol only; no output drift introduced.
- Follow-up impacts:
  - PR-11/PR-12 can refactor execution and evaluator policies with clearer boundary contracts.

### Phase Ledger Entry: PR-11 LXD execution wrapper consolidation (slice 1)

- Date: 2026-07-10
- Promotion: no
- Intent: Reduce wrapper indirection in host/container execution by removing one redundant host wrapper layer.
- Scope boundaries touched:
  - `tools/auto-mir/lxd_runner.py`
- Explicit non-goals:
  - No command retry policy changes.
  - No subprocess behavior or argument-shaping changes.
- Invariants preserved:
  - `_lxc` remains the public helper for `lxc` CLI calls.
  - Error handling still routes through `run_command` with existing logging/check semantics.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: WARN (advisory mode; baseline fixtures absent)
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Behavior-preserving internal simplification; no output drift observed via tests.
- Follow-up impacts:
  - Additional wrapper consolidation continued in PR-33 and PR-34.

### Phase Ledger Entry: PR-33 LXD execution wrapper consolidation (slice 2)

- Date: 2026-07-10
- Promotion: no
- Intent: Remove one remaining direct `subprocess.run` LXD config path in favour of the shared `_lxc` wrapper.
- Scope boundaries touched:
  - `tools/auto-mir/lxd_runner.py`
- Explicit non-goals:
  - No retry-policy changes for in-container commands.
  - No container lifecycle flow changes.
- Invariants preserved:
  - Container environment export still uses `lxc config set` for persistence.
  - Shared command logging/error semantics now cover this path as well.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: SKIP
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Behavior-preserving internal wrapper normalization only.
- Follow-up impacts:
  - LXD wrapper consolidation work is now limited to intentional higher-level execution API boundaries.

### Phase Ledger Entry: PR-34 LXD stdin exec wrapper normalization (slice 3)

- Date: 2026-07-10
- Promotion: no
- Intent: Route the remaining stdin-fed `lxc exec ... tee` write paths through the shared `_lxc` wrapper.
- Scope boundaries touched:
  - `tools/auto-mir/lxd_runner.py`
- Explicit non-goals:
  - No changes to apt-source patching semantics.
  - No changes to proposed-pocket enablement behavior.
- Invariants preserved:
  - Patched apt source content is still written via `tee` inside the container.
  - Shared command logging/error handling now also covers these write-back paths.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: SKIP
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Behavior-preserving wrapper normalization only.
- Follow-up impacts:
  - LXD wrapper consolidation is now complete aside from intentional host-level prerequisite probes.

### Phase Ledger Entry: PR-99 Refactor completion alignment

- Date: 2026-07-10
- Promotion: no
- Intent: Mark the 2026 phased structural refactor as complete and align architecture documentation with that completed state.
- Scope boundaries touched:
  - `tools/auto-mir/design.md`
  - `tools/auto-mir/decisions.md`
- Explicit non-goals:
  - No runtime code changes.
  - No validation-policy changes.
- Invariants preserved:
  - Steady-state gates remain `make test` plus advisory `make parity-contract`.
  - Historical phase entries remain the detailed audit trail of each incremental batch.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: SKIP
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Documentation-only completion alignment; runtime behavior unchanged.
- Follow-up impacts:
  - Implementation/refactor phase is complete; next work should be code review and functional testing.

### Phase Ledger Entry: PR-12 Evaluator fallback centralization (slice 1)

- Date: 2026-07-10
- Promotion: no
- Intent: Remove duplicated LLM-unavailable fallback logic by introducing a shared helper in `checks/llm_eval.py`.
- Scope boundaries touched:
  - `tools/auto-mir/checks/llm_eval.py`
- Explicit non-goals:
  - No prompt/evidence transformation changes.
  - No confidence, severity, or TODO policy changes.
- Invariants preserved:
  - `ev_to_ai` and `ai` modes still degrade to `status=unknown`, `confidence=low` on LLM errors.
  - Existing fallback messages and TODO generation semantics are unchanged.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: WARN (advisory mode; baseline fixtures absent)
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Behavior-preserving deduplication only; no output drift observed in test suite.
- Follow-up impacts:
  - Evaluator-path simplification continued in PR-25 through PR-30.

### Phase Ledger Entry: PR-22 Finding state transition normalization (slice 1)

- Date: 2026-07-10
- Promotion: no
- Intent: Start replacing manual finding field mutation with `Finding` helper methods in shared orchestration paths.
- Scope boundaries touched:
  - `tools/auto-mir/checks/__init__.py`
  - `tools/auto-mir/checks/deterministic.py`
- Explicit non-goals:
  - No check policy or severity policy changes.
  - No catalog or renderer behavior changes.
- Invariants preserved:
  - Language-gate skip path still yields `status=ok`, `severity=ok`, `confidence=high`.
  - Adapter-missing unknown fallback remains `status=unknown`, `severity=ok`, `confidence=low`.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: WARN (advisory mode; baseline fixtures absent)
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - No observed output drift in existing test suite; refactor is state-mutation-internal.
- Follow-up impacts:
  - Deterministic helper migration continued in PR-23 and later slices.

### Phase Ledger Entry: PR-23 Unknown-state helper normalization (slice 2)

- Date: 2026-07-10
- Promotion: no
- Intent: Complete helper-based unknown-state mutation for deterministic fallback paths.
- Scope boundaries touched:
  - `tools/auto-mir/models.py`
  - `tools/auto-mir/checks/deterministic.py`
  - `tools/auto-mir/tests/test_models.py`
  - `tools/auto-mir/tests/test_checks.py`
- Explicit non-goals:
  - No check decision policy changes.
  - No renderer or catalog schema changes.
- Invariants preserved:
  - Unknown fallback remains low-confidence with the same reviewer-facing message/TODO text.
  - PRF-10 adapter-error path remains `status=unknown` with recommended severity.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: SKIP
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Internal state transition wiring changed only; no behavior drift observed in tests.
- Follow-up impacts:
  - Deterministic check state mutation paths were normalized through helper methods.

### Phase Ledger Entry: PR-24 TODO normalization helper in orchestration (slice 3)

- Date: 2026-07-10
- Promotion: no
- Intent: Centralize unresolved TODO normalization in `Finding` helpers and remove orchestrator-level field mutation.
- Scope boundaries touched:
  - `tools/auto-mir/models.py`
  - `tools/auto-mir/checks/__init__.py`
  - `tools/auto-mir/tests/test_models.py`
- Explicit non-goals:
  - No evaluator routing changes.
  - No changes to catalog message/template policy.
- Invariants preserved:
  - Unresolved findings continue to render `TODO:`-prefixed reviewer actions.
  - `status=ok` findings continue to carry empty TODOs.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: SKIP
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Behavior-preserving normalization path extraction; no output drift observed in tests.
- Follow-up impacts:
  - Evaluator helper migration continued in PR-25 and subsequent slices.

### Phase Ledger Entry: PR-25 LLM unknown-path helper normalization (slice 4)

- Date: 2026-07-10
- Promotion: no
- Intent: Normalize LLM evaluator unknown-state fallbacks through shared `Finding` helpers.
- Scope boundaries touched:
  - `tools/auto-mir/checks/llm_eval.py`
  - `tools/auto-mir/tests/test_checks.py`
- Explicit non-goals:
  - No prompt rendering changes.
  - No model tier selection policy changes.
- Invariants preserved:
  - Human-only and LLM-unavailable checks remain unresolved and reviewer-driven.
  - Fallback TODO text and status routing remain unchanged in meaning.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: SKIP
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Internal fallback state mutation paths are unified; no policy drift expected.
- Follow-up impacts:
  - Core LLM response state mutation paths were migrated in PR-28.

### Phase Ledger Entry: PR-26 LLM option-response ok-path helper migration (slice 5)

- Date: 2026-07-10
- Promotion: no
- Intent: Migrate the option-response `outcome=ok` state mutation path to shared `Finding.succeed` helper semantics.
- Scope boundaries touched:
  - `tools/auto-mir/checks/llm_eval.py`
- Explicit non-goals:
  - No changes to `not-ok` option outcome routing.
  - No changes to option selection matching (`id`/`todo_ref`).
- Invariants preserved:
  - Option checks that resolve to `ok` keep canonical statement behavior and empty TODOs.
  - Human confirmation requirement remains enabled for AI-derived findings.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: SKIP
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Internal state mutation path simplification only; no intended output-policy changes.
- Follow-up impacts:
  - `not-ok` option response assignments were migrated in PR-27.

### Phase Ledger Entry: PR-27 LLM option-response not-ok helper migration (slice 6)

- Date: 2026-07-10
- Promotion: no
- Intent: Migrate option-response `not-ok` assignment path to `Finding.fail` and normalize TODO-ref prefix handling.
- Scope boundaries touched:
  - `tools/auto-mir/models.py`
  - `tools/auto-mir/checks/llm_eval.py`
  - `tools/auto-mir/tests/test_models.py`
  - `tools/auto-mir/tests/test_checks.py`
- Explicit non-goals:
  - No changes to option outcome policy (`ok`/`recommended`/`required`/`nack`).
  - No changes to option selection resolution logic.
- Invariants preserved:
  - Non-ok option responses continue to render reviewer TODOs.
  - Existing `TODO:` and `TODO-X:` prefixes remain stable and are not double-prefixed.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: SKIP
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Internal state mutation path consolidation only; no intended behavior drift.
- Follow-up impacts:
  - LLM response mapping now uses helpers for both option outcomes and unknown fallbacks.

### Phase Ledger Entry: PR-28 Core LLM response helper migration (slice 7)

- Date: 2026-07-10
- Promotion: no
- Intent: Route generic LLM response status transitions (`ok`/`not-ok`/`unknown`) through `Finding` helpers.
- Scope boundaries touched:
  - `tools/auto-mir/checks/llm_eval.py`
- Explicit non-goals:
  - No change to status/severity/confidence normalization rules.
  - No change to Summary option TODO aggregation behavior.
- Invariants preserved:
  - Canonical `ok` statement override remains in place for single-statement ev_to_ai checks.
  - Non-ok and unknown outcomes still receive default/normalized TODO text when absent.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: SKIP
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - State transition wiring simplified with no intended policy changes.
- Follow-up impacts:
  - Remaining direct assignment sites are intentionally limited to response payload extras (`risk_flags`, `evidence_refs`, confirmation flag).

### Phase Ledger Entry: PR-29 LLM option rationale helper cleanup (slice 8)

- Date: 2026-07-10
- Promotion: no
- Intent: Remove redundant direct rationale assignment in option response mapping and rely on helper-based state assignment.
- Scope boundaries touched:
  - `tools/auto-mir/checks/llm_eval.py`
  - `tools/auto-mir/tests/test_checks.py`
- Explicit non-goals:
  - No option-selection or outcome policy changes.
  - No changes to TODO routing semantics.
- Invariants preserved:
  - Option outcomes continue to propagate model rationale into findings.
  - Required/recommended option TODO behavior remains unchanged.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: SKIP
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Behavior-preserving deduplication; rationale propagation remains covered by tests.
- Follow-up impacts:
  - LLM state transitions and rationale propagation now consistently flow through helper methods.

### Phase Ledger Entry: PR-30 AI metadata helper extraction (slice 9)

- Date: 2026-07-10
- Promotion: no
- Intent: Extract repeated AI metadata assignment (`risk_flags`, `evidence_refs`, confirmation flag) into a shared `Finding` helper.
- Scope boundaries touched:
  - `tools/auto-mir/models.py`
  - `tools/auto-mir/checks/llm_eval.py`
  - `tools/auto-mir/tests/test_models.py`
- Explicit non-goals:
  - No changes to LLM status/severity/todo mapping behavior.
  - No changes to canonical message override policy.
- Invariants preserved:
  - Empty metadata payload fields do not clear previously set finding fields.
  - AI-derived findings remain marked as requiring human confirmation.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: SKIP
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Deduplicated metadata assignment only; no policy-level drift expected.
- Follow-up impacts:
  - Remaining direct field assignment sites are now limited to intentional semantic overrides.

### Phase Ledger Entry: PR-31 Non-prompt markdown convergence closure (slice 10)

- Date: 2026-07-10
- Promotion: no
- Intent: Close stale documentation follow-up markers after non-prompt markdown alignment audit.
- Scope boundaries touched:
  - `tools/auto-mir/decisions.md`
- Explicit non-goals:
  - No runtime code changes.
  - No prompt markdown changes.
- Invariants preserved:
  - Architecture/testing policy documentation remains aligned with current command surface.
  - Historical strict-parity retirement entries remain as historical context only.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: SKIP
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Documentation consistency update only; runtime behavior unchanged.
- Follow-up impacts:
  - Functional test and review can proceed on a stable, converged non-prompt markdown set.

### Phase Ledger Entry: PR-32 LLM RunContext typing completion (slice 11)

- Date: 2026-07-10
- Promotion: no
- Intent: Complete the previously planned type-boundary cleanup by typing `llm.py` against `RunContext` explicitly.
- Scope boundaries touched:
  - `tools/auto-mir/llm.py`
  - `tools/auto-mir/auto_mir.py`
- Explicit non-goals:
  - No provider, retry, or token-budget behavior changes.
  - No prompt/rendering changes.
- Invariants preserved:
  - `llm.call_llm()` runtime behavior and retry semantics remain unchanged.
  - Reasoning traces remain optional runtime metadata, now declared on `RunContext`.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: SKIP
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Type-only boundary tightening; no output drift expected.
- Follow-up impacts:
  - The earlier RunContext typing suggestion for `llm.py` is now closed.

### Phase Ledger Entry: PR-40/41 Documentation convergence (slice 1)

- Date: 2026-07-10
- Promotion: no
- Intent: Refresh architecture and subsystem documentation to match current runtime boundaries and flow.
- Scope boundaries touched:
  - `tools/auto-mir/design.md`
  - `tools/auto-mir/checks/README.md`
  - `tools/auto-mir/evidence/README.md`
  - `tools/auto-mir/render/README.md`
- Explicit non-goals:
  - No runtime code path or policy behavior changes.
  - No prompt content updates.
- Invariants preserved:
  - Documentation remains aligned with current command surface and stage model.
  - `design.md` now includes an ASCII architecture diagram without external dependencies.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: WARN (advisory mode; baseline fixtures absent)
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Documentation-only changes; runtime output behavior unchanged.
- Follow-up impacts:
  - Non-prompt markdown convergence completed in subsequent documentation cleanup slices.

### Phase Ledger Entry: PR-50 Guardrail retirement (strict parity gate)

- Date: 2026-07-10
- Promotion: no
- Intent: Retire temporary strict parity command-surface enforcement and move to steady-state advisory parity checks.
- Scope boundaries touched:
  - `tools/auto-mir/Makefile`
  - `tools/auto-mir/testing.md`
- Explicit non-goals:
  - No removal of characterization or contract tests.
  - No runtime pipeline behavior changes.
- Invariants preserved:
  - `make test` remains the primary mandatory gate.
  - `make parity-contract` remains available for baseline drift visibility.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: WARN (advisory mode; baseline fixtures absent)
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Strict parity enforcement path retired from Makefile; advisory parity monitoring retained.
- Follow-up impacts:
  - PR-51 finalizes steady-state verification wording and guardrail rationale.

### Phase Ledger Entry: PR-51 Steady-state testing policy update

- Date: 2026-07-10
- Promotion: no
- Intent: Align user-facing testing policy with post-refactor steady-state gates.
- Scope boundaries touched:
  - `tools/auto-mir/testing.md`
- Explicit non-goals:
  - No test implementation changes.
- Invariants preserved:
  - Existing lint/unit and integration guidance remains intact.
  - Baseline parity visibility remains documented via advisory checks.
- Validation run from `tools/auto-mir`:
  - `make lint`: PASS
  - `make test`: PASS
  - `make parity-contract`: WARN (advisory mode; baseline fixtures absent)
  - `python3 integration_smoke.py` (if applicable): SKIP
- Parity result summary:
  - Documentation now reflects settled post-refactor guardrail model.
- Follow-up impacts:
  - Functional test and review can proceed on a stable, documented validation surface.

## Traceability Decisions

- **SUM-3**: use upstream `ubuntu-archive-tools/component-mismatches` logic by fetching and
  running the original tooling (with prerequisites like germinate); avoid local
  reimplementation and avoid HTML parsing as primary logic. Fallback to reviewer TODO.
- **SUM-4**: missing team bug subscriber → emit recommendation that mentions promotion will
  stall later and the subscriber should be added now.
- **DEP-1**: do not rely on outdated `check-mir`; use runtime dependency extraction
  (`dpkg-query` preferred, `apt show` fallback) and component resolution via `apt policy`
  in the target release. Runtime deps are primary; build deps only matter for
  languages/headers that embed active code in final binaries.
- **DEP-3**: `-dev/-debug/-doc` extra excludes are recommendation-level only; hard blocker
  only if broader policy conditions are also triggered.
- **DEP-4**: deterministic test evidence collection + EV→AI interpretation + HUM final
  override. Use `autopkgtest.db` and web results. Weight by importance, not per-dep
  strictness.
- **ESL-2**: include `-static` build-log/invocation checks for static-linking detection.
- **ESL-5/6/8/9/10**: evaluate only when language gates indicate applicability.
- **Go/Rust conflicts**: MIR docs in this repo are authoritative over conflicting Debian
  guidance; results often become recommendations/dialogue rather than hard requirements.

## Security Decisions

- **SEC-1**: always check both the Ubuntu CVE tracker and the cvelistV5/NVD chain; AI risk
  synthesis required with mandatory human confirmation. Concerning patterns (including
  historically patched but risk-significant trends) surface as security-review-triggering
  findings.
- **SEC-3/SEC-4**: hard blockers (required remediation), not merely "security review maybe".
- **SEC-7**: include docs/manpage/package-description evidence in arbitrary web-content
  assessment.
- **SEC-11**: secure-boot/signature/attestation always implies security review path; no
  recommended-only middle state.
- **SEC-13**: EV→AI mitigation analysis with HUM final judgment.

### Security findings never populate the consolidated TODO blocks (2026-07-13)

- Promotion: no
- Decision: findings in the `[Security]` section are **excluded** from the
  Summary's consolidated `Required TODOs:` / `Recommended TODOs:` lists
  (`render._collect_todos_by_severity` skips `section == "Security"`).
- Rationale: a security signal is not an action item for the *reporter* to
  resolve. It is evidence for the human reviewer's single judgement call — "does
  this need a security review?" (SUM-6). Turning e.g. SEC-5 ("does parse
  untrusted data formats") into a "Recommended TODO #3" wrongly implied the
  reporter had to *do* something, when the correct handling is to leave the
  ACK/NACK-style security-review options and their reasoning in the Summary
  (SUM-6 lines) and list the detailed evidence in the `[Security]` Problems
  block. From there the reviewer decides; they can always promote a line
  manually if warranted.
- Reconciliation with the SEC-3/SEC-4 and SEC-11 hard-blocker notes above: those
  checks remain hard blockers and still (a) render in the `[Security]` Problems
  block and (b) drive the SUM-5 ACK/NACK verdict and SUM-6 security-review
  decision. What changed is only the *routing*: they no longer emit a duplicate
  line into the consolidated reporter TODO blocks. The blocking effect lives in
  the verdict, not in a reporter TODO.
- Scope: this is grouped and true for every `[Security]` check; no other section
  is affected (other sections still translate confident problems into
  Required/Recommended TODOs as before).

## Review types: fresh / rereview / reorg fast-paths (2026-07-13)

- Promotion: no
- Context: two MIR fast-paths exist beyond a normal (fresh) review —
  (1) voluntary opt-in re-reviews of packages long in main
  (mir-rereview/#opt-in-re-review) and (2) renamed/reorganised sources already
  in main under another name (mir-rereview/#renamed-or-reorganized-sources). In
  both, the reviewer runs an essentially normal review but treats every finding
  as non-blocking and recommendation-only.
- Decision: add a `review_type` concept resolved once per run.
  - CLI `--review-type {auto,fresh,rereview,reorg}` (default auto). A non-auto
    value forces the type (and is recorded with a rationale); `auto` runs
    detection in `review_type.detect_review_type()`.
  - Detection signals (best-effort, never raising):
    - reorg (checked first, more specific): reporter text mentions a
      rename/split/reorganisation; OR the new `lp-mir-history` adapter found a
      prior MIR bug under a different source name; OR dup-search shows a
      functionally-similar package already in main.
    - rereview: reporter text requests a (voluntary) re-review; OR all binary
      packages are already in main (dep-analysis has binaries while
      component-mismatches lists no promotion candidates).
    - else fresh.
  - Softening: for rereview/reorg, `checks._apply_review_type_softening()`
    downgrades every non-Summary finding with severity required/nack to
    recommended, in place, BEFORE the SUM-5/SUM-6 synthesis runs. This is
    deliberately blunt (Option A, user-confirmed 2026-07-13): even genuine hard
    blockers are softened, because policy says everything is non-blocking on
    these paths and the human can promote any line back to Required. Because
    softening runs before pass 2, the SUM-5 verdict naturally leans ACK (it sees
    no remaining required findings) — no prompt-template change was needed.
  - Rendering: a `Review type:` preamble line and a `[Summary]` NOTE flag the
    fast-path so the reviewer sees why findings were softened.
- New adapter `lp-mir-history` (host, best-effort, `adapters_optional` on
  RDO-1): searches Launchpad bug tasks for the current source and predecessor/
  dup-search candidate names with a server-side `search_text=MIR` filter and
  keeps only MIR-titled bugs (`\[mir\]` / whole-word `\bmir\b`). Inspired by the
  get-mir-bug helper but does not import or reuse it. 404/transient failures per
  candidate are skipped rather than failing the adapter.

## Early review-type pre-detection for reporter template gate (2026-07-15)

- Promotion: no
- Context: the reporter-template hard-stop in `lp_intake.run()` (Stage 1) fired
  before `review_type.detect_review_type()` (Stage 4) could classify a run as a
  re-review/reorg. This blocked legitimate re-review/reorg runs (e.g. a source
  rename like mysql-8.4 → mysql-9.7) where the reporter did not fill a full
  template, which MIR policy explicitly allows
  (mir-rereview: "We'd appreciate it if the owning team could file a
  MIR-reporter bug for it, but would not insist on it if they can't").
- Root cause: stage-ordering conflict. The hard-stop in Stage 1 used only
  `_find_reporter_mir_content()`, while the review-type detection that would
  have allowed the run to proceed lived in Stage 4 — after the hard-stop. The
  evidence adapters feeding detection (`lp-mir-history`, `dup-search`,
  `dep-analysis`, `component-mismatches`) run in Stage 3 and are therefore not
  available at Stage 1.
- Decision:
  - Add `review_type.pre_detect_review_type()` — a Stage-1-compatible function
    that uses only signals available before evidence collection: the
    `--review-type` CLI override and bug text patterns (title, description,
    comments, reporter content). The authoritative `detect_review_type()`
    in Stage 4 remains unchanged and still considers evidence adapters.
  - The two functions share `_text_signals()`, a helper that scans the combined
    bug text with the existing `_REREVIEW_TEXT_RE` and `_REORG_TEXT_RE`
    regexes, so text-based signal logic is never duplicated.
  - `lp_intake.run()` now calls `pre_detect_review_type()` when reporter
    template content is not found. If the result is rereview or reorg, the run
    proceeds with `ctx.reporter_mir_content = ""` and a warning. If fresh, the
    hard-stop fires with an improved message that mentions
    `--review-type rereview/reorg` as the override.
  - Extend `_reporter_text()` to scan bug comments (not just reporter content,
    title, and description) so a re-review/reorg mention in a comment is
    detected by both pre-detection and full detection.
  - Add `\breplac(?:e|es|ed|ing)\b` to `_REORG_TEXT_RE` with word boundaries
    so "mysql-9.7 to replace mysql-8.4" is detected as a reorg signal even
    without the mir-rereview URL. Word boundaries prevent false positives on
    "replacement" (noun).
  - Make SUM-2 (Reporter MIR content present) review-type-aware: when
    `ctx.review_type` is rereview or reorg and `reporter_mir_content` is empty,
    SUM-2 resolves to ok with a dedicated `rereview_ok_message` instead of
    NACKing and relying on the softening pass.
- Non-goals (user-confirmed):
  - Prior reviewer MIR output in comments (`_find_prior_reviews` /
    `prior_review_comment_indices`) stays a console warning only; it is not
    promoted to a formal review-type detection signal.
  - Fresh reviews without a reporter template still hard-stop; the fix is not
    a blanket "proceed without template" — it requires a re-review/reorg
    signal or override.
- Consequences:
  - A pre-detection of `fresh` is not final: Stage 4 full detection may still
    upgrade it to rereview/reorg once evidence adapters are available. The
    reverse (pre-detect reorg, full detect fresh) is possible but unlikely
    since text signals are a strong indicator.
  - All downstream consumers of `reporter_mir_content` already handle empty
    strings gracefully; the only one that NACKed (SUM-2) now resolves to ok.
  - The mysql-9.7 rename case (bug 2160635) is now detected as reorg via
    "replace" in the bug description and the mir-rereview URL, allowing the
    review to proceed without a reporter template.
- Validation from `tools/auto-mir`: `make test` PASS (538 passed, 3 skipped).

## Build / Test Decisions

- **CB-1**: combine local sbuild result with Launchpad multi-arch build state via API.
- **CB-2**: inspect `debian/rules` wiring to verify test failure stops build; build log
  alone is often insufficient.
- **CB non-trivial**: deterministic discovery of tests; AI-assisted trivial/non-trivial
  quality assessment; reviewer override.
- **CB-4/5**: special HW exhaustion judgment remains human-only.
- **CB-6**: reverse-dep autopkgtest summary EV→AI; leaves the final call to the human
  reviewer (never auto-ACK). Fed by the `reverse-deps` + `consumer-autopkgtests`
  adapters (see the 2026-07-13 feedback-round-4 entry). On retrieval failure it falls
  back to the human-only TODO and says the reverse-dep data was unavailable.
- **CB-7**: python2 dependency is a hard blocker.

## Packaging / Maintenance Decisions

- **PRF-1**: escalate to required/NACK only when large unjustified delta also has no
  minimization activity in progress.
- **PRF-2**: symbols applicability must support N/A variants and TODO option pruning;
  language-aware.
- **PRF-5/6**: intentional stable cadence can still resolve to `ok` (explanatory statement);
  dead/unmaintained trajectory can reach NACK-level.
- **URF-6**: aggregate Launchpad package bugspace (`bugs.launchpad.net/ubuntu/+source/PKG`)
  via API + Debian BTS + upstream issue evidence.
- **PRF-8**: Launchpad upload history + MOTU/team context as EV→AI suggested rating, HUM
  final call.
- **RDO-3**: AI drafts tentative verdict suggestion with explicit HUM override flag.

## Catalog Schema Decisions

- **Format**: YAML.
- **Granularity**: one entry per reviewer TODO line (max traceability), with logical check
  option lists for TODO-A/B/C variants inside one logical check.
- **Fallback on evidence failure**: emit explicit reviewer TODO and continue partial report;
  no silent inference.
- **Security trigger output**: dedicated structured field + templated summary line in output.
- **SEC-1 confidence scale**: 3-band — `low`, `medium`, `high`.
- **Hard blockers**: always emit required TODO and block ACK suggestion.
- **Policy snapshot metadata**: include MIR policy/template file hashes in report metadata.
- **Tooling bootstrap (superseded 2026-07-14)**: default to latest upstream branch each
  run for freshness; optional `--pin-tooling <commit>` mode for reproducible
  benchmark/replay runs.
- **Traceability IDs**: semantic TODO identifiers are primary; optional line-number metadata
  is supplemental only (stable across template edits).

## Token / Performance Decisions (Phase 7)

- Reduced evidence payload truncation from 3000 to 500 chars for general strings.
- Large known fields (lintian_output, debian_*, raw_output) now produce summaries only
  (error/warning counts, preview lines) instead of full content.
- List truncation to 10 items + summary line.
- Result: payload fits within gpt-4o-mini 8000 token limit.

## Data Source Decisions (Phase 7)

- **CVE tracker**: replaced flaky ubuntu.com API (returns 422 frequently) with direct
  OVAL JSON parsing from security-metadata.canonical.com. Downloads XZ-compressed OVAL
  JSON, extracts CVEs directly. Added retry-once on transient HTTP errors.
- **cve.org replacement (cvelistV5 + NVD)**: dropped the unreliable cve.org search API in
  favour of a three-adapter chain:
  - `cve-search-terms` (host/heuristic): produces the candidate search terms. Has no hard
    dependencies so a missing upstream match never cascades and skips the whole CVE chain.
  - `cvelist-scan` (host): downloads the documented
    `*_all_CVEs_at_midnight.zip` cvelistV5 baseline on the host and word-matches every record
    with the same stdlib-only scanner logic (`evidence/cvelist_scan_invm.py`). "Parse a lot,
    identify few": the whole corpus is scanned but only a handful of candidate CVE IDs are
    returned.
  - `nvd-enrich` (host/web): enriches each candidate with normalized CVSS severity, CWE and
    CPE version ranges from NVD API 2.0, falling back to the cvelist record data when NVD is
    unavailable. Runs without an API key (5 req/30s budget enforced via a small inter-request
    sleep).
  - Predecessor/sibling terms (e.g. `lua5.5` -> historical `lua` CVEs) are produced by a
    best-effort small-tier LLM call inside `cve-search-terms` (prompt
    `prompts/cve_predecessor_terms.md`), bounded to a handful of distinctive terms and
    instructed to avoid broad ambiguous words. The call degrades gracefully (no LLM token or
    any LLMError -> current-only terms). Matching findings are tagged `kind="predecessor"`
    and surfaced as clearly-labelled *historical* evidence that can influence SEC-1 severity
    (raising the recommendation toward a security review) but never hard-blocks the current
    version.
- **Autopkgtest**: replaced web UI scraping with direct SQLite database download from
  autopkgtest.ubuntu.com/static/autopkgtest.db. Queries results table directly.

## Review Feedback Round (bug 2155757 / lua5.5)

Outcomes from the first real reviewer feedback. Promotion: no (local rationale).

### Rendering / TODO routing
- A finding renders in exactly one of: its section OK block, its section
  Problems block (confirmed), or its section "Left to decide" (reviewer
  judgement). Summary decision checks (ACK/NACK verdict SUM-5, security review
  SUM-6) render their options inline only. The catalog flag `aggregate_todo`
  (carried onto `Finding`) marks the few Summary findings (SUM-4 team
  subscriber) whose actionable TODO is forwarded to the consolidated
  Required/Recommended blocks; everything else in Summary is excluded from
  aggregation so nothing is listed twice.
- Every non-summary section always renders a Problems status, emitting
  `Problems: none` (blank line above) when clean.
- Consolidated Required/Recommended TODOs are auto-numbered `- #N` with one
  continuous index, stripping internal `TODO:`/`TODO-X:` markers.
- Combined language gates (e.g. `go|rust` on ESL-1) suppress their umbrella OK
  message so only the per-language ESL-4/ESL-8 lines render.

### Check correctness / new evidence
- **ESL-2**: static linking is judged from built `.deb` contents (`file`
  "statically linked"), not raw `-static` build-log tokens. libtool
  `-static <pkg>.la` (own convenience lib) and configure probes are not static
  linking; cross-source-package archive linking stays ESL-3's job (Built-Using).
- **PRF-2**: a shipped `debian/*.symbols` file is authoritative for "symbols
  tracking is in place"; shared libraries are recognised from soname-versioned
  package names (control + built deb names), not a `.so` substring in control.
- **CB-1**: Launchpad build records remain authoritative for the FTBFS verdict;
  the local sbuild result is surfaced only as a hint when LP data is missing.
- **URF-1**: generic dpkg-source/dpkg-buildflags diagnostics are filtered as
  noise; genuine toolchain warnings route to "Left to decide" (reviewer judges),
  real errors stay a Problem.
- **URF-4/URF-5**: scan the whole source tree (`grep -RIn`, `find -user nobody`,
  `find -perm -4000/-2000`) and the built binaries (single deb-extraction pass
  shared with ESL-2), with test-context filtering. URF-4 source-tree 'nobody'
  hits additionally require a user-reference code context (quoted strings,
  assignments, chown-style, privilege-dropping functions, CLI flags) so the
  English pronoun in comments/prose does not trip the check; non-executable doc
  files (including Debian's `*.README.Debian`) are filtered for both checks.
- **PRF-5**: cross-series publishing history is collected and a deterministic
  `release_cadence` descriptor (good <=183d avg, slow <=400d, else sporadic) is
  computed and fed to the LLM as primary evidence.
- **PRF-7**: new `ubuntu-upload-permission` adapter lists uploaders so the LLM
  can tell a MOTU-only/sync-from-Debian package (OK) from one with a MOTU-only
  regular Ubuntu uploader.
- **PRF-1**: new `git-ubuntu-delta` adapter classifies the delta from the
  changelog version; git-ubuntu is run only for `...ubuntuN` versions (a pure
  Debian sync carries no delta), removing the hallucinated "provide git-ubuntu
  log/diff" TODO.
- **CB-2**: build-test-hints (rules wiring, nocheck, runners, failures-ignored,
  log pass/fail) are extracted into the payload; the policy decides
  ok/required/left-to-decide and folds the reporter's stated reason for a
  missing suite into the message.

## Initial Modularization and Testing Infrastructure

- **Template rendering simplification**: removed body-only mode from render_review_template.py
  and updated Makefile commands. The old "build the full file" mode was no longer needed
  after catalog-driven template generation was established.

- **Prior review detection**: added detection of prior MIR review comments in Launchpad bugs
  to provide context and avoid duplicating work. The tool now identifies existing reviews
  and can reference them in the generated output.

- **Multi-binary-package handling**: implemented graceful handling of packages with multiple
  binary packages. The tool now correctly processes and reports on all binary packages
  produced by a source package.

- **Output path visibility**: added prominent display of output file paths at the end of
  each run to make it easier for users to locate generated reports and evidence.

- **Version tracking removal**: removed embedded version/hash tracking from generated output.
  Git history is now the authoritative source for version information, eliminating redundancy
  and potential inconsistencies.

- **Three-tier testing strategy**: established comprehensive test coverage with:
  - Unit tests for individual check evaluators (test_checks.py)
  - Integration tests for Launchpad intake logic (test_lp_intake.py)
  - End-to-end tests for render output validation (test_render.py)

- **Modular code structure**: refactored from flat file layout to modular package structure:
  - Split monolithic checks.py into checks/ package with deterministic.py, llm_eval.py
  - Created evidence/ package for evidence collection adapters
  - Extracted models.py for shared data structures (Finding dataclass)
  - This modularization improved code navigation, testability, and maintainability

## Refactoring Decisions (Phases A-E)

### Phase A: Documentation and Type Safety

- **TypedDict for adapter contracts**: introduced `evidence/types.py` with TypedDict
  definitions for all adapter return types. Provides IDE autocomplete, type checking,
  and self-documenting contracts between adapters and check evaluators.
- **Finding dataclass enhancement**: added comprehensive docstring with field descriptions,
  invariants, and usage examples to improve developer onboarding.

### Phase B: Code Organization

- **Evidence module split**: split monolithic `evidence/__init__.py` into logical submodules:
  - `evidence/host_adapters.py` — host-side adapters (Launchpad API, CVE tracker, autopkgtest)
  - `evidence/guest_adapters.py` — in-guest adapters (packaging, dependencies, sbuild)
  - `evidence/__init__.py` — orchestration and adapter registry
  - Rationale: improves code navigation, reduces file size, clarifies execution context.
- **Language gates extraction**: moved language detection logic to dedicated
  `checks/language_gates.py` module. Separates concerns and makes language-specific
  check logic easier to locate and maintain.
- **Finding factory methods**: added `Finding.ok()`, `Finding.not_ok()`, and
  `Finding.unknown()` class methods to simplify finding creation and enforce
  consistent field initialization patterns.

### Phase C: Testing Infrastructure

- **Integration tests**: added `tests/test_evidence.py` with integration tests for
  evidence collection orchestration, adapter dependency ordering, and error handling.
- **Catalog loading tests**: added `tests/test_catalog.py` to verify catalog parsing
  and validation logic.
- **Render snapshot tests**: added snapshot tests to `tests/test_render.py` to ensure
  review draft output remains stable across refactors.
- **Test coverage**: all new modules include corresponding test files to prevent
  regressions during future changes.

### Phase D: Type Safety and Validation

- **Catalog validation**: added `validate_catalog()` function to catch malformed
  catalogs early. Validates required sections, check fields, adapter references,
  and enum values. Integrated into `load_catalog()` to fail fast on schema errors.
- **Finding invariant validation**: added `__post_init__()` method to Finding dataclass
  to enforce invariants at construction time:
  - `status="ok"` implies `severity="ok"`
  - `status="not-ok"` requires non-empty `todo` field
  - Confidence, severity, and status must be valid enum values
- **Enum definitions**: added `catalog_enums.py` with `AdapterID` and `CheckID` enums
  to provide type safety for adapter and check identifiers, catching typos at
  development time rather than runtime.

### Phase E: Retry Utility Extraction

- **Tenacity adoption**: replaced custom retry implementations with python3-tenacity
  library (>=8.0.0). Provides well-tested, standardized retry decorators with
  exponential backoff, jitter, and configurable stop conditions.
- **Retry utilities module**: created `utils/retry.py` with three retry decorators:
  - `retry_transient_network()` — for network operations (ConnectionError, TimeoutError,
    urllib.error.URLError, 5xx HTTP errors)
  - `retry_rate_limited()` — for API calls with rate limiting (429, 5xx errors)
  - `retry_guest_command()` — for LXD-guest commands with transient failures
    (503 errors, DNS failures, connection timeouts)
- **Refactored modules**: updated `lxd_runner.py` and `llm.py` to use tenacity decorators
  instead of custom retry loops. Improves maintainability and reduces code duplication.
- **Dependency management**: added `tenacity>=8.0.0` to `pyproject.toml` dependencies.

## Structural Refactoring and Registries
**Context:** As auto-mir scaled, the `evidence/__init__.py` and `checks/__init__.py` files accumulated massive manual dictionaries tracking adapter dependencies and check support matrices. Furthermore, multiple overlapping subprocess helpers for container and host execution scattered error handling logic.
**Decision:**
- Adopted `graphlib.TopologicalSorter` to handle evidence dependency sorting dynamically, removing custom cycle-breaking logic in `evidence/__init__.py`.
- Replaced hard-coded config dictionaries in `evidence/__init__.py` and `checks/__init__.py` with decorator-based registries (e.g. `@adapter`, `@evaluator`, `@deterministic_check`). Check and adapter configurations now live natively with their implementations.
- Extracted language gate logic to a decorator rather than applying manual conditional wrapping within `checks/__init__.py`.
- Consolidated all CLI wrappers (`_lxc`, `_run_host`, `exec_in`) into one standardized `subprocess.run` handler in `lxd_runner.py` for uniform logging logic.
**Consequences:** Boilerplate has been significantly reduced, making it trivial to add new checks and evidence adapters without touching multiple files.

## SUM-4 Team Mapping Source (2026-06-02)
**Context:** The SUM-4 check needs to verify that a source package has a structural team bug subscription. The authoritative list of valid subscriber teams is maintained in `ubuntu-archive-tools/lputils.py` as `owner_names` (20+ teams), but we cannot depend on that package being installed. A separate `team_names` list in the same file contains display-only teams that should NOT count as valid subscribers.

**Options considered:**
1. Hardcode the full `owner_names` list in auto-mir (brittle, requires manual sync)
2. Fetch `package-team-mapping.json` from static-reports.ubuntu.com and filter out known non-subscriber teams
3. Query Launchpad API directly for each known team (slow, rate-limited, complex)

**Decision:** Option 2 - Fetch the JSON report and maintain a small exclusion list of non-subscriber teams.

**Tradeoffs:**
- ✅ Single source of truth: JSON is generated from authoritative lputils.py
- ✅ Minimal maintenance: only track 3 non-subscriber teams vs 20+ subscriber teams
- ✅ Self-documenting: exclusion list is small and stable
- ✅ Future-proof: new valid teams automatically work
- ❌ Runtime network dependency (acceptable per existing adapter patterns)
- ❌ If new display-only teams are added to lputils.py, we need to update our exclusion list (rare, documented)

**Implementation:** `evidence/team_mapping_adapter.py` fetches `https://static-reports.ubuntu.com/package-team-mapping.json`, filters out `NON_SUBSCRIBER_TEAMS = {kubuntu-bugs, pkg-ime, translators-packages}`, and checks which remaining teams have subscribed to the source package.

## Check Message Templates in Catalog (2026-06-11)

**Context:** Check evaluators currently emit reviewer-facing `Finding.message` and
`Finding.todo` text directly in code. This caused drift between policy/catalog intent
and runtime wording.

**Decision:**
- Add per-check message templates under `checks[].messages` in `catalog.yaml`.
- Use Python `str.format` placeholders for dynamic substitution.
- Keep runtime architecture unchanged:
  - checks evaluate evidence and bind values,
  - checks render templates into `Finding.message/todo`,
  - renderer remains presentation-only.
- Enforce strict validation for migrated checks:
  - required template keys must exist,
  - required placeholders must exist,
  - format syntax errors fail validation.

**Scope and rollout:**
- Rollout started with DEP-3 and expanded to deterministic checks and
  `ai`/`ev_to_ai`/`human_only` fallback/static paths.
- Validation now enforces required templates by mode (`llm_unavailable_message`
  for `ai`/`ev_to_ai`, `human_only_message` + `human_only_todo` for
  `human_only`) plus per-check strict placeholder rules for deterministic checks.
- Static renderer labels (`OK:`, `Problems:`, `Left to decide:`) stay in code for now.

**Consequences:**
- Better declarative traceability of potential output text in catalog.
- Dynamic evidence-specific phrasing preserved via placeholder binding.
- Additional schema/validation complexity is accepted to prevent silent drift.

## Dual-Model Routing and LLM Error Handling (2026-06-12)

**Context:**
The previous single-model CLI configuration could not balance cost and quality
across different check complexities, and ambiguity around fallback semantics
caused confusion.

**Decision:**
- Replace `--llm-model` with two explicit optional flags:
  - `--llm-model-small`
  - `--llm-model-large`
- Keep openai-compatible defaults when omitted:
  - `z-ai/glm-4.7` (small)
  - `z-ai/glm-5.2` (large)
- Route `ai` checks to large tier, and route `ev_to_ai` checks using lightweight
  complexity thresholds over rendered prompt and serialized evidence size.
- LLM failures on both tiers degrade gracefully to low-confidence manual-review
  fallback output. No hard fail-fast behavior is applied for large-tier errors.

**Consequences:**
- Clearer operator control without flag-precedence conflicts.
- Improved average quality on complex checks while preserving cost control on
  simpler checks.
- Consistent fallback semantics across both tiers reduce operational surprise.

## LLM Evidence Reducers and Comment Exclusion (2026-06-12)

**Context:**
Large MIR cases showed that raw adapter payloads (especially large file lists and
build logs) can dominate prompt context. For several LLM checks, Launchpad bug
comments did not improve decision quality and only increased noise.

**Decision:**
- Remove `lp-bug-api` evidence dependency for these LLM checks:
  - `SUM-6`, `RDO-1`, `SEC-5`, `SEC-6`, `SEC-7`, `CB-4`
- Add `packaging-source.file_listing` reducer policy:
  - Strip common leading path prefix when present.
  - Keep full listing up to 1000 paths.
  - Above 1000, send capped normalized listing plus summary metadata.
- Add `sbuild.build_log` two-step retrieval policy:
  - First pass sends condensed line-numbered summary.
  - Model may request up to 3 additional snippets by line range or regex pattern.
  - Runtime executes one follow-up LLM call with requested snippets.

**Consequences:**
- Better context efficiency on large MIR inputs.
- More reliable evidence focus for security and hardware-related LLM checks.
- Keeps interaction bounded and deterministic (single follow-up round, max 3 requests).

## OpenAI-Compatible-Only LLM Path and Parser Hardening (2026-06-25)

**Context:**
Operational runs showed that maintaining multiple auth/provider paths increased
complexity without improving reliability, and real provider responses can include
`choices[0].message.content = null` or structured content parts instead of a
single string.

**Decision:**
- Remove Copilot-specific support and provider auto-failover behavior.
- Keep a single openai-compatible auth/runtime path:
  - Auth via `OPENAI_API_KEY`
  - Optional base override via `OPENAI_API_BASE`
- Keep model tier defaults:
  - small: `z-ai/glm-4.7`
  - large: `z-ai/glm-5.2`
- Harden response parsing to normalize non-string message content and convert
  null/unsupported content into explicit `LLMError` instead of uncaught
  attribute errors.

**Consequences:**
- Simpler operational surface and clearer failure modes.
- Stage 4 LLM parsing now fails gracefully with actionable errors when provider
  response content is null or unexpectedly structured.
- Added regression tests for null and list-based message content handling.

## Prompt-Injection Mitigation via Spotlighting (2026-06-26)

Promotion: no

**Context:**
Launchpad bug text — title, description, and comments — is attacker-controllable:
anyone with a Launchpad account can post content on an MIR bug. That text is fed
into LLM prompts (reporter MIR content, bug metadata, the `lp-bug-api` adapter,
and the CVE predecessor-terms helper), making it an attack surface for prompt
injection. Other evidence sources (package files, build logs, Ubuntu infra APIs)
are lower risk and out of scope for this change.

We evaluated dedicated defences: ML-based detectors (LLM Guard `PromptInjection`,
Rebuff) and external guard APIs (Lakera). All were rejected for this tool:

- ML detectors pull in heavy dependencies (torch/transformers) or extra LLM
  calls, inflating the footprint that has to run alongside the LXD workflow.
- External guard APIs send untrusted *and* package-derived content to a third
  party (privacy/data-egress) and add network, cost, and availability surface.
- Both add ongoing maintenance and supply-chain burden disproportionate to a
  tool that only ever produces a *draft* for a human.

**Decision:**
- Use lightweight "spotlighting" — the standard, dependency-free process —
  implemented in `utils/llm_sanitize.py` and applied at the few points where
  untrusted text enters a prompt:
  - Detect instruction-like patterns at intake (`lp_intake._evaluate_injection_risk`),
    record indicators on `ctx.bug`, warn prominently, and gate the run on
    reviewer confirmation. The gate fails closed (EOF/negative answer aborts).
  - Neutralise chat-structure tokens (role markers, `<|...|>`, control chars)
    and wrap untrusted fields in a per-run nonce'd `<<UNTRUSTED_DATA ...>>`
    envelope so injected text cannot forge the closing delimiter.
  - Harden the LLM system prompt and prompt templates to treat envelope content
    as data only and to raise a `prompt-injection` risk flag on manipulation
    attempts.
- Scope is limited to Launchpad bug text; package-derived evidence is not
  enveloped at this time.

**Rationale:**
- Better maintainability: a small, self-contained, stdlib-only module with no
  model to retrain or service to operate.
- No third-party dependence: nothing is sent to an external classifier; no new
  failure or data-egress surface.
- Limited dependencies: stays within the tool's existing stdlib + launchpadlib
  footprint, which matters for the constrained LXD runtime.
- Human-in-the-loop backstop: every run produces a draft that a human MIR
  reviewer must vet before any action, so the tool never acts autonomously on
  model output.

**Residual risk (accepted):**
- Spotlighting reduces, but cannot eliminate, prompt injection. A crafted bug
  could still bias the *wording* of a generated draft.
- It cannot trigger actions or exfiltrate secrets: the only output is a review
  draft, and existing guards constrain it — strict JSON schema, whitelisted
  status/severity/confidence enums and `human_confirmation_required` always
  set. The later 2026-07-09 outcome-model decision permits high-confidence AI
  findings to render as problems; human confirmation remains mandatory.
- The mandatory final human review of the draft is the authoritative safeguard;
  the injection warning at intake tells the reviewer when to apply extra
  scrutiny.

**Consequences:**
- One new module (`utils/llm_sanitize.py`) plus small call-site changes in
  `lp_intake.py`, `llm.py`, `checks/llm_eval.py`, and `evidence/host_adapters.py`.
- A new interactive confirmation gate can abort runs on suspicious bug content;
  non-interactive runs abort by default when indicators are present.
- Added unit tests for detection, neutralisation, enveloping, and the gate.

## User Feedback Round 2 (bugs 2158712 libgav1 / 2155204 atkmm)

Nine reviewer-reported issues from the first real runs, and how they were resolved.
Promotion: no (implementation detail; the durable rules are captured per-check above).

- **Rendering — empty "Left to decide"**: the renderer no longer emits
  `Left to decide: None`. An empty block carries no meaning (unlike
  `Problems: none`, which asserts checks ran and found nothing), so it is
  omitted. Both `_render_section` and `_render_summary_section` in
  `render/__init__.py` do this. (issue 3)
- **Template fidelity for ev_to_ai OK lines (option render mechanism)**:
  ev_to_ai/ai option checks now carry a canonical `render` statement and an
  `outcome` (`ok|recommended|required|nack`) per option. The model returns a
  `selected_option` id; `checks/llm_eval._apply_option_response` emits that
  option's statement verbatim at its outcome severity, with the model's
  reasoning appended only in parentheses. Single-statement ev_to_ai checks
  reuse the canonical statement from `todo_refs[0]` (unless it is a placeholder
  or a Summary decision check). Catalog validation (`catalog._validate_check_options`)
  enforces `render`+`outcome` on all non-Summary ev_to_ai/ai option checks. (issues 2, 4, 7)
- **RDO-2 owning team vs subscriber**: RDO-2 now also consumes `team-mapping`.
  An existing team bug subscriber satisfies ownership (status ok, team named,
  no TODO). Absence yields a recommended (never required) note — lack of a
  subscriber blocks AA promotion, not the MIR ACK. This removes the false
  "Required" TODO when a subscriber already exists. (issue 1)
- **ESL-11 test-only vendoring**: `packaging-source` now classifies
  `vendored_dirs` into `shipped_vendored_dirs`, excluding directories confined
  to test/example/doc paths (e.g. `tests/third_party`). ESL-11 selects
  "Does not include vendored code" when nothing is shipped, so test-only
  vendoring no longer produces a spurious refresh-documentation TODO. (issue 2)
- **lp-build-api build records**: `collect_lp_build_api` now enumerates builds
  via `archive.getPublishedSources(...).getBuilds()` (newest publication in the
  target series) before falling back to the older `getBuildRecords` paths, so
  CB-1 sees the real multi-arch pass state instead of "no Launchpad build
  records". (issue 5)
- **autopkgtest series resolution**: the autopkgtest DB is keyed by codename,
  not the alias "devel". `collect_autopkgtest` resolves candidates via
  `distro-info` (devel codename first, newest supported stable as fallback for a
  fresh cycle) and records which release the results came from. (issue 6a)
- **CB-3 test non-triviality**: `packaging-source` now captures
  `debian/tests/control`; CB-3 combines it with the fixed autopkgtest results to
  recognise a real functional test as non-trivial and passing. (issue 6a)
- **CB-5 special-hardware gating**: CB-5 is now deterministic and gated on CB-4.
  When CB-4 concludes no special hardware is needed, CB-5 resolves ok (no TODO);
  otherwise it asks for reviewer judgment. Pass-1 findings are exposed on
  `ctx.findings` incrementally so a later check can consult an earlier one. (issue 6b)
- **PRF-1 delta reasonableness**: `git-ubuntu-delta` is collected (adapters_optional
  are now collected best-effort) and adds `delta_category` ("tests-only" when the
  diffstat only touches `debian/tests`). PRF-1 treats tests-only or fully-upstreamed
  deltas as reasonable/ok and always summarises what the delta changes. (issue 7)
- **PRF-9 rules cleanliness**: the full `debian/rules` is now passed to PRF-9
  (per-check `keep_full_fields` bypasses the 300-char summary), and the policy
  encodes the heuristic: base dh + non-disabling overrides = clean; disabling
  hardening/tests or large/complex rules = reviewer judgment with a summary. (issue 8)
- **URF-8/URF-9 UI judgment**: both are now ev_to_ai option checks. Whether a
  package is a user-facing desktop/user-visible program is judged from Section,
  GUI-toolkit dependencies, the description and general knowledge — NOT from the
  presence of a `.desktop`/translation file (a desktop app missing its `.desktop`
  file must still be caught). The `.desktop`/translation facts are surfaced by
  `packaging-source` for verification only. Libraries/CLI tools take the easy way
  out ("not part of the UI"). (issue 9)
- **URF-1 build errors vs test output**: `_parse_build_log_issues` now matches
  only compiler/linker/build-tool diagnostics and skips per-test runner output
  (ctest "N: " prefixed lines), so a decoder emitting "ERROR ... Failed to parse"
  while decoding a fixture is no longer mistaken for a build error. (further consideration, included)

## 2026-07-09 — libgav1 (bug 2158712) feedback round 3

- **Three-path outcome model (feedback #2/#3/#4/#5)**: every finding is now
  classified as `ok`, `problem`, or `undecided` by `render.finding_outcome_class`.
  A `problem` is a deterministic not-ok OR an AI not-ok reported with high
  confidence; it renders in Problems and is surfaced as a Summary Required/
  Recommended TODO. Everything else that is not-ok/unknown is `undecided` and
  renders ONLY in the section's "Left to decide" — it is no longer duplicated
  into the Summary TODOs (the previous `_collect_todos_by_severity` pulled any
  not-ok finding regardless of confidence).
- **Rationale is a first-class field**: `Finding.rationale` holds the evidence/
  reasoning separately from the reviewer statement. The renderer composes it as
  an indented parenthetical for all three paths, so ok/problem/undecided lines
  all carry the "why". Undecided lines keep the original template statement and
  append "(Can't decide: …)".
- **Negation stored, not rewritten (feedback #5)**: single-dimensional checks
  carry an explicit `negated_statement` in the catalog (e.g. CB-1
  "does FTBFS currently"). The renderer uses it for problems; option checks need
  none. Validated non-empty by `catalog.py`.
- **AI confidence cap relaxed (Option A)**: `_apply_llm_response` no longer caps
  AI confidence at medium, so a clear-cut model verdict can raise a Problem/TODO.
  Human confirmation is still always required. The ev_to_ai prompt/policies
  reserve "high" for decisive cases.
- **Analyse the -proposed source (feedback #7)**: `--source-pocket
  {auto,release,proposed}` (default auto). The container enables
  `<codename>-proposed`; packaging-source (now depending on lp-package-api) pins
  the published -proposed version via `apt-get source pkg=<version>` and records
  the analysed version+pocket (shown in the draft preamble); sbuild adds
  -proposed as an `--extra-repository`. Auto falls back to release when no
  -proposed version exists.
- **CB-3 autopkgtest authority (feedback #1)**: the autopkgtest DB pass/fail
  state is authoritative for whether tests run and pass; debian/tests/control
  (now visible via -proposed) confirms declaration and non-triviality. The tool
  must never report a missing test suite while the DB shows passing tests.
- **PRF-2 symbols by shared library, not language (feedback #8)**: the presence
  of a `.so` — not the language — governs whether symbols tracking is required.
  `.symbols` is authoritative and checked first; the python/go/rust
  short-circuit was removed; `_is_python_package` was tightened to require a real
  Python packaging signal rather than any stray `.py`.
- **dup-search adapter (feedback #6)**: a best-effort, suggestion-only adapter
  derives functional search terms from the package description (LLM), probes the
  archive with `apt-cache search`, excludes own binaries, and tags candidates
  with their component. RDO-1 consumes it and, on LLM failure, still surfaces the
  candidates as a fallback rationale.
- **LLM JSON-retry robustness (consideration #1)**: a malformed HTTP envelope now
  raises the retryable `LLMEnvelopeError`, and the one-shot retry appends a
  strict "reply with ONLY valid JSON" instruction rather than only enlarging the
  token budget.

## 2026-07-13 — Host-side web download resilience hardening

**Context:**
- Real runs hit `autopkgtest.db` download `HTTP 429` from
  `https://autopkgtest.ubuntu.com/static/autopkgtest.db`.
- The prior `autopkgtest-db` path had no retry; OVAL had a bespoke one-shot
  retry; other host-side web fetches had inconsistent/no retry behavior.

**Decision:**
- Standardize host-side HTTP resilience via shared helpers in `utils/http.py`
  (`get_bytes`, `get_text`, `get_json`, `download_to_file`) using the existing
  `retry_rate_limited` tenacity strategy.
- Apply one uniform retry profile across hardened host-side endpoints.
- Migrate these paths to shared helpers:
  - `evidence/host_adapters.py`: `_fetch_json`, `_fetch_text`, OVAL download,
    autopkgtest DB download
  - `evidence/team_mapping_adapter.py`: package-team-mapping fetch
  - `evidence/lto_disabled_adapter.py`: lto-disabled-list fetch

**Out of scope (intentional):**
- Container-side downloader logic in `evidence/cvelist_scan_invm.py`
- Replacing autopkgtest DB usage with web page scraping

**Rationale for not adding web scraping fallback:**
- No stable public JSON results API for historical per-package test results.
- Website output is template-driven HTML and has active anti-crawler controls,
  making scraping brittle and operationally fragile.
- `autopkgtest.db` remains the most stable machine-readable source.

**Consequences:**
- Better tolerance of transient 429/5xx/network failures across host-side
  evidence collection with less duplicated retry code.
- Behavior contracts of adapters are preserved: successful outputs are
  unchanged; terminal failures still degrade to existing adapter error paths.

## 2026-07-13 — Bulky-download-in-VM rationale retired

**Context:**
- Earlier decisions preferred running cvelist baseline download/scan inside the
  throwaway VM to keep bulky data off the host.
- Current architecture already performs large host-side downloads (for example
  `autopkgtest.db`) and now has standardized host retry/backoff helpers.

**Decision:**
- Retire the old blanket rationale "bulky downloads should stay in the VM".
- Move `cvelist-scan` to host execution while preserving adapter contracts and
  dependency chain semantics.
- Replace the old rationale with a stricter data-lifecycle policy:
  - large temporary artifacts are allowed on host or VM,
  - they must be created via temporary paths and cleaned up after execution.

**Consequences:**
- Lower implementation and maintenance risk by reusing host-side helper/retry
  infrastructure.
- Execution-location consistency now follows operational fit (build/source work
  stays in VM; web/bulk lookups may run on host) rather than payload size.

## 2026-07-13 — Feedback round 4 (bug 2118381 / libebur128)

**Promotion:** no

**Context:** first user reports against libebur128 surfaced two issues.

**Issue 1 — DEP-3 flagged a same-source promoted binary as offending.**
- `libebur128-dev` auto-includes `libebur128-1`, which is built by the same
  source and is being promoted by this very MIR. The auto-included dependency
  loop in `collect_dep_analysis` marked any non-main dep as offending, ignoring
  the same-source case that the general `deps_not_in_main` loop already handled.
- Decision: "part of this request" == **same source package**. The auto-included
  loop now splits non-main deps into a genuine-offender bucket and a same-source
  bucket (`auto_included_deps_same_source`,
  `auto_included_same_source_deps_by_binary`). DEP-3 succeeds with an
  explanatory note (`ok_same_request_message`) when the only non-main deps are
  same-source, and only fails on genuine offenders.

**Issue 2 — CB-6 had no reverse-dependency autopkgtest data (missed
implementation).**
- CB-6 was designed as a reverse-dep autopkgtest summary, but no adapter ever
  collected reverse dependencies; `collect_autopkgtest` only queried the package
  itself. The model therefore correctly reported it could not see consumer test
  status (the consumer name in reports came from reporter text, not a query).
- Decision: add two adapters.
  - `reverse-deps` (guest): runs `reverse-depends` (ubuntu-dev-tools, already
    provisioned) for runtime and `--build-depends` reverse deps against
    `<codename>-proposed` (fallback to bare codename), maps reverse-dep binaries
    to source packages, and returns deduplicated consumer sources tagged
    runtime/build. The package's own source is excluded.
  - `consumer-autopkgtests` (host, depends_on `reverse-deps`): looks up each
    consumer source in the autopkgtest DB and reports per-consumer
    passing/failing arches.
- The large `autopkgtest.db` is downloaded **once per run** and cached on the
  context (`_get_cached_autopkgtest_db`), shared by `autopkgtest-db` and
  `consumer-autopkgtests`, and removed at the end of evidence collection
  (`cleanup_cached_autopkgtest_db`, called from a `finally` in
  `collect_from_catalog`) — consistent with the data-lifecycle policy above.
- CB-6 stays EV→AI and **reviewer-decided**: the rewritten `ai_policy` names key
  consumers with their autopkgtest arches and reasons about E2E coverage, but
  always leaves the final judgment to the human (never a hard OK). `llm_eval`
  emits a compact, prioritised `consumer_test_summary` (consumers with tests
  first, capped) so the decision-relevant data survives list truncation.

## 2026-07-14 — Ubuntu-first host dependency preflight

**Promotion:** no

**Context:**
- Beta users are expected to run auto-mir with dependencies supplied by the
  Ubuntu archive, not to reproduce the developer `uv` workflow.
- The four dependencies declared in `pyproject.toml` are all active runtime
  dependencies, but they previously failed at different points: Tenacity at
  module import, JSON logging at startup, Launchpad during intake, and PyYAML
  during catalog loading.
- This produced tracebacks or repeated install/run cycles and could defer a
  failure until after useful setup work. Eager imports also prevented
  `--help` from working on an unprepared host.

**Decision:**
- Support Ubuntu 24.04 LTS or newer with Python 3.12 or newer.
- Keep all four PEP 621 runtime dependencies and map them explicitly to Ubuntu
  packages in a standard-library-only registry:
  - `launchpadlib` → `python3-launchpadlib`
  - `pyyaml` → `python3-yaml`
  - `python-json-logger` → `python3-pythonjsonlogger`
  - `tenacity` → `python3-tenacity`
- Parse arguments before the preflight, preserving dependency-free `--help`.
  Run the preflight before `RunContext`, output creation, authentication,
  network access, or LXD work.
- Discover top-level modules without importing them, report all missing direct
  dependencies together, and provide one `apt install` command. Do not catch
  broad import failures that could hide internal or transitive defects.
- Keep the existing Launchpad and YAML guards as defensive local diagnostics.
  Ruff and pytest remain developer/test tools and are not runtime dependencies.

**Consequences:**
- Users get Ubuntu-native, actionable setup guidance without pip instructions.
- `--help` remains available before installation, while every real run fails
  early and consistently when its host is incomplete.
- A unit test keeps the runtime registry aligned with `pyproject.toml`; the
  registry is the source for Ubuntu package names shown by the CLI.

## 2026-07-14 — OpenRouter as the coherent beta default

**Promotion:** no

**Context:**
- The 2026-06-25 provider simplification retained OpenRouter model identifiers
  (`z-ai/glm-4.7` and `z-ai/glm-5.2`) but left the default base URL pointing at
  the OpenAI API. A default run therefore combined models and an endpoint that
  are not compatible.
- The transport already uses the standard OpenAI-compatible request shape.
  OpenRouter's attribution headers are optional, so no provider-specific client
  dependency or request branch is needed.

**Decision:**
- Use `https://openrouter.ai/api/v1` as the default base URL for the beta while
  retaining the existing OpenRouter model defaults.
- Continue reading the credential from `OPENAI_API_KEY` and keep
  `OPENAI_API_BASE` as an explicit override for other compatible services.
- Do not validate token prefixes or log token values. Keep the standard bearer
  authorization and content-type headers.

**Consequences:**
- The zero-configuration endpoint and model defaults now form a working pair.
- Users of another OpenAI-compatible service can still override both the base
  URL and model flags without code changes.
- Tests lock endpoint construction, trailing-slash normalization, overrides,
  and missing-token behavior.

## 2026-07-14 — Host-only credentials and exact-value output redaction

**Promotion:** no

**Context:**
- PR-33 routed persistent `lxc config set` calls through the shared command
  wrapper while preserving guest environment export. That improved execution
  consistency but also caused verbose console and JSON logs to contain the full
  API key.
- The export helper claimed values were not logged, but the shared wrapper
  correctly logged every command. Kept guests also retained the key in LXD
  configuration.
- All LLM calls are host-side. No guest process consumes the exported API key
  or API base; runtime evidence only checked that the unused variables existed.

**Decision:**
- Supersede PR-33's persistent guest-auth invariant. Keep LLM credentials on
  the host and remove guest export and auth-presence evidence.
- Register exact non-empty credential values when resolved, then redact those
  values after log formatting and before writing shareable artifacts.
- Do not infer secrets from provider names, token prefixes, or entropy. Endpoint
  URLs and public evidence remain visible unless they contain a registered
  secret value.

**Consequences:**
- Preserved guests no longer retain Auto-MIR credentials, and verbose command
  logging remains useful without exposing active keys.
- Output directories are credential-safe rather than anonymous; public MIR and
  package data remain available for diagnosis.
- Previously created logs are unchanged. Any credential exposed there must be
  revoked or rotated before the old files are shared.

## 2026-07-14 — Remove unused ubuntu-archive-tools pinning

**Promotion:** no

**Context:**
- The catalog design anticipated an optional pin for reproducible benchmark or
  replay runs, but no test, documented workflow, or invocation used it.
- The default and every observed run already cloned the latest upstream HEAD.
  Keeping the unexercised fetch, checkout, and unshallow branches increased the
  provisioning and CLI surface without serving a beta workflow.

**Decision:**
- Remove `--pin-uat-tooling` and its context field.
- Always shallow-clone the latest ubuntu-archive-tools HEAD during guest
  provisioning.
- If reproducible replay is needed later, design it around captured evidence
  and explicit tool metadata rather than restoring an untested checkout branch.

**Consequences:**
- Guest provisioning retains its existing default behavior with less code and
  fewer failure paths.
- Invocations of the removed, undocumented option now fail argument parsing
  instead of silently implying a supported replay contract.

## 2026-07-14 — Build-managed reviewer-template generation

**Promotion:** no

**Context:**
- The catalog blueprint is the single source for the human MIR reviewer
  template body, while the generated include is intentionally ignored.
- Local Make builds regenerated it because `generate-includes` was phony, but
  used the system Python and non-strict validation. Read the Docs invoked Sphinx
  directly without generating it, and catalog-only pull requests could skip the
  hosted documentation build.
- Strict mode incorrectly required every outcome-specific runtime `todo_ref` to
  occur in the static template, even when the blueprint intentionally selected
  only one of those alternatives.

**Decision:**
- Supported Make and Read the Docs builds generate the include strictly before
  Sphinx. The docs environment explicitly supplies PyYAML.
- Strict validation covers references selected by the blueprint. Additional
  runtime-only outcome alternatives remain valid catalog data.
- Keep the generated include ignored and add structural/idempotency tests rather
  than maintaining a second frozen policy copy.

**Legacy parity proof:**
- Compared `origin/main` commit `5544ab17c2e2b8ad1743dd7aa3bf14c1ff33a4e2`
  with the catalog renderer at pre-change HEAD
  `e0960cd42208b35119d89e08d7b8d17f145c8603`.
- After removing only the old outer code-block fence and `:linenos:`, both
  bodies were 395 lines and 21,604 bytes with SHA-256
  `6f0fa5dd9e1e1bc0ecae14b11c7120fab611a7edea3733b94d51b3b36ae99cbe`.
- `cmp` and the unified diff reported no differences; no policy text repair was
  required.

**Consequences:**
- Catalog or renderer changes trigger hosted docs builds, and clean builds no
  longer depend on an accidentally pre-existing include.
- Intentional future policy changes remain possible through the catalog without
  updating a legacy golden file.

## 2026-07-16 — Reorg signal: drop dup-search, add bug-text predecessor extraction

**Promotion:** no

**Context:**
- A test review of mysql-9.7 (bug 2160635, a rename of mysql-8.4) produced an
  embarrassing reorg rationale: "a functionally-similar package is already in
  main (libdbi-perl, libecpg-compat3, libecpg-dev)". These are a Perl DB
  interface and PostgreSQL/SQLite client libraries — unrelated category
  neighbours, not the actual predecessor (mysql-8.4).
- Root cause: `review_type._dup_predecessor_in_main()` consumed the raw
  `dup-search` candidate list (an LLM-derived, `apt-cache search`-probed
  suggestion pool) and returned every candidate tagged `component == "main"`
  with no functional-overlap filtering. The adapter docstring states it is
  "deliberately best-effort and suggestion-only"; its proper consumer is the
  RDO-1 check, whose AI policy reasons about "genuine FUNCTIONAL overlap, not
  mere name or keyword similarity".
- This produced a direct contradiction in the same report: RDO-1 (consuming
  the same `dup-search` evidence) resolved `ok` with high confidence
  ("postgresql-18 is a distinct server implementation rather than a functional
  duplicate; other candidates are client libraries, documentation, or
  integration tools"), while the review-type rationale asserted a
  "functionally-similar package is already in main" using the very candidates
  RDO-1 had already reasoned away.
- The 2026-07-13 review-types decision listed "dup-search shows a
  functionally-similar package already in main" as a reorg signal, but the
  implementation took the raw candidate list instead of the functional-overlap
  reasoning the design assumed.
- The ideal reorg signal was missed: `lp-mir-history` only matched the current
  bug (mysql-9.7) because `_mir_history_candidate_names()` derived predecessor
  names from `cve-search-terms` (which proposed upstream CVE version families
  mysql-8.0 / mysql-5.7, not the Ubuntu archive source predecessor mysql-8.4)
  and `dup-search` candidates (functionality-neighbours, not name-lineage
  predecessors). The bug text explicitly said "mysql-9.7 to replace mysql-8.4"
  and "MIR for mysql-8.4 - LP: #2089720", but no adapter parsed these.

**Decision:**
- **A1 — Drop dup-search as a reorg signal.** Remove
  `_dup_predecessor_in_main()` and its call site from `review_type.py`. Reorg
  signals are now bug-text patterns (`_REORG_TEXT_RE`) plus `lp-mir-history`
  only. `dup-search` evidence and the RDO-1 check are unchanged; RDO-1 remains
  the sole, correct consumer of dup-search for functional-overlap reasoning.
  A false-fresh (rename with no text signal and no found prior MIR bug) is
  acceptable — the reviewer can use `--review-type reorg`.
- **B1 — Bug-text predecessor extraction.** Add `utils/predecessor_refs.py`, a
  dependency-free module that extracts rename/predecessor references from bug
  text: "X to replace Y", "renamed from Y", "formerly known as Y", "supersedes
  Y", "MIR for Y", and explicit "LP: #NNNN" / bug URL references. A single
  span like "MIR for mysql-8.4 - LP: #2089720" yields one ref carrying both the
  name and the bug id. Names are validated against the Debian source-name
  charset and filtered for stopwords and the current source package.
- **B1 wire — lp-mir-history consumes extracted refs.** Bare name refs are
  added to the searchTasks candidate pool. Explicit "LP: #NNNN" references are
  fetched directly and title-confirmed as MIR bugs (reusing the existing
  `_MIR_TITLE_RE`), with the predecessor source name parsed from the
  "[MIR] <name>" title. A new optional `provenance` field on `PriorMirBug`
  records when a bug was found via a bug-text reference. 404/transient failures
  on the direct fetch are skipped without failing the adapter, consistent with
  the existing searchTasks error handling.
- No core evaluation reorder: `detect_review_type()` still runs before pass-1
  checks (including RDO-1), then `_apply_review_type_softening` runs. The
  reorg signal no longer depends on a check's output, so no ordering change is
  needed.

**Non-goals (user-confirmed):**
- Reordering `evaluate_checks` so review-type detection reuses RDO-1's verdict
  (considered as option A3) is not needed once dup-search is removed from the
  reorg path.
- Tuning `dup-search` search-term precision or `cve-search-terms` predecessor
  semantics is out of scope; RDO-1 handles dup-search correctly, and
  cve-search-terms serves CVE history, not archive rename detection.

**Consequences:**
- The mysql-9.7 reorg rationale now names the correct predecessor via
  `lp-mir-history`: "a prior MIR bug exists under a different source name
  (mysql-8.4, …)".
- The review-type rationale and RDO-1 can no longer contradict each other on
  duplicates in main: review-type detection no longer consults dup-search, and
  RDO-1 remains the single reasoner over that evidence.
- A rename with no textual "replace/renamed" signal and no found prior MIR bug
  classifies as `fresh` (blocking); the reviewer can override with
  `--review-type reorg`.
- `lp-mir-history` may make one additional API call per explicit "LP: #NNNN"
  reference (bounded at 5); searchTasks round-trips are unchanged.

**Validation from `tools/auto-mir`:** `make lint` PASS, `make test` PASS
(565 passed, 3 skipped).

## 2026-07-16 — URF-4 false-positive: 'nobody' pronoun in comments/prose

**Promotion:** no

**Context:**
- A test review of mysql-9.7 (bug 2160635) produced a URF-4 false positive:
  "User 'nobody' found outside test context: ./debian/mysql-server.README.Debian:71:...
  to ensure that nobody else can read; ./vio/viosocket.cc:162:/* Ensure nobody
  uses vio_read_buff ... */; ./storage/ndb/.../DbdihMain.cpp:23689:...nobody
  else can ...".
- Analysis of all 72 raw `grep -RInF nobody` hits in the source tree showed
  zero genuine Unix-user references. After the existing test-context and
  doc-type filters, 54 hits survived: ~51 were the English pronoun "nobody"
  in C/C++ comments, 2 were quoted string literals, and 1 was a prose mention
  in `debian/mysql-server.README.Debian` (a doc file not recognised as such).
- Two distinct root causes:
  - **Problem A:** `_path_is_nonexecutable_doc` classified by the last
    extension only, so Debian's conventional `*.README.Debian` and
    `README.source` (last extension `.Debian` / `.source`, not in the
    doc-extensions list) were not recognised as non-executable docs.
  - **Problem B:** the source-tree grep loop in URF-4 had no comment-context
    filter, so the bare word "nobody" in English comments/prose tripped the
    check.

**Decision:**
- **A1 — Doc classification for compound Debian basenames.** Extended
  `_path_is_nonexecutable_doc` to check whether any dot-separated component of
  the basename (lowercased) is in `_NONEXECUTABLE_DOC_BASENAMES`, so
  `mysql-server.README.Debian` matches because the component `readme` is a
  known doc basename. A denylist of code/script extensions (`.py`, `.sh`, `.c`,
  ...) prevents misclassifying code like `install.sh` (where `install` is a doc
  basename but `.sh` is a code extension). Benefits both URF-4 and URF-5, which
  share the helper for source-tree grep-hit filtering.
- **B1 — User-reference context filter for 'nobody'.** Added
  `_line_references_nobody_user`, a positive regex requiring a code-context
  marker: quoted string literals (`"nobody"` / `'nobody'`), chown-style colon
  syntax (`nobody:group`), assignments (`User=nobody`), privilege-dropping
  function calls (`setuid`, `setuser`, `getpwnam`, `chown`, `su`, `runuser`,
  `initgroups` followed by `nobody`), and CLI flags (`--user nobody`, `-u
  nobody`). Applied to source-tree grep hits only in `_check_urf_4`.

**Non-goals:**
- The debian/rules and debian/control bare-word scan is unchanged (packaging
  files are small and "nobody" there almost always means the user).
- URF-3 (sudo/gksu/pkexec) is unchanged: it only scans debian/rules/control,
  and those keywords are not English pronouns.
- `nobody_source_files` and `nobody_owned_binaries` (find -user nobody) are
  unchanged: they are filesystem ownership facts, not text matches.

**Consequences:**
- The mysql-9.7 case: 72 raw hits → 54 after existing filters → 2 surviving
  hits (both `"nobody"` quoted string literals in C++ code, genuinely worth
  human review).
- A non-standard "nobody" reference pattern not matching the regex would be a
  false negative. This is acceptable: realistic user references in source code
  always appear in code contexts (quoted strings, function calls, assignments).
- The doc-classification fix also benefits URF-5 (setuid/setgid source-tree
  grep hits) since both checks share `_path_is_nonexecutable_doc`.

**Validation from `tools/auto-mir`:** `make lint` PASS, `make test` PASS
(570 passed, 3 skipped).

## 2026-08-03 — DEP-4 grounded in structured per-dependency test-coverage evidence (P10)

**Promotion:** no

**Context:**
- This closes out the reporter user-feedback round started 2026-07-15 (P0-P8,
  commits `e37569e6`..`3d9064ff`: RULE/TODO context and edit path in the
  wizard, catalog-driven dynamic/exclusive choice options, merged security
  items, evidence-grounded function/usage and FHS/Policy checks, gated
  testing-fallback questions, clarified dependency-MIR routing, an A/B license
  lifetime choice, subscribed-team/upstream-project detection, and an
  optional background catch-all). P9 needed no code change. P10 was the last
  substantive item: a correctness gap in **DEP-4** ("Main dependencies not
  only superficially tested"), which lives in the reviewer catalog
  (`catalog.yaml`), not the reporter catalog.
- DEP-4's `adapters_required` was `[dep-analysis, autopkgtest-db]`, but
  `autopkgtest-db` only ever queries the DB for the **source package under
  review itself** — it has no notion of that package's dependencies. Nothing
  in the evidence pipeline actually computed, per runtime dependency already
  in main, whether that dependency has autopkgtest coverage. The `ai_policy`
  asked the LLM to "check autopkgtest.db for test coverage" per dependency,
  but no adapter surfaced that data; the LLM had no grounded evidence to do
  so and could only guess or fabricate coverage claims.
- The codebase already had the exact right precedent for this shape of
  problem: `collect_consumer_autopkgtests` (added in the 2026-07-14 feedback
  round for CB-6) reads a list of packages from one adapter's evidence
  (`reverse-deps.consumers`), queries the shared, per-run-cached autopkgtest
  DB (`_get_cached_autopkgtest_db`) once per source, and returns a structured
  per-item coverage list.

**Decision:**
- **A1 — Expose the in-main dependency set explicitly.**
  `guest_adapters.collect_dep_analysis` now computes
  `runtime_deps_in_main`: the runtime dependencies of **in-scope binaries
  only** (i.e. the binaries this MIR request is actually promoting, honouring
  `ctx.requested_binaries` the same way `in_scope_deps_not_in_main` already
  does) whose component is `main`. This is deliberately scoped the same way
  as the existing `in_scope_deps_not_in_main`/`out_of_scope_deps_not_in_main`
  split, so DEP-4 does not get diluted by every binary's dependency closure
  when only a subset of binaries is requested.
- **A2 — New adapter for per-dependency coverage.** Added
  `evidence.host_adapters.collect_dependency_autopkgtests`
  (`AdapterID.DEPENDENCY_AUTOPKGTESTS = "dependency-autopkgtests"`,
  `depends_on=[AdapterID.DEP_ANALYSIS]`), following the
  `collect_consumer_autopkgtests` pattern: resolve each in-main dependency to
  its source package via `dep-analysis.dep_source_map`, query the shared
  cached autopkgtest DB once per **unique** source (dependencies sharing a
  source are only queried once), and return `dependency_coverage`: a list of
  `{package, source, has_autopkgtest, passing_arches, failing_arches, note}`.
  Best-effort on DB unavailability (`AdapterError`) or query failure
  (`sqlite3.DatabaseError`), matching the existing adapters' fallback style.
- **A3 — DEP-4 now requires the richer adapter instead of the raw DB.**
  `adapters_required` is now `[dep-analysis, dependency-autopkgtests]` (the
  bare `autopkgtest-db` requirement is dropped — it was never the right
  evidence source for this check, and `dependency-autopkgtests` internally
  reuses the same cached DB download, so there is no duplicated cost).
  `ai_policy` now names `runtime_deps_in_main` and `dependency_coverage`
  directly, so the LLM is grounded in structured evidence rather than being
  asked to "check autopkgtest.db" itself.
- **A4 — New TypedDicts.** `DependencyAutopkgtestsResult` and
  `DependencyCoverageEntry` in `evidence/types.py`; `runtime_deps_in_main:
  list[str]` added to `DepAnalysisResult`.

**Consequences:**
- DEP-4 remains `mode: ev_to_ai` with `blocker_class: none` — the reviewer
  still makes the final call; this only improves the evidence the LLM's
  suggestion is grounded in.
- If a dependency's binary package name differs from its source package name
  and `dep_source_map` has no entry for it (e.g. a package the archive has no
  `Source:` field cache for), `collect_dependency_autopkgtests` falls back to
  querying the DB using the binary name itself, same convention as
  `collect_dep_analysis`'s own `dep_source_map` fallback ("Debian convention:
  binary name = source name").
- Reviewer-catalog-only change: the reporter catalog
  (`catalog-mir-report.yaml`) and reporter pipeline are untouched by P10.

**Validation from `tools/auto-mir`:** `make test` PASS (573 passed,
3 skipped). Commit `c0723837`.

## 2026-08-04 — Feedback round 6: guest-preserve UX and upstream-project detection (P1-P2)

**Promotion:** no

**Context:** first two phases of a 15-phase plan responding to real reporter
and reviewer test runs (`mir-rust-ntpd-*` report run, `mir-2138736-*` review
run). Full plan lives in session memory, not duplicated here; only the
concrete decisions are recorded.

**P1 — Only prompt to keep the LXD guest for genuine guest-side failures.**
- Both test runs hit `teardown_guest`'s "Keep LXD guest for debugging?"
  prompt purely because `upstream-tracker` and `cvelist-scan` failed — both
  are host-side adapters (`evidence/host_adapters.py`) that never touch the
  guest at all. Preserving a multi-GB VM for a host-side lookup miss has no
  debugging value and contradicts the tool's own memory-usage warning.
- `stage_collect_evidence` now classifies every failed adapter by its
  collector function's `__module__` (`evidence.guest_adapters` vs. any
  host-only module) and records `collection_summary.guest_adapter_failed`.
  `teardown_guest` only offers the interactive prompt when that is true;
  host-only failures are destroyed automatically with an explanatory log
  line. An explicit `--keep-guest` flag always wins, and a missing/old
  `collection_summary` defaults to the cautious `True` (prompt).

**P2 — Upstream project URL/name auto-detection uses its own already-computed hints.**
- Traced precisely in the rust-ntpd evidence: `debian/control` already had
  `Homepage: https://github.com/pendulum-project/ntpd-rs`, and
  `collect_upstream_tracker` already builds `url_hints` from that Homepage
  plus `debian/watch` via `_collect_upstream_search_terms` — but discarded
  them and raised `AdapterError` whenever release-monitoring.org itself had
  no matching project. "No match found" is a normal, expected outcome for
  most packages, not an adapter failure; it now returns `status: "ok"` and
  falls back to `url_hints[0]` when available (still `""` and non-error when
  truly nothing is known). A release-monitoring.org match now also surfaces
  the project's own `name` as `upstream_name`.
- New generic, catalog-declarative mechanism (`reporter/evaluator.py`):
  `writes_evidence: {adapter, field}` on a `human_only` question backfills an
  evidence adapter field from the human's raw answer, but only when that
  field is still empty and the answer looks like a URL (`^https?://\S+$`),
  and never overwrites an existing value. Used so REP-BG-002 (upstream name,
  free text) can retroactively fill `upstream-tracker.upstream_url` when the
  reporter types a URL there and neither release-monitoring.org nor
  debian/control/watch found one — so REP-BG-003 (upstream link) no longer
  reports "TBD" right next to an upstream URL the reporter already gave, and
  the consistency pass stops flagging it as a false contradiction.
  `default_source: {adapter, field}` mirrors the existing `options_source`
  pattern to pre-fill a question's default answer from evidence (used to
  suggest a confidently-detected `upstream_name`). Both validated in
  `catalog.py` via a shared `_validate_adapter_field_ref` helper (adapter
  must be a known evidence adapter).
- Fixed a related bug: REP-BG-002's prompt promises replying `'same as
  source'` works, but nothing substituted it — `_human_statement` now
  case-insensitively substitutes the source package name for that phrase.

**Validation from `tools/auto-mir`:** `make test` PASS (590 passed,
3 skipped).


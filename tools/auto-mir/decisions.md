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

### Correction: "already in main" signal was wrong (2026-08-05)

- Promotion: no
- Context: beta feedback on the prompt-toolkit MIR bug (2161382) showed the
  tool asserting a voluntary re-review "of a package already in main: all
  binary packages are already in main" for a package that is universe in
  every active release (confirmed via `rmadison -u ubuntu -a source
  prompt-toolkit`).
- Root cause: `_all_binaries_already_in_main()` treated
  `component-mismatches` reporting zero promotion candidates as "already in
  main". That tool only reports seed/component *mismatches* — a package
  correctly sitting in universe with no main-seed expectation at all also
  produces zero candidates, which is indistinguishable from "already in
  main" using that signal alone. This was the original 2026-07-13 design
  decision above, and it was wrong.
- Decision: `lp-package-api` (already fetching `component_name` per publish
  record for the target series) now surfaces a resolved `current_component`
  field (newest `Published` record, falling back to the newest record of any
  status, else `"unknown"`) — the direct archive-level equivalent of
  `rmadison`. `_all_binaries_already_in_main()` now checks
  `current_component == "main"` only, and fails closed (`False`) when
  `lp-package-api` is missing/unresolved, rather than falling back to the old
  proxy. `component-mismatches` keeps running (it may still have archive
  housekeeping value) but is no longer consulted for this decision.
- Scope: this also fixes SUM-3's "list of binaries to promote", which is
  grounded on the same `current_component` signal (see the SUM-3 evidence
  fix below) instead of asking the LLM to re-derive it from a truncated
  `debian/control` excerpt.

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

## 2026-08-04 — Feedback round 6: external editor support for the reporter wizard (P3)

**Promotion:** no

**Context:** the 2026-07-14 decision ("Separate reporter results and terminal
wizard") deliberately made the wizard dependency-free, with raw line-by-line
multi-line entry ended by a lone `.`. Real reporter testing showed this is
uncomfortable for anything beyond a short sentence, especially when revising
an AI suggestion (the transcript showed a reporter typing a multi-paragraph
revision at a bare `| ` prompt with no way to see or edit earlier lines).

**Decision — revisit the 2026-07-14 decision; add an external editor path:**
- New `utils/editor.py`: `resolve_editor_command()` resolves `$VISUAL`, then
  `$EDITOR`, then the Debian update-alternatives `/usr/bin/editor`, then a
  hardcoded `nano` fallback (mirrors `git`'s own resolution order).
  `edit_text(initial_text, comment_lines)` writes a temp file with
  `initial_text` on top and `comment_lines` rendered as `#`-prefixed lines
  below (matching `git rebase --interactive`'s commented-context style),
  launches the resolved editor via `subprocess.run`, strips `#`-prefixed
  lines back out of the result, and returns `None` (never raises) when there
  is no interactive terminal, the editor can't be launched, or it exits
  non-zero — so callers can cleanly fall back to raw terminal entry.
- `reporter/wizard.py`'s `TerminalWizard` gained an injectable `edit_text`
  constructor parameter (defaulting to the real `editor.edit_text`, following
  the same DI pattern as `read_line`/`write_line`) so tests can fake editor
  behavior without spawning a process.
- Applies to **every** multiline question, not just the AI-suggestion
  confirm flow: `_ask_multiline` now tries the editor first (comment lines
  built from the question's prompt/rule_context/hint/answer_guidance),
  reopening it if a required question comes back empty, and only falling
  back to the original raw `_ask_multiline_raw` terminal loop if the editor
  is unavailable. `confirm_suggestion`'s "edit" path (`_edit_multiline`) now
  also opens the editor, pre-filled with the AI's suggested statement and
  its reasoning as a comment, falling back to the old prefill-then-raw-input
  behavior if no editor is usable. "yes" is unaffected (no editor, use
  as-is); "no" already naturally gains editor support because it falls
  through to the normal fallback question via the same `_ask_multiline` path.

**Consequences:**
- No raw-terminal behavior was removed — it remains the fallback whenever an
  editor can't be launched (headless/non-interactive/binary missing), so
  every existing raw-input test keeps passing unchanged (pytest's stdin is
  never a tty, so `editor.edit_text` returns `None` in tests without any
  mocking, and the wizard transparently falls back).
- No new runtime dependency: `subprocess`/`tempfile`/`shlex` are stdlib.

**Validation from `tools/auto-mir`:** `make test` PASS (604 passed,
3 skipped).

## 2026-08-04 — Feedback round 6: TBDSRC substitution and shortcut package spelling (P4)

**Promotion:** no

**Context:** `_question_from_item` (`reporter/evaluator.py`) built
`QuestionOption` objects directly from raw catalog `label`/`statement`
strings with no `TBDSRC` substitution at all — substitution only happened
later, in `_human_statement`, after the option had already been shown to the
reporter containing the literal placeholder (confirmed in a real
transcript: `"1. All binary packages built by this source (shortcut)
[__all_binaries__] recorded as: All binary packages built by TBDSRC need to
be in main."`). `_unavailable()` never substituted at all. Separately, the
shortcut options for binary promotion scope give no indication of which
concrete packages they resolve to.

**Decision:**
- New `reporter/text_utils.py` module (shared between `reporter/evaluator.py`
  and `reporter/ai.py`, which cannot import from each other):
  `strip_todo_prefix` (moved verbatim from both files, which had duplicated
  it identically) and new `substitute_source(text, source_package)`.
  `substitute_source` replaces `TBDSRC` with `src:<pkg>` in prose (matching
  how source packages are conventionally referenced when disambiguating from
  binary package names in the same sentence), except inside a literal
  Launchpad `/+source/` or `/source/` URL path segment, where the bare
  package name is kept so the URL stays valid.
- Applied everywhere `TBDSRC` is substituted: `_question_from_item` (option
  label/statement, before they are ever shown), `_human_statement`,
  `ai.py::_ask_human`, and `_unavailable` (which previously did not
  substitute at all).
- New declarative per-option catalog field `spell_out_filter: all |
  exclude_dev_doc_dbg` (not hardcoded to any specific item). When an option
  is backed by `options_source` (e.g. REP-RATIONALE-004's binary-package
  shortcuts), `_spell_out_option` appends the concrete resolved package list
  to both the option's label and its statement, e.g. "All binary packages
  built by this source" becomes "...: librust-ntpd-dev, ntpd-rs,
  ntpd-rs-metrics". Validated in `catalog.py`.

**Validation from `tools/auto-mir`:** `make test` PASS (609 passed,
3 skipped).

## 2026-08-04 — Feedback round 6: follow-up-question hints for choice options (P5)

**Promotion:** no

**Context:** several reporter choice questions have a conditional follow-up
item (e.g. REP-RATIONALE-007's deadline yes/no leads to REP-RATIONALE-008
asking for the deadline details; REP-QA-TEST-005's access mechanism leads to
REP-QA-TEST-006 asking for the test plan). A reporter picking an option had
no way to know in advance that doing so would prompt for more detail next,
risking them second-guessing an otherwise-fine choice.

**Decision:** derive this purely from the catalog's existing `applicability`
declarations rather than adding new per-item authoring. `_question_from_item`
now calls `_mark_followup_options`, which scans every other catalog item's
`applicability` block for a direct reference to the current item
(`{item: ..., equals: ...}`, `{item: ..., in: [...]}`, or `{item: ...,
truthy: true}`, including inside `all`/`any` wrappers) and flags the
matching option(s) via a new `QuestionOption.leads_to_followup: bool` field.
`reporter/wizard.py`'s `_render_options` prints "(selecting this will ask for
more detail next)" under any flagged option. Negated (`not`) conditions are
not represented as a positive hint (there is no single triggering option to
point at). This keeps working automatically as applicability-linked items
are added, removed, or changed — no catalog changes were needed to enable it
for the five existing pairs (REP-RATIONALE-005/006, 007/008,
REP-STD-002/002B, REP-MAINT-001/001B, REP-DEP-002/003) or the
REP-QA-MAINT-004 -> REP-QA-TEST-005 -> REP-QA-TEST-006 chain.

**Validation from `tools/auto-mir`:** `make test` PASS (613 passed,
3 skipped).

## 2026-08-04 — Feedback round 6: title + indent formatting in the wizard (P6)

**Promotion:** no

**Context:** the wizard's `Context: ...`, `Hint: ...`, `Suggested statement:`
+ text on the next line, `Reasoning: ...`, and `Note: ...` blocks were each
formatted slightly differently (some `Label: text` on one line, some label
then unindented text on the next), making it visually ambiguous which lines
belonged to which label, especially for multi-line content.

**Decision:** purely cosmetic, no information added or removed.
`reporter/wizard.py` gains a shared `_write_titled_block(title, text)` that
always prints the title alone on its own line, then every body line indented
by 4 spaces underneath. Applied to `ask()`'s `Context:`/`Hint:`,
`confirm_suggestion()`'s `Suggested statement:`/`Reasoning:`, and
`show_note()`'s note text and detail (which now also reads `Reasoning:`
instead of an inline parenthetical, for the same visual language).

**Validation from `tools/auto-mir`:** `make test` PASS (615 passed,
3 skipped).

## 2026-08-04 — Feedback round 6: soften the testing-gaps question wording (P7)

**Promotion:** no

**Context:** REP-QA-TEST-003's prompt ("Explain any testing gaps,
hardware/manual test plan, execution frequency, and regression
consequences.") reads as though gaps are assumed to exist, and the question
was required, so answering "none" was the only way through rather than a
genuine, neutrally-framed "nothing to add" path.

**Decision:** reword the prompt to a neutral "if there are any ... worth
noting, explain them" framing, and set `required: false` with a custom
`answer_guidance` explicitly telling the reporter to enter `.` on the first
line when there is nothing to add. `required: false` is necessary for the
new instruction to actually work: `_ask_multiline`/`_ask_multiline_raw`
(`reporter/wizard.py`) reject an empty first line outright for required
questions ("A response is required..."), so without this change the new
wording would have been actively wrong. Skipping the question now cleanly
resolves to `StatementState.NOT_APPLICABLE` / `ReadinessEffect.CLEAR` and is
omitted from the draft entirely, matching "no gaps, no statement needed."

**Validation from `tools/auto-mir`:** `make test` PASS (616 passed,
3 skipped).

## 2026-08-04 — Feedback round 6: shared, field-priority-aware evidence truncation (P8)

**Promotion:** no

**Context:** root-caused a concrete bad-suggestion bug in the reporter's
`ev_to_ai` flow. `reporter/ai.py`'s `evaluate_ai_item` built its evidence
payload by dumping each required/optional adapter's **entire** dict wholesale
via `json.dumps(evidence, default=str, sort_keys=True)[:30000]` — one flat
character cutoff over alphabetically-sorted keys. In a real rust-ntpd run,
`packaging-source.crypto_pattern_hits` contained raw, multi-KB grep matches
from minified SVG files, and alphabetically `crypto_pattern_hits` sorts
before `debian_control`/`debian_rules`/`debian_tests_control` — so on a
large package those small, decision-critical fields could be pushed out of
the 30000-char budget entirely before the LLM ever saw them. This directly
explained an observed bad suggestion for REP-QA-PKG-004 that literally cited
"the provided snippet is an SVG diagram" instead of `debian/rules` content.
The reviewer pipeline (`checks/llm_eval.py`) already solved this correctly
with per-field, priority-aware truncation (`_truncate_adapter_data` +
`_FULL_CONTENT_FIELDS_BY_CHECK`) — re-inventing a second, worse strategy in
the reporter would have been duplicative and left this class of bug
unfixed there.

**Decision:**
- Extracted `_truncate_adapter_data` (renamed `truncate_adapter_data`),
  `_reduce_file_listing`, `_summarise_build_log`, `_line_slice`, and their
  private path-prefix helpers out of `checks/llm_eval.py` into a new shared
  `utils/llm_evidence.py`, parameterized by a caller-supplied
  `keep_full_fields: set[str]`. Behavior is unchanged for the reviewer role
  (`checks/llm_eval.py` now just imports and calls the shared functions);
  the two directly-affected unit tests moved from `tests/test_checks.py` to
  a new `tests/test_utils_llm_evidence.py`, which also gained broader
  coverage (full-field capping, list truncation, nested dicts, and a direct
  regression test proving a large low-priority field can no longer starve a
  small `keep_full_fields` one).
- `reporter/ai.py`'s `evaluate_ai_item` now truncates each adapter's evidence
  individually via the shared `truncate_adapter_data` (mirroring how
  `checks/llm_eval.py._build_evidence_payload` already did it) instead of one
  flat post-serialization cutoff, and the flat `[:30000]` cutoff is removed
  entirely — per-field truncation now does the real bounding, so a second,
  blunter cutoff on top would just reintroduce the same class of risk. New
  reporter-side `_FULL_CONTENT_FIELDS_BY_ITEM` mapping (mirroring the
  reviewer's `_FULL_CONTENT_FIELDS_BY_CHECK`), seeded with
  `REP-QA-TEST-004: {debian_tests_control, debian_rules}`,
  `REP-QA-PKG-004: {debian_rules}`, `REP-STD-001: {debian_control}`.

**Validation from `tools/auto-mir`:** `make test` PASS (628 passed,
3 skipped). `tests/check_parity_baseline.py` still exits 0 (advisory mode;
fixture directories remain absent in this environment).

## 2026-08-04 — Feedback round 6: AI-suggestion confidence-tier contract (P9)

**Promotion:** no

**Context:** two related, real-transcript-confirmed problems in
`reporter/ai.py`'s `evaluate_ai_item`: (6) when the model could not actually
determine an answer, it still returned a "suggestion" that was really a task
description (e.g. "Confirm whether the deprecated algorithm is actually used
in ./docs/development/new-dataflow.svg:4 before flagging Security review."),
offered through the same yes/edit/no flow as a real statement — accepting
"yes" then baked that task description into the draft as if it were a final,
affirmative claim. (8) even "confident-looking" suggestions let hedging
bleed into the statement itself (e.g. "The packaging appears to use standard
dh-cargo tooling ... in the limited metadata provided"), which is neither
clearly a fact nor clearly a TODO.

**Decision:** the model must now commit to an explicit tier instead of
blending confidence into prose:
```
{"confidence": "high"|"low", "statement": "...", "rationale": "..."}
```
`rationale` is always required; `statement` is required (and length- and
hedge-phrase-checked) only when `confidence` is `"high"`. `_validate_response`
rejects (raises `llm.LLMError`, existing fallback path) an invalid
`confidence` value, a missing/oversized `statement` when high-confidence, or
a high-confidence `statement` containing hedge markers ("appears to",
"seems", "may be", "likely", "possibly", "unclear", "in the limited...",
etc.) via a new `_contains_hedge_phrase` check — a lightweight phrasing
gate, not a content judgment.
- `confidence == "high"`: unchanged `confirm_suggestion` yes/edit/no flow.
  The statement is now guaranteed to be one affirmative claim, whichever way
  it goes ("The packaging uses standard dh-cargo tooling with no disabling
  of tests." or "The packaging is quite complex, ...").
- `confidence == "low"`: `confirm_suggestion` is never called (no more
  presenting a task description as if it were "the suggested statement").
  Instead `wizard.show_note()` shows the item's title and the model's
  rationale, then falls straight to `_ask_human`, which now accepts an
  optional `rationale` parameter carried into the resulting
  `StatementResult.rationale` for audit/context even though the final
  `statement` text is the reporter's own answer. Any validation failure
  (bad schema, invalid confidence, missing/oversized/hedged statement) also
  falls back to `_ask_human`, matching the existing LLM-unavailable path.
- The prompt (`reporter/ai.py`'s inline template) now explicitly describes
  the two tiers and gives both a "confident-good" and "confident-bad"
  example, so the model isn't nudged toward always picking "good" outcomes.

**Validation from `tools/auto-mir`:** `make test` PASS (632 passed,
3 skipped).

## 2026-08-04 — Feedback round 6: REP-QA-TEST-004 grounded in real test definitions and logs (P10)

**Promotion:** no

**Context:** REP-QA-TEST-004's `ai_policy` only pointed at `autopkgtest-db`
(pass/fail per architecture) and `sbuild`, with no instruction to inspect the
actual test definitions. The real test content
(`packaging-source.debian_tests_control`, i.e. `debian/tests/control`) was
already collected in evidence and already delivered in full to the model
(Phase 8's `_FULL_CONTENT_FIELDS_BY_ITEM`), but the policy never told the
model to use it to judge non-triviality (e.g. a real functional test suite
vs. a package whose autopkgtest only runs `--help`).

**Decision:**
- Rewrote REP-QA-TEST-004's `ai_policy` to explicitly instruct reading
  `packaging-source.debian_tests_control` in full to judge non-triviality
  before ever declaring low confidence.
- Added a bounded, opt-in second-round fallback for when even that is
  inconclusive, gated by a new declarative catalog boolean
  `autopkgtest_log_followup: true` (only REP-QA-TEST-004 sets it, so this
  never becomes a blanket behavior). `reporter/ai.py`'s
  `_maybe_refine_with_autopkgtest_logs` fetches at most two real autopkgtest
  execution logs (one per architecture, via `test_results[].run_id`) and
  does exactly one additional LLM call with those excerpts added as
  `autopkgtest_log_excerpts`; if the second call still returns low
  confidence, the original (first) rationale path is used unchanged.
- New `evidence.host_adapters.fetch_autopkgtest_log_excerpt(package, series,
  arch, run_id)`. **The exact log-retrieval URL was empirically verified
  against this environment's live `autopkgtest.ubuntu.com`** (not guessed):
  `https://autopkgtest.ubuntu.com/results/autopkgtest-<series>/<series>/<arch>/<prefix>/<package>/<run_id>/log.gz`,
  gzip-compressed plain text, where `<prefix>` follows the standard
  Debian/Ubuntu archive pool convention (`lib`-prefixed packages use their
  first four characters, e.g. `libgit2` -> `libg`; everything else uses just
  the first character, e.g. `python-invoke` -> `p`) — confirmed with
  `libgit2`, `libvirt`, and `python-invoke` against the live site. The fetched
  log is summarised with the existing `utils.llm_evidence.summarise_build_log`
  (head/tail + highlighted error/failure lines) rather than a new bounding
  scheme. This is a plain helper function, not a registered catalog evidence
  adapter — it only runs on-demand for the one opted-in item when needed,
  never for every package. On any failure (network, decompression, decoding,
  missing run) it returns `None` and the original low-confidence result is
  used unchanged; this is genuinely best-effort, matching how the plan
  explicitly allowed "fail soft" given the URL scheme could not be verified
  ahead of time from documentation alone (it now has been, empirically).

**Validation from `tools/auto-mir`:** `make test` PASS (640 passed,
3 skipped).

## 2026-08-04 — Feedback round 6: consistency-pass corrections replace, not append (P11)

**Promotion:** no

**Context:** when the bounded AI consistency pass (`reporter/consistency.py`)
raises a follow-up question and the reporter answers it, the answer was
appended as a second line after the original (possibly self-contradictory or
hedged) statement, e.g. a real transcript ended up with "Autopkgtests exist
and pass on all architectures, they are providing sufficient coverage..."
immediately followed by the reporter's own "I checked the tests, they are
providing sufficient coverage." A reporter who went to the trouble of
checking and confirming something is overriding the tool's uncertainty, not
appending a footnote to it.

**Decision:** `result.statement = correction` replaces the statement outright
instead of `f"{result.statement}\n{correction}"`. `provenance`,
`human_confirmed`, and clearing `rationale` are unchanged. Combined with
Phase 9's confidence-tier fix (which should make same-statement
self-contradictions between a statement and its own rationale rare going
forward, since a low-confidence assessment no longer produces a
"final-looking" statement in the first place), this keeps the consistency
pass focused on genuine cross-item contradictions.

**Validation from `tools/auto-mir`:** `make test` PASS (641 passed,
3 skipped).

## 2026-08-04 — Feedback round 6: consistent bulleted-statement rendering (P12)

**Promotion:** no

**Context:** real transcripts showed the rendered draft mixing bulleted and
unbulleted lines: catalog `template`/option `statement` text already used a
leading `- ` in most (but not all) places, while every deterministic
evaluator in `reporter/evaluator.py` (registered via `@reporter_evaluator`,
19 functions) returned a hand-written f-string with no bullet at all, and
AI-confirmed/consistency-corrected statements had no bullet either. An
earlier design of this fix proposed detecting and inserting bullets inside
`render.py` at render time; the reporter corrected this in favor of making
every catalog template/option statement consistently embed its own `- `
(matching how the reviewer catalog already behaves) and centralizing the
handling of genuinely free-form (non-templated) text in one place instead.

**Decision:**
- Audited every `template:` and option `statement:` string in
  `catalog-mir-report.yaml` and added the missing leading `- ` to the ones
  that lacked it (6 templates, ~23 option statements). Catalog text is now
  the single source of truth for the bullet: `_human_statement` no longer
  needs to add one, since `strip_todo_prefix` only removes the `TODO:`/
  `TODO-X/Y:` marker itself and leaves the template's own `- ` intact.
- Added `reporter/text_utils.ensure_bulleted(text)`: prefixes `- ` onto text
  that doesn't already start with it (checked after `lstrip()`, so it never
  double-dashes). Wired into the three places that produce statement text
  outside of the catalog template mechanism:
  - `reporter/evaluator.py`'s `evaluate_items()` deterministic branch, wrapping
    every registered evaluator's returned `statement` at the single call
    site rather than editing all 19 evaluator functions individually.
  - `reporter/ai.py`'s AI-confirmed branch, wrapping the final
    accepted-or-edited suggestion.
  - `reporter/consistency.py`'s human-correction replace step, wrapping the
    reporter's follow-up answer.
- Added `reporter/render.py`'s `_with_hanging_indent(text)`: for any
  RESOLVED/UNAVAILABLE statement or rationale containing embedded newlines
  (multi-select answers, multi-line free text), continuation lines are
  indented by two spaces so they visually continue the leading bullet
  instead of starting flush-left.
- Added a `catalog.py` structural validation rule (in
  `validate_report_catalog`) requiring every `template` to match
  `TODO(-[A-Z0-9/-]+)?:\s*-\s` and every option `statement` to start with
  `- `, so this can't silently regress as the catalog grows.

**Consequences:**
- Every resolved reporter-draft line now begins with exactly one bullet,
  regardless of whether it came from a catalog template, a human answer, a
  deterministic evaluator, an AI suggestion, or a consistency correction.
- `item_values` (used for `applicability` `equals`/`in` conditions) now
  stores the bulleted deterministic statement text, but no catalog condition
  compares against deterministic statement text (only against human/AI
  choice-option ids), so this has no behavioral effect on conditions.

**Validation from `tools/auto-mir`:** `make test` PASS (652 passed,
3 skipped).

## 2026-08-04 — Feedback round 6: remove `multi_choice`; single_choice + free-text fallback (P13)

**Promotion:** no

**Context:** `multi_choice` only had two real uses: REP-QA-TEST-005 (select
every way the owning team can test non-automated cases) and REP-RATIONALE-004
(select which binary packages need promotion, dynamically expanded from
`dep-analysis.binary_packages` into one selectable option per package). On
review, both are actually "pick the one best/primary answer, or describe a
rare special case in free text" rather than genuine multi-select, and
per-package dynamic option expansion made REP-RATIONALE-004 unwieldy for
sources with many binary packages. Independent of, but bundled with, the
exotic-hardware duplicate-question fix (P14).

**Decision:**
- `reporter/models.py`: removed `QuestionKind.MULTI_CHOICE`; `QuestionSpec`'s
  choice-kind check is now `kind == QuestionKind.SINGLE_CHOICE`.
- `reporter/wizard.py`: removed the multi-select branch from `_parse_answer`
  (comma-separated parsing, exclusive-combination rejection) and the
  "Select one or more options..." message from `_render_options`; the
  exclusive-option "(shortcut)" marker is unchanged and still renders for
  `single_choice`.
- `reporter/evaluator.py`: `_dynamic_options` (the `options_source` lookup)
  no longer gets appended to a question's selectable options — it is now
  used only to compute `known_packages` for `_spell_out_option`'s shortcut
  suffix (`"...: pkg1, pkg2"`). Added a new `binary-packages` evaluator
  (registered like `dependencies`/`team-subscription`, reused as a
  `preface_evaluator`) that lists all binary packages built by the source as
  an informational note shown before REP-RATIONALE-004's question, so the
  concrete package list is still surfaced even though it no longer expands
  into individual options.
- `catalog-mir-report.yaml`:
  - REP-RATIONALE-004: `kind: single_choice` with the two existing shortcut
    options plus a new `specific-packages` option (generic statement,
    "listed below"); gained `preface_evaluator: binary-packages`.
  - New item `REP-RATIONALE-004-SPECIFIC` (`human_only`, `multiline`, gated
    `applicability: {item: REP-RATIONALE-004, equals: specific-packages}`)
    asks for the actual package list as free text — mirrors the existing
    REP-MAINT-001/001B and REP-STD-002/002B choice-then-elaboration pattern
    already used elsewhere in this catalog.
  - REP-QA-TEST-005: `kind: single_choice`; added a new terminal option
    `Z-other` ("Something else / a special situation"), which — like every
    other option — already satisfies REP-QA-TEST-006's existing
    `applicability: {item: REP-QA-TEST-005, truthy: true}` follow-up with no
    further catalog changes needed.
- `tests/test_catalog_roles.py`: hardcoded reporter item count bumped
  54 -> 55 for the new item; hardware-choice-inventory set gained `Z-other`.

**Consequences:**
- Both choice items now behave like every other single-choice item in the
  catalog: exactly one selection, with a "something else" escape hatch that
  asks a genuine free-text follow-up instead of forcing a strained pick among
  fixed options.
- REP-RATIONALE-004 no longer creates one option per binary package, which
  scales better for sources with many binary packages and avoids a wall of
  near-duplicate selectable entries.

**Validation from `tools/auto-mir`:** `make test` PASS (654 passed,
3 skipped).

## 2026-08-04 — Feedback round 6: exotic-hardware duplicate question fixed (P14)

**Promotion:** no

**Context:** REP-QA-MAINT-002 (free text, "Does maintenance require exotic
hardware, and how can the owning team access it?", always asked) and
REP-QA-MAINT-004 (single_choice, "Does maintenance depend on exotic hardware
unavailable to ordinary infrastructure?", always asked) were unlinked
catalog items covering the same determination, with REP-QA-MAINT-002 asked
*before* REP-QA-MAINT-004 in both the asking order (`items:`) and the draft
order (`reporter_template_blueprint`) — the reporter answered the
free-text/elaboration question before ever being asked the canonical
yes/no. REP-QA-TEST-005 already treats REP-QA-MAINT-004's `team-access`
answer as the canonical signal for whether exotic hardware exists, so
REP-QA-MAINT-002 was the redundant, wrongly-ordered one.

**Decision:**
- Reordered both `items:` and `reporter_template_blueprint` so
  REP-QA-MAINT-004 (the choice) precedes REP-QA-MAINT-002 (the elaboration),
  matching the existing choice-then-elaboration pattern used elsewhere
  (REP-RATIONALE-007/008, REP-STD-002/002B, REP-MAINT-001/001B).
- Added a 3rd option to REP-QA-MAINT-004: `other-special` ("Something else /
  a special situation applies").
- Narrowed REP-QA-MAINT-002's prompt to elaboration-only ("Describe how the
  owning team can/will access the required exotic hardware for debugging,
  testing, verification, and development.") and gated it:
  `applicability: {any: [{item: REP-QA-MAINT-004, equals: team-access},
  {item: REP-QA-MAINT-004, equals: other-special}]}`.

**Consequences:**
- Exotic hardware is now asked about once, in the right order: the
  yes/no/other determination first, then (only when relevant) how access is
  actually arranged.
- REP-QA-TEST-005's own applicability (gated on `REP-QA-MAINT-004 ==
  team-access`) is unchanged; `other-special` was deliberately left out of
  that gate since it wasn't part of this fix's motivating case and expanding
  it wasn't decided.

**Validation from `tools/auto-mir`:** `make test` PASS (657 passed,
3 skipped).

## 2026-08-04 — Feedback round 6: human_only readiness propagation fix (P15)

**Promotion:** no

**Context:** while designing REP-MAINT-006's new state, found that
`evaluate_items`'s `human_only` branch (`reporter/evaluator.py`) hardcoded
`readiness=ReadinessEffect.CLEAR` on every resolved answer, completely
ignoring each item's own catalog-declared `readiness: blocker`/`warning`.
Confirmed via a real rust-ntpd draft: "Blocking items: REP-DEP-001,
REP-STD-001" — both `deterministic`, never a `human_only` item, even though
~26 `human_only` items declare non-clear readiness (REP-RATIONALE-001,
REP-STD-002, REP-MAINT-001/003/006, REP-QA-TEST-003/005/006/007, etc.).
These declarations were structurally inert: answering any of them, however
concerning the answer, always reported "clear."

**Decision:**
- `reporter/models.py`: `QuestionOption` gained an optional
  `readiness: ReadinessEffect | None = None` field.
- `reporter/evaluator.py`'s `human_only` branch now computes readiness as
  `selected_option_readiness_override or item.get("readiness", "clear")`
  instead of the hardcoded `CLEAR` (the skipped/optional-and-empty branch is
  unchanged and still always `CLEAR` — "nothing to add" must never block).
  `_spell_out_option` and `_mark_followup_options` (which reconstruct
  `QuestionOption` instances) now both preserve `.readiness` through their
  transformations.
- Per-option overrides were added to exactly the two items motivating this
  fix (not a blanket sweep across the ~26 affected items — deliberately
  incremental): REP-QA-MAINT-004 (`no-exotic-hardware` -> `clear`,
  `team-access`/`other-special` -> `blocker`, matching the item's own
  declared "blocker" for the two hardware-required answers) and
  REP-MAINT-006, which gained a third option `coordination-pending` ("Other
  teams are affected and coordination is still in progress", -> `blocker`),
  alongside explicit `clear` overrides on its existing `no-impact` and
  `coordinated-impact` options (both are fully resolved, non-concerning
  outcomes).
- `reporter/render.py`'s `_readiness_summary` previously required
  `state != RESOLVED or rationale` in addition to a matching readiness value
  before counting an item as a blocker/warning. That extra condition is
  always true for `deterministic` items (readiness is only ever non-clear
  alongside a rationale, enforced at construction) and for `AI_CONFIRMED`
  items (the LLM response schema always requires a non-empty rationale), so
  it never filtered anything for those two provenances — but it silently
  excluded `HUMAN` provenance results, which don't carry a separate
  rationale. Removed that redundant condition; blocker/warning status now
  depends only on `result.readiness`, matching what was already true in
  practice for every other provenance.
- REP-MAINT-003 (static/vendored-code obligations) gained
  `applicability: {evidence: packaging-source.shipped_vendored_dirs, truthy:
  true}`, mirroring exactly what REP-MAINT-004's deterministic evaluator
  already checks, so it's skipped entirely when there's no vendored code.

**Consequences (explicitly considered before deciding):** with only two
items given per-option overrides so far, most `human_only` items with
non-clear declared readiness (free-text ones especially, which have no
option structure to override) now permanently carry that readiness once
resolved — there's no mechanism yet to "clear" them. This makes
`Ready for submission: yes` far harder to reach with the current per-option
coverage than before this fix (a plain default-answer test run now reports
"no", not "yes"). This is treated as a **feature, not a regression**: the
bug being fixed is precisely that `readiness: blocker` catalog declarations
were being silently ignored once *any* answer was given, which made the
summary look falsely reassuring. The fix is intentionally incremental —
extending per-option overrides to the remaining single_choice items (and
deciding whether any multi-line item ever legitimately "clears") is left for
a future round rather than guessed at here.

**Validation from `tools/auto-mir`:** `make test` PASS (669 passed,
3 skipped).

## 2026-08-05 — Physical catalog split completed (user feedback on file naming)

- Promotion: no
- Context: user testing of reporter mode surfaced confusion about the catalog
  YAML layout: `catalog-mir-review.yaml` and `catalog-shared.yaml` were not
  content, only tiny composition contracts (5-7 lines) pointing back into
  `catalog.yaml`, which still held all reviewer-only content (`metadata`,
  `checks`, `security_triggers`, `render_policy`, `fallback_policy`) alongside
  the sections actually shared with reporter mode (`global_policies`,
  `evidence_adapters`). This was the deliberately deferred half of the
  2026-07-15 "Composed reporter catalog and review compatibility contract"
  decision (design.md: "Physical extraction of the shared and review sections
  from the compatibility catalog remains follow-up work").
- Decision:
  - `catalog.yaml` now holds only `global_policies` and `evidence_adapters`.
  - `catalog-mir-review.yaml` now holds the reviewer-only content directly
    (`schema_version`, `role: review`, `metadata`, `checks`,
    `security_triggers`, `render_policy`, `fallback_policy`), mirroring
    `catalog-mir-report.yaml`'s existing shape exactly.
  - `catalog-shared.yaml` is removed; its shared-section allow-list is now the
    `_SHARED_SECTIONS` constant in `catalog.py`.
  - `catalog.load_catalog_for_role()` is rewritten into one symmetric
    composition flow for both roles (load `catalog.yaml`'s shared sections,
    load the role's own file, reject either side overriding the other,
    validate the composed dict as a whole), replacing the previous asymmetric
    review-pointer / report-merge branches. `validate_catalog()` and
    `validate_report_catalog()` are unchanged — they now run against the
    composed dict instead of a single raw file.
  - `render_review_template.py` drops the fragile `if args.catalog ==
    "tools/auto-mir/catalog.yaml":` string-equality special case: no
    `--catalog` override now always loads the composed review catalog.
  - The move is a pure mechanical relocation with no wording/content changes.
- Consequences:
  - Adding a reviewer-only check or reporter-only item now only ever touches
    one file; adding a genuinely shared field only ever touches `catalog.yaml`.
  - Fixed a real latent bug surfaced while removing the now-fully-unused
    `RunContext.catalog_path`: `_save_test_artifacts()` (the `--collect-only`
    fixture-saving path, not covered by unit tests) still loaded
    `catalog.load_catalog(ctx.catalog_path, ...)` against the now-partial
    `catalog.yaml`; switched it to `catalog.load_catalog_for_role(ctx.tool_root,
    ctx.workspace_root, ctx.role)` like every other call site.
  - Verified byte-for-byte equivalence of the moved YAML content (diffed the
    reconstructed original section order against the pre-change file) and
    byte-identical generated `mir-reviewers-template-body.include` /
    `mir-reporters-template-body.include` output before vs after (rendered
    from a `git worktree` at the pre-change commit).
- Validation from `tools/auto-mir`: `make test` PASS (669 passed, 3 skipped).

## 2026-08-05 — Beta feedback: cvelist-scan asset-name drift, bogus predecessor-name extraction, retry decorator swallowing HTTPError

- Promotion: no
- Context: two "consistently fails" beta reports (console logs only, no line
  numbers) about `cvelist-scan` and `lp-mir-history`, investigated against a
  real run's artifacts (`evidence.json`/`report.json`/`auto-mir.log` for bug
  2161382, prompt-toolkit) plus a live check of the upstream GitHub API.
  Three independent root causes, all confirmed empirically before fixing:
  1. **cvelist-scan**: CVEProject/cvelistV5's release automation now uploads
     the daily "all CVEs" baseline asset as
     `<date>_all_CVEs_at_midnight.zip.zip` (doubled `.zip`) instead of a
     single `.zip`; verified sustained across ~40h of hourly releases, not a
     transient blip. `_cvelist_discover_baseline()`'s exact-suffix match no
     longer matched anything, failing the adapter (and skipping the
     dependent `nvd-enrich` adapter) on every run.
  2. **lp-mir-history "them" false positive**: the actual 404'd candidate
     name in the reported log was literally the string `"them"`. The
     reporter's own rationale text explains prompt-toolkit replacing GNU
     Readline/pyreadline3 for cmd2 with ordinary prose like "...prompt-toolkit
     replaces them" (them = the readline family, named earlier in the
     sentence). `utils/predecessor_refs.py`'s `\breplaces?\s+(\w+)`-style
     patterns captured "them" as a literal predecessor package name because
     `_STOPWORDS` covered only a handful of English words and no pronouns/
     determiners at all. "them" is never a real Launchpad source package, so
     the resulting probe 404s deterministically — this is unrelated to
     outages or rate limiting (a very reasonable reviewer pushback that led
     to this deeper root-cause pass rather than accepting the shallower
     "retries are too aggressive" framing as the whole story).
  3. **Shared retry-decorator bug**: `utils/retry.py`'s
     `retry_transient_network()` and `retry_rate_limited()` each OR a
     status-code predicate (meant to gate retries to 5xx/429 only) with
     `retry_if_exception_type((..., urllib.error.URLError))`. Since
     `HTTPError` is a Python subclass of `URLError`, that type check alone
     matched every HTTPError regardless of status code, silently bypassing
     the 4xx exclusion documented in both decorators' docstrings. This let a
     single 404 retry 5 times with 30/60/120/240/300s backoff (~12.5
     minutes) before `collect_lp_mir_history`'s own already-correct
     `except urllib.error.HTTPError` 404-skip logic ever ran. This decorator
     is shared by `utils/http.py` (used by nearly every host adapter) and by
     `llm.py`'s LLM API calls, so the bug was general, not
     lp-mir-history-specific.
- Decision:
  - cvelist-scan: match assets containing `_all_CVEs_at_midnight` and ending
    in `.zip` (renamed constant `_CVELIST_BASELINE_MARKER`) instead of an
    exact suffix, tolerating the current doubled extension and any future
    naming variant without another code change.
  - predecessor_refs.py: add `them, they, these, those, us, we, some, others,
    all, both, either, neither, more, most, several, many` to `_STOPWORDS`.
  - utils/retry.py: add `_is_network_url_error()` (true only for URLErrors
    that are *not* also HTTPErrors) and use it in place of the bare
    `URLError` type check in both decorators, so HTTP status-code gating
    remains the sole authority over whether an HTTP response is retried.
  - Explicitly rejected a separate pre-flight "does this candidate name
    exist" check (rmadison / `apt-cache showsrc` in the guest / Launchpad
    `getPublishedSources`) before doing the full `searchTasks` + bug-detail
    fetch: the existing `searchTasks` call against `+source/<name>` already
    *is* Launchpad's existence check (LP exposes a `DistributionSourcePackage`
    for any name ever published/referenced, any series — 404 means "never a
    real Ubuntu source package, ever"). Once the retry-decorator fix lands,
    that already-correct 404-means-skip path resolves in one fast round
    trip; a separate pre-check would ask Launchpad the same question twice
    for no new information. Noted for future: cve-search-terms' LLM-guessed
    "predecessor" terms bypass predecessor_refs.py's regex entirely, so the
    retry-decorator fix (not the stopword fix) is the general safety net for
    a hallucinated-but-plausible name on that path too.
- Consequences:
  - All three fixes are independent and were committed separately (one
    commit per fix) per the multi-task commit-hygiene convention.
  - New regression coverage: a realistic multi-release fixture for baseline
    discovery (doubled-suffix, single-suffix, no-match cases); false-positive
    and continued-true-positive cases for the expanded stopword list;
    decorator-level tests asserting `HTTPError(404)` fails after a single
    call while `HTTPError(503)`/`HTTPError(429)`/a genuine `URLError` still
    retry to the configured attempt count, for both `retry_transient_network`
    and `retry_rate_limited`.
- Validation from `tools/auto-mir`: `make test` PASS (685 passed, 3 skipped).

## Beta feedback round 2 (bug 2161382 / prompt-toolkit), 2026-08-05

**Context:** first reporter+reviewer round-trip test on a real universe
package surfaced four issues in the same run's `review-draft.txt`.

1. **Wrong "already in main" detection**: rereview rationale claimed
   "all binary packages are already in main" for a package that is universe
   in every active release (`rmadison -u ubuntu -a source prompt-toolkit`).
   Root cause and fix: see the dedicated "Correction: already in main signal
   was wrong (2026-08-05)" entry above (in the "Review types" section) —
   `_all_binaries_already_in_main()` had wrongly treated
   `component-mismatches` reporting zero promotion candidates as "in main";
   it now checks a new `lp-package-api.current_component` field instead and
   fails closed when unavailable.
2. **SUM-3 binary-promotion list stuck on TBD**: `debian_control` is
   unconditionally summarised to a 300-char preview
   (`utils/llm_evidence.py` `SUMMARY_FIELDS`) for every check that doesn't
   explicitly opt out via `_FULL_CONTENT_FIELDS_BY_CHECK`; for prompt-toolkit
   the Source stanza alone exceeded that before any binary `Package:`
   stanza, so the ev_to_ai model for SUM-3 correctly reported it could not
   see one. Rather than exempting `debian_control` for SUM-3 (still fragile
   for larger control files), the binary list and promotion decision are now
   computed deterministically from data already reliably known
   (`ctx.requested_binaries` / `dep-analysis.binary_packages` +
   `lp-package-api.current_component`) and surfaced as a new
   `promotion_status` evidence field (`checks/llm_eval.py`
   `_compute_promotion_status`); the model only phrases it, following the
   same grounding pattern as the earlier DEP-4 fix. SUM-3's catalog entry no
   longer requires `packaging-source`/`component-mismatches`.
3. **CB-8 false positive on `dh-sequence-python3`**: the check only grepped
   `debian/rules` for `dh_python`/`dh_python3`. Modern packaging (including
   prompt-toolkit) declares `dh-sequence-python3` in debian/control
   Build-Depends instead, which auto-invokes `dh_python3` with no
   debian/rules override at all. `_check_cb_8` now also accepts
   `dh-sequence-python3` in `debian_control`.
4. **RDO-1 cited irrelevant "main" candidates** (curl, openssl,
   network-manager) as if they were functional neighbours of a Python
   terminal-prompt library. Root cause: `dup-search`'s LLM-derived search
   terms were generic single-phrase strings ("interactive CLI", "command
   line") that any CLI tool's description can trivially contain verbatim,
   and RDO-1's `ai_policy` said a main-component candidate was "the most
   important to surface" with no relevance filter first — so the model
   dutifully echoed archive noise. Genuinely relevant candidates the user
   found via a generic AI query (`python3-urwid`, `python3-textual`) were
   never probed because the search terms never matched their descriptions.
   Fix, all three (user-selected):
   - `_llm_dup_search_suggestions()` (renamed from `_llm_dup_search_terms`)
     asks for `terms` *and* separately for `named_candidates` — concrete
     package/library names the model directly recognises as functionally
     similar (e.g. "urwid", "textual") — verified against the archive via a
     small set of Debian naming-variant guesses (`_resolve_named_candidates`
     / `_apt_cache_show_synopsis`) before being added as real candidates
     with their own true synopsis, never the model's guess. The term prompt
     now explicitly discourages generic phrases with a worked example.
   - `_apt_cache_search()` now splits a multi-word term into its significant
     (non-stopword) words and passes each as a separate `apt-cache search`
     argv pattern, so apt-cache's real multi-pattern AND semantics apply
     (require each distinct concept word) instead of one literal-phrase
     substring that a shared common phrase trivially satisfies. Only a small
     generic English stopword list is used — no domain/package names are
     hardcoded.
   - RDO-1's `ai_policy` now explicitly states dup-search is a noisy,
     unfiltered suggestion pool: the model must judge genuine functional
     relevance for every candidate first and silently discard irrelevant
     ones, and only then consider whether a *relevant* survivor is in main.
     It must never cite a candidate solely because it happens to be in main.
- Validation from `tools/auto-mir`: `make test` PASS (702 passed, 3 skipped),
  one commit per numbered issue above. `make integration` intentionally left
  for the user to run (slow, network/LXD-dependent).

## Beta feedback round 3 (borgbackup2, 2026-08-06), 13 numbered items, 8-phase implementation

**Context:** first reporter round-trip on a real universe package
(borgbackup2) whose `sbuild` step failed mid-run, surfacing a distinct class
of issue from prior rounds: several problems only showed up because
downstream evidence (lintian, dep-analysis, binary-package-inspection) was
silently unavailable, not because the reporter logic itself was wrong for
the "happy path". 8 commits on branch `auto-mir-review`, `make test` green
throughout, 743 passed/3 skipped final.

- **Phase A — option locking (#1, #2, #11).** No mechanism existed to
  disable a wizard option; every suggestion's "yes" and every single_choice
  option was always accepted. `reporter/ai.py`'s LLM JSON contract for
  `ev_to_ai` items gained a self-reported `requires_reporter_decision` bool
  plus a deterministic `_contains_deferral_phrase()` backstop (same style as
  the existing `_contains_hedge_phrase`), so a suggestion that only restates
  evidence without committing to the question's required conclusion (or
  that says "the reporter should confirm/verify...") can no longer be
  accepted verbatim. `wizard.confirm_suggestion()` gained `lock_yes_reason`;
  `QuestionOption` gained `locked_reason` (runtime-resolved) plus a new
  catalog-authorable `unavailable_if`/`unavailable_reason` pair (reusing
  `conditions.py`'s existing evidence-condition schema, no new operators),
  resolved by `evaluator._apply_option_lock`. Applied to REP-MAINT-001's
  `confirm-subscribed` option (locked when no team is subscribed) and
  strengthened `ai_policy` wording for REP-RATIONALE-003/REP-SECURITY-005 to
  require a decisive conclusion shape.
- **Phase B — logging (#3, #4, #10).** After any editor-sourced answer,
  `wizard.py` now prints "Answer recorded as: ..." to console and logs it at
  INFO via `auto_mir.reporter`, fixing "did my edit actually get recorded"
  confusion. `evaluator.evaluate_items` logs one combined
  `[i/total] Evaluating <id>: <title> (<mode>)` line per catalog item,
  serving both as a progress indicator and a "what is the tool doing right
  now" signal between questions — deliberately one shared mechanism instead
  of two.
- **Phase C — binary spell-out (#5, #6).** Root cause: REP-RATIONALE-004's
  binary-package spell-out sourced names from `dep-analysis`, which is
  skipped whenever `sbuild` fails (as it did for borgbackup2) — the shortcut
  options silently spelled out nothing. `packaging-source` now also exposes
  `binary_package_names` (parsed straight from `debian/control`, reusing the
  existing `_binary_package_names` helper), independent of sbuild; the
  catalog item and its `binary-packages` preface evaluator switched to it.
  Added a `spell_out_filter: list_only` mode (`QuestionOption.list_note`) so
  the "specific packages" option also shows the known package list without
  changing its recorded statement. Removed REP-RATIONALE-004B ("what purpose
  does promoting this scope achieve?") entirely — redundant with the
  overall rationale already collected earlier.
- **Phase D — deadline template (#7).** Real bug: REP-RATIONALE-008's
  template had two `TBD` slots ("no later than TBD due to TBD") but only one
  free-text answer is ever collected, and both `ai.py`/`evaluator.py` fill
  templates via `template.replace("TBD", answer, 1)` — the second slot
  always stayed literal. Collapsed to a single `TBD`; reworded the prompt to
  ask for one combined date/release explanation. `catalog.py` gained a
  validation rule rejecting any reporter template with more than one `TBD`
  (excluding the unrelated `TBDSRC` source-name substitution) so this class
  of bug can't silently recur; confirmed no other template tripped it.
- **Phase E — evidence context in editor (#8, core of #9).** A
  `preface_evaluator`'s finding was only ever shown as a console-only "Note"
  before the question; it never reached the editor's commented-out hint area
  for multiline questions. Extracted `evaluator._preface_text`, shared by
  `_show_preface` (console, unchanged) and a new `_evidence_hint` folded into
  `QuestionSpec.hint` (already rendered in both console and editor). Gave
  REP-QA-TEST-007 a `preface_evaluator: autopkgtests` (reusing REP-QA-TEST-002's
  evaluator) so the passing/failing architecture breakdown is visible before
  answering "explain every failing autopkgtest", instead of the reporter
  answering blind and needing a consistency-pass correction afterwards.
- **Phase F — adapter-unavailability guard + REP-STD-001 redesign (#9b).**
  Root cause: REP-STD-001 (`ev_to_ai`, FHS/Policy) called the LLM even when
  its required `lintian` adapter had `status: error`, so it claimed FHS
  compliance while its own rationale admitted lintian never ran because
  sbuild failed. `ai.evaluate_ai_item` now checks every
  `adapters_required` adapter's status before calling the LLM at all,
  skipping straight to `_ask_human` with a rationale naming which
  adapter(s) were unavailable and why — a generic fix covering every
  `ev_to_ai` item. REP-STD-001 converted from free-text `ev_to_ai` to a
  `human_only` single_choice A/B mirroring REP-STD-002's existing
  License-lifetime pattern, with a `lintian-fhs-summary` preface evaluator
  and option A locked (via Phase A's mechanism) whenever lintian reports
  errors. While testing this, found and fixed a real bug:
  `_mark_followup_options` rebuilt every `QuestionOption` in a question
  without carrying over `locked_reason`/`list_note`, so a locked option
  silently lost its lock the moment ANY sibling option in the same question
  led to a follow-up — this had silently neutered Phase A's REP-MAINT-001
  lock too, once exercised through the real catalog (REP-MAINT-001B) instead
  of a synthetic no-followup test fixture. `_apply_option_lock`'s locked
  branch had the same gap for `list_note`; both fixed.
- **Phase G — optional-answer skip clarity (#12).** Both
  `_render_answer_guidance` (console) and `_multiline_comment_lines`
  (editor) used an if/elif, so a question with a custom `answer_guidance`
  silently suppressed the generic "leave the answer empty to skip" note
  entirely. Both now always show the skip note in addition to any custom
  guidance. Also reworded the console version to stop mentioning the
  raw-terminal "'.' on the first line" convention, misleading now that the
  external editor is the default multiline path. Removed REP-QA-TEST-003's
  matching stale `answer_guidance`.
- **Phase H — readiness summary redesign (#13).** Root cause:
  `_readiness_summary`'s "Blocking items"/"Warnings" lists were sourced from
  each item's static catalog-declared `readiness`, not whether it was
  actually still unresolved, so a fully-answered item (no leftover TODO)
  stayed listed as blocking forever. Now sources both lists from
  `ctx.consistency_report` when available (the normal case — every real run
  calls `run_consistency_pass`, which already reflects final resolution
  state including placeholder/contradiction detection), falling back to the
  old static sweep only when no consistency report is supplied (synthetic
  unit-test setups). The summary block moved to the very top of the draft
  (right after the header), followed by a full-width `"=" * 70` separator;
  each listed item now renders as `REP-ID -- Section / Title` via a catalog
  lookup instead of a bare id; labels renamed to "Remaining TODOs (must
  resolve before submission)" / "Remaining TODOs (recommended,
  non-blocking)".
- Six vscode_askQuestions decisions confirmed up front (all recommended
  options accepted): LLM self-report + phrase backstop for option locking;
  locked options stay visible with `(unavailable: reason)`; drop
  REP-RATIONALE-004B entirely; collapse the deadline template to a single
  blank; two renamed "Remaining TODOs" lists (not merged); one progress/context
  log line per catalog item.
- Scope boundaries: reviewer role/`catalog-mir-review.yaml` untouched (no
  equivalent License/FHS checks exist there); no general-purpose
  option-applicability DSL beyond what's needed (`conditions.py` reused
  as-is, evidence-only); REP-STD-001's lock condition mirrors the existing
  `ai_policy`'s coarser "any lintian error/warning" treatment rather than
  classifying which lintian tags are specifically FHS/Policy-relevant.
- Validation from `tools/auto-mir`: `make test` PASS (743 passed, 3
  skipped), one commit per phase. `make integration` intentionally left for
  the user to run.

## 2026-08-06 — Replace sbuild with fetch-build (download the official Launchpad build)

**Feedback (round, source package prompt-toolkit/borgbackup2 test runs):**
sbuild was "huge and has too many chances to fail" — it rebuilds the whole
package locally (chroot/build-dep resolution, long build times, real
CPU/memory/disk cost), only ever exercises one architecture, and a local
failure (e.g. an unresolvable build-dependency in the local unshare chroot)
cascades into TBD placeholders across lintian, dep-analysis, and binary
inspection for the whole run — even when the package promotion is not
actually blocked by anything. A promotion candidate is expected to already
be published in universe with a successful official Launchpad build, so
rebuilding it locally added a lot of failure surface for little real gain.
Confirmed with real evidence: borgbackup2's local sbuild failed resolving
`python3-backports.zstd`/`python3-jsonargparse` in the local mmdebstrap
chroot, cascading into "Unavailable" TBDs across the reporter draft.

**Design:** New `evidence/launchpad_client.py` centralises the launchpadlib
session, series resolution, per-publication build lookups, and a
`buildstate` classifier (successful/queued/in_progress/failed/unknown) used
by all three of: packaging-source's version resolution, lp-build-api, and
fetch-build.

`packaging-source._resolve_source_pocket_version` is now build-aware and
always pins an explicit version (source, build artifacts, and all
downstream evidence must never drift apart): within the chosen pocket it
prefers the newest fully-built version, and — a design requirement
clarified during alignment — walks up to 5 older versions when the newest
isn't (yet) fully built, offering a genuine choice among *all* buildable
candidates found in that window (not just auto-picking the first one),
differentiating "has not yet built" vs "has failed to build" vs "is
currently building". Interactive on a TTY (numbered list, mirrors
`auto_mir._ask_requested_binaries`'s prompt convention); headless runs
auto-pick the newest fully-built candidate and log why. No polling/waiting
either way — a run with nothing buildable in the lookback window fails
closed with a clear message.

`lp-build-api` is now pinned to that exact `analyzed_version` (fixing a
real bug: `_builds_from_published_sources` used to return builds for
whichever Launchpad publication happened to have *any* builds, not
necessarily the version actually analysed — affecting CB-1 and two reporter
checks that already consumed it independently of sbuild).

New `fetch-build` adapter (renamed from `sbuild`) downloads, for the
guest's own architecture only: the build log (gzip, decompressed via the
`launchpadlib` build record's `build_log_url`), `.changes`, and the `.deb`
binaries (via a fresh `getPublishedBinaries()`/`binaryFileUrls()` lookup
pinned to the same analysed version) — using the existing retry-wrapped
`utils/http.py` downloaders, pushed into the guest with
`lxd_runner.push_file()`. Other architectures only ever get their
lp-build-api build status; nothing is downloaded for them. Reuses
`_inspect_built_debs()` unchanged, so `deb-metadata`/
`binary-package-inspection`/`dep-analysis` needed no contract changes
beyond the renamed dependency — this was a deliberate design constraint to
keep the blast radius contained to "how the build artifacts are obtained",
not "what shape they are".

**New capability (explicit alignment decision):** the official Launchpad
build never runs lintian, so fetch-build now runs it twice — against the
source tree (as before) and, new, against the downloaded binaries/.changes.
The old sbuild flow only ever linted source (`--no-run-lintian` skipped it
during the build, and no `.changes` file existed locally to lint against
even if it hadn't).

**CB-1 simplified** (explicit alignment decision): once "local build" is
really just a download of the already-official build, the old
`hint_local_ok`/`hint_local_failed`/`hint_local_unavailable`/
`ok_local_suffix` dual-phrasing ("local sbuild build succeeded" alongside
"Launchpad build records pass") was redundant. CB-1 is now purely a
Launchpad per-architecture build-state check and depends only on
`lp-build-api`.

**Side-effects found and fixed while wiring this up (not separately
requested, but directly obsoleted by the redesign — left in place would
have been actively wrong/misleading):**
- `lxd_runner.py`'s guest provisioning no longer installs
  `sbuild`/`mmdebstrap`/`uidmap` (including the noble-backports special
  case) — none of it is needed once nothing runs sbuild locally. This is
  itself further "reduced chance to fail" surface removed from every run.
- `lp_intake.py` had a hard gate rejecting any series older than Noble
  (24.04) "for sbuild unshare backend" — that constraint no longer exists,
  so older series can now be reviewed/reported on too. Removed
  `_series_supports_unshare_sbuild`/`_KNOWN_SERIES`.

**Scope boundaries:** no change to `packaging-source`'s actual
`apt-get source` fetch mechanism beyond the new candidate-version probing
loop; no other adapters touched; no cross-architecture building/emulation;
no change to how the reviewer/reporter roles pick which LP bug/series to
target (only which source version within that series to analyse).

Full rename sweep: `AdapterID.SBUILD` → `FETCH_BUILD`, `SbuildResult` →
`FetchBuildResult` (`sbuild_build_log_path` → `build_log_path`), every
`adapters_required`/`depends_on`/`evidence_refs`/message referencing
`sbuild` across `catalog.yaml`, `catalog-mir-review.yaml`,
`catalog-mir-report.yaml`, `checks/deterministic.py`, `checks/llm_eval.py`,
`reporter/evaluator.py`, `auto_mir.py`, and every test fixture.
`tests/test_integration_sbuild.py` renamed to
`tests/test_integration_fetch_build.py` (real-VM smoke test now uses
"hello", a small always-built Ubuntu main package, via a real
`lp-build-api` lookup instead of a real local build).

Validation from `tools/auto-mir`: `make test` PASS (792 passed, 2 skipped),
one commit per phase (shared Launchpad client → build-aware version
resolution → lp-build-api pin fix → fetch-build adapter + full rename
sweep). `make integration` intentionally left for the user to run (real
LXD guest + real Launchpad network calls).

## 2026-08-06 — Consolidated the dual evidence-adapter dependency graph

- Promotion: no
- Context: since the 2026-07-15 "Catalog-authoritative adapter topology"
  decision, every adapter's `depends_on` was declared twice: once in the
  `@adapter(AdapterID.X, depends_on=[...])` decorator (`evidence/registry.py`
  and its ~20 call sites across `host_adapters.py`/`guest_adapters.py`), and
  once in `catalog.yaml`'s `evidence_adapters[].depends_on`. A dedicated test
  (`test_catalog_adapter_dependencies_match_registrations`) caught drift
  between the two, but adding or changing an adapter's dependency still
  required touching both places. The registry copy was already unused at
  runtime except as a fallback for catalogs with no `evidence_adapters`
  section — a case that in practice only existed inside unit-test fixtures.
- Decision:
  - `evidence/registry.py`'s `ADAPTER_REGISTRY` now maps adapter ID directly
    to its collector function (no dependency tuple); the `@adapter` decorator
    drops the `depends_on` parameter entirely.
  - `evidence._catalog_adapter_dependencies(ctx.catalog)` is the sole
    dependency source; `collect_from_catalog` no longer falls back to
    registry-derived dependencies, and `_order_adapters` now requires an
    explicit `adapter_deps` mapping (its dead registry-reading branch, never
    reachable from any real call site, is removed).
  - Stripped the now-redundant `depends_on=[...]` from all ~20 `@adapter(...)`
    call sites; `catalog.yaml`'s `evidence_adapters` is unchanged and remains
    the only place dependency edges are declared.
  - Deleted `test_catalog_adapter_dependencies_match_registrations` (its
    purpose no longer exists) and rewrote the ~6 orchestration unit tests
    that previously monkeypatched `ADAPTER_REGISTRY` with
    `(mock_fn, [deps])` tuples: they now patch in plain mock functions and,
    where ordering matters, declare the dependency via an `evidence_adapters`
    list on the synthetic `ctx.catalog` fixture — matching how real catalogs
    already express it.
- Consequences: an adapter's dependency wiring now has exactly one place to
  edit and reason about (`catalog.yaml`); no behavior change for any real run
  (production catalogs always populated `evidence_adapters`, and the drift
  test already proved the two graphs agreed before this change).
- Validation from `tools/auto-mir`: `make test` PASS (791 passed, 2 skipped —
  one test count lower than before because the now-pointless drift test was
  deleted, not because coverage was lost).

## 2026-08-07 — Fixed a false "has not yet built" positive and unified version resolution

- Promotion: no
- Context: a beta tester's real run against `jitterentropy-library` had
  `packaging-source` fail with "The most recent build version 3.6.3-1 has not
  yet built", even though Launchpad shows it fully built on every
  architecture. Root cause (verified empirically against the live Launchpad
  API, not just by reading code): the target devel series ("stonking") had
  just opened this cycle, and the whole archive - including
  already-built packages like this one - was copied across from the
  predecessor series ("resolute") without creating fresh `Build` records for
  the new series; the binaries were copied straight across, still
  referencing the *original* series' builds. `ISourcePackagePublishingHistory
  .getBuilds()` on the new series' publication legitimately returns zero
  records, but `getPublishedBinaries()` on that same publication shows every
  architecture Published. `evidence.launchpad_client.summarize_build_completeness`
  only ever looked at `getBuilds()`, so a zero-build (but fully available)
  publication was indistinguishable from a genuinely-unbuilt one. Series
  resolution itself was ruled out as a contributing cause: Launchpad's
  `getSeries(name_or_version="devel")` webservice operation defaults
  `follow_aliases=True` server-side and reliably resolves to the real devel
  series without needing an explicit fallback.
  Separately, the same feedback asked that every adapter needing "the exact
  version under review" (packaging-source, lp-build-api, and implicitly
  fetch-build) select it once and agree - not each independently re-derive
  (and potentially re-select) its own answer.
- Decision:
  - `evidence/launchpad_client.py`: added `binaries_for_publication()`
    (mirrors `builds_for_publication`, never raises) and extended
    `summarize_build_completeness(builds, binaries=None)` so an architecture
    with a Published binary but no distinct Build record is treated as built
    too (flagged via a new `carried_over` bool), while a real Build record
    for an architecture always stays authoritative over a binary. `find_buildable_version`
    now probes binaries alongside builds for every candidate.
  - Broadened candidate offering: a "mixed" newest version (built on some
    architectures, not others) is no longer silently discarded in favour of
    an older fully-built one - `BuildCandidate.has_available_arch` is True
    for both "successful" and "mixed", `BuildCandidate.label` spells out
    which architectures pass/fail for a mixed candidate, and headless
    (non-interactive) runs now prefer the newest available candidate even if
    only partially built (interactive TTY runs still offer the full numbered
    choice, newest first). The hard-fail path (`AdapterError`, "re-run once
    Launchpad has a successful build") now only fires when nothing in the
    whole lookback window has any built/available architecture at all.
  - New adapter `version-resolution` (`AdapterID.VERSION_RESOLUTION`, host-
    side, `depends_on: [lp-package-api]`) is the single place that decides
    the exact version/pocket to analyse - moved out of `packaging-source`
    verbatim (`evidence/version_resolution.py`), including the
    interactive/headless fallback UX. `packaging-source`'s `depends_on`
    changed from `lp-package-api` to `version-resolution`; it no longer logs
    into Launchpad itself at all, and copies `resolved_version`/
    `resolved_pocket`/`resolution_note` through into its own
    `analyzed_version`/`analyzed_pocket`/`version_resolution_note` fields
    unchanged, so render.py/reviewer/reporter templates and existing tests
    keep working without a rename sweep. `lp-build-api`'s `depends_on`
    changed from `packaging-source` to `version-resolution` and it now reads
    `resolved_version`/`resolved_pocket` from there; it still runs its own
    targeted Launchpad query (for per-build metadata: log/changesfile/
    buildinfo URLs), but reuses `summarize_build_completeness` against the
    same publication so an architecture with only a carried-over binary is
    also surfaced in `builds` (previously CB-1 reported "no build records"
    for exactly this scenario, a matching false-negative).
- Consequences: a package that is fully available in the archive (whether
  freshly built or carried over unchanged from a predecessor series) is no
  longer misreported as unbuilt, and no longer cascades into skipping
  dup-search/lp-build-api/fetch-build/dep-analysis/binary-package-inspection/
  lintian. Version/pocket selection now has exactly one implementation and
  one point of failure instead of being duplicated (and potentially
  disagreeing) across packaging-source and lp-build-api.
- Validation from `tools/auto-mir`: `make test` PASS (803 passed, 2 skipped).
  `make integration` intentionally left for the user to run (real LXD guest +
  real Launchpad network calls).

## 2026-08-07 — Beta feedback round (jitterentropy-library reporter run), 4 items

- Promotion: no
- Context: a reporter test run against `jitterentropy-library` surfaced four
  pieces of feedback, addressed as four independent, separately committed
  changes on `auto-mir-review`:
  1. REP-QA-TEST-005 (non-automated testing access) had no option for "build
     and autopkgtest already cover everything this package needs" - every
     existing option routed into a REP-QA-TEST-006 follow-up question asking
     for more detail, which made no sense for this answer.
  2. `fetch-build.build_log` stayed empty even though the reporter's own log
     showed "Official Launchpad build succeeded: 2 .deb file(s) downloaded",
     and the user separately confirmed a real, working build log exists and
     is fetchable. Verified empirically against the live Launchpad web UI
     (not just by reading code): `jitterentropy-library` 3.6.3-1's source
     package overview page (`+source/jitterentropy-library/3.6.3-1`) lists
     builds only under "Resolute" - there is no "Stonking" (devel) build
     section at all, confirming the package was carried over unchanged into
     the newly-opened devel series (the exact scenario the prior 2026-08-07
     "has not yet built" fix already handles for *completeness*, but not yet
     for the build log itself). `lp-build-api`'s carried-over-architecture
     fallback (added by that same prior fix) hardcoded `build_log_url: ""`
     for such architectures, since there genuinely is no `Build` record for
     the *current* series to query - but the published binary itself still
     references the real build that originally produced it (an ordinary
     `binary_package_publishing_history.build_link`), so a real log was
     resolvable and simply was never looked up.
  3. REP-UI-001 (human_only free-text "is this end-user facing?") and
     REP-UI-002 (ev_to_ai, same topic, evidence-grounded) covered the exact
     same question with zero data flow between them - forcing a manual
     answer immediately before a better AI-suggested one for the same topic
     was pure friction with no compensating value.
  4. Only 9 of the ~36 human_only/ev_to_ai reporter items showed policy
     "Context: RULE: ..." text ahead of their question (a P0-phase feature);
     the other ~27 showed nothing, even though the exact same policy text
     already lives in `catalog-mir-report.yaml`'s own
     `metadata.reporter_template_blueprint` (which interleaves `'[Section]'`
     markers, `'RULE: ...'` lines, and `item: REP-XXX` entries in template
     render order) - authoring per-item `rule_context` by hand risked
     drifting from that blueprint prose over time, which item 3 below's own
     analysis (see below) confirmed had already happened once.
- Decision:
  1. Added option `Y-build-autopkgtest` to REP-QA-TEST-005, recorded
     verbatim with no follow-up question. No new code: REP-QA-TEST-006's
     `applicability` changed from `{item: REP-QA-TEST-005, truthy: true}` to
     `{item: REP-QA-TEST-005, in: [<the 10 pre-existing option ids>]}`,
     reusing `reporter/conditions.py`'s existing `in` operator and
     `reporter/evaluator.py`'s existing `_condition_triggers`/
     `_mark_followup_options` follow-up-hint derivation unchanged.
  2. `evidence/launchpad_client.py` gained `original_build_for_arch(binaries,
     arch_tag)`: for a carried-over architecture, follows the matching
     published binary's `build` reference to the real originating `IBuild`
     object (never raises - a missing/undereferenceable link is treated as
     "no original build found"). `evidence/host_adapters.py`'s
     `collect_lp_build_api` carried-over-entries loop now populates
     `build_log_url`/`changesfile_url`/`buildinfo_url`/`version`/
     `date_created`/`pocket`/`archive` from that real build instead of
     hardcoded empty placeholders, falling back to the previous empty
     placeholders unchanged when no original build is resolvable. Separately
     (defense in depth for the residual case where even this fails, e.g. a
     genuinely pruned/never-existed log): `reporter/evaluator.py`'s
     `build-tests` evaluator (REP-QA-TEST-001) now falls back to
     `packaging-source.debian_rules_overrides` when `build_log` is empty,
     stating confidently whether the default `dh_auto_test` target is
     disabled/overridden or left to run unmodified, instead of an
     uninformative "log unavailable" TODO. REP-QA-TEST-004's `ai_policy`
     (ev_to_ai "Test adequacy assessment") gained an explicit instruction to
     use the same `debian_rules_overrides`/`debian_rules` evidence (already
     passed to the model in full for this item) the same way, instead of
     declaring the assessment impossible purely because the log is missing.
  3. Removed REP-UI-001 from `catalog-mir-report.yaml` (item definition and
     blueprint reference); REP-UI-002 is now the sole UI-standards item.
     Reporter item count is 55->54. No other code referenced REP-UI-001 by
     name (verified via full-repo grep).
  4. `catalog.py` gained `_blueprint_section_rules(blueprint)` (parses
     `metadata.reporter_template_blueprint` once into `{section: [RULE
     lines]}`, since RULE lines always precede all items in a section) and
     `_apply_reporter_rule_context_defaults(catalog)`, called from
     `load_catalog_for_role` only for the `"report"` role: every
     `human_only`/`ev_to_ai` item without an explicit `rule_context` gets its
     section's RULE line(s) plus its own `template` (`TODO: ...`) line joined
     together, so the reporter sees WHY (policy) and WHAT (what this item
     resolves) with zero hand-duplicated text. Items that already hand-set
     `rule_context` (9 today, e.g. `REP-MAINT-001`) are left completely
     unchanged, including not getting the TODO line appended - hand-picking a
     specific RULE for one item out of several in its section is still a
     legitimate reason to author it explicitly. `validate_report_catalog` now
     rejects any hand-authored `rule_context` line starting with `RULE:` that
     isn't a verbatim match of one of its own section's blueprint RULE
     lines, as a permanent drift guard. **This check immediately caught a
     real, pre-existing drift**: `REP-DEP-002`'s hand-authored `rule_context`
     was a paraphrase, not a verbatim copy, of the `[Dependencies]` section's
     actual blueprint RULE line (8 of the 9 hand-set items matched verbatim;
     this one didn't) - fixed by removing the paraphrase entirely and letting
     it be auto-derived like the other ~27 items, rather than trying to keep
     a hand-written paraphrase in sync forever.
- Consequences: REP-QA-TEST-005 now has a clean terminal answer for the
  common "we don't need anything beyond build+autopkgtest" case. The
  `jitterentropy-library` build-log gap is fixed at its real, verified root
  cause (a carried-over architecture's binary still points at its real
  build) rather than papered over with a retry/guess; REP-QA-TEST-001/004
  additionally degrade gracefully instead of going blank in the rarer case
  where even that resolution fails. The reporter has one fewer redundant
  question. ~27 more reporter items now show policy context ahead of their
  question, all sourced from the catalog's own existing blueprint data with
  a test-enforced guarantee against future drift - and the mechanism itself
  found and fixed one real drift bug during implementation.
- Validation from `tools/auto-mir`: `make test` PASS (814 passed, 2 skipped,
  up from an 803-passed baseline: +2 catalog drift-guard/auto-derivation
  tests, +2 `original_build_for_arch` tests, +2 `collect_lp_build_api`
  carried-over tests, +5 `build-tests`/`_build_tests_without_log` tests).
  `make integration` intentionally left for the user to run (real LXD guest
  + real Launchpad network calls).
- **Follow-up correction (same day)**: item 4's `rule_context` reached the
  external-editor comment header for `human_only`/`ev_to_ai` multiline
  questions via `reporter/wizard.py`'s `_multiline_comment_lines()`, which
  did `lines.append(f"Context: {question.rule_context}")` - a *single* list
  element containing the full, now-multi-line (several `RULE:` lines plus a
  `TODO:` line) string. `utils/editor.py`'s `edit_text()` prefixes each
  `comment_lines` *list element* with `# ` once; it has no way to see the
  embedded `\n` characters inside one element, so only the first physical
  line ("Context: RULE: ...") got commented out and every subsequent
  RULE/TODO line landed in the generated file unprefixed - meaning it would
  have silently become part of the reporter's actual answer text instead of
  being inert commentary. Fixed by emitting `"Context:"` as its own header
  line followed by each `rule_context` line as a separate, indented
  (`"   "` + line, so `edit_text`'s own `"# "` prefix yields the visually
  4-space-indented style already used by the console's
  `_write_titled_block`) list element - one per RULE/TODO line, so every one
  gets its own `#` prefix. Added a direct unit test asserting the exact
  `comment_lines` list for a multi-RULE-plus-TODO `rule_context`, and an
  end-to-end test through the real `utils.editor.edit_text()` asserting no
  generated line containing `RULE:`/`TODO:` is ever missing its `#` prefix.
  `make test`: 816 passed, 2 skipped.

## 2026-08-07 — Reporter feedback round (jitterentropy-library test), phase 1: readiness summary no longer in the draft file

- Promotion: no
- Context: a beta tester's `report` run left the `[Auto-MIR readiness
  summary]` block (with "Ready for submission: yes/no" and both a
  "must resolve" and a "recommended, non-blocking" TODO list) embedded at
  the top of `reporter-draft.txt`. Two problems: (1) a submitter who
  copy-pastes the whole draft onto Launchpad risks posting this internal
  bookkeeping block verbatim into the public bug; (2) the "recommended,
  non-blocking" list is frequently stale by the time the interactive
  session finishes (most of those items get resolved through later
  questions) and re-listing them creates a false impression of remaining
  work, when any genuine leftover is already easy to spot in the draft
  itself (it stays a bare `TODO: -` line).
- Decision: remove the readiness summary entirely from `_build_draft()` (the
  draft now starts directly with the header, then the catalog sections).
  Instead, `reporter/render.py::write_outputs()` logs a trimmed console/log
  variant (`readiness_console_lines()`) via `auto_mir.reporter` after writing
  the files: "Ready for submission" plus the "must resolve before
  submission" list only, each item labelled by section/title. The
  "recommended, non-blocking" section is dropped entirely, not just moved.
  `report.json`'s `readiness` key is left unchanged (still both `blockers`
  and `warnings`) since it's a machine-readable artifact, not something a
  submitter pastes verbatim into a bug — kept for tooling/audit use.
  review mode's separate `[Summary]` rendering (`render/__init__.py`) was
  not touched.
- Consequences: `reporter-draft.txt` is now safe to copy-paste directly;
  reviewers who want the readiness snapshot see it in the console/log output
  of the run instead. Existing tests
  `test_readiness_summary_only_lists_items_still_genuinely_unresolved` /
  `test_readiness_summary_reflects_option_override_blockers` /
  `test_consistency_error_forces_not_ready_rendering` (all asserting on
  `report.json`) are unaffected; the draft-content assertion in
  `test_reporter_render_writes_draft_and_structured_report` and the old
  `test_readiness_summary_block_is_at_top_with_separator_and_labels` (now
  split into `test_readiness_summary_is_absent_from_the_draft_file` and
  `test_readiness_summary_console_log_lists_only_must_resolve_items`) were
  updated accordingly.
  `make test`: 817 passed, 2 skipped.

## 2026-08-07 — Reporter feedback round (jitterentropy-library test), phase 2: upstream URL Homepage priority + existence verification

- Promotion: no
- Context: for `jitterentropy-library`, the reporter's REP-BG-002 preface
  suggested `http://www.chronox.de/jent.html` as the upstream project URL --
  a page that does not exist -- instead of debian/control's own `Homepage:
  https://github.com/smuellerDD/jitterentropy-library`. Root cause: (1)
  `_collect_upstream_search_terms` merged debian/watch-derived URLs (usually
  a download/tarball location, sometimes on a different domain from the
  project's real home) and the debian/control Homepage into one flat,
  unordered `url_hints` list, so a release-monitoring.org project matching
  either scored identically (100) in `_select_upstream_project`, and the
  fallback path (`url_hints[0]`) preferred whichever hint happened to be
  collected first, not necessarily Homepage; (2) nothing ever verified a
  candidate URL actually resolves before presenting it.
- Decision: keep the Homepage hint distinct from debian/watch hints
  throughout (`_collect_upstream_search_terms` now returns
  `(search_terms, homepage_hint, watch_url_hints)`), and give a
  Homepage-hint match the top scoring tier (100) in
  `_select_upstream_project`, above an exact name match (90/80), which is
  itself above a watch-hint-only match (70) and a partial name match (60) --
  a scoring adjustment, not a hard bypass of the release-monitoring.org
  lookup, so a strong independent signal can still outrank it. Added
  `utils/http.py::check_url_exists()`: a single-attempt HEAD (GET fallback
  on 405/501), ~10s timeout, deliberately NOT wrapped in the existing
  `retry_rate_limited` policy (6 attempts, up to 300s) -- a URL-existence
  sanity check on a value about to be shown to a human should fail fast, not
  stall evidence collection for minutes over one broken link. New
  `_verified_upstream_url()` tries an ordered, deduped candidate list
  (whatever `_select_upstream_project` picked, then the Homepage hint, then
  watch hints) and returns the first one that verifies, so a genuinely good
  fallback candidate (e.g. the real Homepage) can still win even when a
  higher-preference candidate (e.g. a release-monitoring.org project's own
  homepage) turns out to be stale -- rather than giving up entirely after
  one failed check. If nothing verifies, `upstream_url` is left empty
  (adapter stays `status: "ok"`, matching the existing graceful-empty
  pattern for "no match found") so the reporter is asked instead of shown a
  dead link.
- Consequences: for the exact jitterentropy-library scenario, the
  release-monitoring.org match via the watch-derived chronox.de hint no
  longer silently wins, and even if it's selected as the best-scoring
  project, its stale URL fails verification and the tool falls through to
  the verified GitHub Homepage. Existing upstream-tracker tests were updated
  to mock `check_url_exists` (no real network calls in unit tests); new
  tests cover the Homepage-vs-watch-hint scoring regression and the
  verification-fallback/all-fail cases, plus direct `check_url_exists` unit
  tests in `tests/test_utils_http.py` (200/404/405-fallback/timeout/
  URLError).
  `make test`: 825 passed, 2 skipped.

## 2026-08-07 — Reporter feedback round (jitterentropy-library test), phase 3: REP-BG-002 upstream name becomes an AI suggestion

- Promotion: no
- Context: REP-BG-002 ("Upstream name") was `human_only` even though, by the
  time it's asked, the tool already has a (now Homepage-prioritized and
  verified, phase 2) upstream URL plus the full `debian/control` content --
  usually enough to confidently guess the project name, leaving the
  reporter to just confirm rather than type it from scratch.
- Decision: change REP-BG-002's `mode` from `human_only` to `ev_to_ai` in
  `catalog-mir-report.yaml`, with `adapters_required: [upstream-tracker,
  packaging-source]` and a new `ai_policy` grounding the guess in
  `upstream-tracker.upstream_url`/`upstream_name` and
  `packaging-source.debian_control`. The existing text question (with its
  `default_source` dynamic default) is kept unchanged as the low-confidence/
  unavailable fallback, reusing `reporter.ai.evaluate_ai_item` +
  `wizard.confirm_suggestion` exactly like the other `ev_to_ai` items --
  no new mechanism.
  **Gotcha hit while writing the new `ai_policy` string**: a `: ` (colon
  immediately followed by a space) mid-sentence ("...distinct upstream
  project: set requires_reporter_decision...") is invalid as a plain YAML
  scalar and broke catalog loading for every test; reworded with a `-`
  instead (this exact class of mistake is already flagged in this project's
  own notes -- see the "YAML gotcha" entries earlier in this log).
  **Real bug found and fixed as a direct consequence of this mode change**:
  `writes_evidence` (REP-BG-002's own URL backfill into
  `upstream-tracker.upstream_url` from a human-typed URL answer) was only
  ever wired into the `mode == "human_only"` dispatch branch in
  `reporter/evaluator.py`. Moving REP-BG-002 to `ev_to_ai` would have
  silently dropped that backfill for its `_ask_human` fallback path (the
  only place a bare-URL answer can still occur). Fixed by moving
  `_maybe_write_evidence`/its URL pattern out of `evaluator.py` into the
  shared `reporter/text_utils.py` (renamed `maybe_write_evidence`, no
  leading underscore -- it's now a cross-module helper, following the same
  pattern already used there for `ensure_bulleted`/`substitute_source` to
  avoid the `evaluator`<->`ai` circular import), and calling it from both
  the `human_only` branch (unchanged behavior) and `reporter/ai.py`'s
  `_ask_human()` (new).
- Consequences: `tests/test_reporter_evaluator.py`'s `maybe_write_evidence`
  tests now import from `reporter.text_utils`. New tests in
  `tests/test_reporter_ai.py` cover the REP-BG-002-shaped ev_to_ai
  suggestion-accept flow and confirm the `writes_evidence` backfill still
  fires through the `_ask_human` fallback. REP-BG-001 (package purpose) is
  untouched -- a different item, still `human_only`.
  `make test`: 827 passed, 2 skipped.

## 2026-08-07 — Reporter feedback round (jitterentropy-library test), phase 4: dead evidence field cleanup

- Promotion: no
- Context: feedback item 4 asked whether the many detail fields adapters
  produce (e.g. `binary-package-inspection`'s `lintian_errors`,
  `static_binaries`, `systemd_units`, etc.) are ever really used, or are
  wasted schema/code. A field-by-field audit (checked every consumer:
  `checks/deterministic.py`, `checks/llm_eval.py`, `reporter/evaluator.py`,
  `reporter/ai.py`, both catalog YAML files' `ai_policy` prose, and
  `utils/llm_evidence.py`'s truncation allow-lists) found all 13 originally-
  cited binary-inspection fields ARE actively used (`lintian_errors`/
  `warnings`/`pedantic` feed URF-5; `static_binaries` feeds ESL-2;
  `setuid_setgid_binaries`/`nobody_owned_binaries` feed URF-5/URF-4;
  `sbin_executables`/`systemd_units`/`cron_jobs`/`apparmor_profiles`/
  `desktop_files`/`translation_files`/`plugin_candidates` are all read by
  name in `reporter/evaluator.py`'s `_binary_security_surface`/
  `_binary_integration_surface`) -- no change needed there, they're simply
  empty for a simple package like jitterentropy-library, exactly as
  hypothesized.
  A broader sweep across every `evidence/types.py` TypedDict field did find
  five genuinely dead ones (zero consumers anywhere outside their own
  producing adapter and `evidence/types.py`'s own declaration -- verified
  directly, not just via a subagent's grep, per this project's own "don't
  trust a single/truncated grep" lesson): `packaging-source.source_homepage`
  (extracted from debian/control but never read -- `source_description`,
  extracted the same way, IS read, via `ai_policy` prose in
  `catalog-mir-report.yaml`, so this isn't a wholesale "nobody reads
  debian/control facts" issue, just this one field); `ubuntu-cve-tracker`'s
  `active_cves`/`fixed_cves` lists (every consumer of CVE data reads the
  combined `cves` list instead, both in `reporter/evaluator.py` and the
  review catalog's SEC `ai_policy` prose); `ubuntu-cve-tracker`'s per-CVE
  `fix_version` field (within `CVEEntry`); `cvelist-scan`'s per-candidate
  `published_date` field; and `lp-team-membership-api`'s
  `ubuntu_mir_subscribed` boolean (the real, working "ubuntu-mir team must
  be subscribed" gate is `lp_intake.py`'s own `_evaluate_mir_heuristics()`,
  reading `ctx.bug["subscribers"]` directly at intake time -- this
  evidence-blob copy, and `lp-bug-api`'s parallel `mir_heuristics` copy of
  the same intake-time dict, were never read by anything downstream).
- Decision: remove all five dead fields from their producing adapters
  (`evidence/guest_adapters.py`, `evidence/host_adapters.py`,
  `evidence/cvelist_scan_invm.py`), their `evidence/types.py` TypedDict
  declarations, and `catalog.yaml`'s `output_contract` documentation blocks
  (confirmed these blocks are pure documentation -- `catalog.py` never
  validates them against real adapter output, so there was no correctness
  risk either way, but leaving them wrong right after touching the exact
  field list would be a needless new inconsistency). Also corrected
  `lp-team-membership-api`'s `output_contract` while there: it was already
  badly stale (`members: list` / `is_subscribed: bool`, matching neither the
  pre- nor post-cleanup real adapter output of `subscribers: list`) --
  fixed to match reality, but did not otherwise change what this adapter
  does (a deeper question of whether it should do real Launchpad team-
  membership lookups, as its name and two consuming checks' `ai_policy`
  text (RDO-2, PRF-7) seem to assume, is a separate, out-of-scope concern
  flagged here for a future look, not fixed now).
- Consequences: `evidence.json` output is slightly smaller/cleaner for every
  run. `tests/test_evidence.py`'s
  `test_parse_source_control_fields_handles_continuations` no longer
  asserts a `homepage` key (the helper it tests still parses `Homepage:`
  internally for `_collect_upstream_search_terms`, an entirely separate
  code path added in phase 2 -- only this one now-unused derived copy was
  removed). **Caught during implementation**: `evidence/guest_adapters.py`'s
  `collect_packaging_source` composes its final ~35-key return dict from
  two helper dicts (`_derive_packaging_facts`, `_scan_source_security_
  markers`) across two separate call sites; removing the field from
  `_derive_packaging_facts`'s own return left a second, now-dangling
  `packaging_facts["source_homepage"]` read in the composer a few dozen
  lines later that a whole-tree grep (not `make test`, which has zero unit
  coverage of this specific composer function -- it's exercised only by the
  real-VM `make integration` smoke test per an earlier refactor's own
  documented gap) caught before it could become a runtime `KeyError`.
  `make test`: 827 passed, 2 skipped (unchanged count -- this phase only
  removes fields, it doesn't add or remove test cases beyond the one fixture
  fix).

## 2026-08-11 — Beta feedback round: optional LLM auth, configurable retry/timeout, ubuntu-upload-permission hang

- Promotion: no
- Context: three feedback items from a test run against a local LLM endpoint
  and a real MIR review (bug 2161382-class run):
  1. `stage_auth()` hard-`SystemExit(1)`'d whenever `OPENAI_API_KEY` was
     unset, even though the endpoint (via `OPENAI_API_BASE`) may not check
     auth at all (common for local/self-hosted OpenAI-compatible servers).
     `stage_optional_auth()` (reporter mode) silently disabled AI suggestions
     in the same situation instead of trying.
  2. The LLM retry backoff (`base_delay=8.0, max_delay=60.0`, hardcoded as a
     `@retry_rate_limited(...)` decorator applied at function-definition
     time) and the per-request HTTP read timeout (`ctx.llm_timeout`, read
     dynamically but never wired to any CLI flag, defaulting to a hardcoded
     60s) gave a slow model/local setup no way to get more room before being
     retried or timing out.
  3. `evidence/guest_adapters.collect_ubuntu_upload_permission` shelled out
     *inside the LXD guest* to `ubuntu-upload-permission --list-uploaders`.
     That CLI tool always performs a real Launchpad OAuth login; a fresh
     guest has no cached credentials, so it attempts interactive
     browser-based authorization that can never complete headlessly and
     hangs until Launchpad's own polling gives up (~15 minutes observed,
     matching the reported log gap exactly). `ubuntu-dev-tools` (which
     provides the binary) was already a required guest package, so a
     missing binary was not the actual root cause here — the existing
     `command -v` preflight already failed fast and cleanly in that case.
- Decision (auth): `llm.resolve_auth()` now returns a placeholder bearer
  token (`llm.FALLBACK_TOKEN = "sk-no-key-required"`, the llama.cpp server
  convention) with a source prefixed `llm.FALLBACK_AUTH_SOURCE_PREFIX =
  "fallback:"` instead of `token=None` when `OPENAI_API_KEY` is unset.
  `stage_auth()`/`stage_optional_auth()` log a `WARNING` and proceed instead
  of aborting/disabling AI; the placeholder is not registered for secret
  redaction (it isn't a real credential, and redacting a well-known
  non-secret string would be confusing if it ever appeared verbatim in
  legitimate text). An endpoint that genuinely requires auth simply rejects
  the placeholder with its own auth error, surfaced normally through the
  existing HTTP error handling.
- Decision (retry/timeout): added `--llm-retry-base-delay` (default `8.0`,
  behavior-preserving) and `--llm-timeout` (default `60.0`) CLI flags, stored
  on `RunContext`. `llm._call_openai_compatible`'s statically-decorated
  function was split into `_call_openai_compatible_impl` (the real HTTP call,
  unchanged) plus a thin `_call_openai_compatible` wrapper that applies
  `retry_rate_limited(...)` *dynamically per call* using
  `ctx.llm_retry_base_delay`, with `max_delay = max(60.0, base_delay)` so the
  cap never shrinks below the configured base delay. Default (no flag) case
  is byte-identical to the previous hardcoded values.
- Decision (ubuntu-upload-permission): replaced the guest-exec CLI-tool
  adapter with a host-side `collect_ubuntu_upload_permission` in
  `evidence/host_adapters.py`, modeled directly on the existing
  `collect_lp_package_api`/`collect_lp_build_api` pattern —
  `launchpad_client.login_anonymously()` → `archive.getUploadersForComponent`
  (for the package's current component, reusing `lp-package-api.
  current_component` via a new `depends_on: [lp-package-api]`) and
  `archive.getUploadersForPackage` (for package/packageset-specific grants).
  Both are real, documented `IArchive` webservice methods (confirmed against
  the vendored `launchpadlib` WADL fixtures in `.venv`, not just the public
  docs); the same anonymous session already resolves `getPublishedSources`
  successfully elsewhere in this codebase, so no auth is needed for these
  either. The `UbuntuUploadPermissionResult` evidence shape
  (`components`/`team_uploaders`/`individual_uploaders`/`raw_output`) is
  unchanged, so PRF-7's catalog wiring needed zero changes; `raw_output` is
  now a synthesized human-readable summary instead of literal CLI stdout.
  `catalog.yaml`'s `ubuntu-upload-permission` entry moved from `type:
  local_exec` to `type: api`. `ubuntu-dev-tools` stays in
  `lxd_runner._REQUIRED_PACKAGES` — it's still needed by the unrelated
  `reverse-deps` guest adapter (`reverse-depends` CLI tool).
- Consequences: no interactive-auth hang is possible for this adapter
  anymore, and it no longer depends on any guest-installed tooling at all.
  `tests/test_evidence.py`'s two `_parse_upload_permission` text-scraping
  tests were replaced with four tests against mocked Launchpad API responses
  (component-only, package-specific individual+team, unknown-component
  skip, missing-source_package error) — no LXD/subprocess mocking needed at
  all now. Not yet verified live against a real package during
  `make integration` (left for the user, as with prior rounds) — if
  anonymous access to `getUploadersForPackage`/`getUploadersForComponent`
  turns out to need auth after all despite the WADL/precedent evidence, the
  fallback is to keep the CLI tool but find a way to force it
  non-interactive, or accept `"unknown"` status for this one optional
  adapter.
- Decision (defense-in-depth, beyond the reported bugs): confirmed by reading
  the whole call chain that `lxd_runner.run_command()`/`exec_in()`/
  `exec_in_retry()` had **no execution timeout anywhere** — any guest command
  could in principle hang forever, not just the one this round fixed.
  `run_command()`, `exec_in()`, and `exec_in_retry()`/`_exec_in_retry_internal()`
  now default to a new `_DEFAULT_GUEST_COMMAND_TIMEOUT_SECONDS = 1800.0` (30
  minutes) — deliberately generous so it never interferes with legitimate
  slow steps (`apt-get install`, `fetch-build` downloads) — with an explicit
  per-call `timeout=` override available for any future caller that
  genuinely needs something different. `run_command()` now catches
  `subprocess.TimeoutExpired` to log a clear message before re-raising it, so
  a timeout reads as an obvious "command timed out after Ns" rather than an
  opaque traceback.

## 2026-08-12 — Reporter feedback round (jitterentropy-library artifact, item 1), Phase 1

- Promotion: no
- Context: user feedback on the same jitterentropy-library reporter artifact
  (`/tmp/mir-jitterentropy-library-20260807-175557/reporter-draft.txt`)
  reported statements like "Security exposure and proportional mitigation
  assessment: Assess security-sensitive behavior, ..." and "Packaging
  complexity and maintainability assessment: Packaging complexity and
  maintainability assessment: Simple" — against the tool's design philosophy
  of confident statements or clearly-marked TODOs, never restated-label
  boilerplate.
- Root cause: `reporter/ai.py::_ask_human()` (the fallback used by every
  `ev_to_ai` item whenever the LLM is unavailable, low-confidence, or an
  adapter is missing) builds the rendered statement via
  `template.replace("TBD", answer, 1)`. Several `ev_to_ai` catalog templates
  are `"<Descriptive label>: TBD"` (a restated title kept for the generated
  doc, see below), so the reporter's own complete sentence gets glued right
  after that label. The AI-confirmed success path
  (`ensure_bulleted(suggestion)`) never had this problem — `_ask_human` was
  the only inconsistent path.
- First attempt (reverted): stripping the label directly from the catalog
  `template` field (making it bare `'TODO: - TBD'`) broke an existing,
  deliberate invariant — `docs/MIR/mir-reporters-template-body.include` is
  **generated** from these exact template strings
  (`render_reporter_template.py`, wired into `docs/Makefile`'s
  `generate-includes` with `--strict`), and
  `test_every_reporter_item_template_is_generated_once` requires every
  item's template line to be **unique** in that human-facing reference doc —
  8 identical bare "TODO: - TBD" lines would be indistinguishable to a human
  reading the static template. The label is legitimate content for the doc
  and for `rule_context` auto-derivation; it just should never be reused to
  build the tool's own rendered statement.
- Actual fix: `_ask_human()` now branches on `question.kind`. For
  `QuestionKind.MULTILINE` (every affected item: `REP-SECURITY-005`,
  `REP-SECURITY-006`, `REP-QA-FUNC-001`, `REP-QA-MAINT-003`,
  `REP-QA-PKG-004`, `REP-QA-TEST-004`, `REP-RATIONALE-003`, `REP-UI-002`),
  the reporter's answer is already expected to be one complete,
  self-contained claim (the same contract the AI prompt already imposes on
  the model) — so it's bulleted directly via `ensure_bulleted(answer.value)`,
  with the catalog template's label never touched. For `QuestionKind.TEXT`
  (only `REP-BG-002`, "Upstream Name is TBD"), the old template-splice
  behavior is kept unchanged — a short fill-in name reads naturally after
  that lead-in and is not a restated label.
- Separately fixed a real, adjacent bug: `REP-RATIONALE-003`'s template
  hardcoded "There is no other/better way already in main; alternatives
  considered: TBD" as a fixed lead-in, which is simply false whenever the
  real conclusion is (b) or (c) from its own `ai_policy` (a named main
  candidate does overlap). Reworded to
  "Alternatives already in main and why they are insufficient, or why none
  exist: TBD" — neutral regardless of which of the three ai_policy outcomes
  applies. This template text only affects the generated doc and
  `rule_context` now (per the fix above), but it was still worth correcting
  since a human could in principle fill this template out by hand without
  the tool.
- Regression tests: `tests/test_reporter_ai.py` gained
  `test_multiline_human_fallback_bullets_answer_without_label_duplication`
  (verified it fails without the fix — reproduces the exact
  "- Assessment: human correction" duplication) and
  `test_text_kind_human_fallback_still_splices_natural_template` (documents
  the intentionally-preserved TEXT-kind behavior). `make test`: 840
  passed/2 skipped (baseline was 838/2, +2 new tests).
- Scope note: `REP-UI-002`'s underlying redesign (splitting UI applicability,
  desktop-file, and translation into separate items, restoring the silently
  dropped translation check) is deferred to a later phase of this same
  feedback round — this phase only fixes the labeling mechanism shared by
  all affected items.

## 2026-08-12 — Reporter feedback round (jitterentropy-library artifact, item 1), Phase 2

- Promotion: no
- Context: continuation of Phase 1 above. The reviewer catalog
  (`catalog-mir-review.yaml` URF-8/URF-9) already lets an `ev_to_ai` check
  declare `options:` (id/predicate/render/outcome, `checks/llm_eval.py`) so
  the model picks exactly one pre-written canonical statement instead of
  writing free prose — no labeling risk, and a clean "not applicable" bucket
  falls out naturally. The reporter role's `ev_to_ai` mode had no equivalent;
  this phase ports it, reusing the reporter's *existing* `QuestionOption`/
  `single_choice` machinery (already used by `human_only` items like
  `REP-QA-MAINT-004`) rather than inventing a parallel schema.
- `reporter/models.py`: `QuestionOption` gained `todo_ref: str = ""` (mirrors
  the reviewer option's `todo_ref`) — threaded through every reconstruction
  site in `reporter/evaluator.py` (`_question_from_item`, `_spell_out_option`
  both branches, `_apply_option_lock`, `_mark_followup_options`) so it can't
  be silently dropped the way `locked_reason`/`list_note` once were (see the
  "Beta feedback round 3" entry's `_mark_followup_options` bug above) — not
  yet consumed anywhere; reserved for Phase 3's "Left to clarify" rendering.
- `reporter/text_utils.py`: extracted `resolve_option_statements(options,
  answer_value, source_package)` out of `evaluator._human_statement` (now a
  thin wrapper around it) so `reporter/ai.py` can reuse the exact same
  option-resolution logic for the `ev_to_ai` fallback without a circular
  import (`evaluator` already imports `ai`).
- `reporter/ai.py::evaluate_ai_item`: when `item["question"]["options"]` is
  set, the LLM prompt gains an `Options:` section (`_render_reporter_options_
  section`, mirrors `checks/llm_eval._render_options_for_prompt`) and the
  JSON contract requires `selected_option`; `_validate_response` resolves it
  against the declared options (raising `LLMError` — falls back to human —
  on an unmatched id) and returns the *option's own* `statement` text as the
  suggestion, never the model's free-form prose. The per-option `readiness`
  override (if declared) now applies to the final `StatementResult`, for
  both the AI-confirmed and human-fallback paths. `StatementResult.
  selected_option` is populated in both paths too, so a later item's
  `applicability` can gate on which option was chosen (needed for Phase 4's
  shared "is this end-user facing" gate) regardless of whether the answer
  came from the model or a human.
- `reporter/ai.py::_ask_human`: gained a third branch for
  `QuestionKind.SINGLE_CHOICE` (previously only MULTILINE vs. everything-
  else-splices-into-template), using the new shared `resolve_option_
  statements` helper — the single_choice fallback UI is built from the exact
  same catalog `options:` the AI prompt used, so the reporter sees the
  identical canonical statements either way.
- **Found and fixed while implementing (not in the original feedback):**
  `_ask_human()` hardcoded `readiness=ReadinessEffect.CLEAR` for every
  fallback answer, ignoring the item's own catalog-declared `readiness`
  (`warning`/`blocker`) entirely — confirmed against the real
  jitterentropy-library artifact's `report.json`: `REP-QA-PKG-004` is
  declared `readiness: warning` and went through the human fallback (no LLM
  credential), yet is absent from `readiness.warnings` in that run's
  `report.json`. `evaluate_ai_item` now threads its already-computed
  `readiness` into every `_ask_human()` call; the single_choice branch
  additionally honors a per-option override the same way `human_only`
  already does (`option_readiness or readiness`).
- Regression tests added to `tests/test_reporter_ai.py` (verified all 5 fail
  on the pre-Phase-2 code, then pass): AI selects and confirms a canonical
  option statement; per-option readiness override on the AI-confirmed path;
  an unmatched `selected_option` id falls back to human instead of crashing
  or silently accepting; the single_choice human fallback uses the same
  canonical statement and readiness; the pre-existing readiness-always-CLEAR
  bug on the plain multiline fallback path. `make test`: 845 passed/2
  skipped (was 840/2 after Phase 1).
- No concrete catalog item uses `options:` on an `ev_to_ai` item yet — this
  phase is purely the reusable mechanism; Phase 4 wires it up for the actual
  UI-standards redesign (REP-UI-001/002/003).

## 2026-08-12 — Reporter feedback round (jitterentropy-library artifact, item 1), Phase 3

- Promotion: no
- Context: continuation of Phases 1-2 above (feedback item 1b): "when the
  reporter mode has aspects it can't sort out, it should be putting those in
  a clear 'Left to clarify:' subsection... whenever possible original
  context in the form of the original RULES and TODO statements should be
  part of the entries", mirroring how the reviewer role already renders its
  "Left to decide:" block (`render/__init__.py::_render_section`).
- Design constraint from the earlier clarification round: "Left to clarify"
  only ever applies to the `ev_to_ai` fallback path; a `human_only` question
  keeps forcing a genuine resolved answer (or an explicit catalog
  `required: false` skip, unchanged). Two triggers land an item there:
  1. **Deterministic evidence unavailable** — already existed as
     `StatementState.UNAVAILABLE` (`evaluator._unavailable`), but
     `_build_draft` previously rendered its `statement` (the item's literal
     `template`, e.g. `"TODO: - It currently builds and works for
     architectures: TBD"`) inline as if it were a real, confident bullet —
     the literal unresolved word "TBD" leaked straight into the draft.
  2. **Reporter-deferred `ev_to_ai` fallback** (new) — previously
     impossible: `ai._ask_human` always forced a real answer for a required
     question (only an EOF/`:cancel` aborting the *entire run* existed as an
     escape). Added an explicit, clearly-labelled `:defer` sentinel:
     `QuestionSpec.deferrable` (only ever set `True` by
     `evaluator._question_from_item(..., deferrable=True)` for the
     `ev_to_ai` dispatch branch, never for `human_only`); `TerminalWizard`
     recognises `:defer` in the single-line/single_choice loop, the
     editor-based multiline flow, and the raw-terminal multiline fallback,
     returning `None` without reopening/looping/aborting. `ai._ask_human`
     now distinguishes *why* it got `None` back: for a `required` question,
     `None` can now only mean an explicit `:defer` (never a legitimate
     optional skip), so it becomes `StatementState.NEEDS_INPUT` with a
     rationale; for a non-required question (e.g. `REP-BG-002`, `required:
     false`), `None` still means a genuine "nothing to add" skip and stays
     `StatementState.NOT_APPLICABLE` exactly as before.
- `reporter/render.py::_build_draft` restructured from flat blueprint-order
  line dumping to per-`[Section]` grouping: confident bullets first (in
  blueprint order, unchanged), then — only if non-empty, mirroring the
  reviewer renderer's "no empty Left to decide" rule — a `Left to clarify:`
  block listing every `NEEDS_INPUT`/`UNAVAILABLE` item in that section.
  Grouping is driven by buffering unresolved results per section and
  flushing right before the next blank-line separator or `[Section]` header
  (defensive on both, though the catalog always uses the blank-line
  convention today) plus once, unconditionally, after the loop for the
  final section. Each entry (`_clarify_entry_lines`) shows: its
  question/title as an intro line, then either every option's own
  `todo_ref` line (for an options-based item, e.g. the UI split coming in
  Phase 4) or the item's own catalog `template` TODO line (for a plain
  free-text item — the closest available original context), then its
  `rationale` as `(Reason: ...)`. A literal "TBD" inside this block is
  expected and fine (it is explicit unresolved-template context, not a fake
  statement); `_lint_draft` gained a check that a raw "TBD" **outside** a
  "Left to clarify:" block is now a hard error, closing exactly the leak
  described in item 2 above.
- No catalog changes in this phase — `REP-UI-002`'s actual redesign (and the
  first real use of the options-based "Left to clarify" rendering with
  multiple `todo_ref` lines) lands in Phase 4.
- New regression tests (verified they fail on the pre-Phase-3 code, then
  pass): `tests/test_reporter_wizard.py` (`:defer` across all three input
  paths, and that it's ordinary literal text when `deferrable=False`),
  `tests/test_reporter_ai.py` (deferred required question ->
  `NEEDS_INPUT`+rationale; optional skip still -> `NOT_APPLICABLE`),
  `tests/test_reporter_render.py` (synthetic-catalog `_build_draft`/
  `_lint_draft` tests: grouping order, per-option `todo_ref` listing, no
  "Left to clarify" when everything is resolved, raw-TBD lint rejection
  outside the block and acceptance inside it). `make test`: 856 passed/2
  skipped (was 845/2 after Phase 2).

## 2026-08-12 — Reporter feedback round (jitterentropy-library artifact, item 1), Phase 4

- Promotion: no
- Context: feedback items 1c/1d. `REP-UI-002` was a single free-text
  `ev_to_ai` item trying to cover both "is this end-user facing" and
  "desktop file/translation exceptions" in one answer; the real artifact
  showed it only ever answered the desktop-file half, and a prior fix
  (2026-08-07) had already deleted its sibling `REP-UI-001` believing the
  two were redundant. The canonical generated template
  (`docs/MIR/mir-reporters-template-body.include`) still has two distinct
  `[UI standards]` TODO lines (general applicability, and an evidence-based
  assessment) — only the second was covered. The reviewer catalog
  (`catalog-mir-review.yaml` URF-8/URF-9) solves the same underlying policy
  cleanly via two independent `ev_to_ai` + `options` items, each re-judging
  "is this end-user facing" on its own.
- Design choice (discussed explicitly per the user's request): rather than
  copying the reviewer's fully-independent URF-8/URF-9 pattern (which asks
  the same "is this end-user facing" judgement twice, risking a
  self-contradicting draft - e.g. "not end-user facing, no desktop file
  needed" alongside "user-visible, ships translations" - if the two
  judgements ever disagreed), the applicability determination is made
  **once** by a new shared gate item and reused by both children via the
  existing `applicability` mechanism:
  - `REP-UI-001` ("End-user UI applicability", `ev_to_ai` + 2 options:
    `end-user-facing` / `not-end-user-facing`) - the single shared judgement,
    reusing Phase 2's options mechanism plus Phase 3's `:defer` fallback for
    free.
  - `REP-UI-002` ("Desktop file applicability", `ev_to_ai` + 2 options:
    `has-desktop-file` / `missing-desktop-file`) - `applicability: {item:
    REP-UI-001, equals: end-user-facing}`, so it is only asked/judged at all
    when relevant.
  - `REP-UI-002-NOT-APPLICABLE` (`deterministic`, new evaluator
    `ui-desktop-not-applicable`) - `applicability: {item: REP-UI-001,
    equals: not-end-user-facing}`, always resolves to a fixed statement
    with zero evidence dependency (the gate already decided everything) -
    this is 1c's requested "not an end-user application... no need for a
    Desktop file" outcome, now a normal visible confident statement rather
    than a hidden/omitted item (an `applicability`-gated item that simply
    isn't applicable is silently dropped from the draft entirely, which
    would have thrown away exactly the statement the user asked to add).
  - `REP-UI-003`/`REP-UI-003-NOT-APPLICABLE` mirror the above for
    translation (`has-translation`/`missing-translation`), restoring the
    silently-dropped translation check from feedback item 1d.
  - Trade-off recorded explicitly: this diverges from the reviewer's
    proven independent-per-item pattern in exchange for consistency
    guarantees and reuse of already-built (Phases 2-3) infrastructure with
    zero new catalog schema. The reviewer catalog's URF-8/URF-9 are left
    untouched (out of scope; the user only asked about the reporter role) -
    a future consistency pass could consider unifying them the same way,
    noted as a possible follow-up, not done here.
- Each `ev_to_ai` option gained a `todo_ref` (Phase 2/3 field, first real
  consumer): `REP-UI-002`'s options carry the user's own pasted TODO-A/B
  wording verbatim; `REP-UI-003`'s carry equivalent TODO-B/C wording — so a
  deferred UI item's "Left to clarify:" block shows the exact original
  alternative phrasing, not a generic placeholder.
- `docs/MIR/mir-reporters-template-body.include` regenerated via
  `render_reporter_template.py --strict` (this file is gitignored/build-only,
  never committed - confirmed via `git check-ignore`) - the `[UI standards]`
  section now shows 5 distinct compact `TODO: - <title>: TBD` placeholder
  lines (one per new item), consistent with every other section's existing
  style, instead of the old single line.
- `tests/test_catalog_roles.py`: item count 54 -> 58 (net +4: -1 old
  `REP-UI-002`, +5 new items); the `rule_context` auto-derivation assertion
  now targets `REP-UI-001` (the new item without a hand-authored
  `rule_context`) instead of the old `REP-UI-002`.
- New end-to-end regression tests in `tests/test_reporter_runtime.py`
  (verified both fail on the pre-Phase-4 catalog, then pass, using the real
  catalog via `catalog.load_catalog_for_role`): the not-end-user-facing gate
  auto-resolves both children without asking either, with the exact 1c
  wording present in the rendered draft; the end-user-facing path resolves
  desktop-file and translation independently (missing-desktop-file +
  has-translation combination proves they are not coupled). Manually
  verified end-to-end (deferred `REP-SECURITY-005` + not-end-user-facing
  gate) that the rendered draft matches the design exactly: confident
  bullets in `[UI standards]`, a `Left to clarify:` block with preserved
  RULE/TODO context and reason in `[Security]`, no `assessment:` labels
  anywhere, no stray `TBD` outside the clarify block. `make test`: 858
  passed/2 skipped (was 856/2 after Phase 3).

## 2026-08-12 — Reporter feedback round (jitterentropy-library artifact, item 1), Phase 5

- Promotion: no
- Context: feedback item 1d asked "are there others which similarly silently
  skipped the whole originally intended checks that also need to be fixed?"
  - a full audit of every `[Section]`'s blueprint `RULE:` line(s) against
  the actual `items:` coverage, looking for the same "assumed redundant,
  actually distinct" failure mode that caused the `REP-UI-001` deletion.
- Method: for each of the 12 sections, every `RULE:` line's individual
  sub-concerns (a RULE line often bundles several, e.g. "X, Y, and Z") were
  checked against every item assigned to that section (question prompt,
  `ai_policy`, and `template` text), looking for a sub-concern with no
  corresponding item at all (not just stylistic/wording gaps).
- **Fixed this round** (small, low-risk, in scope): `REP-QA-TEST-008`
  ("Minimal-library solution-level testing") was `required: false` -
  RULE 4 of `[Quality assurance - testing]` requires a minimal library's
  wider-solution testing to be "identified explicitly", but an optional
  question that's silently skipped when applicable does the opposite. Now
  `required: true` (default) - once `packaging-source.is_library_package`
  triggers its `applicability`, the reporter must answer it. New regression
  test in `tests/test_reporter_runtime.py` asserting this directly against
  the loaded catalog.
- **Found, documented, NOT fixed this round** (genuinely larger in scope -
  each would need new evidence adapters or a new catalog section, not a
  simple reshuffle of existing items/wording):
  1. **No reporter-side static-linking/"Built-Using" coverage at all.** The
     `[Dependencies]` RULE explicitly says "Build-only dependencies may
     remain in universe unless their active code is embedded in final
     binaries" - but `REP-DEP-001` (`_dependencies` evaluator) only ever
     reports `dep-analysis.in_scope_deps_not_in_main` (runtime
     dependencies). Nothing in the reporter catalog asks about embedded/
     statically-linked build-dependencies at all. This is a structural gap,
     not a wording one: the **reviewer** catalog has an entire dedicated
     `[Embedded sources and static linking]` section (ESL-1 through
     ESL-10, with Rust/Golang-specific handling) that the **reporter**
     blueprint has no counterpart section for whatsoever. Recommended
     follow-up: a new reporter section/items surfacing `debian_control`'s
     `Built-Using`/`Static-Built-Using` fields (already collected on the
     guest side for the reviewer role) so the reporter states this
     up-front, rather than a reviewer discovering it later unprompted.
  2. **Security RULE names sources the reporter is never asked to
     consult.** "consult Ubuntu, Debian, NVD/CVE, and OSS-security sources"
     - `REP-SECURITY-001` (`cve-history` evaluator) only queries
     `ubuntu-cve-tracker`/`nvd-enrich`; no reporter item touches Debian's
     security tracker or the OSS-security mailing list archive. Would
     require a genuinely new evidence adapter (Debian security tracker
     and/or oss-security archive lookup), not just a catalog reshuffle.
  3. **Maintenance/Owner RULE 2's full commitment list is only partially
     itemized.** `REP-MAINT-003`'s question asks about "rebuild, update,
     refresh, and security commitments" for vendored code; the RULE also
     explicitly names "testing, tracking, ... and backport" commitments and
     "the full release lifetime, including ESM", plus "new vendored
     components require renewed agreement" (not distinguished from
     already-agreed existing ones). Likely fixable as a wording/question
     expansion on the existing item rather than a new adapter - flagged as
     a smaller, but still separate, follow-up.
  4. **Maintenance/Owner RULE 3 (Rust vendoring path) has no reporter-side
     check.** The RULE specifically calls out that "Rust packages currently
     vendor non-runtime dependencies and use the supported cargo packaging
     path" - the reviewer catalog validates this in its
     `[Embedded sources and static linking]` section; the reporter catalog
     has nothing Rust-specific at all. Related to finding 1 above (same
     missing section).
- **Reviewed, not a gap** (initially flagged by the audit pass, confirmed
  as already adequately covered on closer reading): `[Quality assurance -
  testing]` RULE 3 ("exhaust hardware/partner/simulator/... options before
  declaring untestable") - `REP-QA-TEST-005`'s `single_choice` already
  presents the RULE's full alternative list (including an explicit
  "X-exhausted" option) and forces one definite pick; requiring a written
  essay ruling out every other option individually would add friction
  without a clear benefit. `[Rationale]` RULE 1's "correct understanding of
  main versus universe" - tested indirectly via
  `REP-RATIONALE-001`/`REP-RATIONALE-003`'s existing questions; a dedicated
  standalone item would likely just restate the same ground already
  covered by the main-inclusion rationale.
- Per the user's explicit direction, this audit and its fixes are scoped to
  the **reporter** catalog only; the reviewer catalog's own blueprint-vs-
  items coverage was not re-audited (it already has the richer, more
  mature checks in most of these areas, per the findings above).
- `make test`: 859 passed/2 skipped (was 858/2 after Phase 4).







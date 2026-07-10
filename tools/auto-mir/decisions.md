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
  - Additional wrapper consolidation can proceed incrementally with existing characterization coverage.

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
  - Additional simplification of evaluator pathways can build on shared fallback helper.

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
  - Remaining deterministic checks can be migrated incrementally to helper-based state transitions.

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
  - Remaining direct finding-field mutation in deterministic checks can be reduced in future slices.

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
  - Additional helper migration in evaluator internals can proceed incrementally.

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
  - Remaining direct state mutation in LLM response mapping can be addressed in later slices.

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
  - Remaining `not-ok` option response assignments can migrate in a later bounded slice.

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
  - Remaining non-prompt markdown convergence can proceed from an updated architecture baseline.

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

## Build / Test Decisions

- **CB-1**: combine local sbuild result with Launchpad multi-arch build state via API.
- **CB-2**: inspect `debian/rules` wiring to verify test failure stops build; build log
  alone is often insufficient.
- **CB non-trivial**: deterministic discovery of tests; AI-assisted trivial/non-trivial
  quality assessment; reviewer override.
- **CB-4/5**: special HW exhaustion judgment remains human-only.
- **CB-6**: reverse-dep autopkgtest summary EV→AI; on retrieval failure fall back to
  human-only TODO.
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
- **Tooling bootstrap**: default to latest upstream branch each run for freshness; optional
  `--pin-tooling <commit>` mode for reproducible benchmark/replay runs.
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
  - `cvelist-scan` (container): downloads the documented
    `*_all_CVEs_at_midnight.zip` cvelistV5 baseline *inside the throwaway VM* (keeping the
    bulky corpus off the host) and word-matches every record with a self-contained,
    stdlib-only scanner (`evidence/cvelist_scan_invm.py`, no `unzip` dependency). "Parse a
    lot, identify few": the whole corpus is scanned but only a handful of candidate CVE IDs
    are returned.
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
  shared with ESL-2), with test-context filtering.
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
  - `evidence/container_adapters.py` — in-container adapters (packaging, dependencies, sbuild)
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
  - `retry_container_command()` — for container commands with transient failures
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
  status/severity/confidence enums, AI confidence capped at "medium", and
  `human_confirmation_required` always set.
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

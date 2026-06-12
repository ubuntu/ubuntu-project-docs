# Auto-MIR Decisions Log

Choices and reasoning recorded during development. Grouped by topic.

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

- **SEC-1**: always check both Ubuntu CVE tracker and cve.org; AI risk synthesis required
  with mandatory human confirmation. Concerning patterns (including historically patched but
  risk-significant trends) surface as security-review-triggering findings.
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
- **Autopkgtest**: replaced web UI scraping with direct SQLite database download from
  autopkgtest.ubuntu.com/static/autopkgtest.db. Queries results table directly.

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
- Keep provider-specific defaults when omitted:
  - copilot: `gpt-4.1-mini` (small), `gpt-5.1` (large)
  - openai-compatible: `openai/gpt-4.1-mini` (small), `openai/gpt-5.1` (large)
- Route `ai` checks to large tier, and route `ev_to_ai` checks using lightweight
  complexity thresholds over rendered prompt and serialized evidence size.
- LLM failures on both tiers degrade gracefully to low-confidence manual-review
  fallback output. No hard fail-fast behavior is applied for large-tier errors.

**Consequences:**
- Clearer operator control without flag-precedence conflicts.
- Improved average quality on complex checks while preserving cost control on
  simpler checks.
- Consistent fallback semantics across both tiers reduce operational surprise.

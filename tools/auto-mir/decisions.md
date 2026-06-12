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

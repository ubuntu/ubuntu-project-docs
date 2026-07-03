# Auto-MIR Design

## Scope and Goal

- Build tool to assist MIR review
- Host-orchestrated: but provisions tooling, executes the pipeline in a LXD
  container of the target Ubuntu release for reproducibility.
- Input starts from a Launchpad bug ID to fetch details via the Launchpad API.
- Output is a reviewer-template-aligned draft.
  - TODO statements that can not be resolved stay for the MIR member to resolve.
  - TODO statements that have a low confidence can make suggestions but leave it
    to the MIR member to resolve.
  - Where findings are deterministic or have high confidence results from the AI
    they are answered and their correct review statement grouped either under
    `OK` or `Problems` part in the respective in the section.
- Identified tasks that need to be acted on by the MIR reporter are added to
  make this MIR case acceptable get explained in the respective section
  (reasoning) and referred in the `recommended` or `required` areas of the
  `[Summary]` section
- Policy and the tool needs to be co-developed in this repository so MIR policy
  wording and tool logic/prompts evolve together in the same PR when rules change.

## Guidance boundaries

- `tools/auto-mir/design.md` is the authoritative architecture and workflow
  reference for Auto-MIR.
- `.github/instructions/tools-development.instructions.md` should only contain
  compact, high-frequency contributor rules and command routing.
- Do not duplicate long architecture narratives in instruction files. Link back
  here for detail instead.

## Coding Guidelines (Ruff + Python)

- Run formatting check before committing: `uv tool run ruff format --check .`
- Run linting before committing: `uv tool run ruff check .`
- Keep code Ruff-clean by fixing root causes (do not silence warnings with broad ignores).
- Use spaces for indentation; do not use tab characters for leading indentation.
- Avoid whitespace damage: no trailing spaces, no spaces on empty lines, and keep file endings clean.
- Keep imports sorted and explicit; avoid unused imports and dead code blocks.
- Prefer small, typed helper functions over repeated inline logic.
- Preserve behavior when refactoring: run `make test` after changes.
- Keep error messages actionable and concise, especially for CLI failures.

## Core Workflow Phases

1. Repository bootstrap under `tools/auto-mir`.
2. Normalize checks from the MIR reviewer template into an executable YAML catalog schema.
3. Host-orchestrated LXD lifecycle; container is destroyed after a successful run by default, preserved on failure for debugging. Use `--keep-container` to always preserve, or `--keep-container=false` to always destroy.
4. Launchpad API intake; hard-fail if reporter MIR content is missing.
5. Deterministic evidence collection in-container (sbuild + lintian + API queries and more).
6. AI-assisted synthesis where needed, with mandatory human override on designated checks.
7. Strict template-close rendering: unresolved tasks as `TODO` lines only, no `RULE` leakage.
8. Validation against recent cases in `old-MIRs-as-input` (4 from 2026 + 8 from 2025).
9. Final docs pass to put the user documentation into `tools/auto-mir/README.md`

## LLM Model Tiering

- The runtime now uses a dual-model configuration with separate small and large
  model identifiers:
  - `--llm-model-small` for smaller/simpler LLM requests
  - `--llm-model-large` for larger/more complex LLM requests
- Both flags are optional. OpenAI-compatible defaults apply when omitted:
  - `z-ai/glm-4.7` (small)
  - `z-ai/glm-5.2` (large)
- The legacy single-model flag is removed to avoid precedence conflicts.
- Evaluator routing behavior:
  - `ai` checks use the large tier
  - `ev_to_ai` checks select small vs large by prompt/evidence complexity heuristics
- On LLM unavailability, both tiers degrade gracefully to low-confidence,
  reviewer-actionable fallback findings using existing `llm_unavailable_message`
  template semantics.

## LLM Evidence Reduction and Follow-up Retrieval

- The LLM payload builder now avoids passing Launchpad bug comments for these
  checks, because they are not needed for decision quality:
  - `SUM-6`, `RDO-1`, `SEC-5`, `SEC-6`, `SEC-7`, `CB-4`
- `packaging-source.file_listing` handling:
  - If all listed paths share a leading prefix, that prefix is stripped from
    all paths before sending to the LLM.
  - Reduction only triggers when listing size exceeds 1000 paths.
  - Above threshold, payload includes a summary and first 1000 normalized paths.
- `sbuild.build_log` handling:
  - First pass sends condensed, line-numbered content (head, tail, highlights).
  - The model can ask for up to 3 extra snippets using
    `additional_evidence_requests` in JSON output.
  - Supported follow-up requests: line ranges and regex/pattern matches.
  - Tool performs one follow-up LLM round with requested snippets attached.

## Implementation-Ready Schema Direction

Single file for MVP: `tools/auto-mir/catalog.yaml`. The full field-by-field
schema and a step-by-step "how to add or change a rule and its messages" guide
live in [`CATALOG.md`](CATALOG.md); this section only summarises the shape.

Top-level sections (only fields that runtime code reads are kept; `notes` is the
one documentation-only exception):
- `metadata` — `review_template_blueprint` consumed by the offline doc renderer
- `global_policies` — `confidence_model` shared across checks
- `evidence_adapters[]` — id, type, description, and dependency wiring
- `checks[]` — id, section, title, mode, language_gate, blocker_class,
  synthesis, aggregate_todo, security_trigger, adapters_required,
  adapters_optional, messages, todo_refs, options, ai_policy, notes
- `security_triggers[]` — id, linked checks, and intended cross-cutting actions

### Message Template Source of Truth

- Runtime reviewer-facing finding text is split into two concerns:
  - **catalog declaration**: checks define message templates under
    `checks[].messages` using Python `str.format` placeholders.
  - **evaluator binding**: check code computes evidence-driven values and renders
    those templates into `Finding.message` and `Finding.todo`.
- The renderer stays presentation-only and consumes finalized `Finding` values;
  it does not evaluate check message templates.
- Validation is strict:
  - deterministic migrated checks enforce required template keys/placeholders,
  - `ai`/`ev_to_ai` checks enforce `llm_unavailable_message` with `{error}`,
  - `human_only` checks enforce `human_only_message` and `human_only_todo`
    with `{title}`.
- Evaluators render templates via `checks/messages.py`; missing keys/placeholders
  are validation/runtime errors.

### AI Option Checks (canonical statement selection)

- `ev_to_ai`/`ai` checks may declare mutually-exclusive `options`. Each such
  option (outside the `[Summary]` section) carries a canonical `render`
  statement and an `outcome` (`ok|recommended|required|nack`).
- The model returns a `selected_option` id (or the option's `todo_ref`); the
  evaluator emits that option's `render` statement verbatim at the declared
  `outcome` severity, appending the model's reasoning only in parentheses. This
  keeps the draft template-faithful instead of surfacing free-form model prose.
- Single-statement `ev_to_ai` checks (no options) reuse the canonical statement
  from `todo_refs[0]` for OK findings, unless it is a placeholder (`TBD`/`<…>`)
  or a `[Summary]` decision check.
- `catalog._validate_check_options` enforces `render`+`outcome` on every
  non-Summary `ev_to_ai`/`ai` option. Deterministic option checks render via
  their `messages` map and are exempt.
- Some checks need specific large adapter fields verbatim (e.g. PRF-9 needs the
  whole `debian/rules`); these are declared in
  `checks/llm_eval._FULL_CONTENT_FIELDS_BY_CHECK` and bypass the short-preview
  truncation (bounded by a generous cap).

### Evidence Collection Scope

- `evidence.collect_from_catalog` collects every `adapters_required` referenced
  by the catalog, plus `adapters_optional` on a best-effort basis: an optional
  adapter's failure never fails the run and never counts as a hard adapter
  failure (e.g. `git-ubuntu-delta` enriching PRF-1).
- Check evaluation exposes pass-1 `Finding`s on `ctx.findings` incrementally, so
  a later non-synthesis check can consult an earlier one's verdict (e.g. CB-5
  gates on CB-4).

### Finding Model (per check result)

The `Finding` dataclass in `models.py` represents the result of evaluating a single
check. It includes factory methods for common patterns and enforces invariants via
`__post_init__()`.

**Fields:**
- `check_id`: str — check identifier (e.g., "SUM-1", "DEP-3")
- `status`: "ok" | "not-ok" | "unknown" | "not-applicable"
- `severity`: "ok" | "recommended" | "required" | "nack"
- `confidence`: "low" | "medium" | "high"
- `message`: str — human-readable result description
- `todo`: str — TODO text for unresolved checks (empty if resolved)
- `evidence_refs`: list[str] — references to evidence used
- `adapter_error_cause`: list[str] — adapter IDs that caused unknown status

**Factory Methods:**
- `Finding.ok(check, message, evidence_refs)` — create successful finding
- `Finding.not_ok(check, severity, message, todo, evidence_refs)` — create failed finding
- `Finding.unknown(check, message, todo, adapter_error_cause)` — create unresolved finding

**Invariants (enforced in `__post_init__`):**
- `status="ok"` implies `severity="ok"`
- `status="not-ok"` requires non-empty `todo` field
- All enum fields must contain valid values

**Example Usage:**
```python
from models import Finding

# Successful check
finding = Finding.ok(
    check={"id": "SUM-1", "section": "Summary"},
    message="Source package identified: foo",
    evidence_refs=["lp-bug-api"]
)

# Failed check
finding = Finding.not_ok(
    check={"id": "DEP-1", "section": "Dependencies"},
    severity="required",
    message="Missing runtime dependency",
    todo="TODO: - Add libfoo to Depends",
    evidence_refs=["dep-analysis"]
)

# Unresolved check (adapter failure)
finding = Finding.unknown(
    check={"id": "SEC-1", "section": "Security"},
    message="CVE tracker unavailable",
    todo="TODO: - Manually check CVE database",
    adapter_error_cause=["ubuntu-cve-tracker"]
)
```

## Security Triggers

Security-sensitive checks (SEC-1, SEC-3, SEC-4, SEC-11, SEC-13) carry a
`security_trigger` field in the catalog that links them to entries in the
top-level `security_triggers[]` section of `catalog.yaml`. That catalog
section is the machine-readable source of truth documenting the intended
cross-cutting output actions for when those checks fire: blocking ACK,
emitting structured report fields, and mandating a security review path.

The check evaluators in `checks/deterministic.py` implement the critical hard-blocker
outcomes (webkit/V8) directly. Any future dispatcher that aggregates all
active triggers and acts on the remaining output actions should read from
`security_triggers[]` in the catalog.

## File Layout

```
tools/
  auto-mir/
    design.md          ← this file (conceptual architecture)
    decisions.md       ← choices and reasoning log
    tasks_phase7.md    ← phase task notes
    tasks_phase8.md    ← phase task notes
    tasks_phase9.md    ← phase task notes
    tasks_phase10.md   ← phase task notes
    testing.md         ← how to verify changes before review
    catalog.yaml       ← machine-readable check catalog and security triggers
    catalog_enums.py   ← AdapterID and CheckID enum definitions
    models.py          ← Finding dataclass with factory methods and validation
    auto_mir.py        ← CLI entrypoint and orchestrator
    lp_intake.py       ← Launchpad API intake module
    lxd_runner.py      ← LXD container lifecycle module
    integration_smoke.py ← devel-container isolation smoke runner
    evidence/          ← evidence collection adapters
      __init__.py      ← orchestration and adapter registry
      registry.py      ← decorator registry for evidence adapters
      types.py         ← TypedDict definitions for adapter return types
      host_adapters.py ← host-side adapters (Launchpad, CVE, autopkgtest)
      container_adapters.py ← in-container adapters (packaging, deps, sbuild)
    checks/            ← check evaluation logic
      __init__.py      ← check evaluation orchestration via registered evaluators
      deterministic.py ← deterministic check implementations
      registry.py      ← decorator registry for check evaluators
      llm_eval.py      ← LLM-based check evaluation
      language_gates.py ← language detection (Go, Rust, Python)
    utils/             ← utility modules
      __init__.py      ← package marker
      retry.py         ← tenacity-based retry decorators
    prompts/           ← LLM prompt templates per check section
    render/            ← template renderer and output linter
    tests/             ← test suite
      test_checks.py   ← check evaluation tests
      test_render.py   ← render output tests
      test_evidence.py ← evidence collection integration tests
      test_catalog.py  ← catalog loading and validation tests
      test_lp_intake.py ← Launchpad intake tests
## Relevant Policy Files

- `docs/MIR/mir-reviewers-template.md` — primary reviewer task source and render target
- `docs/MIR/mir-reporters-template.md` — reporter-content structure for intake gate
- `docs/MIR/mir-how-to-use-templates.md` — TODO/RULE semantics and posting workflow
- `docs/MIR/mir-rust.md` — Rust/Go language-specific policy
- `docs/MIR/main-inclusion-review.md` — MIR policy framing
- Debian policy: https://www.debian.org/doc/debian-policy/
- autopkgtest DB: https://autopkgtest.ubuntu.com/static/autopkgtest.db

## Intersphinx / Template Integration

- Template generation is catalog-driven via `metadata.review_template_blueprint` in
  `catalog.yaml`.
- TODO lines in blueprint reference check IDs + `todo_ref` index, so automated check
  text is sourced from `checks[]` instead of duplicated markdown.
- `make -C tools/ render-review-template` regenerates; `check-review-template` verifies.
- Body-only rendering mode was removed in favor of catalog-driven full template generation,
  simplifying the rendering pipeline and Makefile integration.

## Initial Modularization Architecture

The codebase evolved from a flat file structure to a modular package layout to improve
maintainability and testability:

### Package Structure Evolution

**Original flat structure:**
- Single `checks.py` file containing all check evaluators
- Evidence collection logic embedded in main modules
- No clear separation between data models and business logic

**Modular package structure:**
- `checks/` package with specialized modules:
  - `__init__.py` — check dispatcher and evaluation orchestration
  - `deterministic.py` — deterministic check implementations (pure logic, no AI)
  - `llm_eval.py` — LLM-based check evaluation (ev_to_ai, ai modes)
  - `language_gates.py` — language detection (Go, Rust, Python)
- `evidence/` package for evidence collection:
  - `__init__.py` — orchestration and adapter registry
  - `types.py` — TypedDict definitions for adapter contracts
  - `host_adapters.py` — host-side adapters (Launchpad, CVE, autopkgtest)
  - `container_adapters.py` — in-container adapters (packaging, deps, sbuild)
- `models.py` — shared data structures (Finding dataclass with factory methods)
- `utils/` package for cross-cutting concerns:
  - `retry.py` — tenacity-based retry decorators

### Key Architectural Decisions

- **Separation of concerns**: Check evaluation logic separated from evidence collection
  and rendering. Each package has a single responsibility.
- **Deterministic vs AI checks**: Split check evaluators into deterministic (pure logic)
  and LLM-based (AI synthesis) to clarify execution paths and testing strategies.
- **Adapter pattern**: Evidence collection uses adapter pattern with TypedDict contracts,
  making it easy to add new evidence sources without modifying check evaluators.
- **Data model extraction**: Finding dataclass extracted to dedicated module to avoid
  circular dependencies and provide clear data contracts between packages.
- **Prior review detection**: Tool detects existing MIR reviews in Launchpad bugs to
  provide context and avoid duplicating work.
- **Multi-binary-package support**: Gracefully handles source packages that produce
  multiple binary packages, processing and reporting on all binaries.
- **Git as version authority**: Removed embedded version/hash tracking from generated
  output. Git history is authoritative, eliminating redundancy and inconsistencies.

### Testing Strategy

Three-tier testing approach established during initial modularization:

1. **Unit tests** (`test_checks.py`): Test individual check evaluators in isolation
   with mocked evidence data.
2. **Integration tests** (`test_lp_intake.py`): Test Launchpad API intake logic with
   mocked API responses.
3. **End-to-end tests** (`test_render.py`): Validate complete render output against
   expected templates and linting rules.

This testing strategy was later expanded in Phase C with evidence collection integration
tests and catalog validation tests.

## Type Safety and Validation

### TypedDict Contracts

The `evidence/types.py` module defines TypedDict classes for all adapter return types,
providing type safety and IDE autocomplete for adapter contracts:

- `LPBugAPIResult` — Launchpad bug data
- `UbuntuCVETrackerResult` — CVE data from Ubuntu tracker
- `AutopkgtestResult` — autopkgtest database results
- `PackagingSourceResult` — packaging source analysis
- `DepAnalysisResult` — dependency analysis
- `ComponentMismatchesResult` — component mismatch data
- `SbuildResult` — sbuild/lintian results

### Enum Definitions

The `catalog_enums.py` module provides type-safe identifiers:

- `AdapterID` — enum for adapter identifiers (e.g., `AdapterID.LP_BUG_API`)
- `CheckID` — enum for check identifiers (e.g., `CheckID.SUM_1`)

These enums catch typos at development time and provide IDE autocomplete.

### Catalog Validation

The `validate_catalog()` function in `catalog.py` validates catalog structure on load:

- Checks required top-level sections (metadata, global_policies, checks, evidence_adapters)
- Validates check fields (id, section, title, mode)
- Validates adapter fields (id, type, description)
- Checks for duplicate IDs
- Validates adapter references in checks

Validation is integrated into `load_catalog()` to fail fast on schema errors.

## Retry Utilities

The `utils/retry.py` module provides standardized retry decorators using python3-tenacity:

### retry_transient_network()

For network operations that may fail with transient errors:
- Retries on: ConnectionError, TimeoutError, urllib.error.URLError, 5xx HTTP errors
- Default: 4 attempts, exponential backoff (2s base, 30s max)

### retry_rate_limited()

For API calls that may encounter rate limiting:
- Retries on: 429 (rate limit), 5xx HTTP errors
- Default: 4 attempts, exponential backoff (8s base, 60s max)

### retry_container_command()

For container commands that may fail with transient infrastructure issues:
- Retries on: 503 errors, DNS failures, connection timeouts, service unavailable
- Default: 4 attempts, exponential backoff (6s base, 60s max)

**Usage Example:**
```python
from utils.retry import retry_transient_network

@retry_transient_network(max_attempts=3, base_delay=1.0)
def fetch_data(url: str) -> dict:
    # Network operation that may fail transiently
    response = urllib.request.urlopen(url)
    return json.loads(response.read())
```

## Testing Infrastructure

The test suite in `tests/` provides comprehensive coverage:

- `test_checks.py` — unit tests for check evaluation logic
- `test_render.py` — unit tests for render output and snapshot tests
- `test_evidence.py` — integration tests for evidence collection orchestration
- `test_catalog.py` — tests for catalog loading and validation
- `test_lp_intake.py` — tests for Launchpad intake

All tests use pytest and can be run with:
```bash
cd tools/auto-mir
python3 -m pytest tests/ -v
```

## Type Safety and Validation

### TypedDict Contracts

The `evidence/types.py` module defines TypedDict classes for all adapter return types,
providing type safety and IDE autocomplete for adapter contracts:

- `LPBugAPIResult` — Launchpad bug data
- `UbuntuCVETrackerResult` — CVE data from Ubuntu tracker
- `AutopkgtestResult` — autopkgtest database results
- `PackagingSourceResult` — packaging source analysis
- `DepAnalysisResult` — dependency analysis
- `ComponentMismatchesResult` — component mismatch data
- `SbuildResult` — sbuild/lintian results

### Enum Definitions

The `catalog_enums.py` module provides type-safe identifiers:

- `AdapterID` — enum for adapter identifiers (e.g., `AdapterID.LP_BUG_API`)
- `CheckID` — enum for check identifiers (e.g., `CheckID.SUM_1`)

These enums catch typos at development time and provide IDE autocomplete.

### Catalog Validation

The `validate_catalog()` function in `catalog.py` validates catalog structure on load:

- Checks required top-level sections (metadata, global_policies, checks, evidence_adapters)
- Validates check fields (id, section, title, mode)
- Validates adapter fields (id, type, description)
- Checks for duplicate IDs
- Validates adapter references in checks

Validation is integrated into `load_catalog()` to fail fast on schema errors.

## Retry Utilities

The `utils/retry.py` module provides standardized retry decorators using python3-tenacity:

### retry_transient_network()

For network operations that may fail with transient errors:
- Retries on: ConnectionError, TimeoutError, urllib.error.URLError, 5xx HTTP errors
- Default: 4 attempts, exponential backoff (2s base, 30s max)

### retry_rate_limited()

For API calls that may encounter rate limiting:
- Retries on: 429 (rate limit), 5xx HTTP errors
- Default: 4 attempts, exponential backoff (8s base, 60s max)

### retry_container_command()

For container commands that may fail with transient infrastructure issues:
- Retries on: 503 errors, DNS failures, connection timeouts, service unavailable
- Default: 4 attempts, exponential backoff (6s base, 60s max)

**Usage Example:**
```python
from utils.retry import retry_transient_network

@retry_transient_network(max_attempts=3, base_delay=1.0)
def fetch_data(url: str) -> dict:
    # Network operation that may fail transiently
    response = urllib.request.urlopen(url)
    return json.loads(response.read())
```

## Testing Infrastructure

The test suite in `tests/` provides comprehensive coverage:

- `test_checks.py` — unit tests for check evaluation logic
- `test_render.py` — unit tests for render output and snapshot tests
- `test_evidence.py` — integration tests for evidence collection orchestration
- `test_catalog.py` — tests for catalog loading and validation
- `test_lp_intake.py` — tests for Launchpad intake

All tests use pytest and can be run with:
```bash
cd tools/auto-mir
python3 -m pytest tests/ -v
```

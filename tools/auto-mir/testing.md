# Auto-MIR Testing Guide

How agents (and developers) verify changes before requesting human review.

## Quick Reference

All commands run from `tools/auto-mir`.

```bash
# Fast local validation
make lint
make test

# Baseline corpus contract checks
make parity-contract

# Full integration flow (lint + setup + unit + teardown)
make integration
```

## Verification Layers

### Tier 1 — Unit Tests (seconds, offline, automated)

```bash
make test
```

Fast tests exercising the core logic functions without LXD, LP API, or LLM calls:

- `tests/test_lp_intake.py` — reporter and prior-reviewer detection helpers
- `tests/test_checks.py` — per-check evaluator functions with synthetic evidence dicts
- `tests/test_render.py` — draft builder, linter, and binary package header

These must pass on every PR. Zero tolerance for failures.

### Tier 2 — Baseline parity contract gate (steady-state advisory)

```bash
make parity-contract
```

The parity contract now runs in advisory mode and reports baseline drift without
failing the default validation pipeline.

### Tier 3 — Manual Verification Against Real Cases (developer responsibility)

**Required before landing any major feature, check, or output format change.**
Also the standard iteration workflow during development:

```bash
./tools/auto-mir/auto_mir.py <real-LP-bug-id> [--collect-only]
```

Suggested cases from `old-MIRs-as-input/` (covering varied scenarios):

| Case | LP bug | What to check |
|---|---|---|
| `dav1d` | 2133757 | Typical library; clean output structure |
| `ptyxis` | 2108942 | Terminal emulator; [description] |
| [package] | 2138736 | [description] |
| `usbguard` | 1816548 | Security-sensitive; triggers SEC checks |
| `runc` | 1817327 | Go package; language gate active |
| `dh-cargo` | 1993819 | Rust toolchain; Rust language gate |
| `python-boto3` | 2061217 | Python package; multi-binary; dep chain |

For each case, verify:
- Draft renders with no RULE lines and no bare linter errors
- Unresolved items appear as `TODO:` in *Left to decide:* blocks
- High-confidence failures appear in *Problems:* blocks (not as TODOs)
- Summary section lists Required/Recommended TODOs correctly
- Binary package list appears in the preamble header (where data is available)
- Console warns on adapter failures and prior reviews (where applicable)

Use `--keep-guest` to iterate without re-provisioning the LXD guest.

### Tier 3.5 — Deterministic Regression Tests (offline, automated)

```bash
make test
```

Includes `tests/test_artifacts.py` which replays saved test artifacts from real MIR bugs
through the deterministic check evaluators and verifies findings match known-good baselines.

Reporter production contracts are covered separately by:

- `tests/test_catalog_roles.py` — 53-item inventory, adapter/blueprint references,
	option cardinality, and A-H/X coverage;
- `tests/test_reporter_runtime.py` — deterministic/human evaluation, conditional
	questions, selected-option provenance, readiness, and artifacts;
- `tests/test_reporter_ai.py` — confirm/correct behavior and no-LLM fallback;
- `tests/test_reporter_consistency.py` — deterministic invariants and the bounded
	final consistency pass;
- `tests/test_render_reporter_template.py` — strict catalog-driven documentation
	generation and section/item coverage.

**Artifacts are stored in:** `tools/auto-mir/tests/fixtures/<bug_id>/`

Each fixture contains:
- `context.json` — Bug metadata and source package info
- `evidence.json` — Full adapter outputs from evidence collection
- `deterministic_findings.json` — Expected deterministic check results
- `meta.json` — Collection timestamp and git HEAD

**To create or update artifacts (requires LP API + LXD, no LLM tokens needed):**

```bash
./tools/auto-mir/auto_mir.py <bug_id> --collect-only --output-dir tools/auto-mir/tests/fixtures/<bug_id>
```

**Current baseline bugs:**
- `2133757` (dav1d) — Typical library
- `2108942` (ptyxis) — Terminal emulator
- `2138736` ([package]) — [description]

**When to re-baseline:**
- Adding new deterministic adapters
- Changing deterministic check logic
- Updating adapter output format
- When upstream data changes significantly (review diff before committing)

**Review changes before committing:**
```bash
git diff tools/auto-mir/tests/fixtures/
```

### Tier 4 — Integration Smoke Test (optional, requires LXD)

```bash
/usr/bin/python tools/auto-mir/integration_smoke.py
```

Spins up a devel LXD guest, provisions tooling, runs a minimal pipeline
exercise. Validates guest lifecycle and basic adapter connectivity.
Not required for every PR — run when changing LXD runner or evidence adapters.

## Agent Workflow

Before requesting human review, an agent should:

1. Run `make lint` and `make test`
2. Run `make parity-contract`
3. If changes touch evidence adapters or checks: run integration smoke
4. If changes affect output rendering: compare output against a known bug run
5. Record phase-gate outcomes in `decisions.md` using the phase ledger template
6. Report any failures with full error output

## Test Artifact Management

### Creating Initial Artifacts

When setting up the test infrastructure for the first time, or when adding new baseline bugs:

```bash
# Requires: Launchpad API access, LXD, no LLM tokens needed
./tools/auto-mir/auto_mir.py 2133757 --collect-only --output-dir tools/auto-mir/tests/fixtures/2133757
./tools/auto-mir/auto_mir.py 2108942 --collect-only --output-dir tools/auto-mir/tests/fixtures/2108942
./tools/auto-mir/auto_mir.py 2138736 --collect-only --output-dir tools/auto-mir/tests/fixtures/2138736
```

### Re-baselining Artifacts

When deterministic adapters change or upstream data shifts significantly:

```bash
# Re-run for affected bug(s)
./tools/auto-mir/auto_mir.py <bug_id> --collect-only --output-dir tools/auto-mir/tests/fixtures/<bug_id>

# Review the diff carefully before committing
git diff tools/auto-mir/tests/fixtures/<bug_id>/
git add tools/auto-mir/tests/fixtures/<bug_id>/
```

### Verifying Artifacts

The regression tests run automatically as part of `make test`:

```bash
make test
```

Tests will be skipped if no fixtures are present in `tools/auto-mir/tests/fixtures/`.

## Common Failure Modes

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `make lint` fails | New code with lint issues | Fix root cause and re-run `make lint` |
| `make parity-contract` warns | Baseline artifacts missing/incomplete | Refresh fixtures or document accepted advisory drift |
| Unit test failures | Logic regression in checks/render/intake | Fix the root cause; do not weaken tests |
| Artifact regression test failures | Deterministic check logic changed | Re-baseline artifacts if intentional, otherwise fix the regression |
| Smoke test guest fail | LXD not available or image missing | Ensure `lxc` works and the target release (or devel fallback) image is available |
| Token limit errors in LLM checks | Evidence payload too large | Check truncation logic in evidence summarization |

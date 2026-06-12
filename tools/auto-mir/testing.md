# Auto-MIR Testing Guide

How agents (and developers) verify changes before requesting human review.

## Quick Reference

All commands run from the repository root unless noted.

```bash
# Lint + format (fast, run after every change)
make -C tools/ check
make -C tools/ format

# Verify template/catalog consistency
make -C tools/ check-review-template

# Run unit tests (fast, offline, no LXD or LP API)
make -C tools/ test

# Full default target (format + check + render-review-template + test)
make -C tools/
```

## Verification Layers

### Tier 1 — Unit Tests (seconds, offline, automated)

```bash
make -C tools/ test
```

Fast tests exercising the core logic functions without LXD, LP API, or LLM calls:

- `tests/test_lp_intake.py` — reporter and prior-reviewer detection helpers
- `tests/test_checks.py` — per-check evaluator functions with synthetic evidence dicts
- `tests/test_render.py` — draft builder, linter, and binary package header

These must pass on every PR. Zero tolerance for failures.

### Tier 2 — Static Analysis + Template Consistency (seconds, automated)

```bash
make -C tools/ check          # ruff check — linting
make -C tools/ format         # ruff format — formatting
make -C tools/ check-review-template
```

Must pass cleanly. Zero warnings policy.
`check-review-template` ensures `docs/MIR/mir-reviewers-template.md` matches what
the catalog blueprint would generate — fails if catalog and template drift apart.

### Tier 3 — Manual Verification Against Real Cases (developer responsibility)

**Required before landing any major feature, check, or output format change.**
Also the standard iteration workflow during development:

```bash
./tools/auto-mir/auto_mir.py <real-LP-bug-id> [--debug-collect-only]
```

Suggested cases from `old-MIRs-as-input/` (covering varied scenarios):

| Case | LP bug | What to check |
|---|---|---|
| `dav1d` | 2133757 | Typical library; clean output structure |
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

Use `--keep-container` to iterate without re-provisioning the LXD container.

### Tier 4 — Integration Smoke Test (optional, requires LXD)

```bash
/usr/bin/python tools/auto-mir/integration_smoke.py
```

Spins up a devel LXD container, provisions tooling, runs a minimal pipeline
exercise. Validates container lifecycle and basic adapter connectivity.
Not required for every PR — run when changing LXD runner or evidence adapters.

## Agent Workflow

Before requesting human review, an agent should:

1. Run `make -C tools/` (combines format, check, render-review-template, test)
2. If changes touch evidence adapters or checks: run integration smoke
3. If changes affect output rendering: compare output against a known bug run
4. Report any failures with full error output

## Common Failure Modes

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `ruff check` errors | New code with lint issues | Run `make -C tools/ format` then fix remaining |
| Template mismatch | Catalog blueprint changed without regenerating template | Run `make -C tools/ render-review-template` |
| Unit test failures | Logic regression in checks/render/intake | Fix the root cause; do not weaken tests |
| Smoke test container fail | LXD not available or image missing | Ensure `lxc` works and the target release (or devel fallback) image is available |
| Token limit errors in LLM checks | Evidence payload too large | Check truncation logic in evidence summarization |

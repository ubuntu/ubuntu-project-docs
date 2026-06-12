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

# Full default target (format + check + render-review-template + test)
make -C tools/
```

## Verification Layers

### 1. Static Analysis (seconds)

```bash
make -C tools/ check          # ruff check — linting
make -C tools/ format         # ruff format — formatting
```

Must pass cleanly. Zero warnings policy.

### 2. Template Consistency (seconds)

```bash
make -C tools/ check-review-template
```

Ensures `docs/MIR/mir-reviewers-template.md` matches what the catalog blueprint
would generate. Fails if catalog and template drift apart.

### 3. Integration Smoke Test (requires LXD, minutes)

```bash
/usr/bin/python tools/auto-mir/integration_smoke.py
```

Spins up a devel LXD container, provisions tooling, runs a minimal pipeline
exercise. Validates container lifecycle and basic adapter connectivity.

### 4. Real-Bug Integration Run (requires LXD + network, minutes)

```bash
./tools/auto-mir/auto_mir.py 2133757
```

Full end-to-end run against a known LP bug. Produces a reviewer draft.
Use `--keep-container` (default in dev) to iterate without re-provisioning.

### 5. Corpus Validation (Phase 8C target)

Run against recency subset of `old-MIRs-as-input` (4 from 2026 + 8 from 2025).
Verify:
- Template-conformant rendering (no RULE lines, unresolved work as TODO only)
- Representability of `required`, `recommended`, and NACK outcomes
- No silent inference on evidence failure (explicit TODO fallback)

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
| Smoke test container fail | LXD not available or image missing | Ensure `lxc` works and the target release (or devel fallback) image is available |
| Token limit errors in LLM checks | Evidence payload too large | Check truncation logic in evidence summarization |

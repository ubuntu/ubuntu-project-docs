# Phase 8 — Current: Deterministic Coverage + Validation

## Phase 8A — Deterministic Coverage Completion

Implement remaining 18 deterministic check handlers and add them to dispatch.

**Exit criteria**: no deterministic check falls back to "not implemented".

## Phase 8B — Adapter Completion

Implement the 6 missing evidence adapters:
- `cve-org`
- `debian-bts`
- `lintian`
- `lp-bug-search-api`
- `lp-build-api`
- `upstream-tracker`

**Exit criteria**: all catalog adapters present in supported collector map.

## Phase 8C — Corpus Validation

Run against recency cases in `old-MIRs-as-input`.

**Exit criteria**: template-conformant outputs and acceptable review quality.

# Phase 7 + 7b — Completed

## Phase 7: Evidence Adapters Completion (April 2026)

**Status: Complete**

Implemented full set of evidence adapters:
- **Host-side**: lp-bug-api (passthrough), lp-team-membership-api (passthrough),
  lp-package-api (LP API), ubuntu-cve-tracker (OVAL JSON from
  security-metadata.canonical.com), autopkgtest-db (SQLite DB download + query)
- **In-container**: sbuild (lintian source-mode), packaging-source (existing),
  dep-analysis (existing), component-mismatches (existing)
- **Language-gate awareness**: evaluate_checks() now honors language_gate field,
  short-circuits non-applicable language checks to ok/not-applicable status without
  LLM calls.

## Phase 7b: Developer Workflow + Template Single-Source (April 2026)

**Status: Complete**

Completed in this phase:
- Added tools-wide developer workflow targets in `tools/Makefile`:
  - `check` → `uv tool run ruff check`
  - `format` → `uv tool run ruff format`
  - `test` placeholder for upcoming unit tests
  - default target runs `format`, `check`, `render-review-template`, `test`
- Added progress logging improvements:
  - timestamps in HH:MM:SS log format
  - Stage 3 logs current adapter being collected
  - Stage 4 logs current check with ID, title, and mode
- Consolidated output behavior:
  - LLM usage report printed to console
  - review draft kept focused on reviewer content
- Removed hardcoded pricing/cost logic; usage reporting is token/call based.
- Reduced noisy duplicated section lines by de-duplicating repeated OK messages in renderer.
- Enforced source cleanliness with ruff and fixed lint findings across modules.

### Template Generation Milestone
- Implemented `tools/auto-mir/render_review_template.py`.
- Implemented `make -C tools/ render-review-template` and
  `make -C tools/ check-review-template`.
- Generation is now catalog-driven via `metadata.review_template_blueprint` in
  `tools/auto-mir/catalog.yaml`.
- TODO lines in blueprint can reference check IDs + `todo_ref` index, so
  automated check text is sourced from `checks[]` instead of duplicated markdown.
- Verified output identity against `docs/MIR/mir-reviewers-template.md`.

### Completeness Snapshot (end of Phase 7b)
- Deterministic checks declared in catalog: 33
- Deterministic checks dispatched in code: 15
- Remaining deterministic implementations: 18
- Evidence adapters declared in catalog: 15
- Evidence adapters implemented in `evidence/__init__.py`: 9
- Remaining adapters: `cve-org`, `debian-bts`, `lintian`, `lp-bug-search-api`,
  `lp-build-api`, `upstream-tracker`

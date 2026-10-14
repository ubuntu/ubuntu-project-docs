# Render Subsystem

This subsystem converts `Finding` outputs into reviewer-facing artifacts.

## Responsibilities

- build reviewer draft text aligned to MIR section structure,
- classify findings into `OK`, `Problems`, and `Left to decide`,
- aggregate actionable TODOs into summary blocks where policy allows,
- emit machine-readable report output,
- enforce lint-style output consistency checks.

## Key file

- `render/__init__.py`: rendering, classification, summary aggregation, lints.

## Outcome model

Rendering classification follows `finding_outcome_class` semantics:

- `ok`: status is resolved.
- `problem`: non-ok deterministic findings, or non-ok AI findings with high confidence.
- `undecided`: non-ok AI findings with low/medium confidence.

This ensures deterministic/high-confidence failures are rendered as confirmed
problems, while uncertain AI outcomes remain explicit reviewer decisions.

## Output artifacts

- review draft text (reviewer-facing)
- structured JSON report (machine-facing)

## Guardrails

- disallow malformed TODO placement and invalid section content patterns,
- preserve section ordering and summary consistency,
- avoid duplicating undecided AI items into confirmed summary TODO blocks.

## Validation

Run from `tools/auto-mir`:

```bash
make test
```

Focused rendering coverage is in `tests/test_render.py`.

# Checks Subsystem

This subsystem evaluates catalog-defined MIR checks and emits `Finding` objects.

## Responsibilities

- route checks by mode (`deterministic`, `ev_to_ai`, `ai`, `human_only`),
- apply language gates before evaluator execution,
- execute synthesis checks after non-synthesis checks,
- annotate low-confidence/unknown findings with `adapter_error_cause`.

## Key files

- `checks/__init__.py`: orchestration and routing.
- `checks/deterministic.py`: deterministic check implementations.
- `checks/llm_eval.py`: LLM-based evaluators and prompt/evidence shaping.
- `checks/language_gates.py`: Go/Rust/Python applicability heuristics.
- `checks/messages.py`: template rendering for catalog message keys.

## Execution model

1. `evaluate_checks(ctx)` loads checks from `ctx.catalog`.
2. Pass 1 evaluates non-synthesis checks in catalog order.
3. Pass 2 evaluates `synthesis: true` checks with pass-1 findings available.
4. Output list is returned in original catalog order for renderer stability.

## Contracts

- Input context contract is documented by `contracts.ChecksContext`.
- Output contract is `models.Finding`.
- Message text for deterministic checks is catalog-sourced via `messages.py`.

## Guardrails

- AI-derived findings are confidence-capped by evaluator policy.
- Unknown mode degrades to reviewer TODO instead of crashing pipeline.
- Adapter failures are surfaced as explicit causal metadata.

## Validation

Run from `tools/auto-mir`:

```bash
make test
```

Focused checks coverage is in `tests/test_checks.py`.

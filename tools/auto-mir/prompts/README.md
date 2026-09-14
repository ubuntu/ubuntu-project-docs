# Prompts Subsystem

The prompt templates for the LLM calls auto-mir makes, plus the constraints
every one of them obeys.

## Responsibilities

- Shape `ev_to_ai` check evaluation (evidence payload, policy excerpt,
  options, confidence bands) into reviewer-facing findings.
- Propose additional CVE search terms when a package's security history
  lives under predecessor or sibling names.

## Key files

- `ev_to_ai.md`: the shared check-evaluation prompt.
- `cve_predecessor_terms.md`: the CVE search-term prompt.
- Prompt rendering, payload truncation, and answer handling live in
  `checks/llm_eval.py`; the surrounding model is described in
  [design.md](../design.md) ("LLM usage model"). The runtime substitutions
  (`{{check_id}}`, `{{evidence_json}}`, ...) are listed in each template.

## Constraints

- Reviewer-first: suggest findings, never final decisions.
- Evidence-first: cite only provided evidence payload keys.
- Dynamic severity: infer from findings, not from check IDs.
- Ubuntu MIR docs are policy authority over conflicting external guidance.
- All prompts must return JSON only (no markdown wrappers).

## Validation

Run from `tools/auto-mir`:

```bash
make test
```

Focused coverage is in `tests/test_checks.py` and `tests/test_llm.py`.

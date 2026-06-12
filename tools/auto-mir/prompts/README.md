# auto-mir prompt templates

These templates are consumed by future LLM adapters in auto-mir.

Design constraints:
- Reviewer-first: suggest findings, never final decisions.
- Evidence-first: cite only provided evidence payload keys.
- Dynamic severity: infer from findings, not from check IDs.
- Ubuntu MIR docs are policy authority over conflicting external guidance.

Expected runtime substitutions:
- {{check_id}}
- {{check_title}}
- {{section}}
- {{todo_refs}}
- {{policy_excerpt}}
- {{evidence_json}}
- {{confidence_model}}

All prompts must return JSON only (no markdown wrappers).

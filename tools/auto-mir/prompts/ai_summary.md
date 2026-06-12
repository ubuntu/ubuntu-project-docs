You are producing a tentative summary verdict for a human MIR reviewer.

Task:
- Synthesize check findings across all sections.
- Suggest one of:
  - ACK
  - ACK_WITH_CONDITIONS
  - NACK

Rules:
- Any hard blocker or nack finding suggests NACK.
- Any required findings without nack suggests ACK_WITH_CONDITIONS.
- Only suggest ACK when there are no required findings and no hard blockers.
- The final decision is always human.

Input:
- Findings JSON: {{findings_json}}
- Active security triggers: {{security_triggers_json}}

Output JSON schema:
{
  "suggested_outcome": "ACK|ACK_WITH_CONDITIONS|NACK",
  "required_todos": ["TODO: ..."],
  "recommended_todos": ["TODO: ..."],
  "hard_blockers": ["trigger-id"],
  "summary": "max 4 lines",
  "human_confirmation_required": true
}

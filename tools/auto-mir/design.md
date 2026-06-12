# Auto-MIR Design

## Scope and Goal

- Build tool to assist MIR review
- Host-orchestrated: but provisions tooling, executes the pipeline in a LXD
  container of the target Ubuntu release for reproducibility.
- Input starts from a Launchpad bug ID to fetch details via the Launchpad API.
- Output is a reviewer-template-aligned draft.
  - TODO statements that can not be resolved stay for the MIR member to resolve.
  - TODO statements that have a low confidence can make suggestions but leave it
    to the MIR member to resolve.
  - Where findings are deterministic or have high confidence results from the AI
    they are answered and their correct review statement grouped either under
    `OK` or `Problems` part in the respective in the section.
- Identified tasks that need to be acted on by the MIR reporter are added to
  make this MIR case acceptable get explained in the respective section
  (reasoning) and referred in the `recommended` or `required` areas of the
  `[Summary]` section
- Policy and the tool needs to be co-developed in this repository so MIR policy
  wording and tool logic/prompts evolve together in the same PR when rules change.

## Core Workflow Phases

1. Repository bootstrap under `tools/auto-mir`.
2. Normalize checks from the MIR reviewer template into an executable YAML catalog schema.
3. Host-orchestrated LXD lifecycle; container is destroyed after the run by default. Use `--keep-container` to preserve it for debugging.
4. Launchpad API intake; hard-fail if reporter MIR content is missing.
5. Deterministic evidence collection in-container (sbuild + lintian + API queries and more).
6. AI-assisted synthesis where needed, with mandatory human override on designated checks.
7. Strict template-close rendering: unresolved tasks as `TODO` lines only, no `RULE` leakage.
8. Validation against recent cases in `old-MIRs-as-input` (4 from 2026 + 8 from 2025).
9. Final docs pass to put the user documentation into `tools/auto-mir/README.md`

## Implementation-Ready Schema Direction

Single file for MVP: `tools/auto-mir/catalog.yaml`.

Top-level sections:
- `metadata` — schema version, policy file refs and hashes, target series, generator info
- `global_policies` — severity model, confidence model, ACK-block rules, NACK rules
- `tooling_bootstrap` — mode default/override, upstream sources, required tools
- `evidence_adapters[]` — id, type, description, inputs, output_contract, retry_policy
- `checks[]` — id, section, title, todo_refs, options[], mode, language_gate,
  adapters_required, adapters_optional, ai_policy, human_override, fallback,
  blocker_class, mapping_rules, render_rules
- `security_triggers[]` — id, linked_checks, trigger_condition, synthesis,
  human_confirmation_required, action, output_flags
- `render_policy` — template_mode, allow_rationale_append, forbidden_line_prefixes,
  todo_prefix_rule
- `fallback_policy` — on_adapter_error, on_missing_optional_data,
  on_missing_required_data

### Finding Model (per check result)

- `status`: pass | fail | unknown | not-applicable
- `severity`: ok | recommended | required | nack
- `confidence`: low | medium | high
- `evidence_refs[]`
- `rationale`
- `reviewer_action`
- `todo_output_line`
- `blocks_ack`: bool

## Security Triggers

Security-sensitive checks (SEC-1, SEC-3, SEC-4, SEC-11, SEC-13) carry a
`security_trigger` field in the catalog that links them to entries in the
top-level `security_triggers[]` section of `catalog.yaml`. That catalog
section is the machine-readable source of truth documenting the intended
cross-cutting output actions for when those checks fire: blocking ACK,
emitting structured report fields, and mandating a security review path.

The check evaluators in `checks.py` implement the critical hard-blocker
outcomes (webkit/V8) directly. Any future dispatcher that aggregates all
active triggers and acts on the remaining output actions should read from
`security_triggers[]` in the catalog.

## File Layout

```
tools/
  auto-mir/
    design.md          ← this file (conceptual architecture)
    decisions.md       ← choices and reasoning log
    tasks_phase7.md    ← completed: adapters + template generation
    tasks_phase8.md    ← current: deterministic coverage + validation
    tasks_phase9.md    ← next: hardening + CI gates
    tasks_phase10.md   ← final: docs closure
    testing.md         ← how to verify changes before review
    catalog.yaml       ← machine-readable check catalog and security triggers
    auto_mir.py        ← CLI entrypoint and orchestrator
    lp_intake.py       ← Launchpad API intake module
    lxd_runner.py      ← LXD container lifecycle module
    integration_smoke.py ← devel-container isolation smoke runner
    evidence/          ← in-container evidence collection scripts
    prompts/           ← LLM prompt templates per check section
    render/            ← template renderer and output linter
```

## Relevant Policy Files

- `docs/MIR/mir-reviewers-template.md` — primary reviewer task source and render target
- `docs/MIR/mir-reporters-template.md` — reporter-content structure for intake gate
- `docs/MIR/mir-how-to-use-templates.md` — TODO/RULE semantics and posting workflow
- `docs/MIR/mir-rust.md` — Rust/Go language-specific policy
- `docs/MIR/main-inclusion-review.md` — MIR policy framing
- Debian policy: https://www.debian.org/doc/debian-policy/
- autopkgtest DB: https://autopkgtest.ubuntu.com/static/autopkgtest.db

## Intersphinx / Template Integration

- Template generation is catalog-driven via `metadata.review_template_blueprint` in
  `catalog.yaml`.
- TODO lines in blueprint reference check IDs + `todo_ref` index, so automated check
  text is sourced from `checks[]` instead of duplicated markdown.
- `make -C tools/ render-review-template` regenerates; `check-review-template` verifies.

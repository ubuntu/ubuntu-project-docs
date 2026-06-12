# Auto-MIR Plan Checkpoint (Pre-Implementation)

This file is the authoritative planning checkpoint. If a session dies or implementation
needs to restart, load this file and continue from the decisions recorded here.

## Scope and Goal

- Build a reviewer-first MIR assistant.
- Host-orchestrated: tool runs outside, spawns a fresh LXD container from Ubuntu devel
  image aliases, provisions tooling, executes the pipeline in-container.
- Input starts from a Launchpad bug ID via the Launchpad API.
- Output is a reviewer-template-aligned draft where findings dynamically determine severity
  (`ok`, `recommended`, `required`) rather than having severity pre-assigned to TODO lines.
- Policy/tool co-development in this repository under `tools/auto-mir` so MIR wording and
  tool logic/prompts evolve together in the same PR when rules change.

## Core Workflow Phases

1. Repository bootstrap under `tools/auto-mir`.
2. Normalize checks from the MIR reviewer template into an executable YAML catalog schema.
3. Host-orchestrated LXD lifecycle with `--keep-container` default during development.
4. Launchpad API intake; hard-fail if reporter MIR content is missing.
5. Deterministic evidence collection in-container (sbuild + lintian + API queries).
6. AI-assisted synthesis where needed, with mandatory human override on designated checks.
7. Strict template-close rendering: unresolved tasks as `TODO` lines only, no `RULE` leakage.
8. Validation against recent corpus in `old-MIRs-as-input` (4 from 2026 + 8 from 2025).

## Locked Traceability Decisions

- **SUM-3**: use upstream `ubuntu-archive-tools/component-mismatches` logic by fetching and
  running the original tooling (with prerequisites like germinate); avoid local
  reimplementation and avoid HTML parsing as primary logic. Fallback to reviewer TODO.
- **SUM-4**: missing team bug subscriber → emit recommendation that mentions promotion will
  stall later and the subscriber should be added now.
- **DEP-1**: do not rely on outdated `check-mir`; use runtime dependency extraction
  (`dpkg-query` preferred, `apt show` fallback) and component resolution via `apt policy`
  in the target release. Runtime deps are primary; build deps only matter for
  languages/headers that embed active code in final binaries.
- **DEP-3**: `-dev/-debug/-doc` extra excludes are recommendation-level only; hard blocker
  only if broader policy conditions are also triggered.
- **DEP-4**: deterministic test evidence collection + EV→AI interpretation + HUM final
  override. Use `autopkgtest.db` and web results. Weight by importance, not per-dep
  strictness.
- **ESL-2**: include `-static` build-log/invocation checks for static-linking detection.
- **ESL-5/6/8/9/10**: evaluate only when language gates indicate applicability.
- **Go/Rust conflicts**: MIR docs in this repo are authoritative over conflicting Debian
  guidance; results often become recommendations/dialogue rather than hard requirements.
- **SEC-1**: always check both Ubuntu CVE tracker and cve.org; AI risk synthesis required
  with mandatory human confirmation. Concerning patterns (including historically patched but
  risk-significant trends) surface as security-review-triggering findings.
- **SEC-3/SEC-4**: hard blockers (required remediation), not merely "security review maybe".
- **SEC-7**: include docs/manpage/package-description evidence in arbitrary web-content
  assessment.
- **SEC-11**: secure-boot/signature/attestation always implies security review path; no
  recommended-only middle state.
- **SEC-13**: EV→AI mitigation analysis with HUM final judgment.
- **CB-1**: combine local sbuild result with Launchpad multi-arch build state via API.
- **CB-2**: inspect `debian/rules` wiring to verify test failure stops build; build log
  alone is often insufficient.
- **CB non-trivial**: deterministic discovery of tests; AI-assisted trivial/non-trivial
  quality assessment; reviewer override.
- **CB-4/5**: special HW exhaustion judgment remains human-only.
- **CB-6**: reverse-dep autopkgtest summary EV→AI; on retrieval failure fall back to
  human-only TODO.
- **CB-7**: python2 dependency is a hard blocker.
- **PRF-1**: escalate to required/NACK only when large unjustified delta also has no
  minimization activity in progress.
- **PRF-2**: symbols applicability must support N/A variants and TODO option pruning;
  language-aware.
- **PRF-5/6**: intentional stable cadence can still resolve to `ok` (explanatory statement);
  dead/unmaintained trajectory can reach NACK-level.
- **URF-6**: aggregate Launchpad package bugspace (`bugs.launchpad.net/ubuntu/+source/PKG`)
  via API + Debian BTS + upstream issue evidence.
- **PRF-8**: Launchpad upload history + MOTU/team context as EV→AI suggested rating, HUM
  final call.
- **RDO-3**: AI drafts tentative verdict suggestion with explicit HUM override flag.

## Executable Catalog Decisions

- **Format**: YAML.
- **Granularity**: one entry per reviewer TODO line (max traceability), with logical check
  option lists for TODO-A/B/C variants inside one logical check.
- **Fallback on evidence failure**: emit explicit reviewer TODO and continue partial report;
  no silent inference.
- **Security trigger output**: dedicated structured field + templated summary line in output.
- **SEC-1 confidence scale**: 3-band — `low`, `medium`, `high`.
- **Hard blockers**: always emit required TODO and block ACK suggestion.
- **Policy snapshot metadata**: include MIR policy/template file hashes in report metadata.
- **Tooling bootstrap**: default to latest upstream branch each run for freshness; optional
  `--pin-tooling <commit>` mode for reproducible benchmark/replay runs.
- **Traceability IDs**: semantic TODO identifiers are primary; optional line-number metadata
  is supplemental only (stable across template edits).

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

Finding model per check result:
- `status`: pass | fail | unknown | not-applicable
- `severity`: ok | recommended | required | nack
- `confidence`: low | medium | high
- `evidence_refs[]`
- `rationale`
- `reviewer_action`
- `todo_output_line`
- `blocks_ack`: bool

## Security Trigger Table (MVP)

| ID | Source checks | Condition | Synthesis | Human confirmation | Action |
|----|--------------|-----------|-----------|-------------------|--------|
| SEC-1-CVE-SYNTH | SEC-1 | CVE history present from either tracker | AI risk synthesis across both trackers | Required | Structured field + summary line; may trigger security review |
| SEC-3-WEBKIT | SEC-3 | webkit1 or webkit2 in runtime deps | Deterministic | N/A | Required hard blocker; block ACK |
| SEC-4-V8 | SEC-4 | libv8 direct use in runtime deps | Deterministic | N/A | Required hard blocker; block ACK |
| SEC-11-ATTESTATION | SEC-11 | secure boot/signature/TPM involvement | Deterministic/evidence | N/A | Mandatory security review path |
| SEC-13-MITIGATION-GAPS | SEC-13 | Exposure-level mitigations absent | EV→AI synthesis | Required | Reviewer decides severity; can escalate |

## Validation Basis

- Primary corpus: `old-MIRs-as-input` — use recency subset (4 from 2026 + 8 from 2025).
- Verify representability of `required`, `recommended`, and NACK outcomes.
- Verify template-conformant rendering (no RULE lines, unresolved work as TODO only).
- Validate isolation path first via smoke run before adding larger check batches:
  `/usr/bin/python tools/auto-mir/integration_smoke.py`

## Relevant Policy Files

- `docs/MIR/mir-reviewers-template.md` — primary reviewer task source and render target
- `docs/MIR/mir-reporters-template.md` — reporter-content structure for intake gate
- `docs/MIR/mir-how-to-use-templates.md` — TODO/RULE semantics and posting workflow
- `docs/MIR/mir-rust.md` — Rust/Go language-specific policy
- `docs/MIR/main-inclusion-review.md` — MIR policy framing
- Debian policy: https://www.debian.org/doc/debian-policy/
- autopkgtest DB: https://autopkgtest.ubuntu.com/static/autopkgtest.db

## File Layout

```
tools/
  auto-mir/
    plan.md          ← this file (restart anchor)
    catalog.yaml     ← machine-readable check catalog and security triggers
    auto_mir.py      ← CLI entrypoint and orchestrator
    lp_intake.py     ← Launchpad API intake module
    lxd_runner.py    ← LXD container lifecycle module
    integration_smoke.py ← devel-container isolation smoke runner
    evidence/        ← in-container evidence collection scripts
    prompts/         ← LLM prompt templates per check section
    render/          ← template renderer and output linter
```

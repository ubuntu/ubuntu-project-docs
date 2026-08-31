# Auto-MIR Catalog Reference (`catalog.yaml` / `catalog-mir-review.yaml`)

The catalog is the single, human-auditable source of truth for the automated
MIR review, split across two files by ownership:

- `catalog.yaml` — sections shared by both reviewer and reporter mode:
  `global_policies` (confidence model) and `evidence_adapters` (data
  collection interfaces). Keep it small: only add a section here if it is
  genuinely shared by both roles.
- `catalog-mir-review.yaml` — everything reviewer-only: `metadata`
  (reviewer-template blueprint), `checks` (every check definition and —
  crucially — **all reviewer-facing text every check can emit**),
  `security_triggers`, `render_policy`, `fallback_policy`. Evaluator code in
  `checks/` contains only logic; it never contains reviewer-draft wording.
- `catalog-mir-report.yaml` — the reporter-only counterpart: `metadata`
  (reporter-template blueprint) and `items` (reporter questions, readiness
  effects, terminal templates).

If you want to change *what the tool says*, you change the catalog. If you want to
change *how the tool decides*, you change the evaluator. This separation is
enforced by a test (see [Message single-sourcing](#message-single-sourcing)).

`catalog.load_catalog_for_role(tool_root, workspace_root, role)` composes the
runtime view for `"review"` or `"report"`: it loads `catalog.yaml`'s shared
sections plus the role's own file, and rejects either side overriding the
other. Both role files declare their own `role:` marker and are validated as a
composed whole. Direct `load_catalog(path, workspace_root)` remains available
for loading an ad-hoc, standalone, fully self-contained catalog file (used by
some tests and `render_review_template.py --catalog <path>` overrides).

---

## Top-level structure

```yaml
# catalog.yaml (shared)
global_policies:     # confidence_model shared across checks
evidence_adapters:   # data-collection interfaces (APIs, tools, scripts)

# catalog-mir-review.yaml (reviewer-only)
metadata:            # review_template_blueprint for the offline doc renderer
checks:              # the check definitions (grouped by section, with banners)
security_triggers:   # cross-cutting security actions linked from SEC-* checks
render_policy:       # reviewer draft rendering conventions
fallback_policy:     # behavior when evidence collection fails
```

Only fields that runtime code actually reads (plus `notes`, kept as human
documentation) live in the file. Nothing is declared "for future use".

| Section | File | Read by | Purpose |
| --- | --- | --- | --- |
| `metadata.review_template_blueprint` | catalog-mir-review.yaml | `render_review_template.py` | Regenerates the human reviewer template (`docs/MIR/`). Offline only. |
| `global_policies.confidence_model.description` | catalog.yaml | `checks/llm_eval.py` | Injected into AI prompts. |
| `evidence_adapters[]` | catalog.yaml | `catalog.py`, contributors | Adapter id/type/description documentation and reference validation. Runtime dependency wiring currently lives with `@adapter` registrations. |
| `checks[]` | catalog-mir-review.yaml | `checks/` | Check definitions (see below). |
| `security_triggers[]` | catalog-mir-review.yaml | `catalog.py` (count), future dispatcher | Documents intended actions when a `security_trigger` fires. |

---

## Check schema

Every check is a mapping under `checks:`. Fields appear in one **canonical
order** (enforced by hand; keep new checks consistent):

```yaml
- id: SUM-1                    # required — unique check id
  section: Summary             # required — section name (drives banners + grouping)
  title: Source package identified   # required — short human title
  mode: deterministic          # required — deterministic | ev_to_ai | ai | human_only
  language_gate: python        # optional — only run for go/rust/python packages
  blocker_class: hard          # optional — hard | soft | none
  synthesis: true              # optional — aggregate across other findings (ai mode)
  aggregate_todo: true         # optional — surface TODO in a consolidated block
  security_trigger: SEC-3-WEBKIT     # optional — links to security_triggers[]
  adapters_required:           # optional — adapters that must succeed
  - lp-bug-api
  adapters_optional:           # optional — adapters used if available
  - lp-package-api
  messages:                    # see "Messages" — all reviewer text lives here
    ok_message: 'Review for Source Package: {source_package}'
    not_ok_message: Source package could not be determined
    not_ok_todo: 'TODO: Clarify which source package this review is for'
  todo_refs:                   # canonical TODO lines used by the doc renderer
  - 'TODO: Review for Source Package: TBDSRC'
  negated_statement: does FTBFS currently   # optional — problem phrasing (see below)
  options:                     # Summary-only: enumerated reviewer decision options
  - id: SUM-5-A
    todo_ref: 'TODO-A: MIR team ACK'
    predicate: no required findings and no hard blockers
  ai_policy: none              # ev_to_ai/ai: per-check policy excerpt for the prompt
  notes: free-form implementation hint (documentation only)
```

**Required for every check:** `id`, `section`, `title`, `mode`.

**Notes on individual fields**

- `options` is consumed at runtime only as a presence flag for `Summary` checks
  (`checks/llm_eval.py`); its inner fields (`id`/`predicate`/`render`/`todo_ref`)
  are human documentation of the decision options. Keep the list non-empty.
- `negated_statement` is the reviewer phrasing used when a one-dimensional check
  becomes a confirmed **problem**. Most template statements are written to pass
  ("does not FTBFS currently"); when the check fails, the renderer needs the
  inverted statement ("does FTBFS currently") for the Problems section and the
  Summary TODO. It is stored explicitly (never rewritten on the fly) and
  validated to be a non-empty string. Only add it to single-statement checks
  that can fail; option checks (TODO-A/B/...) do not need it because the reviewer
  selects the applicable option instead.
- `ai_policy` is the per-check text spliced into the shared AI prompt
  (`prompts/ev_to_ai.md`) as `{{policy_excerpt}}`. Use `none` for deterministic
  checks.
- `notes` is never read by code; use it for short implementation hints.

---

## Message single-sourcing

All reviewer-facing text a check can produce is declared under
`checks[].messages`, using Python `str.format` placeholders. Evaluators render
them with `render_check_message(check, key, **values)` from
[`checks/messages.py`](checks/messages.py):

```python
finding.fail(
    render_check_message(check, "blocker_message", dep=dep),
    render_check_message(check, "blocker_todo"),
    severity="required",
)
```

Three rules keep this honest:

1. **No literals in evaluators.** A deterministic `_check_*` function must never
   pass a string literal or f-string as the `message`/`todo` argument of
   `finding.succeed()`/`finding.fail()`, nor assign one to `finding.message`/
   `finding.todo`. Dynamic detail is passed as a placeholder value
   (e.g. `{dep}`, `{count}`, `{source}`). This is enforced by
   [`tests/test_message_sourcing.py`](tests/test_message_sourcing.py).
2. **Every outcome is in the catalog.** The `messages` map lists *all* outcomes
   the evaluator can emit (each unknown/ok/not-ok variant), so a reviewer can
   read every possible draft without reading Python.
3. **Strict placeholder validation.** Checks listed in
   `_REQUIRED_MESSAGE_TEMPLATES` (`catalog.py`) must define the named template
   keys, and each template must contain its required placeholders. Mode-based
   templates are also enforced: `ev_to_ai`/`ai` need `llm_unavailable_message`
   with `{error}`; `human_only` needs `human_only_message` and `human_only_todo`
   with `{title}`. Validation runs on every catalog load (`validate_catalog`).

AI (`ev_to_ai`/`ai`) checks keep their runtime, LLM-generated message and only
declare `llm_unavailable_message` plus their `todo_refs`/`options`; the
single-sourcing rule above applies to deterministic checks.

---

## Check modes

| Mode | Evaluator | Reviewer text |
| --- | --- | --- |
| `deterministic` | `checks/deterministic.py` | Fully from `messages` (no LLM). |
| `ev_to_ai` | `checks/llm_eval.py` | LLM draft from evidence; `ai_policy` shapes the prompt; every outcome requires human confirmation. |
| `ai` | `checks/llm_eval.py` | LLM synthesis across findings (`synthesis: true`). |
| `human_only` | — | Reviewer fills in; requires `human_only_message`/`human_only_todo`. |

---

## How to add or modify a deterministic check

1. **Declare the check** in `catalog-mir-review.yaml` under the right `section:`
   (keep the canonical field order; place it within the section's banner block).
2. **Declare every outcome** under `messages:` — one key per draft the evaluator
   can emit. Put dynamic detail in `{placeholders}`. Example:
   ```yaml
   messages:
     unknown_message: Could not inspect packaging source
     unknown_todo: 'TODO: - Manually verify ...'
     not_ok_message: 'Offending dependency found: {dep}'
     not_ok_todo: 'TODO: - remove {dep}'
     ok_message: dependency policy satisfied
   ```
3. **Add strict validation** (recommended) in `_REQUIRED_MESSAGE_TEMPLATES`
   (`catalog.py`): list the template keys and the placeholders each must contain.
4. **Write the evaluator** in `checks/deterministic.py`, registering it with
   `@deterministic_check("ID")`. Render every outcome:
   ```python
   @deterministic_check("XYZ-1")
   def _check_xyz_1(ctx, finding):
       check = _get_check_definition(ctx, "XYZ-1")
       adapters = ctx.evidence.get("adapters", {})
       data = adapters.get("dep-analysis", {})
       if data.get("status") != "ok":
           return _set_unknown_from_adapter(
               finding,
               check,
               todo_key="unknown_todo",
               evidence_refs=["dep-analysis:error"],
           )
       if offending:
           finding.fail(
               render_check_message(check, "not_ok_message", dep=offending),
               render_check_message(check, "not_ok_todo", dep=offending),
               severity="required",
           )
           return finding
       finding.succeed(render_check_message(check, "ok_message"))
       return finding
   ```
5. **Add a unit test** in `tests/test_checks.py`. The test harness builds a
   small catalog fixture inline — add your check's `messages` there too, then
   assert on `status`/`severity`/`confidence` and a message substring.
6. **Run `make test`.** The message-sourcing guard, placeholder validation, and
   your unit test all run.

**To change wording only:** edit the value in `catalog-mir-review.yaml`
`messages` (and the matching fixture in `tests/test_checks.py`). No evaluator
change is needed — that is the whole point of the design.

---

## The reviewer-template blueprint

`metadata.review_template_blueprint` plus each check's `todo_refs` drive
`render_review_template.py`, which regenerates the human reviewer template under
`docs/MIR/`. This is an **offline documentation tool**, not part of a review run.
Supported documentation builds regenerate the ignored
`mir-reviewers-template-body.include` file automatically. Do not edit or commit
the generated include; edit the blueprint or referenced `todo_refs` and run
`make -C docs generate-includes` to inspect the result locally.

---

## Reporter item `rule_context` (auto-derived from the blueprint)

`catalog-mir-report.yaml`'s `metadata.reporter_template_blueprint` interleaves
`'[Section]'` markers, `'RULE: ...'` policy lines, and `item: REP-XXX` entries
in the exact order the rendered template uses — RULE lines always appear
directly after a section marker and before that section's first item. This is
already the single source of truth for which policy rule(s) apply to which
items, so `catalog.load_catalog_for_role(..., "report")` auto-populates each
`human_only`/`ev_to_ai` item's `rule_context` (shown to the reporter as a
"Context:" block ahead of the question) from its section's RULE line(s) plus
its own `template` (the `TODO: ...` placeholder it resolves) — **do not**
hand-author `rule_context` for a new item; it is derived automatically.

A `rule_context` only needs to be hand-authored on an item when a section has
multiple RULE lines and one specific item needs *only* a subset of them (9
items do this today, e.g. `REP-MAINT-001`). A hand-authored `rule_context`
must stay a **verbatim copy** of one or more of its section's blueprint RULE
lines — `catalog.validate_report_catalog()` rejects any `rule_context` line
starting with `RULE:` that doesn't exactly match a RULE line from its own
section's blueprint entries, to prevent it drifting from the blueprint prose
over time. Hand-authored items do not get the item's own `template` line
appended automatically (unlike the auto-derived ones); add it explicitly if
wanted.

---

## Validation and tests

- `catalog.py:validate_catalog()` runs on every load: structure, modes,
  adapter references, and message templates/placeholders.
- `tests/test_catalog.py` covers catalog validation.
- `tests/test_message_sourcing.py` enforces the no-literals rule.
- `tests/test_checks.py` covers evaluator behaviour.

Run everything with `make test` from `tools/auto-mir`.

---

## Catalog stability guardrails

Catalog changes should keep these stability rules:

1. Keep check ids stable. Moving evaluator code is acceptable; renaming ids is
   not, unless explicitly planned with migration notes.
2. Preserve section ordering semantics so renderer grouping stays stable.
3. Keep `messages` complete for deterministic checks; do not move reviewer text
   back into Python logic.
4. If adapter dependencies change, update both `adapters_required`/
   `adapters_optional`, the adapter's `@adapter(..., depends_on=...)`
   registration, and corresponding tests in `tests/test_catalog.py`,
   `tests/test_evidence.py`, and `tests/test_checks.py`. The decorator graph is
   the current runtime authority; keeping the catalog description aligned is a
   required maintenance step until dependency ownership is consolidated.
5. Validate from `tools/auto-mir` with:

```bash
make lint
make test
```

## Reviewer draft rendering conventions and evidence-failure behavior

These conventions were previously declared (but never read) as the
`render_policy` and `fallback_policy` sections of `catalog-mir-review.yaml`;
they are prose conventions, implemented directly in `render/` and the
evidence/checks code:

- Template-close wording; the AI may append up to two sentences of rationale.
- Unresolved reviewer actions begin with `TODO:`; resolved statements do not.
- No `RULE:` lines survive into a rendered draft; an output linter validates
  conformance before anything is written.
- For mutually exclusive TODO-A/B/C/D variants, emit only the single most
  applicable option and remove the others.

Evidence-failure behavior:

- When a deterministic evidence adapter fails, the check emits an explicit
  reviewer TODO naming the evidence gap, marks the finding unknown with low
  confidence, includes the retrieval failure reason, and continues the run.
  Nothing is silently inferred from missing data.
- Optional adapters that fail are noted in report metadata but do not block
  the run or affect other checks' severity.
- Required data that cannot be collected leaves that check's finding
  unknown/low-confidence with an explicit reviewer TODO. The run continues
  unless the missing data is the reporter MIR content for a fresh review
  (a hard stop); re-review/reorg fast-paths proceed without a template.

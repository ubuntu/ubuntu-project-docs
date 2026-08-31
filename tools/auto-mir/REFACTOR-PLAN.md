# auto-mir Refactor Plan (temporary file — deleted in Commit F)

Audit-driven over-engineering removal. 33 commits: P0 (this plan) + B1
(stabilize generated content) + 31 audit findings + F (wrap-up).
Each commit: `make test` green before commit. All commits land on
`auto-mir-review`.

Commit message format: `refactor(auto-mir): <N> <what>` with body explaining
why the change is safe (caller-grep evidence) and what over-engineering it
removes. Update this file's checklist inside each commit.

Reference baseline for generated docs: inner code-block content of
`git show 598e27c31:docs/MIR/mir-reviewers-template.md` and
`git show 598e27c31:docs/MIR/mir-reporters-template.md`.

## Guiding rails

- One commit per audit item (except B1/P0/F). No mixing refactor with
  behavior change. "Text changes, verified equal" commits get explicit
  equality checks (message-render tests, golden fixtures).
- Tests of dead code are deleted with the dead code in the same commit.
- No integration VM available: `make test` (ruff format+lint + pytest unit)
  per commit; LXD integration deferred to final user test.
- Do not commit anything outside the scope of the current numbered item.

## P0 — this plan [DONE]

## Phase 0 — stabilize generated content

### B1 — stabilize generated include content against pre-tool templates

Status: DONE. B1a restored the reporter catalog (render byte-identical to
the 598e27c31 reporter template; reviewer side accepted as-is with only the
user-approved Maintainer-field addition). B1b committed the golden fixtures
(tests/fixtures/include_*.golden) plus byte-for-byte regression tests
(tests/test_template_goldens.py). Every later commit must keep them green.

1. Extract reference content: inner block after `{code-block} text` /
   `:linenos:` in the two `598e27c31` template files. Store as
   `tools/auto-mir/tests/fixtures/include_reviewers.golden` and
   `include_reporters.golden`. Goldens ARE committed with this commit.
2. Run the current render scripts (docs/Makefile path), diff output against
   goldens.
3. Iterate: adapt blueprint YAML / render code ONLY to close mismatches.
   Any delta that looks intentional (rules may have improved since the
   tool switch) is listed, classified, and presented to the user:
   user decides "make it match old text" vs "keep, becomes the golden".
   No guessing.
4. Add regression test regenerating both bodies and comparing byte-for-byte
   to the goldens. This test is the guard for #11 and #28; all subsequent
   commits must keep it green.

## Phase 1 — dead code deletions

### #17 — dead one-offs
Delete (each verified by repo-wide grep: only definition + own tests):
- `_MAX_TOKENS` alias (llm.py:117; code uses `_max_tokens_for_tier`)
- `_ships_shared_library` (checks/deterministic.py:287)
- `pull_file` (lxd_runner.py:633)
- `_affirmative_statement` (render/__init__.py:349)
- `_MIR_BUG_TAG` (lp_intake.py:48)
- unreachable block after `return detector(packaging)`
  (checks/language_gates.py:195-197)
- `_check_esl_1` (deterministic.py:568; never dispatched — ESL-1 is
  `mode: ev_to_ai` in catalog)
- `cvelist_scan_invm.main()` (only `scan_zip` imported)
- `retry_transient_network` (utils/retry.py; superseded by
  `retry_rate_limited`/`retry_guest_command`)
- `scan_for_injection` (utils/llm_sanitize.py; superseded by
  `scan_for_injection_matches`)
Delete their tests.

### #7 — Finding factory classmethods
Drop `Finding.ok/not_ok/unknown` (models.py:271-370); production constructs
directly. Rewrite test_models.py cases to direct construction.

### #26 — free-text evidence-request parsing
Drop the string branch of `_parse_build_log_request`
(checks/llm_eval.py:441-461) + its tests; prompt only specifies JSON dicts;
non-dict requests now return None (ignored).

### #27 — Answer.raw_input
Drop the field (reporter/models.py:128); update 10 constructor sites
(wizard + tests). Never read outside tests.

## Phase 2 — CLI surface

### #12 — remove legacy invocation + dead flags
Delete `_normalize_cli_args`, `_RoleArgumentParser`, `--legacy-invocation`,
refusal branch (auto_mir.py:34-54,285,875-880); drop `_resolve_run_name`
user_name branch (auto_mir.py:87-102); role becomes mandatory. Drop dead
flags `--lxd-options` (hoist `_DEFAULT_LXD_OPTIONS` constant into
lxd_runner) and `--request-binaries` + RunContext wiring. Update the 6
bare-form commands in testing.md:97,144-146,155.

## Phase 3 — catalog as source of truth

### #9 — delete catalog_enums.py
String ids everywhere; add one registry-keys==catalog-ids drift test
(replaces AdapterID's "must match" duty). CheckID has zero refs.

### #10 — delete runtime-dead YAML sections
- `security_triggers` (catalog-mir-review.yaml:1886-1947; only consumer is
  `len()` in catalog.py:1105)
- `render_policy`/`fallback_policy` (1948-1967; behavior hardcoded in
  render/__init__.py + evidence/checks code; only "consumer" is a docstring
  at auto_mir.py:552)
- per-check `security_trigger:` fields; `schema_version` markers (both
  YAMLs); `confidence_model.bands` (fold band names into description);
  `metadata.title` (report catalog)
- Move prose to CATALOG.md. Update test_catalog_roles.py:22-24 asserts,
  test_catalog.py:164-176, drop `security_trigger_count` from summary.

### #3 — data-driven message-template validation
Replace `_REQUIRED_MESSAGE_TEMPLATES` (catalog.py:592-834, 243-line Python
mirror of YAML) with `required_placeholders` map next to each template in
the YAML + one generic validation loop.

### #5 — slim catalog.yaml adapter declarations
Keep `id/type/description/depends_on/notes`; move `inputs:`,
`output_contract:`, per-adapter `fallback:` prose into adapter
docstrings/CATALOG.md (~215 lines never read at runtime).

## Phase 4 — test catalog rewrite

### #1 — test_checks.py loads the real catalog
Rewrite to load real catalog via `catalog.load_catalog_for_role` and index
by check id; delete ~650 lines of hand-copied message blocks and their two
re-copies (lines 1029+, 2614+). Do AFTER all catalog-structure changes
(#3,#5,#9,#10) so the rewrite happens once; BEFORE checks rework so the
rework is validated against real catalog data.

## Phase 5 — checks module (sequential)

### #14 — registries become dict literals
- checks: `EVALUATORS = {...}` in checks/__init__.py (delete
  checks/registry.py + `_ensure_evaluators_registered` importlib dance)
- evidence: `ADAPTER_REGISTRY = {...}` in evidence/__init__.py (delete
  evidence/registry.py + `_ensure_adapters_registered`)
4 evaluators, 29 adapters — plain dicts.

### #16 — unify adapter-failed→unknown blocks
Extend `_set_unknown_from_adapter` (deterministic.py:33) with
`message_key`/`severity`/`evidence_refs` params; replace ~10 inline
9-line blocks (CB-1 at 365-376, CB-2/3 etc. at 925-934, 1079-1088,
1137-1146, 1226-1235, 1301-1310, 1355-1364, 1432-1441, 1482-1491,
1555-1564) with one-line helper calls. Same catalog keys, same severity —
assert rendered messages unchanged in tests.

### #4 — dep-scan spec table
Replace URF-7, SEC-8, CB-7, SEC-3, SEC-4, DEP-1 functions
(deterministic.py:1657-2062) with a spec table + one generic evaluator in
deterministic.py. Messages still rendered from catalog keys. SEC-10 stays
BESPOKE with a comment why (tiered patterns/severity would bloat the
table; user decision). SEC-8's second source (debian_control patterns)
gets an optional second-source spec cell.

### #20 — checks dedup
- merge `_eval_ai` into `_eval_ev_to_ai` (payload-builder param)
  (checks/llm_eval.py:98-143)
- shared `_unexpected_built_using` helper for ESL-3/ESL-10
  (deterministic.py:616-627 vs 786-805)
- retire `render_check_message_or_default` (checks/messages.py:37-46):
  move human_only defaults into the catalog, use strict
  `render_check_message`. Same strings, new home, asserted equal in tests.

### #15 — version compare
`_compare_versions`: two `dpkg --compare-versions` calls (drop redundant
eq call; deterministic.py:2169-2181) + replace ~45 lines of hand-rolled
Debian parsing with `int(re.match(r"\d+", ...))` for the major-gap test;
delete `_parse_version_tuple`/`_split_debian_version`/
`_normalize_upstream_version` after confirming no other callers.

## Phase 6 — evidence/plumbing

### #2 — delete evidence/types.py
651 lines, 52 TypedDicts, zero consumers beyond return annotations;
project runs no type checker (ruff E/F/W/I only). Annotate `-> dict`; one
docstring line per adapter naming notable keys. Update importing modules
(host/guest_adapters, version_resolution) + tests. Commit message notes
the TypedDict reintroduction path if a type checker is ever adopted.

### #18 — inline single-function adapter modules
Fold lto_disabled_adapter.py + team_mapping_adapter.py into
host_adapters.py (where the other 16 host adapters live); delete both
files; update `_ensure_adapters_registered` (or its #14 dict successor).

### #25 — launchpad_client slim
Drop `BuildCandidate` class (launchpad_client.py:292-339; use the dict the
caller already gets), remove `build_attr`/`_binary_arch_tag` dict-or-
attribute dual path (75-91,146-161; tests supply mocks with attributes
instead; delete `test_build_attr_reads_dict_records`), call http_utils
directly for `_fetch_json`/`_fetch_text`/`_download_oval_xz`/
`_download_autopkgtest_db` one-liners (host_adapters.py:836-853).

### #21 — one TODO-normalization helper
One `_normalize_todo` in models.py + one `_strip_todo_prefix` in
reporter/text_utils with a SINGLE unified regex; migrate the 3 diverging
copies (text_utils.py:17-23; render/__init__.py:566-571;
checks/llm_eval.py:863-870). Add a test covering TODO:/TODO- variants to
prove the unified regex supersedes all three.

### #29 — delete contracts.py
Two Protocols with one implementation each, used purely as type hints;
annotate with `RunContext` at their single consumers
(checks/__init__.py:65, evidence/__init__.py:50).

### #31 — micro-batch
- shared `utils.cli.ask_yes_no` (lp_intake.py:186-196, auto_mir.py:707-731,
  reporter/wizard.py)
- `_strip_common_prefix` → `os.path.relpath` (utils/llm_evidence.py:163-170)
- `_extract_template_section` → one `re.search` (checks/llm_eval.py:517-537)
- merge `_with_hanging_indent`/`_with_rationale` (reporter/render.py:50-61
  vs render/__init__.py:382-393)
- utils/dependencies.py frozen dataclass registry → dict literal
  (UPDATE tests/test_dependencies.py::test_runtime_registry_matches_
  pyproject_dependencies in same commit)
- drop `PredecessorRef.raw/.kind` (utils/predecessor_refs.py:89-98,182-188)
- keep one `AdapterError` (guest_adapters.py:45-46 vs host_adapters.py:82-83)
- drop unused `lp` param (lp_intake.py:116)
- drop `with_unknown_todo` param never passed False (deterministic.py:60-70)

### #23 — one shared LLM usage aggregator
`_render_llm_usage_report` duplicates `_estimate_llm_tokens`'s aggregation
(render/__init__.py:35-56,770-797) and is a private symbol imported
cross-module by auto_mir.py:1081. One shared aggregator.

### #22 — shared ai.py/llm_eval helpers
Options-prompt rendering (`_render_reporter_options_section` vs
`_render_options_for_prompt`), per-item field maps
(`_FULL_CONTENT_FIELDS_BY_ITEM` vs `_BY_CHECK`), identical truncate loops →
shared helpers in utils/llm_evidence
(reporter/ai.py:32-35,86-97,361-380; checks/llm_eval.py:41-44,242-253,
744-766).

## Phase 7 — entrypoints/LLM

### #6 — rate limiter onto tenacity
Delete llm.py hand-rolled adaptive limiter: `_RateLimitState` (135-149),
`_get_rate_limiter` (458-463), `_wait_for_slot` (466-472),
`_learn_from_headers` (475-517), `_parse_rate_limit_hint` (748-765),
429-learning/pacing (366-403). `retry_rate_limited`/tenacity stays the
single scheme; feed `extract_retry_after` into the tenacity wait if
Retry-After honoring is kept. Also drop case-duplicate header lookups
(485-486,201; `HTTPMessage.get` is case-insensitive).

### #19 — one review-type detector
Merge `pre_detect_review_type`/`detect_review_type` (review_type.py:158-312)
into `detect_review_type(ctx, use_evidence=...)`; deduplicate
forced-short-circuit and reorg/rereview branches.

### #24 — lxd_runner slim
`shutil.which("lxc")` (lxd_runner.py:134); remove version-extraction feeding
two debug log lines entirely (144-161); fold `_exec_in_retry_internal`
(518-548) into decorator application on `exec_in_retry`.

### #13 — auto_mir.py slim
Inline the 4 single-caller stage pass-throughs (443-561) into main() keeping
`current_stage` labels; merge `stage_auth`/`stage_optional_auth` (564-614);
cut 31-line RunContext lifecycle docstring (308-338); drop
`_log_artifact_locations` (1062-1076, banner covers it); unify
`_finish_run` tail (980-991); remove dead `format()` in `_RunContextFilter`
(825-834); drop `tool_version` meta field (1048).

### #8 — declarative follow-up hints (option b)
Add `leads_to_followup: true` to the triggering options in
catalog-mir-report.yaml; wizard reads the flag (wizard.py:285); delete
`_mark_followup_options`/`_followup_trigger_values`/`_condition_triggers`
(reporter/evaluator.py:343-414) and the runtime derivation of
`QuestionOption.leads_to_followup`. UI hint unchanged.

## Phase 8 — render unification (guarded by B1 goldens)

### #11 — one render script with --role
Merge render_reporter_template.py + render_review_template.py into one
script with `--role`; store body-only content in the blueprint (delete
fence/`:linenos:` slicing, render_review_template.py:98-122); keep `--check`
staleness mode; drop tautological `--strict` re-validation
(125-141,206-216,238-239). ACCEPTANCE: B1 golden test stays green.

### #28 — catalog machinery dedup
Shared `_ensure_yaml()` loader helper (catalog.py:237-245,267-275); drop
unhashable-key branch (194-202); replace 9 hand-copied `rule_context`
blocks with `covers_rule_clauses` slug references
(catalog-mir-report.yaml:211,225,331,343,356,631-636,799,832,862); derive
`section_markers` from the blueprint (catalog-mir-report.yaml:5-17);
rule_context drift validator goes (catalog.py:411-422).

## Phase 9 — wrap-up

### F — final commit
1. Relax B1 golden test into the dual-outcome workflow: failure message
   documents both paths — (a) mistake → fix code; (b) intentional → run
   new `make update-goldens` target, regenerate goldens IN THE SAME COMMIT
   whose message states the intent. Rules may then evolve with
   catalog/logic changes, consciously.
2. Update decisions.md with audit→commit traceability (short section
   mapping each commit to the finding + rationale).
3. Delete this plan file.
4. Final `make test`; regenerate both `.include` files via make; confirm
   only expected diffs.
5. Hand off to LXD user test.

## Checklist

- [x] P0  plan on disk + git
- [x] B1  stabilize generated content (goldens from 598e27c31)
- [x] #17 dead one-offs
- [x] #7  Finding factory classmethods
- [x] #26 free-text evidence-request parsing
- [x] #27 Answer.raw_input
- [x] #12 legacy invocation + dead flags
- [x] #9  catalog_enums.py
- [x] #10 dead YAML sections
- [x] #3  _REQUIRED_MESSAGE_TEMPLATES
- [x] #5  catalog.yaml adapter declarations
- [x] #1  test_checks.py real catalog
- [x] #14 registries → dicts
- [x] #16 unknown-block unification
- [x] #4  dep-scan spec table (SEC-10 bespoke)
- [ ] #20 checks dedup
- [ ] #15 version compare
- [ ] #2  evidence/types.py
- [ ] #18 inline single-function adapters
- [ ] #25 launchpad_client slim
- [ ] #21 TODO normalization
- [x] #29 contracts.py
- [ ] #31 micro-batch
- [ ] #23 LLM usage aggregator
- [ ] #22 ai/llm_eval shared helpers
- [ ] #6  rate limiter onto tenacity
- [ ] #19 review_type detector
- [ ] #24 lxd_runner slim
- [ ] #13 auto_mir.py slim
- [ ] #8  declarative follow-up hints
- [ ] #11 one render script --role
- [ ] #28 catalog machinery dedup
- [ ] F   wrap-up (dual-outcome goldens, decisions.md, delete plan)

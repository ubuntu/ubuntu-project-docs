# auto-mir User-test Fix Round 3 (temporary file — deleted in the final commit)

Seven user-test reports, one logical commit each, all on `auto-mir-review`
with `--no-gpg-sign` and `make test` green before every commit.

## Root causes (artifact-verified from /tmp/mir-2121154-20260902-154941)

1. The adapter-failure WARNING block is printed mid-log by
   render.write_outputs (stage 5); it belongs in the end-of-run tail.
2. llm.py logs request start/finish at INFO; they are progress detail under
   the check-evaluation lines that stay INFO.
3. Stage log lines are plain INFO; need `=== ... ===` visual catch-up.
4. _get_cached_autopkgtest_db caches the good-path download on ctx but never
   caches failures - each of the three autopkgtest adapters re-ran the full
   30->300s backoff ladder (~12.5 min each) in the user's run.
5. WP6 fixed the prior-MIR evidence path; this run's false reorg came from
   _REORG_TEXT_RE matching ordinary rationale language ("replace gnupg2 with
   Sequoia") and process language ("split out of 2089690" - a bug number).
   User decision: replace the brittle regex with an LLM classification of
   the reporter's MIR content + interactive human confirmation.
6. SUM-5: the model bypassed the option machinery (selected_option empty,
   free-form status ok) and the draft rendered a confident "Suggesting ACK"
   line. User decision: new `human_verdict` catalog field on SUM-5 and SUM-6;
   both always render as a decision point with the full option TODO block
   kept and the AI's suggestion as a NOTE.
7. git-ubuntu-delta used refs that do not exist in git-ubuntu clones
   (remotes/origin/...; the remote is `pkg`) -> base never resolved -> empty
   diffstat forever. It also excluded debian/changelog from the diff though
   the changelog is the most informative delta content.

## Commit sequence

### 1 - P0: this plan [DONE]

### 2 - WP-A: three-section end-of-run tail
_move _render_adapter_failure_warning print out of write_outputs into
_print_complete_banner; tail = `Warnings:` (when non-empty) ->
[LLM Usage Report] -> Results box. Tests for both banners._

### 3 - WP-B: LLM progress lines to DEBUG
_start/finish lines become log.debug; failure lines stay INFO. caplog tests._

### 4 - WP-C: stage markers
_`=== Stage N: ... ===` on the review-stage log lines (and report-role
equivalents); current_stage failure labels untouched._

### 5 - WP-D: autopkgtest failure caching
_cache the AdapterError on ctx like the path; later adapters fail fast with
the identical message. Tests: single good-path download across three
adapters, fail-fast on repeat, per-ctx reset._

### 6 - WP-E: LLM-assisted review-type first decision
- Stage 1: one bounded small-tier LLM call classifies the reporter content
  {new|rereview|reorg|unsure} + reasoning.
- Suspicious -> interactive console prompt (utils.cli.ask_yes_no) with the
  reasoning; human decides. Headless -> fresh + warning with the reasoning.
- LLM unavailable -> fallback = narrowed regex (renam*/formerly/was
  previously/reorganis*; split out/from/of not followed by a number;
  replace/supersede removed) + same interactive confirm.
- Stage 4: no raw text regex anymore; order = forced > stage-1 human
  decision > WP6 evidence signals > fresh.
- Tests incl. the exact "replace gnupg2"/"split out of 2089690" content
  classifying as new -> fresh, no prompt.

### 7 - WP-F: human_verdict catalog field
_Optional check field; declared on SUM-5 and SUM-6. The finding is always
unknown/Left-to-decide with the full option TODO block (A/B/C) kept and the
AI suggestion as a NOTE naming the suggested option. Tests for free-form
model responses, option picks, and draft lines; SUM-6 keeps its good shape
structurally._

### 8 - WP-G: git-ubuntu-delta rewrite
- refs: pkg/ubuntu/devel, pkg/import/<version>, pkg/debian/sid.
- base: newest Debian-only pkg/import ancestor (no ubuntu.../buildN suffix),
  fallback git merge-base pkg/ubuntu/devel pkg/debian/sid.
- diffstat INCLUDING debian/changelog (exclude dropped) + bounded
  changelog_excerpt evidence field (~40 lines of the changelog diff); flows
  into PRF-1's payload; its ai_policy points at the excerpt.
- Tests via fake guest exec: tag walk on the 1.3.1-10 -> -10ubuntu1 ->
  -10ubuntu2 example, fallback, honest empty-diffstat path.

### 9 - F: wrap-up
_decisions.md traceability, delete this plan, final make test + goldens._

## Checklist

- [x] 1  P0 plan on disk
- [x] 2  WP-A three-section tail
- [x] 3  WP-B LLM progress to DEBUG
- [x] 4  WP-C stage markers
- [x] 5  WP-D autopkgtest failure caching
- [ ] 6  WP-E LLM-assisted review-type decision
- [ ] 7  WP-F human_verdict field
- [ ] 8  WP-G git-ubuntu-delta rewrite
- [ ] 9  F wrap-up

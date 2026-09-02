# auto-mir User-test Fix Plan (temporary file — deleted in the final commit)

Six user-test feedback fixes plus the rule/coverage gap work, one logical
commit each, all on `auto-mir-review` with `--no-gpg-sign` and `make test`
green before every commit. LXD integration stays deferred to the final
user test.

## Root causes (from artifact-verified analysis, 2026-09-02)

1. Console output degraded: commit 85d5370b (#13) deleted ColorFormatter.format
   believing it dead; it WAS the console formatter (colors + [H:MM:SS] timing).
   Restore verbatim from 85d5370b^. Missing test = the lesson.
2. Version prompt: at run time 1.4.0-1ubuntu2 WAS Published in the Release
   pocket (removed from the archive afterwards, hence absent from the user's
   later rmadison). Pocket filtering was correct. Real issues: (a)
   _candidate_versions_in_pocket includes Deleted/Removed/Obsolete entries,
   (b) a 1-option interactive prompt is needless friction, (c) the headline
   gives no pocket context.
3. Test warnings: pythonjsonlogger.jsonlogger deprecation (auto_mir.py:747),
   unregistered pytest.mark.integration, third-party httplib2/pyparsing
   deprecations from Ubuntu's dist package.
4. Skipped test: tests/test_artifacts.py replays fixtures under
   tests/fixtures/<bug_id>/ that were never committed -> skipped since
   introduction. Decision: delete the replay suite.
5. Comment-only source matches flagged as Problems: URF-3/4/5 scans lack
   comment awareness; all hits in the user's run were rust doc comments.
6. Wrong reorg detection: lp-mir-history matched sibling MIR bug 2089690
   ("[MIR] rust-sequoia-sqv") with matched_name "gnupg2" (the LP project the
   bug was filed under); _prior_mir_under_other_name counted it as rename
   evidence. A prior MIR for a name that still exists is a sibling, not a
   rename.

## Gap re-analysis verdicts (G1-G6, re-verified against current code)

- G1 debconf priority, G2 lintian-overrides explanation, G3 REP-MAINT-003
  wording: STALE - already resolved by later rounds; decisions.md entries
  get corrected in the inventory commit so they stop misleading.
- G4 Built-Using reporter section: IMPLEMENT - new reporter item(s) under
  [Maintenance/Owner], deterministic evaluator over deb-metadata's
  Built-Using/Static-Built-Using entries, reuse _built_using_entries helper,
  adapters_required: [deb-metadata] (report runs already fetch-build).
- G5 security sources: ADPT - mirror SEC-1's reasoned sourcing note
  (cvelistV5/NVD covers Debian-relevant identifiers; oss-security manual
  only) to the reporter side. No new adapter.
- G6 lp-team-membership-api: ADAPT wording - describe what it does (bug
  subscribers = the acknowledgment evidence RDO-2/motu-impact need); id and
  behavior unchanged.
- NEW inventory findings: same a/b/c protocol per finding, user decides
  before implementation.

## Commit sequence

### 1 — P0: this plan on disk [DONE]

### 2 — WP1: restore console formatting
Restore ColorFormatter.format verbatim from 85d5370b^. New regression test:
run the real logging setup with a captured stream, assert level color
sequence + [H:MM:SS] timing + redaction wrapper intact.

### 3 — WP3: warning cleanup
Register `integration` pytest marker (pyproject). Switch to
`from pythonjsonlogger.json import JsonFormatter` with try/except fallback
to pythonjsonlogger.jsonlogger. filterwarnings ignores for the
httplib2/pyparsing PyparsingDeprecationWarning (third-party dist noise).
Verify: make test reports zero warnings.

### 4 — WP4: delete the replay suite
Delete tests/test_artifacts.py, _save_test_artifacts (+ call site, banner
refs), testing.md fixture-regeneration section (86-146 region).

### 5 — WP2: version walk-back hygiene
_candidate_versions_in_pocket: only Published/Superseded qualify (rmadison
view). _ask_buildable_candidate: exactly one buildable candidate -> no
prompt, proceed with note. Headline names the pocket and unbuilt-ness.
Tests with the mixed-status publish-history shape captured from the run
artifacts (1.4.0-1ubuntu2 Published+Deleted+Superseded variants).

### 6 — WP5: comment-aware source scanning
Pure helper: classify grep hit (path:line:content, term) active vs comment,
extension-family aware (.rs: //, ///, //!, /* */; C/C++: //, /* */;
python/shell/debian: #), rule: first marker at-or-before term's first
occurrence => comment. Documented limitation: per-line classification.
Wire into URF-3/4/5. Semantics: all hits comment/test/doc context ->
finding SUCCEEDS with new ok_comment_only_message naming the matches
(found, reported but ok, never under Problems:); mixed -> current not-ok
with active hits. New catalog keys + required_messages rows. Tests per
language family + regression fixtures from the exact rust-vendor /// lines.

### 7 — WP6: evidence-verified reorg detection
lp-mir-history: fix matched_name derivation (title capture first; bug-text
pairing fallback must not adopt the LP project as target), add bounded
still_published check per distinct matched name, exclude the current bug
from prior_mir_bugs. review_type: only count names NOT still published.
Surface decision (review_type, forced, rationale, signals) in report.json.
Tests: sibling-still-published -> FRESH; retired predecessor -> REORG;
regression replaying this run's exact payload (gnupg2) -> FRESH.

### 8 — WP7 Phase A: coverage inventory (PAUSE for user a/b/c)
Clause walk of both blueprints (206 reviewer / 304 reporter RULE lines).
Table: clause -> covering check(s)/item(s) -> {covered, partial, missing,
prose-not-checkable}. Records G1-G6 verdicts (stale ones corrected in
decisions.md). NEW findings presented RULE-vs-coverage side-by-side; user
advises a) adapt rule b) ignore c) implement before anything is built.

### 9 — G5 + G6 alignments
Reporter security sourcing note (SEC-1's position mirrored to
REP-SECURITY-001 guidance/context; appears in reporter-facing output).
lp-team-membership-api honesty fix (description/docstring + overstating
ai_policy wording; id/behavior unchanged).

### 10 — G4: Built-Using reporter items
New reporter item(s) under [Maintenance/Owner], deterministic evaluator
over deb-metadata Built-Using/Static-Built-Using (reuse
_built_using_entries), adapters_required: [deb-metadata] (collection
wiring automatic; depends_on fetch-build already satisfied in report
runs). Facts only, human/AI judges. Blueprint untouched -> goldens green.
Tests: evaluator units (empty/toolchain-only/unexpected), catalog
validation, wizard flow with stub deb-metadata.

### 11 — coverage completion
Slug + covers_rule_clauses for every policy-bearing clause in both
catalogs per the inventory; implement any user-approved new-finding fixes.
Load-time validator enforces the map from here on.

### 12 — F: wrap-up
decisions.md traceability (feedback item -> commit; stale-gap
corrections), delete this plan file, final make test + golden guards,
hand off to the user integration test.

## Checklist

- [x] 1  P0 plan on disk
- [x] 2  WP1 console formatting restored + test
- [x] 3  WP3 warnings clean
- [x] 4  WP4 replay suite deleted
- [x] 5  WP2 version walk-back hygiene
- [x] 6  WP5 comment-aware scanning
- [ ] 7  WP6 verified reorg detection
- [ ] 8  WP7 Phase A inventory (pause)
- [ ] 9  G5 + G6 alignments
- [ ] 10 G4 Built-Using reporter items
- [ ] 11 coverage completion (+ approved new fixes)
- [ ] 12 F wrap-up

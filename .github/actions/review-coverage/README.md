# Review-coverage bot

Keeps one sticky comment per PR listing the CODEOWNERS owner-groups that
still owe an approval, trims redundant reviewers from the review queue, and
keeps `CODEOWNERS-teams.yaml` display names in sync.

## Behavior

- Requirements: changed files × the default branch's CODEOWNERS, matched as
  GitHub does (last match wins; `docs/*` does not cover `docs/sub/x.md`).
- A group is satisfied by the latest APPROVED review of any listed individual
  owner; COMMENTED and PENDING reviews never override it. Team and email
  owners can't be verified, and owners GitHub reports as unknown
  (`codeowners/errors`, e.g. no write access) don't count: they never satisfy
  a group, and the comment lists them.
- A group nobody can approve (no valid individual owner, or the PR author is
  its only one) is flagged in the comment and never blocks.
- A PR that changes CODEOWNERS (at `.github/`, the root or `docs/`, including
  renames) needs one approval from every owned group in the default branch's
  CODEOWNERS, even groups whose files are all covered by later patterns. This
  is stricter than GitHub, which accepts any owner of the CODEOWNERS line.
  Owners of those extra groups are not notified; the comment lists them.
- Once a group is satisfied, its other requested members leave the review
  queue (only removals the queue confirms are recorded). If the group becomes
  pending again, they are re-requested; this state lives in a hidden block in
  the comment. Manually requested members are removed too: the API doesn't
  say who requested a review.
- Removal and re-request failures are noted in the comment, retried on the
  next run, and fail the job.

## Status check

Each run also sets a `review-coverage` commit status on the PR head:
`failure` while any section is pending (or when CODEOWNERS can't be read, or
GitHub lists only part of a very large PR's files), `success` otherwise. To
enforce it, add `review-coverage` as a required status check for `main`.
Caveats: a missed run leaves a stale status (re-run via `workflow_dispatch`),
and required checks are matched by name, so a fork PR could add its own
passing job called `review-coverage`. Keep approval required for fork
workflows and review `.github/` changes.

## Triggers

- `pull_request_target`: yaml sync when CODEOWNERS changes (commit for
  same-repo PRs, suggestion comment for forks), then coverage.
- `pull_request_review` → artifact → `workflow_run`: fork-safe update after
  reviews; the PR number is validated and bound to the triggering head SHA.
- `push` to main touching CODEOWNERS: `sync-yaml --base` (opens a bot PR),
  then one dispatched coverage run per open PR, so a rescan never races a
  review-triggered update of the same PR.
- `workflow_dispatch`: one PR, or (empty input) the same rescan.

Commits made with `GITHUB_TOKEN` (the bot's yaml syncs) don't trigger
workflows; re-run checks via `workflow_dispatch` if needed.

## Local use

`--dry-run` only reads from GitHub: it prints the comment and status it
would write.

```sh
GITHUB_TOKEN=$(gh auth token) GITHUB_REPOSITORY=ubuntu/ubuntu-project-docs \
  python3 script.py coverage --pr N --dry-run
python3 -m pytest test_review_coverage.py
```

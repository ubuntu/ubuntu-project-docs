#!/usr/bin/env python3
"""PR review-coverage bot for ubuntu-project-docs. See README.md here."""

from __future__ import annotations

import argparse
import base64
import hashlib
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any

STICKY_MARKER = "<!-- review-coverage-bot -->"
CODEOWNERS_PATH = ".github/CODEOWNERS"
# GitHub reads the first of these that exists.
CODEOWNERS_LOCATIONS = (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS")
REVIEW_COVERAGE_WORKFLOW = "review-coverage.yml"
TEAMS_YAML_PATH = ".github/CODEOWNERS-teams.yaml"
MAX_FILES_PER_SECTION = 5
YAML_SYNC_MARKER = "<!-- review-coverage-yaml-sync -->"
API_BASE = "https://api.github.com"
BOT_LOGIN = "github-actions[bot]"
STATE_MARKER = "review-coverage-bot-state"
# The state block must sit on a line of its own. Table rows (which carry
# PR-controlled file names) always start with "|", so a file name that
# contains the marker can never match; the last match wins regardless.
STATE_RE = re.compile(
    r"^[ \t]*<!--[ \t]*"
    + re.escape(STATE_MARKER)
    + r"[ \t]+(\{[^\n]*\})[ \t]*-->[ \t]*$",
    re.MULTILINE,
)
MAX_SLEEP_SECONDS = 120
STATUS_CONTEXT = "review-coverage"
# Plain Unicode text symbols (no color emoji) for comment status markers.
SYM_APPROVED = "\u2713"  # ✓ CHECK MARK
SYM_PENDING = "\u25cb"  # ○ WHITE CIRCLE
SYM_WARNING = "\u25b3"  # △ WHITE UP-POINTING TRIANGLE


@dataclass
class OwnerSet:
    pattern: str
    members: list[str]
    # Owners the bot cannot verify approvals for: @org/team and email owners.
    # GitHub still enforces these; a set is satisfied only once one of its
    # individual owners approves (GitHub accepts any listed owner), and a
    # set with no individual approval stays pending.
    unresolvable: list[str] = field(default_factory=list)
    # Owners GitHub itself reports as unknown (typically: no write access).
    # GitHub ignores their approvals, so the bot must too.
    invalid: list[str] = field(default_factory=list)

    @property
    def has_owners(self) -> bool:
        return bool(self.members or self.unresolvable or self.invalid)


_UNKNOWN_OWNER_RE = re.compile(r"make sure (\S+) exists")


def unknown_owners_by_line(errors: list | None) -> dict[int, set[str]]:
    """Map CODEOWNERS line number -> owners GitHub flags as "Unknown owner".

    Input is the `errors` list of GET /repos/{repo}/codeowners/errors.
    Owner tokens are lower-cased; unparseable entries are ignored.
    """
    out: dict[int, set[str]] = {}
    for err in errors or []:
        if not isinstance(err, dict) or err.get("kind") != "Unknown owner":
            continue
        line = err.get("line")
        text = str(err.get("suggestion") or err.get("message") or "")
        m = _UNKNOWN_OWNER_RE.search(text)
        if not isinstance(line, int) or not m:
            continue
        out.setdefault(line, set()).add(m.group(1).lower())
    return out


def _split_codeowners_line(line: str) -> list[str]:
    """Whitespace-split a CODEOWNERS line, respecting `\\ ` escapes.

    CODEOWNERS has no quoting: `'` and `"` are ordinary path characters.
    """
    out: list[str] = []
    i, n = 0, len(line)
    while i < n:
        while i < n and line[i].isspace():
            i += 1
        if i >= n:
            break
        start = i
        while i < n:
            ch = line[i]
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch.isspace():
                break
            i += 1
        out.append(line[start:i])
    return out


def parse_codeowners(
    text: str, unknown: dict[int, set[str]] | None = None
) -> list[OwnerSet]:
    """Parse CODEOWNERS; `unknown` maps line number -> owners to disregard."""
    unknown = unknown or {}
    sets: list[OwnerSet] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = _split_codeowners_line(line)
        pattern = parts[0].replace("\\ ", " ")
        owner_tokens = parts[1:]
        # Inline comments are valid after owners, e.g. `*.js @owner #note`.
        for idx, tok in enumerate(owner_tokens):
            if tok.startswith("#"):
                owner_tokens = owner_tokens[:idx]
                break
        members: list[str] = []
        unresolvable: list[str] = []
        invalid: list[str] = []
        bad = unknown.get(lineno, set())
        for tok in owner_tokens:
            if tok.lower() in bad:
                invalid.append(tok)  # GitHub ignores this owner
            elif tok.startswith("@"):
                if "/" in tok[1:]:
                    unresolvable.append(tok)  # team owner, e.g. @org/team
                else:
                    members.append(tok[1:].lower())  # individual login
            elif "@" in tok:
                unresolvable.append(tok)  # email owner, e.g. docs@example.com
            else:
                members.append(tok.lower())
        # A bare pattern (no owners) is valid CODEOWNERS: it clears the
        # requirement for those paths. Later matching lines override it.
        sets.append(OwnerSet(pattern, members, unresolvable, invalid))
    return sets


def _glob_body(pattern: str) -> str:
    """Translate a gitignore/CODEOWNERS pattern body to a regex fragment.

    `**` is special only in the gitignore forms `**/` (leading), `/**/`
    (mid-pattern) and a trailing `/**`; anywhere else it behaves like a
    single `*` (does not cross a `/`). `[`, `]`, `{`, `}` are treated
    literally: CODEOWNERS does not support character classes or braces.
    """
    out: list[str] = []
    i, n = 0, len(pattern)
    while i < n:
        c = pattern[i]
        if c == "\\" and i + 1 < n:
            out.append(re.escape(pattern[i + 1]))
            i += 2
            continue
        # Multi-character globstar forms are matched on lookahead so the
        # surrounding `/` is consumed as part of the token, not emitted
        # twice (once here, once when the plain `/` char is processed).
        if i == 0 and pattern[:3] == "**/":
            out.append(r"(?:.*/)?")
            i += 3
            continue
        if pattern[i : i + 4] == "/**/":
            out.append(r"/(?:[^/]+/)*")
            i += 4
            continue
        if pattern[i : i + 3] == "/**" and i + 3 == n:
            out.append(r"/.+")
            i += 3
            continue
        if c == "*":
            out.append(r"[^/]*")
            i += 1
            continue
        if c == "?":
            out.append(r"[^/]")
            i += 1
            continue
        out.append(re.escape(c))
        i += 1
    return "".join(out)


def pattern_to_regex(pattern: str) -> re.Pattern:
    pat = pattern
    anchored = pat.startswith("/")
    if anchored:
        pat = pat[1:]
    elif "/" in pat.rstrip("/"):
        anchored = True
    is_dir = pat.endswith("/")
    if is_dir:
        pat = pat[:-1]
    if pat == "**" and not is_dir:
        # A lone `**` (or `/**`) matches everything, recursively.
        return re.compile(r"^.+$")
    trailing_globstar = pat.endswith("**") and len(pat) >= 3 and pat[-3] == "/"
    last_segment = re.sub(r"\\.", "", pat.rsplit("/", 1)[-1])
    wildcard_tail = "*" in last_segment or "?" in last_segment
    body = _glob_body(pat)
    if is_dir:
        # Directory pattern: matches files inside the directory only. A
        # trailing `/**` already expresses "everything inside", so it needs
        # no extra suffix.
        suffix = "" if trailing_globstar else r"/.+"
    elif trailing_globstar or wildcard_tail:
        # A wildcard final segment matches only at that level. GitHub
        # documents that `docs/*` matches `docs/getting-started.md` but not
        # `docs/build-app/troubleshooting.md`.
        suffix = ""
    else:
        # A bare literal name may also name a directory: cover its contents
        # too (gitignore semantics, which CODEOWNERS follows).
        suffix = r"(?:/.*)?"
    rx = ("^" if anchored else r"(?:^|.*/)") + body + suffix + "$"
    return re.compile(rx)


def match_file(path: str, sets: list[OwnerSet]) -> OwnerSet | None:
    found: OwnerSet | None = None
    for s in sets:
        if pattern_to_regex(s.pattern).match(path):
            found = s
    return found


def reduce_pr_sets(paths: list[str], sets: list[OwnerSet]) -> list[OwnerSet]:
    out: list[OwnerSet] = []
    for p in paths:
        s = match_file(p, sets)
        if s is not None and s.has_owners and all(o.pattern != s.pattern for o in out):
            out.append(s)
    return out


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return s


def _parse_yaml_entry(line: str) -> tuple[str, str] | None:
    """Parse one `"key": "value"` (or legacy unquoted) teams-yaml line."""
    m = re.match(r'^"((?:[^"\\]|\\.)*)"\s*:\s*"((?:[^"\\]|\\.)*)"\s*$', line)
    if m:

        def _unesc(s: str) -> str:
            return s.replace('\\"', '"').replace("\\\\", "\\")

        return _unesc(m.group(1)), _unesc(m.group(2))
    m = re.match(r"^(\S+)\s*:\s*(\S.*\S|\S)\s*$", line)
    if m:
        return _unquote(m.group(1)), _unquote(m.group(2))
    return None


def load_team_names(text: str) -> dict[str, str]:
    names: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        entry = _parse_yaml_entry(line)
        if entry:
            names[entry[0]] = entry[1]
    return names


def team_display_name(pattern: str, names: dict[str, str]) -> str:
    return names.get(pattern, pattern)


# Only these review states ever change a user's latest verdict. A COMMENTED
# or still-PENDING review never overrides a prior approval or changes
# request (GitHub keeps an approval when the reviewer later leaves a plain
# comment).
DECISIVE_REVIEW_STATES = ("APPROVED", "CHANGES_REQUESTED", "DISMISSED")


def latest_review_per_user(reviews: list[dict]) -> dict[str, str]:
    latest: dict[str, str] = {}
    for rev in reviews:
        state = rev.get("state", "")
        if state not in DECISIVE_REVIEW_STATES:
            continue
        user = (rev.get("user") or {}).get("login", "")
        if user:
            latest[user.lower()] = state
    return latest


@dataclass
class CoverageResult:
    matched_sets: list[OwnerSet]
    approvers: list[str]
    satisfied: list[OwnerSet]
    pending: list[OwnerSet]
    # Sets nobody can approve for this PR (no valid individual owner, or the
    # author is the only one). Reported with a warning; they never block.
    unapprovable: list[OwnerSet] = field(default_factory=list)


def unapprovable_reason(s: OwnerSet) -> str:
    """Why nobody can approve `s` (assumes it is unapprovable)."""
    if not s.members:
        return "no valid individual owner"
    return "only valid owner is the PR author"


def all_owned_groups(sets: list[OwnerSet]) -> list[OwnerSet]:
    """Every owner-group in CODEOWNERS: per pattern the last line wins
    (as in GitHub's matching); patterns whose last line has no owners are
    dropped. Ordered by each pattern's first appearance."""
    last: dict[str, OwnerSet] = {}
    for s in sets:
        last[s.pattern] = s
    return [s for s in last.values() if s.has_owners]


def compute_coverage(
    paths: list[str],
    sets: list[OwnerSet],
    reviews: list[dict],
    author: str | None = None,
    extra: list[OwnerSet] | None = None,
) -> CoverageResult:
    """`extra` adds required groups beyond those the changed files match
    (used for CODEOWNERS changes); duplicates by pattern are ignored."""
    matched = reduce_pr_sets(paths, sets)
    seen = {s.pattern for s in matched}
    for s in extra or []:
        if s.pattern not in seen:
            seen.add(s.pattern)
            matched.append(s)
    latest = latest_review_per_user(reviews)
    approvers = [
        u
        for u, st in latest.items()
        if st == "APPROVED" and (author is None or u != author.lower())
    ]
    # GitHub accepts an approval from ANY listed owner, so one individual
    # owner's approval satisfies a set even if it also lists a team/email
    # owner. A set that no valid individual other than the author can
    # approve would otherwise stay pending forever (and deadlock a required
    # status), so it is reported as unapprovable instead of blocking.
    author_low = author.lower() if author else None
    satisfied = [s for s in matched if any(m in approvers for m in s.members)]
    satisfied_patterns = {s.pattern for s in satisfied}
    unapprovable = [
        s
        for s in matched
        if s.pattern not in satisfied_patterns
        and not any(m != author_low for m in s.members)
    ]
    blocked_out = satisfied_patterns | {s.pattern for s in unapprovable}
    pending = [s for s in matched if s.pattern not in blocked_out]
    return CoverageResult(matched, sorted(approvers), satisfied, pending, unapprovable)


def compute_cull(requested: list[str], coverage: CoverageResult) -> list[str]:
    satisfied_members: set[str] = set()
    pending_members: set[str] = set()
    for s in coverage.satisfied:
        satisfied_members.update(s.members)
    for s in coverage.pending:
        pending_members.update(s.members)
    out = []
    for r in requested:
        low = r.lower()
        if (
            low in satisfied_members
            and low not in pending_members
            and low not in coverage.approvers
        ):
            out.append(r)
    return out


def _readd_candidates(
    coverage: CoverageResult,
    requested: list[str],
    culled: list[str],
    this_run_cull: list[str],
    author: str | None,
) -> list[str]:
    """Previously culled members whose set is pending again."""
    pending_members = {m for s in coverage.pending for m in s.members}
    requested_low = {r.lower() for r in requested}
    culling_now = {c.lower() for c in this_run_cull}
    out: list[str] = []
    for u in culled:
        low = u.lower()
        if (
            low in pending_members
            and low not in requested_low
            and low not in culling_now
            and low not in coverage.approvers
            and (author is None or low != author.lower())
        ):
            out.append(u)
    return out


def comment_body_hash(body: str) -> str:
    lines = body.splitlines()
    if lines and lines[0].strip() == STICKY_MARKER:
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("*review-coverage bot"):
        lines = lines[:-1]
    return hashlib.sha256("\n".join(lines).strip().encode()).hexdigest()


def parse_culled_state(body: str) -> list[str]:
    matches = STATE_RE.findall(body or "")
    if not matches:
        return []
    try:
        data = json.loads(matches[-1])
    except (ValueError, TypeError):
        return []
    culled = data.get("culled") if isinstance(data, dict) else None
    if not isinstance(culled, list):
        return []
    return [str(u).lower() for u in culled]


def _footer() -> str:
    stamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    run_id = os.environ.get("GITHUB_RUN_ID")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if run_id and repo:
        link = f"{server}/{repo}/actions/runs/{run_id}"
        return f"*review-coverage bot · updated {stamp} · [run]({link})*"
    return f"*review-coverage bot · updated {stamp}*"


def render_comment(
    coverage: CoverageResult,
    names: dict[str, str],
    pr_number: int,
    files_by_pattern: dict[str, list[str]],
    repo_url: str,
    cull: list[str],
    culled: list[str] | None = None,
    notices: list[str] | None = None,
    codeowners_rule: bool | str = False,
) -> str:
    """`codeowners_rule`: truthy when the all-groups rule applies; a string
    names the CODEOWNERS file the PR changes."""
    total, pend = len(coverage.matched_sets), len(coverage.pending)
    unapp = len(coverage.unapprovable)
    lines = [STICKY_MARKER, ""]
    if pend:
        lines.append(
            f"**{SYM_PENDING} {pend} of {total} section(s) still pending approval.**"
        )
    elif unapp:
        lines.append(
            f"**{SYM_APPROVED} No approvable section pending ({unapp} of {total} "
            "cannot be approved; see below).**"
        )
    else:
        lines.append(
            f"**{SYM_APPROVED} All sections approved (0 of {total} pending).**"
        )
    if codeowners_rule:
        rule_file = (
            codeowners_rule if isinstance(codeowners_rule, str) else CODEOWNERS_PATH
        )
        lines += [
            "",
            f"This PR changes `{rule_file}`: every owner-group must approve.",
        ]
    unapp_patterns = {s.pattern for s in coverage.unapprovable}
    lines += ["", "| Section | Files | Status |", "|---|---|---|"]
    for s in coverage.matched_sets:
        name = team_display_name(s.pattern, names)
        files = files_by_pattern.get(s.pattern, [])
        shown = files[:MAX_FILES_PER_SECTION]
        links = []
        for f in shown:
            digest = hashlib.sha256(f.encode()).hexdigest()
            # The label is one code span inside the link text. CommonMark
            # code spans bind tighter than link brackets, so brackets and
            # parens in a path can never form a nested link; backslash
            # escapes are not processed inside code spans, so none are added.
            # Only the span delimiter, the table-cell separator (GFM honours
            # `\|` even inside code spans) and line breaks need handling.
            label = (
                f.replace("`", "'")
                .replace("|", "\\|")
                .replace("\r", " ")
                .replace("\n", " ")
            )
            links.append(
                f"[`{label}`]({repo_url}/pull/{pr_number}/files#diff-{digest})"
            )
        if len(files) > MAX_FILES_PER_SECTION:
            links.append(f"+{len(files) - MAX_FILES_PER_SECTION} more")
        approvers_here = [a for a in coverage.approvers if a in s.members]
        if s.pattern in unapp_patterns:
            status = f"{SYM_WARNING} cannot be approved ({unapprovable_reason(s)})"
        elif approvers_here:
            status = f"{SYM_APPROVED} approved by " + ", ".join(
                "@" + a for a in approvers_here
            )
        elif s.unresolvable:
            status = f"{SYM_PENDING} pending (team/email owner)"
        else:
            status = f"{SYM_PENDING} pending"
        cells = "<br>".join(links) if links else "—"
        lines.append(f"| {name} | {cells} | {status} |")
    if coverage.unapprovable:
        lines += ["", "**Sections that cannot block:**", ""]
        for s in coverage.unapprovable:
            lines.append(
                f"- `{s.pattern}`: {SYM_WARNING} nobody can approve this section "
                f"({unapprovable_reason(s)}), so it does not block the status. "
                "Check its CODEOWNERS entry."
            )
    warnings = []
    for s in coverage.pending + coverage.unapprovable:
        if s.unresolvable:
            owners = ", ".join("`" + o + "`" for o in s.unresolvable)
            warnings.append(
                f"- `{s.pattern}`: {SYM_WARNING} {owners} — approvals for "
                "team/email owners are tracked by GitHub but not by this bot"
            )
        if s.invalid:
            owners = ", ".join("`" + o + "`" for o in s.invalid)
            warnings.append(
                f"- `{s.pattern}`: {SYM_WARNING} {owners} — GitHub reports "
                "these owners as unknown (usually: no write access to the "
                "repository); their approvals do not count"
            )
    if warnings:
        lines += ["", "**Unverifiable owners:**", ""]
        lines += warnings
    # Derived from the persistent culled state (plus this run's culls), so
    # the note survives later runs instead of vanishing after one.
    culled_set = {u.lower() for u in cull} | {u.lower() for u in (culled or [])}
    notes = []
    for s in coverage.satisfied:
        approvers_here = sorted(set(s.members) & set(coverage.approvers))
        removed_here = [m for m in s.members if m in culled_set]
        if removed_here and approvers_here:
            covered = ", ".join("@" + a for a in approvers_here)
            who = ", ".join("@" + m for m in removed_here)
            notes.append(f"- {who} removed from queue (covered by {covered})")
    if notes:
        lines += ["", "**Removed from review queue:**", ""]
        lines += notes
    if notices:
        lines += ["", "**Review-queue notices:**", ""]
        lines += notices
    if culled:
        state = json.dumps({"culled": sorted(set(culled))}, separators=(",", ":"))
        lines += ["", f"<!-- {STATE_MARKER} {state} -->"]
    lines += ["", "---", _footer()]
    return "\n".join(lines)


_UNSET: Any = object()


def upsert_comment(
    client: Any, pr_number: int, body: str, existing: Any = _UNSET
) -> bool:
    """Create or update the sticky comment.

    `existing` may carry an already-fetched `get_sticky_comment` result
    (including None for "no comment") to avoid listing comments twice.
    """
    if existing is _UNSET:
        existing = client.get_sticky_comment(pr_number)
    if existing is None:
        client.post_comment(pr_number, body)
        return True
    cid, old = existing
    if comment_body_hash(old) == comment_body_hash(body):
        return False
    try:
        client.patch_comment(cid, body)
    except ApiError as err:
        if err.status != 404:
            raise
        # The comment was deleted between listing and patching.
        client.post_comment(pr_number, body)
    return True


def _remove_and_verify(
    client: Any, pr: int, cull: list[str], errors: list[str], notices: list[str]
) -> list[str]:
    """DELETE `cull` from the review queue; return the logins really removed.

    GitHub answers the DELETE with the updated pull request, whose
    `requested_reviewers` shows who is still queued; if that is missing the
    queue is re-read. If the DELETE errors (possibly after GitHub applied
    it, e.g. a lost response), the queue is re-read to see what happened;
    anything still queued is reported as a failure.
    """
    if not cull:
        return []
    try:
        resp = client.remove_requested_reviewers(pr, cull)
    except ApiError as err:
        try:
            still = {u.lower() for u in client.get_requested_reviewers(pr)}
            removed = [u for u in cull if u.lower() not in still]
        except Exception:  # noqa: BLE001 - cannot tell; record nothing
            removed = []
        failed = [u for u in cull if u not in removed]
        if failed:
            who = ", ".join("@" + u for u in failed)
            errors.append(f"removing {who} from the review queue failed: {err}")
            notices.append(
                f"- removing {who} from the review queue failed; will retry on the next run"
            )
        return removed
    if isinstance(resp, dict) and isinstance(resp.get("requested_reviewers"), list):
        still = {
            str((u or {}).get("login", "")).lower() for u in resp["requested_reviewers"]
        }
    else:
        still = {u.lower() for u in client.get_requested_reviewers(pr)}
    return [u for u in cull if u.lower() not in still]


def _rerequest(
    client: Any, pr: int, logins: list[str]
) -> tuple[list[str], list[str], list[str]]:
    """Re-request `logins`; return (requested, rejected, transient_failures).

    A 422 means GitHub will never accept the login (e.g. no longer a
    collaborator). One bad login fails the whole batch, so on failure each
    login is retried alone to isolate it.
    """
    try:
        client.request_reviewers(pr, logins)
        return list(logins), [], []
    except ApiError as err:
        if len(logins) == 1:
            if err.status == 422:
                return [], list(logins), []
            return [], [], list(logins)
    done: list[str] = []
    rejected: list[str] = []
    retry: list[str] = []
    for u in logins:
        try:
            client.request_reviewers(pr, [u])
            done.append(u)
        except ApiError as err:
            (rejected if err.status == 422 else retry).append(u)
    return done, rejected, retry


@dataclass
class RunOutcome:
    pr: int
    matched_patterns: list[str]
    cull: list[str]
    changed: bool


def coverage_status(coverage: CoverageResult) -> tuple[str, str]:
    """(state, description) for the `review-coverage` commit status.

    Unapprovable sections never block; they are only mentioned.
    """
    total, pend = len(coverage.matched_sets), len(coverage.pending)
    unapp = len(coverage.unapprovable)
    if pend:
        return "failure", f"{pend} of {total} section(s) pending approval"
    if unapp:
        return (
            "success",
            f"All approvable sections approved ({unapp} cannot be approved)",
        )
    return "success", f"All {total} section(s) approved"


def _publish_status(
    client: Any, pr: int, sha: str | None, state: str, desc: str, dry_run: bool
) -> str | None:
    """Set the commit status; return an error message instead of raising."""
    repo_url = "https://github.com/" + os.environ.get(
        "GITHUB_REPOSITORY", "ubuntu/ubuntu-project-docs"
    )
    if dry_run:
        print(f"review-coverage: would set status {state}: {desc}")
        return None
    if not sha:
        return None
    try:
        client.set_status(sha, state, desc, f"{repo_url}/pull/{pr}")
    except ApiError as err:
        return f"setting the {STATUS_CONTEXT} status failed: {err}"
    return None


def _codeowners_file_changed(files: list[dict]) -> str | None:
    """The CODEOWNERS file (any GitHub location) a PR adds, edits, deletes
    or renames (either side of a rename), else None."""
    for f in files:
        for key in ("filename", "previous_filename"):
            if f.get(key) in CODEOWNERS_LOCATIONS:
                return str(f["filename"])
    return None


def run_coverage(client: Any, pr: int, dry_run: bool = False) -> RunOutcome | None:
    pr_data = client.get_pr(pr)
    if pr_data is None:
        raise RuntimeError(f"cannot fetch PR #{pr}")
    if pr_data.get("state") != "open":
        print(f"review-coverage: PR #{pr} is {pr_data.get('state')}; skipping")
        return None
    head_sha = (pr_data.get("head") or {}).get("sha")
    files = client.get_pr_files(pr)
    paths = [f["filename"] for f in files]
    co_text = client.get_base_codeowners()
    if co_text is None:
        print("review-coverage: cannot read base CODEOWNERS; skipping", file=sys.stderr)
        err = _publish_status(
            client, pr, head_sha, "failure", "cannot read base CODEOWNERS", dry_run
        )
        if err:
            raise RuntimeError(f"PR #{pr}: {err}")
        return None
    if not paths:
        print(f"review-coverage: PR #{pr} has no changed files; skipping")
        err = _publish_status(
            client, pr, head_sha, "success", "No changed files", dry_run
        )
        if err:
            raise RuntimeError(f"PR #{pr}: {err}")
        return None
    sets = parse_codeowners(
        co_text, unknown=unknown_owners_by_line(client.get_codeowners_errors())
    )
    # A CODEOWNERS change (at any GitHub location, including renames) must
    # be approved by every owner-group of the base branch, not just by one
    # owner of the CODEOWNERS line.
    rule_file = _codeowners_file_changed(files)
    codeowners_rule = rule_file is not None
    extra = all_owned_groups(sets) if codeowners_rule else []
    # The files API returns at most 3000 files; with a truncated list the
    # coverage (and the CODEOWNERS rule) cannot be trusted.
    changed_files = pr_data.get("changed_files")
    truncated = isinstance(changed_files, int) and changed_files > len(paths)
    author = (pr_data.get("user") or {}).get("login")
    coverage = compute_coverage(
        paths, sets, client.get_pr_reviews(pr), author=author, extra=extra
    )
    requested = client.get_requested_reviewers(pr)
    cull = compute_cull(requested, coverage)
    existing = client.get_sticky_comment(pr)
    # A culled reviewer who is back in the queue (re-requested by someone,
    # or by a re-request whose response was lost) is no longer tracked.
    requested_low = {r.lower() for r in requested}
    old_culled = [
        u
        for u in (parse_culled_state(existing[1]) if existing else [])
        if u not in requested_low
    ]
    notices: list[str] = []
    errors: list[str] = []
    if dry_run:
        culled = list(dict.fromkeys(old_culled + [u.lower() for u in cull]))
    else:
        removed_ok = _remove_and_verify(client, pr, cull, errors, notices)
        culled = list(dict.fromkeys(old_culled + [u.lower() for u in removed_ok]))
        readd = _readd_candidates(coverage, requested, culled, removed_ok, author)
        if readd:
            done, rejected, retry = _rerequest(client, pr, readd)
            # Re-requested logins leave the state; rejected ones can never
            # be re-requested, so tracking them would fail forever.
            settled = {u.lower() for u in done + rejected}
            culled = [u for u in culled if u not in settled]
            if rejected:
                notices.append(
                    "- "
                    + ", ".join("@" + u for u in rejected)
                    + " could not be re-requested (not requestable, HTTP 422);"
                    " no longer tracked"
                )
            if retry:
                who = ", ".join("@" + u for u in retry)
                notices.append(
                    f"- re-requesting {who} failed; will retry on the next run"
                )
                errors.append(f"re-requesting {who} failed")
        cull = removed_ok
    names = load_team_names(client.get_base_text(TEAMS_YAML_PATH) or "")
    files_by_pattern: dict[str, list[str]] = {}
    for s in coverage.matched_sets:
        files_by_pattern[s.pattern] = [
            p
            for p in paths
            if match_file(p, [s]) is not None and match_file(p, sets) is s
        ] or ([rule_file] if rule_file else [])
    if truncated:
        notices.append(
            f"- GitHub lists only {len(paths)} of this PR's {changed_files} "
            "changed files; coverage may be incomplete"
        )
    repo_url = "https://github.com/" + os.environ.get(
        "GITHUB_REPOSITORY", "ubuntu/ubuntu-project-docs"
    )
    body = render_comment(
        coverage,
        names,
        pr,
        files_by_pattern,
        repo_url,
        cull=cull,
        culled=culled,
        notices=notices,
        codeowners_rule=rule_file or False,
    )
    changed = False
    if dry_run:
        print(body)
    else:
        changed = upsert_comment(client, pr, body, existing=existing)
    state, desc = coverage_status(coverage)
    if truncated:
        state = "failure"
        desc = f"too many files to evaluate ({changed_files} changed)"
    err = _publish_status(client, pr, head_sha, state, desc, dry_run)
    if err:
        errors.append(err)
    if errors:
        # The comment and state are already consistent; now surface the
        # failure so the job goes red. The next run retries.
        raise RuntimeError(f"PR #{pr}: " + "; ".join(errors))
    return RunOutcome(pr, [s.pattern for s in coverage.matched_sets], cull, changed)


def dispatch_coverage_runs(client: Any, dry_run: bool = False) -> int:
    """Trigger one `workflow_dispatch` coverage run per open PR.

    Each run joins its PR's concurrency group, so a rescan can never race a
    review-triggered update of the same PR (GITHUB_TOKEN may trigger
    workflow_dispatch). Returns a process exit code.
    """
    try:
        prs = client.list_open_prs()
    except Exception as err:  # noqa: BLE001 - report and fail
        print(f"review-coverage: failed to list open PRs: {err}", file=sys.stderr)
        return 1
    ref = client._default_branch()
    failures = 0
    for n in prs:
        if dry_run:
            print(f"review-coverage: would dispatch coverage for PR #{n}")
            continue
        try:
            client.dispatch_workflow(REVIEW_COVERAGE_WORKFLOW, ref, {"pr": str(n)})
        except ApiError as err:
            failures += 1
            print(
                f"review-coverage: dispatch for PR #{n} failed: {err}", file=sys.stderr
            )
    return 1 if failures else 0


def make_client(read_only: bool = False) -> "GitHubClient":
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        print(
            "review-coverage: GITHUB_TOKEN and GITHUB_REPOSITORY must be set",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return GitHubClient(token, repo, read_only=read_only)


def _positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid PR number: {text!r}") from None
    if value <= 0:
        raise argparse.ArgumentTypeError(f"PR number must be positive, got {value}")
    return value


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--dry-run",
        action="store_true",
        default=argparse.SUPPRESS,
        help="print planned changes instead of writing",
    )
    parser = argparse.ArgumentParser(
        prog="review-coverage", description=__doc__, parents=[common]
    )
    sub = parser.add_subparsers(dest="command", required=True)
    p_cov = sub.add_parser(
        "coverage",
        help="post or update the review-coverage comment",
        parents=[common],
    )
    sel = p_cov.add_mutually_exclusive_group(required=True)
    sel.add_argument("--pr", type=_positive_int)
    sel.add_argument("--all-open", action="store_true")
    p_cov.add_argument(
        "--dispatch",
        action="store_true",
        help="with --all-open: trigger one per-PR workflow run instead of "
        "computing coverage inline",
    )
    p_sync = sub.add_parser(
        "sync-yaml", help="sync CODEOWNERS-teams.yaml", parents=[common]
    )
    sel = p_sync.add_mutually_exclusive_group(required=True)
    sel.add_argument("--pr", type=_positive_int)
    sel.add_argument("--base", action="store_true")
    p_drift = sub.add_parser(
        "drift-check",
        help="exit 1 if the committed teams yaml is stale",
        parents=[common],
    )
    p_drift.add_argument(
        "--local",
        action="store_true",
        help="compare files in the checked-out workspace instead of the API",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(
            argv, namespace=argparse.Namespace(dry_run=False)
        )
    except SystemExit as exc:
        # argparse exits 0 for --help and 2 for usage errors.
        if exc.code is None:
            return 0
        return exc.code if isinstance(exc.code, int) else 1
    try:
        client = (
            None
            if (args.command == "drift-check" and args.local)
            else make_client(read_only=args.dry_run)
        )
    except SystemExit:
        return 1
    if args.command == "coverage":
        if args.dispatch:
            if not args.all_open:
                print(
                    "review-coverage: --dispatch requires --all-open", file=sys.stderr
                )
                return 2
            return dispatch_coverage_runs(client, dry_run=args.dry_run)
        try:
            prs = [args.pr] if args.pr is not None else client.list_open_prs()
        except Exception as err:  # noqa: BLE001 - report and continue
            print(f"review-coverage: failed to list open PRs: {err}", file=sys.stderr)
            return 1
        failures = 0
        for n in prs:
            try:
                run_coverage(client, n, dry_run=args.dry_run)
            except Exception as err:  # noqa: BLE001 - isolate per-PR failures
                failures += 1
                print(f"review-coverage: PR #{n} failed: {err}", file=sys.stderr)
        return 1 if failures else 0
    if args.command == "sync-yaml":
        if args.pr is not None:
            try:
                status = sync_yaml_for_pr(client, args.pr, dry_run=args.dry_run)
            except Exception as err:  # noqa: BLE001
                print(f"review-coverage: sync-yaml failed: {err}", file=sys.stderr)
                return 1
            if status == "failed":
                return 1
            if status == "commented":
                # Fork PR: the diff comment is posted; fail the step so a
                # maintainer notices the yaml still needs applying (spec).
                return 1
            return 0
        try:
            sync_yaml_base(client, dry_run=args.dry_run)
        except Exception as err:  # noqa: BLE001
            print(f"review-coverage: sync-yaml --base failed: {err}", file=sys.stderr)
            return 1
        return 0
    return drift_check(client, local=args.local)


class ReadOnlyError(RuntimeError):
    """A write was attempted on a read-only (dry-run) client."""


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(f"HTTP {status}: {message[:300]}")
        self.status = status


class GitHubClient:
    RETRYABLE_METHODS = ("GET", "HEAD", "PUT", "DELETE", "PATCH")

    def __init__(self, token: str, repo: str, read_only: bool = False):
        self.token = token
        self.repo = repo
        # Dry-run: every non-GET request is refused, so nothing is written.
        self.read_only = read_only
        self._default_branch_name: str | None = None

    @staticmethod
    def _rate_limit_sleep(headers: Any) -> float:
        headers = headers or {}
        retry_after = headers.get("retry-after")
        if retry_after:
            try:
                return min(float(retry_after), MAX_SLEEP_SECONDS)
            except (TypeError, ValueError):
                pass
        reset = headers.get("x-ratelimit-reset")
        if reset:
            try:
                wait = float(reset) - time.time()
                return max(0.0, min(wait, MAX_SLEEP_SECONDS))
            except (TypeError, ValueError):
                pass
        # GitHub: without retry-after or reset, "wait for at least one
        # minute before retrying".
        return 60.0

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        body: Any | None = None,
        idempotent: bool | None = None,
    ) -> Any | None:
        """`idempotent` overrides the method-based retry policy (e.g. a
        last-write-wins POST such as a commit status is safe to repeat)."""
        if self.read_only and method not in ("GET", "HEAD"):
            raise ReadOnlyError(f"dry-run: refusing {method} {path}")
        url = API_BASE + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        if idempotent is None:
            idempotent = method in self.RETRYABLE_METHODS
        attempt = 0
        while True:
            attempt += 1
            try:
                req = urllib.request.Request(url, method=method)
                req.add_header("Authorization", "Bearer " + self.token)
                req.add_header("Accept", "application/vnd.github+json")
                req.add_header("X-GitHub-Api-Version", "2022-11-28")
                data = None
                if body is not None:
                    data = json.dumps(body).encode()
                    req.add_header("Content-Type", "application/json")
                with urllib.request.urlopen(req, data, timeout=30) as resp:
                    raw = resp.read().decode()
                    return json.loads(raw) if raw else None
            except urllib.error.HTTPError as err:
                status = err.code
                headers = err.headers or {}
                detail = err.read().decode(errors="replace")[:300]
                # Only a read may treat 404 as "absent"; a write that 404s
                # did not happen and must not be reported as success.
                if status == 404 and method in ("GET", "HEAD"):
                    return None
                # Primary limits: 429, or 403 with remaining=0. Secondary
                # limits: 403 carrying retry-after, or saying so in the body
                # (a bare 403 is otherwise a permission error: never retried).
                if status == 429 or (
                    status == 403
                    and (
                        headers.get("x-ratelimit-remaining") == "0"
                        or headers.get("retry-after")
                        or "secondary rate limit" in detail.lower()
                    )
                ):
                    if attempt > 5:
                        raise ApiError(status, detail) from None
                    time.sleep(self._rate_limit_sleep(headers))
                    continue
                if status in (500, 502, 503, 504):
                    if idempotent and attempt <= 3:
                        time.sleep(min(2 ** (attempt - 1), MAX_SLEEP_SECONDS))
                        continue
                    raise ApiError(status, detail) from None
                raise ApiError(status, detail) from None
            except (
                urllib.error.URLError,
                OSError,  # incl. TimeoutError while reading the body
                http.client.HTTPException,  # e.g. IncompleteRead
                ValueError,  # undecodable response body
            ) as err:
                # A non-idempotent request may already have reached GitHub;
                # replaying it could duplicate comments, requests or PRs.
                if idempotent and attempt <= 3:
                    time.sleep(min(2 ** (attempt - 1), MAX_SLEEP_SECONDS))
                    continue
                raise ApiError(0, f"{method} {path}: {err!r}") from None

    def get(self, path: str, **kw: Any) -> Any | None:
        return self.request("GET", path, **kw)

    def post(self, path: str, **kw: Any) -> Any | None:
        return self.request("POST", path, **kw)

    def patch(self, path: str, **kw: Any) -> Any | None:
        return self.request("PATCH", path, **kw)

    def delete(self, path: str, **kw: Any) -> Any | None:
        return self.request("DELETE", path, **kw)

    def get_all_pages(self, path: str, params: dict | None = None) -> list:
        out: list = []
        page = 1
        while True:
            q = dict(params or {})
            q["page"], q["per_page"] = page, 100
            batch = self.get(path, params=q)
            if batch is None:
                raise RuntimeError(
                    f"pagination failed for {path} (page {page}); aborting to avoid acting on partial data"
                )
            out.extend(batch)
            if not batch or len(batch) < 100:
                break
            page += 1
        return out

    def _default_branch(self) -> str:
        if self._default_branch_name is None:
            data = self.get(f"/repos/{self.repo}")
            self._default_branch_name = str((data or {}).get("default_branch", "main"))
        return str(self._default_branch_name)

    def _contents(self, repo_full: str, path: str, ref: str) -> str | None:
        data = self.get(f"/repos/{repo_full}/contents/{path}", params={"ref": ref})
        if not data or data.get("encoding") != "base64":
            return None
        return base64.b64decode(data["content"]).decode()

    def get_codeowners_errors(self) -> list:
        """CODEOWNERS problems GitHub reports for the default branch."""
        data = self.get(
            f"/repos/{self.repo}/codeowners/errors",
            params={"ref": self._default_branch()},
        )
        return (data or {}).get("errors") or []

    def get_pr(self, pr_number: int) -> Any | None:
        return self.get(f"/repos/{self.repo}/pulls/{pr_number}")

    def get_pr_files(self, pr_number: int) -> list:
        return self.get_all_pages(f"/repos/{self.repo}/pulls/{pr_number}/files")

    def get_pr_reviews(self, pr_number: int) -> list:
        return self.get_all_pages(f"/repos/{self.repo}/pulls/{pr_number}/reviews")

    def get_requested_reviewers(self, pr_number: int) -> list[str]:
        data = self.get(f"/repos/{self.repo}/pulls/{pr_number}/requested_reviewers")
        return [u["login"] for u in (data or {}).get("users", [])]

    def get_base_codeowners(self) -> str | None:
        """Base-branch CODEOWNERS from the first GitHub location that exists
        (`.github/`, root, `docs/`), as GitHub resolves it."""
        branch = self._default_branch()
        for loc in CODEOWNERS_LOCATIONS:
            text = self._contents(self.repo, loc, branch)
            if text is not None:
                return text
        return None

    def get_base_text(self, path: str) -> str | None:
        return self._contents(self.repo, path, self._default_branch())

    def get_ref_codeowners(self, repo_full: str, ref: str) -> str | None:
        return self._contents(repo_full, CODEOWNERS_PATH, ref)

    def get_head_yaml(self, pr_number: int) -> str | None:
        """Teams yaml at the PR head commit (sha, not the moving branch)."""
        head = (self.get_pr(pr_number) or {}).get("head") or {}
        ref = head.get("sha") or head.get("ref")
        if not ref:
            return None
        head_repo = (head.get("repo") or {}).get("full_name") or self.repo
        return self._contents(head_repo, TEAMS_YAML_PATH, ref)

    def delete_comment(self, comment_id: int) -> None:
        self.delete(f"/repos/{self.repo}/issues/comments/{comment_id}")

    def set_status(
        self, sha: str, state: str, description: str, target_url: str
    ) -> None:
        self.post(
            f"/repos/{self.repo}/statuses/{sha}",
            body={
                "state": state,
                "context": STATUS_CONTEXT,
                "description": description[:140],
                "target_url": target_url,
            },
            idempotent=True,  # last write wins: safe to retry
        )

    def dispatch_workflow(self, workflow: str, ref: str, inputs: dict) -> None:
        self.post(
            f"/repos/{self.repo}/actions/workflows/{workflow}/dispatches",
            body={"ref": ref, "inputs": inputs},
        )

    def get_sticky_comment(
        self, pr_number: int, marker: str = STICKY_MARKER
    ) -> tuple[int, str] | None:
        comments = self.get_all_pages(f"/repos/{self.repo}/issues/{pr_number}/comments")
        matches = _bot_sticky(comments, marker)
        if not matches:
            return None
        # Duplicate cleanup is a write: never in read-only (dry-run) mode.
        for cid, _ in [] if getattr(self, "read_only", False) else matches[:-1]:
            try:
                self.delete(f"/repos/{self.repo}/issues/comments/{cid}")
            except Exception as err:  # noqa: BLE001 - best-effort cleanup
                print(
                    f"review-coverage: could not remove duplicate sticky comment {cid}: {err}",
                    file=sys.stderr,
                )
        return matches[-1]

    def post_comment(self, pr_number: int, body: str) -> Any | None:
        return self.post(
            f"/repos/{self.repo}/issues/{pr_number}/comments", body={"body": body}
        )

    def patch_comment(self, comment_id: int, body: str) -> Any | None:
        return self.patch(
            f"/repos/{self.repo}/issues/comments/{comment_id}", body={"body": body}
        )

    def remove_requested_reviewers(
        self, pr_number: int, logins: list[str]
    ) -> Any | None:
        if not logins:
            return None
        return self.delete(
            f"/repos/{self.repo}/pulls/{pr_number}/requested_reviewers",
            body={"reviewers": logins},
        )

    def request_reviewers(self, pr_number: int, logins: list[str]) -> Any | None:
        if not logins:
            return None
        return self.post(
            f"/repos/{self.repo}/pulls/{pr_number}/requested_reviewers",
            body={"reviewers": logins},
        )

    def list_open_prs(self) -> list[int]:
        data = self.get_all_pages(f"/repos/{self.repo}/pulls", params={"state": "open"})
        return [p["number"] for p in data]


def _bot_sticky(comments: list[dict], marker: str) -> list[tuple[int, str]]:
    """Bot-authored comments carrying `marker`, oldest first.

    Only comments authored by the bot's own login are eligible: a
    PR-author comment that happens to start with the marker must never be
    mistaken for (or overwritten as) the bot's sticky comment.
    """
    out: list[tuple[int, str]] = []
    for c in comments:
        body = c.get("body") or ""
        user = (c.get("user") or {}).get("login", "")
        if body.lstrip().startswith(marker) and user == BOT_LOGIN:
            out.append((c["id"], body))
    return out


YAML_HEADER = (
    "# Display names for CODEOWNERS owner-groups.\n"
    "# Membership lives in CODEOWNERS; this file only maps patterns to names.\n"
)


def default_team_name(pattern: str) -> str:
    if pattern == "*":
        return "Technical authors"
    if pattern.endswith("/"):
        return pattern.rstrip("/").split("/")[-1]
    base = pattern.split("/")[-1]
    if "*" in base:
        prefix = base.split("*")[0].rstrip("-")
        if prefix.isalpha() and prefix.islower():
            return prefix.upper()
        return prefix or pattern
    return os.path.splitext(base)[0]


def parse_teams_yaml_ordered(text: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        entry = _parse_yaml_entry(line)
        if entry:
            out.append(entry)
    return out


def _yaml_quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def regenerate_yaml(
    existing: list[tuple[str, str]], sets: list[OwnerSet]
) -> tuple[str, bool]:
    known = dict(existing)
    seen: set[str] = set()
    lines = [YAML_HEADER]
    for s in sets:
        if not s.has_owners or s.pattern in seen:
            continue
        seen.add(s.pattern)
        name = known.get(s.pattern, default_team_name(s.pattern))
        lines.append(_yaml_quote(s.pattern) + ": " + _yaml_quote(name) + "\n")
    text = "".join(lines)
    old_entries = "".join(
        _yaml_quote(p) + ": " + _yaml_quote(n) + "\n" for p, n in existing
    )
    changed = text[len(YAML_HEADER) :] != old_entries
    return text, changed


class RefMoved(Exception):
    """The target branch no longer points at the commit the content was
    computed from (a newer push landed meanwhile)."""


def _ref_path(branch: str) -> str:
    """Percent-encode a branch name for a /git/ref(s)/heads/ URL path.

    Git allows `#`, `%` and `?` in branch names; unencoded, `#` truncates the
    path and `%xx` is decoded by GitHub, so the request would target another
    branch. `/` stays literal: it separates ref path segments.
    """
    return urllib.parse.quote(branch, safe="/")


def git_data_commit(
    client: Any,
    branch: str,
    path: str,
    content: str,
    expected_sha: str | None = None,
) -> bool:
    """Create a commit updating `path` on `branch` via the Git Data API.

    Returns False on any API failure (the real client raises ApiError, fakes
    may return None). Raises RefMoved if `expected_sha` is given and the
    branch head differs from it.
    """
    ref_path = _ref_path(branch)
    try:
        ref = client.get(f"/repos/{client.repo}/git/ref/heads/{ref_path}")
        if not ref:
            return False
        name = ref.get("ref")
        if name is not None and name != f"refs/heads/{branch}":
            print(
                f"review-coverage: ref lookup for {branch!r} returned {name!r}; "
                "refusing to write",
                file=sys.stderr,
            )
            return False
        head_sha = ref["object"]["sha"]
        if expected_sha and head_sha != expected_sha:
            raise RefMoved(
                f"{branch} moved from {expected_sha[:12]} to {head_sha[:12]}"
            )
        head_commit = client.get(f"/repos/{client.repo}/git/commits/{head_sha}")
        if not head_commit:
            return False
        blob = client.post(
            f"/repos/{client.repo}/git/blobs",
            body={"content": content, "encoding": "utf-8"},
        )
        if not blob:
            return False
        tree = client.post(
            f"/repos/{client.repo}/git/trees",
            body={
                "base_tree": head_commit["tree"]["sha"],
                "tree": [
                    {"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]}
                ],
            },
        )
        if not tree:
            return False
        commit = client.post(
            f"/repos/{client.repo}/git/commits",
            body={
                "message": "chore: sync CODEOWNERS-teams.yaml",
                "tree": tree["sha"],
                "parents": [head_sha],
            },
        )
        if not commit:
            return False
        return (
            client.patch(
                f"/repos/{client.repo}/git/refs/heads/{ref_path}",
                body={"sha": commit["sha"], "force": False},
            )
            is not None
        )
    except ApiError as err:
        print(f"review-coverage: commit to {branch} failed: {err}", file=sys.stderr)
        return False


def _clear_yaml_suggestion(client: Any, pr_number: int, dry_run: bool) -> None:
    """Delete a fork "suggested yaml" comment that no longer applies."""
    if dry_run:
        return
    sticky = client.get_sticky_comment(pr_number, marker=YAML_SYNC_MARKER)
    if sticky is None:
        return
    try:
        client.delete_comment(sticky[0])
    except ApiError as err:
        if err.status != 404:
            raise


def sync_yaml_for_pr(client: Any, pr_number: int, dry_run: bool = False) -> str:
    """Sync the teams yaml for a PR that touches CODEOWNERS.

    Returns one of: "noop", "committed", "commented", "failed".
    """
    paths = [f["filename"] for f in client.get_pr_files(pr_number)]
    if CODEOWNERS_PATH not in paths:
        _clear_yaml_suggestion(client, pr_number, dry_run)
        return "noop"
    head = (client.get_pr(pr_number) or {}).get("head") or {}
    branch = head.get("ref")
    head_sha = head.get("sha")
    head_repo_info = head.get("repo") or {}
    head_repo = head_repo_info.get("full_name") or ""
    # Same-repo requires an EXACT full_name match; a null/missing head.repo
    # (e.g. a deleted fork) or any mismatch is treated as a fork - never as
    # an implicit same-repo write target. `head.repo.fork` is NOT used: it
    # is true whenever the repository itself is a fork, even for a PR
    # between two of its own branches.
    is_fork = head_repo != client.repo
    # Read at the head commit, not the moving branch, and commit only on top
    # of that same commit (see git_data_commit's expected_sha).
    read_ref = head_sha or branch
    co_text = client.get_ref_codeowners(head_repo, read_ref) if branch else None
    if co_text is None or not branch:
        return "noop"
    sets = parse_codeowners(co_text)
    existing_text = client.get_head_yaml(pr_number) or ""
    existing = parse_teams_yaml_ordered(existing_text)
    new_text, changed = regenerate_yaml(existing, sets)
    if not changed:
        _clear_yaml_suggestion(client, pr_number, dry_run)
        return "noop"
    if dry_run:
        print(new_text)
        return "dry-run"
    if is_fork:
        proposed = "```yaml\n" + new_text + "```"
        body = (
            YAML_SYNC_MARKER
            + "\n\n"
            + "This PR changes `.github/CODEOWNERS`. Suggested update for "
            + f"`{TEAMS_YAML_PATH}` (maintainers: apply to this PR):"
            + "\n\n"
            + proposed
        )
        sticky = client.get_sticky_comment(pr_number, marker=YAML_SYNC_MARKER)
        if sticky is None:
            client.post_comment(pr_number, body)
        elif comment_body_hash(sticky[1]) != comment_body_hash(body):
            client.patch_comment(sticky[0], body)
        print(
            "review-coverage: fork PR - posted suggested teams-yaml; "
            "a maintainer must apply it before merge",
            file=sys.stderr,
        )
        return "commented"
    if branch == client._default_branch():
        # Never write straight to the default branch, even if a same-repo
        # PR's head happens to be named the same as it.
        print(
            f"review-coverage: refusing to commit teams yaml to default branch {branch}",
            file=sys.stderr,
        )
        return "failed"
    try:
        ok = git_data_commit(
            client, branch, TEAMS_YAML_PATH, new_text, expected_sha=head_sha
        )
    except RefMoved as err:
        # The newer push triggers its own run, which syncs from fresh data.
        print(f"review-coverage: {err}; skipping stale sync", file=sys.stderr)
        return "noop"
    return "committed" if ok else "failed"


def sync_yaml_base(client: Any, dry_run: bool = False) -> bool:
    """After a CODEOWNERS merge to main: open a bot PR if the yaml drifted.

    Returns True if a sync PR was opened (or would be, in dry-run mode) and
    False for a benign no-op (nothing drifted, or a sync PR is already
    open). Raises on any unexpected write failure so callers can surface it.
    """
    co_text = client.get_base_codeowners()
    yaml_text = client.get_base_text(TEAMS_YAML_PATH)
    if co_text is None:
        raise RuntimeError("cannot read base CODEOWNERS")
    sets = parse_codeowners(co_text)
    new_text, changed = regenerate_yaml(parse_teams_yaml_ordered(yaml_text or ""), sets)
    if not changed:
        return False
    if dry_run:
        print(new_text)
        return True
    branch = "review-coverage-bot/update-teams-yaml"
    base_branch = client._default_branch()
    branch_path, base_path = _ref_path(branch), _ref_path(base_branch)
    existing_ref = client.get(f"/repos/{client.repo}/git/ref/heads/{branch_path}")
    if existing_ref:
        # The `head` filter takes `owner:branch`; `owner/repo:branch`
        # silently matches nothing.
        owner = client.repo.split("/", 1)[0]
        open_prs = client.get_all_pages(
            f"/repos/{client.repo}/pulls",
            params={"state": "open", "head": f"{owner}:{branch}"},
        )
        if open_prs:
            print("review-coverage: sync PR already open; nothing to do")
            return False
        # Stale branch with no open PR: reset it onto the default branch
        # before reusing it, instead of stacking commits on old history.
        src = client.get(f"/repos/{client.repo}/git/ref/heads/{base_path}")
        if not src:
            raise RuntimeError("cannot read default branch ref")
        client.patch(
            f"/repos/{client.repo}/git/refs/heads/{branch_path}",
            body={"sha": src["object"]["sha"], "force": True},
        )
    else:
        src = client.get(f"/repos/{client.repo}/git/ref/heads/{base_path}")
        if not src:
            raise RuntimeError("cannot read default branch ref")
        created = client.post(
            f"/repos/{client.repo}/git/refs",
            body={"ref": f"refs/heads/{branch}", "sha": src["object"]["sha"]},
        )
        if created is None:
            raise RuntimeError("failed to create sync branch")
    if not git_data_commit(client, branch, TEAMS_YAML_PATH, new_text):
        raise RuntimeError("failed to commit teams yaml")
    pr = client.post(
        f"/repos/{client.repo}/pulls",
        body={
            "title": "chore: sync CODEOWNERS-teams.yaml with CODEOWNERS",
            "head": branch,
            "base": base_branch,
            "body": "Automatic display-name sync by the review-coverage bot.",
        },
    )
    if not pr:
        raise RuntimeError(
            "branch updated but opening the sync PR failed "
            "(check 'Allow GitHub Actions to create pull requests')"
        )
    print(f"review-coverage: opened sync PR {pr.get('html_url', '')}")
    return True


def drift_check(client: Any, local: bool = False) -> int:
    """Exit 0 when the teams yaml matches CODEOWNERS, 1 otherwise.

    With local=True, read both files from the checked-out workspace (used by
    CI to validate the PR tree); otherwise fetch them from the default branch.
    """
    if local:
        try:
            co_text = open(CODEOWNERS_PATH).read()
            yaml_text = open(TEAMS_YAML_PATH).read()
        except OSError as err:
            print(f"review-coverage: cannot read local files: {err}", file=sys.stderr)
            return 1
    else:
        co_text = client.get_base_codeowners()
        yaml_text = client.get_base_text(TEAMS_YAML_PATH)
        if co_text is None or yaml_text is None:
            print(
                "review-coverage: cannot read CODEOWNERS or teams yaml",
                file=sys.stderr,
            )
            return 1
    sets = parse_codeowners(co_text)
    _, changed = regenerate_yaml(parse_teams_yaml_ordered(yaml_text), sets)
    if changed:
        print("CODEOWNERS-teams.yaml is out of date with CODEOWNERS")
        return 1
    print("CODEOWNERS-teams.yaml is up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Weekly issue and PR queue report for ubuntu-project-docs.

Fetches open-issue and open-PR statistics via the GitHub GraphQL API,
formats a summary message, and posts it to Mattermost and Matrix.

Environment variables:
  GITHUB_TOKEN        (required) GitHub API token — auto-set in Actions.
  GITHUB_REPOSITORY   (required) owner/repo slug — auto-set in Actions.

  MATTERMOST_TOKEN       Bot-user token [secret]; notif. skipped if absent.
  MATTERMOST_CHANNEL_ID  Channel ID [secret]; notification skipped if absent.
  MATTERMOST_URL         Base URL [var]; default: https://chat.canonical.com.

  MATRIX_TOKEN           Access token [secret]; notification skipped if absent.
  MATRIX_ROOM_ID         Room ID [secret]; notification skipped if absent.
  MATRIX_HOMESERVER      Homeserver URL [var]; default: https://ubuntu.com.
"""

import html
import json
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

GRAPHQL_URL = "https://api.github.com/graphql"
TWO_WEEKS = timedelta(weeks=2)

# Report structure — the single source of truth for message content.
#
# Each format (Markdown, plain text, HTML) is rendered from this one
# definition, so labels, order, and columns only ever need editing here.
# ``{count}`` and ``{url}`` are filled in per row when the report is built.
REPORT_TITLE = "📋 Ubuntu Project Docs — Issue & PR Queue"
REPORT_INTRO = "Weekly snapshot of issues and PRs in the {repo_link} repo."
REPORT_REPO_NAME = "ubuntu-project-docs"

# Per-section row definitions: (label, stats-attribute, filter-URL key).
# The stats attribute is read from the IssueStats / PRStats instance.
ISSUE_ROWS: tuple[tuple[str, str, str], ...] = (
    ("✅ Triaged", "triaged", "triaged"),
    ("⚠️ Untriaged", "untriaged", "untriaged"),
)
PR_ROWS: tuple[tuple[str, str, str], ...] = (
    ("📝 Draft", "draft", "draft"),
    ("🕐 Older than 2 weeks", "old", "old"),
    ("👀 Awaiting review", "unreviewed", "unreviewed"),
    ("✅ Ready to merge", "approved", "approved"),
    ("🔄 Changes requested", "changes_requested", "changes_requested"),
)
TABLE_COLUMNS = ("Status", "Count", "GitHub filter")


# Domain models


@dataclass
class IssueStats:
    """Counts of open issues by triage status."""

    triaged: int
    untriaged: int

    @property
    def total(self) -> int:
        """Total open issue count."""
        return self.triaged + self.untriaged


@dataclass
class PRStats:
    """Counts of open pull requests by review/draft status."""

    draft: int
    old: int
    unreviewed: int
    approved: int
    changes_requested: int
    total: int


@dataclass
class ReportRow:
    """A single row of a report section: a label, a count, and a filter URL."""

    label: str
    count: int
    url: str


@dataclass
class ReportSection:
    """A titled section of the report containing a table of rows."""

    heading: str
    rows: list[ReportRow]


@dataclass
class Report:
    """The full report as structured data — the single source of truth."""

    title: str
    intro: str
    repo_url: str
    repo_name: str
    sections: list[ReportSection] = field(default_factory=list)


@dataclass
class Config:
    """Runtime configuration loaded from environment variables."""

    github_token: str
    repo_slug: str
    mattermost_token: str
    mattermost_channel_id: str
    mattermost_url: str
    matrix_token: str
    matrix_room_id: str
    matrix_homeserver: str

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.

        Returns:
            Populated Config instance.

        Raises:
            KeyError: If GITHUB_TOKEN or GITHUB_REPOSITORY is not set.
        """
        return cls(
            github_token=os.environ["GITHUB_TOKEN"],
            repo_slug=os.environ["GITHUB_REPOSITORY"],
            mattermost_token=os.environ.get("MATTERMOST_TOKEN", ""),
            mattermost_channel_id=os.environ.get("MATTERMOST_CHANNEL_ID", ""),
            mattermost_url=os.environ.get("MATTERMOST_URL")
            or "https://chat.canonical.com",
            matrix_token=os.environ.get("MATRIX_TOKEN", ""),
            matrix_room_id=os.environ.get("MATRIX_ROOM_ID", ""),
            matrix_homeserver=os.environ.get("MATRIX_HOMESERVER")
            or "https://ubuntu.com",
        )

    @property
    def owner(self) -> str:
        """Repository owner extracted from the owner/repo slug."""
        return self.repo_slug.split("/")[0]

    @property
    def repo(self) -> str:
        """Repository name extracted from the owner/repo slug."""
        return self.repo_slug.split("/")[1]

    @property
    def repo_url(self) -> str:
        """Full GitHub URL for the repository."""
        return f"https://github.com/{self.repo_slug}"


# HTTP helper


def _http_json_request(
    url: str,
    token: str,
    method: str = "GET",
    body: dict[str, Any] | None = None,
) -> Any:
    """Make an authenticated JSON HTTP request.

    Args:
        url: Full request URL.
        token: Bearer token for the Authorization header.
        method: HTTP method (GET, POST, PUT).
        body: Optional JSON-serializable request body.

    Returns:
        Parsed JSON response.
    """
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


# GitHub API


def _github_graphql(
    token: str, query: str, variables: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Execute a GitHub GraphQL query and return the data field.

    Args:
        token: GitHub API token.
        query: GraphQL query string.
        variables: Optional query variables.

    Returns:
        The `data` portion of the GraphQL response.

    Raises:
        RuntimeError: If the API response contains errors.
    """
    result: dict[str, Any] = _http_json_request(
        GRAPHQL_URL, token, "POST", {"query": query, "variables": variables or {}}
    )
    errors = result.get("errors")
    if errors:
        raise RuntimeError(f"GraphQL errors: {errors}")
    return result["data"]


def fetch_issue_stats(cfg: Config) -> IssueStats:
    """Fetch counts of triaged and untriaged open issues.

    Args:
        cfg: Runtime configuration.

    Returns:
        IssueStats with triaged and untriaged counts.
    """
    query = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        allOpen: issues(states: OPEN) { totalCount }
        untriaged: issues(states: OPEN, filterBy: { labels: ["untriaged"] }) { totalCount }
      }
    }
    """
    data = _github_graphql(
        cfg.github_token, query, {"owner": cfg.owner, "repo": cfg.repo}
    )
    untriaged = data["repository"]["untriaged"]["totalCount"]
    total = data["repository"]["allOpen"]["totalCount"]
    return IssueStats(triaged=total - untriaged, untriaged=untriaged)


def _classify_pr(pr: dict[str, Any], cutoff: datetime) -> dict[str, int]:
    """Return incremental category counts for a single open PR.

    reviewDecision semantics:
        APPROVED            All required reviewers have approved.
        CHANGES_REQUESTED   At least one reviewer requested changes.
        REVIEW_REQUIRED     At least one required reviewer hasn't reviewed yet.
        None                No review rules apply — nothing blocking merge.

    Draft PRs are counted only in the draft bucket; review state is ignored.

    Args:
        pr: A pullRequests.nodes entry from the GitHub GraphQL response.
        cutoff: Datetime before which a PR is considered older than 2 weeks.

    Returns:
        Dict of category increments (all keys present, zero if not matching).
    """
    counts: dict[str, int] = {
        "draft": 0,
        "old": 0,
        "unreviewed": 0,
        "approved": 0,
        "changes_requested": 0,
    }
    created_at = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
    if created_at < cutoff:
        counts["old"] = 1

    if pr["isDraft"]:
        counts["draft"] = 1
        return counts  # skip review-state classification for drafts

    decision = pr["reviewDecision"]
    if decision == "CHANGES_REQUESTED":
        counts["changes_requested"] = 1
    elif decision == "REVIEW_REQUIRED":
        counts["unreviewed"] = 1
    else:
        # APPR'D or None (no req. reviews) — unblocked from a review persp.
        counts["approved"] = 1

    return counts


def fetch_pr_stats(cfg: Config) -> PRStats:
    """Fetch open PR counts by category, paginating through all open PRs.

    Args:
        cfg: Runtime configuration.

    Returns:
        PRStats with counts per status category.
    """
    query = """
    query($owner: String!, $repo: String!, $cursor: String) {
      repository(owner: $owner, name: $repo) {
        pullRequests(states: OPEN, first: 100, after: $cursor) {
          pageInfo { hasNextPage endCursor }
          nodes { isDraft createdAt reviewDecision }
        }
      }
    }
    """
    totals: dict[str, int] = {
        "draft": 0,
        "old": 0,
        "unreviewed": 0,
        "approved": 0,
        "changes_requested": 0,
        "total": 0,
    }
    cutoff = datetime.now(timezone.utc) - TWO_WEEKS
    cursor: str | None = None

    while True:
        data = _github_graphql(
            cfg.github_token,
            query,
            {"owner": cfg.owner, "repo": cfg.repo, "cursor": cursor},
        )
        page = data["repository"]["pullRequests"]
        for pr in page["nodes"]:
            totals["total"] += 1
            for key, val in _classify_pr(pr, cutoff).items():
                totals[key] += val
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    return PRStats(**totals)


# URL building


def _issue_url(repo_url: str, extra: str) -> str:
    return f"{repo_url}/issues?q={urllib.parse.quote_plus(f'is:open is:issue{extra}')}"


def _pr_url(repo_url: str, extra: str) -> str:
    return f"{repo_url}/pulls?q={urllib.parse.quote_plus(f'is:open is:pr{extra}')}"


def build_filter_urls(repo_url: str) -> dict[str, str]:
    """Build GitHub filter URLs for each report category.

    Args:
        repo_url: Base URL of the GitHub repository.

    Returns:
        Dict mapping category names to GitHub filter URLs.
    """
    return {
        "triaged": _issue_url(repo_url, " -label:untriaged"),
        "untriaged": _issue_url(repo_url, " label:untriaged"),
        "draft": _pr_url(repo_url, " draft:true"),
        # GitHub has no native age filter; sort oldest-first as a visual proxy.
        "old": _pr_url(repo_url, " sort:created-asc"),
        "unreviewed": _pr_url(repo_url, " review:required draft:false"),
        "approved": _pr_url(repo_url, " review:approved draft:false"),
        "changes_requested": _pr_url(repo_url, " review:changes_requested draft:false"),
    }


# Message formatting
#
# The report is assembled once as a Report model (build_report), then each
# renderer below turns that same model into a specific output format. Message
# content — titles, labels, section order — is defined once in the module-level
# REPORT_* / *_ROWS constants.


def build_report(
    issues: IssueStats, prs: PRStats, urls: dict[str, str], repo_url: str
) -> Report:
    """Assemble the report model from stats, using the module-level layout.

    Args:
        issues: Issue statistics.
        prs: PR statistics.
        urls: GitHub filter URLs keyed by category name.
        repo_url: Repository URL used in the header link.

    Returns:
        A fully populated Report ready to be rendered into any format.
    """

    def rows(stats: Any, spec: tuple[tuple[str, str, str], ...]) -> list[ReportRow]:
        return [
            ReportRow(label=label, count=getattr(stats, attr), url=urls[url_key])
            for label, attr, url_key in spec
        ]

    return Report(
        title=REPORT_TITLE,
        intro=REPORT_INTRO,
        repo_url=repo_url,
        repo_name=REPORT_REPO_NAME,
        sections=[
            ReportSection(f"🐛 Issues ({issues.total} open)", rows(issues, ISSUE_ROWS)),
            ReportSection(f"🔀 Pull Requests ({prs.total} open)", rows(prs, PR_ROWS)),
        ],
    )


def render_markdown(report: Report) -> str:
    """Render the report as Markdown for Mattermost.

    Args:
        report: The report model.

    Returns:
        Formatted Markdown string.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    repo_link = f"[{report.repo_name}]({report.repo_url})"
    lines = [
        f"## {report.title} ({today})",
        "",
        report.intro.format(repo_link=repo_link),
    ]
    header = f"| {' | '.join(TABLE_COLUMNS)} |"
    divider = "|:--|--:|---|"
    for section in report.sections:
        lines += ["", f"### {section.heading}", "", header, divider]
        for r in section.rows:
            lines.append(f"| {r.label} | **{r.count}** | [view]({r.url}) |")
    return "\n".join(lines) + "\n"


def render_plain_text(report: Report) -> str:
    """Render the report as plain text for the Matrix message body field.

    The Matrix spec requires the `body` field to be plain text, so this
    avoids all Markdown syntax and renders correctly in every Matrix client.

    Args:
        report: The report model.

    Returns:
        Formatted plain text string (no Markdown syntax).
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        f"{report.title} ({today})",
        "",
        report.intro.format(repo_link=report.repo_name),
    ]
    for section in report.sections:
        lines += ["", section.heading]
        for r in section.rows:
            lines.append(f"  {r.label}: {r.count}")
    return "\n".join(lines) + "\n"


def render_html(report: Report) -> str:
    """Render the report as HTML for the Matrix formatted_body field.

    Args:
        report: The report model.

    Returns:
        HTML string suitable for Matrix formatted_body.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    repo_link = f"<a href='{report.repo_url}'>{html.escape(report.repo_name)}</a>"
    parts = [
        f"<h2>{html.escape(f'{report.title} ({today})')}</h2>",
        f"<p>{html.escape(report.intro).format(repo_link=repo_link)}</p>",
    ]
    header_cells = "".join(f"<th>{html.escape(c)}</th>" for c in TABLE_COLUMNS)
    table_head = f"<table><thead><tr>{header_cells}</tr></thead><tbody>"
    table_foot = "</tbody></table>"
    for section in report.sections:
        parts.append(f"<h3>{html.escape(section.heading)}</h3>")
        parts.append(table_head)
        for r in section.rows:
            parts.append(
                f"<tr><td>{html.escape(r.label)}</td>"
                f"<td align='right'><strong>{r.count}</strong></td>"
                f"<td><a href='{r.url}'>view</a></td></tr>"
            )
        parts.append(table_foot)
    return "".join(parts)


# Mattermost


def _mm_api(
    cfg: Config, method: str, path: str, body: dict[str, Any] | None = None
) -> Any:
    """Call the Mattermost REST API."""
    return _http_json_request(
        f"{cfg.mattermost_url.rstrip('/')}/api/v4{path}",
        cfg.mattermost_token,
        method,
        body,
    )


def send_mattermost(cfg: Config, message: str) -> None:
    """Post a Markdown message to the configured Mattermost channel.

    Args:
        cfg: Runtime configuration.
        message: Markdown-formatted message text.
    """
    if not cfg.mattermost_token or not cfg.mattermost_channel_id:
        print(
            "MATTERMOST_TOKEN or MATTERMOST_CHANNEL_ID not set — skipping Mattermost."
        )
        return
    _mm_api(
        cfg,
        "POST",
        "/posts",
        {"channel_id": cfg.mattermost_channel_id, "message": message},
    )
    print(f"✓ Sent to Mattermost channel '{cfg.mattermost_channel_id}'")


# Matrix


def _matrix_api(
    cfg: Config, method: str, path: str, body: dict[str, Any] | None = None
) -> Any:
    """Call the Matrix client-server API."""
    return _http_json_request(
        f"{cfg.matrix_homeserver.rstrip('/')}{path}", cfg.matrix_token, method, body
    )


def send_matrix(cfg: Config, body_plain: str, body_html: str) -> None:
    """Post a message to the configured Matrix room.

    Sends with both a plain-text body and an HTML formatted_body as required
    by the Matrix client-server specification (MSC1767 / m.room.message).

    Args:
        cfg: Runtime configuration.
        body_plain: Plain text version of the message (no Markdown syntax).
        body_html: HTML version of the message for clients that support it.
    """
    if not cfg.matrix_token or not cfg.matrix_room_id:
        print("MATRIX_TOKEN or MATRIX_ROOM_ID not set — skipping Matrix.")
        return
    txn_id = int(time.time() * 1000)
    _matrix_api(
        cfg,
        "PUT",
        f"/_matrix/client/v3/rooms/{urllib.parse.quote(cfg.matrix_room_id)}/send/m.room.message/{txn_id}",
        {
            "msgtype": "m.text",
            "body": body_plain,
            "format": "org.matrix.custom.html",
            "formatted_body": body_html,
        },
    )
    print(f"✓ Sent to Matrix room '{cfg.matrix_room_id}'")


# Entry point


def main() -> None:
    """Fetch queue stats, build the report, and send it to Mattermost and Matrix."""
    cfg = Config.from_env()

    print("Fetching issue counts…")
    issues = fetch_issue_stats(cfg)
    print(f"  Triaged: {issues.triaged}, Untriaged: {issues.untriaged}")

    print("Fetching PR stats…")
    prs = fetch_pr_stats(cfg)
    print(
        f"  Draft: {prs.draft}, Old (>2w): {prs.old}, "
        f"Awaiting review: {prs.unreviewed}, "
        f"Ready: {prs.approved}, Changes requested: {prs.changes_requested}"
    )

    urls = build_filter_urls(cfg.repo_url)
    report = build_report(issues, prs, urls, cfg.repo_url)
    message_md = render_markdown(report)
    message_plain = render_plain_text(report)
    message_html = render_html(report)

    print("\n── Message preview ──────────────────────────────────────────────")
    print(message_md)
    print("─────────────────────────────────────────────────────────────────\n")

    send_mattermost(cfg, message_md)
    send_matrix(cfg, message_plain, message_html)
    print("Done.")


if __name__ == "__main__":
    main()

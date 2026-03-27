#!/usr/bin/env python3
"""Weekly issue and PR queue report for ubuntu-project-docs.

Fetches open-issue and open-PR statistics via the GitHub GraphQL API,
formats a summary message, and posts it to Mattermost and Matrix.

Environment variables:
    GITHUB_TOKEN        (required) GitHub API token — auto-set in Actions.
    GITHUB_REPOSITORY   (required) owner/repo slug — auto-set in Actions.

    MATTERMOST_TOKEN       Bot-user token [secret]; notification skipped if absent.
    MATTERMOST_CHANNEL_ID  Channel ID [secret]; notification skipped if absent.
    MATTERMOST_URL         Base URL [var]; default: https://chat.canonical.com.

    MATRIX_TOKEN           Access token [secret]; notification skipped if absent.
    MATRIX_ROOM_ID         Room ID [secret]; notification skipped if absent.
    MATRIX_HOMESERVER      Homeserver URL [var]; default: https://ubuntu.com.
"""

import json
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

GRAPHQL_URL = "https://api.github.com/graphql"
TWO_WEEKS = timedelta(weeks=2)


# ── Domain models ──────────────────────────────────────────────────────────


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
            mattermost_url=os.environ.get("MATTERMOST_URL") or "https://chat.canonical.com",
            matrix_token=os.environ.get("MATRIX_TOKEN", ""),
            matrix_room_id=os.environ.get("MATRIX_ROOM_ID", ""),
            matrix_homeserver=os.environ.get("MATRIX_HOMESERVER") or "https://ubuntu.com",
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


# ── HTTP helper ────────────────────────────────────────────────────────────


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


# ── GitHub API ─────────────────────────────────────────────────────────────


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
        triaged: issues(states: OPEN, filterBy: { labels: ["triaged"] }) { totalCount }
      }
    }
    """
    data = _github_graphql(cfg.github_token, query, {"owner": cfg.owner, "repo": cfg.repo})
    triaged = data["repository"]["triaged"]["totalCount"]
    total = data["repository"]["allOpen"]["totalCount"]
    return IssueStats(triaged=triaged, untriaged=total - triaged)


def _classify_pr(pr: dict[str, Any], cutoff: datetime) -> dict[str, int]:
    """Return incremental category counts for a single open PR.

    reviewDecision semantics:
        APPROVED            All required reviewers have approved.
        CHANGES_REQUESTED   At least one reviewer requested changes.
        REVIEW_REQUIRED     At least one required reviewer hasn't reviewed yet.
        None                No review rules apply — nothing blocking merge.

    Draft PRs are counted only in the draft bucket; their review state is ignored.

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
        # APPROVED or None (no required reviewers) — unblocked from a review perspective
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
            cfg.github_token, query, {"owner": cfg.owner, "repo": cfg.repo, "cursor": cursor}
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


# ── URL building ───────────────────────────────────────────────────────────


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
        "triaged": _issue_url(repo_url, " label:triaged"),
        "untriaged": _issue_url(repo_url, " -label:triaged"),
        "draft": _pr_url(repo_url, " draft:true"),
        # GitHub has no native age filter; sort oldest-first as a visual proxy.
        "old": _pr_url(repo_url, " sort:created-asc"),
        "unreviewed": _pr_url(repo_url, " review:required draft:false"),
        "approved": _pr_url(repo_url, " review:approved draft:false"),
        "changes_requested": _pr_url(repo_url, " review:changes_requested draft:false"),
    }


# ── Message formatting ─────────────────────────────────────────────────────


def build_markdown(
    issues: IssueStats, prs: PRStats, urls: dict[str, str], repo_url: str
) -> str:
    """Format the Markdown report message for Mattermost.

    Args:
        issues: Issue statistics.
        prs: PR statistics.
        urls: GitHub filter URLs keyed by category name.
        repo_url: Repository URL used in the header link.

    Returns:
        Formatted Markdown string.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return (
        f"## 📋 Ubuntu Project Docs — Issue & PR Queue ({today})\n"
        "\n"
        "Weekly snapshot of open issues and pull requests"
        f" in the [ubuntu-project-docs]({repo_url}) repository.\n"
        "\n"
        f"### 🐛 Issues ({issues.total} open)\n"
        "\n"
        "| Status | Count | GitHub filter |\n"
        "|:--|--:|:--|\n"
        f"| ✅ Triaged | **{issues.triaged}** | [view]({urls['triaged']}) |\n"
        f"| ⚠️ Untriaged | **{issues.untriaged}** | [view]({urls['untriaged']}) |\n"
        "\n"
        f"### 🔀 Pull Requests ({prs.total} open)\n"
        "\n"
        "| Status | Count | GitHub filter |\n"
        "|:--|--:|:--|\n"
        f"| 📝 Draft | **{prs.draft}** | [view]({urls['draft']}) |\n"
        f"| 🕐 Older than 2 weeks | **{prs.old}** | [view]({urls['old']}) |\n"
        f"| 👀 Awaiting review | **{prs.unreviewed}** | [view]({urls['unreviewed']}) |\n"
        f"| ✅ Ready to merge | **{prs.approved}** | [view]({urls['approved']}) |\n"
        f"| 🔄 Changes requested | **{prs.changes_requested}** |"
        f" [view]({urls['changes_requested']}) |\n"
    )


def build_plain_text(issues: IssueStats, prs: PRStats) -> str:
    """Format a plain-text summary for the Matrix message body field.

    The Matrix spec requires the `body` field to be plain text.
    This function avoids all Markdown syntax so it renders correctly in
    every Matrix client.

    Args:
        issues: Issue statistics.
        prs: PR statistics.

    Returns:
        Formatted plain text string (no Markdown syntax).
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return (
        f"📋 Ubuntu Project Docs — Issue & PR Queue ({today})\n"
        "\n"
        "Weekly snapshot of open issues and pull requests"
        " in the ubuntu-project-docs repository.\n"
        "\n"
        f"🐛 Issues ({issues.total} open)\n"
        f"  ✅ Triaged: {issues.triaged}\n"
        f"  ⚠️ Untriaged: {issues.untriaged}\n"
        "\n"
        f"🔀 Pull Requests ({prs.total} open)\n"
        f"  📝 Draft: {prs.draft}\n"
        f"  🕐 Older than 2 weeks: {prs.old}\n"
        f"  👀 Awaiting review: {prs.unreviewed}\n"
        f"  ✅ Ready to merge: {prs.approved}\n"
        f"  🔄 Changes requested: {prs.changes_requested}\n"
    )


def build_html(
    issues: IssueStats, prs: PRStats, urls: dict[str, str], repo_url: str
) -> str:
    """Format the HTML report message for Matrix formatted_body.

    Args:
        issues: Issue statistics.
        prs: PR statistics.
        urls: GitHub filter URLs keyed by category name.
        repo_url: Repository URL used in the header link.

    Returns:
        HTML string suitable for Matrix formatted_body.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def row(label: str, count: int, url: str) -> str:
        return (
            f"<tr><td>{label}</td>"
            f"<td align='right'><strong>{count}</strong></td>"
            f"<td><a href='{url}'>view</a></td></tr>"
        )

    table_head = "<table><thead><tr><th>Status</th><th>Count</th><th>GitHub filter</th></tr></thead><tbody>"
    table_foot = "</tbody></table>"

    return (
        f"<h2>📋 Ubuntu Project Docs — Issue &amp; PR Queue ({today})</h2>"
        f"<p>Weekly snapshot of open issues and pull requests in the"
        f" <a href='{repo_url}'>ubuntu-project-docs</a> repository.</p>"
        f"<h3>🐛 Issues ({issues.total} open)</h3>"
        f"{table_head}"
        f"{row('✅ Triaged', issues.triaged, urls['triaged'])}"
        f"{row('⚠️ Untriaged', issues.untriaged, urls['untriaged'])}"
        f"{table_foot}"
        f"<h3>🔀 Pull Requests ({prs.total} open)</h3>"
        f"{table_head}"
        f"{row('📝 Draft', prs.draft, urls['draft'])}"
        f"{row('🕐 Older than 2 weeks', prs.old, urls['old'])}"
        f"{row('👀 Awaiting review', prs.unreviewed, urls['unreviewed'])}"
        f"{row('✅ Ready to merge', prs.approved, urls['approved'])}"
        f"{row('🔄 Changes requested', prs.changes_requested, urls['changes_requested'])}"
        f"{table_foot}"
    )


# ── Mattermost ─────────────────────────────────────────────────────────────


def _mm_api(cfg: Config, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
    """Call the Mattermost REST API."""
    return _http_json_request(
        f"{cfg.mattermost_url.rstrip('/')}/api/v4{path}", cfg.mattermost_token, method, body
    )


def send_mattermost(cfg: Config, message: str) -> None:
    """Post a Markdown message to the configured Mattermost channel.

    Args:
        cfg: Runtime configuration.
        message: Markdown-formatted message text.
    """
    if not cfg.mattermost_token or not cfg.mattermost_channel_id:
        print("MATTERMOST_TOKEN or MATTERMOST_CHANNEL_ID not set — skipping Mattermost.")
        return
    _mm_api(cfg, "POST", "/posts", {"channel_id": cfg.mattermost_channel_id, "message": message})
    print(f"✓ Sent to Mattermost channel '{cfg.mattermost_channel_id}'")


# ── Matrix ─────────────────────────────────────────────────────────────────


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


# ── Entry point ────────────────────────────────────────────────────────────


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
    message_md = build_markdown(issues, prs, urls, cfg.repo_url)
    message_plain = build_plain_text(issues, prs)
    message_html = build_html(issues, prs, urls, cfg.repo_url)

    print("\n── Message preview ──────────────────────────────────────────────")
    print(message_md)
    print("─────────────────────────────────────────────────────────────────\n")

    send_mattermost(cfg, message_md)
    send_matrix(cfg, message_plain, message_html)
    print("Done.")


if __name__ == "__main__":
    main()

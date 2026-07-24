# Weekly queue report

**Files:** `.github/workflows/queue-report.yml` · `.github/scripts/queue-report.py`

Runs every **Monday at 12:00 UTC** (and on demand via `workflow_dispatch`) to post a summary of the open issue and PR queues to Mattermost and Matrix.

## What it reports

The report comes in two kinds:

1. **All-encompassing dashboard** — a counts table (triaged/untriaged issues; draft/old/unreviewed/approved/changes PRs), posted to the configured Mattermost channel and the main Matrix room (`MAIN_MATRIX_ALIAS`). Each row links to a pre-filtered GitHub view.

2. **Per-label item reports** — for each label listed in `LABEL_ROUTES`, a report listing the actual issues and PRs carrying that label, posted to the label's Matrix room. Items with several routed labels appear in every matching room's report. Multiple labels may share one room (e.g. `Release team` and `AA` both post to `#release:ubuntu.com`); such a room receives a single combined report.

### Dashboard categories

| Category | GitHub filter query |
|---|---|
| ✅ Issues — triaged | `is:open is:issue -label:untriaged` |
| ⚠️ Issues — untriaged | `is:open is:issue label:untriaged` |
| 📝 Draft PRs | `is:open is:pr draft:true` |
| 🕐 PRs older than 2 weeks | `is:open is:pr sort:created-asc` (oldest-first proxy) |
| 👀 PRs awaiting review | `is:open is:pr review:required draft:false` |
| ✅ PRs ready to merge | `is:open is:pr review:approved draft:false` |
| 🔄 PRs with changes requested | `is:open is:pr review:changes_requested draft:false` |

### Label routing

To add a new label→room pair, append one `LabelRoute(...)` line to `LABEL_ROUTES` in the script:

```python
LABEL_ROUTES: tuple[LabelRoute, ...] = (
    LabelRoute("MIR", "#ubuntu-mir:ubuntu.com"),
    # …add a new line here…
)
```

Room IDs are resolved at runtime from their aliases (no per-room secrets).

## Implementation

The script uses only the Python standard library (no third-party packages).
GitHub data is fetched via the GraphQL API. PRs are paginated in pages of 100.
Three message formats are produced: Markdown (Mattermost), plain text and HTML
(Matrix `body` / `formatted_body`). Notifications are silently skipped when
their token is absent.

## Configuration

### Secrets

| Secret | Purpose |
|---|---|
| `MATTERMOST_TOKEN` | Mattermost bot-user token |
| `MATTERMOST_CHANNEL_ID` | Mattermost channel ID |
| `MATRIX_TOKEN` | Matrix access token (used for all Matrix rooms) |

Matrix room IDs are resolved at runtime from aliases defined in the script
(`MAIN_MATRIX_ALIAS` / `LABEL_ROUTES`), so no per-room secrets are needed.

### Variables (repo Settings → Variables)

| Variable | Default |
|---|---|
| `MATTERMOST_URL` | `https://chat.canonical.com` |
| `MATRIX_HOMESERVER` | `https://ubuntu.com` |

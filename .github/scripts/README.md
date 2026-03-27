# Weekly queue report

**Files:** `.github/workflows/queue-report.yml` · `.github/scripts/queue-report.py`

Runs every **Monday at 12:00 UTC** (and on demand via `workflow_dispatch`) to post a summary of the open issue and PR queues to Mattermost and Matrix.

## What it reports

Each row in the report table links to a pre-filtered GitHub view.

| Category | GitHub filter query |
|---|---|
| ✅ Issues — triaged | `is:open is:issue label:triaged` |
| ⚠️ Issues — untriaged | `is:open is:issue -label:triaged` |
| 📝 Draft PRs | `is:open is:pr draft:true` |
| 🕐 PRs older than 2 weeks | `is:open is:pr sort:created-asc` (oldest-first proxy) |
| 👀 PRs awaiting review | `is:open is:pr review:required draft:false` |
| ✅ PRs ready to merge | `is:open is:pr review:approved draft:false` |
| 🔄 PRs with changes requested | `is:open is:pr review:changes_requested draft:false` |

## Implementation

The script uses only the Python standard library (no third-party packages).
GitHub data is fetched via the GraphQL API. PRs are paginated in pages of 100.
Three message formats are produced: Markdown (Mattermost), plain text and HTML
(Matrix `body` / `formatted_body`). Either notification is silently skipped
when its token or channel/room ID is absent.

## Configuration

### Secrets

| Secret | Purpose |
|---|---|
| `MATTERMOST_TOKEN` | Mattermost bot-user token |
| `MATTERMOST_CHANNEL_ID` | Mattermost channel ID |
| `MATRIX_TOKEN` | Matrix access token |
| `MATRIX_ROOM_ID` | Matrix room ID (e.g. `!abc123:ubuntu.com`) |

### Variables (repo Settings → Variables)

| Variable | Default |
|---|---|
| `MATTERMOST_URL` | `https://chat.canonical.com` |
| `MATRIX_HOMESERVER` | `https://ubuntu.com` |

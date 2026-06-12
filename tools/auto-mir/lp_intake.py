"""lp_intake.py — Launchpad API intake for auto-mir.

Fetches bug metadata, description, comments, and the targeted source package
from the Launchpad REST API. Uses launchpadlib (python3-launchpadlib) which is
available from the Ubuntu archive — no web scraping.

Hard-fails with a clear message if the reporter MIR template content cannot
be detected in the bug, because the rest of the pipeline depends on it.
"""

import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auto_mir import RunContext

log = logging.getLogger("auto_mir.lp_intake")

# Sentinel strings that reliably identify reporter MIR template content.
# The reporter is expected to have processed the reporters template and posted it.
_REPORTER_TEMPLATE_MARKERS = [
    "[Availability]",
    "[Rationale]",
    "[Security]",
    "[Quality assurance",
    "[Maintenance",
]

# The MIR bug tag used to find MIR-related bugs on Launchpad.
_MIR_BUG_TAG = "MIR"


def _get_launchpad():
    """Return an authenticated (or anonymous) Launchpad API client."""
    try:
        from launchpadlib.launchpad import Launchpad  # type: ignore
    except ImportError:
        log.error(
            "launchpadlib is not installed. Install it with: sudo apt install python3-launchpadlib"
        )
        sys.exit(1)

    try:
        # Try anonymous access first — sufficient for all public MIR bug reads.
        lp = Launchpad.login_anonymously(
            "auto-mir",
            "production",
            version="devel",
        )
        log.debug("Connected to Launchpad API (anonymous)")
        return lp
    except Exception as exc:
        log.error("Failed to connect to Launchpad API: %s", exc)
        sys.exit(1)


def _detect_reporter_mir_content(text: str) -> bool:
    """Return True if text contains recognisable reporter MIR template sections."""
    hits = sum(1 for marker in _REPORTER_TEMPLATE_MARKERS if marker in text)
    # Require at least 3 distinct section markers to avoid false positives.
    return hits >= 3


def _find_reporter_mir_content(bug_description: str, comments: list[str]) -> str | None:
    """Search bug description then comments for reporter MIR content.

    Returns the first matching block, or None if not found.
    """
    if _detect_reporter_mir_content(bug_description):
        log.debug("Reporter MIR content found in bug description")
        return bug_description

    for i, comment in enumerate(comments):
        if _detect_reporter_mir_content(comment):
            log.debug("Reporter MIR content found in comment %d", i)
            return comment

    return None


def _extract_source_package_from_bug(bug, lp) -> str | None:
    """Determine the targeted source package from bug task targets."""
    try:
        tasks = list(bug.bug_tasks)
    except Exception as exc:
        log.warning("Could not fetch bug tasks: %s", exc)
        return None

    for task in tasks:
        try:
            target = task.target
            if hasattr(target, "source_package_name"):
                name = target.source_package_name
                if name:
                    log.debug("Source package from bug task: %s", name)
                    return name
            # target may be a DistributionSourcePackage
            if hasattr(target, "name"):
                name = target.name
                if name:
                    return name
        except Exception as exc:
            log.debug("Skipping task target due to error: %s", exc)
            continue

    return None


def _ask_yes_no(prompt: str, default_no: bool = True) -> bool:
    """Ask user for yes/no confirmation in terminal."""
    suffix = "[y/N]" if default_no else "[Y/n]"
    try:
        raw = input(f"{prompt} {suffix} ").strip().lower()
    except EOFError:
        return not default_no

    if not raw:
        return not default_no
    return raw in ("y", "yes")


def _evaluate_mir_heuristics(ctx) -> None:
    """Warn and ask for confirmation when bug does not look like a MIR bug.

    Heuristics:
    - title should usually contain MIR (non-mandatory)
    - ubuntu-mir team subscription is mandatory for MIR bug flow
    """
    title = ctx.bug.get("title", "")
    subscribers = ctx.bug.get("subscribers", [])
    subscribers_lower = {s.lower() for s in subscribers}

    has_mir_in_title = "mir" in title.lower()
    has_ubuntu_mir_subscription = "ubuntu-mir" in subscribers_lower

    ctx.bug["mir_heuristics"] = {
        "has_mir_in_title": has_mir_in_title,
        "has_ubuntu_mir_subscription": has_ubuntu_mir_subscription,
    }

    if not has_mir_in_title:
        log.warning(
            "Bug title does not contain MIR (non-mandatory heuristic): %s",
            title,
        )

    if has_ubuntu_mir_subscription:
        return

    log.warning(
        "Bug %s does not have ubuntu-mir subscribed, which is mandatory for MIR bug workflow.",
        ctx.bug_id,
    )
    proceed = _ask_yes_no(
        "This bug does not look like a MIR bug. Continue anyway?",
        default_no=True,
    )
    if not proceed:
        log.error("Aborted by user because bug is not MIR-qualified.")
        sys.exit(1)


def _fetch_comments(bug) -> list[str]:
    """Fetch all comment bodies from a bug."""
    comments = []
    try:
        for message in bug.messages:
            try:
                text = message.content
                if text:
                    comments.append(text)
            except Exception as exc:
                log.debug("Skipping comment due to error: %s", exc)
    except Exception as exc:
        log.warning("Could not fetch bug comments: %s", exc)
    return comments


def run(ctx: "RunContext") -> None:
    """Main intake entry point. Populates ctx with bug data.

    Raises SystemExit(1) with a clear message if:
    - Bug ID is not found or not accessible
    - Reporter MIR template content is not found in bug description or comments
    """
    lp = _get_launchpad()

    log.info("Fetching Launchpad bug %s", ctx.bug_id)
    try:
        bug = lp.bugs[int(ctx.bug_id)]
    except KeyError:
        log.error("Bug %s not found on Launchpad.", ctx.bug_id)
        sys.exit(1)
    except Exception as exc:
        log.error("Failed to fetch bug %s: %s", ctx.bug_id, exc)
        sys.exit(1)

    ctx.bug = {
        "id": ctx.bug_id,
        "title": bug.title,
        "description": bug.description or "",
        "tags": list(bug.tags or []),
        "web_link": bug.web_link,
    }

    log.debug("Bug title: %s", bug.title)
    log.debug("Bug tags: %s", ctx.bug["tags"])

    # Fetch all comments
    comments = _fetch_comments(bug)
    ctx.bug["comments"] = comments
    log.debug("Fetched %d comments", len(comments))

    # Determine source package
    source_package = _extract_source_package_from_bug(bug, lp)
    if not source_package:
        log.error(
            "Could not determine source package from bug %s. "
            "Check that the bug is targeted at a source package.",
            ctx.bug_id,
        )
        sys.exit(1)
    ctx.source_package = source_package
    log.info("Source package: %s", ctx.source_package)

    # Series is host-selected (default devel), not auto-detected from bug.
    log.info("Target series: %s", ctx.series)

    # Fetch bug subscribers for MIR qualification heuristics and SUM-4 checks
    subscribers = []
    try:
        for sub in bug.subscriptions:
            try:
                subscribers.append(sub.person.name)
            except Exception:
                pass
        ctx.bug["subscribers"] = subscribers
        log.debug("Subscribers: %s", subscribers)
    except Exception as exc:
        log.warning("Could not fetch bug subscribers: %s", exc)
        ctx.bug["subscribers"] = []

    _evaluate_mir_heuristics(ctx)

    # Gate: reporter MIR content must be present
    reporter_content = _find_reporter_mir_content(
        ctx.bug["description"], ctx.bug["comments"]
    )
    if reporter_content is None:
        log.error(
            "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "HARD STOP: Reporter MIR template content not found in bug %s\n"
            "\n"
            "auto-mir requires the reporter to have filled and posted the\n"
            "MIR reporters template (docs/MIR/mir-reporters-template.md)\n"
            "on the Launchpad bug before a review can be generated.\n"
            "\n"
            "Action: Ask the reporter to post their completed template on\n"
            "the bug, then re-run auto-mir.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
            ctx.bug_id,
        )
        sys.exit(1)

    ctx.reporter_mir_content = reporter_content
    log.info("Reporter MIR content found (%d chars)", len(reporter_content))

    log.info(
        "Launchpad intake complete: bug=%s package=%s series=%s",
        ctx.bug_id,
        ctx.source_package,
        ctx.series or "(unknown)",
    )

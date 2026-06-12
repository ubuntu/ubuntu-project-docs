"""Team mapping adapter for package subscriptions.

Fetches the package-team-mapping.json report to determine which teams have
structural bug subscriptions to the source package being reviewed.
"""

from __future__ import annotations

import json
import logging
import urllib.request
from typing import Any

from catalog_enums import AdapterID
from evidence.registry import adapter

log = logging.getLogger("auto_mir.evidence.team_mapping")

# Teams that appear in package-team-mapping.json but are NOT valid bug subscribers.
# These are from ubuntu-archive-tools/lputils.py team_names (display-only teams).
# See decisions.md for rationale.
NON_SUBSCRIBER_TEAMS = {
    "kubuntu-bugs",  # Display only, not for bug subscription
    "pkg-ime",  # Display only, not for bug subscription
    "translators-packages",  # Display only, not for bug subscription
}

TEAM_MAPPING_URL = "https://static-reports.ubuntu.com/package-team-mapping.json"


@adapter(AdapterID.TEAM_MAPPING)
def collect_team_mapping(ctx) -> dict[str, Any]:
    """Fetch team mapping from static report and check package subscriptions.

    Downloads package-team-mapping.json, filters out non-subscriber teams,
    and checks which valid teams have structural subscriptions to the package.

    Returns a dict with team_mapping and subscribed_teams.
    """
    source_package = ctx.source_package
    if not source_package:
        return {
            "status": "error",
            "error": "source_package not set in context",
        }

    try:
        log.info("Fetching team mapping from %s", TEAM_MAPPING_URL)

        with urllib.request.urlopen(TEAM_MAPPING_URL, timeout=30) as response:
            raw_mapping = json.load(response)

        # Filter out non-subscriber teams and 'unsubscribed'
        team_mapping = {
            team: packages
            for team, packages in raw_mapping.items()
            if team not in NON_SUBSCRIBER_TEAMS and team != "unsubscribed"
        }

        log.info(
            "Loaded team mapping: %d valid teams (filtered %d non-subscriber teams)",
            len(team_mapping),
            len(NON_SUBSCRIBER_TEAMS),
        )

        # Check which teams have subscribed to our package
        subscribed_teams = []
        for team_name, packages in team_mapping.items():
            if source_package in packages:
                subscribed_teams.append(team_name)
                log.info("Found team subscription: %s -> %s", team_name, source_package)

        log.info(
            "Team mapping complete: %d teams subscribed to %s",
            len(subscribed_teams),
            source_package,
        )

        return {
            "status": "ok",
            "team_mapping": team_mapping,
            "subscribed_teams": subscribed_teams,
            "source_package": source_package,
        }
    except Exception as e:
        log.error("Failed to collect team mapping: %s", e)
        return {
            "status": "error",
            "error": str(e),
        }

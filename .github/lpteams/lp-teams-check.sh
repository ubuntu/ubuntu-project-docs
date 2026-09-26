#!/bin/bash

cd "$(dirname "$0")" || exit

if ls -- *.team 1>/dev/null 2>&1; then
    readarray -t TEAMS < <(basename --multiple --suffix=.team -- *.team)
else
    exit
fi

for LP_TEAM in "${TEAMS[@]}"; do
    EXISTING_TEAM=$(cat "$LP_TEAM.team")

    # Fetch team members from Launchpad API
    # Use --fail to detect HTTP errors, and capture the response
    LP_RESPONSE=$(curl --silent --fail --show-error \
        https://api.launchpad.net/devel/~"${LP_TEAM}"/members 2>&1)

    CURL_EXIT_CODE=$?

    if [ $CURL_EXIT_CODE -ne 0 ]; then
        echo "ERROR: Failed to fetch team data for '$LP_TEAM' from Launchpad (curl exit code: $CURL_EXIT_CODE)."
        echo "This may indicate a Launchpad outage or network issue."
        echo "Skipping '$LP_TEAM' to avoid creating an incorrect PR."
        echo "Error details: $LP_RESPONSE"
        continue
    fi

    READ_TEAM=$(echo "$LP_RESPONSE" | jq -r '.entries[] | .name' 2>/dev/null | sort)

    # Verify that we got a non-empty result
    if [ -z "$READ_TEAM" ]; then
        echo "WARNING: Launchpad returned empty or invalid data for team '$LP_TEAM'."
        echo "This may indicate a Launchpad outage or API issue."
        echo "Skipping '$LP_TEAM' to avoid creating an incorrect PR."
        continue
    fi

    if [ "$READ_TEAM" != "$EXISTING_TEAM" ]; then
        git config --local user.email "github-actions[bot]@users.noreply.github.com"
        git config --local user.name "github-actions[bot]"

        BRANCH_NAME="update-$LP_TEAM-$(date +'%Y%m%d-%H%M%S')"

        git checkout -b "$BRANCH_NAME"

        echo "$READ_TEAM" >"$LP_TEAM.team"

        git add .
        git commit -m "Update '$LP_TEAM' team in $LP_TEAM.team"
        git push origin "$BRANCH_NAME"

        gh pr create -B main -H "$BRANCH_NAME" \
            --title "Update $LP_TEAM team" \
            --body "### Description

Automatically generated PR to update '$LP_TEAM' team in '$LP_TEAM.team'.

### For the rewiever

The merging of this PR needs to be followed up by an update of the CODEOWNERS file. There the list of users owning the '$LP_TEAM' docs must be brought up to date to mirror the users in '$LP_TEAM.team'.

See the [README](/ubuntu/ubuntu-project-docs/blob/main/.github/lpteams/README.md) for details."
    else
        echo "No changes detected for $LP_TEAM team."
    fi
done

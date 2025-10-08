#!/bin/bash

cd "$(dirname "$0")" || exit

if ls -- *.team 1>/dev/null 2>&1; then
    readarray -t TEAMS < <(basename --multiple --suffix=.team -- *.team)
else
    exit
fi

for LP_TEAM in "${TEAMS[@]}"; do
    EXISTING_TEAM=$(cat "$LP_TEAM.team")
    READ_TEAM=$(curl --silent https://api.launchpad.net/devel/~"${LP_TEAM}"/members |
        jq -r '.entries[] | .name' | sort)

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

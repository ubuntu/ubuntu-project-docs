#!/bin/bash

cd "$(dirname "$0")" || exit

if ls -- *.team 1>/dev/null 2>&1; then
    readarray -t TEAMS < <(basename --multiple --suffix=.team -- *.team)
else
    exit
fi

for LP_TEAM in "${TEAMS[@]}"; do
    EXISTING_TEAM=$(cat "$LP_TEAM.team")
    READ_TEAM=$(curl --silent https://api.launchpad.net/1.0/~"${LP_TEAM}"/members |
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
            --body "Automatically generated PR to update '$LP_TEAM' team in '$LP_TEAM.team'."
    else
        echo "No changes detected for $LP_TEAM team."
    fi
done

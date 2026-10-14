# Launchpad teams check

A nightly GH Action workflow (`.github/workflows/lp-teams.check.yaml`) calls a local script (`.github/lpteams/lp-teams-check.sh`), which checks the membership list of defined Launchpad teams against locally stored lists and creates a PR to update the local lists in case of changes on the LP side.

This is to automate prompting for changes to `CODEOWNERS` to keep the ACL for special parts of the docs up-to-date.


## Local setup

LP teams are locally defined using plain-text files named `<lp-team-name>.team`, which are placed in the `.github/lpteams/` directory. One LP username per line. E.g. for `https://launchpad.net/~example-team`, it would be:

```
$ cat .github/lpteams/example-team.team
user1
user2
```


## Manual part

Merging of the automated PR, which only updates the `.team` file, must be followed by a manual PR to update the respective team in the `CODEOWNERS` file (as there's no mapping between LP and GH usernames at this point).

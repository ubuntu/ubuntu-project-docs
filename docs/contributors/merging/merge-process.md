(merge-process)=
# Performing a deltarebase

{command}`git ubuntu deltarebase` runs the whole merge process as a series of checked steps.
It looks up the versions on Launchpad, creates the tags and branches for you, and stops with instructions whenever a step needs a human.

::::{admonition} **Merging** series
The article series provides guidance on performing package merges.

Process overview:
:   * {ref}`merges-syncs`

```{raw} html
<span style="font-size:0.1px"></span>
```

{ref}`How to do a merge <merging>`:
:   1. {ref}`merge-preliminary-steps`
    1. {ref}`merge-process` (this article)
    1. {ref}`merge-review-the-changelog`
    1. {ref}`merge-upload-a-ppa`
    1. {ref}`merge-test-the-new-build`
    1. {ref}`merge-git-ubuntu-merge-proposal`

Extra:
:   * {ref}`merge-manually`
    * {ref}`merge-cheat-sheet`
::::

:::{note}
`deltarebase` is our new way for merges and currently available in the `latest/edge` channel of the `git-ubuntu` snap:

```none
$ sudo snap refresh --channel latest/edge git-ubuntu
```

If you encounter problems, please [report a bug](https://bugs.launchpad.net/git-ubuntu). If needed, {ref}`merge manually <merge-manually>`.
:::


(merge-deltarebase-start)=
## Start the merge

In an up-to-date {ref}`package repository <merge-get-the-package-repository>`, start the merge with the {ref}`merge bug <merge-make-a-bug-report-for-the-merge>`:

```none
$ git ubuntu deltarebase start --bug 133734200
```

This rebases the Ubuntu delta of the current development release onto Debian `sid`.
Use `--release` for another Ubuntu release, and `--debian-experimental` to rebase onto Debian `experimental`.

The result is the branch `lp133734200-merge-<release>` and the usual merge tags, prefixed with the bug number: `lp133734200/old/ubuntu`, `lp133734200/split/<version>`, and so on.


(merge-deltarebase-steps)=
## Steps

```{figure} deltarebase-pipeline.svg
:alt: The deltarebase steps from prepare to submit, each ending in a check
```

Each step ends with a check that doesn't depend on who did the work.
The next step only runs once the check passes.

| Step          | What it does                                                                                   | Check                      |
| ------------- | ---------------------------------------------------------------------------------------------- | -------------------------- |
| `prepare`     | Finds the Ubuntu and Debian versions to merge on Launchpad                                     | Versions match the archive |
| `reconstruct` | Tags `old/ubuntu`, `old/debian` and `new/debian` and recreates the delta as commits, with the changelog and `update-maintainer` changes moved to the end | |
| `split`       | {ref}`Splits <merge-split-commits>` commits that mix several changes, then tags `split/<version>` | Tree unchanged             |
| `logical`     | Drops the changelog and `update-maintainer` commits, {ref}`squashes and reorders <merge-prepare-the-logical-view>` the rest, then tags `logical/<version>` | Tree unchanged |
| `rebase`      | {ref}`Rebases <merge-rebase-onto-new-debian>` the delta onto `new/debian`                      | Based on new Debian        |
| `patches`     | {ref}`Checks <merge-check-patches-still-apply-cleanly>` that the quilt patches still apply     | Patches apply              |
| `build`       | Builds the package in a fresh LXD container (optional)                                         | Build passed               |
| `finalize`    | {ref}`Finishes the merge <merge-finish-the-merge>`: merged changelog and `update-maintainer`   | Only the changelog changed |
| `submit`      | {ref}`Pushes <merge-push-to-your-launchpad-repository>` the branch and tags to your Launchpad repository |              |

Without `--ai`, `split` and `logical` only check and tag the delta as it is.
That is enough when the previous merge already left one commit per logical change.
Otherwise, stop after `reconstruct`, clean up the commits yourself with {command}`git rebase -i`, and continue:

```none
$ git ubuntu deltarebase start --bug 133734200 --target-step reconstruct
$ git rebase -i lp133734200/old/debian
$ git ubuntu deltarebase continue
```

The `build` step only runs with `--ai` or when you set a build command, for example `--build-command sbuild` or `git config --global gitubuntu.buildcommand sbuild`.
It needs {ref}`LXD <lxd>`.

If no delta remains after the rebase, there is nothing to merge: {ref}`request a sync <how-to-request-a-sync>` instead.


(merge-deltarebase-when-a-step-stops)=
## When a step stops

```{figure} deltarebase-check-loop.svg
:alt: Each step ends in a check; if it fails, you fix it with plain git and run deltarebase continue, which checks again
```

When a step needs a human, for example for a rebase conflict, a patch that no longer applies, or a failing build, `deltarebase` stops and tells you what to do.
Its state is saved in `.git/`, so fix the problem with plain {command}`git` and carry on:

```none
$ git ubuntu deltarebase status    # where am I, and why did it stop?
$ git ubuntu deltarebase continue  # check my fix and carry on
$ git ubuntu deltarebase abort     # go back to where I started and remove all refs
```

`continue` runs the check of the stopped step on your fix, then runs the remaining steps.
To run the automation of the stopped step again instead, for example after a fix that lets it get further, use `retry`.
To stop after a particular step, pass `--target-step <step>` to `start`, `continue` or `retry`.

{ref}`merge-manually` explains how to do each step by hand.

To start over, use `start --restart`.
To keep the current attempt and make a second one next to it, use `start --reversion 2`, which adds a `-2` suffix to the branch and tags.


(merge-deltarebase-ai)=
## Let an AI agent do the tedious parts

With `--ai`, an AI agent performs the steps that need judgement in an isolated environment:
`split`, `logical`, `rebase`, `patches`, `build` and `finalize`.
It follows a skill file for each step, which describes how that step is done in Ubuntu.

```none
$ git ubuntu deltarebase start --bug 133734200 --ai
```

The agent never touches your checkout, the archive, or your machine:

* It works on a fresh clone of your repository in an {ref}`LXD <lxd>` container.
* Its result only comes back, as the `ai-review/<step>/<branch>` branch, if it passes the step's check.
* A build fix only counts if the build of the agent's final commit succeeded in a separate, trusted build container.
* If the agent gives up, you get its report and its work-in-progress branch, and the step is handed over to you.
  Fix it and run `continue`, or let the agent try again with `retry`.

Configure the model and the API access once:

```none
$ git config --global gitubuntu.aimodel <model>
$ git config --global gitubuntu.aitoken <token>
# to use any OpenAI-compatible API, set the url:
$ git config --global gitubuntu.aiurl <url>
```

By default the agent can use GitHub Copilot, and `git ubuntu ai login` creates the token for you.
To access other APIs set the `gitubuntu.aiurl`.
To watch the agent's reasoning, add `--ai-show-thinking`.

You remain the reviewer: check the result as carefully as if you had written it yourself.


(merge-deltarebase-submit)=
## Review and submit

After `finalize`, review the remaining delta and {ref}`the changelog <merge-review-the-changelog>`:

```none
$ git log --stat lp133734200/new/debian..
$ git show HEAD -- debian/changelog
```

Then submit:

```none
$ git ubuntu deltarebase submit
```

The `submit` step pushes the branch and its tags to your Launchpad repository, the Git remote named after `gitubuntu.lpuser`.
{command}`git ubuntu clone` adds this remote; otherwise add it with `git ubuntu remote add <your-lp-username>`.
Launchpad answers the push with a link to open a merge proposal.
Open it once you have {ref}`tested the result <merge-test-the-new-build>`.

To submit automatically without stopping for review, for example in automation, start with `--target-step submit`.


## Next

* {ref}`merge-review-the-changelog`

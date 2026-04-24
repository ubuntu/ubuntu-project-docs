(merge-git-ubuntu-merge-proposal)=
# `git-ubuntu` merge proposal

Following a merge and testing, submit a merge proposal to include the updated package in the Archive.

::::{admonition} **Merging** series
The article series provides guidance on performing package merges.

Process overview:
:   * {ref}`merges-syncs`

```{raw} html
<span style="font-size:0.1px"></span>
```

{ref}`How to do a merge <merging>`:
:   1. {ref}`merge-preliminary-steps`
    1. {ref}`merge-process`
    1. {ref}`merge-fix-the-changelog`
    1. {ref}`merge-upload-a-ppa`
    1. {ref}`merge-test-the-new-build`
    1. {ref}`merge-git-ubuntu-merge-proposal` (this article)

Extra:
:   * {ref}`merge-manually`
    * {ref}`merge-cheat-sheet`
::::


## Open a merge proposal

See {ref}`submit-mp-open` in {ref}`how-to-submit-a-merge-proposal` for the
full instructions. For merges, use `--target-branch debian/sid`:

```none
$ git ubuntu submit --reviewer $REVIEWER --target-branch debian/sid
Your merge proposal is now available at: https://code.launchpad.net/~kstenerud/ubuntu/+source/at/+git/at/+merge/358655
If it looks OK, please move it to the 'Needs Review' state.
```

:::{note}
Using a target branch of `debian/sid` may seem wrong, but is a workaround for
{lpbug}`1976112`.
:::

If this fails, {ref}`do it manually <merge-submit-merge-proposal-manually>`.


(merge-update-the-merge-proposal)=
## Update the merge proposal

See {ref}`submit-mp-prepare-description` and {ref}`submit-mp-open` in
{ref}`how-to-submit-a-merge-proposal` for guidance on writing the description
and linking your PPA.

When adding a comment to help the reviewer, include:

* a link to the PPA
* test steps and results

Example:

```none
PPA: https://launchpad.net/~kstenerud/+archive/ubuntu/disco-at-merge-1802914

Basic test:
$ echo "echo abc >test.txt" | at now + 1 minute && sleep 1m && cat test.txt && rm test.txt

Package tests:
This package contains no tests.
```

(merge-open-the-review)=
## Open the review

Change the MP status from {guilabel}`work in progress` to
{guilabel}`needs review`.

For sponsorship options, see {ref}`submit-mp-get-sponsorship` in
{ref}`how-to-submit-a-merge-proposal`.


(merge-follow-the-migration)=
## Follow the migration

See {ref}`submit-mp-follow-migration` in {ref}`how-to-submit-a-merge-proposal`.


(merge-submit-merge-proposal)=
# Submit Merge Proposal

Following a merge and testing, submit a merge proposal to include the updated package in the Archive.

:::{admonition} **Merging** series
The article series provides guidance on performing package merges.

Process overview:
:   * {ref}`merges-syncs`
    * {ref}`merging`

How to do a merge:
:   1. {ref}`merge-preliminary-steps`
    1. {ref}`merge-process`
    1. {ref}`merge-fix-the-changelog`
    1. {ref}`merge-upload-a-ppa`
    1. {ref}`merge-test-the-new-build`
    1. {ref}`merge-submit-merge-proposal` (this article)

Extra:
:   * {ref}`merge-manually`
    * {ref}`merge-cheat-sheet`
:::


## Open a merge proposal

Use the {command}`submit` command of {command}`git-ubuntu`:

```none
$ git ubuntu submit --reviewer $REVIEWER --target-branch debian/sid
Your merge proposal is now available at: https://code.launchpad.net/~kstenerud/ubuntu/+source/at/+git/at/+merge/358655
If it looks OK, please move it to the 'Needs Review' state.
```

:::{note}
Git branches with `%` in their name don't work. Use something like `_`.
:::

Set `--reviewer` to the team (or user) on Launchpad that should look at your change -- by default it is `--reviewer ubuntu-sponsors`.

* If you do not have upload rights for this package, use `ubuntu-sponsors` here. That adds your Merge Proposal to the
  [Ubuntu sponsoring queue](http://sponsoring-reports.ubuntu.com/general.html), so people with upload rights for that package may eventually review it for you.

* To notify a specific team, use, e.g. `canonical-foundations`, `canonical-public-cloud`, or `ubuntu-server`.

To avoid having to specify the `--reviewer` flag, configure the reviewers for {command}`git-ubuntu`. Include a section like the following either globally in `~/.gitconfig`, or in individual repositories in `.git/config`:

```ini
[gitubuntu.submit]
    defaultReviewer = <your-ubuntu-teamname>, \
                      <canonical-more-reviewers>, \
                      <canonical-otherteam>
```

The equivalent `git config` command is:

```none
$ git config [--global] gitubuntu.submit.defaultReviewer <launchpad-reviewer>
```

:::{note}
Using a target branch of `debian/sid` may seem wrong, but is a workaround for {lpbug}`1976112`.
:::

If this fails, {ref}`do it manually <merge-submit-merge-proposal-manually>`.


(merge-update-the-merge-proposal)=
## Update the merge proposal

* Link the PPA.

* Add any other info (as a comment) that can help the reviewer.

  Example:

  ```
  PPA: https://launchpad.net/~kstenerud/+archive/ubuntu/disco-at-merge-1802914

  Basic test:
  $ echo "echo abc >test.txt" | at now + 1 minute && sleep 1m && cat test.txt && rm test.txt

  Package tests:
  This package contains no tests.
  ```

(merge-open-the-review)=
## Open the review

Change the MP status from {guilabel}`work in progress` to {guilabel}`needs review`.


(merge-follow-the-migration)=
## Follow the migration

Once the merge proposal goes through, you must follow the package to make sure it gets to its destination.


(merge-package-tests)=
### Package tests

The results from the latest package tests are published for each Ubuntu release. For example: [autopkgtest.ubuntu.com/packages/o/openssh/questing/amd64](http://autopkgtest.ubuntu.com/packages/o/openssh/questing/amd64). See {ref}`automatic-package-testing-autopkgtest`.


(merge-proposed-migration)=
### Proposed migration

The status of all packages is available from the [Ubuntu archive](https://ubuntu-archive-team.ubuntu.com/proposed-migration/) or one of its subdirectories. The top level directory is for the current dev release. Previous releases are in subdirectories. See {ref}`proposed-migration`.


## Further reading

* {ref}`merge-manually`

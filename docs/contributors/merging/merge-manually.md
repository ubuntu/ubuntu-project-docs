(merge-manually)=
# Merge manually

These are the steps that {ref}`git ubuntu deltarebase <merge-process>` automates.
Follow them to understand what `deltarebase` does, or to process a package manually.

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
    1. {ref}`merge-review-the-changelog`
    1. {ref}`merge-upload-a-ppa`
    1. {ref}`merge-test-the-new-build`
    1. {ref}`merge-git-ubuntu-merge-proposal`

Extra:
:   * {ref}`merge-manually` (this article)
    * {ref}`merge-cheat-sheet`
::::

| `deltarebase` step | Manual steps                                                                    |
| ------------------ | ------------------------------------------------------------------------------- |
| `prepare`          | {ref}`merge-decide-on-a-merge-candidate`                                        |
| `reconstruct`      | {ref}`merge-start-a-git-ubuntu-merge`, {ref}`merge-make-a-merge-branch`         |
| `split`            | {ref}`merge-split-commits`                                                      |
| `logical`          | {ref}`merge-prepare-the-logical-view`                                           |
| `rebase`           | {ref}`merge-rebase-onto-new-debian`                                             |
| `patches`          | {ref}`merge-check-patches-still-apply-cleanly`                                  |
| `build`            | {ref}`merge-upload-a-ppa`                                                       |
| `finalize`         | {ref}`merge-finish-the-merge`                                                   |
| `submit`           | {ref}`merge-push-to-your-launchpad-repository`                                  |


(merge-start-a-git-ubuntu-merge)=
## Start the merge

From within the Git source tree:

```none
$ git ubuntu merge start pkg/ubuntu/devel
```

This generates the following tags for you:

| Tag                  | Source                                                                                  |
| -------------------- | --------------------------------------------------------------------------------------- |
| `old/ubuntu`         | `ubuntu/devel`                                                                          |
| `old/debian`         | Last import tag before `old/ubuntu` without `ubuntu` in its version                     |
| `new/debian`         | `debian/sid`, which always matches Debian "unstable"                                    |
| `reconstruct/<uver>` | `old/ubuntu` as commits on top of `old/debian`, where `<uver>` is the `old/ubuntu` version, for example `2.1.11-1ubuntu3` |

If `git ubuntu merge start` fails, {ref}`create the tags manually <merge-create-tags>`.


(merge-create-tags)=
#### Create the tags manually

Find the last Debian import tag before the current Ubuntu version:

```none
$ git describe --tags --abbrev=0 --match 'pkg/import/*' --exclude '*ubuntu*' pkg/ubuntu/disco-devel
pkg/import/3.1.20-3.1
```

Create the tags from it:

```none
$ git tag old/ubuntu pkg/ubuntu/disco-devel
$ git tag old/debian pkg/import/3.1.20-3.1
$ git tag new/debian pkg/debian/sid
```

Then recreate the delta as commits on top of `old/debian`:

```none
$ git checkout old/ubuntu
$ git rebase -i old/debian
```

If the package hasn't been updated since the Git repository structure changed, the rebase lists all changes throughout history, not only those since the last Debian version.
Delete the lines up to and including the import of the last Debian version, in this case `3.1.20-3.1`.

Tag the result:

```none
$ git ubuntu tag --reconstruct
```


(merge-make-a-merge-branch)=
## Make a merge branch

Name the branch after the merge bug and the current Ubuntu development release (in this example, {lpbug}`133734200` and `disco`):

```none
$ git switch -c merge-lp133734200-disco
```

If there's no merge bug, you can use the Debian version you're merging instead, for example `merge-3.1.23-1-disco`.

:::{admonition} Empty directories warning

A message like the following one when making the merge branch indicates a problem with empty directories:

```none
$ git switch -c merge-something-disco
Switched to a new branch 'merge-something-disco'

WARNING: empty directories exist but are not tracked by git:

tests/root/etc/postfix
tests/root/etc/xinetd.d/arch

These will silently disappear on commit, causing extraneous
unintended changes. See: LP: #1687057.
```

These empty directories can cause the rich history to become lost when uploading them to the Archive. When that happens, use {ref}`restore-empty-directories`.
:::


(merge-split-commits)=
## Split commits

Split changes in old-style {ref}`delta <merge-delta>` commits that grouped multiple changes together.


(merge-check-if-there-are-commits-to-split)=
### Check if there are commits to split

List the commits since `old/debian` and the files each of them changed:

```none
$ git log --stat old/debian..
```

Example (from merging the `heimdal` package):

```none
$ git log --stat old/debian..

commit 9fc91638b0aabcd2eb9f79d45d68bc5ac6cd6944 (HEAD ->
merge-7.8.git20221117.28daf24+dfsg-1-lunar)
Author: Deve Loper <deve.loper@ubuntu.com>
Date:   Tue Jan 17 16:16:01 2023 +0100

    Changelog for 7.8.git20221117.28daf24+dfsg-1

 debian/changelog | 1 -
 1 file changed, 1 deletion(-)


commit e217fae2dc54a0a13eabcd97ec7d3be527fa243
Author: Deve Loper <deve.loper@ubuntu.com>
Date:   Tue Jan 17 16:13:49 2023 +0100

    update-maintainer

 debian/control | 3 ++-
 1 file changed, 2 insertions(+), 1 deletion(-)
```

Common examples of commits that need to be split:

* A change to `debian/changelog` together with changes to other files
* An `Import patches-unapplied version 1.2.3ubuntu4 to ubuntu/cosmic-proposed` commit, which imports a whole Ubuntu upload rather than a single change

Check all commits just to make sure.

If there are no commits to split, {ref}`add the "split" tag <merge-tag-split>` and continue to {ref}`merge-prepare-the-logical-view`.


(merge-identify-logical-changes)=
### Identify logical changes

Separate the changes into logical units. For the {pkg}`at` package, this is trivial: put the {file}`changelog` change in one commit and the {file}`control` change in the other.

The second example, for {pkg}`nspr`, is more instructive. There are five files changed that need to be split out:

* All changelog changes go to one commit called `changelog`.
* Maintainer update (in `debian/control`) goes to one commit called `update maintainers`.
* All other logically separable changes go into individual commits.

Look in {file}`debian/changelog`:

```none
nspr (2:4.18-1ubuntu1) bionic; urgency=medium

  * Resynchronize with Debian. Remaining changes:
    - rules: Enable Thumb2 build on armel, armhf
    - d/p/fix_test_errcodes_for_runpath.patch: Fix testcases to handle
      zesty linker default changing to --enable-new-dtags for -rpath
```

There are two logical changes, which you need to separate. Look at the changes in individual files to see which file changes belong together, for example:

```none
$ git show d7ebe661 -- debian/rules
```

In this case, the following file changes are separated into logical units:

:::{list-table}
*    - File(s)
     - Logical unit
*    - `debian/rules`
     - Enable `Thumb2` build on `armel`, `armhf`
*    - `debian/patches/*`
     - Fix test cases to handle `zesty` linker default<br>changing to `--enable-new-dtags` for `-rpath`
*    - `debian/control`
     - Change maintainer
*    - `debian/changelog`
     - Changelog
:::


(merge-split-into-logical-commits)=
### Split into logical commits

1. Start a rebase: `git rebase -i old/debian`
1. Change the commits you're going to split from `pick` to `edit`
1. When the rebase stops at such a commit, bring its changes back as uncommitted changes: `git reset HEAD^`

Then commit each logical unit on its own.
Each commit message follows the changelog entry: The commit subject is the changelog entry, further notes are the body.
`git ubuntu merge finish` turns these messages into the new changelog entry.
See {ref}`how-to-commit-changes` for more information about commit message standards.

```none
$ git add debian/patches/*
$ git commit
```

```none
  * d/p/fix_test_errcodes_for_runpath.patch: Fix testcases to handle
    zesty linker default changing to --enable-new-dtags for -rpath
```

```none
$ git add debian/rules
$ git commit
```

```none
  * d/rules: Enable Thumb2 build on armel, armhf
```

```none
$ git commit -m update-maintainer debian/control
$ git commit -m changelog debian/changelog
```

Finally, complete the rebase:

```none
$ git rebase --continue
```

The result should be a sequence of smaller commits, one per `debian/changelog` entry (with potentially additional commits for previously undocumented changes).
It must not change the content of the latest Ubuntu version, so this must show no difference:

```none
$ git diff old/ubuntu
```


(merge-tag-split)=
### Tag split

Do this even if there were no commits to split:

```none
$ git ubuntu tag --split
```


(merge-prepare-the-logical-view)=
## Prepare the logical view

Make a clean, "logical" view of the history.
It has the same {term}`delta`, but only contains the changes that affect the package's behaviour.

The logical tag is the cleanest possible representation of a previous Ubuntu delta (by combining inverting commits, etc), which makes it as easy as possible to bring the delta forward.
It is also a clear boundary between the analysis of what is already there and the actual work of bringing the {term}`Ubuntu delta` forward, so a reviewer can start from the same point and check it almost automatically.

Start with a rebase from `old/debian`:

```none
$ git rebase -i old/debian
```

Do some cleaning:

* Delete imports, etc.
* Delete any commit that only changes metadata like changelog or maintainer.
* Possibly rearrange commits if it makes logical sense.

Squash these kinds of commits together:

* Changes and reversions of those changes, because they result in no change.
* Multiple changes to the same patch file, because they should be a logical unit.
* Fixes of mistakes made earlier in the same delta.
  For example, if `2.3-4ubuntu2` added the `--build-beter` configure flag and `2.3-4ubuntu3` fixed the typo, the logical delta has one commit adding `--build-better`.
  A mistake that is still in the delta itself is retained.

To squash a commit, move its line underneath the one you want it to become part of, and then change it from `pick` to `fixup`.


(merge-check-the-result)=
### Check the result

At the end of the "squash and clean" phase, the only difference to the split tag must be the changelog and the maintainer update:

```none
$ git diff --stat split/6.8-0ubuntu2
 debian/changelog | 31 -------------------------------
 debian/control   |  3 +--
 2 files changed, 1 insertion(+), 33 deletions(-)
```


(merge-create-logical-tag)=
### Create logical tag

```none
$ git ubuntu tag --logical
```

If this fails with an error like `HEAD is not a defined object in this git repository`, {ref}`merge-create-logical-tag-manually`.


(merge-create-logical-tag-manually)=
#### Create logical tag manually

Use the version of the last Ubuntu upload, for example `3.1.20-3.1ubuntu2`:

```none
$ git tag -a -m "Logical delta of 3.1.20-3.1ubuntu2" logical/3.1.20-3.1ubuntu2
```

:::{note}
Some characters aren't allowed in Git tag names: replace colons (`:`) with percentage signs (`%`), and tildes (`~`) with underscores (`_`).
:::


(merge-rebase-onto-new-debian)=
## Rebase onto new Debian

```none
$ git rebase -i --onto new/debian old/debian
```


(merge-conflicts)=
### Conflicts

If a conflict occurs, you must resolve it. Do so by modifying the conflicting commit during the rebase.

For example, merging `logwatch 7.5.0-1`:

```none
$ git rebase -i --onto new/debian old/debian
...
CONFLICT (content): Merge conflict in debian/control
error: could not apply c0efd06... - Drop libsys-cpu-perl and libsys-meminfo-perl from Recommends to
...
```

Look at the conflict in `debian/control`:

```none
    <<<<<<< HEAD
    Recommends: libdate-manip-perl, libsys-cpu-perl, libsys-meminfo-perl
    =======
    Recommends: libdate-manip-perl
    Suggests: fortune-mod, libsys-cpu-perl, libsys-meminfo-perl
    >>>>>>> c0efd06... - Drop libsys-cpu-perl and libsys-meminfo-perl from Recommends to
```

Upstream removed `fortune-mod` and deleted the entire line because it was no longer needed. Resolve it to:

```none
Recommends: libdate-manip-perl
Suggests: libsys-cpu-perl, libsys-meminfo-perl
```

Continue with the rebase:

```none
$ git add debian/control
$ git rebase --continue
```


(merge-empty-commits)=
### Empty commits

If a commit becomes empty, Debian or upstream already applied the change:

```none
The previous cherry-pick is now empty, possibly due to conflict resolution.
```

In such a case, drop the commit:

```none
$ git rebase --skip
```

`git ubuntu merge finish` lists it under "Dropped changes" in the new changelog entry.


(merge-sync-request)=
### Sync request

If all the commits are empty, or you realized there are no logical changes, you're facing a **sync request**, not a merge. Refer to the {ref}`sync guidelines <syncs>` to continue.


(merge-check-patches-still-apply-cleanly)=
### Check patches still apply cleanly

```none
$ quilt push -a --fuzz=0
```

**If {command}`quilt` fails to find the patches**

You may get an error `No series file found`. In this case, you need to tell `quilt` where to look for the patches. Configure it by setting an environment variable: `export QUILT_PATCHES=debian/patches`. (Or edit your `.quiltrc` file to make the changes permanent.)

**If {command}`quilt` fails to apply the patches**

Quilt can fail at this point if the file being patched has changed significantly upstream. The most common reason is that the issue the patch addresses has since been fixed upstream.

For example:

```none
$ quilt push -a --fuzz=0
...
Applying patch ssh-ignore-disconnected.patch
patching file scripts/services/sshd
Hunk #1 FAILED at 297.
1 out of 1 hunk FAILED -- rejects in file scripts/services/sshd
Patch ssh-ignore-disconnected.patch does not apply (enforce with -f)
```

If the changes in `ssh-ignore-disconnected.patch` are already applied upstream, drop the commit that added the patch:

```none
$ git log --oneline

1aed93f (HEAD -> ubuntu/devel) d/p/ssh-ignore-disconnected: [sshd] ignore disconnected from user (LP: #1644057)
7d9d752 - Drop libsys-cpu-perl and libsys-meminfo-perl from Recommends to   Suggests as they are in universe.
```

Run `git rebase -i 7d9d752` and delete the line of commit `1aed93f`.
If the patch only needs adjusting instead, refresh it with `quilt refresh` and squash the change into the commit that added it.


(merge-unapply-patches-before-continuing)=
### Unapply patches before continuing

```none
$ quilt pop -a
```


(merge-adding-new-changes)=
## Adding new changes

Add any new changes you want to include with the merge.
For instance, the new package version may {term}`fail to build from source (FTBFS) <FTBFS>` in Ubuntu due to new versions of specific libraries or runtimes.

Each logical change should be in its own commit to match the work done up to this point on splitting the logical changes.
There is no need to add changelog entries for these changes: `git ubuntu merge finish` generates them from the commit messages.


(merge-finish-the-merge)=
## Finish the merge

```none
$ git ubuntu merge finish pkg/ubuntu/devel
```

This adds three commits:

* `merge-changelogs`: the old Ubuntu and new Debian changelogs merged
* `d/control: update-maintainer`, unless the maintainer was already right
* `changelog`: the new changelog entry, generated from the commit messages since `new/debian`

If this fails, {ref}`merge-finish-the-merge-manually`.


(merge-finish-the-merge-manually)=
### Finish the merge manually

1. Merge the changelogs of old Ubuntu and new Debian:

    ```none
    $ git show new/debian:debian/changelog > /tmp/debnew.txt
    $ git show old/ubuntu:debian/changelog > /tmp/ubuntuold.txt
    $ merge-changelog /tmp/debnew.txt /tmp/ubuntuold.txt > debian/changelog
    $ git commit -m "merge-changelog" debian/changelog
    ```

1. Update the maintainer:

    ```none
    $ update-maintainer
    $ git commit -m "update-maintainer" debian/control
    ```

1. Create a new changelog entry for the merge:

    ```none
    $ dch -i
    ```

    Which creates, for example:

    ```none
    at (3.1.23-1ubuntu1) disco; urgency=medium

      * Merge with Debian unstable (LP: #133734200). Remaining changes:
        - Suggest an MTA rather than Recommending one.

     -- Deve Loper <deve.loper@ubuntu.com>  Mon, 12 Nov 2018 18:11:53 +0100
    ```

1. Commit the changelog:

    ```none
    $ git commit -m "changelog" debian/changelog
    ```


(merge-get-the-orig-tarball-manually)=
## Get the orig tarball manually

If {ref}`git ubuntu export-orig <merge-get-the-orig-tarball>` fails, regenerate the orig (upstream) tarball with {manpage}`pristine-tar(1)` from the data the importer stores in Git:

```none
$ git branch --force pristine-tar pkg/importer/debian/pristine-tar
$ pristine-tar checkout ../at_3.1.23.orig.tar.gz
```

If that fails too, download the source package from Debian into the parent directory, where {command}`dpkg-buildpackage` looks for the orig tarball:

```none
$ cd ..
$ pull-debian-source --download-only at 3.1.23-1
$ cd -
```


(merge-submit-merge-proposal-manually)=
## Submit merge proposal manually

Push the branch to your Launchpad repository:

```none
$ git push <your-lp-username> merge-lp133734200-disco
```

Then open the merge proposal in Launchpad, using the link in the push output, against the `debian/sid` branch (**not** `ubuntu/devel`), and save its URL.

Next step: {ref}`merge-update-the-merge-proposal`.


## Next

* {ref}`merge-review-the-changelog`

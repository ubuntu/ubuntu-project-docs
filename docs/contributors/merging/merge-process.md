(merge-process)=
# Merge process

Perform the merge using the {manpage}`git-ubuntu(1)` tool. See also the dedicated {external+git-ubuntu:doc}`git-ubuntu documentation <index>`.

:::{admonition} **Merging** series
The article series provides guidance on performing package merges.

Process overview:
:   * {ref}`merges-syncs`
    * {ref}`merging`

How to do a merge:
:   1. {ref}`merge-preliminary-steps`
    1. {ref}`merge-process` (this article)
    1. {ref}`merge-fix-the-changelog`
    1. {ref}`merge-upload-a-ppa`
    1. {ref}`merge-test-the-new-build`
    1. {ref}`merge-submit-merge-proposal`

Extra:
:   * {ref}`merge-manually`
    * {ref}`merge-cheat-sheet`
:::


(merge-start-a-git-ubuntu-merge)=
## Start a Git Ubuntu merge

From within the Git source tree:

```none
$ git ubuntu merge start pkg/ubuntu/devel
```

This generates the following tags for you:

| Tag          | Source                                                                   |
| ------------ | ------------------------------------------------------------------------ |
| `old/ubuntu` | `ubuntu/devel`                                                           |
| `old/debian` | last import tag prior to `old/ubuntu` without `ubuntu` suffix in version |
| `new/debian` | `debian/sid`                                                             |

If `git ubuntu merge start` fails, {ref}`merge-manually`.


(merge-make-a-merge-branch)=
## Make a merge branch

Use the merge-tracking bug and the current Ubuntu `devel` version it's going into (in the example of doing a merge below, the current Ubuntu `devel` was `disco`, and the `merge` bug for the case was {lpbug}`1802914`).

```none
$ git checkout -b merge-lp1802914-disco
```

If there's no merge bug, the Debian package version you're merging into can be used (for example, `merge-3.1.23-1-disco`).

:::{admonition} Empty directories warning

A message like the following one when making the merge branch indicates a problem with empty directories:

```none
$ git checkout -b merge-augeas-mirespace-testing
Switched to a new branch 'merge-augeas-mirespace-testing'

WARNING: empty directories exist but are not tracked by git:

tests/root/etc/postfix
tests/root/etc/xinetd.d/arch

These will silently disappear on commit, causing extraneous
unintended changes. See: LP: #1687057.
```

These empty directories can cause the rich history to become lost when uploading them to the Archive. When that happens, use {external:doc}`howto/restore-empty-directories`.

:::

(merge-split-commits)=
## Split commits

Split old-style commits that grouped multiple changes together.


(merge-check-if-there-are-commits-to-split)=
### Check if there are commits to split

```none
$ git log --oneline

2af0cb7 (HEAD -> merge-3.1.20-6-disco, tag: reconstruct/3.1.20-3.1ubuntu2, tag: split/3.1.20-3.1ubuntu2) import patches-unapplied version 3.1.20-3.1ubuntu2 to ubuntu/disco-proposed
2a71755 (tag: pkg/import/3.1.20-5) Import patches-unapplied version 3.1.20-5 to debian/sid
9c3cf29 (tag: pkg/import/3.1.20-3.1) Import patches-unapplied version 3.1.20-3.1 to debian/sid
...
```

Get all commit hashes since `old/debian` and check the summary for what they changed using:

```none
$ git log --stat old/debian..
```

Example (from merging the `heimdal` package):

```none
$ git log --stat old/debian..

commit 9fc91638b0a50392eb9f79d45d68bc5ac6cd6944 (HEAD ->
merge-7.8.git20221117.28daf24+dfsg-1-lunar)
Author: Michal Maloszewski <michal.maloszewski@canonical.com>
Date:   Tue Jan 17 16:16:01 2023 +0100

    Changelog for 7.8.git20221117.28daf24+dfsg-1

 debian/changelog | 1 -
 1 file changed, 1 deletion(-)


commit e217fae2dc54a0a13e4ac5397ec7d3be527fa243
Author: Michal Maloszewski <michal.maloszewski@canonical.com>
Date:   Tue Jan 17 16:13:49 2023 +0100

    update-maintainer

 debian/control | 3 ++-
 1 file changed, 2 insertions(+), 1 deletion(-)


commit 3c66d873330dd594d593d21870f4700b5e7fd153
Author: Michal Maloszewski <michal.maloszewski@canonical.com>
Date:   Tue Jan 17 16:13:49 2023 +0100

    reconstruct-changelog

 debian/changelog | 10 ++++++++++
 1 file changed, 10 insertions(+)


commit 58b895f5ff6333b1a0956dd83e478542dc7a10d3
Author: Michal Maloszewski <michal.maloszewski@canonical.com>
Date:   Tue Jan 17 16:13:46 2023 +0100

    merge-changelogs

 debian/changelog | 68
 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 68 insertions(+)
```

This command shows the specific commit, as well as what changed within the commit (i.e., how many files were changed and how many insertions and deletions there were).

Common examples of commits that need to be split:

* `changelog` with any other file(s) changed in a single commit
* `debian/changelog` with any other file(s) changed in a single commit
* commit named: `Import patches-unapplied version 1.2.3ubuntu4 to ubuntu/cosmic-proposed`, where it's applying from an Ubuntu source rather than a Debian one (in this case `ubuntu4`)

Check all commits just to make sure.

If there are no commits to split, {ref}`add the "split" tag <merge-tag-split>` and continue to {ref}`merge-prepare-the-logical-view`.


(merge-identify-logical-changes)=
### Identify logical changes

Separate the changes into logical units. For the {pkg}`at` package, this is trivial: put the {file}`changelog` change in one commit and the {file}`control` change in the other.

The second example, for {pkg}`nspr`, is more instructive. There are five files changed that need to be split out:

* All changelog changes go to one commit called `changelog`.
* Maintainer update (in `debian/control`) goes to one commit called `update maintainers`.
* All other logically separable commits go into individual commits.

Look in {file}`debian/changelog`:

```none
nspr (2:4.18-1ubuntu1) bionic; urgency=medium

  * Resynchronize with Debian, remaining changes
    - rules: Enable Thumb2 build on armel, armhf.
    - d/p/fix_test_errcodes_for_runpath.patch: Fix testcases to handle
      zesty linker default changing to --enable-new-dtags for -rpath.
```

There are two logical changes, which you need to separate. Look at the changes in individual files to see which file changes should be logically grouped together.

Example:

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

Start a rebase at `old/debian`, and then reset to `HEAD^` to bring back the changes as uncommitted changes.

1. Start a rebase: `git rebase -i old/debian`
1. Change the commit(s) you're going to separate from `pick` to `edit`
1. Do a `git reset` to get your changes back: `git reset HEAD^`

Next, add the commits:

------------------------------------------------------------------------------

Logical unit:

```none
$ git add debian/patches/*
$ git commit
```

Commit message:

```none
  * d/p/fix_test_errcodes_for_runpath.patch: Fix testcases to handle
    zesty linker default changing to --enable-new-dtags for -rpath.
```

------------------------------------------------------------------------------

Logical unit:

```none
$ git add debian/rules
$ git commit
```

Commit message:

```none
  * d/rules: Enable Thumb2 build on armel, armhf.
```

------------------------------------------------------------------------------

Maintainers:

```none
$ git commit -m "update maintainers" debian/control
```

------------------------------------------------------------------------------

Changelog:

```none
$ git commit -m changelog debian/changelog
```

------------------------------------------------------------------------------

Finally, complete the rebase:

```none
$ git rebase --continue
```

The result of this rebase should be a sequence of smaller commits, one per `debian/changelog` entry (with potentially additional commits for previously undocumented changes).

It should represent a granular history (viewable with `git log`) for the latest Ubuntu version and no content differences to that Ubuntu version. This can be verified with `git diff -p old/ubuntu`.


(merge-tag-split)=
### Tag split

Do this even if there were no commits to split:

```none
$ git ubuntu tag --split
```

:::{admonition} Purpose of logical tags

If we do this step, we have a distinct boundary between looking at the past (analysis of what is there already) and the actual work we want to perform (bringing the old {term}`Ubuntu delta` forward).

By having a well-defined point, it is easier to do the future work, and also for a reviewer to start from the same point. The reviewer can easily and almost completely automatically determine if the logical tag is correct.

The logical tag is the cleanest possible representation of a previous Ubuntu delta. By determining this representation, we make it as easy as possible to bring the delta forward.

:::


(merge-prepare-the-logical-view)=
## Prepare the logical view

Make a clean, "logical" view of the history. This history is cleaned up (but has the same {term}`delta`) and only contains the actual changes that affect the package's behavior.

Start with a rebase from `old/debian`:

```none
$ git rebase -i old/debian
```

Do some cleaning:

* Delete imports, etc.
* Delete any commit that only changes metadata like changelog or maintainer.
* Possibly rearrange commits if it makes logical sense.

Squash these kinds of commits together:

 * Changes and reversions of those changes because they result in no change.
 * Multiple changes to the same patch file because they should be a logical unit.

To squash a commit, move its line underneath the one you want it to become part of, and then change it from `pick` to `fixup`.


(merge-check-the-result)=
### Check the result

At the end of the "squash and clean" phase, the only delta you should see from the split tag is:

```none
$ git diff --stat split/6.8-0ubuntu2
 debian/changelog | 31 -------------------------------
 debian/control   |  3 +--
 2 files changed, 1 insertion(+), 33 deletions(-)
```

Only `changelog` and `control` were changed, which is what we want.


(merge-create-logical-tag)=
### Create logical tag

What is the logical tag? It is a representation of the Ubuntu delta present against a specific historical package version in Ubuntu.

```none
$ git ubuntu tag --logical
```

This may fail with an error like:

```none
ERROR:HEAD is not a defined object in this git repository.
```

In which case, {ref}`merge-create-logical-tag-manually`.


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


(merge-corollaries)=
### Corollaries

Mistake corrections are squashed.

Changes that fix mistakes made previously in the same delta are squashed against them. For example:

* `2.3-4ubuntu1` was the previous merge.
* `2.3-4ubuntu2` adjusted `debian/rules` to add the `--build-beter` configure flag.
* `2.3-4ubuntu3` fixed the typo in `debian/rules` to say `--build-better` instead.
* When the logical tag is created, there is one commit relating to `--build-better`, which omits any mention of the typo.

:::{note}
If a mistake exists in the delta itself, it is retained. For example, if `2.3-4ubuntu3` was never uploaded and the typo is still present in `2.3-4ubuntu2`, then `logical/2.3.-4ubuntu2` should contain a commit adding the configure flag with the typo still present.
:::


(merge-empty-commits)=
### Empty commits

If a commit becomes empty, it's because the change has already been applied upstream:

```none
The previous cherry-pick is now empty, possibly due to conflict resolution.
```

In such a case, drop the commit:

```none
$ git rebase --abort
$ git rebase -i old/debian
```

Make note of the redundant commit's commit message, then delete the commit in the rebase.


(merge-sync-request)=
### Sync request

If all the commits are empty, or you realized there are no logical changes, you're facing a **sync request**, not a merge. Refer to the {ref}`sync guidelines <syncs>` to continue.


(merge-check-patches-still-apply-cleanly)=
### Check patches still apply cleanly

```none
$ quilt push -a --fuzz=0
```

**If {command}`quilt` fails**

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

If this patch fails because the changes in `ssh-ignore-disconnected.patch` are already applied upstream, you must remove this patch.

```none
$ git log --oneline

1aed93f (HEAD -> ubuntu/devel)   * d/p/ssh-ignore-disconnected.patch: [sshd] ignore disconnected from user     USER (LP: 1644057)
7d9d752 - Drop libsys-cpu-perl and libsys-meminfo-perl from Recommends to   Suggests as they are in universe.
```

Removing `1aed93f` removes the patch.

1. Save the commit message from `1aed93f` for later including it in the `Drop Changes` section of the new changelog entry.
1. `git rebase -i 7d9d752` and delete commit `1aed93f`.


(merge-unapply-patches-before-continuing)=
### Unapply patches before continuing

```none
$ quilt pop -a
```


(merge-adding-new-changes)=
## Adding new changes

Add any new changes you want to include with the merge. For instance, the new package version may {term}`fail to build from source (FTBFS) <FTBFS>` in Ubuntu due to new versions of specific libraries or runtimes.

Each logical change should be in its own commit to match the work done up to this point on splitting the logical changes.

Moreover, there is no need to add changelog entries for these changes manually. They are generated from the commit messages with the merge finish process described below.


(merge-finish-the-merge)=
## Finish the merge

```none
$ git ubuntu merge finish pkg/ubuntu/devel
```

If this fails, {ref}`merge-finish-the-merge-manually`.


## Next

* {ref}`merge-fix-the-changelog`

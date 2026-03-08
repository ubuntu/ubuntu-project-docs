(dual-maintenance-with-salsa-and-git-ubuntu)=
# Dual maintenance with Salsa and git-ubuntu

Some packages for Ubuntu are maintained simultaneously using git-ubuntu and
[Debian Salsa](https://salsa.debian.org). This page outlines how to manage
packages with a specific model such as:

* MySQL:
  [Launchpad](https://launchpad.net/ubuntu/+source/mysql-8.0) |
  [Salsa](https://salsa.debian.org/mariadb-team/mysql/-/tree/mysql-8.0/ubuntu/devel)

More packages of this style may be added here later on. There are also some
packages that require dual maintenance with a slightly different behavior. This
includes:

* QEMU:
  [Launchpad](https://launchpad.net/ubuntu/+source/qemu) |
  [Salsa](https://salsa.debian.org/qemu-team/qemu/-/tree/ubuntu-dev)

  Neither git-ubuntu nor Salsa are dominant for QEMU. A long term Ubuntu delta
  is submitted to Debian and becomes part of build-time procedure which
  generates `d/control` and changes `d/rules` behavior. This isn't useful for
  short-term one off patches, but it helps a lot reduce churn on merges.

* DPDK:
  [Launchpad](https://launchpad.net/ubuntu/+source/dpdk) |
  [Salsa](https://salsa.debian.org/debian/dpdk)

  This is primarily managed in Salsa and, whenever possible, Ubuntu is just a
  sync. All new changes are proposed and committed to the main branch in Salsa
  and cherry picked from there whenever needed. Later in the life-cycle, MRE
  uploads are distribution specific and happen via git-ubuntu.

## Overview

Dual maintenance with Salsa and git-ubuntu is done such that git-ubuntu acts
as the primary source of truth for the Ubuntu package. Meanwhile, the
ubuntu/devel branch on Salsa should be synthesized from git-ubuntu, while also
having references to the Salsa Debian and Upstream branches.

The rest of this page describes how to handle possible situations that arise
when maintaining a package in both git-ubuntu and Salsa.

## Process

* {ref}`salsa-local-setup`

* {ref}`salsa-is-behind-git-ubuntu`

  - {ref}`salsa-base-case`

  - {ref}`salsa-commits-with-rich-history`

  - {ref}`salsa-sync-with-debian`

  - {ref}`salsa-version-bump-on-debian-branch`

  - {ref}`salsa-version-bump-upstream`

* {ref}`salsa-has-extra-commits`

* {ref}`salsa-package-is-in-sync-with-debian`

* {ref}`salsa-updating-debian-to-create-a-sync`

* {ref}`salsa-merge-requests`

  - {ref}`salsa-merge-request-in-launchpad`

  - {ref}`salsa-merge-request-in-salsa`


(salsa-local-setup)=
## Local setup

To maintain a package in both git-ubuntu and Salsa, start by setting up a local
copy of both repositories in the same folder. Then, obtain the official Ubuntu
version through git-ubuntu:

```none
$ git ubuntu clone [package name]
```

Next, navigate to the resulting folder, add the Salsa repository as a new remote
named salsa, and fetch its contents:

```none
$ cd [package name]
$ git remote add salsa git@salsa.debian.org:[team]/[package name].git
$ git fetch salsa
```

For example, to set up MySQL, run the following commands:

```none
$ git ubuntu clone mysql-8.0
$ cd mysql-8.0
$ git remote add salsa git@salsa.debian.org:mariadb-team/mysql.git
$ git fetch salsa
```

Another useful tool to have locally is the
[`adopt.py` script](https://git.launchpad.net/~ubuntu-server/+git/ubuntu-helpers/tree/rbasak/adopt.py).
This will make it easier to copy commits from git-ubuntu to Salsa.


(salsa-is-behind-git-ubuntu)=
## Salsa is behind git-ubuntu

When commits in the `ubuntu/devel` branch on Salsa are behind git-ubuntu's,
adjustments should be made to match them up as closely as possible. There are
several cases that may arise when doing this, listed below.

Regardless of the case, the first step is to check out Salsa's `ubuntu/devel`
branch locally in the combined repository setup.

```none
$ git checkout -b local-salsa/ubuntu/devel salsa/ubuntu/devel
```


(salsa-base-case)=
### Base case

The most common situation when updating Salsa is synthesizing the commit(s)
from git-ubuntu for Ubuntu-specific version updates. This applies to the format
of one version per commit, where commits have names like
`1.1-1ubuntu1 (patches unapplied).` For example:


#### git-ubuntu

```none
debian/sid:      ---- 1.1-1
                           \
ubuntu/devel:               1.1-1ubuntu1 -- 1.1-1ubuntu2 [tag: pkg/import/1.1-1ubuntu2]
```


#### Salsa

```none
upstream:    ---- 1.1
                     \
debian:      -------- 1.1-1
                           \
ubuntu/devel:               1.1-1ubuntu1
```

This can be done using the `adopt.py` script.

```none
$ python3 adopt.py pkg/import/1.1-1ubuntu2
```

The command will result in the following:

```none
upstream:    ---- 1.1
                     \
debian:      -------- 1.1-1
                           \
ubuntu/devel:               1.1-1ubuntu1 -- 1.1-1ubuntu2
```


(salsa-commits-with-rich-history)=
### Commits with rich history

Sometimes, instead of having one commit per version, a few commits may
contribute to a single one as **rich history**. In this case, they can be
rebased onto Salsa's `ubuntu/devel` branch. For example:


#### git-ubuntu

```none
debian/sid:     ---- 1.1-1
                          \
ubuntu/devel:              1.1-1ubuntu1 [tag: pkg/import/1.1-1ubuntu1] -- logic1 -- logic2 -- 1.1-1ubuntu2 changelog
```


#### Salsa

```none
upstream:   ---- 1.1
                    \
debian:     -------- 1.1-1
                          \
ubuntu/devel:              1.1-1ubuntu1
```

In git-ubuntu, version `1.1-1ubuntu2` contains two logical changes and a split
changelog commit. To add this to Salsa, rebase from `logic1` onto
`local-salsa/ubuntu/devel`:

```none
$ git rebase --onto local-salsa/ubuntu/devel pkg/import/1.1-1ubuntu1 ubuntu/devel
```

Salsa will then match git-ubuntu with the rich history included:

```none
upstream:    ---- 1.1
                     \
debian:      -------- 1.1-1
                           \
ubuntu/devel:               1.1-1ubuntu1 -- logic1 -- logic2 -- 1.1-1ubuntu2 changelog
```


(salsa-sync-with-debian)=
### Sync with Debian

If the package becomes a sync in git-ubuntu, then this behavior can be matched
in Salsa by pointing `ubuntu/devel` to the commit on the main Debian branch for
the version it should be synced to.


#### git-ubuntu

```none
debian/sid:    ---- 1.1-1 -- 1.2-1 ---------------------------- 1.2-2
                                                                  |
ubuntu/devel:                                                     *
```


#### Salsa

```none
upstream:  ---- 1.1 ---- 1.2
                   \        \
debian:    -------- 1.1-1 -- 1.2-1 ---------------------------- 1.2-2 [tag: debian/1.2-2]
                                  \
ubuntu/devel:                      1.2-1ubuntu1 -- 1.2-1ubuntu2
```

With Salsa's `ubuntu/devel` checked out locally, hard reset the branch to the
desired Debian commit:

```none
$ git reset --hard debian/1.2-2
```

This will result in the following:

```none
upstream:  ---- 1.1 ---- 1.2
                   \        \
debian:    -------- 1.1-1 -- 1.2-1 ---------------------------- 1.2-2
                                                                  |
ubuntu/devel:                                                     *
```

Note that previous commits on the `ubuntu/devel` branch will be eliminated by
this operation. The changes must be force pushed to Salsa:

```none
$ git push --force salsa ubuntu/devel
```


(salsa-version-bump-on-debian-branch)=
### Version bump on Debian branch

If the next version to move from git-ubuntu is not a sync, but is still based
on a new Debian version, then the Debian version in Salsa should be a parent of
the copied commit.


#### git-ubuntu

```none
debian/sid:      ---- 1.3-1 ------------------------------- 1.3-2
                           \                                     \
ubuntu/devel:               1.3-1ubuntu1 -- 1.3-1ubuntu2 -------- 1.3-2ubuntu1 [tag: pkg/import/1.3-2ubuntu1]
```

#### Salsa

```none
upstream:    ---- 1.3
                     \
debian:      -------- 1.3-1 ------------------------------- 1.3-2 [tag: debian/1.3-2]
                           \
ubuntu/devel:               1.3-1ubuntu1 -- 1.3-1ubuntu2
```

To copy git-ubuntu's `ubuntu/devel` commit and parent with Salsa's Debian
branch, run `adopt.py` with the parent argument.

```none
$ python3 adopt.py -p debian/1.3-2 pkg/import/1.3-2ubuntu1
```

The new commit will then match this structure:

```none
upstream:    ---- 1.3
                     \
debian:      -------- 1.3-1 ------------------------------- 1.3-2
                           \                                     \
ubuntu/devel:               1.3-1ubuntu1 -- 1.3-1ubuntu2 -------- 1.3-2ubuntu1
```


(salsa-version-bump-upstream)=
### Version bump upstream

In the case where Ubuntu is updating to a new upstream version but Debian has
not yet done so, the cherry-picked commit will have to use the version commit
in the upstream branch as a parent.


#### git-ubuntu

```none
debian/sid:      ---- 1.4-1
                           \
ubuntu/devel:               1.4-1ubuntu1 -- 1.4-1ubuntu2 -- 1.5-0ubuntu1 [tag: pkg/import/1.5-0ubuntu1]
```


#### Salsa

```none
upstream:    ---- 1.4 ------------------------------- 1.5 [tag: upstream/1.5]
                     \
debian:      -------- 1.4-1
                           \
ubuntu/devel:               1.4-1ubuntu1 -- 1.4-1ubuntu2
```

If the new version needed for the commit is not yet in the Salsa upstream
branch, then it will need to be added via `gbp`.

```none
$ git checkout pkg/import/1.5-0ubuntu1
$ git ubuntu export-orig
$ gbp import-orig --upstream-branch=upstream --no-merge ../[package name]_1.5.orig.tar.gz
$ git checkout local-salsa/ubuntu/devel
```

Similar to parenting a Debian commit, run `adopt.py` and use the upstream
commit as a parent:

```none
$ python3 adopt.py -p upstream/1.5 pkg/import/1.5-0ubuntu1
```

```none
upstream:    ---- 1.4 ------------------------------- 1.5
                     \                                   \
debian:      -------- 1.4-1                               \
                           \                               \
ubuntu/devel:               1.4-1ubuntu1 -- 1.4-1ubuntu2 -- 1.5-0ubuntu1
```


(salsa-has-extra-commits)=
## Salsa has extra commits

If Salsa's `ubuntu/devel` branch contains extra commits not found in git-ubuntu,
these commits should be submitted to it via a rebase. However, if there are also
commits to transfer from git-ubuntu to Salsa, this should be done first. Run
through the [Salsa is behind git ubuntu](#salsa-is-behind-git-ubuntu) process,
but instead of checking out a local copy of Salsa's `ubuntu/devel`, create a new
branch at the commit where git-ubuntu and Salsa diverge. For example:


### git-ubuntu

```none
debian/sid:      ---- 1.1-1
                           \
ubuntu/devel:               1.1-1ubuntu1 -- 1.1-1ubuntu2 -- 1.1-1ubuntu3
```


### Salsa

```none
upstream:    ---- 1.1
                     \
debian:      -------- 1.1-1
                           \
ubuntu/devel:               1.1-1ubuntu1 -- extra-commit
```

Which becomes:

```none
upstream:    ---- 1.1
                     \
debian:      -------- 1.1-1
                           \
ubuntu/devel:               1.1-1ubuntu1 -- extra-commits
                                 |
import-git-ubuntu:               * -- 1.1-1ubuntu2 -- 1.1-1ubuntu3
```

Next, rebase the extra Salsa commits onto the synthesized commits. When doing
so, changelog entries added in the extra commits should be modified accordingly.

```none
upstream:    ---- 1.1
                     \
debian:      -------- 1.1-1
                           \
ubuntu/devel:               \                                                          *
                             \                                                         |
import-git-ubuntu:            1.1-1ubuntu1 -- 1.1-1ubuntu2 -- 1.1-1ubuntu3 -- extra-commits (1.1-1ubuntu4)
```

Note that this change will require a force push to go through.


(salsa-package-is-in-sync-with-debian)=
## Package is in Sync with Debian

When maintaining a package that is currently a sync with Debian, Salsa becomes
the main source of truth. As long as changes are not urgent, they should be
merged into the main Debian branch on Salsa, then synced automatically (or
manually) into git-ubuntu. Make sure Salsa's `ubuntu/devel` branch continues to
point to the Debian branch.


(salsa-updating-debian-to-create-a-sync)=
## Updating Debian to create a Sync

It is ideal to sync Ubuntu with Debian to make dual maintenance easier. This can
be done when Ubuntu is ahead of Debian by one or more deltas, and Salsa matches
up with git ubuntu.

To create a sync, start by breaking down the additional Ubuntu commits into
their logical components (see {ref}`merge-split-commits`).
Set the commit message for each logical commit to match its info in the
changelog. For example, if the tree looks like the following:

```none
upstream:    ---- 1.4
                     \
debian:      -------- 1.4-1
                           \
ubuntu/devel:               1.4-1ubuntu1 -- 1.4-1ubuntu2
```

It may then become:

```none
upstream:    ---- 1.4
                     \
debian:      -------- 1.4-1
                           \
ubuntu/devel:               logic1 -- logic2 -- changelog -- logic3 -- changelog -- update maintainers
```

Now changelog and update maintainer commits can be removed:

```none
upstream:    ---- 1.4
                     \
debian:      -------- 1.4-1
                           \
ubuntu/devel:               logic1 -- logic2 -- logic3
```

Ideally, merge requests should contain singular logical changes. If the logical
changes are independent of each other, then cherry pick each one onto its own
branch and create a Salsa merge request. After checking out the Debian branch,
run the following for each change:

```none
$ git branch logic1-change
$ git cherry-pick [logic1 commit hash]
$ git push salsa logic1-change
```

The tree then becomes:

```none
upstream:    ---- 1.4
                     \
debian:      -------- 1.4-1
                        |  \
ubuntu/devel:           |   logic1 -- logic2 -- logic3
                        |\
logic1-change           | logic1
                        |\
logic2-change           | logic2
                         \
logic3-change             logic3
```

For each merge request, set the source branch to the logical change branch and
the destination to the Debian branch. Changes can then be rebased onto the
Debian branch as they are approved.

Otherwise, if the changes are dependent on each other, check out the Debian
branch, and merge the logical commits.

```none
$ git merge local-salsa/ubuntu/devel
```

The tree then becomes:

```none
upstream:    ---- 1.4
                     \
debian:      -------- 1.4-1 -- logic1 -- logic2 -- logic3
                                                     |
ubuntu/devel:                                        *
```

Finally, add a commit to the Debian branch updating the changelog to a new
version with entries for each logical change. The branch can then be submitted
for review in Salsa.

```none
upstream:    ---- 1.4
                     \
debian:      -------- 1.4-1 -- logic1 -- logic2 -- logic3 -- 1.4-2
                                                     |
ubuntu/devel:                                        *
```

Once it is approved and merged in, create a sync request in Launchpad. Once the
sync is approved there, the Salsa `ubuntu/devel` branch can be reset to the
Debian branch.

```none
upstream:    ---- 1.4
                     \
debian:      -------- 1.4-1 -- 1.4-2
                                 |
ubuntu/devel:                    *
```


(salsa-merge-requests)=
## Merge requests


(salsa-merge-request-in-launchpad)=
### Merge request in Launchpad

In general, merge requests made internally should be done through Launchpad.
Once a Launchpad merge request is approved, the commits can be synthesized for
Salsa. The transfer to Salsa is only required when updating `ubuntu/devel`.


(salsa-merge-request-in-salsa)=
### Merge request in Salsa

When a merge request is made to `ubuntu/devel` in Salsa the commits should be
cherry-picked onto `ubuntu/devel` in git-ubuntu then tested from there. Once the
merge request is reviewed in Salsa and confirmed to work in git-ubuntu, a new
merge request should be created in Launchpad. Once this is approved the commits
can then be synthesized back into Salsa. Once the synthesized commits are
uploaded the merge request can be manually marked as merged.


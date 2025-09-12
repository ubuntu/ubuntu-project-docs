(merge-manually)=
# How to merge manually

In case the regular {command}`git-ubuntu`-based {ref}`merge-process` fails, follow these instructions to perform the merge manually.

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
    1. {ref}`merge-submit-merge-proposal`

Extra:
:   * {ref}`merge-manually` (this article)
    * {ref}`merge-cheat-sheet`
:::


(merge-generate-the-merge-branch)=
## Generate the merge branch

Create a branch to do the merge work in:

```none
$ git checkout -b merge-lp1802914-disco
```


(merge-create-tags)=
## Create tags

| Tag          | Source                                                                   |
| ------------ | ------------------------------------------------------------------------ |
| `old/ubuntu` | `ubuntu/<Ubuntu_release>-devel`                                          |
| `old/debian` | Last import tag prior to `old/ubuntu` without `ubuntu` suffix in version |
| `new/debian` | `debian/sid`                                                             |

As per [Debian releases](https://www.debian.org/releases/), `debian/sid` always matches Debian "unstable".

Find the last import tag using {command}`git log`:

```none
git log | grep "tag: pkg/import" | grep -v ubuntu | head -1

commit 9c3cf29c05c3fddd7359e71c978ff9a9a76e4404 (tag: pkg/import/3.1.20-3.1)
```

Based on that, create the following tags:

```none
$ git tag old/ubuntu pkg/ubuntu/disco-devel
$ git tag old/debian 9c3cf29c05c3fddd7359e71c978ff9a9a76e4404
$ git tag new/debian pkg/debian/sid
```


(merge-start-a-rebase)=
## Start a rebase

```none
$ git rebase -i old/debian
```


(merge-clear-any-history)=
## Clear any history, up to and including the last Debian version

Clear any history, up to and including the last Debian version. If the package hasn't been updated since the Git repository structure changed, it grabs all changes throughout time rather than since the last Debian version. Delete the older lines from the interactive rebase.

In this case, up to, and including the import of `3.1.20-3.1`.


(merge-create-reconstruct-tag)=
## Create reconstruct tag

```none
$ git ubuntu tag --reconstruct
```

Next step: {ref}`merge-split-commits`.


(merge-create-logical-tag-manually)=
## Create logical tag manually

Use the version number of the last ubuntu change. So, if there are:

* `3.1.20-3.1ubuntu1`
* `3.1.20-3.1ubuntu2`
* `3.1.20-3.1ubuntu2`

Run:

```none
$ git tag -a -m "Logical delta of 3.1.20-3.1ubuntu2" logical/3.1.20-3.1ubuntu2
```

:::{note}
Certain characters aren't allowed in Git. For example, replace colons (`:`) with percentage signs (`%`).
:::

Next step: {ref}`merge-rebase-onto-new-debian`.


(merge-finish-the-merge-manually)=
## Finish the merge manually

1. Merge the changelogs of old Ubuntu and new Debian:

    ```none
    $ git show new/debian:debian/changelog > /tmp/debnew.txt
    $ git show old/ubuntu:debian/changelog > /tmp/ubuntuold.txt
    $ merge-changelog /tmp/debnew.txt /tmp/ubuntuold.txt > debian/changelog
    $ git commit -m "Merge changelogs" debian/changelog
    ```

1. Create a new changelog entry for the merge:

    ```none
    $ dch -i
    ```

    Which creates, for example:

    ```none
    at (3.1.23-1ubuntu1) disco; urgency=medium

    * Merge with Debian unstable (LP: #1802914). Remaining changes:
        - Suggest an MTA rather than Recommending one.

    -- Karl Stenerud <karl.stenerud@canonical.com>  Mon, 12 Nov 2018 18:11:53 +0100
    ```

1. Commit the changelog:

    ```none
    $ git commit -m "changelog: Merge of 3.1.23-1" debian/changelog
    ```

1. Update maintainer:

    ```none
    $ update-maintainer
    $ git commit -m "Update maintainer" debian/control
    ```

Next step: {ref}`merge-fix-the-changelog`


(merge-get-the-orig-tarball-manually)=
## Get the orig tarball manually

Use the {manpage}`pristine-tar(1)` tool to regenerate the orig (upstream) tarball:

1. Create a new branch for the orig tarball:

    ```none
    $ git checkout -b pkg/importer/debian/pristine-tar
    ```

1. Regenerate the pristine tarball:

    ```none
    $ pristine-tar checkout at_3.1.23.orig.tar.gz
    ```

1. Switch to the merge branch:

    ```none
    $ git checkout merge-3.1.23-1-disco
    ```

    TODO: Is this ^ branch name correct?


(merge-if-git-checkout-also-fails)=
### If git checkout also fails

```none
$ git checkout merge-lp1802914-disco
$ cd /tmp
$ pull-debian-source at
$ mv at_3.1.23.orig.tar.gz{,.asc} ~/work/packages/ubuntu/
$ cd -
```

TODO: This step needs context/explanation.

Next step: Check the source for errors.


(merge-submit-merge-proposal-manually)=
## Submit merge proposal manually

```none
$ git push kstenerud merge-lp1802914-disco
```

Then create a MP manually in Launchpad, and save the URL.

Next step: {ref}`merge-update-the-merge-proposal`.


(merging)=
# Merging

```{toctree}
:maxdepth: 1
:hidden:

preliminary-steps
merge-process
fix-the-changelog
upload-a-ppa
test-the-new-build
git-ubuntu-merge-proposal
Merge manually <merge-manually>
merge-cheat-sheet
```


:::{admonition} **Merging** series
The article series provides guidance on performing package merges.

Process overview:
:   * {ref}`merges-syncs`

```{raw} html
<span style="font-size:0.1px"></span>
```

{ref}`How to do a merge <merging>` (this article):
:   1. {ref}`merge-preliminary-steps`
    1. {ref}`merge-process`
    1. {ref}`merge-fix-the-changelog`
    1. {ref}`merge-upload-a-ppa`
    1. {ref}`merge-test-the-new-build`
    1. {ref}`merge-git-ubuntu-merge-proposal`

Extra:
:   * {ref}`merge-manually`
    * {ref}`merge-cheat-sheet`
:::


## Overview

**Merging** (also called "delta rebasing") is the process of taking all Ubuntu changes ({term}`Ubuntu delta`) made on top of one Debian version of a package and re-doing them on top of a new Debian version of the package. See {ref}`merges-syncs` for more context information.

This is not to be confused with a **git merge**, wherein two diverging branches are reconciled together. The Ubuntu merge process (counter-intuitively) does not directly involve a git merge. 

The following diagram compares a standard git merge with an Ubuntu merge:

```{figure} ubuntu_merge_comparison.svg
:alt: Comparison of a standard git merge with an Ubuntu merge
```

Merging is done using the {command}`git-ubuntu` tool and is quite similar to a standard {command}`git rebase` where commits from one point are replayed on top of another point.

At a more detailed level, there are other sub-tasks to be done, including:

* Splitting large, "omnibus"-style commits into smaller logical units (one commit per logical unit).
* Harmonizing `debian/changelog` commits into two commits: a changelog merge and a reconstruction.

With this process, we keep the Ubuntu version of a package cleanly applied to the end of the latest Debian version and make it easy to drop changes as they become redundant.


## Merge-o-Matic

For a list of packages that have changed in Debian but not merged into Ubuntu, see the Merge-o-Matic tool:

* [main](https://merges.ubuntu.com/main.html)
* [universe](https://merges.ubuntu.com/universe.html)
* [restricted](https://merges.ubuntu.com/restricted.html)
* [multiverse](https://merges.ubuntu.com/multiverse.html)

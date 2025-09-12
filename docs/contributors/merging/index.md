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
submit-merge-proposal
Merge manually <merge-manually>
merge-cheat-sheet
```

Merging is the process of taking all Ubuntu changes ({term}`Ubuntu delta`) made on top of one Debian version of a package and re-doing them on top of a new Debian version of the package. See {ref}`merges-syncs` for more context information.

:::{admonition} **Merging** series
The article series provides guidance on performing package merges.

Process overview:
:   * {ref}`merges-syncs`
    * {ref}`merging` (this article)

How to do a merge:
:   1. {ref}`merge-preliminary-steps`
    1. {ref}`merge-process`
    1. {ref}`merge-fix-the-changelog`
    1. {ref}`merge-upload-a-ppa`
    1. {ref}`merge-test-the-new-build`
    1. {ref}`merge-submit-merge-proposal`

Extra:
:   * {ref}`merge-manually`
    * {ref}`merge-cheat-sheet`
:::


## Overview

Merging is done using the {command}`git-ubuntu` tool. As such, the process in many ways follows that of a {command}`git rebase` where commits from one point are replayed on top of another point:

<!--
```{mermaid}
   :caption: `git-ubuntu` process overview
   :alt: git-ubuntu process overview
   :zoom:

gitGraph
   commit id: "something 1.2"
   branch 1.2ubuntu
   checkout 1.2ubuntu
   commit id: "Ubuntu changes a, b, c on 1.2"
   commit id: "1.2ubuntu1"
   checkout main
   commit id: "something 1.3"
   branch 1.3ubuntu
   checkout 1.3ubuntu
   commit id: "Ubuntu changes a, b, c on 1.3"
   commit id: "1.3ubuntu1"
```
-->

```none
--- something 1.2 ----------------------------- something 1.3
     \                                           \
      -- Ubuntu changes a, b, c -- 1.2ubuntu1     -- Ubuntu changes a, b, c -- 1.3ubuntu1
```

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


## Further reading

* {ref}`merges-syncs`

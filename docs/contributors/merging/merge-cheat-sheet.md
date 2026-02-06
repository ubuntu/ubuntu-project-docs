(merge-cheat-sheet)=
# Merge cheat sheet

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
    1. {ref}`merge-git-ubuntu-merge-proposal`

Extra:
:   * {ref}`merge-manually`
    * {ref}`merge-cheat-sheet` (this article)
::::


## Steps of the merge procedure

1. `rmadison <package_name>`
1. `rmadison -u debian <package_name>`
1. `git ubuntu clone <package_name> <package_name>-gu`
1. `cd <package_name>-gu`
1. `git ubuntu merge start pkg/ubuntu/devel`
1. `git checkout -b merge-<version_of_debian_unstable>-<current_ubuntu_devel_name>`
1. `git log --stat old/debian..`
1. `git ubuntu tag --split` (if there's nothing to split, type that command straight away)
1. `git rebase -i old/debian`
1. Drop metadata changes and reorder/merge/split commits.
1. `git diff split/`
1. `git ubuntu tag --logical`
1. `git show logical/<version>` (check if the new tag exists)
1. `git rebase -i --onto new/debian old/debian`
1. `quilt push -a --fuzz=0`
1. `quilt pop -a`
1. `git ubuntu merge finish pkg/ubuntu/devel`


## Further reading

* {ref}`merges-syncs`

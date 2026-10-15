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
    1. {ref}`merge-review-the-changelog`
    1. {ref}`merge-upload-a-ppa`
    1. {ref}`merge-test-the-new-build`
    1. {ref}`merge-git-ubuntu-merge-proposal`

Extra:
:   * {ref}`merge-manually`
    * {ref}`merge-cheat-sheet` (this article)
::::


## Merge with `deltarebase`

1. `git ubuntu clone <package_name> && cd <package-name>`
1. `git ubuntu deltarebase start --bug <bug_number>` (add `--ai` to let an AI agent resolve issues)
1. Fix conflicts, then `git ubuntu deltarebase continue` (or `retry`)
1. Review: `git log --stat lp<bug_number>/new/debian..`, `git show HEAD -- debian/changelog`
1. `git ubuntu deltarebase submit` to push the branch and tags to Launchpad


## Merge manually

1. `rmadison <package_name>`
1. `rmadison -u debian <package_name>`
1. `git ubuntu clone <package_name> <package_name>`
1. `cd <package_name>`
1. `git ubuntu merge start pkg/ubuntu/devel`
1. `git switch -c merge-lp<launchpad_bug_id>-<current_ubuntu_devel_name>`
1. `git log --stat old/debian..`
1. `git ubuntu tag --split` (if there's nothing to split, type that command straight away)
1. `git rebase -i old/debian`
1. Drop metadata changes (changelog, update-maintainer) and reorder/merge/split commits.
1. `git diff split/`
1. `git ubuntu tag --logical`
1. `git show logical/<version>` (check if the new tag exists)
1. `git rebase -i --onto new/debian old/debian`
1. `quilt push -a --fuzz=0`
1. `quilt pop -a`
1. `git ubuntu merge finish pkg/ubuntu/devel`


## Further reading

* {ref}`merges-syncs`

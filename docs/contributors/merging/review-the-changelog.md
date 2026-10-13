(merge-review-the-changelog)=
# Review the changelog

The merge generates the new `debian/changelog` entry from the commit messages of the delta.
Review it, and adjust it where the generated text doesn't describe the delta well.

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
    1. {ref}`merge-review-the-changelog` (this article)
    1. {ref}`merge-upload-a-ppa`
    1. {ref}`merge-test-the-new-build`
    1. {ref}`merge-git-ubuntu-merge-proposal`

Extra:
:   * {ref}`merge-manually`
    * {ref}`merge-cheat-sheet`
::::


(merge-the-generated-entry)=
## The generated entry

Show the new entry:

```none
$ git show HEAD -- debian/changelog
```

It lists each commit of the delta under one of three headings:

```none
  * Merge with Debian unstable (LP: #133734200). Remaining changes:
    - d/rules: optimize build flags for enhanced candy production
  * Dropped changes:
    - d/p/fix_recipe: Adjust recipe to improve flavor
      due to our preferences in taste
      [Fixed in 4.20-1]
  * New changes:
    - d/control: Add dependency to olive oil (LP: #133734201)
```

Remaining changes
: Changes of the previous Ubuntu delta that are still needed.

Dropped changes
: Changes of the previous Ubuntu delta that are no longer needed.
  Each one notes where it went: `[Fixed in <Debian version>]` if Debian took it, `[Upstream in <upstream version>]` if upstream did.

New changes
: Changes added in this merge.

Dropped and new changes are only automatically listed if the logical tag exists; without it, every commit is listed as a remaining change.


(merge-adjust-the-entry)=
## Adjust the entry

Check that:

* Each line reads well as a changelog line, keeping its leading path such as `d/rules:` or `d/p/foo:`.
* Each dropped change names the right place.
  The generated note is a guess: if the new Debian changelog mentions the dropped patch, change `[Upstream in …]` to `[Fixed in <new Debian version>]`.
* Lines wrap at 80 columns, with continuation lines aligned to the text after the bullet.
* The merge line closes the merge bug, and other lines only close bugs their commits are about.

If an entry is wrong because its commit is wrong, for example a misleading commit message or a change in the wrong commit, fix the commit rather than the changelog, using {command}`git rebase -i lp133734200/new/debian`.
Then regenerate the entry in `debian/changelog`:

```none
$ git ubuntu deltarebase changelog
```

Edit `debian/changelog`, then amend the `changelog` commit, which is the last one:

```none
$ git commit --amend debian/changelog
```

Next, you can {ref}`submit <merge-deltarebase-submit>` with {command}`git ubuntu deltarebase submit`.


## Next

* {ref}`merge-upload-a-ppa`

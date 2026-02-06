(merge-fix-the-changelog)=
# Fix the changelog

<!-- TODO:
     We may need to adjust the title of this page. "Fix the changelog" is quite a generic statement that I think could apply to many processes.
-->


`git-ubuntu` attempts to put together a changelog entry, but it will likely have problems. Fix it to make sure it follows the standards. See {ref}`committing your changes <how-to-commit-changes>` for information about what it
should look like.

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
    1. {ref}`merge-fix-the-changelog` (this article)
    1. {ref}`merge-upload-a-ppa`
    1. {ref}`merge-test-the-new-build`
    1. {ref}`merge-git-ubuntu-merge-proposal`

Extra:
:   * {ref}`merge-manually`
    * {ref}`merge-cheat-sheet`
::::


(merge-add-dropped-changes)=
## Add dropped changes

If you dropped any changes (due to upstream fixes), you must note them in the changelog entry:

```none
  * Drop Changes:
    - Foo: change to bar
      [Fixed in 1.2.3-4]
```


(merge-format-any-new-added-changes)=
## Format any new added changes

If you added any new changes, they should be in their own section in the changelog:

```none
  * New Changes:
    - Bar: change to foo
    - Baz: adjust for Foo changes
```


(merge-commit-the-changelog-fix)=
## Commit the changelog fix

```none
$ git commit debian/changelog -m changelog
```


(merge-no-changes-to-debian-changelog)=
## No changes to debian/changelog

The range `old/ubuntu..logical/<version>` should contain no changes to `debian/changelog` at all. We do not consider this part of the logical delta. So, any commits that contain only changes to `debian/changelog` should be dropped.

:::{note}
If you {command}`diff` your final logical tag against the Ubuntu package it analyses, the diff should be empty, except:

1. All changes to `debian/changelog`:

   We deliberately exclude these from the logical tag, relying on commit messages instead.

1. The change that `update-maintainer` introduced, and (rarely) similar changes like a change to `Vcs-Git` headers to point to an Ubuntu VCS instead.

   For the purposes of this workflow, these are not considered part of our "logical delta", and instead are re-added at the end.
:::

:::{tip}
You can use the {command}`execsnoop-bpfcc` tool from the {pkg}`bpfcc-tools` package to find what `debhelper` scripts were called for a certain package. This is helpful for debugging what scripts were called, and what parameters were passed to them.

For example:

```none
$ sudo execsnoop-bpfcc -n multipath
```

Now in another shell run:

```none
$ sudo apt install --reinstall multipath-tools
```

In the original shell, you should see something like:

```none
PCOMM            PID     PPID    RET ARGS
multipath-tools  13939   13931     0 /var/lib/dpkg/info/multipath-tools.prerm upgrade 0.9.4-5ubuntu3
multipath-tools  13951   13931     0 /var/lib/dpkg/info/multipath-tools.postrm upgrade 0.9.4-5ubuntu3
multipath-tools  13959   13956     0 /var/lib/dpkg/info/multipath-tools.postinst configure 0.9.4-5ubuntu3
multipathd       14009   1         0 /sbin/multipathd -d -s
```
:::


## Next

* {ref}`merge-upload-a-ppa`

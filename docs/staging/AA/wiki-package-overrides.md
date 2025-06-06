(component-mismatches-and-changing-overrides)=
# Component mismatches and changing overrides (wiki)

Sadly, packages just don't stay where they're put. {ref}`seed-management`
details how packages get chosen for the `main` component, the various meta
packages and presence on the CD. What it doesn't point out is that packages
which fall out of the seeding process are destined for the `universe` component.
 
Every 30 minutes or so, the difference between what the seeds expect to be true
and what the archive actually believes is evaluated by the
`component-mismatches` tool, and the output placed at:

* [`component-mismatches.txt`](https://ubuntu-archive-team.ubuntu.com/component-mismatches.txt)

* [`component-mismatches.svg`](https://ubuntu-archive-team.ubuntu.com/component-mismatches.svg)
  ([dot source](http://people.canonical.com/~ubuntu-archive/component-mismatches.dot))

This is split into four sections:

**Source and binary promotions to `main`**

These are source packages currently in `universe` that appear to need promoting
to `main`. The usual reasons are that they are seeded, or that a package they
build has become a dependency or build-dependency of a package in `main`.

New sources need to be processed through the
[Ubuntu Main Inclusion Queue](https://wiki.ubuntu.com/UbuntuMainInclusionQueue),
and have been approved before they should be promoted. Also ensure that all of
their dependencies (which will be in this list) are approved as well.

**Binary only promotions to `main`**

These are binary packages currently in `universe` that appear to need promoting
to `main`, as above; except that their source package is already in `main`. An
inclusion report isn't generally needed, though the package should be
sanity-checked.

Especially check that all of the package's dependencies are already in `main`,
or have been approved.

**Source and binary demotions to `universe`**

Sources and their binaries that are currently in `main` but are no longer
seeded or depended on by another package. These either need to be seeded
explicitly, or demoted.

**Binary only demotions to `universe`**

Binary packages in `main` that are no longer seeded or depended on, but the
source is still to remain in `main` -- usually because another binary saves it.
Often these tend to be `-dev` or `-dbg` packages and need to be seeded, rather
than demoted; but not always.

Once you've determined what overrides need to be changed, use the
`change-override` client-side tool to do it.

To promote a binary package to `main`:

```bash
$ ./change-override -c main git-email
```

To demote a source package and all of its binaries to `universe`:
```
$ ./change-override -c universe -S tspc
```

To demote a binary package to `universe` to solve a component-mismatch issue
(note the `-proposed` target rather than the release pocket), typically unseeded
because the new version introduced an unwanted dependency:

```bash
$ ./change-override -c universe -s plucky-proposed erlang-doc
```

Less frequently used are the options to just move a source, and leave its
binaries where it is (usually just to repair a mistaken forgotten `-S`):

```bash
$ ./change-override -c universe tspc
...oops, forgot the source...
$ ./change-override -c universe -t tspc
```

and the option to move a binary and its source, but leave any other binaries
where they are:

```bash
$ ./change-override -c universe -B flite
```

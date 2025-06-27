(aa-priority-mismatches)=
# Priority mismatches

```{note}
This page will be moved to:
* Maintainers -> Archive Admin tasks
```

The [`priority-mismatches`](https://ubuntu-archive-team.ubuntu.com/priority-mismatches.txt)
file tracks priority mismatches in the Archive.

Priority mismatches are generally less important than component mismatches
because wrong priorities have relatively little impact. They affect the behavior
of `debootstrap`, but these days `debootstrap` resolves dependencies on its own
-- so packages with a **too-high** priority will be pulled into default installs,
but **too-low** priorities don't really impact users.


## During Feature Freeze

At the start of Feature Freeze, we review priority mismatches and try to drive
the list to zero.

Packages shown as needing their priority raised, have this because they've been
added as *Recommends* or *Depends* to existing central packages.
We need to make sure these additions are actually desired in Ubuntu to avoid
bloating the base system -- sometimes they only make sense in Debian.

This should be done at Feature Freeze to allow developers time to drop
dependencies that aren't wanted.

As with `component-overrides`, these are managed with `change-override`.

The overrides for a given binary name are the same for all architectures, so
attention should be given to per-arch `priority-mismatches` and decisions made
that make sense (e.g. don't raise the priority of `powerpc-specific` libraries),
and we should not expect the `priority-mismatch` report to be zeroed on ALL
arches.


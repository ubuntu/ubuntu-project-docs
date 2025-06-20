(aa-priority-mismatches)=
# Priority mismatches

Like `component-mismatches`,
[`priority-mismatches`](https://ubuntu-archive-team.ubuntu.com/priority-mismatches.txt)
tracks priority mismatches in the Archive. These are generally less important
than `component-mismatches` because wrong priorities have relatively little
impact: they affect the behavior of `debootstrap` so packages with a too-high
priority will be pulled into default installs necessarily, but these days
`debootstrap` will resolve dependencies on its own so too-low priorities don't
really impact users.

However, starting at Feature Freeze we should review these and try to drive the
list to zero because packages showing on this list as needing their priority
raised have this because they've been added as *Recommends* or *Depends* to
existing central packages, and we should make sure these additions are actually
desired in Ubuntu (sometimes they only make sense in Debian) to avoid bloating
the base system. This should be done at Feature Freeze to allow developers time
to drop dependencies that aren't wanted.

As with `component-overrides`, these are managed with `change-override`.

The overrides for a given binary name are the same for all architectures, so
attention should be given to per-arch `priority-mismatches` and decisions made
that make sense (e.g. don't raise the priority of `powerpc-specific` libraries),
and we should not expect the `priority-mismatch` report to be zeroed on ALL
arches.


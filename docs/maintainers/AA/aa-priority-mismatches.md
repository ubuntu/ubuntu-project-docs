(aa-priority-mismatches)=
# Priority mismatches

Priority mismatches are handled by the
{ref}`Archive Admin <archive-administration>` team.

Package priorities are defined in the
[debian policy](https://www.debian.org/doc/debian-policy/ch-archive.html#s-priorities),
but Ubuntu does not follow these exactly. We had seeds and germinate from very
early on in Ubuntu's history and priorities mattered to various installation
tools to varying extents.

When answering the question "how should we set priorities in Ubuntu?",
generating them from seeds seemed like a natural fit. We ended up with the
*required*, *minimal*, and *standard* seeds mapping to *Priority: required*,
*Priority: important*, and *Priority: standard* respectively, while everything
else is *Priority: optional* (or the deprecated *Priority: extra*).

Priority mismatches are generally less important than component mismatches
because wrong priorities have relatively little impact. They affect the behavior
of `debootstrap`, but these days `debootstrap` resolves dependencies on its own
-- so packages with a **too-high** priority will be pulled into default installs,
but **too-low** priorities don't really impact users.


## Priority mismatch report

The `priority-mismatches` file (
[txt](https://ubuntu-archive-team.ubuntu.com/priority-mismatches.html) or
[html](https://ubuntu-archive-team.ubuntu.com/priority-mismatches.html))
tracks and reports priority mismatches in the Archive.


## When we resolve priority mismatches

* Regular: While processing requests and queues, an Archive Admin can handle
  them at any time. However, it is of relatively low priority compared to other
  efforts.

* Towards Feature Freeze: At this time, we review priority mismatches and try
  to drive the list to zero. Doing so during this period still allows developers
  time to drop dependencies that aren’t wanted.

## How to solve a priority mismatch

Packages shown as needing their priority raised, have this because they’ve
been added as *Recommends* or *Depends* to existing central packages. We need
to make sure these additions are actually desired in Ubuntu to avoid bloating
the base system – sometimes they only make sense in Debian.

As with component-overrides, these are managed with change-override. To act on
priority mismatches we:

* Track it down to the dependency/seed change that caused it
* See why it changed:

  * If it is OK, act and override the priority

  * If it is not OK, contact the package owner or the uploader of the change

    Example:

    `$ ./change-override -n -s questing -e 3.5.0-2ubuntu1 -p required openssl-provider-legacy`

The overrides for a given binary name are the same for all architectures, so
attention should be given to per-arch priority-mismatches and decisions made
that make sense (e.g. don’t raise the priority of powerpc-specific libraries).
Due to that we should not expect the priority-mismatch report to be fully
zeroed on ALL arches.


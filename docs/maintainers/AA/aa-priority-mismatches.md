(aa-priority-mismatches)=
# Priority mismatches

Priority mismatches are handled by the
{ref}`Archive Admin <archive-administration>` team.

Package priorities are defined in the
[debian policy](https://www.debian.org/doc/debian-policy/ch-archive.html#s-priorities),
but Ubuntu does not follow these exactly. We had {ref}`seeds` and germinate
from very early on in Ubuntu's history and priorities mattered to various
installation tools to varying extents.

When answering the question "how should we set priorities in Ubuntu?",
generating them from seeds seemed like a natural fit. We ended up with the
*required* and *minimal* seeds mapping to *Priority: required* and
*Priority: important* respectively, while everything else is
*Priority: optional* (or the deprecated *Priority: extra*).

Only the packages listed in those seeds themselves get those priorities.
[Debian policy 4.0.1](https://www.debian.org/doc/debian-policy/upgrading-checklist.html#version-4-0-1)
dropped the rule that a package may not depend on packages of a lower priority,
on the grounds that the tools which construct installations resolve
dependencies themselves, so a library does not inherit *Priority: required*
from the package that depends on it. *Priority: standard* carries no meaning in
Ubuntu either -- what the *standard* seed delivers is the `ubuntu-standard`
metapackage -- so we neither set nor check it, and differences between
*standard*, *optional* and *extra* are left alone.

Priority mismatches are generally less important than component mismatches
because wrong priorities have relatively little impact. They affect the behavior
of `debootstrap`, but these days `debootstrap` resolves dependencies on its own
-- so packages with a **too-high** priority will be pulled into default installs,
but **too-low** priorities don't really impact users.


## Priority mismatch report

The `priority-mismatches` file (
[txt](https://ubuntu-archive-team.ubuntu.com/priority-mismatches.txt) or
[html](https://ubuntu-archive-team.ubuntu.com/priority-mismatches.html))
tracks and reports priority mismatches in the Archive. Packages are grouped by
the set of architectures a mismatch applies to -- most apply to all of them --
and each group is followed by the `change-override` invocation that clears it.


## When we resolve priority mismatches

* Regular: While processing requests and queues, an Archive Admin can handle
  them at any time. However, it is of relatively low priority compared to other
  efforts.

* Towards Feature Freeze: At this time, we review priority mismatches and try
  to drive the list to zero. Doing so during this period still allows developers
  time to drop dependencies that aren’t wanted.

## How to solve a priority mismatch

Packages shown as needing their priority raised are in the *required* or
*minimal* seed without the matching override, so what to look at is the seed
change that added them. We need to make sure these additions are actually
desired in Ubuntu to avoid bloating the base system – sometimes they only make
sense in Debian.

As with component-overrides, these are managed with change-override. To act on
priority mismatches we:

* Track it down to the change that caused it: a seed change, or a new binary
  package carrying a priority of its own from `debian/control`
* See why it changed:

  * If it is OK, act and override the priority

  * If it is not OK, contact the package owner or the uploader of the change

    Example:

    `$ ./change-override -n -s questing -e 3.5.0-2ubuntu1 -p required openssl-provider-legacy`

Binary overrides in Launchpad are per architecture: `change-override -a` sets a
priority that later uploads for that architecture inherit, so the report can be
driven to zero on all architectures. Decisions still have to make sense per
architecture (e.g. don’t raise the priority of powerpc-specific libraries
everywhere). There are two cases where the override is shared rather than
per-architecture, which the report points out instead of suggesting a command:

* an *Architecture: all* binary is published to every architecture with a
  single override, taken from the architecture nominated for
  architecture-independent binaries (amd64), so its priority cannot differ
  between architectures;

* `amd64v3` publishes amd64’s binaries with amd64’s override, unless the
  source is rebuilt for the variant.


#. 

   #. page was renamed from KernelUpdates

.. _kernel_security_and_update_policy_for_post_release_trees:

Kernel security and update policy for post-release trees
========================================================

This document describes the process and criteria for post-release kernel
updates. The kernel is a very complex source package, and it is
fundamentally different than other packages in the archive. The
described process and criteria are built on the normal
StableReleaseUpdates document, and where these documents conflict, this
document takes precedence.

.. _what_sort_of_updates_are_allowed_for_post_release_kernels:

What sort of updates are allowed for post-release kernels?
----------------------------------------------------------

There are several categories of updates, in addition to normal security
updates:

-  Critical bug fixes. These are categorized as non-security issues
   relating to bugs that affect a large range of users. These are bugs
   that keep users from reliably using their systems, or prevent booting
   at all. These patches must pass through rigorous testing by
   Canonical/Ubuntu and the community at large.
-  Supported vendor patches. These are patches generally related to
   hardware support. If they are very specific to a piece of hardware,
   the nature of the patch makes regression on other hardware unlikely
   or impossible, and we have the hardware available for thorough
   testing, then it can be part of an SRU. Otherwise they need to be
   maintained in a separate repository/pocket/PPA specific for that
   vendor or, if appropriate, in \`linux-backports-modules\`, and thus
   need to be maintained separately in the future.
-  Mainline Stable Updates. These are upstream blessed patches which are
   deemed important enough to backport to older releases. These patches
   must pass testing both upstream and by Canonica/Ubuntu.

Other changes are generally avoided on stable kernels, since the
regression potential is so exceptionally high.

All non-security changes need to follow the standard SRU procedure in
terms of having a bug associated with them, which is fixed in the
development release and signed off by \`ubuntu-sru\` or
\`canonical-qa\`, and the changelog needs to include the bug number.

.. _how_long_will_updates_be_allowed_for_a_release:

How long will updates be allowed for a release
----------------------------------------------

This answer is directed at non-LTS releases. For normal 18-month
releases, we will only accept updates to the kernel for 3-4 months after
release. At this point we consider the in-development release to be
stable enough for testing, and the primary target for fixing bugs. Plus,
3-4 months after release, most major bugs are either reported and fixed
in the stable release, or deemed unfixable.

There may be a few exceptions to this, but don't count on them.

.. _mainline_stable_updates:

Mainline Stable Updates
-----------------------

Where mainline is providing stable updates (the stable maintainer trees
stable-2.6.27.y etc) these will be considered for inclusion as they
release.

For non-LTS releases these will generally be incorporated in full for
the initial 3-4 month bug fixing period. After this patches will only be
incorporated where there is demonstrated user need, following the normal
SRU process for each change.

For LTS releases these will generally be incorporated in full for the
life of the release. These will necessitate longer baking of the
releases in -proposed to weed out possible regressions. It should be
noted that as the release matures the flow of these updates are expected
to slow significantly as the release diverges further from the
development version.

.. _how_will_updates_be_provided_in_the_archive:

How will updates be provided in the archive
-------------------------------------------

-  Urgent security updates will be uploaded directly into -security
   without other changes. This just requires a temporary GIT fork which
   will be immediately merged back into the main branch for that stable
   release.
-  Less urgent security updates and non-security patches will be
   uploaded to -proposed and then just follow the normal SRU QA
   procedure (testing, confirming bugs, etc). After verification, these
   kernels are copied verbatim to -security, and the USN is issued. This
   avoids maintaining two GIT trees for stable releases while still
   keeping the testing period.
-  Non-security updates which change the ABI should be either avoided at
   all, or be combined with security updates which require ABI change
   anyway.

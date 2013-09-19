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

Additionally to the generic requirements acceptable bugs fall into one
of the following criteria:

#. It fixes a critical issue (data-loss, OOPs, crashes) or is security
   related (security related issues might be covered by security
   releases which are special in handling and publication).
#. Simple, obvious and short fixes or hardware enablement patches as
   long as the next release has not reached beta status. If there is a
   related upstream stable tree open (see below) this class of patches
   is required to come through the upstream process. Patches sent
   upstream for that reason must include their *!BugLink* reference.
#. For 3 months after a non-LTS release or the lifetime of a LTS release
   we will be pulling upstream stable updates from the corresponding
   series. There will be one tracking bug report for each stable update
   but additional references to existing bugs will be added to the
   contained patches (on best can do base). Uploads containing a
   upstream stable patchset increase the retention period to two weeks,
   while it is one week otherwise.
#. Fixes to drivers which are not upstream are accepted directly if they
   fall into the first two categories.
#. *$DEITY* intervention. Might happen, but very very rarely and will
   not be explainable.

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

.. _how_does_the_process_work:

How does the process work
-------------------------

-  First step for every SRU is to have a bug associated.
-  The patch or patches **must** contain the link to the Launchpad bug
   and contain a Signed-off-by line from the submitter. Please refer to
   https://wiki.ubuntu.com/Kernel/Dev/StablePatchFormat for detailed
   information regarding SRU patch formatting.
-  The beginning of the description area of the bug needs to have a SRU
   justification which should look like this example:

``   SRU Justification:``

| ``   Impact: ``\ 
| ``   Fix: <how was this fixed, where did the fix come from>``
| ``   Testcase: ``\ 

.. raw:: html

   </pre>

-  If the fix for a problem applies to the requirements for a SRU and
   has also been tested to successfully solved the bug, then the next
   step depends on whether the fix is serious enough to be directly
   applied or whether it should go in via upstream stable (as long as
   that is appropriate).
-  For serious problem fixes, the patch must be sent the the kernel-team
   mailing list. There is requires ACKs from two senior kernel-team
   members and then will be applied to the kernel tree. Even though
   going into the tree on the faster path, the next step should be done.

| ``   To: kernel-team@lists.ubuntu.com``
| ``   Subject: [``\ \ ``] SRU: ``\ 

``   ``\ 

``   ``\ 

.. raw:: html

   </pre>

-  For all other patches (as long as the upstream stable is appropriate)
   the fix has to be sent upstream (when the problem is there as well
   and the patch is not a backport) and to stable@kernel.org (if it has
   not been sent there before). As soon as that is accepted there, it
   will come back its way when we pull stable updates.

.. _how_will_updates_be_provided_in_the_archive:

How will updates be provided in the archive
-------------------------------------------

-  Security updates will be uploaded directly into -security without
   other changes. This just requires a temporary GIT fork which will be
   immediately merged back into the main branch for that stable release.
-  Normal updates will be provided as pre-releases through the
   kernel-ppa users PPA. At certain points those get made into proposed
   releases which are uploaded to the proposed pocket. Then again they
   have to get verified to fix the problems and not to cause
   regressions.

.. _reference-exception-kernelupdates:

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

In addition to the generic SRU requirements, we will accept patches
which fall into any of the following categories:

#. It fixes a critical issue (data-loss, OOPs, crashes) or is security
   related. Security related issues might be covered by security
   releases which are special in handling and publication.
#. Simple, obvious and short fixes or hardware enablement patches. If
   there is a related upstream stable tree open (see below) this class
   of patches is required to come through the upstream process. Patches
   sent upstream for that reason must include their *!BugLink*
   reference.
#. The patch is included in a corresponding upstream stable or extended
   stable release. For the lifetime of both LTS and non-LTS releases we
   will be pulling upstream stable updates from the corresponding
   series. There will be one tracking bug report for each stable update
   but additional references to existing bugs will be added to the
   contained patches (on best can do base).
#. Fixes to drivers which are not upstream are accepted directly if they
   fall into the first two categories.

.. _how_does_the_process_work:

How does the process work?
--------------------------

-  First step for every SRU is to have a bug associated.
-  The patch or patches **must** contain the link to the Launchpad bug
   and contain a Signed-off-by line from the submitter. Please refer to
   https://wiki.ubuntu.com/Kernel/Dev/StablePatchFormat for detailed
   information regarding Ubuntu Kernel SRU patch formatting.
-  The beginning of the description area of the bug needs to have a SRU
   justification which should look like this example:

``   SRU Justification:``

| ``   Impact: ``\ 
| ``   Fix: <how was this fixed, where did the fix come from>``
| ``   Testcase: ``\ 

.. raw:: html

   </pre>

-  If the fix for a problem meets the requirements for SRU and has been
   tested to successfully solve the bug, then the next step depends on
   whether the fix is serious enough to be directly applied to an Ubuntu
   kernel series and/or whether it should go in via upstream stable (as
   long as that is appropriate for upstream stable).

   -  For fixes for serious issues, the patch should be sent the the
      `kernel-team mailing list <mailto:kernel-team@lists.ubuntu.com>`__
      in parallel to being submitted upstream. SRU patches submitted for
      inclusion into an Ubuntu kernel require ACK's from at least two
      senior Ubuntu kernel-team members before being applied to an
      Ubuntu kernel tree. Again, even when going into an Ubuntu kernel
      tree on an accelerated path, the patch should also be submitted
      upstream. Ubuntu Kernel SRU patch submission format is loosely as
      follows:

| ``   To: kernel-team@lists.ubuntu.com``
| ``   Subject: [``\ \ ``] SRU: ``\ 

``   ``\ 

``   ``\ 

.. raw:: html

   </pre>

-  

   -  For all other patches which do not need an accelerated path into
      an Ubuntu kernel, it is advised to push the fix upstream when
      appropriate, ie. the problem exists upstream, and CC'ing
      stable@kernel.org during the process. As soon as the patch is
      accepted upstream/upstream-stable, it will naturally find it's way
      back down into our Ubuntu kernel when we pull
      upstream/upstream-stable updates. This ensures patches are getting
      vetted and applied upstream and reduces overall maintenance costs
      for the Ubuntu Kernel Team.

.. _how_will_updates_be_provided_in_the_archive:

How will updates be provided in the archive?
--------------------------------------------

-  Security updates will be uploaded directly into -security without
   other changes. This just requires a temporary GIT fork which will be
   immediately merged back into the main branch for that stable release.
-  Normal updates will be provided as pre-releases through the
   kernel-ppa users PPA. At certain points those get made into proposed
   releases which are uploaded to the proposed pocket. Then again they
   have to get verified to fix the problems and not to cause
   regressions.

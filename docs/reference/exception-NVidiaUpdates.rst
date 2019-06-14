\||<tablestyle="float:right; font-size: 0.9em; width:40%;
background:#F1F1ED; margin: 0 0 1em 1em;" style="padding:0.5em;"><>|\|

Introduction
------------

This document describes the policy, process and criteria for updating
nVidia proprietary drivers in a stable supported distro, including LTS.

nVidia proprietary GPU drivers are broadly used by gamers or for GPU
compute activities (AI/ML). Support for new GPUs as well as bug fixes
are regularly released by the vendor (on average 2 driver updates a
month). For an improved experience or simply to support new GPUs without
installing drivers from unofficial sources (for example PPAs), it is
essential to release the latest version of the drivers regularly to the
stable releases of Ubuntu.

.. _what_sort_of_updates:

What sort of updates
--------------------

There are 3 levels of supported drivers:

-  **Long lived branch**: This series is to provide critical or low risk
   fixes and other minor updates for non-legacy hardware without
   exposing any new functionalities. These releases are intended for
   users of non-legacy GPUs who don't necessarily need the latest and
   greatest features. Support for new GPUs can be backported to this
   series.
-  **Short lived branch**: As opposed to the long lived branch, this
   series provides introduces new features.
-  **Legacy drivers**: Legacy GPUs are older-generation nVidia GPUs
   which are no longer supported in the regular nVidia Unified UNIX
   Graphics Driver. Instead, these GPUs will continue to be supported
   through special "Legacy GPU" drivers that will be updated
   periodically to add support for new versions of Linux system
   components (e.g., new Linux kernels, new versions of the X server,
   etc). Support timeframe for legacy drivers is documented on `the
   official nVidia site support
   page <https://nvidia.custhelp.com/app/answers/detail/a_id/3142>`__

The release targeted by the SRU are:

-  **LTS**

   -  

      -  Long lived branch,
      -  Short lived branch,
      -  Legacy.

-  **Non-LTS**

   -  

      -  Long lived branch,
      -  Legacy.

Short lived branch **are not** SRUed to non-lts releases to align the
policy on the HWE stacks however this decision can be revisited
depending on the demand.

When a new major version of a driver is available and uploaded, the
versioning and naming scheme of the packages is so that users won’t be
automatically upgraded to the latest version. They will only have
updates for minor releases of a driver.

For example if version 100.1 is in the LTS.

-  Version 100.2 is uploaded to the LTS, users will be upgraded.
-  Version 110.1 is uploaded to the LTS, a transitional package is
   created to upgrade the user to the latest version of the branch.
   Although we won’t upgrade a long lived branch to a short lived one.
   However we might upgrade users from a short lived branch to a long
   lived branch.

If several versions of the driver support the GPU, ubuntu-driver will
expose them all.

.. _release_schedule:

Release Schedule
----------------

-  Week 0: New version of a driver released by the vendor

   -  

      -  Week 1: Packaging (porting patches against new kernel and tool
         chain)

| ``    * Week 2: QA (smoke test, installs, boot, shell comes up)``
| ``      * Week 3: Upload to the development release``
| ``    * Week 2: Packaging for stable releases ``
| ``        * Week 4: QA (Full test suite)``
| ``          * Week 6: Upload to stable releases (-proposed pocket)``
| ``            * Week 8: Promotion to the -updates pocket.``

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be done with a single process bug, instead of individual
bug reports for individual bug fixes. The one bug should have the
following: The SRU should be requested per the StableReleaseUpdates
documented process The template at the end of this document should be
used and all ‘TODO’ filled out The change log will contain a reference
to the single SRU process bug, not all bugs fixed by the SRU. However,
if there are very important bugs that are deemed worthy of reference
they too should be included in the change log. Major changes should be
called out in the SRU template, especially where changed behavior is not
backward compatible. For each release that is proposed to be updated by
the SRU a link to the results of the automated tests so that anyone can
verify that they have been executed successfully. Additionally, the SRU
bug should be verbose in documenting any manual testing that occurred.
Any architecture specific fixes need to be noted and architecture
specific test results included. Any packaging changes (e.g. a dependency
change) need to be stated

.. _qa_process:

QA Process
----------

.. _packaging_qa:

Packaging QA
~~~~~~~~~~~~

The objective of the separate packaging QA is to test: package
installation from scratch package upgrades distribution upgrade

The resulting package, with all the changes in place, must undergo and
pass the following additional QA procedures: Installation from scratch
in the current distribution: using apt-get Upgrade test from previous
version of the package. This test must be performed with: apt-get
install/upgrade Upgrade test from previous distribution to the current
one. If the current distribution is an LTS one, the upgrade path from
the previous LTS distro must also be exercised.

.. _qa_tests:

QA tests
~~~~~~~~

Certification test suite must pass on a range of hardware.

.. _sru_template:

SRU Template
------------

[Impact] This release provides both bug fixes and new features and we
would like to make sure all of our users have access to these
improvements. The notable ones are:

-  

   -  <TODO: Create list with LP: # included >

See the changelog entry below for a full list of changes and bugs.

[Test Case] The following development and SRU process was followed:
https://wiki.ubuntu.com/NVidiaUpdates

<TODO Document any QA done, automated and manual>

The QA team that executed the tests will be in charge of attaching the
artifacts and console output of the appropriate run to the bug. nVidia
maintainers team members will not mark ‘verification-done’ until this
has happened.

[Regression Potential] In order to mitigate the regression potential,
the results of the aforementioned system level tests are attached to
this bug.

<TODO: attach nvidia-proposed test artifacts for every SRU release, not
a link as links expire>

[Discussion] <TODO: other background>

<TODO: Paste in change log entry from nVidia for this version of the
driver>

.. _additional_notes:

Additional notes
----------------

``== References ==``

nVidia Unix Drivers Archive Full history of the drivers Support
timeframe for legacy drivers What is a legacy GPU nVidia drivers staging
PPA

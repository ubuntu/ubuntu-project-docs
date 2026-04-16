.. _reference-exception-NVidiaDocaOfed:

Nvidia DOCA-OFED Driver Updates
===============================

Introduction
------------

This document describes the policy, process and criteria for updating
nVidia proprietary DPU drivers (DOCA-OFED) in a stable supported distro,
including LTS.

nVidia DOCA-OFED drivers are used in conjunction with nVidia Bluefield cards,
DGX and IGX platforms and Connect-X cards. These platforms are used in a variety
of scenarios, included data-centers, AI/ML ...

Support for new platforms, bug fixes and general improvements are released 
regularly by the vendor; there are 4 expected releases during the year
(YY.01, YY.04, YY.07, YY.10) plus possible bug-fixes.

The other 3 releases are ad-interim releases and are considered short-lived.

For an improved experience and support new features/hardware without installing
drivers from an unofficial or an external source (PPAs/FTP...), it is
essential to release the latest version of the drivers regularly to the new
stable releases of Ubuntu.

.. _what_kind_of_updates:

What kind of updates
--------------------

There are 4 expected releases during the year, where YY stands for the year
of release (i.e. YY = 26):

- **Long term support releases**: The YY.10 version is the sole LTS release of
  the year, providing three years of full NVIDIA support.
  This release is designed exclusively for the current Ubuntu version and will
  not be backported or forward-ported to other Ubuntu releases.

- **Short lived releases**: YY.01, YY.04, YY.07 are released in their respective
  months by nVidia, and are considered ad-interim releases, to be substituted
  with the newer one and finish their path into the LTS release.

Each YY.mm release will have a separate .deb package to make easier to track
and fix older releases, with the focus on the LTS ones.

The releases targeted by this SRU are all the 4 releases during the year.

When a new short lived release is available and uploaded, the versioning will
make the user update to the newer release. This happens until the new release
is an LTS one.

If a user has a LTS release installed, the versioning will make the user update
*ONLY* to the newer LTS release, is available for the installed Ubuntu release.


.. _release_schedule:

Release Schedule
----------------

- New version of the driver released by nVidia
- Packaging in Canonical git repository
- Internal release in personal PPA
- QA (smoke test, installs, operational tests, upgrade path test)
- Package ready for release, upload to archive (-proposed pocket)
- Promotion to the -updates pocket

SRU Process
-----------

The SRU should be done with a single process bug and not have multiple bug
reports for each bug fix. The LP bug should contain the following:

- The template at the end of this document should be used and all 'TODO'
  filled out.
- The deb changelog will contain a single reference to the SRU LP bug only.
- Major changes must be listed in the SRU template, especially compatibility
  issues.
- Results of all the conducted tests should be listed, even as a comment,
  in the SRU bug. Any manual test or additional steps taken to perform
  testing should be documented.
- Any packaging changes need to be stated.



NVidia SRU Template
-------------------

::

   [Impact]
   This release provides both bug fixes and new features and we would like to
   make sure all of our users have access to these improvements.
   The notable ones are:

   *** <TODO: Create list with LP: # included >

   See the changelog entry below for a full list of changes and bugs.

   [Test Case]
   The following development and SRU process was followed:
   https://documentation.ubuntu.com/sru/en/latest/reference/exception-NVidia-doca-ofed/

   <TODO Document any QA done, automated and manual>

   The QA team that executed the tests will be in charge of attaching the artifacts and console output of the appropriate run to the bug. nVidia maintainers team members will not mark ‘verification-done’ until this has happened.

   [Regression Potential]
   In order to mitigate the regression potential, the results of the
   aforementioned system level tests are attached to this bug.

   <TODO: attach nvidia-proposed test artifacts for every SRU release, not a link as links expire>


   [Discussion]
   <TODO: other background>


   <TODO: Paste in change log entry from nVidia for this version of the driver>



This document describes the policy for updating ubuntu-advantage-tools
and ubuntu-advantage-pro deb packages into a stable supported release.

In order to add Ubuntu Pro support services to all supported LTS,
ubuntu-advantage-tools will need to be updated periodically to add
support for new services offered on those Ubuntu releases. Regular
(non-LTS) releases will likely not have many available support services,
so risk is limited on regular releases.

The ubuntu-advantage-tools is a Python client (also called the Ubuntu
Pro Client) used to attach machines to existing Ubuntu Pro support
contracts and initialise support services such as Livepatch, FIPS, ESM
and common criteria EAL2. It is a command line interface providing a
single point of entry for enabling, disabling and maintaining Ubuntu Pro
support services on a single machine or cloud instance. It interacts
with a backend ` <contracts_server>`__ https://contracts.canonical.com
` <contracts_server>`__ with GETs and POSTs over https to extract
configuration directives to add or remove APT repos, install deb
packages and/or snaps (in the case of Livepatch).

Any services managed by ubuntu-advantage-tools are described in detail
in ` <https://ubuntu.com/pro>`__ https://ubuntu.com/pro
` <https://ubuntu.com/pro>`__ . You can also read the `documentation for
the Ubuntu Pro
Client <https://canonical-ubuntu-pro-client.readthedocs-hosted.com/en/latest/>`__
for more information on interacting with the tools.

The `ubuntu-advantage-client
repository <https://github.com/canonical/ubuntu-advantage-client/>`__ is
the repository from which all ubuntu-advantage-tools and
ubuntu-advantage-pro packages are built as well as where CI for the
project is run.

The intent of the main branch is to support all Ubuntu releases from
16.04 (Xenial) through devel out of the box without release-specific
changes, though functionality is limited on non-LTS releases. The SRU
process for ubuntu-advantage-tools will target any supported LTS
releases as well as the most recent supported regular release.

Since ubuntu-advantage-tools is the primary mechanism for obtaining
Ubuntu Pro support services on cloud-images (AWS, Azure, GCP),
verification is required on applicable cloud platforms, Ubuntu Pro
images, lxc containers and KVM images.

Therefore, the following types of changes are allowed as long as the
processes outlined below are followed:

-  

   -  Bug fixes
   -  New features

In the event of a change breaking backwards compatibility, SRU team
approval will need to be obtained by emailing the ubuntu-release team
mailing list.

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be done with a single process bug, instead of individual
bug reports for individual bug fixes. The one bug should have the
following:

-  

   -  The SRU should be requested per the StableReleaseUpdates
      documented process
   -  The template at the end of this document should be used and all
      ‘TODO’ filled out
   -  The change log will contain a reference to the single SRU process
      bug, not all bugs fixed by the SRU. However, if there are very
      important bugs that are deemed worthy of reference they too should
      be included in the change log.
   -  Major changes should be called out in the SRU template, especially
      where changed behavior is not backward compatible.
   -  For each release (e.g. Ubuntu 16.04, 18.04 etc.) that is targeted
      by the SRU, a link to the results of integration testing for at
      least the following cloud platforms must be provided:

| ``    * CI success runs covering the *-proposed version ubuntu-advantage-tools:``
| ``      * LXD VM and container of all LTS and regular (e.g. Eoan) releases targeted by the SRU.``
| ``      * EC2 Ubuntu Pro images and standard Canonical cloud images on all LTS releases``
| ``      * Azure Ubuntu Pro images and standard Canonical cloud images on all LTS releases``
| ``      * GCP Ubuntu Pro images and standard Canonical cloud images on all LTS releases``
| ``      * LTS to LTS upgrade test of attached machine for all affected LTS``
| ``      * LTS to LTS upgrade test of unattached machine for all affected LTS``

-  

   -  Any architecture-specific fixes need to be noted and
      architecture-specific test results included
   -  Any packaging changes (e.g. a dependency change) need to be
      stated, and appropriate separate test cases provided
   -  If any manual testing occurs it should also be documented with a
      comment and attached manual logs

.. _qa_process:

QA Process
----------

``  ubuntu-advantage-client repo has a suite of automated integration tests that cover AWS Pro, lxc container and KVM images and exercises the bulk of features functionality delivered on Trusty, Xenial, Bionic and Focal. CI runs both tip of main against daily cloud-images and against any ``\ `````\  <ua-client_active_pull_request>`__\ ```https://github.com/canonical/ubuntu-advantage-client/pulls`` <https://github.com/canonical/ubuntu-advantage-client/pulls>`__\ `\ ```` <ua-client_active_pull_request>`__\ `` before merging.  Additional manual missing manual verification will be attached to each SRU process bug.``

Merges
~~~~~~

Updates to tip of
`ubuntu-advantage-tools:main <https://github.com/canonical/ubuntu-advantage-client/tree/main>`__
go through the following process:

-  

   -  Reviewed and approved by a member of the development team
      (Canonical Ubuntu server team only)
   -  Daily integration tests on tip
   -  Successful run of unit tests, style and integration tests based on
      the branch
   -  Branch manually set to the merged state by the approving
      development member with commit access.

Packaging
~~~~~~~~~

The following describes the requirements for each package generated for
the SRU.

For each package generated a successful completion of
ubuntu-advantage-tools integration tests, as described above in
https://wiki.ubuntu.com/UbuntuAdvantageToolsUpdates#Requesting_the_SRU,
using the proposed package with no unexplained errors or failures

The ubuntu-advantage-tools team (Canonical's Ubuntu Server team) will be
in charge of attaching the artefacts and console output of the
appropriate run to the bug. ubuntu-advantage-tools team members will not
mark ‘verification-done’ until this has happened.

.. _sru_template:

SRU Template
------------

::

   == Begin SRU Template ==
   [Impact]
   This release sports both bug-fixes and new features and we would like to
   make sure all of our supported customers have access to these
   improvements. The notable ones are:

   *** <TODO: Create list with LP: # included>

   See the changelog entry below for a full list of changes and bugs.

   [Test Case]
   The following development and SRU process was followed:
   https://wiki.ubuntu.com/UbuntuAdvantageToolsUpdates

   The ubuntu-advantage-tools team will be in charge of attaching the artifacts and
   console output of the appropriate run to the bug. ubuntu-advantage-tools team
   members will not mark ‘verification-done’ until this has happened.

   * Automated Test Results
   <TODO>
   Attach or link the following automated integration test runs for ubuntu-advantage-tools on each affected LTS release:

   - lxd.container platform
   - lxd.kvm platform
   - AWS Ubuntu PRO
   - AWS Ubuntu cloud-images (non-Pro)

   - Azure Ubuntu PRO
   - Azure Ubuntu cloud-images (non-Pro)

   - GCP Ubuntu PRO
   - GCP Ubuntu cloud-images (non-Pro)
   </TODO>

   [Regression Potential]
   In order to mitigate the regression potential, the results of the
   aforementioned integration tests are attached to this bug.

   [Discussion]
   <TODO: other background>

   == End SRU Template ==

   <TODO: Paste in change log entry>

.. _past_srus:

Past SRUs
---------

Links to past SRUs using this process are below:

\|\| **SRU Version** \|\| **SRU bug** \|\|

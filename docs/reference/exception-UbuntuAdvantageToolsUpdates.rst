This document describes the policy for updating ubuntu-advantage-tools
and ubuntu-advantage-pro deb packages into a stable supported release.

In order to add Ubuntu Advantage support services to all supported LTS,
ubuntu-advantage-tools will need to be updated periodically to add
support for new services offered on those Ubuntu releases. Regular
(non-LTS) releases will likely not have many available support services,
so risk is limited on regular releases.

The ubuntu-advantage-tools is a python client used to attach machines to
existing Ubuntu Advantage support contracts and initialize support
services such as livepatch, fips, esm and common criteria EAL2. It is a
command line interface providing a single point of entry for enabling,
disabling and maintaining Ubuntu Advantage support services on a single
machine or cloud instance. It interacts with a backend
` <contracts_server>`__ https://contracts.canonical.com
` <contracts_server>`__ with GETs and POSTs over https to extract
configuration directives to add or remove apt repos, install deb
packages and/or snaps (in the case of livepatch).

Any services managed by ubuntu-advantage-tools are described in detail
in ` <https://ubuntu.com/advantage>`__ https://ubuntu.com/advantage
` <https://ubuntu.com/advantage>`__ .

The `ubuntu-advantage-client
repository <https://github.com/canonical/ubuntu-advantage-client/>`__ is
the repository from which all ubuntu-advantage-tools and
ubuntu-advantage-pro packages are built as well as where CI for the
project is run.

The intent of the master branch is to support all Ubuntu LTS releases
from 14.04 (Trusty) through 20.04 (Focal) out of the box without
release-specific changes. The SRU process for ubuntu-advantage-tools
will target any supported LTS releases as well as the most recent
supported regular release (e.g. 19.10 Eoan).

One of the big drivers of Ubuntu Advantage support is extended support
of (14.04) Trusty ubuntu-advantage-tools may also target trusty-updates.
Since ubuntu-advantage-tools is the primary mechanism for obtaining
Ubuntu Advantage support services on cloud-images (AWS, Azure),
verification is required on applicable cloud platforms, Ubuntu Pro
images, lxc containers and kvm images.

Therefore, the following types of changes are allowed as long as the
processes outlined below are followed:

-  

   -  Bug fixes
   -  New features

In the event of a change breaking backwards compatibility, then SRU team
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
   -  For each release (e.g. Ubuntu 14.04, Ubuntu 16.04, etc.) that is
      targeted by the SRU, a link to the results of integration testing
      for at least the following cloud platforms must be provided:

| ``    * CI success runs covering the *-proposed version ubuntu-advantage-tools:``
| ``      - LXD VM and container of all LTS and regular (e.g. Eoan) releases targeted by the SRU.``
| ``      - EC2 Ubuntu Pro images and standard Canonical cloud images on all LTS releases``
| ``      - Azure Ubuntu Pro images and standard Canonical cloud images on all LTS releases``

| ``    * Manual test verification of the following:``
| ``      * LTS to LTS upgrade test of attached machine for all affected LTS``
| ``      * LTS to LTS upgrade test of unattached machine for all affected LTS``
| ``      * kvm validation of livepatch enablement on trusty HWE kernels``

-  

   -  Any architecture specific fixes need to be noted and architecture
      specific test results included
   -  Any packaging changes (e.g. a dependency change) need to be stated
   -  If any manual testing occurs it should also be documented with a
      comment and attached manual logs

.. _qa_process:

QA Process
----------

``  ubuntu-advantage-client repo has a suite of automated CI tests that cover AWS Pro, lxc container and kvm images and exercise the bulk of features functionality delivered on trusty, xenial, bionic and focal. CI runs both tip of master against daily cloudimages and against any ``\ `````\  <ua-client_active_pull_request>`__\ ```https://github.com/canonical/ubuntu-advantage-client/pulls`` <https://github.com/canonical/ubuntu-advantage-client/pulls>`__\ `\ ```` <ua-client_active_pull_request>`__\ `` before merging.  Additional manual missing manual verification will be attached to each SRU process bug.``

Merges
~~~~~~

Updates to tip of
`ubuntu-advantage-tools:master <https://github.com/canonical/ubuntu-advantage-client/tree/master>`__
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
ubuntu-advantage-tools integration tests, as described below, using the
proposed package with no unexplained errors or failures

.. _integration_tests:

Integration Tests
~~~~~~~~~~~~~~~~~

Integration testing involves two seperate sections: automated and
manual.

.. _automated_tests:

Automated Tests
^^^^^^^^^^^^^^^

Results from the automated test cases using the version from proposed,
against all LTS releases need to be attached. The automated test cases
cover a variety of cloud-config based scenarios to ensure changes to
ubuntu-advantage-tools/pro do not introduce regressions or unnecessary
changes in behavior.

These tests are run against the LXD container and KVM, AWS "Ubuntu PRO",
AWS standard cloud images, Azure "Ubuntu PRO" and Azure standard cloud
images.

.. _manual_tests:

Manual Tests
^^^^^^^^^^^^

Integration testing involves taking the proposed version of
ubuntu-advantage-tools and running it against a specific test case.
Integration testing needs to take place across all updated releases and
a variety of supported platforms. Releases tested should involve all
releases expected to be updated. Supported platforms must contain at
least each of the following:

-  

   -  for Trusty-targeted SRUs: kvm-based livepatch enablement on Trusty
      on HWE kernels kvm
   -  upgrade path testing from previous LTS version of
      ubuntu-advantage-tools to current release -proposed pkg
   -  regular (non-lts) release manual test run on lxd.container and
      lxd.vm (e.g. eoan)

The test case should be developed as a part of each resolved bug or new
feature. This way testing is straightforward and clear as to what is
expected to work.

The ubuntu-advantage-tools team (Canonical's Ubuntu Server team) will be
in charge of attaching the artifacts and console output of the
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
   https://wiki.ubuntu.com/UbuntuAdvantageToolsUpdate

   The ubuntu-advantage-tools team will be in charge of attaching the artifacts and
   console output of the appropriate run to the bug.  ubuntu-advantage-tools team
   members will not mark ‘verification-done’ until this has happened.

   * Automated Test Results
   <TODO: attach or link automated CI run lxd.container platform for ubuntu-advantage-tools each LTS release>
   <TODO: attach or link automated CI run lxd.vm platform for ubuntu-advantage-tools each LTS release>
   <TODO: attach or link automated CI run AWS Ubuntu PRO for ubuntu-advantage-toolsfor each LTS release>

   * Manual Test Results
   If trusty targeted:
      <TODO: attach manual livepatch enablement on HWE kernels for trusty> 
   For all SRUs:
   <TODO: attach manual upgrade path test from previous LTS to current -proposed release>
   <TODO: attach manual AWS Canonical cloud image (non-PRO) integration test run>
   <TODO: attach manual Azure Ubuntu Pro integration test run> 
   <TODO: attach manual Azure Canonical cloud image (non-PRO) integration test run> 

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

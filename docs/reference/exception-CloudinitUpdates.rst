**DRAFT** **DRAFT** **DRAFT** **DRAFT** **DRAFT**

This document describes the policy for updating cloud-init in a stable,
supported release.

cloud-init is initialization software used for standing up cloud
instances. It can help setup, configure, and customize an instance
during boot.

In order to closely align with the MAAS product and the needs of cloud
providers (e.g. AWS, Azure, GWS) cloud-init needs to be periodically
updated in order to enable new features. Therefore, the following types
of changes are allowed as long as the conditions outlined below are met:

-  

   -  Bug fixes
   -  New features

In the event of a change breaking backwards compatibility, then SRU team
approval will need to be obtained.

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
   -  References to each bug fixed by the SRU should be included in the
      changelog and major changes called out in the SRU template,
      especially where changed behavior is not backwards compatible.
   -  For each release (e.g. trusty, xenial, etc.) that is proposed to
      be updated by the SRU a link to the results of integration testing
      for at least the following datasources must be provided:

| ``    * nocloud (e.g. kvm)``
| ``    * lxd``
| ``    * ec2 (e.g. aws)``
| ``    * azure``
| ``    * gce``

-  

   -  Any architecture specific fixes need to be noted and architecture
      specific test results included
   -  Any packaging changes (e.g. a dependency change) need to be stated
   -  If any manual testing occurs it should also be documented. See LP#
      1588052 as an example.

.. _qa_process:

QA Process
----------

Merges
~~~~~~

Updates to cloud-init trunk go through the following process:

-  

   -  Reviewed and approved by a member of the development team
   -  Daily integration tests on trunk
   -  Successful run of unit tests and style tests based on the branch
   -  Branch set to the committed state

Packaging
~~~~~~~~~

The following describes the requirements for each package generated for
the SRU.

For each package generated a successful completion of cloud-init
integration tests, as described below, using the proposed package with
no unexplained errors or failures

.. _integration_tests:

Integration Tests
~~~~~~~~~~~~~~~~~

Integration testing involves two seperate sections: automated and
manual.

.. _automated_tests:

Automated Tests
^^^^^^^^^^^^^^^

Results from the automated test cases using the version from proposed,
against all releases need to be attached. The automated test cases cover
a variety of cloud-config based scenarios to ensure changes to
cloud-init do not introduce regressions or unnecessary changes in
behavior.

These tests are run against the LXD and KVM backend today. Because of
this lack of coverage against other datasources the following manual
test are also required.

.. _manual_tests:

Manual Tests
^^^^^^^^^^^^

Integration testing involves taking the proposed version of cloud-init
and running it against a specific test case. Integration testing needs
to take place across all updated releases and a variety of supported
platforms. Releases tested should involve all releases expected to be
updated. Supported platforms must contain at least each of the
following:

-  

   -  nocloud (e.g. kvm)
   -  lxd
   -  ec2 (e.g. aws)
   -  azure
   -  gce

The test case should be developed as a part of each resolved bug or new
feature. This way testing is straightforward and clear as to what is
expected to work.

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
   https://wiki.ubuntu.com/CloudinitUpdates

   The cloud-init team will be in charge of attaching the artifacts and
   console output of the appropriate run to the bug.  cloud-init team
   members will not mark ‘verification-done’ until this has happened.

   [Regression Potential]
   In order to mitigate the regression potential, the results of the
   aforementioned integration tests are attached to this bug.

   * Automated Test Results
   <TODO: attach automated cloud-init-proposed test artifacts from tests for each release with lxd artifacts>
   <TODO: attach automated cloud-init-proposed test artifacts from tests for each release with kvm artifacts>

   * Manual Test Results
   <TODO: attach manual cloud-init-proposed test artifacts from tests for each release on nocloud datasource>
   <TODO: attach manual cloud-init-proposed test artifacts from tests for each release on lxd datasource>
   <TODO: attach manual cloud-init-proposed test artifacts from tests for each release on ec2 datasource>
   <TODO: attach manual cloud-init-proposed test artifacts from tests for each release on gce datasource>
   <TODO: attach manual cloud-init-proposed test artifacts from tests for each release on azure datasource>

   [Discussion]
   <TODO: other background>

   == End SRU Template ==

   <TODO: Paste in change log entry>

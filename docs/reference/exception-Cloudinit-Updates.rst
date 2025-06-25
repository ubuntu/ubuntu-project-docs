.. _reference-exception-CloudinitUpdates:

cloud-init Updates
==================

Background
----------

This document describes the policy for updating cloud-init in a stable,
supported release.

cloud-init is initialization software used for standing up cloud
instances. It can help setup, configure, and customize an instance
during boot.

In order to closely align with the MAAS product and the needs of cloud
providers (e.g. AWS, Azure, GWS) cloud-init needs to be periodically
updated in order to enable new features. Therefore, the following types
of changes are allowed as long as the processes outlined below are
followed:

-  Bug fixes
-  New features

In the event of a change breaking backwards compatibility, then SRU team
approval will need to be obtained by emailing the ubuntu-release team
mailing list.

.. _exceptions_under_review:

Exceptions [under review]
-------------------------

cloud-init performs upstream releases quarterly and SRUs to all active
stable releases which have yet to reach End of Standard Support. Because
of the quarterly release schedule, two of those planned release dates
coincide with early Feature Freeze periods.

Since these feature changes may land in stable releases at any time due
to our SRU exception policy, adhering to feature freeze during the
development cycle would be counterproductive as those changes would be
forced to land after release instead. Therefore, feature freeze will not
apply when the changes are in scope of this document. However, from beta
freeze on uploads of this package will be subject to the same additional
scrutiny by the Release Team as any other package.


cloud-init Requesting the SRU
-----------------------------

The SRU should be done with a single process bug, instead of individual
bug reports for individual bug fixes. The one bug should have the
following:

-  The SRU should be requested per the StableReleaseUpdates
   documented process
-  The template at the end of this document should be used

   - all ``TODO-PRIOR-TO-PROPOSED`` should be filled in prior to requesting
     SRU unaccepted uploads are accepted into the **-proposed** pockets.
     All ``TODO-SRU-VERIFICATION`` should be filled in when testing against
     binaries once available in the **-proposed** pocket to ensure we are
     validating specific debs that will be accepted into **-updates** pockets.

-  The change log will contain a reference to the single SRU process
   bug, not all bugs fixed by the SRU. However, if there are very
   important bugs that are deemed worthy of reference they too should
   be included in the change log.
-  Major changes should be called out in the SRU template, especially
   where changed behavior is not backward compatible.
-  For each release (e.g. Ubuntu 14.04, Ubuntu 16.04, etc.) that is
   proposed to be updated by the SRU a link to the results of
   integration testing for at least the following datasources must be
   provided:

   -  nocloud (e.g. kvm)
   -  lxd
   -  ec2 (e.g. aws)
   -  azure
   -  gce

-  Any architecture specific fixes need to be noted and architecture
   specific test results included
-  Any packaging changes (e.g. a dependency change) need to be stated
-  If any manual testing occurs it should also be documented. See
   `LP: #1588052 <http://launchpad.net/bugs/1588052>`__ as an
   example.


cloud-init QA Process
---------------------

Merges
------

Updates to cloud-init trunk go through the following process:

-  Reviewed and approved by a member of the development team
-  Daily integration tests on trunk
-  Successful run of unit tests and style tests based on the branch
-  Branch set to the committed state

Packaging
---------

The following describes the requirements for each package generated for
the SRU.

For each package generated a successful completion of cloud-init
integration tests, as described below, using the proposed package with
no unexplained errors or failures


cloud-init Integration Tests
----------------------------

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

-  nocloud (e.g. kvm)
-  lxd
-  ec2 (e.g. aws)
-  azure
-  gce

The test case should be developed as a part of each resolved bug or new
feature. This way testing is straightforward and clear as to what is
expected to work.

.. _curtin_testing:

Curtin Testing
--------------

The curtin vmtest should also be sucessfully ran using cloud-init from
proposed and results attached.

.. _solutions_testing:

Solutions Testing
-----------------

Due to the dependency on cloud-init with various other products, the
solutions testing team will run their continuous integration test
against the cloud-init that is in -proposed. A successful run for each
field-supported LTS release will be required before the proposed
cloud-init can be let into -updates.

The cloud-init team will be in charge of attaching the artifacts and
console output of the appropriate run to the bug. cloud-init team
members will not mark ‘verification-done’ until this has happened.


cloud-init SRU Template
-----------------------

::

   == Begin SRU Template ==
   [Impact]
   This release sports both bug-fixes and new features and we would like to
   make sure all of our supported customers have access to these
   improvements. The notable ones are:

   *** <TODO-PRIOR-TO-PROPOSED>: Create list with LP: # included>

   See the changelog entry below for a full list of changes and bugs.

   [Test Case]
   The following development and SRU process was followed:
   https://documentation.ubuntu.com/sru/en/latest/reference/exception-Cloudinit-Updates

   The cloud-init team will be in charge of attaching the artifacts and
   console output of the appropriate run to the bug.  cloud-init team
   members will not mark ‘verification-done’ until this has happened.

   * Automated Test Results
   <TODO-SRU-VERIFICATION: attach automated cloud-init-proposed test artifacts from tests for each release with lxd artifacts>
   <TODO-SRU-VERIFICATION: attach automated cloud-init-proposed test artifacts from tests for each release with kvm artifacts>
   <TODO-SRU-VERIFICATION: attach automated curtin vmtest with cloud-init proposed>
   <TODO-SRU-VERIFICATION: attach Solutions Testing team test results for each LTS>

   * Manual Test Results
   <TODO-SRU-VERIFICATION: attach manual cloud-init-proposed test artifacts from tests for each release on ec2 datasource>
   <TODO-SRU-VERIFICATION: attach manual cloud-init-proposed test artifacts from tests for each release on gce datasource>
   <TODO-SRU-VERIFICATION: attach manual cloud-init-proposed test artifacts from tests for each release on azure datasource>

   [Regression Potential]
   In order to mitigate the regression potential, the results of the
   aforementioned integration tests are attached to this bug.

   [Discussion]
   <TODO-PRIOR-TO-PROPOSED: other background if applicable>

   == End SRU Template ==

   <TODO-PRIOR-TO-PROPOSED: Paste in change log entry>

.. _past_srus:

Past SRUs
---------

Links to past SRUs using this process are below:

+--------------------+-------------------------------------------------------------------+
| **SRU Version**    + **SRU bug**                                                       |
+====================+===================================================================+
| 17.2-35-gf576b2a2  + https://bugs.launchpad.net/ubuntu/+source/cloud-init/+bug/1747059 |
+--------------------+-------------------------------------------------------------------+
| 18.2-4-g05926e48   + https://bugs.launchpad.net/ubuntu/+source/cloud-init/+bug/1759406 |
+--------------------+-------------------------------------------------------------------+
| 18.5-15-g7a469659  + https://bugs.launchpad.net/ubuntu/+source/cloud-init/+bug/1813346 |
+--------------------+-------------------------------------------------------------------+


Related group of SRU interest
-----------------------------

Cloud-init has a :ref:`group of SRU interest <reference-sru-group-of-interest>`,
please subscribe the
`Interest group <https://launchpad.net/~sru-verification-interest-group-cloud-init>`__
to the SRU bug early on.

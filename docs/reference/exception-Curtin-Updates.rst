.. _reference-exception-CurtinUpdates:

Curtin Updates
==============

This document describes the policy for updating Curtin in a stable,
supported release. Curtin (the curt installer) is a "fast path"
installer designed to install Ubuntu quickly. It is blunt, brief,
snappish, snippety and unceremonious. In order to closely align with the
MAAS product, curtin needs to be periodically updated in order to enable
new features. Therefore, the following types of changes are allowed as
long as the conditions outlined below are met:

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

-  The SRU should be requested per the :ref:`StableReleaseUpdates <howto-perform-standard-sru>`
   documented process
-  The template at the end of this document should be used and all
   ‘TODO’ filled out
-  References to each bug fixed by the SRU should be included in the
   changelog and major changes called out in the SRU template,
   especially where changed behavior is not backwards compatible.
-  For each release (e.g. trusty, xenial, etc.) that is proposed to
   be updated by the SRU a link to the results of integration
   testing, via Curtin’s vmtest, successfully completed using the
   proposed package with no unexplained errors or failures
-  Any architecture specific fixes need to be noted and architecture
   specific test results included
-  Any packaging changes (e.g. a dependency changes) need to be
   stated
-  If any manual testing occurs it should also be documented. See LP#
   1588052 as an example.

.. _qa_process:

Curtin QA Process
-----------------

Merges
~~~~~~

Updates to curtin trunk go through the following process:

-  Reviewed and approved by a member of the development team
-  Daily integration tests on trunk
-  Successful run of unit tests and style tests based on the bzr
   branch
-  Branch set to the committed state

Packaging
~~~~~~~~~

The following describes the requirements for each package generated for
the SRU.

For each package generated a successful completion of Curtin’s
integration tests, as described below, using the proposed package with
no unexplained errors or failures

.. _integration_tests:

Integration Tests
~~~~~~~~~~~~~~~~~

Curtin includes an in-tree integration suite to validating various forms
of custom storage and network configurations. The tests themselves
involve over a hundred installs with a variety of configurations to
touch as many features and functionalities as possible including tests
to cover previous opened bugs. Test installs are done for all of the
supported releases, including Ubuntu LTS releases as well as currently
supported interim releases.

.. _maas_integration_tests:

MAAS Integration Tests
~~~~~~~~~~~~~~~~~~~~~~

In order to avoid regression to existing MAAS product, the MAAS team
will run their continuous integration test against the Curtin that is in
-proposed. A successful run will be required before the proposed Curtin
can be let into -updates.

For each specific release, MAAS c-i will have a job that tests
installation of MAAS and Curtin from -proposed of that release. As
example, there will be a job named 'maas-xenial-proposed' that will be
run with MAAS and Curtin installed from Xenial with the proposed pocket
enabled.

MAAS team c-i is publicly available at http://162.213.35.104:8080/ and
the SRU document will be kept up to date with that link should it
change.

The Curtin team will be in charge of attaching the artifacts and console
output of the appropriate run to the bug. Curtin team members will not
mark ‘verification-done’ until this has happened.

.. _sru_template:

SRU Template
------------

::

   == Begin SRU Template ==
   [Impact]
   This release sports both bug-fixes and new features and we would like to
   make sure all of our supported customers have access to these improvements.
   The notable ones are:

   *** <TODO: Create list with LP: # included>

   See the changelog entry below for a full list of changes and bugs.

   [Test Case]
   The following development and SRU process was followed:
   https://wiki.ubuntu.com/CurtinUpdates

   Curtin now contains an extensive integration test suite that is ran using
   the SRU package for each releases. These suite has documentation here:
   https://curtin.readthedocs.io/en/latest/topics/integration-testing.html

   In order to avoid regression to existing MAAS product, the MAAS team will
   run their continuous integration test against the curtin that is in
   -proposed.  A successful run will be required before the proposed curtin
   can be let into -updates.

   The curtin team will be in charge of attaching the artifacts and console
   output of the appropriate run to the bug.  Curtin team members will not
   mark ‘verification-done’ until this has happened.

   [Regression Potential]
   In order to mitigate the regression potential, the results of the
   aforementioned integration tests are attached to this bug.

   <TODO: attach curtin-proposed test artifacts from vmtest for every SRU release, not a link as links expire>
   <TODO: attach maas-proposed test artifacts from vmtest for every SRU release, not a link as links expire>

   [Discussion]
   <TODO: other background>

   == End SRU Template ==

   <TODO: Paste in change log entry>

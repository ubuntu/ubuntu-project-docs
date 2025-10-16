.. _reference-exception-autopkgtest-Updates:

autopkgtest Updates
===================

This document describes the policy for updating autopkgtest in a stable,
supported release.

Rationale
---------

The autopkgtest package is primarily of interest to Ubuntu developers,
providing tools running autopkgtests locally. Developers should have
consistent behavior from these tools, regardless of which Ubuntu release
they are using. Moreover the Ubuntu QA team aims at keeping the package
in the Ubuntu archive in sync with the autopkgtest version which is used
on the autopkgtest infrastructure (https://autopkgtest.ubuntu.com/), so
the testing environment will always be the same and therefore produce
consistent results.

.. _allowed_updates:

Allowed updates
---------------

The following types of changes are allowed as long as the conditions
outlined below are met:

-  Bug fixes
-  New features

In the event of a change breaking backwards compatibility, then SRU team
approval will need to be obtained.


autopkgtest Requesting the SRU
------------------------------

The SRU should be done with a single process bug, instead of individual
bug reports for individual bug fixes. Individual bug fixes may also be
tracked/closed by the upload; however only the one process bug must have
the following:

-  The SRU should be requested following the the
   :ref:`StableReleaseUpdates <howto-perform-standard-sru>`
   documented process.
-  The template at the end of this document should be used and all
   ‘TODO’ filled out.
-  References to each bug fixed by the SRU should be included in the
   changelog and major changes called out in the SRU template,
   especially where changed behavior is not backwards compatible.
-  For each release that is proposed to be updated by the SRU a link
   to the results of integration testing, via autopkgtest,
   successfully completed using the proposed package with no
   unexplained errors or failures. This testing will be done by
   uploading packages to a PPA and then triggering autopkgtests on
   those.
-  Any architecture specific changes need to be noted.
-  Any packaging changes (e.g. a dependency changes) need to be
   stated.
-  If any manual testing occurs it should also be documented.

If backwards compatibility is to be broken, this should be clearly
written at the top of the bug description for the SRU, as well as in the
title with "[breaks-compat]". Furthermore, an email to ubuntu-release
will be sent to point the release / SRU teams to the bug in order to get
approval before uploading to the release's upload queue.


autopkgtest QA Process
----------------------

.. _build_time_tests:

autopkgtest Build time tests
----------------------------

The project has tests which run at package build time. The package build
will fail if any if the tests fail.


autopkgtest Integration Tests
-----------------------------

The package has a test suite that is run as an autopkgtest which should
be good enough to ensure the package works as expected.


autopkgtest SRU Template
------------------------

::

   This SRU follows the exception process as outlined at https://documentation.ubuntu.com/sru/en/latest/reference/exception-autopkgtest-Updates rather than the standard SRU rules.

   [Impact]

   This release contains both bug fixes and new features and we would like
   to make sure all of our developers have access to these improvements.
   The notable ones are:

   ** <TODO: create list with LP: # references>

   See the changelog entry below for a full list of changes and bugs.

   [Test Plan]

   autopkgtest contains a test suite that is run using the SRU
   package for each release. This test suite's results are
   available here:

   <TODO: link to autopkgtest results done on PPA package>

   <TODO: Run a manual upgrade test (this will cover LP: #2115731)>

   Checkout these repositories:

   upgrade testing code: git clone https://github.com/canonical/auto-upgrade-testing
   upgrade testing profiles: git clone https://git.launchpad.net/auto-upgrade-testing-specifications

   And run the test from within the auto-upgrade-testing checkout:
       python3 -m upgrade_testing.command_line -c ../auto-upgrade-testing-specifications/profiles/ubuntu-noble-oracular-basic-amd64_qemu.yaml --provision --adt-args='--timeout-factor=10 -d' --results-dir /tmp/upgrade_tests

   The upgrade should perform and finish successfully:
     * exit status is 0
     * you should see near the end of the output: Upgrade result: PASS


   <TODO: if relevant: extra manual testing results>

   [Where problems could occur]

   <TODO: highlights areas where regressions might happen>

   [Other Info]

   <TODO: other background (optional)>

   [Changelog]

   <TODO: paste in changelog entry>


Record of regressions
---------------------

`LP:
#2115731 <https://bugs.launchpad.net/ubuntu/+source/autopkgtest/+bug/2115731>`__:
regression affecting upgrade testing.

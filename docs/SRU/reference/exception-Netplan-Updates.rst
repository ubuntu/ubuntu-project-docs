.. _reference-exception-NetplanUpdates:

Netplan Updates
===============

This document describes the policy for updating netplan.io in a stable,
supported release.

Netplan is an abstraction layer for network configuration used on all
releases of Ubuntu since Ubuntu 18.10; and generates systemd-networkd or
`NetworkManager <https://wiki.ubuntu.com/NetworkManager>`__
configuration based on initial netplan configuration
(written in YAML) present at boot time.

In order to closely align with new networking requirements being
backported to supported releases as well as the MAAS product, netplan.io
needs to be periodically updated in order to enable new features.
Therefore, the following types of changes are allowed as long as the
conditions outlined below are met:

-  Bug fixes
-  New features

In the event of a change breaking backwards compatibility, then SRU team
approval will need to be obtained. See below.


Netplan Requesting the SRU
--------------------------

The SRU should be done with a single process bug, instead of individual
bug reports for individual bug fixes. Individual bug fixes may also be
tracked/closed by the upload; however only the one process bug must have
the following:

-  The SRU should be requested per the StableReleaseUpdates
   documented process
-  The template at the end of this document should be used and all
   ‘TODO’ filled out
-  References to each bug fixed by the SRU should be included in the
   changelog and major changes called out in the SRU template,
   especially where changed behavior is not backwards compatible.
-  For each release (e.g. trusty, xenial, etc.) that is proposed to
   be updated by the SRU a link to the results of integration
   testing, via autopkgtest, successfully completed using the
   proposed package with no unexplained errors or failures
-  Any architecture specific fixes need to be noted and architecture
   specific test results included
-  Any packaging changes (e.g. a dependency changes) need to be
   stated
-  If any manual testing occurs it should also be documented. See `LP
   #1588052 <https://bugs.launchpad.net/ubuntu/+source/snapd/+bug/1588052>`__
   as an example.

If backwards compatibility is to be broken, this should be clearly
written at the top of the bug description for the SRU, as well as in the
title with "[breaks-compat]". Furthermore, an email to ubuntu-release
will be sent to point the release / SRU teams to the bug in order to get
approval before uploading to the release's upload queue.


Netplan QA Process
------------------

Merges
------

Updates to `netplan master
branch <http://github.com/canonical/netplan>`__ go through the following
process:

-  Reviewed and approved by a member of the development team
-  Run automatic daily integration tests on master branch (github
   integration)
-  Successful run of unit tests and style tests on a per-commit basis

Packaging
---------

The following describes the requirements for each package generated for
the SRU.

For each package generated a successful completion of netplan’s
integration tests, as described below, using the proposed package with
no unexplained errors or failures


Integration Tests
-----------------

Netplan includes an in-tree integration suite to validating various
network configurations. The tests themselves involve a large number of
different configuration scenarios designed to touch as many features and
functionalities as possible including tests to cover previous opened
bugs.

These tests are run as part of the migration from -proposed to -updates
for an SRU and require passing (or a clear explanation of the failure
and why it's considered ok); using the autopkgtest.ubuntu.com
infrastructure, which is separate from daily integration tests that may
be run on the netplan master branch.


Netplan SRU Template
--------------------

::

   [Impact]
   This release contains both bug-fixes and new features and we would like to
   make sure all of our supported customers have access to these improvements.
   The notable ones are:

   *** <TODO: Create list with LP: # included>

   See the changelog entry below for a full list of changes and bugs.

   [Test Plan]
   The following development and SRU process was followed:
   https://documentation.ubuntu.com/sru/en/latest/reference/exception-Netplan-Updates

   Netplan contains an extensive integration test suite that is ran using
   the SRU package for each releases. This test suite's results are available here:
   http://autopkgtest.ubuntu.com/packages/n/netplan.io

   A successful run is required before the proposed netplan package
   can be let into -updates.

   The netplan team will be in charge of attaching the artifacts and console
   output of the appropriate run to the bug.  Netplan team members will not
   mark ‘verification-done’ until this has happened.

   [Where problems could occur]
   In order to mitigate the regression potential, the results of the
   aforementioned integration tests are attached to this bug.

   <TODO: attach test artifacts for every SRU release, not a link as links expire>

   [Other Info]
   <TODO: other background>

   [Changelog]
   <TODO: Paste in change log entry>

.. _history_of_regressions:

History of regressions
----------------------

-  netplan.io 0.107.1-3ubuntu0.22.04.1 broke Juju in `LP:
   #2084444 <https://bugs.launchpad.net/netplan/+bug/2084444>`__

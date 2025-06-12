.. _reference-exception-landscapeupdates:

Landscape updates
=================

This document describes the policy for updating Landscape client
packages in a stable supported distro, including LTS. It is also the aim
of this document to provide an example for any upstream project that
wants to push updates to an Ubuntu stable release.

Landscape is a commercial service from Canonical which periodically
offers new features to its customers. Being a client-server product, the
client part needs to be periodically updated in order to take advantage
of the new features. Therefore, in addition to bug fixes, new features
are allowed in an update **as long as the conditions outlined below are
met**.

.. _qa_process:

Landscape QA Process
--------------------

This is the mandatory QA process that the proposed packages have to
pass. The following requirements must be met:

-  each change must have a Launchpad ticket filed under the
   landscape-client project
   (https://bugs.launchpad.net/landscape-client/+filebug). Packaging
   bugs should be filed against the landscape-client ubuntu package
   (https://bugs.launchpad.net/ubuntu/+source/landscape-client/+filebug)
-  each one of those tickets must have:

   -  a bzr branch attached with the fix + tests
   -  two Landscape developer reviews approving the change (already a
      standard Landscape coding practice)
   -  a specific QA review. The QA engineer must at least do a before
      and after kind of test, corroborating the fix.
   -  a "Committed" status, meaning the change is already in the code
      base

-  all the code changes must be covered by tests
-  all self tests must pass. Being a project that follows the TDD model
   (Test Driven Development, see
   http://en.wikipedia.org/wiki/Test_driven_development for details),
   any code change in Landscape (client or server) is covered by a test.
   The client part has, as of version 1.0.23, 1469 individual test cases
   that cover the entire code base.

The above tests exercise the code changes and must be performed by a
member of the Landscape team. The packaging changes need an extra QA
procedure outlined below.

.. _packaging_qa:

Packaging QA
~~~~~~~~~~~~

The objective of the separate packaging QA is to test:

-  package upgrades
-  package installation from scratch
-  distribution upgrade

The resulting package, with all the changes in place, must undergo and
pass the following additional QA procedures:

-  upgrade test from previous distribution to the current one. If the
   current distribution is an LTS one, the upgrade path from the
   previous LTS distro must also be exercised.
-  upgrade test from previous version of the package. This test must be
   performed with:

   -  apt-get install/upgrade
   -  using the Landscape service itself

-  installation from scratch in the current distribution:

   -  using apt-get

-  test interaction with update-motd to make sure the motd doesn't get
   trashed or otherwise impaired by landscape-common:

   -  reboot and make sure motd is displayed correctly and not trashed
   -  when update-motd is used by landscape-sysinfo (it's the default),
      make sure its call to landscape-sysinfo works and the output is
      included in the motd
   -  provoke an error (backtrace) in landscape-sysinfo plugin by
      running \`sudo chmod 0 /proc\`: the backtrace must not be included
      in the motd

The above tests can be performed by any QA engineer.

.. _requesting_the_sru:

Landscape Requesting the SRU
----------------------------

The SRU should be requested as usual
(:ref:`StableReleaseUpdates <howto-perform-standard-sru>`) with the additional
note about having the above steps being completed.

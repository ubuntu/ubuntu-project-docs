**DRAFT, please send comments to andreas at ubuntu.com**

This document describes the policy for updating Landscape client
packages in a stable supported distro, including LTS. It is also the aim
of this document to provide an example of the needed minimum
requirements for any upstream project that wants to push updates to an
Ubuntu stable release.

Landscape is a commercial service from Canonical which periodically
offers new features to its customers. Being a client-server product, the
client part needs to be periodically updated in order to take advantage
of the new features. Therefore, in addition to bug fixes, new features
are allowed in an update **as long as the conditions outlined below are
met**.

.. _qa_process:

QA Process
----------

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
   -  a specific QA review
   -  a "Committed" status, meaning the change is already in the code
      base

-  the code changes must be covered by tests
-  all self tests must pass. Being a project that follows the TDD (Test
   Driven Development) model, any code change in Landscape (client or
   server) is covered by a test. The client part has, as of version
   1.0.23, 1469 individual test cases that cover the entire code base.

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

The above tests can be performed by any QA engineer.

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be requested as usual
(`StableReleaseUpdates <StableReleaseUpdates>`__) with the additional
note about having the above steps being completed.

**DRAFT, DO NOT COMMENT ABOUT THIS YET - Andreas - Jan/2008**

This document describes the policy for updating Landscape client
packages in a stable supported distro, be it LTS or not.

Landscape is a commercial service from Canonical which periodically
offers new features to its customers. Being a client-server product, the
client part needs to be periodically updated in order to take advantage
of the new features. Therefore, new features are allowed in an update
**as long as the conditions outlined below are met**.

.. _qa_process:

QA Process
----------

This is the mandatory QA process that the proposed packages have to
pass. The following requirements must be met:

-  each change must have a Launchpad ticket filed under the
   landscape-client project
-  each one of those tickets must have:

   -  two developer reviews approving the change (already a standard
      Landscape coding practice)
   -  a specific QA review

-  all self tests must pass (already a standard Landscape coding
   practice)
-  after the upgrade, the client must still be able to talk to the
   Landscape server

The above tests exercise the code changes. The packaging changes need an
extra QA procedure outlined below.

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
   previous LTS distro must also be exercised. This upgrade test must be
   performed using do-release-upgrade
-  upgrade test from previous version of the package. This test must be
   performed with:

   -  dpkg
   -  apt-get install/upgrade
   -  smart install/upgrade
   -  using the Landscape service itself

-  installation from scratch in the current distribution:

   -  using dpkg
   -  using apt-get
   -  using smart

-  optionally, because of the added complexity and because the author of
   this document is not yet sure how to do it, the installer of the
   current distribution should also be tested using the new package to
   make sure it works in the installer environment

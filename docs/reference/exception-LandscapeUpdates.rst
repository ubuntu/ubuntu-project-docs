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
pass. We will split it into two sections: code QA and package QA.

.. _code_qa:

Code QA
~~~~~~~

The objective of the code QA is to make sure that the code changes fix
or implement what they intended and have no ill side effects.

The following requirements must be met:

-  each change needs to have a Launchpad ticket filed under the
   landscape-client project
-  each one of those tickets needs to have:

   -  two developer reviews (already a standard Landscape coding
      practice)
   -  a specific QA review
   -  self tests must all pass (already a standard Landscape coding
      practice)

.. _packaging_qa:

Packaging QA
~~~~~~~~~~~~

The objective of the separate packaging QA is to test:

-  package upgrades
-  package installation from scratch
-  distribution upgrade

The following requirements must be met:

-  each packaging change must have a Launchpad ticket filed under the
   landscape-client ubuntu package
-  each one of those tickets must have:

   -  two developer reviews (already a standard Landscape coding
      practice)
   -  a specific QA review

The resulting package, with all the changes in place, needs to undergo
the following additional QA procedures:

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

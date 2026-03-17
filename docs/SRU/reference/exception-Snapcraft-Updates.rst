.. _reference-exception-snapcraftupdates:

Snapcraft Updates
=================

This document describes the policy for updating the snapcraft package in
a stable supported distro, including LTS.

snapcraft is the tool to create snaps. This package needs to be kept in
sync with snapd releases so we can build snaps that will work with the
latest features added to Ubuntu Core.
`snapd <https://documentation.ubuntu.com/sru/en/latest/reference/exception-ec2-hibinit-agent-Updates>`__ already has an
exception to release new versions into the stable distro; therefore in
addition to critical bug fixes, new features and small improvements are
allowed in an snapcraft update **as long as the conditions outlined
below are met**.


Snapcraft QA Process
--------------------

This is the mandatory QA process that the proposed packages have to
pass. The following requirements must be met:

.. _before_a_pull_request_lands_into_master:

Before a pull request lands into master
---------------------------------------

-  each change must be reviewed and approved by at least one member
   of the `snapcore github
   team <https://github.com/orgs/snapcore/people>`__ before landing
   into the master branch.
-  each change must be fully tested at the unit level.
-  each change affecting the user interface (cli or others) or file
   format must have an automated integration test.
-  each new feature must have an example that can be built, installed
   and executed as a snap.
-  all the unit, integration and examples tests must pass in one
   architecture.
-  all the bugs reported in Launchpad that will be fixed in this
   release must have a link to the pull request that fixes them.
   These bugs must be marked as "Fix Committed" at the project level
   once that pull request is merged into master.

.. _before_the_package_is_in_proposed:

Before the package is in proposed
---------------------------------

-  all the unit, integration and examples tests must pass in all the
   supported architectures. They are executed for all the
   architectures during the build of the deb package that will go
   into proposed in the case of the unit tests, and during the
   autopkgtest execution in the case of integration and examples
   tests.

.. _when_the_package_is_in_proposed:

When the package is in proposed
-------------------------------

-  upgrade test from previous version of the package. This test must
   be performed with:
   - ``apt install/upgrade``
-  each bug fix that affects the user interface must have one QA
   review. The QA engineer will verify that the bug is fixed in a
   system with the proposed package installed by executing an
   automated or manual test.
-  the QA team will perform extensive exploratory testing on the
   areas that will be changed by the release.
-  test interaction with the snapd installed in the system:

   - build a snap with the new snapcraft package and install it with the existing snapd package.

The tests for the package in proposed will be documented in the SRU bug
and can be performed by any QA engineer.

This is a package new in Ubuntu 16.04 LTS. Once we have another stable
Ubuntu version released this should be added to the above process:

-  upgrade test from previous distribution to the current one. If the
   current distribution is an LTS one, the upgrade path from the
   previous LTS distro must also be exercised.


Snapcraft Requesting the SRU
----------------------------

The SRU should be requested as usual
(:ref:`StableReleaseUpdates <howto-perform-standard-sru>`) with the additional
note about having the above steps being completed.

.. _snapcraft_releasing_the_sru:

Releasing the SRU
-----------------

The SRU may be released without meeting the aging period of 7 days
provided all the above steps have been completed.

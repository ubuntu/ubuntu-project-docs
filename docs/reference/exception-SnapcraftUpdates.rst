This document describes the policy for updating the snapcraft package in
a stable supported distro, including LTS.

snapcraft is the tool to create snaps. This package needs to be kept in
sync with snapd releases so we can build snaps that will work with the
latest features added to Ubuntu Core.
`snapd <https://wiki.ubuntu.com/SnapdUpdates>`__ already has an
exception to release new versions into the stable distro; therefore in
addition to critical bug fixes, new features and small improvements are
allowed in an snapcraft update **as long as the conditions outlined
below are met**.

.. _qa_process:

QA Process
----------

This is the mandatory QA process that the proposed packages have to
pass. The following requirements must be met:

-  

   -  each change must be reviewed and approved by at least one
      ubuntu-core developer before landing into the master branch.
   -  each change must be fully tested at the unit level.
   -  each change affecting the user interface (cli or others) or file
      format must have an automated integration test.
   -  each new feature must have an example that can be built, installed
      and executed as a snap.
   -  all the unit, integration and examples tests must pass in all the
      supported architectures. They are executed for one arch before the
      change is merged into master, and for all the architectures during
      the build of the deb package that will go into proposed in the
      case of the unit tests, and during the autopkgtest execution in
      the case of integration and examples tests.
   -  each bug fix that affects the user interface must have one QA
      review. The QA engineer will verify that the bug is fixed in a
      system with the proposed package installed by executing an
      automated or manual test.
   -  all the bugs reported in launchpad that will be fixed in this
      release must have a link to the pull request that fixes them.
      These bugs must be marked as "Fix Committed" at the project level
      once that pull request is merged into master.
   -  when a new version is ready to be proposed, the QA team will
      perform extensive exploratory testing on the areas that will be
      changed by the release.

.. _packaging_qa:

Packaging QA
~~~~~~~~~~~~

The resulting package, with all the changes in place, must undergo and
pass the following additional QA procedures:

-  

   -  upgrade test from previous version of the package. This test must
      be performed with:

``   * apt install/upgrade.``

-  

   -  test interaction with the snapd installed in the system:

``   * build a snap with the new snapcraft package and install it with the existing snapd package.``

The above tests can be performed by any QA engineer.

This is a package new in Ubuntu 16.04 LTS. Once we have another stable
Ubuntu version released this should be added to the above process:

-  

   -  upgrade test from previous distribution to the current one. If the
      current distribution is an LTS one, the upgrade path from the
      previous LTS distro must also be exercised.

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be requested as usual
(`StableReleaseUpdates <StableReleaseUpdates>`__) with the additional
note about having the above steps being completed.

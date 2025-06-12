.. _reference-exception-snapdupdates:

Snapd Updates
=============

This document describes the policy for updating the snapd package in a
stable supported distro, including LTS.

snapd is the tool to interact with Ubuntu Core Snappy. This package is
also used in the generation of the OS snap package and snappy Ubuntu
Core images. One of the goals of this project is to keep your system
always up-to-date with the latest security fixes and with the newest
developed features. It was designed in a way that makes it easily
extensible, so every new release provides bug fixes and new features
with a low risk of regressions. The team is working with a continuous
delivery process which results in a new version ready to be released
every week. The snapd package that was delivered at the time of the
Ubuntu 16.04 release is also not feature-complete, and the nature of
this project makes it important to be able to continue to deliver new
features on top of a stable Ubuntu release. Therefore, in addition to
critical bug fixes, new features and small improvements are allowed in
an update **as long as the conditions outlined below are met**.


Snapd QA Process
----------------

This is the mandatory QA process that the proposed packages have to
pass. The following requirements must be met:

*  each change must be reviewed and approved by at least two members
   of the `ubuntu-core github
   team <https://github.com/orgs/ubuntu-core/people>`__ before
   landing into the master branch.

*  each change must be fully tested at the unit level.

   * all the unit tests must pass in all the supported architectures.
   They are executed for one arch before the change is merged into
   master, and for all the architectures during the build of the deb
   package that will go into proposed.

*  each bug fix that affects the user interface must have one QA
   review. The QA engineer will verify that the bug is fixed in a
   system with the proposed package installed by executing an
   automated or manual test.

*  all the bugs reported in launchpad that will be fixed in this
   release must have a link to the pull request that fixes them.
   These bugs must be marked as "Committed" once that pull request is
   merged into master.

*  all the new user-facing features will be tested in a real system.

   *  most of these tests are automated and executed as part of the autopkgtest suite of the deb and its reverse-dependencies in a classic ubuntu system, and as part of the automated user-acceptance suite in a snappy Ubuntu Core system.

   *  the tests that can't be automated are documented and manually executed when there are changes in the code that can affect the feature.

*  when a new version is ready to be proposed, the QA team will
   perform extensive exploratory testing on the areas that will be
   changed by the release.


Snapd Packaging QA
------------------

The resulting package, with all the changes in place, must undergo and
pass the following additional QA procedures:

*  upgrade test from previous version of the package. This test must
   be performed with:

   *  ``apt install/upgrade``

*  test interaction with classic apt install and update of debs to
   make sure that snapd doesn't interfere with the classic system:

   *  reboot.

   *  install and update a deb with apt.

*  test interaction with gnome software center:

   *  install and update a snap.

   *  install and update a deb.

The above tests can be performed by any QA engineer.

This is a package new in Ubuntu 16.04 LTS. Once we have another stable
Ubuntu version released this should be added to the above process:

*  upgrade test from previous distribution to the current one. If the
   current distribution is an LTS one, the upgrade path from the
   previous LTS distro must also be exercised.


Snapd Requesting the SRU
------------------------

The SRU should be requested as usual
(:ref:`StableReleaseUpdates <howto-perform-standard-sru>`) with the description
of the bug containing links to automatic testing results (travis unit
test, jenkins autopkg tests, and jenkins integrations tests) so that any
one can verify the testing occurred and its results. Additionally, the
SRU bug should be verbose in documenting any manual testing that occurs
an example of a good SRU bug can be found in
http://launchpad.net/bugs/1588052. The SRU should be done with a single
process bug for this stable release exception, instead of individual bug
reports for individual bug fixes. However, individual bugs may be
referenced in the from the changelog but **each** of those bugs will
need to independently verified and commented on for the SRU to be
considered complete.

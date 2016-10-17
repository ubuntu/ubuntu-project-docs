#. 

   #. page was copied from SnapdUpdates

This document describes the policy for updating the ubuntu-image package
in a stable release.

ubuntu-image is a tool for building bootable images for a variety of
devices and Ubuntu flavors. Initially, it is primarily used to build
bootable snappy images, but will eventually expand its use cases to
include Ubuntu classic. ubuntu-image is closely tied to snapd, since it
depends on snapd for interaction with the snappy store, and for
validating models and gadgets. Thus, the `snapd updates
policy <SnapdUpdates>`__ has relevance. As new snapd releases are made,
new ubuntu-image releases may also be necessary. Even without snapd
releases, new ubuntu-image releases may be necessary in order to
facilitate image building on the Ubuntu infrastructure, including
potentially LTS releases (although ubuntu-image only became available in
the archive as of 16.10). Since at the time of 16.10 release, it is
known that ubuntu-image is not feature complete, and its focus is
narrowly defined to be for image building, new featureful releases will
be made on both the in-development version of Ubuntu, stable releases,
and the snap store. It is a project goal to keep all release channels in
sync.

The QA process for stable ubuntu-image releases are outlined below, in
support of an exception to the standard SRU process.

.. _qa_process:

QA Process
----------

Every change to ubuntu-image is proposed through the `GitHub merge
proposal <https://github.com/CanonicalLtd/ubuntu-image>`__ process. It
is generally reviewed by at least one other member of the ubuntu-image
team, although because of the team's size this cannot always be
guaranteed. Continuous integration is performed on **all** pull
requests, using DEP-8 style `autopackage
tests <http://autopkgtest.ubuntu.com/packages/ubuntu-image>`__ on all
supported Ubuntu releases. Branches are never merged if any test fails.
This includes 100% unit test coverage.

We do not currently test actual image building and booting in the CI
infrastructure, but this is a `planned
task <https://bugs.launchpad.net/ubuntu-image/+bug/1625732>`__.

All bugs fixed or features added are `tracked in
Launchpad <https://bugs.launchpad.net/ubuntu-image>`__ and clearly
described in the

::

   debian/changelog

.

.. _packaging_qa:

Packaging QA
~~~~~~~~~~~~

Candidate packages are tested in all release channels through an
install/upgrade process, by installing the existing archive version, and
upgrading to the latest built package.

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be requested as usual
(`StableReleaseUpdates <StableReleaseUpdates>`__) with the description
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

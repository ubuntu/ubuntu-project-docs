.. _reference-exception-ubuntuimageupdates:

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
potentially on LTS releases (although ubuntu-image only became available
in the archive as of 16.10). Since at the time of 16.10 release, it is
known that ubuntu-image is not feature complete, and its focus is
narrowly defined to be for image building, new featureful releases will
be made on the in-development version of Ubuntu, in stable releases, and
in the snap store. It is a project goal to keep all release channels in
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

With `LP:
#1635337 <https://bugs.launchpad.net/ubuntu-image/+bug/1635337>`__
(ubuntu-image 0.9), we build all of the `official
models <http://people.canonical.com/~vorlon/official-models/>`__ on
every merge proposal, and verify that all mountable partitions can
actually be mounted, including the unspecified *writable* partition at
the end of the disk image, but not including any MBR "non-partitions" at
the front. With ubuntu-image 1.0, we also have autopkgtests that use
ubuntu-image to build and boot an amd64 image. If the image doesn't
boot, verified by connecting to an echo server in the running image,
then the new version fails QA. While the boot test only tests amd64, it
does test this in all release channels.

Boot test:

::

   $ ubuntu-image model/pc-amd64-model.assertion -o /tmp/yakkety.img
   $ qemu-system-x86_64 -m 2G /tmp/yakkety.img

(Season to taste for Xenial image building test. Also, you may have to
twiddle with permissions if you testing this in a chroot.)

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
install/upgrade process, by installing the existing archive version and
upgrading to the latest built package.

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be requested as usual
(`StableReleaseUpdates <StableReleaseUpdates>`__) with the description
of the bug containing links to automatic testing results (github
autopkgtest results) so that any one can verify the testing occurred and
its results. Additionally, the SRU bug should be verbose in documenting
any manual testing that occurs. (An example of a good SRU bug can be
found in Bug:1588052.) The SRU should be done with a single process bug
for this stable release exception, instead of individual bug reports for
individual bug fixes. Individual bugs may be referenced in the
changelog, but in that case **each** of those bugs will need to be
independently verified and commented on for the SRU to be considered
complete.

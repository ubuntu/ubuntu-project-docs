This document describes the policy for updating the fwupd, fwupdate,
fwupd-signed and fwupdate-signed packages to new upstream versions in a
stable, supported distro (including LTS releases).

fwupd is the firmware updating daemon used for performing updates on a
variety of devices both in and out of OS. Updates outside of the OS are
performed using UEFI capsules. fwupd versions older than 1.1.x used
fwupdate package and its EFI binary for performing UEFI capsule updates.
fwupd versions 1.1.x and newer have subsumed fwupdate and now maintains
and fully manage the lifecycle of the EFI binary.

Signed versions of the EFI binaries are in the respsective \*-signed
packages.

The entire firmware update stack is maintained by Richard Hughes and
Mario Limonciello.

Due to the nature of the coverage of various UEFI implementations across
OEMs it's often difficult or impossible to foreshadow the impacts of a
given fix on other OEMs implementations. OEMs that run into a problem on
a particular version of fwupd/fwupdate can place information into the
metadata to prevent updates from running on versions of fwupd/fwupdate
that have known bugs.

Upstream does maintain stable release branches for distros like Ubuntu
to pick up when applicable without going to the latest version of fwupd
but still adopting fixes.

Metadata
--------

Due to this, upstream highly recommends distros to not backport
individual patches so that OEMs can control only running fwupd/fwupdate
updates on safe combinations.

OEMs can add the following to their metadata:

``   ``\ \ ``com.redhat.fwupdate``\ 

.. _what_can_be_srued:

What can be SRUed
-----------------

New versions of fwupd and fwupdate can both be SRU'ed into older
releases provided following process is followed: On an Ubuntu release
that uses both fwupdate and fwupd (such as bionic and earlier):

**fwupdate**: tarball releases only. No backported individual patches.
If a tarball release isn't available, make upstream release one.

**fwupd**: fwupd releases in the 1.0.x series.

On an Ubuntu release that uses fwupd but not fwupdate:

Stay with the same stable release branch that was launched with that
release. For example 1_1_X branch or 1_2_X branch.

.. _qa_process:

QA Process
----------

When a new version of fwupd or fwupdate is uploaded to -proposed, the
following will be done:

-  Test that UEFI capsule updates still work properly on an OEM system
   pulling from LVFS with secure boot enabled.
-  Verify that CI tests have been running for the matching release
   upstream.
-  Test that a system that offers a variety of in OS devices enumerate
   (example Thunderbolt, NVME)
-  The appropriate signed packages have been uploaded as well

If all the testing indicates that the image containing the new package
is acceptable, verification will be considered to be done and the the
package can be released from -proposed without waiting for its age reach
the default SRU aging requirement.

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be done with a single process bug for this stable release
exception, instead of individual bug reports for individual bug fixes.
However, individual bugs may be referenced in the from the changelog but
each of those bugs will need to independently verified and commented on
for the SRU to be considered complete.

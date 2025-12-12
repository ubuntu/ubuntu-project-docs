.. _reference-exception-firmware-updates:

Firmware Updates
================

This document describes the policy for updating the fwupd and fwupd-efi
packages to new upstream versions in a stable, supported distro
(including LTS releases).  The policy applies to Ubuntu 20.04 and newer.

fwupd is the firmware updating daemon used for performing updates on a
variety of devices both in and out of OS. Updates outside of the OS are
performed using UEFI capsules. The EFI binary used for performing UEFI
capsule updatees is distributed in the fwupd-efi package.
Signed versions of the EFI binaries are in the respsective \*-signed
packages.

The entire firmware update stack is maintained by Richard Hughes and
Mario Limonciello.

Due to the nature of the coverage of various UEFI implementations across
OEMs it's often difficult or impossible to foreshadow the impacts of a
given fix on other OEMs implementations. OEMs that run into a problem on
a particular version of fwupd can place information into the metadata to
prevent updates from running on versions of fwupd that have known bugs.

Upstream does maintain stable release branches for distros like Ubuntu
to pick up when applicable without going to the latest version of fwupd
but still adopting fixes.

Metadata
--------

Upstream highly recommends distros to not backport individual patches so
that OEMs can control only running fwupd updates on safe combinations.

OEMs can add the following to their metadata:

::

    <requires>
        <id compare="ge" version="12">org.freedesktop.fwupd</id>
    </requires>


.. _what_can_be_srued:

What can be SRUed
-----------------

New versions of fwupd and fwupd-efi can both be SRU'ed into older
releases provided following process is followed:

**fwupd-efi**: tarball releases only. No backported individual patches.
If a tarball release isn't available, ping upstream to test and release one.

**fwupd**: fwupd releases in the matching major series (for example 1.9.x
or 2.0.x) that was already introduced into Ubuntu. This policy addresses microreleases only.

Firmware QA Process
-------------------

When a new version of fwupd or fwupd-efi is uploaded to -proposed, the
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
package can be released from -proposed after the standard aging period.


Firmware Requesting the SRU
---------------------------

The SRU should be done with a single process bug for this stable release
exception, instead of individual bug reports for individual bug fixes.
However, individual bugs may be referenced in the from the changelog but
each of those bugs will need to independently verified and commented on
for the SRU to be considered complete.

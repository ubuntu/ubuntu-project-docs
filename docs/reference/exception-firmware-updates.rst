This document describes the policy for updating the fwupd, fwupdate,
fwupd-signed and fwupdate-signed packages to new upstream versions in a
stable, supported distro (including LTS releases).

fwupd is the firmware updating daemon used for performing updates on a
variety of devices. Updates outside of the OS are performed using UEFI
capsules.

fwupd versions older than 1.1.x used the fwupdate package and its EFI
binary for performing UEFI capsule updates. fwupd versions 1.1.x and
newer have subsumed fwupdate and now maintains and fully manages the
lifecycle of the EFI binary.

Signed versions of the EFI binaries are in the respective \*-signed
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

``   ``\ \ ``org.freedesktop.fwupd``\ 

.. _what_can_be_srued:

What can be SRUed
-----------------

New versions of fwupd and fwupdate can both be SRU'ed into older
releases provided following process is followed:

On an Ubuntu release that uses fwupd but not fwupdate (after bionic):

**fwupd within the same stable release**: For example 1_3_X to 1_3_Y
branch.

**fwupd across stable version**: For example, SRU from 1_3_X to 1_4_Y
branch.

On an Ubuntu release that uses both fwupdate and fwupd (such as xenial
and earlier):

**fwupdate**: tarball releases only. No backported individual patches.
If a tarball release isn't available, make upstream release one.

**fwupd**: fwupd releases in the 1.0.x series.

.. _full_qa_process_across_stable_releases:

Full QA Process across stable releases
--------------------------------------

When a new version of fwupd (or fwupdate) is uploaded to -proposed, the
following verification needs to be done:

-  Test that UEFI capsule updates still work properly on an OEM system
   pulling from LVFS with secure boot enabled.
-  Test firmware upgrade or re-install that a system that offers a
   variety of in OS devices enumerate (example Thunderbolt, NVME)
-  The appropriate signed packages have been uploaded, and
   incompatibility should be properly prevented by Breaks if needed.
-  Make sure the updated fwupdmgr command line utility is backward
   compatible:

   -  

      -  fwupdmgr update / install / reinstall sub-command needs to be
         checked.
      -  Run the old and new version of fwupdmgr.sh in fwupd-tests deb
         on the new version of fwupd and review the failure test cases,
         if any.

-  Make sure the dbus interface is compatible:

   -  

      -  New methods or enum values are fine.
      -  Renaming, removing and changing is not ok.
      -  Command to dump dbus interface ex: “dbus-send --system
         --type=method_call --print-reply --dest=org.freedesktop.fwupd /
         org.freedesktop.DBus.Introspectable.Introspect”

-  Test updating firmware from the Ubuntu Software user interface, both
   snap and gnome-software deb.

If all the testing indicates that the image containing the new package
is acceptable, verification will be considered to be done and the
package can be released from -proposed after the standard aging period.

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be done with a single process bug for this stable release
exception, instead of individual bug reports for individual bug fixes.
However, individual bugs may be referenced in the changelog but each of
those bugs will need to be independently verified and commented on for
the SRU to be considered complete.

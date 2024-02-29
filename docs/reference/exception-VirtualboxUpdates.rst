#. 

   #. page was renamed from Virtualbox

.. _stable_release_updates_for_virtualbox_updates:

Stable Release Updates for Virtualbox Updates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Virtualbox has a number of features making it a special case for SRUs -
as a virtual-machine provider it has some of the same requirements as
hardware-enablement features. It provides a kernel module, interacting
with the hardware enablement work done for the kernel. Finally, upstream
does not put out security-only patches, so fixing security bugs requires
taking micro-release versions.

Fortunately, upstream has a robust testing system.

As such, upstream micro releases may be SRUed as-is to Ubuntu stable
releases with the following process:

.. _package_list:

Package List
------------

-  

   -  virtualbox
   -  virtualbox-hwe
   -  virtualbox-ext-pack
   -  virtualbox-guest-additions-iso

.. _sru_expectations:

SRU Expectations
----------------

There should be one SRU bug for the update, following the template
below:

::

   [Impact]

   * MRE for Virtualbox $VERSION

   [Test Case]

   The only supported architecture for Virtualbox is amd64, so all testing is done on that architecture.

   Install virtualbox-qt, virtualbox-guest-additions-iso

   Windows VM:
   ** Start a windows VM (Windows install images can be found on the Microsoft site. For example: https://www.microsoft.com/en-au/software-download/windows11)
   ** Add the guest-additions iso (found in /usr/share/virtualbox/VBoxGuestAdditions.iso) to the VM.
   ** Update (or install) the guest additions from iso pack inside the VM.
   ** Reboot the VM.
   ** Check if the VM starts correctly and the acceleration works.

   Linux VM:
   ** Start a linux VM (Most recent Ubuntu LTS).
   ** Add the guest-additions iso (found in /usr/share/virtualbox/VBoxGuestAdditions.iso) to the VM.
   ***********************
   ** Update (or install) the guest additions from iso pack inside the VM.
       This can be done inside the menu of Virtualbox -> Devices -> Insert Guest Additions CD image.
       To install it:
       Windows:
       Click on the newly inserted cd in file manager, and run AutoPlay. After installation, reboot
       Linux:
       Can be done in a similar graphical way (such as Windows), but also via cmdline
       $ sudo mkdir /mnt/cdrom
       $ sudo mount /dev/cdrom /mnt/cdrom
       $ cd /mnt/cdrom
       $ sudo sh ./VBoxLinuxAdditions.run --nox11

   ***********************
   ** Reboot the VM.
   ** Check if the VM starts correctly and the acceleration works.

   ***********************
   ** Remove guest additions (Linux only) and install the virtualbox-guest-x11 package (Linux only).
       Removing can be done via
       $ sudo sh VBoxLinuxAdditions.run uninstall (with iso inserted)
       or
       $ cd /opt/VBoxGuestAdditions-$VERSION
       $ sudo sh uninstall.sh
   ***********************
   ** Check if vboxdrv is correctly built, check if *.ko modules are built on the target linux VM.
       $ find /lib/modules -name "vboxdrv.ko"
       /lib/modules/6.2.0-35-generic/misc/vboxdrv.ko
   ** Install Virtualbox inside the VM and check if it can start correctly.


   ***********************
   Moreover various other tests are performed, like changing configuration, and using vboxmanage from cmdline
   - What tests, how do we perform them?
   check headless start
   $ vboxmanage controlvm $MACHINE-NAME poweroff ; vboxmanage startvm $MACHINE-NAME --type headless
   check normal start
   $ vboxmanage controlvm $MACHINE-NAME poweroff ; vboxmanage startvm $MACHINE-NAME

   Try to enable/disable 3d from machine settings and restart (Display-> Enable 3D Acceleration)
   ***********************

   < OPTIONAL - EITHER >
   The changelog has been inspected and no changes of particular concern have been identified.

   <          - OR >
   $SPECIFIC_CHANGES in this update effect $THING. Additionally to the standard testing above,
   $SPECIFIC_TEST_CASES should be performed.

   [Regression Potential]
   Any aspect of VM functionality could be affected; this risk is mitigated by extensive upstream testing and the test cases above.

   < IF SPECIFIC CHANGES ARE FLAGGED >
   $SPECIFIC_CHANGES could affect $FUNCTIONALITY.

   [Other Info]
   < Any extra information relevant to this update >

.. _other_information:

Other Information
-----------------

Upstream:

| `` - Micro releases happen from low-volume stable branches,``
| ``   approximately once every two months.``

`` - Stable branches are supported with bug fixes for some years``

(normally 5 years + 6 months or more).

`` - Upstream commits are reviewed by members of the Virtualbox team.``

| `` - All commits to stable branches are evaluated w.r.t. potential``
| ``   regressions and signed off by the Virtualbox team.``

| `` - Unit tests and regression tests are run on multiple platforms per``
| ``   push to the source code repository. In addition, there are more``
| ``   extensive test suites run daily and weekly.``

| `` - Each micro release receives extensive testing between code freeze``
| ``   and release. This includes the full functional test suite,``
| ``   performance regression testing, load and stress testing and``
| ``   compatibility and upgrade testing from previous micro and``
| ``   minor/major releases.``

`` - Tests are run on all supported platforms (currently amd64).``

Additional tests done are:

In Debian/Ubuntu:

`` - Upstream generally refuses to give CVE targeted fixes [1], so this``

leaves virtualbox in stable releases generally vulnerable, e.g. to
CVE-2015-2594

`` [1] ``\ ```http://www.oracle.com/us/support/assurance/vulnerability-remediation/disclosure/index.html`` <http://www.oracle.com/us/support/assurance/vulnerability-remediation/disclosure/index.html>`__

- - Usually newer kernels means a bad experience for users, since the
kernel drivers are rebuilt at each kernel update, and leads to failures
like [2] and [3]

[2] https://bugs.launchpad.net/ubuntu/+source/virtualbox/+bug/1457776
[3] https://bugs.launchpad.net/ubuntu/+source/virtualbox/+bug/1457780

This is actually mitigated since Vivid releases, because of:

-  

   -  Re-work the packaging to account for the kernel modules being
      shipped in the master kernel packages, removing the need for dkms
      (LP: #1434579):

| ``   * Make the dkms package provide a virtual package matching what the kernel packages provide to indicate that they ship the dkms modules.``
| ``   * Add an alternate dep from the utils package to the virtual driver.``
| ``   * Make the x11 driver package associate with the VGA controllerPCI ID.``

``-- Adam Conrad <adconrad at ubuntu.com>   Wed, 22 Apr 2015 10:01:25 +0100``

so actually having that change will make the problem disappear when an
official -lts kernel is used, and updating vbox will make the problem
disappear also for custom kernels (unless they are RC kernels, of
course)

Additional notes by Gianfranco Costamagna (Debian Developer and
Virtualbox Maintainer)

as stated in Debian bug 794466 I will (ask for) upload in security
pockets the new micro releases, and wait for feedbacks (on top of the
testing I do locally at each upload, including creating a clean target
environment, doing upgrade testing and checking if VM still starts
correctly).

After that I will do the same testing for Ubuntu supported releases, and
actively monitor bugs for regression that I'll try to promptly fix
whenever a regression is found.

AFAICS I have never saw a regression in my yearly vbox maintenance on
micro releases, but in case I'm sure upstream will help us in fixing
them, because they actively monitor for regressions and bugs on all the
tracker they have (including vbox-dev mail list and vbox forum, other
than the ticket system)

Debian already accepted my request of targeted MRE fixes, so we have a
CVE-free virtualbox in jessie/wheezy/ oldstable (partially, because the
support of virtualbox-ose has ended this year).

Another MRE for Debian is ongoing right now (4.3.32 and 4.1.42) with
fixes for CVE-2015-4896 and CVE-2015-4813

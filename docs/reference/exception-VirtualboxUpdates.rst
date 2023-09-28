#. 

   #. page was renamed from Virtualbox

.. _stable_release_updates_for_virtualbox_updates:

Stable Release Updates for Virtualbox Updates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SRU process for Virtualbox follows the same process as `Ubuntu
Stable Release
Updates <https://wiki.ubuntu.com/StableReleaseUpdates>`__. This page
summarises the process.

.. _package_list:

Package List
------------

.. _virtualbox_packages:

Virtualbox packages
~~~~~~~~~~~~~~~~~~~

-  

   -  virtualbox
   -  virtualbox-hwe
   -  virtualbox-guest-additions-iso
   -  virtualbox-ext-pack

.. _sru_expectations:

SRU Expectations
----------------

Upstream:

| `` - Micro releases happen from low-volume stable branches,``
| ``   approximately once every two months.``

`` - Stable branches are supported with bug fixes for some years``

(normally 5 years + 6 months or more).

| `` - Upstream commits are reviewed by members of the Virtualbox Server``
| ``   Engineering team.``

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

Additional tests done are: Install virtualbox\* packages - put in ppa
https://launchpad.net/~costamagnagianfranco/+archive/ubuntu/virtualbox-ppa
and ask for testing - start a windows VM (generally w10, or w11) -
update the guest additions from iso pack inside the VM - reboot the VM -
check if the VM starts correctly and the acceleration works

- start a linux VM (generally ubuntu LTS or Debian stable) - update the
guest additions from iso pack inside the VM - reboot the VM - check if
the VM starts correctly and the acceleration works - remove guest
additions and install the virtualbox-guest-x11 package (linux only)

- Check if vboxdrv is correctly built, check if \*.ko modules are built
on the target linux VM - Install virtualbox inside the VM and check if
it can start correctly.

Moreover various other tests are performed, like changing configuration,
and using vboxmanage from cmdline. Depending on the diff between the two
releases, the diff is inspected and more deep and targeted tests are
performed.

Upstream update policy (from upstream developers, not from Oracle
company)

For VBox 4.x, the support period was 5 years. As VBox 4.0 was released
in December 2010, the official support for VBox 4.x (including 4.3) will
end in December 2015. For VBox 4.3 we will probably extend the period
for a few month. With VBox 5.x, the support period is still 5 years but
once VBox 5.1.x is released, users have to switch from 5.0 to 5.1 within
a certain period. There will be a grace period of approx. 6 month but
after that, There will be no further updates for 5.0.x. So within the 5
years it will happen that 5.1.x replaces 5.0.x at some time and there
will be no further updates to 5.0 when 5.1.0 is released + approx 6
months. Btw, disclaimer: This is not an official Oracle statement (I'm
not allowed to do that) but you can take these statements serious.

In Debian/Ubuntu:

`` - Upstream generally refuses to give CVE targeted fixes [1], so this``

leaves virtualbox in stable releases generally vulnerable, e.g. to
CVE-2015-2594

`` [1]``

http://www.oracle.com/us/support/assurance/vulnerability-remediation/disclosure/index.html

- - Usually newer kernels means a bad experience for users, since the
kernel drivers are rebuilt at each kernel update, and leads to failures
like [2] and [3]

[2] https://bugs.launchpad.net/ubuntu/+source/virtualbox/+bug/1457776
[3] https://bugs.launchpad.net/ubuntu/+source/virtualbox/+bug/1457780

This is actually mitigated since Vivid releases, because of:

-  

   -  Re-work the packaging to account for the kernel modules being
      shipped in

| ``   the master kernel packages, removing the need for dkms (LP: #1434579):``
| ``   - Make the dkms package provide a virtual package matching what the``
| ``     kernel packages provide to indicate that they ship the dkms modules.``
| ``   - Add an alternate dep from the utils package to the virtual driver.``
| ``   - Make the x11 driver package associate with the VGA controllerPCI ID.``

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

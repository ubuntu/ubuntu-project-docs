.. _reference-package-specific-notes:

Package-specific notes
----------------------

See also: :ref:`Explanation → Non-standard Processes → Package-specific
non-standard processes <explanation-package-specific-non-standard-processes>`

The `Technical Board resolution on
Landscape <https://lists.ubuntu.com/archives/ubuntu-devel-announce/2009-March/000550.html>`__
provides a general rationale for the types of special cases that may be
approved here in future. Most exception approvals are now handled
directly by the SRU team.

To obtain a new ongoing exception such as those documented below:

#. Draft an exception page, like the ones referenced below, outlining what
   you believe should be the exception.

#. Submit it to the SRU team for approval via a PR to this repository.
   To discuss further see :ref:`Howto → Contact <howto-contact>`

Note that the SRU team's delegation from the Technical Board is limited
to accepting SRU uploads that meet the `policy criteria <#When>`__
above. The SRU team maintains documentation for standing exceptions here
to keep individual interpretations of the policy criteria consistent.
Departing from the policy criteria above still requires approval from
the Technical Board.


.. toctree::
    :maxdepth: 1
    :hidden:

    exception-Kernel-Updates
    exception-Apt-Updates
    exception-Bind9-Updates
    exception-Certbot-Updates
    exception-Cloudinit-Updates
    exception-Curtin-Updates
    exception-DPDK-Updates
    exception-Docker-Updates
    exception-GNOME-Updates
    exception-Grub-Updates
    exception-HAProxy-Updates
    exception-Landscape-Updates
    exception-NVidia-Updates
    exception-Netplan-Updates
    exception-OEMMeta-Updates
    exception-OpenJDK-Updates
    exception-OpenLDAP-Updates
    exception-OpenStack-Updates
    exception-OpenVMTools-Updates
    exception-OpenVPN-Updates
    exception-Postfix-Updates
    exception-PostgreSQL-Updates
    exception-Snapcraft-Updates
    exception-SnapdGlib-Updates
    exception-Snapd-Updates
    exception-Sosreport-Updates
    exception-Squid-Updates
    exception-UbuntuAdvantageTools-Updates
    exception-UbuntuDevTools-Updates
    exception-UbuntuImage-Updates
    exception-Virtualbox-Updates
    exception-autopkgtest-Updates
    exception-ec2-hibinit-agent-Updates
    exception-firmware-updates
    exception-gce-compute-image-packages-Updates
    exception-google-compute-engine-Updates
    exception-google-compute-engine-oslogin-Updates
    exception-google-guest-agent-Updates
    exception-google-osconfig-agent-Updates
    exception-rax-nova-agent-Updates
    exception-walinuxagent-Updates
    exception-wslu-Updates

.. _reference-sru-interest-team:

Groups of SRU interest
----------------------

Many packages are commonly used in various important production environments
but as the exceptions show, some updates can be quite complex. In addition to
the tests outlined in the individual exception document we'd ask the
:ref:`SRU driver <explanation-role-expectations>`
to please inform the SRU Interest Team about upcoming updates.

If defined, the package specific notes will refer to this paragraph and
to the group that shall be subscribed.

* **When**: Please do so as early as you know can predict what will be changed,
  document that in the bug and then act. No need to wait until it hits -proposed.

* **How**: Please add the referred Interest group as subscriber to the
  the related SRU bug that you are preparing.

These people/teams might do additional testing, but are not hard committed
for anything. Therefore we will not gate on their positive reply to set a
case to "verified". But if they come back:

* with a good regression report => we expect it to be considered
* with a pass from their tests => more confidence in the proposed change

*Known constraints/imperfections:*
As of today there is no tooling yet ensuring an interested group has been added.
It - for now - only a social/policy request to the driver of the SRU.
Therefore, until this is fully automated, there might be mistakes which we can
not be too upset about - if you are, help to develop the tooling please :-)


Defined Exceptions
------------------

Kernel
~~~~~~

Because of the way updates to the kernel work, it will follow a slightly
different process which is described on :ref:`KernelUpdates <reference-exception-kernelupdates>`.

Landscape
~~~~~~~~~

The landscape-client source package may be uploaded according to the
procedure documented in :ref:`LandscapeUpdates <reference-exception-landscapeupdates>`.
See the `Technical Board resolution <https://lists.ubuntu.com/archives/ubuntu-devel-announce/2009-March/000550.html>`__
for details and rationale.

Snapd
~~~~~

The snapd source package may be uploaded according to the procedure
documented in :ref:`SnapdUpdates <reference-exception-snapdupdates>`.
Per Technical Board discussion regarding delegation of these decisions
to the SRU team, this stable release exception has been approved by
SteveLangasek for the SRU team as of 2016-05-12.

Snapcraft
~~~~~~~~~

Related to the preceding snapd exception, the snapcraft source package
may be uploaded according to the procedure documented in
:ref:`SnapcraftUpdates <reference-exception-snapcraftupdates>`.
This stable release exception has been approved by
SteveLangasek for the SRU team as of 2016-05-16.

Ubuntu-image
~~~~~~~~~~~~

Also related to snapd, the ubuntu-image package may be uploaded
according to the procedure documented in :ref:`UbuntuImageUpdates <reference-exception-ubuntuimageupdates>`.
This stable release exception has been approved by SteveLangasek for the SRU team as
of 2016-10-19.

Docker.io group
~~~~~~~~~~~~~~~

The source packages docker.io, containerd, and runc may be uploaded
according to the procedure documented in :ref:`DockerUpdates <reference-exception-dockerpdates>`.
Per Technical Board discussion regarding delegation of these decisions to the SRU
team, this stable release exception has been approved by BrianMurray for
the SRU team as of 2016-09-20, with changes through to revision 19
further approved by RobieBasak for the SRU team on 2025-04-30.

gce-compute-image-packages
~~~~~~~~~~~~~~~~~~~~~~~~~~

The source package gce-compute-image-packages may be uploaded according
to the procedure documented in
:ref:`gce-compute-image-packages-Updates <reference-exception-gce-compute-image-packages-updates>`.
Per Technical Board discussion regarding delegation of these decisions
to the SRU team, this stable release exception has been approved by
BrianMurray for the SRU team as of 2017-03-10. Further amendment to this
exception for vendored dependencies approved by LukaszZemczak for the
`SRU team as of
2023-04-11 <https://lists.ubuntu.com/archives/ubuntu-release/2023-April/005606.html>`__.

google-compute-engine
~~~~~~~~~~~~~~~~~~~~~

The source package gce-compute-image-packages may be uploaded according
to the procedure documented in
:ref:`google-compute-engine-Updates <reference-exception-google-compute-engine-Updates>`.
Per Technical Board discussion regarding delegation of these decisions
to the SRU team, this stable release exception has been approved by
SteveLangasek for the `SRU team as of
2022-09-01 <https://lists.ubuntu.com/archives/ubuntu-release/2022-September/005479.html>`__.
Further amendment to this exception for vendored dependencies approved
by LukaszZemczak for the `SRU team as of
2023-04-11 <https://lists.ubuntu.com/archives/ubuntu-release/2023-April/005606.html>`__.

google-compute-engine-oslogin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The source package google-compute-engine-oslogin may be uploaded
according to the procedure documented in
:ref:`google-compute-engine-oslogin-Updates <reference-exception-google-compute-engine-oslogin-Updates>`.
Per Technical Board discussion regarding delegation of these decisions
to the SRU team, this stable release exception has been approved by
SteveLangasek for the `SRU team as of
2022-09-01 <https://lists.ubuntu.com/archives/ubuntu-release/2022-September/005479.html>`__.
Further amendment to this exception for vendored dependencies approved
by LukaszZemczak for the `SRU team as of
2023-04-11 <https://lists.ubuntu.com/archives/ubuntu-release/2023-April/005606.html>`__.

google-guest-agent
~~~~~~~~~~~~~~~~~~

The source package gce-compute-image-packages may be uploaded according
to the procedure documented in
:ref:`google-guest-agent-Updates <reference-exception-google-guest-agent-Updates>`.
Per Technical Board discussion regarding delegation of these decisions
to the SRU team, this stable release exception has been approved by
SteveLangasek for the `SRU team as of
2022-09-01 <https://lists.ubuntu.com/archives/ubuntu-release/2022-September/005479.html>`__.
Further amendment to this exception for vendored dependencies approved
by LukaszZemczak for the `SRU team as of
2023-04-11 <https://lists.ubuntu.com/archives/ubuntu-release/2023-April/005606.html>`__.

google-osconfig-agent
~~~~~~~~~~~~~~~~~~~~~

The source package google-osconfig-agent may be uploaded according to
the procedure documented in
:ref:`google-osconfig-agent-Updates <reference-exception-google-osconfig-agent-Updates>`.
Per Technical Board discussion regarding delegation of these decisions
to the SRU team, this stable release exception has been approved by
SteveLangasek for the `SRU team as of
2022-09-01 <https://lists.ubuntu.com/archives/ubuntu-release/2022-September/005479.html>`__.
Further amendment to this exception for vendored dependencies approved
by LukaszZemczak for the `SRU team as of
2023-04-11 <https://lists.ubuntu.com/archives/ubuntu-release/2023-April/005606.html>`__.

curtin
~~~~~~

The source package curtin may be uploaded according to the procedure
documented in :ref:`CurtinUpdates <reference-exception-CurtinUpdates>`.
This stable release exception has been
approved by SteveLangasek for the SRU team as of 2017-04-05.

walinuxagent
~~~~~~~~~~~~

The source package walinuxagent may be uploaded according to the
procedure documented in
:ref:`walinuxagentUpdates <reference-exception-walinuxagentUpdates>`.
This stable release exception has been approved by SteveLangasek for the
SRU team as of 2017-04-05.

GNOME
~~~~~

GNOME has a microrelease exception excepting it from the normal QA
requirements of the microrelease policy, :ref:`documented here <reference-exception-GNOMEUpdates>`.
This was `granted by the technical board on
2012-06-22 <https://lists.ubuntu.com/archives/technical-board/2012-June/001327.html>`__.

OpenStack
~~~~~~~~~

OpenStack packages can be updated according to the procedures
documented in :ref:`OpenStackUpdates <reference-exception-OpenStackUpdates>`,
which includes a list of
source packages covered by the MRE. This stable release exception has
been approved by LukaszZemczak for the SRU team as of 2017-08-07.

Certbot
~~~~~~~

The Certbot family of packages can be updated according to the
procedures documented in :ref:`Certbot <reference-exception-CertbotUpdates>`.
This stable release exception was
`discussed <https://lists.ubuntu.com/archives/ubuntu-release/2017-July/004176.html>`__
and subsequently revision 10 of that document was approved by RobieBasak
for the SRU team on 2017-08-08.

cloud-init
~~~~~~~~~~

The source package cloud-init may be uploaded according to the procedure
documented in :ref:`CloudinitUpdates <reference-exception-CloudinitUpdates>`.
Per Technical Board discussion regarding
delegation of these decisions to the SRU team, this stable release
exception has been approved by BrianMurray for the SRU team as of
2017-10-06 with subsequent updates approved by RobieBasak on 2020-07-15.

DPDK
~~~~

The dpdk source package can be uploaded according to the procedures
documented in :ref:`DPDK <reference-exception-DPDKUpdates>` for supported LTS
releases of Ubuntu. This stable release exception has been approved by
LukaszZemczak for the SRU team as of 2017-08-07.

ubuntu-release-upgrader and python-apt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The packages ubuntu-release-upgrader and python-apt both contain files
with listings of Ubuntu mirrors. To facilitate upgrades to new releases
ubuntu-release-upgrader should be updated (particularly for LTS
releases) so that the list of mirrors is accurate. With that in mind and
given that it is just a text file with urls for mirrors it is okay to
SRU only mirror changes for these packages without an SRU bug.

apt and python-apt
~~~~~~~~~~~~~~~~~~

Not a policy exception, but see :ref:`AptUpdates <reference-exception-AptUpdates>`
for details of unusual SRU versioning.

rax-nova-agent
~~~~~~~~~~~~~~

The source package rax-nova-agent may be uploaded according to the
procedure documented in
:ref:`rax-nova-agent-Updates <reference-exception-rax-nova-agent-Updates>`.
This stable release exception has been approved by SteveLangasek for the
SRU team as of 2018-08-15.

livecd-rootfs
~~~~~~~~~~~~~

The livecd-rootfs package is a frequent target of SRUs as part of
development of changes to image builds for the target series, and is not
intended for general installation on end-user systems. The risk of
user-affecting regression is lower as a result, because the impact of
changes to this package to end users is mediated by way of image builds.
Therefore, the requirement for per-change bug reports and test cases is
relaxed, as long as there is at least one linked bug with a test case.

fwupd and fwupdate
~~~~~~~~~~~~~~~~~~

The source packages fwupd and fwupdate may be uploaded according to the
procedure documented in
:ref:`firmware-updates <reference-exception-firmware-updates>`. This
stable release exception has been approved by BrianMurray for the SRU
team as of 2019-01-15.

snapd-glib
~~~~~~~~~~

The source package snapd-glib may be uploaded according to the procedure
documented in :ref:`snapd-glib updates <reference-exception-SnapdGlibUpdates>`.
This stable release exception has been approved by BrianMurray for the
SRU team as of 2019-02-19.

netplan.io
~~~~~~~~~~

The source package netplan.io may be uploaded according to the procedure
documented in :ref:`netplan updates <reference-exception-NetplanUpdates>`.
This stable release exception has been approved by BrianMurray for the
SRU team as of 2019-04-01 (no really!).

ec2-hibinit-agent
~~~~~~~~~~~~~~~~~

The source package ec2-hibinit-agent may be uploaded according to the
procedure documented in :ref:`ec2-hibinit-agent updates <reference-exception-ec2-hibinit-agent-Updates>`.
This stable release exception has been approved by SteveLangasek for the SRU
team as of 2019-09-06.

NVIDIA driver
~~~~~~~~~~~~~

NVIDIA driver (source packages nvidia-graphics-drivers-\*,
nvidia-settings, fabric-manager-\*, libnvidia-nscq-\*) may be uploaded
according to the procedure documented in :ref:`NVIDIA
updates <reference-exception-NVidiaUpdates>`. This stable release
exception has been approved by ChrisHalseRogers for the SRU team as of
2019-09-17.

wslu
~~~~

The wslu package may be uploaded according to the procedure documented
in :ref:`wslu Updates <reference-exception-wslu-Updates>`. This stable
release exception has been approved by LukaszZemczak for the SRU team as
of 2019-10-24.

openjdk-N
~~~~~~~~~

We allow providing OpenJDK short term support releases in the updates
pocket, instead of the release pocket to be able to remove those after
their support ends as documented in :ref:`OpenJDK
Updates <reference-exception-OpenJDK-Updates>`. This very specific
stable release exception has been approved by LukaszZemczak for the SRU
team as of 2020-04-30.

Postfix
~~~~~~~

The postfix source package may be uploaded according to the procedure
documented in :ref:`PostfixUpdates <reference-exception-PostfixUpdates>`. See the `Technical Board meeting
minutes <https://lists.ubuntu.com/archives/ubuntu-devel-announce/2011-October/000902.html>`__
and its
`approval <https://lists.ubuntu.com/archives/technical-board/2012-May/001266.html>`__
for details and rationale.

sosreport/sos
~~~~~~~~~~~~~

The source package sosreport/sos may be uploaded according to the
procedure documented in :ref:`sosreport
updates <reference-exception-SosreportUpdates>`. This stable
release exception has been approved by LukaszZemczak for the SRU team as
of 2020-06-25. This was updated for the source package sos and `approved
by Robie
Basak <https://lists.ubuntu.com/archives/ubuntu-release/2025-February/006325.html>`__.

oem-\*-meta
~~~~~~~~~~~

Source packages of the form oem-\*-meta may be uploaded according to the
procedure documented in
:ref:`OEMMeta <reference-exception-OEMMetaUpdates>`. This
stable release exception has been approved by AndyWhitcroft for the SRU
team as of 2021-07-15. New packages are acceptable under the same
exception.

ubuntu-dev-tools
~~~~~~~~~~~~~~~~

The source package ubuntu-dev-tools may be uploaded according to the
procedure documented in
:ref:`UbuntuDevToolsUpdates <reference-exception-UbuntuDevToolsUpdates>`.
This stable release exception has been `approved by Robie
Basak <https://lists.ubuntu.com/archives/ubuntu-release/2023-May/005640.html>`__.

OpenLDAP
~~~~~~~~

The OpenLDAP source package may be uploaded according to the procedure
documented in :ref:`OpenLDAPUpdates <reference-exception-OpenLDAPUpdates>`.
This stable release exception `has been
approved <https://lists.ubuntu.com/archives/ubuntu-release/2022-June/005403.html>`__
by SteveLangasek for the SRU team as of 2022-06-02.

HAProxy
~~~~~~~

The haproxy source package may be uploaded according to the procedure
documented in :ref:`HAProxyUpdates <reference-exception-HAProxyUpdates>`. This stable release
exception `has been
approved <https://lists.ubuntu.com/archives/ubuntu-release/2022-June/005417.html>`__
by LukaszZemczak for the SRU team as of 2022-06-27.

autopkgtest
~~~~~~~~~~~

The autopkgtest source package may be uploaded according to the
procedure documented in :ref:`autopkgtest-Updates <reference-exception-autopkgtest-Updates>`.
This stable release exception `has been
approved <https://lists.ubuntu.com/archives/ubuntu-release/2023-January/005530.html>`__
by SteveLangasek for the SRU team as of 2023-01-30.

squid
~~~~~

The squid source package may be uploaded according to the procedure
documented in :ref:`SquidUpdates <reference-exception-SquidUpdates>`. This stable release
exception `has been
approved <https://lists.ubuntu.com/archives/ubuntu-release/2023-April/005589.html>`__
by SteveLangasek for the SRU team on 2023-04-03.

bind9
~~~~~

The bind9 source package may be uploaded according to the procedure
documented in :ref:`Bind9Updates <reference-exception-Bind9Updates>`. This stable release
exception `has been
approved <https://lists.ubuntu.com/archives/ubuntu-release/2023-June/005647.html>`__
by SteveLangasek for the SRU team as of 2023-06-06.

virtualbox
~~~~~~~~~~

-  

   -  THIS IS OUTDATED !!! \**\*

The virtualbox source packages may be uploaded according to the
procedure documented in
:ref:`VirtualboxUpdates <reference-exception-VirtualboxUpdates>`. This
stable release exception `has been
approved <https://lists.ubuntu.com/archives/technical-board/2015-November/002177.html>`__
by Martin Pitt for the SRU team as of 2015-11-04.

ubuntu-advantage-tools
~~~~~~~~~~~~~~~~~~~~~~

The ubuntu-advantage-tools source package may be uploaded according to
the SRU procedures documented in
:ref:`UbuntuAdvantageToolsUpdates <reference-exception-UbuntuAdvantageToolsUpdates>`. This
stable release exception `has been
approved <https://lists.ubuntu.com/archives/ubuntu-release/2023-October/005810.html>`__
by RobieBasak for the SRU team part as of 2023-10-04.

open-vm-tools
~~~~~~~~~~~~~

The open-vm-tools source package may be uploaded according to the
proceedure documented in :ref:`OpenVMToolsUpdates <reference-exception-OpenVMToolsUpdates>`.
This stable release exception `has been
approved <https://lists.ubuntu.com/archives/ubuntu-release/2024-January/005900.html>`__
by ChrisHalseRogers for the SRU team as of 2024-01-25.

postgresql
~~~~~~~~~~

The currently supported postgresql source package (as determined by the
dependency of the postgresql metapackage) for each stable release may be
uploaded according to the proceedure documented in
:ref:`PostgreSQLUpdates <reference-exception-PostgreSQLUpdates>`. This stable release exception
`has been
approved <https://lists.ubuntu.com/archives/ubuntu-release/2024-January/005915.html>`__
by ChrisHalseRogers for the SRU team as of 2024-01-31

GRUB
~~~~

GRUB related packages require a special SRU process due our EFI signing
pipeline, documented at
:ref:`Grub updates <reference-exception-GrubUpdates>`.

OpenVPN
~~~~~~~

Updates including upstream OpenVPN microreleases should follow the
special case documentation at :ref:`OpenVPNUpdates <reference-exception-OpenVPNUpdates>`.
This is not a standing approval or policy exception, but a general pattern to
update OpenVPN upstream microreleases consistently under existing SRU
policy.

Language Packs (language-pack-\*)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is some documentation at:
https://git.launchpad.net/langpack-o-matic/tree/doc/operator-guide.txt

cd-boot-images-<arch>
~~~~~~~~~~~~~~~~~~~~~

These packages have a strict build-dependency on specific versions of
grub and others. It can happen that these build-dependencies are no
longer satisfied since the package was uploaded to unapproved, because
the build-dependencies were updated themselves in the meantime. While
this would just create a failure to build, it would also waste a version
number if accepted into proposed in this state, so it's a recommendation
to check the availability of the build dependencies before accepting the
package into proposed.

For a concrete example, see
https://bugs.launchpad.net/ubuntu/+source/cd-boot-images-riscv64/+bug/2104572/comments/9

Data Packages Kept in Sync with Security
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some data packages must always be kept in sync between -updates and
-security to avoid behaviour or functionality regressions when using
only the security pocket. Because they are pure data, and contain no
compiled code, these packages are safe to build in -proposed and then
copy to both -updates and -security.

tzdata
~~~~~~

The tzdata package is updated to reflect changes in timezones or
daylight saving policies. The verification is done with the "zdump"
utility. The first timezone that gets changed in the updated package is
dumped with "zdump -v $region/$timezone_that_changed" (you can find the
region and timezone name by grep'ing for it in /usr/share/zoneinfo/).
This is compared to the same output after the updated package was
installed. If those are different the verification is considered done.

+---------------+-----------+-----------+-----------+-------+-------+
| Feature       | 16.04 LTS | 18.04 LTS | 20.04 LTS | 21.04 | 21.10 |
+===============+===========+===========+===========+=======+=======+
| icu-data      | No        | No        | Yes       | Yes   | Yes   |
+---------------+-----------+-----------+-----------+-------+-------+
| SystemV tzs   | Yes       | Yes       | Yes       | No    | No    |
+---------------+-----------+-----------+-----------+-------+-------+

The version of tzdata in Ubuntu 20.04 LTS and later includes icu-data
(see the update-icu rule in debian/rules) and the verification of it can
be done after installing the **python3-icu** package. There can be a
slight lag between the tzdata release and the matching icu-data release,
we usually wait for the latter to be released before uploading the
update.

::

   python3 -c "from datetime import datetime; from icu import ICUtzinfo, TimeZone; tz = ICUtzinfo(TimeZone.createTimeZone('Pacific/Fiji')); print(str(tz.utcoffset(datetime(2020, 11, 10))))"

In the above we are checking a timezone with a change, "Pacific/Fiji",
and a date that falls with in the changing period. We expect the output
to be different before (13:00:00) and after (12:00:00) the SRU is
installed.

The version of tzdata in Ubuntu 20.10 removed supported for SystemV
timezones, however SRUs of tzdata to Ubuntu 20.04 LTS and earlier
releases should still include the SystemV timezones. To test that they
are still available confirm the following command returns nothing.

::

   diff <(zdump -v America/Phoenix | cut -d' ' -f2-) <(zdump -v SystemV/MST7 | cut -d' ' -f2-)

Because tzdata's packaging has changed subtly from release to release,
rather than just backporting the most recent release's source package,
we just update the upstream tarball instead. You then need to edit
debian/changelog to add bug closures, and make sure to use a version
number consistent to the previous numbering scheme (e. g.
\`2012e-0ubuntu0.12.04\`). Uploads should also be made to any releases
supported via ESM.

Due to the potentially disastrous consequences of having localtime
differ between systems running -updates and systems running only
-security, this package is always kept in sync between the two pockets.
However, the package can be built with -updates and then copied from
-proposed to -updates and -security after the security team has signed
off on the SRU bug e.g. `Bug 1878108 <https://bugs.launchpad.net/ubuntu/+source/tzdata/+bug/1878108>`__.

distro-info-data
~~~~~~~~~~~~~~~~

Many tools behave drastically differently based on the contents of
ubuntu.csv in distro-info-data. As such, information for new releases is
always backported to -updates, and should always be copied to -security
to avoid behaviour skew between the two pockets.

This package should be updated as soon as possible after the new
release's name is known. If only the adjective is known, it should be
updated even with this partial information (use XANIMAL for the animal
where X is the first letter of the adjective). The aging requirement is
not applied for releasing to -updates / -security. A tracking bug is
still required for SRUs. Verification is still required. The testing
section should contain:

::

   [ Test Plan ]
     
   Verify that the following subcommands of `distro-info` print information about the new devel and current stable releases:
     
   * `--devel`
   * `--supported`
   * `--stable`

   and try the same commands with these modifiers:

   * `--date=<1 day after release>` along with the above
   * `--fullname`
   * `--release`

linux-firmware
~~~~~~~~~~~~~~

linux-firmware in stable releases is kept in sync with new driver
features and lts-hwe kernel updates. linux-firmware follows the normal
SRU process (with bugs filed and regression tests performed), however it
must also be copied to the -security pocket once verified, due to the
vast majority of kernel SRUs also being in the -security pocket, and the
necessity of linux and linux-firmware not being mismatched.

wireless-regdb
~~~~~~~~~~~~~~

Much like linux-firmware, wireless-regdb follows the usual SRU process,
including a bug and regression testing, however it is another package
that needs to be kept in sync between -updates and -security pockets to
avoid potential local legal issues for -security users who would
otherwise not get the local regdb updates.

Toolchain Updates
~~~~~~~~~~~~~~~~~

Due to the nature of the various Ubuntu toolchain packages (gcc-\*,
binutils, glibc), any stable release updates of these packages should be
released to both the -updates and -security pockets. For that to be
possible, any updates of those should be first built in a reliable
security-enabled PPA (without -updates or -proposed enabled) and only
then **binary-copied** into -proposed for testing (that is a
hard-requirement for anything copied into -security). After the usual
successful SRU verification and aging, the updated packages should be
released into both pockets.

Toolchains:

* Java: `Java updates PPA <https://launchpad.net/~openjdk-r/+archive/ubuntu/ppa>`__
* Go: `Go updates PPA <https://launchpad.net/~ubuntu-toolchain-r/+archive/ubuntu/golang>`__


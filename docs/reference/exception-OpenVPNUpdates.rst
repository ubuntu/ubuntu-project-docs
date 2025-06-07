.. _reference-exception-OpenVPNUpdates:

.. _openvpn_updates:

OpenVPN Updates
===============

This document describes the policy for doing micro-release updates of
the OpenVPN package in Ubuntu stable releases.

Note that openvpn does not have an accepted micro-release exception.
However, the SRU team has agreed to consider further releases given a
full knowledge and possible mitigation of backwards-incompatible
changes. See
https://lists.ubuntu.com/archives/ubuntu-release/2023-July/005688.html

.. _about_openvpn:

About OpenVPN
-------------

`OpenVPN <https://openvpn.net/>`__ is an open source VPN daemon.

.. _upstream_release_policy:

Upstream release policy
-----------------------

The OpenVPN community maintains multiple versions in parallel. According
to their `supported versions
documentation <https://community.openvpn.net/openvpn/wiki/SupportedVersions>`__:

-  The current stable release will always be in the Full stable support
   release type
-  The previous major release will remain in Full stable support for at
   least 6 months after a new major version is out, followed by a move
   to Old stable support
-  Old stable support will continue for at least 12 months. After that
   the release is moved to git tree only mode, which is then maintained
   in that state for an additional 12 months

Versions with Full stable support are provided with all bug fixes and
security updates, and have regular version releases. Those with Old
stable support maintain all benefits of Full stable on Linux, excluding
smaller bug fixes. Versions with git-tree only support are only provided
with critical security updates. As of writing this document, the current
stable version is 2.6.4, previous stable is 2.5.9, and version 2.4.12 is
no longer supported as of March 2023.

When it comes to updates in Ubuntu, only releases in the full stable and
old stable categories should be considered. Once a version has moved to
git-tree only, the normal SRU process must be followed for individual
bug fixes.

.. _ubuntu_and_openvpn_releases_affected_by_this_mre:

Ubuntu and OpenVPN releases affected by this MRE
------------------------------------------------

Currently, these are the Ubuntu releases and the corresponding OpenVPN
package versions affected by this policy:

-  Noble (24.04): OpenVPN 2.6.x
-  Jammy (22.04): OpenVPN 2.5.x
-  Focal (20.04): OpenVPN 2.4.x (One time update to 2.4.12 as that is
   the final release for this version)

QA
--

.. _upstream_tests:

Upstream tests
~~~~~~~~~~~~~~

OpenVPN contains a set of build and regression tests which are executed
for each commit and release via `GitHub
Actions <https://github.com/OpenVPN/openvpn/actions>`__. Upstream tests
are provided in the `tests/
directory <https://github.com/OpenVPN/openvpn/tree/master/tests>`__.

There is also a `Buildbot
system <https://community.openvpn.net/openvpn/wiki/SettingUpBuildslave>`__
which builds OpenVPN for various operating systems. The results are
accessible only when connected to the community VPN.

Autopkgtest
-----------

The package contains two DEP-8 tests:

-  server-setup-with-ca - creates and tests an OpenVPN server setup with
   its own certificate authority
-  server-setup-with-static-key - creates and tests an OpenVPN server
   setup using a static key for authentication

These tests are extensive enough to catch major errors when it comes to
the integration of OpenVPN with Ubuntu, along with issues in setup and
VPN configuration.

.. _avoiding_breaking_changes:

Avoiding Breaking Changes
-------------------------

Since upstream has shown that they are occasionally willing to make
changes to their stable releases that break backwards compatibility or
add new features, additional due diligence must be done to avoid causing
problems for Ubuntu users. Prior to merging, version release notes and
announcements from upstream must be checked for these changes. If any do
show up, they must be noted in the bug report. Also, prior to uploading,
discuss with the SRU team as to how to handle the changes. This may
result in a reversion of the backwards-incompatible changes through
patches.

This situation happens most often earlier in the full stable support
phase of a version. For example, as a part of the 2.5.3 release, a new
feature was added which implements auth-token-user. The change was then
referenced in the `release
notes <https://community.openvpn.net/openvpn/wiki/ChangesInOpenvpn25#Changesin2.5.3>`__.

The upstream source directory distro/systemd/ contains systemd unit
files that end up in packaging directly. These must be checked for
changes. If there are any changes, they must be considered independently
and documented in the SRU tracking bug.

Process
-------

As with regular MREs, the aim here is to offer bugfixes and security
fixes to all supported releases.

To do this we will:

#. File a bug to cover the upgrade.

| ``   * Add tasks to all Ubuntu releases which will be updated.``
| ``   * Add a link to the upstream changelog and list major changes.``
| ``2. Make sure the development release contains the fixes that will be added. In general this should be the case as long as it is up to date with its associated release version.``
| ``3. Setup merge with new versions, reverting any backwards-incompatible changes that must be avoided in released versions of Ubuntu.``
| ``4. Run autopkgtest on all supported architectures.``
| ``5. Run autopkgtest on reverse-dependencies against the new release - eurephia, network-manager-openvpn, openvpn-auth-ldap, openvpn-auth-radius, openvpn-systemd-resolved for jammy and focal; and gadmin-openvpn-client and gadmin-openvpn-server for focal only``
| ``6. Upload the microrelease to the SRU queue and wait until it is approved.``
| ``7. Watch the migration page until it lands in the -updates pocket. Fix any regression that might appear during the process.``

.. _sru_template:

SRU template
~~~~~~~~~~~~

::

   This bug tracks an update for the OpenVPN package, moving to versions:

   * [Release codename]  ([Release version]): OpenVPN [OpenVPN version - highest possible number on the last digit]
   * [...]

   These updates include bug fixes following the SRU special case documentation at https://wiki.ubuntu.com/OpenVPNUpdates.

   Note that openvpn does not have an accepted micro-release exception. However, the SRU team has agreed to consider further releases given a full knowledge and possible mitigation of backwards-incompatible changes. See https://lists.ubuntu.com/archives/ubuntu-release/2023-July/005688.html

   [Upstream changes]

   TODO: List updates, CVE fixes, and relevant bug fixes
   TODO: Add a link to the upstream changelog

   TODO: Specifically note any backwards-incompatible changes or features added by upstream and their announcements/release notes and relevant commits.

   [Test Plan]

   TODO: Check DEP-8 and reverse-depends DEP-8 tests pass
   TODO: if there are any non passing tests - explain why that is ok in this case
   TODO: add results of an autopkgtest run against all the new versions

   [Regression Potential]

   Upstream has an extensive build and integration test suite. So regressions would likely arise from a change in interaction with Ubuntu-specific integrations.

   TODO: consider any other regression potential specific to the version being
   updated and list if any.

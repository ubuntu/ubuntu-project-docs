.. _openvpn_updates:

OpenVPN Updates
===============

This document describes the policy for doing micro-release updates of
the OpenVPN package in Ubuntu stable releases.

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
stable version is 2.6.0, previous stable is 2.5.9, and version 2.4.12
will be in support until March 2023.

.. _ubuntu_and_openvpn_releases_affected_by_this_mre:

Ubuntu and OpenVPN releases affected by this MRE
------------------------------------------------

Currently, these are the Ubuntu releases and the corresponding OpenVPN
package versions affected by this policy:

-  Jammy (22.04): OpenVPN 2.5.x
-  Focal (20.04): OpenVPN 2.4.x

QA
--

.. _upstream_tests:

Upstream tests
~~~~~~~~~~~~~~

OpenVPN contains a set of build and regression tests which are executed
for each commit and release via GitHub Actions. Upstream tests are
provided in the `tests/
directory <https://github.com/OpenVPN/openvpn/tree/master/tests>`__.

There is also a `Travis CI
pipeline <https://github.com/OpenVPN/openvpn/blob/master/.travis.yml>`__
which builds OpenVPN for various architectures alongside Windows and Mac
OS. The architectures include:

-  amd64
-  ppc64el
-  arm64
-  s390x

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

Process
-------

As with regular MREs, the aim here is to offer bugfixes and security
fixes to all supported releases.

To do this we will:

#. File a bug to cover the upgrade.

| ``   * Add tasks to all Ubuntu releases which will be updated.``
| ``   * Add a link to the upstream changelog and list major changes.``
| ``2. Make sure the development release contains the fixes that will be added. In general this should be the case as long as it is up to date with its associated release version.``
| ``3. Upload the microrelease to the SRU queue and wait until it is approved.``
| ``4. Watch the migration page until it lands in the -updates pocket. Fix any regression that might appear during the process.``

.. _sru_template:

SRU template
~~~~~~~~~~~~

::

   This bug tracks an update for the OpenVPN package, moving to versions:

   * [Release codename]  ([Release version]): OpenVPN [OpenVPN version - highest possible number on the last digit]
   * [...]

   These updates include bug fixes following the SRU policy exception defined at https://wiki.ubuntu.com/OpenVPNUpdates.

   [Upstream changes]

   TODO: List updates, CVE fixes, and relevant bug fixes
   TODO: Add a link to the upstream changelog

   [Test Plan]

   TODO: Check DEP-8 tests pass
   TODO: if there are any non passing tests - explain why that is ok in this case
   TODO: add results of an autopkgtest run against all the new versions

   [Regression Potential]

   Upstream has an extensive build and integration test suite. So regressions would likely arise from a change in interaction with Ubuntu-specific integrations.

   TODO: consider any other regression potential specific to the version being
   updated and list if any.

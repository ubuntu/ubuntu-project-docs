.. _bind9_updates:

Bind9 Updates
=============

This document describes the policy for doing micro-release updates of
the bind9 package in Ubuntu releases.

.. _about_bind9:

About Bind9
-----------

`Bind9 <https://www.isc.org/bind/>`__ is a versatile, classic, and
complete name server software.

.. _upstream_release_policy:

Upstream release policy
-----------------------

The `Internet Systems Consortium <https://www.isc.org/>`__ maintains
multiple versions in parallel. According to their `support
policy <https://kb.isc.org/docs/aa-00896>`__, there are four version
types:

-  **Development**: Odd-numbered releases (9.17, 9.19, etc.) are used
   for development for 24 months, and updates are not necissarily
   backwards compatible. After the development period the release is
   re-labeled as the next even number and made into a stable release.
-  **Stable**: Each even-numbered major release (9.16, 9.18, etc.)
   starts here and is supported with feature updates and bug fixes for
   12-18 months. Afterward it becomes an ESV release.
-  **Extended Support Versions (ESV)**: Even-numbered releases marked as
   ESV are given critical fixes and security updates up until four years
   after their initial release date. They are then marked EOL.
-  **Supported Preview**: Not relevant to Ubuntu, but worth mentioning.
   These releases are used to provide early access to feature updates in
   bind9.

Development and stable versions typically have a new minor release every
month, while for ESV this may happen less often. As of writing this
document, 9.19.x is the current development version, 9.18.x is in normal
extended support, and 9.16.x is ESV receiving security fixes.

.. _ubuntu_and_bind9_releases_affected_by_this_mre:

Ubuntu and Bind9 releases affected by this MRE
----------------------------------------------

Currently, these are the Ubuntu releases and the corresponding bind9
package versions affected by this policy:

-  Noble (24.04): bind9 9.18.x
-  Jammy (22.04): bind9 9.18.x
-  Focal (20.04): bind9 9.16.x (Since USN-6909-1 also on 9.18.x)

This MRE should be also applicable to future Ubuntu LTS releases
containing a stable or ESV version of Bind9.

QA
--

.. _upstream_tests:

Upstream tests
~~~~~~~~~~~~~~

Bind9 contains a set of build and code tests which are executed for each
commit and release via `GitHub
Actions <https://github.com/isc-projects/bind9/actions>`__.
`CodeQL <https://codeql.github.com/>`__ and
`SonarCloud <https://www.sonarsource.com/products/sonarcloud/>`__ are
used to build bind9 and check for vulnerabilities in the code. Upstream
tests and additional builds are also run via `GitLab
pipelines <https://gitlab.isc.org/isc-projects/bind9/-/pipelines>`__.
The tests are provided in the `tests/
directory <https://gitlab.isc.org/isc-projects/bind9/-/tree/main/tests>`__.

Autopkgtest
-----------

The package contains three DEP-8 tests:

-  simpletest - Confirms the installation worked by using the default
   bind9 configuration to query localhost with dig
-  zonetest - In depth test of DNS zone, creating a local domain then
   confirming a query against the local domain with dig is successful
-  validation - This test is marked as flaky and will always fail using
   Ubuntu's autopkgtest infrastructure since it requires an internet
   connection to run. This test is inherited from Debian.

simpletest and zonetest are extensive enough to catch major errors,
especially when it comes to packaging bind9 with Ubuntu and using dig /
bind9 internally.

.. _avoiding_breaking_changes:

Avoiding Breaking Changes
-------------------------

Since upstream has shown that they are occasionally willing to make
changes to their stable releases that break backwards compatibility,
additional due diligence must be done to avoid causing problems for
Ubuntu users. Prior to merging, version release notes and announcements
from upstream must be checked for these changes. If any do show up, they
must be noted in the bug report. Also, prior to uploading, discuss with
the SRU team as to how to handle the changes. This may result in a
reversion of the backwards-incompatible changes through patches.

An example of this situation is a change made by upstream in 9.18.7 and
9.16.33 that broke configuration compatibility for the sake of security.
This change was noted in two places: `their
docs <https://kb.isc.org/docs/dnssec-policy-requires-dynamic-dns-or-inline-signing>`__
which note when and why this was done, and `their release
notes <https://bind9.readthedocs.io/en/v9_18_12/notes.html#notes-for-bind-9-18-7>`__
in the second point of the Feature Changes section.

Process
-------

As with regular MREs, the aim here is to offer bugfixes and security
fixes to all supported releases. This process will only allow updates
from microreleases that update the final digit of the bind9 version
number for each Ubuntu version (e.g. 9.18.x -> 9.18.x+1 and not 9.18.x
-> 9.20.y).

To do this we will:

#. File a bug to cover the upgrade.

| ``   * Add tasks to all Ubuntu releases which will be updated.``
| ``   * Add a link to the upstream changelog and list major changes.``
| ``   * Look through changelogs and announcements to check for backwards-incompatible changes, and note them down.``
| ``2. Make sure the development release contains the fixes that will be added. In general this should be the case as long as it is up to date with its associated release version.``
| ``3. Setup merge with new versions, reverting any backwards-incompatible changes that must be avoided in released versions of Ubuntu. ``
| ``4. Run autopkgtest on all supported architectures.``
| ``5. Run autopkgtest on reverse-dependencies against the new release.``
| ``6. Upload the microrelease to the SRU queue and wait until it is approved.``
| ``7. Watch the migration page until it lands in the -updates pocket. Fix any regression that might appear during the process.``

.. _sru_template:

SRU template
~~~~~~~~~~~~

::

   This bug tracks an update for the bind9 package, moving to versions:

   * [Release codename]  ([Release version]): bind9 [Bind9 version - highest possible number on the last digit]
   * [...]

   These updates include bug fixes following the SRU policy exception defined at https://wiki.ubuntu.com/Bind9Updates.

   [Upstream changes]

   TODO: List updates, CVE fixes, and relevant bug fixes
   TODO: Add a link to the upstream changelog

   TODO: Specifically note any backwards-incompatible changes noted by upstream and their announcements/release notes.

   [Test Plan]

   TODO: Check DEP-8 and reverse-depends DEP-8 tests pass
   TODO: if there are any non passing tests - explain why that is ok in this case
   TODO: add results of an autopkgtest run against all the new versions

   [Regression Potential]

   Upstream has an extensive build and integration test suite. So regressions would likely arise from a change in interaction with Ubuntu-specific integrations.

   TODO: consider any other regression potential specific to the version being
   updated and list if any.

.. _log_of_regressions:

Log of regressions
------------------

Here is a log of known regressions.

.. _introduced_by_security_update_httpsubuntu.comsecuritynoticesusn_6909_1:

Introduced by security update https://ubuntu.com/security/notices/USN-6909-1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

None reported in Ubuntu yet, but Debian did the same update and got
these regressions reported:

-  segfault:
   https://lists.debian.org/debian-security-announce/2024/msg00146.html,
   https://bugs.debian.org/1077281, https://bugs.debian.org/1074378.
   Ubuntu not affected because we don't link with jemalloc
-  removal of SIG(0) (this removal is the actual CVE fix):
   https://bugs.debian.org/1077653
-  Deprecated options now finally removed:
   https://bugs.debian.org/1077512. Reporter seems to be using ubuntu
   packages, though.
-  `Missing binaries, new DNSSEC
   checks <https://bugs.launchpad.net/ubuntu/+source/bind9/+bug/2075542>`__:
   user reported broken sysadmin scripts due to missing binaries, and
   broken DNSSEC config due to new checks

Upstream published this guide to help with the transition from 9.16 to
9.18:
https://kb.isc.org/docs/changes-to-be-aware-of-when-moving-from-bind-916-to-918

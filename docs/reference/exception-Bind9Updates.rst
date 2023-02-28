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

As of writing this document, 9.19.x is the current development version,
9.18.x is in normal extended support, and 9.16.x is ESV receiving
security fixes.

.. _ubuntu_and_bind9_releases_affected_by_this_mre:

Ubuntu and Bind9 releases affected by this MRE
----------------------------------------------

Currently, these are the Ubuntu releases and the corresponding bind9
package versions affected by this policy:

-  Kinetic (22.10): bind9 9.18.x
-  Jammy (22.04): bind9 9.18.x
-  Focal (20.04): bind9 9.16.x

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

Process
-------

As with regular MREs, the aim here is to offer bugfixes and security
fixes to all supported releases.

To do this we will:

#. File a bug to cover the upgrade.

| ``   * Add tasks to all Ubuntu releases which will be updated.``
| ``   * Add a link to the upstream changelog and list major changes.``
| ``2. Make sure the development release contains the fixes that will be added. In general this should be the case as long as it is up to date with its associated release version.``
| ``3. Run autopkgtest on all supported architectures.``
| ``4. Run autopkgtest on reverse-dependencies against the new release.``
| ``4. Upload the microrelease to the SRU queue and wait until it is approved.``
| ``5. Watch the migration page until it lands in the -updates pocket. Fix any regression that might appear during the process.``

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

   [Test Plan]

   TODO: Check DEP-8 and reverse-depends DEP-8 tests pass
   TODO: if there are any non passing tests - explain why that is ok in this case
   TODO: add results of an autopkgtest run against all the new versions

   [Regression Potential]

   Upstream has an extensive build and integration test suite. So regressions would likely arise from a change in interaction with Ubuntu-specific integrations.

   TODO: consider any other regression potential specific to the version being
   updated and list if any.

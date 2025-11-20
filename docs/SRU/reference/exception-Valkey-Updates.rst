.. _reference-exception-ValkeyUpdates:

.. _valkey_updates:

Valkey Updates
===============

This document describes the policy for doing micro-release updates of
the Valkey package in Ubuntu stable releases.

.. _about_valkey:

About Valkey
------------

`Valkey <https://valkey.io/>`__ is an open source VPN high-performance
key/value datastore that supports a variety of workloads such as caching,
message queues, and can act as a primary database.


Valkey Upstream release policy
-------------------------------

The Valkey community maintains multiple versions in parallel. According
to their `supported versions
documentation <https://valkey.io/topics/releases/>`__:

-  The latest stable release is always fully supported and maintained.
-  All latest minor version of each major version will have extended
   security support for 5 years.
-  Every minor release will be fully supported with bug fixes for 3 years.

When it comes to updates in Ubuntu, the latest micro release for each
corresponding minor release should be considered for SRU. When security updates
are included in a new micro release, the update should also be added to the
security pocket through a no-change rebuild after releasing to the updates
pocket.

.. _ubuntu_and_valkey_releases_affected_by_this_mre:

Ubuntu and Valkey releases affected by this MRE
------------------------------------------------

Currently, these are the Ubuntu releases and the corresponding Valkey
package versions affected by this policy:

-  Resolute (26.04): Valkey 9.0.x (projected)
-  Questing (25.10): Valkey 8.1.x
-  Plucky (25.04): Valkey 8.0.x
-  Noble (24.04): Valkey 7.2.x

QA
--

Upstream tests
^^^^^^^^^^^^^^

Valkey contains a set of build and regression tests which are executed
for each commit and release via `GitHub
Actions <https://github.com/valkey-io/valkey/actions>`__. Upstream tests
are provided in the `tests/
directory <https://github.com/valkey-io/valkey/tree/unstable/tests>`__.

Autopkgtest
^^^^^^^^^^^

The package contains five DEP-8 tests in every supported Ubuntu release, along
with one extra in noble and plucky:

-  valkey-cli - Smoke test to confirm valkey-cli can show info and version.
-  benchmark - Run the benchmark command and display its info.
-  valkey-check-aof - Smoke test to confirm the check-aof command runs.
-  valkey-check-rdb - Run a synchronous save then confirm the check-rdb command
   runs successfully.
-  cjson - Confirm the cjson module can be loaded and used.
-  migrate-from-redis - (Noble and Plucky only) Confirm that using the
   valkey-redis-compat package to migrate data from a Redis server succeeds by
   default.

These tests are extensive enough to catch major errors when it comes to
the integration of Valkey with Ubuntu, specifically when starting valkey-server
and running standard cli commands, along with issues in setup and compatibility
with Redis if relevant.

.. _valkey_avoiding_breaking_changes:

Avoiding Breaking Changes
-------------------------

In order to confirm that upstream continues to match our expectation of
backwards compatibility in micro releases, additional due diligence must be
done by whoever prepares the SRU. Prior to merging, version release notes and
announcements from upstream must be checked for backwards-incompatible changes.
Any change that may fit this description must be noted in the bug report. Also,
prior to uploading, discuss with the SRU team as to how to handle the changes.
This may result in a reversion of the backwards-incompatible changes through
patches.

Valkey Update Process
----------------------

As with regular MREs, the aim here is to offer bugfixes and security
fixes to all supported releases.

To do this we will:

#. File a bug to cover the upgrade.

   -  Add tasks to all Ubuntu releases which will be updated.
   -  Add a link to the upstream changelog and list major changes.
   -  Look through changelogs and announcements to check for backwards-incompatible changes, and note them down.

#. Make sure the development release contains the fixes that will be added. In general this should be the case as long as it is up to date with its associated micro release version.
#. Setup merges with each new version.
#. Run autopkgtest on all supported architectures.
#. Upload the microrelease to the SRU queue and wait until it is approved.
#. Watch the migration page until it lands in the -updates pocket. Fix any regression that might appear during the process.


Valkey SRU template
--------------------

.. code-block:: text

   This bug tracks an update for the Valkey package, moving to versions:

   * [Release codename]  ([Release version]): Valkey [Valkey version - highest possible number on the last digit]
   * [...]

   These updates include bug fixes following the SRU special case documentation at https://documentation.ubuntu.com/sru/en/latest/reference/exception-Valkey-Updates

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

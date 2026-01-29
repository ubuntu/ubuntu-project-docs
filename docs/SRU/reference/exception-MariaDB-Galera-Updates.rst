.. _reference-exception-MariaDB-Galera-Updates:

MariaDB and Galera Updates
==========================

This document describes the policy for doing microrelease updates of the MariaDB
and Galera packages in Ubuntu releases.

.. _about_mariadb_galera:

About MariaDB and Galera
------------------------

MariaDB is a fork of the MySQL relational database management system. It started
in 2009 by the original developers of MySQL around the time of Oracle's
acquisition of Sun Microsystems. The open source community around MariaDB is
supported by the MariaDB Foundation, while multiple companies offer commercial
services, with the MariaDB Corporation being the most prominent.

Galera Cluster is a synchronous multi-master cluster technology for MariaDB that
provides high availability, no data loss, and scalability for growth. It
operates as a plugin for MariaDB and enables the creation of a true multi-master
cluster where all nodes contain the same data.

In Ubuntu, both MariaDB and Galera are frequently used components of the server
infrastructure stack, providing database functionality for numerous applications
and services. For the past decade, Debian releases have shipped MariaDB instead
of MySQL.

.. _mariadb_upstream_release_policy:

Upstream release policy
^^^^^^^^^^^^^^^^^^^^^^^

The MariaDB Foundation follows a specific versioning scheme for releases:

* 10.3, 10.6, 10.11, 11.4, 11.8: Long-term supported new major releases
* 10.6.18, 10.6.19, 10.6.20: Minor maintenance releases with only critical bug fixes and security fixes

Galera Cluster follows a similar versioning policy with versions that correspond
to the MariaDB releases they support:

* 25.3, 26.4: Long-term supported new major releases
* 25.3.34, 25.3.27, 26.4.20: Minor maintenance releases with only critical bug fixes and security fixes

.. _mariadb_ubuntu_releases_affected:

Ubuntu releases affected by this exception
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently, these are the Ubuntu releases and the corresponding MariaDB and
Galera package versions affected by this policy:

* Plucky (25.04): MariaDB (src:mariadb) 11.4.x, Galera (src:galera-4) 26.4.x
* Noble (24.04): MariaDB (src:mariadb) 10.11.x, Galera (src:galera-4) 26.4.x
* Jammy (22.04): MariaDB (src:mariadb-10.6) 10.6.x, Galera (src:galera-4) 26.4.x
* Focal (20.04): MariaDB (src:mariadb-10.3) 10.3.x, Galera (src:galera-4) 26.4.x

.. _mariadb_history_track_record:

History and track record
^^^^^^^^^^^^^^^^^^^^^^^^^

Ubuntu has maintained MariaDB packages since the transition from MySQL, which
began with Ubuntu 14.04 LTS. Since then, microrelease updates have been
regularly incorporated into Ubuntu's supported releases.

Historical data shows that microrelease updates have been highly reliable, with
only a small number of regressions reported over the years. These were primarily
related to specific edge cases and were quickly addressed in subsequent updates.

* https://launchpad.net/ubuntu/+source/mariadb/+publishinghistory
* https://launchpad.net/ubuntu/+source/mariadb-10.6/+publishinghistory
* https://launchpad.net/ubuntu/+source/mariadb-10.5/+publishinghistory
* https://launchpad.net/ubuntu/+source/mariadb-10.3/+publishinghistory
* https://launchpad.net/ubuntu/+source/mariadb-10.1/+publishinghistory
* https://launchpad.net/ubuntu/+source/mariadb-10.0/+publishinghistory
* https://launchpad.net/ubuntu/+source/mariadb-5.5/+publishinghistory

* https://launchpad.net/ubuntu/+source/galera-4/+publishinghistory
* https://launchpad.net/ubuntu/+source/galera-3/+publishinghistory

.. _mariadb_quality_assurance:

Quality assurance
-----------------

The process for integrating microrelease updates into Ubuntu involves several
layers of quality assurance testing to ensure stability and compatibility.

Upstream tests
^^^^^^^^^^^^^^

MariaDB's upstream testing at https://buildbot.mariadb.org/ includes:

* Comprehensive SQL test suite with more than 5,000 test cases
* Stress testing under various workloads
* Replication testing across versions
* Platform-specific tests for different operating systems

Debian tests
^^^^^^^^^^^^

The MariaDB packaging in Debian utilizes all the regular Debian QA facilities
such as autopkgtests, Lintian, cross-builds etc. Additionally, it has an
extended Salsa CI pipeline testing various upgrade and compatibility issues that
are specific for Debian and Ubuntu.

For details see:

* https://salsa.debian.org/mariadb-team/mariadb-server/-/pipelines
* https://salsa.debian.org/mariadb-team/galera-4/-/pipelines
* https://debconf19.debconf.org/talks/63-how-mariadb-packaging-uses-salsa-ci-to-ensure-smooth-upgrades-and-avoid-regressions/
* https://optimizedbyotto.com/post/gitlab-mariadb-debian/

Uploads of all new upstream microreleases are done first to Debian unstable and
prepared for Debian stable releases, which allows Ubuntu releases to benefit
from all the additional exposure in Debian for higher confidence that there are
no regressions.

Ubuntu tests
^^^^^^^^^^^^

* All new releases are always vetted at https://launchpad.net/~mysql-ubuntu/ for compatibility with each target release
* Additional verification steps are documented at https://wiki.ubuntu.com/SecurityTeam/PublicationNotes#Sponsoring_MariaDB_Security_Updates

The Ubuntu microreleases are also manually reviewed in Merge Requests, see
example at
https://salsa.debian.org/mariadb-team/mariadb-server/-/merge_requests/109

.. _2014_mre_exception:

2014 MRE exception
^^^^^^^^^^^^^^^^^^

A MRE exception was granted in 2014:

* https://lists.ubuntu.com/archives/technical-board/2014-April/001927.html
* https://lists.ubuntu.com/archives/technical-board/2014-May/001941.html

However, it was not recorded later when
https://wiki.ubuntu.com/StableReleaseUpdates#Documentation_for_Special_Cases was
created.

.. _mariadb_security_uploads:

Security uploads
^^^^^^^^^^^^^^^^

In past years, all microreleases have been uploaded on the basis of open CVEs,
sponsored by the security team. MariaDB is a large piece of software and
typically has at least 2-5 CVEs per year. See
https://mariadb.com/kb/en/security/ for details. Note that about 10% of the CVEs
in Oracle MySQL apply for MariaDB too due to the shared historical code base.

In both MariaDB and MySQL the CVEs are always resolved by publishing the entire
upstream maintenance release. Doing security-only updates with cherry-picked CVE
fixes without the whole upstream maintenance release is not feasible due to the
complexity of the software, and additionally the long-term maintenance of a
custom fork that gets 4-5 updates per year for multiple years would require
increase the risk level far above just sticking to the policy of following
upstream releases.

MariaDB's security status has been improving over time, and there are now
stable releases made that do not fix any CVEs and so do not need to go to
``-security``. This documentation is to clarify the process for those releases;
stable releases which fix CVEs will go to ``-security`` as normal.

.. _mariadb_process:

Process
-------

As with regular SRU exceptions, the aim here is to offer bugfixes and security
fixes to all supported releases.

To do this we will:

1. File a bug to cover the upgrade.

   * Add tasks to all Ubuntu releases for the versions of MariaDB and/or Galera which will be updated.
   * Add a link to the upstream changelogs and list major changes.

2. Make sure the development release contains the fixes that will be added. In general this should be the case as long as it is up to date with its associated release version.

3. Run autopkgtest on all supported architectures.

4. Upload the new releases to the SRU queue and wait until it is approved.

5. Watch the migration page until it lands in the -updates pocket. Fix any regression that might appear during the process.

.. _mariadb_sru_template:

SRU template
^^^^^^^^^^^^

::

    This bug tracks an update for the MariaDB and Galera packages, moving to versions:

    * [Release codename] ([Release version]): MariaDB [MariaDB version - highest possible number on the last digit]
    * [Release codename] ([Release version]): Galera [Galera version - highest possible number on the last digit]
    * [...]

    These updates include bug fixes following the SRU special case documentation at
    https://wiki.ubuntu.com/MariaDB-and-Galera-updates.

    [Upstream changes]

    TODO: List updates, CVE fixes, and relevant bug fixes
    TODO: Add a link to the upstream changelog

    [Test Plan]

    TODO: Check that builds pass on all Ubuntu architectures
    TODO: Check that the full build passed, including checks for file locations,
          symbols file and ABI stability and the post-build upstream tests
    TODO: Check DEP-8 (autopkgtests) pass
    TODO: If that the same update in Debian unstable and Ubuntu devel passed all
          QA systems, including DEP-8 (autopkgtests) for reverse dependencies
    TODO: if there are any non passing tests - explain why that is ok in this case
    TODO: add results of an autopkgtest run against all the new versions

    TODO: If available, check status of Debian Salsa pipelines

    [Regression Potential]

    The build incorporates an extensive build and integration test suite. The
    upstream also releases their own .deb packages and they too run extensive
    tests on them. Regressions would likely arise from a change in interaction
    with Ubuntu-specific integrations.

    Example of ABI regression that upstream missed but that was caught in the
    .deb builds: https://github.com/mariadb-corporation/mariadb-connector-c/pull/219

    TODO: consider any other regression potential specific to the version being
    updated and list if any.

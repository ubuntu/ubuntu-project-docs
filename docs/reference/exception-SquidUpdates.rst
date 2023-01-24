.. _squid_updates:

Squid Updates
=============

This document describes the policy for doing micro-release updates of
the Squid package in Ubuntu LTS releases.

.. _about_squid:

About Squid
-----------

`Squid <http://www.squid-cache.org>`__ is a high-performance proxy
caching server for web clients, supporting

``FTP, gopher, ICY and HTTP data objects.``

.. _upstream_release_policy:

Upstream release policy
-----------------------

As described in
http://wiki.squid-cache.org/DeveloperResources/ReleaseProcess and
discussed in the upstream mailing list at
http://lists.squid-cache.org/pipermail/squid-dev/2015-March/001853.html,
starting in Squid 4, Squid follows a Major.Point release policy where
the Point releases could be considered new upstream microreleases as per
https://wiki.ubuntu.com/StableReleaseUpdates#New_upstream_microreleases.

This has been recently confirmed through the squid users mailing list in
http://lists.squid-cache.org/pipermail/squid-users/2023-January/025586.html

New releases are cut when one of the following criteria is met:

-  At least one new major, critical, or blocker bug is fixed.
-  OR, 4 or more less important bugs have been fixed.
-  OR, 100 lines or more have been changed in the code.

**Releases in the X.Y.Z format should be ignored since these are
considered beta releases**.

.. _ubuntu_and_squid_releases_affected_by_this_mre:

Ubuntu and Squid releases affected by this MRE
----------------------------------------------

Currently, these are the Ubuntu releases and the corresponding Squid
package versions affected by this policy:

-  Jammy (22.04): Squid 5.x
-  Focal (20.04): Squid 4.x

This MRE should be also applicable to future Ubuntu LTS releases as long
as the Squid release policy is not changed regarding the formats and
commitments described above.

QA
--

.. _upstream_tests:

Upstream tests
~~~~~~~~~~~~~~

Squid contains an extensive testsuite that is executed during the Ubuntu
package build time on all supported architectures.

.. _upstream_ci:

Upstream CI
~~~~~~~~~~~

BuildFarm
^^^^^^^^^

.. _github_actions:

GitHub Actions
^^^^^^^^^^^^^^

Autopkgtest
~~~~~~~~~~~

The package contains two of DEP-8 tests. The first runs the upstream
test suite on the installed package. The second runs simple checks to
ensure the proxy server is up, running and responding to simple
requests.

Process
-------

.. _sru_template:

SRU template
~~~~~~~~~~~~

.. _squid_updates:

Squid Updates
=============

This document describes the policy for doing micro-release updates of
the Squid package in Ubuntu LTS releases.

.. _about_squid:

About Squid
-----------

`Squid <http://www.squid-cache.org>`__ is a high-performance proxy
caching server for web clients, supporting FTP, gopher, ICY and HTTP
data objects.

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

The upstream project performs builds for different OSes and platforms
from different branches in a continuous manner. This process is
described in http://wiki.squid-cache.org/BuildFarm and is performed in
Squid's own Jnekins instance at http://build.squid-cache.org/.

.. _github_actions:

GitHub Actions
^^^^^^^^^^^^^^

All changes to the upstream code base are tested through GitHub Actions
before being incorporated. This is done as per
https://github.com/squid-cache/squid/blob/master/.github/workflows/default.yaml.
Test results are available at
https://github.com/squid-cache/squid/actions.

Autopkgtest
~~~~~~~~~~~

The package contains two of DEP-8 tests. The first runs the upstream
test suite on the installed package. The second runs simple checks to
ensure the proxy server is up, running and responding to simple
requests.

Process
-------

As with regular MREs, we aim to offer bug and security fixes to all
supported releases. This will be done by

#. Filing a bug to cover the MRE (e.g. "New upstream microreleases 4.x,
   5.x") with one task for each Ubuntu release which will receive a
   Squid update. This bug should follow the SRU template described
   below.

``2. Uploading the package to the proposed pocket (if it's a non-security upload), and, once approved, perform all needed verification steps and keep an eye on the excuses page to investigate any DEP8 failures that may occur. ``

.. _sru_template:

SRU template
~~~~~~~~~~~~

This bug tracks the following MRE updates for the Squid package:

-  [Release codename] ([Release version]): Squid [Squid version]
-  [...]

This update includes bugfixes following the SRU policy exception defined
at https://wiki.ubuntu.com/SquidUpdates.

[Upstream changes]

TODO: Add a link to the upstream changelog

TODO: List the major changes introduced in this release

[Test Plan]

TODO: link the build log containing all tests being executed

TODO-A: All tests are passing during build time, as shown in the build
log.

TODO-B: list each non passing test, explain why that is ok in this case

TODO: add results of local autopkgtest run against all the new Squid
versions being uploaded here

[Regression Potential]

Upstream tests are always executed during build-time.

Squid does not have many reverse dependencies. However, any upgrade is a
risk to introduce breakage to other packages. Whenever a test failure is
detected, either in build time or in autopkgtests, we will be on top of
it and make sure it doesn't affect existing users.

TODO: consider any other regression potential specific to the version
being updated and list them here if any.

[Other Info]

TODO-A: No CVEs are being addressed this time. Therefore, this should go
through the updates pockets.

TODO-B: CVEs TBD are being addressed by these updates. Therefore, this
update should go through the security pocket.

TODO: list previous MREs for this package, if any.

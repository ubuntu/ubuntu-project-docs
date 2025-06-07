.. _haproxy_updates:

HAProxy Updates
===============

This document describes the policy for doing micro-release updates of
the HAProxy package in Ubuntu LTS releases.

.. _about_haproxy:

About HAProxy
-------------

`HAProxy <https://www.haproxy.org>`__ is a free, very fast and reliable
reverse-proxy offering high availability, load balancing, and proxying
for TCP and HTTP-based applications.

.. _upstream_release_policy:

Upstream release policy
-----------------------

The HAProxy core team maintains multiple versions in parallel. Since
version 1.8, two major version are emitted every year. The upstream
maintainers backport fixes to all supported releases, being careful to
not break anything, and they do recommend to stay updated to the highest
possible number on the last digit of the version where only bug fixes
are present (*Description* section of its `home
page <http://www.haproxy.org>`__). For example, in Jammy, HAProxy
version 2.4.14 is shipped, we should keep it updated to the the highest
last digit which is 2.4.17 right now (at the moment this document is
written).

Versions where the second digit is an even number are called "LTS" and
those are maintained for 5 years after the release (those are released
usually between May and June). The ones with odd numbers are called
"stable" and those are maintained between 12 and 18 months
(*Description* section of its `home page <http://www.haproxy.org>`__).
In Ubuntu, we took care to ship only LTS releases.

.. _ubuntu_and_haproxy_releases_affected_by_this_mre:

Ubuntu and HAProxy releases affected by this MRE
------------------------------------------------

Currently, these are the Ubuntu releases and the corresponding HAProxy
package versions affected by this policy:

-  Jammy (22.04): HAProxy 2.4.x (until 2026-Q2)
-  Focal (20.04): HAProxy 2.0.x (critical fixes only until 2024-Q2)
-  Bionic (18.04): HAProxy 1.8.x (critical fixes only until 2022-Q4)

This MRE should be also applicable to future Ubuntu LTS releases
containing a HAProxy LTS version.

QA
--

.. _upstream_tests:

Upstream tests
~~~~~~~~~~~~~~

HAProxy contains a set a functional and regression tests which are
executed by upstream via Github Actions. For the regression tests,
upstream uses an external project called
`VTest <https://github.com/vtest/VTest/>`__ to run them (this was
formerly known as Varnishtest, used by Varnish, and now it is adapted
for HAProxy).

The mentioned Github Actions test the following:

-  Build/Compilation
-  Regression tests using VTest

   -  

      -  Use gcc and clang (ASAN)
      -  Use multiple SSL libraries (openssl, libressl)
      -  Different compression configuration

Moreover, those things are also tested on other operating systems. More
details, about how this is implemented can be found in
`.github/workflows <https://github.com/haproxy/haproxy/tree/master/.github/workflows>`__
directory.

There is also a `Travis CI
pipeline <https://github.com/haproxy/haproxy/blob/master/.travis.yml>`__
which builds HAProxy and runs the regression tests in non-amd64
architecture, they are:

-  ppc64el
-  arm64
-  arm64-graviton2
-  s390x

Unfortunately, all those regression tests are not executed during
package build time. I do believe the Debian maintainer considers the
upstream testing good enough and did not bother to package for instance
VTest as a required test dependency. Packaging VTest is something that
would require some coordination with upstream since it has no releases
and according to its README file there is no plan for that.

Autopkgtest
-----------

The package contains a couple of DEP-8 tests, checking the CLI usage and
also if the proxy feature is working. It is not too extensive and
complete as the upstream testing but it would catch some obvious
regressions. In order to improve this and also run upstream tests we
would need to package VTest which was commented above.

Process
-------

As with regular MREs, the aim here is to offer bugfixes and security
fixes to all supported releases.

To do this we will:

#. File (or find, our users are quite proactive about wanting this) a
   bug to cover the upgrade.

| ``   * Add tasks to all Ubuntu releases which will be updated.``
| ``   * Add a link to the upstream changelog.``
| ``   * Add links to the upstream CI pipelines demonstrating everything is good.``
| ``2. Make sure the development release already contains those fixes. Ideally, HAProxy in the Ubuntu development release should have the highest possible number on the last digit of the version.``
| ``3. Upload the microrelease to the SRU queue of the supported Ubuntu releases affected by this update and wait until the SRU team approve it.``
| ``4. Watch the migration page until it lands in the -updates pocket. Fix any regression that might appear during the process.``

.. _sru_template:

SRU template
~~~~~~~~~~~~

::

   This bug tracks an update for the HAProxy package in the following Ubuntu
   releases to the versions below:

   * [Release codename]  ([Release version]): HAProxy [HAProxy version - highest possible number on the last digit]
   * [Release codename]  ([Release version]): HAProxy [HAProxy version - highest possible number on the last digit]
   * [Release codename]  ([Release version]): HAProxy [HAProxy version - highest possible number on the last digit]

   These updates include bugfixes only following the SRU policy exception defined
   at https://wiki.ubuntu.com/HAProxyUpdates.

   [Upstream changes]

   TODO: Add a link to the upstream changelog
   TODO: Highlight any important bug fix

   [Test Plan]

   TODO: link to the upstream CI pipelines demonstrating all tests are passing
   TODO: if there are any non passing tests - explain why that is ok in this case
   TODO: add results of a local autopkgtest run against all the new HAProxy versions

   [Regression Potential]

   HAProxy itself does not have many reverse dependencies, however, any upgrade is
   a risk to introduce some breakage to other packages. Whenever a test failure is
   detected, we will be on top of it and make sure it doesn't affect existing
   users.

   TODO: consider any other regression potential specific to the version being
   updated and list if any.

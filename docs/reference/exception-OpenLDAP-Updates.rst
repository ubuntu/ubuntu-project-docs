.. _reference-exception-OpenLDAPUpdates:

OpenLDAP Updates
================

This document describes the policy for doing microrelease updates of the
OpenLDAP package in Ubuntu LTS releases. The specific Ubuntu LTS
releases affected by this policy are listed below.

.. _about_openldap:

About OpenLDAP
--------------

`OpenLDAP <https://www.openldap.org>`__ is a Free implementation of the
Lightweight Directory Access Protocol (LDAP).


Upstream release policy
-----------------------

After a long time releasing major updates only in the 2.4.x series, its
community has revisited their release strategy in 2022 and decided to
provide both long-term (LTS) and short-term releases (Feature Releases).
You can read more about it
`here <https://www.symas.com/post/openldap-project-release-maintenance-policy>`__.

In summary, their LTS releases will be supported for 5 years and will be
released approximately every 3 years. These are the releases this MRE
document applies to; we don't intend to do MREs for Feature Releases.

.. _ubuntu_and_openldap_releases_affected_by_this_mre:

Ubuntu [and OpenLDAP] releases affected by this MRE
---------------------------------------------------

Currently, all supported **Ubuntu LTS releases** are affected by this policy.

Each supported Ubuntu release with OpenLDAP version `a.b.x` gets stable upstream updates on `x`.

Note this will include non-LTS releases of Ubuntu as needed to satisfy the :ref:`"newer releases" criteria <explanation-newer-releases>`.

Since OpenLDAP releases LTS versions as well, we intend to ship the most recent OpenLDAP LTS release in the next Ubuntu LTS release.


QA
--

Upstream tests
^^^^^^^^^^^^^^

The OpenLDAP software contains an extensive testsuite that is executed
during build time on all supported architectures. These tests exercise
different aspects of the software like remote authentication, slapadd
usage, concurrency, amongst many other things.

Pipelines
^^^^^^^^^

Upstream also makes use of `GitLab
pipelines <https://git.openldap.org/openldap/openldap/-/pipelines>`__ in
order to automate the testing of new commits. At the time of this
writing, these are the `available
pipelines <https://git.openldap.org/openldap/openldap/-/blob/master/.gitlab-ci.yml>`__:

-  ``build-no-threads-no-slapd``
-  ``build-openssl-heimdal-lloadd``
-  ``build-gnutls-mit-standalone-lloadd``

The Ubuntu OpenLDAP package is compiled with GnuTLS support, so the last
one is the most interesting for us. The other 2 pipelines are also
indirectly valuable because they can offer data points for comparison
if/when a regression is detected in the third. Another very important
fact is that these pipelines use Debian stable as their base OS, which
makes the results much more reliable for Ubuntu.

.. _calls_for_testing:

Calls for testing
-----------------

Before every release, upstream publishes calls for testing in their
mailing list. Although not everybody will publicly release their raw
test results, it is common for downstream contributors to help with
this. We intend to step up and also publish test results in order to
make the release more stable.

As an example, some of their calls for testing can be found below:

-  `Testing call for OpenLDAP
   2.6.2 <https://lists.openldap.org/hyperkitty/list/openldap-technical@openldap.org/thread/XDKRUNDBTTODZ65ZBEN2DE3ZNUG3DR6R/>`__
-  `Testing call for OpenLDAP
   2.5.12 <https://lists.openldap.org/hyperkitty/list/openldap-technical@openldap.org/thread/5ZJEOQSVFQBG5TRLAAF6S5M3VRJH5IAV/>`__

Autopkgtests
------------

The Debian/Ubuntu packages also carry autopkgtests. These tests
currently don't exercise many features of the package, but the Server
team is working towards improving them.

There are also several reverse dependencies that implement autopkgtests
which indirectly exercise OpenLDAP's features, like `SSSD's LDAP login
tests <https://git.launchpad.net/ubuntu/+source/sssd/tree/debian/tests>`__,
or Cyrus SASL's `GSSAPI and shared secret mechanisms
tests <https://git.launchpad.net/ubuntu/+source/cyrus-sasl2/tree/debian/tests>`__,
python-bonsai's `SASL DIGEST-MD5
tests <https://git.launchpad.net/ubuntu/+source/python-bonsai/tree/debian/tests>`__
and these will be executed on every microrelease update. These tests
will be very important when determining API/ABI stability across minor
LTS updates, as they have caught such issues in the past.

OpenLDAP Update Process
-----------------------

.. _openldap_preparing_for_the_sru:

Preparing for the SRU
^^^^^^^^^^^^^^^^^^^^^

Before filing an SRU/MRE bug and kickoff the process officially, we need
to perform the following actions:

#. Merge the latest OpenLDAP LTS microrelease into our existing
   package, rebasing whatever delta the package may contain.

#. Upload the resulting package to a PPA, making sure that the build succeeds **and** that there are no autopkgtest regressions introduced.

When everything looks OK, we are ready to start the SRU process.


OpenLDAP Requesting the SRU
^^^^^^^^^^^^^^^^^^^^^^^^^^^

As with regular MREs, the aim here is to offer bugfixes and security
fixes to all supported releases. The SRU will be done using a single bug
instead of individual bug reports for each fix.

We will:

#. File an MRE bug including the rationale for the upgrade. This MRE
   bug will contain references to previous MREs bugs, as well as a
   summary of the important bugfixes present in the new microrelease.
   See the SRU template below for more details on how this bug will
   look like.

#. Once everything is OK, upload the package to the proposed pocket
   (if it's a non-security upload), and, once approved, keep an eye
   on the excuses page and investigate any DEP8 failures.

The UbuntuServer team has been doing MREs for other packages as well
(postgresql, for example). We can use an existing MRE bug as a template
for the OpenLDAP MREs (for example, `bug
#1961127 <https://bugs.launchpad.net/ubuntu/+source/postgresql-12/+bug/1961127>`__).

.. _openldap_testing_and_verification:

Testing and verification
^^^^^^^^^^^^^^^^^^^^^^^^

As explained above, the testing will be done primarily using a PPA, from
which we will also run autopkgtests for all of the reverse dependencies
as well as upstream's testsuite during the package build.

We will also provide a link to upstream's "call for testing" email and
to the !GitLab jobs that were executed when the release was cut.

.. _openldap_sru_template:

OpenLDAP SRU template
^^^^^^^^^^^^^^^^^^^^^

::

   [ Impact ]

   This bug tracks the following MRE updates for the OpenLDAP package:

   * MRE for latest stable OpenLDAP a.b release, a.b.x.

   These updates only include bug fixes, following the SRU policy exception defined at https://documentation.ubuntu.com/sru/en/latest/reference/exception-OpenLDAP-Updates/

   [ Major Changes ]

   TODO: List the major changes if any
   TODO: Link to the announce mail containing all changes on https://lists.openldap.org/hyperkitty/list/openldap-announce@openldap.org/

   [ Test Plan ]

   See https://documentation.ubuntu.com/sru/en/latest/reference/exception-OpenLDAP-Updates/#qa

   1. Upstream gitlab pipeline results: TODO link for release on https://git.openldap.org/openldap/openldap/-/tags

   2. Upstream "call for testing": TODO link to email on https://lists.openldap.org/hyperkitty/list/openldap-technical@openldap.org/

   3. As specified in the MRE page for OpenLDAP, the test plan is to build the package in "-proposed" and make sure that
      (a) all build-time tests pass and
      (b) all autopkgtest runs (from reverse dependencies) also pass.

   * Build log confirming that the build-time testsuite has been performed and completed successfully:
     - TODO link to build log(s)

   * Test results:
     - TODO autopkgtest results and discussion

   [ Where problems could occur ]

   Upstream tests are always executed during build-time.
   There are many reverse dependencies whose dep8 tests depend on OpenLDAP so the coverage is good.
   Nevertheless, there is always a risk for something to break since we are dealing with a microrelease upgrade.
   Whenever a test failure is detected, we will be on top of it and make sure it doesn't affect existing users.

   TODO: consider any other regression potential specific to the version being updated and list if any or list N/A.  OpenLDAP is used as a library by many other projects, so care must be taken when considering how this MRE might affect these dependencies.

   * Current versions in supported releases that got updates:
     - openldap | ``TODO current-version`` | ``$release-pocket`` -updates

   [ Other Info ]

   This is a recurring effort. For reference, here are previous OpenLDAP SRU backports:

   * TODO: bug links to more recent cases of SRU backports for this package

**THIS IS A DRAFT**

This document describes the policy for doing microrelease updates of the
OpenLDAP package in Ubuntu LTS releases. The specific Ubuntu LTS
releases affected by this policy are listed below.

.. _about_openldap:

About OpenLDAP
--------------

`OpenLDAP <https://www.openldap.org>`__ is a Free implementation of the
Lightweight Directory Access Protocol (LDAP).

.. _upstream_release_policy:

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

Currently, these are the Ubuntu releases and the corresponding OpenLDAP
package versions affected by this policy:

-  

   -  **Jammy (22.04)** [**OpenLDAP 2.5.x**]

The OpenLDAP 2.5.x series is upstream's first LTS release, and its
inclusion in Jammy was no coincidence. Newer Ubuntu releases will likely
have non-LTS OpenLDAP releases in them until our next Ubuntu LTS series
is released, when we intend to ship the next OpenLDAP LTS release.

QA
--

.. _upstream_tests:

Upstream tests
~~~~~~~~~~~~~~

The OpenLDAP software contains an extensive testsuite that is executed
during build time on all supported architectures. These tests exercise
different aspects of the software like remote authentication, slapadd
usage, concurrency, amongst many other things.

Pipelines
~~~~~~~~~

Upstream also makes use of `GitLab
pipelines <https://git.openldap.org/openldap/openldap/-/pipelines>`__ in
order to automate the testing of new commits. At the time of this
writing, these are the `available
pipelines <https://git.openldap.org/openldap/openldap/-/blob/master/.gitlab-ci.yml>`__:

-  

   -  ::

         build-no-threads-no-slapd

   -  ::

         build-openssl-heimdal-lloadd

   -  ::

         build-gnutls-mit-standalone-lloadd

The Ubuntu OpenLDAP package is compiled with GnuTLS support, so the last
one is the most interesting for us. The other 2 pipelines are also
indirectly valuable because they can offer data points for comparison
if/when a regression is detected in the third. Another very important
fact is that these pipelines use Debian stable as their base OS, which
makes the results much more reliable for Ubuntu.

.. _calls_for_testing:

Calls for testing
~~~~~~~~~~~~~~~~~

Before every release, upstream publishes calls for testing in their
mailing list. Although not everybody will publicly release their raw
test results, it is common for downstream contributors to help with
this. We intend to step up and also publish test results in order to
make the release more stable.

As an example, some of their calls for testing can be found below:

-  

   -  `Testing call for OpenLDAP
      2.6.2 <https://lists.openldap.org/hyperkitty/list/openldap-technical@openldap.org/thread/XDKRUNDBTTODZ65ZBEN2DE3ZNUG3DR6R/>`__
   -  `Testing call for OpenLDAP
      2.5.12 <https://lists.openldap.org/hyperkitty/list/openldap-technical@openldap.org/thread/5ZJEOQSVFQBG5TRLAAF6S5M3VRJH5IAV/>`__

Autopkgtests
~~~~~~~~~~~~

The Debian/Ubuntu packages also carry autopkgtests. These tests
currently don't exercise many features of the package, but the Server
team is working towards improving them.

+There are also several reverse dependencies that implement autopkgtests
which indirectly exercise OpenLDAP's features, like `SSSD's LDAP login
tests <https://git.launchpad.net/ubuntu/+source/sssd/tree/debian/tests>`__,
or Cyrus SASL's `GSSAPI and shared secret mechanisms
tests <https://git.launchpad.net/ubuntu/+source/cyrus-sasl2/tree/debian/tests>`__,
python-bonsai's `SASL DIGEST-MD5
tests <https://git.launchpad.net/ubuntu/+source/python-bonsai/tree/debian/tests>`__
and these will be executed on every microrelease update. These tests
will be very important when determining API/ABI stability across minor
LTS updates, as they have caught such issues in the past.

Process
-------

.. _preparing_for_the_sru:

Preparing for the SRU
~~~~~~~~~~~~~~~~~~~~~

Before filing an SRU/MRE bug and kickoff the process officially, we need
to perform the following actions:

#. 

   #. Merge the latest OpenLDAP LTS microrelease into our existing
      package, rebasing whatever delta the package may contain.

`` 2. Upload the resulting package to a bileto PPA, making sure that the build succeeds ``\ **``and``**\ `` that there are no autopkgtest regressions introduced.``

When everything looks OK, we are ready to start the SRU process.

.. _requesting_the_sru:

Requesting the SRU
~~~~~~~~~~~~~~~~~~

As with regular MREs, the aim here is to offer bugfixes and security
fixes to all supported releases. The SRU will be done using a single bug
instead of individual bug reports for each fix.

We will:

#. 

   #. File an MRE bug including the rationale for the upgrade. This MRE
      bug will contain references to previous MREs bugs, as well as a
      summary of the important bugfixes present in the new microrelease.
      See the SRU template below for more details on how this bug will
      look like.

`` 2. Once everything is OK, upload the resulting package to the archive (if it's a non-security upload) and make sure it migrates.``

The UbuntuServer team has been doing MREs for other packages as well
(postgresql, for example). We can use an existing MRE bug as a template
for the OpenLDAP MREs (for example, `bug
#1961127 <https://bugs.launchpad.net/ubuntu/+source/postgresql-12/+bug/1961127>`__).

.. _testing_and_verification:

Testing and verification
~~~~~~~~~~~~~~~~~~~~~~~~

As explained above, the testing will be done primarily using a bileto
ticket, which will also run autopkgtests for all of the reverse
dependencies as well as upstream's testsuite during the package build.

We will also provide a link to upstream's "call for testing" email and
to the !GitLab jobs that were executed when the release was cut.

.. _sru_template:

SRU template
~~~~~~~~~~~~

::

   This bug tracks an update for the OpenLDAP package, version XYZ.

   This update includes bugfixes only following the SRU policy exception defined at https://wiki.ubuntu.com/StableReleaseUpdates/OpenLDAPUpdates.

   [Major Changes]

   TODO: List the major changes
   TODO: list to the announce mail containing all changes

   [Test Plan]

   See https://wiki.ubuntu.com/StableReleaseUpdates/OpenLDAPUpdates#SRU_TestVerify
   TODO: link the build log containing all tests being executed
   TODO: if there are any non passing tests - explain why that is ok in this case.
   TODO: link upstream's "call for testing" email
   TODO: link upstream's gitlab job for this release (look here: https://git.openldap.org/openldap/openldap/-/tags)

   [Regression Potential]

   Upstream tests are always executed during build-time.  There are many reverse dependencies whose dep8 tests depend on OpenLDAP so the coverage is good.  Nevertheless, there is always a risk for something to break since we are dealing with a microrelease upgrade.  Whenever a test failure is detected, we will be on top of it and make sure it doesn't affect existing users.

   TODO: consider any other regression potential specific to the version being updated and list if any or list N/A.  OpenLDAP is used as a library by many other projects, so care must be taken when considering how this MRE might affect these dependencies.

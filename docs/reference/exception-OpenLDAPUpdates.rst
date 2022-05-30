**THIS IS A DRAFT**

This document describes the policy for doing microrelease updates of the
OpenLDAP package in Ubuntu LTS releases. The specific Ubuntu LTS
releases affected by this policy are listed below.

.. _about_openldap:

About OpenLDAP
--------------

`OpenLDAP <https://en.wikipedia.org/wiki/OpenLDAP>`__ is a Free
implementation of the Lightweight Directory Access Protocol (LDAP).

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

Process
-------

As with regular MREs, the aim here is to offer bugfixes and security
fixes to all supported releases.

In order to do this, we will:

#. 

   #. File an MRE bug including the rationale for the upgrade. This MRE
      bug will contain references to previous MREs bugs, as well as a
      summary of the important bugfixes present in the new microrelease.

| `` 2. Merge the latest OpenLDAP LTS microrelease into our existing package, rebasing whatever delta the package may contain.``
| `` 3. Upload the resulting package to a bileto PPA, making sure that the build succeeds ``\ **``and``**\ `` that there are no autopkgtest regressions introduced.``
| `` 4. Once everything is OK, upload the resulting package to the archive (if it's a non-security upload) and babysit it until it migrates.``

The UbuntuServer team has been doing MREs for other packages as well
(postgresql, for example). We can use an existing MRE bug as a template
for the OpenLDAP MREs (for example, `bug
#1961127 <https://bugs.launchpad.net/ubuntu/+source/postgresql-12/+bug/1961127>`__).

QA
--

.. _upstream_tests:

Upstream tests
~~~~~~~~~~~~~~

The OpenLDAP software contains an extensive testsuite that is executed
during build time on all supported architectures. These tests exercise
different aspects of the software like its SASL/GSSAPI integration,
remote authentication, slapadd usage, concurrency, amongst many other
things.

Pipelines
~~~~~~~~~

Upstream also makes use of GitLab pipelines in order to automate the
testing of new commits. At the time of this writing, these are the
pipelines available:

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
mailing list. Although not everybody will publicly release their test
results, it is common for downstream contributors to help with this. We
intend to step up and also publish test results in order to make the
release more stable.

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

There are also several reverse dependencies that implement autopkgtests
which indirectly exercise OpenLDAP's features, and these will be
executed on every microrelease update. These tests will be very
important when determining API/ABI stability across minor LTS updates,
as they have caught such issues in the past.

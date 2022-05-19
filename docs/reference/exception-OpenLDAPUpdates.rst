**THIS IS A DRAFT**

This document describes the policy for doing microrelease updates of the
OpenLDAP package in Ubuntu LTS releases. The specific Ubuntu LTS
releases affected by this policy are listed below.

`OpenLDAP <https://en.wikipedia.org/wiki/OpenLDAP>`__ is a Free
implementation of the Lightweight Directory Access Protocol (LDAP).
After a long time releasing major updates only in the 2.4.x series, its
community has recently revisited their release strategy and decided to
provide both long-term (LTS) and short-term releases (Feature Releases).
You can read more about it
`here <https://www.symas.com/post/openldap-project-release-maintenance-policy>`__.

In summary, their LTS releases will be supported for 5 years and will be
released approximately every 3 years. These are the releases this MRE
document applies to.

.. _affected_ubuntu_releases:

Affected Ubuntu releases
------------------------

Currently, these are the Ubuntu releases and the corresponding OpenLDAP
package versions affected by this policy:

-  

   -  **Jammy (22.04)** [**OpenLDAP 2.5.x**]

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

The server team has been doing MREs for other packages as well
(postgresql, for example). We can use an existing MRE bug as a template
for the OpenLDAP MREs (for example, `bug
#1961127 <https://bugs.launchpad.net/ubuntu/+source/postgresql-12/+bug/1961127>`__).

QA
--

The OpenLDAP software contains an extensive testsuite that is executed
during build time on all supported architectures. The Debian/Ubuntu
packages also carry autopkgtests on top. There are also several reverse
dependencies that implement autopkgtests which indirectly exercise
OpenLDAP's features, and these will be executed on every microrelease
update.

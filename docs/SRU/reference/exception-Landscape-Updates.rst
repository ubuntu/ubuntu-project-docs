.. _reference-exception-landscapeupdates:

Landscape updates
=================

Background
----------

This document describes the policy for updating Landscape Client
packages in stable supported Ubuntu releases. `Landscape Client
<https://github.com/canonical/landscape-client>`__ is a client
application that enables Ubuntu systems to be managed via Canonical's
commercial `Landscape offering <https://ubuntu.com/landscape>`__.
Periodically, new features are introduced to Landscape, and the
client-side implementation and enablement of those features needs to be
released to supported Ubuntu releases.

Upstream release policy
-----------------------

Canonical's `Landscape Team <https://launchpad.net/~landscape>`__
maintains a single release version of Landscape Client, which supports
every supported Ubuntu release.

Landscape Client is released upstream, then released to the Ubuntu
Archive prior to the feature freeze date of each Ubuntu release.

Landscape Client versions follow "Calendar Versioning". Each version
number starts with the release year, a full-stop character, then the
release month. For example, version ``25.08.2`` was released in August
of 2025. Any numbers after the second full-stop character represent
backwards-compatible bug-fixes or security fixes.

Requirements
------------

-  If an update targets one stable release, it must also target all
   subsequent releases (whether interim or LTS) and the development
   release.

-  All releases shall share the same source tree. This is to make the
   process simpler, and so the process documented here assumes this.

-  Any changes to the source tree that are Ubuntu-specific must be
   accounted for as debian patches in ``debian/patches``. These may
   differ for different Ubuntu releases as necessary.

Upstream QA
-----------

Landscape Client contains a set of tests that are executed for each
commit via `Github Actions
<https://github.com/canonical/landscape-client/blob/main/.github/workflows/ci.yml>`__.
These tests are also run at package build time and by autopkgtest, and
the package build will fail if they do not pass. The results of recent
upstream test runs can be viewed in the `Github Actions history <https://github.com/canonical/landscape-client/actions/workflows/ci.yml>`__.

Updates to the tip of `landscape-client:main
<https://github.com/canonical/landscape-client/tree/main>`__ go through
the following checks prior to being merged by a member of the Canonical
Landscape Team:

-  Review and approval by a member of the Canonical Landscape Team who
   is not the author of the change

-  A successful run of unit tests, style and linting tests, and unit
   test code coverage check

Upload Process
--------------

Documentation
-------------

debian/changelog must contain a reference to a Launchpad bug specific to
the SRU. It may contain references to other Launchpad bugs on a
case-by-case basis in order to ensure that those bugs manual test plans
are also considered during testing. Not every change is required to
reference a Launchpad bug. In addition, major changes and new features
must be called out.

Any packaging changes need to be stated, with appropriate test cases
provided.

Any architecture-specific fixes need to be noted, with
architecture-specific test cases provided.

The following types of changes must be called out for explicit SRU
review:

#. How Landscape Client interacts with apt
#. How Landscape Client interacts with systemd
#. How Landscape Client interacts with snapd
#. How Landscape Client interacts with motd
#. How Landscape Client interacts with Ubuntu Advantage Tools/Ubuntu Pro
#. How Landscape Client interacts with Ubuntu Pro for WSL or WSL itself

Review/Sponsoring
-----------------

To minimize the effort required to handle the multiple uploads to each
stable Ubuntu release, All concurrent uploads will be identical to the
upload for the Ubuntu development release, except for the straight
backport version number, changelog changes, and possible minor changes
required to support different Python versions or Ubuntu release
differences. These minor changes will be accounted for in debian patches.

During review, additional tests may be added to the Test Plan for manual
testing.

Verification
------------

The following integration tests will be performed:

-  Testing integration with update-motd to ensure that the message of
   the day does not get adversely affected by landscape-common

   -  Ensure motd is displayed correctly

   -  Ensure that an error in landscape-sysinfo does not break motd

-  Testing integration with currently-supported versions of Landscape
   Server Self-Hosted and Landscape SaaS (landscape.canonical.com).

   -  Ensure that Landscape Client can register with Landscape Server

   -  Ensure that Landscape Client reports system state to Landscape
      Server without errors

   -  Ensure that common Landscape management operations can succeed:
      package installation, package upgrade, snap installation, reboot

-  Testing integration with Ubuntu Advantage Tools

   -  Ensure that ``pro enable landscape`` succeeds in installing and
      enabling Landscape Client

   -  Ensure that, post-registration with Landscape Server, Ubuntu Pro
      entitlement status is reported and appears correct

-  Testing integration with Windows Subsystem for Linux (WSL)

   -  Ensure that enabling Ubuntu Pro for WSL and configuring Landscape
      succeeds in installing and configuring Landscape Client on new WSL
      instances

Successful results of integration testing of the -proposed package must
be provided for at least the following platforms:

-  LXD containers of all LTS and interim releases targeted by the
   SRU

-  The following upgrade tests for both Landscape-registered and
   Landscape-unregistered affected releases targeted by the SRU:

   -  LTS to LTS

   -  LTS to interim release

   -  interim release to interim release

   -  interim release to LTS

If the Test Plan calls for any additional manual testing, such testing
and its results must be documented, usually in the associated bugs
linked in debian/changelog.

SRU Bug Template
----------------

::

   [ Impact ]

   This release introduces bug-fixes and new features for Landscape
   Client, and we would like to make sure all of our supported customers
   have access to these improvements on all releases.

   The most important changes are:
   <create a list that spotlights fixes and features>

   See the changelog entry below for a full list of changes and bug-fixes.

   [ Test Plan ]

   The following development SRU process was followed:
   https://documentation.ubuntu.com/sru/en/latest/reference/exception-LandscapeUpdates

   The Landscape Team will be in charge of attaching the artifacts of
   the appropriate test runs to the bug, and will not mark
   'verification-done' until afterwards.

   Besides the automated test runs, manual tests were executed to verify
   fixes for these bugs:
   <list bugs which required manual testing>

   [ Where problems could occur ]

   <Please replace the text in this section, considering the following

       * Think about what the upload changes in the software. Imagine
         the change is wrong or breaks something else: how would this
         show up?

       * This must '''never''' be "None" or "Low" or entirely an
         argument as to why your upload is low-risk

       * This shows the SRU team that the risks have been considered and
         provides guidance for tests when regression-testing the SRU

   >

   [ Other Info ]

     * Anything else you think is useful to include

     * Anticipate questions from users, SRU, +1 maintenance, security
       teams and the Technical Board and address these questions in
       advance

   [ Changelog ]

   <insert changelog entry>

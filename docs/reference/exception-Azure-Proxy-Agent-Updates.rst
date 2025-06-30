.. _reference-exception-azure-proxy-agent-Updates:

.. _azure-proxy-agent_updates:

azure-proxy-agent Updates
=========================

This document describes the process to update and test new versions of the
azure-proxy-agent package in SRUs.

The azure-proxy-agent package is an Ubuntu distribution of the upstream
Microsoft Guest Proxy Agent that secures access to the Instance MetaData Service
(IMDS) and the Wireserver service. For a detailed list of functionality this
package provides to Ubuntu cloud images, refer to the upstream project page at
GitHub: https://github.com/Azure/GuestProxyAgent.

Cloud platforms evolve at a rate that can't be handled in six-month increments,
and they will often develop features that they would like to be available to
customers who don't want to upgrade from earlier Ubuntu releases. As such,
updating azure-proxy-agent to more recent upstream releases is required within
all Ubuntu releases, so they continue to function properly in their environment.

New versions of azure-proxy-agent can be SRUed into older releases provided the
following process is followed.


azure-proxy-agent QA Process
----------------------------

When a new version of azure-proxy-agent is uploaded to -proposed, the following
will be done:

-  the CPC team will write new automated tests to cover new testable
   functionality (if any) in the new package
-  the automated testing that the CPC team normally runs against Azure images
   before they are published will be run against the -proposed package
-  the Microsoft team maintaining the GuestProxyAgent will be asked to validate

    -  that the new package addresses the issues it is expected to address, and
    -  that the new package passes their internal image validation

In addition, the CPC team does the following testing

-  The new package candidate version is built in devel-proposed and tested on
   the target suite. This will involve one or both of:

  -  Installing the devel-proposed packages on an Azure VM, manually restoring
     the VM to a first boot state and rebooting it,
  -  Generating a fresh image with the devel-proposed package version
     preinstalled and testing that directly

-  Once the manual packaging tests pass successfully and the package requires no
   further changes, it will be marked as such on the tracking bug. On the
   development release, this is done by removing the block-proposed tag.

**If appropriate due to the nature of the changes (embargo on publication), the
steps above may be done in a private PPA prior to landing in devel-proposed.**

The following additional steps also apply for the SRUs to supported releases
once the packages have been accepted into the development release (if
applicable):

-  Once accepted in to -proposed, a test image is built from -proposed, which is
   subjected to the full CPC image tests; this tests for more regressions across
   multiple Azure instance sizes.

.. _pre_sru_test_cases:

Pre-SRU Test Cases
------------------

These are the test cases that all azure-proxy-agent are subjected to before even
getting to SRU:

::

    1.) Launch instance on Azure
    2.) Upgrade azure-proxy-agent (usually from PPA)
    3.) Confirm that "azure-proxy-agent" is running, check journalctl for errors
    4.) Call the IMDS/Wireserver endpoint with an authorized user and verify that the
        request is intercepted by the agent (journalctl) but allowed
    5.) Call the IMDS/Wireserver endpoint with an unauthorized user and verify
        that the request is blocked by the agent

.. _sru_test_cases:

SRU Test Cases
--------------

The following will be executed for representative combinations of supported
architectures, image types and machine sizes:

::

    1.) Build new cloud image with -proposed package
    2.) Boot machine from image
    3.) Run all CPC image tests against machine

.. _azure-proxy-agent_releasing_the_sru:

Releasing the SRU
-----------------

Since the only consumer of the azure-proxy-agent is the Azure cloud, the SRU may
be released without meeting the aging period of 7 days provided all the above
steps have been completed.


azure-proxy-agent SRU Template
------------------------------

::

  == Begin SRU Template ==
  [Impact]
  This release contains both bug-fixes and new
  features and we would like to make sure all of our supported customers have
  access to these improvements. The notable ones are:

  *** <TODO: list any LP: # included>

  See the changelog entry below for a full list of changes and bugs.

  [Test Case]
  The following development and SRU process was followed:
  https://documentation.ubuntu.com/sru/en/latest/reference/exception-azure-proxy-agent-Updates

  The Microsoft team will execute their testsuite, against the azure-proxy-agent
  that is in -proposed. A successful run will be required before the proposed
  azure-proxy-agent can be let into -updates.

  The CPC team will be in charge of attaching a summary of testing to the bug.
  CPC team members will not mark ‘verification-done’ until this has happened.

  == End SRU Template ==

  <TODO: Paste in change log entry>

.. _walinuxagent_updates:

walinuxagent Updates
====================

This document describes the process to update and test new versions of
the walinuxagent package in SRUs.

The walinuxagent package is an Ubuntu distribution of the upstream
Microsoft Azure Linux Agent that manages Linux provisioning, and VM
interaction with the Azure Fabric Controller. For a detailed list of
functionality this package provides to Ubuntu cloud images, refer to the
upstream project page at Git``Hub: https://github.com/Azure/WALinuxAgent

Cloud platforms evolve at a rate that can't be handled in six-month
increments, and they will often develop features that they would like to
be available to customers who don't want to upgrade from earlier Ubuntu
releases. As such, updating walinuxagent to more recent upstream
releases is required within all Ubuntu releases, so they continue to
function properly in their environment.

New versions of walinuxagent can be SRU'd in to older releases provided
the following process is followed.

.. _qa_process:

QA Process
----------

When a new version of walinuxagent is uploaded to -proposed, the
following will be done:

-  the CPC team will write new automated tests to cover new testable
   functionality (if any) in the new package
-  the automated testing that the CPC team normally runs against Azure
   images before they are published will be run against the -proposed
   package
-  the Microsoft Azure Linux Agent team will be asked to validate

   -  that the new package addresses the issues it is expected to
      address, and
   -  that the new package passes their internal image validation, with
      emphasis on walinuxagent extension support.

In addition, prior to being uploaded to -proposed, the CPC team does the
following testing

-  The new package candidate version is built in a PPA and tested on the
   target suite before being uploaded to the archive at all. This will
   involve one or both of:

   -  Installing the PPA packages on an Azure VM, manually restoring the
      VM to a first boot state and rebooting it,
   -  Generating a fresh image with the PPA package version preinstalled
      and testing that directly

-  Once the manual packaging tests pass successfully and the package
   requires no further changes, it will be uploaded to the archive.
-  Once accepted in to -proposed, a test image is built from -proposed,
   which is subjected to the full CPC image tests; this tests for more
   regressions across multiple Azure instance sizes. This includes tests
   for the following bugs:

   -  `Bug #1479610 regression on dhcp
      configuration <https://bugs.launchpad.net/ubuntu/+source/walinuxagent/+bug/1479610>`__
   -  `Bug #1079897 mangled server identity and access on
      upgrade <https://bugs.launchpad.net/ubuntu/+source/walinuxagent/+bug/1079897>`__
   -  `Bug #1305418 breaks sshd
      configuration <https://bugs.launchpad.net/ubuntu/+source/walinuxagent/+bug/1305418>`__

.. _pre_sru_test_cases:

Pre-SRU Test Cases
~~~~~~~~~~~~~~~~~~

These are the test cases that all walinuxagent are subjected to before
even getting to SRU:

::

   [Test case 1]: Upgrade testing
   1.) Launch instance on Azure
   2.) Upgrade walinuxagent (usually from PPA)
   3.) Confirm that "waagent" is running, check /var/log/waagent.log for errors
   4.) Reboot, repeat step 3
   5.) Remove /var/lib/cloud and /var/lib/waagent (to simulate first boot conditions)
   6.) Reboot, repeat step 3
   7.) Repeat step 5, capture the instance as an image and provision a new instance from it; repeat step 3
     
   [Test Case 2]: New instance
   1.) Build new cloud image with PPA package
   2.) Boot instance
   3.) Confirm that instance provisioned

.. _sru_test_cases:

SRU Test Cases
~~~~~~~~~~~~~~

These are automated tests:

::

   1.) Build new cloud image with -proposed package
   2.) Boot instance
   3.) Confirm that instance provisioned
   4.) Run standard tests and regression tests
   5.) Repeat from step 2 for all other Azure VM Sizes.

.. _sru_template:

SRU Template
------------

::

   == Begin SRU Template ==
   [Impact]
   This release contains both bug-fixes and new features and we would like to
   make sure all of our supported customers have access to these improvements.
   The notable ones are:

   *** <TODO: list any LP: # included>

   See the changelog entry below for a full list of changes and bugs.

   [Test Case]
   The following development and SRU process was followed:
   https://wiki.ubuntu.com/walinuxagentUpdates

   The Microsoft Azure Linux Agent team will execute their testsuite, which
   includes extension testing , against the walinuxagent that is in
   -proposed.  A successful run will be required before the proposed walinuxagent
   can be let into -updates.

   The CPC team will be in charge of attaching a summary of testing to the bug.  CPC team members will not
   mark ‘verification-done’ until this has happened.

   == End SRU Template ==

   <TODO: Paste in change log entry>

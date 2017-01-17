.. _walinuxagent_updates:

walinuxagent Updates
====================

This document describes the process to update and test new versions of
the walinuxagent package in SRUs.

The walinuxagent package is an Ubuntu distribution of the upstream
Microsoft Azure Linux Agent that manages Linux provisioning, and VM
interaction with the Azure Fabric Controller.

It provides the following functionality for Ubuntu cloud image
deployments:

-  Image Provisioning.
-  Networking setup.
-  Kernel setup.
-  Diagnostics setup.
-  SCVMM Deployments
-  VM Extensions Management

For a more detailed list of functionality this package provides to
Ubuntu cloud images, refer to the upstream project page at GitHub:
https://github.com/Azure/WALinuxAgent

.. _sru_verification_process:

SRU Verification Process
------------------------

This is the QA process that proposed walinuxagent packages are subjected
to:

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
------------------

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
--------------

These are automated tests:

::

   1.) Build new cloud image with -purposed package
   2.) Boot instance
   3.) Confirm that instance provisioned
   4.) Run standard tests and regression tests
   5.) Repeat from step 2 for all other Azure VM Sizes.

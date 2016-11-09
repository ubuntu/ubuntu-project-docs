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

For a more detailed list of functionallity this package provides to
Ubuntu cloud images, refer to the upstream project page at GitHub:
https://github.com/Azure/WALinuxAgent

.. _qa_process:

QA Process
----------

This is the QA process that proposed walinuxagent packages are subjected
to:

-  The new package candidate version is built in a PPA and tested on the
   target suite before being uploaded to the archive at all. This will
   involve one or both of:

   -  installing the PPA packages on an Azure VM, manually restoring the
      VM to a first boot state and rebooting it,
   -  generating a fresh image with the PPA package version preinstalled
      and testing that directly

-  Once the manual packaging tests pass successfully and the package
   requires no further changes, it will be uploaded to the archive.
-  Once accepted in to -proposed, a test image is built from -proposed,
   which is subjected to the full CPC image tests; this tests for more
   regressions across multiple Azure instance sizes.

.. _sru_test_cases:

SRU Test Cases
--------------

These are the test cases that all walinuxagent SRUs are subjected to:

::

   [Test case 1]: Upgrade testing
   1.) Launch instance on Azure
   2.) Upgrade walinuxagent from -proposed
   3.) Confirm that "waagent" is running, check /var/log/waagent.log
   4.) Reboot, repeat step 3
   5.) Capture instance and provision new instances; repeat step 3
     
   [Test Case 2]: New instance
   1.) Build new cloud image from -proposed
   2.) Boot instance
   3.) Confirm that instance provisioned

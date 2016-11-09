walinuxagentUpdates
===================

This document describes the process to update and test new versions of
the walinuxagent package in SRUs.

The walinuxagent package is an ubuntu distribution of the upstream
Microsoft Azure Linux Agent that manages Linux provisioning, and VM
interaction with the Azure Fabric Controller.

It provides the following functionality for ubuntu cloud image
deployments:

-  Image Provisioning.
-  Networking setup.
-  Kernel setup.
-  Diagnostics setup.
-  SCVMM Deployments
-  VM Extensions Management

For a more detailed list of functionallity this package provides to
ubuntu cloud images, refer to the upstream project page at github:
https://github.com/Azure/WALinuxAgent

.. _qa_process:

QA Process
----------

This is the mandatory QA process that the proposed walinuxagent packages
have to pass. The following requirements must be met:

-  The new package candidate version is to be placed on a PPA and tested
   manually on the target suite during upstream changes packaging phase.
   This tests include:

   -  Installing the PPA packages on an Azure VM, restore the VM to a
      first boot state and reboot it.
   -  Or might require to generate an image with the PPA package version
      preinstalled and test that directly.

-  Once the manual packaging tests pass succesfully and the package
   seems to require no more changes, a test image is required to be
   generated having the PPA package version preinstalled before CPC
   Cloudimages Automated Testing can be done.
-  CPC Couldimages Automatic Testing will run the test image of target
   suite through a series of tests for all relevant Azure VM sizes.
   Currently those tests include:

   -  **Azure general tests**: CPC default Azure tests
   -  **Ubuntu basic tests**: CPC standard ubuntu tests
   -  **Cloud-init tests**: Cloud-init tests
   -  **Walinuxagent regresion tests**: such as checking `bug
      #1479610 <https://bugs.launchpad.net/ubuntu/+source/walinuxagent/+bug/1479610>`__
      did not regress.

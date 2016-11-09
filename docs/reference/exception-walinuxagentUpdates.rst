walinuxagentUpdates
===================

Package walinuxagent is an ubuntu distribution of upstream Microsoft
Azure Linux Agent that manages Linux provisioning, and VM interaction
with the Azure Fabric Controller. It provides the following
functionality for Linux and FreeBSD IaaS deployments:

**Image Provisioning**

-  Creation of a user account

-  Configuring SSH authentication types

-  Deployment of SSH public keys and key pairs

-  Setting the host name

-  Publishing the host name to the platform DNS

-  Reporting SSH host key fingerprint to the platform

-  Resource Disk Management

-  Formatting and mounting the resource disk

-  Configuring swap space

**Networking**

-  Manages routes to improve compatibility with platform DHCP servers

-  Ensures the stability of the network interface name

**Kernel**

-  Configure virtual NUMA (disable for kernel <2.6.37)

-  Consume Hyper-V entropy for /dev/random

-  Configure SCSI timeouts for the root device (which could be remote)

**Diagnostics**

-  Console redirection to the serial port

**SCVMM Deployments**

-  Detect and bootstrap the VMM agent for Linux when running in a System
   Center Virtual Machine Manager 2012R2 environment

**VM Extension**

-  Inject component authored by Microsoft and Partners into Linux VM
   (IaaS) to enable software and configuration automation

-  VM Extension reference implementation on
   https://github.com/Azure/azure-linux-extensions

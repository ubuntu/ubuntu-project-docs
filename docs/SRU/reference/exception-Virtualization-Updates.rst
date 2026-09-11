.. _reference-exception-VirtualizationUpdates:

Virtualization Updates
======================

This document describes the policy for updating [hardware enablement virtualization components](https://ubuntu.com/server/docs/how-to/virtualisation/virt-hwe/) in a stable,
supported release. These opt-in components are available in Ubuntu starting from Ubuntu Resolute 26.04.

This covers the following list of source packages:

-  `qemu-hwe <https://launchpad.net/ubuntu/+source/qemu-hwe>`__
-  `libvirt-hwe <https://launchpad.net/ubuntu/+source/libvirt-hwe>`__
-  `edk2-hwe <https://launchpad.net/ubuntu/+source/edk2-hwe>`__
-  `seabios-hwe <https://launchpad.net/ubuntu/+source/seabios-hwe>`__

Rationale
---------

With the advent of hardware-assisted virtualization in modern CPUs, the
virtualization stack (kernel KVM, QEMU and libvirt) evolves quickly alongside
silicon, particularly with the addition of major hardware features such as
confidential computing. Production environments predominantly rely on Ubuntu LTS
releases, whose two-year cadence makes it challenging to deliver the latest
virtualization features to LTS-only users in a timely manner.

To address this, and mirroring the long-standing
:ref:`HWE kernel <https://canonical-kernel-docs.readthedocs-hosted.com/reference/hwe-kernels/>`
model, starting from 26.04 LTS, Ubuntu provides an opt-in rolling **HWE virtualization stack** for the
LTS that tracks the upstream versions shipped in the latest Ubuntu interim release.

Key notes
---------

- The HWE virtualization stack is **opt-in**

   It is separate from the base stack that remains the default in Ubuntu. Users have to
   explicitly install the HWE packages to switch to the HWE virtualization stack.

- The HWE virtualization stack will be **upgraded once every 6 months**

   The upgrade follows the same schedule as the [HWE kernel](https://documentation.ubuntu.com/kernel/reference/hwe-kernels/). For example, shortly after the next Ubuntu
   interim release (e.g. 26.10) is released, the HWE virtualization stack will be updated in
   the current LTS (e.g. 26.04) to **match the version shipped in that interim release**.

- The HWE virtualization stack **stops rolling after 2 years** when the next LTS becomes available.

   For example, the 26.04 LTS HWE virtualization stack will stop rolling when the next LTS (e.g. 28.04) is released,
   and the last upgrade will be to match the versions shipped in the 28.04 LTS.

Here is the illustrative timeline of a HWE component's upgrade across future Ubuntu releases:

.. image:: https://assets.ubuntu.com/v1/4d67e99d-timeline.png
   :alt: Timeline of the HWE virtualization stack release and upgrade across future Ubuntu releases

Upgrade contents
----------------

- The upgrade will include the **upstream version** along with **relevant bug & security fixes** from the latest Ubuntu release.

- Some **adjustments** (e.g. not enabling a particular new feature in the backport) may be needed for the new upstream version to make it build and fit into the older LTS.

- Sometimes it might happen that adjustments are not enough to ensure the build and compatibility of the virtualization stack. In that case updating it might depend on the availability of **additional packages**, it is expected that build dependencies like toolchains are the most likely to come up like that. We'd need to wait for (by toolchain team) or drive such updates (if the components are on us) to unblock the hardware enablement virtualization stack updates.

Risk and mitigation
-------------------

Upgrading the virtualization stack to have a whole new upstream version in a stable release is a major change that
might break our traditional commitments of stability and security in stable releases. This section covers the mitigations
that we put in place to both minimize the risk of such breakage. The mitigations are of 3 kinds:

- Documentation
- Feature drop: case by case decision on dropping support for a particular feature or component if it is too risky to upgrade it.
- Testing

.. _virt-updates-documentation:

Documentation
~~~~~~~~~~~~~
Can you add the link to the Documentation section 
The places where the upgrade is documented are:

  - d/NEWS, d/changelog
  - `Launchpad`_ SRU bug.
  - `Ubuntu Discourse <UbuntuDiscourse_>`_

For each upgrade, the following information should be documented:

- any adjustments that are needed to make the new upstream version fit in the current LTS.
- any compatibility breakage with existing components or usage.

Features drop
~~~~~~~~~~~~~

To mitigate the risk of breakage, we might decide to drop support for a particular
feature or component if it is too risky or impossible to have it in the current LTS.
This decision should be made on a case by case basis after careful consideration of the potential impact.

Testing
~~~~~~~

In addition to the usual testing that the HWE stack naturally inherits
from the last Ubuntu release (since it has the same upstream version), some specific testing is needed to ensure
that the upgrade does not break existing usage or compatibility in the current LTS.
The following are the main areas of concern:

1) There are complex packaging dependencies between the *base* and the *HWE* stack, to ensure they are not mixed.
The upgrade of the HWE stack could affect the installation and usage of the base stack.
Testing should be done to ensure that:

-  installing the HWE stack should remain opt-in and needs to be explicitly requested by the user.
-  switching between the base and HWE stacks performs a complete one-to-one replacement, preserving dependencies and each package's auto/manual install mark.

2) The new version might also break runtime compatibility with existing components in the LTS. This runtime
breakage is hard to identify and occurs in production, so we need to do our best to identify and fix it before the
upgrade is released. This is done by the integration test suite that makes sure that the HWE stack is compatible
with the depending applications (virt-manager, libvirt-python, ...).

3) Introducing a new version might affect VM migration as Ubuntu defines new machine types; extensive testing 
on migration is important to ensure we do not break existing migration scenarios, and to identify any necessary
adjustments to the new upstream version to ensure the compatibility of the stack.

.. important::

   As of now, we cannot run the autopkgtests for the reverse dependencies against the HWE stack since the HWE stack
   is opt-in and by default the base stack will be installed for these tests. We need to figure out a way to force
   the HWE stack to be installed for these tests, or to run the tests against the HWE stack in a different way.

SRU Process
-----------

The SRU should be done with a single bug, for all the source packages. This is because the components
are tightly coupled and should be upgraded together to ensure the compatibility of the stack.
The SRU process should be followed as usual, with the following additional requirements to ensure
that the upgrade is done smoothly and with minimal regressions:

-  The SRU should be requested per the :ref:`Stable Release Updates <stable-release-updates-sru>`
   documented process.
-  The template at the end of this document should be used and all
   ‘TODO’ filled out
-  For each release (e.g. resolute, etc.) that is proposed to
   be updated by the SRU a link to the results of integration
   testing, via autopkgtest or other testing frameworks, successfully completed using the
   proposed package with no unexplained errors or failures
-  Documentation as described in the :ref:`Documentation <virt-updates-documentation>` section.


SRU Template
------------

::

   [Impact]

   This release upgrades the HWE stack to the upstream version shipped in Ubuntu <version>.

   *** <TODO: List the packages and target version>

   [Notable changes and changelog]

   To have a complete list of changes, please refer to the Ubuntu release notes:
   *** <TODO: link to release notes for each package>.

   Following are the notable adjustments that have been done to make the new upstream version fit
   in the current LTS:

   *** <TODO: list of the adjustments>

   Following are the breaking changes with existing components or usage:

   *** <TODO: list of the breakages>

   [Test Plan]

   - Autopkgtests with -proposed from the PPA

   - Regression tests : migration

   - Additional integration tests with the depending applications (virt-manager, libvirt-python, ...)

   [Where problems could occur]

   This update brings a whole new upstream version into a stable release, so the
   regression potential is higher than a typical SRU. The main areas where
   problems could occur are:

   - The HWE and base stacks are mutually exclusive. A packaging mistake could
     mix packages from both stacks, or cause the HWE stack to be pulled in
     without the user explicitly opting in.

   - Runtime compatibility with depending applications (virt-manager,
     libvirt-python, ...) could break.

   - New machine types may affect VM migration, potentially breaking existing
     migration scenarios.

   To mitigate these risks, the integration test suite, migration regression
   tests and autopkgtests described in the [Test Plan] are run with
   the proposed packages, and their results are attached to this bug.

   [Other Info]

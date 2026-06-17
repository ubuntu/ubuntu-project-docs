.. _reference-exception-VirtualizationUpdates:

Virtualization Updates
======================

This document describes the policy for updating [hardware enablement virtualization components](https://ubuntu.com/server/docs/how-to/virtualisation/virt-hwe/) in a stable,
supported release. These opt-in components are available in Ubuntu starting from Ubuntu Resolute 26.04.

This cover the following list of source packages:

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
model, Starting from 26.04 LTS, Ubuntu provides an opt-in rolling **HWE virtualization stack** for the
LTS that tracks the upstream versions shipped in the latest Ubuntu interim release.

Key notes
---------

- The HWE virtualization stack is **opt-in**

   It is separate from the base stack that remains the default in Ubuntu. Users have to
   explicitly install the HWE packages to switch to the HWE virtualization stack.

- The HWE virtualization stack will be **upgraded once every 6 months**

   The upgrade follows the same schedule as the [HWE kernel](https://documentation.ubuntu.com/kernel/reference/hwe-kernels/). For example, shortly after the next Ubuntu
   interim release (e.g. 26.10) is released, the HWE virtualization stack will be updated in
   the current LTS (e.g. 26.04) to match the versions shipped in that interim release.

- The HWE virtualization stack rolls to have the **same upstream version that is in the latest Ubuntu release**, it has already been tested and available there for a while to collect additional feedback before rolling its counterpart in the LTS.

   When the HWE stack rolls, it will be upgraded to have the same upstream version as the one shipped in
   the latest Ubuntu release. For example, when 26.10 is released, the 26.04 HWE stack will be upgraded
   to have the same upstream version as the one shipped in 26.10.

- The HWE virtualization stack is **stopped from rolling after 2 years**.

   For example, the 26.04 LTS HWE virtualization stack will stop rolling when the next LTS (e.g. 28.04) is released,
   and the last upgrade will be to match the versions shipped in the 28.04 LTS.

Here is the illustrative timeline of a HWE component's upgrade across future Ubuntu releases:

.. image:: https://assets.ubuntu.com/v1/4d67e99d-timeline.png
   :alt: Timeline of the HWE virtualization stack release and upgrade across future Ubuntu releases

Upgrade contents
----------------

- The upgrade will include the **upstream version** along with **relevant bug & security fixes** from the latest Ubuntu release.

- Some **adjusments** may be needed to the new upstream version to make it fit in the older LTS.

- With the above adjustments are not possible or enough to ensure the compability of the virtualization stack, **additional packages** might be needed in the SRU. For example, the build system or other dependencies of the virtualization stack (libvirt-python, virt-manager, meson, ...etc).

Risk and mitigation
-------------------

Upgrading the virtualization stack to have a whole new upstream version in a stable release is a major change that
might break our traditional commitments of stability and security in stable releases. This section covers the mitigations
that we put in place to both minimize the risk of such breakage.

1 - The new version will bring in new features, deprecate/modify existing features. These should be detailed both in the file d/NEWS and the SRU bug that is linked to the d/changelog entry.

2 - Any adjustments that are needed to make the new upstream version fit in the older LTS should be detailed in the SRU bug, and should be as minimal as possible to reduce the risk of regressions.

3 - The upgrade might break compatiblity or exising usage. This should be avoided by extensive testing:

Since there is complex packaging dependencies between the base and the HWE stacks to ensure they are not mixed, the upgrade
might break the base stack installation and usage. Extensive testing should be done to ensure that the upgrade does
not break the base stack installation and usage, and that switching between the base and HWE stacks with `ubuntu_virt_helper switch`
performs a complete one-to-one replacement, preserving dependencies and each package's auto/manual install mark.

Introducting a new version might affect VM migration as Ubuntu defines new machine types; extensive testing 
on migration is important to ensure we do not break existing migration scenarios, and to identify any necessary
adjustments to the new upstream version to ensure the compatibility of the stack.

The new version might also break runtime compatibility with existing components in the LTS. This runtime
breakage is hard to identify and occurs in production, so we need to do our best to identify and fix it before the
upgrade is released. This is done by the extensive integration test suite that the virtualization components contain,
which covers a wide range of scenarios and use cases, and is ran using the SRU package for each release. The results
of these tests are attached to the SRU bug.


SRU Process
-----------

The SRU should be done with a single bug, for all the source packages. This is because the components
are tightly coupled and should to be upgraded together to ensure the compatibility of the stack.
The SRU process should be followed as usual, with the following additional requirements to ensure
that the upgrade is done smoothly and with minimal regressions:

-  The SRU should be requested per the StableReleaseUpdates
   documented process
-  The template at the end of this document should be used and all
   ‘TODO’ filled out
-  For each release (e.g. resolute, etc.) that is proposed to
   be updated by the SRU a link to the results of integration
   testing, via autopkgtest, successfully completed using the
   proposed package with no unexplained errors or failures
-  Any packaging changes (e.g. a dependency changes) need to be
   stated

If backwards compatibility is to be broken, this should be clearly
written at the top of the bug description for the SRU, as well as in the
title with "[breaks-compat]". Furthermore, an email to ubuntu-release
will be sent to point the release / SRU teams to the bug in order to get
approval before uploading to the release's upload queue.


SRU Template
------------

::

   [Impact]
   This release contains bug fixes, security fixes and/or new features (and, for
   the HWE stack, may bring it in line with a newer upstream version) and we
   would like to make sure all of our supported customers have access to these
   improvements. The notable ones are:

   *** <TODO: Create list with LP: # included>

   See the changelog entry below for a full list of changes and bugs.

   [Test Plan]
   The following development and SRU process was followed:
   https://documentation.ubuntu.com/sru/en/latest/reference/exception-Virtualization-Updates

   Virtualization components contain an extensive integration test suite that is ran using
   the SRU package for each releases. This test suite's results are available here:
   http://autopkgtest.ubuntu.com/packages/n/virtualization-components
   A successful run is required before the proposed virtualization components package
   can be let into -updates.

   The virtualization team will be in charge of attaching the artifacts and console
   output of the appropriate run to the bug.  Virtualization team members will not
   mark ‘verification-done’ until this has happened.

   For HWE stack uploads, verification must also confirm that switching between
   the base and HWE variants with `ubuntu_virt_helper switch` performs a complete
   one-to-one replacement, preserving dependencies and each package's auto/manual
   install mark.

   [Where problems could occur]
   In order to mitigate the regression potential, the results of the
   aforementioned integration tests are attached to this bug.

   The HWE and base stacks are mutually exclusive and the HWE packages are
   separate source packages; particular attention is required to ensure that no
   variant or supported release misses a relevant change, including security
   fixes.

   <TODO: attach test artifacts for every SRU release, not a link as links expire>

   [Other Info]
   <TODO: other background, including which variant (base or HWE) and which
   releases are targeted>

   [Changelog]
   <TODO: Paste in change log entry, including a link to the upstream release
   announcement for any new upstream version>


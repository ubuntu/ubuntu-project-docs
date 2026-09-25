.. _reference-criteria-closely-coupled-kernel-userspace:

==========================================
Closely-Coupled Kernel Userspace Releases
==========================================

Abstract
========

In Linux distros, there are a variety of packages that are closely coupled to the Linux kernel.
Examples include filesystem userspace tools, networking utilities, and device drivers.
As the Ubuntu hwe (hardware enablement) kernel moves forward, new capabilities are available
for users, however, the userspace packages are frozen. An example is ``btrfs-progs`` which
is maintained separately in GitHub [#f1]_. From the README in the repository: “The major version
releases are time-based and follow the cycle of the linux kernel releases. The cycle usually takes
2 months [sic: from the upstream kernel release]. A minor version release may happen in the meantime
if there are bug fixes or minor useful improvements queued.” The goal, in the case of ``btrfs-progs``,
is to have userspace and kernel capabilities in lockstep for users. This is not the current case in Ubuntu.

Userspace packages in Ubuntu also have the issue of being pulled from Debian. If Debian is seeking
to keep userspace and kernel in-line, this will lead to misalignment with Ubuntu kernels.
This is easily shown on an Ubuntu 24.04 Noble Numbat system, where the LTS kernel is 6.8,
and ``btrfs-progs`` is at 6.6.3. The misalignment with kernel and difficulty in maintaining
the package lead to bugs that can cause major repercussions. [#f2]_ [#f3]_ [#f4]_

This page specifies the general approach and workflow for packages that are closely coupled
to the Ubuntu kernels. 


Rationale
=========

When userspace and kernel are so tightly coupled, users of the `Ubuntu HWE Kernel`_ should have the full
capabilities of that kernel available in the associated user space packages.

Backporting specific fixes in tightly-coupled kernel userspace packages can be tricky, as bugfixes may be
relying on kernel changes as well.

Example scenario: a bug is reported against ``btrfs``. It turns out that this issue has a kernel and userspace
component. The kernel portion is addressed in ``$NEW_KERNEL`` in an HWE roll. ``btrfs-progs`` stays on the same
major version and a targeted fix is done. However, due to the mixing of new features and bug fixes related to
new ``btrfs`` work in the kernel and userspace, extracting only the bugfix is difficult.


Specification
=============

High Level Considerations for Inclusion
---------------------------------------

Not all packages can be considered a part of the userspace hwe-kernel tight coupling set.
The following are base criteria to see if a package should be considered a part of this specification:

1. Primary functionally of the package is directly tied to Kernel version

2. Kernel capabilities added in an HWE roll are *inaccessible* to most users without the userspace package

3. Upstream development does *not* maintain any “long term stable” branches

4. Changes to upstream code mix bugfix and features

   1. As upstream code moves forward, a bug which affects “older” versions may be fixed on top of
      already changed code. Thus crafting specific bugfix patches is difficult, and can lead to
      incompatible changes with older versions.

   2. This may lead to situations where a new version is being backported that only contains
      enablement for the HWE kernel and no bugs being addressed. This should be safe for users,
      but can lead to an extra update.

5. Upstream projects set *acceptable minimum version compatibility against the kernel*.

   1. Ex: an upstream project supports *backwards compatibility* with the LTS kernel available
      in a given Ubuntu release.

   2. Bonus points for backwards compatibility against all standard supported kernels, as it means
      keeping a consistent version through Ubuntu releases.

6. Packages are end-user applications not strictly libraries

   1. Library changes create a huge blast radius. While applications may be called by other applications
      (``package-a`` relies on ``ethtool``) there are better guarantees on API compatibility compared to
      bumping a SONAME and ABI compatibility.

   2. As is, it must be proven that a package is *best* served by rolling, and has minimal possible
      disruptions to the Ubuntu ecosystem at large.

Workflow
--------

What follows is the general flow of the package, from development to SRU. This includes required steps
and considerations.

Ubuntu Devel
~~~~~~~~~~~~

The Ubuntu kernel is taking a bleeding edge approach, taking as new a version as possible.
This may mean releasing with an RC kernel from upstream. Many userspace packages do not update until
after the release of the upstream kernel, with lag being different for each package. If a time
differential is generally known, it must be documented by the package. Basic steps:

1. Follow upstream releases as close as possible, ensuring the latest release is in Ubuntu devel
2. If a kernel is released, and no userspace package is available at the time of release,
   the package must first be put into Ubuntu Devel and then SRU’d.

   1. It is acceptable to do an SRU before the development release is complete if it offers enablement
      for the kernel provided functionality in ``$PREVIOUS_RELEASE``.

      1. Ex: Ubuntu Resolute Racoon 26.04 is shipping with kernel 7.0.0, taken from 7.0.0rc7 upstream.
         At 26.04 release, userspace tools are not released yet. It is acceptable to get the new tool
         into 26.10 Stonking Stingray, and SRU into 26.04 before 26.10 release.

Ubuntu LTS
~~~~~~~~~~

The Ubuntu kernel follows two primary tracks during LTS releases – HWE and Stable. There are also specialized
OEM kernels that are on fixed versions that may differ from HWE and Stable. This leads to a situation where
there are, minimally, two versions of the kernel available. For a package to be able to be backported to a
Stable Release, it must declare support for the Stable LTS kernel. An example upstream README from ``btrfs-progs``
states:
As the documentation states:

    **Feature compatibility**

    The btrfs-progs of version X.Y declare support of kernel features of the same version. 
    New progs on old kernel are expected to work, limited only by features 
    provided by the kernel. [#f5]_

If the above condition is met, a package may be backported from Devel into Stable Releases. This must follow standard procedures, not skipping any release unless there is a documented reason. A fictitious example:

* ``tightly-coupled-package-a`` is at version 1.90 in devel
* Ubuntu Development for 28.10 Winsome Weasel (WW) has begun
* ``tightly-coupled-package-a`` 1.90 defines that it has support for kernel versions starting at 6.15.0
* The Ubuntu Kernel moves to 7.6
* ``tightly-coupled-package-a`` follows with version 1.91 enabling features in 7.6 during Ubuntu Development

  * It retains the same earliest starting version of the kernel

* ``tightly-coupled-pakage-a`` is updated to 1.91 during development
* Ubuntu is released
* At 28.04 VV .2 release

  * The current LTS kernel is 7.4
  * HWE kernel rolls to 7.6

* Based on the above criteria, rolling ``tightly-coupled-package-a`` version 1.91 into 28.04 is most desirable
* A team member prepares an SRU, with full-template, for the release of 1.91 to enable the HWE kernel
* They also check for any bugs that may be addressed…
* Bundled in 1.91 are various bugfixes. Because of the enablement of new features, separating the fixes from
  the feature work is difficult.
* A bug is reported in ``tightly-coupled-package-a`` on the original version of the package, 1.83, as found
  in Ubuntu 26.04 Resolute Racoon. This bug affected 28.04 as well with their version 1.89
* Version 1.91 upstream specifies it fixes the bug.
* After successfully testing 1.91 on 28.04, a team member prepares uploads for 26.04, as it is the
  *next supported release*

  * Note: because this happened after the .2 release, Ubuntu UU is an interim version with only 9 months of support
    and has already been deprecated. Therefore it does *not* need to receive an update

* This follows a standard SRU procedure – do not skip releases, ensure no breaking changes, ensure compatibility
  of the tool, especially against both the LTS and HWE kernels.

Backport/SRU Release Timing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Kernel team rolls the HWE kernel roughly 3 months after the release of an interim or the next LTS release.
These coincide with the “dot” releases for an LTS. [#f6]_ This means that tools must also follow this timing.
Due to the time between Ubuntu release and backport of the HWE kernel, a new userspace filesystem tool is likely.
Use the “dot” releases as a milestone, with coordination with the release team and kernel team.

Things like filesystem tools are often *seeded*, which means needing to be prepared and ready for dot release
candidate images. This is because filesystem tools are made available on the ISOs for users to freely choose
root file systems.

Documentation
-------------

All packages meeting the above criteria must be documented in “SRU/Package Specific Notes” [#f7]_. A link must
be added to this page for the documentation, and a reference to this page made in the package specific notes.
The documentation for each package must outline all the information for the package:

* Release cadence (if publicized)
* Statements of and links to compatibility statements
* Testing documentation

  * Autopkgtests and their coverage
  * Kernel integration testing
  * Any manual testing steps required for packages.

* Any *exceptions* that need to be made

  * Ex: inability of running autopkgtests due to environment

Testing
-------

Autopkgtests
~~~~~~~~~~~~

Tools *should* have autopkgtests. Minimally, these tests must exercise:

* Installation of the package (in most cases, this will *upgrade* a system)
* Basic operations

If a package does *not* have autopackage tests, it must be clearly documented why they are *not* appropriate
and what testing will be done to ensure quality and lack of regressions. These tests *must* be run against
the LTS and HWE kernels.

Kernel Testing
~~~~~~~~~~~~~~

In the case of the kernel containing tests exercising the capabilities, including using the userspace tool,
those tests *must* be run. These tests *must* be run against the LTS and HWE kernels.

Manual Testing
~~~~~~~~~~~~~~

If a manual test is required, either due to lack of autopkgtest capability or kernel integration tests,
the manual test must be documented fully. These test plans must be written in such a manner that any individual can run the tests, given reasonable pre-requisites.


Included Packages
-----------------

.. toctree::
    :maxdepth: 1

    exception-btrfs-progs


|br|
|br|

.. rubric:: Footnotes

.. [#f1] https://github.com/kdave/btrfs-progs
.. [#f2] https://bugs.launchpad.net/ubuntu/+source/btrfs-progs/+bug/2115454
.. [#f3] https://bugs.launchpad.net/ubuntu/+source/btrfs-progs/+bug/2091894
.. [#f4] Note that in Debian it got orphaned, and then salvaged https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1088329
.. [#f5] https://github.com/kdave/btrfs-progs?tab=readme-ov-file#feature-compatibility
.. [#f6] A “dot” release is, essentially, the kernel roll + a more fully tested ISO. Some packages may follow the “dot” releases due to tight coupling with the ISO (such as ``subiquity``) or internal Canonical teams may use dot releases as milestones to achieve partner commitments. Cloud images are continuously built, tested, and released.
.. [#f7] :ref:`SRU/reference/package-specific <reference-package-specific-notes>`

.. _Ubuntu HWE Kernel: https://canonical-kernel-docs.readthedocs-hosted.com/latest/reference/hwe-kernels/

.. |br| raw:: html

   <br />
.. _btrfs-progs:

===========
Btrfs-progs
===========

Basic Information
-----------------

* ``btrfs-progs`` is maintained in GitHub and follows the kernel release cycle. [#f1]_
* ``btrfs-progs`` states:

    “The *btrfs-progs* of version *X.Y* declare support of kernel features of the same version. New progs on old kernel are expected to work, limited only by features provided by the kernel.” [#f2]_

* Releases use tags. As can be seen in the tags, there are no long-term branches, instead continuous moving versions aligning with upstream kernels. [#f3]_
* Primary functionality of ``btrfs`` is contained in the kernel.
* For minor releases: “A minor version release may happen in the meantime if there are bug fixes or minor useful improvements queued.” [#f4]_

Autopkgtest
-----------

As of 20260128, ``btrfs-progs`` does not have autopkgtests. Reverse run-time dependencies are outlined below.

Dependency Analysis
~~~~~~~~~~~~~~~~~~~

Reverse-Depends
===============

* ``apt-btrfs-snapshot``: create btrfs snapshots whenever apt is run (universe)
* ``btrbk``: backup tool for btrfs volumes (universe)
* ``btrfsd`` [amd64 amd64v3 arm64 armhf ppc64el riscv64 s390x]: daemon for btrfs maintenance (universe)
* ``btrfsmaintenance``: scripts automating btrfs maintenance tasks (universe)
* ``calamares-settings-mobian``: calamares + Mobian for small touch screen devices (universe)
* ``freedom-maker``: FreedomBox image maker. Freedombox is a personal cloud server (universe)
* ``golang-github-containerd-btrfs-dev`` (src: ``golang-github-containerd-btrfs``): go bindings for btrfs (universe)
* ``initramfs-tools-devices``: Common initramfs scripts for Ubuntu Core and Classic (universe)
* ``kiwi-dracut-lib`` [amd64 amd64v3 arm64 armhf ppc64el riscv64 s390x] (src: ``kiwi``): modules for dracut for kiwi image builder
* ``kiwi-systemdeps-filesystems`` [amd64 amd64v3 arm64 armhf ppc64el riscv64 s390x] (src: ``kiwi``): kiwi image builder host setup helper (universe)
* ``libblockdev-btrfs3`` (src: ``libblockdev``): library plugin and standalone for btrfs and C++ projects (universe)
* ``libguestfs0t64`` [amd64 amd64v3 arm64 armhf ppc64el riscv64 s390x] (src: ``libguestfs``): shared library for guest disk image management (universe)
* ``mkosi``
* ``ubuntu-server`` [amd64 amd64v3 arm64 armhf ppc64el riscv64 s390x]: meta
* ``ubuntu-server-minimal`` [amd64 amd64v3 arm64 armhf ppc64el riscv64 s390x]: meta
* ``ubuntu-server-raspi`` [arm64 armhf]: meta

Reverse-Recommends
==================

* ``calamares`` [amd64 amd64v3 arm64 armhf ppc64el riscv64 s390x]: alternative graphical installer (universe)
* ``calamares-extensions`` [amd64 amd64v3 arm64 armhf ppc64el riscv64 s390x]: mobile modules for calamares
* ``distrobuilder`` [amd64 amd64v3 arm64 armhf ppc64el riscv64 s390x]
* ``lubuntu-desktop`` [amd64 amd64v3 arm64 armhf ppc64el riscv64 s390x]: meta
* ``lubuntu-desktop-minimal`` [amd64 amd64v3 arm64 armhf ppc64el riscv64 s390x]: meta
* ``ntfs2btrfs`` [amd64 amd64v3 arm64 armhf ppc64el riscv64 s390x]: convert ntfs to btrfs (universe)
* ``ubiquity`` [amd64 amd64v3 arm64 armhf ppc64el riscv64 s390x]: old installer

Reverse-Build-Depends
=====================

* ``btrfsd``: yet another btrfs daemon for maintenance tasks (universe)
* ``containerd-app``: daemon to control runc. Runc + containers = can use btrfs
* ``containerd-stable``: as above
* ``docker.io-app``: as above, except Docker
* ``golang-github-containerd-btrfs``: stated above with ``golang-github-containerd-btrfs-dev``
* ``libguestfs``: stated above with ``libguestfs0t64``

..

Of these dependencies, only ``libblockdev`` provides direct ``btrfs`` testing mounting ``btrfs`` filesystems, manipulating volumes and snapshots, and validating the plugin path from top level to the kernel module. Of the build dependencies, only ``docker.io-app`` contains any reference to ``btrfs``, and it’s somewhat ancillary. Running the ``docker-in-lxd`` tests configure ``lxd`` with a ``btrfs`` backend.

The packages broadly show a need to have matching functionality with the kernel. For image building, container runtimes, and libraries it is important to ensure full-functionality with kernel features. For btrfs-specific maintenance scripts and daemons, stability of the interface is important.

Autopkgtest Requirements and Addition of Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Btrfs-progs`` needs to have autopkgtests added to be able to be SRU’d safely. Further, passing ``libblockdev`` tests are of high importance.

1. Test installation and upgrade of ``btrfs-progs`` (it’s currently seeded on server, so will likely be in any VM, container, or chroot unless explicitly pruned).
2. Test basic filesystem operations:

   1. Create a bare partition
   2. Ensure partition is unmounted
   3. Mkfs.btrfs the new partition
   4. ``btrfs check --read-only --force $device``
   5. Ensure partition is mounted
   6. Write a bunch of files
   7. Run ``btrfs filesystem du``, ensure nothing crashes
   8. Run ``btrfs device stats $device``
   9. All commands need sudo
   10. Tests must be run with ``isolation-machine``

The goal of the tests is not to run every command, nor to cover every case. It’s a selection of “low-hanging fruit” that tests that the program is installed and common commands are available. We will not be able to cover all the cases in an autopkgtest, including functions such as subgroups, managing quota, replication, etc.

Tests must be run with the LTS and HWE kernel. Creating a proper dependency graph that ensures these tests are automatically run on upload of any filesystem tool may not be possible. In which case a single case will be covered for any interim bugfix updates, and manual testing against LTS and HWE done on ``btrfs-progs`` updates.

Kernel Testing
--------------

The Ubuntu Kernel team maintains a test suite that exercises filesystem capabilities. During the coordinated dot release, the kernel team will run these tests against the LTS kernel and the HWE kernel with the new version of ``btrfs-progs`` that has been prepared. Aspirationally, this testing will be done with a package made in a PPA, as there is currently no way to block proposed-migration on an external test. The kernel team will also aid when the new version of any filesystem tool is made available to do similar testing. The Kernel team regularly runs filesystem tests using the version of userspace tools already released, so continuous testing will occur related to kernel updates. Test results from the kernel runs will be posted to the appropriate SRU bugs.

.. rubric:: Footnotes

.. [#f1] https://github.com/kdave/btrfs-progs?tab=readme-ov-file#release-cycle
.. [#f2] https://github.com/kdave/btrfs-progs?tab=readme-ov-file#feature-compatibility
.. [#f3] https://github.com/kdave/btrfs-progs/tags
.. [#f4] https://github.com/kdave/btrfs-progs?tab=readme-ov-file#release-cycle
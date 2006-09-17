.. _kernel_updates_for_stable_releases:

Kernel Updates for Stable Releases
----------------------------------

Procedures for on-going updates to stable releases of the kernel.

Patches to the kernel not related to security will first appear in
-proposed. To use these kernels, you must add a line to your
*/etc/apt/sources.list* file:

::

   deb http://archive.ubuntu.com/ubuntu <release>-proposed main restricted

Currently, there are no *linux-meta* packages, so updates will have to
be manually installed initially. Use this command:

::

   sudo apt-get install linux-image-2.6.15-50-<flavour> linux-restricted-modules-2.6.15-50-<flavour>

Where *flavour* is one of 386, 686, k7 (for i386 dapper). If you have a
different architecture, or are using some other stable release besides
dapper, this may change a little. If you do not need
linux-restricted-modules, you can choose not to install that. The ABI
(50) will remain the same. Other releases will change the kernel
version. For example, it will be 2.6.17 for edgy, instead of 2.6.15.

Eventually, stable patches to this kernel will be migrated to the main
stable release. Testing (by you) is required to make this happen.

All changes from the stable kernel are listed in the top level changelog
entry (there are not multiple entries in the changelog for each upload,
just a single rolling entry). When changes are migrated to the stable
kernel, they will be removed from the *proposed* changelog entry.

Every effort will be made to keep the *proposed* kernel synced with
security updates, but do not count on it.

--------------

CategoryKernel

.. _how-to-build-packages-locally:

How to build packages locally
=============================

In Ubuntu, packages can be built in several ways, depending on the intended artifacts. This article describes local building using the following methods:

* Source and binary (using ``dpkg-buildpackage``)
* Source and binary (using ``sbuild`` for a clean environment)
* Binary-only (using ``sbuild`` for a clean environment)
* Source-only (using ``debuild``)
* Binary-only (using ``debuild`` and installed build dependencies)

(Many other backends are available, including an ``schroot``-based backend.)

Only source uploads are permitted to PPAs or the Archive. That said, it is best practice to perform a local build and fix any potential issues before uploading it to any Archive.

To let the Launchpad infrastructure build packages for you, see :ref:`how-to-build-packages-in-a-ppa`.


Prerequisites
-------------

.. code-block:: none

    $ sudo apt install dpkg-dev sbuild debhelper ubuntu-dev-tools piuparts

All of the following sections assume you have already fetched the packaging (see :ref:`how-to-get-the-source-of-a-package`) and are in the same directory as the :file:`debian/` sub-directory.


.. _build-with-dpkg-buildpackage:

Build with ``dpkg-buildpackage``
--------------------------------

To build the source from within the package repository:

.. code-block:: none

    $ dpkg-buildpackage -S -I -i -nc -d

**Used options:**

``-S`` (``--build=source``):
  Build a source (``.dsc``, ``.changes``).

``-I`` (``--tar-ignore``):
  For the created tarball, filter out control files and directories of the most common revision control systems, backup and swap files, and Libtool build output directories.

``-i`` (``--diff-ignore``):
  Like ``--tar-ignore`` but for the ``diff``.

``-nc`` (``--no-pre-clean``):
  Do not clean the tree before building.

``-d`` (``--no-check-builddeps``):
  Do not check build dependencies and conflicts (the check is not unnecessary for source builds).

When building a package based on a ``git-ubuntu`` branch for an upload to the Ubuntu Archive, add the output of ``git ubuntu prepare-upload args``, which adds the arguments to allow ``git-ubuntu`` to properly reference this on importing the new version - thereby retaining the history of your branch.

Build for an upload to the Archive:

.. code-block:: none

    $ dpkg-buildpackage -S -I -i -nc -d $(git ubuntu prepare-upload args)


Sign the ``changes`` file
~~~~~~~~~~~~~~~~~~~~~~~~~

In order for a source package to be accepted by Launchpad, it must be signed. If your GPG keys are properly installed, `dpkg-buildpackage` may automatically sign the package. If not, sign the source package manually with ``debsign``:

.. code-block:: none

    $ debsign ../<filename>_source.changes

.. tip::

    To automatically find the :file:`changes` file, create a script that extracts the info from :file:`debian/changelog`:

    .. code-block:: none

        $ source_package=$(dpkg-parsechangelog -n1 --show-field Source)
        $ version=$(dpkg-parsechangelog -n1 --show-field Version)
        $ debsign "../${source_package}_${version}_source.changes



Build with ``sbuild``
---------------------

This is the standard way of building a package for Ubuntu. All of the Debian and Ubuntu infrastructure use :manpage:`sbuild(1)`. For more information on setting it up, see :ref:`sbuild`.

Consider

To do a binary-only build of a package using ``sbuild``, run:

.. code-block:: none

    $ sbuild --chroot <RELEASE>-<ARCH>[-shm]

**Useful options:**

Distribution:
  It is possible to use ``--dist`` (``-d``) to specify the distribution for the build instead of ``--chroot``, which explicitly selects the chroot to use, but that causes the produced files to contain the entire chroot name (``<RELEASE>-<ARCH>[-shm]``) instead of just ``<RELEASE>``. An example chroot name is ``noble-amd64-shm``.

Parallel builing:
  To speed up the build, set the ``parallel`` option through the ``DEB_BUILD_OPTIONS`` environment variable. For example:

  .. code-block:: none

      $ DEB_BUILD_OPTIONS="parallel=3" sbuild --chroot <RELEASE>-<ARCH>[-shm]

Shell in the chroot:
  To get a shell inside of the chroot (e.g. to investigate build failures), use the ``--build-failed-commands`` option. For example:

  .. code-block:: none

      $ sbuild --chroot <RELEASE>-<ARCH>[-shm] \
               --build-failed-commands=%SBUILD_SHELL

Run :term:`lintian` after the build:
  .. code-block:: none

      $ sbuild -c <RELEASE>-<ARCH>[-shm] \
               --run-lintian [--lintian-opts="-EvIiL +pedantic"]

Build without running :manpage:`dh_clean(1)`:
  .. code-block:: none

      $ sbuild -c <RELEASE>-<ARCH>[-shm] --no-clean-source

Build both a binary *and* a source package:
  .. code-block:: none

      $ sbuild -c <RELEASE>-<ARCH>[-shm] -s

.. note::

    Launchpad rejects uploads that contains both binaries and sources. However, this is required for uploads to the Debian NEW queue. That said, uploads to Debian with binaries `do not migrate to Testing <https://lists.debian.org/debian-devel-announce/2019/07/msg00002.html>`_.

Here is a complete, working example of running :manpage:`autopkgtest(1)` following the build:

.. code-block:: none

    $ sbuild -c noble-amd64-shm --run-autopkgtest \
      --autopkgtest-virt-server=qemu \
      --autopkgtest-virt-server-opt="/path/to/autopkgtest-noble-amd64.img" \
      --autopkgtest-opt="--apt-pocket=proposed=src:qt6-base" \
      --autopkgtest-opt="-U" --autopkgtest-opt="--ram-size=12000" \
      --autopkgtest-opt="--setup-commands='apt-get -y install aptitude \
        && aptitude -t noble-proposed -y install qt6-base-dev=6.8.1+dfsg-0ubuntu1'"

.. note::

    Starting with Ubuntu 23.04 (Lunar Lobster), the ``series-proposed`` suite is disabled by default via :manpage:`APT Preferences <apt_preferences(5)>`. This affects schroots created with ``sbuild-launchpad-chroot``, so packages from the ``-proposed`` pocket are not used in the build process (see :lpbug:`1996205`).


Build with ``debuild``
----------------------

:manpage:`debuild(1)` (short for :manpage:`dpkg-buildpackage(1)`) is another tool used to build Debian packages. It is part of the :manpage:`debhelper(7)` package and written in Perl.

Ubuntu maintains its own version of the ``debhelper`` package. Therefore, packages built on Debian may be slightly different than packages built on Ubuntu.


Source-only builds
~~~~~~~~~~~~~~~~~~

To build a source package *without* including the upstream tarball, run:

.. code-block:: none

    $ debuild -S -d


**Useful options:**

Build a source package *with* the upstream tarball:
  .. code-block:: none

      $ debuild -S -d -sa

Build a source package without running :term:`lintian`:
  .. code-block:: none

      $ debuild --no-lintian -S -d

  .. note::

      The ``--no-lintian`` flag only works in this case if it is first.

Build a source package without running :manpage:`dh_clean(1)`:
  .. code-block:: none

      $ debuild -S -d -nc

  Use this to fix failures regarding missing build dependencies.


Local binary-only builds
~~~~~~~~~~~~~~~~~~~~~~~~

This is really only useful for packages you need to test locally or packages with minimal build dependencies. Otherwise use :manpage:`sbuild(1)`.

To do a binary-only build of a package, run:

.. code-block:: none

    $ debuild -b


Clean up after build
--------------------

To remove build artifacts for a clean package directory, use one of the following methods to call the ``clean`` target from :file:`debian/control`. This is not required before running a new build because all build methods perform the cleaning automatically before starting a build (unless instructed otherwise).

* ``dpkg-buildpackage -T clean``
* ``sbuild --clean-source``
* ``debuild -T clean``

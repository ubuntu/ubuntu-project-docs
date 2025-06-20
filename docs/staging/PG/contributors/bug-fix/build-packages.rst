Build packages
==============

In Ubuntu, packages can be built in several ways, depending on the intended
artifacts. We cover the following types of builds:

* Source and binary (using ``sbuild`` for a clean environment)
* Binary-only (using ``sbuild`` for a clean environment)
* Source-only (using ``debuild``)
* Binary-only (using ``debuild`` and installed build dependencies)

(Many other backends are available, including an ``schroot``-based backend.)

Only source uploads are permitted to PPAs or the archive. That
being said, it is best practice to perform a local build and iron out any
potential issues prior to uploading it to any archive.


Prerequisites
-------------

.. code-block:: text

    $ sudo apt install sbuild debhelper ubuntu-dev-tools piuparts

All of the following sections assume you have already fetched the packaging
and are in the same directory as :file:`debian/`.


``sbuild``-based builds
-----------------------

This is the standard way of building a package for Ubuntu. All of the Debian
and Ubuntu infrastructure use :manpage:`sbuild(1)`, so it is beneficial to
learn how to use it. For more information on setting up :manpage:`sbuild(1)`,
refer to the links in the Resources section.

To do a binary-only build of a package using ``sbuild``, run:

.. code-block:: text

    $ sbuild -c <RELEASE>-<ARCH>[-shm]

.. note::

    It is possible to use ``-d`` instead of ``-c``, but that causes the produced
    files to contain the entire chroot name (``<RELEASE>-<ARCH>[-shm]``) instead
    of just ``<RELEASE>``. An example chroot name is ``noble-amd64-shm``.

To explicitly run Lintian following the build:

.. code-block:: text

    $ sbuild -c <RELEASE>-<ARCH>[-shm] --run-lintian [--lintian-opts="-EvIiL +pedantic"]

To build a package without running :manpage:`dh_clean(1)`, run:

.. code-block:: text

    $ sbuild -c <RELEASE>-<ARCH>[-shm] --no-clean-source

To build both a binary *and* a source package with one ``sbuild`` run:

.. code-block:: text

    $ sbuild -c <RELEASE>-<ARCH>[-shm] -s

.. note::

    Launchpad rejects uploads that contains both binaries and sources.
    However, this is required for uploads to the Debian NEW queue. That being
    said, uploads to Debian with binaries `do not migrate to Testing <https://lists.debian.org/debian-devel-announce/2019/07/msg00002.html>`_.

Here is a complete, working example of running the ``autopkgtest`` following the build:

.. code-block:: text

    $ sbuild -c noble-amd64-shm --run-autopkgtest \
      --autopkgtest-virt-server=qemu \
      --autopkgtest-virt-server-opt="/path/to/autopkgtest-noble-amd64.img" \
      --autopkgtest-opt="--apt-pocket=proposed=src:qt6-base" \
      --autopkgtest-opt="-U" --autopkgtest-opt="--ram-size=12000" \
      --autopkgtest-opt="--setup-commands='apt-get -y install aptitude \
        && aptitude -t noble-proposed -y install qt6-base-dev=6.8.1+dfsg-0ubuntu1'"


Building with ``debuild``
-------------------------

:manpage:`debuild(1)` (short for :manpage:`dpkg-buildpackage(1)`) is
another tool used to build Debian packages. It is part of the
:manpage:`debhelper(7)` package and written in Perl.

Ubuntu maintain its own version the ``debhelper`` package. Therefore,
packages built on Debian may be slightly different than packages built on
Ubuntu.


Source-only builds
~~~~~~~~~~~~~~~~~~

To build a source package *without* including the upstream tarball, run:

.. code-block:: text

    $ debuild -S -d

To build a source package *with* the upstream tarball, run:

.. code-block:: text

    $ debuild -S -d -sa

To build a source package without running Lintian, run:

.. code-block:: text

    $ debuild --no-lintian -S -d

.. note::

    The ``--no-lintian`` flag only works in this case if it is first.

To build a source package without running :manpage:`dh_clean(1)`, run:

.. code-block:: text

    $ debuild -S -d -nc

.. note::

    This tends to fix failures regarding missing build dependencies.

To build a source package without a cryptographic signature (not recommended), run:

.. code-block:: text

    $ debuild -S -d -us -uc


Local binary-only builds
~~~~~~~~~~~~~~~~~~~~~~~~

This is really only useful for packages you need to test locally or
packages with minimal build dependencies. Otherwise use :manpage:`sbuild(1)`.

To do a binary-only build of a package, run:

.. code-block:: text

    $ debuild -b


Resources
---------

* `Chapter 6. Building the package (Debian New Maintainers' Guide) <https://www.debian.org/doc/manuals/maint-guide/build.html>`_

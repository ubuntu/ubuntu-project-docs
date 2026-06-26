.. _how-to-build-packages-locally:

How to build packages locally
=============================

.. note::

        This is about building an existing package locally. If you want to
        build a new package, please refer to
        :ref:`how-to-create-a-new-package`.

In Ubuntu, packages can be built in several ways, depending on the intended
artifacts. The standard and recommended way to build packages for Ubuntu is
with ``dpkg-buildpackage`` and ``sbuild``. This ensures that the build
dependencies are properly declared and that the resulting package is
reproducible.

``dpkg-buildpackage`` is used to build **source-only** packages.

``sbuild`` is used to build **binary-only** and **source** + **binary**
packages.

PPAs and the Archive permit exclusively **source-only** package uploads,
however it is best practice to first perform a local **binary** build and fix
any potential issues before uploading.

To let the Launchpad infrastructure build packages for you, see
:ref:`how-to-build-packages-in-a-ppa`.


Prerequisites
-------------

Complete the following sections from :ref:`how-to-set-up-for-ubuntu-development`:

* :ref:`ubuntu-development-dependencies` - install the dependencies for Ubuntu
  development
* :ref:`configure-groups` - setup your user groups for Ubuntu development
* :ref:`sbuild` - setup ``sbuild``


Fetching the package source
~~~~~~~~~~~~~~~~~~~~~~~~~~~

See :ref:`how-to-get-the-source-of-a-package` for instructions on how to fetch the source of a package. You need the source to build it locally.


.. _building-packages:

Building packages
-----------------

Issue ``sbuild`` build commands from the source package directory that contains
:file:`debian/`:

.. code-block:: none

    $ cd <package>/debian/

``sbuild`` allows for targeting builds towards specific releases of Ubuntu. This is useful for testing builds in the same environment as the intended upload target.

Specify the release using the ``--dist=`` (``-d``) option:

.. code-block:: none

    $ sbuild --dist=<RELEASE>

where ``<RELEASE>`` is the name of the Ubuntu release (e.g. ``resolute``).

.. tip::

    If you have set a default distribution in :file:`~/.config/sbuild/config.pl`, you can omit the ``-d`` option to build for the default release.


Building binary-only packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, ``sbuild`` builds a **binary-only** package. Run the following command to build a binary package for a specific release:

.. code-block:: none

    $ sbuild --dist=<RELEASE>

This produces architecture-specific binary packages without generating a source package and is mostly useful for packages you need to test locally.


Building source-only packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To build a **source-only** package for a specific release, the current
recommended practice is to use ``dpkg-buildpackage`` instead of ``sbuild``:

.. code-block:: none

    $ dpkg-buildpackage --build=source --no-check-builddeps --no-pre-clean

The flags used have the following meaning:

* ``--build=source`` (``-S``): source-only build
* ``--no-check-builddeps`` (``-d``): do not check build dependencies
* ``--no-pre-clean`` (``-nc``): do not clean the source tree before build


Building both source and binary packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To build both **source** and **binary** packages for a specific release, use the ``--source`` (``-s``) option:

.. code-block:: none

    $ sbuild --source --dist=<RELEASE>

.. note::

    Launchpad rejects uploads that contain both binaries and sources.


Useful ``sbuild`` options
~~~~~~~~~~~~~~~~~~~~~~~~~

Parallel building:
  To speed up the build, set the ``parallel`` option through the ``DEB_BUILD_OPTIONS`` environment variable. For example:

  .. code-block:: none

      $ DEB_BUILD_OPTIONS="parallel=3" sbuild --chroot <RELEASE>-<ARCH>[-shm]

Run :term:`lintian` after the build:
  .. code-block:: none

     --run-lintian [--lintian-opts="-vIiL +pedantic"]

Large package linting:
  Some large packages take a long time to lint. To avoid :term:`lintian` after
  the build:

  .. code-block:: none

     --no-run-lintian


Signing the ``changes`` file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a source package to be accepted by Launchpad, it must be signed. If you specify ``key_id`` in your ``sbuild`` configuration, this is used. Otherwise, sign the source package manually with the ``debsign`` tool:

.. code-block:: none

    $ debsign ../<filename>_source.changes

.. tip::

    To automatically find the :file:`changes` file, create a script that extracts the info from :file:`debian/changelog`:

    .. code-block:: none

        $ source_package=$(dpkg-parsechangelog -n1 --show-field Source)
        $ version=$(dpkg-parsechangelog -n1 --show-field Version)
        $ debsign "../${source_package}_${version}_source.changes


Advanced usage
--------------

In some cases, builds may be more complex and require additional configuration. For example, you may need to build for a different architecture or use locally built dependencies.


Building for a different architecture (cross-building)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. dropdown:: Without ``unshare`` (additional setup required)

   Building for a different architecture without ``unshare`` requires using an emulated schroot.

   Make sure you have followed the ``schroot`` setup for
   :ref:`sbuild` in :ref:`how-to-set-up-for-ubuntu-development` before proceeding.

   To setup an emulated schroot, use the ``mk-sbuild`` command from the
   ``ubuntu-dev-tools`` package.

   Install ``ubuntu-dev-tools``:

   .. code-block:: none

       $ sudo apt install ubuntu-dev-tools

   Then, create the schroot with the ``mk-sbuild`` command:

   .. code-block:: none

       $ mk-sbuild --arch=<ARCH> <RELEASE>

   where ``<ARCH>`` is the *target* architecture (e.g. ``arm64``).

When building with ``sbuild``, specify the target architecture with the ``--arch=`` option:

.. code-block:: none

    $ sbuild --arch=<ARCH> --dist=<RELEASE>


Building for architecture variants
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some architectures have variants (e.g. ``amd64`` has ``amd64v3``). To build for an architecture variant, specify the variant as an argument to ``--host=``:

.. code-block:: none

    $ sbuild --host=<ARCH_VARIANT> --dist=<RELEASE>

where ``<ARCH_VARIANT>`` is the architecture variant (e.g. ``amd64v3``).


Using locally built dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use a locally built a dependency in your build, specify the path to the
dependency or a directory of dependencies with the ``--extra-package`` option:

.. code-block:: none

    $ sbuild --extra-package=/path/to/dependency.deb -d <RELEASE>

To specify extra packages in your ``sbuild`` configuration file:

.. code-block:: perl

    $extra_packages = [
      # '/path/to/dependency.deb',
    ];

This way, it is possible to quickly toggle between using the locally built dependency by commenting/uncommenting the path in the configuration file.


Other build tools
-----------------

While ``sbuild`` is the recommended tool for building packages locally, there are other tools that can be used for building packages. These include:

* :manpage:`pbuilder(8)` - a tool that builds packages in a clean chroot environment, similar to ``sbuild``. It is less commonly used than ``sbuild`` but can be useful in certain situations.
* :manpage:`cowbuilder(8)` - a wrapper for ``pbuilder`` that builds packages in a clean chroot environment using copy-on-write filesystems. It is similar to ``pbuilder`` but can be faster for subsequent builds.

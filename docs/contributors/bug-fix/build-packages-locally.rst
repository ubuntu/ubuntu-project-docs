.. _how-to-build-packages-locally:

How to build packages locally
=============================

In Ubuntu, packages can be built in several ways, depending on the intended artifacts. The standard and recommended way to build packages for Ubuntu is with ``sbuild``, which builds packages in a clean environment. This ensures that the build dependencies are properly declared and that the resulting package is reproducible.

``sbuild`` can be used to build:

* **Binary-only** packages
* **Source-only** packages
* **Source** and **binary** packages

PPAs and the Archive permit exclusively **source-only** package uploads, however it is best practice to first perform a local **binary** build and fix any potential issues before uploading.

To let the Launchpad infrastructure build packages for you, see :ref:`how-to-build-packages-in-a-ppa`.


Prerequisites
-------------

Building packages locally requires a few tools to be installed and configured. The following sections will guide you through the process of setting up your environment for building packages locally with ``sbuild``.


Installing the necessary tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    $ sudo apt install devscripts sbuild mmdebstrap uidmap piuparts


Setting up ``sbuild``
~~~~~~~~~~~~~~~~~~~~~

Add your user to the ``sbuild`` group:

.. code-block:: none

    $ sudo adduser $USER sbuild

Make the required mount points for builds, logs, and scratch:

.. code-block:: none

    $ mkdir -p ~/shcroot/{build,logs,scratch}

Add a :file:`~/schroot/scratch` entry to :file:`/etc/schroot/sbuild/fstab`:

.. code-block:: none

    $HOME/schroot/scratch  /scratch          none  rw,bind  0  0

``sbuild`` reads the user specific configuration file :file:`~/.config/sbuild/config.pl` (create the file if it does not exist). Save the file with the following content, replacing ``my_user`` with your username:

.. code-block:: perl

    # Name to use as override in .changes files for the Maintainer: field
    # (optional; only uncomment if needed).
    # $maintainer_name = 'Your Full Name <your@email.com>';

    # Backend to use for chroot management. 'unshare' is the recommended
    # backend.
    $chroot_mode = 'unshare';
    $unshare_mmdebstrap_keep_tarball = 1;

    # Default distribution to build.
    $distribution = "resolute";
    # Build arch-all by default.
    $build_arch_all = 1;

    # Do not check for the presence of the build dependencies on the host
    # system, as these exist only in the unshare chroot.
    $clean_source = 0;

    # When to purge the build directory afterwards; possible values are 'never',
    # 'successful', and 'always'.  'always' is the default. It can be helpful
    # to preserve failing builds for debugging purposes.  Switch these comments
    # if you want to preserve even successful builds, and then use
    # 'schroot -e --all-sessions' to clean them up manually.
    $purge_build_directory = 'successful';
    $purge_session = 'successful';
    $purge_build_deps = 'successful';

    # Directory for chroot symlinks and sbuild logs.  Defaults to the
    # current directory if unspecified.
    $build_dir = '/home/my_user/schroot/build';

    # Directory for writing build logs to
    $log_dir = '/home/my_user/schroot/logs';

    # Key used to sign the source package. Defaults to not using any key.
    # $key_id = '';

    # don't remove this, Perl needs it:
    1;


Fetching the package source
~~~~~~~~~~~~~~~~~~~~~~~~~~~

See :ref:`how-to-get-the-source-of-a-package` for instructions on how to fetch the source of a package. You need the source to build it locally.


.. _building-with-sbuild:

Building with ``sbuild``
------------------------

Issue ``sbuild`` build commands from the :file:`debian/` sub-directory of the source package:

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

To build a **source-only** package for a specific release use the ``--source-only-changes`` option:

.. code-block:: none

    $ sbuild --source-only-changes --dist=<RELEASE>


Building both source and binary packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To build both **source** and **binary** packages for a specific release, use the ``--source`` (``-s``) option:

.. code-block:: none

    $ sbuild --source --dist=<RELEASE>

.. note::

    Launchpad rejects uploads that contains both binaries and sources. However, this is required for uploads to the Debian NEW queue. That said, uploads to Debian with binaries `do not migrate to Testing <https://lists.debian.org/debian-devel-announce/2019/07/msg00002.html>`_.


Useful options
~~~~~~~~~~~~~~

Parallel building:
  To speed up the build, set the ``parallel`` option through the ``DEB_BUILD_OPTIONS`` environment variable. For example:

  .. code-block:: none

      $ DEB_BUILD_OPTIONS="parallel=3" sbuild --chroot <RELEASE>-<ARCH>[-shm]

Shell in the chroot:
  To get a shell inside of the chroot (e.g. to investigate build failures), use the ``--build-failed-commands`` option:

  .. code-block:: none

     --build-failed-commands=%SBUILD_SHELL

Run :term:`lintian` after the build:
  .. code-block:: none

     --run-lintian [--lintian-opts="-EvIiL +pedantic"]


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

Building for a different architecture requires using an emulated schroot. To setup an emulated schroot, use the ``mk-sbuild`` command from the ``ubuntu-dev-tools`` package.

Install ``ubuntu-dev-tools``:

.. code-block:: none

    $ sudo apt install ubuntu-dev-tools

Then, create the schroot with the ``mk-sbuild`` command:

.. code-block:: none

    $ mk-sbuild --arch=<ARCH> <RELEASE>

where ``<ARCH>`` is the *target* architecture (e.g. ``arm64``).

Finally, when building with ``sbuild``, specify the target architecture with the ``--arch=`` option:

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

To use a locally built a dependency in your build, specify the path to the dependency with the ``--extra-package`` option:

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

* :manpage:`debuild(1)` - a wrapper around :manpage:`dpkg-buildpackage(1)` that provides additional features and is commonly used for building packages locally.
* :manpage:`pbuilder(8)` - a tool that builds packages in a clean chroot environment, similar to ``sbuild``. It is less commonly used than ``sbuild`` but can be useful in certain situations.
* :manpage:`cowbuilder(8)` - a wrapper for ``pbuilder`` that builds packages in a clean chroot environment using copy-on-write filesystems. It is similar to ``pbuilder`` but can be faster for subsequent builds.

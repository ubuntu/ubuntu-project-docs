.. _package-model:

Package model
=============

Because :term:`Ubuntu` is based on the community-driven :term:`Debian` project, Ubuntu uses the Debian packaging model/format.

This consists of :ref:`source packages <SourcePackages>` and :ref:`binary packages <BinaryPackages>`.

.. _SourcePackages:

Source packages
---------------

A source package contains the :term:`source <Source>` material used to build one or more binary packages.

A source package is composed of:

- a Debian Source Control (:file:`.dsc`) file,
- one or more compressed tar files, and 
- optionally additional files depending on the type and format of the source package.

The **Source Control** file contains metadata about the source package, for instance, a list of additional files, name and version, list of the binary packages it produces, dependencies, a :term:`digital signature <Signature>` and many more fields.

.. note::

   The :ref:`overview-of-debian-directory`
   article showcases the layout of an unpacked source package.

Source package formats
~~~~~~~~~~~~~~~~~~~~~~

There are multiple formats for how the source is packaged. The format of a source package is declared in the :file:`debian/source/format` file. This file should always exist. If this file can not be found, the :ref:`format 1.0 <SourcePackageFormat_1.0>` is assumed for backwards compatibility, but :manpage:`lintian(1)` will warn you about it when you try to build a source package.

.. tip::

    We strongly recommend to use the :ref:`3.0 (quilt) <SourcePackageFormat_3.0quilt>` format for new packages.

    You should only pick a different format if you **really** know what you are doing.


.. _native-source-packages:

Native source packages
^^^^^^^^^^^^^^^^^^^^^^

In most cases, a software project is packaged by external contributors called the :term:`maintainers <Maintainer>` of the package. Because the packaging is often done by a 3rd-party (from the perspective of the software project), the software to be packaged is often not designed to be packaged. In these cases the source package has to do modifications to solve specific problems for its target :term:`distribution <Distribution>`. The source package can, in these cases, be considered as its own software project, like a :term:`fork <Fork>`. Consequently, the :term:`upstream` releases and source package releases do not always align.

Native packages almost always originate from software projects designed with Debian packaging in mind and have no independent existence outside its target distribution. Consequently native packages do not differentiate between Upstream releases and source package releases. Therefore, the version identifier of a native package does not have an Debian-specific component.

For example:

- The :pkg:`debhelper` package (provides tools for building Debian packages) is a native package from Debian. Because it is designed with packaging in mind, the packaging specific files are part of the original :term:`source code <Source Code>`. The :pkg:`debhelper` developers are also maintainers of the Debian package. The Debian :pkg:`debhelper` package gets merged into the Ubuntu :pkg:`debhelper` package and has therefore a ``ubuntu`` suffix in the version identifier.

- In contrast, the `Ubuntu Bash package`_ (the default :term:`shell <Shell>` on Ubuntu) is **NOT** a native package. The `Bash software`_ originates from the :term:`GNU project <GNU>`. The Bash releases of the GNU project project will get packaged by Debian maintainers and the `Debian Bash package`_ is merged into the Ubuntu bash package by Ubuntu maintainers. The Debian and Ubuntu packages both are effectively their own separate software projects maintained by other people than the developers of the software that gets packaged. This is the process how most software is packaged on Ubuntu.

.. warning::

    Although native packages sound like the solution to use for your software project if you want to distribute your software to Ubuntu/Debian, we **strongly** recommend against using native package formats for new packages. Native packages are known to cause long-term maintenance problems.


.. _format-3-0-quilt:

Format: ``3.0 (quilt)``
^^^^^^^^^^^^^^^^^^^^^^^

A new-generation source package format that records modifications in a :manpage:`quilt(1)` :term:`patch` series within the :file:`debian/patches` directory. The patches are organized as a :term:`stack`, and you can apply, unapply, and update them by traversing the stack (push/pop). These changes are automatically applied during the extraction of the source package.

A source package in this format contains at least an original tarball (``.orig.tar.ext`` where ``ext`` can be ``gz``, ``bz2``, ``lzma``, or ``xz``) and a Debian tarball (``.debian.tar.ext``). It can also contain additional original tarballs (``.orig-component.tar.ext``), where ``component`` can only contain alphanumeric (``a-z``, ``A-Z``, ``0-9``) characters and hyphens (``-``). Optionally, each original tarball can be accompanied by a :term:`detached signature` from the upstream project (``.orig.tar.ext.asc`` and ``.orig-component.tar.ext.asc``).

For example, look at the ``hello`` package:

.. code:: none

    pull-lp-source --download-only 'hello' '2.10-3'

.. note::

    Install ``ubuntu-dev-tools`` to run the :command:`pull-lp-source`:

    .. code:: none

        sudo apt install ubuntu-dev-tools

When you now run :manpage:`ls(1)`:

.. code:: none

    ls -1 hello_*

you should see the following files:

- :file:`hello_2.10-3.dsc`: The **Debian Source Control** file of the source package.
- :file:`hello_2.10.orig.tar.gz`: The tarball containing the original source code of the upstream project.
- :file:`hello_2.10.orig.tar.gz.asc`: The detached upstream signature of :file:`hello_2.10.orig.tar.gz`.
- :file:`hello_2.10-3.debian.tar.xz`: The tarball containing the content of the Debian directory.


.. _format-3-0-native:

Format: ``3.0 (native)``
^^^^^^^^^^^^^^^^^^^^^^^^

A new-generation source package format extends the native package format defined in the :ref:`format 1.0 <SourcePackageFormat_1.0>`.

A source package in this format is a tarball (``.tar.ext`` where ``ext`` can be ``gz``, ``bz2``, ``lzma``, or ``xz``).

For example, look at the ``debhelper`` package:

.. code:: none

    pull-lp-source --download-only 'debhelper' '13.11.6ubuntu1'

When you now run :manpage:`ls(1)`:

.. code:: none

    ls -1 debhelper_*

you should see the following files:

- :file:`debhelper_13.11.6ubuntu1.dsc`:  The **Debian Source Control** file of the source package.
- :file:`debhelper_13.11.6ubuntu1.tar.xz`: The tarball containing the source code of the project.

Other examples of native source packages are:

- `ubuntu-dev-tools <https://launchpad.net/ubuntu/+source/ubuntu-dev-tools>`_
- `ubuntu-release-upgrader <https://launchpad.net/ubuntu/+source/ubuntu-release-upgrader>`_
- `dh-cargo <https://launchpad.net/ubuntu/+source/dh-cargo>`_
- `ubiquity <https://launchpad.net/ubuntu/+source/ubiquity>`_
- `subiquity <https://launchpad.net/ubuntu/+source/subiquity>`_


.. _format-1-0:

Format: ``1.0``
^^^^^^^^^^^^^^^

The original source package format. Nowadays, this format is rarely used.

A native source package in this format consists of a single ``.tar.gz`` file containing the source.

A non-native source package in this format consists of a ``.orig.tar.gz`` file (containing the upstream source) associated with a ``.diff.gz`` file (the patch containing Debian packaging modifications). Optionally, the original tarball can be accompanied by a detached Upstream signature ``.orig.tar.gz.asc``.

.. note::

   This format does not specify a patch system, which makes it harder for :term:`maintainers <Maintainer>` to track modifications. There were multiple approaches to how packages tracked patches. Therefore, the source packages of this format often contained a :file:`debian/README.source` file explaining how to use the patch system.


``3.0`` formats improvements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some of the improvements that apply to most ``3.0`` formats are:

- Support for additional compression formats: ``bzip2``, ``lzma``, and ``xz``.
- Support for multiple upstream tarballs.
- Supports inclusion of binary files.
- Debian-specific changes are no longer stored in a single ``.diff.gz``.
- The Upstream tarball does not need to be repacked to strip the Debian directory.


Other formats
^^^^^^^^^^^^^

The following formats are rarely used, experimental, or historical. You should only choose these if you know what you are doing.

- ``3.0 (custom)``: Doesn't represent an actual source package format but can be used to create source packages with arbitrary files.
- ``3.0 (git)``: An experimental format to package from a :term:`git` repository.
- ``3.0 (bzr)``: An experimental format to package from a :term:`Bazaar` repository.
- ``2.0``: The first specification of a new-generation source package format. It was never widely adopted and eventually replaced by :ref:`3.0 (quilt) <format-3-0-native>`.


``.changes`` file
~~~~~~~~~~~~~~~~~

Although technically not part of a source package -- every time a source package is built, a :file:`.changes` file is created alongside it. The :file:`.changes` file contains metadata from the Source Control file and other information (e.g. the latest changelog entry) about the source package. :term:`Archive` tools and :term:`Archive Administrators <Archive Admin>` use this data to process changes to source packages and determine the appropriate action to upload the source package to the :term:`Ubuntu Archive`.


.. _binary-packages:

Binary packages
---------------

A **binary package** is a standardized format that the :term:`package manager` (:manpage:`dpkg(1)` or :manpage:`apt(8)`) can understand to install and uninstall software on a target machine. This simplifies distributing software to a target machine and managing the software on that machine.

A Debian binary package uses the :file:`.deb` file extension and contains a set of files that will be installed on the host system and a set of files that control how the files are to be installed or uninstalled.


Further reading
---------------

- Debian policy manual: `Binary packages <https://www.debian.org/doc/debian-policy/ch-binary.html>`_
- Debian policy manual: `Source packages <https://www.debian.org/doc/debian-policy/ch-source.html>`_
- The manual page :manpage:`dpkg-source(1)`
- `Debian wiki -- 3.0 source package format <https://wiki.debian.org/Projects/DebSrc3.0>`_

.. _debhelper package: https://launchpad.net/ubuntu/+source/debhelper
.. _Bash software: https://www.gnu.org/software/bash/
.. _Debian Bash package: https://tracker.debian.org/pkg/bash
.. _Ubuntu Bash package: https://launchpad.net/ubuntu/+source/bash

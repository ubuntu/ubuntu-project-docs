.. _overview-of-debian-directory:

Overview of :file:`debian/` directory
=====================================

This article explains the different files important to the packaging of Ubuntu packages that are contained in the :file:`debian/` directory. The most important of them are:

- :file:`debian/changelog`
- :file:`debian/control`
- :file:`debian/copyright`
- :file:`debian/rules`

These are required for all packages. A number of additional files in the :file:`debian/` directory may be used to customize and configure the behavior of the package. Some of these files are discussed in this article, but this is not meant to be a complete list.


The :file:`changelog` file
--------------------------

This file is a listing of the changes made in each version. It has a specific format that gives the package name, version, distribution changes, and who made the changes at a given time. The following is a template :file:`debian/changelog`:

.. code-block:: none

    package (version) distribution; urgency=urgency
    [optional blank line(s), stripped]
      * change details
        - more change details
      * even more change details
    [optional blank line(s), stripped]
     -- maintainer name <email address>[two spaces]  date

``package`` and ``version`` are the source package name and version number, respectively.

The ``distribution`` field lists the distribution(s) in which this release should be installed.

``urgency`` describes how important an upgrade is. Its value can be one of the following: ``low``, ``medium``, ``high``, ``emergency``, or ``critical``.

The change details consist of lines indented by at least two spaces, but these conventionally are a list. Major bullet points use an asterisk ``*``, while minor bullet points are indicated by a dash ``-``.

The changelog entry ends with a line indented by one space that contains the name, email of the maintainer, and date of change. The maintainer here is the one responsible for the release, but it need not be the package maintainer.

If you have a :term:`signing key`, use the same name and email address in :file:`debian/changelog` entry as you have in your key.

.. important::

    The date should be in :rfc:`5322` format, which can be obtained by using the command :command:`date -R`. For convenience, the command :command:`dch` may be used to edit the changelog. It updates the date automatically. For further information, see :manpage:`dch(1)` and :ref:`updating-the-changelog`.

When packaging from scratch, use :command:`dch --create` (:command:`dch` is in the ``devscripts`` package) to create a standard :file:`debian/changelog`.

A sample :file:`debian/changelog` file for the :pkg:`hello` package:

.. code-block:: none

    hello (2.8-0ubuntu1) trusty; urgency=low

     * New upstream release with lots of bug fixes and feature improvements.

    -- Jane Doe <packager@example.com>  Thu, 21 Oct 2013 11:12:00 -0400

Notice that the version has ``-0ubuntu1`` appended to it. This is the distribution revision -- used so that the package can be updated (to fix bugs for example) with new uploads within the same source release version.

Ubuntu and Debian have slightly different package versioning schemes to avoid conflicting packages with the same source version. If a Debian package has been changed in Ubuntu, it has ``ubuntuX`` (where ``X`` is the Ubuntu revision number) appended to the end of the Debian version. So if the Debian :pkg:`hello` ``2.6-1`` package is changed by Ubuntu, the version string is ``2.6-1ubuntu1``. If a package for the application does not exist in Debian, then the Debian revision is ``0`` (e.g. ``2.6-0ubuntu1``).

For further information, see the `changelog section (Section 4.4) <policy-changelog_>`_ of the Debian Policy
Manual.


The :file:`control` file
------------------------

The :file:`debian/control` file contains the information that the :term:`package manager` (such as :term:`APT`) uses, build-time dependencies, maintainer information, and much more. The file consists of one or more stanzas of fields, with each stanza separated by empty lines. The fields consist of key-value pairs separated by a colon ``:``; conventionally, a single space follows the colon.

For the Ubuntu :pkg:`hello` package, the :file:`debian/control` file looks something like this:

.. code-block:: control

    Source: hello
    Section: devel
    Priority: optional
    Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
    XSBC-Original-Maintainer: Jane Doe <packager@example.com>
    Standards-Version: 4.6.2
    Build-Depends: debhelper-compat (= 13), help2man, texinfo
    Homepage: https://www.gnu.org/software/hello/

    Package: hello
    Architecture: any
    Depends: ${misc:Depends}, ${shlibs:Depends}
    Description: The classic greeting, and a good example
     The GNU hello program produces a familiar, friendly greeting. It
     allows non-programmers to use a classic computer science tool which
     would otherwise be unavailable to them. Seriously, though: this is
     an example of how to do a Debian package. It is the Debian version of
     the GNU Project's `hello world' program (which is itself an example
     for the GNU Project).

The first stanza describes the source package. It contains the following fields:

- ``Source`` (required): The name of the source package.
- ``Maintainer`` (required): The name and email of the package maintainer.

.. note::

    In Ubuntu, we set the ``Maintainer`` field to a general address because anyone can change any package (this differs from Debian where changing packages is usually restricted to an individual or a team). Packages in Ubuntu should generally have the ``Maintainer`` field set to ``Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>``.

    If the ``Maintainer`` field is modified, the old value should be saved in the ``XSBC-Original-Maintainer`` field. This can be done automatically with the ``update-maintainer`` script available in the ``ubuntu-dev-tools`` package.

- ``Uploaders``: The list of names and email addresses of co-maintainers.
- ``Section`` (recommended): The application area into which the package has been classified.
- ``Priority`` (recommended): How important the package is.
- ``Build-Depends`` fields: Lists the packages required to build the package from source.
- ``Standards-Version`` (required): The version of Debian Policy that the package complies with.
- ``Homepage``: The :term:`upstream` home page.
- :term:`Version Control System` fields:

  * ``VCS-Browser``: Web interface to browse the repository.
  * ``VCS-<type>``: The repository location. See `Version Control System fields (Section 5.6.26) <policy-vcs_>`_ of the *Debian Policy Manual* for more details.

- ``Testsuite``: A comma-separated list of values allowing test execution environments to discover packages which provide tests.
- ``Rules-Requires-Root``: Defines whether the source package requires root access during selected targets.

Each additional stanza describes a :term:`binary package` to be built. These stanzas contain the following fields:

- ``Package`` (required): The name of the binary package.
- ``Architecture`` (required): The :term:`architectures <Architecture>` supported.
- ``Section`` (recommended): The application area into which the package has been classified.
- ``Priority`` (recommended): How important the package is.
- ``Essential``: Optional boolean field to prevent the package manager from removing the package when set to ``yes``. When this field is absent, the default behavior is ``no``.
- ``Depends`` fields:
   - TODO
- ``Description`` (required): Contains a description of the binary package. This field consists of a synopsis and a long description.
- ``Homepage``: The upstream home page.
- ``Built-Using``: This field is used in cases where the package incorporates parts of other packages and relies on specific versions.
- ``Package-Type``: Indicates the type of the package, for example: ``deb`` or ``udeb``.

For further information, see the `control file section (Chapter 5) <policy-control_>`_ of the Debian Policy
Manual.


.. _the-copyright-file:

The :file:`copyright` file
--------------------------

This file gives the :term:`copyright` information for both the upstream source and the packaging. Ubuntu and `Debian Policy (Section 12.5) <policy-copyright_>`_ require that each package installs a verbatim copy of its copyright and license information to :file:`/usr/share/doc/$(package_name)/copyright`.

Generally, copyright information is found in the :file:`COPYING` file in the program source directory. This file should include such information as:

- the names of the author and the packager
- the URL from which the source came
- a copyright line with the year and copyright holder
- the text of the copyright itself

An example template:

.. code-block:: none

    Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
    Upstream-Name: Hello
    Source: ftp://ftp.example.com/pub/games

    Files: *
    Copyright: Copyright 1998 John Doe <jdoe@example.com>
    License: GPL-2+

    Files: debian/*
    Copyright: Copyright 1998 Jane Doe <packager@example.com>
    License: GPL-2+

    License: GPL-2+
    This program is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public
    License as published by the Free Software Foundation; either
    version 2 of the License, or (at your option) any later
    version.
    .
    This program is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
    PURPOSE.  See the GNU General Public License for more
    details.
    .
    You should have received a copy of the GNU General Public
    License along with this package; if not, write to the Free
    Software Foundation, Inc., 51 Franklin St, Fifth Floor,
    Boston, MA  02110-1301 USA
    .
    On Debian systems, the full text of the GNU General Public
    License version 2 can be found in the file
    `/usr/share/common-licenses/GPL-2'.

This example follows the `Machine-readable debian/copyright <DEP5_>`_ format. You are encouraged to use this format.


The :file:`rules` file
----------------------

The :file:`debian/rules` file does all the work for creating a package. It is a Makefile with targets to compile and install the application, then create the :file:`.deb` file from the installed files. It also has a target to clean all the build files, so only a source package remains after a build.

The :file:`debian/rules` file has the following targets:

- ``build`` (required)

  Configures and compiles the package.

- ``build-arch`` (required)

  Configures and compiles architecture-dependent binary packages (distinguished by not having the ``all`` value in the ``Architecture`` field).

- ``build-indep`` (required)

  Configures and compiles architecture-independent binary packages (distinguished by the ``all`` value for the ``Architecture`` field).

- ``binary`` (required)

  Builds binary package(s) from the source package. It is typically an empty target that depends on its two parts: ``binary-arch`` and ``binary-indep``.

``binary-arch`` (required)

  Builds the binary packages that are architecture-dependent.

``binary-indep`` (required)

  Builds the binary packages that are architecture-independent.

- ``clean`` (required)

  Undoes the effects of the ``build`` and ``binary`` targets, but it does not affect output files that a ``binary`` target creates in the parent directory.

- ``patch`` (optional)

  Prepares the source for editing. For example, it may unpack additional upstream archives, apply patches, etc.

A simplified version of the :file:`debian/rules` file created by :command:`dh_make` (from the :pkg:`dh-make` package):

.. code-block:: make

    #!/usr/bin/make -f
    # -*- makefile -*-

    # Uncomment this to turn on verbose mode.
    #export DH_VERBOSE=1

    %:
        dh $@

This passes every build target that :file:`debian/rules` is called with as an argument to :file:`/usr/bin/dh`, which itself calls the necessary ``dh_*`` commands.

``dh`` runs a sequence of ``debhelper`` commands. The supported sequences correspond to the targets of a :file:`debian/rules` file: ``build``, ``clean``, ``install``, ``binary-arch``, ``binary-indep``, and ``binary``. To see what commands are run in each target, run:

.. code-block:: bash

    dh binary-arch --no-act

- Commands in the ``binary-indep`` sequence are passed the ``-i`` option to ensure they only work on binary independent packages.
- Commands in the ``binary-arch`` sequences are passed the ``-a`` option to ensure they only work on architecture dependent packages.

Each ``debhelper`` command records successful runs in :file:`debian/package.debhelper.log` (which ``dh_clean`` deletes). So, ``dh`` can tell which commands have already been run, for which packages, and skip running those commands again.

Each time ``dh`` is run, it examines the log, and finds the last logged command that is in the specified sequence. It then continues with the next command in the sequence. The ``--until``, ``--before``, ``--after``, and ``--remaining`` options can override this behavior.

If :file:`debian/rules` contains a target with a name like ``override_dh_command``, then when it gets to that command in the sequence, ``dh`` runs that target from the rules file rather than running the actual command. The override target can then run the command with additional options or run entirely different commands instead.

.. note::

    To use the override feature, set ``Build-Depend`` on ``debhelper`` version 7.0.50 or above.

Look at :file:`/usr/share/doc/debhelper/examples/` and :manpage:`dh(1)` for more examples. Also see `the rules section (Section 4.9) <policy-rules_>`_ of the *Debian Policy Manual*.


Additional files
----------------


The :file:`install` file
~~~~~~~~~~~~~~~~~~~~~~~~

The :file:`install` file is used by ``dh_install`` to install files into the binary package. It has two standard use cases:

- Installing files into your package that are not handled by the upstream build system.
- Splitting a single large source package into multiple binary packages.

In the first case, the :file:`install` file should have one line per file installed, specifying both the file and the installation directory. For example, the following :file:`install` file installs the script ``example`` from the root directory of the source package to :file:`usr/bin` and a desktop file from the :file:`debian` directory to :file:`usr/share/applications`:

.. code-block:: none

    example usr/bin
    debian/example.desktop usr/share/applications

When a source package is producing multiple binary packages, ``dh`` installs the files into :file:`debian/tmp` rather than directly into :file:`debian/<package>`. Files installed into :file:`debian/tmp` can then be moved into separate binary packages using multiple :file:`$package_name.install` files. This is often done to split large amounts of architecture independent data out of architecture dependent packages and into ``Architecture: all`` packages. In this case, only the name of the files (or directories) to be installed are needed without the installation directory. For example, :file:`example.install` containing only the architecture dependent files might look like:

.. code-block:: none

    usr/bin/
    usr/lib/example/*.so

While the :file:`example-common.install` containing only the architecture independent file might look like:

.. code-block:: none

    /usr/share/doc/
    /usr/share/icons/
    /usr/share/example/
    /usr/share/locale/

This creates two binary packages, ``example`` and ``example-common``. Both would require their own stanza in :file:`debian/control`.

See :manpage:`dh_install(1)` and the `install file section (Section 5.11) <maint-install_>`_ of the Debian New
Maintainers' Guide for additional details.


The :file:`watch` file
~~~~~~~~~~~~~~~~~~~~~~

The :file:`debian/watch` file automatically checks for new upstream versions using the tool ``uscan`` found in the :pkg:`devscripts` package. The first line of the watch file must be the format version (4, at the time of this writing), while the following lines contain any URLs to parse. For example:

.. code-block:: none

    version=4
    http://ftp.gnu.org/gnu/hello/hello-(.*).tar.gz

.. note::

    For tarballs on :term:`Launchpad`, the :file:`debian/watch` file is a little more complicated (see `Question 21146 <Q21146_>`_ and `Bug 231797 <Bug231797_>`_ for why this is). In that case, use something
    like:

    .. code-block:: none

        version=4
        https://launchpad.net/flufl.enum/+download http://launchpad.net/flufl.enum/.*/flufl.enum-(.+).tar.gz

Running :command:`uscan` in the root source directory now compares the upstream version number in the :file:`debian/changelog` with the latest upstream version. If a new upstream version is found, it is automatically downloaded. For example:

.. code-block:: none

    $ uscan
    hello: Newer version (2.7) available on remote site:
        http://ftp.gnu.org/gnu/hello/hello-2.7.tar.gz
        (local version is 2.6)
    hello: Successfully downloaded updated package hello-2.7.tar.gz
        and symlinked hello_2.7.orig.tar.gz to it


For further information, see :manpage:`uscan(1)` and the `watch file section (Section 4.11) <policy-watch_>`_ of the Debian Policy
Manual.


The :file:`source/format` file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This file indicates the format of the source package. It contains a single line indicating the desired format:

- ``3.0 (native)`` for Debian native packages (no upstream version)
- ``3.0 (quilt)`` for packages with a separate upstream tarball
- ``1.0`` for packages wishing to explicitly declare the default format

.. note::

    The :file:`debian/source/format` file should always exist. If the file cannot be found, the format ``1.0`` is assumed for backwards compatibility, but :manpage:`lintian(1)` warns you about it when you try to build a source package.

It is recommended to use the newer ``3.0`` source format. It provides a number of new features:

- Support for additional compression formats: ``bzip2``, ``lzma`` and ``xz``
- Support for multiple upstream tarballs
- Not necessary to repack the upstream tarball to strip the debian directory
- Debian-specific changes are no longer stored in a single :file:`.diff.gz` but in multiple patches compatible with :command:`quilt` under :file:`debian/patches/`. The patches to be applied automatically are listed in the :file:`debian/patches/series` file.

The Debian `DebSrc3.0 <DebSrc3.0_>`_ page summarizes additional information concerning the switch to the ``3.0`` source package formats.

See :manpage:`dpkg-source(1)` and the `source/format section (Section 5.21) <maint-format_>`_  of the *Debian New Maintainers' Guide* for additional details.


Further reading
---------------

In addition to the links to the *Debian Policy Manual* in each section above, the *Debian New Maintainers' Guide* has more detailed descriptions of each file. `Chapter 4, "Required files under the debian directory" <RequiredFiles_>`_ further discusses the :file:`control`, :file:`changelog`, :file:`copyright`, and :file:`rules` files. `Chapter 5, "Other files under the debian directory" <OtherFiles_>`_ discusses additional files that may be used.

.. _policy-changelog: https://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog
.. _policy-vcs: https://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-vcs-fields
.. _policy-control: https://www.debian.org/doc/debian-policy/ch-controlfields.html
.. _policy-copyright: https://www.debian.org/doc/debian-policy/ch-docs.html#s-copyrightfile
.. _policy-rules: https://www.debian.org/doc/debian-policy/ch-source.html#s-debianrules
.. _maint-install: https://www.debian.org/doc/manuals/maint-guide/dother.en.html#install
.. _policy-watch: https://www.debian.org/doc/debian-policy/ch-source.html#s-debianwatch
.. _DebSrc3.0: https://wiki.debian.org/Projects/DebSrc3.0
.. _maint-format: https://www.debian.org/doc/manuals/maint-guide/dother.en.html#sourcef
.. _DEP5: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
.. _MaintField: https://wiki.ubuntu.com/DebianMaintainerField
.. _Q21146: https://answers.launchpad.net/launchpad/+question/21146
.. _Bug231797: https://launchpad.net/launchpad/+bug/231797
.. _RequiredFiles: https://www.debian.org/doc/manuals/maint-guide/dreq.en.html
.. _OtherFiles: https://www.debian.org/doc/manuals/maint-guide/dother.en.html

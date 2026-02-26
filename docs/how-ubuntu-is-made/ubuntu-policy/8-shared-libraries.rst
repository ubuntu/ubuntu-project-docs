.. _ubuntu-policy-shared-libraries:

Chapter 8 - Shared libraries
----------------------------

    **Editor's note**: This chapter is similar to the current Debian Policy
    Manual Chapter 8, but has some differences in its content. Review is
    suggested.

(*Modifies*: `Debian Policy Manual, Chapter 8
<https://www.debian.org/doc/debian-policy/ch-sharedlibs.html#shared-libraries>`_)

Packages containing shared libraries must be constructed with a little care to
make sure that the shared library is always available. This is especially
important for packages whose shared libraries are vitally important, such as
the C library (currently ``libc6``).

Packages involving shared libraries should be split up into several binary
packages. This section mostly deals with how this separation is to be
accomplished; rules for files within the shared library packages are in
`Libraries, Section 10.2 <ubuntu-policy-libraries>` instead.

----

8.1 Run-time shared libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 8.1
<https://www.debian.org/doc/debian-policy/ch-sharedlibs.html#run-time-shared-libraries>`_)

The run-time shared library needs to be placed in a package whose name changes
whenever the shared object version changes. [#f50]_ The most common mechanism
is to place it in a package called :pkg:`librarynamesoversion`, where
``soversion`` is the version number in the soname of the shared library
[#f51]_. Alternatively, if it would be confusing to directly append
``soversion`` to ``libraryname`` (e.g. because ``libraryname`` itself ends in a
number), you may use :pkg:`libraryname-soversion` and
:pkg:`libraryname-soversion-dev` instead.

If you have several shared libraries built from the same source tree you may
lump them all together into a single shared library package, provided that you
change all of their sonames at once (so that you don't get filename clashes if
you try to install different versions of the combined shared libraries
package).

The package should install the shared libraries under their normal names. For
example, the :pkg:`libgdbm3` package should install :file:`libgdbm.so.3.0.0` as
:file:`/usr/lib/libgdbm.so.3.0.0`. The files should not be renamed or re-linked
by any ``prerm`` or ``postrm`` scripts; :pkg:`dpkg` will take care of renaming
things safely without affecting running programs, and attempts to interfere
with this are likely to lead to problems.

Shared libraries should not be installed executable, since the dynamic linker
does not require this and trying to execute a shared library usually results in
a core dump.

The run-time library package should include the symbolic link that ``ldconfig``
would create for the shared libraries. For example, the :pkg:`libgdbm3` package
should include a symbolic link from :file:`/usr/lib/libgdbm.so.3` to
:file:`libgdbm.so.3.0.0`. This is needed so that the dynamic linker (for
example :file:`ld.so` or :file:`ld-linux.so.*`) can find the library between
the time that dpkg installs it and the time that ``ldconfig`` is run in the
``postinst`` script. [#f52]_

----

8.1.1 ``ldconfig``
^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 8.1.1
<https://www.debian.org/doc/debian-policy/ch-sharedlibs.html#ldconfig>`_)

----

8.2 Shared library support files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 8.2
<https://www.debian.org/doc/debian-policy/ch-sharedlibs.html#shared-library-support-files>`_)

----

8.3 Static libraries
~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 8.3
<https://www.debian.org/doc/debian-policy/ch-sharedlibs.html#static-libraries>`_)

----

8.4 Development files
~~~~~~~~~~~~~~~~~~~~~

    **Editor's note**: This section contradicts the current Debian
    Policy Manual regarding package names. Review is suggested.

(*Modifies*: `Debian Policy Manual, Section 8.4
<https://www.debian.org/doc/debian-policy/ch-sharedlibs.html#development-files>`_)

The development files associated to a shared library need to be placed in a
package called :pkg:`librarynamesoversion-dev`, or if you prefer only to support one
development version at a time, :pkg:`libraryname-dev`.

In case several development versions of a library exist, you may need to use
:pkg:`dpkg`'s Conflicts mechanism (see :ref:`Conflicting binary packages -
Conflicts, Section 7.4 <ubuntu-policy-conflicting-binary-packages>`) to ensure
that the user only installs one development version at a time (as different
development versions are likely to have the same header files in them, which
would cause a filename clash if both were installed).

The development package should contain a symlink for the associated shared
library without a version number. For example, the :pkg:`libgdbm-dev` package
should include a symlink from :file:`/usr/lib/libgdbm.so` to
:file:`libgdbm.so.3.0.0`. This symlink is needed by the linker (``ld``) when
compiling packages, as it will only look for :file:`libgdbm.so` when compiling
dynamically.

----

8.5 Dependencies between the packages of the same library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian:* `Debian Policy Manual, Section 8.5
<https://www.debian.org/doc/debian-policy/ch-sharedlibs.html#dependencies-between-the-packages-of-the-same-library>`_)

----

8.6 Dependencies between the library and other packages - the ``shlibs`` system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Editor's note**: ``shlibs`` has largely been superseded by the
    ``symbols`` system.

(*Modifies*: `Debian Policy Manual, Section 8.6
<https://www.debian.org/doc/debian-policy/ch-sharedlibs.html#dependencies-between-the-library-and-other-packages-the-shlibs-system>`_)

 If a package contains a binary or library which links to a shared library, we
 must ensure that when the package is installed on the system, all of the
 libraries needed are also installed. This requirement led to the creation of
 the ``shlibs`` system, which is very simple in its design: any package which
 *provides* a shared library also provides information on the package
 dependencies required to ensure the presence of this library, and any package
 which *uses* a shared library uses this information to determine the
 dependencies it requires. The files which contain the mapping from shared
 libraries to the necessary dependency information are called ``shlibs`` files.

Thus, when a package is built which contains any shared libraries, it must
provide a ``shlibs`` file for other packages to use, and when a package is
built which contains any shared libraries or compiled binaries, it must run
:ref:`dpkg-shlibdeps <ubuntu-policy-appendix-c-dkpg-shlibdeps>` on these to
determine the libraries used and hence the dependencies needed by this
package. [#f57]_

In the following sections, we will first describe where the various ``shlibs``
files are to be found, then how to use :ref:`dpkg-shlibdeps
<ubuntu-policy-appendix-c-dkpg-shlibdeps>`, and finally the ``shlibs``` file
format and how to create them if your package contains a shared library.

8.6.1 The ``shlibs`` files present on the system
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Modifies*: `Debian Policy Manual, Section 8.6.4.1
<https://www.debian.org/doc/debian-policy/ch-sharedlibs.html#the-shlibs-files-present-on-the-system>`_)

There are several places where shlibs files are found. The following list gives
them in the order in which they are read by dpkg-shlibdeps. (The first one
which gives the required information is used.)

    - :file:`debian/shlibs.local`
      This lists overrides for this package. Its use is described below (see
      :ref:`Writing the debian/shlibs.local file, Section 8.6.5
      <ubuntu-policy-writing-the-debian-shlibs-local-file>`).

    - :file:`/etc/dpkg/shlibs.override`
      This lists global overrides. This list is normally empty. It is maintained
      by the local system administrator.

    - :file:`DEBIAN/shlibs` files in the "build directory"
      When packages are being built, any :file:`debian/shlibs` files are copied
      into the control file area of the temporary build directory and given the
      name shlibs. These files give details of any shared libraries included in
      the package. [#f58]_

    - :file:`/var/lib/dpkg/info/*.shlibs`
      These are the shlibs files corresponding to all of the packages installed
      on the system, and are maintained by the relevant package maintainers.

    - :file:`/etc/dpkg/shlibs.default` This file lists any shared libraries
      whose packages have failed to provide correct ``shlibs`` files. It was
      used when the ``shlibs`` setup was first introduced, but it is now
      normally empty. It is maintained by the :pkg:`dpkg` maintainer.

8.6.2 How to use ``dpkg-shlibdeps`` and the ``shlibs`` files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Put a call to :ref:`dpkg-shlibdeps <ubuntu-policy-appendix-c-dkpg-shlibdeps>`
into your :file:`debian/rules` file. If your package contains only compiled
binaries and libraries (but no scripts), you can use a command such as:

.. code-block:: bash

   dpkg-shlibdeps debian/tmp/usr/bin/* debian/tmp/usr/sbin/* \
       debian/tmp/usr/lib/*

Otherwise, you will need to explicitly list the compiled binaries and
libraries. [#f59]_

This command puts the dependency information into the :file:`debian/substvars`
file, which is then used by ``dpkg-gencontrol``. You will need to place a
``${shlibs:Depends}`` variable in the ``Depends`` field in the control file for
this to work.

If ``dpkg-shlibdeps`` doesn't complain, you're done. If it does complain you
might need to create your own :file:`debian/shlibs.local` file, as explained
below (see `Writing the debian/shlibs.local file, Section 8.6.5
<ubuntu-policy-writing-the-debian-shlibs-local-file>`).

If you have multiple binary packages, you will need to call ``dpkg-shlibdeps``
on each one which contains compiled libraries or binaries. In such a case, you
will need to use the ``-T`` option to the :pkg:`dpkg` utilities to specify a different
substvars file.

If you are creating a udeb for use in the Debian Installer, you will need to
specify that ``dpkg-shlibdeps`` should use the dependency line of type ``udeb``
by adding ``-tudeb`` as option [#f60]_. If there is no dependency line of type
``udeb`` in the :file:`shlibs` file, ``dpkg-shlibdeps`` will fall back to the
regular dependency line.

For more details on ``dpkg-shlibdeps``, please see :ref:`dpkg-shlibdeps -
calculates shared library dependencies, Section C.1.4
<ubuntu-policy-appendix-c-dkpg-shlibdeps>` and :manpage:`dpkg-shlibdeps(1)`.

8.6.3 The ``shlibs`` File Format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Modifies*: `Debian Policy Manual, Section 8.6.4.2
<https://www.debian.org/doc/debian-policy/ch-sharedlibs.html#the-shlibs-file-format>`_)

Each ``shlibs`` file has the same format. Lines beginning with ``#`` are
considered to be comments and are ignored. Each line is of the form:

.. code-block:: none

   [type: ]library-name soname-version dependencies ...

We will explain this by reference to the example of the :pkg:`zlib1g` package,
which (at the time of writing) installs the shared library
:file:`/usr/lib/libz.so.1.1.3`.

*type* is an optional element that indicates the type of package for which the
line is valid. The only type currently in use is udeb. The colon and space
after the type are required.

*library-name* is the name of the shared library, in this case :pkg:`libz`.
(This must match the name part of the soname, see below.)

*soname-version* is the version part of the soname of the library. The soname
is the thing that must exactly match for the library to be recognized by the
dynamic linker, and is usually of the form ``name.so.major-version``, in our
example, :file:`libz.so.1`. [#f61]_ The version part is the part which comes
after ``.so.``, so in our case, it is 1.

*dependencies* has the same syntax as a dependency field in a binary package
control file. It should give details of which packages are required to satisfy
a binary built against the version of the library contained in the package. See
:ref:`Syntax of relationship fields, Section 7.1
<ubuntu-policy-syntax-of-relationship-fields>` for details.

In our example, if the first version of the :pkg:`zlib1g` package which
contained a minor number of at least ``1.3`` was ``1:1.1.3-1``, then the
``shlibs`` entry for this library could say:

.. code-block:: none

   libz 1 zlib1g (>= 1:1.1.3)

The version-specific dependency is to avoid warnings from the dynamic linker
about using older shared libraries with newer binaries.

As :pkg:`zlib1g` also provides a udeb containing the shared library, there
would also be a second line:

.. code-block:: none

   udeb: libz 1 zlib1g-udeb (>= 1:1.1.3)

8.6.4 Providing a ``shlibs`` file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Modifies*: `Debian Policy Manual, Section 8.6.4.3
<https://www.debian.org/doc/debian-policy/ch-sharedlibs.html#providing-a-shlibs-file>`_)

If your package provides a shared library, you need to create a ``shlibs`` file
following the format described above. It is usual to call this file
:file:`debian/shlibs` (but if you have multiple binary packages, you might want
to call it :file:`debian/shlibs.package` instead). Then let
:file:`debian/rules` install it in the control area:

.. code-block:: none

   install -m644 debian/shlibs debian/tmp/DEBIAN

or, in the case of a multi-binary package:

.. code-block:: none

   install -m644 debian/shlibs.package debian/package/DEBIAN/shlibs

An alternative way of doing this is to create the ``shlibs`` file in the
control area directly from :file:`debian/rules` without using a
:file:`debian/shlibs` file at all, [#f62]_ since the :file:`debian/shlibs` file
itself is ignored by ``dpkg-shlibdeps``.

As dpkg-shlibdeps reads the :file:`DEBIAN/shlibs` files in all of the binary
packages being built from this source package, all of the :file:`DEBIAN/shlibs`
files should be installed before ``dpkg-shlibdeps`` is called on any of the
binary packages.

.. _ubuntu-policy-writing-the-debian-shlibs-local-file:

8.6.5 Writing the ``debian/shlibs.local`` file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This file is intended only as a *temporary* fix if your binaries or libraries
depend on a library whose package does not yet provide a correct ``shlibs``
file.

We will assume that you are trying to package a binary ``foo``. When you try
running ``dpkg-shlibdeps`` you get the following error message (``-O`` displays
the dependency information on stdout instead of writing it to
:file:`debian/substvars`, and the lines have been wrapped for ease of reading):

.. code-block:: shell

   $ dpkg-shlibdeps -O debian/tmp/usr/bin/foo
   dpkg-shlibdeps: warning: unable to find dependency
     information for shared library libbar (soname 1,
     path /usr/lib/libbar.so.1, dependency field Depends)
   shlibs:Depends=libc6 (>= 2.2.2-2)

You can then run ``ldd`` on the binary to find the full location of the library
concerned:

.. code-block:: shell

   $ ldd foo
   libbar.so.1 => /usr/lib/libbar.so.1 (0x4001e000)
   libc.so.6 => /lib/libc.so.6 (0x40032000)
   /lib/ld-linux.so.2 => /lib/ld-linux.so.2 (0x40000000)

So the ``foo`` binary depends on the ``libbar`` shared library, but no package
seems to provide a :file:``*.shlibs`` file handling :file:`libbar.so.1` in
:file:`/var/lib/dpkg/info/`. Let's determine the package responsible:

.. code-block:: shell

     $ dpkg -S /usr/lib/libbar.so.1
     bar1: /usr/lib/libbar.so.1
     $ dpkg -s bar1 | grep Version
     Version: 1.0-1

This tells us that the :pkg:`bar1` package, version ``1.0-1``, is the one we
are using. Now we can file a bug against the :pkg:`bar1` package and create our
own :file:`debian/shlibs.local` to locally fix the problem. Including the
following line into your :file:`debian/shlibs.local` file:

.. code-block:: none

     libbar 1 bar1 (>= 1.0-1)

should allow the package build to work.

As soon as the maintainer of :pkg:`bar1` provides a correct ``shlibs`` file,
you should remove this line from your :file:`debian/shlibs.local` file. (You
should probably also then have a versioned ``Build-Depends`` on :pkg:`bar1` to
help ensure that others do not have the same problem building your package.)

----

:doc:`← Back <7-declaring-relationships>` | :doc:`Next → <9-the-operating-system>`

----

.. [#f50]
   Since it is common place to install several versions of a package that just
   provides shared libraries, it is a good idea that the library package should
   not contain any extraneous non-versioned files, unless they happen to be in
   versioned directories.
.. [#f51]
   The soname is the shared object name: it's the thing that has to match
   exactly between building an executable and running it for the dynamic linker
   to be able run the program. For example, if the soname of the library is
   :file:`libfoo.so.6`, the library package would be called :pkg:`libfoo6`.
.. [#f52]
   The package management system requires the library to be placed before the
   symbolic link pointing to it in the :file:`.deb` file. This is so that when
   :pkg:`dpkg` comes to install the symlink (overwriting the previous symlink
   pointing at an older version of the library), the new shared library is
   already in place. In the past, this was achieved by creating the library in
   the temporary packaging directory before creating the symlink.
   Unfortunately, this was not always effective, since the building of the tar
   file in the :file:`.deb` depended on the behavior of the underlying file
   system. Some file systems (such as reiserfs) reorder the files so that the
   order of creation is forgotten. Since version 1.7.0, :pkg:`dpkg` reorders
   the files itself as necessary when building a package. Thus it is no longer
   important to concern oneself with the order of file creation.
.. [#f57]
   In the past, the shared libraries linked to were determined by calling
   ``ldd``, but now ``objdump`` is used to do this. The only change this makes
   to package building is that ``dpkg-shlibdeps`` must also be run on shared
   libraries, whereas in the past this was unnecessary. The rest of this
   footnote explains the advantage that this method gives.

   We say that a binary ``foo`` directly uses a library ``libbar`` if it is
   explicitly linked with that library (that is, it uses the flag ``-lbar``
   during the linking stage). Other libraries that are needed by ``libbar`` are
   linked indirectly to ``foo``, and the dynamic linker will load them
   automatically when it loads ``libbar``. A package should depend on the
   libraries it directly uses, and the dependencies for those libraries should
   automatically pull in the other libraries.

   Unfortunately, the ``ldd`` program shows both the directly and indirectly
   used libraries, meaning that the dependencies determined included both
   direct and indirect dependencies. The use of ``objdump`` avoids this problem
   by determining only the directly used libraries.

   A good example of where this helps is the following. We could update
   ``libimlib`` with a new version that supports a new graphics format called
   ``dgf`` (but retaining the same major version number). If we used the old
   ``ldd`` method, every package that uses ``libimlib`` would need to be
   recompiled so it would also depend on ``libdgf`` or it wouldn't run due to
   missing symbols. However with the new system, packages using ``libimlib``
   can rely on ``libimlib`` itself having the dependency on ``libdgf`` and so
   they would not need rebuilding.
.. [#f58]
   An example may help here. Let us say that the source package foo generates
   two binary packages, :pkg:`libfoo2` and :pkg:`foo-runtime`. When building
   the binary packages, the two packages are created in the directories
   :file:`debian/libfoo2` and :file:`debian/foo-runtime` respectively.
   (:file:`debian/tmp` could be used instead of one of these.) Since
   :pkg:`libfoo2` provides the :pkg:`libfoo` shared library, it will require a
   ``shlibs`` file, which will be installed in
   :file:`debian/libfoo2/DEBIAN/shlibs`, eventually to become
   :file:`/var/lib/dpkg/info/libfoo2.shlibs`. Then when ``dpkg-shlibdeps`` is
   run on the executable :file:`debian/foo-runtime/usr/bin/foo-prog`, it will
   examine the :file:`debian/libfoo2/DEBIAN/shlibs` file to determine whether
   :pkg:`foo-prog`'s library dependencies are satisfied by any of the libraries
   provided by :pkg:`libfoo2`. For this reason, ``dpkg-shlibdeps`` must only be
   run once all of the individual binary packages' ``shlibs`` files have been
   installed into the build directory.
.. [#f59]
   If you are using ``debhelper``, the ``dh_shlibdeps`` program will do this
   work for you. It will also correctly handle multi-binary packages.
.. [#f60]
   ``dh_shlibdeps`` from the ``debhelper`` suite will automatically add this option if
   it knows it is processing a udeb.
.. [#f61]
    This can be determined using the command

    .. code-block:: shell

       objdump -p /usr/lib/libz.so.1.1.3 | grep SONAME
.. [#f62]
   This is what ``dh_makeshlibs`` in the ``debhelper`` suite does. If your
   package also has a udeb that provides a shared library, ``dh_makeshlibs``
   can automatically generate the udeb: lines if you specify the name of the
   udeb with the ``--add-udeb`` option.


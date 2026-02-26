Chapter 4 - Source packages
---------------------------

4.1 Standards conformance
~~~~~~~~~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 4.1
<https://www.debian.org/doc/debian-policy/ch-source.html#standards-conformance>`_)

Source packages should specify the most recent version number of this policy
document with which your package complied when it was last updated.

This information may be used to file bug reports automatically if your package
becomes too much out of date.

The version is specified in the Standards-Version control field. The format of
the ``Standards-Version`` field is described in :ref:`Standards-Version, Section 5.6.11 <ubuntu-policy-standards-version-field>`.

You should regularly, and especially if your package has become out of date,
check for the newest Policy Manual available and update your package, if
necessary. When your package complies with the new standards you should update
the ``Standards-Version`` source package field and release it. [#f14]_

----

4.2 Package relationships
~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 4.2
<https://www.debian.org/doc/debian-policy/ch-source.html#package-relationships>`_)

----

4.3 Changes to upstream sources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 4.3
<https://www.debian.org/doc/debian-policy/ch-source.html#changes-to-upstream-sources>`_)

If changes to the source code are made that are not specific to the needs of
the Ubuntu system, they should be sent to the upstream authors in whatever form
they prefer so as to be included in the upstream version of the package.

If you need to configure the package differently for Ubuntu or for Linux, and
the upstream source doesn't provide a way to do so, you should add such
configuration facilities (for example, a new ``autoconf`` test or ``#define``)
and send the patch to the upstream authors, with the default set to the way
they originally had it. You can then easily override the default in your
debian/rules or wherever is appropriate.

You should make sure that the ``configure`` utility detects the correct
architecture specification string (refer to :ref:`Architecture specification
strings, Section 11.1 <ubuntu-policy-architecture-specification>` for details).

If you need to edit a :file:`Makefile` where GNU-style ``configure`` scripts
are used, you should edit the :file:`.in` files rather than editing the
:file:`Makefile` directly. This allows the user to reconfigure the package if
necessary. You should *not* configure the package and edit the generated
:file:`Makefile`! This makes it impossible for someone else to later
reconfigure the package without losing the changes you made.

----

4.4 Ubuntu changelog: :file:`debian/changelog`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 4.4
<https://www.debian.org/doc/debian-policy/ch-source.html#debian-changelog-debian-changelog>`_)

Changes in the Ubuntu version of the package should be briefly explained in the Ubuntu changelog file :file:`debian/changelog`. [#f17]_ This includes modifications made in the Ubuntu package compared to the upstream one or the Debian package as well as other changes and updates to the package. [#f18]_

The format of the :file:`debian/changelog` allows the package building tools to
discover which version of the package is being built and find out other
release-specific information.

That format is a series of entries like this:

.. code-block:: none

     package (version) distribution(s); urgency=urgency
     	    [optional blank line(s), stripped]
       * change details
         more change details
     	    [blank line(s), included in output of dpkg-parsechangelog]
       * even more change details
     	    [optional blank line(s), stripped]
      -- maintainer name <email address>[two spaces]  date

*package* and *version* are the source package name and version number.

*distribution(s)* lists the distributions where this version should be
installed when it is uploaded - it is copied to the ``Distribution`` field in
the :file:`.changes` file. See :ref:`Distribution, Section 5.6.14
<ubuntu-policy-distribution-field>`.

*urgency* is the value for the ``Urgency`` field in the :file:`.changes` file
for the upload (see :ref:`Urgency, Section 5.6.17
<ubuntu-policy-urgency-field>`). It is not possible to specify an urgency
containing commas; commas are used to separate ``keyword=value`` settings in
the :pkg:`dpkg` changelog format (though there is currently only one useful
*keyword*, `urgency`).

The change details may in fact be any series of lines starting with at least
two spaces, but conventionally each change starts with an asterisk and a
separating space and continuation lines are indented so as to bring them in
line with the start of the text above. Blank lines may be used here to separate
groups of changes, if desired.

If this upload resolves bugs recorded in the Debian Bug Tracking System (BTS),
they may be automatically closed on the inclusion of this package into the
Debian archive by including the string: ``closes: Bug#nnnnn`` in the change
details. [#f19]_ This information is conveyed via the ``Closes`` field in the
:file:`.changes` file (see :ref:`Closes, Section 5.6.22
<ubuntu-policy-closes-field>`).

Ubuntu: If this upload resolves bugs recorded in Launchpad, they may be
automatically closed on the inclusion of this package into the Ubuntu archive
by including the string: ``LP: #nnnnn`` in the change details. [#f20]_ This
information is conveyed via the Launchpad-Bugs-Fixed field in the
:file:`.changes` file (see :ref:`Launchpad-Bugs-Fixed, Section 5.6.23
<ubuntu-policy-launchpad-bugs-fixed-field>`).

The maintainer name and email address used in the changelog should be the
details of the person uploading *this* version. They are not necessarily those
of the usual package maintainer. The information here will be copied to the
``Changed-By`` field in the :file:`.changes` file (see :ref:`Changed-By,
Section 5.6.4 <ubuntu-policy-changed-by-field>`), and then later used to send
an acknowledgement when the upload has been installed.

The *date* must be in RFC822 format [#f21]_; it must include the time zone
specified numerically, with the time zone name or abbreviation optionally
present as a comment in parentheses.

The first "title" line with the package name must start at the left hand
margin. The "trailer" line with the maintainer and date details must be
preceded by exactly one space. The maintainer details and the date must be
separated by exactly two spaces.

The entire changelog must be encoded in UTF-8.

For more information on placement of the changelog files within binary
packages, please see :ref:`Changelog files, Section 12.7
<ubuntu-policy-changelog-files>`.

----

4.5 Copyright: :file:`debian/copyright`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 4.5
<https://www.debian.org/doc/debian-policy/ch-source.html#copyright-debian-copyright>`_)

Every package must be accompanied by a verbatim copy of its copyright and
distribution license in the file :file:`/usr/share/doc/package/copyright` (see
:ref:`Copyright information, Section 12.5 <ubuntu-policy-copyright-information>` for
further details). Also see :ref:`Copyright considerations, Section 2.3
<ubuntu-policy-copyright-considerations>` for further considerations relayed to
copyrights for packages.

----

4.6 Error trapping in makefiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 4.6
<https://www.debian.org/doc/debian-policy/ch-source.html#error-trapping-in-makefiles>`_)

----

4.7 Time Stamps
~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 4.7
<https://www.debian.org/doc/debian-policy/ch-source.html#time-stamps>`_)

----

4.8 Restrictions on objects in source packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 4.8
<https://www.debian.org/doc/debian-policy/ch-source.html#restrictions-on-objects-in-source-packages>`_)

The source package may not contain any hard links [#f23]_, device special
files, sockets or setuid or setgid files. [#f24]_

----

4.9 Main building script: :file:`debian/rules`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Editor's note**: This section deviates significantly from the current
    Debian Policy Manual. Future revisions of this section are encouraged.

(*Modifies*: `Debian Policy Manual, Section 4.9
<https://www.debian.org/doc/debian-policy/ch-source.html#main-building-script-debian-rules>`_)

This file must be an executable makefile, and contains the package-specific
recipes for compiling the package and building binary package(s) from the
source.

It must start with the line ``#!/usr/bin/make -f``, so that it can be invoked
by saying its name rather than invoking make explicitly.

Since an interactive :file:`debian/rules` script makes it impossible to
auto-compile that package and also makes it hard for other people to reproduce
the same binary package, all *required targets* MUST be non-interactive. At a
minimum, required targets are the ones called by ``dpkg-buildpackage``, namely,
*clean*, *binary*, *binary-arch*, *binary-indep*, and *build*. It also follows
that any target that these targets depend on must also be non-interactive.

The targets are as follows (required unless stated otherwise):

``build``

    The ``build`` target should perform all the configuration and compilation of
    the package. If a package has an interactive pre-build configuration
    routine, the Debianized source package must either be built after this has
    taken place (so that the binary package can be built without rerunning the
    configuration) or the configuration routine modified to become
    non-interactive. (The latter is preferable if there are
    architecture-specific features detected by the configuration routine.)

    For some packages, notably ones where the same source tree is compiled in
    different ways to produce two binary packages, the ``build`` target does
    not make much sense. For these packages it is good enough to provide two
    (or more) targets (``build-a`` and ``build-b`` or whatever) for each of the
    ways of building the package, and a ``build`` target that does nothing. The
    ``binary`` target will have to build the package in each of the possible
    ways and make the binary package out of each.

    The ``build`` target must not do anything that might require root
    privilege.

    The ``build`` target may need to run the ``clean`` target first - see
    below.

    When a package has a configuration and build routine which takes a long
    time, or when the makefiles are poorly designed, or when ``build`` needs to
    run ``clean`` first, it is a good idea to ``touch build`` when the build
    process is complete. This will ensure that if :file:`debian/rules` build is
    run again it will not rebuild the whole program. [#f25]_

``build-arch`` (optional), ``build-indep`` (optional)

    A package may also provide both of the targets ``build-arch`` and
    ``build-indep``. The ``build-arch`` target, if provided, should perform all
    the configuration and compilation required for producing all
    architecture-dependant binary packages (those packages for which the body
    of the ``Architecture`` field in :file:`debian/control` is not all).
    Similarly, the ``build-indep`` target, if provided, should perform all the
    configuration and compilation required for producing all
    architecture-independent binary packages (those packages for which the body
    of the ``Architecture`` field in :file:`debian/control` is all). The
    ``build`` target should depend on those of the targets ``build-arch`` and
    ``build-indep`` that are provided in the rules file.

    If one or both of the targets ``build-arch`` and ``build-indep`` are not
    provided, then invoking :file:`debian/rules` with one of the not-provided
    targets as arguments should produce a exit status code of 2. Usually this
    is provided automatically by make if the target is missing.

    The ``build-arch`` and ``build-indep`` targets must not do anything that
    might require root privilege.

``binary``, ``binary-arch``, ``binary-indep``

    The ``binary`` target must be all that is necessary for the user to build
    the binary package(s) produced from this source package. It is split into
    two parts: ``binary-arch`` builds the binary packages which are specific to
    a particular architecture, and ``binary-indep`` builds those which are not.

    ``binary`` may be (and commonly is) a target with no commands which simply
    depends on ``binary-arch`` and ``binary-indep``.

    Both ``binary``-* targets should depend on the ``build`` target, or on the
    appropriate ``build-arch`` or ``build-indep`` target, if provided, so that
    the package is built if it has not been already. It should then create the
    relevant binary package(s), using ``dpkg-gencontrol`` to make their control
    files and ``dpkg-deb`` to build them and place them in the parent of the top
    level directory.

    Both the ``binary-arch`` and ``binary-indep`` targets *must* exist. If one
    of them has nothing to do (which will always be the case if the source
    generates only a single binary package, whether architecture-dependent or
    not), it must still exist and must always succeed.

    The *binary* targets must be invoked as root. [#f26]_

``clean``

    This must undo any effects that the ``build`` and ``binary`` targets may
    have had, except that it should leave alone any output files created in the
    parent directory by a run of a ``binary`` target.

    If a :file:`build` file is touched at the end of the ``build`` target, as
    suggested above, it should be removed as the first action that ``clean``
    performs, so that running ``build`` again after an interrupted ``clean``
    doesn't think that everything is already done.

    The ``clean`` target may need to be invoked as root if ``binary`` has been
    invoked since the last ``clean``, or if ``build`` has been invoked as root
    (since ``build`` may create directories, for example).

``get-orig-source`` (optional)

    This target fetches the most recent version of the original source package
    from a canonical archive site (via FTP or WWW, for example), does any
    necessary rearrangement to turn it into the original source tar file format
    described below, and leaves it in the current directory.

    This target may be invoked in any directory, and should take care to clean
    up any temporary files it may have left.

    This target is optional, but providing it if possible is a good idea.

``patch`` (optional)

    This target performs whatever additional actions are required to make the
    source ready for editing (unpacking additional upstream archives, applying
    patches, etc.). It is recommended to be implemented for any package where
    ``dpkg-source -x`` does not result in source ready for additional
    modification. See :ref:`Source package handling: debian/README.source, Section
    4.14 <ubuntu-policy-source-package-handling>`.

The ``build``, ``binary`` and ``clean`` targets must be invoked with the
current directory being the package's top-level directory.

Additional targets may exist in :file:`debian/rules`, either as published or
undocumented interfaces or for the package's internal use.

The architectures we build on and build for are determined by :pkg:`make`
variables using the utility ``dpkg-architecture``. You can determine the Debian
architecture and the GNU style architecture specification string for the build
machine (the machine type we are building on) as well as for the host machine
(the machine type we are building for). Here is a list of supported :pkg:`make`
variables:

    - DEB_*_ARCH (the Debian architecture)

    - DEB_*_GNU_TYPE (the GNU style architecture specification string)

    - DEB_*_GNU_CPU (the CPU part of DEB_*_GNU_TYPE)

    - DEB_*_GNU_SYSTEM (the System part of DEB_*_GNU_TYPE)

where * is either ``BUILD`` for specification of the build machine or ``HOST``
for specification of the host machine.

Backward compatibility can be provided in the rules file by setting the needed
variables to suitable default values; please refer to the documentation of
:manpage:`dpkg-architecture(1)` for details.

It is important to understand that the ``DEB_*_ARCH`` string only determines
which Debian architecture we are building on or for. It should not be used to
get the CPU or system information; the GNU style variables should be used for
that.

4.9.1 :file:`debian/rules` and ``DEB_BUILD_OPTIONS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 4.9.1
<https://www.debian.org/doc/debian-policy/ch-source.html#debian-rules-and-deb-build-options>`_)

----

.. _ubuntu-policy-variable-substitution:

4.10 Variable substitution in: :file:`debian/substvars`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 4.10
<https://www.debian.org/doc/debian-policy/ch-source.html#variable-substitutions-debian-substvars>`_)

When ``dpkg-gencontrol``, ``dpkg-genchanges`` and ``dpkg-source`` generate
control files they perform variable substitutions on their output just before
writing it. Variable substitutions have the form ``${variable}``. The optional
file :file:`debian/substvars` contains variable substitutions to be used;
variables can also be set directly from :file:`debian/rules` using the -V
option to the source packaging commands, and certain predefined variables are
also available.

The :file:`debian/substvars` file is usually generated and modified dynamically
by :file:`debian/rules` targets, in which case it must be removed by the clean
target.

See :manpage:`deb-substvars(5)` for full details about source variable
substitutions, including the format of :file:`debian/substvars`.

----

4.11 Optional upstream source location: :file:`debian/watch`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 4.11
<https://www.debian.org/doc/debian-policy/ch-source.html#upstream-source-location-debian-watch>`_)

This is an optional, recommended control file for the :pkg:`uscan` utility
which defines how to automatically scan ftp or http sites for newly available
updates of the package. This is used by http://dehs.alioth.debian.org/ and
other Debian QA tools to help with quality control and maintenance of the
distribution as a whole. 

----

4.12 Generated files list: :file:`debian/files`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 4.12
<https://www.debian.org/doc/debian-policy/ch-source.html#generated-files-list-debian-files>`_)

----

4.13 Convenience copies of code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, Renamed from "Embedded copies of code", see:* `Debian Policy Manual Section 4.13
<https://www.debian.org/doc/debian-policy/ch-source.html#embedded-copies-of-code>`_)

----

.. _ubuntu-policy-source-package-handling:

4.14 Source package handling: :file:`debian/README.source`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 4.14
<https://www.debian.org/doc/debian-policy/ch-source.html#source-package-handling-debian-readme-source>`_)

----

:doc:`← Back <3-binary-packages>` | :doc:`Next → <5-control-files>`

----

.. [#f14]
   See the file :file:`upgrading-checklist` for information about policy which
   has changed between different versions of this document.
.. [#f17]
   Mistakes in changelogs are usually best rectified by making a new changelog
   entry rather than "rewriting history" by editing old changelog entries.
.. [#f18]
   Although there is nothing stopping an author who is also the Ubuntu
   maintainer from using this changelog for all their changes, it will have to
   be renamed if the Ubuntu and upstream maintainers become different people.
   In such a case, however, it might be better to maintain the package as a
   non-native package.
.. [#f19]
   To be precise, the string should match the following Perl regular
   expression:
   ``/closes:\s*(?:bug)?\#?\s?\d+(?:,\s*(?:bug)?\#?\s?\d+)*/i``

   Then all of the bug numbers listed will be closed by the archive maintenance
   script (katie) using the version of the changelog entry.
.. [#f20]
   To be precise, the string should match the following Perl regular expression:

   ``/lp:\s+\#\d+(?:,\s*\#\d+)*/i``

   Then all of the bug numbers listed will be closed by the archive
   maintenance software using the version of the changelog entry. 
.. [#f21]
   This is generated by date -R.
.. [#f23]
   This is not currently detected when building source packages, but only when
   extracting them.

   Hard links may be permitted at some point in the future, but would require a
   fair amount of work.
.. [#f24]
   Setgid directories are allowed.
.. [#f25]
   Another common way to do this is for ``build`` to depend on ``build-stamp``
   and to do nothing else, and for the ``build-stamp`` target to do the
   building and to ``touch build-stamp`` on completion. This is especially
   useful if the build routine creates a file or directory called
   :file:`build`; in such a case, ``build`` will need to be listed as a phony
   target (i.e., as a dependency of the ``.PHONY`` target). See the
   documentation of :pkg:`make` for more information on phony targets.

.. [#f26]
   The :pkg:`fakeroot` package often allows one to build a package correctly
   even without being root.

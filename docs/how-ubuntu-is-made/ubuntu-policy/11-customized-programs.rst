.. _chapter-11-customized-programs:

Chapter 11 - Customized Programs
--------------------------------

.. _ubuntu-policy-architecture-specification:

11.1 Architecture specification strings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Chapter 11
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html>`_)

----

11.2 Daemons
~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 11.2
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#daemons>`_)

----

11.3 Using pseudo-ttys and modifying wtmp, utmp and lastlog
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 11.3
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#using-pseudo-ttys-and-modifying-wtmp-utmp-and-lastlog>`_)

----

11.4 Editors and pagers
~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 11.4
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#editors-and-pagers>`_)

----

11.5 Web servers and applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 11.5
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#web-servers-and-applications>`_)

----

11.6 Mail transport, delivery and user agents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 11.6
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#mail-transport-delivery-and-user-agents>`_)

----

11.7 News system configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 11.7
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#news-system-configuration>`_)

----

11.8 Programs for the X Window System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

11.8.1 Providing X support and package priorities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 11.8.1
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#providing-x-support-and-package-priorities>`_)

11.8.2 Packages providing an X server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 11.8.2
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#packages-providing-an-x-server>`_)

11.8.3 Packages providing a terminal emulator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 11.8.3
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#packages-providing-a-terminal-emulator>`_)

11.8.4 Packages providing a window manager
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Modifies*: `Debian Policy Manual, Section 11.8.4
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#packages-providing-a-window-manager>`_)

Packages that provide a window manager should declare in their control data
that they provide the virtual package :pkg:`x-window-manager`. They should also
register themselves as an alternative for :file:`/usr/bin/x-window-manager`,
with a priority calculated as follows:

- Start with a priority of 20.

- If the window manager supports the Debian menu system, add 20 points if this
  support is available in the package's default configuration (i.e., no
  configuration files belonging to the system or user have to be edited to
  activate the feature); if configuration files must be modified, add only 10
  points.

- If the window manager complies with `The Window Manager Specification Project
  <http://www.freedesktop.org/Standards/wm-spec>`_, written by the Free Desktop
  Group, add 40 points.

- If the window manager permits the X session to be restarted using a different
  window manager (without killing the X server) in its default configuration,
  add 10 points; otherwise add none.

11.8.5 Packages providing fonts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 11.8.5
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#packages-providing-fonts>`_)

11.8.6 Application default files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 11.8.6
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#application-default-files>`_)

11.8.7 Installation directory issues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **Editor's note:** This section is outdated and is different to the Debian
    policy. Review is suggested.

(*Modifies*: `Debian Policy Manual, Section 11.8.7
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#installation-directory-issues>`_)

Packages using the X Window System should not be configured to install files
under the :file:`/usr/X11R6/` directory. The :file:`/usr/X11R6/` directory
hierarchy should be regarded as obsolete.

Programs that use GNU ``autoconf`` and ``automake`` are usually easily
configured at compile time to use :file:`/usr/` instead of :file:`/usr/X11R6/`,
and this should be done whenever possible. Configuration files for window
managers and display managers should be placed in a subdirectory of
:file:`/etc/X11/` corresponding to the package name due to these programs'
tight integration with the mechanisms of the X Window System. Application-level
programs should use the :file:`/etc/` directory unless otherwise mandated by
policy.

The installation of files into subdirectories of
:file:`/usr/X11R6/include/X11/` and :file:`/usr/X11R6/lib/X11/` is now
prohibited; package maintainers should determine if subdirectories of
:file:`/usr/lib/` and :file:`/usr/share/` can be used instead.

Packages should install any relevant files into the directories
:file:`/usr/include/X11/` and :file:`/usr/lib/X11/`, but if they do so, they
must pre-depend on :pkg:`x11-common (>= 1:7.0.0)` [#f87]_

11.8.8 The OSF/Motif and OpenMotif libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **Editor's note:** This section is missing from the Debian policy. Review
    is suggested.

*Programs* that require the *non-DFSG-compliant* *OSF/Motif* or *OpenMotif
libraries* [#f88]_ should be compiled against and tested with LessTif (a free
re-implementation of Motif) instead. If the maintainer judges that the program
or programs do not work sufficiently well with LessTif to be distributed and
supported, but do so when compiled against Motif, then two versions of the
package should be created; one linked statically against Motif and with
``-smotif`` appended to the package name, and one linked dynamically against
Motif and with ``-dmotif`` appended to the package name.

Both Motif-linked versions are dependent upon non-DFSG-compliant software and
thus cannot be uploaded to the *main* distribution; if the software is itself
DFSG-compliant it may be uploaded to the *contrib* distribution. While known
existing versions of Motif permit unlimited redistribution of binaries linked
against the library (whether statically or dynamically), it is the package
maintainer's responsibility to determine whether this is permitted by the
license of the copy of Motif in their possession. 

11.8.9 Icon caching
^^^^^^^^^^^^^^^^^^^

Ubuntu: Packages that provide icons in a subdirectory of
:file:`/usr/share/icons` must invoke ``update-icon-caches`` on each directory
into which they installed icons. This invocation must occur in both the
``postinst`` (for all arguments) and ``postrm`` (for all arguments) scripts
[#f89]_. Doing this allows GTK+ to make use of the icon cache for efficiency
gains, while ensuring that the cache does not get out of date and cause
problems for some applications.

If ``update-icon-caches`` is not installed, this invocation may safely be
skipped. No additional dependency is necessary.

----

11.9 Perl programs and modules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 11.9
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#perl-programs-and-modules>`_)

----

11.10 Emacs lisp programs
~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 11.10
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#emacs-lisp-programs>`_)

----

11.11 Games
~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 11.11
<https://www.debian.org/doc/debian-policy/ch-customized-programs.html#games>`_)

----

:ref:`← (Chapter 10 - Files) <chapter-10-files>` | :ref:`(Chapter 12 - Documentation) → <chapter-12-documentation>`

----

.. [#f87]
   These libraries used to be all symbolic links. However, with ``X11R7``,
   :file:`/usr/include/X11` and :file:`/usr/lib/X11` are now real directories,
   and packages should ship their files here instead of in
   ``/usr/X11R6/{include,lib}/X11``. :pkg:`x11-common (>= 1:7.0.0)` is the
   package responsible for converting these symlinks into directories.
.. [#f88]
   OSF/Motif and OpenMotif are collectively referred to as "Motif" in this
   policy document.
.. [#f89]
   If you are using debhelper, the dh_icons program will do this work for you.

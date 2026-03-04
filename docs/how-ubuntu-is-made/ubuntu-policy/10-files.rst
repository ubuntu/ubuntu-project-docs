.. _chapter-10-files:

Chapter 10 - Files
------------------

10.1 Binaries
~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 10.1
<https://www.debian.org/doc/debian-policy/ch-files.html#binaries>`_)

----

10.2 Libraries
~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 10.2
<https://www.debian.org/doc/debian-policy/ch-files.html#libraries>`_)

----

10.3 Shared libraries
~~~~~~~~~~~~~~~~~~~~~

This section has moved to `Shared libraries, Chapter 8
<chapter-8-shared-libraries>`_.

----

10.4 Scripts
~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 10.4
<https://www.debian.org/doc/debian-policy/ch-files.html#scripts>`_)

----

10.5 Symbolic links
~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 10.5
<https://www.debian.org/doc/debian-policy/ch-files.html#symbolic-links>`_)

----

10.6 Device files
~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 10.6
<https://www.debian.org/doc/debian-policy/ch-files.html#device-files>`_)

Packages must not include device files in the package file tree.

If a package needs any special device files that are not included in the base
system, it must call MAKEDEV in the postinst script, after notifying the
user [#f72]_.

Packages must not remove any device files in the postrm or any other script.
This is left to the system administrator.

Ubuntu uses the serial devices :file:`/dev/ttyS*`. Programs using the old
:file:`/dev/cu*` devices should be changed to use :file:`/dev/ttyS*`.

----

10.7 Configuration files
~~~~~~~~~~~~~~~~~~~~~~~~

    **Editor's note**: This section is considerably similar to the Debian
    policy. Review is suggested.

10.7.1 Definitions
^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 10.7.1
<https://www.debian.org/doc/debian-policy/ch-files.html#configuration-files-definitions>`_)

10.7.2 Location
^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 10.7.2
<https://www.debian.org/doc/debian-policy/ch-files.html#configuration-files-location>`_)

10.7.3 Behavior
^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 10.7.3
<https://www.debian.org/doc/debian-policy/ch-files.html#configuration-files-behavior>`_)

10.7.4 Sharing configuration files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Modifies*: `Debian Policy Manual, Section 10.7.4
<https://www.debian.org/doc/debian-policy/ch-files.html#sharing-configuration-files)>`_)

Packages which specify the same file as a ``conffile`` must be tagged as
*conflicting* with each other. (This is an instance of the general rule about
not sharing files. Note that neither alternatives nor diversions are likely to
be appropriate in this case; in particular, :pkg:`dpkg` does not handle
diverted conffiles well.)

The maintainer scripts must not alter a conffile of any package, including the
one the scripts belong to.

If two or more packages use the same configuration file and it is reasonable
for both to be installed at the same time, one of these packages must be
defined as *owner* of the configuration file, i.e., it will be the package
which handles that file as a configuration file. Other packages that use the
configuration file must depend on the owning package if they require the
configuration file to operate. If the other package will use the configuration
file if present, but is capable of operating without it, no dependency need be
declared.

If it is desirable for two or more related packages to share a configuration
file *and* for all of the related packages to be able to modify that
configuration file, then the following should be done:

One of the related packages (the "owning" package) will manage the
configuration file with maintainer scripts as described in the previous
section.

The owning package should also provide a program that the other packages may
use to modify the configuration file.

The related packages must use the provided program to make any desired
modifications to the configuration file. They should either depend on the core
package to guarantee that the configuration modifier program is available or
accept gracefully that they cannot modify the configuration file if it is not.
(This is in addition to the fact that the configuration file may not even be
present in the latter scenario.)

Sometimes it's appropriate to create a new package which provides the basic
infrastructure for the other packages and which manages the shared
configuration files. (The :pkg:`sgml-base` package is a good example.)

10.7.5 User configuration files ("dotfiles")
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 10.7.5
<https://www.debian.org/doc/debian-policy/ch-files.html#user-configuration-files-dotfiles>`_)

----

10.8 Log files
~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 10.8
<https://www.debian.org/doc/debian-policy/ch-files.html#log-files>`_)

----

10.9 Permissions and owners
~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 10.9
<https://www.debian.org/doc/debian-policy/ch-files.html#permissions-and-owners>`_)

----

:ref:`← (Chapter 9 - The Operating System) <chapter-9-the-operating-system>` | :ref:`(Chapter 11 - Customized programs) → <chapter-11-customized-programs>`

----

.. [#f72]
   This notification could be done via a (low-priority) debconf message, or an
   echo (printf) statement.

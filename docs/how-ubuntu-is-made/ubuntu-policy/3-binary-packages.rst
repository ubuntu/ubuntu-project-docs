.. _chapter-3-binary-packages:

Chapter 3 - Binary packages
---------------------------

The Ubuntu distribution is based on the Debian package management system,
called :pkg:`dpkg`. Thus, all packages in the Ubuntu distribution must be
provided in the ``.deb`` file format.

----

3.1 The package name
~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 3.1
<https://www.debian.org/doc/debian-policy/ch-binary.html#the-package-name>`_)

----

3.2 The version of a package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 3.2
<https://www.debian.org/doc/debian-policy/ch-binary.html#the-version-of-a-package>`_)

3.2.1 Version numbers based on dates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Modifies*: `Debian Policy Manual, Section 3.2.1
<https://www.debian.org/doc/debian-policy/ch-binary.html#version-numbers-based-on-dates>`_)

In general, Ubuntu packages should use the same version numbers as the upstream
sources.

However, in some cases where the upstream version number is based on a date
(e.g., a development "snapshot" release) the package management system cannot
handle these version numbers without epochs. For example, dpkg will consider
"96May01" to be greater than "96Dec24".

To prevent having to use epochs for every new upstream version, the date based
portion of the version number should be changed to the following format in such
cases: "19960501", "19961224". It is up to the maintainer whether they want to
bother the upstream maintainer to change the version numbers upstream, too.

Note that other version formats based on dates which are parsed correctly by
the package management system should not be changed.

Native Debian or Ubuntu packages (i.e., packages which have been written
especially for Debian or Ubuntu) whose version numbers include dates should
always use the "YYYYMMDD" format.

----

3.3 The maintainer of a package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 3.3
<https://www.debian.org/doc/debian-policy/ch-binary.html#the-maintainer-of-a-package>`_)

Every package must have a Debian maintainer (the maintainer may be one person
or a group of people reachable from a common email address, such as a mailing
list). The maintainer is responsible for ensuring that the package is placed in
the appropriate distributions.

The maintainer must be specified in the ``Maintainer`` control field with their
correct name and a working email address. If one person maintains several
packages, they should try to avoid having different forms of their name and
email address in the ``Maintainer`` fields of those packages.

The format of the ``Maintainer`` control field is described in :ref:`Maintainer, Section 5.6.2 <ubuntu-policy-maintainer-field>`.

If the maintainer of a package quits from the Debian project, "Debian QA Group"
mailto:packages@qa.debian.org takes over the maintainer-ship of the package
until someone else volunteers for that task. These packages are called orphaned
packages. [#f8]_

Ubuntu: Packages that are modified in Ubuntu should have an Ubuntu-specific
``Maintainer field``. [#f9]_ All Ubuntu binary packages, and Ubuntu source
packages that are modified relative to Debian (that is, its version number
contains the string "ubuntu"), should have their ``Maintainer`` field adjusted as
follows:

    - If the ``Maintainer`` field contains an ``ubuntu.com`` email address, or
      one associated with an Ubuntu developer, then no modifications should be
      made.

    - If the package is in ``main`` or ``restricted``, the ``Maintainer`` field
      should be set to Ubuntu Core Developers
      mailto:ubuntu-devel-discuss@lists.ubuntu.com.

    - If the package is in ``universe`` or ``multiverse``, the ``Maintainer``
      field should be set to Ubuntu MOTU Developers
      mailto:ubuntu-motu@lists.ubuntu.com.

If the ``Maintainer`` field is modified, then the old value must be saved in a
field named ``XSBC-Original-Maintainer``. Because it is mandated and very
common, it is not necessary or appropriate to document this change in
:file:`debian/changelog`, unless it is the only change involved in the upload.

----

3.4 The description of a package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 3.4
<https://www.debian.org/doc/debian-policy/ch-binary.html#the-description-of-a-package>`_)

----

3.5 Dependencies
~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 3.5
<https://www.debian.org/doc/debian-policy/ch-binary.html#dependencies>`_)

----

3.6 Virtual packages
~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 3.6
<https://www.debian.org/doc/debian-policy/ch-binary.html#virtual-packages>`_)

----

3.7 Base system
~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 3.7
<https://www.debian.org/doc/debian-policy/ch-binary.html#base-system>`_)

----

3.8 Essential packages
~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 3.8
<https://www.debian.org/doc/debian-policy/ch-binary.html#essential-packages>`_)

----

3.9 Maintainer scripts
~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 3.9
<https://www.debian.org/doc/debian-policy/ch-binary.html#maintainer-scripts>`_)

3.9.1 Prompting in maintainer scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 3.9.1
<https://www.debian.org/doc/debian-policy/ch-binary.html#prompting-in-maintainer-scripts>`_)

----

:ref:`← (Chapter 2 - The Ubuntu Archive) Back  <chapter-2-ubuntu-archive>` | :ref:`Next (Chapter 4 - Source packages) → <chapter-4-source-packages>`

----

.. [#f8]
   The detailed procedure for doing this gracefully can be found in the Debian
   Developer's Reference, see :ref:`Related documents, Section 1.4
   <ubuntu-policy-related-documents>`.

.. [#f9]
   This is in response to a poll of Debian maintainers, documented in the
   `DebianMaintainerField <https://wiki.ubuntu.com/DebianMaintainerField>`_
   specification.

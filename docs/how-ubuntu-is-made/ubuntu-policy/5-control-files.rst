.. _chapter-5-control-files:

Chapter 5 - Control files and their fields
-------------------------------------------

(*Modifies*: `Debian Policy Manual, Chapter 5
<https://www.debian.org/doc/debian-policy/ch-controlfields.html>`_)

The package management system manipulates data represented in a common format,
known as *control data*, stored in *control files*. Control files are used for
source packages, binary packages and the :file:`.changes` files which control
the installation of uploaded files [#f32]_.

----

5.1 Syntax of control files
~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 5.1
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#syntax-of-control-files>`_)

A control file consists of one or more paragraphs of fields [#f33]_. The
paragraphs are separated by blank lines. Some control files allow only one
paragraph; others allow several, in which case each paragraph usually refers to
a different package. (For example, in source packages, the first paragraph
refers to the source package, and later paragraphs refer to binary packages
generated from the source.)

Each paragraph consists of a series of data fields; each field consists of the field name, followed by a colon and then the data/value associated with that field. It ends at the end of the (logical) line. Horizontal whitespace (spaces and tabs) may occur immediately before or after the value and is ignored there; it is conventional to put a single space after the colon. For example, a field might be:

.. code-block:: none

     Package: libc6

the field name is ``Package`` and the field value ``libc6``.

Many fields' values may span several lines; in this case each continuation line
must start with a space or a tab. Any trailing spaces or tabs at the end of
individual lines of a field value are ignored.

In fields where it is specified that lines may not wrap, only a single line of
data is allowed and whitespace is not significant in a field body. Whitespace
must not appear inside names (of packages, architectures, files or anything
else) or version numbers, or between the characters of multi-character version
relationships.

Field names are not case-sensitive, but it is usual to capitalize the field
names using mixed case as shown below.

Blank lines, or lines consisting only of spaces and tabs, are not allowed
within field values or between fields - that would mean a new paragraph.

All control files must be encoded in UTF-8.

----

5.2 Source package control files -- :file:`debian/control`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 5.2
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#debian-source-package-template-control-files-debian-control>`_)

The :file:`debian/control` contains the most vital (and version-independent)
information about the source package and about the binary packages it creates.

The first paragraph of the control file contains information about the source
package in general. The subsequent sets each describe a binary package that the
source tree builds.

The fields in the general paragraph (the first one, for the source package)
are:

- :ref:`Source <ubuntu-policy-source-field>` (mandatory)

- :ref:`Maintainer <ubuntu-policy-maintainer-field>` (mandatory)

- :ref:`Uploaders <ubuntu-policy-uploaders-field>` (optional)

- :ref:`Section <ubuntu-policy-section-field>` (recommended)

- :ref:`Priority <ubuntu-policy-priority-field>` (recommended)

- :ref:`Build-Depends et al <ubuntu-policy-build-depends>`

- :ref:`Standards-Version <ubuntu-policy-standards-version-field>` (recommended)

- :ref:`Homepage <ubuntu-policy-homepage-field>` (optional)

The fields in the binary package paragraphs are:

- :ref:`Package <ubuntu-policy-package-field>` (mandatory)

- :ref:`Architecture <ubuntu-policy-architecture-field>` (mandatory)

- :ref:`Section <ubuntu-policy-section-field>` (recommended)

- :ref:`Priority <ubuntu-policy-priority-field>` (recommended)

- :ref:`Essential <ubuntu-policy-essential-field>` (optional)

- :ref:`Depends et al <ubuntu-policy-binary-deps>` (recommended)

- :ref:`Description <ubuntu-policy-description-field>` (mandatory)

- :ref:`Homepage <ubuntu-policy-homepage-field>` (optional)

The syntax and semantics of the fields are described below.

These fields are used by ``dpkg-gencontrol`` to generate control files for
binary packages (see below), by dpkg-genchanges to generate the
:file:`.changes` file to accompany the upload, and by ``dpkg-source`` when it
creates the :file:`.dsc` source control file as part of a source archive. Many
fields are permitted to span multiple lines in :file:`debian/control` but not
in any other control file. These tools are responsible for removing the line
breaks from such fields when using fields from :file:`debian/control` to
generate other control files.

The fields here may contain variable references - their values will be
substituted by ``dpkg-gencontrol``, ``dpkg-genchanges`` or ``dpkg-source`` when
they generate output control files. See :ref:`Variable substitutions:
debian/substvars, Section 4.10 <ubuntu-policy-variable-substitution>` for
details.

In addition to the control file syntax described above, this file may also
contain comment lines starting with ``#`` without any preceding whitespace. All
such lines are ignored, even in the middle of continuation lines for a
multiline field, and do not end a multiline field.

----

5.3 Binary package control files -- :file:`DEBIAN/control`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 5.3
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#debian-binary-package-control-files-debian-control>`_)

The :file:`DEBIAN/control` file contains the most vital (and version-dependent) information about a binary package.

The fields in this file are:

- :ref:`Package <ubuntu-policy-package-field>` (mandatory)

- :ref:`Source <ubuntu-policy-source-field>`

- :ref:`Version <ubuntu-policy-version-field>` (mandatory)

- :ref:`Section <ubuntu-policy-section-field>` (recommended)

- :ref:`Priority <ubuntu-policy-priority-field>` (recommended)

- :ref:`Architecture <ubuntu-policy-architecture-field>` (mandatory)

- :ref:`Essential <ubuntu-policy-essential-field>`

- :ref:`Depends et al <ubuntu-policy-binary-deps>`

- :ref:`Installed-Size <ubuntu-policy-installed-size-field>`

- :ref:`Maintainer <ubuntu-policy-maintainer-field>` (mandatory)

- :ref:`Description <ubuntu-policy-description-field>` (mandatory)

- :ref:`Homepage <ubuntu-policy-homepage-field>`

----

5.4 Debian source control files -- :file:`.dsc`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 5.4
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#debian-source-package-control-files-dsc>`_)

This file contains a series of fields, identified and separated just like the
fields in the control file of a binary package. The fields are listed below;
their syntax is described above, in :ref:`Control files and their fields (from
old Packaging Manual), Appendix D <ubuntu-policy-appendix-d-control-files>`.

- :ref:`Format <ubuntu-policy-format-field>` (mandatory)

- :ref:`Source <ubuntu-policy-source-field>` (mandatory)

- :ref:`Version <ubuntu-policy-version-field>` (mandatory)

- :ref:`Maintainer <ubuntu-policy-maintainer-field>` (mandatory)

- :ref:`Uploaders <ubuntu-policy-uploaders-field>`

- :ref:`Binary <ubuntu-policy-binary-field>`

- :ref:`Architecture <ubuntu-policy-architecture-field>`

- :ref:`Build-Depends et al <ubuntu-policy-build-depends>`

- :ref:`Standards-Version <ubuntu-policy-standards-version-field>`
  (recommended)

- :ref:`Files <ubuntu-policy-files-field>` (mandatory)

Homepage

The source package control file is generated by ``dpkg-source`` when it builds
the source archive, from other files in the source package, described above.
When unpacking, it is checked against the files and directories in the other
parts of the source package.

----

5.5 Debian upload changes control files -- :file:`.changes`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Editor's note**: This section is significantly different to the current
    Debian Policy Manual.

(*Modifies*: `Debian Policy Manual, Section 5.5
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#debian-upload-changes-control-files-changes>`_)

The :file:`.changes` files are used by the Ubuntu archive maintenance software
to process updates to packages. They contain one paragraph which contains
information from the :file:`debian/control` file and other data about the source
package gathered via :file:`debian/changelog` and :file:`debian/rules`.

The fields in this file are:

- :ref:`Format <ubuntu-policy-format-field>` (mandatory)

- :ref:`Date <ubuntu-policy-date-field>` (mandatory)

- :ref:`Source <ubuntu-policy-source-field>` (mandatory)

- :ref:`Binary <ubuntu-policy-binary-field>` (mandatory)

- :ref:`Architecture <ubuntu-policy-architecture-field>` (mandatory)

- :ref:`Version <ubuntu-policy-version-field>` (mandatory)

- :ref:`Distribution <ubuntu-policy-distribution-field>` (mandatory)

- :ref:`Urgency <ubuntu-policy-urgency-field>` (recommended)

- :ref:`Maintainer <ubuntu-policy-maintainer-field>` (mandatory)

- :ref:`Changed-By <ubuntu-policy-changed-by-field>`

- :ref:`Description <ubuntu-policy-description-field>` (mandatory)

- :ref:`Closes <ubuntu-policy-closes-field>`

- :ref:`Launchpad-Bugs-Fixed <ubuntu-policy-launchpad-bugs-fixed-field>`

- :ref:`Changes <ubuntu-policy-changes-field>` (mandatory)

- :ref:`Files <ubuntu-policy-files-field>` (mandatory)

----

5.6 List of fields
~~~~~~~~~~~~~~~~~~

|

.. _ubuntu-policy-source-field:

5.6.1 ``Source``
^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.1
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#source>`_)

.. _ubuntu-policy-maintainer-field:

5.6.2 ``Maintainer``
^^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.2
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#maintainer>`_)

.. _ubuntu-policy-uploaders-field:

5.6.3 ``Uploaders``
^^^^^^^^^^^^^^^^^^^

(*Modifies*: `Debian Policy Manual, Section 5.6.3
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#uploaders>`_)

List of the names and email addresses of co-maintainers of the package, if any.
If the package has other maintainers beside the one named in the
:ref:`Maintainer field <ubuntu-policy-maintainer-field>`, their names and email
addresses should be listed here. The format is the same as that of the
Maintainer tag, and multiple entries should be comma separated. Currently, this
field is restricted to a single line of data. This is an optional field.

Any parser that interprets the Uploaders field in :file:`debian/control` must
permit it to span multiple lines. Line breaks in an Uploaders field that spans
multiple lines are not significant and the semantics of the field are the same
as if the line breaks had not been present.

.. _ubuntu-policy-changed-by-field:

5.6.4 ``Changed-By``
^^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.4
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#changed-by>`_)

.. _ubuntu-policy-section-field:

5.6.5 ``Section``
^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.5
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#section>`_)

.. _ubuntu-policy-priority-field:

5.6.6 ``Priority``
^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.6
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#priority>`_)

.. _ubuntu-policy-package-field:

5.6.7 ``Package``
^^^^^^^^^^^^^^^^^

(*Modifies*: `Debian Policy Manual, Section 5.6.7
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#package>`_)

The name of the binary package.

Package names must consist only of lower case letters (``a-z``), digits
(``0-9``), plus (``+``) and minus (``-``) signs, and periods (``.``). They must
be at least two characters long and must start with an alphanumeric character.

.. _ubuntu-policy-architecture-field:

5.6.8 ``Architecture``
^^^^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.8
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#architecture>`_)

.. _ubuntu-policy-essential-field:

5.6.9 ``Essential``
^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.9
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#essential>`_)

5.6.10 Package interrelationship fields: ``Depends``, ``Pre-Depends``, ``Recommends``, ``Suggests``, ``Breaks``, ``Conflicts``, ``Provides``, ``Replaces``, ``Enhances``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.10
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#package-interrelationship-fields-depends-pre-depends-recommends-suggests-breaks-conflicts-provides-replaces-enhances>`_)

.. _ubuntu-policy-standards-version-field:

5.6.11 ``Standards-Version``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(*Modifies*: `Debian Policy Manual, Section 5.6.11
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#standards-version>`_)

The most recent version of the standards (the policy manual and associated
texts) with which the package complies.

The version number has four components: major and minor version number and
major and minor patch level. When the standards change in a way that requires
every package to change the major number will be changed. Significant changes
that will require work in many packages will be signaled by a change to the
minor number. The major patch level will be changed for any change to the
meaning of the standards, however small; the minor patch level will be changed
when only cosmetic, typographical or other edits are made which neither change
the meaning of the document nor affect the contents of packages.

Thus only the first three components of the policy version are significant in
the *Standards-Version* control field, and so either these three components or
the all four components may be specified. [#f37]_

Ubuntu: Packages should not include the Ubuntu revision of the policy manual
(e.g. "ubuntu1" in "3.8.0.1ubuntu1") in their *Standards-Version* field. This
tends to create unnecessary diffs relative to Debian. For the same reason,
Ubuntu developers should not generally change the *Standards-Version* field in
packages originating in Debian.

.. _ubuntu-policy-version-field:

5.6.12 ``Version``
^^^^^^^^^^^^^^^^^^

    **Editor's note**: This subsubsection lacks additional subsubsubsections
    that exist in the current Debian Policy Manual.

(*Modifies*: `Debian Policy Manual, Section 5.6.12
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#version>`_)

The version number of a package. The format is:
[*epoch*:] *upstream_version* [-*debian_revision*]

The three components here are:

*epoch*
    This is a single (generally small) unsigned integer. It may be omitted, in
    which case zero is assumed. If it is omitted then the *upstream_version* may
    not contain any colons.

    It is provided to allow mistakes in the version numbers of older versions
    of a package, and also a package's previous version numbering schemes, to
    be left behind.

*upstream_version*
    This is the main part of the version number. It is usually the version
    number of the original ("upstream") package from which the :file:`.deb`
    file has been made, if this is applicable. Usually this will be in the same
    format as that specified by the upstream author(s); however, it may need to
    be reformatted to fit into the package management system's format and
    comparison scheme.

    The comparison behavior of the package management system with respect to
    the *upstream_version* is described below. The *upstream_version* portion
    of the version number is mandatory.

    The *upstream_version* may contain only alphanumerics [#f38]_ and the
    characters . + - : ~ (full stop, plus, hyphen, colon, tilde) and should
    start with a digit. If there is no *debian_revision* then hyphens are not
    allowed; if there is no *epoch* then colons are not allowed.

*debian_revision*
    This part of the version number specifies the version of the Ubuntu package
    based on the upstream version. It may contain only alphanumerics and the
    characters + . ~ (plus, full stop, tilde) and is compared in the same way
    as the *upstream_version* is.

    It is optional; if it isn't present then the *upstream_version* may not
    contain a hyphen. This format represents the case where a piece of software
    was written specifically to be turned into a Debian or Ubuntu package, and
    so there is only one "debianisation" of it and therefore no revision
    indication is required.

    It is conventional to restart the *debian_revision* at 1 each time the
    upstream_version is increased.

    The package management system will break the version number apart at the
    last hyphen in the string (if there is one) to determine the
    *upstream_version* and *debian_revision*. The absence of a
    *debian_revision* is equivalent to a *debian_revision* of 0.

Ubuntu: The string "ubuntu" in a version number instructs the archive
management software not to copy newer versions of the package from Debian
automatically. It should therefore be used when modifying packages relative to
Debian, taking care that the Ubuntu version number compares less than the next
expected version in Debian. For example, the first Ubuntu modification of
version ``1.0-1`` in Debian would be ``1.0-1ubuntu1``.

When comparing two version numbers, first the *epoch* of each are compared, then
the *upstream_version* if *epoch* is equal, and then *debian_revision* if
*upstream_version* is also equal. *epoch* is compared numerically. The
*upstream_version* and *debian_revision* parts are compared by the package
management system using the following algorithm:

    The strings are compared from left to right.

    First the initial part of each string consisting entirely of non-digit
    characters is determined. These two parts (one of which may be empty) are
    compared lexically. If a difference is found it is returned. The lexical
    comparison is a comparison of ASCII values modified so that all the letters
    sort earlier than all the non-letters and so that a tilde sorts before
    anything, even the end of a part. For example, the following parts are in
    sorted order from earliest to latest: ~~, ~~a, ~, the empty part, a.
    [#f39]_

    Then the initial part of the remainder of each string which consists
    entirely of digit characters is determined. The numerical values of these
    two parts are compared, and any difference found is returned as the result
    of the comparison. For these purposes an empty string (which can only occur
    at the end of one or both version strings being compared) counts as zero.

    These two steps (comparing and removing initial non-digit strings and
    initial digit strings) are repeated until a difference is found or both
    strings are exhausted.

    Note that the purpose of epochs is to allow us to leave behind mistakes in
    version numbering, and to cope with situations where the version numbering
    scheme changes. It is not intended to cope with version numbers containing
    strings of letters which the package management system cannot interpret
    (such as ``ALPHA`` or ``pre-``), or with silly orderings (the author of
    this manual has heard of a package whose versions went ``1.1, 1.2, 1.3, 1,
    2.1, 2.2, 2`` and so forth).

.. _ubuntu-policy-description-field:

5.6.13 ``Description``
^^^^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.13
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#description>`_)

.. _ubuntu-policy-distribution-field:

5.6.14 ``Distribution``
^^^^^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.14
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#distribution>`_)

.. _ubuntu-policy-date-field:

5.6.15 ``Date``
^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.15
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#date>`_)

.. _ubuntu-policy-format-field:

5.6.16 ``Format``
^^^^^^^^^^^^^^^^^

(*Modifies*: `Debian Policy Manual, Section 5.6.16
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#format>`_)

This field specifies a format revision for the file. The most current format
described in the Policy Manual is version **1.8**. The syntax of the format
value is the same as that of a package version number except that no epoch or
Debian revision is allowed - see :ref:`Version, Section 5.6.12
<ubuntu-policy-version-field>`.

.. _ubuntu-policy-urgency-field:

5.6.17 ``Urgency``
^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.17
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#urgency>`_)

.. _ubuntu-policy-changes-field:

5.6.18 ``Changes``
^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.18
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#changes>`_)

.. _ubuntu-policy-binary-field:

5.6.19 ``Binary``
^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.19
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#binary>`_)

.. _ubuntu-policy-installed-size-field:

5.6.20 ``Installed-Size``
^^^^^^^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.20
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#installed-size>`_)

.. _ubuntu-policy-files-field:

5.6.21 ``Files``
^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.21
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#files>`_)

.. _ubuntu-policy-closes-field:

5.6.22 ``Closes``
^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.22
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#closes>`_)

.. _ubuntu-policy-launchpad-bugs-fixed-field:

5.6.23 ``Launchpad-Bugs-Fixed``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A space-separated list of Launchpad bug report numbers that the upload governed
by the :file:`.changes` file closes.

.. _ubuntu-policy-homepage-field:

5.6.24 ``Homepage``
^^^^^^^^^^^^^^^^^^^

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.6.24
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#homepage>`_)

----

5.7 User-defined fields
~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 5.7
<https://www.debian.org/doc/debian-policy/ch-controlfields.html#user-defined-fields>`_)

----

:doc:`← (Chapter 4 - Source packages) Back <4-source-packages>` | :ref:`Next (Chapter 6 - Package maintainer scripts) → <chapter-6-package-maintainer-scripts>`

----

.. [#f32]
   :pkg:`dpkg`'s internal databases are in a similar format.
.. [#f33]
   The paragraphs are also sometimes referred to as stanzas.
.. [#f37]
   In the past, people specified the full version number in the
   Standards-Version field, for example "2.3.0.0". Since minor patch-level
   changes don't introduce new policy, it was thought it would be better to
   relax policy and only require the first 3 components to be specified, in
   this example "2.3.0". All four components may still be used if someone
   wishes to do so.
.. [#f38]
   Alphanumerics are ``A-Za-z0-9`` only.
.. [#f39]
   One common use of ``~`` is for upstream pre-releases. For example,
   ``1.0~beta1~svn1245`` sorts earlier than ``1.0~beta1``, which sorts earlier
   than ``1.0``.

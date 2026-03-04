.. _chapter-7-declaring-relationships:

Chapter 7 - Declaring relationships between packages
----------------------------------------------------

.. _ubuntu-policy-syntax-of-relationship-fields:

7.1 Syntax of relationship fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 7.1
<https://www.debian.org/doc/debian-policy/ch-relationships.html#syntax-of-relationship-fields>`_)

----

.. _ubuntu-policy-binary-deps:

7.2 Binary Dependencies - ``Depends``, ``Recommends``, ``Suggests``, ``Enhances``, and ``Pre-Depends``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 7.2
<https://www.debian.org/doc/debian-policy/ch-relationships.html#binary-dependencies-depends-recommends-suggests-enhances-pre-depends>`_)

----

7.3 Packages which break other packages - ``Breaks``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Editor's note**: This section should be considered outdated as it was
    written before the stable release of Debian supported ``Breaks``. The use
    of ``Breaks`` is now common in Debian and Ubuntu packages, and the issues
    mentioned in this section are no longer relevant. Consider sharing it with
    the Debian Policy Manual, and updating it to reflect the current state of
    affairs.

(*Modifies*: `Debian Policy Manual, Section 7.3
<https://www.debian.org/doc/debian-policy/ch-relationships.html#packages-which-break-other-packages-breaks>`_)

Using ``Breaks`` may cause problems for upgrades from older versions of Debian
and should not be used until the stable release of Debian supports ``Breaks``.

Ubuntu: ``Breaks`` may safely be used in Ubuntu packages, as all supported upgrade
paths to current releases involve upgrading :pkg:`dpkg` to a version that
supports ``Breaks``.

When one binary package declares that it breaks another, :pkg:`dpkg` will
refuse to allow the package which declares ``Breaks`` be installed unless the
broken package is deconfigured first, and it will refuse to allow the broken
package to be reconfigured.

A package will not be regarded as causing breakage merely because its
configuration files are still installed; it must be at least half-installed.

A special exception is made for packages which declare that they break their
own package name or a virtual package which they provide (see below): this does
not count as a real breakage.

Normally a ``Breaks`` entry will have an "earlier than" version clause; such a
``Breaks`` is introduced in the version of an (implicit or explicit) dependency
which violates an assumption or reveals a bug in earlier versions of the broken
package. This use of ``Breaks`` will inform higher-level package management
tools that broken package must be upgraded before the new one.

If the breaking package also overwrites some files from the older package, it
should use ``Replaces`` (not ``Conflicts``) to ensure this goes smoothly.

----

.. _ubuntu-policy-conflicting-binary-packages:

7.4 Conflicting binary packages - ``Conflicts``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 7.4
<https://www.debian.org/doc/debian-policy/ch-relationships.html#conflicting-binary-packages-conflicts>`_)

----

7.5 Virtual packages - ``Provides``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 7.5
<https://www.debian.org/doc/debian-policy/ch-relationships.html#virtual-packages-provides>`_)

----

7.6 Replacing files from other packages - ``Replaces``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 7.6
<https://www.debian.org/doc/debian-policy/ch-relationships.html#overwriting-files-and-replacing-packages-replaces>`_)

----

.. _ubuntu-policy-build-depends:

7.7 Declaring relationships between source packages - ``Build-Depends``, ``Build-Depends-Indep``, ``Build-Conflicts``, ``Build-Conflicts-Indep``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 7.7
<https://www.debian.org/doc/debian-policy/ch-relationships.html#relationships-between-source-and-binary-packages-build-depends-build-depends-indep-build-depends-arch-build-conflicts-build-conflicts-indep-build-conflicts-arch>`_)

----

:ref:`← (Chapter 6 - Package maintainer scripts) Back <chapter-6-package-maintainer-scripts>` | :ref:`Next (Chapter 8 - Shared libraries) → <chapter-8-shared-libraries>`

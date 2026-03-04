.. _chapter-1-about-this-manual:

Chapter 1 - About this manual
-----------------------------

1.1 Scope
~~~~~~~~~

This manual describes the policy requirements for the Ubuntu distribution. This
includes the structure and contents of the Ubuntu archive and several design
issues of the operating system, as well as technical requirements that each
package must satisfy to be included in the distribution.

This manual also describes Ubuntu policy as it relates to creating Ubuntu
packages. It is not a tutorial on how to build packages, nor is it exhaustive
where it comes to describing the behavior of the packaging system. Instead,
this manual attempts to define the interface to the package management system
that the developers have to be conversant with. [#f1]_

The footnotes present in this manual are merely informative, and are not part
of Ubuntu policy itself.

The appendices to this manual are not necessarily normative, either. Please see
`Appendix A <ubuntu-policy-appendix-a-introduction>` for more information.

In the normative part of this manual, the words *must*, *should* and *may*, and
the adjectives *required*, *recommended* and *optional*, are used to
distinguish the significance of the various guidelines in this policy document.
Packages that do not conform to the guidelines denoted by must (or required)
will generally not be considered acceptable for the Ubuntu distribution.
Non-conformance with guidelines denoted by *should* (or *recommended*) will
generally be considered a bug, but will not necessarily render a package
unsuitable for distribution. Guidelines denoted by *may* (or *optional*) are
truly optional and adherence is left to the maintainer's discretion.

These classifications are roughly equivalent to the bug severities *serious*
(for *must* or *required* directive violations), *minor*, *normal* or
*important* (for *should* or *recommended* directive violations) and *wishlist*
(for optional items). [#f2]_

Much of the information presented in this manual will be useful even when
building a package which is to be distributed in some other way or is intended
for local use only.

The Ubuntu distribution differs from its parent Debian distribution in a
number of significant ways. In this document, these are marked with the tag
*Ubuntu*:.

----

1.2 New versions of this document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Historically, this manual has been distributed via the Ubuntu package
ubuntu-policy (packages.ubuntu.com http://packages.ubuntu.com/ubuntu-policy).
Now, the policy is hosted on the Ubuntu Project Docs under the
:ref:`ubuntu-policy`.

----

1.3 Authors and Maintainers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Originally called "Debian GNU/Linux Policy Manual", this manual was initially
written in 1996 by Ian Jackson. It was revised on November 27th, 1996 by David
A. Morris. Christian Schwarz added new sections on March 15th, 1997, and
reworked/restructured it in April-July 1997. Christoph Lameter contributed the
"Web Standard". Julian Gilbey largely restructured it in 2001.

The Ubuntu branch of this manual is maintained by the `ubuntu-devel mailing
list <mailto:ubuntu-devel@lists.ubuntu.com>`_. In 2026 Simon Johnsson reduced
the branch to the differences between Debian and Ubuntu, and moved it to the
Ubuntu Project Docs.

Since September 1998, the responsibility for the contents of the Debian
version of this document lies on the `debian-policy mailing list
<mailto:debian-policy@lists.debian.org>`_. Proposals are
discussed there and inserted into policy after a certain consensus is
established.

----

.. _ubuntu-policy-related-documents:

1.4 Related documents
~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 1.4
<https://www.debian.org/doc/debian-policy/ch-scope.html#related-documents>`_)

----

1.5 Definitions
~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 1.5
<https://www.debian.org/doc/debian-policy/ch-scope.html#definitions>`_)

----

:ref:`← (Ubuntu Policy Manual) <ubuntu-policy>` | :ref:`(Chapter 2 - The Ubuntu Archive) → <chapter-2-ubuntu-archive>`

----

.. [#f1]
   Informally, the criteria used for inclusion is that the material meet one of
   the following requirements:

    :Standard interfaces:

        The material presented represents an interface to the packaging system
        that is mandated for use,     and is used by, a significant number of
        packages, and therefore should not be changed without peer review.
        Package maintainers can then rely on this interfaces not changing, and
        the package management software authors need to ensure compatibility
        with these interface definitions. (Control file and changelog file
        formats are examples.) 

    :Chosen Convention:

        If there are a number of technically viable choices that can be made,
        but one needs to select one of these options for inter-operability. The
        version number format is one example.

    Please note that these are not mutually exclusive; selected conventions
    often become parts of standard interfaces.
.. [#f2]
   Compare RFC 2119. Note, however, that these words are used in a different
   way in this document.


.. _chapter-2-ubuntu-archive:

Chapter 2 - The Ubuntu Archive
------------------------------

The Ubuntu system is maintained and distributed as a collection of *packages*.
Since there are so many of them (currently well over 60000), they are split
into *sections* and given *priorities* to simplify the handling of them.

The effort of the Ubuntu project is to build a *free* operating system, but
not every package we want to make accessible is free in our sense (see the
Ubuntu Licensing Policy, below), or may be imported/exported without
restrictions. Thus, the archive is split into areas [#f3]_ based on their licenses
and other restrictions. We also divide up packages based on whether they are
supported or not.

The aims of this are:

- to allow us to make as much software available as we can

- to allow us to encourage everyone to write free software, and

- to allow us to make it easy for people to produce CD-ROMs of our system
  without violating any licenses, import/export restrictions, or any other
  laws.

----

2.1 The Ubuntu Licensing Policy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Ubuntu Licensing Policy forms our definition of "free software". The
following guidelines apply to the *main* and *universe* categories of the
archive:

Must include source code.

    The *main* and *universe* categories have a strict and non-negotiable
    requirement that application software included in them must come with full
    source code.

Must allow modification and distribution of modified copies under the same
license.

    Just having the source code does not convey the same freedom as having the
    right to change it. Without the ability to modify software, the Ubuntu
    community cannot support software, fix bugs, translate it, or improve it.

The following additional guidelines apply to the *main*, *restricted* and
*universe* categories of the archive:

Must allow these rights to be passed on along with the software.

    You should be able to have exactly the same rights to the software as we
    do.

Must not discriminate against persons, groups or against fields of endeavour.

    The license of software included in Ubuntu can not discriminate against
    anyone or any group of users and cannot restrict users from using the
    software for a particular field of endeavour - a business for example. Thus
    we will not distribute software that is licensed "freely for non-commercial
    use".

Must not be distributed under a license specific to Ubuntu.

    The rights attached to the software must not depend on the programme's
    being part of Ubuntu system. So we will not distribute software for which
    Ubuntu has a "special" exemption or right, and we will not put our own
    software into Ubuntu and then refuse you the right to pass it on.

The following additional guidelines apply to the entire archive:

Must allow redistribution.

    Your right to sell or give away the software alone, or as part of an
    aggregate software distribution, is important because:

    - You, the user, must be able to pass on any software you have received from
      Ubuntu in either source code or compiled form.

    - While Ubuntu will not charge license fees for this distribution, you
      might well want to charge to print Ubuntu CD's, or create your own
      customized versions of Ubuntu which you sell, and should have the freedom
      to do so.

Must not require royalty payments or any other fee for redistribution or
modification.

    It's important that you can exercise your rights to this software without
    having to pay for the privilege, and that you can pass these rights on to
    other people on exactly the same basis.

Must not contaminate other software licenses.

    The license must not place restrictions on other software that is
    distributed along with it. For example, the license must not insist that
    all other programmes distributed on the same medium be free software.

May require source modifications to be distributed as patches.

    In some cases, software authors are happy for us to distribute their
    software and modifications to their software, as long as the two are
    distributed separately, so that people always have a copy of their pristine
    code. We are happy to respect this preference. However, the license must
    explicitly permit distribution of software built from modified source code.

The "GPL," "BSD," and "Artistic" licenses are examples of licenses that we
consider *free*.

Ubuntu contains licensed and copyrighted works that are not application
software. For example, the default Ubuntu installation includes documentation,
images, sounds, video clips and firmware. The Ubuntu community will make
decisions on the inclusion of these works on a case-by-case basis, ensuring
that these works do not restrict our ability to make Ubuntu available free of
charge, and that Ubuntu remains re-distributable by you. 

----

2.2 Archive Areas
~~~~~~~~~~~~~~~~~

|

2.2.1 The main archive area
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every package in *main* must comply with the Ubuntu Licensing Policy.

In addition, the packages in *main*:

- must not require a package outside of *main* for compilation or execution
  (thus, the package must not declare a "Depends", "Recommends", or
  "Build-Depends" relationship on a non-*main* package),

- must not be so buggy that we refuse to support them, and

- must meet all policy requirements presented in this manual.

2.2.2 The restricted archive area
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every package in *restricted* must comply with the Ubuntu Licensing Policy,
with the exceptions that source code may not be available and that modification
may not be permitted.

In addition, the packages in *restricted*:

- must not be so buggy that we refuse to support them, and
- must meet all policy requirements presented in this manual that it is
  possible for them to meet. [#f4]_

The Ubuntu team recognises that many users have vital hardware in their
computer that requires drivers that are currently only available in binary
format. We urge all hardware vendors to insist that their suppliers provide
open source drivers for their components, but we recognise that in some cases
binary drivers are the only way to make your hardware work. As a result,
Ubuntu includes several of these drivers on the CD and in the repository,
clearly separated from the rest of the software by being placed in the
*restricted* archive area.

Binary drivers are a poor choice, if you have a choice. Without source code,
Ubuntu cannot support this software, we only provide it for users who require
it to be able to run the Free Software we provide in main. Also, we cannot
make binary drivers available on other architectures (such as the Mac or IPAQ)
if we don't have the ability to port the software source code ourselves. If
your hardware is fully supported with open source drivers you can simply
remove the *restricted* archive area, and we would encourage you to do so.

The *restricted* archive area may not include application software, only
hardware drivers.

2.2.3 The universe archive area
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every package in universe must comply with the Ubuntu Licensing Policy.

Packages in the *universe* archive area are not supported by the core Ubuntu
developers and Canonical Ltd. Packages may be moved between *main* and
*universe* as their support status changes.

In addition, the packages in *universe*:

- must not require a package outside of *main* and *universe* for
  compilation or execution (thus, the package must not declare a "Depends",
  "Recommends", or "Build-Depends" relationship on a non-*main* and
  non-*universe* package), and

- must meet all policy requirements presented in this manual.


2.2.4 The multiverse archive area
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every package in *multiverse* must comply with the Ubuntu Licensing Policy, with
the exceptions that source code may not be available, that modification may
not be permitted, that rights may not be passed on along with the software,
that they may discriminate against persons, groups or fields of endeavour, and
that their license may be specific to Ubuntu. (In other words, they must be
redistributable without a fee and must not contaminate other software
licenses.)

Packages must be placed in *multiverse* if they are not compliant with the parts
of the Ubuntu Licensing Policy that cover other categories of the archive, or
if they are encumbered by patents or other legal issues that make their
distribution problematic.

Packages in the *multiverse* archive area are not supported by the core Ubuntu
developers and Canonical Ltd.

In addition, the packages in *multiverse*:

- must not be so buggy that we refuse to support them, and

- must meet all policy requirements presented in this manual that it is
  possible for them to meet. [#f5]_

----

.. _ubuntu-policy-copyright-considerations:

2.3 Copyright considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every package must be accompanied by a verbatim copy of its copyright and
distribution license in the file :file:`/usr/share/doc/package/copyright` (see
:ref:`Copyright information, Section 12.5
<ubuntu-policy-copyright-information>` for further details).

We reserve the right to restrict files from being included anywhere in our
archives if

- their use or distribution would break a law,

- there is an ethical conflict in their distribution or use,

- we would have to sign a license for them, or

- their distribution would conflict with other project policies.

Programs whose authors encourage the user to make donations are fine for the
main distribution, provided that the authors do not claim that not donating is
immoral, unethical, illegal or something similar; in such a case they must go
in *multiverse*.

Packages whose copyright permission notices (or patent problems) do not even
allow redistribution of binaries only, and where no special permission has been
obtained, must not be placed on the Ubuntu FTP site and its mirrors at all.

Note that under international copyright law (this applies in the United States,
too), *no* distribution or modification of a work is allowed without an
explicit notice saying so. Therefore a program without a copyright notice *is*
copyrighted and you may not do anything to it without risking being sued!
Likewise if a program has a copyright notice but no statement saying what is
permitted then nothing is permitted.

Many authors are unaware of the problems that restrictive copyrights (or lack
of copyright notices) can cause for the users of their supposedly-free
software. It is often worthwhile contacting such authors diplomatically to ask
them to modify their license terms. However, this can be a politically
difficult thing to do and you should ask for advice on the ``ubuntu-archive
mailing`` list first, as explained below.

When in doubt about a copyright, send mail to
mailto:ubuntu-archive@lists.ubuntu.com. Be prepared to provide us with the
copyright statement. Software covered by the GPL, public domain software and
BSD-like copyrights are safe; be wary of the phrases "commercial use
prohibited" and "distribution restricted". 

----

2.4 Sections
~~~~~~~~~~~~

The packages in the archive areas *main*, *restricted*, *universe* and
*multiverse* are grouped further into sections to simplify handling.

The archive area and section for each package should be specified in the
package's ``Section`` control record (see :ref:`Section, Section 5.6.5
<ubuntu-policy-section-field>`). However, the maintainer of the Ubuntu
archive may override this selection to ensure the consistency of the Ubuntu
distribution. The ``Section`` field should be of the form:

    - section if the package is in the main archive area, 
    - area/section if the
      package is in the restricted, universe or multiverse archive areas.
      [#f6]_

The Ubuntu archive maintainers provide the authoritative list of sections. At
present, they are: ``admin``, ``cli-mono``, ``comm``, ``database``, ``devel``, ``debug``, ``doc``, ``editors``,
``electronics``, ``embedded``, ``fonts``, ``games``, ``gnome``, ``graphics``, ``gnu-r``, ``gnustep``, ``hamradio``,
``haskell``, ``httpd``, ``interpreters``, ``java``, ``kde``, ``kernel``, ``libs``, ``libdevel``, ``lisp``,
``localization``, ``mail``, ``math``, ``metapackages``, ``misc``, ``net``, ``news``, ``ocaml``, ``oldlibs``,
``otherosfs``, ``perl``, ``php``, ``python``, ``ruby``, ``science``, ``shells``, ``sound``, ``tex``, ``text``, ``utils``,
``vcs``, ``video``, ``web``, ``x11``, ``xfce``, ``zope``.

Ubuntu: The *metapackages* section exists for the benefit of package management
tools. When removing a package in that section, its dependencies will not be
automatically considered for removal by tools which track the distinction
between packages that were installed explicitly and packages that were only
installed to satisfy dependencies. 

----

2.5 Priorities
~~~~~~~~~~~~~~

Each package should have a priority value, which is included in the package's
*control record* (see :ref:`Priority, Section 5.6.6
<ubuntu-policy-priority-field>`). This information is used by the Ubuntu
package management tools to separate high-priority packages from less-important
packages.

The following *priority* levels are recognized by the Ubuntu package management
tools.

``required``
    Packages which are necessary for the proper functioning of the system
    (usually, this means that dpkg functionality depends on these packages).
    Removing a ``required`` package may cause your system to become totally
    broken and you may not even be able to use :pkg:`dpkg` to put things back,
    so only do so if you know what you are doing. Systems with only the
    required packages are probably unusable, but they do have enough
    functionality to allow the sysadmin to boot and install more software.

``important``
    Important programs, including those which one would expect to find on any
    Unix-like system. If the expectation is that an experienced Unix person who
    found it missing would say "What on earth is going on, where is foo?", it
    must be an important package. [#f7]_ Other packages without which the
    system will not run well or be usable must also have priority important.
    This does not include Emacs, the X Window System, TeX or any other large
    applications. The important packages are just a bare minimum of
    commonly-expected and necessary tools.

``standard``
    These packages provide a reasonably small but not too limited
    character-mode system. This is what will be installed by default if the
    user doesn't select anything else. It doesn't include many large
    applications.

``optional``
    (In a sense everything that isn't required is optional, but that's not what
    is meant here.) This is all the software that you might reasonably want to
    install if you didn't know what it was and don't have specialized
    requirements. This is a much larger system and includes the X Window
    System, a full TeX distribution, and many applications. Note that optional
    packages should not conflict with each other.

``extra``
    This contains all packages that conflict with others with required,
    important, standard or optional priorities, or are only likely to be useful
    if you already know what they are or have specialized requirements (such as
    packages containing only detached debugging symbols).

    Packages must not depend on packages with lower priority values (excluding
    build-time dependencies). In order to ensure this, the priorities of one or
    more packages may need to be adjusted.

----

:ref:`← (Chapter 1 - About this manual) Back  <chapter-1-about-this-manual>` | :ref:`Next (Chapter 3 - Binary packages) → <chapter-3-binary-packages>`

----

.. [#f3]
   The Ubuntu archive software uses the term "component" internally and in the
   Release file format to refer to the division of an archive. The Debian
   Social Contract simply refers to "areas." This document uses terminology
   similar to the Social Contract.

.. [#f4]
   It is possible that there are policy requirements which the package is
   unable to meet, for example, if the source is unavailable. These situations
   will need to be handled on a case-by-case basis.

.. [#f5]
   It is possible that there are policy requirements which the package is
   unable to meet, for example, if the source is unavailable. These situations
   will need to be handled on a case-by-case basis.

.. [#f6]
   Packages that originally came from the Debian archive will often not have
   ``Section`` fields matching the archive area selected for them in Ubuntu.
   There is no need to change the package just for this; the maintainers of the
   Ubuntu archive can and will override its placement.

.. [#f7]
   This is an important criterion because we are trying to produce, amongst
   other things, a free Unix.

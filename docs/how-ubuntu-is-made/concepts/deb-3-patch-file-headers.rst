.. _dep-3-patch-file-headers:

DEP 3 - patch file headers
==========================

This article provides a brief overview of the `Debian Enhancement Proposal 3
Specification (DEP-3) -- Patch Tagging Guidelines <DEP3Spec_>`_ for ``.patch``
file headers and shows :ref:`sample-dep-3-compliant-headers`.

For the full, authoritative specification of each field -- including
``Description``, ``Origin``, ``Bug-<Vendor>``, ``Forwarded``, ``Author``,
``Reviewed-by``, ``Last-Update``, and ``Applied-Upstream`` -- refer to
the `DEP-3 Specification <DEP3Spec_>`_ on the Debian wiki. The Debian
specification is the canonical source and is updated independently; this page
only provides Ubuntu-specific context and examples.

.. note::

   Keeping the canonical field definitions on the Debian side avoids
   duplication and ensures Ubuntu packagers always reference the latest
   version of the spec.


.. _sample-dep-3-compliant-headers:

Sample DEP-3 compliant headers
------------------------------

A patch cherry-picked from upstream:

.. code-block:: none

    From: Ulrich Drepper <drepper@redhat.com>
    Subject: Fix regex problems with some multi-bytes characters

    * posix/bug-regex17.c: Add testcases.
    * posix/regcomp.c (re_compile_fastmap_iter): Rewrite COMPLEX_BRACKET
    handling.

    Origin: upstream, http://sourceware.org/git/?p=glibc.git;a=commitdiff;h=bdb56bac
    Bug: http://sourceware.org/bugzilla/show_bug.cgi?id=9697
    Bug-Debian: http://bugs.debian.org/510219

A patch created by the Debian maintainer John Doe, which got forwarded and rejected:

.. code-block:: none

    Description: Use FHS compliant paths by default
    Upstream is not interested in switching to those paths.
    .
    But we will continue using them in Debian nevertheless to comply with
    our policy.
    Forwarded: http://lists.example.com/oct-2006/1234.html
    Author: John Doe <johndoe-guest@users.alioth.debian.org>
    Last-Update: 2006-12-21

A vendor specific patch not meant for upstream submitted on the BTS by a Debian developer:

.. code-block:: none

    Description: Workaround for broken symbol resolving on mips/mipsel
    The correct fix will be done in etch and it will require toolchain
    fixes.
    Forwarded: not-needed
    Origin: vendor, http://bugs.debian.org/cgi-bin/bugreport.cgi?msg=80;bug=265678
    Bug-Debian: http://bugs.debian.org/265678
    Author: Thiemo Seufer <ths@debian.org>

A patch submitted and applied upstream:

.. code-block:: none

    Description: Fix widget frobnication speeds
    Frobnicating widgets too quickly tended to cause explosions.
    Forwarded: http://lists.example.com/2010/03/1234.html
    Author: John Doe <johndoe-guest@users.alioth.debian.org>
    Applied-Upstream: 1.2, https://git.example.com/frobnicator/commit/123
    Last-Update: 2010-03-29


Further reading
---------------

- `DEP-3 Specification -- Patch Tagging Guidelines <DEP3Spec_>`_

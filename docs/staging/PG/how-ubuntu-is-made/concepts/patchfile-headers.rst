.. _dep-3-patch-file-headers:

DEP 3 - patch file headers
==========================

This article lists and briefly explains standard fields of the 
`Debian Enhancement Proposal 3 Specification (DEP-3) -- Patch Tagging Guidelines <DEP3Spec_>`_
for ``.patch`` file headers and also shows :ref:`SampleDEP3CompliantHeaders`.

Standard fields
---------------

``Description`` or ``Subject`` |required|
    This obligatory field contains at least a short description on the first
    line. When ``Subject`` is used, it is expected that the long description is
    outside of the structured fields. With ``Description`` it is possible to
    embed them in the field using continuation lines.

    In both cases, the long description allows for a more verbose explanation
    of the patch and its history.

    This field should explain why the patch is vendor-specific (e.g., branding patch)
    when that is the case. If the patch has been submitted :term:`upstream` but
    has been rejected, the description should also document why it's kept and what
    were the reasons for the reject.

    It's recommended to keep each line shorter than 80 characters.

``Origin`` |required|
    .. note::
        If the ``Author`` field is present, the ``Origin`` field can be omitted and it's
        assumed that the patch comes from its author.
    
    This field should document the origin of the patch. In most cases, it should be a
    simple URL. For patches backported/taken from upstream, it should point into the
    upstream :term:`VCS` web interface when possible, otherwise it can simply list the relevant
    commit identifier (it should be prefixed with "commit:" in that case).
    For other cases, one should simply indicate the URL where the patch was taken from
    (mailing list archives, distribution :term:`bug tracking system`, etc.) when possible.

    The field can be optionally prefixed with a single keyword followed by a comma and a
    space to categorize the origin. The allowed keywords are:
    
    - ``upstream`` in the case of a patch cherry-picked from the upstream VCS,
    - ``backport`` in the case of an upstream patch that had to be modified to apply on the current version,
    - ``vendor`` for a patch created by Debian or another distribution vendor, or
    - ``other`` for all other kind of patches.

    In general, a user-created patch grabbed from a :term:`Bug Tracking System` should be
    categorized as `other`. When copying a patch from another vendor, the meta-information
    (and hence this field) should be kept if present, or created if necessary with a
    `vendor` origin.

``Bug-<Vendor>`` or ``Bug`` |optional|
    It contains one URL pointing to the related bug (possibly fixed by the patch).
    The ``Bug`` field is reserved for the bug URL of the upstream bug tracker.
    Those fields can be used multiple times if several bugs are concerned.

    The ``<Vendor>`` name is explicitly encoded in the field name so that vendors
    can share patches among them without having to update the meta-information in
    most cases. The upstream bug URL is special cased because it's the central point
    of cooperation and it must be easily distinguishable among all the bug URLs.

``Forwarded`` |optional|
    Any value other than ``no`` or ``not-needed`` means that the patch has been
    forwarded upstream. Ideally the value is an URL proving that it has been
    forwarded and where one can find more information about its inclusion status.

    If the field is missing, its implicit value is ``yes`` if the ``Bug`` field is
    present, otherwise it's ``no``. The field is really required only if the patch
    is vendor specific, in that case its value should be ``not-needed`` to indicate
    that the patch must not be forwarded upstream (whereas ``no`` simply means that
    it has not yet been done).

``Author`` or ``From`` |optional|
    This field can be used to record the name and email of the patch author
    (e.g., ``John Bear <foo@example.com>``). Its usage is recommended when the patch
    author did not add copyright notices for his work in the patch itself.
    It's also a good idea to add this contact information when the patch needs to be
    maintained over time because it has very little chance of being integrated upstream.
    
    This field can be used multiple times if several people authored the patch.

``Reviewed-by`` or ``Acked-by`` |optional|
    This field can be used to document the fact that the patch has been reviewed and
    approved by someone. It should list their name and email in the standard format
    (e.g., ``John Bear <foo@example.com>``).
    
    This field can be used multiple times if several people reviewed the patch.

``Last-Update`` |optional|
    This field can be used to record the date when the meta-information was last updated.
    It should use the ISO date format ``YYYY-MM-DD``.

``Applied-Upstream`` |optional|
    This field can be used to document the fact that the patch has been applied upstream.
    
    It may contain the upstream version expected to contain this patch, or the URL
    or commit identifier of the upstream commit (with commit identifiers prefixed with
    ``commit:``, as in the ``Origin`` field), or both separated by a comma and a space.

.. _SampleDEP3CompliantHeaders:

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
    Applied-Upstream: 1.2, http://bzr.example.com/frobnicator/trunk/revision/123
    Last-Update: 2010-03-29

Resources
---------

- `DEP-3 Specification -- Patch Tagging Guidelines <DEP3Spec_>`_

.. |required| replace:: :bdg-primary:`required`
.. |optional| replace:: :bdg-secondary:`optional`

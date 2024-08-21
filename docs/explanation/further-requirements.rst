Reasons for requirements
------------------------

Preconditions
~~~~~~~~~~~~~

.. _explanation-devel-first:

Development release fixed first
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a stable release is fixed but the development release is not, then
after the development release becomes a stable release, users upgrading
would face an unexpected regression. Therefore, it is a general
requirement that the development release is fixed before fixes are
backported to the stable releases. Equivalently for new upstream
releases, this (or a newer) release must be in the development release.

It is also, in general, not appropriate to release updates for stable
systems without first testing them in the current development branch.

One exception to this general rule is the case where the development
release is not yet open. There can sometimes be a delay between the
release of the most recent version of Ubuntu and the opening for
development of the next version. Provided they are important enough,
stable release updates should not and do not need to wait for the
development release to open, as long as the development release upload
is prepared and ready.

.. _explanation-newer-releases:

Newer Releases
^^^^^^^^^^^^^^

If a bug is being fixed in a particular stable release, we would like
for all subsequent releases that are still supported to also be fixed at
the same time. This is to prevent a user from facing a regression when
they upgrade to a newer release.

Exceptions:

The following two exceptions apply to bugfixes, but do not apply to
hardware enablement or new features.

1. **When there are two subsequent interim releases:** if there are two
   subsequent interim releases that are both current, then, as a
   compromise, additionally fixing only the most recent one is
   acceptable. Rationale: a user facing this class of regression will at
   least have an upgrade path available to them that fixes it.
2. **When you don't want to fix a subsequent interim release at all:**
   we recognise that making it a hard requirement to fix all subsequent
   interim releases would mandate more work, and that a team may not
   have the resources available to fix and verify (say) an LTS as well
   as a subsequent interim release that has fewer users. We wouldn't
   want to block a fix from landing at all, so we are not making it a
   hard requirement that subsequent interim releases be fixed. However,
   we strongly recommend that subsequent interim releases be fixed, and
   it is our expectation that normally uploaders will ensure this. If
   you are unable to do this, then please: 1) create and mark bug tasks
   against the subsequent affected releases "Won't Fix"; and 2)
   explicitly state in the bug that you are deliberately seeking to fix
   a release without fixing the subsequent releases. An SRU team member
   may then accept your upload at their discretion and on a case-by-case
   basis. If this is not done, then uploaders should expect an SRU
   review round trip while your intentions are clarified.

See also: :ref:`Reference → Requirements → General requirements for all
SRUs <reference-general-requirements>`

.. _explanation-documentation:

Documentation
~~~~~~~~~~~~~

[Insert specifics here: SRU template, what is expected in each section,
etc]

Documentation must be provided in order to meet our :ref:`public
documentation requirement <explanation-public-documentation>` as well to
assist the SRU team to review your upload. This is usually done
individually in the description area of the bug, for each bug being
fixed by the SRU, and should follow the :ref:`SRU bug template
<reference-sru-bug-template>`.

Explicit is better than implicit: if there's anything a reviewer might
find unexpected, calling it out will help us tell the difference between
an inadvertent error or omission and a deliberate choice. The former is
likely to result in a further review iteration. The latter gives us
confidence that you, as the subject matter expert, have considered the
matter and we are much more likely to accept your suggestion on how to
deal with it. In any case we will save at least one review iteration in
determining whether the matter is real or has been missed.

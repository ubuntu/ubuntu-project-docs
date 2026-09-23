.. _explanation-sru-requirements:

Requirements and rationale
--------------------------

.. include:: /SRU/_sru-series.rst

Given our principles, when updates are proposed, they must be
accompanied by a strong rationale and present a low risk of regressions.
These requirements therefore follow.

1. **Real world impact**. We won't make a change unless there's real
   world impact for users and the proposed change will address it.

2. **Minimal changes only**. We think this correlates well with
   minimising regression risk.

3. **Public documentation**. We must explain, in a way that is
   understandable to technical users not familiar with Ubuntu
   development, how we ensured the above.

It may be the case that even though an SRU meets all documented
requirements, the SRU team concludes that the risk of an update breaking
users' expectations outweigh the benefit of making the change, and in this
case your SRU will be refused. In this case your only options are to fix
the issue for interested users in the development release and for users of
stable releases via the backports archive component, or a PPA or similar
out-of-band method.


Real world impact
~~~~~~~~~~~~~~~~~

Every change carries regression risk, and pushing unnecessary additional
downloads to users harms their experience. If it's a valid bug but
nobody appears affected in practice and nobody is likely to be affected
in practice, then a change to existing users is not acceptable.


.. _explanation-minimal:

Minimal changes only
~~~~~~~~~~~~~~~~~~~~

[This section needs cleaning up]

Some take the view that sticking to upstream point releases is safer. We
do not. We have experiences of regression across the archive, from code
shipped by tens of thousands of upstream projects. We find that they
vary considerably both in quality and in what upstreams consider
acceptable to deliberately change.

Users expect us to maintain our standards across our packages.

It is increasingly common for upstreams to tell us that they only
support their exact released sources, and minimal patching by
distributions to fix bugs is not acceptable to them over taking a more
recent upstream release wholesale.

While we value upstream expertise and opinion, this does not extend as
far as to overrule our own release policies.

Even the simplest of changes can cause unexpected regressions due to
lurking problems:

-  In :lpbug:`81125`, the upgrade
   regression had nothing to do with the content of the change that
   triggered it: any user who had installed the ``libpthread20`` package
   would encounter a problem the next time ``libc6`` was upgraded.
-  In :lpbug:`309674`, the
   failure was a misbuild due to timestamp skew in the build process.
   The underlying problem existed in the source package in the original
   release, but would only manifest in a small percentage of builds.
-  In :lpbug:`559822`, a C++
   library (``wxwidgets2.8``) was uploaded with no code changes. Due to an
   underlying toolchain change/bug, this caused an ABI change, causing a
   lot of unrelated packages to break (see :lpbug:`610975`)
-  In :lpbug:`2055718`,
   updating the package is the trigger for the bug, because the package
   update reconfigures ``tzdata``.

We never assume that any change, no matter how obvious, is completely
free of regression risk.

In line with this, the requirements for stable updates are not
necessarily the same as those in the development release. When preparing
future releases, one of our goals is to construct the most elegant and
maintainable system possible, and this often involves fundamental
improvements to the system's architecture, rearranging packages to avoid
bundled copies of other software so that we only have to maintain it in
one place, and so on. However, once we have completed a release, the
priority is normally to minimise risk caused by changes not explicitly
required to fix qualifying bugs, and this tends to be well-correlated
with minimising the size of those changes. As such, the same bug may
need to be fixed in different ways in stable and development releases.


.. _explanation-public-documentation:

Public documentation
~~~~~~~~~~~~~~~~~~~~

Consider what happens when something goes wrong. Suddenly we're on the
front pages of the industry media. How will we be judged? We think it'll
be on the basis of whether the choices we made appear reasonable, or
irresponsible, with respect to users' production systems. Critics as
well as affected and therefore angry users tend to jump to the worst
conclusions; that's human nature. If on the other hand we *already have*
a clear, documented explanation of the trade-offs we made, then suddenly
we appear far more reasonable. Otherwise, those worst conclusions appear
justified and public confidence in our product is damaged. Timeliness is
important here; the media moves faster than we do, so it's essential to
have the documentation in place *before* a regression is published.

We must therefore document clearly the choices we have made and our
justifications for them, such that a technical non-Ubuntu-familiar
reader can understand it. This includes publication of this policy
itself. For individual SRUs, we must clearly document how the individual
SRU meets our policy. This should include:

1. The real world impact to users that explains why we are making the
   change in the first place.
2. What we are doing to minimise risk to existing users, including our
   analysis of the risks, and a QA plan that mitigates that risk as far
   as is reasonable.

For details, see :ref:`Documentation <explanation-documentation>` below.


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

Newer releases
^^^^^^^^^^^^^^

If a bug is being fixed in a particular stable release, we would like
for all subsequent releases that are still supported to also be fixed at
the same time. This is to prevent a user from facing a regression when
they upgrade to a newer release.

Exceptions:

The following exceptions apply to bugfixes, but do not apply to
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
3. **When the package no longer exists in subsequent releases:** sometimes
   a package only exists in one particular Ubuntu release, and was removed
   from later releases. This decision usually happens during the
   development release: for some reason, it was decided that Ubuntu shouldn't
   carry that package anymore. As time goes by, we will get into the
   situation where the package exists in a stable release, but not in any
   other stable release. For example, it could exist in 22.04, but not in
   24.04 or any other release after that, including interim ones. In such
   a case, it's OK to SRU fixes to the package only in the releases where
   it exists.

   **NOTE**: the intention of this point is to cover software that was really
   removed in subsequent releases. This does NOT cover source package
   renames (like *src:sosreport* being renamed to *src:sos*), or versioned
   source packages which just got a version bump (like *src:php7.2* which
   became *src:php8.4* in the new version), or any other similar case where
   the same software remains in the archive, just under a different name.

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

.. vale off

.. _explanation-test-plan-detail:

Detail in Test Plans
^^^^^^^^^^^^^^^^^^^^

.. vale on

Consider if another person were to follow the Test Plan as written.
Are they likely to perform the same actual steps in practice? If not,
then the Test Plan is not sufficiently detailed and unambiguous.
Otherwise we might end up performing insufficient testing because the
Test Plan that was approved is not the Test Plan that was actually
executed. Ambiguity would result in unnecessary regression risk,
violating our :ref:`principles <explanation-principles>`.

If a regression is found, then we will need to consider what went wrong
to see if there are any opportunities for improvement next time. To be
able to analyse this effectively, our QA must be reproducible.
Otherwise, if original tester is unavailable, developers could waste
time due to the ambiguity.

It follows that the Test Plan must be unambiguously reproducible.

There are multiple roles interacting here: the developer who writes the
Test Plan, the SRU team member who approves it, the person who performs
it, and the SRU team member who reads the tester's report before
releasing the update. It is essential that everyone involved agrees on
the actual steps to perform, without any misunderstanding.

How do we avoid needless detail? Here's a suggestion: if another person
were to follow the Test Plan and it's likely that they will interpret it
to use the same steps as you intend, then further detail is not needed.

Example
"""""""

"Check that the service still works" is an ambiguous instruction. Should
the tester run ``systemctl status`` and verify that systemd reports the
service as active and running, or actually verify that the service works
by running a query against the service? If a query, then what query
exactly?

If, later, a regression is found, then we will want to know what the
tester actually did. Perhaps the regression occurred because they
*didn't* check that the service actually works by running a query
against the service, even though the person who wrote the Test Plan
intended it:

* The developer would say: "Yes obviously you needed to check the
  service actually works; that's what I meant when I wrote the Test
  Plan.

* The SRU reviewer would say: "On review, given the nature of the bug
  being fixed and the changes being made, I thought it was important to
  check the service responds correctly to a query, but that's what the
  Test Plan included so I approved it.

* The tester would say: "I carried out the testing exactly as
  instructed" and then report in the bug for SRU verification "I have
  carried out the Test Plan specified against version X and it passed".

...but this would then have regressed users solely because of the
ambiguity.


.. seealso::

   :ref:`Reference → Requirements <reference-general-requirements>`
      Detailed SRU requirements (general, documentation, and upload requirements).

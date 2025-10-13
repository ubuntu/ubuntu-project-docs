Requirements
------------

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

-  In bug `81125 <https://bugs.launchpad.net/bugs/81125>`__, the upgrade
   regression had nothing to do with the content of the change that
   triggered it: any user who had installed the ``libpthread20`` package
   would encounter a problem the next time ``libc6`` was upgraded.
-  In bug `309674 <https://bugs.launchpad.net/bugs/309674>`__, the
   failure was a misbuild due to timestamp skew in the build process.
   The underlying problem existed in the source package in the original
   release, but would only manifest in a small percentage of builds.
-  In bug `559822 <https://bugs.launchpad.net/bugs/559822>`__, a C++
   library (``wxwidgets2.8``) was uploaded with no code changes. Due to an
   underlying toolchain change/bug, this caused an ABI change, causing a
   lot of unrelated packages to break (see bug
   `610975 <https://bugs.launchpad.net/bugs/610975>`__)
-  In bug `2055718 <https://bugs.launchpad.net/bugs/2055718>`__,
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

For details, see :ref:`Explanation → Reason for requirements → Documentation <explanation-documentation>`.

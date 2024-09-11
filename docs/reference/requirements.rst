Requirements
------------

.. _reference-what-is-acceptable-to-sru:

What is acceptable to SRU
~~~~~~~~~~~~~~~~~~~~~~~~~

*Governance note: policy decisions on the broad criteria described in
this section have historically been made by the Technical Board with
individual review for compliance against these criteria performed by the
SRU team. The authority to materially change these criteria therefore
rests with the Technical Board, and not the SRU team. If, in the opinion
of the SRU team, a proposed update does not meet these criteria, then
the SRU will be rejected, unless the Technical Board change the
criteria, make a clarification or grant an exception.*

Stable release updates will, in general, only be issued in order to fix
**high-impact bugs**. Examples of such bugs include:

-  Bugs which represent **severe regressions** from the previous release
   of Ubuntu. This includes packages which are totally unusable, like
   being uninstallable or crashing on startup.
-  Bugs which may, under realistic circumstances, directly cause a
   **loss of user data**

.. _reference-criteria-environment:

-  Updates that need to be applied to Ubuntu packages to adjust to
   changes in the environment, server protocols, web services, and
   similar, i. e. where the current version just ceases to work.
   Examples:

   -  app-install-data-commercial is a package index which regularly
      needs to be adjusted to changes in the commercial package archive.
   -  clamav needs `regular
      updates <https://wiki.ubuntu.com/ClamavUpdates>`__ to latest virus
      signatures
   -  tor needs a newer version to still work with the current Tor
      network.
   -  A library for a web service needs to be updated for changes to the
      web server API.

Other safe cases
^^^^^^^^^^^^^^^^

In the following cases a stable release update is also applicable as
they have a low potential for regressing existing installations but a
high potential for improving the user experience, particularly for Long
Term Support releases:

-  Bugs which do not fit under above categories, but (1) have an
   obviously safe patch and (2) affect an application rather than
   critical infrastructure packages (like X.org or the kernel).

.. _reference-criteria-hardware:

-  For Long Term Support releases we regularly want to enable new
   hardware. Such changes are appropriate provided that we can ensure
   not to affect upgrades on existing hardware. For example, modaliases
   of newly introduced drivers must not overlap with previously shipped
   drivers. This also includes updating hardware description data such
   as udev's keymaps, media-player-info, mobile broadband vendors, or
   PCI vendor/product list updates. To avoid regressions on upgrade, any
   such hardware enablement must first also be added to any newer
   supported Ubuntu release.

.. _reference-criteria-features:

-  For Long Term Support releases we sometimes want to introduce new
   features. They must not change the behaviour on existing
   installations (e. g. entirely new packages are usually fine). If
   existing software needs to be modified to make use of the new
   feature, it must be demonstrated that these changes are unintrusive,
   have a minimal regression potential, and have been tested properly.
   To avoid regressions on upgrade, any such feature must then also be
   added to any newer supported Ubuntu release. Once a new
   feature/package has been introduced, subsequent changes to it are
   subject to the usual requirements of SRUs to avoid regressions.
-  **FTBFS** (Fails To Build From Source) can also be considered. Please
   note that in **main** the release process ensures that there are no
   binaries which are not built from a current source. Usually those
   bugs should only be SRUed in conjunction with another bug fix.

.. _reference-criteria-autopkgtest:

-  **Autopkgtest failures** should also normally be SRUed only in
   conjunction with other high-priority fixes affecting users at
   runtime, optionally by :ref:`staging <explanation-staged-uploads>`
   them. As an exception, when an SRU of one package will introduce a
   regression in the autopkgtests of another package, it is appropriate
   to do an autopkgtest-only SRU of the other package.

For new upstream versions of packages which provide new features, but
don't fix critical bugs, a
`backport <https://help.ubuntu.com/community/UbuntuBackports>`__ should
be requested instead.

.. _reference-criteria-microreleases:

New upstream microreleases
^^^^^^^^^^^^^^^^^^^^^^^^^^

In some cases, when upstream fixes bugs, they do a new microrelease
instead of just sending patches. If all of the changes are appropriate
for an SRU by the criteria above, then it is acceptable (and usually
easier) to just upload the complete new upstream microrelease instead of
backporting the individual patches. Note that some noise introduced by
autoreconf is okay, but making structural changes to the build system
(such as introducing new library dependencies) is generally not.

For upstreams who have

-  a reliable and credible test suite for assuring the quality of every
   commit or release,
-  the tests are covering both functionality and API/ABI stability,
-  the tests run during package build to cover all architectures,
-  the package has an
   `autopkgtest <http://packaging.ubuntu.com/html/auto-pkg-test.html>`__
   to run the tests in an Ubuntu environment against the actual binary
   packages,

it is also acceptable to upload new microreleases with many bug fixes
without individual Launchpad bugs for each of them (~ubuntu-sru will
make the final decision). The upstream QA process must be
documented/demonstrated and linked from the SRU tracking bug. In other
cases where such upstream automatic testing is not available, exceptions
must still be approved by at least one member of the Ubuntu Technical
Board.

Out of scope
^^^^^^^^^^^^

-  Bugs which may, under realistic circumstances, directly cause a
   **security vulnerability** are out of scope of this process
   [:ref:`explanation <explanation-security>`]. See instead
   `SecurityTeam/UpdateProcedures
   <https://wiki.ubuntu.com/SecurityTeam/UpdateProcedures>`__ for
   details of how these are handled.

.. _reference-general-requirements:

General requirements for all SRUs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  The development release must already be fixed and its bug task marked
   "Fix Released", unless the development release is not yet open, in
   which case the development release upload must be prepared, ready and
   documented [:ref:`explanation <explanation-devel-first>`].
-  Changes must be minimal [:ref:`explanation <explanation-minimal>`],
   unless at least one of the following cases apply:

   -  The SRU is one of the :ref:`documented special types
      <reference-special-types-of-sru>` and that type, by definition,
      requires a non-minimal upload.
   -  There is a :ref:`documented standing permission
      <reference-package-specific-notes>` that permits non-minimal
      changes.
   -  You provide full justification of why the case is special and our
      general policy should not apply, and this justification is
      accepted by the SRU team when they review your upload.

-  Any fix or feature addition being made to one release must first be
   made to all future releases to prevent users regressing when they
   upgrade. This includes any interim non-LTS releases that are still
   supported [:ref:`explanation <explanation-newer-releases>`]. Exceptions:

   -  If there are two subsequent interim releases that are both
      current, then, as a compromise, additionally fixing only the most
      recent one is acceptable.
   -  You cannot supply the resources to fix an interim non-LTS release,
      you have explicitly stated your intention to use this exception in
      the SRU documentation in the relevant bugs, you have marked the
      relevant bug tasks Won't Fix, and an SRU team member accepts your
      upload on a case-by-case basis.

-  The SRU Driver and (if there is one) the Sponsor must be subscribed
   to relevant SRU bugs.

.. _reference-documentation-requirements:

Documentation
~~~~~~~~~~~~~

Bugs
^^^^

[This section needs cleaning up]

Launchpad bugs are used for SRU documentation. Stable series bug tasks
against existing Launchpad bugs should be used, such that there is only
one Launchpad bug per issue being fixed. Exceptionally a generic bug may
exist for special SRUs that track the special state being sought that is
not complete.

Examples for standard SRU bugs:

-  "When I do X it crashes"

Examples for special SRU bugs:

-  "Release X not available on Ubuntu stable releases"

All bugs linked from the upload must be public. If required information
exists in private bugs that cannot be made public, you must first create
a separate public bug report in Launchpad and use that to present the
required information instead.

Keep in mind that certain packages can change source package names
between releases. In that case, if the given bug applies to a different
source package that replaced the old one in a later releases, this
source package has to be added as 'Also affecting'. Make sure that the
devel releases package has the bug fixed before proceeding.

-  If a change (eg. from upstream) is known to exceed the scope of a
   standing exception to regular requirements, this must be pointed out

Special cases that must be mentioned
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  If :ref:`package-specific SRU notes
   <reference-package-specific-notes>` exist and/or a standing approval
   exists to deviate from regular SRU policy, link to them from the bug
-  If it's a :ref:`special SRU type <reference-special-types-of-sru>`,
   mention which, and check the documentation for the special SRU type
   for any other documentation that must be supplied
-  If the basis of the justification of the SRU depends on something
   other than a special SRU type or the user impact statement, then this
   justification must be made

User Impact
^^^^^^^^^^^

-  The impact to users must be made clear, and form the basis of the
   justification of the SRU.

Test Plan
^^^^^^^^^

-  Detailed instructions on how to reproduce the bug and verify that the
   updated package fixes the problem.
-  If the instructions do not exercise the common use of the package,
   then further instructions on how to ensure that the package still
   works.
-  If the instructions do not exercise risks found in the Risk Analysis,
   then further instructions on performing testing to mitigate those
   risks.
-  All instructions must provide enough detail such that someone who is
   not familiar with the affected package can follow them. They must be
   unambiguous so that two different developers will follow the same
   actual steps. To a reasonable limit, there should not be ambiguity.
-  The idea is that this is agreed at review/accept time, and then if
   followed and the results presented precisely, then there should be no
   blockers at release time. Subject to any concerns raised that were
   not documented as considered previously.
-  Must use the package from -proposed and no third party software.

Risk Analysis
^^^^^^^^^^^^^

-  "None" is not OK.
-  What risks we assume always exist.
-  What the real purpose of this section is.
-  If an obvious risk is missing, then we cannot determine if it was
   considered and discounted, or it's an omission, and therefore this is
   a blocker.
-  Should feed back into the Test Plan.

Other Information
^^^^^^^^^^^^^^^^^

-  It is helpful, but not required, to include an explanation of how the
   upload fixes this bug

.. _reference-upload-requirements:

Upload
~~~~~~

[maybe this section could have a better name and it needs cleaning up
generally]

[Insert specifics here: minimal changes, version number, what should be
in the changelog, bug references, etc]

The upload must have the correct *release* in the changelog header, a
detailed and user-readable changelog, and no other unrelated changes.

The version number does not conflict with any later and future version
in other Ubuntu releases (the `security policy
document <https://wiki.ubuntu.com/SecurityTeam/UpdatePreparation#Update_the_packaging>`__
has a well-working scheme which can be used for SRUs.)

There is at least one reference to a Launchpad bug number in the
changelog, using the 'LP: #NNNNNN' convention, and the required
documentation can be found there. Private bugs must not be referenced in
the changelog.

Bug references in changelogs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When uploading a new upstream version of a package as an SRU, there may
be bugs fixed in the new version which will not go through a manual
per-bug verification process. It is acceptable to still reference these
bugs in the changelog, so that users can know about the bugs that will
be fixed as part of the update and so that the status of these bugs in
Launchpad can be managed automatically when the update is released.

If you include such bug references in your changelog, you should state
in the bug description that these bugs are not being verified because of
the use of the exception process.

After the SRU has been accepted, you should then add the
verification-done-<series> tag to these bugs.

Release
~~~~~~~

Before release, the following requirements must be met. Most of these are
tracked automatically on the `pending SRU report`_.

* All referenced bugs have a QA report in a bug comment explaining how the
  Test Plan was performed, what package version was tested, and what the
  overall result was (pass or fail).

* All referenced bugs have ``verification-done-<series>`` set, and the
  ``verification-needed-<series>`` and ``verification-failed-<series>`` tags
  are absent.

* No bugs are marked ``block-proposed-<series>``, for example because they are
  held by :ref:`staging <explanation-staged-uploads>`.

* There are no packages that failed to build such that this is a
  regression over the previous build status.

* All autopkgtest failures have been investigated and a resolution
  provided [:ref:`how-to <howto-handle-autopkgtest-failure>`].

* The minimum ageing period of seven days has passed since the package was
  accepted into -proposed.

* All relevant SRUs for subsequent series are already released
  [:ref:`explanation <explanation-newer-releases>`].

* Any other concerns raised in the referenced bugs have been addressed.

.. _pending SRU report: https://ubuntu-archive-team.ubuntu.com/pending-sru.html

Check for common issues with your SRU
-------------------------------------

General
~~~~~~~

-  Something in the submission is exceptional, unexpected or otherwise a
   surprise to the reviewer, and there is no explanation given.
-  Someone without upload access asks an SRU team member before upload
   because they are unfamiliar with SRU process (ask a sponsor instead;
   try the `patch pilot
   programme <https://discourse.ubuntu.com/t/ubuntu-patch-pilots/37705>`__
   if you cannot find one).

Documentation
~~~~~~~~~~~~~

-  Missing or unclear SRU information
-  Not explaining the user story from a user's perspective. We won't
   accept an SRU unless we understand why it is needed, because our
   policy is not to accept an SRU unless it impacts actual users.
   Consider if the user would recognise the user impact stated; if not,
   then it isn't an explanation of user impact.
-  It turns out that the bug is valid but there don't seem to be any
   users who would benefit from the SRU (e.g. after five years of the bug
   existing, the one reporter moved on and nobody else has commented at
   all). In that case, why are we doing the SRU?

Test Plan
^^^^^^^^^

-  Test Plan is ambiguous. For example, if another person were
   to follow the Test Plan, they might not end up testing adequately, or
   using the steps that you intend. [:ref:`Explanation
   <explanation-test-plan-detail>`].
-  Test Plan only covers the fix, and not general use of the package to
   make sure that it still works after the update. A smoke test will
   suffice. If that's implied by verifying the bug is fixed then it's
   not needed as a separate step.
-  The Test Plan verifies a technical change but not the user story.
   Example: "file exists at location A instead of location B" instead of
   "run the app and check that function X behaves as expected".
-  The Test Plan or verification only tested part of the user story that
   we are fixing with a series of SRUs. In this case, we expect all
   packages in proposed and verification of the entire user story at
   once. E.g. a hardware enablement needs to be done across three
   packages. This avoids iteration in the stable release.
-  It is assumed that uploaders believe their changes are as risk free
   as possible, but this section is for demonstrating that some thought
   has been given to "expecting the unexpected". This section goes along
   with the Test Plan section: while that one is for testing the
   specific bug being fixed in the upload, here is a place to give any
   additional test cases to help to ensure that there are no regressions
   in the update. Think "what if this change is wrong? How would that
   show up?" `1590321 <https://bugs.launchpad.net/bugs/1590321>`__ is an
   example of a simple fix with a legitimate regression analysis.

Upload
~~~~~~

-  [too long; needs moving to Explanation with only a summary here]
   Upload doesn't **minimally** fix the user story. Remember that the
   most minimal fix is not necessarily a cherry-pick from upstream. The
   appropriate fix is often more minimal than that. Refactoring is often
   appropriate in a development branch, but not for a stable branch. You
   are expected to understand the problem and its upstream fix, and
   develop a fix that is less risk with your own patch that is truly
   minimal. However, there is a balance here and a fix that is already
   trivial does not need to be minimised further. But if a cherry-pick
   from upstream is complex compared to an ideal minimal fix, expect
   push-back on this point.

   -  You may take the position that you're more confident in an upstream
      fix than your own ability to create a minimal patch. However, that
      only applies in the context of upstream patch base, and not
      necessarily ours. The minimal fix is the easier of the two options
      to review, and it is our default policy position that the minimal
      fix is preferable.

-  Upload contains extra changes not explained by the SRU documentation
-  Upload contains extra changes not mentioned in the changelog
-  Changelog mentions things not found in the upload.
-  Changelog is missing bug references
-  Launchpad-Bugs-Fixed header in the changes file is missing (this
   happens if you generate it on a pure Debian system for example)
-  Launchpad-Bugs-Fixed header doesn't track all bugs that need
   verifying before this SRU lands. For example if you're building on an
   existing SRU in proposed, then -v may be required when you build the
   source package

Verification
~~~~~~~~~~~~

-  Verification doesn't state what version was tested or from where it
   was obtained.
-  Verification doesn't state what test steps were performed. Just
   stating that you followed the Test Plan is fine. But we often get
   verification comments saying "it works for me" which quite reasonably
   didn't follow the Test Plan, and we need to differentiate the same
   cases so please avoid ambiguity.
-  Verification used packages from outside the archive (e.g. a local
   build or PPA).

Release
~~~~~~~

-  Expecting action when the pending SRU report is not clean.

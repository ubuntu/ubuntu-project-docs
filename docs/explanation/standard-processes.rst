Standard Processes
------------------

[this section needs cleaning up]

-  We'd like the minimum process necessary. It should be clear why any
   process we have is required because of the principles.

-  The SRU team should strive for consistency. No moving goalposts. Good
   communication needed usually through documentation. Cannot expect
   consistency if something has always been done without documentation
   by one SRU team member.

-  Any deviance from the ideal SRU must be called out and justified

-  Anticipate our questions. If we ask questions, try to anticipate them
   next time!

-  We would prefer for users affected to do the verification that the
   bug is fixed, and for many people to verify that the change didn't
   regress their use cases. However in practice it is difficult to find
   people to do SRU verification. As long as the agreed Test Plan is
   followed we will accept verification reports from anyone, including
   the person driving the SRU. Additional feedback of any form is also
   welcome; that doesn't need to follow the Test Plan. But one
   verification that followed the Test Plan is the minimum requirement
   for an SRU to be released. Note that we require that the package *as
   built in -proposed* be tested, and verifications should include
   evidence that this has happened (typically by including the version
   number of the package tested).

-  No iterating in stable releases. [Robie needs to explain what he
   means here]

.. _explanation-autopkgtest-failures:

Autopkgtest failures
~~~~~~~~~~~~~~~~~~~~

Packages accepted into -proposed as per the SRU process automatically
trigger related autopkgtests, similarly to how it happens for the
development series. Once those tests are finished, the pending SRU page
provides links to any failures that have been noticed for the selected
upload. The responsibility of the SRU driver (and/or the person
performing update verification) is to make sure the upload does not
cause any regressions—both in manual and automated testing.

In the case where an SRU upload triggers an autopkgtest regression, the
target package will not be released into -updates until the failure is
*resolved*. There are a few ways that can happen:

-  If the reported autopkgtest regression is a **real regression**
   caused by the upload, the update should be considered
   verification-failed and the package should be re-uploaded with the
   regression fixed. Otherwise the update will be removed from -proposed
   as per the usual procedures.
-  If the reported autopkgtest regression is **not a real regression**
   or not a regression caused by the proposed update (but instead broken
   by some other dependency), the analysis of this has to be documented
   for the SRU team. The generally recommended way is commenting on one
   of the SRU bugs for the upload. Once the rationale is submitted and
   approved/validated by an SRU member, the SRU team will add a badtest
   or reset-test hint for the broken package and release the update as
   per usual procedures (once validation and ageing is complete).
   Alternatively, the uploader/verifier can modify the hints and provide
   an MP in the bug along with the rationale. Useful input here can be
   re-running the failing test against only the release/updates pocket,
   as documented in the
   `Proposed Migration <https://wiki.ubuntu.com/ProposedMigration#How_to_run_autopkgtests_of_a_package_against_the_version_in_the_release_pocket>`__
   wiki page.
-  If the reported autopkgtest regression is the result of a **flaky
   test**, the uploader can try re-running the test to see if it is
   indeed just a transient issue. If the issue still persists but the
   analysis clearly shows that it is not a real regression, a rationale
   for that should be provided in one of the SRU bugs.

It is important to remember that firstly it is the *uploader's
responsibility* to make sure the package is in a releasable state and
that all the autopkgtests triggered by the upload are either passing or
badtested. Of course, it is not the uploader's responsibility to provide
the hints for badtests themselves, but it is it's responsibility to
perform the analysis and verification of each listed regression.

Expected resolution for reported autopkgtest failures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If an SRU did not cause a regression, the update is intended to land but
autopkgtest regressions are still found, then the possible resolutions
for this situation are as follows:

-  An SRU must not be released if outstanding autopkgtest regressions
   are reported on the `Pending SRU
   Report <https://people.canonical.com/~ubuntu-archive/pending-sru.html>`__.
-  Ideally regressions can be fixed with new uploads to the proposed
   pockets as required. Fixes for autopkgtests are generally always
   acceptable. However uploads providing only test fixes will generally
   be
   :ref:`staged <explanation-staged-uploads>`
   using block-proposed-<series> (in which case they need a bug
   reference).
-  A regression not caused by the SRU may be badtest or reset-tested
   away (doesn't matter which for SRUs).

See also: :ref:`How-to → Handle an autopkgtest
failure <howto-handle-autopkgtest-failure>`.

.. _explanation-phasing:

Phasing
~~~~~~~

Once a package is released to -updates, the update is then phased so
that the update is gradually made available to expanding subsets of
Ubuntu users. This process allows us to automatically monitor for
regressions and halt the update process if any are found. Complete
details about the process can be found in a `blog post by Brian
Murray <https://web.archive.org/web/20210507035933/http://www.murraytwins.com/blog/?p=127>`__.

The Phased-Update-Percentage is initially set to 10%, then a job is run
(every 6 hours) that checks for regressions and if none are found the
phased update percentage will be incremented by 10%. So an update will
become fully phased after 54 hours or about 2 days. In the event that a
regression is detected the Phased-Update-Percentage will be set to 0%
thereby causing supported package managers (update-manager) not to
install the update.

The progress of phased updates is visible in a
`report <http://people.canonical.com/~ubuntu-archive/phased-updates.html>`__
which is updated by the same job that does the phasing.

See also:

-  :ref:`How-to → Phasing → Investigate a halted phased update
   <investigate-halted-phased-update>`
-  :ref:`internal-override-phasing`
-  :ref:`Reference → Status Pages <reference-status-pages>`

.. _explanation-regressions:

Regressions
~~~~~~~~~~~

See also: :ref:`How-to → Handling regressions
<howto-handle-regression-report>` for the playbook to follow when a regression
is reported

The SRU team drives the process that handles regressions reported
against the updates pocket. Regressions that have taken place elsewhere
(e.g. during a release upgrade, in the security pocket, in the proposed
pocket or in Pro-specific repositories) are out of scope of this
section.

Once a regression is confirmed, usually we have two choices to resolve
it and we are under time pressure to do so:

1. Release an exact revert ("revert").
2. Analyse the reason for the regression and try to amend the regressing
   update to fix that ("pushing ahead").

By definition, a regression occurs as a failure in quality of the
original fix together with a failure of QA ("failing factors"). Pushing
ahead under time pressure is unlikely to resolve either of these issues,
so we risk further regression by doing so.

Therefore, the SRU team takes the position that pushing ahead must not
take place until the failing factors have been addressed and mitigations
reviewed and approved without time pressure, and therefore in the
general case our immediate and expected action shall be to revert
instead. As a policy position, we will not waste time considering
pushing ahead, unless one of the exceptions below applies.

.. _explanation-regressions-pushing-ahead:

Exceptions that justify pushing ahead
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. There is a known technical reason that a revert will fail (i.e. not
   work or cause a further issue), or that an SRU team member considers
   the risk of the revert failing to be too high.
2. The regression has been published in the updates pocket for long
   enough that the cost/benefit trade-off of a revert has diminished
   compared to users who are enjoying the fix.
3. There is some other good reason, in the opinion of an SRU team
   member, that has not been considered by this policy.

Responsibilities
^^^^^^^^^^^^^^^^

It is expected that the SRU Driver will be available and take all
non-SRU-privileged actions in handling the regression, under the
direction of a decision-making SRU team member.

See also: :ref:`Explanation → Role expectations
<explanation-role-expectations>`

Phases
^^^^^^

Regression reports must be triaged like any other. When a regression is
first reported, we are uncertain if it is valid, and even if we are sure
it is valid, we are unsure if it warrants action. Taking a clear
position on our collective opinion on whether or not action is warranted
is vital, and prevents confusion. Therefore, we define the following
phases:

-  **Uncertainty phase:** there is a report of a regression, but we are
   not sure if it is valid.
-  **Alert phase:** in the opinion of an SRU team member, there is a
   credible report of a regression that warrants further investigation.
-  **Action phase:** an SRU team member has considered the available
   information, taken the decision that action is warranted, and
   communicated this decision.

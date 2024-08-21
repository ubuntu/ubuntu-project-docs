Doing this in a Google Doc for ease of writing, review, etc. Once
complete, this can be moved into the wiki to replace and restructure the
existing SRU documentation page. Probably into multiple pages rather
than one megapage, while trying to preserve existing URLs that have
anchors, etc.

SRU Documentation Reboot
========================

Once an Ubuntu release has been completed and published, updates for it
are only released under certain circumstances, and must follow a special
procedure called a "stable release update" or SRU.

This documentation describes the principles and processes we follow in
order to keep stable Ubuntu releases stable.

Our documented principles are intended to be read by all Ubuntu users if
they wish to understand what to expect from Ubuntu stable releases, and
are for upstream and Ubuntu developers to read if they wish to
understand what changes would or would not be acceptable to us. The rest
is intended for Ubuntu developers and SRU team members to achieve this
in practice.

**Did you notice a regression in a package which went to -updates?**
Please report this using `these steps <#report-a-regression>`__.

`Explanation <#explanation>`__

`Principles <#principles>`__

`Minimise regression <#minimise-regression>`__

`Confidence <#confidence>`__

`Maintain usefulness <#maintain-usefulness>`__

`Requirements <#requirements>`__

`Real world impact <#real-world-impact>`__

`Minimal changes only <#minimal-changes-only>`__

`Public documentation <#public-documentation>`__

`Overview of the SRU pipeline <#overview-of-the-sru-pipeline>`__

`Role expectations <#role-expectations>`__

`Standard Processes <#standard-processes>`__

`Autopkgtest failures <#autopkgtest-failures>`__

`Phasing <#phasing>`__

`Regressions <#regressions>`__

`Non-standard Processes <#non-standard-processes>`__

`Package-specific non-standard
processes <#package-specific-non-standard-processes>`__

`Staging low priority uploads <#staging-low-priority-uploads>`__

`Removals <#removals>`__

`Security updates <#security-updates>`__

`Freezes and release opening <#freezes-and-release-opening>`__

`Removal of languishing updates <#removal-of-languishing-updates>`__

`Reasons for requirements <#reasons-for-requirements>`__

`Preconditions <#preconditions>`__

`Documentation <#documentation>`__

`How-to <#how-to>`__

`Perform a standard SRU <#perform-a-standard-sru>`__

`Prepare a special type of SRU <#prepare-a-special-type-of-sru>`__

`Get an SRU released from
proposed <#get-an-sru-released-from-proposed>`__

`Check for common issues with your
SRU <#check-for-common-issues-with-your-sru>`__

`General <#general>`__

`Documentation <#documentation-1>`__

`Test Plan <#test-plan>`__

`Upload <#upload>`__

`Verification <#verification>`__

`Release <#release>`__

`Special types of SRU <#special-types-of-sru>`__

`Request a package-specific non-standard
process <#request-a-package-specific-non-standard-process>`__

`Stage an upload <#stage-an-upload>`__

`Land an upload blocked by
staging <#land-an-upload-blocked-by-staging>`__

`Remove a package <#remove-a-package>`__

`Handle an autopkgtest failure <#handle-an-autopkgtest-failure>`__

`Handle a regression <#handle-a-regression>`__

`Report a regression <#report-a-regression>`__

`Handle a regression report <#handle-a-regression-report>`__

`Investigate a halted phased
update <#investigate-a-halted-phased-update>`__

`Contact the SRU team <#contact-the-sru-team>`__

`Reference <#reference>`__

`Status Pages <#status-pages>`__

`Team Rota <#team-rota>`__

`SRU Bug Template <#sru-bug-template>`__

`Requirements <#requirements-1>`__

`What is acceptable to SRU <#what-is-acceptable-to-sru>`__

`General requirements for all
SRUs <#general-requirements-for-all-srus>`__

`Documentation <#documentation-2>`__

`Upload <#upload-1>`__

`Special types of SRU <#special-types-of-sru-1>`__

`Package-specific notes <#package-specific-notes>`__

`Historical removals <#historical-removals>`__

`Internal SRU team docs <#internal-sru-team-docs>`__

`Decision making <#decision-making>`__

`Reviewing procedure and tools <#reviewing-procedure-and-tools>`__

`Override phasing <#override-phasing>`__

`Adding members to the team <#adding-members-to-the-team>`__

`Criteria for new SRU team
members <#criteria-for-new-sru-team-members>`__

`Hard requirements <#hard-requirements>`__

`Nice to haves <#nice-to-haves>`__

`Draft texts that need moving into the documentation
structure <#draft-texts-that-need-moving-into-the-documentation-structure>`__

`Why I bring this up <#why-i-bring-this-up>`__

`TODO <#todo>`__

Explanation
===========

Principles
----------

We carefully manage what we change in a stable Ubuntu release for the
following principles:

1. **Minimise regressions**

2. **User confidence**

3. **Maintain usefulness**

A fourth principle is simply to focus on **user experience**, but this
of course applies across Ubuntu and isn't SRU-specific.

Minimise regression
~~~~~~~~~~~~~~~~~~~

Behaviour a user reasonably relies upon that works today must not break
tomorrow as a result of an update. In a stable release, this includes
*any* user interface change! Exception: behaviour that we deem buggy
must necessarily change in order to fix it. [Expand on this]. See xkcd
spacebar heater.

In contrast to pre-release versions, official releases of Ubuntu are
subject to much wider use, and by a different demographic of users.
During development, changes to the distribution primarily affect
developers, early adopters and other advanced users, all of whom have
elected to use pre-release software at their own risk.

Users of the official release, in contrast, expect a high degree of
stability. They use their Ubuntu system for their day-to-day work, and
problems they experience with it can be extremely disruptive. Many of
them are less experienced with Ubuntu and with Linux, and expect a
reliable system which does not require their intervention.

Stable release updates are automatically recommended to a very large
number of users, and so it is critically important to treat them with
great caution.

Confidence
~~~~~~~~~~

We must maintain confidence in the stability of our stable releases.
This requires consistent application of policy, documented diligence,
rationale for exceptions, etc. "Headline/outrage avoidance"

What do we mean by stability?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. There's stability as in "things don't crash". That's easy.

2. There's stability as in "things behave in the way that upstream meant
them to behave". This is mostly a superset of "things don't crash".

3. There's stability as in **predictability** - if the user did
something yesterday it will do the same thing today.

We want stability in all three of these senses for the "stable release",
but with a much higher emphasis on the third than in other contexts.

Maintain usefulness
~~~~~~~~~~~~~~~~~~~

We make exceptions to keep the distribution useful. Eg. Firefox,
hardware enablement, Internet protocol [need to expand on this].

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

Real world impact
~~~~~~~~~~~~~~~~~

Every change carries regression risk, and pushing unnecessary additional
downloads to users harms their experience. If it's a valid bug but
nobody appears affected in practice and nobody is likely to be affected
in practice, then a change to existing users is not acceptable.

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
   triggered it: any user who had installed the libpthread20 package
   would encounter a problem the next time libc6 was upgraded.
-  In bug `309674 <https://bugs.launchpad.net/bugs/309674>`__, the
   failure was a misbuild due to timestamp skew in the build process.
   The underlying problem existed in the source package in the original
   release, but would only manifest in a small percentage of builds.
-  In bug `559822 <https://bugs.launchpad.net/bugs/559822>`__, a C++
   library (wxwidgets2.8) was uploaded with no code changes. Due to an
   underlying toolchain change/bug, this caused an ABI change, causing a
   lot of unrelated packages to break (see bug
   `610975 <https://bugs.launchpad.net/bugs/610975>`__)
-  In bug `2055718 <https://bugs.launchpad.net/bugs/2055718>`__,
   updating the package is the trigger for the bug, because the package
   update reconfigures tzdata.

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

For details, see `Explanation → Reason for requirements →
Documentation <#documentation>`__.

Overview of the SRU pipeline
----------------------------

1. An SRU driver prepares the relevant bugs with the necessary
   documentation and makes an SRU upload available.
2. When an SRU is uploaded by a developer with upload access to the
   Ubuntu package archive, it enters the "Unapproved" queue, which you
   can see here: https://launchpad.net/ubuntu/jammy/+queue?queue_state=1
   (modify for different series as needed).
3. The SRU team will then review from the Unapproved queue,
   communicating in the bug as necessary. When ready, the upload is
   *accepted* into the -proposed pocket, and then built. Once accepted
   into -proposed, its status appears in the `Pending SRU
   Report <https://ubuntu-archive-team.ubuntu.com/pending-sru.html>`__
   when the report is next generated.
4. Once builds are ready, the agreed QA steps are performed on the
   package build using the -proposed pocket, with results being posted
   to the relevant bugs as comments. The `Pending SRU
   Report <https://ubuntu-archive-team.ubuntu.com/pending-sru.html>`__
   tracks progress on this, as well as any other blockers detected, such
   as build or test failures.
5. Once the `Pending SRU
   Report <https://ubuntu-archive-team.ubuntu.com/pending-sru.html>`__
   displays all outstanding tasks as reported to be resolved, the SRU is
   ready to be released. The SRU team regularly reviews the report. For
   packages marked as ready, they review the corresponding bug comments,
   ensure that all agreed QA steps have been performed satisfactorily
   and that there are no outstanding blockers. If satisfied, they
   *release* packages into the -updates pocket.
6. The SRU is now complete. If a regression is found, see `How-to →
   Handling regressions <#handle-a-regression-report>`__ for next steps.

See also: `Reference → Status Pages <#status-pages>`__

Role expectations
-----------------

The SRU team is a narrowly scoped team that has privileged access:
primarily to "accept" packages from the stable series' unapproved queues
into the -proposed pocket, and "release" packages from the -proposed
pocket into the -updates pocket. Reviews and decision making, and the
policy, processes and documentation around these reviews and decision
making are the responsibility of the SRU team.

Other work that does not require elevated privilege, such as bug triage
and management, preparing updates, performing QA, handling any follow-on
regression reports and so forth, can be performed by any Ubuntu
developer or prospective Ubuntu developer.

Therefore, the SRU team, when on shift and "wearing an SRU hat", takes a
narrow view of our role, focusing our limited resources on only
progressing processes limited by this privilege. It is our expectation
that Ubuntu developers at large drive the non-privileged tasks because
they scale better.

We expect all Ubuntu developers to be familiar with the SRU process as
documented here, should they need to interact with SRUs.

It is normal and expected for prospective developers to not yet be
familiar with SRU process. If prospective developers are preparing
uploads for SRU, then they will need a sponsor, for example through the
`patch pilot
programme <https://discourse.ubuntu.com/t/ubuntu-patch-pilots/37705>`__.
We expect Ubuntu developers to ensure that any uploads that they sponsor
meet our expectations. As above, since SRU team members focus on
operations limited by privilege during their shifts, prospective
developers who need help should seek that help from their sponsors, and
not from the SRU team directly. To find a sponsor, try the `patch pilot
programme <https://discourse.ubuntu.com/t/ubuntu-patch-pilots/37705>`__.

If review iterations are required, then prospective developers are
welcome to help. However, we expect this to be supervised by sponsors
and for them to intervene if required.

We therefore arrive at a set of distinct roles. Note that the person who
takes on each role can change over time, even for an individual SRU.

+-----------------------+-----------------------+-----------------------+
| Role                  | Responsibility        | Who can do it         |
+=======================+=======================+=======================+
| SRU Driver            | Manage and triage     | Anyone who            |
|                       | bugs, follow the SRU  | understands the       |
|                       | process and perform   | packaging changes     |
|                       | the necessary         | necessary to land a   |
|                       | development and QA    | particular fix into a |
|                       | tasks to see fixes    | stable release of     |
|                       | land.                 | Ubuntu and is willing |
|                       |                       | to do that work. If   |
|                       |                       | this person does not  |
|                       |                       | have upload access to |
|                       |                       | Ubuntu, then they can |
|                       |                       | still take this role, |
|                       |                       | under the supervision |
|                       |                       | of a sponsor          |
|                       |                       | (sponsors can be      |
|                       |                       | found via the `patch  |
|                       |                       | pilot                 |
|                       |                       | programme             |
|                       |                       | <https://discourse.ub |
|                       |                       | untu.com/t/ubuntu-pat |
|                       |                       | ch-pilots/37705>`__). |
+-----------------------+-----------------------+-----------------------+
| Sponsor               | Help the SRU Driver   | Someone familiar with |
|                       | with the required     | SRU process who has   |
|                       | process.              | upload access to the  |
|                       |                       | Ubuntu package        |
|                       |                       | archive.              |
+-----------------------+-----------------------+-----------------------+
| SRU Reviewer          | Review and negotiate  | SRU team members      |
|                       | proposed uploads for  | only.                 |
|                       | compliance with `SRU  |                       |
|                       | criteria <#what-is-a  |                       |
|                       | cceptable-to-sru>`__, |                       |
|                       | agree the QA plan,    |                       |
|                       | accept uploads into   |                       |
|                       | -proposed, confirm    |                       |
|                       | the agreed plan was   |                       |
|                       | followed, and release |                       |
|                       | -proposed packages    |                       |
|                       | into -updates.        |                       |
+-----------------------+-----------------------+-----------------------+
| SRU Process Developer | Drive process         | Anyone, under the     |
|                       | changes,              | leadership of the SRU |
|                       | documentation, etc.   | team.                 |
+-----------------------+-----------------------+-----------------------+
| Overriding authority  | Agree exceptions to   | Technical Board       |
|                       | the `SRU              | members only.         |
|                       | criteria <#what-is-a  |                       |
|                       | cceptable-to-sru>`__. |                       |
+-----------------------+-----------------------+-----------------------+

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
   per usual procedures (once validation and aging is complete).
   Alternatively, the uploader/verifier can modify the hints and provide
   an MP in the bug along with the rationale. Useful input here can be
   re-running the failing test against only the release/updates pocket,
   as documented in the
   `ProposedMigration <https://wiki.ubuntu.com/ProposedMigration#How_to_run_autopkgtests_of_a_package_against_the_version_in_the_release_pocket>`__
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
   `staged <https://wiki.ubuntu.com/StableReleaseUpdates#Staging_an_upload>`__
   using block-proposed-<series> (in which case they need a bug
   reference).
-  A regression not caused by the SRU may be badtest or reset-tested
   away (doesn't matter which for SRUs).

See also: `How-to → Handle an autopkgtest
failure <#handle-an-autopkgtest-failure>`__.

Phasing
~~~~~~~

Once a package is released to -updates, the update is then phased so
that the update is gradually made available to expanding subsets of
Ubuntu users. This process allows us to automatically monitor for
regressions and halt the update process if any are found. Complete
details about the process can be found in a `blog post by Brian
Murray <http://www.murraytwins.com/blog/?p=127>`__.

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

-  `How-to → Phasing → Investigate a phased
   update <#investigate-a-halted-phased-update>`__
-  `How-to → Phasing → Override phasing <#override-phasing>`__
-  `Reference → Status Pages <#status-pages>`__

Regressions
~~~~~~~~~~~

See also: `How-to → Handling
regressions <#handle-a-regression-report>`__ for the playbook to follow
when a regression is reported

The SRU team drives the process that handles regressions reported
against the updates pocket. Regressions that have taken place elsewhere
(eg. during a release upgrade, in the security pocket, in the proposed
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

Exceptions that justify pushing ahead
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. There is a known technical reason that a revert will fail (ie. not
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

See also: `Explanation → Role expectations <#role-expectations>`__

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

Non-standard Processes
----------------------

Package-specific non-standard processes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a package or set of packages requires deviation from our standard
process, but we expect to routinely deviate in the same way for
subsequent updates to the same packages, we document these deviations
under `package-specific notes <#package-specific-notes>`__. This allows
us to be consistent in our approaches to review, QA and release. If the
package-specific note has been approved by one member of the SRU team,
other SRU team members will try to honour that previous approval when
reviewing.

Staging low priority uploads
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SRUs for bugs which do not affect users at runtime are inappropriate to
force users to apply. There is a cost to our users (and our mirror
network) for downloading updates of packages, which should be balanced
against the utility of the update to the user downloading it.

However, if such an update otherwise complies with SRU policy, it can be
staged to be bundled with a future SRU or security update.

It is essential to carry out SRU verification on all related bugs as
usual as soon as the upload enters the proposed pocket. We do not want
to burden a future SRUer with verification of your low priority bug. If
timely verification is not performed, then as usual the staged upload is
a candidate for deletion, and a future SRUer is quite entitled to base
their upload on the version prior to your staged upload instead. If this
happens, the future SRU will not include your changes, effectively
cancelling the staging.

Since we try to avoid regressing users on upgrade to a new release, it
is essential to carry out this SRU verification for every affected bug
series task. If you skip verification of one series then staged uploads
in all series are candidates for deletion or overriding as above at the
discretion of the SRU team.

Removals
~~~~~~~~

While it is always preferable to fix a package, rather than drop it,
there are rare cases when a universe package becomes actively
detrimental in stable releases: If it is unmaintained in Ubuntu and has
unfixed security issues or has been broken because of changing network
protocols/APIs, it is better to stop offering it in Ubuntu altogether
rather than continuing to encourage users to install it.

It is not technically possible to remove a package from a stable
release, but this can be approximated by SRUing an essentially empty
package with an appropriate explanation in NEWS and a corresponding
critical debconf note.

When a package is removed in this way from a stable release, it may need
similar removal from the devel release as well, depending on the
justification for removal.

See also:

-  `How-to → Remove a package <#remove-a-package>`__
-  `Reference → Historical removals <#historical-removals>`__

Security updates
~~~~~~~~~~~~~~~~

Since some users choose to receive security updates but not SRUs, if a
proposed SRU appears to fix security issues, it should be considered for
the security update process first instead.

Sometimes an issue being fixed may or may not be a security issue
depending on opinion, or the security team may otherwise consider it not
appropriate for the -security pocket. In this case, the SRU process may
be used to fix the issue if the change being made otherwise meets `SRU
criteria <#what-is-acceptable-to-sru>`__.

Freezes and release opening
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  After final freeze, the release team may decline to accept changes,
   so uploaders should assume that they will become SRUs and include bug
   references. They must provide SRU documentation if they become SRUs.
   See the freeze announcement from the release team for details.
-  After release, the development release will not yet have opened, but
   uploaders may need SRUs regardless.

   -  *How to do this*
   -  [this section needs cleaning up]

-  The release team will do a copy-forward-en-masse and then hand queue
   management of the just-released updates pocket to the SRU team. From
   this point on, uploaders should upload to the new development
   Unapproved queue when needed for SRU process, even though it hasn't
   yet opened.

Removal of languishing updates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a bug fixed by an update does not get any testing or verification
feedback for 90 days an automated call for testing comment will be made
on the bug report. In the event that there is still no testing after an
additional 15 days (a total of 105 days without any testing), the Stable
Release Managers will remove the package from -proposed and usually
close the bug task as "Won't Fix", due to lack of interest. Removal will
happen immediately if a package update in -proposed is found to
introduce a nontrivial regression.

Reasons for requirements
------------------------

Preconditions
~~~~~~~~~~~~~

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

See also: `Reference → Requirements → General requirements for all
SRUs <#general-requirements-for-all-srus>`__

Documentation
~~~~~~~~~~~~~

[Insert specifics here: SRU template, what is expected in each section,
etc]

Documentation must be provided in order to meet our `public
documentation requirement <#public-documentation>`__ as well to assist
the SRU team to review your upload. This is usually done individually in
the description area of the bug, for each bug being fixed by the SRU,
and should follow the `SRU bug template <#sru-bug-template>`__.

Explicit is better than implicit: if there's anything a reviewer might
find unexpected, calling it out will help us tell the difference between
an inadvertent error or omission and a deliberate choice. The former is
likely to result in a further review iteration. The latter gives us
confidence that you, as the subject matter expert, have considered the
matter and we are much more likely to accept your suggestion on how to
deal with it. In any case we will save at least one review iteration in
determining whether the matter is real or has been missed.

How-to
======

Perform a standard SRU
----------------------

This how-to is for standard SRUs, where straightforward bugs are fixed
using minimal cherry-picks. For other types of SRUs, see `How-to →
Prepare a special type of SRU <#prepare-a-special-type-of-sru>`__
instead.

1.  Check that the upload complies with `Reference → Requirements → What
    is acceptable to SRU <#what-is-acceptable-to-sru>`__.
2.  If this is not a straightforward set of bugs being fixed by minimal
    cherry-picks, see `How-to → Prepare a special type of
    SRU <#prepare-a-special-type-of-sru>`__ first.
3.  Check for compliance against `Reference →
    Requirements <#general-requirements-for-all-srus>`__
    `→ <#what-is-acceptable-to-sru>`__ `General requirements for all
    SRUs <#general-requirements-for-all-srus>`__.
4.  Document the SRU, starting with the `SRU Bug
    Template <#sru-bug-template>`__ and following and ensuring
    compliance against `Reference <#documentation-2>`__
    `→ <#general-requirements-for-all-srus>`__
    `Requirements <#documentation-2>`__
    `→ <#general-requirements-for-all-srus>`__
    `Documentation <#documentation-2>`__.
5.  Prepare the upload, ensuring compliance against `Reference →
    Requirements → Upload. <#upload-1>`__ If you do not have access to
    upload to the Ubuntu package archive yourself, you may prepare this
    in the form of a debdiff or a git-ubuntu branch.
6.  If you:

    1. have a debdiff, then `request
       sponsorship <https://wiki.ubuntu.com/SponsorshipProcess>`__ by
       attaching the debdiff and subscribing 'ubuntu-sponsors' to one
       bug.
    2. have a git-ubuntu branch, then request sponsorship by filing a
       merge proposal and ensuring that the ubuntu-sponsors team has
       been requested to review it.
    3. have access to upload to the Ubuntu package archive directly,
       then go ahead and upload, and set the relevant bug task status to
       In Progress.
    4. are sponsoring an upload for someone else, then check that the
       above steps have been performed correctly, iterate or fix up as
       necessary, ensure that you are subscribed to all referenced bugs,
       upload, and set the relevant bug task statuses to In Progress.

7.  Wait for review, following any instructions you are given. If you
    wish, you can follow progress through the `SRU
    pipeline <#overview-of-the-sru-pipeline>`__ using the various
    `status pages <#status-pages>`__.
8.  After the package is accepted into -proposed, you will be asked to
    execute your Test Plan against the built packages. Please do so,
    using bug comments to report your results. Once done, change the bug
    tags according to the instructions given.
9.  Subscribe yourself to bugmail for the package in Launchpad, if you
    haven't done so already, and monitor Launchpad for bug reports
    relating to the update for at least one week following release of
    the package.
10. If you find a regression, follow `Howto → Report a
    regression <#report-a-regression>`__. If someone else reports a
    regression, please also follow `Howto → Report a
    regression <#report-a-regression>`__ and ensure that all steps
    documented there have been performed correctly.

Prepare a special type of SRU
-----------------------------

1. If your special type of SRU already has `package-specific
   notes <#package-specific-notes>`__ then follow `How-to → Perform a
   standard SRU <#perform-a-standard-sru>`__ as modified by those notes
   instead.
2. Some special types of SRU have specific How-tos to follow instead:

   1. `Stage an upload <#stage-an-upload>`__
   2. `Remove a package <#remove-a-package>`__

3. Consider `Reference → Special types of
   SRU <#special-types-of-sru-1>`__ to try to find existing documented
   patterns for what you wish to achieve.
4. Consider `Reference → Requirements → What is acceptable to
   SRU <#what-is-acceptable-to-sru>`__ and ensure that your goal is
   compliant with our policy.
5. If you are looking to update packages using a special type of SRU on
   a routine basis, follow `How-to → Request a package-specific
   non-standard
   process <#request-a-package-specific-non-standard-process>`__
   instead.

Get an SRU released from proposed
---------------------------------

The Stable Release Updates team regularly checks for SRUs that have
successfully completed verification (all bugs are marked
verification-done-$RELEASE for the given release) and releases those to
the -updates pocket. Having said that, if there is a priority SRU
waiting in the unapproved queue for release to -proposed, or needing
release to -updates from -proposed, feel free to `contact an SRU
vanguard <#contact-the-sru-team>`__.

Please note that SRUs will not be published to the -updates pocket on
Friday (or Saturday or Sunday). Any exception will need justification.

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

.. _documentation-1:

Documentation
~~~~~~~~~~~~~

-  Missing or unclear SRU information
-  Not explaining the user story from a user's perspective. We won't
   accept an SRU unless we understand why it is needed, because our
   policy is not to accept an SRU unless it impacts actual users.
   Consider if the user would recognise the user impact stated; if not,
   then it isn't an explanation of user impact.
-  It turns out that the bug is valid but there don't seem to be any
   users who would benefit from the SRU (eg. after five years of the bug
   existing, the one reporter moved on and nobody else has commented at
   all). In that case, why are we doing the SRU?

Test Plan
~~~~~~~~~

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
   once. Eg. a hardware enablement needs to be done across three
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
-  

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

   -  You may take the position that you're more confident in upstream's
      fix than your own ability to create a minimal patch. However, that
      only applies in the context of upstream's patch base, and not
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
-  Verification used packages from outside the archive (eg. a local
   build or PPA).

Release
~~~~~~~

-  Expecting action when the pending SRU report is not clean.

Special types of SRU
--------------------

This section is for the special types of SRU listed at
`Reference <#special-types-of-sru-1>`__
`→ <#staging-low-priority-uploads>`__ `Special types of
SRU <#special-types-of-sru-1>`__.

Request a package-specific non-standard process
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This hasn't been transferred into the new documentation yet. See
https://wiki.ubuntu.com/StableReleaseUpdates#Documentation_for_Special_Cases
for now.

Stage an upload
~~~~~~~~~~~~~~~

See also: `Explanation → Special types of SRU → Staging low priority
uploads <#staging-low-priority-uploads>`__

1. Follow the usual process but additionally add a
   block-proposed-<series> tag to at least one of the SRU bugs together
   with a comment explaining the reason for the staging. Staging can
   also be added retrospectively simply by adding the tag; this can be
   done at any time before an SRU is released. If you do so, please make
   sure that you add a bug comment that explains the reason.
2. Ensure that you perform SRU verification as normal as soon as the
   package is accepted into proposed.

Land an upload blocked by staging
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See also: `Explanation → Special types of SRU → Staging low priority
uploads <#staging-low-priority-uploads>`__

In principle the block-proposed-<series> tag should be removed by an SRU
team member when accepting a newer upload not planned for further
staging. But if they overlook this, it's appropriate for whoever notices
it (SRU team, or uploader) to remove the block-proposed-<series> tag
with a suitable comment when it no longer applies.

Remove a package
~~~~~~~~~~~~~~~~

See also:

-  `Explanation → Special types of SRU → Removals <#removals>`__
-  `Reference → Historical removals <#historical-removals>`__

Steps for the uploader
^^^^^^^^^^^^^^^^^^^^^^

1. If appropriate depending on the reason for the removal, ensure that
   the package is also removed in the development release and any
   releases subsequent to the release being targetted.
2. Construct an essentially empty package with an appropriate
   explanation in NEWS and a corresponding critical debconf note. Follow
   the pattern used previously (see `the list of historical
   removals <#historical-removals>`__).
3. Create an SRU tracking but with an appropriate explanation.
4. `Write to the technical
   board <https://lists.ubuntu.com/mailman/listinfo/technical-board>`__
   for approval.
5. Upload as normal

Steps for the SRU reviewer:
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Check the above list has been performed correctly, and that the
   Technical Board has approved
2. Document in the `list of historical
   removals <#historical-removals>`__.
3. Process the SRU as normal.

Handle an autopkgtest failure
-----------------------------

See also: `Explanation → Autopkgtest failures <#autopkgtest-failures>`__

1. Determine if the failure represents a regression caused by the SRU,
   or if it is a false positive that will not cause a regression if the
   SRU is released to -updates.
2. If this is a real regression, follow `How-to → Report a
   regression <#report-a-regression>`__ instead.
3. Submit autopkgtest retries if you consider this appropriate, such as
   if you think the cause of the failure is a flaky test. If this
   resolves the issue, no further action is required.
4. If possible, submit further SRUs into -proposed that resolve the
   issue, such as [TBC]
5. Post an explanation to the relevant bug containing your analysis that
   describes how you arrive at your conclusion that this is a false
   positive.

Handle a regression
-------------------

Report a regression
~~~~~~~~~~~~~~~~~~~

If a package update introduces a regression which already made it
through the verification process to -updates, please **immediately**
ensure that a separate bug exists for the issue by filing one as needed,
and add the tag regression-update to the bug.

If the regression *only* applies to the package in -proposed, please
follow up to the bug with a detailed explanation, and tag the bug with
regression-proposed. To ensure that the package doesn't accidentally get
released, add a comment to an existing bug and change the appropriate
tag to verification-<series>-failed.

Handle a regression report
~~~~~~~~~~~~~~~~~~~~~~~~~~

See also: `Explanation → Standard Process →
Regressions <#regressions>`__

This is the playbook to follow when there is a concern about a
regression that has taken place in the updates pocket, such that a user
receiving the recommended updates within a stable release is regressed
somehow. Regressions that have taken place elsewhere (eg. during a
release upgrade, in the security pocket, in the proposed pocket or in
Pro-specific repositories) are out of scope.

Uncertainty phase
^^^^^^^^^^^^^^^^^

Actions to take
'''''''''''''''

-  All: ensure that a separate bug report exists and that it is tagged
   regression-update.
-  All: ensure that the most relevant bug related to the update has a
   comment stating that a regression is suspected, linking to the
   regression bug.
-  Ubuntu developers: if you think the situation warrants moving to the
   alert phase, contact an SRU team member.

Examples of why we may be stuck in this phase:

-  Reports may not have all the necessary information
-  We are not confident in the reliability of the information available
   to us
-  The regression can not be reproduced (in by itself, this is not
   enough reason to doubt it, though)

Alert phase
^^^^^^^^^^^

Roles
'''''

-  An SRU team member should be nominated to drive decision-making.
-  It is expected that further technical investigation is carried out by
   the Ubuntu developer who uploaded the update in question, by a
   sponsoree under their supervision, or by some other Ubuntu developer
   delegated by them or their team. However, in their absence, anyone
   may assume this role. Please coordinate with the nominated SRU team
   member.

.. _actions-to-take-1:

Actions to take
'''''''''''''''

-  Nominate an SRU team member who will coordinate and ensure that they
   are available and their name is communicated.
-  Nominate the technical investigator, ensure that they are available
   and that their name is communicated.
-  If phasing is still in progress then `find an
   AA <https://launchpad.net/~ubuntu-archive/+members#active>`__ to stop
   phasing, since this is considered easy and risk-free.

Examples of why we may be stuck in this phase:

-  The source package that caused the regression has not been
   confidently identified.

Action phase
^^^^^^^^^^^^

.. _roles-1:

Roles
'''''

-  An SRU team member should be nominated to drive decision-making.
-  It is expected that preparation of the reverting upload and
   subsequent SRU verification is carried out by the Ubuntu developer
   who uploaded the regressing update in question, by a sponsoree under
   their supervision, or by some other Ubuntu developer delegated by
   them or their team. However, in their absence, anyone may assume this
   role. Please coordinate with the nominated SRU team member.

.. _actions-to-take-2:

Actions to take
'''''''''''''''

-  Verify that there is no reason to think that an exact revert won't
   exacerbate the issue. For example, if it's a postinst failure due to
   an upgrade path problem, or some other latent bug triggered by the
   action of updating itself, then an exact revert is probably not
   appropriate. In this case, these instructions end and you will need
   to solve the problem according to your best judgement. See also:
   `Explanation → Standard Process → Regressions → Exceptions that
   justify pushing ahead <#exceptions-that-justify-pushing-ahead>`__.
-  Otherwise, upload an exact revert of the regressing update for
   immediate release to updates as soon as appropriate QA is completed,
   bypassing the usual ageing period. If possible, one SRU team member
   and one other Ubuntu developer should work together (or one reviewing
   the other) to minimise the risk of mistakes or unforeseen
   consequences. However, if nobody is available, the SRU team member
   may release their own work alone.

Investigate a halted phased update
----------------------------------

See also: `Explanation → Phasing <#phasing>`__

Here are some tips on how to utilize the phased updates report to
investigate why the phasing has stopped.

When looking at an increased rate of crashes you'll want to look at the
crash(es) with the greatest number of occurrences. Then check to see if
the crash is occurring more frequently (by examining the Occurrences
table) with the updated version of the package. If it is then you want
to sort out why and address the crash in a follow on SRU. If it isn't
then `contact the SRU team <#contact-the-sru-team>`__ regarding
overriding the crash.

When looking at a new error you'll want to confirm that the error is in
fact a new one by using the versions table. The phased-updater currently
checks if the error has been reported about the version immediately
before the current version, so if the previous version wasn't around
very long its possible a specific error wasn't reported about it.
Additionally, you can check to see if the error is really about the
identified package or if it occurs in an underlying library by looking
at the Traceback or Stacktrace e.g. python crashes being reported about
a package using python. If you do not believe the error is a new one or
was not caused by your stable release update then `contact the the SRU
team <#contact-the-sru-team>`__ regarding overriding the crash.

Contact the SRU team
--------------------

If you do not have upload access to the archive, you should ask your
sponsor for help in the first instance. If you don't have a sponsor, you
can `ask a patch
pilot <https://discourse.ubuntu.com/t/ubuntu-patch-pilots/37705>`__ or
try asking generally on `#ubuntu-devel on
Libera.Chat <https://wiki.ubuntu.com/IRC>`__, or the
`ubuntu-devel-discuss <https://lists.ubuntu.com/mailman/listinfo/ubuntu-devel-discuss>`__
mailing list. See
`SponsorshipProcess <https://wiki.ubuntu.com/SponsorshipProcess>`__ for
details.

If you do have upload access, you can contact the SRU team by asking
generally in #ubuntu-release on Libera.Chat, or on the
`ubuntu-release <https://lists.ubuntu.com/mailman/listinfo/ubuntu-release>`__
mailing list.

See also: `Reference → Team Rota <#team-rota>`__

Reference
=========

Status Pages
------------

-  **Pending sponsorship**: `general sponsorship
   queue <http://sponsoring-reports.ubuntu.com/general.html>`__.
-  **Pending accept:** package updates awaiting review for:

   -  `Ubuntu 24.04 LTS "Noble
      Numbat" <https://launchpad.net/ubuntu/noble/+queue?queue_state=1&queue_text=>`__
   -  `Ubuntu 22.04 LTS "Jammy
      Jellyfish" <https://launchpad.net/ubuntu/jammy/+queue?queue_state=1&queue_text=>`__
   -  `Ubuntu 20.04 LTS "Focal
      Fossa" <https://launchpad.net/ubuntu/focal/+queue?queue_state=1&queue_text=>`__
   -  (edit the URL for other series)

-  **Pending release:** `package updates that are accepted and pending
   QA <https://ubuntu-archive-team.ubuntu.com/pending-sru.html>`__. This
   also has an "Upload queue status" section which links to all stable
   review queues (as directly linked above).
-  **After release:** `phased update
   status <http://people.canonical.com/~ubuntu-archive/phased-updates.html>`__
   displays the Phased-Update-Percentage of packages in the -proposed
   repository for releases and any regressions detected in that package.

Team Rota
---------

Vanguards from the SRU team can also usually be found in #ubuntu-release
on the following schedule:

+-----------+-----------------------------------------------------------------+
| Day       | SRU Team Member (IRC nick)                                      |
+===========+=================================================================+
| Monday    | Łukasz Zemczak (sil2100), Mauricio Oliveira (mfo)               |
+-----------+-----------------------------------------------------------------+
| Tuesday   | Chris Halse Rogers (RAOF), Brian Murray (bdmurray)              |
+-----------+-----------------------------------------------------------------+
| Wednesday | Robie Basak (rbasak)                                            |
+-----------+-----------------------------------------------------------------+
| Thursday  | Andreas Hasenack (ahasenack), Łukasz Zemczak (sil2100 - backup) |
+-----------+-----------------------------------------------------------------+
| Friday    | Timo Aaltonen (tjaalton), Steve Langasek (vorlon - backup)      |
+-----------+-----------------------------------------------------------------+

SRU Bug Template
----------------

[ Impact ]

\* An explanation of the effects of the bug on users and

\* justification for backporting the fix to the stable release.

\* In addition, it is helpful, but not required, to include an

explanation of how the upload fixes this bug.

[ Test Plan ]

\* detailed instructions how to reproduce the bug

\* these should allow someone who is not familiar with the affected

package to reproduce the bug and verify that the updated package fixes

the problem.

\* if other testing is appropriate to perform before landing this
update,

this should also be described here.

[ Where problems could occur ]

\* Think about what the upload changes in the software. Imagine the
change is

wrong or breaks something else: how would this show up?

\* It is assumed that any SRU candidate patch is well-tested before

upload and has a low overall risk of regression, but it's important

to make the effort to think about what ''could'' happen in the

event of a regression.

\* This must '''never''' be "None" or "Low", or entirely an argument as
to why

your upload is low risk.

\* This both shows the SRU team that the risks have been considered,

and provides guidance to testers in regression-testing the SRU.

[ Other Info ]

\* Anything else you think is useful to include

\* Anticipate questions from users, SRU, +1 maintenance, security teams
and the Technical Board

\* and address these questions in advance

.. _requirements-1:

Requirements
------------

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
-  For Long Term Support releases we regularly want to enable new
   hardware. Such changes are appropriate provided that we can ensure
   not to affect upgrades on existing hardware. For example, modaliases
   of newly introduced drivers must not overlap with previously shipped
   drivers. This also includes updating hardware description data such
   as udev's keymaps, media-player-info, mobile broadband vendors, or
   PCI vendor/product list updates. To avoid regressions on upgrade, any
   such hardware enablement must first also be added to any newer
   supported Ubuntu release.
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
-  **Autopkgtest failures** should also normally be SRUed only in
   conjunction with other high-priority fixes affecting users at
   runtime, optionally by
   `staging <https://wiki.ubuntu.com/StableReleaseUpdates#Staging_low_priority_uploads>`__
   them. As an exception, when an SRU of one package will introduce a
   regression in the autopkgtests of another package, it is appropriate
   to do an autopkgtest-only SRU of the other package.

For new upstream versions of packages which provide new features, but
don't fix critical bugs, a
`backport <https://help.ubuntu.com/community/UbuntuBackports>`__ should
be requested instead.

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
   [`explanation <#heading=h.zg78amb0dn63>`__]. See instead
   `SecurityTeam/UpdateProcedures <https://wiki.ubuntu.com/SecurityTeam/UpdateProcedures>`__
   for details of how these are handled.

General requirements for all SRUs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  The development release must already be fixed and its bug task marked
   "Fix Released", unless the development release is not yet open, in
   which case the development release upload must be prepared, ready and
   documented [`explanation <#development-release-fixed-first>`__].
-  Changes must be minimal [`explanation <#minimal-changes-only>`__],
   unless at least one of the following cases apply:

   -  The SRU is one of the `documented special
      types <#special-types-of-sru-1>`__ and that type, by definition,
      requires a non-minimal upload.
   -  There is a `documented standing
      permission <#package-specific-notes>`__ that permits non-minimal
      changes.
   -  You provide full justification of why the case is special and our
      general policy should not apply, and this justification is
      accepted by the SRU team when they review your upload.

-  Any fix or feature addition being made to one release must first be
   made to all future releases to prevent users regressing when they
   upgrade. This includes any interim non-LTS releases that are still
   supported [`explanation <#newer-releases>`__]. Exceptions:

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

.. _documentation-2:

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

-  If `package-specific SRU notes <#heading=h.6ia7bft0j6g1>`__ exist
   and/or a standing approval exists to deviate from regular SRU policy,
   link to them from the bug
-  If it's a `special SRU type <#special-types-of-sru-1>`__, mention
   which, and check the documentation for the special SRU type for any
   other documentation that must be supplied
-  If the basis of the justification of the SRU depends on something
   other than a special SRU type or the user impact statement, then this
   justification must be made

User Impact
^^^^^^^^^^^

-  The impact to users must be made clear, and form the basis of the
   justification of the SRU.

.. _test-plan-1:

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

.. _upload-1:

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
''''''''''''''''''''''''''''

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

.. _special-types-of-sru-1:

Special types of SRU
--------------------

`What is acceptable to SRU <#what-is-acceptable-to-sru>`__, together
with other considerations, give rise to the following special types of
permitted SRU, some of which overlap:

-  | **Package-specific non-standard process:** for routine non-standard
     cases, we create `package-specific
     notes <#package-specific-notes>`__ for consistency. These may
     incorporate any of the other special types below and may include
     any exceptions to our `usual
     criteria <#what-is-acceptable-to-sru>`__ that have been approved by
     the Technical Board.

-  | **Hardware enablement:** for Long Term Support releases we
     regularly want to enable new hardware
     [`criteria <#bookmark=id.sbi9jlwmqv2t>`__].

-  | **Environmental change:** updates that need to be applied to Ubuntu
     packages to adjust to changes in the environment, server protocols,
     web services, and similar
     [`criteria <#bookmark=id.f4snv2j2hbbu>`__].

-  **Autopkgtest fix:** autopkgtest fixes may be included in SRUs. An
   update that fixes only autopkgtests is also acceptable, but should
   normally be `staged <#staging-low-priority-uploads>`__
   [`criteria <#bookmark=id.wgkh6ggtxywi>`__].

-  **Extended Security Maintenance:** there are special procedures for
   uploads to stable releases in their `Extended Security Maintenance
   (ESM) <https://ubuntu.com/esm>`__ period. Please prepare the `SRU
   Bug <https://wiki.ubuntu.com/StableReleaseUpdates#srubug>`__ then
   contact `the ESM team <https://launchpad.net/~ubuntu-esm-team>`__.

-  | **Staged upload**
     [`explanation <#staging-low-priority-uploads>`__].

-  | **Bundled upload:** an SRU performed "on top" of an existing
     package already in -proposed. [TBC]

-  **New upstream release:**

   -  **New bugfix-only upstream release**
      Bugfix-only releases are acceptable if all changes are appropriate
      for an SRU under our normal
      `criteria <#what-is-acceptable-to-sru>`__, by one of two paths:

1. The upload may use the new upstream orig tarball, but with individual
   Launchpad bugs to track verification of each fix individually.
2. Instead, if upstreams meet, in the opinion of the SRU team, our `more
   specific QA criteria for upstream
   microreleases <#new-upstream-microreleases>`__ then it is acceptable
   to process them with a single tracking bug instead of individual
   Launchpad bugs for each fix. If relying on this path, the upstream QA
   process that meets this criteria must be documented/demonstrated and
   linked from the SRU tracking bug.

-  **New upstream release that adds features without breaking existing
   behaviour**

   For Long Term Support releases we sometimes consider it appropriate
   to introduce new features. We may choose to do so we can do this
   safely. However, to meet expectations of release stability, we will
   consider these on a case-by-case basis
   [`criteria <#bookmark=id.bimt5deg053q>`__].

-  **New upstream release that changes existing behaviour**

   Deliberately changing existing behaviour is to be avoided due to our
   `minimise regression principle <#minimise-regression>`__, so such
   SRUs are generally not permitted. Exceptions may be granted by the
   Technical Board, but require exceptional justification. Standing
   exceptions are documented in `Package-specific
   notes <#heading=h.6ia7bft0j6g1>`__.

-  | **Removals:** in rare cases, a package is or has become actively
     harmful to users, and is replaced by an empty package
     [`explanation <#removals>`__].

-  **Security updates:** these usually follow a different process and
   are out of scope of the SRU team and processes documented here. See
   `SecurityTeam/UpdateProcedures <https://wiki.ubuntu.com/SecurityTeam/UpdateProcedures>`__
   for details [`explanation <#security-updates>`__].

Package-specific notes
----------------------

See also: `Explanation → Non-standard Processes → Package-specific
non-standard processes <#package-specific-non-standard-processes>`__

These have yet to be imported into the new documentation. See the `old
documentation <https://wiki.ubuntu.com/StableReleaseUpdates#Documentation_for_Special_Cases>`__
for now.

Historical removals
-------------------

See also:

-  `Explanation → Removals <#removals>`__
-  `How-to → Remove a package <#remove-a-package>`__

The following packages have previously been (pseudo-)removed via SRU
following our removals process.

-  `tor <https://lists.ubuntu.com/archives/ubuntu-devel/2007-September/024453.html>`__
   (was reintroduced later on in
   `#413657 <https://launchpad.net/bugs/413657>`__)
-  `bitcoin <https://bugs.launchpad.net/ubuntu/+source/bitcoin/+bug/1314616>`__
-  `owncloud <https://launchpad.net/bugs/1384355>`__
-  `jsunit and tinyjsd <https://launchpad.net/bugs/1895643>`__ (more
   context in `this
   post <https://discourse.ubuntu.com/t/thunderbird-lts-update/20819>`__)

Internal SRU team docs
======================

See also: `Reference → Team-internal
processes <#heading=h.x4b5g1y1rofs>`__ for:

-  Adding new team members to the team
-  Criteria for new SRU team members

Decision making
---------------

-  Act for the team if you're confident that the team would concur
-  If unsure, ask, and if you need to follow up, add to the SRU team
   meeting agenda where we can make a team decision

Reviewing procedure and tools
-----------------------------

If you are a member of the `SRU reviewing
team <https://launchpad.net/~ubuntu-sru>`__, you should check out the
`ubuntu-archive-tools <https://launchpad.net/ubuntu-archive-tools>`__
scripts with

-  git clone https://git.launchpad.net/ubuntu-archive-tools

which greatly simplifies the reviewing procedure. You should symlink
sru-review and sru-accept somewhere to your ~/bin/ directory for easy
access, or put the checkout into your $PATH.

The following review procedure is recommended:

-  Open the unapproved queue for a particular release, e. g.
   `https://launchpad.net/ubuntu/noble/+queue?queue_state=1 <https://launchpad.net/ubuntu/precise/+queue?queue_state=1>`__
   for noble. This shows the list of SRU uploads which have to be
   reviewed, commented on, and approved/accepted/rejected.
-  For each package, generate the debdiff to the current version in the
   archive and open the corresponding bugs:
   sru-review -s noble gnash
   This opens all the bugs which are mentioned in the .changes file in
   the browser, and will generate a debdiff between the current archive
   and the unapproved upload (unless the orig.tar.gz changes this will
   only download the two diff.gz, so it is reasonably fast).

   -  In case the SRU is a package sync instead of a standard upload,
      the sru-review tool will not be able to fetch the debdiff for you
      and will exit with an error. You will have to review the changes
      manually and then re-run the tool with an additional argument of
      --no-diff.
   -  For `Bileto <https://wiki.ubuntu.com/Bileto>`__ published SRU's
      you can easily fetch the relevant debdiffs by following the link
      to the sync's source PPA and opening the ticket URL that's
      provided in the PPA description. Each upload present there has two
      diffs generated for review convenience: full and packaging-only.

-  Review the bugs for complete description, justification, check that
   they have a stable release task, are conformant to SRU rules, etc,
   and comment accordingly.
-  Scrutinize the debdiff for matching the changes in the bugs, not
   having unrelated changes, etc. If you have doubts, comment on the
   bug.
-  *If you are in the ubuntu-sru team:*

   -  Exit the tool you are using to review the debdiff
   -  If the bugs and debdiff are okay, accept the package by pressing y
      at the ""Accept the package into -proposed?" prompt.
      This will tag the bug(s) with verification-needed,
      verification-needed-$RELEASE, subscribe ubuntu-sru, and add a
      general "please test and give feedback"-like comment.
   -  If the upload is broken or unsuitable for an SRU, reject it by
      pressing N at the ""Accept the package into -proposed?" prompt and
      pressing y at the "REJECT the package from -proposed?" prompt.

-  *If you are not in the ubuntu-sru team:* Send a follow up comment to
   the bugs:

   -  If all is okay: send an "ubuntu-sru approved and reviewed" comment
      and set the task to "In Progress"
   -  If something is wrong: send the feedback to the bug and set the
      task to "Incomplete"

The `pending
SRUs <http://people.canonical.com/~ubuntu-archive/pending-sru>`__ should
also be reviewed to see whether or not there are any to be released or
removed from the archive. The process for dealing with these follows:

Packages in -proposed can be moved to -updates once they are approved by
someone from sru-verification, and have passed the minimum aging period
of **7 days**. Use the sru-release script from ubuntu-archive-tools for
this:

-  $ ./sru-release noble kdebase

Please see --help, you can also use this tool to copy packages to
-security and to the current development release. N.B. before copying a
package to -security ping a member of the
`ubuntu-security <https://launchpad.net/~ubuntu-security/+members>`__
team.

-  `Currently pending
   SRUs <http://people.canonical.com/~ubuntu-archive/pending-sru.html>`__

If a package should be removed from -proposed, use the remove-package
tool (from ubuntu-archive-tools). e.g., to remove source and binaries
for the libreoffice package currently in xenial-proposed:

-  $ ./remove-package -m "SRU abandoned (verification-failed)" -s
   noble-proposed libreoffice

Override phasing
----------------

*Overriding phasing can only be performed by a member of the SRU team.*

Overriding halted phasing is done in a similar way to overriding
autopkgtest failures. The phased update machinery looks at
`phased-update-overrides.txt <https://code.launchpad.net/~ubuntu-sru/+junk/phased-update-overrides>`__,
which is a simple CSV file containing lines of the form *source
package*, *version*,
*:math:`THING\_TO\_IGNORE* where *`\ THING_TO_IGNORE* can either be an
errors.ubuntu.com problem URL to ignore or *increased-rate*.

Adding members to the team
--------------------------

-  Existing SRU team members identify when new team members are needed.
   They will privately nominate suitable candidates, with regard to
   their availability (eg. a discussion with their manager may be
   required).

-  One existing team member will study a candidate's recent SRU
   activity, assess them against our criteria and write a summary.

-  The team will then decide whether the candidate is suitable.

-  One existing team member will onboard a given new trainee,
   "sponsoring" privileged SRU actions such as review accept and
   release.

-  This mentor will consult with other existing team members and the
   trainee will be given equivalent privileges when appropriate.

Criteria for new SRU team members
---------------------------------

Hard requirements
~~~~~~~~~~~~~~~~~

-  Must be able to upload all SRUs they expect to review; ie. Ubuntu
   Core Developer or SRU Developer. A member of the SRU team who is an
   SRU Developer is expected to be in the process of applying to be an
   Ubuntu Core Developer: the role involves exercising judgement about
   whether a change in the development series is **good**, and therefore
   someone in this role should be formally trusted by the project to
   make such decisions for the development series as well.

-  Recent track record of good quality SRUs.

-  Recent uploads (whether sponsored or not) either met our expectations
   or successfully anticipated concerns that could reasonably have been
   predicted by existing SRU team members.

-  Few recent poor quality SRUs (nice to have: none). This includes
   uploads for issues that are unsuitable for SRU, as well as missing
   SRU information, missing bug references, poorly completed SRU
   information, etc. Exception: if an omission or concern is called out
   by the uploader and the upload was for the purpose of asking the SRU
   team about it.

-  Can they say no?

Nice to haves
~~~~~~~~~~~~~

-  Demonstrated familiarity **across** existing SRU policies and
   procedures (rather than just having correctly submitted good SRUs
   that might be limited in parts of SRU policy and procedure that they
   exercise)

-  What about SRUs they've sponsored: do they successfully raise the
   quality of SRU submissions to our expected level before they sponsor
   them? If so, then this might be a good indicator that they'll be able
   to do similar at SRU review time.

-  Do they have a track record of spotting issues before they occur? How
   broadly do they look when determining "Where problems could occur"?
   Do they then make sure the Test Plan covers identified risks?

-  Do they seek to change general policy when appropriate, rather than
   ignoring it? Can they identify the difference between individual
   exceptions and the general case?

Draft texts that need moving into the documentation structure
=============================================================

Why I bring this up
-------------------

If I had to rate the current state of the relationship between the SRU
team and Ubuntu uploaders, it'd have to be "poor". How to measure?
Consider the number of further questions, review changes requested, and
rejects. Quantitatively, the accept rate is perhaps not as important as
the total amount of uploader and SRU reviewer time spent compared to
what was necessary. The actual proportion is biased because review
feedback and communication prior to accept takes a disproportionately
large amount of time. So this is what we should minimise.

Consider why review feedback is necessary instead of an immediate SRU
accept.

Things I think are OK:

1. Because it was a genuinely complicated issue with no obviously
correct answer that needed discussion for the SRU team to agree some
kind of compromise.

2. Because of an oversight on the part of the uploader. Oversights are
normal and why we have a review process, but we should all seek to
minimise them.

Things I think aren't OK:

3. SRU team failed to set expectations effectively. This is what I'm
trying to address here.

4. Failure on the part of the uploader to meet clear SRU policy, and/or
anticipate review questions. For example: "what's this non-minimal
change here?" "I had to do it because X" -> so why didn't you state X in
the SRU documentation in the first place?

Feedback from Mark: in the case of repeated occurrences of 4 above, a
conversation with the uploader's manager is appropriate - be kind, not
nice.

-  \* Reproducible test results

\* Written rationale for exceptions

Avoiding regressions

\* All updates carry risk, even no change rebuilds. So we will only
accept changes that are worth making. There must be a broken user story
to fix. For our confidence priority, this must be well articulated.

Fixing an older release but not a newer release creates a regression
when the user upgrades. Exception: we expect this in hardware
enablements eg. LP: #2023201.

Testing

\* Regressions slip through. But did we apply due diligence?

\* Test Plan agreed with SRU team at accept time avoids surprises at
release time.

\* Verification reports can be vague. This has resulted in regressions.
No need to copy and paste, but please be explicit and we will believe
you. Include specific version tested and a reference to precise steps
followed (eg. say you followed the Test Plan). For manual testing please
try to copy and paste the version and the plan to avoid errors. For
automation please have it output the result of apt-cache policy
<package> and the version tested, then copy and paste that. The
automation should be auditable (eg. provide a link to it) but no need
for any more detail in testing results than that.

\* It's important to not regress other use cases. This is easy to
overlook so I tend to focus on it. It's much easier to be confident that
your use case is being fixed. But what other use cases exist and how are
they being tested? Generally the team driving the SRU cares about the
former, and making sure the former is fixed is easy because that's why
they're doing it. The latter is ready to overlook. Consider when
regression reports arrive later.

\* So, we want to ensure that 1) the package isn't fundamentally broken
by the SRU and 2) the specific story being addressed is fixed. The
former is sometimes tested by verifying the latter but not always.

\* If testing what we need tested can be covered entirely by automated
testing then there is no need for manual steps. Just please explain how
this is the case.

\* Should test actual user stories that we are fixing. Looking for some
technical change is insufficient.

Commentary

Everyone wants their thing updated in the LTS. We did that: that's what
Lunar is. Because do that for everyone and you've updated everything. So
if you want an exception to a minimal cherry pick fixing a specific
broken user case, there must be a differentiating reason your situation
warrants it.

-  

TODO
----

-  Explain different types of SRUs:

   -  Hardware enablement (this came up because you **must** fix all
      future supported releases for new features and hardware enablement
      cases.
   -  Regular bugfix
   -  Micro/minor/major direct from upstream
   -  0-day

On team consistency

It's better to stick to a previous SRU team member's decision. However,
equally we shouldn't be forced to accept or release something we're
uncomfortable with, or release a mistake to users. So this has to be
balanced carefully. The important thing to appreciate is that there are
two sides to a decision relating to consistency across the SRU team.

\* Rejections with feedback is normal

\* rejections are not final and we can accept from the rejected queue

\* You're the domain expert, not us. Please don't assume we know the
subject matter in detail, or can infer things. And remember the audience
of the SRU documentation is the general public as well. It will matter
if there's a regression that we appear to have acted reasonably.

Other

-  Automated verification is fine. All we need is:

   -  Where the test code is so we can review it.
   -  The automation only needs to output two things:

      -  If the overall result is a pass or a fail.
      -  What versions was tested.

   -  No other output is needed!

\* Upstream point releases are usually explicitly opted in to by
dedicated direct upstream consumers. Distribution updates are consumed
by disinterested users (in that specific thing). Appropriate criteria
for inclusion is often different.

\* Fixes for stable releases do not fit otherwise good development
practice. Calculation wrt. tech debt eg. refactoring is often different.
Don't even need to clean up skeleton code. Minimal change is key.

\* We're often upstreams' biggest consumers. Just because upstream
released it doesn't mean it's good. They vary enormously in quality.
Selection bias: they shipped bugs. Fixes should be well tested. Let's
not let our users be guinea pigs.

\* Landing new changes we've just written simultaneously in development
and stable releases is especially dangerous as the assumption that fixes
have had real world testing fails.

\* Interim release expectations

\* Staging

\* "Upstream recommends" is not a reason for deviation from SRU policy.
Upstreams vary tremendously in quality - ironically, most SRUs fix bugs
that upstream introduced!

\* Upstream sometimes fixes issues after the commit we cherry pick.
Please do not blindly cherry-pick!

\* "Let's see what the SRU team thinks about this dubious sponsorship
request" -> no thanks. We're overburdened and expect sponsors to be
gatekeepers. Makes you look bad. Unless you really think something is
subjectively either-way, in which case it should be flagged as such and
the nuances presented in the SRU documentation.

\* Is the behaviour proposed to be changed relied upon by users who
would see the behaviour change as a regression, even if the previous
behaviour was not intended by the developers?

-  Pure dep8 changes and other test improvements do not require
   paperwork.

-  Review process

   -  We work on a rota. Cannot deal with SRU issues raised on our
      non-SRU days.

-  | If submitting an SRU that appears to be fixing a security issue,
     must receive an ack from the security team that they don't consider
     it appropriate for the security pocket process instead, or
     otherwise provide an explanation.

-  Mitigating difficulties in regression handling

   -  Do not publish on Fridays or during the weekend.
   -  Have the uploading developer available

Idea from Lucas Moura: examples of things that cause regressions that
are surprising:

-  Changing the service name and description of a Pro Service. There
   were translations for the service description, and so changing the
   name caused translation regressions.
-  apt-news and debconf prompt

Move documentation about phasing from Brian's blog post into our docs.

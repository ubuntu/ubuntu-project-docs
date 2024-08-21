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

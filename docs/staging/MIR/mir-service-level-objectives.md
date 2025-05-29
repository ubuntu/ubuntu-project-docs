(mir-slo)=

# MIR Service Level Objectives

Reviews take time, scaling up with the complexity of the case. Sadly it is
usually the very complex, very special cases that tend to come in very late --
then the submitters are unhappy with the velocity of the review.

For transparency and to manage expectations, we hereby define the Service Level
Objectives (SLOs) for this process.

Furthermore, to be clear - you can help!

You know in advance what we will check. History shows that a well-prepared case
will pass through more quickly in each phase. By truly caring about tests,
quality, warnings and the many other things we check for, you can help increase
efficiency. So please take all the statements we ask for seriously and try to
fulfill them.

### MIR review SLO

While we aim for more when possible, our goal is to assign (in the weekly meeting)
one review per active MIR member per week, to come back with the result before
the next meeting. On average that means we can handle about 4 cases per week,
sometimes more (if we can make the space or they are trivial) and sometimes
less (PTO times).

So far this used to be enough, and allowed < 1 week responses for almost
all cases for several years now. Except during spikes of everyone dumping huge
changes at the last minute right before feature freeze. Try to avoid that phase,
to help yourself getting a timely review.

The above of course is for the initial review, if everything is fine and no
security review is needed -- then that is it and you are done. But findings
have to be answered or fixed and, if needed, a security review has to be
exercised. The time for this depends on the complexity of the findings -- and
remember that there have been cases as bad as being rejected, forcing the
requester to look for alternative solutions.

Please consider this in your estimations when you plan a contribution.

### Security review SLO

Security team MIRs are laborious and require lead time. Make MIR requests as
early in a release cycle as possible, ideally well before Feature Freeze. For
an MIR to be considered for a release, it must be assigned to the Security
team (by the MIR team) *before* Beta Freeze. This does not guarantee that a
security review can be completed by Final Release. Ask the director of
Security for exceptions.

The best ways to contact the Security team about MIRs is the
[MIR / Audits Jira Page](https://warthogs.atlassian.net/jira/software/c/projects/SEC/boards/594)
or through the Mattermost channels `~mir-security-review-priority` or `~security-engineering`.

Teams are encouraged to set the relative importance of MIRs they own on the
[MIR / Audits Jira Page](https://warthogs.atlassian.net/jira/software/c/projects/SEC/boards/594).
Security attempts to work across and prioritize all teams equally.
Jira priority drives the order we work on MIRs.


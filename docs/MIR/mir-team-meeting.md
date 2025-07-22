(mir-team-meeting)=
# MIR team weekly status meeting

The MIR Team holds weekly meetings for 30 minutes every Tuesday at
<time datetime="T16:30+01:00">16:30 CET</time> on the
[Ubuntu Matrix Server](https://ubuntu.com/community/communications/matrix)
in the [Ubuntu Main inclusion requests](https://matrix.to/#/#ubuntu-mir:ubuntu.com) channel.

The purpose of the meeting is:

* to allocate a fair share of work between each member of the MIR team
* to provide a timely response to reporters of MIR requests
* to detect and discuss any current or complex cases

You should attend these meetings if you submit an MIR request, until it is
approved or rejected.

Due to the nature of the
[Ubuntu Development Process](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/2.0-preview/explanation/development-process/),
there are times (e.g. close to Feature Freeze) when this meeting is busy and
others (e.g. right after a new release) when it is quieter. Consequently,
response times to MIR requests are (on average) usually faster in those quieter
periods after the release of a new Ubuntu version.


## Meeting template

If you're chairing the meeting, you can use the following template:

```
# Start of the Main inclusion request team meeting
Welcome to the MIR Team's weekly meeting
General rules and the process description can be found at https://canonical-ubuntu-project.readthedocs-hosted.com/MIR/main-inclusion-review
Ping for MIR meeting members - @didrocks:matrix.org @joalif:matrix.org @seth-arnold:ubuntu.com @paelzer:ubuntu.com @mylesjp:matrix.org @pushkarnk:matrix.org ( @dviererbe:ubuntu.com @slyon:ubuntu.com )

## Topic 1/7: Awareness of external agenda items
### Mission: To be aware and potentially allocate the required time, poll if anyone attending has discussions that should be added to the agenda today.
Please speak up if you have a topic to add

## Topic 2/7: Current component mismatches
### Mission: Identify required actions and spread the load among the teams
Check these generated reports:
* [component-mismatches-proposed](https://people.canonical.com/~ubuntu-archive/component-mismatches-proposed.svg)
* [component-mismatches](https://people.canonical.com/~ubuntu-archive/component-mismatches.svg)

## Topic 3/7: New MIRs
### Mission: ensure to assign all incoming reviews for fast processing
Check this launchpad bug list:
* [New MIRs](https://bugs.launchpad.net/ubuntu/?field.searchtext=&orderby=-date_last_updated&field.status%3Alist=NEW&field.status%3Alist=CONFIRMED&assignee_option=none&field.assignee=&field.subscriber=ubuntu-mir)

## Topic 4/7: Incomplete bugs / questions
### Mission: Identify required actions and spread the load among the teams
Check this launchpad bug list:
* [Incomplete bugs](https://bugs.launchpad.net/ubuntu/?field.searchtext=&orderby=-date_last_updated&field.status%3Alist=INCOMPLETE_WITH_RESPONSE&field.status%3Alist=INCOMPLETE_WITHOUT_RESPONSE&field.subscriber=ubuntu-mir)

## Topic 5/7: Process/Documentation improvements
### Mission: Review pending process/documentation pull-requests or issues
Check these GH based lists:
* [PRs](https://github.com/ubuntu/ubuntu-project-docs/pulls?q=is%3Aopen+is%3Apr+label%3AMIR)
* [Issues](https://github.com/ubuntu/ubuntu-project-docs/issues?q=is%3Aissue%20state%3Aopen%20label%3AMIR)

## Topic 6/7: MIR related Security Review Queue
### Mission: Check on progress, do deadlines seem doable?
* ensure your teams items are prioritized among each other as you'd expect
* ensure community requests do not get stomped by teams calling for favors too much
* [Security assigned MIR in launchpad](https://bugs.launchpad.net/~ubuntu-security/+bugs?field.searchtext=%5BMIR%5D&assignee_option=choose&field.assignee=ubuntu-security&field.bug_reporter=&field.bug_commenter=&field.subscriber=ubuntu-mir&orderby=-date_last_updated&start=0)
* [(internal) kanban board](https://warthogs.atlassian.net/jira/software/c/projects/SEC/boards/594)

## Topic 7/7: Any other business?
### Mission: catch-all chance for anything missed or not covered by the usual agenda items.
Please also report if you have nothing, so we know that no one has fallen asleep :-P

# End of the Main inclusion request team meeting
```


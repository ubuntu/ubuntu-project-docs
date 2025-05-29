# Main Inclusion Review (MIR) process

Packages in Ubuntu {term}`main` (and {term}`restricted`) are officially
maintained, supported and recommended by the Ubuntu project.
{term}`Canonical` provides security updates, standard support services, and
certain {term}`SLA` guarantees for these packages.

Therefore, special consideration is necessary before adding new packages
to `main` or `restricted`. The [Ubuntu MIR team](https://launchpad.net/~ubuntu-mir)
reviews packages for promotion:

* from {term}`universe` to `main`.
* from {term}`multiverse` to `restricted`.

The process of reviewing packages before they can be promoted is the
**Main Inclusion Review (MIR)** process.

## The MIR documentation

The guidelines and review process is constantly evolving. Even if you have
submitted a package for Main Inclusion Review in the past, you should still
re-read the MIR documentation.

The MIR documentation is also a living document. External contributions,
suggestions, discussions or questions about the process are always welcome. We
would love to hear from you!

To contribute, simply submit a pull request with your changes or create an
issue as described in our {ref}`Contributing guide<contribute>`. Please
also attend the weekly {ref}`MIR Team meeting <mir-team-meeting>` if you want
to discuss your issue with the MIR Team.

## MIR process overview

* {ref}`mir-process-states`

```{admonition} To do
:class: note

Add the simplified overview of the MIR state machine diagram here
```

## MIR documentation

```{note}
This section just collects all the documentation pages together for ease of
reference-- this is not the final format.
```

* {ref}`mir-requirements`
* {ref}`mir-templates-and-rules`
* {ref}`mir-file-a-bug`
* {ref}`mir-review-a-bug`
* {ref}`mir-slo`

* {ref}`mir-helpers`

* {ref}`mir-exceptions`
  * {ref}`mir-exceptions-oem`

* {ref}`mir-rust`


(mir-team-meeting)=
## MIR team weekly status meeting

The MIR Team holds weekly meetings every Tuesday at
<time datetime="T16:30+01:00">16:30 CET</time> on the {term}`IRC` server
`irc.libera.chat` in the `#ubuntu-meeting` channel. You can follow
[these instructions](https://libera.chat/guides/connect) on how to connect to
`irc.libera.chat`.

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

### Meeting structure

In such quiet phases the leader of the meeting can pre-check the links we
usually check together, and skip steps of the agenda quoting that a
pre-check has not shown anything worth discussing.

From there we can then go rather directly to *Any other business?*
which serves as a catch all for all attendees. By that we can make the
meeting more efficient in those times, instead of filing a monologue-log
every week.

If you're chairing the meeting, you can the following meetingology
template:

```
#startmeeting Weekly Main Inclusion Requests status

Ping for MIR meeting - didrocks joalif slyon sarnold cpaelzer mylesjp pushkarnk ( dviererbe )

# Awareness of external agenda items
Mission: To be aware and potentially allocate the required time, poll if anyone attending has discussions that should be added to the agenda today.

#topic current component mismatches
Mission: Identify required actions and spread the load among the teams

#link https://people.canonical.com/~ubuntu-archive/component-mismatches-proposed.svg
#link https://people.canonical.com/~ubuntu-archive/component-mismatches.svg

#topic New MIRs
Mission: ensure to assign all incoming reviews for fast processing

#link https://bugs.launchpad.net/ubuntu/?field.searchtext=&orderby=-date_last_updated&field.status%3Alist=NEW&field.status%3Alist=CONFIRMED&assignee_option=none&field.assignee=&field.subscriber=ubuntu-mir

#topic Incomplete bugs / questions
Mission: Identify required actions and spread the load among the teams

#link https://bugs.launchpad.net/ubuntu/?field.searchtext=&orderby=-date_last_updated&field.status%3Alist=INCOMPLETE_WITH_RESPONSE&field.status%3Alist=INCOMPLETE_WITHOUT_RESPONSE&field.subscriber=ubuntu-mir

#topic Process/Documentation improvements
Mission: Review pending process/documentation pull-requests or issues

#link https://github.com/canonical/ubuntu-mir/pulls
#link https://github.com/canonical/ubuntu-mir/issues

#topic MIR related Security Review Queue
Mission: Check on progress, do deadlines seem doable?

Some clients can only work with one, some with the other escaping - the URLs point to the same place.
#link https://bugs.launchpad.net/~ubuntu-security/+bugs?field.searchtext=%5BMIR%5D&assignee_option=choose&field.assignee=ubuntu-security&field.bug_reporter=&field.bug_commenter=&field.subscriber=ubuntu-mir&orderby=-date_last_updated&start=0
#link https://bugs.launchpad.net/~ubuntu-security/+bugs?field.searchtext=[MIR]&assignee_option=choose&field.assignee=ubuntu-security&field.bug_reporter=&field.bug_commenter=&field.subscriber=ubuntu-mir&orderby=-date_last_updated&start=0

Internal link
- ensure your teams items are prioritized among each other as you'd expect
- ensure community requests do not get stomped by teams calling for favors too much
#link https://warthogs.atlassian.net/jira/software/c/projects/SEC/boards/594

#topic Any other business?
Mission: catch-all chance for anything missed or not covered by the usual agenda items.

#endmeeting
```





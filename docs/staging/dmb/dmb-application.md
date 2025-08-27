(dmb-application)=
# DMB application process

```{note}
[Page source](https://wiki.ubuntu.com/DeveloperMembershipBoard/ApplicationProcess)
```


## When to apply for team membership

It can be difficult to know when you are ready to apply for uploader team
membership. Here are some guidelines:

* There is no minimum number of sponsored uploads into the Archive that you need
  to have. You need to have demonstrated enough previous work to be able to
  assure your endorsers that you can be trusted with unsupervised upload access
  to the primary Archive.  

  * On your application wiki page, you will describe your areas of work. As a
    guideline, the DMB will expect to see that you have demonstrated competence
    in at least those areas.  

* At least some of your endorsers should be your (future) peers. If you are
  applying for upload rights to a package set, for example, we will expect to
  see your fellow set members providing endorsements.

* You should have knowledge of the Ubuntu release cycle and processes (for
  example SRUs).

* It is nice and probably makes your application easier if you are a part of the
  development community. Consider hanging out on IRC, joining in with
  discussions and helping new contributors.  

* You are encouraged to participate in peer review and to help with the
  training of new developers. This will make your application stronger.

* The DMB will expect you to have a need to upload directly such that membership
  of the requested team will fulfil this need. Usually the need is to reduce
  friction by eliminating sponsorship delays and/or the burden of sponsorship
  review work from your sponsors. In this case you will be expected to
  demonstrate your need in the form of already sponsored uploads to some of the
  packages for which you are requesting direct upload access. These examples
  will also help the DMB to assess your technical readiness to upload the
  requested packages without sponsorship supervision.


## Applying for team membership


To become a {ref}`ubuntu-developers-contributing`,
{ref}`MOTU <ubuntu-developers-motu>`,
{ref}`Per-Package Uploader <ubuntu-developers-per-package>`,
{ref}`Core Developer (core-dev) <ubuntu-developers-core-dev>`,
{ref}`SRU developers <ubuntu-developers-sru>` or
developer of a delegated team for which the DMB handles applications, you must
apply to the {ref}`Developer Membership Board <dmb>` via the following process:

* Create a dedicated wiki page for your application, using the
  [Ubuntu Development/Developer Application Template](https://wiki.ubuntu.com/UbuntuDevelopment/DeveloperApplicationTemplate).  

* Ask other developers to endorse your application by adding information to your
  wiki page. A typical application will have three to five endorsements.
  Developers who [sponsored several uploads for you](https://udd.debian.org/cgi-bin/ubuntu-sponsorships.cgi)
  are good candidates.  

* {ref}`Add yourself to the agenda <dmb-agenda>` on a suitable application
  meeting date.

* Announce your application and meeting date from the previous step (agenda) by
  writing an email to the `devel-permissions@` list, which includes:  

  * The link to your wiki page application.  

  * The date of your meeting date and a link to the agenda.  

* Attend the meeting in `#ubuntu-meeting` on `irc.libera.chat` (to get an idea
  of the format of the meeting, you can read some of the
  [old meeting logs](https://wiki.ubuntu.com/DeveloperMembershipBoard/Logs)).

All members of the development community are welcome to attend and ask
questions, add your feedback (even if unsolicited) to the application wiki page
or ask questions of an applicant on the
[`devel-permissions` mailing list](https://lists.ubuntu.com/mailman/listinfo/devel-permissions).

Please note that anyone applying for an Ubuntu development team membership is
required to have read and signed the {ref}`Ubuntu Code of Conduct <code-of-conduct>`),
as visible under `https://launchpad.net/~<LPUSERNAME>/+codesofconduct`.

The {ref}`Developer Membership Board <dmb>` will have prepared for the meeting
(reviewed the application details, checked a few examples of your work, talked
to sponsors, etc.) and ask questions to make sure the applicant qualifies for
the team.
During the meeting the DMB members will cast their votes.
There is no mandatory abstience of voters due to knowing the applicant - after
all we are looking for just that: evidence and endorsements from people knowing
the applicants work and behavior. If a DMB member feels biased by having a
personal relationship they can themselfe decide to abstain to avoid a conflict
of interest.
If quorum is reached (4 of 7 currently), will add the applicant to the
requested team.
If no approving quorum was reached the DMB members might, if possible, suggest
what to study or work on, and ask the applicant to then re-apply in due time.

For part of the world (e.g APAC) where the DMB meeting times can be challenging
to attend due to the timezone gap, note that the DMB usually tries to be
accomodating. While the preference always remains the IRC interview meeting, the
DMB team can exceptionally do the interview by email if the applicant cannot
make the regular meeting times. Please reach out to the DMB team to let them
know if you fall into this category.


## Debian Developers applying for Per-Package Upload rights

The DMB has established a procedure for interested Debian Developers to gain
upload rights to their packages, on a dynamic and ongoing basis. That is, the
list of packages one can upload can be further extended after the initial
application to include other packages the Debian Developer maintains. This
includes team-maintained packages.

To exercise this process, the Debian Developer should first be an existing
Ubuntu developer, for example by applying for Per-Package Upload rights as per
the above process or by joining the MOTU team if interest is broad. Subsequent
changes are requested by mailing `devel-permissions@lists.ubuntu.com` listing
the packages to add. If the "impact" of the packages changes -- for example, one
of the packages is part of release media for the first time -- the DMB may wish
to ask some further clarifying questions to satisfy itself that the Debian
Developer is sufficiently familiar with the differences between Ubuntu and
Debian to upload the package(s) in question without supervision.


## Applying for upload permissions which grant no further access

The DMB recognizes that individuals may wish to become members of teams they
have no *technical* reason to want to join, so that they may feel explicitly
included as a member of the team.

For such "social" applications, the DMB will expect to see evidence of a large
degree of social involvement in the team. Examples include mentoring new
contributors and discussing policy.

It would be helpful if applicants could seek endorsements from existing members
of the team when applying.


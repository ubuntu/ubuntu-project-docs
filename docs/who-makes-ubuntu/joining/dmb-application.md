(dmb-application)=
# Developer Membership application process

```{note}
[Page source](https://wiki.ubuntu.com/DeveloperMembershipBoard/ApplicationProcess)
```

```{toctree}
:titlesonly:
:hidden:

dmb-application-knowledge-requirements
dmb-aspects-of-a-good-application
```

To become an {ref}`Ubuntu Contributing Developer <ubuntu-developers-contributing>`,
{ref}`MOTU <ubuntu-developers-motu>`,
{ref}`Per-Package Uploader <ubuntu-developers-per-package>`,
{ref}`Ubuntu Core Developer (core-dev) <ubuntu-developers-core-dev>`,
{ref}`SRU developer <ubuntu-developers-sru>` or
developer of a delegated team for which the DMB handles applications, you must
apply to the {ref}`Developer Membership Board <dmb>` via the processes outlined
on this page.


## Application process

Reserve your spot
: Check the Developer Membership Board (DMB) [agenda](https://discourse.ubuntu.com/t/ubuntu-developer-membership-board-agenda/66634)
  to see when the DMB next meeting is, and to check the queue of applications.
  Only 2 applications are considered each meeting so if there's a queue, make
  sure to reserve a spot for when you think you'll be ready for consideration.

Create your space
: If it's your first time applying for upload rights,
  {ref}`packageset-create-discourse-post`. If you already have a page, you can
  reuse it.

Training and preparation
: The depth of your learning here depends on the upload rights you are applying
  for:
: 1. {ref}`PPU or Package Set <packageset-training-and-preparation>`  
: 1. {ref}`MOTU <motu-training-and-preparation>`
: 1. {ref}`Core Developer <core-dev-training-and-preparation>`

Prepare application form
: {ref}`packageset-prepare-application-form` on your Discourse post.

Collect endorsements
: {ref}`packageset-collect-endorsements` from those who have worked with you.

Once you have enough endorsements
: If you haven't already, add yourself to the
  [DMB agenda](https://discourse.ubuntu.com/t/ubuntu-developer-membership-board-agenda/66634).
: Then you can announce your application and meeting date by writing an email
  to the `devel-permissions@` mailing list. Your email should include:

  * The link to your Discourse application page

  * The date you reserved for your meeting

  * A link to the meeting agenda

Attend your meeting
: Then you can {ref}`attend your meeting <dmb-application-meeting>`, answer
  questions, and receive your votes.


(packageset-create-discourse-post)=
### Create a Discourse post for yourself

Create a dedicated Discourse page for your application, using the
[Developer Application Template](https://discourse.ubuntu.com/t/developer-application-template/66670).

On this page you should (at least):

* Introduce yourself and your past Ubuntu-related work

* Include a "Contact Information" section with

  * Your Matrix nickname

  * Your Launchpad ID

You can look at other people's pages for ideas of other things you can include.
You'll be reusing this text in your membership applications later.


(packageset-prepare-application-form)=
### Prepare your application form

In your {ref}`personal Discourse page <packageset-create-discourse-post>`,
copy and paste the
[Developer Application Template](https://discourse.ubuntu.com/t/developer-application-template/66670)
and add your details in each section.

```{note}
You can look at
[past Wiki applications](https://wiki.ubuntu.com/Home?action=fullsearch&context=180&value=DeveloperApplication&titlesearch=Titles)
such as
[`Paride`'s](https://wiki.ubuntu.com/ParideLegovini/UbuntuServerDeveloperApplication)
or check out the [Discourse membership section](https://discourse.ubuntu.com/c/community/membership/93)
if you need some examples.
```

Specify in your post title what upload rights you're applying for.


(packageset-collect-endorsements)=
### Collect endorsements

To gain upload rights, you'll need to collect endorsements from people who have
sponsored your packages. Ask other developers to endorse your application by
replying to your Discourse page.

A typical application has three to five endorsements. Developers who
[sponsored several uploads for you](https://udd.debian.org/cgi-bin/ubuntu-sponsorships.cgi)
are good candidates. It's good form to only ask people who have sponsored
multiple packages for you, or that have worked with you on particularly tricky
packaging efforts. You want to strike a good balance between quality and
quantity here.
 
If you work for Canonical, ask in your team's regular discussion channels, and
individually contact each sponsor who is not in your team.

For applications for MOTU, you should seek endorsements from people who have
reviewed or sponsored your packages, or worked with you on noteworthy packaging
efforts. If you work for Canonical, seek out diversity in your endorsers by
looking outside your immediate team. Since MOTU is more focused on community
maintainers, their testimonials are of particular value. Even words from
noteworthy Debian maintainers can carry weight for MOTU applications.


## When to apply for team membership

It can be difficult to know when you are ready to apply for uploader team
membership. Here are some guidelines:

* There is no minimum number of sponsored uploads into the Archive that you need
  to have. You need to have demonstrated enough previous work to be able to
  assure your endorsers that you can be trusted with unsupervised upload access
  to the primary Archive.  

  * On your application Discourse page, describe your areas of work.
    As a guideline, the DMB expects to see that you have demonstrated
    competence in at least those areas.  

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


(dmb-application-meeting)=
## What to expect at the DMB meeting

All members of the development community are welcome to attend and ask
questions, add your feedback (even if unsolicited) as comments to the
application Discourse page or ask questions of an applicant on the
[`devel-permissions` mailing list](https://lists.ubuntu.com/mailman/listinfo/devel-permissions).

Please note that anyone applying for an Ubuntu development team membership is
required to have read and signed the {ref}`Ubuntu Code of Conduct <code-of-conduct>`),
as visible under `https://launchpad.net/~<LPUSERNAME>/+codesofconduct`.

The {ref}`Developer Membership Board <dmb>` will have prepared for the meeting
(reviewed the application details, checked a few examples of your work, talked
to sponsors, etc.) and ask questions to make sure the applicant qualifies for
the team.
During the meeting the DMB members will cast their votes.

There is no mandatory abstinence of voters due to knowing the applicant - after
all we are looking for just that: evidence and endorsements from people knowing
the applicant's work and behavior. If a DMB member feels biased by having a
personal relationship they can choose to abstain to avoid a conflict
of interest.

If quorum is reached (4 of 7 currently), the applicant will be added to the
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


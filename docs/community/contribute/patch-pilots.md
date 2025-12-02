(patch-pilots)=
# Patch Pilots

Welcome to the Patch Pilot Program!

Our aim is to support contributors with their patches, package sponsoring, and other activities to improve Ubuntu.
The program is designed to make contributing to Ubuntu a welcoming and inspiring experience while fostering community knowledge and maintaining ongoing contributions.


## Get help from a Patch Pilot

Are you interested in contributing patches to Ubuntu?
There are a number of ways to participate, and through this program we'd like to provide you with mentoring and support in getting your patches into Ubuntu.
You should reach out to a Patch Pilot if:

* You have a {ref}`patch against an Ubuntu-specific package <sponsorship>` that you'd like to contribute.
* Your package can't go into Debian and you'd like to contribute a {ref}`new Ubuntu-specific package <new-packages>`.
* You'd like a new package or patch to appear in Ubuntu, but need some guidance on how to make it part of Debian.

Patch Pilots are available in the {matrix}`devel` channel on [Matrix](https://ubuntu.com/community/communications/matrix) and will be monitoring bugs with patches on Launchpad.
The current Pilot is noted in the channel topic.
If you'd like to plan ahead, see the [<a href="https://calendar.google.com/calendar/embed?showPrint=0&showCalendars=0&mode=WEEK&src=Y184ZWRhZjk2OTllYWFmMWFmMmNjYTY2ZTYyOGZkNDEwODQ2ZTkwMjcwNmQ2YTMzMTU1OTNmODhiOTk0ZTZlOWE2QGdyb3VwLmNhbGVuZGFyLmdvb2dsZS5jb20&color=%23F4511E">Ubuntu Patch Pilots</a> calendar.


## Being a Patch Pilot

As a Patch Pilot, you will be a primary contact in supporting the community towards Ubuntu development.
It is the development equivalent of being "on call" in the site reliability engineering (SRE) world.


### Welcoming the community

We value the support from Ubuntu community members and strive to create a positive and engaging atmosphere.
To achieve this, we identify contributors with potential to grow as advocates or future Patch Pilots while ensuring that all contributors are treated respectfully, provided with learning resources, and supported throughout their journey.

Some techniques to foster engagement include:

* Thanking contributors for their contributions and time commitment
* Offering encouragement and highlighting their strengths
* Informing contributors of their progress and setting expectations


### Reasonable contributions

Please do your best to accept contributions in any reasonable form.
Remember, every contributor has their own unique journey and way of giving.
All we ask is that the submitted contribution is functional (e.g. patch applies), builds correctly, and has been tested.
If you're ever uncertain, here are some examples of where you as a Patch Pilot can support contributors:

* Patch against the wrong git branch
* Needs a quilt patch rather than a change directly to upstream sources

If there are opportunities to improve tooling for uncommon types of contributions, please discuss on the [`ubuntu-devel` mailing list](https://lists.ubuntu.com/archives/ubuntu-devel/).
You are welcome to point contributors to guides on preferred ways to contribute for their future patches, which helps them learn more about our ecosystem.


### Activities breakdown

Sponsoring queue
: The primary focus is the [general sponsoring queue](http://sponsoring-reports.ubuntu.com/general.html). The Patch Piloting program is designed to support community contributors to Ubuntu. When reviewing changes and sponsoring uploads, keep the following in mind:
: * Prioritize community contributions before contributions by Canonical employees
: * Prioritize items waiting the longest
: * Manage expectations by informing contributors about expected feedback times
: * Avoid moving goal posts and provide thorough explanations when abandoning long-pending changes


Availability on Matrix
: During your Piloting session, you are the primary representative for inquiries in {matrix}`devel` on Matrix. Address questions about contribution processes, technical patch issues, or repository support while fostering encouraging conversations about patch contributions.

: When you begin your session, please write `@pilot in` in {matrix}`devel`, which will add a note to the topic that you are the current Patch Pilot. Once your session is finished, use `@pilot out` to remove yourself.

: When conversing on other platforms such as Launchpad, you are also welcome to point patch authors to {matrix}`devel` and this program to continue discussions. If contributors reach out to you outside of your session, feel free to refer them to the current Patch Pilot.


Operation Cleansweep
: There is a growing number of <a href="https://bugs.launchpad.net/ubuntu/+bugs?field.subscriber=ubuntu-reviewers&field.tag=-patch-needswork%20-patch-forwarded-upstream%20-patch-forwarded-debian%20-patch-accepted-upstream%20-patch-accepted-debian%20-patch-rejected-upstream%20-patch-rejected-debian%20-patch-rejected&field.tags_combinator=ALL">open bugs with patches on them</a>. Following the [Review Guide](https://wiki.ubuntu.com/ReviewersTeam/ReviewGuide#Workflow), you can help make sure community members have the support they need to get their patches into Ubuntu. Contributors might occasionally need clarification on the guidelines, and we're here to provide support and guidance.


Developer documentation
: There's extensive documentation on Ubuntu Development in these Ubuntu Project docs. Even small changes can greatly improve the documentation, ensuring it remains updated and effective. This is a great opportunity to improve on that, which will decrease recurring questions over time.

: If you are unsure about the scope of your changes and would like some guidance, please reach out to {matrix}`documentation`. However, don't be afraid to make more extensive changes. A large amount of outdated documentation can cause more harm than a small amount of available up-to-date information.


### Program logistics

Communication and handoff
: The primary channel to exchange information as a Patch Pilot is {matrix}`devel`. Please avoid private messages unless needed, as this helps keep the community in the loop and provides context for the next Patch Pilot.

: After completing your work, provide a helpful handoff to the next Patch Pilot, including context and additional instructions as needed. Handoff should be posted in the [Patch Pilot handoff thread](https://discourse.ubuntu.com/t/patch-pilot-hand-off-25-10/60037) for the 25.10 cycle.


Requirements
: To be a Patch Pilot, you need to be able to upload packages to Ubuntu. There are a number of ways to get there, but the first step is to become an {ref}`Ubuntu Developer <ubuntu-developers>`.

: When you begin Patch Piloting, ask to be added to the [Ubuntu Sponsors](https://launchpad.net/~ubuntu-sponsors/) group as well. If you're not currently an Ubuntu Developer but wish to become one, {ref}`find out how to apply <dmb-application>`.

Time commitment
: Our rotation schedule presently results in one pilot session every 3 weeks. Each session lasts up to 4 hours, designed to offer uninterrupted time for contributors to ask questions. However, if you're a community member interested in joining and have concerns about the session duration, please reach out. We're open to feedback and discussions about possible adjustments to make participation feasible for you.

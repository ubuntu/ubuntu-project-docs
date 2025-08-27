(dmb-aspects-of-a-good-application)=
# DMB Aspects of a good application

```{note}
[Source page](https://wiki.ubuntu.com/RobieBasak/DMB/Expectations)

```

Since every applicant is unique, what makes a "good" DMB application can be flexible. No two applications are ever exactly the same, and everyone has a different position to some extent.

If you need different considerations for some reason, make sure to explain this in your application and we are happy to consider it.

## Track record

Applicants must have an existing track record of sponsored uploads to the packages they are requesting direct upload access to.
The DMB normally approves applications either to reduce contributor friction in needing sponsorship or to save the work of sponsors.

Example:

* Alice is working diligently on Openstack packages, getting many sponsored uploads every cycle. After a second cycle, in which only minimal / minor changes needed to happen, Alice feels confident in applying for cloud packageset upload rights.

## Culture

The Ubuntu development process and {ref}`Code of Conduct <code-of-conduct>` dictates that all actions by Ubuntu developers be considerate, respectful, responsible, collaborative, balancing between decisiveness and consensus.

Individuals are empowered to propose changes from the bottom upwards through delegated authority. This relies on individual developers understanding when other team members will be affected, if there could be possible objections, and being active in seeking collaboration and consensus when conflicts occur.

Examples:

* Bob is a long-time Ubuntu user who recently had issues with a package. First, Bob opens a bug on the package to explain the issue. Through more serious debugging, Bob identifies a root cause and a possible patch. The patch is fairly invasive, and will cause an ABI change. Bob adds a comment to the bug describing all the debugging efforts and attaches the patch. Carol maintains the package and notices the fix will affect ABI. A discussion follows, to ensure a patch can be made that keeps the stable ABI while addressing Bob's problem. This shows collaboration from Bob and Carol; Carol as package maintainer showing knowledge of the Ubuntu ecosystem and what is acceptable, and Bob's respectful interactions and willingness to amend the patch. Big kudos to everyone involved.

* Daryl is a Core Dev, and decides it's time to move ahead of Debian for a major library. Without discussion with any team or other Core Devs, Daryl uploads a new version of the major library during the development period. Ubuntu development grinds to a halt as many projects are suddenly affected  by problems like nebulous build errors and confusing autopkgtest failures. Daryl only sends an email to the mailing list *after upload*, with no discussion of what breaking changes the upload may cause. This action shows poor judgement, a lack of understanding of the ecosystem, and was generally inconsiderate. What should Daryl have done?

## Communication

Becoming an Ubuntu member means joining a global team of diverse developers working together on a common project.
It is expected you should be in regular contact with developers, both in relation to your own work and in helping others, so you can build connections and trust with your peers.
For a Core Dev, this means across the entire Ubuntu ecosystem. For MOTU, it is more focused on `universe` or Flavors, and the scope narrows down through the levels.
You should communicate in the appropriate public channels, such as Matrix, Discourse, or mailing lists.

You do not have to fill the channels with non useful messages.
But if you have not/rarely been active in public communication, depending on your other provided evidence that might cause doubts
if you are able to coordinate well and know when you should reach out - if that is the case it will affect your application negatively.

Examples:

* Daryl, learning from their past mistake, is working on their communication. Before their next upload, they produce an informative Discourse entry with changelog information and possible issues that could happen. Along with the Discourse post, they post a topic in the mailing list, alerting everyone that they are planning the change on a specific date. They've prepared a PPA already and are considering a series of test builds to ensure issues are caught. Several Ubuntu members voice concerns, and ask for tests of their packages in `main`. Daryl works with everyone to ensure a smooth transition, unblocking members during the testing and upload of their major library.

## Endorsements and application materials

Applicants must follow the {ref}`DMB application process <dmb-application>` to collect their materials on an application page.
The application must contain evidence of appropriate work for the level of upload rights, if you can also provide evidence of the learning topic along the way even better.
Topics must include endorsements from current Ubuntu members, developers, and uploaders.
When applying for a specific level, having endorsements from current members with the same rights is required.

For Canonical employees, it is recommended to have endorsements of members outside of Canonical.
Depending on the upload rights being pursued, and breadth of delegated power, an applicant should have endorsements from outside their current Canonical organization.

Including endorsements from sponsors is the best way to show evidence.
If an application lacks endorsements from major package sponsors, it will negatively impact an application if it causes the suspicion that those that have seen a lot of your work would not support your application.
That does not mean, if you have many sponsors, that all of them have to endorse you, but help us to understand why some has been left out.

Example:

* Evelyn is a member of the Canonical Foundations Toolchain Squad. They have worked extensively on Zig, not just on the toolchain but on many leaf packages. Over time, Evelyn has built up a portfolio of helping across Ubuntu, not just with Zig but in other areas. First, they applied for a speciality packageset `zig-packages`, and got endorsements from current packageset uploaders and a Core Dev, all within Canonical Foundations (but including a Core Dev outside their immediate team). When applying for Core Dev, they went through their uploads and asked sponsors from Debcrafters and Server to provide endorsements as well. This shows a work across immediate Canonical Teams.

* Frederick is a member of Canonical Support Engineering. Their work has been focused on SRUs of fixes to stable releases. They attained SRU-dev and are working toward Core Dev. In their first application, they only included endorsements from current Support Engineering members. This application will raise concerns from the DMB over Frederick’s communication and culture fit.

* Günther is working in the project for quite some time. They have 2 contributions to 3 packages each - and the people sponsoring those have endorsed Günther. But those have been long ago and there are two other sponsors that have done the majority of the work of Günther in recent years. Without an explanation that will make people question if that recent work was not good quality.

## Knowledge of Ubuntu Development

There are many things to know about, from a thorough understanding of (and experience in) Debian packaging, to Ubuntu-specific aspects such as Ubuntu package merges, SRUs, the release cycle, milestones and exceptions, autopkgtest and proposed migration, handling transitions, the operation of the seeds and MIRs.

We expect demonstrated understanding and evidence of such. An extended list is outlined at {ref}`DMB Application Knowledge Requirements <dmb-application-knowledge-requirements>`

## Use the different stages to your advantage

We would expect a Core Dev applicant to be an already experienced Ubuntu uploader through one of the other uploading teams such as a packageset or MOTU.
To directly go to Core Dev we would expect an **exceptionally** strong application. It is hard to go from zero to hero, but it does not have to be!

Socially, we prefer to approve people -- and you prefer to be approved -- so we suggest not applying for the strictest permissions immediately.

Please consider applying in steps. Start with something easier, matching your experience and contributions.
Use these permissions to further collaborate and extend your track record, then apply for the next stages sometime later.

# Canonical employees

Working at Canonical does not create a special circumstance where an applicant is excused from Ubuntu-specific knowledge or evidence.

A Canonical employee must demonstrate the same knowledge and skills as any other applicant.

An applicant from Canonical must be able to negotiate the distinction between Ubuntu governance and Canonical priorities.
These can appear to collide, and diplomacy is required to find a solution that works for both sides.
An applicant may not be able to provide direct evidence of this, as they may not have run into it during their journey to upload status, however it is important to demonstrate the leadership and judgement required to navigate the situation.

It is nice, though not required, to get sponsorship from a non-Canonical employee during your journey.
It is required that you communicate openly and clearly with all of Ubuntu, and not just internally at Canonical.
This means taking conversations to Matrix public channels and Ubuntu Discourse when appropriate, and generally engaging in community building.

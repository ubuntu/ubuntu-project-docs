(dmb-aspects-of-a-good-application)=
# DMB Aspects of a good application

```{note}
[Source page](https://wiki.ubuntu.com/RobieBasak/DMB/Expectations)

Note, I have not touched the wording of this document -- only added formatting
to provide visual markers
```

All of this is flexible
No application is exactly the same; everyone’s position is different to some extent
Where a situation calls for different consideration for some reason, I am happy to consider it
If this applies to you, please make sure to explain in your application how you think you need different consideration.

## Track Record

Applicants must have an existing track record of sponsored uploads to packages to which direct upload access is requested
The DMB normally approves applications either to reduce contributor friction in needing sponsorship or to save the work of sponsors.

Example:

* Alice is working diligently on Openstack packages, getting many sponsored uploads every cycle. After a second cycle, in which only minimal / minor changes needed to happen, Alice feels confident in applying for cloud packageset upload rights.

## Culture

The Ubuntu development process and [Code of Conduct](https://canonical-ubuntu-project.readthedocs-hosted.com/how-ubuntu-is-made/governance/code-of-conduct/#code-of-conduct) dictates that all actions by Ubuntu developers be considerate, respectful, responsible, collaborative, balancing decisiveness and consensus
Individuals are empowered to propose changes from the bottom upwards through delegated authority
This relies on individual developers understanding when other team members will be affected, if there could be possible objections, and being active in seeking collaboration and consensus when conflict any occur.

Examples:

* Bob is a long time user in Ubuntu, and has recently had issues with a package. First, Bob opens a bug on the package explaining the issue. Through more serious debugging, Bob identifies a root cause and a possible patch. The patch is fairly invasive, and will cause an ABI change. Bob adds a comment to the bug describing all the debugging efforts and attaches the patch. Carol maintains $PACKAGE and sees that the fix will affect ABI. A discussion ensues to ensure a patch can be made that keeps the stable ABI and addresses Bob's problem. This shows collaboration from Bob and Carol, Carol as package maintainer showing knowledge of the Ubuntu ecosystem and what is acceptable, and Bob's respectful interactions and willingness to amend the patch shows professionalism. Big kudos to everyone involved.

* Daryl is a core-dev and has decided it's time to move ahead of Debian for a major library. Without discussion with any team or other core-devs, Daryl uploads a new version of the major library during the development period. Ubuntu development grinds to a halt as many projects are affected and confused as to what has happened (nebulous build errors, confusing autopkgtest failures). Only after upload does Daryl send an email to the mailing list, with no discussion of what breaking changes the upload may occur. This action shows poor judgement, a lack of understanding of the ecosystem, and was generally inconsiderate. What should Daryl have done?

## Communication

Becoming an Ubuntu member means joining a team of world-wide distributed, diverse developers working together on a common project.
It is expected you be in regular contact with developers, both in relation to your work and in helping others, that way you build connections and trust with your peers
As a core-developer this would mean across the entire Ubuntu ecosystem, MOTU focusing on universe or Flavors, and with a more narrowing scope down through the levels
This communication should be made in the appropriate public channels, such as Matrix, Discourse, or mailing lists
If you have not been active in public communication, it will affect your application negatively.

Examples:

* Daryl, in learning from their past mistake, is working on improving their communication. Before their next upload, they produce an informative Discourse entry with changelog information and possible issues that could happen. Along with the Discourse post, they post a topic in the mailing list, alerting everyone that they are planning the change on a given specific date. They've prepared a PPA already and are considering a series of test builds to ensure issues are caught. Several Ubuntu members voice concerns, and ask for tests of their packages in main. Daryl works with everyone to ensure a smooth transition, helping to unblock members during the testing and upload of $MAJOR\_LIBRARY.

## Endorsements and Application Materials

Applicants must follow the details of the {ref}`DMB application process <dmb-application>` to collect their materials on a page.
The application must contain evidence of appropriate work for the level of upload rights, if you can also provide evidence of the learning topic along the way even better.
Topics must include endorsements from current Ubuntu members, developers, and uploaders.
When applying for a specific level, having endorsements from current members with the same rights is required.
For Canonical employees, it is recommended to have endorsements of members outside of Canonical.
Depending on the upload rights being pursued, and breadth of delegated power, an applicant should have endorsements from outside their current Canonical organization.
Including endorsements from sponsors is the best way to back up your evidence.
If an application lacks endorsements from your package sponsors, it will negatively impact an application.

Example:

* Evelyn is a member of Canonical Foundations Toolchain Squad. They have worked extensively on Zig, not just on the toolchain but on many leaf packages. Over time, Evelyn has built up a portfolio of helping across Ubuntu, not just with Zig but in other areas. First, they applied for a speciality packageset “zig-packages”, and got endorsements from current packageset uploaders and a core-dev, all within Canonical Foundations (but including a core-dev outside their immediate team). When applying for core-dev, they went through their uploads and asked sponsors from Debcrafters and Server to provide endorsements as well. This shows a work across immediate Canonical Teams.  

* Frederick is a member of Canonical Support Engineering. Their work has been focused on SRUs of fixes to stable releases. They attained SRU-dev and are endeavoring toward core-dev. In their first application, they only included endorsements from current Support Engineering members. This application will raise concerns from the DMB over Frederick’s communication and culture fit.

## Knowledge of Ubuntu Development

There are many things to know about, from a thorough understanding and experience in Debian packaging to Ubuntu-specific aspects such as Ubuntu package merges, SRUs, the release cycle, milestones and exceptions, autopkgtest and proposed migration, handling transitions, the operation of the seeds and MIRs.

We expect demonstrated understanding and evidence of such, an extended list of those is outlined at {ref}`DMB Application Knowledge Requirements <dmb-application-knowledge-requirements>`

## Use the different stages to your advantage

We would expect a Core Dev applicant to be an already experienced Ubuntu uploader through one of the other uploading teams such as a packageset or MOTU
To directly go to Core Dev we’d expect an exceptionally strong application
It is hard to go from zero to hero, but it does not have to be
Socially we prefer to approve people and you prefer to be approved \- therefore we suggest not to apply for the strictest permissions right away.

Please consider applying in steps, start with something easier to achieve matching your experience and contributions
Then use these permissions to further collaborate and extend your track record to apply for the next stages sometime later.

# Canonical employees

Working at Canonical does not create a special circumstance where an applicant is excused from Ubuntu specific knowledge or evidence.

It is still expected that you demonstrate the same knowledge and skills as any other applicant.

An applicant from Canonical must be able to negotiate the distinction between Ubuntu governance and Canonical priorities.
These can appear to collide, and diplomacy is required to find a solution that works for both sides.
An applicant may not be able to provide direct evidence of this, as they may not have run into it during their journey to upload status, however it is important to demonstrate the leadership and judgement required to navigate the situation.

It is nice, though not required, to get sponsorship from a non-Canonical employee during your journey.
It is required that you communicate openly and clearly with all of Ubuntu, and not just internally at Canonical.
This means taking conversations to Matrix public channels and Ubuntu Discourse when appropriate, and engaging in general community building.

(dmb-application-knowledge-requirements)=
# DMB application knowledge requirements

```{note}
Extension of [Source page](https://wiki.ubuntu.com/RobieBasak/DMB/Expectations)
based on DMB discussions, and the ubuntu uploaders program feedback
```

There are several {ref}`dmb-aspects-of-a-good-application`, but questions are often asked around what knowledge and evidence an applicant should provide.

In the table below we show the topics, descriptions of what the topic includes, and the depth to which the topic should be understood for each role.
We do not expect rote memorization of answers. 
The objective is to determine your understanding of the underlying reasons for those answers.
This often requires a thorough understanding of the policies, technologies, and processes pertinent to a given topic.

Therefore, while contributing to the Ubuntu project, your focus should be on cultivating understanding rather than being able to provide answers to a predetermined set of questions.
Consider the following not as "questions you must be able to answer," but rather as "topics to comprehend, accompanied by a few illustrative questions that have arisen in the past."

\*1: "expected level" is a non linear, non unit description of how deep a particular topic should be covered. Abbreviated as B \= Basic, I \= Intermediate, A \= Advanced. If an E is present in the column, this will be mostly demonstrated by Evidence over being to answer questions.

| Topic | Description => Expected level\*¹ | |  |  |  |  |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
|  |  | PPU | pkg-set | SRU-dev | MOTU | core-dev |
| **Upstream/Downstream** |  |  |  |  |  |  |
| The Derived Distribution Model | Understanding the derivative model (upstream \-\> Debian \-\> Ubuntu, how deltas are added and managed, basic package versioning in regard to that context. Ubuntu as a derivative) | I | I | B | A | A |
| To fork or not to fork | When adding a delta is appropriate, the maintenance burden of doing so, and how we track and manage that burden | I | A | B | A | A |
| The possibility tree of versions and modifications | Understanding various exceptions to the basic derivative model, such as Ubuntu packaging a new upstream, syncing from experimental, SRUs and security updates as branches of the derivative graph | I | A | B | A | A |
| Ubuntu and Launchpad packaging data model | Understanding the data model of packages, particularly within Launchpad: source and binary package versions being distinct, burning versions, the various pockets and pocket copies, source uploads only, one set of successful builds against each source upload only | I | I | B | A | A |
| Differences between Debian and Ubuntu | Deviations from Debian such as no binNMUs (or any binary uploads), no individual package "ownership", team uploads only, management of transitions | B | B | B | I | A |
| Ubuntu Code of Conduct and decision making | How decisions are made in Ubuntu: CC, TB, Ubuntu Developers at large, and the key privileged teams (SRU, Release, AA). Operating by consensus and how to handle disagreements. | B | B | B | I | A |
| Canonical's interest in Ubuntu | Separation of Canonical and Ubuntu and how to deal with decision making when they are conflicted | B | B | A | I | A |
| **Ubuntu Development** |  |  |  |  |  |  |
| Uploads (not merges or syncs) to Ubuntu development release | Demonstrate the ability to prepare Uploads of good quality and the communication/tracking around doing so. | BE | IE |  | AE | AE |
| Ubuntu package merges and syncs | Demonstration of how to merge and sync packages from Debian to Ubuntu. Understand when this happens automatically, when manual action is required, and the processes we use to ensure that packages don't languish when they don't autosync | BE | IE |  | AE | AE |
| Launchpad's bug model and Ubuntu bugs | How bug tasks work, community expectations from the bug tracker, team ownership and triage of bugs | B | I | IE | IE | AE |
| Development Milestones | Understand the development milestones during the development cycle and what their purpose is.  | B | B |  | I | A |
| Stable Point releases | Active releases will have point releases, which implies freezes, coordinated testing and more -- know your role and interaction with that. | B | B | A | I | A |
| Freeze Exceptions (and how to get one) | Understand when an exception to a development freeze is appropriate and how to request one -- [Freeze Exception Process](https://wiki.ubuntu.com/FreezeExceptionProcess) | B | I | B | B | A |
| *Library Transitions* | Understand how library transitions work in Ubuntu and how they can be tracked. | B | I |  | IE | AE |
| *Operation of Seeds* | Understand the purposes of the Ubuntu Seeds and how to make a change to one -- {ref}`seed-management` | B | B |  | I | AE |
| **Quality assurance** |  |  |  |  |  |  |
| **Ubuntu Proposed Migrations** |  Understand that uploading or sponsoring is not the moment when you are done, what is {ref}`proposed-migration`, what value does it provide to the project and how to deal with the most common cases and issues. | B | I | I | A | A |
| Understand the use of proposed in Ubuntu | Understand how the proposed pocket is used in Ubuntu and how this contributes to the quality of Ubuntu. | B | I | I | I | A |
| Write new autopkgtest tests and run them locally | Understand how to add tests to a Debian package to help ensure the quality of the distribution. | B | I | B | B | IE |
| Understand the autopkgtest Ubuntu queue \=\> update\_excuses | How to parse and understand the information on the regular [excuses page](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_excuses.html). What is and how to handle the less common [update\_output](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_output.txt). | B | B | I | I | A |
| **Active Releases** |  |  |  |  |  |  |
| **Ubuntu Stable Release Update process** | Broad understanding of all [SRU types](https://canonical-sru-docs.readthedocs-hosted.com/en/latest) and how to drive them. Detailed understanding of the specifics required for a standard SRU. Able to identify the next step needed for any given SRU. | B | I | A | I | A |
| Understand the Stable Release Update process | Understand the purpose of the Stable Release Update process and how it operates across released versions of Ubuntu and the development release. | B | I | A | I | A |
| Upload and testing of stable release updates (SRU) | Demonstrate experience of stable release updates to packages in Ubuntu. Multiple uploads to the same are good, but the wider the application should allow uploads the more demonstrating some width is required. | BE | BE | IE | IE | AE |
| **Universe vs Main** |  |  |  |  |  |  |
| **Main Inclusion Review (MIR) process** | Understand the {ref}`MIR process <main-inclusion-review>`, its purpose. When invoking that process is needed and how to do so. | B | I |  | B | A |
| Understand main vs universe | Why does the [split exist](https://documentation.ubuntu.com/server/tutorial/managing-software/#where-do-packages-come-from%20), what does it mean to the Developer and what to the user | B | I | B | B | A |
| MIR submission | Having submitted, and finalized MIR cases |  | BE |  |  | IE |

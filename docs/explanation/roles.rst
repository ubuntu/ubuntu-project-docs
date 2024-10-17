.. _explanation-role-expectations:

Role expectations
-----------------

The SRU team is a narrowly scoped team that has privileged access:
primarily to "accept" packages from the stable series' unapproved queues
into the -proposed pocket, and "release" packages from the -proposed
pocket into the -updates pocket. Reviews and decision making, and the
policy, processes and documentation around these reviews and decision
making are the responsibility of the SRU team.

Other work that does not require elevated privilege, such as bug triage
and management, preparing updates, performing QA, handling any follow-on
regression reports and so forth, can be performed by any Ubuntu
developer or prospective Ubuntu developer.

Therefore, the SRU team, when on shift and "wearing an SRU hat", takes a
narrow view of our role, focusing our limited resources on only
progressing processes limited by this privilege. It is our expectation
that Ubuntu developers at large drive the non-privileged tasks because
they scale better.

We expect all Ubuntu developers to be familiar with the SRU process as
documented here, should they need to interact with SRUs.

It is normal and expected for prospective developers to not yet be
familiar with SRU process. If prospective developers are preparing
uploads for SRU, then they will need a sponsor, for example through the
`patch pilot programme <https://discourse.ubuntu.com/t/ubuntu-patch-pilots/37705>`__.
We expect Ubuntu developers to ensure that any uploads that they sponsor
meet our expectations. As above, since SRU team members focus on
operations limited by privilege during their shifts, prospective
developers who need help should seek that help from their sponsors, and
not from the SRU team directly. To find a sponsor, try the
`patch pilot programme <https://discourse.ubuntu.com/t/ubuntu-patch-pilots/37705>`__.

If review iterations are required, then prospective developers are
welcome to help. However, we expect this to be supervised by sponsors
and for them to intervene if required.

We therefore arrive at a set of distinct roles. Note that the person who
takes on each role can change over time, even for an individual SRU.

+-----------------------+-----------------------+-----------------------+
| Role                  | Responsibility        | Who can do it         |
+=======================+=======================+=======================+
| SRU Driver            | Manage and triage     | Anyone who            |
|                       | bugs, follow the SRU  | understands the       |
|                       | process and perform   | packaging changes     |
|                       | the necessary         | necessary to land a   |
|                       | development and QA    | particular fix into a |
|                       | tasks to see fixes    | stable release of     |
|                       | land.                 | Ubuntu and is willing |
|                       |                       | to do that work. If   |
|                       |                       | this person does not  |
|                       |                       | have upload access to |
|                       |                       | Ubuntu, then they can |
|                       |                       | still take this role, |
|                       |                       | under the supervision |
|                       |                       | of a sponsor          |
|                       |                       | (sponsors can be      |
|                       |                       | found via the `patch  |
|                       |                       | pilot                 |
|                       |                       | programme             |
|                       |                       | <https://discourse.ub |
|                       |                       | untu.com/t/ubuntu-pat |
|                       |                       | ch-pilots/37705>`__). |
+-----------------------+-----------------------+-----------------------+
| Sponsor               | Help the SRU Driver   | Someone familiar with |
|                       | with the required     | SRU process who has   |
|                       | process.              | upload access to the  |
|                       |                       | Ubuntu package        |
|                       |                       | archive.              |
+-----------------------+-----------------------+-----------------------+
| SRU Reviewer          | Review and negotiate  | SRU team members      |
|                       | proposed uploads for  | only.                 |
|                       | compliance with `SRU  |                       |
|                       | criteria <#what-is-a  |                       |
|                       | cceptable-to-sru>`__, |                       |
|                       | agree the QA plan,    |                       |
|                       | accept uploads into   |                       |
|                       | -proposed, confirm    |                       |
|                       | the agreed plan was   |                       |
|                       | followed, and release |                       |
|                       | -proposed packages    |                       |
|                       | into -updates.        |                       |
+-----------------------+-----------------------+-----------------------+
| SRU Process Developer | Drive process         | Anyone, under the     |
|                       | changes,              | leadership of the SRU |
|                       | documentation, etc.   | team.                 |
+-----------------------+-----------------------+-----------------------+
| Overriding authority  | Agree exceptions to   | Technical Board       |
|                       | the `SRU              | members only.         |
|                       | criteria <#what-is-a  |                       |
|                       | cceptable-to-sru>`__. |                       |
+-----------------------+-----------------------+-----------------------+

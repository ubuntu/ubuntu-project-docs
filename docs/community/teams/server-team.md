(server-team)=
# Server team

The Ubuntu Server team works to enable and promote the use of Ubuntu Server, the number one cloud OS.

The team focuses on three key areas:

1. Providing a robust and stable infrastructure for scale-out computing deployments
2. Supporting the latest scale-out computing workloads and architectures
3. Providing the right tools for orchestrating services within a scale-out computing environment


## Communication

**Mailing list**
: [ubuntu-server](https://lists.ubuntu.com/mailman/listinfo/ubuntu-server) ([archives](https://lists.ubuntu.com/archives/ubuntu-server/))

**IRC**
: `#ubuntu-server` on [Libera.Chat](https://libera.chat/), where the team offers support for server-related questions

**Launchpad**
: [~ubuntu-server](https://launchpad.net/~ubuntu-server)


## Meetings

No regular public meeting is currently advertised.
Periodic calls for input happen on the ubuntu-server mailing list.


## Authority

The Server team looks after the packages and features that make up Ubuntu Server.
The [list of packages](https://bugs.launchpad.net/~ubuntu-server/+packagebugs) the team maintains is tracked through the ~ubuntu-server team on Launchpad.


## Contributing

There are many areas where you can help the Ubuntu Server team:

**Help on the mailing list and IRC**
: Lend a hand with people's questions and problems on the ubuntu-server mailing list and the `#ubuntu-server` IRC channel. Ask and answer questions, provide suggestions, and provide input in the team's periodic calls for input.

**Test, test, test**
: If you have server-type hardware, or can spin up virtual machines and containers, you can make sure that Ubuntu is supported and works well on it. You can also test software and features worked on by the team.

**Improve documentation**
: Help keep server-related documentation up to date, or help with the [Ubuntu Server documentation](https://documentation.ubuntu.com/server/).

**Verify SRUs**
: Whenever a bug is fixed in a stable release, someone other than the developer who made the fix needs to verify that the package fixes the bug without causing regressions. See {ref}`stable-release-updates` for how stable release updates work.

**Triage bugs**
: Help move server bugs from a new, unconfirmed state to a confirmed (or invalid) state. You can view the [list of bugs related to the Server team](https://bugs.launchpad.net/~ubuntu-server/) and subscribe to the [ubuntu-server-bugs mailing list](https://lists.ubuntu.com/mailman/listinfo/ubuntu-server-bugs), where all the bugs are sent. For details of the triage process, see the [Ubuntu maintainers handbook](https://github.com/canonical/ubuntu-maintainers-handbook/blob/main/BugTriage.md).

**Improve packages**
: Look through the [list of packages](https://bugs.launchpad.net/~ubuntu-server/+packagebugs) looked after by the team to see if any need packaging work. This is an excellent way to gain experience on the path to becoming an Ubuntu developer (see {ref}`sponsorship`).


## Additional information

### Ubuntu Server bug triage

The goal of bug triage is to successfully review every bug filed against Ubuntu Server related packages.
A review involves analyzing a bug to determine whether it is valid and whether sufficient information was provided.
If the bug is both valid and sufficiently detailed, it is marked as triaged and will be worked to closure by a member of the Server team.
Otherwise, the bug is responded to and marked as incomplete (more details needed), invalid (not a real bug), or won't fix.

### Ubuntu Server packaging

The team uses a {spellexception}`git`-based workflow for handling package changes, which allows the use of Launchpad merge proposals and reviews before publishing a new package version.
For details, see the [merge proposals](https://github.com/canonical/ubuntu-maintainers-handbook/blob/main/MergeProposal.md) and [package merges](https://github.com/canonical/ubuntu-maintainers-handbook/blob/main/PackageMerging.md) documentation in the Ubuntu maintainers handbook.

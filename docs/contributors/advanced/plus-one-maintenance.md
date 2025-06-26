(plus-one-maintenance)=
# +1 Maintenance

The +1 maintenance is originally a Canonical program to improve the general
health of the Ubuntu archive, and more specifically its devel series — the next
version, `$current+1`. This document is written with that framework in mind,
and some parts of it might not apply to community members wanting to take part
in the effort.

The program consists of Canonical engineers from various teams taking up shifts
to work on the archive. While their regular duties might entail looking after a
specific set of packages, during their shift they should instead be looking
after the archive as a whole. This *can* include their regular package set,
e.g. if it involved in a massive transition.

## Contact

Most of the day-to-day communication around +1 should take place on the public
[Ubuntu Development](https://matrix.to/#/#devel:ubuntu.com) channel on Matrix.

The [Debcrafters](https://launchpad.net/~debcrafters-packages) team, and [Simon Chopin ](https://launchpad.net/~schopin) in particular, is responsible for
coordinating the effort.

## Who can participate?

We expect participants to be proficient in "distro work". Core Developers and
MOTUs would of course qualify, but people working on their application for such
a status are welcome. For the latter category, +1 shifts are a good way to get
more exposure to some specific situations such as transitions, proposed
migration, or merges, although participants are expected to already understand
those notions and have at least *some* experience with them.

While some Canonical teams are committed to having people on +1 duty on a regular basis, others can
pick up the occasional shift, in accordance with their managers.

It is possible, and encouraged, to shadow someone experienced on their shift before signing
up for one.

## Shift duration

Most regular contributors pick up shifts for an entire work week. This allows
them to take the time to dig deeply into thorny issues that would be difficult
to tackle on one's free time — and makes for less administrative overhead.
Furthermore many of the cases eventually need a build, or a combined proposed
migration which you'd want to track and follow up on for a few days.

However, it is perfectly fine to pick up shifts for a shorter duration.

## The work

### Shift report

Regardless of the exact work, it is advised to keep track of what has been
accomplished during a shift. This will serve as the basis for a +1 maintenance
report to be posted to the [dedicated Discourse
category](https://discourse.ubuntu.com/c/pre-release-discussion/plusone-maintenance/415)
at the end of shift.

The report has two main purposes. The first is to act as a hand-off document to
the next shift, outlining work items that need following up on. Those could be
fixes needing sponsorship, unfinished investigations, upcoming transitions from
Debian, etc.

The second purpose of the document is to document your contributions for others
to see what it is we actually do. This typically comes in the form of a list of
bugs, along with a description of the actions taken there.

To aid with the composition of the report, you can use our {ref}`template
<plus-one-report-template>`.

### Coordinating the effort

There are plenty of people working on Ubuntu, and there even can be multiple
people on +1 at the same time. To avoid stepping on each other's toes,
communication is crucial.

When working on a package, contributors should first check Launchpad for a
relevant open bug, and if it has been assigned to someone. If not, they should
open the bug if needed, and assign it to themselves. You should liberally
document your progress on the bug itself.

To give the bug some visibility, and since it is expected that most issues
being worked on affect a package in -proposed, you should apply the
`update-excuse` tag for the bug to show up on the excuses page. The tool
`pm-helper` (provided by `ubuntu-dev-tools`) can be used for the creation of
such bugs.

### Finding work

As mentioned, the focus is the `devel` series. Depending on when the shift
takes place in the cycle, the tasks can vary. The first thing to check for
should be the previous shift report for actionable items — see below.

One can also ask on Matrix if there are transitions that people might need help
for, e.g. a new version of Python.

Failing that, there are a few places that one might want to look at to find
work. They are loosely listed in order of priority, but that importance varies
depending on the development cycle.

It is of course reasonable for individual contributors to skew their workload
towards their own affinities, e.g. a RISC-V specialist might want to look a bit
more closely to issues only showing up on riscv64.

#### Transition tracker, NBS

The [NBS tracker](https://ubuntu-archive-team.ubuntu.com/nbs.html), for "Not
Buildable from Sources", tracks binary packages in the archive that cannot be rebuilt from source.
While that can happen for several reasons, by far the most common is that the binary
in question is the old version of a library that is having an ABI transition.

A more specialized view for transitions is the [transition
tracker](https://ubuntu-archive-team.ubuntu.com/transitions/) but it might not
track all ongoing transitions since it requires manual intervention to setup a
new tracker.

#### FTBFS

The priority of these rises along with the cycle. We want as few packages
failing to build at release time as possible, as it makes security updates of
these packages that much harder. An interesting aspect of these is that they
are usually isolated and can be worked on without interfering much with other
contributors.

Good sources for these are test rebuild results, periodically posted to [the
ubuntu-devel list](https://lists.ubuntu.com/archives/ubuntu-devel/), as well as
the [build status report](http://qa.ubuntuwire.com/ftbfs/).

#### update-excuses

A lot of the issues that can be found by the tools above is also visible in the
[update-excuses
page](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_excuses.html),
along with a lot of other problems, except that it's fairly impenetrable.

One possible approach is to start at the bottom and work your way up. For very
old issues, asking for a package removal on the grounds that it
wastes everyone's time is valid!

Another approach is to use
[visual-excuses](https://github.com/mclemenceau/visual-excuses) or [ubuntu-excuses](https://github.com/mclemenceau/ubuntu-excuses) to try (which are also available as snaps) and find
high-impact issues that would unblock large sets of packages.

#### Universe merges

While it is typically the responsibility of the last person that meaningfully
touched a package to merge changes from Debian — aka TIL, at archive
opening and before Feature Freeze, whoever is on +1 can help with them, e.g. if
the TIL is not around.

The obvious resource for this is [Merge-o-matic](https://merges.ubuntu.com/universe.html).

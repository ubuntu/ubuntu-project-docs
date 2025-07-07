(transitions-process)=

# Library Transitions

A library transition is the process that happens when a library gets updated to a new
version that includes API/ABI changes and requires rebuilding and re-testing all
the reverse dependencies. A library transition can be more or less complex depending
on the API/ABI breaking change and the number of reverse dependencies, especially
when some of them fail to build with the new package version.

Very complex transitions require a concerted, organized effort, and that's what we'll
primarily focus on in this document. Simpler transitions often go through automatically,
or sometimes with a bit of manual assistance.

To keep track of all recent, planned or ongoing transitions, there is the Launchpad project
[Ubuntu Transition Tracker](https://launchpad.net/ubuntu-transition-trackeer) managed
by the [Ubuntu Transition Trackers](https://launchpad.net/ubuntu-transition-tracker) team.

There is a page [NBS](https://ubuntu-archive-team.ubuntu.com/nbs.html) that lists all binary
packages in the archive (and its reverse dependencies) that are not built from any source
package. These packages existence in the list might result from an ongoing transition.

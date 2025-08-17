---
orphan: true
---

(issues-preventing-migration)=
# Issues preventing migration

Packages can fail to migrate for a vast number of different reasons. Sometimes
the clues listed under the 'Issues preventing migration:" line item on the
'update_excuses' page will be enough to indicate the next action needed; that
will be the focus of this section. In other cases, the autopkgtest log file will
need to be analyzed.


:::{admonition} **Proposed migration** series
The {ref}`proposed-migration` article series explains the various migration failures and ways of investigating them.

Process overview:
: {ref}`proposed-migration`

Practical guidance:
: {ref}`resolve-a-migration-issue`

Issue types:
:   * {ref}`failure-to-build-from-source-ftbfs`
    * {ref}`autopkgtest-regressions`
    * {ref}`issues-preventing-migration` (this article)
    * {ref}`special-migration-cases`
:::


(main-universe-binary-mismatch)=
## `main`/`universe` binary mismatch

A given source package may have some binaries in `main` and others in `universe`,
but this can get mixed up for various reasons. This genre of issues, known as
["component mismatches"](https://ubuntu-archive-team.ubuntu.com/component-mismatches.txt)
is spotted from migration excuses like:

```none
"php8.1-dba/amd64 in main cannot depend on libqdbm14 in universe"
```

Check the prior release to see if `php8.1-dba` and `libqdbm14` were both in
`main`, or both in `universe`. If both were in `universe` before, then most likely the
package in `main` needs to be demoted to `universe`. Ask an Archive Admin to do
this, and/or file a bug report (for an example, see
[LP: #1962491](https://bugs.launchpad.net/ubuntu/+source/php8.1/+bug/1962491)).

Conversely, if the dependency in `universe` actually needs to be in `main`, for
example a newly introduced binary package, then a 'Main Inclusion Request' (MIR)
bug report will need to be filed. See {ref}`main-inclusion-review` for details
on this procedure.

If both packages were previously in `main`, then some additional investigation
should be done to see why the `universe` package was moved out of `main`. The
resolution may be to move one or the other package so they're both in the same
pocket, or find a way to remove the dependency between them.

One very special case of these is unintended dependencies due to extra-includes.
Be aware that while most dependencies seem obvious (seeds --> packages -->
packages) there is an aspect of
[germinate](https://ubuntu-archive-team.ubuntu.com/germinate-output/ubuntu.jammy/all)
which will
[automatically include](https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/ubuntu/tree/supported#n124)
all `-dbg`, `-dev`, `-doc*` packages in a source archive that is in main. In
germinate these will appear as `Rescued from <src>`. If a merge is affected,
the solution without adding delta usually is to add an `Extra-exclude` like in
this [example with `net-snmp`](https://code.launchpad.net/~sergiodj/ubuntu-seeds/+git/ubuntu/+merge/414063).

For more information on component mismatches, from an Archive Administration
perspective, see {ref}`aa-package-overrides`.


(impossible-depends)=
## Impossible depends

An excuse like this:

```none
"Impossible Depends: aaa -> bbb/x/<arch>"
```

means package `aaa` has a dependency on package `bbb`, version `x`, for
architecture `<arch>`, but it is not possible to satisfy this.

One reason this can occur is if the package `bbb` is in `universe` whereas `aaa`
is in `main`. It may be that some of package `aaa`'s binaries need to be moved
to `universe`. See {ref}`main-universe-binary-mismatch` for directions.


(migrating-makes-something-uninstallable)=
## Migrating makes something uninstallable

A migration excuse in this format:

```none
"migrating [aaa]/[aaa-new-version]/[arch] to testing makes [bbb]/[bbb-version]/[arch] uninstallable"
```

means that package `bbb` has a versioned build dependency against the old
version of package `aaa`. A no-change rebuild can be used in these cases to
force a rebuild.


## Depends: `aaa [bbb]` (not considered)

Package `aaa` is blocked because it depends on `bbb`, however `bbb` is either
invalid or rejected.

If the dependency itself is not valid, this line will be followed by an
'Invalidated by dependency' line. In this case, look at the situation with
package `bbb` and resolve that first, in order to move package `aaa` forward.

If there is no 'Invalidated by dependency' line, then the dependency may be
rejected. There are three reasons why a rejection can occur:

1. it needs approval, 
2. cannot determine if permanent, or
3. permanent rejection.


## Implicit dependency: `aaa [bbb]`

An implicit dependency is a pseudo dependency where Breaks/Conflicts creates an
inverted dependency. For example, `pkg-b` Depends on `pkg-a`, but `pkg-a=2.0-1`
breaks `pkg-b=1.0-1`, so `pkg-b=2.0-1` must migrate first (or they must migrate
together). A way to handle this is to re-run `pkg-b`'s autopkgtest (for 2.0-1)
and include a trigger for `pkg-a=2.0`. For example, run:

```none
$ excuses-kicker -t pkg-a pkg-b
```

This can also occur if `pkg-b` has "Depends: pkg-a (<< 2.0)", due to the use of
some non-stable internal interface.

It can also occur if `pkg-a` has a Provides that changes from 1.0-1 to 2.0-1,
but `pkg-b` has a Depends on the earlier version.


## Implicit dependency: `aaa [bbb]` (not considered)

Similar to above, `aaa` and `bbb` are intertwined, but `bbb` is also either
invalid or rejected. For these cases, attention should first be paid to
resolving the issue(s) for `bbb`, and then re-running the autopkgtest for it
with a trigger included against package `aaa`.


## Has no binaries on arch `<arch>`

Usually this means the package has either failed to build or failed to upload
the binaries for a build. Refer to the
{ref}`failed to build from source <failure-to-build-from-source-ftbfs>` section for
tips on how to handle this class of problem.


## Has no binaries on any arch (`- to x.y.z`)

If the package doesn't have a current version, this error can indicate the
package is not (yet) in the Archive, or it can mean its binaries were removed
previously but not sync-blocklisted and thus reappeared.

If the package should not be synced into the Archive, on `#ubuntu-release` ping
`ubuntu-archive` with a request to remove the packages' binaries and add them to
[sync-blocklist.txt](https://ubuntu-archive-team.ubuntu.com/sync-blocklist.txt).

Otherwise, there are several things worth checking. Note that these links are
for Jammy; modify them for the current development release:

- [Stuck in New queue](https://launchpad.net/ubuntu/jammy/+queue?queue_state=0)
- [Stuck in Unapproved queue](https://launchpad.net/ubuntu/jammy/+queue?queue_state=1)


## No reason - still stuck?

If the package, as shown in
[excuses](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_excuses.html),
looks good but is not migrating, it might mean an installability conflict.
So, do not be confused by the status "Will attempt migration (Any information
below is purely informational)" - there are more checks happening afterwards.
This is checked and reported in
[update output.txt](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_output.txt)

Here is an example of `exim4` meeting this situation:

```none
trying: exim4
skipped: exim4 (4, 0, 137)
    got: 11+0: a-0:a-0:a-0:i-2:p-1:r-7:s-1
    * riscv64: sa-exim
```

That output is hard to read
([as explained here](https://wiki.ubuntu.com/ProposedMigration#The_update_output.txt_file_is_completely_unreadable.21)),
but in this example it means that a few packages on those architectures became
uninstallable.

You can usually reproduce that in a `-proposed`-enabled container and in this
example we see:

```none
root@k:~# apt install exim4 sa-exim
...
The following packages have unmet dependencies:
 sa-exim : Depends: exim4-localscanapi-4.1
```

Now we know that, let us compare the old and new `exim4`, which has:

```none
root@k:~# apt-cache show exim4-daemon-light | grep -e scanapi -e '^Versi'
Version: 4.96-3ubuntu1
Provides: exim4-localscanapi-6.0, mail-transport-agent
Version: 4.95-4ubuntu3
Provides: exim4-localscanapi-4.1, mail-transport-agent
```

So our example needs (as is most often the solution in these cases) a no-change
rebuild to pick up the new dependency. After a test build to be sure it works,
you can often upload and resolve this situation.

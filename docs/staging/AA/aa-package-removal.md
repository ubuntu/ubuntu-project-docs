(aa-package-removal)=
# Package removal


The `ubuntu-archive` team handles removals of both source and binary packages.
See the [work list of source package removals requested by developers](https://bugs.launchpad.net/ubuntu/+bugs?field.subscriber=ubuntu-archive&field.status=NEW&field.status=Confirmed&field.status=Triaged&field.status=INPROGRESS&field.status=FIXCOMMITTED&field.status=INCOMPLETE_WITH_RESPONSE&orderby=-id&start=0).
Binary package removals generally do not require a bug report; for source
packages I require either a Launchpad or Debian bug # to reference in the
removal, because from time to time users will find the publishing
history and complain to the Archive Admin who did the removal, so it's useful
to be able to redirect them.


## Source package removals via Debian

If a source package has been removed from Debian, then there is no need for
someone to file a separate removal bug because these can be handled through
`process-removals`. Whenever I get a ping about removing a package from the
devel series and they say as justification that it's been removed from
`unstable`, I handle the request by firing up `process-removals` and deal that
way with the entire pending queue.

When processing removals of packages that have been removed from Debian, it is
important not to break consistency of the Archive when they still have
`reverse-depends`, but it is also important to not let these packages linger
forever. When there are reverse-dependencies, particularly Ubuntu-specific ones,
I make a point to file bug reports to give Ubuntu developers time to respond;
see below.

Recommends should not block removals of packages. Seed references should be
referred to the maintainers of the relevant flavor before removal.


## Other source removals of packages from Debian

If we are removing a package from Ubuntu that is still in Debian `unstable`,
some sort of justification for the removal is needed. A non-comprehensive list
of sufficient justifications:

* The package {term}`FTBFS` and is blocking some transitions (either in
  [`proposed-migration`](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_excuses.html)
  or in [NBS removal](https://ubuntu-archive-team.ubuntu.com/nbs.html)).

* The package FTBFS or fails autopkgtests and has been removed from Debian
  `testing`.

* Upstream has fast-moving development and it does not make sense to ship the
  package in a stable Ubuntu release.

  * If not removing, but keeping it in the Archive -- then the driving team
    should ensure they can maintain it despite changing so fast. For example,
    an agreed SRU exception.

* The Security Team has flagged the package as unsupportable. In some cases I
  have asked the Security Team to also raise bugs on these packages in Debian
  as well before removing.

There is a `demote-to-proposed` command which can be used to move a package to
`devel-proposed` instead of removing it entirely. I **NEVER** use this command,
except if the package has an Ubuntu delta that is important to preserve in the
event that a fix becomes available in Debian. Otherwise, if a package is buggy
enough to be removed from the `-release` pocket, it is better to remove it
entirely and wait for Debian to fix it rather than land it in `-proposed` where
it takes attention of our {ref}`+1 maintenance <plus-one-maintenance>` folks
and the Release Team.
Not removing it would continue to potentially contaminate `-proposed` and on
the other hand we have plenty of ways nowadays to get access to the former
delta again.

In some cases, a package must be removed not because it is buggy but because it
depends on another package which is buggy. These removals should be tracked in
the `extra-removals.txt` file within the
[`sync-blocklist` repository](https://code.launchpad.net/~ubuntu-archive/+git/sync-blocklist).


## Source removals of Ubuntu-specific packages

During the heyday of {term}`MOTU`, Ubuntu acquired many Ubuntu-specific
packages that were uploaded by an Ubuntu developer who is no longer active. Over
time, many of these packages have bit-rotted; in particular, by not having their
packaging updated to make sure they continue to be buildable, or not being
ported to newer versions of library dependencies. We are generally content to
let these packages drift until they become blockers, either by Failing to Build
from Source and blocking transitions, or depending on packages that have been
removed from Debian.

Before removing an Ubuntu-specific package, even if it is "obviously" abandoned,
I always file a bug report against the package with the rationale, and where
there is an obvious historic "owner" of the package I will subscribe them to
the bug if they don't already have a bug subscription to the package (they
usually don't) and give them time to remedy the situation if they still care
about the package.

Such bugs should be given a deadline of the end of the current release cycle,
to ensure {term}`NBS` gets cleaned up before a stable release.


## Source removals of SRU upload from `-proposed`

The [SRU Pending Report](https://ubuntu-archive-team.ubuntu.com/pending-sru.html)
has a section at the bottom suggesting removals from `-proposed` for several
different reasons.


### **`-updates` is equal or higher than `-proposed`**

This is the normal sequence of events. An SRU is verified, released, and the
package has to also be removed from `-proposed`. The suggested command-line in
the report is correct, and can be run.

When can it be run? Only when everything has been published, i.e., avoid the
{term}`LP` publishing lag. Rule of thumb: give it a few days.

Example:

```bash
remove-package -y -m "moved to -updates" -s noble-proposed -e \
 4.18.4-1ubuntu0.1 xfce4-panel
```


### **`-release` is equal or higher than `-proposed`**

Haven't seen this case before. I suspect it can happen at release opening. To
be determined.


### **Failed verification for more than 10 days**

If an SRU has the `verification-failed` tag, it is expected to be corrected
within 10 days, either by a new upload, or something else that fixes the
problem.

If that does not happen, the package is eligible for removal from `-proposed`.
The `sru-remove` package, when given the "failed" reason, will automatically
add a comment to the LP bug with the reason for removal, and mention this "10
days" period.

Example:

```bash
sru-remove --reason=failed -s oracular -p samba 2092308
```


### **No test plan verification done in more then 105 days**

If an upload has been sitting in `-proposed` and not verified for 105 days or
more, it's also eligible for removal. That is the '`--reason=ancient`' parameter
(which is the assumed default if not given), and it will also add the
appropriate explanation to the bug behind the SRU.

Example:

```bash
sru-remove -s focal -p libxmlb 1988440
```


## Removals of binary packages

When a binary package ceases to be built by its source package, it must be
manually removed by an Archive Admin. These to-be-removed packages show up in
several places.

* If `proposed-migration` can work out how to move the new source package to
  the `-release` pocket without making any binary packages uninstallable, then
  they show up on the [NBS removal](https://ubuntu-archive-team.ubuntu.com/nbs.html)
  list. This is the easiest case, as the top of the page gives a command that
  can be used to remove all binaries that are safe to remove (no remaining
  reverse-dependencies).

* If the NBS package is in the `-proposed` pocket, it will be reported on
  [`update_excuses`](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_excuses.html)
  as `old binaries`. These are unfortunately not reported in their own report,
  but have to be found when someone happens to look at the corresponding
  `update_excuses` entry.

* If the packages are {term}`NBS` because support for a given architecture has
  been dropped entirely by the source package, these instead appear in
  `update_excuses` as a `missing build`. These require additional discernment
  before removal, since a missing build could also mean the package is supposed
  to be built on the architecture but failed to do so (or is still building).

* In some cases a binary may be dropped on a particular architecture, but the
  package manages to migrate from `-proposed` to the `-release` pocket anyway.
  In this case, they don't show up on the NBS list because that binary package
  is **not** NBS on all architectures. Instead you have to check the
  [uninstallable report](https://ubuntu-archive-team.ubuntu.com/proposed-migration/noble_uninst.txt)
  and [out-of-date package report](https://ubuntu-archive-team.ubuntu.com/proposed-migration/noble_outdate.txt)
  for the corresponding series. 


(revert-a-package-to-a-previous-version)=
## Revert a package to a previous version

A special case of package removals is where we want to remove a package and
replace it with a previous version. This most commonly occurs in the development
series.

For example, if a transition is almost complete we may receive a request to
revert a new upload that accidentally entangles the transition. To do this, we
need to remove the existing package with `remove-package`, then copy the
previous package forwards with:

```bash
copy-package --force-same-destination --auto-approve --version=$VERSION_TO_RESTORE --include-binaries --from-suite=$SUITE --to-suite=$SUITE $PKG
```


## Checking dependencies before removal

You usually want to check to avoid causing:

* Installation issues by something having a dependency on the produced
  binaries.

* Fail to build due to missing dependencies, for a package that builds depends
  on a produced binary.

There are many ways to check for reverse dependencies, with different pros and
cons. The following list gets gradually more complete, but also takes longer
and is sometimes harder to set up.


### **`reverse-depends`**

The most common and most widely used tool, even fine for normal cases is
`reverse-depends` from the package `ubuntu-dev-tools`. Quick and helpful, but
not always fully complete.


### **`apt-cache rdepends`**

The other two tools check the current state of a release. To instead inspect a
particular system configuration one would tend to use `apt-cache rdepends`
instead.


### **`checkrdepends`**

We've had cases where the other tools struggled to follow virtual dependencies
or the rust ecosystem's use of `provides` in build dependencies. So far
`checkrdepends` from `ubuntu-archive-tools` seems to cover this the best.

We recommend at least:

* Using `archive-base` to not require a local mirror.

* Using `--include-provides` to also check if we might make things un-buildable.

Example:

```bash
./checkrdepends --no-ports --include-provides --suite plucky --archive-base 'http://archive.ubuntu.com/ubuntu' debian-pan debian-astro
```


## Checking removal reasons in publication history 

Sometimes one might want to double check if something was removed and
asynchronous tools like `rmadison` will not immediately update as they need a
publishing run and then some processing. Instead one could check such via
launchpad API or the web.

Commonly known is the source publishing history, which is also linked from the
package. For example in
[publishing history](https://launchpad.net/ubuntu/+source/libsdl2/+publishinghistory)
you can see automatic and manual removals, but also the effects of a package
going through `-proposed` migration.

Less known is that there also is a binary package publishing history, which you
might want to check if e.g. removing a binary for a single architecture. For
example [in this case](https://bugs.launchpad.net/ubuntu/+source/pdfsandwich/+bug/2092549/comments/5)
which can be seen in effect on
[`https://launchpad.net/ubuntu/plucky/armhf/pdfsandwich`](https://launchpad.net/ubuntu/plucky/armhf/pdfsandwich).




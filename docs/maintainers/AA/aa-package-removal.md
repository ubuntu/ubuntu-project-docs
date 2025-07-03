(aa-package-removal)=
# Remove a package

The {ref}`Archive Admin <archive-administration>` team handles removals of both
source and binary packages.

As per the corresponding contributor guide {ref}`request-package-removal`, 
requests to remove a package are submitted in the form of bugs on Launchpad.

* [List of source package removal requests](https://bugs.launchpad.net/ubuntu/+bugs?field.subscriber=ubuntu-archive&field.status=NEW&field.status=Confirmed&field.status=Triaged&field.status=INPROGRESS&field.status=FIXCOMMITTED&field.status=INCOMPLETE_WITH_RESPONSE&orderby=-id&start=0)

You may need to remove a package completely, or only remove either a source or
a binary.

Source removals shall always have a bug associated. Binary package removals do
not strictly require a bug report, but they are the way to contact the Archive
Administrators therefore likely one exists.

Either way, if a bug exists it shall be referenced in the removal comment,
which helps a lot for users
{ref}`tracking it down in the publishing history <checking-removal-reasons>` which
will point them to the related discussion and action.


## Why to remove packages


(justification-for-removal)=
### Justification for removal

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


### Removals of binary packages

When a binary package ceases to be built by its source package, it must be
manually removed by an Archive Admin. These to-be-removed packages show up in
several places.

* If `proposed-migration` can work out how to move the new source package to
  the `-release` pocket without making any binary packages uninstallable, then
  they show up on the [NBS removal](https://ubuntu-archive-team.ubuntu.com/nbs.html)
  list. This is the easiest case, as the top of the page gives a command that
  can be used to remove all binaries that are safe to remove (no remaining
  {ref}`reverse-dependencies <check-reverse-dependencies>`).

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


(aa-nbs-removals)=
### NBS-related removals

Sometimes binary packages are Not Built by any Source (NBS) any more. This
usually happens with library SONAME changes, package renames, etc. Those need
to be removed from the archive from time to time, and right before a release,
to ensure that the entire archive can be rebuilt by current sources.

Such packages are detected by `archive-cruft-check`. This tool does not check
for {ref}`reverse dependencies <check-reverse-dependencies>`, though, so you
should use `checkrdepends -b` for checking if it is safe to actually remove NBS
packages from the archive.

Look at the
[half-hourly generated NBS report](https://ubuntu-archive-team.ubuntu.com/nbs.html)
which shows all NBS packages, their reverse dependencies, and a
copy-and-paste-able command to clean up the "safe" ones.

The rest needs to be taken care of by developers, by doing transition uploads
for library SONAME changes, updating build dependencies, etc. The remaining
files will list all the packages that still need the package in question.

Don't remove NBS kernel packages for old {term}`ABIs <ABI>`
until `debian-installer` and the seeds have been updated, otherwise daily
builds of alternate and server CDs will be made uninstallable.


(source-package-removals-via-debian)=
### Source package removals via Debian

Source packages that have been removed from Debian do not need a removal request
bug. They can be periodically removed using the `process-removals` tool from
`ubuntu-archive-tools`:

```none
$ ./process-removals
```

This tool interactively processes the entire pending queue, and asks for
confirmation for each removal. You can run this tool whenever you receive a
request to remove a package from the devel series due to it being removed from
`unstable`.

It is important, when removing packages, not to break consistency of the Archive
when they still have `reverse-depends`. However, it is also important to not let
these packages linger forever. Therefore, when there are reverse-dependencies
(particularly Ubuntu-specific ones), **file a bug report** to give Ubuntu
developers time to respond.

*Recommends* should not block removals of packages.
Seed references should be referred to the maintainers of the relevant flavor before removal.

Some packages removed from Debian do need to be kept, e.g. `firefox`, since we
did not do the `firefox` -> `iceweasel` renaming.


### Source removals of Ubuntu-specific packages

During the heyday of {term}`MOTU`, Ubuntu acquired many Ubuntu-specific
packages that were uploaded by an Ubuntu developer who is no longer active. Over
time, many of these packages have bit-rotted; in particular, by not having their
packaging updated to make sure they continue to be buildable, or not being
ported to newer versions of library dependencies. We are generally content to
let these packages drift until they become blockers, either by Failing to Build
from Source and blocking transitions, or depending on packages that have been
removed from Debian.

Before removing an Ubuntu-specific package, even if it is "obviously" abandoned,
please file a bug report against the package with the rationale, and where
there is an obvious historic "owner" of the package subscribe them to
the bug if they don't already have a bug subscription to the package (they
usually don't) and give them time to remedy the situation if they still care
about the package.

Such bugs should be given a deadline of the end of the current release cycle,
to ensure {term}`NBS` gets cleaned up before a stable release.


(aa-remove-a-package)=
## How to remove a package

To remove a package entirely from the Archive, use the `remove-package`
client-side tool.


### Remove a source package

By default, this removes both the named source and any binaries:

```none
$ ./remove-package -m "LP: #12345 - reason for removal" konserve
```

The tool tells you what it’s going to do, and asks for confirmation before
doing it, so it’s reasonably safe to get the wrong options and say N.


### Remove only a binary package

To remove only a binary, use the `-b` flag with the `remove-package` tool. For
example:

```none
$ ./remove-package -m "LP: #12345 - reason for removal" -b konserve -a riscv64
```


### Alternative demote-to-proposed

There is a `demote-to-proposed` command which can be used to move a package to
`devel-proposed` instead of removing it entirely. We rarely use this command,
except if the package has an Ubuntu delta that is important to preserve in the
event that a fix becomes available in Debian. Otherwise, if a package is buggy
enough to be removed from the `-release` pocket, it is better to remove it
entirely and wait for Debian to fix it rather than land it in `-proposed` where
it takes attention of our {ref}`+1 maintenance <plus-one-maintenance>` folks
and the Release Team.
Not removing it would continue to potentially contaminate `-proposed` and on
the other hand we have plenty of ways nowadays to get access to the former
delta again.


### Source removals of SRU upload from `-proposed`

The [SRU Pending Report](https://ubuntu-archive-team.ubuntu.com/pending-sru.html)
has a section at the bottom suggesting removals from `-proposed` for several
different reasons.


#### `-updates` is equal or higher than `-proposed`

This is the normal sequence of events that lead to this situation: An SRU is
verified, released, and the package has to also be removed from `-proposed`.
The suggested command-line in the report is correct, and can be run.

When can it be run? Only when everything has been published, i.e., avoid the
Launchpad publishing lag. Rule of thumb: give it a few days.

Example:

```none
remove-package -y -m "moved to -updates" -s noble-proposed -e \
 4.18.4-1ubuntu0.1 xfce4-panel
```


#### `-release` is equal or higher than `-proposed`

Haven't seen this case before. I suspect it can happen at release opening. To
be determined.


#### Failed verification for more than 10 days

If an SRU has the `verification-failed` tag, it is expected to be corrected
within 10 days, either by a new upload, or something else that fixes the
problem.

If that does not happen, the package is eligible for removal from `-proposed`.
The `sru-remove` package, when given the "failed" reason, will automatically
add a comment to the LP bug with the reason for removal, and mention this "10
days" period.

Example:

```none
sru-remove --reason=failed -s oracular -p samba 2092308
```


#### No test plan verification done in more then 105 days

If an upload has been sitting in `-proposed` and not verified for 105 days or
more, it's also eligible for removal. That is the '`--reason=ancient`' parameter
(which is the assumed default if not given), and it will also add the
appropriate explanation to the bug behind the SRU.

Example:

```none
sru-remove --reason=ancient -s focal -p libxmlb 1988440
```


(revert-a-package-to-a-previous-version)=
### Revert a package to a previous version

A special case of package removals is where we want to remove a package and
replace it with a previous version. This most commonly occurs in the development
series.

For example, if a transition is almost complete we may receive a request to
revert a new upload that accidentally entangles the transition. To do this, we
need to remove the existing package with `remove-package`, then copy the
previous package forwards with:

```none
copy-package --force-same-destination --auto-approve --version=$VERSION_TO_RESTORE --include-binaries --from-suite=$SUITE --to-suite=$SUITE $PKG
```


## Related actions

```{note}
Add contextual text
```

### Tracking dependency removals

In some cases, a package must be removed not because it is buggy but because it
depends on another package which is buggy. These removals should be tracked in
the `extra-removals.txt` file within the
[`sync-blocklist` repository](https://code.launchpad.net/~ubuntu-archive/+git/sync-blocklist).


### Blocking a package from returning

If you remove source packages which are in Debian, and they are not meant to
ever come back, add it to the blocklist in
`lp:~ubuntu-archive/+git/sync-blocklist`, document the reason, and
`git commit` it with an appropriate changelog. This will avoid getting the
package back to source NEW in the next round of auto-syncs from Debian.




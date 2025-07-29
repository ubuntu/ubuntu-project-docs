(the-package-archive)=
# The Package Archive

```{note}
This content comes [from the wiki](https://wiki.ubuntu.com/UbuntuDevelopment/PackageArchive)
It has not yet been reviewed for currency or accuracy.

DUPLICATE: Mostly covered in {ref}`package-archive`
```

All current official Ubuntu packages are stored in the primary archive, which is
widely {ref}`mirrored <mirrors>`.
A search interface is available at [packages.ubuntu.com](https://packages.ubuntu.com).
Old versions can be retrieved from [Launchpad](https://launchpad.net/ubuntu).

It is administered by the [archive administration team](https://launchpad.net/~ubuntu-archive).

(Uploading)=
## Uploading

If you are not yet an official Ubuntu developer, you can arrange for your
package to be uploaded via the {ref}`sponsorship-process`.

Packages are [uploaded via FTP](ftp://upload.ubuntu.com/) using `dput` or `dupload`.

Notes for preparing your upload:

* Make source-only uploads, i.e. use "`dpkg-buildpackage -S`"
* If you need to include the {term}`orig tarball` as well, use parameters `-S -sa`

When your upload is processed (typically within a matter of minutes), you will
receive an email with the result of your upload, whether it succeeds or fails,
**unless** you use an unregistered email address. The system will only send mail
to an address which belongs to a launchpad account which is a member of the
relevant team for uploading. E.g. [`motu`](https://launchpad.net/~motu) for
universe and [`ubuntu-core-dev`](https://launchpad.net/~ubuntu-core-dev) for main.

Your upload must be signed by a GPG key registered in Launchpad. If the
signature cannot be traced to a member of the appropriate team, then the upload
will be **silently rejected**.

To add a new package to Ubuntu, simply upload it as usual. Any new packages
uploaded are [put in a queue](https://launchpad.net/ubuntu/questing/+queue) to
be checked by the administrators before being included.

[Ubuntu Development/Uploading](https://wiki.ubuntu.com/UbuntuDevelopment/Uploading)
has much more information about the topic.

(autobuilding-and-publishing)=
## Autobuilding and publishing

Once an upload has been accepted, it takes some time to be
[built](https://wiki.ubuntu.com/UbuntuDevelopment/PackageArchive#Autobuilders)
and published in the archive. For simple packages, this is usually on the order
of an hour, but varies depending on release activity (uploads may be temporarily
suspended), the time needed to build the package (including other packages in
the build queue), and other factors.

After a package has been built, the next publisher run that starts at 3 and 33
minutes past each hour will process it, usually finishing towards the end of
that half-hour; at the end of that process it will be visible in the public
archive.

(notification-of-changes)=
## Notification of changes

Notifications of uploads are sent to a mailing list.  A different list is used for each Ubuntu release:

* [8.04 (hardy)](https://lists.ubuntu.com/mailman/listinfo/hardy-changes/)
* [10.04 (lucid)](https://lists.ubuntu.com/mailman/listinfo/lucid-changes)
* [11.04 (natty)](https://lists.ubuntu.com/mailman/listinfo/natty-changes)
* [11.10 (oneiric)](https://lists.ubuntu.com/mailman/listinfo/oneiric-changes)
* [12.04 (precise)](https://lists.ubuntu.com/mailman/listinfo/precise-changes)
* [12.10 (quantal)](https://lists.ubuntu.com/mailman/listinfo/quantal-changes)

```{admonition} Question
:class: important
Do we, in principle, want to keep this list? If so, we should consider trying
to create it in a way that makes it better maintainable (otherwise it will get
this out of date again).
```

You can find changelogs for all packages at
http://changelogs.ubuntu.com/changelogs/ (this is the source used by
`update-manager` and Synaptic).

(syncing-and-merging)=
## Syncing and merging

(See the [Release Process / Merge Process rationale](https://wiki.ubuntu.com/UbuntuDevelopment/ReleaseProcess#MergeProcess_rationale)

Most packages in Ubuntu originate elsewhere, including Debian and related
package repositories.

A **sync** copies a source package verbatim from an external repository into
Ubuntu, overwriting any package of the same name. This is used when a newer
version of it is available, and should be included in Ubuntu, and happens
automatically during some phases of the release cycle. To request a sync,
follow the [Sync Request Process](https://wiki.ubuntu.com/SyncRequestProcess).

A **merge** is a three-way merge of a package which originated in an external
repository. This is used when there is a newer version available from the
external repository, but the package has also been modified (branched) in
Ubuntu. [Merge-o-Matic](https://merges.ubuntu.com) assists with this work, and
[the Merging page](https://wiki.ubuntu.com/UbuntuDevelopment/Merging) explains
how and when to merge. Packages which are
[maintained in Bazaar](https://wiki.ubuntu.com/UbuntuDevelopment/#Bazaar) can
and should be merged using Bazaar itself.

The "Last Uploader" column in the Merge-o-Matic output is the default assignee
for the merge, following the "touched-it-last" maintenance principle. However,
you can and often should grab other people's merges if they don't have time or
you feel you can do a better job. It's polite and often a good idea (though not
mandatory) to contact the other person first to make sure you aren't
duplicating work.

Backports work similarly to syncs, but have somewhat different requirements.
To request a backport, follow the
[Ubuntu Backports](https://wiki.ubuntu.com/UbuntuBackports) process.

(package-archive-consistency)=
## Consistency

The archive is periodically checked for various inconsistencies, such as
incorrect dependency relationships between packages.

* [Packages that are uninstallable](https://ubuntu-archive-team.ubuntu.com/proposed-migration/questing_uninst.txt)
  -- due to dependencies that cannot be satisfied.
* [Ubuntu Development/NBS](https://wiki.ubuntu.com/UbuntuDevelopment/NBS) -
  binary packages that are no longer built by any source package.
  These packages are not automatically removed from the archive, since
  generally they still have reverse dependencies (packages depending on them).

(package-archive-freezes)=
## Freezes

Freezes are restrictions on which changes can be uploaded in order to try and
stabilize Ubuntu for release. There are various different freezes that happen
at different times in the cycle, and they are of different types, affect
different packages, and have different procedures for uploading during them,
so understanding them all can be difficult.

You can see which freezes happen and when on the
[Release Schedule](https://wiki.ubuntu.com/ReleaseSchedule), and each is linked
to a page about that particular freeze, so that is a great place to go for the
information. This page will provide a bit more explanation about the types of
freezes and how to handle them.

Freezes are generally also announced on
[`ubuntu-devel-announce`](https://lists.ubuntu.com/mailman/listinfo/ubuntu-devel-announce), so
subscribing to that can keep you up-to-date. However, there aren't reminders
about upcoming freezes posted to that list, so keep on top of which freezes are
upcoming will help you to meet the deadlines in your work.

### Uploading restrictions

There are two ways that freezes are enforced, which are known as "soft" and
"hard" freezes. Knowing whether a particular freeze is soft or hard is
important, as it will allow you to know what effect uploading will have, and
who needs to be aware of changes that you make for them to be included.

#### Soft freezes

Soft freezes have no mechanism in the archive software to enforce them, they
just rely on each developer to ensure that they only upload appropriate changes.

For instance, [Feature Freeze](https://wiki.ubuntu.com/FeatureFreeze) is a soft
freeze, as you can still upload as before, you are just required to seek
exceptions for new features.

Most importantly, freezes for the alpha releases of Ubuntu are soft freezes.
This means that nothing will prevent your changes from entering the archive, so
you must ensure that they don't interfere with the process of releasing the
alpha. Convention for milestone stabilization is to upload to `-proposed`,
during this freeze interval. See the section on milestone freezes later for
more information on what this means.

#### Hard freezes

In contrast to soft freezes, hard freezes flick a switch in the archive
software such that all uploads are not immediately accepted, they instead end
up in the UNAPPROVED Queue. Packages remain in this queue until they are
explicitly accepted by an Archive Administrator.

This means that your changes can be reviewed before they are accepted, so that
extra review can be done, and it is not left to your discretion to enforce the
rules of the freeze.

While this could mean that you could upload with less care, it is not wise to,
as those who can review are generally very busy at this time already, and extra
work at these crucial periods is not appreciated. It is generally a good idea to
ensure that someone on the release team knows that you will be making an upload
to fix the particular issue before you do so (fixing a release critical bug is
generally permission enough).

(package-archive-components)=
## Managing components

Ubuntu packages are classified into components according to
[maintenance and licensing criteria](https://ubuntu.com/community),
a process which is described in {ref}`seed-management`.

Packages sometimes move from one component to another, according to policy or
licensing changes, as managed by the archive administrators. Special
consideration is necessary when packages move into `main` or `restricted`, as
this implies a commitment of ongoing maintenance. Such changes must follow the
[Main Inclusion Process](https://wiki.ubuntu.com/MainInclusionProcess).

(package-archive-autobuilders)=
## Autobuilders

Ubuntu source packages are automatically built for a variety of platforms by
Launchpad, which provides [build status information](https://launchpad.net/ubuntu/+builds).
Build log files are available from Launchpad as well, by
[searching for the package](https://launchpad.net/ubuntu/) and selecting a version.

Some supplementary information about the build infrastructure is available on
[Build Daemons](https://wiki.ubuntu.com/BuildDaemons).

(Removals)=
## Removing Packages

Packages which are removed from Debian are semi-automatically removed from
Ubuntu universe on a regular basis by the administrators. However, packages are
not removed from Ubuntu {term}`Main` without explicit request, nor are packages
which originated elsewhere. To request removal of such a package, file a bug
against the package.  

The bug must have the following elements:

* Which release to remove it from (e.g., `hardy`)

* Whether to remove both the source package and all binary packages

* A rationale for why they should be removed

* Confirmation that the binary packages have no `rdepends` (no other package
  depends on them)

  * There is `checkrdepends` in `ubuntu-archive-tools`, but it needs a mirror
    to work with.

  * There is `reverse-depends` and `reverse-depends -b` (build depends) in
    `ubuntu-dev-tools`, but it can return false positives for alternative
    dependencies.

If you are not an [Ubuntu Developer](https://wiki.ubuntu.com/UbuntuDevelopers)
use the following {ref}`sponsorship-process`. If you are an Ubuntu Developer,
then subscribe the `ubuntu-archive` team to the bugs. If you need help deciding
whether a package ought to be removed, please discuss on the `ubuntu-devel`
mailing list rather than asking the archive administrators.

Refer to `https://launchpad.net/ubuntu/+source/<source package>` for the reason
of the removal of a specific package.

(package-archive-architectures)=
## Architectures

Packages are typically built for each of several architectures. For example,
the `hello` package is built on {term}`i386`, {term}`amd64`, etc. These are
divided into categories according to their level of use and official support by
the project.

### Official architectures

These are officially supported and maintained by the Ubuntu project.
{term}`Canonical` provides server resources to build, store and distribute
packages and installation media for them, and the core development team is
responsible for their upkeep.

Build failures on these architectures are considered serious bugs. Each official
Ubuntu release and update includes appropriate support for these architectures.
There may or may not be a team which is specifically responsible for
architecture-specific issues. The kernel team builds and tests the Ubuntu
kernel on these architectures:

* `amd64`

* `armhf`

* `i386`

### Unofficial architectures

These are maintained on a best-effort basis by interested volunteers in the
Ubuntu community. Each architecture has a corresponding community team formed
of the developers who support it. {term}`Canonical` provides server resources
to build, store and distribute packages and installation media for ports,
however, the porting teams are responsible for their operation and maintenance,
including the kernel, toolchain and build infrastructure.

Build failures are not considered a serious issue by the core team. Ports may
issue new releases or updates out of sync with official Ubuntu releases.

* `arm64`

* `armel` (official from Ubuntu 9.10 to Ubuntu 11.10; [discontinued as of Ubuntu 13.04](https://lists.ubuntu.com/archives/ubuntu-devel/2012-November/036106.html))

* `hppa` ([HPPA Port Status](https://wiki.ubuntu.com/HPPAPortStatus), https://launchpad.net/~ubuntu-hppa)
  ([discontinued as of Ubuntu 9.10](https://lists.ubuntu.com/archives/ubuntu-devel-announce/2009-May/000571.html))

* `ia64` ([IA64 Port Status](https://wiki.ubuntu.com/IA64PortStatus), https://launchpad.net/~ubuntu-ia64)
  ([discontinued as of Ubuntu 10.10](https://lists.ubuntu.com/archives/technical-board/2010-August/000441.html))

* `lpia` ([discontinued as of Ubuntu 10.04](https://lists.ubuntu.com/archives/ubuntu-devel-announce/2009-November/000643.html))

* `powerpc` (https://launchpad.net/~ubuntu-powerpc)
  ([official up to Ubuntu 6.10](https://lists.ubuntu.com/archives/ubuntu-announce/2007-February/000098.html))

* `ppc64el`

* `sparc` ([official up to Ubuntu 7.10](https://lists.ubuntu.com/archives/ubuntu-devel-announce/2008-March/000400.html);
  [discontinued as of Ubuntu 10.10](https://lists.ubuntu.com/archives/technical-board/2010-August/000441.html))

### Primary architectures

These are provided on archive.ubuntu.com, and [are widely mirrored](https://launchpad.net/ubuntu/+archivemirrors).

* `amd64`

* `i386`

### Ports

These are provided only on `ports.ubuntu.com`, and are not generally available
on the mirror network. This decision is made on the basis of levels of use;
mirrors on the mirror network only have so much space available, and so we only
designate as primary those architectures which have very high download rates.

* `arm64` (from Ubuntu 13.10)

* `armel` (from Ubuntu 9.04; [discontinued as of Ubuntu 13.04](https://lists.ubuntu.com/archives/ubuntu-devel/2012-November/036106.html))

* `armhf` (from Ubuntu 12.04)

* `hppa` ([HPPA Port Status](https://wiki.ubuntu.com/HPPAPortStatus),
  https://launchpad.net/~ubuntu-hppa)
  ([discontinued as of Ubuntu 9.10](https://lists.ubuntu.com/archives/ubuntu-devel-announce/2009-May/000571.html))

* `ia64` ([IA64 Port Status](https://wiki.ubuntu.com/IA64PortStatus),
  https://launchpad.net/~ubuntu-ia64)
  ([discontinued as of Ubuntu 10.10](https://lists.ubuntu.com/archives/technical-board/2010-August/000441.html))

* `lpia` ([discontinued as of Ubuntu 10.04](https://lists.ubuntu.com/archives/ubuntu-devel-announce/2009-November/000643.html))

* `powerpc` (https://launchpad.net/~ubuntu-powerpc)

* `ppc64el` (from Ubuntu 14.04)

* `s390x` (from Ubuntu 16.04)

* `sparc` ([discontinued as of Ubuntu 10.10](https://lists.ubuntu.com/archives/technical-board/2010-August/000441.html))

The ports system [was announced here](https://lists.ubuntu.com/archives/ubuntu-announce/2005-October/000040.html)

### Summary as of Ubuntu 14.04

|         | Official    | Unofficial              |
| ------- | --------    | ----------              |
| Primary | amd64, i386 |                         |
| Ports   | armhf       | arm64, powerpc, ppc64el |

(package-archive-installation-media)=
## Installation media

Installation media (for CDs, DVDs, USB drives, etc.) are built from the package
archive, and published on different hosts as follows.

### `releases.ubuntu.com`

[releases.ubuntu.com](http://releases.ubuntu.com/) hosts the most frequently
downloaded images. It is [widely mirrored](https://launchpad.net/ubuntu/+cdmirrors).
All images here are officially supported by the Ubuntu project.

### `cdimage.ubuntu.com`

[`cdimage.ubuntu.com`](http://cdimage.ubuntu.com/) hosts less frequently
downloaded images. It is not widely mirrored due to its very large size. Some
images here are officially supported by the Ubuntu project and some are not; if
an image is on `cdimage.ubuntu.com`, it simply means that it won't fit on
`releases.ubuntu.com`. For example, Ubuntu DVD images are hosted on
`cdimage.ubuntu.com`.


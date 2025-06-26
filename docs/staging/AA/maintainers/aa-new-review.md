(aa-new-review)=
# NEW review

There are three main functions of a manual NEW process:

* Managing the package namespace

* Ensuring compliance with, and correct documentation of, the software license

* Ensuring the package is shipped in the correct component based on its license

New sources need to be checked to make sure they're well packaged, the licence
details are correct and permissible for us to redistribute, etc. See:

* [Packaging new software](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/1.0/how-to/packaging-new-software.html)

* {ref}`debian/copyright file <the-copyright-file>`

* and [Debian's Reject FAQ](https://ftp-master.debian.org/REJECT-FAQ.html)

## The NEW queue

To work with the upload queue, you may either use the
[web interface](https://launchpad.net/ubuntu/questing/+queue) or the `queue` API
client in `ubuntu-archive-tools`. The API client should generally be faster and
more flexible; in particular, it is not currently possible to override
individual binaries using the web interface. See
[bug #828649](https://bugs.launchpad.net/launchpad/+bug/828649).

Both source packages and new binaries which have not yet been approved are not
automatically accepted into the archive, but are instead held for checking and
manual acceptance. Once accepted they'll be automatically approved from then on.

The current queue can be obtained with:

```none
$ ./queue info
```

This is the `NEW` queue for the development series of Ubuntu by default; you
can change the queue with `-Q`, the distro with `-D` and the release using `-s`.
To list the `UNAPPROVED` queue for `ubuntu/xenial`, for example:

```none
$ ./queue -s xenial -Q unapproved info
```

Packages are placed in the `UNAPPROVED` queue if they're uploaded to a closed
distribution, and are usually security updates or similar; this should be
checked with the uploader.

You can give a string argument after `info`, which is interpreted as a sub-string
match filter.

To obtain a report of the size of all the different queues for a particular
release:

```none
$ ./queue report
```

Back to the `NEW` queue for now, however. You'll see output that looks somewhat
like this:

```text
$ ./queue info
 Listing ubuntu/dapper (New) 4
---------|----|----------------------|----------------------|---------------
   25324 | S- | diveintopython-zh    | 5.4-0ubuntu1         | 3 minutes
         | * diveintopython-zh/5.4-0ubuntu1 Component: main Section: doc
   25276 | -B | language-pack-kde-co | 1:6.06+20060427      | 2 hours 20 minutes
         | * language-pack-kde-co-base/1:6.06+20060427/i386 Component: main Section: translations Priority: OPTIONAL
   23635 | -B | upbackup (i386)      | 0.0.1                | 2 days
         | * upbackup/0.0.1/i386 Component: main Section: admin Priority: OPTIONAL
         | * upbackup_0.0.1_i386_translations.tar.gz Format: raw-translations
   23712 | S- | gausssum             | 1.0.3-2ubuntu1       | 45 hours
         | * gausssum/1.0.3-2ubuntu1 Component: main Section: science
---------|----|----------------------|----------------------|---------------
                                                               4
```

The number at the start can be used with other commands instead of referring to
a package by name. The next field shows you what is actually in the queue,
"`S-`" means it's a new source and "`-B`" means it's a new binary. You then have
the package name, the version, and how long it's been in the queue.


## Fetch a package for processing

You can fetch a package from the queue for manual checking:

```none
$ ./queue fetch 25324
```

Or, if you just want to print the URLs, so that you can fetch them on a system
with a faster network connection:

```none
$ ./queue show-urls 25324
```

The source is now in the current directory and ready for checking. Any problems
should result in the rejection of the package (also send a mail to the uploader
explaining the reason and cc ubuntu-archive@lists.ubuntu.com):

```none
$ ./queue reject 25324
```


## Process the package

In addition to the following checks, run `lintian -I` on the source package
(or the binaries) to check that they aren't obviously very buggy in ways that
the linter can detect.

You can flag `lintian` warnings and errors to the uploader, but there are very
few that will give you cause to reject the package. Reports of a malformed
`debian/copyright` are an example that will.


### Managing the package namespace

This is a judgement call, but very short names (3--5 characters) are bad even
if they're not taken already and even if that's the name Upstream calls it by.
A new package with a short name is effectively "squatting" the namespace. After
30+ years of free software, chances are any package which is new now is not
going to have the staying power to warrant claiming a short name, so we should
in general discourage this.

Also bear in mind that we share a package namespace with Debian, and we are
downstream of Debian. So accepting a package name through NEW that is not
obviously tied to the particular software we're introducing runs the risk of
namespace collisions in the future that are painful and annoying to resolve. We
should take care to avoid accepting Ubuntu-specific packages under names that
we think might be used otherwise by Debian in the future.


### Ensuring compliance with the software license

Ensuring compliance with the software license means:

* verifying that the software licenses allow free redistribution (a requirement
  for all packages in Ubuntu, regardless of component)

* verifying that `debian/copyright` correctly reports the licenses and the
  copyright holders.

Some very common free software licenses have requirements that the binary be
accompanied by the full text of the license, and/or list the copyright holders
(e.g. GPL and LGPL). To avoid any possible problems with license compliance, we
expect `debian/copyright` to be maximally conformant with our strictest Free
Software licenses in this regard, by documenting the licenses and the copyright
information fully.

Use of the Debian machine-readable copyright file format is encouraged, but
optional. However, IF someone declares at the top of `debian/copyright` that it
is in this format, I consider failures to follow the standard to be
reject-level bugs.

The actual process of assessing whether a given package's `debian/copyright` is
correct is a disaster. There should be standard tools, shared between package
maintainers, Debian FTP team, and Ubuntu Archive Admins, that traverse the
source package tree, work out the license and copyright of all files, and
compare that with the contents of a machine-readable `debian/copyright` to see
if they match; with support for a `debian/copyright.overrides` that allows the
maintainer to add declarations when auto-detection of the license/copyright in
the source tree is incorrect.

We don't have that.

Instead, we have `licensecheck -r`, which you can run over the tree of a source
package to get a guess as to the copyright and license, one line per file; and
then you can do *ad hoc* scripting to work out from that output whether
`debian/copyright` matches.

You'd be surprised how often something uploaded to the NEW queue doesn't.

Also, it's good to bear in mind the Canonical licensing policy for open source
projects is GPLv3 by default.

If someone produces a `debian/copyright` file listing Canonical as a copyright
holder and claiming the license of the Canonical-copyrighted files is GPLv2,
this is an automatic rejection. But there is a policy that Canonical makes
contributions to upstream projects under the same license that the project uses;
Current Canonical policy is that changes to `debian/packaging` should be
treated as an upstream contribution. Therefore contributing under the license
that the project uses is also acceptable.

And if someone provides a `debian/copyright` that lists an individual with an
`@canonical.com` email address as the copyright holder, this is also an
automatic reject.

The copyright holder for work produced by Canonical employees is Canonical Ltd.

Canonical employees can find details of the copyright and licensing policy in
[the Canonical Reference Library](https://library.canonical.com/legal/licensing-policy).

Technically, ensuring license compliance should also ensure that the license of
newly-introduced packages is compatible with the license of the other packages
they depend on. We have no tooling for this and this check is not enforced at
NEW acceptance currently.

(ensuring-correct-component-based-on-license)=
### Ensuring correct component based on license

In general, Ubuntu follows the Debian Free Software Guidelines and Debian's
interpretation of them with regards to package inclusion in `main` and
`universe`. There is one notable exception, which is that Ubuntu does not
consider GFDL-licensed documentation to be non-free.

This is unlikely to come up in NEW processing however, since almost no one
outside of the FSF/the GNU Project itself uses this license for documentation,
and there's almost no new software from the FSF that we would need to package
directly as opposed to taking via Debian. But some packages have Ubuntu-separate
upstream tarballs because they re-add documentation that is stripped in Debian.

When the license used is one you can obviously point to as being used by other
packages in Ubuntu `main`/`universe`, no further review is needed. If the
license is bespoke or otherwise uncommon/unfamiliar, it's important to check
before accepting the package into `universe` that the license allows: freedom to
redistribute, freedom to modify and redistribute those modifications in turn,
and freedom to distribute binaries built from the code (yes, this is a thing).

Note that for `restricted` vs. `multiverse` there is a technical distinction in
how these components are defined which is *separate* from statements of
Canonical support. The `restricted` component is intended to be used only for
non-free hardware enablement (including drivers and firmware) and non-free
codec support.

Sometimes software that would otherwise go to `restricted` goes to `main`, for
dependency reasons. That is OK, but should be the exception and then has to
pass a full MIR.

Non-free software not in these categories should be shipped in `multiverse`;

* we should not promote other packages to `restricted` based on a Canonical
  position of "support".

Examples that confused, but therefore provide great examples we can align
future decisions to:

* `Linux-firmware-nvidia-tegra`

  * The [license](https://git.launchpad.net/ubuntu/+source/linux-firmware-nvidia-tegra/tree/debian/copyright?h=applied/ubuntu/noble-devel)
    seems non-free

  * [It is for hardware enablement](https://launchpadlibrarian.net/756872927/buildlog_ubuntu-plucky-arm64.linux-firmware-nvidia-tegra_36.4.0-20240912212859-0ubuntu1_BUILDING.txt.gz)
    quote "This package contains proprietary firmware extracted from the
    `nvidia-l4t-firmware` package and needed for all hardware to work on NVIDIA
    Tegra devices."

  * => `restricted`

* `nvidia-firmware-$version`

  * We have mixed states in the Archive right now.

  * ```
    $ rmadison nvidia-firmware-550-550.78
    nvidia-firmware-550-550.78 | 550.78-0ubuntu0.20.04.1 | focal-proposed/**multiverse** | amd64, arm64
    nvidia-firmware-550-550.78 | 550.78-0ubuntu0.22.04.1 | jammy-proposed/restricted | amd64, arm64
    nvidia-firmware-550-550.78 | 550.78-0ubuntu0.24.04.1 | noble-proposed/restricted | amd64, arm64
    ```

  * ```
    $ rmadison nvidia-firmware-535-535.183.01
    nvidia-firmware-535-535.183.01 | 535.183.01-0ubuntu0.20.04.1 | focal-security/restricted | amd64, arm64
    nvidia-firmware-535-535.183.01 | 535.183.01-0ubuntu0.20.04.1 | focal-updates/restricted  | amd64, arm64
    nvidia-firmware-535-535.183.01 | 535.183.01-0ubuntu0.22.04.1 | jammy-security/restricted | amd64, arm64
    nvidia-firmware-535-535.183.01 | 535.183.01-0ubuntu0.22.04.1 | jammy-updates/restricted  | amd64, arm64
    nvidia-firmware-535-535.183.01 | 535.183.01-0ubuntu0.24.04.1 | noble-security/restricted | amd64, arm64
    nvidia-firmware-535-535.183.01 | 535.183.01-0ubuntu0.24.04.1 | noble-updates/restricted  | amd64, arm64
    ```

  * It is hardware enablement

  * It is non-free

  * Firmware counts as drivers

  * => So it should be `restricted`, the one outlier should be fixed right?

  * (vorlon) I think so.


(new-packages-from-debian)=
## New packages from Debian

From time to time, packages will end up in the Ubuntu NEW queue that were
synced from Debian. Source packages that were auto-synced will be also be
auto-accepted, bypassing the NEW queue. Binary packages will, however, land in
the NEW queue; these can be batch accepted using `new-binary-debian-universe`.

Source packages that come from Debian can also land in the NEW queue if they
were manually synced (most often because there is a conflict with existing
Ubuntu binary packages that prevent an auto-sync, or when a sync needs to be
done on a package in `experimental` rather than `unstable`; sometimes, simply
because an Ubuntu developer has gotten impatient waiting for an auto-sync).
Before Feature Freeze, it is sufficient to verify that the package in question
is a sync from Debian based on the Launchpad queue page; no further NEW review
is required. During Feature Freeze, it's a good idea to check whether the new
package would trigger a transition, in which case this should have been
discussed with the release team.


## New packages targeted at stable releases

The SRU policy does not forbid uploading a new source or binary to stable
releases. But, if that happens it needs double approval; one from an {term}`AA`
for the aspect of new queue processing and that of an SRU member for the
regression evaluation. While in the past that often has been done by the few
people wearing both roles at once, that is not always possible. The recommended
way in that case is the following:

1. Ensure there is a tracking bug (which it needs anyway for being an SRU), it 
   will help to coordinate the approvals, later allow to audit why things were
   done and allow the late part of this process to follow the normal SRU steps.

1. Have the Archive Admin evaluate the case and state on the bug about the
   confirmation to be OK in regard to the NEW queue processing.

1. Have the SRU member evaluate the case and state on the bug about
   confirmation to be OK in regard to the SRU rules.

1. Once both agree, the Archive Admin will accept from the new queue. If it was
   a new source package first that and then the subsequent binaries that are
   built. On accepting, ensure the target is "`-proposed`" (the default).

1. That will make the source/binaries all land in `-proposed` of the target
   release.

1. From there, the SRU member can take over with bug updates -- e.g. post the
   "accepted to proposed, please verify" -- as usual.

In reference to the
[SRU documentation](https://documentation.ubuntu.com/sru/en/latest/explanation/pipeline/)
that changes:

* Step 2 different, as it lands in NEW instead of "unapproved".

* Step 3 which is the evaluation that is shared between the AA and SRU person
  for this case.

* From Step 4 all is normal and follows the same paths as any SRU.

The same approach was suggested for the SRU documentation
[in this PR](https://code.launchpad.net/~paelzer/sru-docs/+git/sru-docs/+merge/473706).


## Further special cases processing NEW queue

There are a few special cases which can make this less complex than a full NEW
review in step 2, and gladly they make the most common cases.


### **New -- backports**

Backports of packages already present in the devel series; these should not
require any real NEW review from {term}`AAs <AA>`, just a debdiff to make sure
they match the devel series as expected.


### **New -- source renames**

Renames of newer versions of toolchain packages to allow them to be used as
build-dependencies in support of particular packages; e.g. `gcc-mozilla`,
`golang-1.x.`. These require Archive Admin review of the package names to
satisfy ourselves that they're reasonable, but there should not need to be
license review since again these are backports.

A common issue in this case can be related to transitions, promoting the new is
fine but should go alongside demoting the old. If that is ready to do so, fine.
Sometimes bigger transitions require adding one to `main` and reminding the
person/team driving the case accountable to make the old fully able to be
demoted.

### **New -- kernel metapackages**

There is also the special case of OEM kernel metapackages, which are completely
different and in special ways. Any AA+SRU team member can process one of these;
they are processed using the `oem-metapackage-mir-check` tool in
`lp:ubuntu-archive-tools`.

### **New -- binaries**

The consensus on "bin NEW" reviews is that it's usually lighter than
"source NEW", especially for the case where the sources have *just* been through
NEW. Since there is less ability to provide feedback, only egregious issues
should cause outright regressions, less-critical problems should lead to bugs
being filed. In some cases, we don't actually review the package, see
{ref}`new-packages-from-debian`.

Most checks are based on listing the contents of the `.deb` files.

* If it's an existing binary but on a new architecture, you want to compare the
  contents to, say, the {term}`amd64` version.

* If it's a SONAME transition, compare the contents of `libfoo2` to the last
  version of `libfoo1`.

* Be on the lookout for short filenames in `$PATH`, there's a possibility of
  namespace clashes.

You might also want to run `lintian` on the binaries, and check the control
files for *Breaks*/*Replaces* that are often supposed to accompany new binary
packages for existing sources.

Before accepting, care must be taken to check the target components for each
binary, as some sources produce binaries going to different components, see
{ref}`ensuring-correct-component-based-on-license`.

Before accepting, one should further ensure that all architectures that are
meant to be built are built. Let us not create per-arch differences.

**Beware of the Web UI** for packages outside `universe`: accepting new binaries
for a package will override *all* binaries for that package into the same
component as its source.


## Contact the uploader

Sometimes we might need to discuss with the uploader instead of just rejecting.
In that case have a look at the `.dsc` file with `gpg –verify` to get the
sponsor and the changelog to get the packager. Use that info to connect to them.

## Accepting a package


If the package is fine, you should next check that it's going to end up in the
right part of the archive. On the next line of the `info` output, you have
details about the different parts of the package, including which component,
section, etc. it is expected to head into. One of the important jobs is making
sure that this information is actually correct through the application of
overrides.

To alter the overrides for a package, use:

```none
$ ./queue override -c universe ubuntustudio-menu
```

Where the override can be `-c <component>`, `-x <section>`, and/or (for binary
packages) `-p <priority>`. If you want to limit the override application to
only source or only binary packages, use the `--source` or `--binary` options
respectively.

Often, a binary will be in the `NEW` queue because it is a shared library that
has changed `SONAME`. In this case, check the existing overrides to make sure
anything new matches. These can be found in `/ubuntu/indices` on Ubuntu mirrors.

Currently, a special case of this are the kernel packages, which change package
names with each ABI update and build many distinct binary packages in different
sections. A helper tool has been written to apply overrides to the queue based
on the packages that are currently published:

```none
$ ./kernel-overrides [-s <sourcepackage>] <newabi>
```

Binary packages are not often rejected (they go into a black hole with no
automatic notifications), so, check the `.deb` contains files, run `lintian` on
it and file bugs when things are broken. The binaries also need to be put into
`universe` etc as appropriate even if the source is already there.

If you're happy with a package, and the overrides are correct, accept it with:

```none
$ ./queue accept 23712
```

You can also use `./queue accept binary-name`, which will accept it for all
architectures.


## Partner archive

The Canonical partner archive, though not part of Ubuntu proper, is managed
using the same tools and queues. As such, use the same procedures when
processing partner packages. E.g.:

```text
$ ./queue -s hardy info
Listing ubuntu/hardy (New) 2
---------|----|----------------------|----------------------|---------------
 1370980 | S- | arkeia               | 8.0.9-3              | 19 hours
	 | * arkeia/8.0.9-3 Component: partner Section: utils
 1370964 | S- | arkeia-amd64         | 8.0.9-3              | 19 hours
	 | * arkeia-amd64/8.0.9-3 Component: partner Section: utils
---------|----|----------------------|----------------------|---------------
                                                               2
```

Notice `'Component: partner'`. Use `-A ubuntu/partner` to remove a package:

```none
$ ./remove-package -m "request from First Last name" \
  -A ubuntu/partner -s precise adobe-flashplugin
```

The rules governing package inclusion in partner are not the same as those for
the main Ubuntu archive. See
[Extension Repository Policy](https://wiki.ubuntu.com/ExtensionRepositoryPolicy)
for the Technical Board's requirements regarding the contents of add-on
repositories made available through the `Software Sources` interface.


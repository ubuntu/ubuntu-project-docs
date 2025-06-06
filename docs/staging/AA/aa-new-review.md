(aa-new-review)=
# NEW review

Three main functions of a manual NEW process:

* managing the package namespace

* ensuring compliance with, and correct documentation of, the software license

* ensuring the package is shipped in the correct component based on its license

In addition, I always run `lintian -I` on the source package (or the binaries)
to check that they aren't obviously very buggy in ways that the linter can
detect. I will flag `lintian` warnings and errors to the uploader, but there are
very few that will cause me to reject the package.

(Reports of a malformed `debian/copyright` are one of them.)


## Managing the package namespace

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


## Ensuring compliance with the software license

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
## Ensuring correct component based on license

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

It is sufficient to verify that the package in question is a sync from Debian
based on the Launchpad queue page; no further NEW review is required.


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



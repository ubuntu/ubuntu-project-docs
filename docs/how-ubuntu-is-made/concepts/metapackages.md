(metapackages)=
# Metapackages

A {term}`metapackage <Metapackage>` is a package that does not install any
files itself; it exists only to declare dependencies on other packages, so
that installing it pulls in a predefined set of packages.

Ubuntu's metapackages fall into a few kinds, which differ in why they exist
and in who decides what they depend on.


## Product (seed) metapackages

Metapackages such as `ubuntu-desktop`, `ubuntu-server` or `kubuntu-desktop`
define the set of packages that make up an Ubuntu product or flavor.
Installing one of them gives you the complete corresponding system.

These metapackages are generated from the {term}`Seeds`. Each flavor
maintains a `<flavor>-meta` source package (for example `ubuntu-meta` or
`kubuntu-meta`) whose dependency lists are regenerated from the seeds; the
flavor's maintainer then uploads the resulting package to the Archive. See
{ref}`seed-management` for how that update is done.


## Default version (toolchain) metapackages

Languages and toolchains that have several versions in the archive at once
provide unversioned metapackages that designate which version is the default
for a given Ubuntu release. Examples include `rustc` and `cargo` (from
{lpsrc}`rust-defaults`), `golang-go` (from {lpsrc}`golang-defaults`), `gcc`
(from {lpsrc}`gcc-defaults`), `python3` (from {lpsrc}`python3-defaults`),
`clang` (from {lpsrc}`llvm-defaults`), and `postgresql` (from
{lpsrc}`postgresql-common`).

Unlike the product metapackages, these come from hand-maintained source
packages, usually named `*-defaults`. Updating one to point at a newer version
is the final step of
{ref}`introducing a new default language version <transitions-update-default-version>`.

The point of the unversioned name is that users and build systems can depend on
it without tracking exact version numbers.


## Kernel metapackages

Metapackages such as `linux-image-generic`, `linux-headers-generic` and
`linux-generic` are built from the `linux-meta` source package and always
depend on the packages of the current kernel {term}`ABI`. When a new kernel
version with a new ABI is uploaded, `linux-meta` is uploaded alongside it,
so a regular system upgrade installs the new kernel (the old kernel remains
installed, so the system can still boot into it).

Variants exist for the other kernel flavors, including the hardware
enablement (HWE) kernels (`linux-generic-hwe-*`) and OEM kernels.


## OEM metapackages

`oem-<product>-meta` packages enable support for specific OEM hardware.
They differ from the other categories in several ways:

* They are matched to the hardware they support through `XB-Modaliases`,
  and are offered for installation by `ubuntu-drivers` when the machine
  matches.
* They install an {term}`APT` source that enables the OEM archive.
* They follow a streamlined {ref}`MIR exception <mir-exceptions-oem>` and
  {ref}`SRU exception <reference-exception-OEMMetaUpdates>` instead of the
  regular processes, and are verified with the `oem-metapackage-mir-check`
  tool from `lp:ubuntu-archive-tools`.


## Other metapackages

Not every metapackage falls neatly into the categories above. For example,
`build-essential` pulls in the toolchain required to build Debian packages,
and `ubuntu-restricted-extras` pulls in commonly used multimedia codecs.

Ubuntu also carries a large number of metapackages inherited unchanged from
Debian. Most of these are the task-based metapackages of the
[Debian Pure Blends](https://www.debian.org/blends/) (Debian Astro, Debian
Science, Debian Med, Debian Games, and so on -- see the
[Blends manual](https://blends.debian.org/blends/) for how they are
generated), plus metapackages for desktop environments Ubuntu doesn't ship as
a flavor (`kde-standard`, `lxqt`, `cinnamon-core`, and similar). These are not
reviewed or maintained by any Ubuntu team.

A related but distinct concept is the **transitional package**: an
empty package left behind after a package rename or split, which depends on
the replacement package so that upgrades continue to work. Unlike the
metapackages above, transitional packages are temporary by design and can
be removed once the upgrade is done.


## Summary

| Category        | Examples                                  | Built from                    | Dependencies determined by           |
|-----------------|-------------------------------------------|-------------------------------|--------------------------------------|
| Product (seed)  | `ubuntu-desktop`, `kubuntu-desktop`       | `<flavor>-meta`               | The {term}`Seeds`                    |
| Default version | `rustc`, `golang-go`, `gcc`, `postgresql` | `*-defaults` and similar      | Maintainers of those source packages |
| Kernel          | `linux-image-generic`, `linux-generic`    | `linux-meta` and its variants | The current kernel {term}`ABI`       |
| OEM             | `oem-qemu-meta`                           | `oem-<product>-meta`          | Hardware enablement needs            |
| Other           | `build-essential`, Debian Pure Blends     | Various, mostly from Debian   | Whoever maintains them, often in Debian |


(how-apt-treats-some-metapackages)=
## How APT treats (some) metapackages

The default {term}`APT` configuration handles packages in the
`metapackages` {term}`section` differently when deciding which
packages may be automatically removed.

Normally, a package that is installed only as a
dependency of another package is marked as automatically installed,
and `apt autoremove` offers to remove it once no manually installed
package depends on it anymore.

By default, Ubuntu configures APT to *never* mark packages in the
`metapackages` section as automatically installed
(`APT::Never-MarkAuto-Sections "metapackages"`, see {ref}`archive-sections`).
A metapackage installed by the user therefore stays "manually installed" --
and keeps its dependencies installed -- until it is explicitly removed.

The product metapackages (`ubuntu-desktop` and friends) are in the
`metapackages` section, as are many of the ones inherited from Debian --
`kde-standard`, `lxqt` and `cinnamon-core` among them. Not all of them are,
though: several Debian Pure Blends metapackages sit in `misc` instead, such as
`med-bio` and `science-mathematics`.

The other categories are not in that section at all -- toolchain metapackages
are in `devel`, kernel ones in `kernel` -- so if they ever get marked as
automatically installed, a later `apt autoremove` may remove them and
everything they pull in.

See also:

* {manpage}`apt-mark(8)`
* [Metapackage (Debian Wiki)](https://wiki.debian.org/metapackage)
* {ref}`archive-sections`

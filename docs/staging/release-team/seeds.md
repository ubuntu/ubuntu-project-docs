(seeds)=
# Seeds

```{note}
* Page source: [wiki - Seed Management](https://wiki.ubuntu.com/SeedManagement)
* Page source: [wiki - Ubuntu Studio/seeds](https://wiki.ubuntu.com/UbuntuStudio/Seeds)

This page will be moved to:
* How Ubuntu is made > concepts >
```

```{admonition} **Seed management** series
The article series explains seeds and how they are used.

Seeds overview:
: {ref}`seeds` (this article)

Related topics:
: {ref}`germinate`

Practical guidance:
: {ref}`seed-management`
```

Seeds are text files listing the packages we want to include in the Ubuntu
distribution. A {ref}`germinate` script parses these seed files and ensures the
packages are installed on the user's system.


## Available seeds

There are seven primary seeds, which define what goes into the Ubuntu Package
Archive's `main` component:

* {ref}`seeds-minimal`
* {ref}`seeds-boot`
* {ref}`seeds-standard`
* {ref}`seeds-desktop`
* {ref}`seeds-ship`
* {ref}`seeds-live`
* {ref}`seeds-supported`

These are described in more detail below.

These are not the only seeds that exist - you can
[view the current seeds](https://ubuntu-archive-team.ubuntu.com/seeds/)
and the corresponding
[germinate output](https://ubuntu-archive-team.ubuntu.com/germinate-output/)
for them.


## How seeds are used

Seeding a package pulls all of its dependencies into the appropriate part of
the Archive and ensures everything needed to build that package is at least
placed in `supported`.

The actual movement of packages between `main` and `universe` is semi-automatic.
A tool called
[`component-mismatches`](https://ubuntu-archive-team.ubuntu.com/component-mismatches.txt)
reports on what should be promoted or demoted according to the seeds. The
Archive Administrators review these mismatches by hand and process them.


### Germinate

The seeds are read by a program called {ref}`germinate`, which
resolves the dependencies of packages in the seed lists. By
adding additional packages to satisfy these dependencies, the final package
lists are produced.


### CD builds

* The Desktop CD contains the software in the `ship-live` seed (and its
  dependencies)
* The Alternate CD contains the software in the `ship` seed (and its
  dependencies)
* The DVD contains the software in the `dvd` seed (and its dependencies)
* The Live Server CD contains the software in the `server-ship-live` seed
  (and its dependencies)


## Seed descriptions

(seeds-minimal)=
### Minimal

The minimal system provides enough packages to install a basic command-line
system, boot, and install more packages. It also contains any packages that
should be available the first time the system boots after installation (for
example, hardware detection blocklists). It does not provide X11 or any services
listening on any non-localhost ports.

Packages in minimal should be:

* Absolutely stable, standard tools we think will be around forever and are
  willing to maintain (even if the whole world moves on).

* Diagnostic tools to get the system and network up and running, that are
  valuable to have "always there" (just in case).
  
* Widely applicable (in the Lowest Common Denominator sense) to every
  installation -- Desktop or Server.

A "minimal" system is not expected to be useful for any particular purpose;
it exists for bootstrapping more interesting systems.

```{admonition} Historical note
:class: note

In Ubuntu 5.04 and earlier, the minimal and standard seeds were part of a single
base seed. They were separated to reduce the size of the system installed by
`debootstrap`.
```


(seeds-boot)=
### Boot

The boot seed lists the default kernels and boot loaders required for each
processor architecture. It is kept separate from the minimal seed for technical
reasons; chiefly that having `debootstrap` install default kernels and
bootloaders reduces the flexibility of the installer to choose alternatives.

```{admonition} Historical note
:class: note

In Ubuntu 5.10 and earlier, the boot seed was part of the minimal seed.
```


(seeds-standard)=
### Standard

The standard seed provides the package list to create a solid foundation for a
Desktop or Server, without providing X11 or any services listening on any
non-localhost ports.

The criteria for packages in standard are similar to those for packages in
minimal, but in standard we concentrate more on the Greatest Common Factor.
The standard system includes packages that make up a traditional comfortable
UNIX system, a variety of networking clients and tools, advanced filesystem
support, and various diagnostic utilities.

A "standard" system is not expected to be useful for any particular purpose.
It's simply the minimal working system that we support. It should be a platform
that one can quickly get working, and on top of which one can construct a
useful collection of services. Typically, servers start out as a "standard"
system, and the system administrator then adds specific services and packages
as needed.

```{admonition} Historical note
:class: note

In Ubuntu 5.04 and earlier, the minimal and standard seeds were part of a
single base seed. They were separated in order to reduce the size of the system
installed by `debootstrap`.
```


(seeds-desktop)=
### Desktop

The desktop seed ought to be a checklist of Desktop features that would appeal
to a user or procurer. Thus, the desktop seed should be as simple as possible
without being too simple, and be directly focused on solving Desktop problems.

One of the valuable design choices in Debian is that if you install a daemon,
it is assumed that you intend to use it. If you don't want to run it, don't
install it. Requiring that a daemon be installed but not wanting to run it is a
rarely-by-few use case, so Debian doesn't optimize for it. Rightly so. We look
at our Desktop seed in a similar light. If we put it on the list, it should be
installed; if we install it, assume that it will be used. In some cases, this
will be "running by default", but in most cases on the desktop, it just means
"available or visible by default".

We should not confuse the Desktop seed with "what's on the CD", because we can
always fill the remaining space on the CD with high priority items. Similarly,
we should not put important things that are independent of our desktop solution
in the Desktop seed, as this will adversely affect our focus. Major distro
features that are not Desktop-oriented should have their own sections on the
Supported seed page.


(seeds-ship)=
### Ship

The ship seed lists packages included on the CD for convenience, but that are
not part of the default set of packages to install. Common examples include:

* Utilities that may be necessary (in some cases) to connect to a network.

* Common server applications.


(seeds-live)=
### Live

Software to be installed on the Ubuntu Live CD, in addition to the default
desktop list.


(seeds-supported)=
### Supported

The supported system provides functionality not included by the standard or
desktop systems but which meets the following criteria:

1. It is very widely used, people are committed to it.

1. It is not architecturally insecure, it is thus easy for us to provide
  security fixes and updates.

This list would include popular servers other than the ones we include in a
standard or desktop install, additional desktop software, and a build
environment. It is never expected that someone would install the entire
supported list of packages; they would choose specific packages that provide
specific needed functionality.

This list is all the extra packages we think need to be supported in our distro.
We will accept contributions of additional packages into this list, if they:

1. Have an external maintainer who agrees to maintain them to our standard,
   in [Bzr](https://wiki.ubuntu.com/Bzr), using `Soyuz`.
1. Pass a one-time security review from `MartinPitt` and agree to be responsive to him on `SecurityPage` issues.

```{note}
These steps are VERY out of date. `MartinPitt` and `SecurityPage` no longer
exist on the wiki, but also don't redirect anywhere. Please update the process,
and then delete this note.
```

Some packages in this list will also ship on the CD, subject to the amount of
space we have on the CD. They would typically be cached on the installed hard
drive for rapid installation without the CD. All of these packages will be
available in the online archive of packages.



supported-desktop
: Should not contain anything; it aggregates the more specific Desktop-related
  seeds.

supported-desktop-extra
: Packages that get additional support for 5 years on an LTS.

supported-server
: Should not contain anything; it aggregates the more specific Server-related
  seeds.

supported-hardware-desktop
: Hardware-related packages used on Desktop only.

supported-hardware-common
: Hardware-related packages that are used on both Desktop and Server.

supported-installer-desktop
: Installer-related packages used for Desktop installations only.

supported-installer-common
: Installer-related packages that are used on both Desktop and Server.

supported-network-common
: Network-related packages that are used on both Desktop and Server.

supported-sysadmin-desktop
: System administration packages that are used on both Desktop and Server.

supported-sysadmin-common
: System administration packages that are used on both Desktop and Server.

supported-development
: Development packages that are used on both Desktop and Server.

supported-misc-servers
: Miscellaneous Server-only packages.

supported-kernel
: Kernel packages that are used on both Desktop and Server.

```{admonition} Historical note
:class: note

The supported seed has been split during the Intrepid cycle, so that the
supported seed is split functionally and allows people to distinguish between
Server and Desktop packages. This was particularly needed in order to know if
the three-year or five-year maintenance period would apply for a given package.
A good way to gain an understanding of it is to take a look at the
{ref}`seed-management-graphs`.
```

(seeds-extra)=
### Extra

Binary packages which are built by a supported source package, but not
supported themselves, are automatically added to a special "extra" list.


## Maintenance period

**Maintained** means that the team *commits to providing security updates for
the packages that are defined in the seed and whatever dependencies are
necessary to make them work*.

```{admonition} Lynx link's invalid - what's the current replacement?
The exact manifests are release-specific and can be found at the Release
Manifest page of the release in question (e.g. for 10.04 LTS at
[Lucid Lynx/Release Manifest](https://wiki.ubuntu.com/LucidLynx/ReleaseManifest).
```

Canonical provides free maintenance for Ubuntu products as follows:

````{admonition} Needs to be updated

Ubuntu Desktop, Kubuntu, Ubuntu Server
: Security updates and select bug fixes:
  * 9 months since Raring [13.04]
  * 18 months for prior non-LTS releases
: This is currently defined as the entire content of `main`

Ubuntu Desktop LTS, Kubuntu LTS
: Security updates and select bug fixes:
  * 5 years since Precise [12.04]
  * 3 years for prior LTS releases
: This is defined as the union of the ship, supported-desktop and
  supported-desktop-extra seeds

Ubuntu Server LTS
: Hardware compatibility updates (until next LTS)
: Security updates and select bug fixes (5 years)
: This is defined as the union of the server-ship and supported-server seeds

The `Packages` file contains the `Supported` field, as generated by Soyuz via
the `maintenance-check.py` file from
[`ubuntu-archive-publishing`](http://code.launchpad.net/~ubuntu-archive/ubuntu-archive-publishing/trunk/).

```{note}
Since it is no longer possible to view bazaar-hosted files in the web browser,
it is necessary to check this file out locally, following the instructions in
the repository.
```
````

The content of `main` is defined as the union of the seeds: `ubuntu.all`,
`kubuntu.all`, `edubuntu.all`, `netbook.all`. If that changes then the code in
`maintenance-check.py` needs updating.

```{admonition} Question
Should we also reference Ubuntu Pro and the maintenance schedule for that here?
```


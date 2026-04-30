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

A seed is a plain-text file that defines a curated set of packages using a small, specialized syntax.
Seeds are used to describe which packages should be included in the support
package set represented by the [main component](https://documentation.ubuntu.com/project/how-ubuntu-is-made/concepts/package-archive/#main)
, as well as which packages make up different Ubuntu system images.

Rather than listing every dependency explicitly, seeds express the intended package selection at a high level; tools
like {ref}`germinate` then expand these definitions into complete, dependency-resolved package lists used for
building and maintaining the distribution.

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

These are not the only seeds that exist. You can
[view the current seeds](https://static-reports.ubuntu.com/seeds/)
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

The supported seeds allow to include packages into main while not including
it in any media (ISOs), images or installation (via meta packages). This list
is all the extra packages we think need to be supported in our distro.

Additional packages can be added to this list, but they need to complete a
{ref}`Main Inclusion Review <main-inclusion-review>` process and have an
owning team.

The supported set is categorized into different sets, usually prefixed with
"supported":

supported-server
: Additional packages that are considered part of the supported server package set,
  but are not necessarily part of the default installed image.

supported-desktop
: Additional packages that are considered part of the supported desktop package set,
  but are not necessarily part of the default installed image.

supported-common
: Server and Desktop packages defined in supported-server and supported-desktop

For the full list of supported categories, see the
[Platform seed repository](https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/platform).

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

A binary package being in `main` implies that the
[owning team](http://reports.qa.ubuntu.com/m-r-package-team-mapping.html)
commits to maintain the source package. Furthermore, the Ubuntu security team
provides security coverage.
This coverage is further extended by [Ubuntu Pro](https://documentation.ubuntu.com/project/how-ubuntu-is-made/concepts/glossary/#term-Ubuntu-Pro),
which provides expanded security maintenance coverage.

(seed-management)=
# Seed management

## Definition

**Seeds** are the lists of packages we want to include in the distribution. We
have seven primary seeds;

* **minimal**
* **boot**
* **standard**
* **desktop**
* **ship**
* **live**
* **supported**.

These define what goes into the archive's **main** component. The **minimal**,
**boot**, **standard**, **desktop**, and either **ship** or **live** seeds go
onto our CDs and the **supported** packages are available from the FTP site.

Seeding a package pulls all of its dependencies into the appropriate part of
the archive and ensures everything needed to build that package is at least
placed in **supported**.

You can [view the current seeds](https://ubuntu-archive-team.ubuntu.com/seeds/)
and the [current output of germinate](https://ubuntu-archive-team.ubuntu.com/germinate-output/)
for them.

The actual movement of packages between main and universe is semi-automatic. A
tool called [`component-mismatches`](https://ubuntu-archive-team.ubuntu.com/component-mismatches.txt)
produces a report on what should be promoted or demoted according to the seeds,
which the archive administrators review by hand and process.

(seed-management-graphs)=
## Graph

Germinate was modified so that it produces a `structure.dot` file which can be
used to produce a graph of the seeds structure using `graphviz`. This can be
useful to figure how the seed are overall linked:

```bash
wget http://people.canonical.com/~ubuntu-archive/germinate-output/ubuntu.precise/structure.dot
dot -Tpng structure.dot > structure.png
```

## Descriptions of seeds

### Boot

The boot seed lists default kernels and boot loaders required for each processor
architecture. It is kept separate from the minimal seed for technical reasons,
chiefly that having `debootstrap` install default kernels and bootloaders
reduces the flexibility of the installer to choose alternatives.

In Ubuntu 5.10 and earlier, the boot seed was part of the minimal seed.

The raw boot seed list for the Gutsy Gibbon release can be found in
`http://people.canonical.com/~ubuntu-archive/seeds/ubuntu.gutsy/boot`.

### Minimal

The minimal system provides enough packages to install a basic command-line
system, boot, and install more packages. It also contains any packages that
should be available the first time the system boots after installation (for
example, hardware detection blacklists). It does not provide X11 or any services
listening on any non-localhost ports.

Packages in minimal should be:

* Absolutely stable, standard tools that we think will be around forever and we
  are prepared to maintain even if the whole world moves on.
* Useful diagnostic tools that one can use to get the system and network up and
  running, and are valuable to have "always there" in case of need.
* Widely applicable (in the Lowest Common Denominator sense) to every
  installation -- Desktop or Server.

A "minimal" system is not expected to be useful for any particular purpose;
it's simply there for bootstrapping more interesting systems.

In Ubuntu 5.04 and earlier, the minimal and standard seeds were part of a single
base seed. They were separated in order to reduce the size of the system
installed by `debootstrap`.

The raw minimal seed list for the Gutsy Gibbon release can be found in
`http://people.canonical.com/~ubuntu-archive/seeds/ubuntu.gutsy/minimal`.

### Standard

The standard system provides a solid foundation for a desktop or server without
providing X11 or any services listening on any non-localhost ports. This seed
package list, once the complete dependency set has been added, provides that
system.

The criteria for packages in standard are similar to those for packages in
minimal, but we concentrate more on the Greatest Common Factor than on the
Lowest Common Denominator. The standard system includes packages that make up a
traditional comfortable UNIX system, a variety of networking clients and tools,
advanced filesystem support, and various diagnostic utilities.

A "standard" system is not expected to be useful for any particular purpose.
It's simply the minimal working system that we support. It should be a platform
that one can quickly get working, and on top of which one can construct a
useful collection of services. Typically, servers would start out life as a
"standard" system, and the system administrator would then add specific services
and packages as needed.

In Ubuntu 5.04 and earlier, the minimal and standard seeds were part of a
single base seed. They were separated in order to reduce the size of the system
installed by `debootstrap`.

The raw standard seed list for the Gutsy Gibbon release can be found in
`http://people.canonical.com/~ubuntu-archive/seeds/ubuntu.gutsy/standard`.

### Desktop

The Desktop seed, minimally summarized, ought to be a checklist of desktop
features that would appeal to a user or procurer. Our default Desktop install
should include every single package mentioned in the Desktop seed. Thus, the
seed should be as simple as possible without being too simple, and be directly
focused on solving desktop problems.

One of the valuable design choices in Debian is that if you install a daemon,
it is assumed that you intend to use it. If you don't want to run it, don't
install it. Requiring that a daemon be installed but not wanting to run it is a
rarely-by-few use case, so Debian doesn't optimize for it. Rightly so. We ought
to look at our Desktop seed in a similar light. If we put it on the list, it
should be installed. If we install it, assume that it will be used. In some
cases, this will be "running by default", but in most cases on the desktop, it
just means "available or visible by default".

We should not confuse the Desktop seed with "what's on the CD", because we can
always fill the remaining space on the CD with high priority items. Similarly,
we should not put important things that are independent of our desktop solution
in the Desktop seed, as this will adversely affect our focus. Major distro
features that are not Desktop-oriented should have their own sections on the
Supported seed page.

The raw desktop seed list for the Gutsy Gibbon release can be found in
`http://people.canonical.com/~ubuntu-archive/seeds/ubuntu.gutsy/desktop`.

### Ship

Packages which will be included on the CD for convenience, but are not part of
the default set of packages to install. Common examples include:

* Utilities which might be necessary in some cases in order to connect to a network.
* Common server applications.

The raw Ship seed list for the Gutsy Gibbon release can be found in
`http://people.canonical.com/~ubuntu-archive/seeds/ubuntu.gutsy/ship`.

### Live

Software which will be installed on the Ubuntu Live CD, in addition to the
default desktop set.

The raw Live seed list for the Gutsy Gibbon release can be found in
`http://people.canonical.com/~ubuntu-archive/seeds/ubuntu.gutsy/live`.

### Installer

The installer seed tracks packages which are part of the installer as used on
the install CD.

The raw Installer seed list for the Gutsy Gibbon release can be found in
`http://people.canonical.com/~ubuntu-archive/seeds/ubuntu.gutsy/installer`.

### Casper

The Casper seed tracks packages which are part of the installer subset used on
the live CD. It is no longer used as of
[Dapper Drake](https://wiki.ubuntu.com/DapperDrake), following the introduction
of the new [simplified live CD](https://wiki.ubuntu.com/SimplifiedLiveCD).

### Supported

The supported system provides functionality not included by the Base or Desktop
systems but which meets the following criteria:

1. It is very widely used, people are committed to it.
1. It is not architecturally insecure, it is thus easy for us to provide
  security fixes and updates.

This list would include popular servers other than the ones we include in a
Base or Desktop install; additional desktop software; and a build environment.
It is never expected that someone would install the entire Supported list of
packages, they would choose specific packages that provide specific needed
functionality.

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

The raw Supported seed list for the Gutsy Gibbon release can be found in
`http://people.canonical.com/~ubuntu-archive/seeds/ubuntu.gutsy/supported`.

The supported seed has been split during the Intrepid cycle, so that the
supported seed is split functionally and allows people to distinguish between
Server and Desktop packages. This was particularly needed in order to know if
the three-year or five-year maintenance period would apply for a given package.
A good way to gain an understanding of it is to take a look at the
{ref}`seed-management-graphs`.

* **supported-desktop**

  Should not contain anything; it aggregates the more specific Desktop-related seeds.

* **supported-desktop-extra**

  Packages that get additional support for 5 years on a LTS.

* **supported-server**

  Should not contain anything; it aggregates the more specific Server-related seeds.

* **supported-hardware-desktop**

  Hardware-related packages used on Desktop only.

* **supported-hardware-common**

  Hardware-related packages that are used on both Desktop and Server.

* **supported-installer-desktop**

  Installer-related packages used for Desktop installations only.

* **supported-installer-common**

  Installer-related packages that are used on both Desktop and Server.

* **supported-network-common**

  Network-related packages that are used on both Desktop and Server.

* **supported-sysadmin-desktop**

  System administration packages that are used on both Desktop and Server.

* **supported-sysadmin-common**

  System administration packages that are used on both Desktop and Server.

* **supported-development**

  Development packages that are used on both Desktop and Server.

* **supported-misc-servers**

  Miscellaneous Server-only packages.

* **supported-kernel**

  Kernel packages that are used on both Desktop and Server.

### Extra

Binary packages which are built by a supported source package, but not
supported themselves, are automatically added to a special "extra" list.

## How the seeds are used

### Germinate

The seeds are read by a program called {ref}`Germinate <germinate>`, which
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

## Changing the seeds

If seeding the package would mean that it had to be in main and it is not
currently then you should go through the
[Main Inclusion Review (MIR)](https://github.com/canonical/ubuntu-mir) process
for the package first. If the package is in main, or seeding the package
wouldn't require it to be in main (e.g. seeding for a CD built from universe)
then you can skip this step.

Seeds are maintained in a [Launchpad project](https://launchpad.net/ubuntu-seeds) 
whose git repositories [are published here](https://code.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/)

To get a checked-out copy of the seeds that you can edit:

```bash
git clone -b cosmic https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/ubuntu
```

Make sure to set an appropriate user ID in git, like this:

```bash
git config --global user.name 'Colin Watson'
git config --global user.email 'colin.watson@canonical.com'
```

```{admonition} Is this still true?
:class: caution

Some seeds have not yet been migrated to git. See [revision 73](https://wiki.ubuntu.com/SeedManagement?action=recall&rev=73) of this page for the old, bzr-based instructions.
```

You can find some documentation of the syntax of seeds files in the [germinate manual page](https://manpages.ubuntu.com/manpages/jammy/en/man1/germinate.1.html).

* Note that changes to the seeds do not automatically cause packages to move to
  a new component in the archive. See the [MIR queue](https://bugs.launchpad.net/~ubuntu-mir/+subscribedbugs).

* If any of the `ubuntu-meta`, `kubuntu-meta`, `edubuntu-meta`, or `xubuntu-meta`
  source packages build a metapackage for the seed you changed, run the `update`
  script in the appropriate source package and upload it (after your changes
  have been effected in the seeds archive; you will need to wait about 20 minutes
  for these changes to propagate to the public mirror).

## Debugging seed problems

**Why does package X get pulled onto the CD (or into the archive)?**

All the logs necessary to answer this kind of question are available, but they
do take some interpretation, and sometimes you need to run `germinate` locally
if you don't have access to all its output. Let's take a worked example, of
investigating why `exim4-base` and friends landed on the Ubuntu alternate
install CD (this happened on 2009-01-15):

* There are several packages involved, but they all start with `exim4`, so we'll just search for that.
* Look at the `germinate` output to find out which seed contains `exim4`
  (`grep -l ^exim4 *` in the appropriate directory, in this case `/srv/cdimage.ubuntu.com/scratch/ubuntu/daily/germinate/jaunty/i386` on `antimony`;
  had we not had direct access, running `germinate` by hand with some
  appropriate arguments usually produces a good approximation).
* This produces quite a lot of output. Cut down on some of `germinate`'s
  auxiliary output files:

  ```bash
  $ grep -l ^exim4 * | fgrep -v . | xargs
  
  all all+extra d-i-requirements dvd provides server-ship supported-development supported-misc-servers supported-sysadmin-common
  ```
* `all`, `all+extra`, and `provides` are not real seeds, so ignore these. The
  only one of the rest on the alternate CD is `d-i-requirements`. You can look
  at the file itself, and the result is sometimes useful:
  ```bash
  $ grep ^exim4 d-i-requirements | cut -d\| -f1-3

  exim4-base          | exim4            | exim4-daemon-heavy
  exim4-config        | exim4            | exim4-base
  exim4-daemon-heavy  | exim4            | mdadm (Recommends)
  ```
* Alternatively, you can look at `germinate`'s output, which sometimes provides
  rationale and supporting information (although in a rather terse form). In
  this case, the output is in
  [CD build logs](https://ubuntu-archive-team.ubuntu.com/cd-build-logs/). We
  know which seed was involved, so search for "`Resolving d-i-requirements dependencies`". Here's the output:
  ```bash
  Resolving d-i-requirements dependencies ...
  * Chose libcurl4-openssl-dev out of libcurl3-dev to satisfy libxen3
  ! Promoted exim4-daemon-heavy from server-ship to d-i-requirements to satisfy mdadm
  ! Promoted exim4-base from server-ship to d-i-requirements to satisfy exim4-daemon-heavy
  * Chose cron to satisfy exim4-base
  ! Promoted exim4-config from server-ship to d-i-requirements to satisfy exim4-base
  * Chose exim4-config to satisfy exim4-base
  ! Promoted mailx from ship to d-i-requirements to satisfy exim4-base
  ! Promoted libmysqlclient15off from server-ship to d-i-requirements to satisfy exim4-daemon-heavy
  ! Promoted mysql-common from server-ship to d-i-requirements to satisfy libmysqlclient15off
  ! Promoted libpq5 from server-ship to d-i-requirements to satisfy exim4-daemon-heavy
  ```
* This confirms the earlier results: `mdadm` `Recommends: mail-transport-agent`,
  so `germinate` picked one. It tries seeds that strictly contain
  `d-i-requirements` first, so used `server-ship` and found (arbitrarily)
  `exim4-daemon-heavy`. The problem may be fixed by using
  `Recommends: postfix | mail-transport-agent` instead.
* Often, more than one dependency arc is involved, and `germinate` won't always
  list them all verbosely. You can look in the `rdepends` files for this, which
  are published at URLs of the form
  `http://people.canonical.com/~ubuntu-archive/germinate-output/<seedcollection>/rdepends/ALL/<packagename>'`,
  where `<seedcollection>` might be `ubuntu.jaunty` or `kubuntu.intrepid`, etc.

## Maintenance period

**Maintained** means that the team *commits to providing security updates for
the packages that are defined in the seed and whatever dependencies are
necessary to make them work*.

The exact manifests are release specific and can found at the [Release Manifest](https://wiki.ubuntu.com/ReleaseManifest) page of the release in question (e.g. for 10.04 LTS at [Lucid Lynx/Release Manifest](https://wiki.ubuntu.com/LucidLynx/ReleaseManifest).

Canonical provides free maintenance for Ubuntu products as follows:

* Ubuntu Desktop, Kubuntu, Ubuntu Server:

  * Security updates and select bug fixes (9 months since Raring [13.04], 18 months for prior non-LTS releases)
  * This is currently defined as the entire content of main

* Ubuntu Desktop LTS, Kubuntu LTS:

  * Security updates and select bug fixes (5 years since Precise [12.04], 3 years for prior LTS releases)
  * This is defined as the union of the ship, supported-desktop and supported-desktop-extra seeds

* Ubuntu Server LTS:

  * Hardware compatibility updates (until next LTS)
  * Security updates and select bug fixes (5 years)
  * This is defined as the union of the server-ship and supported-server seeds

The `Packages` file contains the `Supported` field, as [generated by Soyuz](http://bazaar.launchpad.net/~ubuntu-archive/ubuntu-archive-publishing/trunk/view/head:/scripts/maintenance-check.py).

The content of main is defined as the union of the seeds: ubuntu.all, kubuntu.all, edubuntu.all, netbook.all. If that changes then the code in `http://bazaar.launchpad.net/~ubuntu-archive/ubuntu-archive-publishing/trunk/view/head:/scripts/maintenance-check.py` needs updating.

## Notes

```{caution}
These are probably obsolete, and need a technical review to see what's still
relevant
```

### Brain-dump notes

Launchpad does not manage seeds within its database. Instead we have an arch
branch on the super-mirror and tell the Launchpad about the branch. We then have
a tool which takes germinate output, interacts with launchpad (E.g. over XMLRPC)
and does the component changes. We can also integrate that into the appservers
so you can click a button, launchpad will check out the branch from the
super-mirror, germinate and let you manipulate things that way.

The pluses of this method are:

* Much less coding resource needed from the Launchpad team in the short term
  (don't need to design entire DB sections and pages for editing seeds) but in
  the long term we're still flexible for moving to more control in Launchpad.
* Ubuntu team gets their history, branching, merging, diffing, etc all for free
  from bazaar.
* Ubuntu team continues to get their direct low-level control of how seeds
  affect the components.
* Ubuntu team have slightly less to learn to move to Launchpad in the initial
  case.

The minuses of this method are:

* Less direct control in Launchpad
* Launchpad has to have access to the super-mirror
* Direct `pybaz` dependency will be introduced.

The Launchpad stuff:

* Launchpad gains a concept called a 'Flavour' which for now has an arch branch
  in a text field. Later we can always key seed tables off this table.
* Flavours do not inherit within the Launchpad because that'd be too confusing
  for the seed management people. They get inheritance by virtue of bazaar's
  branching and merging, ancestry etc and this seems a desirable level for them.

### Status

* Originally Created: 2005-04-28
* Last updated: 2022-04-06
* Contributors: `DanielSilverstone`, `schopin`

### Dependents

```{caution}
These pages are linked as dependents on the original wiki page. They all contain
content that either may be relevant (and should be moved) or that will need the
links to this page updating.
```

* [Archive Administration](https://wiki.ubuntu.com/ArchiveAdministration?highlight=%28SeedManagement%29)
* [Archive Reorganization](https://wiki.ubuntu.com/ArchiveReorganisation?highlight=%28SeedManagement%29)
* [Base Seed Proposals](https://wiki.ubuntu.com/BaseSeedProposals?highlight=%28SeedManagement%29)
* [Derivative Distro How-to](https://wiki.ubuntu.com/DerivativeDistroHowto?highlight=%28SeedManagement%29)
* [Foundations Team/Specs/Lucid Support Time frame Information](https://wiki.ubuntu.com/FoundationsTeam/Specs/LucidSupportTimeframeInformation?highlight=%28SeedManagement%29)
* [Frank Heimes/FAQ](https://wiki.ubuntu.com/FrankHeimes/FAQ?highlight=%28SeedManagement%29)
* [MOTU/Wiki Clean Up/Some Review Notes](https://wiki.ubuntu.com/MOTU/WikiCleanUp/SomeReviewNotes?highlight=%28SeedManagement%29)
* [Specs/Mobile Team Seed Management](https://wiki.ubuntu.com/Specs/MobileTeamSeedManagement?highlight=%28SeedManagement%29)
* [Supported Seed Proposals](https://wiki.ubuntu.com/SupportedSeedProposals?highlight=%28SeedManagement%29)
* [Ubuntu Architecture](https://wiki.ubuntu.com/UbuntuArchitecture?highlight=%28SeedManagement%29)
* [Ubuntu Developers](https://wiki.ubuntu.com/UbuntuDevelopers?highlight=%28SeedManagement%29)
* [Ubuntu Developers/Team Delegation](https://wiki.ubuntu.com/UbuntuDevelopers/TeamDelegation?highlight=%28SeedManagement%29)
* [Ubuntu Development/Installation Media](https://wiki.ubuntu.com/UbuntuDevelopment/InstallationMedia?highlight=%28SeedManagement%29)
* [Ubuntu Development/Package Archive](https://wiki.ubuntu.com/UbuntuDevelopment/PackageArchive?highlight=%28SeedManagement%29)
* [Ubuntu Down Under/BOFs/Derivative Distro Data Model](https://wiki.ubuntu.com/UbuntuDownUnder/BOFs/DerivativeDistroDataModel?highlight=%28SeedManagement%29)
* [Ubuntu Down Under/BOFs/Identifying Primary Packages](https://wiki.ubuntu.com/UbuntuDownUnder/BOFs/IdentifyingPrimaryPackages?highlight=%28SeedManagement%29)
* [Ubuntu Down Under/BOFs/Package Selection](https://wiki.ubuntu.com/UbuntuDownUnder/BOFs/PackageSelection?highlight=%28SeedManagement%29)
* [Ubuntu Down Under/Schedule Wednesday](https://wiki.ubuntu.com/UbuntuDownUnder/ScheduleWednesday?highlight=%28SeedManagement%29)
* [Ubuntu Flavors](https://wiki.ubuntu.com/UbuntuFlavors?highlight=%28SeedManagement%29)
* [Ubuntu Studio/Developer Documentation/Scratchpad](https://wiki.ubuntu.com/UbuntuStudio/DeveloperDocumentation/Scratchpad?highlight=%28SeedManagement%29)





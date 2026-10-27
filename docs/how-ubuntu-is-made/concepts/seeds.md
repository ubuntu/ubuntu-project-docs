(seeds)=

# Seeds

Seeds are how Ubuntu developers identify subsets of packages they care
about: a seed defines the set of packages that make up "an Ubuntu desktop
system", for example.

Ubuntu uses seeds to:

- Define the {term}`metapackages <Metapackage>` such as `ubuntu-server` or
  `kubuntu-desktop`.
- Specify which packages are part of each image Ubuntu produces.
- Specify which snaps are part of those images.
- Specify which packages ship on install media to support offline installs.
- Define which packages are part of the `main` and `restricted` components
  -- the packages officially maintained and supported by the Ubuntu
  project.

A seed is a text file in -- for historical reasons -- an unusual format
reminiscent of `wikitext`. {ref}`seed-management` covers that format and the
process for changing a seed.

Sets of seeds are managed in git repositories. The canonical ones used to
do all the above things live in the
[ubuntu-seeds project in Launchpad](https://launchpad.net/ubuntu-seeds) and
have a branch per Ubuntu release. To read the current seeds without cloning
anything, the archive team publishes a copy of every collection at
[static-reports.ubuntu.com/seeds](https://static-reports.ubuntu.com/seeds/).

A core `platform` collection defines the fundamentals -- among them the
`required` seed, which lists the packages every Ubuntu system needs to function
at all. Each {term}`flavor <Ubuntu flavors>` of Ubuntu, including Ubuntu
itself, then maintains a seed collection of its own.

## Important seeds

Some important seeds, and what defines them (simplified; the current
collections are the source of truth):

* `required` (platform) -- defines the packages that have
  `Priority: required`.
  * The packages that must be present for the system to work at all -- in
    practice, the ones needed to install more packages.
  * Which packages get this priority is controlled in Launchpad;
    Archive admins use the {ref}`aa-priority-mismatches` report to keep
    the seed and the archive in sync.
* `minimal` (platform) -- defines the packages that have
  `Priority: important`.
  * The packages you would expect on any Unix system. Almost all Ubuntu
    systems have them; those not expected to have human users -- minimal
    cloud or server images, OCI containers -- do not.
* `boot` (platform) -- the default kernels and bootloaders for each
  architecture. Kept separate from minimal so `debootstrap` and the
  `*-minimal` metapackages don't pull them in.
* `standard` (platform) -- a small character-mode system on top of
  minimal, aimed at being a sensible foundation for a server or desktop
  install.
* `desktop-common` (platform) -- desktop infrastructure shared across
  flavors (audio, Bluetooth, input, printing, ...). Flavor collections
  then add their own desktop environment on top.
* `desktop` (all flavors) -- the desktop layer for the given flavor;
  GNOME for `ubuntu`, XFCE for `xubuntu`, etc.
* `server` (ubuntu) -- packages to install by default on Ubuntu Server.
* `ship-live` (all flavors) -- the packages to include in the pool on
  desktop install media to support offline installs.
* `server-ship-live` (ubuntu) -- like `ship-live` but for the server
  installer.
* `supported` (the last seed listed in `STRUCTURE`) -- everything Ubuntu
  commits to supporting. Germinate adds the full build-dependency closure
  here, and it also holds packages that are supported but not installed by
  default, including all the language packs.


### The supported seeds

`supported` is not a single list. It sits at the top of a family of
`supported-*` seeds in the `platform` collection, grouped by purpose --
hardware, installer, kernel, sysadmin, development and network tools, plus
per-product server stacks such as `supported-cloud`, `supported-openstack`,
`supported-maas` and `supported-landscape`. Three of them hold no packages of
their own and exist only to aggregate the rest: `supported-server`,
`supported-desktop`, and `supported-common` above both.

Many of these seeds carry a `-common`, `-desktop` or `-server` suffix. That
split was introduced so the archive could compute different LTS maintenance
windows for desktop and server packages, and publish the result as a
`Supported` field in the `Packages` file. **That machinery is retired.**

Treat this family as historical structure rather than a live taxonomy. Some of
these seeds hold only one or two packages, several list software that has long
since left the archive, and the collection contains a few `supported-*` files
that `STRUCTURE` does not reference at all. The collection's `STRUCTURE` file
is the only authority on which of them are live in a given release.


## Seed inheritance

Seeds are organized in an inheritance hierarchy, defined by the `STRUCTURE`
file in each seed collection: each line names a seed, followed after the
colon by the seeds it inherits from. Collections can also pull in other
collections with `include <collection>` lines, and set processing flags with
`feature <flag>` lines (for example `follow-recommends`, which treats
`Recommends` as `Depends`, or `no-follow-build-depends`). For example:

```none
include platform.resolute
desktop: desktop-minimal desktop-common
```

Each seed's own germinate output is *not* a superset of the seeds it
inherits from. If anything it is the reverse: a package already provided by an
inherited seed (or that seed's dependencies) is left out of this seed's own
output, so only newly-introduced packages appear. `desktop`'s output does not
include `desktop-minimal`'s packages, even though `desktop` inherits from it.

Getting the full set for `desktop` therefore means combining its output with
`desktop-minimal`'s and `desktop-common`'s yourself. The image layers described
in {ref}`how-seeds-are-used` do exactly that, combining several seeds' output
rather than reading one seed's file. {manpage}`germinate(1)` states the rule
directly: "If a package in the
desktop seed depends on 'foo', but 'foo' is already part of the minimal seed
or dependency list, then 'foo' will not be added to the desktop output."

A `!<package>` entry is a tripwire rather than a filter. It declares that the
package must not appear in that seed or in the seeds it inherits from. If
germinate finds it there anyway, it logs an error naming the seed that pulled it
in and then leaves the package out of that seed's output -- which can make the
output inconsistent, because other packages may still depend on it and `apt`
knows nothing about seed blocklists. The point is to make an unwanted inclusion
visible so that the package relationships can be fixed, not to work around them.

A collection may also carry a global `blacklist` file (`blocklist` since
germinate 2.48). Despite the name it excludes nothing; germinate only uses it to
annotate its `blocklisted` report with build-dependency source packages that
matched.

The {manpage}`germinate(1)` manual page documents the `STRUCTURE` file in full.

The hierarchy can be easier to take in as a picture than as a file. Every germinate
run writes a `structure.dot` alongside its other output, which `graphviz` will
render:

```bash
wget https://ubuntu-archive-team.ubuntu.com/germinate-output/ubuntu.resolute/structure.dot
dot -Tpng structure.dot -o structure.png
```


## Task headers in seed files

`STRUCTURE` is not the only thing that shapes the flavor metapackages. Seed
files may also begin with a block of `Task-*` headers:

```none
Task-Per-Derivative: 1
Task-Section: user
Task-Description: Edubuntu desktop
Task-Extended-Description: This task provides the full Edubuntu desktop environment.
Task-Key: edubuntu-desktop
Task-Metapackage: edubuntu-desktop
Task-Seeds: desktop-gnome-minimal
```

Only two of these affect metapackage generation. `germinate-update-metapackage`
reads them straight out of the seed text, separately from the `STRUCTURE`
inheritance machinery:

* `Task-Metapackage` -- the name of the metapackage to generate. Without it,
  germinate names the metapackage `<flavor>-<seed>`.
* `Task-Seeds` -- when germinate generates the metapackage for this seed,
  it unions the listed seeds' package lists (instead of just this seed's).
  This is a second, header-driven layer of inheritance in addition to the
  `STRUCTURE` inheritance.

The example above is Edubuntu's `desktop-gnome` seed. It produces an
`edubuntu-desktop` metapackage (rather than the default
`edubuntu-desktop-gnome`) whose dependencies cover both `desktop-gnome` and
`desktop-gnome-minimal`.

`Task-Seeds` is read for two further purposes. Germinate itself uses it to
decide which seeds count as generating the same task: when an entry lists
alternatives (`foo | bar`), germinate may promote the first alternative from
any lesser seed, but promotes the later ones only from these closely-allied
seeds. Outside germinate, the archive publisher's `generate-extra-overrides`
script -- part of the publisher's `finalize.d` hooks -- uses it, together with
`Task-Per-Derivative` and an optional `Task-Name`, to decide which seeds'
packages get the archive's `Task:` field. `livecd-rootfs`'s `expand-task`
reads the same three headers to decide which seeds' germinate output to
combine when building an image layer; see {ref}`how-seeds-are-used` below.
Neither of those two tools reads `Task-Metapackage`, and germinate never reads
`Task-Per-Derivative` or `Task-Name`.

The remaining headers -- `Task-Key`, `Task-Section`, `Task-Description`,
`Task-Extended-Description` -- match the fields of a Debian tasksel task
stanza, but nothing in germinate, `livecd-rootfs`, or the archive publisher
reads them, and Ubuntu's installers don't use tasksel. They are vestiges of
the "task" concept, which Debian still uses but Ubuntu does not.


(germinate)=
(how-seeds-are-used)=
## How seeds are used

The software that interprets seeds is called
[germinate](https://launchpad.net/germinate). Its core operation is to
"sprout" a seed -- a list of packages -- into a set that is closed under
dependencies. It can also be used to convert a seed's unusual input format
into something other tools can parse.

### Defining metapackages

Each flavor's seeds are turned into an installable
{term}`metapackage <Metapackage>` (`ubuntu-desktop`, `kubuntu-desktop`, and so
on) by that flavor's `<flavor>-meta` source package (for example `ubuntu-meta`
or `kubuntu-meta`). The `Task-*` headers described above determine which seed
feeds which metapackage, and its dependency list comes from germinating that
seed.

See {ref}`seed-management` for how a `<flavor>-meta` package is regenerated
and uploaded after a seed change.

### Package and snap selection at image build time

Image builds are driven by the
[livecd-rootfs](https://git.launchpad.net/livecd-rootfs) package.

When building images for a particular flavor, `livecd-rootfs` downloads that
flavor's seeds and runs `germinate` on them. The build process then uses
the result of this to know which packages and snaps to include in
which part of the image.

A preinstalled image -- WSL, or a cloud image -- has only one "part".
Installer images have layers instead: `minimal`, `standard` and `live` for
desktop, each drawing on different seeds.

### Building the package pool for offline installs

Some images carry a pool of `.deb` files on the install media itself, so that
an installation with no network access can still offer those packages. The
`ship-live` seed -- or `server-ship-live` for the server installer -- lists
what goes into that pool. These packages ship on the media without being
installed by default.

### Defining main and restricted

Germinating the `ubuntu` seed collection -- which pulls in `platform` through
its `include` line -- defines which packages Ubuntu supports. Everything in the
resulting `all` output list is supported: every seed's own packages, their
dependencies, and the build-dependency closure. Everything else is not.

The seeds decide *whether* a package is supported, not *which* of the two
supported components it lands in. Germinate produces a single `all` list with
no `main`/`restricted` distinction; that split is a licensing question, and the
package's existing component has already answered it. A supported package that
is free software belongs in `main`, one that is not belongs in `restricted`.
Promotions run along that axis -- `universe` to `main`, `multiverse` to
`restricted` -- which is why {ref}`Main Inclusion Review
<main-inclusion-review>` covers both.

Seeding a package does not move it. The
{ref}`component-mismatches <aa-component-mismatches>` tool reports the
difference between what the seeds expect and what the Archive actually says --
listing movements to `main` and to `restricted` separately -- and Archive
Administrators review and process those mismatches by hand.

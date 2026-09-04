(seed-management)=
# Seed management

Seeds are the lists of packages that define what goes into the archive's
`main` and `restricted` components and onto the installation images. They are
plain text files, kept in the
[ubuntu-seeds project](https://launchpad.net/ubuntu-seeds) on Launchpad. This
article covers how to change them; for what they are and how they are used,
see {ref}`seeds`.


## Where the seeds live

Each seed collection is a separate git repository, and each repository is owned
by the team responsible for that collection rather than by one central team:

| Collection | Owning team |
| --- | --- |
| `platform`, `ubuntu`, `ubuntu-core`, `i386` | `~ubuntu-core-dev` |
| `edubuntu`, `kubuntu`, `xubuntu`, `ubuntustudio`, `lubuntu`, `ubuntu-mate`, `ubuntucinnamon` | `~<collection>-dev` |
| `ubuntu-budgie` | `~ubuntubudgie-dev` |
| `ubuntukylin` | `~ubuntukylin-members` |
| `ubuntu-unity` | `~unity7maintainers` |

The repository URL follows from the collection and its owning team, and each
release has its own branch, named after the series:

```none
https://git.launchpad.net/~<team>/ubuntu-seeds/+git/<collection>
```

Make sure you work on the branch for the release you want to modify. Most of
the time this will be the development release.

The `platform` and `ubuntu` seeds define which packages Ubuntu supports, so
adding a package to these seeds requires it to be in `main` (or `restricted`,
if its licensing keeps it out of `main`). If it is not already, you must go
through the {ref}`Main Inclusion Review <main-inclusion-review>` process for
the package first -- that process covers `universe` to `main` and `multiverse`
to `restricted` alike.

Adding a package that is already in `main` or `restricted` to these seeds, or
to another flavor's seed, does not have this constraint.


## Editing a seed

The syntax of seed files is documented in the
{manpage}`germinate manual page <germinate(1)>`.

A minimized version of a real seed, Ubuntu Studio's `graphics`:

```none
Task-Per-Derivative: 1
Task-Description: 2D/3D creation and editing suite

 * agave                 # A dependency
 * (blender)             # Parentheses mean a recommend
 * !gphoto2              # Must not appear in this seed (see below)
 * (darktable) [amd64]   # Only on amd64
 * foo | bar             # Alternatives
 * %libreoffice          # Every binary from the libreoffice source package
 * snap:firefox          # A snap rather than a deb

 * ubuntustudio-graphics # Metapackage for everything here.
```

Real seeds carry more `Task-*` headers than this, `Task-Key` and `Task-Section`
among them. Only some of them do anything; {ref}`seeds` explains which.

The `!package` form is a tripwire, not a way to keep a package out of an image.
It declares that the package must not appear in this seed or in the seeds this
one inherits from; if germinate finds it there anyway it logs an error and drops
the package, which can leave the output uninstallable, because whatever pulled
the package in still depends on it. Use it to make an unwanted inclusion
visible so the dependency can be fixed, and use it sparingly.

The global `blacklist` file some collections carry (`blocklist` since germinate
2.48) excludes nothing at all. Germinate uses it only to annotate a report.


## Submitting a seed change

Seed changes normally go through a merge proposal, even from developers who
have commit rights on the repository, so that the change gets reviewed by the
team that owns the collection. Push your branch to a personal fork and propose
it for merging into the branch for the target series; see
{ref}`how-to-submit-a-merge-proposal`. If you are not a member of the owning
team you will also need someone who is to review and merge it, which works the
same way as {ref}`finding a sponsor for an upload <how-to-find-a-sponsor>`.

Refer to the Launchpad bug number in the commit message. If there is not a bug
yet, create one with a verbose description of the reason for the change; it will
help make the change clear further down the road.

Changing the seeds does not automatically move packages to a new component in
the Archive; see the
[MIR queue](https://bugs.launchpad.net/~ubuntu-mir/+subscribedbugs).

If a `<flavor>-meta` source package builds a
{term}`metapackage <Metapackage>` for the seed you changed, also follow
{ref}`updating-a-metapackage` below, once your change has reached the public
seed mirror.


(updating-a-metapackage)=
## Updating a metapackage

Changing a seed does not by itself update the corresponding
{term}`metapackage <Metapackage>` (`ubuntu-desktop`, `kubuntu-desktop`, and so
on); that requires a separate upload of the flavor's `<flavor>-meta` source
package (`ubuntu-meta`, `kubuntu-meta`, `xubuntu-meta`, and so on).

Your seed change has to reach the public mirror first, which can take from a few
minutes to an hour or so. Then, in a checkout of the relevant `<flavor>-meta`
package, run the `update` script.

`update` checks that `devscripts`, `debootstrap` and `germinate` are installed
and then hands over to `germinate-update-metapackage --vcs`, from the germinate
source package. That reads its settings from the checked-in `update.cfg` and
refreshes three things: the `<seed>-<arch>` files, the
`<seed>-recommends-<arch>` files, and `metapackage-map`, which maps each seed
name to its metapackage name. Commit the refreshed files and upload the new
`<flavor>-meta` revision to the Archive.

`debian/control` in `<flavor>-meta` is hand-maintained, not regenerated by
`update`: it declares `${germinate:Depends}` / `${germinate:Recommends}`
tokens, which `dh_germinate_metapackage` substitutes at build time using the
checked-in `metapackage-map` and the `<seed>-<arch>` /
`<seed>-recommends-<arch>` files from the most recent `update` run.


## Debugging seed problems

Sometimes a package is pulled into an image, or turns up on the
{ref}`component-mismatches <aa-component-mismatches>` report, and it is not
obvious why. Everything you need to answer that is in the seeds and the
germinate output; it is just buried under a layer of dependency expansion.


### Where the output lives

The germinate output for all flavors is published at
[ubuntu-archive-team.ubuntu.com/germinate-output](https://ubuntu-archive-team.ubuntu.com/germinate-output/),
in directories named `<collection>.<series>` -- for example
`ubuntu.resolute/`.

Each run covers a single architecture: `amd64` for every collection except the
`i386.*` ones, which cover `i386`. Each run resolves dependencies against the
release and `-updates` pockets of all four components. A package pulled in only
on another architecture will not show up there; to see that one you have to
{ref}`run germinate yourself <running-germinate-yourself>`.


### What the output files are

Germinate writes a group of files per seed, plus a handful that describe the
run as a whole. The ones worth knowing:

| File | Contents |
| --- | --- |
| `<seed>` | The seed's packages *and* everything they drag in. This is the one you usually want. |
| `<seed>.seed` | Only the entries written in the seed file itself. |
| `<seed>.depends` | Only the packages pulled in as dependencies. |
| `<seed>.build-depends` | Packages reached by following build-dependencies. |
| `<seed>.sources` / `.build-sources` | The corresponding source packages. |
| `<seed>.snaps` | Snaps seeded for this seed. |
| `<seed>.seedtext` | The raw text of the seed, as germinate read it. |
| `all` | Every package in every seed -- what defines the supported set. |
| `all+extra` | `all`, plus binaries built by a supported source but not themselves seeded. |
| `<supported>+build-depends` | The supported seed plus every seed's build-dependencies. |
| `provides` | Virtual packages and what provides them. |
| `structure`, `structure.dot` | The inheritance hierarchy, as text and as a `graphviz` graph. |
| `blocklisted` | Build-dependency sources matched by the global blocklist file (still named `blacklisted` wherever germinate is older than 2.48). |
| `rdepends/ALL/<package>` | The reverse-dependency tree for one package. |
| `_germinate_output` | The log of the run itself -- usually the fastest way to an answer. See below. |

The per-seed lists are tables, with the package, its source, and a `Why` column
naming whatever caused it to be included:

```none
Package             | Source          | Why
--------------------+-----------------+-------------------------
accountsservice     | accountsservice | language-selector-common
```

Watch out for `all`, `all+extra`, `provides`, `structure`, `blocklisted` and
`extra`: these are not seeds, so they match a search for a package name without
telling you anything about how it got seeded.


### Finding out why a package is there

1. **Find which seeds contain it.** Grep the whole directory, discarding the
   files that are not seeds:

   ```bash
   grep -l '^exim4' * | grep -vE '^(all|all\+extra|provides|structure|blocklisted|extra)$'
   ```

2. **Read the `Why` column** in the seed lists that matched. That names the one
   package that caused the inclusion, which is often enough.

3. **Read the log.** `_germinate_output` records each resolution decision as it
   is made, and it is far more informative than the lists. Search it for
   `Resolving <seed> dependencies ...` to find the section for the seed you
   care about. Two prefixes matter:

   ```none
   * Chose gawk out of awk to satisfy base-files
   ! Promoted cloud-guest-utils from cloud-minimal to server-cloud-minimal to satisfy cloud-init-base
   ```

   `* Chose` means germinate picked one of several alternatives. `! Promoted`
   means it pulled a package *up* out of a seed it already belonged to, in
   order to satisfy something in a seed that inherits from it -- which is the
   usual explanation for a package appearing somewhere unexpected. `?` marks an
   error, such as a blocklisted package that was seeded anyway.

   The fix is often in the package relationships rather than the seeds. A bare
   `Recommends: mail-transport-agent` lets germinate pick any provider, and it
   may pick a heavy one; `Recommends: postfix | mail-transport-agent` states a
   preference while still accepting alternatives.

4. **Follow the chain.** More than one dependency arc is usually involved, and
   the log does not always spell out all of them. `rdepends/ALL/<package>`
   gives the full reverse-dependency tree, annotated with the seeds each
   package belongs to:

   ```none
   gawk
   * Reverse Depends:
    +- auditd
    |  * Supported seed
    |  * Reverse Depends:
    |   +- audispd-plugins
    |      * Extra seed
   ```


(running-germinate-yourself)=
### Running germinate yourself

Run germinate yourself to look at an architecture other than the published one,
or to test a seed change before proposing it.

Clone the seeds, then germinate against the local checkout:

```bash
mkdir -p ~/seeds && cd ~/seeds
git clone -b resolute https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/platform platform.resolute
git clone -b resolute https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/ubuntu ubuntu.resolute

mkdir -p ~/germinate-run && cd ~/germinate-run
germinate -S file://$HOME/seeds/ -s ubuntu.resolute \
    -m http://archive.ubuntu.com/ubuntu/ \
    -d resolute,resolute-updates \
    -a arm64 \
    -c main,restricted
```

The options, in order:

`-S`
: Where to fetch seed collections from. `file://` reads the local checkout;
  drop it entirely to use the published seed mirror.

`-s`
: The collection to germinate, as `<collection>.<series>`. Pulls in any
  collection named by an `include` line -- here, `platform.resolute`, which is
  why it had to be cloned too.

`-m`
: The archive mirror to resolve against. Use `http://ports.ubuntu.com/ubuntu-ports/`
  for architectures that are not `amd64` or `i386`.

`-d`
: Which suites to resolve against, comma-separated. Include `-updates` to match
  what the published runs do.

`-a`
: The architecture -- usually the reason for running germinate by hand.

`-c`
: Which components to consider. Restrict this to `main,restricted` to see what
  would happen if a package were not available in `universe`.

Germinate writes its output into the current directory, so run it somewhere
empty. `-v` gives a more verbose log; `--no-rdepends` skips building the
reverse-dependency tree, which is the slowest part of a run.

For a working reference, the archive team's own invocation lives in
[`update-one-germinate`](https://git.launchpad.net/ubuntu-archive-scripts/tree/update-one-germinate)
in `lp:ubuntu-archive-scripts`.

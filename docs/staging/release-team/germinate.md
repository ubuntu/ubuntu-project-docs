(germinate)=
# Germinate

```{note}
Page source: [Germinate](https://wiki.ubuntu.com/Germinate)

Will move to:
* How Ubuntu is made -> concepts
```

```{admonition} **Seed management** series
The article series explains seeds and how they are used.

Seeds overview:
: {ref}`seeds`

Related topics:
: {ref}`germinate` (this article)

Practical guidance:
: {ref}`seed-management`
```

Germinate is a package available in Debian and Ubuntu which starts with lists of
packages (called seeds) and grows them into a full list of packages including
dependencies and (in additional lists) suggests, recommends, and sources for
each of these lists.


(seed-management-graphs)=
## Graph of seed structure

Germinate was modified so that it produces a `structure.dot` file which can be
used to produce a graph of the seeds structure using `graphviz`. This can be
useful to figure how the seed are overall linked:

```bash
wget http://people.canonical.com/~ubuntu-archive/germinate-output/ubuntu.precise/structure.dot
dot -Tpng structure.dot > structure.png
```

## Files you need

The minimum set of seeds this author has used is:

* STRUCTURE
* required
* minimal
* standard
* custom
* blocklist
* supported

It might be possible to exclude some of these (the full set of seeds for Ubuntu
is much larger), but this set works and at least some of these are hard-coded
into germinate.

Each required seed is a file that must exist. However any file you don't
actually want to use may be an empty file (e.g. created with `touch filename`).

## Special Files

*STRUCTURE* is special in that it is not actually a list of packages. Rather it
is the list of seeds and how they depend on each other.

An example STRUCTURE is:

```
required:
minimal: required
standard: required minimal
custom:
blocklist:
supported:
```

The first thing on each line is the name of a seed followed by a colon. For any
seed list so defined, a file of the same name must exist in the same directory
as the STRUCTURE file.

After the colon is a space and a space-separated list of seeds the first seed
on the line depends on. This is used in generating the output such that each
seed has a corresponding output list of packages which includes the packages
and depends in the seed itself, plus any packages and dependencies for the
seeds listed as dependencies for the seed (recursively).

*blocklist* is also special in that it doesn't define a list of packages to
include. Instead it lists packages which will never be included in the output
of `germinate`.

## Seed lists

For each seed you actually use, list each package you want to include on line
in wiki bullet list format. E.g.

```
 * packagename
```

If you wish, you can use some additional wiki formatting for header and text.
Anything that is not a bullet item (i.e. package to include), is ignored by
`germinate`, but could be useful if you want to use a wiki to group-edit the
lists.

## Invoke germinate

```{note}
This bold text pointing to the manpage was present on the original wiki page.
Please determine what is the correct approach, and make sure that is reflected
here (to avoid confusion). If it's a versioning issue, let us know!
```
**It is probably best to refer to the [manual page](https://manpages.ubuntu.com/manpages/questing/en/man1/germinate.1.html) instead and ignore the following.**

Grab the seeds that you need:
```bash
mkdir -p /home/user/projects/seeds
cd /home/user/projects/seeds
bzr branch lp:~ubuntu-core-dev/ubuntu-seeds/platform.hardy
bzr branch lp:~ubuntu-core-dev/ubuntu-seeds/ubuntu.hardy
```

Now that you have your seeds in the directory
`/home/user/projects/seeds/ubuntu.hardy` and you are currently in
`/home/user/projects`, you would use the following command to generate the output
files (in `/home/user/projects`):

```bash
germinate -S file:///home/user/projects/seeds/ -s ubuntu.hardy -m http://archive.ubuntu.com/ubuntu/ -d hardy,hardy-updates -a i386 -c main,restricted,universe,multiverse
```

* `-S file:///home/user/projects/seeds/` is the URL of the seeds and can by any
  and may be local or remote (e.g. `http://` instead of `file://`)
* `-s ubuntu.hardy` is the name of the sub-directory of the seeds URL for the
  distribution we are working on. Often named (as here) by the distribution the
  seeds are intended to be used with.
* `-m http://archive.ubuntu.com/ubuntu/` is the mirror containing the
  `Packages.gz` and `Sources.gz` files (usually any valid Ubuntu mirror)
* `-d hardy,hardy-updates` is the comma-separated list of distributions for
  which to find dependencies. Can be a single distribution (`no ,`) or any list
  of distribution names available on the mirror
* `-a i386` is the architecture to generate output for (in this case, i386)
* `-c main,restricted,universe,multiverse` is the comma-separated set of
  distribution components to generate output for. May be only one, or anything
  the mirror supports.

## Output

* A file named the same as the seed, for each seed, which contains the packages
  and required dependencies for those packages
* Files named `filename.seed-recommends`, `filename.build-depends` and
  `filename.build-sources` where filename is the seed list filename and the files
  list the packages (and dependencies) which the APT understands as the
  recommends, build-depends, and build-sources (sources plus depends and
  build-depends sources) for the packages in the seed, respectively.
* There are also files named `all` and `all.sources` which list all packages in
  all the other output lists and their source packages
* Packages resulting from following build-dependencies and their dependencies
  are added to the output for the last seed file in the STRUCTURE file, which is
  called supported.
* Other files are also generated. See the README if you want to know about them.

## Source code

Germinate, the program that processes seeds and expands out their dependencies,
is also available in git:

```bash
git clone https://git.launchpad.net/germinate
```


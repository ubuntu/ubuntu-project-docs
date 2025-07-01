(germinate)=
# About Germinate

Germinate is a package available in Debian and Ubuntu which starts with lists of
packages (called seeds) and grows them into a full list of packages including
dependencies and (in additional lists) suggests, recommends, and sources for
each of these lists.

For instructions on using `germinate`, refer to the
{manpage}`germinate manual page <germinate(1)>`.


## Files you need

The minimum set of seeds is:

* `STRUCTURE`
* `required`
* `minimal`
* `standard`
* `custom`
* `blocklist`
* `supported`

It might be possible to exclude some of these (the full set of seeds for Ubuntu
is much larger), but this set works and at least some of these are hard-coded
into `germinate`.

Each required seed is a file that must exist. However, placeholders (empty
files) can be created for any files you don't want to use.


## The STRUCTURE file

`STRUCTURE` is special in that it is not actually a list of packages. Rather it
is the list of seeds and how they depend on each other.

An example `STRUCTURE` is:

```none
required:
minimal: required
standard: required minimal
custom:
blocklist:
supported:
```

The first thing on each line is the name of a seed followed by a colon. For any
seed list so defined, a file of the same name must exist in the same directory
as the `STRUCTURE` file.

After the colon is a space and a space-separated list of seeds the first seed
on the line depends on. This is used in generating the output such that each
seed has a corresponding output list of packages which includes the packages
and depends in the seed itself, plus any packages and dependencies for the
seeds listed as dependencies for the seed (recursively).


## The blocklist file

`blocklist` is also special in that it doesn't define a list of packages to
include. Instead it lists packages that will never be included in the output
of `germinate`.


## Seed lists

For each seed used, each package is listed on separate lines in wiki bullet
list format. E.g.

```none
 * packagename
```

Items bulleted in this way are assumed to be packages that should be included.
Anything that is not a bullet list item is ignored by `germinate`, which means
additional wiki formatting can be used for headers and text.


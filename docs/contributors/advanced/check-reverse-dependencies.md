(check-reverse-dependencies)=
# Checking reverse dependencies

You usually want to check reverse dependencies to avoid causing:

* Installation issues by something having a dependency on the produced
  binaries.

* Fail to build due to missing dependencies, for a package that builds depends
  on a produced binary.

There are many ways to check for reverse dependencies, with different pros and
cons. The following list gets gradually more complete, but also takes longer
and is sometimes harder to set up.


## `reverse-depends`

The most common and most widely used tool, even fine for normal cases is
`reverse-depends` from the package `ubuntu-dev-tools`. Quick and helpful, but
not always fully complete.


## `apt-cache rdepends`

The other two tools check the current state of a release. To instead inspect a
particular system configuration one would tend to use `apt-cache rdepends`
instead.


## `checkrdepends`

We've had cases where the other tools struggled to follow virtual dependencies
or the rust ecosystem's use of `provides` in build dependencies. So far
`checkrdepends` from `ubuntu-archive-tools` seems to cover this the best.

We recommend at least:

* Using `archive-base` to not require a local mirror.

* Using `--include-provides` to also check if we might make things un-buildable.

Example:

```none
./checkrdepends --no-ports --include-provides --suite plucky --archive-base 'http://archive.ubuntu.com/ubuntu' debian-pan debian-astro
```


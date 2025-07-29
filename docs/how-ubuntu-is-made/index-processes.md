(process-overviews)=
# Process overviews

High-level overviews of the various processes used in the building of Ubuntu, how they work, and who's involved.


## Ubuntu release cycle

The processes that together make up the bulk of the work on the creation of Ubuntu are mostly tied to various phases of distribution's release cycle.

```{toctree}
:maxdepth: 1

processes/release-cycle
processes/freezes
```


## Archive processes

For the most part, development work on the distribution revolves around getting packages to build and adding them to the Archive.


### Basic archive management and maintenance

Getting new versions of packages from Debian, dealing with build dependencies, and resolving build and test failures.

```{toctree}
:maxdepth: 1

processes/merges-and-syncs
processes/transitions
processes/proposed-migrations
processes/backports
```


### Contributor support

Allowing developers without Archive upload rights to submit their patches or new packages for review.

```{toctree}
:maxdepth: 1

processes/sponsorship
```


### Inclusion gatekeeping

Special review processes and quality safeguards for adding updates to published releases, and to the officially supported sets of packages.

```{toctree}
:maxdepth: 1

processes/stable-release-updates
/MIR/main-inclusion-review
```

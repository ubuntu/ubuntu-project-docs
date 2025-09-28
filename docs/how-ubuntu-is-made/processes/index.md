(process-overviews)=
# Process overviews

High-level overviews of the various processes used in the building of Ubuntu, how they work, and who's involved.


## Ubuntu release cycle

The processes that together make up the bulk of the work on the creation of Ubuntu are mostly tied to various phases of distribution's release cycle.

```{toctree}
:maxdepth: 1

/release-team/release-cycle
/release-team/freezes
/release-team/freeze-exceptions
```


## Archive processes

For the most part, development work on the distribution revolves around getting packages to build and adding them to the Archive.


### Archive management and maintenance

Getting new versions of packages from Debian, dealing with build dependencies, and resolving build and test failures.

```{toctree}
:maxdepth: 1

merges-and-syncs
transitions
backports
automatic-package-testing-autopkgtest
```


### Contributor support

Allowing developers without Archive upload rights to submit their patches or new packages for review.

```{toctree}
:maxdepth: 1

sponsorship
```


#### Proposed migration

The process of moving (uploaded or merged) packages from the `-proposed` {term}`pocket` to the `-release` pocket to make them available to users:

```{toctree}
:maxdepth: 1

proposed-migration/index
```

Automatic migration may be blocked for many different reasons. The following article series explains the various migration failures:

* {ref}`issues-preventing-migration`
* {ref}`autopkgtest-regressions`
* {ref}`failure-to-build-from-source-ftbfs`
* {ref}`special-migration-cases`


### Inclusion gatekeeping

Special review processes and quality safeguards for adding updates to published releases, and to the officially supported sets of packages.

```{toctree}
:maxdepth: 1

stable-release-updates
/MIR/main-inclusion-review
```

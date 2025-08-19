(failure-to-build-from-source-ftbfs)=
# Failure to Build From Source (FTBFS)

A package has to be buildable to be able to migrate from the `-proposed` to `-release` {term}`pocket`. This article describes a number of common reasons why a package build may fail.

:::{admonition} **Proposed migration** series
The {ref}`proposed-migration` article series explains the various migration failures and ways of investigating them.

Process overview:
: {ref}`proposed-migration`

Practical guidance:
: {ref}`resolve-a-migration-issue`

Issue types:
:   * {ref}`failure-to-build-from-source-ftbfs` (this article)
    * {ref}`autopkgtest-regressions`
    * {ref}`issues-preventing-migration`
    * {ref}`special-migration-cases`
:::

General classes of problems during the build step:

{ref}`normal-build-issues`
: Locally reproducible build problems (that should have been addressed before uploading).

{ref}`platform-specific-issues`
: Issues that may have been overlooked due to being present only on unfamiliar hardware.

{ref}`intermittent-problems`
: Temporary network or framework problems that require retrying the build.

{ref}`dependency-problems`
: Requiring adding the right version of some other package to the `-release` pocket.

{ref}`abi-changes`
: {term}`ABI` changes with dependencies; often requiring a no-change rebuild.

{ref}`package-specific-issues`
: Other package-specific build problems that usually require a tweak to the package itself.


(normal-build-issues)=
## Normal build issues

All the normal build issues, such as syntax errors. In practice, these are rare because developers are usually diligent in making sure their packages build before uploading them. Fixes for these is standard development work.


(platform-specific-issues)=
## Platform-specific issues

Normal build issues that arise only on specific platforms. Common situations:

* Tests or code that rely on [endianness](https://en.wikipedia.org/wiki/Endianness) of data types, and so break on big-endian systems (e.g. s390x).
* Code expecting 64-bit data types that breaks on 32-bit (e.g. armhf).

{term}`Canonistack` provides hardware for Canonical employees to reproduce these problems.

```{note}
i386 in particular fails less due to data type issues, but more because it is a partial port and has numerous limitations that require special handling, as described on the {ref}`i386 troubleshooting page <aa-i386>`.
```


(intermittent-problems)=
## Intermittent problems

Local building is fine, but the uploaded build may have failed on Launchpad due to a transitory issue. For example:

* Network outage, a race condition, or other stressed resource.
* A strange dependence on some variable, such as the day of the week.

In these cases, clicking on {guilabel}`Retry Build` button in Launchpad once or twice can sometimes cause the build to randomly succeed, thus allowing the transition to proceed (if you're not yet a Core Dev, ask for a Core Dev in the
{matrix}`devel` Matrix channel to click the link for you).

To make the build process robust and predictable, try to identify the cause (especially if it's a recurring problem) find a way to fix it properly.


(dependency-problems)=
## Dependency problems

When a dependency is not the right version or is not present in the right {term}`pocket`, investigate what is wrong with the dependency, and fix it.

Keep in mind that in some situations, the problem is the definition of dependency itself. The solution then might be:

* Change the version of the dependency.
* Adjust the dependency version requirement.
* Remove invalid binary packages.
* Or similar.

Removing packages often requires asking an Archive Admin for help in the {matrix}`release` Matrix channel.


(abi-changes)=
## ABI changes

ABI changes tend to arise when Ubuntu is introducing new versions of toolchains, language runtime environments, or core libraries (i.e. new `glibc`, `gcc`, `glib2.0`, `ruby`, `python3`, `phpunit`, etc.).

This happens when the release of the underlying libraries or toolchains is newer than the project that uses it. A package may fail to build because, for example, one of its dependencies is built:

* Against a different version of `glibc`.
* With less strict `gcc` options (check [Ubuntu Defaults](https://wiki.ubuntu.com/ToolChain/CompilerFlags#Notes)).

Such cases need a (no-change) rebuild (and/or patching) to build with the new version or stricter options.

If upstream has already adapted to the changed behavior **and** produced a release:
: * If we already have the release in Ubuntu, try a no-change rebuild.

  * If we don't have the release, sync or merge it, or add the new changes in a patch on top of the release that's in Ubuntu.

If upstream has not *released* the changes:
: Consider packaging a snapshot of their Git repository.

If upstream has *not yet made* the changes, and there no existing bug reports or pull requests yet:
: We may need to make the changes in Ubuntu. Communicate with Debian and upstream, and if leads nowhere, file bug reports.

:::{note}
With ABI changes, these updates often cause the same kind of errors in many places. Ask in the {matrix}`devel` Matrix channel to check whether standard solutions are already known that you can reuse. Such solutions can include:

* Ignoring a new warning using the `-W...` option.
* Switching to the old behavior using the `-f...` option.

Report your findings, so others can reuse them when they run into more cases.


(package-specific-issues)=
## Package-specific issues

There are a myriad of other problems that can result in build failures. Many of these are package-specific or situation-specific. Remember to update this documentation when you encounter new situations that occur frequently.

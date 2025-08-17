---
orphan: true
---

(failure-to-build-from-source-ftbfs)=
# Failure to Build From Source (FTBFS)

A package has to be buildable top be able to migrate from the `-proposed` to `-release` {term}`pocket`. This article describes a number of common reasons why a package build may fail.

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

The first case covers all the usual normal build issues like syntax errors and
so on. In practice these tend to be quite rare, since developers tend to be
very diligent in making sure their packages build before uploading them. Fixes
for these is standard development work.


(platform-specific-issues)=
## Platform-specific issues

The second case is similar to the first but pertains to issues that arise only
on specific platforms. Common situations are tests or code that relies on
[endianness](https://en.wikipedia.org/wiki/Endianness) of data types, and so
breaks on big-endian systems (e.g. s390x), code expecting 64-bit data types that
breaks on 32-bit (e.g. armhf), and so on.

{term}`Canonistack` provides hardware for Canonical employees to use to try and reproduce these problems.

```{note}
i386 in particular fails less due to data type issues, but more because it is
a partial port and has numerous limitations that require special handling, as
described on the {ref}`i386 troubleshooting page <aa-i386>`.
```


(intermittent-problems)=
## Intermittent problems

In the third case, local building was fine but the uploaded build may have
failed on Launchpad due to a transitory issue such as a network outage, or a
race condition, or other stressed resource. Alternatively, it might have failed
due to a strange dependence on some variable like the day of the week.

In these cases, clicking on the "Retry Build" button in Launchpad once or twice
can sometimes cause the build to randomly succeed, thus allowing the transition
to proceed (if you're not yet a Core Dev, ask for a Core Dev on the
`#ubuntu-devel` IRC channel to click the link for you).

Needless to say, we want the build process to be robust and predictable. If the
problem is a recurring one, and you are able to narrow down the cause, it can
be worthwhile to find the root cause and figure out how to fix it properly.


(dependency-problems)=
## Dependency problems

For the fourth case, where a dependency is not the right version or is not
present in the right pocket, the question becomes one of identifying what's
wrong with the dependency and fixing it.

Be aware there may be some situations where the problem really is with the
dependency itself. The solution then might be to change the version of the
dependency, or adjust the dependency version requirement, or remove invalid
binary packages, or so forth. The latter solutions often require asking an
Archive Admin for help on the `#ubuntu-release` IRC channel.


(abi-changes)=
## ABI changes

The fifth case, of ABI changes, tends to come up when Ubuntu is introducing new
versions of toolchains, language runtime environments or core libraries (i.e.
new `glibc`, `gcc`, `glib2.0`, `ruby`, `python3`, `phpunit`, etc).

This happens when the release of the underlying libraries/toolchains is newer
than the project that uses it. Your package may fail to build because, for
example, one of its dependencies was built against a different version of
`glibc`, or with less strict `gcc` options (the
[Ubuntu Defaults](https://wiki.ubuntu.com/ToolChain/CompilerFlags#Notes) can be
checked here) etc, and it needs a (no-change) rebuild (and/or patched) to build
with the new version or stricter options.

Assuming the upstream project has already adapted to the changed behavior or
function-prototypes **and** produced a release, then:

* If we already have the release in Ubuntu a simple no-change rebuild may
  suffice.

* If we don't have the release, then it will need a sync or merge, or patching
  in the changes to what we're carrying.

If upstream has not *released* the changes, then you could also consider
packaging a snapshot of their git repository.

If upstream has *not yet made* the changes, and there no existing bug reports or
pull requests yet, it may be necessary to make the changes on our end.
Communication with Debian and upstream can be effective here, and where it
isn't, filing bug reports can be worth the effort.

It's worth noting that with ABI changes, these updates often cause the same kind
of errors in many places. It's worth asking in the `#ubuntu-devel` IRC channel
in case standard solutions are already known that you can re-use, such as
ignoring a new warning via a `-W...` option or switching to the old behavior
via a `-f...` option. It's also worth reporting your findings in ways others can
easily re-use when they run into more cases.


(package-specific-issues)=
## Package-specific issues

Finally, there are a myriad of other problems that can result in build
failures. Many of these will be package-specific or situation-specific. As you
run into situations that crop up more frequently than a couple of times please
update these docs.

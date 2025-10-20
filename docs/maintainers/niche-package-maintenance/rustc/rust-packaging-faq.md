(rust-packaging-faq)=
# Rust Packaging FAQ

You may want to start by reading the [Debian Rust Packaging Policy document](https://wiki.debian.org/Teams/RustPackaging/Policy).
The goal of this FAQ is to collect information in a single place without too many overwhelming details, but the policy document should be the source of truth as things change over time or if anything here is unclear.

## How do Debian maintainers package Rust tooling and applications in general?

Debian includes all of the standard Rust tooling in their archive, including [`rustc`](https://packages.debian.org/rustc) and [`cargo`](https://packages.debian.org/cargo).
Their [Rust developer documentation](https://wiki.debian.org/Rust) recommends these packages mainly as tools to package other crates for Debian, and instead recommends the [`rustup`](https://packages.debian.org/rustup) package to install toolchains.

The code that builds the Rust crate packages [lives in monorepo](https://salsa.debian.org/rust-team/debcargo-conf).
Besides the package definitions, it also contains helper scripts for basic development and policy tasks, such as creating tickets, filtering the packages, finding outdated packages, and tracking crates that are intentionally excluded from the archive.

That repo makes heavy use of a tool called [`debcargo`](https://salsa.debian.org/rust-team/debcargo/), written in Rust, which extends the typical Debian tooling ecosystem with some Rust-specific workflows.
It has a number of features, but fundamentally it downloads crates, tries to parse metadata from them, determines the transitive dependencies, maps those to candidate Debian packages, and then lays out a starter package structure.

From there, packaging processes vary depending on the software being packaged, discussed below.
For more information about tooling, see [this separate question](#debian-rust-tools).

## How does Ubuntu differ from Debian with respect to Rust packages?

First, you should be familiar with the [process that Ubuntu goes through to merge and sync packages from Debian](#key-concepts).
Additionally, it's worth noting that the preferred workflow for Rust developers is the [`rustup` Snap package](https://snapcraft.io/rustup).
Like with Debian, the system packages are primarily intended to ensure the availability of Rust within Ubuntu itself, which is less directly relevant to application developers.

Due to the merge and sync process, the overwhelming number of Rust packages are imported directly from Debian.
The relatively small number of packages that carry an Ubuntu diff can be spotted by checking [Merge-o-Matic](https://merges.ubuntu.com/).
This can also be determined for an individual package by simply checking for the presence of `ubuntu` in the version string.
Ubuntu diffs exist for a number of reasons, such as dependency issues to support [Ubuntu's oxidation efforts](https://discourse.ubuntu.com/t/carefully-but-purposefully-oxidising-ubuntu/56995), hardware support, or other Ubuntu-specific integration issues.

There are also a small number of packages that are excluded from the sync for various technical reasons, usually dependencies that are unsatisfiable.  That configuration is handled via [this Launchpad repo](https://git.launchpad.net/~ubuntu-archive/+git/sync-blocklist).

While the number of packages that differ from Debian is small, some of them are critically important.
Notably, the `rustc` source package is one which carries a nontrivial diff compared to Debian, and that source package is responsible for generating a number of important binary packages, including: `rustc`, `cargo`, `libstd-rust-X.Y`, and more.
It's not reasonable to enumerate every difference here, but fundamentally they stem from the desire to ship more versions of the compiler in Ubuntu than Debian currently packages.

Debian's version of `rustc` is frozen for the lifetime of each stable Debian release.
Ubuntu, on the other hand, uses versioned packages which are frequently backported to LTS releases in order to support more software.
Whereas Debian features a single `rustc` binary package, Ubuntu releases typically have multiple with the version information contained directly in the name of the package, e.g. `rustc-X.Y`.
Ubuntu then also produces a simply named `rustc` package which corresponds to the default version of Rust for that release.

Because Ubuntu produces Rust compiler packages that don't exist on Debian, they necessarily contain a different set of patches and build scripts.

## What do Debian and Ubuntu maintainers change in `rustc` to enable packaging?

Ubuntu's `rustc` packages obviously have Debian's package as an ancestor, but due to the requirements of shipping multiple versions in a single stable release, they have diverged over time.
This means that doing a simple diff of the files in the `debian` directory will show a significant number of small tweaks and documentation updates that both teams have made seperately.
Due to the differences in packaging goals, it's increasingly unlikely that the packages will be unified again soon.
This FAQ is focused on the Ubuntu package and not everything is likely apply to Debian.

Arguably the primary packaging tasks for `rustc` involve finding common ground between system packages and the Rust upstream vendoring model, which generally would result in building separate versions of `libc`, `openssl`, `llvm`, and more.
Ubuntu and Debian both prefer to use system libraries whenever possible, and so modify the package to locate those and link agaist them.

A complicating factor is that not all versions of the Ubuntu package use an identical set of vendored dependencies.
For instance, the default `rustc` version on Ubuntu generally makes use of the system `llvm` (although it's statically linked, and so not a runtime dependency).
However, versions are backported to LTS releases out of step with how LLVM is packaged.
This means that some newer versions of `rustc` will used a vendored LLVM.

The actual patches that are applied to the upstream source are split into categories, although nearly all of them are fundamentally focused on finding the right system files and platform-specific issues:

**`behavior`**
: Despite the name, these patches do not change the behavior of the compiler per se.
Instead, it refers to the fact that they apply to `rustc` at runtime.
They mostly set paths so that system resources can be located, they add some additional symlinks to simplify dynamic linking against Rust libraries, and remove some irrelevant platform-specific workarounds.

**`build`**
: These patches adjust paths and options in the build process so that system libraries and tools can be found correctly.
They also makes some checks more strict since the assumptions about which tools will be built are changed.

**`cargo`**
: These mostly disable tests that aren't relevant, such as some that require network connectivity or only apply to particular filesystems.
It also ensures that Cargo is forced to follow the `dev` channel, ensuring it doesn't update itself or download vendored libraries.

**`prune`**
: These are the patches that remove unused code from the tarball.
This includes some vendored libraries and irrelevant platform-specific code, in order to reduce the final size of the package.
There is also some special handling for cross compilation in a way that uses sytem tooling.

**`ubuntu`**
: Ubuntu-specific patches that are mostly focused on making sure that system tooling is found correctly, but also disable some platform-specific tests and ensure that other tests use the system `gcc` compiler.

**`upstream`**
: These patches are official upstream code that hasn't been pushed into a stable release yet.  Mostly this is focused on getting edge-case tests to pass, but also fixes some linker path issues.

**`vendor`**
: Fixes for vendored dependencies, mostly so they can locate and use system libraries.


## How are Rust binaries packaged?

:::{note}
"Binary" is an overloaded term in Rust packaging.  This FAQ topic refers to the binary targets of a Cargo-based Rust project, as opposed to library targets.  However, we also need to distinguish Debian source packages from Debian binary packages, which is entirely orthogonal.
:::

According to the [Debian Rust Packaging Policy](https://wiki.debian.org/Teams/RustPackaging/Policy), Rust crates that include one or more binary executable targets have all their executables bundled into a single Debian binary package.
These are conceptually simpler than Rust library crates from a packaging perspective, and are assembled much like any other Debian package.

The only additional complication is that Cargo is forbidden from accessing the network when building the package, which is typically how it fetches dependencies.
Instead, it must find all dependencies within the package archive.
This is achieved by packaging the library crates in the archive, and then automatically setting up a Cargo registry that makes them available.
This is handled automatically by `dh-cargo`.

Since Rust does not have a stable ABI, and therefore is nearly always statically linked, you may be wondering how the dependencies in the package archive work.  That brings us to our next question!


## How are Rust libraries packaged?

Rust libraries are packaged unlike nearly any other language ecosystem, due to Rust's lack of a stable ABI.
Typically, system libraries are compiled into shared objects and then linked later.

Because we don't have that option, Rust libraries are packaged as _source code_.
That is, a Rust library in the Debian binary format is effectively the same as the relevant source package.
When a Rust application (i.e., a binary Cargo target) is built, it grabs that source code from the library packages and links it statically.

There is special functionality in dh-cargo for this.

## What about crates with optional features?

Rust packages with optional features are divided into multiple, separate packages.
That means for a package named `librust-<cratename>-dev`, an optional feature will _additionally_ need to be packaged as `librust-<cratename>+<featurename>-dev`.
Note the use of the plus symbol, which is chosen deliberately to avoid conflicts with Cargo crate names.

Sometimes, if a crate has a large number of features, they can be collapsed using the `Provides` mechanism.

## What about Rust crates that specify a Rust edition or require a specific toolchain?

Rust editions are effectively handled by the Rust tooling itself.
Every version of `rustc` is guaranteed to be backwards compatible with all previous editions of Rust.
If all the archive crate package versions are frozen alongside the version of `rustc` itself, then that version of `rustc` should support all editions used by the packaged crates.

Rust crates can include a `rust-toolchain.toml` file, which can specify a particular compiler version.
This is effectively orthogonal to the official stable Rust editions.
The most common use-case for this is to specify that unstable "nightly" features are being used by a crate, and so an unstable "nightly" version of `rustc` is required.
The approach for these packages is, more or less, to just exclude them unless there's a really compelling reason not to.
By definition, they are unstable packages, and so do not belong in a distribution's archive of stable, supported packaged crates.

Debian maintainers do make exceptions for extremely valuable software, such as Firefox.
The general approach for these exceptions is to use special settings to temporarily configure the compiler to allow unstable features in a stable version.
Ubuntu packages Firefox as a Snap, which avoids the need for special hacks like this.

(debian-rust-tools)=
## What Rust-specific tooling do maintainers use, and how does it fit into the wider ecosystem of packaging tools?

The ecosystem of Debian packaging tools is big and diverse, with a great deal of overlap and intended deprecation.
This section focuses only on those tools that are likely to be useful when working on Rust code.
A much more comprehensive reference is available in [the Debian developers-reference](https://www.debian.org/doc/manuals/developers-reference/tools.en.html).

There are, roughly speaking, three phases to creating a `.deb` package.

1. Create the source package.
2. Build the binary package from the source package.
3. Test and upload the binary package.

Although coarse, keeping this in mind can help build a more coherent mental model of how the tools interoperate.

### Tools for creating and modifying the source package

**Language-agnostic tools:**

`uscan`
: Short for "upstream scan", it automates tasks related to keeping up-to-date with upstream code.
It relies on you creating a `debian/watch` file, and then can look for new releases, grab them, and verify signatures.
Source packages require "orig" tarballs as a component, which are the unmodified upstream source code, and `uscan` can help you grab them.

`quilt`
: An older, but still widely-used tool to manage a sequence of patches that apply to the upstream source.
It can not only help you manage the order of patches and their current state of application, but can help you generate patches from modified source code.
Some maintainers prefer to manage patches with git-based tooling, which didn't exist when `quilt` was first developed.
In theory, a `git` branch could encode the order of the patches, which are then rebased onto the new code when doing an update.
Nevertheless, being familiar with `quilt` is helpful when understanding packages worked on by multiple maintainers.

`dch`
: Automation for managing the `/debian/changelog` file.
It helps you generate timestamps, author information, and more.

`git-ubuntu`
: An extension to `git` that can clone the repository attached to a package directly from Launchpad.
It has many other features intended to enable more complex package workflows, which are described in the [Ubuntu Maintainer's Handbook](https://github.com/canonical/ubuntu-maintainers-handbook).

`pull-lp-source`
: Similar to `git-ubuntu`, which should be used instead where possible.
The main difference is that instead of cloning the `git` repository, it grabs the source package from Launchpad.
That means you'll get things like the orig tarball, but not the `git` history.

**Rust-specific tools:**

`debcargo`
: A tool written in Rust that will attempt to automatically convert a Rust crate into a Debian source package, by mapping dependencies to Debian packages and generating important files like `debian/control`, `debian/rules`, and `debian/changelog`.

`cargo-debstatus`
: Pull the dependencies from a Cargo project, and determine if appropriate versions of them are already available in the package archive.

### Tools for building the binary package from the source package

**Language-agnostic tools:**

`sbuild`
: The primary tool Ubuntu Rust packagers will likely use to build binary packages.
Fundamentally it is an orchestration tool and replaces the direct invocation of many other tools.
It creates clean build environments using `schroot`s as a sandbox, containing all the necessary dependencies already installed.
It then invokes `dpkg-buildpackage`, and copies the output out of the `schroot`.
There is an alternative backend for `sbuild`, which replaces `schroot`, called `unshare`.
At the time of writing, Launchpad still uses `schroot` and it is probably preferable to do the same locally to avoid behavior differences.

`dpkg-buildpackage`
: The lower-level build tool that is invoked for you by `sbuild`.
It is responsible for running all of the scripts defined in `debian/rules`.

`debhelper`
: A suite of tools used to simplify many of the elements that packages often have in common.
It defines a clear sequence of steps that packages go through when building, which can all be overridden as necessary within `/debian/rules`.
Giving names and order to these steps means that packages no longer need custom scripts to do things like apply patches, or perform configuration.
If you see a call to `dh` in `/debian/rules`, that package is using `debhelper`.
Some older packages may not have migrated to `debhelper` from the manual approach yet.
Lots of add-on packages exist, most notably `dh-cargo` which is listed separately.

`lintian`
: The static analysis tool use to check packages for policy violations, usually executed on your behalf by `sbuild`.
While it's listed under source tooling, it can also check binary packages.

**Rust-specific**

`dh-cargo`
: A `debhelper` add-on which lets you use `--with-cargo` when calling `dh`.
In essence, it enables the direct use of Cargo as a build tool for compiling and linking the code in your package.
Note that `dh-cargo` should _not_ be used applications built only partially with Rust.


### Tools for working with the binary package

**Language-agnostic tools:**

`autopkgtest`
: The testing framework for `.deb` packages.
It sets up an isolated environment, which can be any of a number of containers or VMs, and runs the tests defined in the `debian/tests` directory.
In the official archives, these tests run automatically as part of CI.
However, for PPAs in a typical Ubuntu workflow, the tests are not triggered automatically.

`dput`
: Upload your package to the package archive or a PPA.

## What is the relationship between `llvm` packages and `rustc` packages?

The relationship can be one of two things, depending on the particular `rustc` package version.

1. For the default `rustc` package, with no version number in the name, `llvm` will be a build-time dependency.
Due to static linking, that means that all the relevant `llvm` code will be effectively copied into the `rustc` binary and the `llvm` package will no longer be strictly needed at runtime.
It is generally listed as a suggested dependency of `rustc` in order to support debugging and code generation tasks.

2. For other `rustc-X.Y` packages, `llvm` might be a build-time dependency or we might use a vendored version of `llvm` to avoid the need to backport both packages in lockstep.
Either way, as in the above case, the `llvm` package is not needed at runtime but may still be useful for developers.

## I see `llvm-X-dev` in the archive, but my version of `rustc` doesn't use it

Many LLVM packages are actually universe packages, which are community-maintained.
Packages in the main component of the archive are not allowed to depend on universe component packages.
Accordingly, `rustc` will sometimes use a vendored version of LLVM, even if that version is technically already available.

## What is the status of Rust support for WASM/WASI on Ubuntu?

Ubuntu does not currently build a package for the cross-compilation tooling for WASM.
However, that workflow should be fully supported via `rustup`, which is available as a Snap or in `universe`.

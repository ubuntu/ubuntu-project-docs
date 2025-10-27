(rust-packaging-faq)=
# Rust Packaging FAQ

You may want to start by reading the [Debian Rust Packaging Policy document](https://wiki.debian.org/Teams/RustPackaging/Policy).
The goal of this FAQ is to collect information in a single place without too many overwhelming details, but the policy document should be the source of truth as things change over time or if anything here is unclear.

## How do Debian maintainers package Rust tooling and applications in general?

Debian includes all of the standard Rust tooling in their archive, including [`rustc`](https://packages.debian.org/rustc) and [`cargo`](https://packages.debian.org/cargo).
Their [Rust developer documentation](https://wiki.debian.org/Rust) recommends these packages mainly as tools to package other crates for Debian, and instead recommends the [`rustup`](https://packages.debian.org/rustup) package to install toolchains.

The code that builds the Rust crate packages lives in a monorepo: [debcargo-conf](https://salsa.debian.org/rust-team/debcargo-conf).
Besides the package definitions, it also contains helper scripts for basic development and policy tasks, such as creating tickets, filtering the packages, finding outdated packages, and tracking crates that are intentionally excluded from the archive.

That repo makes heavy use of a tool called [`debcargo`](https://salsa.debian.org/rust-team/debcargo/), written in Rust, which extends the typical Debian tooling ecosystem with some Rust-specific workflows.
It has a number of features, but fundamentally it:

1. downloads crates
1. tries to parse metadata from the crates
1. determines the transitive dependencies
1. maps the dependencies to candidate Debian packages
1. lays out a starter package structure

From there, packaging processes vary depending on the software being packaged, discussed below.
For more information about tooling, see {ref}`debian-rust-tools`.

## How does Ubuntu differ from Debian with respect to Rust packages?

First, you should be familiar with the [process that Ubuntu goes through to merge and sync packages from Debian](#key-concepts).
Additionally, it's worth noting that the preferred workflow for Rust developers is the [`rustup` Snap package](https://snapcraft.io/rustup).
Like with Debian, the system packages are primarily intended to ensure the availability of Rust within Ubuntu itself, which is less directly relevant to application developers.

Due to the merge and sync process, the overwhelming number of Rust packages are imported directly from Debian.
The relatively small number of packages that carry an Ubuntu delta can be spotted by checking [Merge-o-Matic](https://merges.ubuntu.com/).
This can also be determined for an individual package by checking for the presence of `ubuntu` in the version string.
Ubuntu deltas exist for a number of reasons, such as dependency issues to support [Ubuntu's oxidation efforts](https://discourse.ubuntu.com/t/carefully-but-purposefully-oxidising-ubuntu/56995), hardware support, or other Ubuntu-specific integration issues.

There is also a small number of packages that are excluded from the sync for various technical reasons, usually dependencies that are unsatisfiable.  That configuration is handled via the [sync-blocklist](https://git.launchpad.net/~ubuntu-archive/+git/sync-blocklist) Launchpad repo.

While the number of packages that differ from Debian is small, some of them are critically important.
Notably, the `rustc` source package is one that carries a nontrivial delta compared to Debian, and that source package is responsible for generating a number of important binary packages, including: `rustc`, `cargo`, `libstd-rust-X.Y`, and more.
It's not reasonable to enumerate every difference here, but fundamentally they stem from the desire to ship more versions of the compiler in Ubuntu than Debian currently packages.

Debian's version of `rustc` is frozen for the lifetime of each stable Debian release.
Ubuntu, on the other hand, uses versioned packages, which are frequently backported to LTS releases in order to support more software.
Whereas Debian features a single `rustc` binary package, Ubuntu releases typically have multiple with the version information contained directly in the name of the package: `rustc-X.Y`.
Ubuntu then also produces a package named `rustc`, which corresponds to the default version of Rust for that release.

Because Ubuntu produces Rust compiler packages that don't exist on Debian, they necessarily contain a different set of patches and build scripts.

## What do Debian and Ubuntu maintainers change in `rustc` to enable packaging?

Ubuntu's `rustc` packages have Debian's package as an ancestor, but due to the requirements of shipping multiple versions in a single stable release, they have diverged over time.
This means that doing a simple diff of the files in the `debian` directory shows a significant number of small tweaks and documentation updates that both teams have made separately.
Due to the differences in packaging goals, it's increasingly unlikely that the packages would be unified again soon.
This FAQ is focused on the Ubuntu package and not everything is likely to apply to Debian.

Arguably the primary packaging tasks for `rustc` involve finding common ground between system packages and the Rust upstream vendoring model, which generally would result in building separate versions of `libc`, `openssl`, `llvm`, and more.
Ubuntu and Debian both prefer to use system libraries whenever possible, and so modify the package to locate those and link agaist them.

A complicating factor is that not all versions of the Ubuntu package use an identical set of vendored dependencies.
For instance, the default `rustc` version on Ubuntu generally makes use of the system `llvm` (although it's statically linked, and so not a runtime dependency).
However, versions are backported to LTS releases out of step with how LLVM is packaged.
This means that some newer versions of `rustc` use a vendored LLVM.

The actual patches that are applied to the upstream source are split into categories, although nearly all of them are fundamentally focused on finding the right system files and platform-specific issues:

**`behavior`**
: Despite the name, these patches do not change the behavior of the compiler per se.
Instead, it refers to the fact that they apply to `rustc` at runtime.
They mostly set paths, so that system resources can be located. They add some additional symlinks to simplify dynamic linking against Rust libraries and remove some irrelevant platform-specific workarounds.

**`build`**
: These patches adjust paths and options in the build process, so that system libraries and tools can be found correctly.
They also make some checks more strict because the assumptions about which tools are built are changed.

**`cargo`**
: These mostly disable tests that aren't relevant, such as some that require network connectivity or only apply to particular filesystems.
It also ensures that Cargo is forced to follow the `dev` channel, ensuring it doesn't update itself or download vendored libraries.

**`prune`**
: These are the patches that remove unused code from the tarball.
This includes some vendored libraries and irrelevant platform-specific code, in order to reduce the final size of the package.
There is also some special handling for cross compilation in a way that uses system tooling.

**`ubuntu`**
: Ubuntu-specific patches that are mostly focused on making sure that system tooling is found correctly, but also disable some platform-specific tests and ensure that other tests use the system `gcc` compiler.

**`upstream`**
: These patches are official upstream code that hasn't been pushed into a stable release yet.  This is mostly focused on getting edge-case tests to pass, but it also fixes some linker path issues.

**`vendor`**
: Fixes for vendored dependencies; mostly so they can locate and use system libraries.


## How are Rust binaries packaged?

:::{note}
"Binary" is an overloaded term in Rust packaging.  This FAQ topic refers to the binary targets of a Cargo-based Rust project, as opposed to library targets.  However, we also need to distinguish Debian source packages from Debian binary packages, which is an entirely unrelated concept.
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

There is special functionality in `dh-cargo` for this.

## How are crates with optional features packaged?

Rust packages with optional features are divided into multiple, separate packages.
That means for a package named `librust-<cratename>-dev`, an optional feature must _additionally_ be packaged as `librust-<cratename>+<featurename>-dev`.
Note the use of the plus symbol, which is chosen deliberately to avoid conflicts with Cargo crate names.

Sometimes, if a crate has a large number of features, they can be collapsed using the `Provides` mechanism.

## How are Rust crates that specify a Rust edition or require a specific toolchain packaged?

Rust editions are effectively handled by the Rust tooling itself.
Every version of `rustc` is guaranteed to be backwards compatible with all previous editions of Rust.
If all the archive crate package versions are frozen alongside the version of `rustc` itself, then that version of `rustc` should support all editions used by the packaged crates.

Rust crates can include a `rust-toolchain.toml` file, which can specify a particular compiler version.
This is unrelated to the official stable Rust editions.
The most common use case for this is to specify that unstable "nightly" features are being used by a crate, and so an unstable "nightly" version of `rustc` is required.
The approach for these packages is, more or less, to just exclude them unless there's a really compelling reason not to.
By definition, they are unstable packages, and so do not belong in a distribution's archive of stable, supported packaged crates.

Debian maintainers do make exceptions for extremely valuable software, such as Firefox.
The general approach for these exceptions is to use special settings to temporarily configure the compiler to allow unstable features in a stable version.
Ubuntu packages Firefox as a Snap, which avoids the need for special hacks like this.

(debian-rust-tools)=
## What Rust-specific tooling do maintainers use, and how does it fit into the wider ecosystem of packaging tools?

There are a handful of tools useful for Rust package maintainers, but you should first have a good understanding of the {ref}`general Debian tooling <understand-the-tools>`.
Specifically for Rust packages, you should also be familiar with the following.

`debcargo`
: A tool written in Rust that attempts to automatically convert a Rust crate into a Debian source package by mapping dependencies to Debian packages and generating important files like `debian/control`, `debian/rules`, and `debian/changelog`.

`cargo-debstatus`
: Pull the dependencies from a Cargo project, and determine if appropriate versions of them are already available in the package archive.

`dh-cargo`
: A `debhelper` add-on that lets you use `--with-cargo` when calling `dh`.
In essence, it enables the direct use of Cargo as a build tool for compiling and linking the code in your package.
Note that `dh-cargo` should _not_ be used for applications built only partially with Rust.

## What is the relationship between `llvm` and `rustc` packages?

The relationship can be one of two things, depending on the particular `rustc` package version.

1. For the default `rustc` package, with no version number in the name, `llvm` is a build-time dependency.
Due to static linking, that means that all the relevant `llvm` code is effectively copied into the `rustc` binary, and the `llvm` package is no longer strictly needed at runtime.
It is generally listed as a suggested dependency of `rustc` in order to support debugging and code generation tasks.

2. For other `rustc-X.Y` packages, `llvm` might be a build-time dependency or we might use a vendored version of `llvm` to avoid the need to backport both packages in lockstep.
Either way, as in the above case, the `llvm` package is not needed at runtime but may still be useful for developers.

## I see `llvm-X-dev` in the archive, but my version of `rustc` doesn't use it

Many LLVM packages are actually universe packages, which are community-maintained.
Packages in the main component of the archive are not allowed to depend on universe component packages.
Accordingly, `rustc` sometimes uses a vendored version of LLVM, even if that version is technically already available.

## What is the status of Rust support for WASM/WASI on Ubuntu?

Ubuntu does not currently build a package for the cross-compilation tooling for WASM.
However, that workflow should be fully supported via `rustup`, which is available as a Snap or in `universe`.

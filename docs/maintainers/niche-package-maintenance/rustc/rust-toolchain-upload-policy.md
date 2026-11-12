(rust-toolchain-upload-policy)=
# Rust toolchain upload policy


## Background

`rustc` is a large package and can take a long time to build. The build times
differ between architectures, ranging from around two hours on `s390x` to around
a day and a half on `riscv64`. When uploading a Rust toolchain package, Rust
maintainers must be aware that large packages with long build times can block
other packages waiting to {term}`migrate <Proposed migration>`.

Packages in the `-proposed` {term}`pocket` which rely on Rust to build will use
the newest toolchain version available. If a new Rust toolchain is in
`-proposed` and currently building, that package must wait for the build to
complete before its transition can continue, delaying its migration.

Imagine other Ubuntu contributors are migrating a large number of Rust
packages, which all build in a few minutes. If you upload a new Rust toolchain
during this time, those packages will need to use that new toolchain to build,
so they will be unexpectedly blocked for a day and a half while your new Rust
toolchain builds on `riscv64`.

Luckily, there is a way to upload Rust toolchains without disrupting other
maintainers' uploads.


## Binary copy from PPA

Instead of waiting for the package to build in the `-proposed` pocket while it
blocks other uploads, Rust maintainers can instead build the package in a
{term}`PPA`, then request their sponsor binary copy the built package directly
to the {term}`archive`. By doing this, the Rust toolchain upload is already
built once it lands in `-proposed`, so it won't block any pending uploads of
Rust crates.

However, this should only be done when necessary: the archive can change in the
time between your PPA build and the eventual binary copy. When possible, it's
best to go through the standard upload process so you can be sure that your
package builds against the archive as it currently exists.


## When to request a binary copy

Luckily, most Rust uploads can be done normally. A binary copy is only necessary
when _all_ of the following are true:

1. **The upload is a versioned Rust package (`rustc-X.Y`), not
   `rust-defaults`**: `rust-defaults` has nothing to compile and has a
   negligible build time. Only the actual `rustc-X.Y` packages have long enough
   build times to block other uploads.

1. **The versioned Rust package already exists in the archive and is not a new
   package**: If you are uploading a {ref}`brand-new Rust version
   <how-to-update-rust>`, then no packages in the archive rely on it yet, so
   uploading it will not block anything.

1. **The versioned Rust package is the version pointed to by `rust-defaults`**:
   The vast majority of Rust packages in the archive just use the default Rust.
   If the Rust package you're updating isn't the default version, a new upload
   won't cause significant blockages.

To summarize, a binary copy is only necessary when you're uploading a fix to the
existing `rustc-X.Y` package pointed to by `rust-defaults`.

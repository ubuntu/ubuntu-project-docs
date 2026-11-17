(llvm-upload-policy)=
# LLVM upload policy


## Background

LLVM is a large package and can take a long time to build. The build times
differ dramatically between architectures, ranging from around three hours on
`s390x` to nearly eleven days on `riscv64`. When uploading an LLVM package, LLVM
maintainers must be aware that large packages with long build times can block
other packages waiting to {term}`migrate <Proposed migration>`.

Packages in the `-proposed` {term}`pocket` which rely on LLVM to build will use
the newest toolchain version available. If a new LLVM toolchain is in
`-proposed` and currently building, that package must wait for the build to
complete before its transition can continue, delaying its migration.

Imagine other Ubuntu contributors are migrating a large number of packages
which rely on LLVM. They all build in a few minutes. If you upload a new LLVM
toolchain during this time, those packages will need to use that new toolchain
to build, so they will be unexpectedly blocked for nearly two weeks while your
new LLVM builds on `riscv64`.

Luckily, there is a way to upload LLVM toolchains without disrupting other
maintainers' uploads.


## Binary copy from PPA

Instead of waiting for the package to build in the `-proposed` pocket while it
blocks other uploads, LLVM maintainers can instead build the package in a
{term}`PPA`, then request their sponsor binary copy the built package directly
to the {term}`archive`. By doing this, the LLVM toolchain upload is already
built once it lands in `-proposed`, so it won't block any pending uploads of
packages which rely on LLVM.


## Current upload policy

When uploading an update to an existing LLVM toolchain package, LLVM maintainers
should build the final package version in a PPA then request a binary copy from
their sponsor once the PPA build is finished.

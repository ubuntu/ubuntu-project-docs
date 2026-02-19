For Rust versions 1.89 and later, we use a separate "vendor tarball" for the filtered contents of the upstream `vendor` directory. The `vendor` directory contains the source code for all external crates that the Rust toolchain depends on. The filename for this separate tarball ends in `.orig-vendor.tar.xz`. 

The vendor tarball needs to be rebuilt any time we make a change that affects which crate versions are needed, or when working on a new upstream Rust version. Similar to the main "orig tarball", the vendor tarball is saved as a package artifact in the Ubuntu Archive or PPA, and it can be downloaded from Launchpad if no such changes are needed.

To rebuild the vendor tarball, first replace the `vendor` directory with the unfiltered upstream version. If `uscan` has been run previously for this Rust version, the parent directory should contain a file `rustc-<X.Y.Z>-src.tar.xz`. Extract this into a temporary location, then copy over the `vendor` directory:

```none
~/rustc/rustc$ cd ..
~/rustc$ tar xf rustc-<X.Y.Z>-src.tar.xz
~/rustc$ rm -rf rustc/vendor/
~/rustc$ cp -ra rustc-<X.Y.Z>-src/vendor/ rustc/
```

It is expected that you have a copy of the toolchain installed locally (e.g. using `rustup`), with toolchain version matching the version of the toolchain you are packaging. When invoking commands using `debian/rules`, it expects the environment variable `RUST_BOOTSTRAP_DIR` to point to the sysroot of the local toolchain, which you can locate using `rustup`. For example, if packaging version 1.92.0 of Rust, you can run:

```none
~/rustc/rustc$ rustup install 1.92.0
~/rustc/rustc$ rustup +1.92.0 which rustc
/home/<user>/.rustup/toolchains/1.92.0-x86_64-unknown-linux-gnu/bin/rustc
~/rustc/rustc$ export RUST_BOOTSTRAP_DIR=/home/<user>/.rustup/toolchains/1.92.0-x86_64-unknown-linux-gnu
```

The process of filtering the vendored crates relies on a custom cargo subcommand [`cargo-vendor-filterer`](https://github.com/coreos/cargo-vendor-filterer), which we run indirectly via the `vendor-tarball` target of `debian/rules`. You first need to install the `cargo-vendor-filterer` binary:

```none
cargo install cargo-vendor-filterer
```

This installs the binary `cargo-vendor-filterer` into the location `~/.cargo/bin` inside your home directory. Add `~/.cargo/bin` to your `PATH` if it is not already there. Then run the `debian/rules` script using the `vendor-tarball` target:

```none
~/rustc/rustc$ debian/rules vendor-tarball
```

When it finishes, there should be a file in the parent directory named `rustc-<X.Y>_<version>.orig-vendor.tar.xz`, which is the vendor tarball. Extract it to replace the unfiltered `vendor` directory with the filtered version:

```none
~/rustc/rustc$ rm -rf vendor
~/rustc/rustc$ tar xf ../rustc-<X.Y>_<version>.orig-vendor.tar.xz
```

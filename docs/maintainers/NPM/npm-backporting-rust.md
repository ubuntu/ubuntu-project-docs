(npm-backporting-rust)=

# rustc: Backporting Rust

This guide details the process of {term}`backporting <backport>` an existing version of the Rust toolchain to older {term}`releases <ubuntu release>` of Ubuntu.

- To see the process of creating a _new_ versioned `rustc` package, consult the [Updating Rust](npm-updating-rust.md) guide instead.
- To see the process of fixing an existing Rust package, consult the [Patching Rust](npm-patching-rust.md) guide instead.

## Background

Every once in a while, old {term}`Ubuntu releases <ubuntu release>` will need newer versions of `rustc`. [LP: #2100492](https://pad.lv/2100492) is a typical example — Firefox and Chromium started requiring Rust 1.82 to build, so every release going back to Focal needed the versioned `rustc-1.82` package in the archive.

The process of adding a new package to an old Ubuntu release is called a {term}`backport`. Backports don't come with the same security guarantees as regular packages and must be manually enabled for a given machine.

Backporting Rust is tricky because every `rustc` package we create is designed to work with a specific version of the {term}`archive`. It expects a particular version of LLVM, a particular version of CMake, a particular version of `debhelper`, etc... The challenge of backporting stems from trying to get the Rust package to work with an entirely different archive from the one it was built around.

---

## The Proper Order of a Backport

To backport `rustc`, we take a currently-working version and make it build on previous releases of Ubuntu. _However_, in order for a given `rustc` package to build, we _also_ need the previous _Rust_ version for that particular Ubuntu release.

(backporting-rust-example-backport)=

### Example: Backporting rustc-1.86 to Jammy

This concept is better illustrated by an example. Let's say you need to backport `rustc-1.86` to Jammy Jellyfish. In this example, here's the newest `rustc` version supported by every supported Ubuntu release:

| Ubuntu Release   | Supported `rustc` Version |
| ---------------- | ------------------------- |
| Jammy            | `rustc-1.83`              |
| Noble            | `rustc-1.83`              |
| Plucky           | `rustc-1.85`              |
| Questing (devel) | `rustc-1.86`              |

#### Going back in time, one step at a time

It's _strongly discouraged_ to backport the Questing version of `rustc-1.86` directly to Jammy. Since Plucky and Noble are just snapshots along the way from Jammy to Questing, you're not actually reducing the amount of work by jumping straight to Jammy. Additionally, Plucky and Noble may need `rustc-1.86` as well at some point.

Because of this, we're going to go "back in time" one step at a time: Questing -> Plucky, Plucky -> Noble, Noble -> Jammy. Doing it this way gives more immediate feedback and provides "checkpoints" along the way; if you have issues at, say, the "Noble -> Jammy" step, you _know_ that Noble works fine, so the issue stems from something Jammy-specific.

#### Bootstrapping toolchain needed

Remember, in order to build the Rust compiler, you need the _previous Rust version's compiler_ to bootstrap it. Jammy only has `rustc-1.83` in this example. This means that we _also_ can't jump directly to `rustc-1.86` on Jammy; we have to backport `rustc-1.84` and `rustc-1.85` to Jammy as well.

#### Putting it all together

Now we know _what_ we have to do, AND the _order_ to do it in. To backport `rustc-1.86` to Jammy, we must perform the following backports in the given order:

1. `rustc-1.84`
   1. Backport `rustc-1.84` from Plucky to Noble
   1. Backport `rustc-1.84` from Noble to Jammy
1. `rustc-1.85`
   1. Backport `rustc-1.85` from Plucky to Noble
   1. Backport `rustc-1.85` from Noble to Jammy
1. `rustc-1.86`
   1. Backport `rustc-1.86` from Questing to Plucky
   1. Backport `rustc-1.86` from Plucky to Noble
   1. Backport `rustc-1.86` from Noble to Jammy

By doing things this way, you'll discover that the most common problems pop up again and again, and you'll eventually already know how to fix most of them in advance.

---

## Reference

From now on, `<X.Y>` and `<X.Y.Z>` refer to the Rust version number you're backporting.

`<X.Y_old>` and `<X.Y.Z_old>` refer to the Rust version number before the version you're backporting.

`<release>` refers to the Ubuntu release you're backporting _to_, while `<source_release>` refers to the Ubuntu release you're backporting _from_.

`<release_number>` is the version number of the Ubuntu release you're backporting to.

For example, if you were backporting `rustc-1.82` to Jammy...

- `<X.Y>` = 1.82
- `<X.Y.Z>` = 1.82.0
- `<X.Y_old>` = 1.81
- `<X.Y.Z_old>` = 1.81.0
- `<release>` = Jammy
- `<source_release>` = Noble
- `<release_number>` = 22.04

`<lpuser>` refers to your Launchpad username.

`<N>` is the suffix for `~bpo` in the [changelog version number](npm-rust-version-strings.md) and signals which crucial Rust dependencies (if any) were re-included in the source tarball.

`<lp_bug_number>` refers to the bug number on Launchpad.

---

```{include} common/local-repo-setup.md

```

## The Backport Process

The baseline backport process is essentially trivial on its own and has few distinguishing features from a regular Rust toolchain update. The majority of these docs is taken up by the [Common Backporting Changes](backporting-rust-common-backporting-changes) section, which details things you'll often have to do in order to get the backport to build properly.

### The Bug Report

To keep track of backport progress and status, a Launchpad bug report is absolutely necessary.

It's quite likely that there's a specific _reason_ why the backport was needed (e.g., a Rust-based application in an old Ubuntu release has an SRU that needs a newer toolchain to build). In this case, simply reference that bug report throughout the process, assigning the bug to yourself.

If no bug exists, you'll need to create your own. You can find a good example [here](https://pad.lv/2100492). If you need to go back multple Ubuntu releases, target the bug to _all_ series along the way as well, so each of the intermediate backports can be monitored. Additionally, if you need to go back multiple Rust versions, a separate bug report must be filed for each Rust version.

- Going back to our [Jammy 1.86 example](backporting-rust-example-backport), we'd have to create three bug reports:
  1. `rustc-1.84` bug targeting Noble and Jammy
  2. `rustc-1.85` bug targeting Noble and Jammy
  3. `rustc-1.86` bug targeting Plucky, Noble, and Jammy

### Setup

Make sure you're on the `<X.Y>` branch of `<source_release>`, i.e. the version of Rust you want to backport on the Ubuntu release _newer_ than your target:

```none
$ git checkout <source_release>-<X.Y>
```

Then, create your own branch:

```none
$ git checkout -b <release>-<X.Y>
```

Example — backporting `rustc-1.85` to Jammy:

```none
$ git checkout noble-1.85
$ git checkout -b jammy-1.85
```

### Changelog Version

The first thing we should do on our new branch is create a new changelog entry right off the bat. Before we change anything, however, it's important to understand the meaning of every component of the version number. Ensure you read and understand the ["Rust Version Strings"](npm-rust-version-strings.md) article before proceeding.

#### Creating the new changelog entry

To begin, you only have to add/change `<release_number>` in the changelog version number. Don't forget to decrement it! You can leave any `~bpo<N>`s (or lack thereof) as-is for now, as you haven't made any changes to which dependencies have been {term}`vendored <vendored dependency>` yet.

`<existing_version_number>` is the full version number of the latest changelog entry.

```none
$ dch -bv \
    <existing_version_number>.<decremented_release_number> \
    --distribution "<release>"
```

Examples:

| Existing release | Backport      | `existing_version_number`               | New version number                      |
| ---------------- | ------------- | --------------------------------------- | --------------------------------------- |
| 1.82 Devel       | 1.82 Oracular | 1.82.0+dfsg0ubuntu1-0ubuntu2            | 1.82.0+dfsg0ubuntu1-0ubuntu0.24.09      |
| 1.81 Jammy       | 1.81 Focal    | 1.81.0+dfsg0ubuntu1~bpo0-0ubuntu0.22.03 | 1.81.0+dfsg0ubuntu1~bpo0-0ubuntu0.20.03 |

As you can see, we leave everything untouched except for the addition of the decremented release number at the very end.

Make the changelog entry description something like this:

```none
  * Backport to <release> (LP: <lp_bug_number>)
```

(backporting-rust-generating-the-orig-tarball)=

### Generating the Orig Tarball

```{include} common/uscan.md

```

If you've had to vendor LLVM or `libgit2`, add the [relevant `~bpo`](npm-rust-version-strings.md) to the end of the orig tarball's version number too.

```{include} common/local-build.md

```

(backporting-rust-ppa-build)=

```{include} common/ppa-build.md

```

### Uploading the Backport

Once your backport builds successfully in a PPA for all targets, bump the `<release_number>` to its proper number and re-upload to your PPA once more.

After it builds, reach out to the Security team and politely request they upload your backport. Make sure you include the following:

- A link to the bug report
- A link to the PPA

You can monitor upload progress in the [Security Proposed PPA](https://launchpad.net/~ubuntu-security-proposed/+archive/ubuntu/ppa/+packages?field.name_filter=rustc&field.status_filter=&field.series_filter=).

---

(backporting-rust-common-backporting-changes)=

## Common Backporting Changes

While every backport is different, there are several procedures that must occur somewhat regularly. This section is an independent collection of such procedures that should be added to as necessary.

(backporting-rust-vendoring-llvm)=

### Vendoring LLVM

By default, `rustc` uses the distro's packaged LLVM instead of the vendored LLVM bundled in with the upstream Rust source.

However, if you see a message regarding `libclang-rt-*-dev`, `libclang-common-*-dev`, etc. not being installable, then the LLVM version in this Ubuntu release's archive is likely too old.

#### Verifying an outdated LLVM

Consult the Launchpad page for the relevant LLVM release to see if the right version is available. Example: [`llvm-toolchain-19`](https://pad.lv/u/llvm-toolchain-19) isn't available for Jammy. If the Rust version you're backporting uses LLVM 19 or newer, then in order to backport it to Jammy, you'll need to vendor.

If you're unsure whether or not the "broken package" described in the failing buildlog is part of LLVM, check to see which source package it belongs to:

```none
$ dpkg -s <offending_package> | grep Source
```

#### Re-including the upstream LLVM source

Since the Ubuntu Rust package doesn't typically need the vendored LLVM, we yank it out of the tarball. You need to _re-include_ the vendored LLVM source next time we generate the tarball. To prepare for this, remove `src/llvm-project` from `Files-Excluded` in `debian/copyright`:

```diff
@@ -4,7 +4,6 @@ Source: https://www.rust-lang.org
 Files-Excluded:
  .gitmodules
  *.min.js
- src/llvm-project
 # Pre-generated docs
  src/tools/rustfmt/docs
 # Fonts already in Debian, covered by d-0003-mdbook-strip-embedded-libs.patch
```

#### Modifying debian/control and debian/control.in

First, you'll need to remove the relevant packages from `Build-Depends` in both `debian/control` AND `debian/control.in`:

```diff
@@ -17,11 +17,7 @@ Build-Depends:
  python3:native,
  cargo-<X.Y_old> | cargo-<X.Y> <!pkg.rustc.dlstage0>,
  rustc-<X.Y_old> | rustc-<X.Y> <!pkg.rustc.dlstage0>,
- llvm-*-dev:native,
- llvm-*-tools:native,
- libclang-rt-*-dev (>= *),
- libclang-common-*-dev (>= *),
- cmake (>= *) | cmake3,
+ cmake (>= *) | cmake3 (>= *),
 # needed by some vendor crates
  pkgconf,
 # this is sometimes needed by rustc_llvm
@@ -54,7 +54,6 @@ Build-Depends:
  curl <pkg.rustc.dlstage0>,
  ca-certificates <pkg.rustc.dlstage0>,
 Build-Depends-Indep:
- clang-19:native,
  libssl-dev,
 Build-Conflicts: gdb-minimal (<< 8.1-0ubuntu6) <!nocheck>
 Standards-Version: 4.6.2
```

You'll also need to _add_ certain `Build-Depends` required to build LLVM:

```diff
@@ -37,6 +33,10 @@ Build-Depends:
  libgit2-dev (<< *),
  libhttp-parser-dev,
  libsqlite3-dev,
+# Required for llvm build
+ autotools-dev,
+ m4,
+ ninja-build,
 # test dependencies:
  binutils (>= *) <!nocheck> | binutils-* <!nocheck>,
  git <!nocheck>,
```

Finally, you can remove the binary package dependencies as well:

```diff
@@ -157,7 +156,7 @@ Description: Rust debugger (gdb)
 Package: rust-1.83-lldb
 Architecture: all
 # When updating, also update rust-lldb.links
-Depends: lldb-19, ${misc:Depends}, python3-lldb-19
+Depends: ${misc:Depends}
 Replaces: rustc (<< 1.1.0+dfsg1-1)
 Description: Rust debugger (lldb)
  Rust is a curly-brace, block-structured expression language.  It
@@ -271,7 +271,6 @@ Description: Rust formatting helper
 Package: rust-<X.Y>-all
 Architecture: all
 Depends: ${misc:Depends}, ${shlibs:Depends},
- llvm-*,
  rustc-<X.Y> (>= ${binary:Version}),
  rustfmt-<X.Y> (>= ${binary:Version}),
  rust-<X.Y>-clippy (>= ${binary:Version}),
```

#### Modifying debian/config.toml.in

Remove the option declaring LLVM as a dynamically-linked library (as opposed to the default statically-linked library):

```diff
--- a/debian/config.toml.in
+++ b/debian/config.toml.in
@@ -68,9 +68,6 @@ profiler = false

 )dnl

-[llvm]
-link-shared = true
-
 [rust]
 jemalloc = false
 optimize = MAKE_OPTIMISATIONS
```

The lines pointing `rustc` to the proper system LLVM tools can be removed in favour of using the default vendored LLVM:

```diff
--- a/debian/config.toml.in
+++ b/debian/config.toml.in
@@ -31,25 +31,6 @@ optimized-compiler-builtins = false
 [install]
 prefix = "/usr/lib/rust-RUST_VERSION"

-[target.DEB_BUILD_RUST_TYPE]
-llvm-config = "LLVM_DESTDIR/usr/lib/llvm-LLVM_VERSION/bin/llvm-config"
-linker = "DEB_BUILD_GNU_TYPE-gcc"
-PROFILER_PATH
-
-ifelse(DEB_BUILD_RUST_TYPE,DEB_HOST_RUST_TYPE,,
-[target.DEB_HOST_RUST_TYPE]
-llvm-config = "LLVM_DESTDIR/usr/lib/llvm-LLVM_VERSION/bin/llvm-config"
-linker = "DEB_HOST_GNU_TYPE-gcc"
-PROFILER_PATH
-
-)dnl
-ifelse(DEB_BUILD_RUST_TYPE,DEB_TARGET_RUST_TYPE,,DEB_HOST_RUST_TYPE,DEB_TARGET_RUST_TYPE,,
-[target.DEB_TARGET_RUST_TYPE]
-llvm-config = "LLVM_DESTDIR/usr/lib/llvm-LLVM_VERSION/bin/llvm-config"
-linker = "DEB_TARGET_GNU_TYPE-gcc"
-PROFILER_PATH
-
-)dnl
 [target.wasm32-wasi]
 wasi-root = "/usr"
 profiler = false
```

#### Modifying debian/rules

The build process must be modified somewhat in order to account for the newly-vendored LLVM.

```diff
--- a/debian/rules
+++ b/debian/rules
@@ -34,38 +34,37 @@ include debian/architecture.mk
 # for dh_install substitution variable
 export DEB_HOST_RUST_TYPE

+# Let rustbuild control whether LLVM is compiled with debug symbols, rather
+# than compiling with debug symbols unconditionally, which will fail on
+# 32-bit architectures
+CFLAGS := $(shell echo $(CFLAGS) | sed -e 's/\-g//')
+CXXFLAGS := $(shell echo $(CFLAGS) | sed -e 's/\-g//')
+
 # for dh_install substitution variable
 export RUST_LONG_VERSION
 export RUST_VERSION

 DEB_DESTDIR := $(CURDIR)/debian/tmp

-# Use system LLVM (comment out to use vendored LLVM)
-LLVM_VERSION = 19
-OLD_LLVM_VERSION = $(shell echo "$$(($(LLVM_VERSION)-1))")
-# used by the upstream profiler build script
-CLANG_RT_TRIPLE := $(shell llvm-config-$(LLVM_VERSION) --host-target)
-LLVM_PROFILER_RT_LIB = /usr/lib/clang/$(LLVM_VERSION)/lib/$(CLANG_RT_TRIPLE)/libclang_rt.profile
.a
-ifneq ($(wildcard $(LLVM_PROFILER_RT_LIB)),)
-# Clang per-target layout
-export LLVM_PROFILER_RT_LIB := /../../$(LLVM_PROFILER_RT_LIB)
-else
-# Clang legacy layout
-CLANG_RT_ARCH := $(shell echo '$(CLANG_RT_TRIPLE)' | cut -f1 -d-)
-ifeq ($(DEB_HOST_ARCH),armhf)
-CLANG_RT_ARCH := armhf
-endif
-export LLVM_PROFILER_RT_LIB := /usr/lib/clang/$(LLVM_VERSION)/lib/linux/libclang_rt.profile-$(CLANG_RT_ARCH).a
-endif
+# # Use system LLVM (comment out to use vendored LLVM)
+# LLVM_VERSION = 19
+# OLD_LLVM_VERSION = $(shell echo "$$(($(LLVM_VERSION)-1))")
+# # used by the upstream profiler build script
+# CLANG_RT_TRIPLE := $(shell llvm-config-$(LLVM_VERSION) --host-target)
+# LLVM_PROFILER_RT_LIB = /usr/lib/clang/$(LLVM_VERSION)/lib/$(CLANG_RT_TRIPLE)/libclang_rt.profi
le.a
+# ifneq ($(wildcard $(LLVM_PROFILER_RT_LIB)),)
+# # Clang per-target layout
+# export LLVM_PROFILER_RT_LIB := /../../$(LLVM_PROFILER_RT_LIB)
+# else
+# # Clang legacy layout
+# CLANG_RT_ARCH := $(shell echo '$(CLANG_RT_TRIPLE)' | cut -f1 -d-)
+# ifeq ($(DEB_HOST_ARCH),armhf)
+# CLANG_RT_ARCH := armhf
+# endif
+# export LLVM_PROFILER_RT_LIB := /usr/lib/clang/$(LLVM_VERSION)/lib/linux/libclang_rt.profile-$(
CLANG_RT_ARCH).a
+# endif
 # Cargo-specific flags
 export LIBSSH2_SYS_USE_PKG_CONFIG=1
-# Make it easier to test against a custom LLVM
-ifneq (,$(LLVM_DESTDIR))
-LLVM_LIBRARY_PATH := $(LLVM_DESTDIR)/usr/lib/$(DEB_HOST_MULTIARCH):$(LLVM_DESTDIR)/usr/lib
-LD_LIBRARY_PATH := $(if $(LD_LIBRARY_PATH),$(LD_LIBRARY_PATH):$(LLVM_LIBRARY_PATH),$(LLVM_LIBRAR
Y_PATH))
-export LD_LIBRARY_PATH
-endif
-
 ifneq (,$(filter parallel=%,$(DEB_BUILD_OPTIONS)))
 ifeq ($(DEB_HOST_ARCH),riscv64)
 NJOBS := -j $(patsubst parallel=%,%,$(filter parallel=%,$(DEB_BUILD_OPTIONS)))
```

It's no longer necessary to set certain configuration variables:

```diff
@@ -257,8 +256,6 @@ debian/config.toml: debian/config.toml.in debian/rules debian/preconfigure.st
amp
                -DDEB_TARGET_GNU_TYPE="$(DEB_TARGET_GNU_TYPE)" \
                -DMAKE_OPTIMISATIONS="$(MAKE_OPTIMISATIONS)" \
                -DVERBOSITY="$(VERBOSITY)" \
-               -DLLVM_DESTDIR="$(LLVM_DESTDIR)" \
-               -DLLVM_VERSION="$(LLVM_VERSION)" \
                -DRUST_BOOTSTRAP_DIR="$(RUST_BOOTSTRAP_DIR)" \
                -DRUST_VERSION="$(RUST_VERSION)" \
                -DPROFILER_PATH="profiler = \"$(LLVM_PROFILER_RT_LIB)\"" \
```

The `check-no-old-llvm` rule and certain other checks also become obsolete:

```diff
@@ -272,12 +269,7 @@ ifneq (,$(filter $(DEB_BUILD_ARCH), armhf armel i386 mips mipsel powerpc pow
erpc
        sed -i -e 's/^debuginfo-level = .*/debuginfo-level = 0/g' "$@"
 endif

-check-no-old-llvm:
-       # fail the build if we have any instances of OLD_LLVM_VERSION in debian, except for debian/changelog
-       ! grep --color=always -i '\(clang\|ll\(..\|d\)\)-\?$(subst .,\.,$(OLD_LLVM_VERSION))' --exclude=changelog --exclude=copyright --exclude='*.patch' --exclude-dir='.debhelper' -R debian
-.PHONY: check-no-old-llvm
-
-debian/dh_auto_configure.stamp: debian/config.toml check-no-old-llvm
+debian/dh_auto_configure.stamp: debian/config.toml
        # fail the build if the vendored sources info is out-of-date
        CARGO_VENDOR_DIR=$(CURDIR)/vendor /usr/share/cargo/bin/dh-cargo-vendored-sources
        # fail the build if we accidentally vendored openssl, indicates we pulled in unnecessary dependencies
@@ -365,13 +357,6 @@ ifneq (,$(filter $(DEB_BUILD_ARCH), armhf))
   FAILED_TESTS += | grep -v '^test \[debuginfo-gdb\] src/test/debuginfo/'
 endif
 override_dh_auto_test-arch:
-       # ensure that rustc_llvm is actually dynamically linked to libLLVM
-       set -e; find build/*/stage2/lib/rustlib/* -name '*rustc_llvm*.so' | \
-       while read x; do \
-               stat -c '%s %n' "$$x"; \
-               objdump -p "$$x" | grep -q "NEEDED.*LLVM"; \
-               test "$$(stat -c %s "$$x")" -lt 6000000; \
-       done
 ifeq (, $(filter nocheck,$(DEB_BUILD_PROFILES)))
 ifeq (, $(filter nocheck,$(DEB_BUILD_OPTIONS)))
        # there's a test that tests stage0 rustc, so we need to use system rustc to do that
```

Finally, we can clean up the LLVM source directory after installation to save on disk space:

```diff
@@ -507,6 +492,8 @@ endif
 override_dh_install-indep:
        dh_install
        $(RM) -rf $(SRC_CLEAN:%=debian/rust-$(RUST_VERSION)-src/src/usr/src/rustc-$(RUST_LONG_VERSION)/%)
+       # Get rid of src/llvm-project
+       $(RM) -rf debian/rust-$(RUST_VERSION)-src/usr/src/rustc-$(RUST_LONG_VERSION)/src/llvm-project
        # Get rid of lintian warnings
        find debian/rust-$(RUST_VERSION)-src/usr/src/rustc-$(RUST_LONG_VERSION) \
                \( -name .gitignore \
```

#### LLVM copyright stanza

We also need to re-include the LLVM copyright stanza in `debian/copyright`:

```diff
--- a/debian/copyright
+++ b/debian/copyright
@@ -919,6 +919,10 @@ Files-Excluded:
  vendor/zeroize_derive-1.4.2
 # DO NOT EDIT above, AUTOGENERATED

+Files: src/llvm-project/*
+Copyright: 2003-2025 University of Illinois at Urbana-Champaign
+License: Apache-2.0 with LLVM exception
+
 Files: C*.md
        R*.md
        Cargo.lock
```

#### Re-including the LLVM source

Update the [changelog version number](npm-rust-version-strings.md) accordingly. Your version number should now contain either `~bpo0` or `~bpo2` depending on the status of `libgit2`.

You can now [regenerate the orig tarball](npm-rust-version-strings.md), which should now include the upstream LLVM source in `src/llvm-project`.

After regenerating the orig tarball, get all the new LLVM files and overlay them on your working directory:

```none
$ cd ..
$ tar -xf rustc-<X.Y>_<X.Y.Z>+dfsg0ubuntu1\~bpo<N>.orig.tar.xz
$ cp -ra rustc-<X.Y.Z>-src/src/llvm-project rustc/src
$ cd -
```

Finally, you can add the vendored LLVM source to Git as well:

```none
$ git add src/llvm-project
```

```{include} common/empty-directories-notice.md

```

### Outdated libgit2-dev

A common problem when backporting is that the version of the `libgit2-dev` C library in the target Ubuntu release is too old for what the version `rustc` requires. If your Ubuntu release's [available `libgit2` version](https://pad.lv/u/libgit2) doesn't meet your Rust toolchain's requirements, then you have two options:

1. [Downgrade](backporting-rust-downgrading-libgit2-dev). This is the easier option, but it only works if the `libgit2-dev` version in the archive isn't _too_ old.
1. [Vendor](backporting-rust-vendoring-libgit2). This is a much bigger change, but it's often necessary if the `libgit2-dev` version in the archive is so old that it breaks things.

(backporting-rust-downgrading-libgit2-dev)=

### Downgrading libgit2-dev

It may be possible to simply downgrade the required `libgit2-dev` version to the most recent version in your target release's archive.

For example, assume that the required `libgit2-dev` version is `1.9.0`, and the most recent version in the archive is `1.7.2`.

#### Modifying debian/control and debian/control.in

Simply reduce the minimum requirement to the version in the archive, and restrict the maximum to anything newer:

```diff
--- a/debian/control
+++ b/debian/control
@@ -33,8 +33,8 @@ Build-Depends:
  bash-completion,
  libcurl4-gnutls-dev | libcurl4-openssl-dev,
  libssh2-1-dev,
- libgit2-dev (>= 1.9.0~~),
- libgit2-dev (<< 1.10~~),
+ libgit2-dev (>= 1.7.2~~),
+ libgit2-dev (<< 1.8~~),
  libhttp-parser-dev,
  libsqlite3-dev,
 # test dependencies:
```

Don't forget to change `debian/control.in` too!

```diff
--- a/debian/control.in
+++ b/debian/control.in
@@ -33,8 +33,8 @@ Build-Depends:
  bash-completion,
  libcurl4-gnutls-dev | libcurl4-openssl-dev,
  libssh2-1-dev,
- libgit2-dev (>= 1.9.0~~),
- libgit2-dev (<< 1.10~~),
+ libgit2-dev (>= 1.7.2~~),
+ libgit2-dev (<< 1.8~~),
  libhttp-parser-dev,
  libsqlite3-dev,
 # test dependencies:
```

#### Patching libgit2-sys

The vendored `libgit2-sys` crate tries to search for the system libgit2 C library. It's your job to point it to the right version.

Create a new patch and add the `build.rs` script of your `libgit2-sys` crate:

```none
$ quilt push -a
$ quilt new ubuntu/ubuntu-libgit2-downgrade.patch
$ quilt add vendor/libgit2-sys-<version>/build.rs
```

Adjust the versions it searches for in `try_system_libgit2()` accordingly:

```diff
--- a/vendor/libgit2-sys-<version>/build.rs
+++ b/vendor/libgit2-sys-<version>/build.rs
@@ -7,7 +7,7 @@
 /// Tries to use system libgit2 and emits necessary build script instructions.
 fn try_system_libgit2() -> Result<pkg_config::Library, pkg_config::Error> {
     let mut cfg = pkg_config::Config::new();
-    match cfg.range_version("1.9.0".."1.10.0").probe("libgit2") {
+    match cfg.range_version("1.7.2".."1.8.0").probe("libgit2") {
         Ok(lib) => {
             for include in &lib.include_paths {
                 println!("cargo:root={}", include.display());
```

#### Testing

Try to build the package and see if it works. If not, then you must vendor the `libgit2` C library included with the upstream Rust source. Undo your changes and consult ["Vendoring libgit2](backporting-rust-vendoring-libgit2) below.

(backporting-rust-vendoring-libgit2)=

### Vendoring libgit2

If the version of `libgit2-dev` in your target Ubuntu release's archive is too old to function properly, you must vendor the `libgit2` C library instead, which is normally included in the vendored `libgit2-sys` crate.

#### Re-including libgit2 in Files-Excluded

Comment out `libgit2` from `Files-Excluded` in `debian/copyright`, so next time you regenerate the tarball, it's included within the files:

```diff
--- a/debian/copyright
+++ b/debian/copyright
@@ -43,7 +43,7 @@ Files-Excluded:
 # Embedded C libraries
  vendor/curl-sys-*/curl
  vendor/libdbus-sys-*/vendor
- vendor/libgit2-sys-*/libgit2
+# vendor/libgit2-sys-*/libgit2
  vendor/libssh2-sys-*/libssh2
  vendor/libsqlite3-sys-*/sqlite3
  vendor/libsqlite3-sys-*/sqlcipher
```

#### Removing libgit2-dev and libhttp-parser-dev from Build-Depends

You must also comment out `libgit2-dev` and `libhttp-parser-dev` from `Build-Depends` in `debian/control` and `debian/control.in`. `libhttp-parser-dev` is removed because it's also included within the vendored `libgit2` source code.

```diff
--- a/debian/control
+++ b/debian/control
@@ -33,9 +33,9 @@ Build-Depends:
  bash-completion,
  libcurl4-gnutls-dev | libcurl4-openssl-dev,
  libssh2-1-dev,
- libgit2-dev (>= 1.9.0~~),
- libgit2-dev (<< 1.10~~),
- libhttp-parser-dev,
+# libgit2-dev (>= 1.9.0~~),
+# libgit2-dev (<< 1.10~~),
+# libhttp-parser-dev,
  libsqlite3-dev,
 # test dependencies:
  binutils (>= 2.26) <!nocheck> | binutils-2.26 <!nocheck>,
```

Don't forget `debian/control.in`, too!

```diff
--- a/debian/control.in
+++ b/debian/control.in
@@ -33,9 +33,9 @@ Build-Depends:
  bash-completion,
  libcurl4-gnutls-dev | libcurl4-openssl-dev,
  libssh2-1-dev,
- libgit2-dev (>= 1.9.0~~),
- libgit2-dev (<< 1.10~~),
- libhttp-parser-dev,
+# libgit2-dev (>= 1.9.0~~),
+# libgit2-dev (<< 1.10~~),
+# libhttp-parser-dev,
  libsqlite3-dev,
 # test dependencies:
  binutils (>= 2.26) <!nocheck> | binutils-2.26 <!nocheck>,
```

#### Editing the patch

After that, we must edit the patch removing vendored C crates so the vendored version is used properly:

```none
$ quilt push prune/d-0010-cargo-remove-vendored-c-crates.patch
```

Edit `src/tools/cargo/Cargo.toml` to re-include the `vendored-libgit2` feature:

```diff
  [features]
+ vendored-libgit2 = ["libgit2-sys/vendored"]
```

When you refresh the patch and pop everything off again, the patch diff should look something like this:

```diff
--- a/debian/patches/prune/d-0010-cargo-remove-vendored-c-crates.patch
+++ b/debian/patches/prune/d-0010-cargo-remove-vendored-c-crates.patch
@@ -22,12 +22,12 @@ Forwarded: not-needed
  rustc-hash = "2.1.1"
  rustc-stable-hash = "0.1.1"
  rustfix = { version = "0.9.0", path = "crates/rustfix" }
-@@ -268,10 +268,8 @@
+@@ -268,10 +268,9 @@
  doc = false

  [features]
 -vendored-openssl = ["openssl/vendored"]
--vendored-libgit2 = ["libgit2-sys/vendored"]
+ vendored-libgit2 = ["libgit2-sys/vendored"]
 +# Debian: removed vendoring flags
  # This is primarily used by rust-lang/rust distributing cargo the executable.
 -all-static = ['vendored-openssl', 'curl/static-curl', 'curl/force-system-lib-on-osx', 'vendored-libgit2']
```

#### Re-including the libgit2 source

Update the [changelog version number](npm-rust-version-strings.md) accordingly. Your version number should now contain either `~bpo0` or `~bpo10`, depending on the status of LLVM.

You can now [regenerate the orig tarball](backporting-rust-generating-the-orig-tarball), which should now include the upstream `libgit2` source in `vendor/libgit2-sys-<version>/libgit2`.

After regenerating the orig tarball, get all the new `libgit2` files and overlay them on your working directory:

```none
$ cd ..
$ tar -xf rustc-<X.Y>_<X.Y.Z>+dfsg0ubuntu1\~bpo<N>.orig.tar.xz
$ cp -ra rustc-<X.Y.Z>-src/vendor/libgit2-sys-<version>/libgit2 rustc/vendor/libgit2-sys-<version>/
$ cd -
```

Finally, you can add the vendored `libgit2` source to Git as well:

```shell
git add vendor/libgit2-sys-<version>/libgit2
```

```{include} common/empty-directories-notice.md

```

### Disabling dh-cargo

Earlier Ubuntu releases may not have access to [`dh-cargo`](https://launchpad.net/ubuntu/+source/dh-cargo) for the purposes of validating the custom `XS-Vendored-Sources-Rust` field in `debian/control`. If this is the case, then it must be removed from the build dependencies and build scripts.

#### Removing dh-cargo from Build-Depends

```diff
--- a/debian/control
+++ b/debian/control
@@ -12,7 +12,7 @@ Rules-Requires-Root: no
 Build-Depends:
  debhelper (>= 9),
  debhelper-compat (= 13),
- dh-cargo (>= 28ubuntu1~),
+# dh-cargo (>= 28ubuntu1~),
  dpkg-dev (>= 1.17.14),
  python3:native,
  cargo-1.85 | cargo-1.86 <!pkg.rustc.dlstage0>,
```

Don't forget `debian/control.in` too!

```diff
--- a/debian/control.in
+++ b/debian/control.in
@@ -12,7 +12,7 @@ Rules-Requires-Root: no
 Build-Depends:
  debhelper (>= 9),
  debhelper-compat (= 13),
- dh-cargo (>= 28ubuntu1~),
+# dh-cargo (>= 28ubuntu1~),
  dpkg-dev (>= 1.17.14),
  python3:native,
  cargo-@RUST_PREV_VERSION@ | cargo-@RUST_VERSION@ <!pkg.rustc.dlstage0>,
```

#### Removing the Vendored-Sources-Rust check

`debian/rules` must be modified so it doesn't try to use `dh-cargo` to validate `Vendored-Sources-Rust`:

```diff
--- a/debian/rules
+++ b/debian/rules
@@ -278,8 +278,6 @@ check-no-old-llvm:
 .PHONY: check-no-old-llvm

 debian/dh_auto_configure.stamp: debian/config.toml check-no-old-llvm
-       # fail the build if the vendored sources info is out-of-date
-       CARGO_VENDOR_DIR=$(CURDIR)/vendor /usr/share/cargo/bin/dh-cargo-vendored-sources
        # fail the build if we accidentally vendored openssl, indicates we pulled in unnecessary dependencies
        test ! -e vendor/openssl-src-*
        # fail the build if our version contains ~exp and we are not releasing to experimental
```

### Reverting from pkgconf to pkg-config

[`pkgconf`](http://pkgconf.org/) is a drop-in modern replacement for the older [`pkg-config`](https://www.freedesktop.org/wiki/Software/pkg-config/), but if you get an error stating that `the pkg-config command could not be found`, then your target Ubuntu release is likely too old to have `pkgconf`. In this case, we must fall back on using `pkg-config` instead.

#### Editing Build-Depends

```diff
--- a/debian/control
+++ b/debian/control
@@ -23,7 +23,7 @@ Build-Depends:
  libclang-common-19-dev (>= 1:19.1.2),
  cmake (>= 3.0) | cmake3,
 # needed by some vendor crates
- pkgconf,
+ pkg-config,
 # this is sometimes needed by rustc_llvm
  zlib1g-dev:native,
  zlib1g-dev,
```

Don't forget to edit `debian/control.in` as well!

```diff
--- a/debian/control.in
+++ b/debian/control.in
@@ -23,7 +23,7 @@ Build-Depends:
  libclang-common-19-dev (>= 1:19.1.2),
  cmake (>= 3.0) | cmake3,
 # needed by some vendor crates
- pkgconf,
+ pkg-config,
 # this is sometimes needed by rustc_llvm
  zlib1g-dev:native,
  zlib1g-dev,
```

#### Editing debian/rules

`debian/rules` must be modified so Cargo uses `pkg-config` instead of `pkgconf`:

```diff
--- a/debian/rules
+++ b/debian/rules
@@ -59,6 +59,7 @@ export LLVM_PROFILER_RT_LIB := /usr/lib/clang/$(LLVM_VERSION)/lib/linux/libclang
 endif
 # Cargo-specific flags
 export LIBSSH2_SYS_USE_PKG_CONFIG=1
+export PKG_CONFIG=pkg-config
 # Make it easier to test against a custom LLVM
 ifneq (,$(LLVM_DESTDIR))
 LLVM_LIBRARY_PATH := $(LLVM_DESTDIR)/usr/lib/$(DEB_HOST_MULTIARCH):$(LLVM_DESTDIR)/usr/lib
```

### Outdated cmake

If the version of [`cmake`](https://pad.lv/u/cmake) in the archive is too old, we can't just update the `cmake` version in the archive. This would change how countless other packages were built. Instead, we use [`cmake-mozilla`](https://pad.lv/u/cmake-mozilla), which is updated specifically for backports to use.

Add `cmake-mozilla` to the possible `cmake` options in the `Build-Depends` of `debian/control` and `debian/control.in`:

```diff
--- a/debian/control
+++ b/debian/control
@@ -21,7 +21,7 @@ Build-Depends:
  llvm-19-tools:native,
  libclang-rt-19-dev (>= 1:19.1.2),
  libclang-common-19-dev (>= 1:19.1.2),
- cmake (>= 3.0) | cmake3,
+ cmake (>= 3.0) | cmake3 | cmake-mozilla (>= 3.0),
 # needed by some vendor crates
  pkgconf,
 # this is sometimes needed by rustc_llvm
```

Don't forget `debian/control.in`!

```diff
--- a/debian/control.in
+++ b/debian/control.in
@@ -21,7 +21,7 @@ Build-Depends:
  llvm-19-tools:native,
  libclang-rt-19-dev (>= 1:19.1.2),
  libclang-common-19-dev (>= 1:19.1.2),
- cmake (>= 3.0) | cmake3,
+ cmake (>= 3.0) | cmake3 | cmake-mozilla (>= 3.0),
 # needed by some vendor crates
  pkgconf,
 # this is sometimes needed by rustc_llvm
```

### Outdated debhelper-compat

[`debhelper-compat`](https://www.man7.org/linux/man-pages/man7/debhelper.7.html#COMPATIBILITY_LEVELS) serves as a way of denoting a versioned build dependency on a specific version of {manpage}`debhelper(7)`.

If your target Ubuntu release doesn't have `debhelper-compat`, you can downgrade the required version in `debian/control` and `debian/control.in`, but you must adjust your packaging accordingly. These changes can often be quite significant.

For instance, reverting to version 12 from version 13 requires using an older format of substitution variables in debian install files:

```diff
--- a/debian/libstd-rust-X.Y-dev.install.in
+++ b/debian/libstd-rust-X.Y-dev.install.in
@@ -1 +1 @@
-usr/lib/rust-${env:RUST_VERSION}/lib/rustlib/${env:DEB_HOST_RUST_TYPE}/lib/
+usr/lib/rust-@RUST_VERSION@/lib/rustlib/@DEB_HOST_RUST_TYPE@/lib/
```

You can cherry-pick the following commit and deal with the merge conflicts if you're going from 13->12. It also works as a reference for all the changes you'll have to make:

```none
$ git cherry-pick 20ce525927c2e9176dd3c7209968038b09a49a25
```

### Failing rustdoc-ui Tests

For older Ubuntu releases (likely those with `make < 4.4`), it's possible for emitted `job-server` warnings to cause `rustdoc-ui` tests which use byte-for-byte standard error comparisons to fail.

This is a [known issue](https://github.com/rust-lang/cargo/issues/14407) with `jobserver-rs` — it's even noted in the [`rustc` book](https://doc.rust-lang.org/stable/rustc/jobserver.html#gnu-make).

If this happens, try [building in a PPA](backporting-rust-ppa-build). There's a good chance our actual build infrastructure doesn't trigger those warnings and passes the tests.

:::{note}
More investigation is needed to figure out why the tests fail in local build environments and succeed in PPAs.
:::

### Missing OpenSSL

If you get a message similar to the following:

```none
  The system library `openssl` required by crate `openssl-sys` was not found.
  The file `openssl.pc` needs to be installed and the PKG_CONFIG_PATH environment variable must contain its parent directory.
  The PKG_CONFIG_PATH environment variable is not set.

  HINT: if you have installed the library, try setting PKG_CONFIG_PATH to the directory containing `openssl.pc`.


  --- stderr
  thread 'main' panicked at /<<PKGBUILDDIR>>/vendor/openssl-sys-0.9.102/build/find_normal.rs:190:5:


  Could not find directory of OpenSSL installation, and this `-sys` crate cannot
  proceed without this knowledge. If OpenSSL is installed and this crate had
  trouble finding it,  you can set the `OPENSSL_DIR` environment variable for the
  compilation process.

  Make sure you also have the development packages of openssl installed.
  For example, `libssl-dev` on Ubuntu or `openssl-devel` on Fedora.
```

Then the error message is accurate. Add `libssl-dev` to `Build-Depends` within `debian/control` and `debian/control.in`:

```diff
@@ -29,6 +29,7 @@ Build-Depends:
  libcurl4-gnutls-dev | libcurl4-openssl-dev,
  libssh2-1-dev,
  libsqlite3-dev,
+ libssl-dev,
 # Required for llvm build
  autotools-dev,
  m4,
```

### RISC-V "Z" Extension Issues

Certain tests may fail on {term}`RISC-V` because older versions of [`binutils`](https://launchpad.net/ubuntu/+source/binutils) don't know how to handle newer RISC-V extensions included with the [newly-vendored LLVM](backporting-rust-vendoring-llvm). Therefore, these extensions must be removed from the vendored LLVM.

(backporting-rust-disabling-zicsr)=

#### Disabling zicsr (LLVM 18+)

There exists a patch which disables the [`zicsr`](https://www.five-embeddev.com/riscv-user-isa-manual/latest-adoc/zicsr.html) RISC-V extension:

```none
$ git cherry-pick e7285a65b8ae134c7bd506e23beef4a3f088eab5
```

This works for LLVM 18. To disable `zicsr` on LLVM 19+, you must also include an update to this patch:

```none
$ git cherry-pick eea627ceb5ec7ab312a10aafaa191c602efd561a
```

#### Disabling zmmul (LLVM 19+)

LLVM 19 also added the [`zmmul`](https://www.five-embeddev.com/riscv-user-isa-manual/latest-adoc/m-st-ext.html#_zmmul_extension_version_1_0) RISC-V extension, which _also_ isn't supported on older versions of `binutils`.

There is a patch that disables `zmmul`. It's intended to be overlaid on top of the [`zicsr` removal patch](backporting-rust-disabling-zicsr), but it will be able to apply cleanly with minimal changes:

```none
$ git cherry-pick 9b5dda44b0de0a3e1e9dfd552e6097c08aed298f
```

### No Space Left on Device

Sometimes, especially when vendoring [LLVM](backporting-rust-vendoring-llvm) and/or [`libgit2`](backporting-rust-vendoring-libgit2), the build will succeed locally but fail in a PPA due to the PPA builder running out of space.

Consult the failing PPA buildlog for a "No space left on device" message to confirm that this is the cause. Take note of the point in `debian/rules` in which the PPA builder runs out of space.

Then, right before the builder runs out of space, add some diagnostic information:

```makefile
	@echo "------- disk usage -------"
	-df -h /
	@echo "------- inode usage -------"
	-df -ih /
	@echo "------- top space hogs in cwd -------"
	-du -xh $(CURDIR) | sort -h | tail -n 20
```

Hopefully, the PPA builder will run out of space _past_ the point at which `stage0` `stage1`, and `test` artifacts are no longer needed. In that case, they can simply be deleted earlier than usual:

```makefile
	$(RM) -rf $(CURDIR)/build/$(DEB_BUILD_RUST_TYPE)/test
	$(RM) -rf $(CURDIR)/build/$(DEB_BUILD_RUST_TYPE)/stage0-rustc
	$(RM) -rf $(CURDIR)/build/$(DEB_BUILD_RUST_TYPE)/stage1-rustc
```

(how-to-update-rust)=
# How to update Rust

This guide details the process of creating a new versioned `rustc` Ubuntu package for a new upstream Rust release.

- To see the process of {term}`backporting <backport>` Rust, consult the {ref}`how-to-backport-rust` guide instead.
- To see the process of fixing an existing Rust package, consult the {ref}`how-to-patch-rust` guide instead.

:::{attention}
This is _not_ a guide for updating your system's Rust toolchain. This guide is intended only for Ubuntu toolchain package maintainers seeking to add new Rust versions to the Ubuntu Archive.
:::

## Background

The `rustc` {term}`source package`, which provides {term}`binary packages <binary package>` for the Rust toolchain, is a _versioned_ package. This means that a new source package is created for every Rust release (e.g., {lpsrc}`rustc-1.83` and {lpsrc}`rustc-1.84`).

These packages are maintained largely in order to support building other Rust packages in the {term}`Ubuntu archive`. Rust developers seeking to work on their own Rust programs typically use the [`rustup` snap](https://snapcraft.io/rustup) instead.

The default Rust toolchain version used to build Rust packages in the archive is denoted using the {lpsrc}`rust-defaults` package.

---

## High-Level Summary of the Update Process

A typical `rustc` update goes through the following steps:

1. The source code of the new Rust version is downloaded from upstream, overwriting the old upstream source code.
1. The existing package {term}`patches <patch>` are refreshed so they apply properly onto the new Rust source code.
1. Unnecessary {term}`vendored <vendored dependency>` dependencies are pruned.
1. The upstream Rust source is re-downloaded with the new list of files to yank out, overwriting the source code once again, but with the unnecessary files removed.

---

```{include} common/substitution-terms.md

```

```{include} common/local-repo-setup.md

```

## The Rust Update

This section details the process of the actual Rust package update, which is repeated every time a new upstream Rust release comes out.

(updating-rust-creating-a-bug-report)=

### Creating a Bug Report

In order to publicly track the progress and status of the update, you must create a bug report on Launchpad. The type of bug report you create depends on whether or not this Rust version will be the default for the current {term}`devel` release.

#### Bug report for the default release

If this Rust version is the target `rust-defaults` version for devel, then you should create a bug under [`rust-defaults`](https://launchpad.net/ubuntu/+source/rust-defaults). This is because you will eventually need to update `rust-defaults` to point to this new Rust version. As an example, consult this real-life `rust-defaults` {lpbug}`bug report <2109761>`.

#### Bug report for non-default releases

If this Rust version is _not_ the target default for devel, then the process is closer to adding a [new package](https://wiki.ubuntu.com/UbuntuDevelopment/NewPackages) to the archive in general. You can create a general Ubuntu bug tagged with `needs-packaging` and Wishlist importance. A real-life bug report for `rustc-1.86` can {lpbug}`be found here <2117513>`. Notice that it is targeted to the appropriate {term}`series` and tagged accordingly.

### Setting Up

You're now ready to start work on the next Rust version. To begin, you must create a new Git branch titled `merge-<X.Y>`. All new Rust branches for devel use this naming convention.

First, make sure you're on the previous version's branch:

```none
$ git fetch --all
$ git checkout merge-<X.Y_old>
```

Create your new branch, then upload it to your personal Git repo:

```none
$ git checkout -b merge-<X.Y>
$ git push <lpuser> merge-<X.Y>
```

### Getting the New Upstream Rust Source

In this step, you get the source code of the new Rust version. The {term}`watch file`, `debian/watch`, automates this process.

#### Updating the changelog and package name

:::{important}
The changelog version string is complicated. It's _strongly recommended_ to consult the {ref}`rust-version-strings` article before making this change to ensure you understand the version string.
:::

First, update the {term}`changelog` at `debian/changelog`, manually setting the version number:

```none
$ dch -v <X.Y.Z>+dfsg-0ubuntu1
```

You must also update the versioned package name in the changelog, i.e., `rustc-<X.Y_old>` -> `rustc-<X.Y>`

Finally, within the changelog entry, you must declare the new Rust version you're packaging, including the Launchpad bug number.

Your new changelog entry should look similar to this:

```none
rustc-<X.Y> (<X.Y.Z>+dfsg-0ubuntu1) <release>; urgency=medium

  * New upstream version <X.Y.Z> (LP: #<lp_bug_number>)

 -- Jane Doe <example@example.com>  Thu, 01 Jan 1970 00:00:00 -0000
```

:::{important}
Make sure `<lp_bug_number>` matches the bug number you created earlier!
:::

(updating-rust-including-all-vendored-dependencies)=

#### Temporarily including all vendored dependencies

Later on in the upgrade process, unwanted {term}`vendored dependencies <vendored dependency>` will be pruned from the upstream source. Right now, however, we don't know _which_ dependencies must be pruned, so we must temporarily include _all_ vendored dependencies.

_Temporarily_ modify `debian/copyright`, commenting out the line in `Files-Excluded` which excludes the `vendor/` directory from the {term}`orig tarball`:

```diff
--- a/debian/copyright
+++ b/debian/copyright
@@ -10,7 +10,7 @@ Files-Excluded:
 # Pre-generated docs
  src/tools/rustfmt/docs
 # Exclusions on the vendor/ dir should be in Files-Excluded-vendor
- vendor
+# vendor
 # DOCX versions of TRPL book prepared for No Starch Press
  src/doc/book/nostarch/docx
 # Exclude submodules https://github.com/rust-lang/rust/tree/master/src/tools
```

:::{important}
Remember, this change shouldn't be committed to version control. It's just a temporary measure for the next step.
:::

This means that in the next step, _all_ vendored dependencies will be included in the tarball.

(updating-rust-getting-the-new-source-and-orig-tarball-with-uscan)=

#### Getting the new source and orig tarball with uscan

```{include} common/uscan.md

```

You are now free to restore `debian/copyright` to its original state, un-commenting the `vendor` line in `Files-Excluded`:

```none
$ git restore debian/copyright
```

Since this particular tarball contains all vendored dependencies and will therefore be different from the final tarball, it should be renamed with an `~old` suffix, like so:

```none
$ mv ../rustc-<X.Y>_<X.Y.Z>+dfsg{1,~old}.orig.tar.xz
```

(updating-rust-updating-the-source-code-in-your-repository)=

#### Updating the source code in your repository

`uscan` just downloads the new Rust source, yanks out the ignored files, and packs the orig tarball. Your actual Git repository hasn't changed at all yet. To do that, we can use `gbp` to import the new Rust source code onto your existing repository.

:::{note}
This is point at which your _actual source code_ moves from `<X.Y.Z_old>` to `<X.Y.Z>`.
:::

We use the `experimental` branch to store the upstream releases. Normally, this would be where the Debian `experimental` branch is, but we can't use that because our Rust package is not downstream from Debian. Make sure you reset this branch beforehand, branching it off from your current Git branch:

```none
$ git branch -D experimental
$ git branch experimental
```

Now, we're ready to invoke `gbp`:

```none
$ gbp import-orig \
    --no-symlink-orig \
    --no-pristine-tar \
    --upstream-branch=experimental \
    --debian-branch=merge-<X.Y> \
    ../rustc-<X.Y>_<X.Y.Z>+dfsg~old.orig.tar.xz
```

Afterwards, you should now see two commits in your Git log stating that your upstream source has been updated.

It can be useful to be able to return to this point just in case you make a mistake repacking the tarballs. It's recommended to create a branch here for safekeeping:

```none
git branch import-old-<X.Y>
git push <lpuser> import-old-<X.Y>
```

(updating-rust-initial-patch-refresh)=

### Initial Patch Refresh

Now that the actual upstream source code has changed, many of the different patches in `debian/patches` won't apply cleanly. In this step, you must fix these patches.

#### Getting the next patch to refresh

To identify the next patch that fails to apply, try to push all the patches:

```none
$ quilt push -a
```

`quilt` will then stop applying patches right before the patch that fails to apply. You can then force-apply this patch, displaying the conflicts in a Git-style merge conflict format:

```none
$ quilt push -f --merge
```

The response you get from this command will list all of the patch components which failed to apply.

There are several common reasons why a patch fails to apply. These reasons are listed below.

#### Surrounding code changed

The easiest situation is that the surrounding code was changed.

In this case, you must simply verify that the changes don't impact the patch itself before re-applying it to this new context.

#### Patch implemented upstream

Sometimes, a patch has changes that were incorporated upstream.

In this case, you can drop the patch entirely by deleting the `.patch` file itself and removing it from `debian/patches/series`.

#### Vendored dependency changed

Whenever a vendored dependency gets updated, patches which apply to vendored dependencies won't be able to find their target files because the file paths have changed.

The easiest solution in this case is to manually edit the target file paths within the `.patch` file, then try to reapply the patch and solve any remaining conflicts from there.

#### Targeted code refactored

The most difficult case to deal with is when the code impacted by a patch is refactored or replaced entirely.

In this case, you must consult the upstream changes to figure out what replaced it, then act accordingly, modifying or dropping the patch if warranted.

Remember, your goal here is to preserve the _intent_ of the patch. If, for example, a patch disables certain tests which require an internet connection, and those tests get refactored completely, it's your responsibility to track down the tests which require an internet connection and disable them accordingly.

(updating-rust-pruning-unwanted-dependencies)=

### Pruning Unwanted Dependencies

As mentioned above, we don't want to include unnecessary dependencies, especially Windows-related crates like `windows-sys`. This pruning ensures adherence to free software principles, reduces the attack surface of the binary packages, and reduces the binary package size on the end user's hard drive.

Since we [included all vendored dependencies](updating-rust-including-all-vendored-dependencies) before [getting the upstream source](updating-rust-getting-the-new-source-and-orig-tarball-with-uscan), our `vendor` directory will contain _everything_. We must now remove the dependencies on things we don't need.

#### Generating the pruned vendor tarball component

In addition to the standard orig tarball containing all the upstream code, the Rust toolchain Ubuntu package also comes with an additional {term}`orig tarball` component called `vendor`. This tarball component contains _just_ the pruned vendored dependencies of the Rust toolchain.

[`cargo-vendor-filterer`](https://crates.io/crates/cargo-vendor-filterer/) is used to generate a pruned vendor directory. It's recommended to download the `rustup` snap, use `rustup` to download the toolchain matching your target version, then install `cargo-vendor-filterer` for that Rust installation:

```none
# snap install rustup
$ rustup install <X.Y.Z>
$ cargo +<X.Y.Z> install cargo-vendor-filterer
```

Make sure that `~/.cargo/bin` is in your `$PATH`, otherwise you won't be able to run `cargo-vendor-filterer`.

(updating-rust-vendor-tarball-rule)=

After that, call the `vendor-tarball` rule in `debian/rules`. This will use `cargo-vendor-filterer` to generate a vendor directory which _only_ contains the dependencies required by supported Ubuntu targets. It then repacks this directory into the `vendor` tarball component. Make sure you point it to your installed Rust toolchain via `RUST_BOOTSTRAP_DIR`:

```none
$ RUST_BOOTSTRAP_DIR=~/.rustup/toolchains/<X.Y.Z>-x86_64-unknown-linux-gnu/bin/rustc \
    debian/rules vendor-tarball
```

You should now see a new tarball in the parent directory: `../rustc-<X.Y>_<X.Y.Z>+dfsg.orig-vendor.tar.xz`. In later steps, we will use this to replace the existing `vendor/` directory.

### Removing Vendored C Libraries

Unlike C, Rust doesn't have a stable ABI, meaning that dependencies (generally) must be statically linked to the binary. An [excellent article](https://blogs.gentoo.org/mgorny/2021/02/19/the-modern-packagers-security-nightmare/) by a Gentoo maintainer goes more in depth regarding the conflicts between Linux packaging and static dependencies.

This is relevant because while we must vendor Rust dependencies, we _don't_ have to vendor the C libraries included within some vendored crates. This can be seen in the `Files-Excluded` field of `debian/copyright`:

```none
Files-Excluded:
 ...
# Embedded C libraries
 vendor/blake3-*/c
 vendor/curl-sys-*/curl
 vendor/libdbus-sys-*/vendor
 vendor/libgit2-sys-*/libgit2
 ...
```

Subdirectories _within_ vendored crates are being pruned from the orig tarball. They are replaced by the _system_ C libraries, thoughtfully provided in the Ubuntu archive. Considering the exclusion of `vendor/libgit2-sys-*/libgit2` above, we can consult `debian/control`:

```none
Build-Depends:
 ...
 libgit2-dev (>= 1.9.0~~),
 libgit2-dev (<< 1.10~~),
 ...
```

These two changes form the basis of removing vendored C dependencies.

#### Finding vendored C dependencies

Search for C source files within your newly-pruned `vendor` tarball:

```none
tar -tJf ../rustc-<X.Y>_<X.Y.Z>+dfsg.orig-vendor.tar.xz | grep '\.c$'
```

:::{note}
You don't want to search your unpacked source directory right now because it contains a bunch of things we just pruned in the [previous step](updating-rust-pruning-unwanted-dependencies).
:::

Individual C files are likely fine. You're just looking for entire C libraries which have been bundled in with vendored crates.

#### Removing C dependencies from the vendored orig tarball

Naturally, the process of pruning a vendored C library varies from library to library. As an example, we will use a removal of the bundled `oniguruma` library from `rustc-1.86`, which caused some {lpbug}`build failures <2119556>` when it wasn't removed.

To do this, simply add the C library directory to `Files-Excluded-vendor` in `debian/copyright`:

```diff
--- a/debian/copyright
+++ b/debian/copyright
@@ -52,6 +52,7 @@ Files-Excluded-vendor:
  vendor/libsqlite3-sys-*/sqlcipher
  vendor/libz-sys-*/src/zlib*
  vendor/lzma-sys*/xz-*
+ vendor/onig_sys*/oniguruma
 # Embedded binary blobs
 # vendor/jsonpath_lib-*/docs
  vendor/mdbook-*/src/front-end/playground_editor
```

:::{caution}
Remember, this new exclusion should be under `Files-Excluded-vendor`, _not_ `Files-Excluded`! The primary tarball doesn't contain anything in the `vendor/` directory.
:::

After that, return to the previous step and [regenerate the vendored tarball component](updating-rust-vendor-tarball-rule). The `vendor-tarball` rule will read your new `debian/copyright` and generate a new vendor tarball without the C library source code you just excluded.

#### Adding the system library as a build dependency

We can't remove a C library needed by a vendored dependency without providing a proper equivalent of said library in its place. Instead, we can use the oniguruma Ubuntu package, {lpsrc}`libonig-dev`. We do this by adding the package to `Build-Depends` in `d/control` AND `d/control.in`:

```diff
--- a/debian/control
+++ b/debian/control
@@ -37,6 +37,7 @@ Build-Depends:
  libgit2-dev (<< 1.10~~),
  libhttp-parser-dev,
  libsqlite3-dev,
+ libonig-dev,
 # test dependencies:
  binutils (>= 2.26) <!nocheck> | binutils-2.26 <!nocheck>,
  git <!nocheck>,
```

```diff
--- a/debian/control.in
+++ b/debian/control.in
@@ -37,6 +37,7 @@ Build-Depends:
  libgit2-dev (<< 1.10~~),
  libhttp-parser-dev,
  libsqlite3-dev,
+ libonig-dev,
 # test dependencies:
  binutils (>= 2.26) <!nocheck> | binutils-2.26 <!nocheck>,
  git <!nocheck>,
```

#### Making the vendored crate use the system library instead

In all likelihood, you'll need to adjust the vendored crate so it knows to use the system library instead of the bundled one. This can vary greatly, but it usually involves patching the crate's `Cargo.toml` or `build.rs`, so look in those places first.

In the case of `onig_sys`, we can simply patch it to use the system library by default:

```diff
--- a/vendor/onig_sys-69.8.1/build.rs
+++ b/vendor/onig_sys-69.8.1/build.rs
@@ -219,7 +219,7 @@

 pub fn main() {
     let link_type = link_type_override();
-    let require_pkg_config = env_var_bool("RUSTONIG_SYSTEM_LIBONIG").unwrap_or(false);
+    let require_pkg_config = env_var_bool("RUSTONIG_SYSTEM_LIBONIG").unwrap_or(true);

     if require_pkg_config || link_type == Some(LinkType::Dynamic) {
         let mut conf = Config::new();
```

### Updating the Source Tree Again

At this point, you've updated the list of files which must be excluded from the upstream source. This means that you need a new upstream tarball and a new Rust source.

We download the upstream Rust source code using `uscan` again, which will use your new `debian/copyright` exclusion list to yank out everything you just pruned:

```none
$ uscan --download-version <X.Y.Z> -v 2>&1 | tee <path_to_log_output>
```

Since we've now updated the orig tarball repack, we can rename this new orig tarball by making its last number `1`, i.e., `rustc-<X.Y>_<X.Y.Z>+dfsg0ubuntu1`, symbolizing that we've repacked the source once again.

We can also update our `debian/changelog` version number to `<X.Y.Z>+dfsg0ubuntu1-0ubuntu1`. Make sure that the portion of the version number before the hyphen matches the new orig tarball. You can use `dch -r` to automatically bump the changelog timestamp.

#### Keeping the tree clean

To keep the Git tree clean, we must rebase all our changes on top of the newly-packed orig tarball.

First, make a backup just to be safe:

```none
$ git branch backup
```

Next, start an interactive rebase, dropping the `gbp` commit where we [imported the upstream source](updating-rust-updating-the-source-code-in-your-repository):

```none
$ git rebase -i merge-<X.Y_old>
```

Here's an example of what the 1.87 rebase todo looked like. Note that we took the opportunity to clean up the Git tree in general: squashing the large list of vendored pruning commits into one, dropping the initial removal of the old auto-generated `Files-Excluded` chunk, etc.:

```none
drop f24d250953b Remove autogenerated Files-Excluded chunk
pick 222264f2705 Create 1.87.0 changelog entry
drop 93acc98c031 New upstream version 1.87.0+dfsg0ubuntu0
pick ec0e3f69232 Refresh upstream/u-ignore-ppc-hangs.patch
squash 7c73c0c7640 Refresh upstream/u-hurd-tests.patch
squash a7aecdca8cc Refresh upstream/d-ignore-test_arc_condvar_poison-ppc.patch
[...]
squash 8269adcb6d8 Refresh ubuntu/ubuntu-enzyme-use-system-llvm.patch
pick d045017bed6 d/p/series: Drop u-mdbook-robust-chapter-path.patch applied upstream
pick 960395225de Prune termcolor-1.1.2
squash 0c8624920e7 Prune ring-0.16.20
squash b5316157d1f Prune mio-1.0.1
[...]
squash d0696832bf1 Prune openssl-sys from libssh2-sys-0.2.23
pick 1239a9b4309 d/control, d/s/lintian-overrides: Update versioned identifiers
pick 713e26dc275 d/copyright: Update Files-Excluded with newly-pruned vendored crates
pick 3a590ea16cd d/copyright: Remove src/tools/rls from Files-Excluded (dropped upstream)
pick 46d9e994fbd Update changelog
```

:::{important}
Remember, the only change that's actually necessary for this step is the dropping of the `New upstream version <X.Y.Z>+dfsg0ubuntu0` commit.
:::

After the interactive rebase, we can go back to the previous Rust version and re-import the new orig tarball:

```none
$ git checkout merge-<X.Y_old>
$ git checkout -b import-new-<X.Y>
```

Recreate the `experimental` branch:

```none
$ git branch -D experimental
$ git branch experimental
```

Then, we can merge our newly-pruned upstream source onto the previous Rust version's source cleanly:

```none
$ gbp import-orig \
    --no-symlink-orig \
    --no-pristine-tar \
    --upstream-branch=experimental \
    --debian-branch=import-new-<X.Y> \
    ../rustc-<X.Y>_<X.Y.Z>+dfsg0ubuntu1.orig.tar.xz
```

Finally, we can switch back to our actual branch and rebase:

```none
$ git checkout merge-<X.Y>
$ git rebase import-new-<X.Y>
```

Consulting your `git log`, you should see the two new `gbp` commits immediately after the final commit of the last Rust version.

#### Verifying your Git changes

Before you force-push to your personal Launchpad remote, you must be absolutely sure you didn't miss anything. Compare your branch with your `backup` branch:

```none
$ git diff backup --name-status
```

You should **only** see a huge list of deleted `vendor` files.

:::{warning}
If there are _any other changes_ apart from deleted `vendor` files, then you made a mistake during the rebase — reset to your backup branch and try again.
:::

Once you're absolutely sure everything is good, you may safely delete your `import-new-<X.Y>` and `backup` branches. This is also a good time to force-push to your `<lpuser>` remote.

### After-Repack Patch Refreshes

Some of the patches will no longer apply now that more files have been removed. You must refresh all the patches so they once again apply cleanly onto the newly-pruned source.

In general, you will follow the same protocol as the [initial patch refresh](updating-rust-initial-patch-refresh).

Naturally, many lines will be removed from `debian/patches/prune/d-0021-vendor-remove-windows-dependencies` because many of the vendored crates you pruned were _themselves_ unnecessary.

### Updating XS-Vendored-Sources-Rust

Inside of `debian/control` and `debian/control.in`, there's a special field called `XS-Vendored-Sources-Rust` which must be updated. It simply lists all the vendored crate dependencies, along with their version numbers, on a single line.

Luckily, the {lpsrc}`dh-cargo` package contains a script for automatically generating this line. Push all your patches, then run the script:

```none
$ quilt push -a
$ CARGO_VENDOR_DIR=vendor/ /usr/share/cargo/bin/dh-cargo-vendored-sources
```

Copy-paste the expected value it provides to both `debian/control` AND `debian/control.in`.

:::{attention}
Make sure there's still an empty line after the end of the field! Mistakenly dropping the empty line will result in a build failure right at the end of the test build.
:::

#### Outdated toolchain issues

If you're running a pre-versioned Rust Ubuntu release, then there's a decent chance the `cargo` installation required by `dh-cargo` will be too old. In this case, don't use `dh-cargo`—instead, manually download [`dh-cargo-vendored-sources`](https://git.launchpad.net/ubuntu/+source/dh-cargo/tree/dh-cargo-vendored-sources) (it's just a Perl script) and use it _without_ deb-based installations of Rust, which ensures that the Rustup snap's version will be used instead.

### Updating debian/copyright

All the new `vendor` files must be added to `debian/copyright`. Luckily, we can use a script which uses {term}`Lintian` ({manpage}`lintian(1)`) to generate all the missing copyright stanzas.

This script requires `pytoml`, so we must create and enter a virtual environment.

```none
# apt install python3-venv
```

Create the virtual environment somewhere convenient, such as `~/.venvs/`:

```none
$ python3 -m venv rustc-lintian-to-copyright
```

After that, enter the virtual environment and install `pytoml`:

```none
$ source ~/.venvs/rustc-lintian-to-copyright/bin/activate
$ which python3
$ python3 -m pip install pytoml
```

Temporarily edit `debian/lintian-to-copyright.sh` to recognize the virtual environment:

```diff
@@ -1,5 +1,5 @@
 #!/bin/sh
 # Pipe the output of lintian into this.
 sed -ne 's/.* file-without-copyright-information //p' | cut -d/ -f1-2 | sort -u | while read x; do
-       /usr/share/cargo/scripts/guess-crate-copyright "$x"
+   python3 /home/maxgmr/rustc/rustc/debian/scripts/guess-crate-copyright "$x"
 done
```

[Clean up previous build artifacts](updating-rust-clean-build), build the source package using {manpage}`dpkg-buildpackage(1)`, then run Lintian and pipe the output to the script:

```none
$ dpkg-buildpackage -S -I -i -nc -d -sa
$ lintian -i -I -E --pedantic | debian/lintian-to-copyright.sh
```

Leave the virtual environment afterwards:

```none
$ deactivate
```

You may need to fill in some fields manually. [This](https://stackoverflow.com/questions/23611669/how-to-find-the-created-date-of-a-repository-project-on-github) is an easy way to find the start date of a GitHub repo.

Keep things clean by adding the new `d/copyright` stanzas alphabetically. It makes things a lot easier in the long run.

```{include} common/local-build.md

```

(updating-rust-lintian-checks)=

```{include} common/lintian-checks.md

```

```{include} common/ppa-build.md

```

(updating-rust-autopkgtests)=

### autopkgtests

:::{seealso}
[Ubuntu Maintainers' Handbook - Running Package Tests](https://github.com/canonical/ubuntu-maintainers-handbook/blob/main/PackageTests.md)

[Ubuntu Wiki - autopkgtests](https://wiki.ubuntu.com/ProposedMigration#autopkgtests)
:::

The comprehensive suite of tests included with the Rust toolchain source code is run every time the package is built. _These_ tests, however, only check to see how the package _itself_ functions — _not_ how the package interacts with other packages in a real Ubuntu system.

{term}`autopkgtests <autopkgtest>` fill this role. autopkgtests are tests for the _installed package_. For a package to {term}`migrate <proposed migration>` from the `-proposed` {term}`pocket` to the `-release` pocket, all autopkgtests must pass.

Currently, the Rust toolchain package has two autopkgtests:

1. Use _the installed Rust toolchain_ (i.e. this package) to build the current Rust compiler from scratch
1. Use [`cargo`](https://doc.rust-lang.org/cargo/) to build, test, and run a ["Hello, World!"](https://en.wikipedia.org/wiki/%22Hello,_World!%22_program) binary crate with a `1 + 1 = 2` unit test and external [`anyhow`](https://docs.rs/anyhow/latest/anyhow/) dependency

Naturally, the first test requires a considerable amount of time and resources. In fact, you'll likely need to request more resources for the test runner.

#### Checking autopkgtest resource usage locally

We must experimentally verify that the default resources allocated to the autopkgtest test bed are insufficient. By default, autopkgtests are run using limited resources, but select packages can be added to the [`big_packages`](https://git.launchpad.net/~ubuntu-release/autopkgtest-cloud/+git/autopkgtest-package-configs/tree/big_packages) list to be granted more resources. This can be done locally using {manpage}`autopkgtest(1)` and {manpage}`qemu-system-x86_64(1)`.

(updating-rust-creating-local-test-beds)=

#### Creating local test beds

If this is your first time running Rust autopkgtests locally, you must create two local test beds.

There are multiple [Openstack flavours](https://wiki.ubuntu.com/ProposedMigration#autopkgtests) used to run autopkgtests. Compare the default `m1.small` unit resources with the `m1.large` unit resources:

| Unit       | RAM Size (MB) | CPU Cores | Disk Size (GB) |
| ---------- | ------------- | --------- | -------------- |
| `m1.small` | 4096          | 2         | 20             |
| `m1.large` | 8192          | 4         | 100            |

Packages in the `big_packages` list use `m1.large`. Therefore, we'll make one testbed modelled after `m1.small` and another modelled after `m1.large` and use them to determine whether or not we must add this Rust package to `big_packages`.

In a convenient place, e.g. `~/test_beds`, create the default test bed using {manpage}`autopkgtest-buildvm-ubuntu-cloud(1)` and rename it accordingly:

```none
$ autopkgtest-buildvm-ubuntu-cloud -v -r <release>
$ mv autopkgtest-<release>-<arch>.img autopkgtest-<release>-<arch>-default.img
```

Then, in the same place, create a `big_packages` test bed:

```none
$ autopkgtest-buildvm-ubuntu-cloud -s 100G --ram-size=8192 --cpus=4 -v -r <release>
$ mv autopkgtest-<release>-<arch>.img autopkgtest-<release>-<arch>-big.img
```

#### Verifying the necessity of big_packages

First, run the autopkgtests locally using the default test bed to check if the default Openstack flavour resources are sufficient for this build:

:::{note}
The `--log-file` option is picky. It doesn't do bash path expansions and the log file needs to exist already.
:::

```none
$ autopkgtest rustc-<X.Y> \
    --apt-upgrade \
    --shell-fail \
    --add-apt-source=ppa:<lpuser>/rustc-<X.Y>-merge \
    --log-file=<path/to/log/file> \
    -- \
    qemu \
    --ram-size=4096 \
    --cpus=2 \
    <path/to/test/bed/autopkgtest-<series>-<arch>-default.img
```

If the autopkgtests pass, then you are ready to [run the autopkgtests for real](updating-rust-running-the-actual-ppa-autopkgtests). No further action is necessary. Otherwise, consult the log for something like the following:

```none
Did not run successfully: signal: 9 (SIGKILL)
rustc exited with signal: 9 (SIGKILL)
```

If you see this, then the default autopkgtest resources are insufficient. To verify that adding your package to `big_packages` will fix the problem, you must now try the autopkgtests again using the big testbed you [set up earlier](updating-rust-creating-local-test-beds):

```none
$ autopkgtest rustc-<X.Y> \
    --apt-upgrade \
    --shell-fail \
    --add-apt-source=ppa:<lpuser>/rustc-<X.Y>-merge \
    --log-file=<path/to/log/file> \
    -- \
    qemu \
    --ram-size=8192 \
    --cpus=4 \
    <path/to/test/bed/autopkgtest-<series>-<arch>-big.img
```

If _these_ autopkgtests pass, then you have successfully proven that the default autopkgtest runner will not have enough resources.

#### Getting more resources for the autopkgtests

We need to make sure that when the autopkgtests are run for real, they're run on the larger test bed profile.

To do this, create a merge proposal in the [`autopkgtest-package-configs` repo](https://code.launchpad.net/~ubuntu-release/autopkgtest-cloud/+git/autopkgtest-package-configs) adding the new Rust version to the list of `big_packages`, which are granted the 100GB disk space, 8192MiB of memory, and 4 vCPUs we used earlier.

Launchpad may autofill the incorrect default branch. Make sure you double-check the target repository into which you're merging — you want to merge into `autopkgtest-package-configs`, NOT `autopkgtest-cloud`.

The change itself is trivial:

```diff
--- a/big_packages
+++ b/big_packages
@@ -174,6 +174,7 @@ rsass
 ruby-minitest
 ruby-parallel
 rustc
+rustc-<X.Y>
 rust-ahash
 rust-axum/ppc64el
 rust-cargo-c/ppc64el
```

For an example on how to format this merge proposal, you can see a real-life proposal [here](https://code.launchpad.net/~maxgmr/autopkgtest-cloud/+git/autopkgtest-package-configs/+merge/489449).

(updating-rust-running-the-actual-ppa-autopkgtests)=

#### Running the actual PPA autopkgtests

```{include} common/running-autopkgtests.md

```

### Uploading the Package

You're nearly ready to request sponsorship. First, it's your duty to make your sponsor's job _as easy as possible_.

(updating-rust-obtaining-the-right-info)=

#### Obtaining the right info

```{include} common/obtaining-upload-info.md

```

#### The i386 allowlist

We must ask an {term}`Archive Admin` to add the new `rustc-<X.Y>` package to the i386 allowlist so it can be added to the [new upload queue](https://launchpad.net/ubuntu/devel/+queue).

Usually, the easiest and fastest thing way of doing this is just messaging an Archive Admin directly, politely asking them to add `rustc-<X.Y>` to the i386 allowlist and providing them a link to the [bug report](updating-rust-creating-a-bug-report).

#### Requesting a review

Once your comment is ready, subscribe `ubuntu-sponsors` to your bug to make it visible for sponsorship and upload.

After that, go to the [bug report you originally opened](updating-rust-creating-a-bug-report) and add a comment providing [all the necessary info](updating-rust-obtaining-the-right-info) you compiled earlier.

An example of such a comment can be found at the `rustc-1.87` bug report [here](https://bugs.launchpad.net/ubuntu/+source/rustc-1.87/+bug/2118790/comments/1).

:::{note}
You will likely have difficulties finding a sponsor just by subscribing `ubuntu-sponsors`. You're uploading a new package and it's large and complicated. To get a timely sponsorship, it's better to reach out to the Foundations or Toolchains teams and personally request sponsorship that way.
:::

### Toolchain Availability Page

```{include} common/toolchain-availability.md

```

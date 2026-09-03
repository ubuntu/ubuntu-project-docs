(how-to-package-a-rust-binary-crate)=
# How to package a Rust binary crate

This is a practical step-by-step tutorial for creating an Ubuntu
{term}`binary package` of a Rust binary
[crate](https://doc.rust-lang.org/book/ch07-01-packages-and-crates.html). For a
general background of Rust
packaging in Debian and Ubuntu, consult the
[Debian Rust Team Book](https://rust-team.pages.debian.net/book/intro.html).

This guide assumes you have the standard development tools set up on your
system. Consult the
{ref}`getting set up <how-to-set-up-for-ubuntu-development>` article for more
information.

In this tutorial, you will create an Ubuntu package for
[`prettyhello`](https://crates.io/crates/prettyhello), a simple Rust application
which prints a colourful greeting tailored to your operating system.

:::{important}
This is *not* a general guide to Ubuntu packaging. This guide is targeted
towards experienced package maintainers who wish to know how to package binary
Rust crates.
:::


## Setting up the package with `debcargo`

{manpage}`debcargo(1)` automatically translates an {term}`upstream` crate from
[crates.io](https://crates.io/) to a Debian/Ubuntu package. It does most of the
actual packaging work on its own.

Install `debcargo`:

```none
# apt update && apt install -y debcargo
```

Use {manpage}`debcargo-package(1)` to get `prettyhello` from `crates.io` and set
up the packaging files:

```none
$ debcargo package prettyhello
$ cd rust-prettyhello-0.2.1
```

The `debcargo` command will likely print the following lines:

```none
You (...) are not in Uploaders; adding "Team upload" to d/changelog
```

```none
FIXME found in the following files.
	•  rust-prettyhello-0.2.1/debian/changelog
	•  rust-prettyhello-0.2.1/debian/control
	•  rust-prettyhello-0.2.1/debian/copyright
```

This is normal. `debcargo` cannot infer all information about the package
automatically. Additionally, `debcargo` is primarily used by Debian Rust
packagers. Certain changes must be made because this package is for Ubuntu only,
not Debian. These changes shall be made later on in the tutorial.


## Introduction to the Rust package

`debcargo` performs the vast majority of packaging work automatically, but it's
useful to know the Rust-specific parts of the different package files.

If you are already familiar with Rust packages and you wish to immediately
continue the process of packaging `prettyhello`, you may skip directly to the
{ref}`Ubuntu-specific changes <package-rust-binary-ubuntu-changes>` section
below.


### Package name

Even though the Rust crate itself is called `prettyhello`, the Ubuntu package is
called `rust-prettyhello` due to Debian/Ubuntu Rust package
[naming policy](https://rust-team.pages.debian.net/book/policy.html#package-naming).
All Rust {term}`source package` names begin with `rust-`.


### `debian/cargo-checksum.json`

When [Cargo](https://doc.rust-lang.org/cargo/) is used to build Debian/Ubuntu
packages, it must verify the checksum of the crates it uses.
`cargo-checksum.json` is the checksum of the original {term}`upstream` crate
with the `"files"` section emptied so any applied {term}`patches <patch>` don't
trigger a checksum mismatch.


(package-rust-binary-debian-control)=
### `debian/control`

The Ubuntu/Debian {term}`archives <archive>` don't just contain binary crates—
they also contain many *library crate packages*. Unlike binary crate packages,
library crate packages in Ubuntu and Debian are just source code.

Usually, when a Debian/Ubuntu binary Rust package needs dependencies, instead of
using `crates.io`, it instead installs the needed library crate packages from
the archive into a local repository and uses those instead. Therefore, a Rust
crate's dependencies must correspond to actual library crate packages in the
archive.

:::{note}
While *most* Rust packages in Ubuntu use library crate packages from the
archive, not *all* of them do. Unique to Ubuntu, Rust packages in the
{term}`main` {term}`component` must have their dependencies
{term}`vendored <vendored dependency>`. Consult the
{ref}`Rust code in main<mir-rust>` article for more information on vendored
dependencies.
:::

In our example, `prettyhello` just has one dependency: `owo-colors` version 3 or
4. This can be verified in its `Cargo.toml`:

```toml
[dependencies]
owo-colors = ">=3, <5"
```

`debcargo` takes all direct and transitive dependencies of a Rust crate and
translates them into the following build dependencies in `debian/control`:

```none
Build-Depends-Arch: cargo:native,
 rustc:native (>= 1.85),
 libstd-rust-dev,
 librust-owo-colors+default-dev (<< 5),
 librust-owo-colors+default-dev (>= 3)
```

In this example, `owo-colors` does not have any transitive dependencies. The
`+default` in the package name signifies that only the default feature flags are
used.

Additionally, for purely informational purposes, `debian/control` contains two
additional custom fields denoting the upstream Rust crate name and version:

```none
X-Cargo-Crate: prettyhello
X-Cargo-Crate-Version: 0.2.1
```


### `debian/rules`

The file itself is short, but adding `--buildsystem cargo` to all
{manpage}`debhelper(7)` invocations significantly changes what certain
`debhelper` rules do behind the scenes. The modified rules are as follows:


(package-rust-binary-auto-configure)=
#### `dh_auto_configure`

The configure step consists of

1. copying the `debian/cargo-checksum.json` file to the place Cargo expects it
to be,
1. baking in flags used for all Rust package builds, and
1. writing a `config.toml` file which replaces the standard `crates.io` source
with a local directory registry.

The final step is needed because, as stated
{ref}`above <package-rust-binary-debian-control>`, most Rust binary packages in
Ubuntu must use the packaged Ubuntu library crates from the archive as their
source for dependencies.


#### `dh_auto_build`

Since `prettyhello` is a binary crate, nothing happens in this step. Rust
compilation is deliberately deferred to the
{ref}`installation step described below <package-rust-binary-auto-install>`.

For library crates, this step copies the crate source into a staging tree.


#### `dh_auto_test`

As shown in `debian/rules`, the testing step has been overridden to run
`cargo test --all`, meaning that the tests are run across the entire workspace,
not just the default package.


(package-rust-binary-auto-install)=
#### `dh_auto_install`

This step runs `cargo install`, which both compiles and places the built binary
in its intended place. Somewhat counterintuitively, this step is where all the
compilation of Rust code actually happens.

After compilation and installation, the `Built-Using` and `Static-Built-Using`
fields in `debian/control`are generated by inspecting the actual dependency
graph and statically linked libraries.

For library crates, this step does not compile anything—it simply copies the
staged source code into its intended system installation location.


#### `dh_auto_clean`

This step simply runs `cargo clean`, then removes the Cargo checksum file copied
over by the {ref}`configure step <package-rust-binary-auto-configure>`.


(package-rust-binary-ubuntu-changes)=
## Ubuntu-specific changes

`debcargo` is intended for Debian packages. Since Ubuntu is a Debian derivative,
most things work without issue, with a few exceptions:


### `debian/changelog`

`debcargo` likely added a "Team upload" line in `debian/changelog`. Since we are
uploading for Ubuntu and not as a member of the Debian Rust packaging team, this
line should be removed:

```diff
 rust-prettyhello (0.2.1-1) UNRELEASED-FIXME-AUTOGENERATED-DEBCARGO; urgency=medium
 
-  * Team upload.
   * Package prettyhello 0.2.1 from crates.io using debcargo 2.8.2
 
  -- Jane Doe <jane.doe@canonical.com>  Thu, 01 Jan 1970 00:00:00 -0700
```

Next, the {ref}`version string <version-strings>` must be fixed. Since
`prettyhello` is not packaged for Debian, use `-0` as the Debian revision and
set the Ubuntu revision to `ubuntu1`:

```diff
-rust-prettyhello (0.2.1-1) UNRELEASED-FIXME-AUTOGENERATED-DEBCARGO; urgency=medium
+rust-prettyhello (0.2.1-0ubuntu1) UNRELEASED-FIXME-AUTOGENERATED-DEBCARGO; urgency=medium
```

:::{tip}
See the {ref}`version string format docs <going-ahead-of-debian>` for an example
of packaging an upstream source not yet in Debian.
:::

Next, give your changelog entry the correct {term}`Ubuntu series <series>`
{term}`code name`. In this example, `resolute` shall be used for 26.04 LTS, but
but the current {term}`devel` release should be used here when following along:

```diff
-rust-prettyhello (0.2.1-0ubuntu1) UNRELEASED-FIXME-AUTOGENERATED-DEBCARGO; urgency=medium
+rust-prettyhello (0.2.1-0ubuntu1) resolute; urgency=medium
```


### `debian/control`

The `Maintainer:` field in `debian/control` is likely set to
`Debian Rust Maintainers`. Change this field to its proper Ubuntu value:

```diff
  librust-owo-colors+default-dev (<< 5),
  librust-owo-colors+default-dev (>= 3)
-Maintainer: Debian Rust Maintainers <pkg-rust-maintainers@alioth-lists.debian.net>
+Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
 Standards-Version: 4.7.3
 Vcs-Git: https://salsa.debian.org/rust-team/debcargo-conf.git [src/prettyhello]
```

Additionally, since this package isn't being developed by the Debian Rust Team,
the {term}`VCS` links may be removed:

```diff
 Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
 Standards-Version: 4.7.3
-Vcs-Git: https://salsa.debian.org/rust-team/debcargo-conf.git [src/prettyhello]
-Vcs-Browser: https://salsa.debian.org/rust-team/debcargo-conf/tree/master/src/prettyhello
 Homepage: https://github.com/maxgmr/prettyhello
 X-Cargo-Crate: prettyhello
```

Finally, the automatically generated description is insufficient. Write a better
one:

```diff
 Built-Using: ${cargo:Built-Using}
 Static-Built-Using: ${cargo:Static-Built-Using}
-Description: Pretty hello world
- This package contains the following binaries built from the Rust crate
- "prettyhello":
-  - prettyhello
+Description: Distro-specific hello world
+ This package prints a pretty coloured greeting dependent on the user's
+ OS/Linux distro.
```


### `debian/copyright`

`debcargo` has also assigned the copyright of the `./debian` directory to the
Debian Rust Team. Replace it with the Ubuntu team:

```diff
 Files: debian/*
-Copyright: 2027 Debian Rust Maintainers <pkg-rust-maintainers@alioth-lists.debian.net>
+Copyright: 2027 Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
 License: AGPL-3.0-or-later
```


### Manpage

The manpage included with the Rust crate (`./prettyhello.1`) must be installed
during the package build. To do so, create a new `debian/prettyhello.manpages`
file containing the path to that manpage:

```none
$ echo 'prettyhello.1' > debian/prettyhello.manpages
```


## Fixing `debcargo` issues

`debcargo` is unable to do everything autonomously and will likely need some
help. The following section details files with common `debcargo` issues and how
they must be fixed.


### `debian/control`

The proper `Section:` value must be given. Debian provides a
[full list](https://packages.debian.org/unstable/) of valid sections. In this
case, since `prettyhello` is a simple OS reporter, it belongs in the `utils`
section:

```diff
 Source: rust-prettyhello
-Section: FIXME-IN-THE-SOURCE-SECTION
+Section: utils
 Build-Depends: debhelper-compat (= 13),
  dh-sequence-cargo
```


### `debian/copyright`

The proper years must be given for the upstream crate copyright. In this
example, the crate is being packaged in 2027, but set the latter year to the
current year when following along. Additionally, remove the automatically
generated comment:

```diff
 Files: *
-Copyright: FIXME (overlay) UNKNOWN-YEARS Max Gilmour <max.gilmour@canonical.com>
+Copyright: 2026-2027 Max Gilmour <max.gilmour@canonical.com>
 License: AGPL-3.0-or-later
-Comment:
- FIXME (overlay): Since upstream copyright years are not available in
- Cargo.toml, they were extracted from the upstream Git repository. This may not
- be correct information so you should review and fix this before uploading to
- the archive.
```

If the `./LICENSE` file was given its own stanza, remove it. The license file is
bundled under the overall project's terms:

```diff
 Files: *
 Copyright: 2027 Max Gilmour <max.gilmour@canonical.com>
 License: AGPL-3.0-or-later
 
-Files: LICENSE
-Copyright: 2007 Free Software Foundation, Inc. <https://fsf.org/>
-License: UNKNOWN-LICENSE; FIXME (overlay)
-Comment:
- FIXME (overlay): These notices are extracted from files. Please review them
- before uploading to the archive.
-
 Files: debian/*
```


### Additional issues

Certain additional fixes may be necessary. To ensure that you have addressed all
potential issues, search for any remaining `FIXME`s in the package source tree:

```none
$ grep -r 'FIXME' .
```


## Test build

Your package is now ready to build. Run {manpage}`sbuild(1)` to test the package
build on your system, ensuring {manpage}`lintian(1)` checks are being run:

```none
$ sbuild --run-lintian
```

You should get a successful build with no Lintian warnings or errors (pedantic
or informational Lintian messages are OK).


## PPA build and installation

Create a {term}`PPA` to build the package:

```none
$ ppa create hello-rust
```

Build and upload the source package:

```none
$ dpkg-buildpackage -S -I -i -nc -d -sa
$ dput ppa:<lp_username>/hello-rust ../rust-prettyhello_0.2.1-0ubuntu1_source.changes
```


## Install and test the package

Once the PPA has build and published the package, install it in a {term}`LXC`
container of the current devel series. In this example, `resolute` is the devel
series:

```none
$ lxc launch ubuntu-daily:resolute hello-rust-test
$ lxc shell hello-rust-test
```

Add the PPA, update the package lists, and install the package:

```none
# add-apt-repository -y ppa:<lp_username>/hello-rust
# apt update
# apt install -y prettyhello
```

Finally, run the installed program and you should be greeted with a colourful
hello:

```none
$ prettyhello
```

Congratulations! You have successfully packaged a Rust binary crate for Ubuntu.

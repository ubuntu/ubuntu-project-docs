(rust-version-strings)=
# Rust version strings

The Rust version string format used in the {term}`Ubuntu archive` is complicated and contains certain unique features.
It's a combination of {term}`Debian` policy, Ubuntu conventions, and legacy code.
Although you will usually change only a few parts of the version string, it's a good idea to know what all of it means.

:::{important}
An understanding of how [Ubuntu version strings normally work](version-strings) is mandatory before this article can be read.
:::


## Full breakdown

Here, `<angle_brackets>` indicate placeholders to be edited, while `[square_brackets]` indicate optional parts.

```none
<rust_version>+dfsg0ubuntu<repack>[~bpo<vendored_dependencies>]-0ubuntu<revision>.[<ubuntu_release>][~ppa<PPA>]
```


## `<rust_version>`

> _The upstream Rust toolchain version._

This is simple; it's just the {term}`upstream` version of the given Rust toolchain. It's only updated when {ref}`adding a new Rust version to the archive <how-to-update-rust>`.

**Examples:**

- `1.88.0+dfsg0ubuntu1-0ubuntu1~ppa1`: Rust 1.88.0
- `1.87.0+dfsg0ubuntu1-0ubuntu1`: Rust 1.87.0
- `1.85.1+dfsg0ubuntu2-0ubuntu2~ppa3`: Rust 1.85.1
- `1.80.0+dfsg0ubuntu1~bpo2-0ubuntu0.24.09~ppa4`: Rust 1.80.0


(dfsg0ubuntu-repack)=
## `+dfsg0ubuntu<repack>`

> _The number of times you have edited Files-Excluded._

`dfsg` is short for "Debian {term}`free software` guidelines."
The presence of `+dfsg<whatever>` in any package indicates that the {term}`orig tarball` has been _repacked_ in some way.

Usually, this is done for copyright reasons.
However, in this case, we are doing it to make our tarballs smaller.
Rust comes with a lot of functionality that we don't need, most notably Windows support.
To save space, we use Debian's ability to _exclude_ all those unnecessary files from the tarball.
That way, we aren't hauling around megabytes of code the compiler is going to ignore anyways.

Returning to `+dfsg0ubuntu<repack>`, since we don't use Debian's upstream package, the number after `dfsg` shall always be `0`, because Debian won't have repacked the tarball.
We (`ubuntu`) have repacked it `<repack>` times.

Since we always repack the tarball when {ref}`updating the Rust version <how-to-update-rust>`, a newly-released versioned Rust package will always use `+dfsg0ubuntu1`.

:::{note}
The {ref}`how-to-update-rust` docs instruct you to start with `+dfsg0ubuntu0` in the version number.
This is because it's simply an interim number that will be replaced with `+dfsg0ubuntu1` once the package is ready for upload.
:::

**Examples:**

- `1.88.0+dfsg0ubuntu1-0ubuntu1~ppa1`: 1st repack
- `1.87.0+dfsg0ubuntu1-0ubuntu1`: 1st repack
- `1.85.1+dfsg0ubuntu2-0ubuntu2~ppa3`: 2nd repack
- `1.80.0+dfsg0ubuntu1~bpo2-0ubuntu0.24.09~ppa4`: 1st repack


## `[~bpo<vendored_dependencies>]`

> _Code number for what dependencies are {term}`vendored <vendored dependency>`._

This portion of the version string is applicable to {term}`backports <backport>` _only_.
More info on Rust backports can be found in {ref}`how-to-backport-rust`.

If you have {term}`vendored <vendored dependency>` LLVM or `libgit2` for your backport, then you must include this part.
Otherwise, then this portion must be omitted entirely.

`<vendored_dependencies>` is a code number:

- `0` when `libgit2` _and_ LLVM are vendored
- `2` when _only_ LLVM is vendored, and the system `libgit2` is used
- `10` when _only_ `libgit2` is vendored, and the system `LLVM` is used

**Examples:**

- `1.88.0+dfsg0ubuntu1-0ubuntu1~ppa1`: No vendored dependencies
- `1.87.0+dfsg0ubuntu1-0ubuntu1`: No vendored dependencies
- `1.85.1+dfsg0ubuntu2-0ubuntu2~ppa3`: No vendored dependencies
- `1.80.0+dfsg0ubuntu1~bpo2-0ubuntu0.24.09~ppa4`: Only LLVM is vendored
- `1.83.0+dfsg0ubuntu1~bpo0-0ubuntu0.24.09~ppa1`: Both `libgit2` and LLVM are vendored


## `0ubuntu<revision>`

> _The "real" version._

This is the component that actually indicates the number of times you have edited this particular package.
Every time you need to edit a particular version of Rust on a particular version of Ubuntu, you increment this number.

`<revision>` starts at 1.
When {ref}`creating a new Rust release package for the archive <how-to-update-rust>`, this portion will always be `0ubuntu1` upon upload to the archive.

:::{note}
The {ref}`how-to-update-rust` docs instruct you to start with `0ubuntu0` in the version number.
This is because it's simply an interim number that will be replaced with `0ubuntu1` once the package is ready for upload.
:::

When {ref}`updating an existing Rust toolchain in the archive <how-to-patch-rust>`, `<revision>` will be incremented.

This number gets reset back to 1 whenever {ref}`'repack' <dfsg0ubuntu-repack>` is incremented.
For example, repacking `1.82.0+dfsg0ubuntu1-0ubuntu3` means the new version number would be `1.82.0+dfsg0ubuntu2-0ubuntu1`.

**Examples:**

- `1.88.0+dfsg0ubuntu1-0ubuntu1~ppa1`: First Revision
- `1.87.0+dfsg0ubuntu1-0ubuntu1`: First Revision
- `1.85.1+dfsg0ubuntu2-0ubuntu2~ppa3`: Second Revision (#2)


## `[<ubuntu_release>]`

> _The Ubuntu release in case of backport, plus some hacks._

This portion of the version string is applicable to {term}`backports <backport>` _only_.
More info on Rust backports can be found in {ref}`how-to-backport-rust`.

In theory, this part is simple: it's the number of the Ubuntu release this backport is for.
In practice, however, there's a catch; while the backport is a work-in-progress, decrement the last number by 1.
That way it always sorts before the finalized version.

This portion is omitted entirely if this is not a backport.

**Examples:**

- `1.88.0+dfsg0ubuntu1-0ubuntu1~ppa1`: Not a backport
- `1.87.0+dfsg0ubuntu1-0ubuntu1`: Not a backport
- `1.80.0+dfsg0ubuntu1~bpo2-0ubuntu0.24.09`: WIP, for Ubuntu 24.10 (that's Oracular Oriole)
- `1.83.0+dfsg0ubuntu1-0ubuntu1.24.03~ppa3`: WIP, for Ubuntu 24.04 (that's Noble Numbat)
- `1.83.0+dfsg0ubuntu1~bpo0-0ubuntu1.24.04`: Complete, for Ubuntu 24.04 (again, Noble Numbat)


## `[~ppa<PPA>]`

> _The number of times you have pushed it to your PPA for testing._

Every time you make some changes, and want to check that it builds and passes tests by pushing it to your {term}`PPA`, you should increment this number.
This is because {term}`Launchpad` does not let you "re-upload" a version with the same version string but different source code.
Thus you have to make each PPA upload's version string different.
This is our convention for doing that.

Every time you change the rest of the version string in some way, you can reset this to 1.

If this part is _not_ present, that means it's on the main archive, so it's a version that's actually out.

:::{note}
{term}`Changelog` (`debian/changelog`) entries with `~ppa<PPA>` should should never make itonto a {term}`version control system`; they are only for the benefit of the PPA itself.
When working on a Rust toolchain locally, the PPA-specific changelog entry (and version string) should be removed after successful PPA upload.
:::

**Examples:**

- `1.88.0+dfsg0ubuntu1-0ubuntu1~ppa1`: First push to your PPA
- `1.87.0+dfsg0ubuntu1-0ubuntu1`: No PPA (i.e., real complete release)
- `1.85.1+dfsg0ubuntu2-0ubuntu2~ppa3`: 3rd push to your PPA


## Putting it all together

To recap, let's do a complete breakdown of some example version strings:

| String | `<rustc_version>` | `<repack>` | `~bpo<vendored_dependencies>` | `<revision>` | `<ubuntu_release>`                 | `~ppa<PPA>` |
| --- | --- | --- | --- | --- | --- | --- |
| `1.80.0+dfsg0ubuntu1~bpo2-0ubuntu0.24.09~ppa4` | 1.80.0 | 1 | 2, so only LLVM | 0 | In-dev backport for 24.10 (OO) | 4 |
| `1.88.0+dfsg0ubuntu1-0ubuntu1~ppa1` | 1.88.0 | 1 | System libgit2 and LLVM | 1 | Omitted b/c this is a normal port | 1 |
| `1.83.0+dfsg0ubuntu1~bpo0-0ubuntu1.24.03~ppa3` | 1.83.0 | 2 | 0, so both libgit2 and LLVM | 1 | In-dev backport for 24.03 (NN) | 3 |

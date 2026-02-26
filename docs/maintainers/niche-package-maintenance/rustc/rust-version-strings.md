(rust-version-strings)=
# Rust version strings

The Rust toolchain version string format used in the {term}`Ubuntu archive` is complicated and contains certain unique features.
It's a combination of {term}`Debian` policy, Ubuntu conventions, and legacy code.
Although you will usually change only a few parts of the version string, it's a good idea to know what all of it means.

:::{important}
An understanding of how [Ubuntu version strings normally work](version-strings) is mandatory before this article can be read.
:::


## Typical Rust version string

Components in `<angle brackets>` are required placeholders to be filled in, while components in `[square brackets]` are optional.

The version string format for a versioned `rustc-X.Y` {term}`source package` is as follows:

```none
<upstream_version>+dfsg[<repack_number>]-0ubuntu<ubuntu_revision>
```


### `<upstream_version>`

This component shows what upstream version of the Rust toolchain this package is. Since Ubuntu Rust toolchain packages are versioned, this number only changes if the upstream Rust Foundation releases a patch for the current release, e.g., `1.85.0` -> `1.85.1`.

If the Rust Foundation releases a new patch release, then the rest of the version number gets reset back to `+dfsg-0ubuntu1`.

> Example: `1.85.0+dfsg3-0ubuntu5` -> `1.85.1+dfsg-0ubuntu1`


(rust-repack-number)=
### `+dfsg[<repack_number>]`

This component signifies that the original upstream source has been modified from its original state, i.e., the {term}`orig tarball` has been repacked.

The `+dfsg` component is _always_ there because during the `rustc` update process, several unneeded dependencies are {ref}`pruned from the upstream source <pruning-unwanted-dependencies>`.

Normally, the `[<repack_number>]` can be elided entirely. However, if after the first release the {term}`orig tarball` must be repacked for whatever reason, a `[<repack_number>]` must be added afterwards, starting at `1`.

If this number must be incremented, then the `<ubuntu_revision>` (described in {ref}`rust-ubuntu-revision`) must be reset back to `1`.

> Example: `1.85.1+dfsg-0ubuntu3` -> `1.85.1+dfsg1-0ubuntu1`

Here are some examples of this component:

| Component | Meaning                                                              |
|-----------|----------------------------------------------------------------------|
| `+dfsg`   | This tarball has not been modified since the initial package upload. |
| `+dfsg1`  | This tarball has been modified after the original package upload.    |
| `+dfsg2`  | This tarball has been modified twice.                                |


(rust-ubuntu-revision)=
### `-0ubuntu<ubuntu_revision>`

Finally, this component shows how many modifications the Ubuntu maintainers have made to this Rust toolchain. For the first upload, `<ubuntu_revision>` starts at `1`.

The '`0`' at the start of the `0ubuntu<ubuntu_revision>` component signifies that this package is separate from Debian and is _never_ synced.

If the `[<repack_number>]` described [above](rust-repack-number) is ever added or incremented, `<ubuntu_revision>` is reset back to `1`.
Examples of this component:

| Component   | Meaning                                                  |
|-------------|----------------------------------------------------------|
| `-0ubuntu1` | Initial upload for the given upstream source.            |
| `-0ubuntu3` | The third Ubuntu revision for the given upstream source. |


### Example: Uploading and updating a new Rust toolchain

:::{list-table} Toolchain versions for various upload situations
:header-rows: 1

*   - Situation
    - Action
    - Version string
*   - Initial upload
    - Use the default
    - `1.95.0+dfsg-0ubuntu1`
*   - Fixing a bug
    - Increment `<ubuntu_revision>`
    - `1.95.0+dfsg-0ubuntu2`
*   - Pruning an unwanted dependency accidentally included in the orig tarball
    - Add a `1` after `+dfsg`, resetting `<ubuntu_revision>` back to `1`
    - `1.95.0+dfsg1-0ubuntu1`
*   - Upstream (Rust Foundation) creates a patch release for Rust 1.95
    - Update the `<upstream_version>`, resetting the rest of the version number
    - `1.95.1+dfsg-0ubuntu1`
*   - Uploading another Ubuntu-specific fix
    - Use new `<upstream_version>` and increment `<ubuntu_revision>`
    - `1.95.1+dfsg-0ubuntu2`
:::


## Rust backport version string

A {term}`backported <backport>` Rust toolchain follows the same rules as a normal upload, with a few modifications:

```none
<upstream_version>+dfsg[<repack_number>]~<series>[.<backport_repack>]-0ubuntu<ubuntu_revision>~<series>.<backport_revision>
```


### `~<series>[.<backport_repack>]`

During backporting, there are certain cases in which the Rust toolchain's dependencies can't be met because the archive is too old. When this happens, the dependencies must be {term}`vendored <vendored dependency>`, i.e., included in the orig tarball. (This commonly happens with [LLVM](rust-vendoring-llvm) and [`libgit2`](rust-vendoring-libgit2).)

When assigning a version number to a backport, the existing `[<repack_number>]` is untouched. Instead, `~<series>` is added, which shows that the repacked tarball is applied to this specific {term}`Ubuntu series <series>`. Note that the `~<series>` should always be added regardless of whether the orig tarball was modified for the backport. Likewise, when backporting to a different series, the `~<series>` should be updated regardless of whether the orig tarball was modified from the previous backport.

If, after the initial backport upload, the orig tarball must be modified _again_ for the same series, `[.<backport_repack>]` is added and incremented as necessary.
Examples of this component:

| Component       | Meaning                                                                                    |
|-----------------|--------------------------------------------------------------------------------------------|
| `+dfsg`         | The orig tarball in the original upload                                                    |
| `+dfsg~24.04`   | The orig tarball applied to a 24.04 backport (with or without modification)                |
| `+dfsg1`        | The orig tarball, revised in the original upload                                           |
| `+dfsg1~24.04`  | The revised orig tarball applied to a 24.04 backport                                       |
| `+dfsg1~24.04.1`| The revised orig tarball applied to a 24.04 backport, then revised later                   |

### `-0ubuntu<ubuntu_revision>~<series>.<backport_revision>`

The `<series>` number is added after the `<ubuntu_revision>` and will always be the same as the one in the orig tarball part of the version string. Although it duplicates the information already present in the first part of the version string, it gives context to the following `<backport_revision>` number and follows the convention commonly used for backports of other packages.

The `<backport_revision>` is added to the end of the version string, starting at `1`. This is incremented every time a change is made to the backport that doesn't affect the orig tarball. 

The `<backport_revision>` is reset back to `1` whenever any previous part of the version string is changed, e.g., if the orig tarball must be modified again, or if the backport is applied to a different series.

Here are some examples of this component:

| Component           | Meaning                                                             |
|---------------------|---------------------------------------------------------------------|
| `-0ubuntu3~22.04.1` | This is the initial upload of the 22.04 backport.                   |
| `-0ubuntu3~20.10.2` | This 20.10 backport has been revised once after the initial upload. |


### Example: Backporting a Rust toolchain

Let's say you need to backport the `1.90.0+dfsg2-0ubuntu3` Rust toolchain to Ubuntu 24.04:

:::{list-table} Toolchain upload and update versions
:header-rows: 1

*   - Situation
    - Action
    - Version string
*   - Backporting to 24.04 (with or without orig tarball changes)
    - Add `<series>` and set `<backport_revision>` to `1`
    - `1.90.0+dfsg2~24.04-0ubuntu3~24.04.1`
*   - Fixing a bug
    - Increment `<backport_revision>`
    - `1.90.0+dfsg2~24.04-0ubuntu3~24.04.2`
*   - Fixing an issue with the 24.04 repack
    - Add `[.<backport_repack>]` and set `<backport_revision>` to `1`
    - `1.90.0+dfsg2~24.04.1-0ubuntu3~24.04.1`
*   - Backporting to 22.04
    - Update `[<repack_series>]` and set `<backport_revision>` to `1`
    - `1.90.0+dfsg2~22.04-0ubuntu3~22.04.1`
:::


## Legacy version string format

:::{important}
This format is _no longer used_!

It's possible you may need to work with older versions of the Rust toolchain with potentially confusing version strings. While these formats are no longer used, they should help one understand the version strings of these older toolchains.
:::

Here, `<angle_brackets>` indicate placeholders to be edited, while `[square_brackets]` indicate optional parts.

```none
<rust_version>+dfsg0ubuntu<repack>[~bpo<vendored_dependencies>]-0ubuntu<revision>[.<ubuntu_release>][~ppa<PPA>]
```


### `<rust_version>`

> _The upstream Rust toolchain version._

This is simple; it's just the {term}`upstream` version of the given Rust toolchain. It's only updated when {ref}`adding a new Rust version to the archive <how-to-update-rust>`.

**Examples:**

- `1.88.0+dfsg0ubuntu1-0ubuntu1~ppa1`: Rust 1.88.0
- `1.87.0+dfsg0ubuntu1-0ubuntu1`: Rust 1.87.0
- `1.85.1+dfsg0ubuntu2-0ubuntu2~ppa3`: Rust 1.85.1
- `1.80.0+dfsg0ubuntu1~bpo2-0ubuntu0.24.09~ppa4`: Rust 1.80.0


(dfsg0ubuntu-repack)=
### `+dfsg0ubuntu<repack>`

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


### `[~bpo<vendored_dependencies>]`

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


### `0ubuntu<revision>`

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


### `<[ubuntu_release]>`

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


### `[~ppa<PPA>]`

> _The number of times you have pushed it to your PPA for testing._

Every time you make some changes, and want to check that it builds and passes tests by pushing it to your {term}`PPA`, you should increment this number.
This is because {term}`Launchpad` does not let you "re-upload" a version with the same version string but different source code.
Thus you have to make the version string different for each PPA upload.
This is our convention for doing that.

Every time you change the rest of the version string in some way, you can reset this to 1.

If this part is _not_ present, that means the version is intended as a candidate to be uploaded to the main archive.

:::{note}
{term}`Changelog` (`debian/changelog`) entries with `~ppa<PPA>` should never make it onto a {term}`version control system`; they are only for the benefit of the PPA itself.
When working on a Rust toolchain locally, the PPA-specific changelog entry (and version string) should be removed after successful PPA upload.
:::

**Examples:**

- `1.88.0+dfsg0ubuntu1-0ubuntu1~ppa1`: First push to your PPA
- `1.87.0+dfsg0ubuntu1-0ubuntu1`: No PPA (i.e., real complete release)
- `1.85.1+dfsg0ubuntu2-0ubuntu2~ppa3`: 3rd push to your PPA


### Putting it all together

To recap, let's do a complete breakdown of some example version strings:

| String | `<rustc_version>` | `<repack>` | `~bpo<vendored_dependencies>` | `<revision>` | `<ubuntu_release>`                 | `~ppa<PPA>` |
| --- | --- | --- | --- | --- | --- | --- |
| `1.80.0+dfsg0ubuntu1~bpo2-0ubuntu0.24.09~ppa4` | 1.80.0 | 1 | 2, so only LLVM | 0 | In-dev backport for 24.10 (OO) | 4 |
| `1.88.0+dfsg0ubuntu1-0ubuntu1~ppa1` | 1.88.0 | 1 | System libgit2 and LLVM | 1 | Omitted b/c this is a normal port | 1 |
| `1.83.0+dfsg0ubuntu1~bpo0-0ubuntu1.24.03~ppa3` | 1.83.0 | 2 | 0, so both libgit2 and LLVM | 1 | In-dev backport for 24.03 (NN) | 3 |

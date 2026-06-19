(how-to-patch-rust)=
# How to patch Rust

This guide details the process of fixing an existing versioned `rustc` Ubuntu package.

- To see the process of creating a _new_ versioned `rustc` package, consult the {ref}`how-to-update-rust` guide instead.
- To see the process of {term}`backporting <backport>` Rust, consult the {ref}`how-to-backport-rust` guide instead.

:::{attention}
This guide assumes that you already have a basic understanding of maintaining Ubuntu packages in general. It _only_ covers the things that make Rust package patching unique.
:::


## Background

`rustc` {term}`VCS` policy is unique because it is a versioned {term}`source
package`. This means that every new upstream Rust version corresponds to a new
package in the {term}`Ubuntu Archive`.

Therefore, there are two repositories for every `rustc` version uploaded to the
archive:

1. The
   [Foundations Rust repository](https://code.launchpad.net/~canonical-foundations/ubuntu/+source/rustc):
   this repository is used for
   {ref}`adding new Rust versions to the archive <how-to-update-rust>`. It
   tracks the complete history of all `rustc` packages in Ubuntu, but once a
   versioned package is uploaded to the archive, updates to that package must
   be synced back to this repository manually.

2. The package's unique {term}`git-ubuntu` ({manpage}`git-ubuntu(1)`) repository
   (example: [rustc-1.93](https://code.launchpad.net/ubuntu/+source/rustc-1.93)):
   this is the repository that matches the actual state of the package in the
   Ubuntu archive. Whenever an update to the package is uploaded, this
   repository gets updated automatically.

In short, patching an existing `rustc` release entails modifying and uploading
the release's `git-ubuntu` repository, then manually copying over the changes to
the Foundations Rust repository after your changes are uploaded to the archive.


## Substitution Terms

From now on, the documentation will contain certain terms within angle brackets
which must be replaced with the actual value that applies to your situation.

As an example, let's assume you are patching `rustc-1.94` ({term}`upstream` version
`1.94.1`) for 26.10 Stonking Stingray:

- `<X.Y>`: The short Rust version you're working on.
  - Example: `1.94`
- `<X.Y.Z>`: The long Rust version you're on.
  - Example: `1.94.1`
- `<release>`: The target {term}`Ubuntu release` adjective.
  - Example: `stonking`
- `<lpuser>`: Your {term}`Launchpad` username. This is also used to refer to
  your personal Launchpad Git {term}`repository's <repository>` remote name.
- `<foundations>`: Your local Git remote name for the [Foundations Rust repository](https://code.launchpad.net/~canonical-foundations/ubuntu/+source/rustc).
- `<lp_bug_number>`: The number of the {term}`Launchpad` {term}`bug` associated
   with this upload.


(foundations-rust-repo-setup)=
```{include} common/local-repo-setup.md

```


## Setting up the git-ubuntu Repository

Just like the Foundations Rust repository, set up a parent directory, then clone
the versioned package repository:

```none
$ mkdir rustc-<X.Y>
$ cd rustc-<X.Y>
$ git-ubuntu clone rustc-<X.Y>
$ cd rustc-<X.Y>
```

Inspect `debian/changelog` and make sure the most recent {term}`changelog` entry
version matches the version in the archive.

After that, get the current {term}`orig tarball` from the archive so you are
able to build the package locally:

```none
$ git-ubuntu export-orig
```

Create your own new branch referencing the Launchpad bug you're fixing:

```none
$ git checkout -b lp<lp_bug_number>
```

:::{attention}
Any patches to `rustc` must fix at least one Launchpad bug. If your patch
doesn't have a Launchpad bug yet, create one and reference its version number in
your changelog.
:::


## The Patching Process

You must make _all changes_ to the package within the `git-ubuntu` repository,
_not_ the Foundations Rust repository.

You may make your changes to the package the same way you would with any other
package.

Don't forget to update the changelog! See the
{ref}`version string format guide <version-strings>` if you need help selecting
the proper version string.

The changelog must also reference the bug you are fixing.

After that, you are ready to test the build locally.

```{include} common/local-build.md

```

```{include} common/ppa-build.md

```

### autopkgtests

You must also verify that none of your changes have interfered with {term}`autopkgtests <autopkgtest>` in any way.

```{include} common/running-autopkgtests.md

```

### Uploading the Patched Package

Once you are satisfied with your changes, you are ready to upload the package.

First, push your changes to your personal branch:

```none
$ git push <lpuser>
```

Then, go to your personal repository list at
`https://code.launchpad.net/~<lpuser>/+git`. Select your repo, select your
`lp<lp_bug_number>` branch, then select "Propose for merging". Submit your
{term}`merge proposal` there.


## Updating the Foundations Rust Repository

After your changes have been uploaded to the archive, the Foundations Rust
repository must be manually updated to reflect the package's actual state in the
archive.

You must add your changes to the rich Git history of the Foundations repo.
First, go to your `git-ubuntu` repo, switch to the `ubuntu/devel` branch, and
ensure it's synced up with the archive:

```none
$ git checkout ubuntu/devel
$ git pull
```

Then, create a series of patches for each commit you added since the last
version published in the archive:

```none
$ git format-patch pkg/import/<version_string_before_your_changes>..
```

This command will generate a series of numbered patches which you can then apply
to the Foundations Rust repository.

Go to the Foundations Rust repository working tree you
{ref}`set up earlier <foundations-rust-repo-setup>` and switch to the
appropriate `merge` branch:

```none
$ git checkout merge-<X.Y>
```

Then, apply each patch to the branch in numerical order:

```none
$ git am <path_to_git_ubuntu_repo>/rustc-<X.Y>/rustc-<X.Y>/0001-<patch_name>.patch
$ git am <path_to_git_ubuntu_repo>/rustc-<X.Y>/rustc-<X.Y>/0002-<patch_name>.patch
[...]
```

Once every patch has been applied, update both your personal remote and the
general Foundations remote:

```none
$ git push <lpuser>
$ git push <foundations>
```

Finally, delete the patches you generated from your `git-ubuntu` repo:

```none
$ rm <path_to_git_ubuntu_repo>/rustc-<X.Y>/rustc-<X.Y>/00*
```

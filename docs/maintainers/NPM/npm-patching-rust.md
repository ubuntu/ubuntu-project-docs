(npm-patching-rust)=

# rustc: Patching Rust

This guide details the process of fixing an existing versioned `rustc` Ubuntu package.

- To see the process of creating a _new_ versioned `rustc` package, consult the [Updating Rust](npm-updating-rust.md) guide instead.
- To see the process of {term}`backporting <backport>` Rust, consult the [Backporting Rust](npm-backporting-rust.md) guide instead.

## Background

Unfortunately, since `rustc` is a versioned {term}`source package`, we are unable to use the more modern {term}`git-ubuntu` ({manpage}`git-ubuntu(1)`) workflow. Whenever you must fix a bug in an already-released Rust source package, you must follow the legacy {manpage}`debdiff(1)` workflow instead.

:::{attention}
This guide assumes that you already have a basic understanding of maintaining Ubuntu packages in general. It _only_ covers the things which make Rust package patching unique.
:::

---

```{include} common/substitution-terms.md

```

```{include} common/local-repo-setup.md

```

## The Patching Process

You may make your changes to the package the same way you would with any other package. After that, you are ready to test the build locally.

```{include} common/local-build.md

```

```{include} common/lintian-checks.md

```

```{include} common/ppa-build.md

```

### autopkgtests

You must also verify that none of your changes have interfered with {term}`autopkgtests <autopkgtest>` in any way.

```{include} common/running-autopkgtests.md

```

### Creating a Reviewable Diff

Once you've verified that your updated package builds properly in a PPA, passes all autopkgtests, and meets Lintian standards, then you're ready to create a reviewable diff using {manpage}`debdiff(1)`.

:::{seealso}
To get more info on the legacy `debdiff` process in general, consult the "Submitting the Fix" section of [this page](../../contributors/bug-fix/propose-changes.rst).
:::

Essentially, since the Git history of `rustc-<X.Y>` was wiped when it was uploaded as a new package, we need to manually generate a diff between the uploaded version of `rustc-<X.Y>` and your updated version of `rustc` that doesn't rely on Git. To do this, we'll need `.dsc`s for both package versions.

Build the source package for both the new and old versions:

```none
$ dpkg-buildpackage -S -I -i -nc -d -sa
```

After that, use `debdiff` to generate a diff between the two `.dsc`s. Redirect the output to an easily-accessible place:

```none
$ debdiff <old_dsc> <new_dsc> > 1-<new_full_version_number>.debdiff
```

### debdiff patch naming convention

:::{important}
An understanding of Rust-specific version string conventions is necessary for this portion. Read the ["Rust Version Strings"](npm-rust-version-strings.md) article before continuing.
:::

Let's break down an example debdiff patch name: `1-1.86.0+dfsg0ubuntu2-0ubuntu1.debdiff`

- `1-` means that this is the first revision of this patch.
- `1.86.0+dfsg0ubuntu2-0ubuntu1` is the full version number of your updated version.
  - `0ubuntu2` means that the orig tarball has been regenerated after the initial upload. You don't have to increment this number unless you've changed the orig tarball.
  - `0ubuntu1` has been reset, no matter what the previous version number is. This is because the orig tarball was regenerated. You only have to increment this portion of the version number when the orig tarball was the same.
- The `.debdiff` suffix is simply a hint that this is a patch. Launchpad will complain (but still allow you to upload the patch) if this is not here.

Here's another example: `2-1.81.0+dfsg0ubuntu1-0ubuntu3.debdiff`

- `2-`: It's the second revision of this patch, meaning that the sponsor had some feedback and another patch had to be generated.
- `0ubuntu1`: The orig tarball has been unchanged since the initial upload.
- `0ubuntu3`: This package has already been updated once before since its initial upload.

### Sharing your changes for review

Instead of opening a merge proposal, you must share your patch directly underneath the bug report.

First, subscribe `ubuntu-sponsors` to the bug.

Then, click "Add attachment or patch" underneath the bug report description and add your `debdiff` as an attachment, ticking the box labelled "This attachment contains a solution (patch) for this bug". As for the comment field itself, all the regular sponsorship request standards apply — include links to the passing autopkgtests, the PPA build, the Lintian results, and the updated Git branch itself.

If you had to regenerate the orig tarball, you must also include the tarball as an attachment to the bug report.

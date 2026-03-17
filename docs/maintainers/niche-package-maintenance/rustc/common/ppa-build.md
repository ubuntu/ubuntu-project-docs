### PPA Build

Once everything builds on your local machine and Lintian is satisfied, it's time to test the package on all architectures by uploading it to a {term}`PPA`. This step is optional if doing a backport, but it is still recommended when doing a backport for the first time, or if there is reason to expect that the backport may need extensive troubleshooting.

#### Creating a new PPA

If this is your first PPA upload for this Rust version, you can create a new PPA using the [`ppa-dev-tools` snap](https://snapcraft.io/ppa-dev-tools) (it is also possible to use the Launchpad web UI). It is recommended to use the following naming convention for the PPA depending on whether you are updating Rust, backporting Rust, or patching Rust.

New versioned Rust package:

```none
$ ppa create rustc-<X.Y>-merge
```

Rust backport:

```none
$ ppa create rustc-<X.Y>-release
```

Rust patch:

```none
$ ppa create rustc-<X.Y>-lp<lp_bug_number>
```

The command should return a URL leading to the PPA. You must go to that Launchpad URL and do two things:

1. "Change Details" -> Enable all "Processors" (Make sure RISC-V is enabled!)
1. "Edit PPA Dependencies" -> Set Ubuntu dependencies to "Security" if doing a backport, or "Proposed" otherwise.

If you are using another PPA to bootstrap, then you must explicitly add this PPA as a dependency in the "Edit PPA Dependencies" menu.

:::{note}
When a new Rust toolchain is uploaded to the Archive for the devel series, it initially goes into the {ref}`proposed pocket <archive-pockets-proposed>`. By configuring your PPA to depend on "Proposed", the set of available packages in the PPA aligns with what will be available in the Archive. This avoids a situation where the PPA build could succeed but then the Archive build fails due to missing dependencies, or vice versa.

On the other hand, when backporting a Rust toolchain to a stable release, it will be uploaded to the {ref}`security pocket <archive-pockets-security>`. In this case configuring your PPA to depend on "Security" aligns with the dependencies that will be available in the Archive. For this same reason, the Staging PPA is configured to depend on "Security" since it is used for backports.
:::


#### PPA changelog entry

Next, add a temporary changelog entry, appending `~ppa<N>` to your version number so the PPA version isn't used in favour of the actual version in the archive:

:::{note}
`<N>` is just the number of the upload. You may have to fix something and re-upload to this PPA, so you should use `~ppa1` for your first PPA upload, `~ppa2` for your second, etc.
:::

```none
$ dch -bv <X.Y.Z>+dfsg0ubuntu1-0ubuntu1\~ppa<N> \
    --distribution "<release>" \
    "PPA upload"
```

#### Uploading the source package

[Make sure that your source directory is clean](updating-rust-clean-build) (especially `debian/files`), then build the source package:

```none
$ dpkg-buildpackage -S -I -i -nc -d -sa
```

Finally, upload the newly-created source package.

New versioned Rust package:

```none
$ dput ppa:<lpname>/rustc-<X.Y>-merge <path_to_source_changes>
```

Rust backport:

```none
$ dput ppa:<lpname>/rustc-<X.Y>-<release> <path_to_source_changes>
```

Rust patch:

```none
$ dput ppa:<lpname>/rustc-<X.Y>-lp<lp_bug_number> <path_to_source_changes>
```

The PPA will then build the Rust package for all architectures supported by Ubuntu. These builds will highlight any architecture-specific build failures.

#### Handling early PPA build failures

Sometimes, a PPA build on a specific architecture will fail in under 15 minutes with no build log provided. If this happens, there was a Launchpad issue, and you can simply retry the build without consequence.

If the build failed and there _is_ a build log provided, then there was indeed a build failure which you must address.

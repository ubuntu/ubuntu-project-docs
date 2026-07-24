It's recommended to create a local draft for your upload comment, so you can make sure everything is correct beforehand.

You need both the [Lintian](updating-rust-lintian-checks) and the [autopkgtest](updating-rust-autopkgtests) results for your package.

Retrieve links to all your passing autopkgtest build logs provided by the [autopkgtest command you used earlier](updating-rust-autopkgtests-url-command).

Get the default Lintian output for the source package by [cleaning up all build artifacts](updating-rust-clean-build), using `dpkg-buildpackage` to [build the source package](updating-rust-build-source-package), then simply running the default Lintian command, redirecting the output to a file for later use:

```none
$ lintian > <path_to_saved_lintian_output_file>
```

For updating the toolchain to a new version (necessitating a new package upload), an {term}`Archive Admin` needs to approve the new package. To make their job easier and speed up the package upload by generating a diff of the `debian/` directory and including it as an attachment, allowing the Archive Admin to easily review the changes:

```none
$ git diff merge-<X.Y_old> -- debian > my_diff.diff
```

Finally, you can push your `merge-<X.Y>` branch to the Foundations `rustc` Launchpad Git remote:

```none
$ git push <foundations> merge-<X.Y>
```

Compile the following information:

- A link to your successfully-built PPA packages
- A link to your `merge-<X.Y>` branch in the Foundations `rustc` Launchpad Git repository
- A list of any notable packaging changes (_not_ upstream changes). These are changes _you_ made to the package, such as the removal or addition of patches. Nothing routine (such as patch refreshes or vendored dependency pruning) should be added here.
- The output of `lintian` you just got
- The links to the build logs of all PPA autopkgtests you just got
- For Rust updates, an attachment of the diff of the `debian/` directory between the old and new Rust versions

See a real example of such an upload request at {lpbug}`2156635`.

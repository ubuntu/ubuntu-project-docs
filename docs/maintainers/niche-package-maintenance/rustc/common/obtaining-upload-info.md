It's recommended to create a local draft for your upload comment, so you can make sure everything is correct beforehand.

You need both the [Lintian](updating-rust-lintian-checks) and the [autopkgtest](updating-rust-autopkgtests) results for your package.

Retrieve links to all your passing autopkgtest build logs provided by the [autopkgtest command you used earlier](updating-rust-autopkgtests-url-command).

Get the default Lintian output for the source package by [cleaning up all build artifacts](updating-rust-clean-build), using `dpkg-buildpackage` to [build the source package](updating-rust-build-source-package), then simply running the default Lintian command, redirecting the output to a file for later use:

```none
$ lintian > <path_to_saved_lintian_output_file>
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

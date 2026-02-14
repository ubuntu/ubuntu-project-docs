We can use {manpage}`uscan(1)` (from the {lpsrc}`devscripts` package) to generate the new {term}`orig tarball`. This is the upstream source code for the Rust toolchain, filtered to exclude any files listed in `Files-Excluded` of the `debian/copyright` file. Files can be excluded for various reasons:

- They are vendored dependencies (e.g. `src/gcc`) where we prefer to instead use a system version.
- They are only relevant for executing on platforms unsupported by Ubuntu (e.g. Windows).
- They apply to unstable Rust features which we do not yet support, e.g. `src/tools/enzyme`.

The orig tarball needs to be rebuilt anytime we make a change to the `Files-Excluded` or when working on a new upstream Rust version. If no such changes are made, the orig tarball can instead be downloaded from Launchpad; it will be listed as a file ending in `.orig.tar.xz` under the "Package files" for the package, either on the Ubuntu Archive or on the PPA to which it was uploaded (e.g. the ["Rust Toolchain" Staging PPA](https://launchpad.net/~rust-toolchain/+archive/ubuntu/staging/+packages)).

To rebuild the orig tarball, run `uscan` while saving its log somewhere:

```none
$ uscan --download-version <X.Y.Z> -v 2>&1 | tee <path_to_log_output>
```

The output will will warn you if any files you've excluded from `debian/copyright` aren't actually in the original source. You must consult the upstream Rust changes and see what happened to that file, updating `debian/copyright` accordingly depending on if it was removed, renamed, or refactored.

This process can take a while. Once it is complete, you will find a file with an `.orig.tar.xz` suffix in your parent `rustc` directory. You must then rename it to match the part of your package version number before the first hyphen, e.g., if your package name is `rustc-1.89` and package version is `1.89.0+dfsg-0ubuntu1`, you would rename the orig tarball to `rustc-1.89_1.89.0+dfsg.orig.tar.xz`.

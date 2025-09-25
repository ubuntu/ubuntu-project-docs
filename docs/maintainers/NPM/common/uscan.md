We can use {manpage}`uscan(1)` (from the [`devscripts`](https://launchpad.net/ubuntu/+source/devscripts) package) to get the new source code and generate the new {term}`orig tarball`.

The log of this should be saved somewhere because `uscan` will warn you if any files you've excluded from `debian/copyright` aren't actually in the original source. You must consult the upstream Rust changes and see what happened to that file, updating `debian/copyright` accordingly depending on if it was removed, renamed, or refactored.

Download the orig tarball from the upstream Rust source, yanking out all excluded files:

```none
$ uscan --download-version <X.Y.Z> -v 2>&1 | tee <path_to_log_output>
```

This process can take a while. Once it is complete, you will find a file with an `.orig.tar.xz` suffix in your parent `rustc` directory. That is your orig tarball. It contains the new upstream source code for the new Rust version.

You must then rename the orig tarball to match the first part of your package version number, i.e., `rustc-<X.Y>_<X.Y.Z>+dfsg0ubuntu0`.

### Lintian Checks

{term}`Lintian` ({manpage}`lintian(1)`) checks your source package for bugs and [Debian policy](https://www.debian.org/doc/debian-policy/) violations.

(updating-rust-lintian-prep)=

[Clean up previous build artifacts](updating-rust-clean-build) then build the source package:

(updating-rust-build-source-package)=

```none
$ dpkg-buildpackage -S -I -i -nc -d -sa
```

First, check the Lintian output with just the warnings and errors:

```none
$ lintian -i --tag-display-limit 0 2>&1 | tee <path_to_log_file>
```

#### Addressing warnings and errors

You must address all of these in one way or another. They must either be fixed or added to `debian/source/lintian-overrides{,.in}`, with a few notable exceptions:

- `E: rustc-1.86 source: field-too-long Vendored-Sources-Rust`
  - This is simply the length of the field. While we _would_ like to change this in the future in `dh-cargo`, there's nothing that can (or should) be done about this for now.
- `E: rustc-1.86 source: unknown-file-in-debian-source [debian/source/lintian-overrides.in]`
  - This is just the file used to generate the Lintian overrides for a given Rust version. It's completely harmless to have in the source tree.
- `E: rustc-1.86 source: version-substvar-for-external-package Depends ${binary:Version} cargo-<X.Y> -> rustc [debian/control:*]`
  - This is just a fallback for a non-versioned `rustc` package. While it's unlikely to ever be used, it's not a typo, so you don't need to worry about it.
- `W: rustc-1.86 source: unknown-field Vendored-Sources-Rust`
  - This is a custom field, not a typo.

As for any other warnings or errors, you must figure out whether the lint should be ignored or remedied. Don't be afraid to ask for help from more experienced package maintainers, or consult the existing Lintian overrides for precedence.

#### Extra lints

Now you can run Lintian with all the pedantic, experimental, and informational lints enabled. It isn't typically necessary to fix most of the extra lints, but it's a good idea to check everything and see if there are some ways to improve the package based on these lints.

```none
$ lintian -i -I -E --pedantic
```

:::{important}
Don't forget to [clean and rebuild the source package](updating-rust-lintian-prep) before re-running Lintian, otherwise your changes to the package won't apply!
:::

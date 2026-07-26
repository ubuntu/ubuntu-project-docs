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

Some warnings and errors should be fixed, some should be silenced, and some should be left alone. Consult the {ref}`common-rustc-lintian-issues` article for information on specific Lintian problems.

#### Extra lints

Now you can run Lintian with all the pedantic, experimental, and informational lints enabled. It isn't typically necessary to fix most of the extra lints, but it's a good idea to check everything and see if there are some ways to improve the package based on these lints.

```none
$ lintian -i -I -E --pedantic
```

:::{important}
Don't forget to [clean and rebuild the source package](updating-rust-lintian-prep) before re-running Lintian, otherwise your changes to the package won't apply!
:::

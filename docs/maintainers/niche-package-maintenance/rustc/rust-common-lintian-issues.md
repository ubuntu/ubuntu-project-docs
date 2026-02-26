(rust-common-lintian-issues)=
# Common `rustc` Lintian Issues

The {term}`Lintian` ({manpage}`lintian(1)`) program checks your
{term}`source package` for bugs and
[Debian policy](https://www.debian.org/doc/debian-policy/) violations.

In an ideal world, the {pkg}`rustc` toolchain package would have no
Lintian errors or warnings whatsoever. However, since `rustc` is a
complex and unconventional package, certain policy violations must
be tolerated in order for the package to function properly.


## Possible courses of action

This article lists common Lintian issues faced when packaging `rustc`
and describes what to do when encountering them. There are three
possible routes to take:

1. **Fix**: Lintian issues marked as "fix" should be addressed. In these
   cases, Lintian has flagged a genuine issue with the package. Most
   issues not included in this article should be fixed.

1. **Override**: Lintian issues marked as "override" should be
   overridden in `debian/source/lintian-overrides` if it's an issue
   with the {term}`source package`, or
   `debian/<PACKAGE>.lintian-overrides.in` if it's an issue with a
   {term}`binary package`. In these cases, Lintian is incorrectly
   flagging a policy violation that does not apply to the package.

1. **No Action**: Lintian issues marked as "no action" should be left
   alone and included in the Lintian report. They should _not_ be
   overridden — the crucial difference between "override" and "no 
   action" is the _legitimacy_ of the issue. Overridden Lintian issues
   are simply false positives, while "no action" Lintian issues are
   _genuine policy violations_ which are necessary for the `rustc`
   package to work properly.


## Common issues

The following list of issues is not exhaustive. When new Lintian issues
arise and a course of action is decided, then those issues should be
added to this list.


### `E: rust-<X.Y>-doc: privacy-breach-logo`: **Fix**

The upstream Rust documentation tries to fetch the Rust logo from an
external site at runtime, potentially causing a privacy breach.
Naturally, this must be avoided.

In the `override_dh_auto_install-indep` rule of `debian/rules`, all
references to external logos are replaced with links to the local
copy of the logo distributed with the upstream {term}`orig tarball`.

If you are seeing this error, then within that step is no longer working
properly. Consult `debian/rules` to try and identify the reason why the
logo replacement is no longer working properly.


### `E: rust-<X.Y>-src: package-installs-python-pycache-dir`: **Fix**

This error is triggered by compiled Python source files accidentally
being shipped in the `rustc` source code package. This should be
remedied.

In `debian/rules`, there is a variable called `SRC_CLEAN` that should
look similar to the following:

```make
# Build products or non-source files in src/, that shouldn't go in rust-src
SRC_CLEAN = src/bootstrap/bootstrap.pyc \
	src/bootstrap/__pycache__ \
	src/etc/__pycache__/
```

If there are no issues with `SRC_CLEAN`, the actual removal of the
compiled files takes place in the `override_dh_auto_install-indep` rule.
Check that section to ensure that the removals point to the correct file
paths.


### `E: rustc-<X.Y> source: field-too-long Vendored-Sources-Rust`:  **No Action**

No action can be taken here; the lint is accurate.
`XS-Vendored-Sources-Rust` is a special field specific to Rust packages
with {term}`vendored dependencies <vendored dependency>`. It lists the
vendored dependencies of the given Rust package. Since `rustc` has many
dependencies, this field will always be very large.


### `W: rustc-<X.Y> source: file-without-copyright-information`: **Fix**

Considering the complexity of the Rust toolchain package, it's normal
for new files without copyright information to be added to the source.
Consult the
"{ref}`updating debian/copyright <updating-rust-updating-debian-copyright>`"
section of the "Updating Rust" article to handle new vendored dependency
copyright stanzas.

If the file without copyright information *isn't* in the `vendor/`
directory, then it can be added to the first copyright stanza in
`debian/copyright` alongside all the other files specific to the Rust
toolchain itself.


### `E: rustc-<X.Y> source: source-is-missing [*.min.js]`: **Override**

This error triggers not only when the source is indeed missing, but also
when there is a very long line length within the source file.

If any `.min.js` files are triggering this error, then Lintian is
erroneously tagging them as missing because minimized JS files consist
of just a single line. This means that they will almost invariably be
extremely long single lines.

It is necessary to override this Lintian warning for such files, as we
know that the files are indeed present. Include the following lines in
`debian/source/lintian-overrides`:

```none
# The naturally long lines of minimized JS files trigger
# very-long-line-length-in-source-file, which triggers source-is-missing
rustc-1.93 source: source-is-missing [*.min.js]
```

### `W: rustc-<X.Y> source: unknown-field Vendored-Sources-Rust`: **No Action**

Lintian is correctly identifying `Vendored-Sources-Rust` as an
unrecognized field. This is to be expected, as `Vendored-Sources-Rust`
an unofficial "hack" for expressing the list of vendored dependencies,
and it is not an actual Debian control file field.


### `E: rustc-<X.Y> source: version-substvar-for-external-package Depends ${binary:Version} cargo-<X.Y> -> rustc`: **Fix**

Since the `rustc` binary package is now built by `rust-defaults`, it's
an external package and triggers the error.

This dependency is an artifact of the transition from a non-versioned
source package (`rustc`) to (`rustc-X.Y`). The intent of this
dependency was to provide a non-versioned alternative if the
versioned dependency wasn't available. Since non-versioned `rustc` has
been deprecated for some time now, this dependency can safely be
removed.

(mir-rust)=
# MIR - Rust code in main

Due to the current state of the Rust ecosystem, the MIR rules state that
packages in main that contain Rust code should vendor their Rust dependencies
rather than rely on the individual package versions.

See [`cpaelzer/ubuntu-mir#3`](https://github.com/cpaelzer/ubuntu-mir/pull/3) for
some background on the issue.

## Vendoring Rust dependencies

It's a simple matter of running `cargo vendor debian/rust-vendor/` where you're
on the top-level directory. Sadly, it's not possible to exclude irrelevant
dependencies during vendoring yet, so you might want to automate that step and
add some post-processing to remove voluminous, unused dependencies, and/or the
C code for some system libraries that could be statically linked.

### Automation via `debian/rules`

A good example for automating Rust vendoring is provided by
[s390-tools](https://git.launchpad.net/ubuntu/+source/s390-tools/tree/debian/rules)
and can be executed via `debian/rules`.

First, the package is updated as usual, including the new `debian/changelog`
entry. Then a vendor tarball can be (re-)created, using the `vendor-tarball`
target:

```sh
debian/rules vendor-tarball
```

See [`debian/README.source`](https://git.launchpad.net/ubuntu/+source/s390-tools/tree/debian/README.source)
for more details.

The relevant parts of `s390-tools` `debian/rules` file are listed below:

```text
export CARGO = /usr/share/cargo/bin/cargo
export CARGO_VENDOR_DIR = rust-vendor
export CARGO_HOME = $(CURDIR)/debian/cargo_home

include /usr/share/rustc/architecture.mk
export DEB_HOST_RUST_TYPE DEB_HOST_GNU_TYPE

VENDOR_TARBALL = s390-tools_$(DEB_VERSION_UPSTREAM).orig-$(CARGO_VENDOR_DIR).tar.xz

vendor-tarball-sanity-check:
        if [ -e ../$(VENDOR_TARBALL) ]; then echo "../$(VENDOR_TARBALL) already exists, bailing!"; exit 1; fi

vendor-deps:
        if QUILT_PATCHES=debian/patches quilt applied | grep vendor-remove-unused-deps ; then \
                echo "Detecting patch on vendor dir applied, aborting."; \
                exit 1; \
        fi
        rm -rf $(CARGO_VENDOR_DIR)
        # Deliberately don't use the wrapper, as it expects the configure step
        # to have occurred already.
        # If you have to modify the path here, don't forget to change the README.source doc
        # as well.
        cargo vendor --manifest-path rust/Cargo.toml $(CARGO_VENDOR_DIR)
        # Remove some crates that aren't useful for us and take up a lot of space
        rm -r \
                $(CARGO_VENDOR_DIR)/winapi \
                $(CARGO_VENDOR_DIR)/winapi-* \
                $(CARGO_VENDOR_DIR)/windows-* \
                $(CARGO_VENDOR_DIR)/windows_* \
                # End of list
        # Remove the C sources from the binding crates, we're using the system libs
        rm -r \
                $(CARGO_VENDOR_DIR)/libz-sys/src/zlib \
                $(CARGO_VENDOR_DIR)/libz-sys/src/zlib-ng \
                $(CARGO_VENDOR_DIR)/curl-sys/curl \
                # End of list
        # Remove unused and undesirable data files (e.g. test data for vendored crates)
        rm -r \
                $(CARGO_VENDOR_DIR)/vcpkg/test-data \
                $(CARGO_VENDOR_DIR)/*/tests \
                # End of list
        # Remove the checksum files to allow us to patch the crates to remove extraneous dependencies
        for crate in $(CARGO_VENDOR_DIR)/*; do \
                sed -i 's/^{"files":.*"package":"\([a-z0-9]\+\)"}$$/{"files":{},"package":"\1"}/' $$crate/.cargo-checksum.json; \
        done
        # Cleanup temp files
        rm -rf $(CARGO_HOME)

vendor-tarball: vendor-tarball-sanity-check vendor-deps
        tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner --pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime -caf ../$(VENDOR_TARBALL) $(CARGO_VENDOR_DIR)

%:
        dh $@

override_dh_auto_configure:
        DEB_CARGO_CRATE=s390-tools_$(shell dpkg-parsechangelog --show-field Version) \
        $(CARGO) prepare-debian $(CARGO_VENDOR_DIR)
        /usr/share/cargo/bin/dh-cargo-vendored-sources
        dh_auto_configure

override_dh_clean:
        dh_clean
        rm -rf $(CARGO_HOME)
```

### Handling binaries inside vendored crates

Some vendored crates include binary files which `dpkg-source` does not like.
Here are commands to handle such cases:

```sh
rm debian/source/include-binaries
dpkg-source --include-binaries -b .
git add debian/source/include-binaries
git commit -m "Update debian/source/include-binaries"
git reset --hard && git clean -fdx
```

### Teaching `dh-cargo` about vendored sources

`dh-cargo` by default assumes the dependencies of the main project will be
provided by packaged crates from our archive. Since our MIR policy is to vendor
dependencies, you need to set the `CARGO_VENDOR_DIR` environment to wherever
the vendored dependencies are stored, e.g.:

```sh
export CARGO_VENDOR_DIR = debian/rust-vendor/
```

Note that even if you're using the more manual steps, you'll want to export
this variable, as some scripts might expect it.

### Modifying individual vendored crates

If you have to modify the contents of individual vendored crates, e.g. to remove
pre-compiled files, this will change the checksum of the crate, and cargo will
complain. So far, the best solution we've come up with is to do JSON surgery in
the crate's `.cargo-checksum.json` to remove the individual file checksums while
keeping intact the individual crate checksum.

Eventually we should provide helper scripts to do so in the `dh-cargo` package,
but meanwhile the following snippet does the trick:

```sh
[ -e /usr/bin/jq ] || (echo "jq is required to run this script. Try installing it with 'sudo apt install jq'" && exit 1);
for dep in $(ls vendor_rust -1); do
    checksum_file="vendor_rust/${dep}/.cargo-checksum.json";
    a_files=$(cat ${checksum_file} | jq '.files | keys | map(select(.|test(".a$")))');
    if [ "$a_files" = "[]" ]; then
        continue;
    fi;
    pkg_checksum=$$(cat "${checksum_file}" | jq '.package');
    echo "{\"files\": {}, \"package\": ${pkg_checksum}}" >"${checksum_file}";
done;
```

## Cargo wrapper

The `cargo` package ships a wrapper script around the actual `cargo` binary that
sets default options useful for packaging, and exposes custom sub-commands.
Therefore, it is advised to use it rather than the binary directly whenever you
need to do manual calls:

```text
CARGO := /usr/share/cargo/bin/cargo
```

## `dh-cargo`

If your project is pure Rust code in a single crate, `dh-cargo` should be able
to drive the build via the following snippet:

```text
%:
    dh $@ --buildsystem=cargo
```

Sadly, `dh` cannot have multiple `buildsystem`s at the same time, so for hybrid
codebases you'll need to trigger the build phases manually. Moreover, `dh-cargo`
does *not* support building workspaces at the moment, at it was designed to work
on source packages pulled directly from `crates.io` (which only ships individual
crates), so there's a likely chance it would choke on it.

### Jammy support

Support for vendored dependencies hasn't been SRU-ed to Jammy yet. This is
tracked in [LP: #2028153](https://bugs.launchpad.net/ubuntu/+source/dh-cargo/+bug/2028153).

## Manual steps

### `prepare-debian`

The wrapper expects a few things to be set up before the build:

```text
override_dh_auto_configure:
    dh_auto_configure
    dh_auto_configure --buildsystem=cargo
```

If you're targeting Jammy, you would want to run something like this instead:

```text
DEB_HOST_GNU_TYPE=$(DEB_HOST_GNU_TYPE) DEB_HOST_RUST_TYPE=$(DEB_HOST_RUST_TYPE) \
CARGO_HOME=$(CURDIR)/debian/cargo_home DEB_CARGO_CRATE=adsys_$(shell dpkg-parsechangelog --show-field Version) \
$(CARGO) prepare-debian $(CARGO_VENDOR_DIR)
```

### Tests

Due to the oddities of the Debian Rust ecosystem, by default `dh-cargo` does not
run the tests but rather only does a build test. One needs an override to force
it to run the tests:

```text
override_dh_auto_test:
    dh_auto_test --buildsystem=cargo -- test --all
```

### Build

`dh-cargo` does *not* build the code in the build stage, it's all folded into
the `install` stage.

### Install

This should work out of the box for single-crate projects:

However, for more complex projects, you'll need this somewhat gnarly invocation
along those lines:

```
    # Here we utilise a logical flaw in the cargo wrapper to our advantage:
    # when specifying DEB_CARGO_CRATE_IN_REGISTRY=1, the wrapper will
    # avoid adding the `--path` option, so that we can specify it ourselves
    DEB_HOST_GNU_TYPE=$(DEB_HOST_GNU_TYPE) \
    DEB_HOST_RUST_TYPE=$(DEB_HOST_RUST_TYPE) \
    CARGO_HOME=$(CURDIR)/debian/cargo_home \
    DEB_CARGO_CRATE=adsys_mount_0.1.0 \
    DEB_CARGO_CRATE_IN_REGISTRY=1 \
    DESTDIR=$(CURDIR)/debian/tmp \
        $(CARGO) install --path $(ADSYS_MOUNT)
    # Currently doesn't work because of https://github.com/rust-lang/cargo/issues/4101
    # combined with a lack of flexibility in the cargo wrapper. That means we
    # have to do it manually (with the build split out in dh_auto_build for good
    # measure, even though dh-cargo does it all in the install step)
    # dh_auto_install --buildsystem=cargo -- --path $(ADSYS_MOUNT)
```

### Rust vendored sources tracking

The tracking of embedded Rust vendored dependencies is done via a field in the
source package, fittingly named `XS-Vendored-Sources-Rust`, composed of a
comma-separated list of versioned crate names of the format `CRATE@VERSION`.

From version `28ubuntu1` onward, the `dh-cargo` package contains a script that
checks this field's content against the contents of the vendor tree, and fails
the build if it doesn't match, outputting the expected value.

The script is available in `/usr/share/cargo/bin/dh-cargo-vendored-sources`.

Note that the field can easily be fairly gigantic.

#### Manual tracking of vendored sources

In cases where the provided script does not work due to build environment
constraints (e.g. using the `meson` `buildsystem`), the vendored dependencies
should be tracked manually. The following commands can help with that:

```sh
rm Cargo.toml
# Use the output to update the XS-Vendored-Sources-Rust line in debian/control
CARGO_VENDOR_DIR=debian/rust-vendor/ /usr/share/cargo/bin/dh-cargo-vendored-sources
git add debian/control
git commit -m "Update XS-Vendored-Sources-Rust field"
git reset --hard # restore Cargo.toml
```

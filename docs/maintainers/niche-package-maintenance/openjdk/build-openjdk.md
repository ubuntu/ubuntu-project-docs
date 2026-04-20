(build-openjdk)=
# Build OpenJDK

## Key variables

### Release and distribution detection

`debian/rules` detects the current vendor and release at the start of the
build using `lsb_release` and `dpkg-vendor`. The values drive almost every
conditional in the file.

### Version variables

The package version is parsed from `debian/changelog` and split into
components so that the JDK's `--with-version-*` configure options can be set
precisely.

| Variable | Meaning |
| :--- | :--- |
| `shortver` | Major JDK version number (e.g. `17`). |
| `jvmver` | Full JVM specification version string (e.g. `1.17.0`). |
| `v_debian` | Full Debian package version without the EA marker. |
| `v_upstream` | Upstream version stripped of the Debian suffix. |
| `v_upbase` | Upstream base version (before `+` or `~`). |
| `v_upbuild` | Upstream build number (after `+` or `~`). |
| `v_pkgrel` | Debian/Ubuntu packaging revision (after the last `-`). |

### Architecture lists

Several named sets of architectures control what gets built and tested:

| Variable | Purpose |
| :--- | :--- |
| `hotspot_archs` | Architectures where the JIT (HotSpot) VM is built. Non-listed archs use the Zero interpreter-only VM. |
| `altzero_archs` | Architectures where an alternate Zero VM is also built alongside HotSpot. |
| `jtreg_archs` | Architectures where the `jtreg` test suite is run. |

### Build feature flags

| Variable | Default | Effect when disabled |
| :--- | :--- | :--- |
| `with_check` | `yes` | Skip all `jtreg` tests (`--without-jtreg`). |
| `with_docs` | `yes` | Skip `javadoc` generation. |
| `with_nss` | `yes` | Disable NSS provider (`--disable-nss`). |
| `bootcycle_build` | `yes` on HotSpot archs | Build only once with the boot JDK instead of twice. |
| `is_default` | `yes` on modern releases | Controls `update-alternatives` priority. |

`with_check` is automatically disabled on several slow or unsupported
architectures and on older releases that do not package `jtreg`.

### Build directories

| Variable | Path | Contains |
| :--- | :--- | :--- |
| `builddir` | `build/` | Main HotSpot/Zero build tree. |
| `zbuilddir` | `build-zero/` | Alternate Zero VM build tree (cross-arch). |
| `sdkimg` | `build/images/jdk` (or `bootcycle-build/images/jdk`) | Final JDK image used for packaging. |

## Targets

### Package generation: `update-control-files`

```bash
lsb_release --codename && make -f debian/rules update-control-files
```

This must be run whenever the package version, supported Ubuntu/Debian
releases, or architecture lists change. It regenerates:

- `debian/control` from `debian/control.in` — substituting architecture lists,
  build-dependency sets, and package names.
- `debian/tests/control` from `debian/tests/control.in` — setting the
  minimum required `jtreg` version.
- `debian/tests/*.sh` from `debian/tests/*.in` — substituting the JDK
  basename (e.g. `openjdk-21`) and the installation path.
- `debian/copyright` via `debian/copyright-generator/copyright-gen.py`.

The generated files are checked against their previous versions; if they
differ, the build is aborted and the user is asked to commit the new files
before retrying.

To suppress the auto-regeneration step during a build (e.g. for local
experiments), add `nogen` to `DEB_BUILD_OPTIONS`:

```bash
DEB_BUILD_OPTIONS=nogen dpkg-buildpackage -b
```

### Build: `build`, `build-arch`, `build-indep`

The standard `dpkg-buildpackage` targets ultimately invoke:

1. **`pre-build`** — runs `update-control-files` (unless `nogen` is set) and
   verifies the installed `jtreg` version meets the minimum required.
2. **`stamps/configure`** — runs the upstream `configure` script inside
   `build/`. Key arguments are assembled from `COMMON_CONFIGURE_ARGS`,
   `DEFAULT_CONFIGURE_ARGS`, and the compiler/flag variables.
3. **`stamps/build`** — invokes `$(MAKE) -C build images test-image`
   (or the `bootcycle` equivalents). Logs any `hs_err_pid` crash dumps.
4. **`stamps/zero-configure`** / **`stamps/zero-build`** — repeated for the
   alternate Zero VM on `altzero_archs`.
5. **`stamps/jtreg-check-default`** — runs the test suite if `with_check=yes`.
6. **`stamps/build-docs`** — generates Javadoc when `with_docs=yes`.

### Configure arguments

The configure step assembles flags from three groups:

| Group | Variable | Used for |
| :--- | :--- | :--- |
| Shared | `COMMON_CONFIGURE_ARGS` | Both HotSpot and Zero builds. |
| HotSpot | `DEFAULT_CONFIGURE_ARGS` | The primary JVM build. |
| Zero | `ZERO_CONFIGURE_ARGS` | The alternate interpreter-only build. |

### Testing: `check-hotspot`, `check-jdk`, `check-jaxp`, `check-langtools`

Each of these make targets runs one test subsystem against the just-built JDK
image by delegating to the corresponding `debian/tests/` wrapper script.

The test logs are published in `openjdk-<N>-jdk` package.

See {ref}`test-openjdk` for running tests outside the package build system.

### `install`

Copies the built JDK image into `debian/tmp/$(basedir)`, performs
post-processing, and sorts files across the binary packages:

- Moves configuration files (`conf/`, `lib/security/`, etc.) to `/etc/java-<N>-openjdk/` and creates symlinks back.
- Strips binaries and relocates `.debuginfo` files to `usr/lib/debug/` with
  build-ID–based paths (when `with_debugedit=yes`).
- Generates `.install` and `.links` files for each binary package
  (`-jre-headless`, `-jre`, `-jdk-headless`, `-jdk`, `-dbg`, etc.) dynamically
  based on the tool lists and architecture.
- Registers the JVM with `update-alternatives` via a `.jinfo` file.

### `get-orig`

Downloads and repacks the upstream source tarball, removing bundled copies of
system libraries (`zlib`, `libjpeg`, `giflib`, `libpng`, MUSCLE/pcsclite):

```bash
make -f debian/rules get-orig
```

This also downloads the GoogleTest source (needed for the JVM unit tests) as a
separate `orig` tarball.

### `clean`

Removes the `stamps/`, `build/`, `build-zero/`, and `jtreg-test-output/`
directories.  `debian-clean` additionally removes generated `debian/*.install`
and `debian/*.links` files.

## Bootcycle build

On HotSpot architectures, the build uses a *boot JDK* (the previous
major release, found in `BOOTJDK_HOME`) to compile OpenJDK, and the resulting
JDK is then used to compile OpenJDK again (`bootcycle-images`). This confirms
the new JDK can build itself.

```{note}
This does not protect from the bugs in packaging such as missing files in the resulting package. To validate that the package works correctly, please build openjdk against the newly built package.
```

The bootcycle can be disabled with:

```bash
DEB_BUILD_OPTIONS=nobootcycle dpkg-buildpackage -b
```


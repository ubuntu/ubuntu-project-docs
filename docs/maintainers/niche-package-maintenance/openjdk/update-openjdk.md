(update-openjdk)=
# Update OpenJDK

## Get a new upstream version

### Check for the new version

```bash
$ uscan
```

### Update git tag, changelog and generate original tarball

1. Update variable `git_tag` in `debian/rules`.
2. Add a changelog entry with the new version.
3. Generate the original tarball:
   ```bash
   $ make -f debian/rules get-orig
   ```

### Validate the tarball

OpenJDK vendors additional libraries in the source tree.
Run `make -f debian/rules update-license` to generate `debian/copyright`
and check the new entries.

The vendored libraries should be removed from the source tree:
- Update `Files-Excluded:` in `debian/copyright`.
- Update `get-orig` target in `debian/rules`.
- Add package dependency in `bd_syslibs` variable in `debian/rules`
- Patch the build if necessary, see `debian/patches/system-pcsclite.diff`
- Regenerate control files:
  ```bash
  $ make -f debian/rules update-control-files
  ```

### Validate the build

Build the package locally (see {ref}`how-to-build-packages-locally`), refreshing patches if they do not apply.

To ensure the package is fully functional and the build environment is correct, install the newly built packages and perform a "bootcycle" build check:

1. Install the built packages:
   ```bash
   $ sudo apt install ../openjdk-*.deb
   ```
   (See {ref}`how-to-install-built-packages` for more details on installing built packages).

2. Re-run the build in the same or a fresh source tree to verify that the newly installed JDK can successfully build OpenJDK.

### Build the source package and upload

Once validated, follow the standard {ref}`uploading-to-the-archive` procedure to submit the update.

## Update an existing version

To update an existing version in the archive (e.g., to fix a packaging bug or add a security patch) without changing the upstream base:

1. Add a new changelog entry with `dch -i`.
2. Apply your fixes or add new patches to `debian/patches/`.
3. Regenerate the control files:
   ```bash
   $ make -f debian/rules update-control-files
   ```

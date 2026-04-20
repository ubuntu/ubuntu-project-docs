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
3. make -f debian/rules get-orig

### Validate the tarball

OpenJDK vendors additional libraries in the source tree.
Run `make -f debian/rules update-license` to generate `debian/copyright`
and check the new entries.

The vendored libraries should be removed from the source tree:
- Update `Files-Excluded:` in `debian/copyright`.
- Update `get-orig` target in `debian/rules`.
- Add package dependency in `bd_syslibs` variable in `debian/rules`
- Patch the build if necessary, see `debian/patches/system-pcsclite.diff`
- Regenerate control files `make -f debian/rules update-control-files`

### Validate the build

Build the package, refreshing patches if they do not apply.
Install newly build package and build again to ensure that the package is usable.

### Build the source package and upload

Follow the usual source package build and upload procedure.

## Update an existing version

The process is similar to updating to a new version, but you do not need to update the git tag or generate a new original tarball.
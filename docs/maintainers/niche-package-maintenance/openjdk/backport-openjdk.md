(backport-openjdk)=
# Backport OpenJDK

OpenJDK is tightly coupled with `jtreg<N>` versioned package. Ensure that `jtreg<N>` is available in the target release before backporting OpenJDK.

## JTREG<N> packages

The jtreg package is maintained on [salsa](https://salsa.debian.org/java-team/jtreg8). It uses an exception from Java policy that allows vendoring of jtreg dependencies.

## Regenerate control files

OpenJDK `debian/rules` provides `update-control-files` target that regenerates files using the current Debian or Ubuntu release. Ensure that `lsb_release` is installed so that the target can determine the current release.

```bash
$ lsb_release --codename && make -f debian/rules update-control-files
```

## Build the source package and upload

Follow the usual process to build and upload the source package.

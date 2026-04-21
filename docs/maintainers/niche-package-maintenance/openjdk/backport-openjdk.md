(backport-openjdk)=
# Backport OpenJDK

Ubuntu follows an **N-2 policy** for OpenJDK backports. Under this policy, a new stable (LTS) release introduced in Ubuntu version *N* is backported to the current LTS release and the two preceding LTS releases.

**Interim OpenJDK releases** (the non-LTS releases published every six months) are strictly for the current development version of Ubuntu and are not backported to older releases.

## JTREG<N> packages

OpenJDK is tightly coupled with `jtreg<N>` versioned package. Ensure that `jtreg<N>` is available in the target release before backporting OpenJDK.

The jtreg package is maintained on [salsa](https://salsa.debian.org/java-team/jtreg8). It uses an exception from Java policy that allows vendoring of jtreg dependencies.

## Regenerate control files

OpenJDK `debian/rules` provides `update-control-files` target that regenerates files using the current Debian or Ubuntu release. Ensure that `lsb_release` is installed so that the target can determine the current release.

```bash
$ lsb_release --codename && make -f debian/rules update-control-files
```

## Build the source package and upload

Follow the standard procedure to build the package locally ({ref}`how-to-build-packages-locally`) and upload the source package ({ref}`uploading-to-the-archive`) to the staging PPA.


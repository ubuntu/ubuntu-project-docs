(aa-i386-whitelist-updates)=
# i386 whitelist updates

The i386 [is a partial archive now](https://wiki.ubuntu.com/i386).

To add packages to the whitelist:

* Update the `update-i386-whitelist` script from `u-a-t` (typically adding a
  `newSet.update(['$package'])` entry

* Run the script

* Trigger the i386 build either by doing an upload or by copying the package
  over itself (`copy-package -b --force-same-destination -e $version $pkg`)

Note that if the binary package was built for an earlier release, e.g. Oracular
for the current Plucky, you'll need to adjust the `copy-package` invocation to:

```none
./copy-package -b --from-suite=oracular --to-suite=plucky -e $version $pkg
```

The copy should trigger a build on i386, once it's published:

* Remove the entry from the `update-i386-whitelist` script

* If the new item isn't pulled in as a build-/dependencies, manually add it to
  the [ubuntu-seeds repository](https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/i386/)

  * If a source package builds multiple binary packages, and a binary package
    other than the one pulled into the seed has dependencies that are not
    otherwise included, then this binary package will also need to be seeded in
    order to ensure dependency availability.


(aa-i386-whitelist-updates)=
# i386 whitelist updates

```{admonition} Question
:class: important

Can we change whitelist to allowlist?

Also, do we need more intro than this?
```

The i386 [is a partial archive now](https://wiki.ubuntu.com/i386).

## Add packages to the whitelist

Update the `update-i386-whitelist` script from `ubuntu-archive-tools`
(typically adding a `newSet.update(['$package'])` entry.

Run the `update-i386-whitelist` script.

Trigger the i386 build either by:

* doing an upload

* copying the package over itself:
  
  `copy-package -b --force-same-destination -e $version $pkg`

Note that if the binary package was built for an earlier release, e.g. Oracular
for the current Plucky, you'll need to adjust the `copy-package` invocation to:

```none
./copy-package -b --from-suite=oracular --to-suite=plucky -e $version $pkg
```

The copy should trigger a build on i386

## After it's published

Remove the entry from the `update-i386-whitelist` script.

If the new item isn't pulled in as a build-/dependencies, manually add it to
the [ubuntu-seeds repository](https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/i386/)

If a source package builds multiple binary packages, and a binary package
other than the one pulled into the seed has dependencies that are not
otherwise included, then this binary package will also need to be seeded in
order to ensure dependency availability.

```{admonition} Question
:class: important

Do we need to provide a link to the instructions for seeding? Is this is also an
AA task?
```

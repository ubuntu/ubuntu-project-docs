# Removals (wiki)

## Manual

Sometimes packages just need removing entirely, because they are no longer
required. This can be done using the `remove-package` client-side tool:

```bash
$ ./remove-package -m "reason for removal" konserve
```

By default this removes the named source and binaries, to remove just a binary
use `-b`:

```bash
$ ./remove-package -m "NBS" -b konserve
```

"NBS" is a common short-hand meaning that the binary is "No-longer Built by the
Source".

To remove just a source, use `-S`.

The tool tells you what it's going to do, and asks for confirmation before
doing it, so it's reasonably safe to get the wrong options and say `N`.


## Blacklisting

If you remove source packages which are in Debian, and they are not meant to
ever come back, add it to the blacklist in
`lp:~ubuntu-archive/+junk/sync-blacklist`, document the reason, and
`bzr commit` it with an appropriate changelog. This will avoid getting the
package back to source NEW in the next round of auto-syncs from Debian.


## Removals in Debian

From time to time we should remove packages that were removed in Debian, to
avoid accumulating unmaintained packages. This client-side tool (from
`ubuntu-archive-tools`) will interactively go through the removals and ask for
confirmation:

```bash
$ ./process-removals
```

Please note that we do need to keep some packages that were removed in Debian
(e.g. `firefox`, since we did not do the `firefox` -> `iceweasel` renaming).

## Failed SRUs

If a package should be removed from `-proposed`, use the `remove-package` tool
(from `ubuntu-archive-tools`) to remove source and binaries, e.g. for the
`libreoffice` package in `xenial-proposed`:

```bash
$ ./remove-package -m "SRU abandoned (verification-failed)" -s xenial-proposed libreoffice
```

(aa-nbs)=
## NBS

Sometimes binary packages are Not Built by any Source (NBS) any more. This
usually happens with library SONAME changes, package renames, etc. Those need
to be removed from the archive from time to time, and right before a release,
to ensure that the entire archive can be rebuilt by current sources.

Such packages are detected by `archive-cruft-check`. This tool does not check
for reverse dependencies, though, so you should use `checkrdepends -b` for
checking if it is safe to actually remove NBS packages from the archive.

Look at the
[half-hourly generated NBS report](https://ubuntu-archive-team.ubuntu.com/nbs.html)
which shows all NBS packages, their reverse dependencies, and a
copy-and-paste-able command to clean up the "safe" ones.

The rest needs to be taken care of by developers, by doing transition uploads
for library SONAME changes, updating build dependencies, etc. The remaining
files will list all the packages which still need the package in question.

Please refrain from removing NBS kernel packages for old {term}`ABIs <ABI>`
until `debian-installer` and the seeds have been updated, otherwise daily
builds of alternate and server CDs will be made uninstallable.

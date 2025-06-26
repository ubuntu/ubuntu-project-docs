(request-package-removal)
# How to request a package removal

```{note}
This page will be moved to:
* Contributors -> Advanced
```

```{note}
Content from: The Package Archive -> package-removals
`https://wiki.ubuntu.com/UbuntuDevelopment/PackageArchive#Removing_Packages`
```

Packages that are removed from Debian are semi-automatically removed from
Ubuntu `universe` on a regular basis by the administrators. However, packages
are not removed from Ubuntu `main` without an explicit request, and nor are
packages which originated elsewhere. To request removal of such a package, file
a bug against the package.

The bug must have the following elements:

* The release to remove it from (e.g., `noble`)

* Whether to remove: the source package, all binary packages, or both

* A rationale for why they should be removed

* Confirmation that the binary packages have no `rdepends` (no other package
  depends on them)

  * There is `checkrdepends` in `ubuntu-archive-tools`, but it needs a mirror
    to work with

  * There is `reverse-depends` and `reverse-depends -b` (build depends) in
    `ubuntu-dev-tools`, but it can return false positives for alternative
    dependencies

If you are not an [Ubuntu developer](https://wiki.ubuntu.com/UbuntuDevelopers)
use the {ref}`Sponsorship process <sponsorship>`.
If you *are* an Ubuntu developer then subscribe the `ubuntu-archive` team to
the bugs. If you need help deciding whether a package ought to be removed,
please discuss on the `ubuntu-devel` mailing list rather than asking the
Archive Administrators.

Refer to `https://launchpad.net/ubuntu/+source/<source package>` for the reason
of the removal of a specific package. 


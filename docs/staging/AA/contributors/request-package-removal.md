(request-package-removal)
# How to request a package removal

```{note}
This page will be moved to:
* Contributors -> Advanced
```

Packages that are removed from Debian are semi-automatically removed from
Ubuntu `universe` on a regular basis by the Archive Admin team. However, packages
are not removed from Ubuntu `main` without an explicit request, and nor are
packages which originated elsewhere.

## The removal request

To request removal of a package, file a bug against the package. The bug must
have the following elements:

* The release to remove it from (e.g., `noble`)

* What to remove:

  * the source package
  * all binary packages
  * both source and binary packages

* A rationale for why they should be removed

```{admonition} Question
:class: important

Do we need to include a list of valid reasons for removal?
```

* Confirmation that the binary packages have no `rdepends` (no other package
  depends on them)

  * There is `checkrdepends` in `ubuntu-archive-tools`, but it needs a mirror
    to work with

  * There is `reverse-depends` and `reverse-depends -b` (build depends) in
    `ubuntu-dev-tools`, but it can return false positives for alternative
    dependencies

```{admonition} Question
:class: important

What's the expected way to confirm this? What constitutes proof that this has
been checked?
```

If you are not an [Ubuntu developer](https://wiki.ubuntu.com/UbuntuDevelopers)
use the {ref}`Sponsorship process <sponsorship>`.

If you *are* an Ubuntu developer then subscribe the `ubuntu-archive` team to
the bugs.

## Getting help

If you need help deciding whether a package ought to be removed,
please discuss on the `ubuntu-devel` mailing list rather than asking the
Archive Administrators.

```{admonition} Question
:class: important

Is this still the correct way?
```

Refer to `https://launchpad.net/ubuntu/+source/<source package>` for the reason
of the removal of a specific package. 


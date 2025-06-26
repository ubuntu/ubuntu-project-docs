(archive-administration)=
# Archive Administration

```{note}
This page will be moved to:
* Who makes Ubuntu -> The Ubuntu Archive team
```

Every contributor to Ubuntu is concerned with the good health and long-term
maintainability of the Package Archive. Although many operations can be handled
by uploaders, there are certain specific activities in the Archive that
require an additional level of administrative privileges above Core Dev. These
specific activities are handled by the **Archive Administration (AA)** team.

## About the team

The team is defined on Launchpad as the
["Ubuntu Package Archive Administrators" team](https://launchpad.net/~ubuntu-archive).
They are often referred to as "Archive Admins" or just "the AA team".

## Tasks and responsibilities

The main tasks the Archive Admin team is responsible for are:

* {ref}`aa-new-review`
* {ref}`aa-package-removal`
* {ref}`aa-package-overrides`

Less commonly, they are asked to do the following tasks:

* {ref}`aa-priority-mismatches`
* {ref}`aa-signing-bootloaders`
* {ref}`aa-phasing-sru-updates`
* {ref}`aa-i386-whitelist-updates`

The following list of Archive-related services needs to be updated with details
of the charmed hosted services as they are migrated.

- {ref}`aa-archive-related-services` 


## How to contact the team

To get in contact with the Archive Admin team, you generally just need to
follow the outlined processes (using bugs).

For special cases, you can contact an Archive Admin of your choice using the
[`ubuntu-development`](https://matrix.to/#/#devel:ubuntu.com) or
[`ubuntu-release`](https://matrix.to/#/#release:ubuntu.com) channels on Matrix.

-----

```{note}
The content that follows will be deleted from this page on moving out of staging
```

Doesn't belong here (should go to maintainers -> index):

> ## Client-side tools
> Archive Administration is done client side using the LP API through various
> tools. To [get hold of these tools](https://code.launchpad.net/~ubuntu-archive/ubuntu-archive-tools/trunk):
> ```none
> $ git clone lp:ubuntu-archive-tools
> ```


Contributors -> index-advanced
```{toctree}
:titlesonly:

contributors/request-package-removal
```


Maintainers -> index-AA

```{toctree}
:titlesonly:

maintainers/aa-new-review
maintainers/aa-package-removal
maintainers/aa-package-overrides
maintainers/aa-priority-mismatches
maintainers/aa-signing-bootloaders
maintainers/aa-phasing-sru-updates
maintainers/aa-i386-whitelist-updates
maintainers/aa-archive-related-services
```

To stay in staging ->

```{toctree}
:titlesonly:

aa-museum
not-AA
```

Page still needs to be split ->

```{toctree}
:titlesonly:

new-packages
```

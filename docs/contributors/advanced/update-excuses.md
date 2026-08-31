(update-excuses)=
# update-excuses

The [update-excuses page](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_excuses.html)
is the primary tool used by archive admins to track the progress of updating packages to the next Ubuntu release.
Unfortunately, it is somewhat infamous for being difficult to read; this page aims to help.

## What is it for?

`update-excuses` essentially serves as the integration test for the entire in-development version of Ubuntu.
It presents a list of package updates that are not able to {term}`migrate` from the current version of Ubuntu to the development version.

The name is somewhat tongue-in-cheek; you can think of it as a list of excuses as to why the next version of Ubuntu isn't out yet.

When a new version of a package is created, it must of course build and pass its {term}`autopkgtests <autopkgtest>`; it will not be approved otherwise.
However, it is possible that even if the package "works" in isolation, its internals have changed in a way that causes it to not work with its dependencies or reverse-dependencies.[^why-dependency-breakage]
This is called a *migration failure*, and if it were to make it into the final Ubuntu version, then packages that claim to work together would instead break at runtime in strange ways.

Checking for migration failures is done by a tool called [Britney2](https://release.debian.org/doc/britney/index.html), which we inherited from Debian.
`update-excuses` is a dashboard view over what our Britney instance has found.

[^why-dependency-breakage]: For example, packages sometimes do not have 100% test coverage. Therefore, its tests may succeed, but a package that depends on it may rely on untested behavior that has changed between versions. See also [Hyrum's Law](https://www.hyrumslaw.com/).

## What am I looking at?

`update-excuses` presents a list of package updates that have failed to migrate, and the packages preventing it from doing so.

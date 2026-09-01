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

Part of the difficulty in reading update-excuses is that all the information about each package is in a flat list, instead of hierarchical.
Each package's information can be broken down into some sections.

1. Overall status
2. Its own failing autopkgtests (if there are any)
3. Failing autopkgtests of its reverse dependencies
4. Migration failures of its dependencies
5. Additional information.

### Overall status

This is a short blurb explaining why the package is in the `update-excuses` page.
In order from most to least common:

- `BLOCKED: Rejected/violates migration policy/introduces a regression`. This usually means that one of its reverse dependencies has a failing autopkgtest that may be due to this package.
- `BLOCKED: Cannot migrate due to another item, which is blocked`. This means that one of the package's dependencies has problems.
- `BLOCKED: Maybe temporary, maybe blocked but Britney is missing information`. Usually Britney is missing information on a build because it simply has not happened yet.
- `Waiting for test results, another package or too young (no action required now - check later)`. In this case do as the message says and be patient.
- `Will attempt migration (Any information below is purely informational)`. The package is ready to migrate; it is simply waiting for Britney to confirm the migration.

### Autopkgtests

A package cannot migrate if any of its reverse dependencies have failing autopkgtests.

Each of the package's reverse dependencies are printed, along with a status line about the tests.
For each architecture, there is a link provided to its test logs.
For packages marked as REGRESSION, there is also a recycling emoji (♲).
Clicking that button will re-run the tests.

Often times, tests appear to fail for "trivial" reasons.
For example, a package cannot run if its dependencies are not built, or if it was built in the wrong `term`{pocket}.
In an ideal world Britney would re-run such tests automatically, but for now, clicking the little recycling button can fix a surprising number of issues.

If the package itself also has failing autopkgtests, `update-excuses` will say so here.
However, this is rare, as packages aren't usually approved if their autopkgtests fail.

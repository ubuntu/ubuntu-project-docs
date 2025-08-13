---
orphan: true
---

(special-migration-cases)=
# Special migration cases


:::{admonition} **Proposed migration** series
The {ref}`proposed-migration` article series explains the various migration failures and ways of investigating them.

Process overview:
: {ref}`proposed-migration`

Issue types:
:   * {ref}`issues-preventing-migration`
    * {ref}`autopkgtest-regressions`
    * {ref}`failure-to-build-from-source-ftbfs`
    * {ref}`special-migration-cases` (this article)

Practical guidance:
: {ref}`resolve-a-migration-issue`
:::


## Circular build dependencies

When two or more packages have new versions that depend on each other's new
versions in order to build, this can lead to a
[circular build dependency](https://wiki.debian.org/CircularBuildDependencies).
There are a few different ways these come into being, which have unique
characteristics that can help find a way to work through them.


### Build-dependencies for test suites

If package A's build process invokes a test suite as part of the build (i.e. in
`debian/rules` under `override_dh_auto_test`), and the test suite requires
package B, then if package B requires package A to build, this creates a
situation where neither package will successfully build.

The workaround in this case is to (temporarily) disable running the test suite
during a build. This is usually OK when the package's autopkgtests (defined in
`debian/tests/control`) also run the test suite. For instance:

```none
override_dh_auto_test:
    echo "Disabled: phpunit --bootstrap vendor/autoload.php"
```

You may also need to delete test dependencies from `debian/control`, and/or move
them to `debian/tests/control`.

With package A's test suite thus disabled during build, it will build
successfully but then fail its autopkgtest run. Next, from package B's Launchpad
page, request rebuilds for each binary in a failed state. Once package B has
successfully built on all supported architectures, package A's autopkgtests can
be re-run using package B as a trigger.

Once everything's migrated successfully, a clean-up step would be to re-enable
package A's test suite and verify that it now passes.


### Bootstrapping

In this situation, packages A-1.0 and B-1.0 are in the archive. We're
introducing new versions A-3.0 and B-3.0 (skipping 2.0); A-3.0 depends on B-3.0,
and B-3.0 requires A-2.0 or newer. Both A-3.0 and B-3.0 will fail to build.

One example of where this can occur is if code common to both A and B is
refactored out to a new binary package that is provided in A starting at
version 2.0.

The most straightforward solution to this situation is to ask an Archive Admin
to delete both A-3.0 and B-3.0 from the Archive, then upload version A-2.0 and
allow it to build (and ideally migrate). Next reintroduce B-3.0, and then once
that's built, do the same for A-3.0.

With even larger version jumps, e.g. from A-1.0 to A-5.0, it may be necessary to
do multiple bootstraps, along with some experimentation to see which
intermediate version(s) need to be jumped to. Another common complication can be
where the cycle involves more than two packages.


## Test dependency irregularities

The package's `debian/tests/control` file
[defines what gets installed](https://salsa.debian.org/ci-team/autopkgtest/blob/master/doc/README.package-tests.rst)
in the test environment before executing the tests. You can review and verify
the packages and versions in the DEP-8 test log, between the lines
"`autopkgtest...: test integration: preparing testbed`" and
"`Removing autopkgtest-satdep`".

A common issue is that the test should be run against a version of a dependency
present in the `-proposed` pocket, however it failed due to running against the
version in `-release`. Often this is straightforward to prove by running the
autopkgtests locally in a container.

Another easy way to test this is to re-run the test but set it to preferentially
pull packages from `-proposed` -- this is done by appending `&all-proposed=1` to
the test URL. If that passes, but the package still does not migrate, then look
in the test log for all packages that were pulled from `-proposed` and include
those as triggers.
[Excuses Kicker](https://git.launchpad.net/~bryce/+git/excuses-kicker) and
[retry-autopkgtest-regressions](https://git.launchpad.net/ubuntu-archive-tools/tree/retry-autopkgtest-regressions)
are handy tools for generating these URLs.

As with rebuilds, these re-triggers also require Core Dev permissions, so if
you're not yet a Core Dev give the links to someone who is for assistance.


## Test framework timeouts and out of memory

The autopkgtest framework will kill tests that take too long to run. In some
cases it makes sense to just configure autopkgtest to let the test run longer.
This is done by setting the `long_tests` option. Similarly, some tests may need
more CPU or memory than in a standard worker. The `big_packages` option directs
autopkgtest to run these on workers with more CPU and memory. Both these options
are explained on the
[Proposed Migration wiki](https://wiki.ubuntu.com/ProposedMigration#autopkgtests)
page.

It is worthwhile to mention that Debian test sizing is currently (as of 2021)
equivalent to our `big_packages`.

The configuration that associates source packages to either `big_packages` /
`long_tests` and the actual deployment code was recently split.
[The new docs](https://autopkgtest-cloud.readthedocs.io/en/latest/administration.html#give-a-package-more-time-or-more-resources)
explain this and
[link to a repository](https://code.launchpad.net/~ubuntu-release/autopkgtest-cloud/+git/autopkgtest-package-configs)
which can now be merged by any Release Team member.


## Disabling / skipping tests

While (ideally) failing tests should receive fixes to enable them to pass
properly, sometimes this is not feasible or possible. In such extreme situations
it may be necessary to explicitly disable a test case or an entire test suite.
For instance, if an unimportant package's test failure blocks a more important
package from transitioning.

As a general rule, try to be as surgical as possible and avoid disabling more
than is absolutely required. For example, if a test has 10 sub-cases and only
one sub-case fails, prefer to comment out or delete that sub-case rather than
the entire test.

There is no single method to disabling tests, unfortunately, since different
programming languages take different design approaches for their test harnesses.
Some test harnesses have provisions for marking tests "SKIP". In other
situations it may be cleaner to add a Debian patch that simply deletes the
test's code from the codebase. Sometimes it works best to insert an early return
with a fake PASS in the particular code path that broke.

Take care, when disabling a test, to include a detailed enough explanation as to
why you're disabling it, which will inform a future packager when the test can
be re-enabled. For instance, if a proper fix will be available in a future
release, say so and indicate which version will have it. Or, if the test is
being disabled just to get another package to transition, indicate what that
package's name and expected version are. Bug reports, DEP-3 comments, and
changelog entries can be good places to document these clues.


## Disabling / skipping / customizing tests for certain architectures

If you need to disable the entire test suite for a specific architecture, such as
an arch that upstream doesn't include in their CI testing, and that sees
frequent / ample failures on our end, then you can skip the testing via checks
in the `debian/rules` file. For example (from `util-linux-2.34`):

```none
override_dh_auto_test:
ifneq (,$(filter alpha armel armhf arm64,$(DEB_HOST_ARCH)))
        @echo "WARNING: Making tests non-fatal because of arch $(DEB_HOST_ARCH)"
        dh_auto_test --max-parallel=1 || true
else ifeq ($(DEB_HOST_ARCH_OS), linux)
        dh_auto_test --max-parallel=1
endif
```

If the issue is the integer type size, here's a way to filter based on that
(from `mash-2.2.2+dfsg`):

```none
override_dh_auto_test:
ifeq (,$(filter nocheck,$(DEB_BUILD_OPTIONS)))
ifeq ($(DEB_HOST_ARCH_BITS),32)
        echo "Do not test for 32 bit archs since test results were calculated for 64 bit."
else
        dh_auto_test --no-parallel
endif
endif
```

Or based on the CPU type itself (from `containerd-1.3.3-0ubuntu2.1`):

```none
override_dh_auto_test:
ifneq (arm, $(DEB_HOST_ARCH_CPU)) # skip the tests on armhf ("--- FAIL: TestParseSelector/linux (0.00s)  platforms_test.go:292: arm support not fully implemented: not implemented")
        cd '$(OUR_GOPATH)/src/github.com/containerd/containerd' && make test
endif
```


## Skipping autopkgtesting entirely

If an autopkgtest is badly written, it may be too challenging to get it to pass.
In these extreme cases, it's possible to request that test failures be ignored
for the sake of package migration.

* Check out [`lp:~ubuntu-release/britney/hints-ubuntu`](https://git.launchpad.net/~ubuntu-release/britney/+git/hints-ubuntu)

File an MP against it with a description indicating the Launchpad bug #, the rationale
for why the test can and should be skipped, and an explanation of what will be
unblocked in the migration.

Reviewers should be `canonical-<your-team>` (e.g. `canonical-server-reporter`
for Server team members), `ubuntu-release`, and any Archive Admins or
Foundations team members you've discussed the issue with.

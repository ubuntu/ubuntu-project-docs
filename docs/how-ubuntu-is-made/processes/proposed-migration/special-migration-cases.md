(special-migration-cases)=
# Special migration cases

This article describes cases when automatic migration from the `-proposed` to `-release` pocket is blocked due to situations other than common build or test failures.

:::{admonition} **Proposed migration** series
The {ref}`proposed-migration` article series explains the various migration failures and ways of investigating them.

Process overview:
: {ref}`proposed-migration`

Practical guidance:
: {ref}`resolve-a-migration-issue`

Issue types:
:   * {ref}`failure-to-build-from-source-ftbfs`
    * {ref}`autopkgtest-regressions`
    * {ref}`issues-preventing-migration`
    * {ref}`special-migration-cases` (this article)
:::


## Circular build dependencies

When two or more packages have new versions that depend on each other's new versions in order to build, it can lead to a [circular build dependency](https://wiki.debian.org/CircularBuildDependencies). This section describes the different ways these happen, which have unique characteristics that can help find a way to resolve them.


### Build-dependencies for test suites

If the build process for package `A` invokes a test suite as part of the build (i.e. in `debian/rules` under `override_dh_auto_test`), and the test suite requires package `B`, then if package `B` requires package `A` to build, this creates a situation where neither package successfully builds.

The workaround is to (temporarily) disable running the test suite during a build (this is usually OK when the package's autopkgtests (defined in `debian/tests/control`) also run the test suite).

1. Disable test suite in package `A`. For example:

    ```none
    override_dh_auto_test:
        echo "Disabled: phpunit --bootstrap vendor/autoload.php"
    ```

   You may also need to delete test dependencies from `debian/control`, and/or move them to `debian/tests/control`.

   With the test suite of package `A` disabled during build, it builds successfully but then fails its autopkgtest run.

1. From the Launchpad page of package `B`, request rebuilds for each binary in a failed state. Wait for package `B` to
successfully build on all supported architectures.

1. Re-run autopkgtests for package `A` using package `B` as the trigger:

    ```none
    https://autopkgtest.ubuntu.com/request.cgi?release=<RELEASE>&arch=<ARCH>&package=<A>&trigger=<B>/<VERSION>
    ```

1. Once everything migrates successfully, re-enable the test suite for package `A`, and verify that it now passes.


### Bootstrapping

In this situation, packages `A-1.0` and `B-1.0` are in the archive. We're introducing new versions `A-3.0 `and `B-3.0` (skipping both `A-2.0` and `B-2.0`); `A-3.0` depends on `B-3.0`, and `B-3.0` requires `A-2.0` or newer. Both `A-3.0` and `B-3.0` fail to build.

One example of where this can occur is if code common to both `A` and `B` is refactored out to a new binary package that is provided in `A` starting at version `A-2.0`.

To resolve this situation:

1. Ask an Archive Admin to delete both `A-3.0` and `B-3.0` from the Archive.
1. Upload version `A-2.0` and allow it to build (and ideally migrate).
1. Reintroduce `B-3.0`, and wait for it to build.
1. Reintroduce `A-3.0`.

With even larger version jumps, e.g. from `A-1.0` to `A-5.0`, it may be necessary to do multiple bootstraps, along with some experimentation to see which intermediate version(s) need to be jumped to. Another common complication can be where the cycle involves more than two packages.


## Test-dependency irregularities

The package's `debian/tests/control` file defines what is installed in the test environment before executing the tests (see [Autopkgtest - Defining tests for Debian packages](https://salsa.debian.org/ci-team/autopkgtest/blob/master/doc/README.package-tests.rst)). To review and verify the packages and versions, check the DEP-8 test log between these lines:

```none
autopkgtest...: test integration: preparing testbed

[...]

Removing autopkgtest-satdep
```

A common issue is that the test should run against a version of a dependency present in the `-proposed` pocket, however, it fails due to running against the version in `-release`. This is often straightforward to prove by running the
autopkgtests locally in a container.

Another easy way to test this is to re-run the test but set it to preferentially pull packages from `-proposed` -- this is done by appending `&all-proposed=1` to the test URL (see {ref}`against-other-packages-in-proposed`). If that passes, but the package still does not migrate, look in the test log for all packages that were pulled from `-proposed`, and include those as triggers.

See {ref}`generate-test-re-trigger-urls` for guidance on how to generate autopkgtest URLs.

As with rebuilds, these re-triggers also require {term}`core dev` permissions, so if you're not yet a Core Dev, give the links to someone who is for assistance.


## Test framework timeouts and out of memory

The autopkgtest framework kills tests that run too long. In some cases, it makes sense to configure autopkgtest to let the test run longer. This is done by setting the `long_tests` option.

Similarly, some tests may need more CPU or memory than in a standard worker. The `big_packages` option directs autopkgtest to run these on workers with more CPU and memory.

TODO: Add info from [Proposed Migration wiki](https://wiki.ubuntu.com/ProposedMigration#autopkgtests):

autopkgtest tests are run in ephemeral cloud instances as described on /AutopkgtestInfrastructure. The autopkgtests can be configured to run on different types of workers in https://code.launchpad.net/~ubuntu-release/autopkgtest-cloud/+git/autopkgtest-package-configs. The README.md provides more details, but briefly, this repo specifies which VM worker should be used for a given autopkgtest execution. The big_packages file specifies packages which need more memory and CPU - by default tests run on something similar to an m1.small unit (1 vCPU and 1592 MiB Memory), while big_packages run on an m1.large (4 vCPU and 8192 Mib Memory) unit. The Debian Continuous Intergration test environment runs tests on systems with 8G of memory so if a package is passing in Debian but not Ubuntu consider running the test with more memory. The list of packages in long_tests are passed an increased timeout value ('--timeout-test=40000') to autopkgtest. Additionally, any big_packages are passed '--timeout-test=20000'. 

Changes to ^ can be merged by any Release Team member.

See also [Give a package more time or more resources](https://autopkgtest-cloud.readthedocs.io/en/latest/administration.html#give-a-package-more-time-or-more-resources)


## Disabling or skipping tests

While failing tests should receive fixes to enable them to pass properly, sometimes this is not feasible or possible. In such extreme situations, it may be necessary to explicitly disable a test case or an entire test suite. For instance, if an unimportant package's test failure blocks a more important package from transitioning.

As a general rule, try to be as surgical as possible and avoid disabling more than is absolutely required. For example, if a test has 10 sub-cases and only one sub-case fails, comment out or delete that sub-case rather than the entire test.

There is no single method to disabling tests as since different programming languages take different design approaches for their test harnesses:

* Some test harnesses have provisions for marking tests `SKIP`
* In other situations, it may be cleaner to add a Debian patch that simply deletes the test's code from the codebase.
* Sometimes, it works best to insert an early return with a fake `PASS` in the particular code path that broke.

When disabling a test, include a detailed enough explanation why you're disabling it, which informs a future packager when the test can be re-enabled. For instance:

* If a proper fix will be available in a future release, explain that and indicate which version will have it.
* If the test is being disabled to get another package to transition, indicate that package's name and expected version.

Document these clues in bug reports, DEP-3 comments, or changelog entries.


## Disabling, skipping, or customizing tests for certain architectures

To disable the entire test suite for a specific architecture, such as an architecture that upstream doesn't include in their CI testing, and that sees frequent or ample failures in Ubuntu, skip the testing via checks
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

If the issue is the integer type size, filter based on that (from `mash-2.2.2+dfsg`):

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

If an autopkgtest is badly written, it may be too challenging to get it to pass. In these extreme cases, it's possible to request that test failures be ignored to enable package migration.

Check [`lp:~ubuntu-release/britney/hints-ubuntu`](https://git.launchpad.net/~ubuntu-release/britney/+git/hints-ubuntu)

File an MP against it with a description indicating:

* Launchpad bug number
* Rationale for why the test can and should be skipped
* Explanation of what will be unblocked in the migration

As reviewers, select:

* `canonical-<your-team>` (e.g. `canonical-server-reporter` for Server team members)
* `ubuntu-release`
* Any Archive Admins or Foundations team members you've discussed the issue with

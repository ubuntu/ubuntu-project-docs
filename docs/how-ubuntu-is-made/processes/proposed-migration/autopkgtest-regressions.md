---
orphan: true
---

(autopkgtest-regressions)=
# Autopkgtest regressions

After a package has successfully built, the
[autopkgtest infrastructure](https://autopkgtest.ubuntu.com/) will run its
[DEP8 tests](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/1.0/explanation/auto-pkg-test.html)
for each of its supported architectures. Failed tests can block the migration,
and "Regression" listed for the failed architecture(s), worded in one of the
following ways.

:::{admonition} **Proposed migration** series
The {ref}`proposed-migration` article series explains the various migration failures and ways of investigating them.

Process overview:
: {ref}`proposed-migration`

Issue types:
:   * {ref}`issues-preventing-migration`
    * {ref}`autopkgtest-regressions` (this article)
    * {ref}`failure-to-build-from-source-ftbfs`
    * {ref}`special-migration-cases`

Practical guidance:
: {ref}`resolve-a-migration-issue`
:::


## Common regression reasons


### "Migration status for `aaa (x to y): <reason>`"

This means package `aaa` has a new version `y` uploaded to `-proposed`, to
replace the existing version `x`, but the change has not yet been permitted.
The various reasons typically seen are outlined in the items below.


### "Waiting for test results, another package or too young (no action required now - check later)"

This means one or more tests still need to be run. These will be noted as 'Test
in progress' under the 'Issues preventing migration' line item.


### "Will attempt migration (Any information below is purely informational)"

This is good -- it indicates the item is currently in process and will likely
migrate soon (within a day or so).


### "Waiting for another item to be ready to migrate (no action required now - check later)"

This can be good if it's recent, but if it's more than a few days old then there
may be a deeper issue going on with a dependency. If it's recent, just give it
some time (maybe a day or so). If it's older, refer to the items listed under
the 'Issues preventing migration:' line to see what specifically has gone wrong,
and then see the {ref}`issues-preventing-migration` section for diagnostic tips.


### "BLOCKED: Cannot migrate due to another item, which is blocked (please check which dependencies are stuck)"

The package itself is likely fine, but it's being blocked by some issue with
some other package. Check beneath the 'Invalidated by dependency' line to see
what package(s) need attention.


### "BLOCKED: Maybe temporary, maybe blocked but Britney is missing information (check below)"

One situation where this can occur is if one of the package's dependencies is
failing to build, which will be indicated by a line stating "`missing build on
<arch>`". Once the dependency's build failure is resolved, this package should
migrate successfully; if it doesn't migrate within a day or so, a re-trigger may
be needed.


### "BLOCKED: Rejected/violates migration policy/introduces a regression"

This indicates an "Autopkgtest Regression" with the given package, and is by far
the most common situation where your attention will be required. A typical
result will look something like:

> autopkgtest for [package]/[version]: amd64: <span style="background-color:darkred">Regression</span>, arm64: <span style="background-color:yellow">Not a regression</span>, armhf: <span style="background-color:green">Pass</span>, ppc64el: <span style="background-color:#99DDFF">Test in progress</span>, ...

The 'Regression' items indicate problems needing to be solved. See the
{ref}`issues-preventing-migration` section for diagnostic tips.

Sometimes you'll see lines where all the tests have passed (or, at least, none
are marked Regression). Passing packages are usually not shown. When they *are*
shown, it generally means that the test ran against an outdated version of the
dependency. For example, you may see:

```none
* python3-defaults (3.10.1-0ubuntu1 to 3.10.1-0ubuntu2)
    - Migration status for python3-defaults (3.10.1-0ubuntu1 to 3.10.1-0ubuntu2): BLOCKED: Rejected/violates migration policy/introduces a regression
    - Issues preventing migration:
    - ...
    - autopkgtest for netplan.io/0.104-0ubuntu1: amd64: Pass, arm64: Pass, armhf: Pass, ppc64el: Pass, s390x: Pass.
    - ...
```

In this case, check `rmadison`:

```none
$ rmad netplan.io
netplan.io | 0.103-0ubuntu7   | impish
netplan.io | 0.104-0ubuntu2   | jammy

netplan.io | 0.103-3       | unstable
```

We can see our test ran against version `0.104-0ubuntu1`, but a newer version
(`0.104-0ubuntu2`) is in the archive. If we look at the autopkgtest summary page
for one of the architectures, we see:

```none
## https://autopkgtest.ubuntu.com/packages/n/netplan.io/jammy/amd64
0.104-0ubuntu2    netplan.io/0.104-0ubuntu2   2022-03-10 11:38:36 UTC     1h 01m 59s  -   pass    log   artifacts
...
0.104-0ubuntu1    python3-defaults/3.10.1-0ubuntu2    2022-03-08 04:26:47 UTC     0h 44m 47s  -   pass    log   artifacts  
...
```

Notice that version `0.104-0ubuntu1` was triggered against the `python3`-defaults
version currently in `-proposed`, but version `0.104-0ubuntu2` was only run
against `netplan.io` itself, and thus ran against the old `python3`-defaults. We
need to have a test run against both these new versions (and against any other
of `netplan.io`'s dependencies also in `-proposed`.)

The ['excuses-kicker' tool](https://code.launchpad.net/~bryce/+git/excuses-kicker)
is a convenient way to generate the re-trigger URLs:

```none
$ excuses-kicker netplan.io
https://autopkgtest.ubuntu.com/request.cgi?release=jammy&arch=amd64&package=netplan.io&trigger=netplan.io%2F0.104-0ubuntu2&trigger=symfony%2F5.4.4%2Bdfsg-1ubuntu7&trigger=pandas%2F1.3.5%2Bdfsg-3&trigger=babl%2F1%3A0.1.90-1&trigger=python3-defaults%2F3.10.1-0ubuntu2&trigger=php-nesbot-carbon%2F2.55.2-1
...
```

Notice how it's picked up not only `python3`-defaults but also several additional
packages that `netplan.io` has been run against in the recent past. These aren't
necessarily direct dependencies for `netplan.io`, but serve as an informed guess.



(pm-autopkgtest-log-files)=
## Autopkgtest log files

You can view the recent test run history for a package's architecture by
clicking on the respective architecture's name.

Tests can fail for many reasons.

Flaky tests, hardware instabilities, and intermittent network issues can cause
false positive failures. Re-triggering the test run (via the '♻' symbol) is
typically all that's needed to resolve these. Before doing this, it is
worthwhile to check the recent test run history to see if someone else has
already tried doing that.

When examining a failed autopkgtest's log, start from the end of the file,
which will usually either show a summary of the test runs, or an error message
if a fault was hit. For example:

```none
done.
done.
(Reading database ... 50576 files and directories currently installed.)
Removing autopkgtest-satdep (0) ...
autopkgtest [21:40:55]: test command1: true
autopkgtest [21:40:55]: test command1: [-----------------------
autopkgtest [21:40:58]: test command1: -----------------------]
command1             PASS
autopkgtest [21:41:03]: test command1:  - - - - - - - - - - results - - - - - - - - - -
autopkgtest [21:41:09]: @@@@@@@@@@@@@@@@@@@@ summary
master-cron-systemd  FAIL non-zero exit status 1
master-cgi-systemd   PASS
node-systemd         PASS
command1             PASS
```

Here we see that the test named `master-cron-systemd` has failed. To see why it
failed, do a search on the page for `master-cron-systemd`, and iterate until
you get to the last line of the test run, then scroll up to find the failed test
cases:

```none
autopkgtest [21:23:39]: test master-cron-systemd: preparing testbed
...
...
autopkgtest [21:25:10]: test master-cron-systemd: [-----------------------
...
...
not ok 3 - munin-html: no files in /var/cache/munin/www/ before first run
#
#	  find /var/cache/munin/www/ -mindepth 1 >unwanted_existing_files
#	  test_must_be_empty unwanted_existing_files
#
...
...
autopkgtest [21:25:41]: test master-cron-systemd: -----------------------]
master-cron-systemd  FAIL non-zero exit status 1
autopkgtest [21:25:46]: test master-cron-systemd:  - - - - - - - - - - results - - - - - - - - - -
autopkgtest [21:25:46]: test master-cron-systemd:  - - - - - - - - - - stderr - - - - - - - - - -
rm: cannot remove '/var/cache/munin/www/localdomain/localhost.localdomain': Directory not empty
```

All autopkgtests follow this general format, although the output from the tests
themselves varies widely.

Beyond "regular" test case failures like this one, autopkgtest failures can also
occur due to missing or incorrect dependencies, test framework timeouts, and
other issues. Each of these is discussed in more detail below.


### Flaky or actually regressed in release

Tests might break due to the changes we applied -- catching those is the reason
the tests exist in the first place. But sometimes the tests do fail but are not
flaky. In that case, it is often another unrelated change to the test
environment that made it suddenly break permanently.

If you have checked the recent test run history as suggested above and have
retried the tests often enough that it seems unreasonable to continue retrying,
then you might want to tell the autopkgtest infrastructure that it shouldn't
expect this test to pass.

This can now be done via a migration-reference run. To do that, open the same
URL you'd normally use to re-run the test, but instead of `package` + `version`
as the trigger, you would add `migration-reference/0`. This is a special key,
which will re-run the tests with the version of the requested package in the
target release, without any proposed packages.

For example:

```none
https://autopkgtest.ubuntu.com/request.cgi?release=RELEASE&arch=ARCH&package=SRCPKG&trigger=migration-reference/0
```

If this fails too, it will update the expectations so that if other packages are
trying to migrate they will not be required to pass.

If this does not fail, then your assumption that your upload/change wasn't
related to the failure is most likely wrong.

More details about that can be found in the
[How to run autopkgtests of a package against the version in the release pocket](https://wiki.ubuntu.com/ProposedMigration#How_to_run_autopkgtests_of_a_package_against_the_version_in_the_release_pocket).

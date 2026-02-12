(resolve-a-migration-issue)=
# How to resolve a migration issue

This article provides guidance on how to resolve migration issues.

:::{admonition} **Proposed migration** series
The {term}`proposed migration` article series explains the various migration failures and ways of investigating them.

Process overview:
: {ref}`proposed-migration`

Issue types:
:   * {ref}`issues-preventing-migration`
    * {ref}`autopkgtest-regressions`
    * {ref}`failure-to-build-from-source-ftbfs`
    * {ref}`special-migration-cases`

Practical guidance:
: {ref}`resolve-a-migration-issue` (this article)
:::


(understand-autopkgtest-logs)=
## Understand autopkgtest logs

When examining a log of a failed autopkgtest run, start from the end of the file. This usually shows a summary of the test runs or an error message in case of an error. For example:

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

This shows that the test named `master-cron-systemd` has failed. To see why it failed, search the page for `master-cron-systemd`, and iterate until you get to the last line of the test run. Then scroll up to find the failed test cases:

```none
autopkgtest [21:23:39]: test master-cron-systemd: preparing testbed
...
...
autopkgtest [21:25:10]: test master-cron-systemd: [-----------------------
...
...
not ok 3 - munin-html: no files in /var/cache/munin/www/ before first run
#
#   find /var/cache/munin/www/ -mindepth 1 >unwanted_existing_files
#   test_must_be_empty unwanted_existing_files
#
...
...
autopkgtest [21:25:41]: test master-cron-systemd: -----------------------]
master-cron-systemd  FAIL non-zero exit status 1
autopkgtest [21:25:46]: test master-cron-systemd:  - - - - - - - - - - results - - - - - - - - - -
autopkgtest [21:25:46]: test master-cron-systemd:  - - - - - - - - - - stderr - - - - - - - - - -
rm: cannot remove '/var/cache/munin/www/localdomain/localhost.localdomain': Directory not empty
```

All autopkgtests follow this general format, although the output from different tests varies.

Beyond "regular" test case failures like this one, autopkgtest failures also occur due to missing or incorrect dependencies, test framework timeouts, and other issues. See {ref}`autopkgtest-regressions` for details.


## External test dependencies

Autopkgtest runs tests in a controlled network environment, so if a test case expects to download material from the internet, it likely fails. This usually means the test case is attempting to download of one the following:

Dependency (e.g. via PIP or Maven)

: Try to work around this by adding the missing dependency to {file}`debian/tests/control`.

Example file

: Try to make the test case use a local file, or load the file from the proxy network.


## Learn to run autopkgtest

The {term}`autopkgtest` infrastructure runs tests automatically. This section describes various ways to (re-)trigger test runs or request tests with non-standard dependencies.


### Autopkgtest with non-standard dependencies

When investigating an autopkgtest failure, try running the test against various versions of trigger packages. See [Test request format](https://autopkgtest-cloud.readthedocs.io/en/latest/architecture.html#test-request-format) in autopkgtest-cloud documentation for detailed reference.

Every autopkgtest request URL uses this format:

```none
https://autopkgtest.ubuntu.com/request.cgi?<PARAM1>=<VALUE>&<PARAM2>=<VALUE>
```

Special characters, such as `+` in `<VERSION>`, must be URL-encoded. Use, for example, the {manpage}`urlencode(1)` tool from the {pkg}`gridsite-clients` package:

```none
$ urlencode 2.15+dfsg-2
2.15%2Bdfsg-2
```

:::{list-table} Useful triggers for autopkgtest
:widths: 25 35 40
:header-rows: 1

*   - Test setup
    - Placement
    - New URL parameter
*   - Include other packages from `-proposed`
    - Append as many as needed to end of URL
    - `&trigger=<SRCPKG>/<VERSION>`
*   - Install everything from `-proposed`
    - Append to end of URL
    - `&all-proposed=1`
*   - Test against packages in `-release`
    - Substitute for existing `&trigger` value
    - `migration-reference/0`
:::


(against-other-packages-in-proposed)=
#### Against other packages in `-proposed`

By default, autopkgtest only uses only one trigger source package from the `-proposed` pocket. To specify more packages (i.e. to test a package with dependencies on other packages in the `-proposed` pocket), suffix `&trigger=<SRCPKG>/<VERSION>` to the test re-trigger URL for each additional source package to use from proposed (right-click the retry URL, copy & paste it into your browser, and append an appropriate string). To construct the URL, append the following after `https://autopkgtest.ubuntu.com/request.cgi?`:

```none
release=<RELEASE>&arch=<ARCH>&package=<SRCPKG>&trigger=<SRCPKG>/<VERSION>
```

To install *all* of the packages involved in your test from the `-proposed` pocket, append `&all-proposed=1` to the request URL (every package installed in the testbed is then installed from `-proposed`). To construct the URL, append the following after `https://autopkgtest.ubuntu.com/request.cgi?`:

```none
release=<RELEASE>&arch=<ARCH>&package=<SRCPKG>&trigger=<SRCPKG>/<VERSION>&all-proposed=1
```


#### Against packages in `-release`

To test whether an autopkgtest regression is present in the package version that's already in the `-release` and `-updates` pocket, run autopkgtest against the `-release` and `-updates` pocket only (without considering any versions that are in `-proposed`).

To do this, use the URL `&trigger` parameter with a value of `migration-reference/0` instead of specifying a trigger package and version. To construct the URL, append the following after `https://autopkgtest.ubuntu.com/request.cgi?`:

```none
release=<RELEASE>&arch=<ARCH>&package=<SRCPKG>&trigger=migration-reference/0
```

:::{note}
When finished, this test run is visible on the autopkgtest result page for the package but not on the {term}`update excuses` page.
:::

**Possible results** with the `migration-reference/0` trigger:

Test fails

: The test failure for the `-proposed` version is ignored -- the result instructs the autopkgtest infrastructure that it shouldn't expect this test to pass. Other packages trying to migrate are also not required to pass.

Test succeeds

: The assumption that the regression is already present in the package version in `-proposed` is likely incorrect. The test failure has likely been caused by the new change (upload).


#### Against a PPA

To get autopkgtest results against PPA uploads (e.g. when attempting to test a regression fix), use the `&ppa=<LPUSER>/<PPA>` parameter to the test-trigger URL. To construct the URL, append the following after `https://autopkgtest.ubuntu.com/request.cgi?`:

```none
release=<RELEASE>&arch=<ARCH>&package=<SRCPKG>&trigger=<SRCPKG>/<VERSION>&ppa=<LPUSER>/<PPA>
```

:::{important}
You must have upload rights for the package (`<SRCPKG>` above) for the test request to be successful.
:::

The test is then displayed at [`autopkgtest.ubuntu.com/running`](https://autopkgtest.ubuntu.com/running). Upon completion, the test result is available at an index page at `https://autopkgtest.ubuntu.com/results/autopkgtest-<RELEASE>-<LPUSER>-<PPA>/?format=plain`. The index contains the results for each autopkgtest run against this particular `<PPA>` for this `<RELEASE>`. To see a particular test, append the appropriate path from the index to

```none
https://autopkgtest.ubuntu.com/results/autopkgtest-<RELEASE>-<LPUSER>-<PPA>/
```


(generate-test-re-trigger-urls)=
### Generate test re-trigger URLs

While tests are discoverable in multiple ways, a user can navigate the web
overview of [`autopkgtest.`](https://autopkgtest.ubuntu.com) to find
regular patterns or they can use the {ref}`Update Excuses page <update-excuses-page>`
to analyze an issue in depth.
Each of these views allow to (re-)trigger failed tests, via interaction in the web UI.

But sometimes that would be a lot of clicks at different places, this is when
helpful tools come into play like `retry-autopkgtest-regressions`.

One way to look at it is "please give me all tests that block a particular package.
This essentially delivers all the URLs you would see for the same package at
the {ref}`Update Excuses page <update-excuses-page>` with a failure and retry icon.

```bash
./retry-autopkgtest-regressions --blocks apache2 --series resolute
https://autopkgtest.ubuntu.com/request.cgi?release=resolute&arch=s390x&package=mediawiki-extension-youtube&trigger=apache2%2F2.4.66-2ubuntu1
https://autopkgtest.ubuntu.com/request.cgi?release=resolute&arch=amd64&package=sitesummary&trigger=apache2%2F2.4.66-2ubuntu1
https://autopkgtest.ubuntu.com/request.cgi?release=resolute&arch=arm64&package=sitesummary&trigger=apache2%2F2.4.66-2ubuntu1
https://autopkgtest.ubuntu.com/request.cgi?release=resolute&arch=i386&package=sitesummary&trigger=apache2%2F2.4.66-2ubuntu1
https://autopkgtest.ubuntu.com/request.cgi?release=resolute&arch=s390x&package=sitesummary&trigger=apache2%2F2.4.66-2ubuntu1
https://autopkgtest.ubuntu.com/request.cgi?release=resolute&arch=ppc64el&package=sitesummary&trigger=apache2%2F2.4.66-2ubuntu1
```

But if an issue have been found, analyzed and resolved - there often is the need
to run the test on a bigger scale. In the example above `sitesummary` was generally
broken and also blocked the migration of other packages.

While these tests could be executed one by one, that would consume more test resources.
Instead using `--blocked-by-tests` one can get URLs that will run the respective
test, against all packages that currently are blocked due to it at once.

```bash
./retry-autopkgtest-regressions --blocked-by-tests sitesummary
https://autopkgtest.ubuntu.com/request.cgi?release=resolute&arch=amd64&package=sitesummary&trigger=debconf%2F1.5.91build1&trigger=gnupg2%2F2.4.8-4ubuntu3&trigger=apache2%2F2.4.66-2ubuntu1
https://autopkgtest.ubuntu.com/request.cgi?release=resolute&arch=arm64&package=sitesummary&trigger=debconf%2F1.5.91build1&trigger=gnupg2%2F2.4.8-4ubuntu3&trigger=apache2%2F2.4.66-2ubuntu1
https://autopkgtest.ubuntu.com/request.cgi?release=resolute&arch=ppc64el&package=sitesummary&trigger=debconf%2F1.5.91build1&trigger=gnupg2%2F2.4.8-4ubuntu3&trigger=apache2%2F2.4.66-2ubuntu1
https://autopkgtest.ubuntu.com/request.cgi?release=resolute&arch=i386&package=sitesummary&trigger=gnupg2%2F2.4.8-4ubuntu3&trigger=apache2%2F2.4.66-2ubuntu1
```

There are more options, quite common for example is the use of `--all-proposed`, here an excerpt of the --help output:

```text
  --all-proposed        run tests against all of proposed, i. e. with disabling apt pinning
  --add-trigger ADD_TRIGGER
                        add trigger(s) with a $PKG/$VERSION combo
  --state STATE [STATE ...]
                        Generate commands for given test state (default: []). --state=RUNNING also enables triggering already queued and running tests
  --max-age DAYS        only consider candidates which are at most this number of days old (float allowed)
  --min-age DAYS        only consider candidates which are at least this number of days old (float allowed)
  --blocks BLOCKS       rerun only those tests that were triggered by the named package
  --blocked-by BLOCKED_BY
                        rerun only those tests that are blocked by (rdeps of) the named package
  --blocked-by-tests BLOCKED_BY_TESTS
                        rerun only those tests that are blocked by test failures of the named package
  --no-proposed         run tests against release+updates instead of against proposed, to re-establish a baseline for the test. This currently only works for packages that do not themselves
                        have a newer version in proposed.
  --only-unknown        only include tests with version of "unknown". This version can be returned in the case of breakage in the base system, or some types of infrastructure issues, and it
                        can be helpful to mass retry these only.
  --log-regex LOG_REGEX
                        only consider tests with logs matching the (Python) regular expression
```

(trigger-tests-from-the-command-line)=
### Trigger tests from the command line

To (re-)trigger several tests at once, use your `autopkgtest.ubuntu.com` credentials from a browser cookie to perform the HTTP requests from the command line.

:::{warning}
These instructions involve extracting your credentials for the {term}`autopkgtest` infrastructure from the browser. Secure the credentials, and not to share them.
:::

The credentials are available in a cookie for `autopkgtest.ubuntu.com`. There are two values to extract:

* `session`
* `SRVNAME`

1. Extract the `session` and `SRVNAME` values. See instructions on how to do it Firefox or Chromium-based browsers:

    :::::{tab-set}
    ::::{tab-item} Firefox
    :::{admonition} Using Firefox Developer Tools
    1. Browse to [autopkgtest.ubuntu.com](https://autopkgtest.ubuntu.com/), and log in.
    1. Open the {guilabel}`Developer Tools` (by pressing {kbd}`F12` or {kbd}`Ctrl+Shift+C`).
    1. Open the {guilabel}`Storage` tab.
    1. Expand the {guilabel}`Cookies` menu in the left panel.
    1. Look for an `autopkgtest.ubuntu.com` entry, and find the values for `session` and `SRVNAME`.
    :::
    ::::
    ::::{tab-item} Chromium-based
    :::{admonition} Using Chrome Developer Tools
    1. Browse to [autopkgtest.ubuntu.com](https://autopkgtest.ubuntu.com/), and log in.
    1. Open the {guilabel}`Developer Tools` (by pressing {kbd}`F12` or {kbd}`Ctrl+Shift+I`).
    1. Open the {guilabel}`Application` tab.
    1. Under {guilabel}`Storage` in the left panel, expand the {guilabel}`Cookies` item.
    1. Look for an `autopkgtest.ubuntu.com` entry, and find the values for `session` and `SRVNAME`.
    :::
    ::::
    :::::

1. Save the values in a local file (e.g., `~/.cache/autopkgtest.cookie`) with the following contents:

    ```none
    autopkgtest.ubuntu.com	TRUE	/	TRUE	0	session	<YOUR_COOKIE_SESSION_VALUE_HERE>
    autopkgtest.ubuntu.com	TRUE	/	TRUE	0	SRVNAME	<YOUR_COOKIE_SRVNAME_VALUE_HERE>
    ```

    Note that the delimiters used above are tabs (`\t`) and not spaces. If unsure, use the following commands to create the file with the right format:

    ```none
    $ printf "autopkgtest.ubuntu.com\\tTRUE\\t/\\tTRUE\\t0\\tsession\\t<YOUR_COOKIE_SESSION_VALUE_HERE>\\n" \
      > ~/.cache/autopkgtest.cookie
    $ printf "autopkgtest.ubuntu.com\\tTRUE\\t/\\tTRUE\\t0\\tSRVNAME\\t<YOUR_COOKIE_SRVNAME_VALUE_HERE>\\n" \
      >> ~/.cache/autopkgtest.cookie
    ```

1. Set proper permissions on the `.cookie` file, so other users cannot read it, e.g. `0600`:

    ```none
    $ chmod 0600 ~/.cache/autopkgtest.cookie
    ```

1. Use `curl` to trigger the autopkgtest URLs. For example:

    ```none
    $ curl --cookie ~/.cache/autopkgtest.cookie <TEST_TRIGGER_URL>
    ```

    To use a list of test-trigger URLs:

    ```none
    $ cat <FILE_WITH_TEST_URL_LIST> | vipe | xargs -rn1 -P10 \
      curl --cookie ~/.cache/autopkgtest.cookie -o /dev/null \
           --silent --head --write-out '%{url_effective} : %{http_code}\\n'
    ```

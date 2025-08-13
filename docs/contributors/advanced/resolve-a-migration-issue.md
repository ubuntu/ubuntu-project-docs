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


## Downloading test dependencies

Autopkgtest runs tests in a controlled network environment, so if a test case expects to download material from the internet, it likely fails. This usually means the test case is attempting to download of one the following:

Dependency (e.g. via PIP or Maven)
: Try to work around this by adding the missing dependency to `debian/tests/control`.

Example file
: Try to make the test case use a local file, or load the file from the proxy network.


(trigger-tests-from-the-command-line)=
## Trigger tests from the command line

To (re-)trigger several tests at once, use your `autopkgtest.ubuntu.com` credentials from a browser cookie to perform the HTTP requests from the command line.

:::{warning}
These instructions involve extracting your credentials for the {term}`autopkgtest` infrastructure from the browser. Secure the credentials, and not to share them.
:::

The credentials are available in a cookie for `autopkgtest.ubuntu.com`. There are two values to extract:

* `session`
* `SRVNAME`


### Using Firefox Developer Tools

In Firefox:

1. Browse to [autopkgtest.ubuntu.com](https://autopkgtest.ubuntu.com/), and log in.

1. Open the {guilabel}`Developer Tools` (by pressing {kbd}`F12` or {kbd}`Ctrl+Shift+C`).

1. In the {guilabel}`Storage` tab, expand the {guilabel}`Cookies` menu in the left panel.

1. Look for an `autopkgtest.ubuntu.com` entry, and find the values for `session` and `SRVNAME`.

1. Save the values in a local file (e.g., {file}`~/.cache/autopkgtest.cookie`) with the following contents:

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

You can now use {command}`curl` to trigger the autopkgtest URLs. For example:

```none
$ curl --cookie ~/.cache/autopkgtest.cookie <TEST_TRIGGER_URL>
```

To use a list of test-trigger URLs:

```none
$ cat <FILE_WITH_TEST_URL_LIST> | vipe | xargs -rn1 -P10 \
  curl --cookie ~/.cache/autopkgtest.cookie -o /dev/null \
       --silent --head --write-out '%{url_effective} : %{http_code}\\n'
```

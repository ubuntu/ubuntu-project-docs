(merge-test-the-new-build)=
# Test the new build

Before submitting a merge proposal to add the merged package to the Archive, test it to ensure there are no regressions.

::::{admonition} **Merging** series
The article series provides guidance on performing package merges.

Process overview:
:   * {ref}`merges-syncs`

```{raw} html
<span style="font-size:0.1px"></span>
```

{ref}`How to do a merge <merging>`:
:   1. {ref}`merge-preliminary-steps`
    1. {ref}`merge-process`
    1. {ref}`merge-fix-the-changelog`
    1. {ref}`merge-upload-a-ppa`
    1. {ref}`merge-test-the-new-build` (this article)
    1. {ref}`merge-git-ubuntu-merge-proposal`

Extra:
:   * {ref}`merge-manually`
    * {ref}`merge-cheat-sheet`
::::


(merge-run-package-tests)=
## Run package tests

See {ref}`how-to-run-package-tests`.


(merge-test-upgrading-from-the-previous-version)=
## Test upgrading from the previous version

1. Create and start a new LXD container to test in:

    ```none
    $ lxc launch ubuntu-daily:ubuntu/<ubuntu-codename> tester && lxc exec tester bash
    ```

1. Install the currently available version of the package you've been working on:

    ```none
    $ apt update && apt dist-upgrade -y && apt install -y at
    ```

1. Run the test:

    ```none
    echo "echo xyz > test.txt" | at now + 1 minute && sleep 1m && cat test.txt && rm test.txt
    ```

1. Add your PPA to the virtual system to upgrade the package to the version you want to test:

    ```none
    $ sudo add-apt-repository -y ppa:kstenerud/at-merge-lp1802914
    ```

    If the Ubuntu release for which you've built the package is not yet available, modify the source list entry. For example:

    ```none
    $ vi /etc/apt/sources.list.d/kstenerud-ubuntu-at-merge-lp1802914-cosmic.list
    * change cosmic to disco
    ```

1. Upgrade to the new version of the package from your PPA:

    ```none
    $ apt update && apt dist-upgrade -y
    ```

1. Test the upgraded version:

    ```none
    $ echo "echo abc > test.txt" | at now + 1 minute && sleep 1m && cat test.txt && rm test.txt
    ```


(merge-test-installing-the-latest-from-scratch)=
## Test installing the latest from scratch

1. Create and start a new LXD container to test in:

    ```none
    $ lxc launch ubuntu-daily:ubuntu/<ubuntu-codename> tester && lxc exec tester bash
    ```

1. Add your PPA to the virtual system to upgrade the package to the version you want to test:

    ```none
    $ sudo add-apt-repository -y ppa:kstenerud/at-merge-lp1802914
    ```

1. Install the new version of the package from your PPA:

    ```none
    $ apt update && apt dist-upgrade -y && apt install -y at
    ```

1. Run the test:

    ```none
    echo "echo xyz > test.txt" | at now + 1 minute && sleep 1m && cat test.txt && rm test.txt
    ```


(merge-other-smoke-tests)=
## Other smoke tests

* Run various basic commands.

* Run [regression tests](https://git.launchpad.net/qa-regression-testing).

* For a package that `Build-Depends` on itself (`openjdk`, `jruby`, `kotlin`, etc.), build it using the new version.


## Next

* {ref}`merge-git-ubuntu-merge-proposal`

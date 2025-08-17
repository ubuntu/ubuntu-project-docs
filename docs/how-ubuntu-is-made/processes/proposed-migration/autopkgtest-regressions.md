---
orphan: true
---

(autopkgtest-regressions)=
# Autopkgtest regressions

After a package has successfully built, the {term}`autopkgtest` infrastructure at [autopkgtest.ubuntu.com](https://autopkgtest.ubuntu.com/) runs its {term}`DEP-8` for each of its supported architectures. Failed tests can block the migration and result in a **Regression** listed for the failed architecture(s). The failed migrations, along with the reasons, are listed on the {term}`update excuses` page.

This article explains common regression reasons.

:::{admonition} **Proposed migration** series
The {ref}`proposed-migration` article series explains the various migration failures and ways of investigating them.

Process overview:
: {ref}`proposed-migration`

Practical guidance:
: {ref}`resolve-a-migration-issue`

Issue types:
:   * {ref}`failure-to-build-from-source-ftbfs`
    * {ref}`autopkgtest-regressions` (this article)
    * {ref}`issues-preventing-migration`
    * {ref}`special-migration-cases`
:::

## Migration status

Each package listed on the {term}`update excuses` page reports its **Migration status**. The line is in this format:

**Migration status for &lt;package&gt; (&lt;version-x&gt; to &lt;version-y&gt;): &lt;reason&gt;**

This means: package &lt;package&gt; has a new version &lt;version-y&gt; uploaded to the `-proposed` {term}`pocket`, which should replace the existing version &lt;version-x&gt;. But the change has not yet been permitted. The various reasons typically seen are outlined in the items below.

BLOCKED: Rejected/violates migration policy/introduces a regression

: This indicates an {command}`autopkgtest` **Regression** with the given package. It is by far the most common situation that requires attention. A typical result looks like this:

   :::{card}
   autopkgtest for &lt;package&gt;/&lt;version&gt;: amd64: <span style="color:#0000EE; text-decoration:underline;  background-color:#FF6565">Regression</span> ♻,  arm64: <span style="color:#0000EE; text-decoration:underline; background-color:#E5C445">Not a regression</span>, armhf: <span style="color:#0000EE; text-decoration:underline; background-color:#86D86B">Pass</span>, ppc64el: <span style="color:#0000EE; text-decoration:underline; background-color:#98DCFE">Test in progress</span>, ...
   :::

   The **Regression** items indicate problems needing to be solved. See the {ref}`issues-preventing-migration` section for diagnostic tips.

Waiting for test results, another package or too young (no action required now - check later)

: This means one or more tests still need to run. These are noted as **Test in progress** under the **Issues preventing migration:** line.

Will attempt migration (Any information below is purely informational)

: This is good -- it indicates the item is currently in process and is likely to migrate soon (within a day or so).

Waiting for another item to be ready to migrate (no action required now - check later)

: This is usually good if it's recent, but if it's more than a few days old, then there may be a deeper issue with a dependency. For items that are:

   * Recent: wait (a day or so)
   * Few days old: refer to the items listed under the **Issues preventing migration:** line to see what specifically has gone wrong, and then see the {ref}`issues-preventing-migration` article for diagnostic tips.

BLOCKED: Cannot migrate due to another item, which is blocked (please check which dependencies are stuck)

: The package itself is probably fine, but it's blocked by an issue with some other package. Check beneath the **Invalidated by dependency** line to see what package(s) need attention.

BLOCKED: Maybe temporary, maybe blocked but Britney is missing information (check below)

: This often occurs when one of the package's dependencies is failing to build, which is indicated by a line stating **missing build on &lt;arch&gt;**. Once the dependency's build failure is resolved, this package should migrate successfully. If it doesn't migrate within a day or so, re-trigger the test.

:::{tip}
In case of unreliable tests, hardware instabilities, and intermittent network issues, re-triggering a test run (by clicking the ♻ symbol) is often the only thing needed to achieve a **Pass** result. Before doing so, check the recent test-run history to see if someone else has already tried doing that. To view the recent test-run history for a specific architecture, click the respective name of the architecture.
:::


### All tests passing

Passing packages are usually not shown. When no test is marked **Regression**, it generally means that the test ran against an outdated version of the dependency. For example, you may see:

:::{card}
Example: All tests passing
^^^
* python3-defaults (3.10.1-0ubuntu1 to 3.10.1-0ubuntu2)
    - Migration status for python3-defaults (3.10.1-0ubuntu1 to 3.10.1-0ubuntu2): BLOCKED: Rejected/violates migration policy/introduces a regression
    - Issues preventing migration:
    - ...
    - autopkgtest for netplan\.io/1.1.2-2ubuntu1: amd64: <span style="color:#0000EE; text-decoration:underline; background-color:#86D86B">Pass</span>, arm64: <span style="color:#0000EE; text-decoration:underline; background-color:#86D86B">Pass</span>, armhf: <span style="color:#0000EE; text-decoration:underline; background-color:#86D86B">Pass</span>, ppc64el: <span style="color:#0000EE; text-decoration:underline; background-color:#86D86B">Pass</span>, s390x: <span style="color:#0000EE; text-decoration:underline; background-color:#86D86B">Pass</span>.
    - ...
:::

In this case, use the {command}`rmadison` tool to check versions of the package in the Ubuntu Archive:

```none
$ rmadison netplan.io
 netplan.io | 1.1.2-2ubuntu1    | plucky          | source, amd64, arm64, ...
 netplan.io | 1.1.2-2ubuntu1.1  | plucky-updates  | source, amd64, arm64, ...
 netplan.io | 1.1.2-7ubuntu2    | questing        | source, amd64, arm64, ...
```

Note the test ran against version `1.1.2-2ubuntu1`, but a newer version (`1.1.2-7ubuntu2`) is in the Archive. Look at the [autopkgtest summary page](https://autopkgtest.ubuntu.com/packages/n/netplan.io/jammy/amd64) for one of the architectures:

:::{list-table} [`https://autopkgtest.ubuntu.com/packages/n/netplan.io/jammy/amd64`](https://autopkgtest.ubuntu.com/packages/n/netplan.io/jammy/amd64)

*   - 0.104-0ubuntu2
    - netplan\.io/0.104-0ubuntu2
    - 2022-03-10<br>11:38:36<br>UTC
    - 1h 01m<br>59s
    - \-
    - ✔ pass
    - log
    - artifacts
*   - _[...]_
    -
    -
    -
    -
    -
    -
    -
*   - 0.104-0ubuntu1
    - python3-defaults/3.10.1-0ubuntu2
    - 2022-03-08<br>04:26:47<br>UTC
    - 0h 44m<br>47s
    - \-
    - ✔ pass
    - log
    - artifacts
:::

Notice:

* Version `0.104-0ubuntu1` was triggered against the `python3-defaults` version currently in `-proposed` (`3.10.1-0ubuntu2`).

* But version `0.104-0ubuntu2` only ran against `netplan.io` itself, and thus ran against the old `python3-defaults`.

A test needs to run against both of these new versions (and against any other dependencies of the {pkg}`netplan.io` package that are also in `-proposed`).

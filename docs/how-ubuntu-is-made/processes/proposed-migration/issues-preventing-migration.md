---
orphan: true
---

(issues-preventing-migration)=
# Issues preventing migration

Packages fail to migrate for a many different reasons. Sometimes the clues listed under the **Issues preventing migration:** line item on the {term}`update excuses` page are enough to indicate the next action needed; that is the focus of this article.

In other cases, the autopkgtest log file needs to be analyzed. For that, see {ref}`understand-autopkgtest-logs`.

:::{admonition} **Proposed migration** series
The {ref}`proposed-migration` article series explains the various migration failures and ways of investigating them.

Process overview:
: {ref}`proposed-migration`

Practical guidance:
: {ref}`resolve-a-migration-issue`

Issue types:
:   * {ref}`failure-to-build-from-source-ftbfs`
    * {ref}`autopkgtest-regressions`
    * {ref}`issues-preventing-migration` (this article)
    * {ref}`special-migration-cases`
:::


(main-universe-binary-mismatch)=
## `main`/`universe` binary mismatch

A given source package may have some binaries in `main` and others in `universe`, but this can get mixed up for various reasons. This type of issues, known as "component mismatches" (see the list of current [Component mismatches](https://ubuntu-archive-team.ubuntu.com/component-mismatches.html)), looks like this in the list of migration excuses:

```none
php8.1-dba/amd64 in main cannot depend on libqdbm14 in universe
```

Check the prior release to see if `php8.1-dba` and `libqdbm14` were both in `main`, or both in `universe`:

Both packages were previously in `universe`:
: * Most likely the package in `main` needs to be demoted to `universe`. Ask an Archive Admin to do this, or file a bug report (for an example, see [LP: #1962491](https://bugs.launchpad.net/ubuntu/+source/php8.1/+bug/1962491)).

  * If the dependency in `universe` needs to be in `main`, for example a newly introduced binary package, then file a {ref}`main-inclusion-review` bug report.

Both packages were previously in `main`:
: Investigate why the `universe` package was moved out of `main`. The resolution may be to:

  * Move one or the other package, so they're both in the same pocket.
  * Find a way to remove the dependency between them.

:::{note}
**Extra-includes and unintended dependencies**

One very special case of a component mismatch is unintended dependencies due to extra-includes. While most dependencies seem obvious (seeds --> packages --> packages) there is an aspect of {term}`germinate` (see [germinate-output](https://ubuntu-archive-team.ubuntu.com/germinate-output/) for a list of outputs for all flavors) that automatically includes all `-dbg`, `-dev`, and `-doc*` packages in a source archive that is in `main` (look for line with `Extra-Include:` in the [`supported`](https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/ubuntu/tree/supported) seed). In {command}`germinate`, these appear as `Rescued from <src>`.

If a merge is affected, the solution -- without adding delta -- usually is to add an `Extra-exclude` to the {file}`supported` file. See an [example with `net-snmp`](https://code.launchpad.net/~sergiodj/ubuntu-seeds/+git/ubuntu/+merge/414063).
:::

For more information on component mismatches, from an Archive Administration perspective, see {ref}`aa-package-overrides`.


(impossible-depends)=
## Impossible depends

A migration excuse in this format:

```none
Impossible Depends: <AAA> -> <BBB>/<VERSION>/<ARCH>
```

means package `<AAA>` has a dependency on package `<BBB>`, version `<VERSION>`, for architecture `<ARCH>`, but it is not possible to satisfy this.

One reason this can occur is if the package `<BBB>` is in `universe` whereas `<AAA>` is in `main`. It may be that some of package `<AAA>`'s binaries need to be moved to `universe`. See {ref}`main-universe-binary-mismatch` for directions.


(migrating-makes-something-uninstallable)=
## Migrating makes something uninstallable

A migration excuse in this format:

```none
migrating [<AAA>]/[<AAA>-<NEW-VERSION>]/[ARCH] to testing makes [<BBB>]/[<BBB>-<VERSION>]/[arch] uninstallable
```

means that package `<BBB>` has a versioned build dependency against the old version of package `<AAA>`. A no-change rebuild can be used in these cases to force a rebuild.


## Depends: `<AAA> [<BBB>]` (not considered)

A migration excuse in this format:

```none
Depends: <AAA> [<BBB>] (not considered)
```

Package `<AAA>` is blocked because it depends on `<BBB>`, however, `<BBB>` is either invalid or rejected.

If the dependency itself is not valid, this line is followed by an **Invalidated by dependency** line. In this case, look at the situation with package `<BBB>`, and resolve that first in order to move package `<AAA>` forward.

If there is no **Invalidated by dependency** line, then the dependency may be rejected. There are three reasons why a rejection can occur:

1. It needs approval
1.  determine if permanent, or
3. permanent rejection.


(implicit-dependency-aaa-bbb)=
## Implicit dependency: `<AAA> [<BBB>]`

A migration excuse in this format:

```none
Implicit dependency: <AAA> [<BBB>]
```

An implicit dependency is a pseudo dependency where **Breaks**/**Conflicts** creates an inverted dependency. For example, `<BBB>` **Depends** on `<AAA>`, but `<AAA>=2.0-1` breaks `<BBB>=1.0-1`, so `<BBB>=2.0-1` must migrate first (or they must migrate together).

A way to handle this is to re-run autopkgtest for `<BBB>` (for 2.0-1) and include a trigger for `<AAA>=2.0`. For example:

```none
$ excuses-kicker -t <AAA> <BBB>
```

This can also occur when:

* `<BBB>` has **Depends: &lt;AAA&gt; (&lt;&lt; 2.0)**, due to the use of some non-stable internal interface.

* `<AAA>` has a **Provides** that changes from `1.0-1` to `2.0-1`, but `<BBB>` has a **Depends** on the earlier version.


## Implicit dependency: `<AAA> [<BBB>]` (not considered)

A migration excuse in this format:

```none
Implicit dependency: <AAA> [<BBB>] (not considered)
```

Similar to {ref}`implicit-dependency-aaa-bbb`, `<AAA>` and `<BBB>` are intertwined, but `<BBB>` is also either
invalid or rejected. In these cases, resolve the issue(s) for `<BBB>` and then re-run the autopkgtest for it
with `<AAA>` as the trigger.


## Has no binaries on arch `<ARCH>`

A migration excuse in this format:

```none
Has no binaries on arch <ARCH>
```

This usually means the package has either failed to build or failed to upload the binaries for a build. See {ref}`failure-to-build-from-source-ftbfs` for tips on how to handle this class of problems.


## Has no binaries on any arch (`- to X.Y.Z`)

A migration excuse in this format:

```none
Has no binaries on any arch (- to X.Y.Z)
```

If the package doesn't have a current version, this error can indicate:

* The package is not (yet) in the Archive.
* Its binaries were removed previously but not sync-blocklisted and thus reappeared.

If the package should not be synced into the Archive, on [#release:ubuntu.com](https://matrix.to/#/#release:ubuntu.com), request to remove the packages' binaries and add them to [sync-blocklist.txt](https://ubuntu-archive-team.ubuntu.com/sync-blocklist.txt).

<!-- 'stable_distro' defined in conf.py -->

Otherwise, check the {{ '[Upload queue](https://launchpad.net/ubuntu/{}/+queue)'.format(stable_distro) }} in Launchpad:

* {{ '[Stuck in New queue](https://launchpad.net/ubuntu/{}/+queue?queue_state=0)'.format(stable_distro) }}
* {{ '[Stuck in Unapproved queue](https://launchpad.net/ubuntu/{}/+queue?queue_state=1)'.format(stable_distro) }}


## No reason - still stuck?

If the package, as shown in [update_excuses](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_excuses.html), looks good but is not migrating, it might mean an installability conflict. Do not be confused by the **Will attempt migration (Any information below is purely informational)** status - there are more checks happening afterwards. This is checked and reported in [update output.txt](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_output.txt).


### Parse the {file}`update_output.txt` file

Using the {pkg}`exim4` package as an example.

1. Find the package in [update output.txt](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_output.txt):

    ```none
    trying: exim4
    skipped: exim4 (4, 0, 137)
        got: 11+0: a-0:a-0:a-0:i-2:p-1:r-7:s-1
        * riscv64: sa-exim
    ```

    This means that if {pkg}`exim4` goes into the `-release` pocket, {pkg}`sa-exim` becomes uninstallable in the `-release` pocket on `riscv64`.

    :::{note}
    Architectures are checked in a fixed order, and only the problems on the first architecture with problems are shown.
    :::

    Explanation of the lines in the output:

    `skipped: exim4 (4, 0, 137)`
    : This means:

        * 4 packages have already been found that won't be planned to be upgraded because they would break dependencies, i.e. they are rejected.

        * 0 packages are unsure ("maybe rejected").

        * 137 packages remain to be examined after this package before this check of all packages is completed.

    `got: 11+0: a-0:a-0:a-0:i-2:p-1:r-7:s-1`
    : The `got` line shows the number of problems in the release pocket on the different architectures (until the first architecture where a problem is found). In this case, it's 11 uninstallable packages on all architectures together. The letters stand for (in this order):

        * `a`: amd64
        * `a`: arm64
        * `a`: armhf
        * `i`: i386
        * `p`: ppc64el
        * `r`: riscv64
        * `s`: s390x

        The `i-2` means that if {pkg}`exim4` would go into the `-release` pocket, there would be 2 uninstallable packages on `i386`.

1. Try to reproduce that in a `-proposed`-enabled container. In this example:

    ```none
    root@k:~# apt install exim4 sa-exim
    ...
    The following packages have unmet dependencies:
    sa-exim : Depends: exim4-localscanapi-4.1
    ```

1. Now that it's confirmed, compare the old and new `exim4`:

    ```none
    root@k:~# apt-cache show exim4-daemon-light | grep -e scanapi -e '^Versi'
    Version: 4.96-3ubuntu1
    Provides: exim4-localscanapi-6.0, mail-transport-agent
    Version: 4.95-4ubuntu3
    Provides: exim4-localscanapi-4.1, mail-transport-agent
    ```

1. Therefore, the example needs (as is most often the solution in these cases) a no-change rebuild to pick up the new dependency. Do a test build to ensure it works, and submit an upload to resolve this situation.

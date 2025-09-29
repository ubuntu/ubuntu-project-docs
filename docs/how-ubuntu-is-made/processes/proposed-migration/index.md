(proposed-migration)=
# Proposed migration

```{toctree}
:maxdepth: 1
:hidden:

failure-to-build-from-source-ftbfs
autopkgtest-regressions
issues-preventing-migration
special-migration-cases
```

Uploads of {ref}`fixed <how-to-fix-a-bug-in-a-package>` or {ref}`merged <merges>` packages are not automatically released to Ubuntu users. Instead, they go into a special {term}`pocket` called `-proposed` for testing and integration. Once a package is deemed OK, it **migrates** into the `-release` pocket for users to consume. This is called the "proposed migration" process.

This article series outlines the upload and migration process.

:::{admonition} **Proposed migration** series
The article series explains the various migration failures and ways of investigating them.

Process overview:
: {ref}`proposed-migration` (this article)

Practical guidance:
: {ref}`resolve-a-migration-issue`

Issue types:
:   * {ref}`issues-preventing-migration`
    * {ref}`autopkgtest-regressions`
    * {ref}`failure-to-build-from-source-ftbfs`
    * {ref}`special-migration-cases`
:::


(lifecycle-of-an-upload)=
## Lifecycle of an upload

1. Issue identified, fixed, and packaged.

1. The `*source.changes` file uploaded.

1. If the fix is an {term}`SRU`, or if the release cycle is in a {ref}`feature-freeze`:

   * Upload goes into the `unapproved` queue.
   * The SRU team reviews and approves the upload (go to 4).
   * The SRU team disapproves (go to 1).

1. The upload goes into the `[codename]-proposed` queue.

1. Launchpad builds binary package(s) the from source package.

1. {ref}`Autopkgtests <automatic-package-testing-autopkgtest>` run on the Ubuntu infrastructure:

   * Autopkgtests for the package itself.
   * Autopkgtests for the reverse{-build}-dependencies.

1. Archive consistency checks:

   * Are binary packages installable?
   * Are all required dependencies at the right version?
   * Does it cause anything to become uninstallable?
   * etc.

1. If (and only if) the fix is an SRU:

   * [SRU bug](https://documentation.ubuntu.com/sru/en/latest/howto/common-issues/) updated with a request to verify.
   * Reporter or developer verifies the fix and updates tags.

1. Package released from `[codename]-proposed` to `[codename]`.


(migration-issues)=
## Migration issues

The migration often proceeds automatically, but when issues arise, someone needs to resolve the problem. It is generally the responsibility of the uploader to analyze and {ref}`resolve the issue <resolve-a-migration-issue>`.

Other situations, for which there is no specific responsible party, can also lead to migration trouble. These types of problems are focused on as part of the {ref}`plus-one-maintenance` effort, where individuals across the distribution team are tasked with examining and resolving issues. Some of these problems arise from items auto-synced from Debian, or via a side-effect of some other change in the distribution.


(update-excuses-page)=
## Update-excuses page

All unresolved migration issues for the current development release are displayed on the [Update Excuses page](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_excuses.html). Similar pages exist for stable releases: [proposed-migration](https://ubuntu-archive-team.ubuntu.com/proposed-migration/) (these items generally relate to particular SRUs). These pages are created by a software service named {term}`Britney`, which updates the page after each batch of test runs, typically every 2--3 hours depending on load.

The page is ordered from newest to oldest, so the items at the top of the page may still be processing (indicated by "Test in progress" marked for one or more architectures). There is also a variant of the page that groups the items by maintainer teams: [devel-proposed by team](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_excuses_by_team.html).

In general, there are two things to watch for:

"Missing builds"
: Can indicate a failure to build the source package ({term}`FTBFS`).

"Regressions"
: Indicates a ({term}`autopkgtest`) test failure.

Both of these situations are described in more depth in this article series.

Many of the items on the page are not actually broken -- they're just blocked by something else that needs resolving. This often happens for new libraries or language runtimes, or any package that a lot of other things depend on to build, install, or run tests against.

See the articles in the series for details on how to interpret the status reported on the {term}`update excuses` page:

* {ref}`failure-to-build-from-source-ftbfs`
* {ref}`autopkgtest-regressions`
* {ref}`issues-preventing-migration`
* {ref}`special-migration-cases`


(finding-issues-to-resolve)=
### Finding issues to resolve

Look for build failures towards the upper-middle of the page, particularly those affecting only one architecture. Single-arch build failures tend to be more localized and more deterministic in their cause. Items towards the top of the page (but after all the **"Test in progress"** items) are newer, and so have a higher chance of being something simple that fewer people have looked at yet, without being so new that it's still being actively worked on by someone.

:::{tip}
For tasks like {ref}`plus-one-maintenance` where the goal is to ensure not too much migration backlog builds up, it's helpful to use the {command}`visual-excuses` tool, which visualizes the excuses page in different ways. Such tools can help unblock a lot with only a few changes - but be careful, depending on these tools only causes less central cases to be stuck for a long time.

Install {command}`visual-excuses` with:

```none
$ sudo snap install visual-excuses
```
:::

To check whether someone is already working on an item, ask in the [Ubuntu Devel Matrix channel](https://matrix.to/#/#devel:ubuntu.com). For any case that requires more effort or a deeper analysis, submit an {ref}`update-excuses bug <bug-reports-for-migration-problems>` to help with coordination.


(bug-reports-for-migration-problems)=
#### Bug reports for migration problems

When you file a bug report about a build or test failure shown on the {ref}`update-excuses-page`, tag the bug report `update-excuse`. {term}`Britney` then includes a link to the bug report the next time it refreshes the {ref}`update-excuses-page` page. This helps other developers see the investigative work you've already done and can be used to identify the next action. Mark yourself as the *Assignee* if you're actively working on the issue, and leave the bug unsubscribed if you aren't, so that others can carry things forward.


## Further reading

* {ref}`resolve-a-migration-issue`
* [Visualizing and Exploring Ubuntu Excuses](https://discourse.ubuntu.com/t/visualizing-and-exploring-ubuntu-excuses/59824)

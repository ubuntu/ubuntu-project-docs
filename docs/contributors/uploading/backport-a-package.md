(how-to-backport-a-package)=
# How to backport a package

Backporting makes new functionality available in a stable Ubuntu release. Unlike the {ref}`SRU process <stable-release-updates>`, which only applies to bug fixes, backports can introduce new features.

For an overview of what backports are, see {ref}`backports`.

:::{admonition} **Sponsorship** series
The article series provides guidance on requesting sponsorship and sponsoring.

Overview:
:   * {ref}`sponsorship`

For contributors:
:   * {ref}`how-to-find-a-sponsor`
    * {ref}`how-to-request-an-upload`
    * {ref}`how-to-request-a-sync`
    * {ref}`how-to-backport-a-package` (this article)

For sponsors:
:   * {ref}`how-to-review-a-merge-proposal`
    * {ref}`how-to-sponsor-an-upload`
    * {ref}`how-to-sponsor-a-sync`
:::


## Requesting a backport

File a bug against the package you want to backport, subscribe the `ubuntu-backporters` team, and summarize the key fixes or features that justify the backport. Unlike an SRU, you do not need to list every fixed bug — a summary of the main reasons is sufficient.

Backports are intended for new features, not for bug fixes that could go through the SRU process. If the only motivation is a bug fix, use the SRU process instead.


## Rules

* Some packages are forbidden from backporting (see below).
* Backports to non-LTS releases are not accepted, with specific exceptions.
* Backports should come from:
  * The current Ubuntu stable release (preferred), or
  * The current LTS release, targeting the prior LTS release, or
  * The current package version in the Ubuntu development release.
* Users must be able to upgrade from LTS to LTS. Backported packages must not break the upgrade path between releases.

### Forbidden packages

Some packages are handled exclusively by the Ubuntu Backports Team and cannot be backported by contributors. For the current list, check with the team in the tracking bug or on the [ubuntu-backporters mailing list](https://lists.ubuntu.com/mailman/listinfo/ubuntu-backporters).


## Preparing the backport

Prepare the backported package and make it available for review. You can:

* Provide a `debdiff` against the version you are backporting from.
* Link to a PPA where you have a backported build prepared.

The format is up to your sponsor — ask them what they prefer.

For a refresher on building packages locally, see {ref}`how-to-build-packages-locally`.


## Review and upload

Once you have prepared the backport, request a sponsor to review and upload it. Follow the standard {ref}`sponsorship <how-to-find-a-sponsor>` process.

The sponsor will review the package for:

* Correctness of the backport (no unnecessary changes).
* Compatibility with the target release.
* No regressions introduced.


## Responsibilities

As the backporter, you are responsible for:

* Monitoring the backported package for bug reports, security patches, and additional updates that should be backported.
* Any backport-specific bugs that were not present in the original version.


## See also

* {ref}`backports`
* {ref}`stable-release-updates`
* {ref}`how-to-upload-packages-to-a-ppa`
* [Ubuntu Backports user documentation](https://help.ubuntu.com/community/UbuntuBackports)
* [Ubuntu Backports team policies](https://wiki.ubuntu.com/UbuntuBackports/Policies)

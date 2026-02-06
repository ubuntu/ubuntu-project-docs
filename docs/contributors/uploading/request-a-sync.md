(how-to-request-a-sync)=
# How to request a sync

When an Ubuntu package carries a delta, but it is no longer needed (because it has been merged in Debian or upstream), request a manual sync. This article describes how to request a sync.

:::{admonition} **Sponsorship** series
The article series provides guidance on requesting sponsorship and sponsoring.

Overview:
:   * {ref}`sponsorship`

For contributors:
:   * {ref}`how-to-find-a-sponsor`
    * {ref}`how-to-request-an-upload`
    * {ref}`how-to-request-a-sync` (this article)

For sponsors:
:   * {ref}`how-to-review-a-merge-proposal`
    * {ref}`how-to-sponsor-an-upload`
    * {ref}`how-to-sponsor-a-sync`
:::

Before submitting a sync request, check the [sponsorship queue](http://sponsoring-reports.ubuntu.com/) (all review requests with the `ubuntu-sponsors` subscribed) that a similar request has not been filed already.

:::{important}
A sync cannot be reversed. Check the package thoroughly before requesting a sync. If there are Ubuntu changes in the current package, ensure the Ubuntu changes have been merged or are no longer relevant. If the Ubuntu changes are still relevant, the package should be merged from Debian, not synced.
:::


## Special considerations

Freezes and exceptions
: The automatic syncing of packages from Debian is only active for some of the Ubuntu release cycle - see {ref}`debian-import-freeze` for more information. To request a sync after the freeze, you need a {ref}`freeze-exceptions`.

  Before seeking an exception, review the Debian changes to make sure the fixes would improve Ubuntu; some changes (maintainer change, new uploader, NMU (Non-Maintainer Upload) acknowledgement with no additional fixes, etc.) are better left for the next cycle.

Fakesync
: If the version in Ubuntu is a `-0ubuntu*` version, i.e. it introduces a new upstream that Debian doesn't have, check that the md5sum of the `.orig.tar.gz` in the Ubuntu archive matches the md5sum of the tarball in the Debian archive (or wherever the sync is from).

  If it does not match, there's a possibility the source package cannot be unpacked, or it is not valid. If it does not match, request a "fakesync".

Sync not necessary
: An explicit sync is not necessary when all of the following is true:

  * It's before {ref}`debian-import-freeze` (check the {{ '[Ubuntu release schedule]({})'.format(release_schedule) }}).
  * The Ubuntu version of the package has no Ubuntu changes.
  * The Debian package is in Debian `unstable` (SID) (or in `testing` for LTS releases of Ubuntu).


## Use the {command}`requestsync` tool

{command}`requestsync` is a tool (from the {pkg}`ubuntu-dev-tools` package) that automates the bureaucratic part of the sync-request process.

{command}`requestsync` performs the following actions:

1. Checks the versions of the source package in Debian and Ubuntu.
1. Prompts for an explanation of why the Ubuntu changes (if any) should be dropped.
1. Downloads the new Debian changelog entries
1. Files a request-sync bug in Launchpad.

For details on using the tool, see the {manpage}`requestsync(1)` manual page.


## Request a sync manually

When there's only a single patch, open a bug with the required information. Cases like this include:

* Debian adopts the same patch as Ubuntu, possibly with a different name.
* Upstream has accepted the change, Debian includes upstream, and Ubuntu can drop its delta.

When multiple changes are adopted, and many patches can be dropped, submit a {term}`merge proposal`, so the reviewers can understand the change. Ensure there is an accompanying bug (either change an automatic merge bug to a sync, or file a new sync bug).

Sync-request bug
:   * Bug {guilabel}`Summary` must include:
    * Source package name.
    * Source package version number to sync.
    * Where to sync from (e.g. "Debian sid main").
    * Bug {guilabel}`Description` must include:
    * If there are Ubuntu changes apart from {file}`debian/changelog`, or if {ref}`feature-freeze` is in effect:
        * A copy of the entries from {file}`debian/changelog` corresponding to the changes relative to the current version in Ubuntu.
    * If there are Ubuntu changes:
        * A description of each of the Ubuntu changes (a bullet point list, not copies of {file}`debian/changelog`).
        * A brief explanation of why each change can be dropped (e.g., it's been merged into Debian, is no longer appropriate, etc.).
        * An explicit confirmation that the Ubuntu changes should be overridden.
    * Include the patch that has been adopted upstream.
    * Subscribe (_not_ assign) the `ubuntu-sponsors` team.
    * Don't change the status of the bug or put it back to {guilabel}`New`; package sponsors use this field.

Sync-request merge proposal
:   * Specify that the MP is for a sync request.
    * Explain how you discovered it is a sync:
        * changelog entries
        * step in which the empty commit message appeared
        * point to upstream Git repository
        * etc.
    * Change the changelog using `dch -i` to get a new version with the `ubuntu1` suffix and check the Ubuntu series for which the package is to be built. Include the following in the new changelog entry:

        ```none
        Build Debian version to verify before a sync
        ```

    * {ref}`Build the source package <how-to-build-packages-locally>` and upload to the PPA you're using in this MP.

Useful examples:

* Simple sync: {pkg}`sass-spec` bug for 25.04: {lpbug}`2098389`.
* Complex sync: {pkg}`freeipmi` MP for 21.10: [MP: #407014](https://code.launchpad.net/~mirespace/ubuntu/+source/freeipmi/+git/freeipmi/+merge/407014).

## Further reading

* {ref}`merges-syncs`

(how-to-sponsor-a-sync)=
# How to sponsor a sync

Use these instructions when sponsoring an upload.

:::{admonition} **Sponsorship** series
The article series provides guidance on requesting sponsorship and sponsoring.

Overview:
:   * {ref}`sponsorship`

For contributors:
:   * {ref}`how-to-find-a-sponsor`
    * {ref}`how-to-request-an-upload`
    * {ref}`how-to-request-a-sync`

For sponsors:
:   * {ref}`how-to-review-a-merge-proposal`
    * {ref}`how-to-sponsor-an-upload`
    * {ref}`how-to-sponsor-a-sync` (this article)
:::

If you have the permissions to upload the package to Ubuntu, you can issue a sync request using the {manpage}`syncpackage(1)` tool (from the {pkg}`ubuntu-dev-tools` package).

The tool asks Launchpad to copy the source-package publication entry from its import of Debian. You can do this for any package you could upload directly to Ubuntu.

To be able to use `syncpackage`, the package needs to be known to Launchpad. The process relies on several steps that need to be completed for the Debian source upload:

1. Having been processed by the Debian archive.
1. Pushed to mirrors.
1. Imported by Launchpad.

Therefore, there may be a delay before recent recent uploads are available, i.e. before you can use the `syncpackage` tool (in general, not more than a day). The Debian publication history in Launchpad shows when uploads have been imported:

`https://launchpad.net/debian/+source/<source_package_name>/+publishinghistory`

For example: [Publishing history of hello package in Debian](https://launchpad.net/debian/+source/hello/+publishinghistory).

:::{note}
Although you don't need to file a sync-request bug if you have direct upload permissions (unless you need {ref}`freeze-exceptions`), still check {ref}`how-to-request-a-sync` and make sure there's a good reason for dropping any Ubuntu changes as a result of the sync.
:::


## Use the {command}`syncpackage` tool

The general syntax of a sync request is:

```none
$ syncpackage --release=<target-Ubuntu-release> \
              --distribution=<source-Debian-distribution> \
              --verbose --force \
              <package_name>
```

For example:

```none
$ syncpackage -r questing-proposed -d unstable -v -f hello
```


## Further reading

* {ref}`merges-syncs`

(merge-upload-a-ppa)=
# Upload a PPA

Following a successful merging procedure, upload the updated package to a {term}`PPA` for building.

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
    1. {ref}`merge-review-the-changelog`
    1. {ref}`merge-upload-a-ppa` (this article)
    1. {ref}`merge-test-the-new-build`
    1. {ref}`merge-git-ubuntu-merge-proposal`

Extra:
:   * {ref}`merge-manually`
    * {ref}`merge-cheat-sheet`
::::


(merge-get-the-orig-tarball)=
## Get the orig tarball

Ubuntu doesn't know about the new tarball yet, so we must create it.

```none
$ git ubuntu export-orig
```

If the upstream version does not yet exist in Ubuntu, that is, the new package from Debian also includes a new upstream version, you should add the `--for-merge` option:

```none
$ git ubuntu export-orig --for-merge
```

If this fails, {ref}`do it manually <merge-get-the-orig-tarball-manually>`.


(merge-build-source-package)=
## Build source package

```none
$ dpkg-buildpackage \
    --build=source \
    --no-pre-clean \
    --no-check-builddeps \
    -sa \
    -v3.1.20-3.1ubuntu2
```

The switches are:

`-sa`
: include orig tarball (required on a merge)

`-vXYZ`
: include changelog since `XYZ`

As the merge upload represents all changes that happened in Debian since the last merge plus anything added as part of the merge itself, `-v` should usually point to the last published Ubuntu version. For example:

1. Ubuntu merged as `1.3-1ubuntu1`.
1. Then Ubuntu had a fix in `1.3-1ubuntu2`.
1. But in the meantime, Debian merged upstream as `1.4-1`.
1. And then Debian added a fix in `1.4-2`.
1. New Ubuntu will be `1.4-2ubuntu1`.
1. `-v` should be set to `1.3-1ubuntu2`.
   1. Thereby the `.changes` file will include `1.4-1`, `1.4-2`, and `1.4-2ubuntu1`.
   1. That represents all the changes that happened from the perspective of an Ubuntu user upgrading from `1.3-1ubuntu2` to `1.4-2ubuntu1`.

:::{note}
If sponsoring a merge or any other upload for someone else, remember the need to sign their upload with your key. See {ref}`Sponsor a package <sponsor-a-package>` for more information about that.

Furthermore just like you, the sponsor needs to know about setting `-v` right and using `-sa` when needed. If in doubt, coordinating with them is helpful.
:::


(merge-push-to-your-launchpad-repository)=
## Push to your Launchpad repository

The `submit` step of {ref}`git ubuntu deltarebase <merge-process>` pushes the branch and its tags for you.
After a manual merge, once the package builds successfully, push it to your Launchpad repository:

```none
git push <your-lp-username>
```


(merge-push-your-lp-tags)=
### Push your `lp` tags

```none
$ git push <your-git-remote> old/ubuntu old/debian new/debian \
           reconstruct/<version> logical/<version> split/<version>
```

For example:

```none
$ git push git+ssh://your-user@git.launchpad.net/~your-user/ubuntu/+source/at \
           old/ubuntu old/debian new/debian \
           reconstruct/3.1.20-3.1ubuntu2 \
           logical/3.1.20-3.1ubuntu2 \
           split/3.1.20-3.1ubuntu2

To ssh://git.launchpad.net/~your-user/ubuntu/+source/at
 * [new tag]         split/3.1.20-3.1ubuntu2 -> split/3.1.20-3.1ubuntu2
 * [new tag]         logical/3.1.20-3.1ubuntu2 -> logical/3.1.20-3.1ubuntu2
 * [new tag]         new/debian -> new/debian
 * [new tag]         old/debian -> old/debian
 * [new tag]         old/ubuntu -> old/ubuntu
 * [new tag]         reconstruct/3.1.20-3.1ubuntu2 -> reconstruct/3.1.20-3.1ubuntu2
```


(merge-create-a-ppa)=
## Create a PPA

You need to have a {term}`PPA` for reviewers to test.

(merge-create-a-ppa-repository)=
### Create a PPA repository


(merge-create-a-ppa-repository-manually)=
### Create a PPA repository manually

`https://launchpad.net/~<your-username>/+activate-ppa`

Give it a name that identifies its contents, for example `lp<bugid>-<package_name>-<description>` such as `lp123456789-openldap-merge`.

:::{important}
Be sure to enable all architectures to check that it builds (click {guilabel}`Change details` in the top right corner of the newly created PPA page).
:::

The URL of the PPA is formed as follows:

`https://launchpad.net/~<your-username>/+archive/ubuntu/<PPA-name>`


(merge-upload-files)=
### Upload files

Install `dput-ng`, and use it to upload a source package:

```none
$ dput ppa:your-username/lp123456789-openldap-merge ../openldap_32.13.1-1ubuntu1_source.changes
```


(merge-wait-for-packages-to-be-ready)=
### Wait for packages to be ready

1. Check the PPA page to see when packages are finished building
1. Look at the package contents to make sure they have actually been published (click {guilabel}`View package details` in the top right corner of the PPA page, or append `+packages` to its URL)

## Next

* {ref}`merge-test-the-new-build`

---
relatedlinks: "[PackagingWithGit &#32; - &#32; Debian Wiki](https://wiki.debian.org/PackagingWithGit)"
---

(maintain-ubuntu-desktop-software)=
# Maintain Ubuntu Desktop software

These are some common, day-to-day operations to build, maintain and package GNOME software for Ubuntu Desktop using the Git Build Package (`gbp`) workflow.

We use the `gnome-control-center` repository as an example.

:::{note}
Some applications on Ubuntu Desktop are developed outside of Salsa and GNOME. They have their own, separate workflows, which aren't described in this guide. The Desktop Team can help you find the right instructions on Matrix: {matrix}`desktop-dev`.
:::


## Prerequisites

Before you start, follow the instructions in {ref}`set-up-git-for-ubuntu-desktop-work`.


## Workflow overview for external contributors

If you're a community contributor and not a member of the Ubuntu Desktop Team, you have to send your contributions through a merge request:

1. Fork the Git repository on Salsa.
1. Follow this guide and make the changes in your fork.
1. Open a Salsa merge request from your fork to the original repository.

In some projects, no Ubuntu branch has been created in a long time. You might have to ask the Desktop Team to create the new branch for you. Contact them on Matrix at {matrix}`desktop-dev`.


## Local changes

With the suggested Git configuration, any non-committed changes (file modifications, additions, or removal) halt the build because they won't be included. This is a safety reminder.

What you can do when you have such changes:

* Ignore them. The resulting package and build won't include those uncommitted changes. The `../build-area/<your-package>` directory will match the last commit.

    To do this, add the `--git-ignore-new` Git option.

* Force using the current directory with your local modifications instead of the `build-area` directory, and include any local modifications to the package despite the `ignore-new` option.

    For this, add the `--git-ignore-new --git-export=INDEX` options to `gbp`.


## Refresh branches

Use the following command to refresh the current `ubuntu/<release>` branch and the corresponding `upstream/<release>` branch. This applies only to the branches referenced in the `debian/gbp.conf` file on your current checkout. Also refresh the `pristine-tar` branch. 

* For example, on the `ubuntu/latest` branch:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pull

    gbp:info: Fetching from default remote for each branch
    gbp:info: Branch 'upstream/latest' is already up to date.
    gbp:info: Branch 'ubuntu/latest' is already up to date.
    gbp:info: Updating 'pristine-tar': 2bed57f20816..e59ab7422a13
    ```

    The `pristine-tar` branch has been updated as referenced in `debian/gbp.conf`.

* If you have a separate `ubuntu/noble` branch with its own `upstream/46.x` branch:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git checkout ubuntu/noble

    :input: gbp pull

    gbp:info: Fetching from default remote for each branch
    gbp:info: Branch 'ubuntu/noble' is already up to date.
    gbp:info: Branch 'upstream/46.x' is already up to date.
    gbp:info: Branch 'pristine-tar' is already up to date.
    ```

The `gbp pull` command, contrary to `git pull`, is a way to avoid checking out each branch and pulling them one by one.


## Push your Git changes to Salsa

To contribute changes back to Salsa, push your changes using `gbp`:

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: gbp push
```


(desktop-git-merge-a-new-upstream-version-to-latest)=
## Merge a new upstream version to latest

When upstream releases a new version of a given project, you can merge the version on the Debian and Ubuntu branches.

1. Switch to the branch where you want to import the new version, such as `ubuntu/latest`:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git fetch upstreamvcs

    :input: git checkout ubuntu/latest
    ```

1. Create a `patch/queue/ubuntu/latest` branch that is useful in case you need to refresh patches later.

    * If you already have the `patch/queue` branch, rebase it:

        ```{terminal}
        :copy:
        :host:
        :dir: gnome-control-center
        :user:
        :input: gbp pq rebase
        ```

    * Otherwise, create the `patch/queue` branch:

        ```{terminal}
        :copy:
        :host:
        :dir: gnome-control-center
        :user:
        :input: gbp pq import
        ```

1. Check whether this upstream version already exists in Debian:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git tag -l | grep upstream

    […]
    upstream/46.0
    upstream/46.0.1
    upstream/46.1
    upstream/46.3
    […]
    ```

1. If Debian already has the upstream version, you don't have to import the tarball. Merge with the latest upstream code:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git merge upstream/46.3 -m "Update upstream source from tag 'upstream/46.3'"
    ```

    The new upstream version is now merged. Push the changes:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp push origin
    ```

### Merge a new upstream version to Debian

If Debian doesn't have the new upstream version, add the release to Debian and Ubuntu.

1. Scan for new releases:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: uscan --verbose --no-download

    […]
    Newest version of gnome-control-center on remote site is 49.1, local version is 46.7
     => Newer package available from:
            => https://download.gnome.org/sources/gnome-control-center/49/gnome-control-center-49.1.tar.xz
    ```

1. Is `uscan` showing the upstream release that you want to import?

    If so, you can let `gbp` download and import the latest release automatically:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp import-orig --uscan
    ```

    Otherwise, download the tarball with the new upstream release manually. Then, import the tarball:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp import-orig ../gnome-control-center-46.2.tar.xz

    What is the upstream version? [46.2] 
    gbp:info: Importing '../gnome-control-center-46.2.tar.xz' to branch 'upstream/latest'...
    gbp:info: Source package is gnome-control-center
    gbp:info: Upstream version is 46.2
    gbp:info: Replacing upstream source on 'ubuntu/noble'
    gbp:info: Successfully imported version 46.2 of ../gnome-control-center-46.2.tar.xz
    ```

1. Push all related branches:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp push origin
    ```

    The `gbp` tool handles all branches automatically. In the example of this upstream release, `gbp` pushes the `ubuntu/latest`, `pristine-tarball` + `upstream/46.x` or `upstream/latest` branches.

    Sync the affected upstream branch to Salsa, or push it to your fork and propose it as a merge request if you aren't an Ubuntu developer.

### Check for dependency changes

New upstream releases often change the dependencies of the application. Check for changes.

For example, if the application uses the Meson build system and you've updated from version `49.alpha` to `49.0`:

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: git diff 49.alpha..49.0 -- meson.build
```

Reflect the updated package dependencies in the `debian/control` file. For details, see {ref}`debian-directory`.


### Troubleshooting

You might get the following errors when importing the tarball.


#### Revision not found

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: gbp import-orig ../gnome-control-center-46.2.tar.xz

What is the upstream version? [46.2] 
gbp:info: Importing '../gnome-control-center-46.2.tar.xz' to branch 'upstream/latest'...
gbp:info: Source package is gnome-control-center
gbp:info: Upstream version is 46.2
gbp:error: Import of ../gnome-control-center-46.2.tar.xz failed: revision '…' not found
```

The reason might be one of the following:

* You didn't get the latest commits and tags in your repository metadata. Fetch them:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git fetch upstreamvcs
    ```

* Upstream has changed the tagging pattern. Update the `upstream-tag` value in the `debian/gbp.conf` file to match it. For details, see [No upstream tarballs](https://honk.sigxcpu.org/projects/git-buildpackage/manual-html/gbp.import.upstream-git.html#gbp.import.upstream.git.notarball) in the `gbp` documentation.

* Upstream is using an inconsistent release pattern. Therefore, the `debian/gbp.conf` file can't use a regular expression for the version.

    Find the exact tag:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git describe --tags --abbrev=0 upstreamvcs/main
    ```

    Specify the version manually:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp import-orig <tarball> --upstream-vcs-tag=<exact_version_tag>
    ```

#### Upstream tag already exists

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: gbp import-orig ../gnome-control-center-46.2.tar.xz

What is the upstream version? [46.2] 
gbp:error: Upstream tag 'upstream/46.2' already exists
```

This error means that Debian already has this tarball. Merge from Debian as described in {ref}`desktop-git-merge-a-new-upstream-version-to-latest`.


## Merge a new upstream version to maintenance

When upstream releases a new version of a given project, you can merge the version on an Ubuntu maintenance branch.

If `main` has a newer version than the maintenance branch and you are the first one to deal with that case for that maintenance release, additional steps are required.

1. Check if the `debian/gbp.conf` file sets the `upstream-branch=upstream/latest` option.

1. Check if the `ubuntu/latest` branch has a newer upstream version than the one that you are importing, which was never imported.

    For example:

    - `ubuntu/latest` is on 46.2.
    - `ubuntu/noble` is on 46.1, and we want to update to 46.2.
    - The `pristine-tar` log lists that 46.1 and 46.2 have been imported.
    - Consequently, the `upstream/latest` branch has upstream commits and tags for 46.1, 46.2 and corresponding `gbp` tags `upstream/46.1` and `upstream/46.2`.

1. If the option is present and `ubuntu/latest` is newer, proceed with the next steps.

    Otherwise, follow these sections:
    
    1. {ref}`desktop-git-create-a-new-maintenance-branch`.
    1. Switch to the maintenance branch.
    1. {ref}`Merge a new upstream version <desktop-git-merge-a-new-upstream-version-to-latest>`, while on the maintenance branch.

1. Switch to the maintenance branch:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git checkout ubuntu/noble
    ```

1. Create a new `upstream/<series>` branch:

    Checkout the latest version of `upstream/latest` in your maintenance branch. In this example, it's `upstream/46.1`:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git branch upstream/46.x upstream/46.1
    ```

1. Update the `debian/gbp.conf` file to reference the correct upstream `gbp` branch:

    ```{code-block} ini
    :caption: `debian/gbp.conf`

    upstream-branch=upstream/46.x
    ```

1. Commit the changes:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git commit -a
    ```

1. Check whether Debian already has the new version in Salsa:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git tag -l | grep upstream

    […]
    upstream/46.0
    upstream/46.0.1
    upstream/46.1
    upstream/46.3
    […]
    ```

1. If the version already exists in Debian, use Debian's upstream branch tags:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git merge upstream/46.3 -m "Update upstream source from tag 'upstream/46.3'"
    ```

    Push the `upstream` and `pristine-tar` branches to Salsa:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp push origin
    ```

### Add the maintenance version in Debian

If the version doesn't exist in Debian yet, add it to Debian and Ubuntu using an upstream tarball.

1. Fetch from upstream:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git fetch upstreamvcs
    ```

1. Scan for new releases:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: uscan --verbose --no-download

    […]
    Newest version of gnome-control-center on remote site is 49.1, local version is 46.7
     => Newer package available from:
            => https://download.gnome.org/sources/gnome-control-center/49/gnome-control-center-49.1.tar.xz
    ```

1. Is `uscan` showing the upstream release that you want to import?

    If so, you can let `gbp` download and import the latest release automatically:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp import-orig --uscan
    ```

    Otherwise, download the tarball with the new upstream release manually. Then, import the tarball:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp import-orig ../gnome-control-center-46.2.tar.xz

    What is the upstream version? [46.2] 
    gbp:info: Importing '../gnome-control-center-46.2.tar.xz' to branch 'upstream/latest'...
    gbp:info: Source package is gnome-control-center
    gbp:info: Upstream version is 46.2
    gbp:info: Replacing upstream source on 'ubuntu/noble'
    gbp:info: Successfully imported version 46.2 of ../gnome-control-center-46.2.tar.xz
    ```

1. Push your changes, including the new branch that you want to track:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp push origin
    ```

1. Push the `upstream` and `pristine-tar` branches to Salsa.

    You can push directly to the GNOME branch if you have the permissions. Otherwise, push to your personal fork and prepare a merge request.

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp push origin
    ```


## Refresh patches

Before merging with an upstream release, refresh the patches.

1. Rebase the `pq` branch:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq rebase
    ```

1. Use the Git rebase tools to refresh the patches.


### Troubleshooting

The rebase might not work in certain cases, such as if you're merging with an `upstream/x.z.y` tag or if you didn't create the `patch/queue` branch first. In those cases, follow these steps:

1. Switch to the corresponding branch.

1. If the `patch-queue` branch exists, remove it:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq drop

    gbp:info: Dropped branch 'patch-queue/ubuntu/noble'.
    ```

1. Try to find the earliest point where the patches still apply. Increase the value until you find the previous release commit:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq import --force --time-machine=30

    gbp:info: 30 tries left
    gbp:info: Trying to apply patches at '10ee426e74c4643a8b723e874c71b74cfc55746d'
    gbp:info: 38 patches listed in 'debian/patches/series' imported on 'patch-queue/ubuntu/noble'
    ```

    Replace `30` with a number that determines how far in history you want to look for the patches. The exact number depends on the size of your repository. Larger numbers provide better results, but the search gets increasingly slow, so start small.

1. Re-apply the `debian/patches/series` file on top of the new upstream code, stopping for manual action if needed:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq rebase
    ```

1. If a patch doesn't apply cleanly, fix it:

    1. Resolve the conflict, and record the fix using `git add` or `git rm`.
    1. Proceed with `git rebase --continue`.

1. If the `--time-machine` step or `gbp pq rebase` fail, import the patches into the `pq` branch manually from a file:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git am -3 < debian/patches/<patch-file>
    ```

1. Regenerate the `debian/patches` data:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq export --no-patch-numbers
    ```

1. Switch back to your `ubuntu/latest` or `ubuntu/<series>` branch.

1. Commit the changes.


### See also

[Importing a new upstream version](https://honk.sigxcpu.org/projects/git-buildpackage/manual-html/gbp.patches.newupstream.html) in the `gbp` documentation.


(desktop-git-add-or-modify-patches)=
## Add or modify patches

You can turn patch files into commits on a branch. This enables you to add new patches or modify existing ones.

:::{note}
We recommend that you manage patches using the `gbp` tool on Ubuntu Desktop software, as described here. For the legacy patching workflow using the `quilt` tool, see {ref}`how-to-work-with-debian-patches`.
:::

1. Switch to the correct `ubuntu/` branch or your local `experimental-feature` branch. For example:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git checkout ubuntu/latest
    ```

1. Turn all patches from the `debian/patches/` directory into Git commits:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq rebase

    gbp:info: Switching to 'patch-queue/ubuntu/latest'
    Current branch patch-queue/ubuntu/latest is up to date.
    ```

    This command creates the `patch-queue/ubuntu/latest` branch and switches to it. This branch is based on the `ubuntu/latest` branch, and all patches referenced in the `debian/patches/series` file are applied as separate commits on top of it.

1. Check the commits:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git missing ubuntu/latest..

    * 11a3a8cc6 - (HEAD -> patch-queue/ubuntu/latest) [PATCH] night-ligth-dialog: Avoid dereferencing invalid p
    ointer (5 minutes ago)
    * da06252e1 - [PATCH 4/4] thunderbolt: move to the 'Devices' page (5 minutes ago)
    * 2c9f5bcbb - [PATCH 3/4] thunderbolt: new panel for device management (5 minutes ago)
    * 660e9e633 - [PATCH 2/4] shell: Icon name helper returns symbolic name (5 minutes ago)
    * a78ae89dd - [PATCH 1/4] shell: Don't set per-panel icon (5 minutes ago)
    […]
    ```

    This is similar to using `git log` to browse the commits, which also works.

1. Add or modify patches:

    * Modify the software. Fix a bug or add a new feature. This will be the content of your new patch.

        When you commit your changes, every new commit turns into a separate patch applied at the end of the `debian/patches/series` file. The commit description is then converted to the patch description.

        If you want to build a package with the current content without having to switch your branch, use the following command:

        ```{terminal}
        :copy:
        :host:
        :dir: gnome-control-center
        :user:
        :input: gbp buildpackage -b --git-ignore-new --git-export=INDEX
        ```

    * Reorder your patches. If you don't want this patch to be the last one, use an interactive Git rebase:

        ```{terminal}
        :copy:
        :host:
        :dir: gnome-control-center
        :user:
        :input: git rebase -i ubuntu/latest
        ```

        There, reorder the patches as commits, amend or stash them. Removing a commit also removes the patch from the `debian/patches/series` file.
    
    * Remove or edit patches. Any change to the commits results in the same change to the patch files.

        For example, you can use Git commit with the `--amend` option to modify the commit history. For details, see [Git Tools - Rewriting History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History).

1. Reapply all your changes to the original branch:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq export --no-patch-numbers

    gbp:info: On 'patch-queue/ubuntu/latest', switching to 'ubuntu/latest'
    gbp:info: Generating patches from git (ubuntu/latest..patch-queue/ubuntu/latest)
    ```

1. Update the changelog. For details, see {ref}`desktop-git-update-the-changelog`.

1. The new patches end up as unstaged changes on your branch. Commit your changes.


## Cherry-pick upstream commits

You can cherry-pick an upstream commit into a patch file.

1. Switch to the branch where you want to add the cherry-picked commit. For example, on the `ubuntu/latest` branch:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git checkout ubuntu/latest
    ```

1. Update the branch:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pull origin
    ```

1. Turn patches into commits:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq rebase || gbp pq import
    ```

1. Display the upstream Git log in the patch format. Note the hash of the commit that you want to cherry-pick:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git log -p upstream/latest
    ```

1. Cherry-pick your selected commit using its hash and edit the commit message:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git cherry-pick -x <hash>
    ```

1. Are there any conflicts?

    If there are no conflicts, edit the commit message to comply with {ref}`dep-3-patch-file-headers`. This ends up as the patch header.

    If there are conflicts:
    
    1. Fix them. For example:

        ```{terminal}
        :copy:
        :host:
        :dir: gnome-control-center
        :user:
        :input: git mergetool
        ```
        
    1. Continue with cherry-picking:

        ```{terminal}
        :copy:
        :host:
        :dir: gnome-control-center
        :user:
        :input: git cherry-pick --continue
        ```

    1. Edit the commit message to comply with {ref}`dep-3-patch-file-headers`.

1. Reapply all your changes to the original branch:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq export --no-patch-numbers
    ```

1. Update the changelog. For details, see {ref}`desktop-git-update-the-changelog`.

1. Commit the changes:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git add debian/patches/* debian/changelog

    :input: git commit
    ```

For details about `gbp pq`, see {ref}`desktop-git-add-or-modify-patches`. 


(desktop-git-update-the-changelog)=
## Update the changelog

You can edit the `debian/changelog` file manually, but it's recommended to use the following command instead:

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: gbp dch
```

By default, this command adds the first line of every commit to the changelog. You can adjust this behavior by including a string at the end of your commit message:

`Gbp-Dch: Full`
: Add this full commit message, not just the first line.

`Gbp-Dch: Ignore`
: Skip this commit in the changelog.

Alternatively, you can include all the commit descriptions:

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: gbp dch --full
```

Then, filter them out by hand at the commit phase.


## Import an Ubuntu upload tracked outside of Git

You can import a Debian Source Control (DSC) source package as a tarball, even if it doesn't exist in Git.

1. Download the source tarball.

    You can download the tarball that belongs to an Ubuntu release, like Noble:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: pull-lp-debs --download-only gnome-control-center noble

    Found gnome-control-center 1:46.7-0ubuntu0.24.04.3 in noble
    Downloading gnome-control-center_46.7-0ubuntu0.24.04.3.dsc from archive.ubuntu.com (0.004 MiB)
    ```

    Or you can download the tarball based on a package version:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: pull-lp-debs --download-only gnome-control-center 46.7-0ubuntu0
    ```

1. Switch to the branch where you want to place this Ubuntu upload.

1. Import the tarball:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp import-dsc ../gnome-control-center_46.1-0ubuntu5.dsc
    ```

1. If there had been changes in your tree, importing the latest tarball reverted all previous changes in Git.

    :::{important}
    Do not use Git rebase to restore your changes (which would rewrite history) because everyone who pulls from the repository would have conflicts upon refreshing.
    :::

    Reintroduce your changes by cherry-picking the commits. Because your commits are already in tree but reverted, you must cherry-pick using the following commands:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git show <hash> | git apply

    :input: git commit -C <hash>
    ```

1. Push the changes:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp push origin
    ```

    This pushes all needed branches, such as `ubuntu/latest`, and `pristine-tarball` + `upstream/latest` if this upload is a new upstream release.


(desktop-git-create-a-new-maintenance-branch)=
## Create a new maintenance branch

1. Find the latest version in common between the development release and that maintenance branch.

    Here, we use the `ubuntu/1%46.1-0ubuntu4` version tag as an example.

2. Create a branch from the starting point.

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git branch ubuntu/noble ubuntu/1%46.1-0ubuntu4

    :input: git checkout ubuntu/noble
    ```

3. In the `debian/gbp.conf` file, change `debian-branch` to `ubuntu/noble`:

    ```{code-block} ini
    :caption: `debian/gbp.conf`

    debian-branch = ubuntu/noble
    ```

4. In the `debian/control` file, change `Vcs-Browser` to the branch's page on `https://salsa.debian.org/<package>/tree/<branch>`. For example:

    ```{code-block} ini
    :caption: `debian/control`

    Vcs-Browser: https://salsa.debian.org/gnome-team/gnome-control-center/tree/ubuntu/noble
    ```

    :::{note}
    Certain outdated projects might still use the `debian/control.in` file. To generate `debian/control` from it, use the `dh_gnome` tool during the `clean` target in the `debian/rules` file.
    :::

5. At the end of the `Vcs-Git` value, use the `-b ubuntu/noble` option. For example:

    ```{code-block} ini
    :caption: `debian/control`

    Vcs-Git: https://salsa.debian.org/gnome-team/gnome-control-center.git -b ubuntu/noble
    ```

6. Make sure that the `XS-Debian-Vcs-Git` and `XS-Debian-Vcs-Browser` fields are set to the `Vcs-*` values but without their Ubuntu versions:

    ```{code-block} ini
    XS-Debian-Vcs-Git: https://salsa.debian.org/gnome-team/gnome-control-center.git
    XS-Debian-Vcs-Browser: https://salsa.debian.org/gnome-team/gnome-control-center
    ```

7. Commit the changes:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git commit -a
    ```

8. Push your changes to Salsa:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp push origin

    Total 0 (delta 0), reused 0 (delta 0)
    To git+ssh://git@salsa.debian.org:gnome-team/gnome-control-center
     * [new branch]          ubuntu/noble -> ubuntu/noble
    Branch 'ubuntu/noble' set up to track remote branch 'ubuntu/noble' from 'origin'.
    ```


## Build a package locally

To build a local package, we use the {ref}`sbuild framework <sbuild>` and specify the target Ubuntu release. We don't recommend building the package directly on your system without using `sbuild` because the test and build phase might be affected by the state of your machine.

* Build a binary package for your Ubuntu release and CPU architecture. For example, Ubuntu Noble on the AMD64 architecture:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp buildpackage -b --git-builder=sbuild noble-amd64
    ```

* Build a source package: 

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp buildpackage -b --git-builder=sbuild noble-amd64 -S
    ```

With the proposed configuration, the artifacts all end up in the `../build-area` directory, including the tarball, which is reconstructed from the `pristine-tar` + `upstream/latest` branch. The build directory is then cleaned up.

Useful tips in some potential cases:

* Don't purge the `build-area` directory after building:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp buildpackage --git-no-purge
    ```

* Build current branch with local uncommitted modifications:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp buildpackage --git-ignore-new --git-export=INDEX
    ```

* When merging with Debian, releasing an SRU or uploading a version on top of one that is still in the proposed pocket, include both the Ubuntu and Debian part of the changelog in the `.changes` file, which is generated by `dpkg-genchanges`. Including all changelog entries ensures that bugs are automatically closed.

    Add the `-vX` option to include all Debian and Ubuntu versions greater than `X`, which is the current version in `main`, `security` or `updates` repositories:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp buildpackage -S -vX
    ```

    For example, see the [`gnome-control-center_49.0-1ubuntu2_source.changes`](https://launchpadlibrarian.net/820313141/gnome-control-center_49.0-1ubuntu2_source.changes) generated file.


## Release a new version

:::{note}
If this is a sponsored upload, the sponsor performs these steps.
:::

1. Generate the changelog for native packages. For details, see {ref}`desktop-git-update-the-changelog`.

1. You might need to manually edit the `debian/changelog` file to improve its syntax and clarity.

1. Finalize the changelog and specify the Ubuntu release:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: dch -r "" --distribution noble

    :input: git commit -m "Upload to Noble" debian/changelog
    ```

1. Tag the package:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp buildpackage --git-tag-only --git-ignore-new
    ```

1. Build the source package:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp buildpackage -S
    ```

    If this version hasn't arrived in the `main` repository yet, include both the Ubuntu and Debian part of the changelog in the `.changes` file, which is generated by `dpkg-genchanges`. Add the `-vX` option to include all Debian and Ubuntu versions greater than `X`, where `X` is the current version in `main`, `security` or `updates` repositories:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp buildpackage -S -vX
    ```

    For example, consider the following scenario:
    
    * The `main` pocket contains version `3.1.0-1ubuntu1`.
    * The `proposed` pocket contains `3.1.0-1ubuntu2`.
    * You're uploading version `3.1.0-2ubuntu1`.
    
    In this case, use the `-v3.1.0-1ubuntu1` option so that the changes in `3.1.0-1ubuntu2` are also listed in the change files.

1. Check the `../build-area/<your-package>.changes` file to make sure that it's correct. This file instructs `dput` which files to upload and provides a high-level view of the changes, such as the latest changelog entries.

    For example, changes to the GNU Hello program as packaged for Ubuntu would be described in the `hello_2.10-0ubuntu1.changes` file.

1. Upload the files to the Ubuntu package upload queue:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: dput ../build-area/<your-package>.changes
    ```

1. Push the changes to Salsa:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp push origin
    ```

    This pushes all tracked branches to Salsa if you made any changes. The branches include:

    * `ubuntu/latest`
    * `ubuntu/old-series`
    * `pristine-tar`
    * `upstream/lastest`

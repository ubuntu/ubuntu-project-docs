---
relatedlinks: "[PackagingWithGit &#32; - &#32; Debian Wiki](https://wiki.debian.org/PackagingWithGit)"
---

(maintain-ubuntu-desktop-software)=
# Maintain Ubuntu Desktop software

These are some common, day-to-day operations to build, maintain and package GNOME software for Ubuntu Desktop using the Git Build Package (`gbp`) workflow.

We'll use the `gnome-control-center` repository as an example.

:::{note}
Some applications on Ubuntu Desktop are developed outside of Salsa and GNOME. They have their own, separate workflows, which aren't described in this guide. The Desktop Team can help you find the right instructions on Matrix: [#desktop-dev:ubuntu.com](https://app.element.io/#/room/#desktop-dev:ubuntu.com).
:::


## Prerequisites

Before you start, follow the instructions in {ref}`set-up-git-for-ubuntu-desktop-work`.


## Team members, contributors and permissions

If you're a community contributor and not a member of the Ubuntu Desktop Team, you have to send your contributions through a merge request:

1. Fork the Git repository on Salsa.
1. Follow this guide and make the changes in your fork.
1. Open a Salsa merge request from your fork to the original repository.

In some projects, no Ubuntu branch has been created in a long time. You might have to ask the Debcrafters team to create the new branch for you. You can contact them [on Matrix](https://app.element.io/#/room/#devel:ubuntu.com) or [on the Canonical Mattermost](https://chat.canonical.com/canonical/channels/debcrafters).


## Local changes

With the suggested Git configuration, any non-committed changes (file modifications, additions or removal) halt the build because they won't be included. This is a safety reminder.

What you can do when you have such changes:

* Ignore them. The resulting package and build won't include those uncommitted changes. The `../build-area/<your-package>` directory will match the last commit.

    To do this, add the `--git-ignore-new` Git option

* Force using the current directory with your local modifications instead of the `build-area` directory, and include any local modifications to the package despite the `ignore-new` option.

    For this, use the `--git-ignore-new --git-export-dir=""` Git options.

* Remove the local changes:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: dh_clean
    ```
    
    If that command doesn't work for you package, you can reset the changes in the following way:
    
    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git checkout .

    :input: git clean -fd .
    :input: quilt -f pop -a
    ```


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

* If you have a separate `ubuntu/noble` branch, with its own `upstream/46.x` branch:

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

The `gbp pull` command, contrary to `git pull`, is a way to avoid checking out each branch and pulling them one by one. With `git pull`, you need to have the branch as the current checkout for potential conflicts when pulling.


## Push your Git changes to Salsa

To contribute changes back to Salsa, push your changes using Git. For example:

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: git push
```


(desktop-git-merge-a-new-upstream-version-to-latest)=
## Merge a new upstream version to latest

When upstream releases a new version of a given project, you can merge the version on the `ubuntu/latest` branch.

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

    * If you already have the `patch/queue` branch, just rebase it:

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

1. If Debian has already this upstream version, you don't have to import the actual tarball. You just merge with the latest upstream code:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git merge upstream/46.2 -m "Update upstream source from tag 'upstream/46.2'"
    ```

    The new upstream version is now merged.

1. Only if Debian doesn't have the new version, proceed with the next steps.

    Since we don't want to have duplicated `upstream/x.y.z` tags, in this case you should push the `pristine-tar` and `upstream/<current>` branches to `origin`.

1. Download the tarball with the new upstream release.

1. Import the tarball:

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

    You can also use `--uscan` to let it download and import.

1. Push all needed branches (for example, `ubuntu/latest` and `pristine-tarball` + `upstream/46.x` or `upstream/latest` if this upload is a new upstream release):

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git push
    ```

1. Sync the affected upstream branch to Salsa, or propose it if you aren't an Ubuntu developer. Make sure to push the new tag, too.

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

* Upstream has changed the tagging pattern. Update the `debian/gbp.conf` file to match it.

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

This error means that Debian already has this tarball. Merge from Debian as described earlier.


## Merge a new upstream version to maintenance

When upstream releases a new version of a given project, you can merge the version on an Ubuntu maintenance branch.

If `main` has a newer version than the maintenance branch and you are the first one to deal with that case for that maintenance release, additional steps are required.

1. Open the `debian/gbp.conf` file.

    Check if it sets the `upstream-branch=upstream/latest` option.

1. Check if the `ubuntu/latest` branch has a newer upstream version than the one that you are importing, which was never imported.

    For example:

    - `ubuntu/latest` is on 46.2
    - `ubuntu/noble` is on 46.1 and we want to update to 46.2
    - We have `pristine-tar` having 46.1 and 46.2 imported
    - Consequently, the `upstream/latest` branch has upstream commits and tags for 46.1, 46.2 and corresponding `gbp` tags `upstream/46.1` and `upstream/46.2`.

1. If the option is present and `ubuntu/latest` is newer, proceed with the next steps.

    Otherwise, just follow these existing sections:
    
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

1. Create a new `upstream/<series>` branch.

    You need to checkout the latest version of `upstream/latest` in your maintenance branch. In this example, it's `upstream/46.1`:

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

1. Does Debian already have the new version in Salsa?

    * If it does, use Debian's upstream branch tags:

        ```{terminal}
        :copy:
        :host:
        :dir: gnome-control-center
        :user:
        :input: git merge upstream/46.2 -m "Update upstream source from tag 'upstream/46.2'"
        ```

    * If it doesn't, use an upstream tarball:

        1. Fetch from upstream:

            ```{terminal}
            :copy:
            :host:
            :dir: gnome-control-center
            :user:
            :input: git fetch upstreamvcs
            ```

        1. Download the upstream tarball.

        1. Import the tarball:

            ```{terminal}
            :copy:
            :host:
            :dir: gnome-control-center
            :user:
            :input: gbp import-orig ../gnome-control-center-46.2.tar.xz
            ```

        1. Push your changes, including the new branch that you want to track:

            ```{terminal}
            :copy:
            :host:
            :dir: gnome-control-center
            :user:
            :input: git push

            :input: git push -u upstream/46.x
            ```

1. Push the `upstream` and `pristine-tar` branches to Salsa.

    You can push directly to the `gnome` branch if you have the permissions. Otherwise, push to your personal fork and prepare a merge request.

    :::{admonition} TODO
    :class: attention
    What does this mean specifically? What are the commands?
    :::


## Refresh patches

When merging with an upstream release, you might need to refresh the patches.

:::{admonition} TODO
:class: attention
How can you tell that you need to refresh?
:::

If your `patch/queue` branch is in sync with the previous release, you can just rebase:

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: gbp pq rebase
```

Then you can use the Git rebase tools to refresh the patches.

For the case of using `gbp import-orig`, this is better described in the [`gbp` documentation](https://honk.sigxcpu.org/projects/git-buildpackage/manual-html/gbp.patches.newupstream.html).

This might not work if you're instead merging with an `upstream/x.z.y` tag or if you didn't create the `patch/queue` branch first.

The following steps work in both cases:

1. Switch to the corresponding branch.

1. If the `patch-queue` branch exists, remove it:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq drop
    ```

1. Try to find the first point where the patches merge. Increase the value until you don't find the previous release commit:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq import --force --time-machine=30
    ```

    :::{admonition} TODO
    :class: attention
    How much should you increase the value and how can you tell that you should stop?
    :::

1. Re-apply the `debian/patches/series` file on top of the new upstream code, stopping for manual action if is needed:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq rebase
    ```

1. If a patch doesn't apply cleanly, fix it:

    1. Resolve the conflict using `git add` and `git rm`.
    1. Proceed with `git rebase --continue`.

1. Regenerate the `debian/patches` data, ready to be committed, and switch back to your `ubuntu/` branch:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq export --no-patch-numbers
    ```

    :::{admonition} TODO
    :class: attention
    Does this command both regenerate the data and switch to the branch, or are other commands needed?
    :::

1. Once back on the `ubuntu/latest` or `ubuntu/<series>` branch, you need to commit the changes, too.

    :::{admonition} TODO
    :class: attention
    Commands? Just a regular `git add && git commit`?
    :::


(desktop-git-add-or-modify-patches)=
## Add or modify patches

You can turn patch files into commits on a branch. This enables you to add new patches or modify existing ones.

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

        When you commit your changes, every new commit turns into a separate patch applied at the end of the `debian/patches/series` file. The commit description will be then converted to the patch description.

        If you want to build a package with the current content without having to switch your branch, use the following command:

        ```{terminal}
        :copy:
        :host:
        :dir: gnome-control-center
        :user:
        :input: gbp buildpackage --git-ignore-new --git-export-dir=""
        ```

    * Reorder your patches. If you don't want this patch to be the last one, you can use an interactive Git rebase:

        ```{terminal}
        :copy:
        :host:
        :dir: gnome-control-center
        :user:
        :input: git rebase -i ubuntu/latest
        ```

        There, you can reorder the patches as commits, amend or stash them. Removing a commit also removes the patch from the `debian/patches/series` file.
    
    * Remove or edit patches. Any change to the commits will result in the same change to the patch files.

        For example, you can use Git amend to modify the commit history. For details, see [Git Tools - Rewriting History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History).

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

:::{note}
The `gbp pq` command unfuzzes a lot of patches every time you use it, creating some noise. Add those changes separated from your new or modified patch hack.

And either push the change to your branch or to the main branches with a simple git push!
:::

:::{admonition} TODO
:class: attention
I don't know what this note is trying to say.
:::

### Additional resources

For a different patching workflow using the `quilt` tool, see {ref}`how-to-work-with-debian-patches`.


## Cherry-pick upstream commits

1. Refresh the upstream repository.

    We don't have a local checkout, only a remote that we need to refresh:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git fetch upstreamvcs
    ```

1. Find the commits that you want to cherry-pick. Browse the Git history. 

    For example, look at the Git log of the `main` branch:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git log -p upstreamvcs/main
    ```

    Many GNOME projects now use `main` instead of `master`. If your project is still using `master`, adjust the branch:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git log -p upstreamvcs/master
    ```

1. Cherry-pick a commit as a patch. For example, on the `ubuntu/latest` branch:

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
    :input: git pull
    ```

1. Turn patches into commits:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq rebase
    ```

    :::{note}
    Instead, you can also use the following commands. This deletes your patch queue and re-creates it from `debian/patches`, which can be useful if the `patch-queue` branch gets out of sync with `latest`:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp pq drop

    :input: gbp pq import
    ```
    :::

1. Display the upstream Git log in the patch format:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git log -p upstream/latest
    ```

    :::{admonition} TODO
    :class: attention
    What is this for? It seems to just display the log without affecting your repository in any way.
    :::

1. Cherry-pick your selected commit using its hash and edit the commit message:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git cherry-pick -e -x <hash>
    ```

1. Are there any conflicts?

    If there are no conflicts, edit the commit message to comply with {ref}`dep-3-patch-file-headers`. This will end up as the patch header.

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

You can edit the `debian/changelog` file manually but it's recommended to use the following command instead:

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


## Import an Ubuntu upload tracked outside of VCS

You can import a Debian Source Control (DSC) source package as a tarball, even if it doesn't exist in the Git version tracking system (VCS).

:::{admonition} TODO
:class: attention
This procedure really needs a review. I rearranged the steps but I'm not sure if they still work.
:::

1. Downloading the source tarball.

1. Switch to the branch where you want to place this Ubuntu upload.

1. Import the tarball:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp import-dsc ../gnome-control-center_46.1-0ubuntu5.dsc
    ```

1. If there had been changes in your tree, importing the latest tarball reverted all previous changes in the VCS.

    To restore your changes, you could rewrite the history using a Git rebase. However, everyone who pulls from the repository would have conflicts upon refreshing. This is discouraged.

    Instead, reintroduce your changes by cherry-picking the commits. Because your commits are already in tree but reverted, you must cherry-pick using the following commands:

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
    :input: git push
    ```

    This pushes all needed branches, such as `ubuntu/latest`, and `pristine-tarball` + `upstream/latest` if this upload is a new upstream release.


(desktop-git-create-a-new-maintenance-branch)=
## Create a new maintenance branch

1. Find the latest version in common between the development release and that maintenance branch.

    Here, we'll use the `ubuntu/1%46.1-0ubuntu4` version tag as an example.

2. Create a branch from the start starting point.

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

8. Push your changes to Salsa and track that branch:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git push -u origin ubuntu/noble

    Total 0 (delta 0), reused 0 (delta 0)
    To git+ssh://git@salsa.debian.org:gnome-team/gnome-control-center
     * [new branch]          ubuntu/noble -> ubuntu/noble
    Branch 'ubuntu/noble' set up to track remote branch 'ubuntu/noble' from 'origin'.
    ```


## Build a package locally

* Build a binary package: 

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp buildpackage
    ```

* Build a source package: 

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp buildpackage -S
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
    :input: gbp buildpackage --git-ignore-new --git-export-dir="" 
    ```

* When merging with Debian, include both the Ubuntu and Debian part of the changelog in the `.changes` file, which is generated by `dpkg-genchanges`.

    Add the `-vX` option to include all Debian and Ubuntu versions greater than `X`:

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

1. You might need to manually edit the `debian/changelog` file to properly group changes per people.

1. Finalize the changelog. On the corresponding branch:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: dch -r ""

    :input: git commit debian/changelog -m "Finalize changelog"
    ```

1. Build the binary and source package:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: gbp buildpackage --git-tag-only
    
    :input: gbp buildpackage -S
    ```

1. Upload the files to the Debian package upload queue:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: dput ../build-area/….changes
    ```

    :::{admonition} TODO
    :class: attention
    What's `../build-area/….changes`? Looks like a rendering artifact.
    :::

1. Push the changes to Salsa:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git push
    ```

1. Push the tags that we care about to Salsa:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git tag | grep -E '^ubuntu/|^debian/|^upstream/' | xargs -r git push
    ```

    This pushes all tracked branches to Salsa if you made any changes. The branches include:

    * `ubuntu/latest`
    * `ubuntu/old-series`
    * `pristine-tar`
    * `upstream/lastest`

---
relatedlinks: "[PackagingWithGit &#32; - &#32; Debian Wiki](https://wiki.debian.org/PackagingWithGit)"
---

(set-up-git-for-ubuntu-desktop-work)=
# Set up Git for Ubuntu Desktop work

The [Desktop Team](https://library.canonical.com/our-organisation/ubuntu-engineering/desktop) uses Git and Git Build Package (`gbp`) to maintain GNOME packages for Ubuntu. Let's set up your system so that you can contribute to GNOME on Ubuntu Desktop.

We'll use the Settings application as an example. Internally, the application is known as the GNOME Control Center.


## Initial setup

1. Install the basic packages for working in Git:

    ```{terminal}
    :copy:
    :host:
    :dir:
    :user:
    :input: sudo apt install git git-buildpackage
    ```

2. Install Ubuntu packaging tools:

    ```{terminal}
    :copy:
    :host:
    :dir:
    :user:
    :input: sudo apt install gnupg pbuilder ubuntu-dev-tools apt-file
    ```

    For details about the packaging environment, see [Getting Set Up](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/1.0/tutorial/getting-set-up.html) in the Ubuntu Packaging Guide.

3. In the Software & Updates application, enable {guilabel}`Source code` on the {guilabel}`Ubuntu Software` tab.

    This provides information about the source repository of every package so that you can easily clone it.

4. Enable the `salsa:name-or-team/repo` and `salsa-gnome:repo` short format for Salsa Git repositories.

    Add the following configuration to your `~/.config/git/config` file:

    ```{code-block} ini
    :caption: `~/.config/git/config`

    [url "git@salsa.debian.org:"]
        insteadof = salsa:

    [url "git@salsa.debian.org:gnome-team/"]
        insteadof = salsa-gnome:
    ```

5. Some projects might require that you sign tags with your GPG key. Enable automatic signing.

    Display your public GPG key:

    ```{terminal}
    :copy:
    :host:
    :dir:
    :user:
    :input: gpg --list-secret-keys --fingerprint

    /home/user/.gnupg/pubring.kbx
    -----------------------------------------------------
    sec   rsa2048 YYYY-MM-DD [SC]
        XXXX XXXX XXXX XXXX XXXX  XXXX XXXX XXXX D1B7 6B89
    uid           [ unknown] Key Name <my@email.com>
    ssb   rsa2048 YYYY-MM-DDD [E]
    ```

    Your short GPG key ID is the last eight digits of your public GPG key, or `D1B76B89` in this example.

    Add the following configuration to your `~/.gbp.conf` file:

    ```{code-block} ini
    :caption: `~/.gbp.conf`

    [buildpackage]
    sign-tags = True
    keyid = 0xGPGKEYID
    ```

    Replace `GPGKEYID` with your short GPG key ID.


## Optional configuration

The following configuration can simplify certain tasks on Ubuntu Desktop projects.

Enable Git command aliases:

```{code-block} ini
:caption: `~/.config/git/config`

[alias]
    matching-tags = "!f() { git for-each-ref --sort=creatordate --format '%(refname)' refs/tags| grep \"$1\"| sed s,^refs/tags/,,; }; f"
    last-tags = matching-tags '.*'
    last-match-tag = "!f() { git matching-tags $1 | tail -n1; }; f"
    last-tag = last-match-tag '.*'
    last-debian-tag = last-match-tag debian/
    last-ubuntu-tag = last-match-tag ubuntu/
    ubuntu-delta = "!f() { git diff $(git last-debian-tag) -- ${1:-debian} ':(exclude)debian/changelog'; }; f"
```

Export the `../build-area/` directory before building with the `git-buildpackage` tool:

```{code-block} ini
:caption: `~/.gbp.conf`

[buildpackage]
export-dir = ../build-area/
```

For details, see the `gbp.conf(5)` and `gbp-buildpackage` man pages.


## Required accounts

1. If you don't have accounts on the following GitLab instances, create them:

    * [GNOME GitLab](https://gitlab.gnome.org/) is the upstream GNOME repository.
    * [Salsa](https://salsa.debian.org/) hosts the Debian and Ubuntu packaging and modifications.

    It might take a while for your account to be approved.

2. In your account preferences, upload your SSH public key to be able to interact with the Git repositories.


## Clone a repository

Let's clone the GNOME Control Center repository. 

1. Check if the package provides information about its source repository:

    ```{terminal}
    :copy:
    :host:
    :dir:
    :user:
    :input: apt-cache showsrc gnome-control-center | grep Vcs

    Vcs-Browser: https://salsa.debian.org/gnome-team/gnome-control-center/tree/ubuntu/master
    Vcs-Git: https://salsa.debian.org/gnome-team/gnome-control-center.git -b ubuntu/master
    Debian-Vcs-Browser: https://salsa.debian.org/gnome-team/gnome-control-center
    Debian-Vcs-Git: https://salsa.debian.org/gnome-team/gnome-control-center.git
    ```

    A link to a Git repository is attached to this package. We can clone it using the `debcheckout` tool.

2. Clone the repository from the Salsa remote:

    ```{terminal}
    :copy:
    :host:
    :dir:
    :user:
    :input: debcheckout --git-track=* gnome-control-center

    declared git repository at https://salsa.debian.org/gnome-team/gnome-control-center/
    git clone https://salsa.debian.org/gnome-team/gnome-control-center -b ubuntu/latest gnome-control-center ...
    […]
    ```

    If the `Vcs-Git` field was missing or incorrect, you could clone the repository manually using `gbp`:

    ```{terminal}
    :copy:
    :host:
    :dir:
    :user:
    :input: gbp clone salsa-gnome:gnome-control-center

    gbp:info: Cloning from 'salsa-gnome:gnome-control-center'
    ```


## Configure branches

1. Switch to the cloned repository:

    ```{terminal}
    :copy:
    :host:
    :dir:
    :user:
    :input: cd gnome-control-center
    ```

1. Enable Git to push tags automatically because `gbp` relies on them.

    Apply this as local configuration in the cloned repository:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git config push.followTags true
    ```

1. Add the upstream GNOME remote repository and call it `upstreamvcs`:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git remote add -f upstreamvcs git@ssh.gitlab.gnome.org:GNOME/gnome-control-center.git
    ```

1. Check that you now have the following three branches:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git branch -vv

      pristine-tar             a96c0e2e98 [origin/pristine-tar] pristine-tar data for gnome-control-center_49.0.orig.tar.xz
    * ubuntu/latest            a8640ab8a4 [origin/ubuntu/latest] debian/salsa-ci: Enable for ubuntu
      upstream/latest          4db8b3a502 [origin/upstream/latest] New upstream version 49.0
    ```

1. Check that you have the following two remotes:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git remote

    origin
    upstreamvcs
    ```


## Examine the branches and repositories

We use a layout with two remote repositories. Let's take a look.

Run these commands in the `gnome-control-center` repository that we cloned earlier.

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: git remote show
```

The command lists the following remote repositories:

`origin`
: Points to the Salsa repository. The default for pull and push without any argument.

`upstreamvcs`
: Points to the upstream GNOME repository, to easily cherry-pick upstream fixes.

    This remote is called `upstreamvcs` to not be confused with local branch names, which might be called `debian/branchname` or `upstream/branchname`. Instead of having a local `debian/latest` branch tracking the `debian/debian/latest` remote, we have the `debian/latest` local branch tracking the `origin/debian/latest` remote, which is easier to understand.

:::{note}
The `debian/latest` and `ubuntu/latest` branches were previously called `debian/master` and `ubuntu/master`, respectively. We renamed them on 4 September 2023 to use more inclusive naming and more closely follow [DEP-14](https://dep-team.pages.debian.net/deps/dep14/).
:::

These names of remote repositories are local to your system. You can rename them without affecting the content of the remote repositories.

### Salsa remote branches

Let's look at the various branches in the Salsa remote repository:

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: git remote show origin

* remote origin
  […]
  HEAD branch: debian/latest
  Remote branches:
    pristine-tar             tracked
    ubuntu/latest            tracked
    upstream/latest          tracked
  […]
```

`ubuntu/latest`, sometimes `ubuntu/main` or `ubuntu/master`
: This branch is the content of the latest Ubuntu development release. Work ready to be uploaded or uploaded in a development release mostly happens here. It's the default branch.

`pristine-tar`
: This branch is an internal `gbp-buildpackage` branch, used to reconstruct release tarballs using `upstream/latest`. You don't interact with it directly.

`upstream/latest`
: This is another internal `gbp-buildpackage` branch. It's a merge between the upstream Git branch corresponding to the latest release from the upstream repository and extra content coming from the tarball. You don't interact with it directly.

We find back those 3 branches locally:

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: git branch
```

`ubuntu/latest`
: Pull and push from the `origin` (Salsa) remote repository, tracking the `ubuntu/latest` remote branch (`origin/ubuntu/latest`).

`pristine-tar`
: Pull and push from the `origin` (Salsa) remote repository, tracking the `pristine-tar` remote branch (`origin/pristine-tar`).

`upstream/latest`
: Pull from the `upstream` remote repository, tracking the `latest` remote branch (`upstream/latest`), and push to the `origin` (Salsa) remote repository, tracking the `upstream/latest` remote branch (`origin/upstream/latest`).

In this configuration, you only interact with the `ubuntu/latest` branch and let `gbp` handle the other two branches. When you pull and push using `gbp`, it keeps all three branches up to date if no conflict occurs. This is easier than checking out every branch before pushing them.

### Maintenance branches

Many release maintenance branches are available on the Salsa remote repository:

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: git remote show origin

* remote origin
  […]
  Remote branches:
    […]
    pristine-tar             tracked
    ubuntu/noble             tracked
    ubuntu/latest            tracked
    upstream/latest          tracked
    upstream/46.x            tracked
    […]
```

`ubuntu/noble`
: This branch contains the version of the project for the given Ubuntu release. In this example, the branch contains GNOME Control Center 46 for Ubuntu Noble. When a new release comes out of development, its `ubuntu/latest` branch becomes a maintenance branch.

`upstream/46.x`
: This is a maintenance branch tracking a particular upstream GNOME series, similar to the `ubuntu/noble` branch. It's derived from the `upstream/latest` branch when a new upstream release comes out.

    This branch is only necessary if you imported a new tarball (like the 46 series) in `upstream/latest` and you want to release a yet unimported 46.3 upstream release in Noble, for instance.

    This branch is automatically managed by `gbp buildpackage`.

Each remote branch should have a corresponding local branch when working on Noble.

Let's track the `ubuntu/noble` maintenance branch:

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: git checkout ubuntu/noble

Switched to branch 'ubuntu/noble'
Your branch is up to date with 'origin/ubuntu/noble'.
```

:::{note}
This short syntax is only available because we created a local `ubuntu/noble` branch that tracks the matching `ubuntu/noble` branch on the `origin` repository.

To create another local branch that tracks a remote branch, use the following commands:

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: git branch -u <local-branch-name> <remote>/<branch-name>

:input: git checkout <local-branch-name>
```
:::


### Debian remote branches

In addition, we have at least one other branch tracking the Salsa Debian remote repository. Their main (default) branch is called `debian/latest`:

`debian/latest`
: Pull from the `origin` remote repository, tracking the `debian/latest` remote branch. You can only push if you're are a Debian developer.

### Upstream GNOME remote branches

By default, we don't have upstream GNOME branches checked out locally. We added the `upstreamvcs` repository and have access to its content, which will be fetched when importing a new upstream tarball thanks to the version tag, and inject the history in `upstream/latest` (or `upstream/version`, as explained before).

:::{admonition} TODO
:class: attention
That's a long sentence. Who fetches the content? Who injects the history? What does it mean to inject history in Git?
:::

Let's browse the content of the `upstreamvcs` repository:

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: git remote show upstreamvcs

* remote upstreamvcs
[…]
  HEAD branch: main
  Remote branches:
[…]
    gnome-49                                  tracked
[…]
```

You can check out any of those branch locally. We have the local `upstream/latest` branch tracking the `main` branch of the `upstreamvcs` repository. We can track any additional branches as needed for cherry-picking fixes.

:::{admonition} TODO
:class: attention
That's not true though. `upstream/latest` is tracking `origin/upstream/latest` in my testing.
:::

Let's check out the `upstreamvcs/main` branch locally and call it `upstreamvcs-main`:

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: git checkout -b upstreamvcs-main upstreamvcs/main

Branch 'upstreamvcs-main' set up to track remote branch 'main' from 'upstreamvcs'.
Switched to a new branch 'upstreamvcs-main'
```

### Summary

To sum up all this, our minimal setup consists of the following local branches. Their remote tracking branches are in square brackets (`[]`):

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: git branch -vv

  debian/latest            1f06aced56 [origin/debian/latest] debian/salsa-ci: Enable for debian
  upstreamvcs-main         b3b4035c07 [upstreamvcs/main] Update Brazilian Portuguese translation
  pristine-tar             a96c0e2e98 [origin/pristine-tar] pristine-tar data for gnome-control-center_49.0.orig.tar.xz
* ubuntu/latest            a8640ab8a4 [origin/ubuntu/latest] debian/salsa-ci: Enable for ubuntu
  upstream/latest          4db8b3a502 [origin/upstream/latest] New upstream version 49.0
```

In addition, we can have several other branches:

* An Ubuntu maintenance branch, such as for Ubuntu Noble
* A `gbp buildpackage` tarball branch linked to the maintenance release, such as for GNOME 46
* An upstream `main` branch checked out as a local branch

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: git branch -vv
  ubuntu/noble             10ee426e74 [origin/ubuntu/noble] Upload to noble
  upstream/46.x            f5817b6dce [origin/upstream/46.x] New upstream version 46.7
  upstreamvcs-main         b3b4035c07 [upstreamvcs/main] Update Brazilian Portuguese translation
```


## Next steps

Now that your Git setup is complete, you can contribute to Ubuntu Desktop software. You can build, modify, maintain and package applications. See {ref}`maintain-ubuntu-desktop-software`.


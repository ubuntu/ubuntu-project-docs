---
relatedlinks: "[PackagingWithGit &#32; - &#32; Debian Wiki](https://wiki.debian.org/PackagingWithGit)"
---

(set-up-git-for-ubuntu-desktop-work)=
# Set up Git for Ubuntu Desktop work

The [Desktop Team](https://discourse.ubuntu.com/c/project/desktop/8) uses Git and Git Build Package (`gbp`) to maintain GNOME packages for Ubuntu. Let's set up your system so that you can contribute to GNOME on Ubuntu Desktop.

We use the Settings application as an example. Internally, the application is known as the GNOME Control Center.


## Initial setup

1. Install the basic packages for working in Git and Ubuntu packaging:

    ```{terminal}
    :copy:
    :host:
    :dir:
    :user:
    :input: sudo apt install git git-extras git-buildpackage ubuntu-dev-tools gnupg
    ```

    For details about the packaging environment, see {ref}`how-to-set-up-for-ubuntu-development`.

1. Install and configure the `sbuild` tool. Follow {ref}`sbuild`. Set the Ubuntu releases for which you're preparing packages.

1. In the Software & Updates application, enable {guilabel}`Source code` on the {guilabel}`Ubuntu Software` tab.

    This provides information about the source repository of every package so that you can easily clone it.

1. Enable short formats for Git repositories: `salsa:name-or-team/repo` and `salsa-gnome:repo` for Salsa, `fdo:repo` for freedesktop\.org:

    Add the following configuration to your `~/.config/git/config` file:

    ```{code-block} ini
    :caption: `~/.config/git/config`

    [url "git@salsa.debian.org:"]
        insteadof = salsa:

    [url "git@salsa.debian.org:gnome-team/"]
        insteadof = salsa-gnome:
    
    [url "https://gitlab.freedesktop.org/"]
        insteadof = fdo:
    ```


## Sign your commits

Some projects might require that you sign tags with your GPG key. Enable automatic signing.

1. Create your GPG key as described in {ref}`gnupg`.

1. Display your public GPG key:

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

1. Add the following configuration to your `~/.gbp.conf` file:

    ```{code-block} ini
    :caption: `~/.gbp.conf`

    [buildpackage]
    sign-tags = True
    keyid = 0xGPGKEYID
    ```

    Replace `GPGKEYID` with your short GPG key ID.


## Required accounts

1. If you don't have accounts on the following GitLab instances, create them:

    * [GNOME GitLab](https://gitlab.gnome.org/) is the upstream GNOME repository.
    * [freedesktop\.org GitLab](https://gitlab.freedesktop.org/) hosts other desktop projects such as PipeWire.
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
    :input: apt-cache showsrc gnome-control-center | grep-dctrl -n -s Vcs-Git -

    https://salsa.debian.org/gnome-team/gnome-control-center.git -b ubuntu/master
    ```

    A link to a Git repository is attached to this package.

2. Clone the repository from the Salsa remote:

    ```{terminal}
    :copy:
    :host:
    :dir:
    :user:
    :input: gbp clone salsa-gnome:gnome-control-center

    gbp:info: Cloning from 'salsa-gnome:gnome-control-center'
    ```

    You can also use the repository link found earlier:

    ```{terminal}
    :copy:
    :host:
    :dir:
    :user:
    :input: gbp clone https://salsa.debian.org/gnome-team/gnome-control-center.git

    gbp:info: Cloning from 'https://salsa.debian.org/gnome-team/gnome-control-center.git'
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

    :::{note}
    If you don't have an account on the GNOME GitLab or if your account is missing an SSH key, you can also refer to the repository using the HTTPS protocol:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git remote add -f upstreamvcs https://gitlab.gnome.org/GNOME/gnome-control-center.git
    ```
    :::

1. Check that you now have the following three branches:

    ```{terminal}
    :copy:
    :host:
    :dir: gnome-control-center
    :user:
    :input: git branch -vv

      pristine-tar      a96c0e2e98 [origin/pristine-tar] pristine-tar data for gnome-control-center_49.0.orig.tar.xz
    * ubuntu/latest     a8640ab8a4 [origin/ubuntu/latest] debian/salsa-ci: Enable for ubuntu
      upstream/latest   4db8b3a502 [origin/upstream/latest] New upstream version 49.0
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
:input: git remote -v
```

The command lists the following remote repositories:

`origin`
: Points to the Salsa repository. The default for pull and push without any argument.

`upstreamvcs`
: Points to the upstream GNOME repository, to easily cherry-pick upstream fixes.

    This remote is called `upstreamvcs` to not be confused with local branch names, which might be called `debian/<branch-name>` or `upstream/<branch-name>`. Instead of having a local `debian/latest` branch tracking the `debian/debian/latest` remote, we have the `debian/latest` local branch tracking the `origin/debian/latest` remote, which is easier to understand.

:::{note}
The `debian/latest` and `ubuntu/latest` branches were previously called `debian/master` and `ubuntu/master`, respectively. We renamed them on 4 September 2023 to use more inclusive naming and more closely follow [DEP-14](https://dep-team.pages.debian.net/deps/dep14/).
:::



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
: This branch is an internal `gbp-buildpackage` branch, used to reconstruct release tarballs using `upstream/latest`. Usually, you don't interact with it directly. When you do need to interact with it, such as to manage the tarballs, use the `pristine-tar` tool.

`upstream/latest`
: This is another internal `gbp-buildpackage` branch. It's a merge between the upstream Git branch corresponding to the latest release from the upstream repository and extra content coming from the tarball. You don't interact with it directly.

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
: This is a maintenance branch tracking a particular upstream GNOME series, similar to the `ubuntu/noble` branch. It's derived from the `upstream/latest` branch when a new upstream release series, such as GNOME 46, comes out.

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
: Pull from the `origin` remote repository, tracking the `debian/latest` remote branch. To push to this branch, you must be a [Debian Developer](https://wiki.debian.org/DebianDeveloper).



### Upstream GNOME remote branches

By default, we don't have upstream GNOME branches checked out locally. We added the `upstreamvcs` repository and have access to its content.

:::{note}
Later, we'll import a new upstream tarball, representing a new release of the `gnome-control-center` project. The `gbp` tool will fetch the content of `upstreamvcs` thanks to the version tag.
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

The branches within `origin/upstream` on Salsa, such as the `origin/upstream/latest` branch, tag unmodified releases from the GNOME `upstreamvcs` remote, without the Debian packaging and changes. As a result, the local `upstream/latest` branch tracks the `main` branch of the `upstreamvcs` repository.

You can check out any of those branch locally. We can track any additional branches as needed for cherry-picking fixes.

Our convention is to check out the `upstreamvcs/main` branch locally and call it `upstreamvcs-main`:

```{terminal}
:copy:
:host:
:dir: gnome-control-center
:user:
:input: git checkout -b upstreamvcs-main upstreamvcs/main

Branch 'upstreamvcs-main' set up to track remote branch 'main' from 'upstreamvcs'.
Switched to a new branch 'upstreamvcs-main'
```


## Optional configuration

The following configuration can simplify certain tasks on Ubuntu Desktop projects.



### Git command aliases

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



### Exporting the build area

Export the `../build-area/` directory before building with the `git-buildpackage` tool:

```{code-block} ini
:caption: `~/.gbp.conf`

[buildpackage]
export-dir = ../build-area/
```

For details, see the {manpage}`gbp.conf(5)` and {manpage}`gbp-buildpackage(1)` manual pages.



### Merging the changelog automatically

To merge the changelog automatically, enable the `dpkg-mergechangelogs` tool in the `~/.config/git/config` file:

```{code-block} ini
:caption: `~/.config/git/config`

[merge "dpkg-mergechangelogs"]  
    name = debian/changelog merge driver
    driver = dpkg-mergechangelogs -m %O %A %B %A
```

Create the `~/.config/git/attributes` file and set `dpkg-mergechangelogs` as the default strategy in it:

```{code-block} ini
:caption: `~/.config/git/attributes`

debian/changelog merge=dpkg-mergechangelogs
```

:::{warning}
This automation might not work when Ubuntu packages use a higher [epoch](https://www.debian.org/doc/debian-policy/ch-controlfields.html#version) than the Debian ones. In that case, fix the changelog manually.
:::


## Next steps

Now that your Git setup is complete, you can contribute to Ubuntu Desktop software. You can build, modify, maintain and package applications. See {ref}`maintain-ubuntu-desktop-software`.


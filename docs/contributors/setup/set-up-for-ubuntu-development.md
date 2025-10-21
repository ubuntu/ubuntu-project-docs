(how-to-set-up-for-ubuntu-development)=
# How to set up for Ubuntu development

The following is a short guide to getting set up for Ubuntu development.

## Prerequisites

You must have a Launchpad ID. To get an ID:

* Go to [Launchpad](https://launchpad.net/)
* Click {guilabel}`Log in / Register`


## Install software

```none
$ sudo apt update && \
  sudo apt dist-upgrade -y && \
  sudo apt install -y \
    apt-cacher-ng \
    autopkgtest \
    build-essential \
    debconf-utils \
    debmake \
    dh-make \
    git-buildpackage \
    libvirt-daemon-system \
    pastebinit \
    pkg-config \
    quilt \
    sbuild-launchpad-chroot \
    ubuntu-dev-tools && \
  sudo snap install lxd && \
  sudo snap install --classic snapcraft && \
  sudo snap install --classic ustriage && \
  sudo snap install --classic --edge git-ubuntu && \
  sudo snap install --classic --beta multipass
```

## Configure software

(gnupg)=
### GnuPG

[GnuPG](https://gnupg.org/) is an encryption tool that helps manage your
{term}`encryption keys <Signing Key>`. You'll need it later to be able to add
a {term}`signature` to each {ref}`upload <Uploading>`.

This setup example is quite concise and only contains the basics, but
eventually the {term}`private key <Signing Key>` will represent your identity
and therefore has to be {ref}`kept safe <pgp-key-storage>` and out of reach of
other entities.


* Install and set up GPG normally.
* List the keys and make sure you associate the email you want to use for
  publishing.

  ```none
  $ gpg --list-secret-key
  /home/karl/.gnupg/pubring.kbx
  -----------------------------
  sec   rsa4096 2018-08-15 [SC]
        7C177302572849D84A5048349E9C224744EF2A5A
  uid           [ultimate] Karl Stenerud <kstenerud@gmail.com>
  ssb   rsa4096 2018-08-15 [E]
  ```

  * In this case, my Canonical address isn't in there, so I need to add it:

    ```none
    $ gpg --edit-key 7C177302572849D84A5048349E9C224744EF2A5A
    ...
    gpg> adduid
    Real name: Karl Stenerud
    Email address: karl.stenerud@canonical.com
    Comment:
    You selected this USER-ID:
        "Karl Stenerud <karl.stenerud@canonical.com>"

    Change (N)ame, (C)omment, (E)mail or (O)kay/(Q)uit? o
    ```

* Then save and quit:

  ```none
  gpg> save
  ```

* And push to the keyserver:

  ```none
  $ gpg --keyserver keyserver.ubuntu.com --send-keys 7C177302572849D84A5048349E9C224744EF2A5A
  ```

Make sure you note the key strength of your GPG key. In this case its rsa4096,
but if you have an older key it may be a weaker 2048-bit or 1024-bit key. If
so, create a new 4096-bit one and deprecate the old one in Launchpad, GitHub,
etc.


(git)=
### Git

Installing `git-ubuntu` will modify your `.gitconfig`. Make sure it got your
Launchpad username correct:

```none
[gitubuntu]
    lpuser = your-launchpad-username
```

You must also ensure that the `[user]` section has your name and email:

```none
[user]
    name = Your Full Name
    email = your@email.com
```

You may also want to add the following to your `.gitconfig`:

```none
[log]
    decorate = short
[commit]
    verbose = true
[merge]
    summary = true
    stat = true
[core]
    whitespace = trailing-space,space-before-tab

[diff "ruby"]
    funcname = "^ *\\(\\(def\\) .*\\)"
[diff "image"]
    textconv = identify

[url "git+ssh://my_lp_username@git.launchpad.net/"]
    insteadof = lp:
```


(quilt)=
### Quilt

[Quilt](https://savannah.nongnu.org/projects/quilt) is a CLI used to manage
patch stacks. It can take any number of patches and condense them into a
single patch.

A working `.quiltrc`:

```none
d=. ; while [ ! -d $d/debian -a `readlink -e $d` != / ]; do d=$d/..; done
if [ -d $d/debian ] && [ -z $QUILT_PATCHES ]; then
    # if in Debian packaging tree with unset $QUILT_PATCHES
    QUILT_PATCHES="debian/patches"
    QUILT_PATCH_OPTS="--reject-format=unified"
    QUILT_DIFF_ARGS="-p ab --no-timestamps --no-index --color=auto"
    QUILT_REFRESH_ARGS="-p ab --no-timestamps --no-index"
    QUILT_COLORS="diff_hdr=1;32:diff_add=1;34:diff_rem=1;31:diff_hunk=1;33:diff_ctx=35:diff_cctx=33"
    if ! [ -d $d/debian/patches ]; then mkdir $d/debian/patches; fi
fi
```

This configures Quilt for use with Debian packages, with default settings that
conform to standard Debian practices.


(dput)=
### DPut

[DPut](https://packages.debian.org/sid/dput) is the Debian Package Upload Tool.
It's used to upload a software package to the Ubuntu repository, or to a
personal package archive (PPA).

A working `.dput.cf`:

```none
[DEFAULT]
default_host_main = unspecified

[unspecified]
fqdn = SPECIFY.A.TARGET
incoming = /

[ppa]
fqdn            = ppa.launchpad.net
method          = ftp
incoming        = ~%(ppa)s/ubuntu
```

This configures `dput` for safety, such that if you accidentally forget to
specify a destination, it'll default to doing nothing.


(sbuild)=
### sbuild

[sbuild](https://wiki.debian.org/sbuild) is a wrapper script around `schroot`.

```{note}
A newer backend, `unshare`, can be used for `sbuild` in place of `schroot`. Compared to `schroot`, it does not need chroot configuration and does not need to run the build as root.

To use `unshare`:

* Install the {pkg}`mmdebstrap` and {pkg}`uidmap` packages.

* Add the following to your `sbuild` configuration in {file}`~/.sbuildrc`:

    ```none
    $chroot_mode = "unshare";
    $unshare_mmdebstrap_keep_tarball = 1;
    ```

Note that while Debian has transitioned to `unshare`, it is not used by Launchpad builders, so it may fail to build some packages.
```

In these examples, replace `my_user` with your own username.

Make mount points:

```none
$ mkdir -p ~/schroot/build
$ mkdir -p ~/schroot/logs
```

Set up a scratch directory:

```none
$ mkdir -p ~/schroot/scratch
$ echo "/home/my_user/schroot/scratch  /scratch          none  rw,bind  0  0" \
 >> /etc/schroot/sbuild/fstab
```

Optionally, you can mount your home directory inside the container:

```none
$ echo "/home/my_user  /home/my_user          none  rw,bind  0  0" \
 >> /etc/schroot/sbuild/fstab
```

In the following template (`.sbuildrc`), replace the following:

* `$maintainer_name = 'Your Full Name <your@email.com>';`

* `$build_dir = '/home/my_user/schroot/build';`

* `$log_dir = "/home/my_user/schroot/logs";`

Template:

```none
# Name to use as override in .changes files for the Maintainer: field
# (optional; only uncomment if needed).
# $maintainer_name = 'Your Full Name <your@email.com>';

# Default distribution to build.
$distribution = "focal";
# Build arch-all by default.
$build_arch_all = 1;

# When to purge the build directory afterwards; possible values are 'never',
# 'successful', and 'always'.  'always' is the default. It can be helpful
# to preserve failing builds for debugging purposes.  Switch these comments
# if you want to preserve even successful builds, and then use
# 'schroot -e --all-sessions' to clean them up manually.
$purge_build_directory = 'successful';
$purge_session = 'successful';
$purge_build_deps = 'successful';
# $purge_build_directory = 'never';
# $purge_session = 'never';
# $purge_build_deps = 'never';

# Directory for chroot symlinks and sbuild logs.  Defaults to the
# current directory if unspecified.
$build_dir = '/home/my_user/schroot/build';

# Directory for writing build logs to
$log_dir = '/home/my_user/schroot/logs';

# don't remove this, Perl needs it:
1;
```

A working `.mk-sbuild.rc`:

```none
SCHROOT_CONF_SUFFIX="source-root-users=root,sbuild,admin
source-root-groups=root,sbuild,admin
preserve-environment=true"
# you will want to undo the below for stable releases, read `man mk-sbuild` for details
# during the development cycle, these pockets are not used, but will contain important
# updates after each release of Ubuntu
SKIP_UPDATES="1"
SKIP_PROPOSED="1"
# if you have e.g. apt-cacher-ng around
DEBOOTSTRAP_PROXY=http://127.0.0.1:3142/
```

```{note}

For more info, see the [Ubuntu wiki page on sbuild](https://wiki.ubuntu.com/SimpleSbuild)
```

(getting-schroots)=
### Getting Schroots

Having `sbuild` set up is only half of the solution. Schroot environments for
the respective builds are also needed.

As outlined in the [Ubuntu wiki page on `sbuild`](https://wiki.ubuntu.com/SimpleSbuild)
one can use e.g. `mk-sbuild noble --arch=amd64` for that.
But many use `sbuild-launchpad-chroot` instead which includes two `sbuild` hooks
and a command line tool to setup and maintain build chroots that are as close
as possible to a standard Launchpad `sbuild` chroot.

```none
$ sudo sbuild-launchpad-chroot create -n noble-amd64 -s noble -a amd64
```

This will create multiple schroots which allow to easily select building against
different configurations like `-proposed` or `-backports`.

In general, schroots can get stale and there are more and more updates needed
in a build. They can be updated individually using `sbuild-update`. The common
`-udcar` options map to `apt update`, `dist-upgrade`, `clean` and `autoremove`.

```none
$ sudo sbuild-update -udcar jammy-proposed-amd64
```

Furthermore, sometimes a schroot for Debian is needed to contribute there
or to compare build results. Those can be created with `sbuild-createchroot`
that comes with the `sbuild` package. We usually add a few packages
that help us later and refer to where to create and where to get the content.
Here is an example:

```none
$ sudo sbuild-createchroot --include=eatmydata,ccache,gnupg unstable /srv/chroot/unstable-amd64-sbuild http://deb.debian.org/debian
```


(lxd)=
### LXD

[LXD](https://documentation.ubuntu.com/lxd/latest/) is a powerful container
system similar in concept to Docker and other container software.

Install and set up LXD using the
[standard installation](https://documentation.ubuntu.com/lxd/latest/installing/)
directions.

Create some helper aliases for common LXD tasks:

```none
$ lxc alias add ls 'list -c ns4,user.comment:comment'

$ lxc alias add login 'exec @ARGS@ \
--mode interactive -- bash -xac $@my_user - exec /bin/login -p -f '
```

Note that the trailing space after the `-f` is important. Replace '`my_user`'
with '`ubuntu`' or whatever username you use in your containers.

```{note}

For more info, see the
[LXD documentation](https://documentation.ubuntu.com/lxd/latest/)
```

(understanding-tooling)=
## Understanding the tooling

The ecosystem of Debian packaging tools is big and diverse, with a great deal of overlap and intended deprecation.
This section introduces some of the most common tools used to generate Ubuntu packages.
A much more comprehensive reference is available in [the Debian developers-reference](https://www.debian.org/doc/manuals/developers-reference/tools.en.html).

There are, roughly speaking, three phases to creating a `.deb` package.

1. Create the source package.
2. Build the binary package from the source package.
3. Test and upload the binary package.

Although coarse, keeping this in mind can help build a more coherent mental model of how the tools interoperate.

### Tools for working on the source package

`uscan`
: Short for "upstream scan", it automates tasks related to keeping up-to-date with upstream code.
It relies on you creating a `debian/watch` file, and then can look for new releases, grab them, and verify signatures.
Source packages require "orig" tarballs as a component, which are the unmodified upstream source code, and `uscan` can help you grab them.

`quilt`
: An older, but still widely-used tool to manage a sequence of patches that apply to the upstream source.
It can not only help you manage the order of patches and their current state of application, but can help you generate patches from modified source code.
Some maintainers prefer to manage patches with git-based tooling, which didn't exist when `quilt` was first developed.
In theory, a `git` branch could encode the order of the patches, which are then rebased onto the new code when doing an update.
Nevertheless, being familiar with `quilt` is helpful when understanding packages worked on by multiple maintainers.

`dch`
: Automation for managing the `/debian/changelog` file.
It helps you generate timestamps, author information, and more.

`git-ubuntu`
: An extension to `git` that can clone the repository attached to a package directly from Launchpad.
It has many other features intended to enable more complex package workflows, which are described in the [Ubuntu Maintainer's Handbook](https://github.com/canonical/ubuntu-maintainers-handbook).

`pull-lp-source`
: Similar to `git-ubuntu`, which should be used instead where possible.
The main difference is that instead of cloning the `git` repository, it grabs the source package from Launchpad.
That means you'll get things like the orig tarball, but not the `git` history.

### Tools for building the binary package from the source package

`sbuild`
: The primary tool Ubuntu Rust packagers will likely use to build binary packages.
Fundamentally it is an orchestration tool and replaces the direct invocation of many other tools.
It creates clean build environments using `schroot`s as a sandbox, containing all the necessary dependencies already installed.
It then invokes `dpkg-buildpackage`, and copies the output out of the `schroot`.
There is an alternative backend for `sbuild`, which replaces `schroot`, called `unshare`.
At the time of writing, Launchpad still uses `schroot` and it is probably preferable to do the same locally to avoid behavior differences.

`dpkg-buildpackage`
: The lower-level build tool that is invoked for you by `sbuild`.
It is responsible for running all of the scripts defined in `debian/rules`.

`debhelper`
: A suite of tools used to simplify many of the elements that packages often have in common.
It defines a clear sequence of steps that packages go through when building, which can all be overridden as necessary within `/debian/rules`.
Giving names and order to these steps means that packages no longer need custom scripts to do things like apply patches, or perform configuration.
If you see a call to `dh` in `/debian/rules`, that package is using `debhelper`.
Some older packages may not have migrated to `debhelper` from the manual approach yet.
Lots of add-on packages exist, most notably `dh-cargo` which is listed separately.

`lintian`
: The static analysis tool use to check packages for policy violations, usually executed on your behalf by `sbuild`.
You should run it on your source package, but also on your compiled binary packages, as the results of just one or the other are not comprehensive.


### Tools for working with the compiled binary package

`lintian` (again)
: As mentioned, you should do static analysis of both your source package and your binary package, as the results will differ and both can be useful.

`autopkgtest`
: The testing framework for `.deb` packages.
It sets up an isolated environment, which can be any of a number of containers or VMs, and runs the tests defined in the `debian/tests` directory.
In the official archives, these tests run automatically as part of CI.
However, for PPAs in a typical Ubuntu workflow, the tests are not triggered automatically.

`dput`
: Upload your package to the package archive or a PPA.

`ppa-dev-tools`
: This collection of tools makes it easy to trigger autopkgtests on Launchpad for a PPA, and to otherwise administer your PPAs.


(caching-packages)=
## Caching packages

Downloading packages can be a bottleneck, so it helps to set up a local cache:

```none
$ echo 'Acquire::http::Proxy "http://127.0.0.1:3142";' \
| sudo tee /etc/apt/apt.conf.d/01acng
```


## Configure your groups

Your user should be a member of the following groups:

* `adm`
* `libvirt`
* `lxd`
* `sbuild`
* `sudo`

Ensure you have installed the packages listed above, which will be the trigger
to create most of these groups. For group membership to be activated one
usually needs to re-login. Then, one can double check group membership via:

```none
$ groups my_user
my_user : my_user adm cdrom sudo dip plugdev lpadmin sambashare \
 libvirt sbuild lxd
```

If any of the following groups is missing for your user you can fix it via
`adduser`, like this:

```none
$ sudo adduser my_user lxd
$ sudo adduser my_user sbuild
$ sudo adduser my_user libvirt
```


## Configure your .profile

Your `.profile` should include entries for `DEBFULLNAME` and `DEBEMAIL`:

```none
export DEBFULLNAME="Your Full Name"
export DEBEMAIL=your@email.com
```

You can also set the `DEBSIGN` variables:

```none
export DEBSIGN_PROGRAM="/usr/bin/gpg2"
export DEBSIGN_KEYID="0xMYKEYHASH"
```

A fix for "clear-sign failed: Inappropriate ioctl for device":

```none
$ export GPG_TTY=$(tty)
```

If you're operating from a GUI, this can be useful:

```none
$ eval `dbus-launch --sh-syntax`
```


(keyring-with-plaintext-storage)=
### Keyring with plaintext storage

See `git-ubuntu` {ref}`keyring-integration` for details on how `git-ubuntu` uses keyring. If
you want to reconfigure keyring to use plaintext storage to avoid getting
keyring password prompts, create the file
`~/.local/share/python_keyring/keyringrc.cfg` with the following contents:

```none
[backend]
default-keyring=keyrings.alt.file.PlaintextKeyring
```

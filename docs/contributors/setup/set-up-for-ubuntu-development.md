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
    autopkgtest \
    dh-make \
    git-buildpackage \
    pastebinit \
    sbuild-launchpad-chroot \
    ubuntu-dev-tools && \
  sudo snap install lxd && \
  sudo snap install --classic snapcraft && \
  sudo snap install --classic git-ubuntu
```

## Configure software

(gnupg)=
### GnuPG

[GnuPG](https://gnupg.org/) is an encryption tool that helps manage your
{term}`encryption keys <Signing Key>`. You'll need it later to be able to add
a {term}`signature` to each {ref}`upload <uploading-to-the-archive>`.

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

[sbuild](https://wiki.debian.org/sbuild) is the recommended tool for building
packages on Ubuntu.

Add your user to the `sbuild` group:

```bash
$ sudo adduser $USER sbuild
$ newgrp sbuild
```

::::{tab-set}

:::{tab-item} Ubuntu 25.10 and later

Install the `mmdebstrap` and `uidmap` packages:

```shell
$ sudo apt install -y mmdebstrap uidmap
```

`sbuild` reads the user specific configuration file
`~/.config/sbuild/config.pl`.

Create the file if it does not exist:
```shell
$ mkdir -p ~/.config/sbuild
$ touch ~/.config/sbuild/config.pl
```


Save the file with the following content:

```perl
$chroot_mode = 'unshare';
$unshare_mmdebstrap_keep_tarball = 1;

$unshare_tmpdir_template = '/var/tmp/tmp.sbuild.XXXXXXXXXX';

$clean_source = 0;
$run_lintian = 0;
```

:::

:::{tab-item} Ubuntu 24.04 LTS and earlier

Make the required mount points for builds, logs, and scratch:

```shell
$ mkdir -p ~/schroot/{build,logs,scratch}
```

Add a the scratch directory to `/etc/schroot/sbuild/fstab`:

```shell
$ echo "$HOME/schroot/scratch  /scratch          none  rw,bind  0  0" \
  | sudo tee -a /etc/schroot/sbuild/fstab

```

Optionally, you can mount your home directory inside the container:

```none
$ echo "$HOME  $HOME          none  rw,bind  0  0" \
  | sudo tee -a /etc/schroot/sbuild/fstab
```

`sbuild` reads the user specific configuration file
`~/.config/sbuild/config.pl`.

Create the file if it does not exist:
```shell
$ mkdir -p ~/.config/sbuild
$ touch ~/.config/sbuild/config.pl
```

Save the file with the following content, replacing the placeholders:

* `$maintainer_name = 'Your Full Name <your@email.com>';`

* `$build_dir = '/home/my_user/schroot/build';`

* `$log_dir = "/home/my_user/schroot/logs";`

```perl
# Name to use as override in .changes files for the Maintainer: field
# (optional; only uncomment if needed).
# $maintainer_name = 'Your Full Name <your@email.com>';

$chroot_mode = 'schroot';
$unshare_mmdebstrap_keep_tarball = 1;

# Default distribution to build.
$distribution = "resolute";
# Build arch-all by default.
$build_arch_all = 1;

# Do not check for the presence of the build dependencies on the host
# system, as these exist only in the unshare chroot.
$clean_source = 0;
$run_lintian = 0;

# When to purge the build directory afterwards; possible values are 'never',
# 'successful', and 'always'.  'always' is the default. It can be helpful
# to preserve failing builds for debugging purposes.  Switch these comments
# if you want to preserve even successful builds, and then use
# 'schroot -e --all-sessions' to clean them up manually.
$purge_build_directory = 'successful';
$purge_session = 'successful';
$purge_build_deps = 'successful';

# Directory for chroot symlinks and sbuild logs.  Defaults to the
# current directory if unspecified.
$build_dir = '/home/my_user/schroot/build';

# Directory for writing build logs to
$log_dir = '/home/my_user/schroot/logs';

# Key used to sign the source package. Defaults to not using any key.
# $key_id = '';

# don't remove this, Perl needs it:
1;
```

Create `~/.mk-sbuild.rc`:

```shell
$ touch ~/.mk-sbuild.rc
```

Save the file with the following content:

```none
SCHROOT_CONF_SUFFIX="source-root-users=root,sbuild,admin
source-root-groups=root,sbuild,admin
preserve-environment=true"
# you will want to undo the below for stable releases, read `man mk-sbuild` for details
# during the development cycle, these pockets are not used, but will contain important
# updates after each release of Ubuntu
SKIP_UPDATES="1"
SKIP_PROPOSED="1"
# if you have a local proxy like apt-cacher-ng around enable the following
# DEBOOTSTRAP_PROXY=http://127.0.0.1:3142/
```

(schroots)=
### schroots

Having `sbuild` set up is only half of the solution - schroot (secure chroot)
environments for the respective builds are also needed.

Get a schroot for a specific release of Ubuntu using `mk-sbuild`:

```shell
$ mk-sbuild resolute --arch=amd64
```

List the available schroots:

```none
$ sbuild -l
```

Update a schroot:

```shell
$ sbuild-update -udc resolute-amd64
```

Delete a schroot:

```shell
$ sudo rm /etc/schroot/chroot.d/sbuild-resolute-amd64
$ sudo rm -rf /var/lib/schroot/chroots/resolute-amd64
```

:::

::::

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

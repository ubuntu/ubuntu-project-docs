(how-to-run-package-tests)=
# How to run package tests

Packages have their own tests under `debian/tests`. Run those to ensure there are no regressions.

We can have Launchpad do it against a PPA, or use an LXC container, or a VM to
run the `autopkgtests` locally. Each approach has its benefits, so they're all
worth learning, but the first option (PPA-based testing) produces results most
similar to what occurs in the archive itself, so we'll start there.


## 1) PPA-based `autopkgtest` testing

First, if you haven't already, install `ppa-dev-tools`:

```none
$ sudo snap install ppa-dev-tools
$ ppa --help
usage: ppa [-h] [-C CONFIG_FILENAME] [-D] [-V] [--dry-run] [-v] [-q]
       {create,desc,destroy,list,set,show,status,tests,wait} ...
```

Next, you'll need to
{ref}`set up a PPA and build your package in it <how-to-build-packages-in-a-ppa>`. Once it has built binaries for
the architecture(s) you intend to test:

```none
$ ppa tests \
  --show-url ppa:kstenerud/postfix-postconf-segfault-1753470 \
  --release bionic
```

This prints to the console a bunch of lines like:

```none
 Using Release Packages ♻️
 http://autopkgtest.ubuntu.com/request.cgi?release=bionic&arch=amd64&package=postfix&ppa=kstenerud/postfix-postconf-segfault-1753470&trigger=postfix/3.3.0-1ubuntu0.1~ppa1
 http://autopkgtest.ubuntu.com/request.cgi?release=bionic&arch=s390x&package=postfix&ppa=kstenerud/postfix-postconf-segfault-1753470&trigger=postfix/3.3.0-1ubuntu0.1~ppa1
  ...
```

The `autopkgtest` requests require special permissions to run; as a new
developer you'll need to ask your co-workers or a Core Dev to load them. If you
don't know where else to ask, the `#ubuntu-devel` Matrix channel is suitable.
The `--showurl` parameter causes these URLs to be printed out so they're easier to
cut-and-paste into email or chat channels.

Once you've gained permissions to run `autopkgtests`, you can load each of these
URLs in your web browser yourself, which will cause the appropriate
autopkgtests to run. If you omit the `--show-url` parameter, `ppa tests` will
instead display clickable links, making it even more convenient. Alternatively,
it is possible to
{ref}`trigger the tests through the command line <trigger-tests-from-the-command-line>`,
which is useful when you need to trigger several tests.

After a while, run `ppa tests` again to see how the tests are coming along:

```none
$ ppa tests ppa:kstenerud/postfix-postconf-segfault-1753470 --release bionic
...
Results: (from http://autopkgtest.ubuntu.com/results/.../?format=plain)
  postfix @ amd64:
    14.06.22 21:57:01 ✅     Triggers: postfix/3.3.0-1ubuntu0.1~ppa1
...
```

If anything failed, you can load up the log URLs to see details about why.


## Testing with VMs and containers

If you use a container or VM, you'll need an image to test from. `autopkgtest`
will build a suitable image for you. You may want to regenerate the image from
time to time to cut down on the number of updates it must run.

The type of image you can use (chroot, container, or VM) depends on the
restrictions in `debian/tests/control` (see this page
[in the `autopkgtest` docs](https://salsa.debian.org/ci-team/autopkgtest/-/blob/master/doc/README.package-tests.rst)).

Important restrictions:

* `breaks-testbed`: This test is liable to break the testbed system (VM or container recommended)
* `isolation-machine`: You must use a VM to run these tests
* `isolation-container`: You must use a VM or container to run these tests
* `needs-reboot`: The test reboots the machine, so you must use a VM or container


### The general process

No matter whether you are testing in a VM or a container, the command to run
the tests (and indeed, the general process) is constructed in the same way. 


#### Build the image

First, we will build the image we prepared in the previous section.

* To build a VM image:

  ```none
  $ autopkgtest-buildvm-ubuntu-cloud -r noble -v
  ```

  (Replace `noble` with your release of choice)
 
  Copy the resulting image (`autopkgtest-noble-amd64.img`) to the
  `/var/lib/adt-images` directory.

  ```{note}
  Use `-m` to specify a closer mirror or `-p` to use a local proxy
  if it's slow.

* To build a container image:

  ```none
  $ autopkgtest-build-lxd ubuntu-daily:resolute
  ```

  You should see an `autopkgtest` image now when you run `lxc image list`.

  ```{warning}
  The `autopkgtest-build-lxd` command only works with Ubuntu 18.04 (Bionic Beaver) images and later; when applied to older releases, it fails with a timeout or network errors. In this case you can use the `autopkgtest-buildvm-ubuntu-cloud` command to build a VM image instead.
  ```


#### Constructing the command

For every method, our command will use the same format:

```none
autopkgtest <options> <what we want to test> -- <where we want to test> 
```

We have already created the image, thing we want to test, so the part of the
command **before** the `--` will be the same in every example, and uses the
following options:

```none
$ autopkgtest \
  --apt-upgrade \
  --shell-fail \
  --output-dir <package-name>
    <what we want to test>
  -- <where we want to test> </image path/image name.img>
```

For more details on these options you can refer to the {manpage}`autopkgtest(1)`
manual page.

Then, for each method, the only part that will change is the "where" we want
to test, which will be the part **after** the `--`. 


## 2) Testing with a VM


### Run the tests (manually) against a local directory

Make sure you're one directory up from your package directory and run:

```none
$ autopkgtest \
  --apt-upgrade \
  --shell-fail \
  --output-dir dep8-mypackage \
    mypackage/ \
  -- qemu /var/lib/adt-images/autopkgtest-noble-amd64.img
```

Where:

 * `--apt-upgrade`: runs `apt-get upgrade`

 * `--shell-fail`: stops and gives you a shell if there is a failure (good for debugging)

 * `--output-dir dep8-mypackage`: Put your package name in here -- writes output report to the directory `dep8-mypackage`

 * `mypackage/`: Put your package name here; the trailing slash tells it to interpret this as a directory rather than a package name

Everything after the `--` tells it how to run the tests. `qemu` is shorthand for `autopkgtest-virt-qemu`.


#### In a VM, Using the PPA


```none
$ autopkgtest \
  --apt-upgrade \
  --shell-fail \
  --output-dir dep8-mypackage-ppa \
  --setup-commands="sudo add-apt-repository \
    --yes \
    --enable-source \
    --ppa mylaunchpaduser/noble-mypackage-fixed-something-1234567" \
  --no-built-binaries \
  mypackage \
  -- qemu /var/lib/adt-images/autopkgtest-noble-amd64.img
```

Where (in setup-commands):

* `--yes`: Assume "yes" for all questions

* `--ppa`: Add an Ubuntu Launchpad Personal Package Archive in the format USER/PPA

* `--enable-source`: Add `deb-src` line for the repository

* `--no-built-binaries`: Don't build

Note: In this case, the package name **doesn't** have a trailing slash because we want to install the package.


#### In a Container, Using the PPA

The command only differs after the `--` part. For example:


```none
$ autopkgtest \
  --apt-upgrade \
  --shell-fail \
  --output-dir dep8-mypackage-ppa \
  --setup-commands="sudo add-apt-repository \
    --yes \
    --enable-source \
    --ppa mylaunchpaduser/noble-mypackage-fixed-something-1234567" \
  --no-built-binaries \
  mypackage \
  -- lxd autopkgtest/ubuntu/noble/amd64
```


## 3) Testing with a container


### Run the tests (against the PPA)

```none
$ autopkgtest \
 --apt-upgrade \
 --shell-fail \
 --output-dir dep8-mypackage-ppa \
 --setup-commands="sudo add-apt-repository -y -u -s \
 ppa:mylaunchpaduser/noble-mypackage-fixed-something-1234567" \
 --no-built-binaries \
 mypackage \
 -- lxd autopkgtest/ubuntu/noble/amd64
```

The `setup-commands` options are as described in the previous section.


## Common options you'll need


### Run against `-proposed` or its subsets

Quite often, a test fails by running against new packages in the `-proposed`
pocket. In this case, it's helpful to check if the test needs other packages
from `-proposed` to resolve the issue. This can easily be done via the
`--apt-pocket` option.

A test will usually run against all packages in `-release` plus the new
candidate from `-proposed`, which looks like this:

```none
--apt-pocket=proposed=src:yourpkg
```

To run against all packages in `-proposed`, you can remove the reference to a
specific package.

```none
--apt-pocket=proposed
```

If instead you need a given set of packages, but not *everything* else from
`-proposed`, you can use a comma-separated list:

```none
--apt-pocket=proposed=src:srcpkg1,srcpkg2
```

Here are some examples testing various combinations against `octave-parallel`:

```none
# normal
$ autopkgtest --apt-pocket=proposed \
 --shell-fail octave-parallel_4.0.1-2ubuntu1~ppa1.dsc \
 -- qemu ~/work/autopkgtest-noble-amd64.img
# all proposed
$ autopkgtest --apt-pocket=proposed \
 --shell-fail octave-parallel_4.0.2-1ubuntu1~ppa1.dsc \
 -- qemu ~/work/autopkgtest-noble-amd64.img
# specific subset
$ autopkgtest --apt-pocket=proposed=src:octave,octave-parallel,octave-struct \
 --shell-fail octave-parallel_4.0.2-1ubuntu1~ppa1.dsc \
 -- qemu ~/work/autopkgtest-noble-amd64.img
```


### Size the test VM

One might often wonder "hmm, might this work with more CPU/memory?". At least
in the case of QEMU and nova, that can be controlled.

For `qemu` you can add `--ram-size` and `--cpus`. For example, to run the same
test in different sizes:

```none
$ autopkgtest --no-built-binaries --apt-upgrade \
 --shell-fail octave-parallel_4.0.2-1ubuntu1~ppa1.dsc \
 -- qemu --ram-size=1536 --cpus 1 ~/work/autopkgtest-noble-amd64.img
$ autopkgtest --no-built-binaries --apt-upgrade \
 --shell-fail octave-parallel_4.0.2-1ubuntu1~ppa1.dsc \
 -- qemu --ram-size=4096 --cpus 4 ~/work/autopkgtest-noble-amd64.img
```


### Restrict networking

Some DEP-8 test failures occur due to the `autopkgtest` environment's network
restrictions. A good clue that this has happened is when the tests reliably
pass locally, yet fail after uploading to Launchpad. Other clues include:

* Test logs mentioning port errors
* Inaccessible URLs or IPs
* Upstream language packaging tools like `npm`, `compose`, `pip`, etc.

The network restrictions can be mimicked by invoking `autopkgtest` locally with
an internal proxy. This won't fully replicate it as there are also firewalls
in place, but when in doubt it often is worthwhile to retry with a local
VM-based repro to check if it fails this way.

To do this, add the internal proxy (this needs the VPN up); or if you want
to, try another proxy of your choice that is rather restrictive. Then add the
following to the call of `autopkgtest:

```none
--env='no_proxy=127.0.0.1,127.0.1.1,localhost,localdomain,novalocal,internal,archive.ubuntu.com,security.ubuntu.com,ddebs.ubuntu.com,changelogs.ubuntu.com,ppa.launchpad.net' \ 
--env='http_proxy=http://squid.internal:3128'
```

Here's an example from when we tracked down an issue with `ulfius`:

```none
$ autopkgtest \
 --env='no_proxy=127.0.0.1,127.0.1.1,localhost,localdomain,novalocal,internal,archive.ubuntu.com,security.ubuntu.com,ddebs.ubuntu.com,changelogs.ubuntu.com,ppa.launchpad.net' \
 --env='http_proxy=http://squid.internal:3128' \
 --no-built-binaries \
 --apt-upgrade \
 --shell-fail ulfius_2.7.1-3.dsc  \
 -- qemu ~/work/autopkgtest-impish-amd64.img
```


## Save the results

You'll see the tests run:

```none
autopkgtest [11:47:12]: version 5.3.1
autopkgtest [11:47:12]: host karl-tp; command line: /usr/bin/autopkgtest -U -s -o dep8-postfix-ppa '--setup-commands=sudo add-apt-repository -y -u -s ppa:kstenerud/postfix-postconf-segfault-1753470' -B postfix -- lxd autopkgtest/ubuntu/focal/amd64
autopkgtest [11:47:31]: @@@@@@@@@@@@@@@@@@@@ test bed setup

...

----------------------------------------------------------------------
Ran 15 tests in 67.027s

OK
autopkgtest [11:49:51]: test postfix: -----------------------]
autopkgtest [11:49:51]: test postfix:  - - - - - - - - - - results - - - - - - - - - -
postfix              PASS
autopkgtest [11:49:52]: @@@@@@@@@@@@@@@@@@@@ summary
postfix              PASS
```

Save the last part for the description for your merge proposal.

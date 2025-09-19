(how-to-build-packages-in-a-ppa)=
# How to build packages in a PPA

The easiest way to build a package is to let Launchpad do it. {term}`Personal Package Archives (PPAs) <ppa>` are encapsulated build spaces in Launchpad that are owned and controlled by you. Packages you sign and upload to a PPA are built with the same machinery as official Ubuntu packages, so they're also a great way to verify your work before formally submitting it to Ubuntu.

See also {ref}`how-to-build-packages-locally`.


## About building in a PPA

Once built, the packages in a PPA are publicly available, allowing you to share them with bug reporters for testing fixes and with reviewers of your {ref}`merge proposals <how-to-submit-a-merge-proposal>` who can readily use them for testing.

The downsides to PPAs are:

1. They share resources with other Launchpad build processes, so during busy times, it can take a while.

1. It's less hands-on than a local build, so it can be hard to use for highly iterative workflows like investigating dependency issues or git-bisecting build failures (if you expect that you'll need to debug the build, such as going into the environment to modify and retry, a {ref}`local build <how-to-build-packages-locally>` is recommended).

1. The PPAs are picky about version strings.


### Set the version string

For the PPA, we should change the version in the changelog to one that's lower
than the official version we plan to release. For example:

```diff
-postfix (3.3.0-1ubuntu0.1) bionic; urgency=medium
+postfix (3.3.0-1ubuntu0.1~bionic1) bionic; urgency=medium
```

Since the tilde `~` character sorts lower than everything else in Launchpad, we
can append `~<string>1` to the version string in `debian/changelog`. See more
details about the sorting algorithm here: {manpage}`deb-version(7)`

Having a numeric digit in this suffix is important because once Launchpad has
accepted your upload, it won't accept another one with the same version number
(nor any earlier version number). So if you need to fix something in your
upload -- even just copyediting your changelog entry -- you need an
incrementally higher version number. Incrementing the suffix allows you to do
this without needing to modify the official version number.

For the text, you can use any string as desired; often people use their
username, or just '`ppa`'. An advantage of using the release codename, however,
is that if you later intend to port the same package to multiple releases (e.g.
you're doing an MRE, or an SRU that has the same official version in multiple
Ubuntu releases), using the codename ensures each has a unique version (for
Launchpad) while also indicating which package to use for which Ubuntu release
(for users).

As an aside, you'll sometimes run across the suffix style `"~18.04.1"` which is
adopted for reasons similar to the codename, and tends to be a preferred choice
in semi-official PPAs such as ones used for official customer deliveries or
formally maintained backports to the wider user base. To avoid confusion, the
`'~<codename>N'` style may be better for the one-off testing-oriented PPAs
being discussed here.


### Modify the version for PPA

The command below can be used to modify the version for PPA usage:

```none
$ codename="bionic"
$ dch -l "~${codename}1" --distribution "${codename}" "Build for PPA"
```

If a PPA is used to build the package and the version string was changed as
described above, make sure to rebuild and resign the source package:

```none
$ dpkg-buildpackage -S -I -i -nc -d
```


### Create the PPA archive

First, install `ppa-dev-tools` from the snap store:

```none
$ sudo snap install ppa-dev-tools
```

Next, follow the directions in `INSTALL.md` to install prerequisites and to install
the tool. Then, to use it:

```none
$ ppa create <ppa-name>
```

This creates the PPA for you, and enables all available build architectures.
The first time you run it, it'll ask for authentication via the web.

You can use whatever you want for your `ppa-name`, so long as it's unique in
your own namespace. For consistency, you may want to use a standard naming
style, such as:

```none
$ ppa_name="<package>-<type>-<lpbug>-<desc>"
# or
$ ppa_name="lp-<lpbug>-<package>-<desc>"
```

It isn't important which you use, just be consistent.
What is important though is that this has to be all lower case.
Many of us even keep the associated git-ubuntu branch names consistent with the PPA names.

So for example, you might have PPAs named `apache2-sru-lp12345678`, `clamav-fix-lp1920217`, and `clamav-fix-lp1920217-alternative`.


### (Optional) Create the PPA archive via web

Alternatively, you can create PPAs directly via Launchpad's web interface.

Go to your launchpad page (`https://launchpad.net/~your-username`) and click
"Create a new PPA". Give it a name such that you'll remember what it's about
in a few months' time. A useful form is `package-type-lpbug-description`:

For example:

* **URL:** `postfix-sru-lp1753470-segfault`
* **Display name:** `postfix-fix-lp1753470-segfault`
* **Description:** `(leave it empty)`

Now click "Activate".

It is also helpful to enable all architectures to ensure no build regressions
were introduced. Do so by clicking on `Change Details` in the newly-created
PPA page, and then selecting the other architectures.


### Upload the source package

```none
$ dput ppa:kstenerud/postfix-sru-lp1753470-segfault ../postfix_3.3.0-1ubuntu0.1~bionic1_source.changes
```

When it finishes, you should be able to see it, e.g.:
`https://launchpad.net/~kstenerud/+archive/ubuntu/postfix-postconf-segfault-1753470/+packages`


```{note}

You must wait for the package to build server-side before you can use the
PPA to install packages. This might take anywhere from a few minutes to a
few hours depending on how busy things are!
 
It'll first build the binaries for each architecture, then publish the
source and binary packages to be publicly downloadable.
```


#### Check progress with `ppa`

You can use the `ppa` tool to poll launchpad for progress status:

```none
$ ppa wait ppa:kstenerud/postfix-sru-lp1753470-segfault
```

It will exit with `0` once the PPA packages have fully built.

Launchpad also sends "status updates" notification mails, so monitor your
inbox.

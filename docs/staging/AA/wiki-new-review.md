# NEW processing (wiki)

To work with the upload queue, you may either use the
[web interface](https://launchpad.net/ubuntu/xenial/+queue) or the `queue` API
client in `ubuntu-archive-tools`. The API client should generally be faster and
more flexible; in particular, it is
[not currently possible to override individual binaries using the web interface](https://bugs.launchpad.net/bugs/828649).

Both source packages and new binaries which have not yet been approved are not
automatically accepted into the archive, but are instead held for checking and
manual acceptance. Once accepted they'll be automatically approved from then on.

The current queue can be obtained with:

```bash
$ ./queue info
```

This is the `NEW` queue for the development series of Ubuntu by default; you
can change the queue with `-Q`, the distro with `-D` and the release using `-s`.
To list the `UNAPPROVED` queue for `ubuntu/xenial`, for example:

```bash
$ ./queue -s xenial -Q unapproved info
```

Packages are placed in the `UNAPPROVED` queue if they're uploaded to a closed
distribution, and are usually security updates or similar; this should be
checked with the uploader.

You can give a string argument after `info` which is interpreted as a sub-string
match filter.

To obtain a report of the size of all the different queues for a particular
release:

```bash
$ ./queue report
```

Back to the `NEW` queue for now, however. You'll see output that looks somewhat
like this:

```text
$ ./queue info
 Listing ubuntu/dapper (New) 4
---------|----|----------------------|----------------------|---------------
   25324 | S- | diveintopython-zh    | 5.4-0ubuntu1         | 3 minutes
         | * diveintopython-zh/5.4-0ubuntu1 Component: main Section: doc
   25276 | -B | language-pack-kde-co | 1:6.06+20060427      | 2 hours 20 minutes
         | * language-pack-kde-co-base/1:6.06+20060427/i386 Component: main Section: translations Priority: OPTIONAL
   23635 | -B | upbackup (i386)      | 0.0.1                | 2 days
         | * upbackup/0.0.1/i386 Component: main Section: admin Priority: OPTIONAL
         | * upbackup_0.0.1_i386_translations.tar.gz Format: raw-translations
   23712 | S- | gausssum             | 1.0.3-2ubuntu1       | 45 hours
         | * gausssum/1.0.3-2ubuntu1 Component: main Section: science
---------|----|----------------------|----------------------|---------------
                                                               4
```

The number at the start can be used with other commands instead of referring to
a package by name. The next field shows you what is actually in the queue,
"`S-`" means it's a new source and "`-B`" means it's a new binary. You then have
the package name, the version and how long it's been in the queue.

New sources need to be checked to make sure they're well packaged, the licence
details are correct and permissible for us to redistribute, etc. See:

* [Packaging new software](http://packaging.ubuntu.com/html/packaging-new-software.html)

* [debian/copyright file](http://packaging.ubuntu.com/html/debian-dir-overview.html#the-copyright-file)

* and [Debian's Reject FAQ](https://ftp-master.debian.org/REJECT-FAQ.html).

You can fetch a package from the queue for manual checking:

```bash
$ ./queue fetch 25324
```

Or, if you just want to print the URLs so that you can fetch them on a system
with a faster network connection:

```bash
$ ./queue show-urls 25324
```

The source is now in the current directory and ready for checking. Any problems
should result in the rejection of the package (also send a mail to the uploader
explaining the reason and cc ubuntu-archive@lists.ubuntu.com):

```bash
$ ./queue reject 25324
```

If the package is fine, you should next check that it's going to end up in the
right part of the archive. On the next line of the `info` output, you have
details about the different parts of the package, including which component,
section, etc. it is expected to head into. One of the important jobs is making
sure that this information is actually correct through the application of
overrides.

To alter the overrides for a package, use:

```bash
$ ./queue override -c universe ubuntustudio-menu
```

Where the override can be `-c <component>`, `-x <section>`, and/or (for binary
packages) `-p <priority>`. If you want to limit the override application to
only source or only binary packages, use the `--source` or `--binary` options
respectively.

Often, a binary will be in the `NEW` queue because it is a shared library that
has changed `SONAME`. In this case you'll probably want to check the existing
overrides to make sure anything new matches. These can be found in
`/ubuntu/indices` on Ubuntu mirrors.

Currently, a special case of this are the kernel packages, which change package
names with each ABI update and build many distinct binary packages in different
sections. A helper tool has been written to apply overrides to the queue based
on the packages that are currently published:

```bash
$ ./kernel-overrides [-s <sourcepackage>] <newabi>
```

Binary packages are not often rejected (they go into a black hole with no
automatic notifications), so, check the `.deb` contains files, run `lintian` on
it and file bugs when things are broken. The binaries also need to be put into
`universe` etc as appropriate even if the source is already there.

If you're happy with a package, and the overrides are correct, accept it with:

```bash
$ ./queue accept 23712
```

You can also use `./queue accept binary-name` which will accept it for all
architectures.


## Partner archive

The Canonical partner archive, though not part of Ubuntu proper, is managed
using the same tools and queues. As such, use the same procedures when
processing partner packages. E.g.:

```text
$ ./queue -s hardy info
Listing ubuntu/hardy (New) 2
---------|----|----------------------|----------------------|---------------
 1370980 | S- | arkeia               | 8.0.9-3              | 19 hours
	 | * arkeia/8.0.9-3 Component: partner Section: utils
 1370964 | S- | arkeia-amd64         | 8.0.9-3              | 19 hours
	 | * arkeia-amd64/8.0.9-3 Component: partner Section: utils
---------|----|----------------------|----------------------|---------------
                                                               2
```

Notice `'Component: partner'`. Use `-A ubuntu/partner` to remove a package:

```bash
$ ./remove-package -m "request from First Last name" -A ubuntu/partner -s precise adobe-flashplugin
```

The rules governing package inclusion in partner are not the same as those for
the main Ubuntu archive. See
[Extension Repository Policy](https://wiki.ubuntu.com/ExtensionRepositoryPolicy)
for the Technical Board's requirements regarding the contents of add-on
repositories made available through the `Software Sources` interface.

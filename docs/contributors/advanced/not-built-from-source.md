(what-is-a-nbs)=
# What is a NBS?

NBS stands for **"Not Built from Source"**, i. e. binary packages that are no longer built by any source package. The most common reasons for that are:

* A library gets a new SONAME (libfoo1), the previous version built libfoo0.
* A package gets renamed by upstream and the renaming is reflected in the package name change. 

These packages are not automatically removed from the archive, since generally they still have reverse dependencies (packages depending on them).

An appreciated activity involving NBS is to rebuild or port packages that depend on them, so that the NBS has no more reverse dependencies and can be removed from the archive. Frequently, a rebuild will cause a selection of new binary dependencies, and the package will work, although sometimes adjusting debian/control is needed, and more rarely, one needs to port the package to work with the new system.

A list of NBS is available at <https://people.ubuntu.com/~ubuntu-archive/nbs.html> and is updated every hour. For each package that is NBS, the list of packages that depends on the NBS and needs to be ported is provided. Once everything is confirmed as ported (and the list reaches 0 packages), the NBS can be removed from the archive.

Note that all NBS packages have to be removed by the final release. Packages which have not been transitioned will become uninstallable in the final release! 

(example-1-libminc0)=
## Example 1: libminc0

libminc0 is a NBS superseded by libminc2-1 in Hardy. The NBS report page reports that one package still depends on libminc0:

```
libminc0:
   minc-tools    universe    sparc
```

In this case, we need to rebuild minc-tools against libminc2-1 to remove libminc0 from the archive.

First of all, we need to find the source package that builds minc-tools. We can use <https://packages.ubuntu.com/> or {command}`apt-cache` :

```{terminal}
apt-cache showsrc minc-tools | grep Package

Package: minc
```

What we have to do now is download the minc source package and check how to rebuild the binary package minc-tools with the new library. The {file}`debian/control` file shows:

```
Depends: ${shlibs:Depends}, csh | c-shell, netcdf-bin, libgetopt-tabular-perl, libtext-format-perl, imagemagick
```

This means that the dependency is not hardcoded in it, and is automatically chosen at build-time.

Let's modify the {file}`debian/changelog` file. Last changelog entry is:

```
minc (2.0.14-2) unstable; urgency=low
```

Since Ubuntu didn't make any changes to the package, we just add build1 to the current version and a good description for the transition we are doing:

```
minc (2.0.14-2build1) hardy; urgency=low

  * Rebuild for libminc0 -> libminc2-1 transition.

 -- Name Surname <email@ubuntu.com>  Sun, 2 Mar 2008 10:55:10 +0100
```

If a bug exists on Launchpad, add a (LP: #XXXXXX) tag to automagically close it.

Since this is a no-change rebuild, we do not modify the Maintainer field in {file}`debian/control`. The "build1" is not treated as a delta, and will be dropped at next package sync. {command}`dch -R` should do the right thing here.

Now, a test build is needed to check that the package doesn't FTFBS with the new library. Once the build-install-run test is successfull, we can upload the package (or create a debdiff for sponsoring). 

(example-2-libmpich1.0c2)=
## Example 2: libmpich1.0c2

libmpich1.0c2 is a NBS superseded by libmpich1.0ldbl. These packages still depends on libmpich1.0c2:

```
-- hardy/universe amd64 deps on libmpich1.0c2:
illuminator-demo
libluminate7
libpetsc2.3.2
-- hardy/universe i386 deps on libmpich1.0c2:
illuminator-demo
libluminate7
libpetsc2.3.2
-- hardy/universe sparc deps on libmpich1.0c2:
illuminator-demo
libluminate7
libpetsc2.3.2
```

In this case, we have three binary packages to inspect: illuminator-demo, libluminate7, and libpetsc2.3.2. Looking at a hardy cache, we can discover that those come from two sources: illuminator and petsc.

```{terminal}
apt-cache showsrc petsc | grep Binary

Binary: libpetsc2.3.3-dbg, libpetsc2.3.3-dev, petsc-dev, petsc2.3.3-doc, libpetsc2.3.3
```

Our reverse dependency for petsc is libpetsc2.3.2, which means we don't really care, as the new source doesn't use it, but we need to NBS libpetsc2.3.2 before we can NBS libmpich1.0c2. This is the report for libpetsc2.3.2:

```
-- hardy/universe amd64 deps on libpetsc2.3.2:
illuminator-demo
libluminate7
-- hardy/universe i386 deps on libpetsc2.3.2:
illuminator-demo
libluminate7
-- hardy/universe sparc deps on libpetsc2.3.2:
illuminator-demo
libluminate7
```

Next step is to inspect the binary packages to see if they have alternatives defined in the dependencies. In this case, there are hard-dependencies for libmpich1.0c2 for both illuminator-demo and libluminate7.

Next thing to try is a rebuild. Update the changelog with a <version>-<debian>build1 entry, and report the transition you are processing in a form like:

```
  * rebuild for libmpich1.0c2 -> libmpich1.0ldbl and libpetsc2.3.2 -> libpetsc2.3.3
```

Don't touch any other files in the package, generate a new source candidate, and try a test build.

If the package rebuilds fine, the transition is complete. Sometimes, anyway, the transition brings to a FTFBS that must be tackled and fixed before the NBS can be removed from the archive. This is the case for illuminator, whose rebuild stops with this error:

```
checking for PetscPrintf in -lpetsc... no
configure: error: "PETSc libraries not found"
make: *** [stamp-configure] Error 1
dpkg-buildpackage: failure: debian/rules build gave error exit status 2
```

In this case, we need to fix the error related with missing PETSc libraries, update the changelog and try a test build again.

## Remarks

* Once reverse dependencies from the NBS list are zeroed, announcing it on #ubuntu-devel would be greatly appreciated, so that an archive-admin can remove the NBS.
* Sometimes one NBS package will depend on another, which can confuse a transition.
* In case a package has an alternate dependency, it will still show (but doesn't always need fixing).
* Remember that NBS removals are manual, which can confuse the results. 

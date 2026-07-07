(how-to-package-llvm)=
# How to package LLVM

This article provides a guide for understanding how the LLVM toolchain is packaged for Ubuntu.


## Setting up

Ubuntu's LLVM packages follow Debian as closely as is reasonable. To simplify that process, maintainers typically use {ref}`git-ubuntu` rather than a separate, dedicated repository.

As an example, if you are planning to work on LLVM version 22, you would clone that package directly.

```none
$ git ubuntu clone llvm-toolchain-22
```


(understanding-the-common-llvm-packages)=
### Understanding the common LLVM packages

LLVM packages are versioned (i.e., the major version is appended to the package name), but Debian maintainers have made an effort to avoid some duplication across versions using the notion of {ref}`common packages <what-are-llvm-common-packages>`, and are listed in the repository in `debian/packages.common`. These packages are generally considered ABI-stable, and so can be shared among all versions of LLVM in the archive.

In Debian, the latest version of LLVM in the archive is used to build the common libraries without the version info appended. Consider Resolute as an example: while the `llvm-toolchain-22` source package produces a versioned `libllvm22` binary package, because it is the most recent version available at the time of writing it also produces an unversioned `libc++1` binary package, one of the common packages. Each of the earlier versions in the Resolute archive then depend on that. For example, `libc++-19-dev` depends on `libc++1`.

The way the package treats the common packages can be configured in `debian/rules` using two variables: `SKIP_COMMON_PACKAGES` and `NEW_LLVM_VERSION`.

`SKIP_COMMON_PACKAGES`
: When set to `no`, the package builds the common packages. When set to `yes`, building them is skipped. If you skip the common packages, you must then set `NEW_LLVM_VERSION` to teach the package what to depend on.

`NEW_LLVM_VERSION`
: Set this to the major LLVM version number of the package that builds the common package.

For example, when working on a fix for LLVM 19 on Resolute, where LLVM 22 is the newest in the archive and the default, set `SKIP_COMMON_PACKAGES=yes` and `NEW_LLVM_VERSION=22`.


### Regenerating the control file

The LLVM package uses many templated configuration files, generally named with a `.in` suffix. This includes `debian/control.in`, which you will likely need to tweak frequently. However, because we track `debian/control` in git, unlike some other generated files, we always need to re-generate the control file whenever we make a change.

However, since the Debian maintainers also maintain infrastructure for LLVM upstream, the package that Ubuntu inherits is set up for some CI/CD systems we do not use and generating this file is a bit unintuitive. The easiest way is to set variables to pretend to be that CI/CD system. You can do that with `APT_LLVM_ORG=yes`. You should also set the `DISTRO` flag, which can sometimes affect package dependencies. So, if you are building a package for Resolute and need to generate the control file, you can do that as follows.

```none
$ debian/rules stamps/preconfigure APT_LLVM_ORG=yes DISTRO=resolute

$ git clean -fd   # to remove the other generated files not tracked in git
```


## Fixing or updating an existing LLVM version

When shipping a new patch release for an existing LLVM package, or fixing a bug in an existing package, it's generally important to try to minimize the diff from the existing package. Because of that, any required fixes should typically be cherry-picked into the existing git-ubuntu source tree rather than wholesale bringing in the latest packaging from Debian.

The steps are generally similar to any other Ubuntu package and so some details are omitted. For more information of making changes to a package, see {ref}`how-to-make-changes-to-a-package`.

1. Ensure that you set the common package variables in `debian/rules` appropriately.
1. Make your fix, or unpack the new upstream LLVM source code using `uupdate`.
1. Build the source package using `dpkg-buildpackage`, `debuild`, or `sbuild`. Usually something like `dpkg-buildpackage -S -nc -sa` is good enough.
1. Lint the source package by running `lintian` on the `.dsc` file.
1. Build the binary package with `sbuild`.
1. Lint the debs by pointing `lintian` at them.
1. Run the autopkgtests with the LXD backend, i.e. `autopkgtest . --shell-fail -- lxd autopkgtest/ubuntu/resolute/amd64`. If you need the image, run `autopkgtest-build-lxd ubuntu:resolute` or use the `daily:` remote for devel.
1. Assuming success, push the source package to a PPA with `dput`.


## Backporting a new version of LLVM to a stable Ubuntu

This is often the most complex of the packaging tasks that Ubuntu LLVM maintainers perform regularly. The reason is that the entire architecture of the package is designed for the common package workflow, discussed above. However, consider what happens if you backport LLVM version X+1 to a stable LTS Ubuntu series with a default LLVM version of X.

According to how the common packages work, we should be building the shared libraries with the most recent version of the package. However, the new backport is the most recent version, and not every user will have access to backports. Moreover, changing the libraries away from being provided by the default LLVM version might be problematic for some users—backports are intended to be standalone applications which can be safely updated without impacting the rest of the system.

We also do not really have the option of setting `NEW_LLVM_VERSION=<X>` for version X+1, as the libraries' backwards compatibility does not imply forward compatibility.

That leaves us with the requirement that we ship backports that are entirely standalone and sandboxed. That means Ubuntu maintainers will need to actually restore the versioned binary outputs for the common packages which Debian explicitly removed. That means, e.g., `llvm-toolchain-22` backported to an older LTS will likely ship `libc++1-22`.

There a number of steps you will need to go through, which will vary slightly for every version. At a high level, they are as follows:

- Ensuring `SKIP_COMMON_PACKAGES` is *always* set to `no`, so we always build everything.
- Modifying `debian/rules`, so that when `dh_makeshlibs` is invoked, the major version is appended.
- Modifying `control.in` to restore the versioned packages and ensure you regenerate `control`.
- Renaming `.install.in`, `.links.in`, and `.lintian-overrides.in` files so that the names match the new package names in `control`.
- Ensuring that all of the files in `.install.in` and `.links.in` files are not in potentially conflicting global directories. Generally, a backported LLVM package should just install files into a versioned directory like `usr/lib/llvm-@LLVM_VERSION@/lib/` and not put anything, including symlinks, in the global multiarch directory. The version of clang that you will build from this package will know how to find its own libraries, which is all we need.

  It's good practice to also make the python libraries co-installable by not installing those files in the global python `site-packages` directory. Users can adjust their `PYTHON_PATH` if they absolutely need to make use of the backported Python libraries.
- Updating `.gitignore` as needed for file renames.


(bootstrapping-the-backport)=
### Bootstrapping the backport

It's quite likely that you'll need to bootstrap your backport, due to some {ref}`circular dependencies <llvm-circular-dependencies>`. This process is tedious, but not difficult.

First, build LLVM using the `stage1` [build profile](https://wiki.debian.org/BuildProfileSpec). Unfortunately, while the `dpkg` tooling supports this natively, Launchpad does not. That means that you currently can't specify the type of build you want and upload it to a PPA. Instead, you need to hardcode that profile to make its configuration the default. That is, remove dependencies from the `control` file that are marked as `<!stage1>` and so on.

We have an experimental script to do this on your behalf, which is currently available only upon request until it stabilizes. Reach out to maintainers on Ubuntu's matrix channels.

After you build your `stage1` version of LLVM, build the circular dependencies to match. Depending on your version of LLVM, that is likely to include `spirv-llvm-translator-XY`, `spirv-headers`, and `spirv-tools`. You can generally backport the versions that are in the archive from which you're backporting LLVM itself.

Once you have the `stage1` compiler, and those 3 packages together in a PPA, use that PPA to start doing full builds of LLVM. To use them locally, have `sbuild` inject the PPA as a source. The simplest, but not very secure way to do this, is as follows. (Handling the signing correctly is out of scope here.) Do not use this insecure approach outside of a sandboxed build with no access to your system.

```none
$ sbuild -d noble --extra-repository="deb [trusted=yes] http://ppa.launchpadcontent.net/gcc-llvm-toolchains/llvm-staging/ubuntu noble main"
```

The PPA itself automatically picks up its own dependencies, but if you want to use several, configure them to depend on one another as necessary.


### New major LLVM releases

Usually, new versions of LLVM are first produced by Debian maintainers. The process is not significantly different from {ref}`bootstrapping-the-backport`. Start with the code available on [Debian Salsa](https://salsa.debian.org/pkg-llvm-team/llvm-toolchain). To create new packages corresponding to the circular dependencies, get them from Salsa in the following repositories:

- https://salsa.debian.org/xorg-team/vulkan/spirv-tools
- https://salsa.debian.org/xorg-team/vulkan/spirv-headers
- https://salsa.debian.org/opencl-team/spirv-llvm-translator

The final `spirv-llvm-translator` package can be tricky to build, as the upstream Debian package definition doesn't always build cleanly on Ubuntu. For example, you might need to adjust the version of GCC it requires, which in turn breaks the symbols file included with the package. You have to fix these things as you would in any other package. For that specific problem, reference the [Debian documentation on symbols files](https://wiki.debian.org/UsingSymbolsFiles). Depending on the application, it may also be appropriate to relax the symbol checking.

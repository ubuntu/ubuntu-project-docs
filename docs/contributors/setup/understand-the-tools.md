(understand-the-tools)=
# Understand the tools

The ecosystem of Debian packaging tools is big and diverse, with a great deal of overlap and intended deprecation.
This section introduces some of the most common tools used to generate Ubuntu packages.
A much more comprehensive reference is available in [the Debian developers-reference](https://www.debian.org/doc/manuals/developers-reference/tools.en.html).

There are, roughly speaking, three phases to creating a `.deb` package.

1. Create the source package.
2. Build the binary package from the source package.
3. Test and upload the binary package.

Although coarse, keeping this in mind can help build a more coherent mental model of how the tools interoperate.

## Tools for working on the source package

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

## Tools for building the binary package from the source package

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


## Tools for working with the compiled binary package

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

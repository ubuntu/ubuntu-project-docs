(ubuntu-development)=
# Ubuntu development

```{note}
[Page source](https://wiki.ubuntu.com/UbuntuDevelopment)

TODO: This page could probably be broken up and used as overview/intros for many
of our landing pages.
```
	
## Overview of development

The development of Ubuntu is transparent to the public, and open to any
contributor with the necessary skills and commitment to the project.

Ubuntu is based on [Debian](http://www.debian.org/), sharing many packages,
tools and techniques with that project. Like most operating systems, Ubuntu is
complex, and it can help to get a broad overview
[of its architecture first](https://wiki.ubuntu.com/UbuntuArchitecture).

Ubuntu is [periodically released](https://wiki.ubuntu.com/UbuntuDevelopment/ReleaseProcess)
according to a set schedule.

If you have been directed to this page for advice on contributing to Ubuntu as
a developer, you may also be interested in
[Contribute To Ubuntu](https://wiki.ubuntu.com/ContributeToUbuntu).


## Working with other developers

You are not alone! Ubuntu is the work of many developers, and we devote our
efforts to enabling efficient collaboration with tools, infrastructure,
governance and a cooperative spirit.


### Starting points

{ref}`ubuntu-developers` explains the roles of developers in the Ubuntu project
and how to join the teams.

If you are brand new to Ubuntu development and need to install the development
tool set, or need step by step reminder on how to, check out the
[Ubuntu Beginner Developers' Tools Installation Quick Start](https://wiki.ubuntu.com/BeginnersTeam/FocusGroups/Development/Devbeginnings)

If you're looking for tasks which need doing, many of those are tracked in the
bug tracking system. The {ref}`bug-squad` maintains several lists of them at
[Bugs/Tags](https://wiki.ubuntu.com/Bugs/Tags).

If you already have experience working with Debian packages, most of your
knowledge applies equally well to Ubuntu packaging. If you are a Debian developer,
[Ubuntu For Debian Developers](https://wiki.ubuntu.com/UbuntuForDebianDevelopers)
summarizes the differences between the projects, and later sections in this
document provide details of our infrastructure.

To submit patches for review or to help reviewing patches, refer to
[the Code Review process](https://wiki.ubuntu.com/UbuntuDevelopment/CodeReviews).

To find the developer responsible for the component you're working on, see
[Developer Responsibilities](https://wiki.ubuntu.com/DeveloperResponsibilities).


### Communication

Email discussion among Ubuntu developers takes place on the
[`ubuntu-devel` mailing list](http://lists.ubuntu.com/mailman/listinfo/ubuntu-devel),
which is moderated (excepting registered Ubuntu developers). The
[`ubuntu-devel-discuss` mailing list](http://lists.ubuntu.com/mailman/listinfo/ubuntu-devel-discuss)
is available for open discussion about Ubuntu development (not for
[reporting bugs](https://help.ubuntu.com/community/ReportingBugs#Reporting_non-crash_hardware_and_desktop_application_bugs)
or [user support](http://www.ubuntu.com/support)). All
{ref}`ubuntu-developers` should subscribe to the
[`ubuntu-devel-announce` mailing list](http://lists.ubuntu.com/mailman/listinfo/ubuntu-devel-announce),
where important development events are announced.
[Various other mailing lists](https://lists.ubuntu.com/mailman/listinfo/) are
available, some of which focus on specific areas of development.

The `#ubuntu-devel` channel on Matrix is home to many Ubuntu developers for
real-time communication. [Automated notifications of development activity](https://wiki.ubuntu.com/UbuntuDevelopment/PackageArchive#Notification)
are also useful for keeping up with what other developers are working on.

A comprehensive matrix of communication channels can be found on
[Developer Communication](https://wiki.ubuntu.com/DeveloperCommunication).


### Bugs and the Bug Squad

[Ubuntu bug reports](http://bugs.launchpad.net/ubuntu) are tracked in Launchpad.
[Helping with bugs](https://wiki.ubuntu.com/HelpingWithBugs) contains information
about how they are handled. The {ref}`bug-squad` documentation describes how to
cooperate with other developers and volunteers working on bug triage; it is
required reading for new developers, as developers will typically need to spend
a significant amount of time working with the bug tracking system.

The Bug Squad (and the {ref}`Ubuntu Bug Control team <bug-control-team>`, which
is comprised of more experienced triagers who can prioritize bugs) are here to
help you as a developer. If you are responsible for a non-trivial number of bugs,
it is a good idea to spend some time helping them to help you. A useful starting
point is to add specific information about your packages to
[Debugging Procedures](https://wiki.ubuntu.com/DebuggingProcedures): this may
include both special tricks for debugging them effectively and any particular
policy you have on how you want your bugs to be handled (e.g. assignment, tags,
etc.). When adding significant chunks of new information to Debugging Procedures,
please send a note to `ubuntu-bugsquad@lists.ubuntu.com` about it.

Members of the Bug Squad can be found on the `#ubuntu-devel` channel on Matrix.
There is also the [`ubuntu-bugsquad` mailing list](https://lists.ubuntu.com/mailman/listinfo/ubuntu-bugsquad)
for general discussion regarding bugs and bug triaging.


### Papercuts

[Papercuts](https://wiki.ubuntu.com/One%20Hundred%20Papercuts) are trivial-to-fix
but annoying bugs. Ideal for getting started helping with bugs.


### Release-critical bugs

[RC Bug Targeting](https://wiki.ubuntu.com/RCBugTargetting) documents the
intended use of the various facilities of the bug tracking system to track
release-critical bugs.

[Showstopper bugs](https://bugs.launchpad.net/ubuntu/+bugs?field.searchtext=&orderby=-importance&search=Search&field.status%3Alist=Unconfirmed&field.status%3Alist=Needs+Info&field.status%3Alist=Confirmed&field.status%3Alist=In+Progress&field.status%3Alist=Fix+Committed&field.importance%3Alist=Critical&assignee_option=any&field.assignee=&field.bug_reporter=&field.bug_contact=&field.milestone%3Alist=50164&field.component=1&field.component=2&field.component-empty-marker=1&field.status_upstream=&field.status_upstream-empty-marker=1&field.omit_dupes.used=&field.omit_dupes=on&field.has_patch.used=&field.tag=&field.has_cve.used=&field.has_no_package.used=)
: Critical and milestoned to the relevant release. These bugs will hold up the
  release if not fixed.  

[Release-critical bugs](https://bugs.launchpad.net/ubuntu/+bugs?field.searchtext=&orderby=-importance&field.importance%3Alist=CRITICAL&field.importance%3Alist=HIGH&field.milestone%3Alist=50160&field.milestone%3Alist=50161&field.milestone%3Alist=50162&field.milestone%3Alist=50163&field.milestone%3Alist=50164) 
: Critical and high importance bugs milestoned to the relevant release. Those
  bugs need to be fixed or worked around/documented before the release.

In particular, if you make a temporary change to a package for whatever reason
which should be reverted before release, please file a release-critical bug
about it so that this can be tracked by the release team.


## The release process

Ubuntu does time-based releases. The [Release Process](https://wiki.ubuntu.com/UbuntuDevelopment/ReleaseProcess)
section covers all the release management steps such as beginning a new release,
planning it, merging with upstream, feature development, stabilization and
freezes, milestone, finalization and stable releases.


## Packaging

If you're interested in packaging work, but don't have much experience yet, you
should read [the MOTU getting started guide](https://wiki.ubuntu.com/MOTU/GettingStarted)
to get involved in the [MOTU](https://wiki.ubuntu.com/MOTU) team.


### Working with Debian-format packages

Ubuntu uses the Debian packaging format. The following resources explain how to
create and modify Debian-format packages.

* If you are already familiar with Debian development,
  [Ubuntu for Debian Developers](https://wiki.ubuntu.com/UbuntuForDebianDevelopers)
  explains some of the differences between the projects.

* All Ubuntu developers should be familiar with the
  `Ubuntu Policy Manual: http://people.ubuntu.com/~cjwatson/ubuntu-policy/policy.html/`
  (derived from the [Debian Policy Manual](http://www.debian.org/doc/debian-policy/)).

  **TODO: link is broken**
  
* All Ubuntu developers should be familiar with the
  [Debian New Maintainer Guide](http://www.debian.org/doc/maint-guide/); though
  be aware that there are many differences (technical, social and procedural)
  between Ubuntu and Debian of which they must also be aware.

* [A packaging tutorial](http://wiki.debian.org/PackagingTutorial) is available
  from the Debian Wiki, as is
  [an explanation of maintainer scripts](http://wiki.debian.org/MaintainerScripts)
  and [further help with building packages](http://wiki.debian.org/AdvancedBuildingTips).

* Many packages use tools to help manage multiple patches.
  {ref}`Patching Ubuntu packages <patching>` explains how to work with them.

  * The `CDBS Manual: https://perso.duckcorp.org/duck/cdbs-doc/cdbs-doc.xhtml`
    explains how to work with packages using the CDBS packaging scripts, one
    example of a patch system (and more).
    
    **TODO: link is broken**

* Packaging shared libraries is a delicate task, and getting it wrong can cause
  upgrade headaches for users. The [Debian Library Packaging Guide](http://www.netfort.gr.jp/~dancer/column/libpkg-guide/libpkg-guide.html)
  can be useful in avoiding some of the common traps.

* For a deeper understanding of the packaging process, you might want to have a
  look at [Debian wiki: building without helper](http://wiki.debian.org/Courses2005/BuildingWithoutHelper)

* [How to write watch files](https://lists.ubuntu.com/archives/ubuntu-motu/2006-February/000443.html)
  for `sourceforge.net`-hosted projects.


### Working with Ubuntu packages

* Set the target suite in `debian/changelog` to be the code name of the current
  development branch, e.g. `dch -D zesty`.

* When working with a package which originated in Debian, use a version number
  derived from the Debian version number with `ubuntu\<revision\>` appended. e.g.
  Debian `1.0-2` becomes `1.0-2ubuntu1`, followed by `1.0-2ubuntu2`, etc.

* When fixing a bug tracked in Launchpad, be sure to insert `LP: #xxxxxx`
  notation in your changelog entry, for example:

  ```none
  mypackage (2.2-2) zesty; urgency=low

  * hello(1) now prints "Hello, world!" instead of "Hello yourself." (LP: #500000)

   -- A. Developer <adeveloper@ubuntu.com> Mon, 17 Dec 2007 18:27:50 +0000
  ```

  Note: The regex in Launchpad looks for `LP: #xxxxxx` at a minimum. The
  preferred form is `(LP: #xxxxxx)`.

* When creating a new package that may later be added to Debian, use a revision
  of the form `-0ubuntu1`.

* Remember to include the `orig.tar.gz` if this is a new upstream version of a
  non-native package but you have already patched it before upload. A missing
  original tarball may cause the upload to be rejected or silently dropped. Use
  `dpkg-buildpackage -S -sa` to generate such an upload. If the `orig.tar.gz` is
  already in the distribution then you don't need to upload it again.

* Always be aware of the release schedule and any applicable {ref}`freezes`. The
  cooperation of all developers is needed to ensure a successful release!

* If your changes may affect the work of other developers, it is a good idea to
  discuss the changes on a mailing list first.

* For merging a Ubuntu package with a newer Debian version, see
  [Merging](https://wiki.ubuntu.com/UbuntuDevelopment/Merging).


### Revision control (Bazaar)

Bazaar, an open source revision control system and Canonical sponsored project,
is the preferred revision control system in Ubuntu. Many Ubuntu packages are
[maintained in Bazaar](https://wiki.ubuntu.com/BzrMaintainerHowto), which makes
it easy for other developers to [contribute changes to them](https://wiki.ubuntu.com/BzrContributorHowto),
which can be easily merged by the maintainer.

Note that, as a practical matter, many packages are not yet maintained in Bazaar,
but in other revision control systems or none on a case-by-case basis.
[Work is underway](https://wiki.ubuntu.com/DistributedDevelopment) to rectify
this. Where no revision control system is used, the history of uploads recorded
in [Launchpad](https://launchpad.net/ubuntu/+search) may be useful.


### Ubuntu Flavors and derivative distributions

The Ubuntu project produces several distributions each release cycle. These are
sometimes called "Flavours". Kubuntu, Edubuntu, and Xubuntu are all maintained
directly in the Ubuntu Archive. There are also a large number of derivative
distributions that are based on the Ubuntu Archive, but separately developed.

* [Kubuntu Packaging Guide](https://wiki.ubuntu.com/KubuntuPackagingGuide)


### Upstream

"Upstream" is the term used to describe all the places where Ubuntu pulls its
software from. The developers of this software write it and then it flows
downstream in to Ubuntu and then in to its derivatives.

See [Why upstream?](http://distributions.freedesktop.org/wiki/Packaging/WhyUpstream)
for why upstream is so important, and some tips on working with upstream to
improve the software, and hence Ubuntu.

There is one upstream that is critical to Ubuntu: [Debian](https://wiki.ubuntu.com/Debian).
This is where most of the packages in Ubuntu come from, and so working with
them is important.


### Building

You should always build and test packages locally before submitting them to
Ubuntu. Failure to do so will waste the time of other members of the community,
so please be considerate.

* You may want to build them in a [`debootstrap chroot`](https://wiki.ubuntu.com/DebootstrapChroot)
  or in [`pbuilder`](https://wiki.ubuntu.com/PbuilderHowto).
  [Using Development Releases](https://wiki.ubuntu.com/UsingDevelopmentReleases)
  explains how to safely work and test on the current development release.

* Backports are explained at [Ubuntu Backports](https://wiki.ubuntu.com/UbuntuBackports)


### Tools

[Ubuntu Developers' Tools Installation Quick Start](https://wiki.ubuntu.com/BeginnersTeam/FocusGroups/Development/Devbeginnings)

You will find some tools explained in the {ref}`how-to-contribute`, also from
Gutsy on, you will find `ubuntu-dev-tools` in the Archive, which contains
[tools for developing Ubuntu](https://wiki.ubuntu.com/UbuntuDevTools).


### New packages

The process for either requesting a new package or getting your own new package
included in Ubuntu is described at {ref}`new-packages`.


## The Package Archive

All current official Ubuntu packages are stored in the primary Package Archive,
which is widely {ref}`mirrored <mirrors>`. It is administered by the
{ref}`archive-administration` team. The {ref}`Packaging Archive section <the-package-archive>`
covers details such as interactions with the build daemons and the Archive. It
also explains how different architectures and package components are handled and
how the autobuilders work.


## Installation media

The [Installation media](https://wiki.ubuntu.com/UbuntuDevelopment/InstallationMedia)
section discusses the different supported installation media types, how to obtain
them and contains pointers to Installer development.


## Language packs: internationalisation and localisation

We do not ship upstream translations from source packages directly in binary
application packages in `main` and `restricted`, since this does not allow us
any flexibility to edit them in a central place (Launchpad), update them
independently from the applications, and update them post-release. That is why
we separate packages and their translations in Ubuntu and maintain/package them
independently.

The complete lifecycle of translations (import, maintenance, export, and language
pack structure) is described in
[Translation Lifecycle](https://wiki.ubuntu.com/TranslationLifecycle).

The main article is at [Internationalisation Guide for Developers](https://wiki.ubuntu.com/UbuntuDevelopment/Internationalisation)


## Other Resources

These resources should be incorporated into new or existing sections elsewhere
in this document, but are temporarily recorded here so that we remember to come
back to them later:

* Debian Python Policy: [http://www.debian.org/doc/packaging-manuals/python-policy/](http://www.debian.org/doc/packaging-manuals/python-policy/)



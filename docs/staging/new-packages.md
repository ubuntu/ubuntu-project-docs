(new-packages)=
# New packages

```{note}
This content comes [from the wiki](https://wiki.ubuntu.com/UbuntuDevelopment/NewPackages)
It has not yet been reviewed for currency or accuracy.
Last updated: 2025
```

## Criteria

In order for a piece of software to be included in Ubuntu, it must meet the
[Ubuntu License Policy](https://help.ubuntu.com/community/License).

## Requesting a new package for Ubuntu

Packages that have recently been added to Debian unstable will be automatically
synced into Ubuntu prior to the
[Debian Import Freeze (DIF)](https://wiki.ubuntu.com/DebianImportFreeze).
After the Debian Import Freeze, you will have to
[file a bug](https://launchpad.net/ubuntu/+filebug/?no-redirect) with the
summary field "Please sync `<packagename>` from debian `<distro>`" where
`<packagename>` is the package you would like to see. Find the date for Debian
Import Freeze on
[the release schedule page](https://wiki.ubuntu.com/ReleaseSchedule).

To get a package into Ubuntu, please
[file a bug in Launchpad](https://bugs.launchpad.net/ubuntu/+filebug?no-redirect&field.tag=needs-packaging)
and make sure it has the tag [`needs-packaging`](https://lists.ubuntu.com/archives/ubuntu-motu/2007-March/001471.html).
Please mention where to get the source for it and which license it is under. An
example request [is shown here](https://wiki.ubuntu.com/UbuntuDevelopment/NewPackages/ExamplePackageRequest).
Make sure you check which [packages have already been requested](https://launchpad.net/ubuntu/+bugs?field.tag=needs-packaging). 

Because we want Free Software to reach as many people as possible and do not
want to have too much duplication of packaging effort, it is useful for packages
that meet the requirements of the
[Debian Free Software Guidelines](http://www.debian.org/social_contract#guidelines)
to be requested within Debian's
[Work-Needing and Prospective Packages](http://www.debian.org/devel/wnpp/)
(WNPP) process by filing a Request for Package (RFP) bug on the WNPP package in
Debian's bug tracker.

If you file a `needs-packaging` bug, please link it to the Debian WNPP bug as
well.

## Packaging it yourself

You can follow the [Packaging Guide directives](http://packaging.ubuntu.com/html/).

To get a screenshot included for software-center, please use http://screenshots.debian.net/upload

### NEW packages through Debian

Ubuntu regularly incorporates source packages from Debian, so it is encouraged
to upload a package to Debian first to automatically have it in Ubuntu in due
time. In addition to that, your package will reach a much broader audience if
it is in Debian and all of its derivatives.

In order to have faster reviews, several teams have been set up to manage a
given subset of packages. Some of them are:

* [Debian GNOME Team](http://wiki.debian.org/Teams/DebianGnome)
* [Debian KDE Team](https://salsa.debian.org/qt-kde-team/)
* [Debian XFCE Group](http://wiki.debian.org/Teams/DebianXfceGroup)
* [Debian Games Team](http://wiki.debian.org/Games/Team)
* [Debian Multimedia](http://wiki.debian.org/DebianMultimedia)
* [Debian Perl Group](http://wiki.debian.org/Teams/DebianPerlGroup)
* [Debian Python Modules Team](http://wiki.debian.org/Teams/PythonModulesTeam)
* [Debian Python Applications Packaging Team](http://wiki.debian.org/Teams/PythonAppsPackagingTeam)
* [Debian CLI Applications Team](http://wiki.debian.org/Teams/DebianCliAppsTeam)
* [Debian Mozilla Extension Team](https://wiki.debian.org/Teams/DebianWebextensionTeam)
* [Debian X Team](https://salsa.debian.org/xorg-team)

More teams [can be found here](http://wiki.debian.org/Teams). If there is no
team available that takes care of the group of packages you are interested in,
contact the Debian mentors (see "Further Reading" below).

Ubuntu does virtually all package maintenance in teams. If your package is
related to any of the existing teams within Debian, work with that team to get
the package uploaded to Debian. If there is no team already, you should consider
starting a new team within Debian (e.g. at Alioth) for any package that is
likely to have a significant number of bugs or other maintenance overheads
(like architecture-specific issues).

Additionally there are roughly an order of magnitude more Debian Developers
than Ubuntu developers. It is quite difficult to get a new package into Ubuntu
due to the sheer volume of requests compared to the available resources for
reviews. In many cases, people have an easier time getting their package into
Ubuntu via Debian than directly.

If you choose to do this, file an [Intent to Package (ITP)](http://www.debian.org/devel/wnpp/being_packaged)
bug on the WNPP package in Debian to let others know that you're working on it
(`reportbug -B debian wnpp` should do the right thing), then go through the
[Debian Mentors](http://mentors.debian.net/) to get the package
uploaded. A number of Ubuntu Developers are also Debian Maintainers or Debian
Developers, so they may be able to help you navigate Ubuntu/Debian interactions.

```{admonition} Some good tips
:class: tip
* [Follow the procedures](http://www.debian.org/doc/manuals/developers-reference/pkgs.html#newpackage)
  to get a [new package into Debian](http://ftp-master.debian.org/new.html).
* Subscribe to bugs of the package once it is accepted.
```

### Going through MOTU

Submitting new packages through Debian is the preferred path. But, if your
package is Ubuntu-specific or can't go into Debian for some other reason, you
can submit it directly to MOTU. There are a limited number of available
reviewers, so you may encounter delays here.

New packages require extra scrutiny and go through a special review process,
before they get uploaded and get a final review by the [Archive Admins](http://launchpad.net/~ubuntu-archive).
More information on the review process, including the criteria that will be
applied, can be found on the [Code Reviewers page](https://wiki.ubuntu.com/UbuntuDevelopment/CodeReviews#NewPackage).
Developers are encouraged to examine their own packages using these guidelines
prior to submitting them for review.

To receive higher quality bug reports write an
[apport hook](https://wiki.ubuntu.com/Apport#Per-package_Apport_Hooks) for your package.

The [MOTU](https://wiki.ubuntu.com/MOTU) team approval policy for new packages:

* New MOTU contributors (who are not [members of the MOTU team](https://launchpad.net/~motu)
  yet), need to get their packages reviewed and signed off by two
  [MOTUs (core-devs are included in this)](https://launchpad.net/~motu/+members)
  to get them uploaded to Ubuntu.

* MOTUs can upload new packages directly to the archive. However they are
  greatly encouraged to have a new package reviewed prior to uploading.
  (cf. [MOTU/Council/Meetings/2007-02-23](https://wiki.ubuntu.com/MOTU/Council/Meetings/2007-02-23))

The MOTU team uses the following workflow:

* Join the `#ubuntu-devel` channel on `irc.libera.chat` and talk with the MOTU.
  It's good to do this early on, to get advice on how to package (avoid common
  mistakes), to find out if your package is likely to be accepted (before you
  invest a lot of work in packaging it), and to find mentors willing to sponsor
  your package or to point you in the right direction.

* When you start to work on a new package, assign the `needs-packaging` bug to
  yourself and set it to "In Progress" (if there is no `needs-packaging` bug,
  [file one](http://bugs.launchpad.net/ubuntu/+filebug)).

* Once you have an initial package, follow the
  {external:doc}`new packaging instructions <tutorial/create-new-package>`
  to upload it to your PPA or a Launchpad branch, then add a link to the package
  in the description of the bug. Requests for changes or other communication
  about your package will be made as comments on your bug. Subscribing
  `ubuntu-sponsors` to sponsorship requests is generally advised, as it makes
  the request appear on the list that people look at.

* Once the approved package is uploaded, the uploading MOTU will set the bug
  status to "Fix Committed".

* When the package clears the NEW queue it will automatically be set to "Fix
  Released" (`debian/changelog` must close the `needs-packaging` bug). This is
  done with a bullet point that follows the format:

  * `Initial release (LP: #242910)`
 
  where "LP" refers to "Launchpad". See the Packaging Guide for
  [more information on changelogs](https://wiki.ubuntu.com/PackagingGuide/Howtos/PackagingFromScratchHelloChangelog).

* Even if you don't run Debian as your primary OS, most packaging can be tested
  perfectly well in a chroot, or failing that in a VM (and most packages will
  work fine without any changes anyway).
  (→ [Using Development Releases](https://wiki.ubuntu.com/UsingDevelopmentReleases))

* `#debian-ubuntu` on OFTC and the
  [debian-derivatives mailing list](http://lists.debian.org/debian-derivatives/)
  are good places for Ubuntu developers to ask their questions.


### Deadline

[Feature Freeze](https://wiki.ubuntu.com/FeatureFreeze) is the latest approval
date, it is recommended to get things done in a couple of weeks earlier, as
getting approval may take some time.


## Further reading

* Always check if there is an {term}`Intent to Package (ITP) <ITP>`
  [bug filed against the WNPP package](https://bugs.debian.org/cgi-bin/pkgreport.cgi?pkg=wnpp;dist=unstable) in Debian.
  That means, somebody is already working on packaging the software for Debian.
  Join forces with them rather than reinventing the wheel.

* [mentors.debian.net](http://mentors.debian.net/), a website where people
  interested in getting their packages into Debian can upload their packages.
  You need to [browse the directories](http://mentors.debian.net/debian/pool/)
  to find packages. [Contributing To Debian](https://wiki.ubuntu.com/ContributingToDebian)
  has additional information on getting your work into Debian.
  (→ [Debian Mentors FAQ](http://wiki.debian.org/DebianMentorsFaq))

* [Debian's SCM](https://salsa.debian.org/) -- it's possible that a package has
  been worked on for Debian but has a status of UNRELEASED. Check the
  appropriate directories that begin with "pkg" that your package may fall
  under. For example, game packages would be under "pkg-games".
  [The Debian Package Tracking System](http://packages.qa.debian.org/common/index.html)
  will help you find the specific branch where the package is being maintained.


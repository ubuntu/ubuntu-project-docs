(new-packages)=
# New packages

For a piece of software to be included in Ubuntu, it must meet the [Ubuntu License Policy](https://help.ubuntu.com/community/License).


## Requesting a new package for Ubuntu

Packages that have recently been added to Debian unstable will be automatically synced into Ubuntu prior to the {ref}`debian-import-freeze` (DIF). Once synced, they will follow the {ref}`proposed-migration flow <proposed-migration>`.
If instead the release process already reached the Debian Import Freeze, you must [file a bug](https://launchpad.net/ubuntu/+filebug/?no-redirect) with the summary field "Please sync `<packagename>` from debian `<distro>`" where
`<packagename>` is the package you would like to see.

To get a package into Ubuntu, [file a bug in Launchpad](https://bugs.launchpad.net/ubuntu/+filebug?no-redirect&field.tag=needs-packaging) and make sure it has the tag [`needs-packaging`](https://lists.ubuntu.com/archives/ubuntu-motu/2007-March/001471.html).

In the bug, mention where to get the source for it and which license it is under.
An example request [is shown here](https://wiki.ubuntu.com/UbuntuDevelopment/NewPackages/ExamplePackageRequest).
Make sure you check which [packages have already been requested](https://launchpad.net/ubuntu/+bugs?field.tag=needs-packaging). 

Since we want Free Software to reach as many people as possible and do not want too much duplication of packaging effort, it is useful for packages that meet the requirements of the [Debian Free Software Guidelines](https://www.debian.org/social_contract) to be requested within Debian's [Work-Needing and Prospective Packages](https://www.debian.org/devel/wnpp/) (WNPP) process by filing a Request for Package (RFP) bug on the WNPP package in Debian's bug tracker.

If you file a `needs-packaging` bug, please link it to the Debian WNPP bug as well.


## Packaging it yourself

If you want to try packaging it yourself, refer to our guide on {ref}`how-to-create-a-new-package`.


### NEW packages through Debian

Ubuntu regularly incorporates source packages from Debian, so it is encouraged to upload a package to Debian first.
Your package will reach a much broader audience if it is in Debian and all of its derivatives.

To have faster reviews, several teams have been set up to manage subsets of packages, including:

* [Debian GNOME Team](https://wiki.debian.org/Teams/DebianGnome)
* [Debian KDE Team](https://salsa.debian.org/qt-kde-team/)
* [Debian XFCE Group](https://wiki.debian.org/Teams/DebianXfceGroup)
* [Debian Games Team](https://wiki.debian.org/Teams/Games)
* [Debian Multimedia](https://wiki.debian.org/DebianMultimedia)
* [Debian Perl Group](https://wiki.debian.org/Teams/DebianPerlGroup)
* [Debian Python Modules Team](https://wiki.debian.org/Teams/PythonTeam)
* [Debian Python Applications Packaging Team](https://wiki.debian.org/Teams/PythonTeam)
* [Debian CLI Applications Team](https://wiki.debian.org/Teams/DebianCliAppsTeam)
* [Debian Mozilla Extension Team](https://wiki.debian.org/Teams/DebianWebextensionTeam)
* [Debian X Team](https://salsa.debian.org/xorg-team)

[See the full list of teams](https://wiki.debian.org/Teams).
If there is no team available that takes care of the group of packages you are interested in, contact the Debian mentors (see "Further Reading" below).

Ubuntu does virtually all package maintenance in teams.
If your package is related to any of the existing teams within Debian, work with that team to get the package uploaded to Debian.
If there is no team already, consider starting a new team within Debian (e.g. at Alioth) for any package that is likely to have a significant number of bugs or other maintenance overheads (like architecture-specific issues).

Additionally, there are roughly an order of magnitude more Debian Developers than Ubuntu Developers.
It is comparably more difficult to get a new package into Ubuntu due to the sheer volume of requests compared to the available resources for reviews.
In many cases, people have an easier time getting their package into Ubuntu via Debian than doing so directly.

If you choose to do this, file an [Intent to Package (ITP)](https://www.debian.org/devel/wnpp/being_packaged) bug on the WNPP package in Debian to let others know you're working on it (`reportbug -B debian wnpp` should do the right thing).
Then, go through the [Debian Mentors](https://mentors.debian.net/) to get the package uploaded.
A number of Ubuntu Developers are also Debian Maintainers or Debian Developers, so they may be able to help you navigate Ubuntu/Debian interactions.

```{admonition} Some good tips
:class: tip
* [Follow the procedures](https://www.debian.org/doc/manuals/developers-reference/pkgs.html#newpackage) to get a [new package into Debian](https://ftp-master.debian.org/new.html).
* Subscribe to bugs of the package once it is accepted.
```


### Going through MOTU

Submitting new packages through Debian is the preferred path.
However, if your package is Ubuntu-specific or can't go into Debian for some other reason, you can submit it directly to MOTU.
There are a limited number of available reviewers, so you may encounter delays here.

New packages require extra scrutiny and go through a special review process, before they get uploaded and get a final review by the [Archive Admins](https://launchpad.net/~ubuntu-archive).
More information on the review process, including the criteria that will be applied, can be found on the [Code Reviewers page](https://wiki.ubuntu.com/UbuntuDevelopment/CodeReviews#NewPackage).
Developers are encouraged to examine their own packages using these guidelines prior to submitting them for review.

To receive higher quality bug reports, consider writing an [apport hook](https://wiki.ubuntu.com/Apport#Per-package_Apport_Hooks) for your package.

The {ref}`MOTU <dmb-joining-motu>` team approval policy for new packages:

* New MOTU contributors (who are not [members of the MOTU team](https://launchpad.net/~motu) yet), need to get their packages reviewed and signed off by two [MOTUs (core-devs are included in this)](https://launchpad.net/~motu/+members) to get them uploaded to Ubuntu.

* MOTUs can upload new packages directly to the Archive.
  However they are greatly encouraged to have a new package reviewed prior to uploading.
  (cf. [MOTU/Council/Meetings/2007-02-23](https://wiki.ubuntu.com/MOTU/Council/Meetings/2007-02-23))

The MOTU team uses the following workflow:

* Join the {matrix}`devel` channel on Matrix and talk with the MOTU.
  It's good to do this early on, to get advice on how to package (avoid common mistakes), to find out if your package is likely to be accepted (before you invest a lot of work in packaging it), and to find mentors {ref}`willing to sponsor your package <sponsorship>` or to point you in the right direction.

* When you start to work on a new package, assign the `needs-packaging` bug to yourself and set it to {guilabel}`In Progress` (if there is no `needs-packaging` bug, [file one first](https://bugs.launchpad.net/ubuntu/+filebug/+login)).

* Once you have an initial package, follow the {ref}`new packaging instructions <how-to-create-a-new-package>` to upload it to your PPA or a Launchpad branch, then add a link to the package   in the description of the bug.
  Requests for changes or other communication about your package will be made as comments on your bug.
  Subscribing `ubuntu-sponsors` to sponsorship requests is generally advised, as it makes the request appear on the list that people look at.

* Once the approved package is uploaded, the uploading MOTU will set the bug status to {guilabel}`Fix Committed`.

* When the package clears the NEW queue it will automatically be set to {guilabel`Fix Released` (`debian/changelog` must close the `needs-packaging` bug).
  This is done with a bullet point that follows the format:

  * `Initial release (LP: #242910)`
 
  where "LP" refers to "Launchpad". See the {ref}`debian-directory` page for more information on changelogs.

* Even if you don't run Debian as your primary OS, most packaging can be tested perfectly well in a chroot, or failing that, in a Virtual Machine (and most packages will work fine without any changes anyway).
  (→ [Using Development Releases](https://wiki.ubuntu.com/UsingDevelopmentReleases))

* `#debian-ubuntu` on OFTC and the [debian-derivatives mailing list](https://lists.debian.org/debian-derivatives/) are good places for Ubuntu Developers to ask questions.


### Deadline

{ref}`feature-freeze` is the latest approval date. It is recommended to get things done a couple of weeks earlier than that, as getting approval may take some time. If you have a deadline, make sure you factor review and approval time into your timeline.


## Review of new packages

After the new package is uploaded, it will show up and be held in the NEW queue.
It is then {ref}`checked by the Archive Admin team <aa-new-review>`.


## Further reading

* Always check if there is an {term}`Intent to Package (ITP) <ITP>` [bug filed against the WNPP package](https://bugs.debian.org/cgi-bin/pkgreport.cgi?pkg=wnpp;dist=unstable) in Debian.
  If there is, somebody is already working on packaging the software for Debian.
  Join forces with them rather than reinventing the wheel.

* [mentors.debian.net](https://mentors.debian.net/) is a website where people interested in getting their packages into Debian can upload their packages.
  You need to [browse the directories](https://mentors.debian.net/debian/pool/) to find packages.
  [Contributing To Debian](https://wiki.ubuntu.com/Debian/ForUbuntuDevelopers) has additional information on getting your work into Debian.
  (→ [Debian Mentors FAQ](https://wiki.debian.org/DebianMentorsFaq))

* [Debian's SCM](https://salsa.debian.org/public) -- it's possible that a package has been worked on for Debian but has a status of *UNRELEASED*.
  Check the appropriate directories beginning with "pkg" that your package may fall under.
  For example, game packages would be under "pkg-games".
  [The Debian Package Tracking System](https://packages.qa.debian.org/common/index.html) will help you find the specific branch where the package is being maintained.


(new-packages)=
# New packages

For a piece of software to be included in Ubuntu, it must meet the [Ubuntu License Policy](https://help.ubuntu.com/community/License).


## Requesting a new package for Ubuntu

Packages that have recently been added to Debian unstable will be automatically synced into Ubuntu prior to the {ref}`debian-import-freeze` (DIF). Once synced, they will follow the {ref}`proposed-migration flow <proposed-migration>`.
If instead the release process already reached the Debian Import Freeze, you must [file a bug](https://launchpad.net/ubuntu/+filebug) with the summary field "Please sync `<packagename>` from debian `<distro>`" where
`<packagename>` is the package you would like to see.

To get a package into Ubuntu, [file a bug in Launchpad](https://bugs.launchpad.net/ubuntu/+filebug) and make sure it has the tag [`needs-packaging`](https://lists.ubuntu.com/archives/ubuntu-motu/2007-March/001471.html).

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


### Request sponsorship

Submitting new packages through Debian is the preferred path.
However, if your package is Ubuntu-specific or can't go into Debian for some other reason, request sponsorship to have it reviewed and uploaded.

Start with {ref}`how-to-find-a-sponsor` for the current sponsorship process.


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
  [The Debian Package Tracking System](https://tracker.debian.org/) will help you find the specific branch where the package is being maintained.


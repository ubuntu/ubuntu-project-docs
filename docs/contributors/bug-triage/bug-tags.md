(bug-tags)=
# Bug tags

Tags provide us with ways to group bugs across packages, easily find certain types of bugs, or divide a package's bug reports into smaller parts.

Here we outline some standard tags with information about when to use them while working on Ubuntu bug reports.


## Different ways you can help

| Tag | Use case |
| :---- | :---- |
| [`bitesize`](https://launchpad.net/ubuntu/+bugs?field.tag=bitesize) | This bug is easy to fix and suitable for new contributors |
| [`needs-artwork`](https://launchpad.net/ubuntu/+bugs?field.tag=needs-artwork) | A bug that needs new artwork to be created |
| [`needs-coding`](https://launchpad.net/ubuntu/+bugs?field.tag=needs-coding) | A bug that needs new source code to be written |
| [`needs-design`](https://launchpad.net/ubuntu/+bugs?field.tag=needs-design) | A bug that needs UI design done first |
| [`needs-packaging`](https://launchpad.net/ubuntu/+bugs?field.tag=needs-packaging) | Request to package software that isn't packaged for Ubuntu yet |
| [`needs-sound`](https://launchpad.net/ubuntu/+bugs?field.tag=needs-sound) | A bug that needs new sound to be created |


## Generic bug tags

| Tag | Use case |
| :---- | :---- |
| [`apport-bug`](https://launchpad.net/ubuntu/+bugs?field.tag=apport-bug) | A bug reported using "Report a Problem" in an application's {guilabel}`Help` menu -- contains lots of details! |
| [`apport-collected`](https://launchpad.net/ubuntu/+bugs?field.tag=apport-collected) | A bug that has had `apport-collect` run against it, which will contain additional information |
| [`apport-crash`](https://launchpad.net/ubuntu/+bugs?field.tag=apport-crash) | A crash reported by Apport -- Ubuntu's automated problem reporter |
| [`apport-package`](https://launchpad.net/ubuntu/+bugs?field.tag=apport-package) | A bug reported by Apport when a package operation failed |
| [`package-conflict`](https://launchpad.net/ubuntu/+bugs?field.tag=package-conflict) | A bug reported by Apport when a package operation failed due to a conflict with a file provided by another package |
| [`derivatives`](https://bugs.launchpad.net/ubuntu/+source/linux/+bugs?field.tag=derivatives) | Bugs related to Derivatives |
| [`desktop-file`](https://launchpad.net/ubuntu/+bugs?field.tag=desktop-file) | The bug requests the addition/fix of a `.desktop` file |
| <a href="https://launchpad.net/ubuntu/+bugs?field.status:list=FIXRELEASED&field.tag=fix-to-verify">`fix-to-verify`</a> | A bug that is *{ref}`Fix Released <bug-status>`* and should be verified when performing ISO testing of daily builds or milestones |
| [`ftbfs`](https://launchpad.net/ubuntu/+bugs?field.tag=ftbfs) | Bugs describing build failures of packages |
| [`gobuntu`](https://bugs.launchpad.net/ubuntu/+source/linux/+bugs?field.tag=gobuntu) | Bugs related to Gobuntu |
| [`hw-specific`](https://launchpad.net/ubuntu/+bugs?field.tag=hw-specific) | A bug requiring a specific piece of hardware to replicate |
| [`iso-testing`](https://launchpad.net/ubuntu/+bugs?field.tag=iso-testing) | A bug found when performing [ISO testing](https://iso.qa.ubuntu.com/) |
| [`likely-dup`](https://launchpad.net/ubuntu/+bugs?field.tag=likely-dup) | The bug is likely a duplicate of another bug (maybe an upstream bug) but you can't find it |
| [`manpage`](https://launchpad.net/ubuntu/+bugs?field.tag=manpage) | This bug is about a package's manual page being incorrect |
| [`metabug`](https://launchpad.net/ubuntu/+bugs?field.tag=metabug) | This bug has a high probability of duplicate reports being filed |
| [`multiarch`](https://launchpad.net/ubuntu/+bugs?field.tag=multiarch) | This bug is due to an issue with [multiarch triplet paths](https://wiki.debian.org/Multiarch); this could be build time, install time, or run time issues |
| [`nautilus-desktop-icons`](https://launchpad.net/ubuntu/+bugs?field.tag=nautilus-desktop-icons) | Bugs related to the Nautilus desktop; especially the alignment, display, and grid of icons |
| <a href="https://launchpad.net/ubuntu/+bugs?orderby=-importance&field.status%3Alist=New&field.status%3Alist=Incomplete&field.status%3Alist=Invalid&field.status%3Alist=Won%27t+Fix&field.status%3Alist=Confirmed&field.status%3Alist=Triaged&field.status%3Alist=In+Progress&field.status%3Alist=Fix+Committed&field.status%3Alist=Fix+Released&field.tag=needs-devrelease-testing&search=Search">needs-devrelease-testing</a> | A bug that existed in a previous release of Ubuntu and needs to be tested in the latest development release |
| [`needs-reassignment`](https://launchpad.net/ubuntu/+bugs?field.tag=needs-reassignment) | A bug reported about the wrong package but the package maintainer isn't sure which package it belongs to |
| [`packaging`](https://launchpad.net/ubuntu/+bugs?field.tag=packaging) | This bug is likely to be a packaging mistake |
| [`screencast`](https://launchpad.net/ubuntu/+bugs?field.tag=screencast) | This bug report includes a screencast of the bug in action! |
| [`string-fix`](https://launchpad.net/ubuntu/+bugs?field.tag=string-fix) | This bug is a string fix (not code) for spelling and grammatical errors; ideal for new contributors |
| [`touch`](https://launchpad.net/ubuntu/+bugs?field.tag=touch) | An issue with touch support in applications or X |
| [`triage-mentoring-available`](https://launchpad.net/ubuntu/+bugs?field.tag=triage-mentoring-available) | This bug could use some additional information and another triager is offering guidance for getting that information |
| [`units-policy`](https://launchpad.net/ubuntu/+bugs?field.tag=units-policy) | A bug that violates the [Units Policy](https://wiki.ubuntu.com/UnitsPolicy) |
| [`unmetdeps`](https://launchpad.net/ubuntu/+bugs?field.tag=unmetdeps) | Bugs that indicate packages not being installable due to missing dependencies |
| [`upgrade-software-version`](https://launchpad.net/ubuntu/+bugs?field.tag=upgrade-software-version) | Bugs that request new software versions -- please help reviewing them carefully |
| [`work-intensive`](https://launchpad.net/ubuntu/+bugs?field.tag=work-intensive) | Triaging requires intensive work to validate/reproduce |
| [`dist-upgrade`](https://launchpad.net/ubuntu/+bugs?field.tag=dist-upgrade) | A bug encountered when upgrading between releases of Ubuntu |
| [`testcase`](https://launchpad.net/ubuntu/+bugs?field.tag=testcase) | A bug containing a test case with steps to recreate the bug. |


## Application-specific tags

### Cheese

Tags Apport adds while collecting information for Cheese Webcam Booth.

| Tag | Use case |
| :---- | :---- |
| [`gstreamer-error`](https://launchpad.net/ubuntu/+bugs?field.tag=gstreamer-error) | Bug is related to bad drivers and not Cheese; *switch bug to the `linux` package for missing/bad drivers* |
| [`gstreamer-ok`](https://launchpad.net/ubuntu/+bugs?field.tag=gstreamer-ok) | Video `gstreamer` input works fine (drivers seem fine) -- most likely a Cheese bug |


### Unity

The full list of tags for Unity is maintained at: [Unity/Bug tags](https://wiki.ubuntu.com/Unity/FilingBugs#Bug_Tags), including:

| Tag | Use case |
| :---- | :---- |
| [`unity`](https://launchpad.net/ubuntu/+source/compiz/+bugs?field.tag=unity) | `Compiz` bugs that are affecting Unity |
| [`running-unity`](https://launchpad.net/ubuntu/+bugs?field.tag=running-unity) | Bugs reported by people who are running Unity |
| [`needs-design`](https://launchpad.net/unity/+bugs?field.tag=needs-design) | A bug that needs UI design done first |
| [`backlog`](https://launchpad.net/unity/+bugs?field.tag=backlog) | Things that design has finished with, that now need to be implemented |


### Update Manager

| Tag | Use case |
| :---- | :---- |
| [`cdrom-upgrade`](https://launchpad.net/ubuntu/+bugs?field.tag=cdrom-upgrade) | Bugs related to an upgrade from CD-ROM or DVD media |


## Other specific bug tags

### Ayatana

Specific bugs concerning parts of the [Ayatana project](https://launchpad.net/ayatana).

| Tag | Use case |
| :---- | :---- |
| [`app-menu`](https://bugs.launchpad.net/ubuntu/+bugs?field.tag=app-menu) | Bugs related to the [App Menu](https://wiki.ubuntu.com/DesktopExperienceTeam/ApplicationMenu) |
| [`indicator-applet`](https://bugs.launchpad.net/ubuntu/+bugs?field.tag=indicator-applet) | Bugs related to the use of the Indicator Applet that are not in the `indicator-applet` package (no Application Indicators) |
| [`indicator-application`](https://bugs.launchpad.net/ubuntu/+bugs?field.tag=indicator-application) | Bugs related to the use of Indicator Application that are not in the `indicator-application` package |
| [`trayaway`](https://bugs.launchpad.net/ubuntu/+bugs?field.tag=trayaway) | Bugs related to the [Notification Area transition](https://wiki.ubuntu.com/NotificationAreaTransition) |


### Hardware-specific

| Tag | Use case |
| :---- | :---- |
| [`ac97-jack-sense`](https://launchpad.net/ubuntu/+bugs?field.tag=ac97-jack-sense) | This bug deals with headphone sense for AC'97-based codecs (0401) |
| [`hda-jack-sense`](https://launchpad.net/ubuntu/+bugs?field.tag=hda-jack-sense) | This bug deals with headphone sense for HDA-based codecs (0403) |
| [`macbook`](https://launchpad.net/ubuntu/+bugs?field.tag=macbook) | These bugs deal with Mac Book systems |
| [`macbookpro`](https://launchpad.net/ubuntu/+bugs?field.tag=macbookpro) | These bugs deal with Mac Book Pro systems |
| [`ps3`](https://launchpad.net/ubuntu/+bugs?field.tag=ps3) | These bug reports are about people running Ubuntu on a PlayStation 3 |
| [`ume`](https://launchpad.net/ubuntu/+bugs?field.tag=ume) | These bugs deal with Ubuntu Mobile and Embedded systems |
| [`armel`](https://launchpad.net/ubuntu/+bugs?field.tag=armel) | These bugs deal with Ubuntu ARM systems |


### Launchpad retracers tags

These tags were relevant previously for Ubuntu bugs and may still appear in some bugs.

| Tag | Use case |
| :---- | :---- |
| [`need-$arch-retrace`](https://launchpad.net/ubuntu/+bugs?field.tag=need-amd64-retrace) | The bug contains a crash report that needs retracing with `apport-retrace` on the `$arch` actitecture |

### Kernel-specific

| Tag | Use case |
| :---- | :---- |
| [`apport-kerneloops`](https://launchpad.net/ubuntu/+bugs?field.tag=apport-kerneloops) | This Kernel Oops was reported using Apport |
| <a href="https://launchpad.net/ubuntu/+bugs?field.searchtext=linux&field.tag=bitesize">`bitesize`</a> | For the kernel, this includes things like enabling modules and changing kernel config options |
| [`cherry-pick`](https://launchpad.net/ubuntu/+bugs?field.tag=cherry-pick) | A kernel bug that has a git commit SHA from the upstream kernel |
| <a href="https://launchpad.net/ubuntu/+bugs?field.tags_combinator=ALL&field.tag=hibernate+resume">`hibernate-resume`</a> | This bug was triggered by a hibernate/resume failure |
| [`kernel-bug`](https://launchpad.net/ubuntu/+bugs?field.tag=kernel-bug) | A "BUG:" message output was noted in the logs but it did not contain an Oops |
| [`kernel-oops`](https://launchpad.net/ubuntu/+bugs?field.tag=kernel-oops) | This bug causes a kernel Oops message |
| [`needs-upstream-testing`](https://launchpad.net/ubuntu/+bugs?field.tag=needs-upstream-testing) | This bug needs to be tested with the [upstream kernel](https://wiki.ubuntu.com/KernelMainlineBuilds). |
| [`kernel-fixed-upstream`](https://launchpad.net/ubuntu/+bugs?field.tag=kernel-fixed-upstream) | This bug is not reproducible with the latest [upstream kernel](https://wiki.ubuntu.com/KernelMainlineBuilds) version available that allows the reporter to test it, and the version is higher than the Ubuntu kernel after [mapping](http://kernel.ubuntu.com/~kernel-ppa/info/kernel-version-map.html) |
| [`kernel-bug-exists-upstream`](https://launchpad.net/ubuntu/+bugs?field.tag=kernel-bug-exists-upstream) | This bug is reproducible with the latest [upstream kernel](https://wiki.ubuntu.com/KernelMainlineBuilds) version available that allows the reporter to test it, and the version is higher than the Ubuntu kernel after [mapping](http://kernel.ubuntu.com/~kernel-ppa/info/kernel-version-map.html). |
| <a href="https://launchpad.net/ubuntu/+bugs?field.tags_combinator=ALL&field.tag=suspend+resume">`suspend-resume`</a> | This bug was triggered by a suspend/resume failure |
| [`xorg-needs-kernel-fix`](https://launchpad.net/ubuntu/+bugs?field.tag=xorg-needs-kernel-fix) | This is an xorg bug which is dependent on a kernel patch |

For more tags see [Kernel/Tagging](https://wiki.ubuntu.com/Kernel/Tagging).


### Kubuntu-specific

| Tag | Use case |
| :---- | :---- |
| [`guidance-powermanager`](https://launchpad.net/ubuntu/+bugs?field.tag=guidance-powermanager) | This `kde-guidance` bug is in `powermanager` |
| [`kde-guidance-displayconfig`](https://launchpad.net/ubuntu/+bugs?field.tag=kde-guidance-displayconfig) | This `kde-guidance` bug is in `displayconfig` |
| [`kde-guidance-mountconfig`](https://launchpad.net/ubuntu/+bugs?field.tag=kde-guidance-mountconfig) | This `kde-guidance` bug is in `mountconfig` |
| [`kde-guidance-serviceconfig`](https://launchpad.net/ubuntu/+bugs?field.tag=kde-guidance-serviceconfig) | This `kde-guidance` bug is in `serviceconfig` |
| [`kde-guidance-userconfig`](https://launchpad.net/ubuntu/+bugs?field.tag=kde-guidance-userconfig) | This `kde-guidance` bug is in `userconfig` |
| [`kde-guidance-wineconfig`](https://launchpad.net/ubuntu/+bugs?field.tag=kde-guidance-wineconfig) | This `kde-guidance` bug is in `wineconfig` |
| [`needs-upstream-report`](https://launchpad.net/ubuntu/+bugs?field.tag=needs-upstream-report) | This bug needs the report to be forwarded to the upstream project |
| [`needs-upstream-sync`](https://launchpad.net/ubuntu/+bugs?field.tag=needs-upstream-sync) | This bug has been forwarded to the upstream project, which has released a fix that has not been merged yet |
| [`upstream`](https://launchpad.net/ubuntu/+bugs?field.tag=upstream) | This bug is reported to the upstream project |

### More specific

| Tag | Use case |
| :---- | :---- |
| [`a11y`](https://launchpad.net/ubuntu/+bugs?field.tag=a11y) | This bug is an accessibility problem |
| [`apport-hook`](https://launchpad.net/ubuntu/+bugs?field.tag=apport-hook) | This bug is about modifying or adding an Apport hook for a package |
| [`dxteam`](https://launchpad.net/ubuntu/+bugs?field.tag=dxteam) | This bug is specifically targeted by Canonical developers, only to be associated with the `notifications` tag |
| [`ec2-images`](https://launchpad.net/ubuntu/+bugs?field.tag=ec2-images) | This bug is related to Ubuntu on [EC2](https://help.ubuntu.com/community/EC2StartersGuide) |
| [`java-headless`](https://launchpad.net/ubuntu/+bugs?field.tag=java-headless) | This bug is related to a Java program or library that could run headless but depends on a full Java environment (including graphics and sound) |
| [`ldap`](https://launchpad.net/ubuntu/+bugs?field.tag=ldap) | This bug is an LDAP problem |
| [`linuxfirmwarekit`](https://launchpad.net/ubuntu/+bugs?field.tag=linuxfirmwarekit) | This bug contains Linux firmware kit test results |
| [`ngo`](https://launchpad.net/ubuntu/+bugs?field.tag=ngo) | This bug affects [NGOs](https://wiki.ubuntu.com/NGO) |
| [`notifications`](https://launchpad.net/ubuntu/+bugs?field.tag=notifications) | This bug is related to the notification system (`notify-osd`) |
| [`nscd`](https://launchpad.net/ubuntu/+bugs?field.tag=nscd) | This bug deals with `nscd` which is part of the `glibc` package |
| [`usability`](https://launchpad.net/ubuntu/+bugs?field.tag=usability) | This bug is a usability problem |
| [`rtl`](https://launchpad.net/ubuntu/+bugs?field.tag=rtl) | This bug is a right-to-left problem |
| [`uec-images`](https://launchpad.net/ubuntu/+bugs?field.tag=uec-images) | This bug is related to the Ubuntu Enterprise Cloud (UEC) [images](http://uec-images.ubuntu.com/releases) |
| [`xinerama`](https://launchpad.net/ubuntu/+bugs?field.tag=xinerama) | This bug is a `xinerama` problem (multiple-monitor configuration) |


### Patch-specific

| Tag | Use case |
| :---- | :---- |
| [`patch`](https://launchpad.net/ubuntu/+bugs?field.tag=patch) | A patch in its final form that can immediately be released into the appropriate Ubuntu repository as outlined in [Bugs/Patches](https://wiki.ubuntu.com/Bugs/Patches): A raw patch copied from an external location, or possible/test/draft patches don't fit this criteria |
| [`patch-accepted-debian`](https://launchpad.net/ubuntu/+bugs?field.tag=patch-accepted-debian) | This bug has a patch attached to it that has been accepted by Debian |
| [`patch-accepted-upstream`](https://launchpad.net/ubuntu/+bugs?field.tag=patch-accepted-upstream) | This bug has a patch attached to it that has been accepted by upstream |
| [`patch-forwarded-debian`](https://launchpad.net/ubuntu/+bugs?field.tag=patch-forwarded-debian) | This bug has a patch attached to it that has been forwarded to Debian |
| [`patch-forwarded-upstream`](https://launchpad.net/ubuntu/+bugs?field.tag=patch-forwarded-upstream) | This bug has a patch attached to it that has been forwarded upstream |
| [`patch-needswork`](https://launchpad.net/ubuntu/+bugs?field.tag=patch-needswork) | This bug has a patch attached to it that needs some work done on it |
| [`patch-rejected`](https://launchpad.net/ubuntu/+bugs?field.tag=patch-rejected) | This bug has a patch attached to it that was not included in Ubuntu |
| [`patch-rejected-debian`](https://launchpad.net/ubuntu/+bugs?field.tag=patch-rejected-debian) | This bug has a patch attached to it that has been rejected by Debian |
| [`patch-rejected-upstream`](https://launchpad.net/ubuntu/+bugs?field.tag=patch-rejected-upstream) | This bug has a patch attached to it that has been rejected by upstream |
| [`patch-upstreaminput`](https://launchpad.net/ubuntu/+bugs?field.tag=patch-upstreaminput) | This bug has a patch attached to it that has been forwarded upstream and requires their input or incorporation |


### Regression specific

See the [regression tracker](http://qa.ubuntu.com/reports/regression/regression_tracker.html) for a list of these bugs and [QA Team/Regression Tracking](https://wiki.ubuntu.com/QATeam/RegressionTracking) for more information.

| Tag | Use case |
| :---- | :---- |
| [`regression-release`](https://launchpad.net/ubuntu/+bugs?field.tag=regression-release) | A bug in a release that was not present in a previous release: Should be used together with a separate tag for the release the regression was found in (also applies to a development release where an update introduces a regression prior to its official release) |
| [`regression-update`](https://launchpad.net/ubuntu/+bugs?field.tag=regression-update) | A bug in a stable release that was introduced by a package from `-updates`: This would not apply to a development release where a regression was introduced prior to its official release |
| [`regression-proposed`](https://launchpad.net/ubuntu/+bugs?field.tag=regression-proposed) | A bug in a stable release of Ubuntu that was found when testing a package from `-proposed` |
| [`regression-retracer`](https://launchpad.net/ubuntu/+bugs?field.tag=regression-retracer) | An Apport crash bug report that was identified by the retracer as having the same characteristics as a fixed crash report |
| [`needs-bisect`](https://launchpad.net/ubuntu/+bugs?field.tag=needs-bisect) | This is for when a bisect is requested or required to fix the bug |
| [`performing-bisect`](https://launchpad.net/ubuntu/+bugs?field.tag=needs-bisect) | The reporter, developer, or triager is in the process of performing a bisection |
| [`bisect-done`](https://launchpad.net/ubuntu/+bugs?field.tag=bisect-done) | Add when a bisect has been completed and the offending commit(s) identified |


### Release-specific

| Tag | Use case |
| :---- | :---- |
| [`update-excuse`](https://launchpad.net/ubuntu/+bugs?field.tag=update-excuse) | A bug tracking a cause of a package not being migrated to the `-release` pocket (this tag causes the bug to appear on the [update excuses report](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_excuses.html
)) |
| [`block-proposed`](https://launchpad.net/ubuntu/+bugs?field.tag=block-proposed) | A bug that should be held back from migrating into the `-release` pocket |


### SRU-specific

See [Stable Release Updates](https://documentation.ubuntu.com/sru/en/latest/) documentation for more information.

| Tag | Use case |
| :---- | :---- |
| [`verification-done`](https://launchpad.net/ubuntu/+bugs?field.tag=verification-done) | A Stable Release Update bug with a package in `-proposed` that has been confirmed to fix the bug |
| [`verification-failed`](https://launchpad.net/ubuntu/+bugs?field.tag=verification-failed) | A Stable Release Update bug with a package in `-proposed` that has been verified to not fix the bug |
| [`verification-needed`](https://launchpad.net/ubuntu/+bugs?field.tag=verification-needed) | A Stable Release Update bug with a package in `-proposed` needing testing |
| `block-proposed-<series>` | A bug that should be held back from being released into the `-updates` pocket for the corresponding stable series (see [Staging an upload](https://documentation.ubuntu.com/sru/en/latest/howto/special/#stage-an-upload)) |


### X-specific

For X tags please check [X Tagging](https://wiki.ubuntu.com/X/Tagging) with all the official X tags.


## Experiments

| Tag | Use case |
| :---- | :---- |
| [`asked-to-upstream`](https://launchpad.net/ubuntu/+bugs?field.tag=asked-to-upstream) | Users were asked to report the bug upstream themselves |

## Canonical team tags

Some of the Canonical teams across Ubuntu development have evolved a shared
understanding of the tags they use for their own workflows. These are meant
to be added/removed during those teams' regular triage processes, but are documented
here so everyone can find and understand their meaning.

Tags are not the only way to get awareness - Teams are structurally subscribed
when they own (see {ref}`main-inclusion-review`) a package.
In addition they might also subscribe their team to a specific bug so it can
be included in future reviews of the acknowledged backlog.

| Tag | Use case |
| :---- | :---- |
| `$team-todo`      | Among the vast backlog, bugs with this tag are considered both important and actionable. They require a person to be assigned, and must be regularly tracked so they do not fall through the cracks. If, while working on a case, the bug becomes un-actionable this tag should be dropped to keep the overview clear. |
| `$team-freezer`   | This is like `$team-todo`, but for bugs that should be remembered even if they cannot be immediately acted upon. This tag puts the bug into the "freezer", effectively establishing a second tier of cases that are actionable but waiting to be handled. If there is a condition or date by which the case should be re-considered, teams are encouraged to state that when adding this tag. |
| `rls-$$-incoming` | This tag is used as a trigger for getting the attention of the team that is structurally subscribed to the package. `$$` is a abbreviation for the corresponding Ubuntu release name - for example `rr` for `26.04 resolute raccoon` - and allows to target a particular release this shall be considered for. If you have any additional context, please add a comment alongside the tag. |


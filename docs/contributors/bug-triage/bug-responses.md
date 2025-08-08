(bug-responses)=
# Bug responses

It is common when triaging bugs that you need to respond to the original
reporter -- perhaps to request more information, or to redirect their request,
etc. Over time, a set of curated standard responses has been created, and you
can use these when you correspond with the reporter.

These standard responses (and other amazing scripts) are available as a FireFox
extension [in a PPA](https://launchpad.net/~gm-dev-launchpad/+archive/ppa).

When you update one of these responses, you should also update the response
used by the Firefox extension. These responses can be found in the bazaar branch
[lp:ubuntu-bugcontrol-tools](https://code.launchpad.net/ubuntu-bugcontrol-tools)
in the `gm-xml-files/bugsquad-replies.xml` file. To check out a branch, use

```none
bzr branch lp:ubuntu-bugcontrol-tools
```

Only members of `bug-control` can commit to this branch, but even if you are not
a member you can submit a merge proposal, and they can be used when replying to
a bug report if merged.


## Missing information


### Not described well

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. Unfortunately, we cannot work on this bug because your description
didn't include enough information. You may find it helpful to read "How to
report bugs effectively" http://www.chiark.greenend.org.uk/~sgtatham/bugs.html.
We'd be grateful if you would then provide a more complete description of the
problem.

We have instructions on debugging some types of problems at
http://wiki.ubuntu.com/DebuggingProcedures.

At a minimum, we need:

1. The specific steps or actions you took that caused you to encounter the
   problem.
2. The behavior you expected.
3. The behavior you actually encountered (in as much detail as possible).

Please also ensure that you include the release and flavour of Ubuntu that you
are using.

Thank you!
```


### Missing steps to recreate bug

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. Please answer these questions:

* Is this reproducible?
* If so, what specific steps should we take to recreate this bug?

This will help us to find and resolve the problem.
```


### Missing Apport information

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. Please execute the following command only once, as it will automatically
gather debugging information, in a terminal:

  apport-collect BUGNUMBER

When reporting bugs in the future please use apport by using 'ubuntu-bug' and
the name of the package affected. You can learn more about this functionality at
https://wiki.ubuntu.com/ReportingBugs.
```


## Package- or domain-specific questions

The following packages or type of bugs require specific debugging information.


### Debugging kernel (general)

Pleas also see the Ubuntu Kernel Team's
[specific responses](https://wiki.ubuntu.com/Kernel/BugTriage/Responses) for
Linux (Ubuntu) kernel bugs.


### Debugging sound problems

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. We need some more information from you before we can start working on
this bug.

Please include the information requested from the "Reporting Sound Bugs" section
of https://wiki.ubuntu.com/DebuggingSoundProblems as separate attachments.

This information can be gathered for you automatically by using the following
command only once:

  apport-collect -p alsa-base BUGNUMBER

where BUGNUMBER is the number of the bug you've reported.
```


### Debugging ACPI

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. We need some more information from you before we can start working on
this bug.

Please include the information requested at https://wiki.ubuntu.com/DebuggingACPI
as separate attachments.
```


### Debugging Removable Devices

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. We need some more information from you before we can start working on
this bug.

Please include the information requested at https://wiki.ubuntu.com/DebuggingRemovableDevices
as separate attachments.
```


### Debugging Printing problems

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. We need some more information from you before we can start working on
this bug.

Please include the information requested at https://wiki.ubuntu.com/DebuggingPrintingProblems
as separate attachments.
```


### Debugging Hardware Detection

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. We need some more information from you before we can start working on
this bug.

Please include the information requested at https://wiki.ubuntu.com/DebuggingHardwareDetection
as separate attachments.
```


### Debugging USB Storage

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. We need some more information from you before we can start working on
this bug.

Please include the information requested at https://help.ubuntu.com/community/DebuggingUSBStorage
as separate attachments.
```


### Debugging Xorg in general

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. In order to attach necessary information for debugging this as an Xorg
problem please run the following command only once:

  apport-collect BUGNUMBER

Please ensure you have xdiagnose installed, and that you click the Yes button
for attaching additional debugging information. Thanks in advance.
```


### Freeze during boot or shutdown screen

```none
Thanks for your bug report and for your contribution to Ubuntu. In order to
determine if this issue is plymouth related, please boot your computer with
plymouth disabled and then shutdown to see if you can reproduce the issue.
To disable plymouth for a single boot, follow these steps:

1. Hold Right-Shift during Grub boot delay to access the boot menu.
2. Select your actual Ubuntu boot line and press "e" to edit it.
3. Select the "linux" line and at the end of the line, remove "splash" and
   "quiet".
4. Type "F10" to boot the custom boot line.
```


### Debugging Plymouth

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. Please run the following command only once via a terminal:

  apport-collect BUGNUMBER

which will attach necessary information for debugging this as a plymouth problem.
Thanks in advance.
```


### Debugging Live Installation

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. Unfortunately we can't start working on it yet, because your description
didn't include enough information.

Please execute the following command 'ubuntu-bug ubiquity' as it will gather
detailed information regarding your installation. Thanks in advance.
```


### Debugging A Distribution Upgrade

[Debugging Update Manager](https://wiki.ubuntu.com/DebuggingUpdateManager)

```none
Thanks for taking the time to report this bug and helping to make Ubuntu better.
Could you please add the log files from '/var/log/dist-upgrade/' to this bug
report as separate attachments? Thanks in advance.
```


### Debugging GNOME Power Manager

```none
Thanks for taking the time to report this bug and helping to make Ubuntu better.
Could you please run the following command only once in a terminal:

  apport-collect BUGNUMBER

You might also want to take a look at the debugging instructions located at
https://wiki.ubuntu.com/DebuggingGNOMEPowerManager and submit any other logs
related to your problem. Thanks in advance.
```

Apport will add the output of the upstream script `gnome-power-bugreport.sh` and
`devkit-power --dump`. `gnome-power-bugreport.sh` also includes the output of
`devkit-power --dump`.


### Debugging Network Manager

If a Network Manager bug report is about not being able to connect, the title or
summary should be in the format: `[CHIPSET] cannot connect to (ENCRYPT_METHOD)`
where `CHIPSET` is the wireless driver used and `ENCRYPT_METHOD` is the
encryption method used by your wireless network.

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. Unfortunately we can't start working on it yet, because your bug report
didn't include enough information.

Please include the information requested at https://wiki.ubuntu.com/DebuggingNetworkManager
If you have trouble, do not hesitate to ask for more assistance. Thanks in
advance.
```


### Debugging Firefox

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. Could you please try to obtain a backtrace by following the instructions
on https://wiki.ubuntu.com/MozillaTeam/Bugs? Also, please answer these questions:

Is this crash reproducible? If so, which are the steps that lead to it?
Which flash package do you have installed?
Which Java package do you have installed?
Which Firefox extensions do you have installed?

This will greatly aid us in tracking down your problem.
```


#### Firefox crash report that fails retrace

Firefox bug triaging policy is to close (set to *Invalid*) crash reports from
Apport that fail retracing.

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. However, your crash report didn't yield the required information. Please
go ahead and submit a new crash report if it crashes again with the latest
available version of the package. Thanks in advance for your cooperation and
understanding.
```


### Debugging Samba

Please see the [debugging Samba](https://wiki.ubuntu.com/DebuggingSamba) article
for debugging and standard replies.


### Debugging OpenLDAP

Please see the [debugging OpenLDAP](https://wiki.ubuntu.com/DebuggingOpenldap)
article for debugging and standard replies.


### Debugging `ffmpeg`

Mostly `libavcodec` and `libavformat` bugs.

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. You have reported a crash that actually happened in the libavcodec or
libavformat library. In order to be able to actually fix this bug, we must be
able to:

1. Reproduce it;
2. Check if it happens with the latest version; and
3. Understand where it actually crashes.

You can help with the first point by attaching an example file to this bug
report. Please note that a proper attachment is preferred over a link to some
remote site. Remote sites that are password protected or otherwise restricted
(services like rapidshare.com) are absolutely not acceptable. If your file is
too large, try to reproduce with the first few MB only. See
http://ffmpeg.org/bugreports.html section "Submitting Sample Media" for
guidelines.

Please also make sure that your file crashes with the commandline application
"ffplay" from the ffmpeg package. If the crash does not happen with that tool,
the bug does not belong to the ffmpeg package, but to some higher-level package
like libxine1-ffmpeg or gstreamer0.10-ffmpeg (depending on what player has been
used).
```


### Debugging SCIM-related issues

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. In order to determine the cause of this issue, we would need some
additional information.

Please post or attach the following:
1. the output of: dpkg -l | grep scim
2. the output of: im-switch -l
3. the files '/etc/scim/config', '/etc/scim/global' and '~/.scim/config'

Additionally, please answer the following questions:
1. Is this bug reproducible (always/sometimes/no)?
2. If you can reproduce the bug, what are the steps to do so?
3. Which desktop environment are you using? (Gnome/KDE3/KDE4)
4. If you remove '~/.scim/config', '~/.scim/global' and restart your X
   session by logging out and in again, does this bug still appear?
5. If you reinstall the 'scim', 'libscim8c2a', 'scim-bridge-agent' and
   'scim-bridge-client-{gtk|qt4}' packages, followed by the procedure described
   in 4., does the bug still appear?
```


## Incomplete bugs without a response from submitter

Some bugs are never responded to by the submitter (also called "original poster",
or "OP"). These bugs will be automatically expired by Launchpad in 60 days,
counted from the day it was set incomplete.

There is no need to act on them (and, actually, changing the bug will restart
the expiry period). Note that this applies for the Ubuntu project (i.e., those
bug tasks that have "(Ubuntu)" in their name). Other projects may, or may not,
have automatic incomplete bug expiration set.


## Bugs without a package

Sometimes bugs will be reported just using the "Ubuntu" package. This is not the
best place for the bug though and we should encourage bug reporters to report
the bug against the correct package by pointing them at some documentation. Keep
in mind `PKGNAME` is a placeholder.

```{warning}

If you use this response, you must assign a package. If you do not know what
package to assign, please leave the bug alone, and ask for help.
```

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. This bug did not have a package associated with it, which is important
for ensuring that it gets looked at by the proper developers. You can learn more
about finding the right package at https://wiki.ubuntu.com/Bugs/FindRightPackage.
I have classified this bug as a bug in PKGNAME.

When reporting bugs in the future please use apport by using 'ubuntu-bug' and
the name of the package affected. You can learn more about this functionality at
https://help.ubuntu.com/community/ReportingBugs.
```


## Bug resolved after update or config change

Occasionally, bug reporters will indicate that a bug has been fixed after some
software update or after changing a configuration value back to its default
value. These bug reports should be set to *Invalid* since we don't know the root
cause. When closing the bug report it is a good idea to take an opportunity to
let the reporter know how to manage bug statuses.

```none
This bug report is being closed due to your last comment regarding this being
fixed with an update. For future reference you can manage the status of your own
bugs by clicking on the current status in the yellow line and then choosing a
new status in the revealed drop down box. You can learn more about bug statuses
at https://wiki.ubuntu.com/Bugs/Status. Thank you again for taking the time to
report this bug and helping to make Ubuntu better. Please submit any future bugs
you may find.
```


## Needs testing in the development release

A lot of bug reports need testing in the development release of Ubuntu. This is
something that most anyone can do by downloading the Desktop ISO, booting from
it and testing their particular bug.

Before using this, *please* check `rmadison <package>` to see if the package
version has changed between when the bug was reported and the current development
release. If it has not changed, there is no need to ask. If it has changed,
check the changelog (via `aptitude changelog $PKGNAME`) to see if this issue has
been specifically addressed.

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. The issue that you reported is one that should be reproducible with the
live environment of the Desktop ISO of the development release. It would help us
greatly if you could test with it so we can work on getting it fixed in the next
release of Ubuntu. You can find out more about the development release at
http://www.ubuntu.com/testing/. Thanks again and we appreciate your help.
```


## Missing a crash report or having a .crash attachment

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. It sounds like some part of the system has crashed. To help us find the
cause of the crash please follow these steps:

1. Run these commands:
     journalctl -b0 > journal.txt
     journalctl -b-1 > prevjournal.txt
   and attach the resulting text files here.

2. Look in /var/crash for crash files and if found run:
       ubuntu-bug YOURFILE.crash
   Then tell us the ID of the newly-created bug.

3. If step 2 failed then look at https://errors.ubuntu.com/user/ID where ID is
   the content of file /var/lib/whoopsie/whoopsie-id on the machine. Do you find
   any links to recent problems on that page? If so then please send the links
   to us.

Please take care to avoid attaching .crash files to bugs as we are unable to
process them as file attachments. It would also be a security risk for yourself.
```


## A duplicate bug

When making a bug report a duplicate of another it is important to communicate
to the reporter that any discussion regarding the bug should take place in the
primary bug. Keep in mind that NUMBER is a placeholder and should be the number of
the primary bug report.

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. This particular bug has already been reported and is a duplicate of bug
NUMBER, so it is being marked as such. Please look at the other bug report to
see if there is any missing information that you can provide, or to see if there
is a workaround for the bug. Additionally, any further discussion regarding the
bug should occur in the other report. Feel free to continue to report any other
bugs you may find.
```


## About an obsolete version of the software for reporter's release

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. However, according to this report, you are not using the most recent
version of this package for your Ubuntu release. Please upgrade to the most
recent version and let us know if you are still having this issue. Thanks in
advance.
```


## Missing a backtrace

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. Please try to obtain a backtrace following the instructions at
http://wiki.ubuntu.com/DebuggingProgramCrash and upload the backtrace (as an
attachment) to the bug report. This will greatly help us in tracking down your
problem.
```


## Unusable stack trace after retracing

This is an alternative to the previous response, if there is a good chance that
another retrace will work better (e.g. outdated package versions). Please close
the bug as *Invalid* with this comment:

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better.

However, processing it in order to get sufficient information for the developers
failed (it does not generate an useful symbolic stack trace). This might be caused
by some outdated packages which were installed on your system at the time of the
report. Please upgrade your system to the latest package versions. If you still
encounter the crash, please file a new report.

Thank you for your understanding, and sorry for the inconvenience!
```


## Need valgrind log

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. Please try to obtain a valgrind log following the instructions at
https://wiki.ubuntu.com/Valgrind and attach the file to the bug report. This
will greatly help us in tracking down your problem.
```


## A bug that should be handled upstream

If you are sure the reported bug is not caused by the packaging for Ubuntu, it should usually be sent upstream by someone affected by the bug. If appropriate, replace GNOME with the organization behind the software (see [the upstream wiki page](https://wiki.ubuntu.com/Bugs/Upstream/) for available organizations):

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. The issue you are reporting is an upstream one and it would be nice if
somebody having it could send the bug to the developers of the software by
following the instructions at https://wiki.ubuntu.com/Bugs/Upstream/GNOME. If
you have done so, please tell us the number of the upstream bug (or the link),
so we can add a bugwatch that will inform us about its status. Thanks in
advance.
```

If you have already pointed out that the reported bug is an upstream one, but
there hasn't been any feedback about the requested upstream bug for 2 weeks, the
reporter (or someone else affected by the bug) might have forgotten it. If that's
the case, you should ask if someone has already forwarded the bug upstream and
can tell you the number of the upstream bug:

```none
Is there any news about this bug? Has someone affected by this bug sent the
report upstream? Could you tell us the bug number, so we can add a bugwatch that
will inform us about its status? Thanks in advance.
```

However, if you have already sent the bug upstream, you should leave a comment
stating where the upstream bug can be found:

```none
Thank you for your bug report. This bug has been reported to the developers of
the software. You can track it and make comments at:
```


## Old untouched bugs

Old new bugs that haven't been touched in a quite a while and you are unable to
recreate the bug.

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. We are sorry that we do not always have the capacity to look at all
reported bugs in a timely manner. There have been many changes in Ubuntu since
that time you reported the bug and your problem may have been fixed with some of
the updates. It would help us a lot if you could test it on a currently
supported Ubuntu version. When you test it and it is still an issue, kindly
upload the updated logs by running only once:

  apport-collect <bug #>

and any other logs that are relevant for this particular issue.
```


## Packages not provided by Ubuntu

Occasionally, bug reporters will report a bug about a version of a package not
provided by Ubuntu or (less often) about software not provided by Ubuntu. In
this case we can not help them and the bug should be set to *Invalid*.

```none
Thank you for taking the time to report this bug and trying to help make Ubuntu
better. However, it seems that you are not using a software package provided by
the official Ubuntu repositories. Because of this the Ubuntu project can not
support or fix your particular bug. Please report this bug to the provider of
the software package. Thanks!

If you are interested in learning more about software repositories and Ubuntu,
check https://help.ubuntu.com/community/Repositories.
```


## Fixed in Development release while still existing in a previous release

The bug's state should become *Fix Released* and if the package qualifies for a
[Stable Release Update (SRU)](https://documentation.ubuntu.com/sru/en/latest/):

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. However, I am closing it because the bug has been fixed in the latest
development version of Ubuntu.

This is a significant bug in Ubuntu. If you need a fix for the bug in previous
versions of Ubuntu, please perform as much as possible of the SRU Procedure [1]
to bring the need to a developer's attention.

[1]: https://wiki.ubuntu.com/StableReleaseUpdates#Procedure
```

The bug's state should become *Fix Released* and if the package does not qualify
for an SRU because it is considered a minor bug and the package can be backported:

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. However, I am closing it because the bug has been fixed in the latest
development version of Ubuntu.

If you need a fix for the bug in previous versions of Ubuntu, please follow the
instructions for "Requesting a Backport" at https://wiki.ubuntu.com/UbuntuBackports#Requesting_a_Backport.
```

The bug's state should become *Fix Released* and if the package can not be
backported:

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. However, I am closing it because the bug has been fixed in the latest
development version of Ubuntu. It won't be fixed in previous versions of Ubuntu
because the package doesn't fit the requirements for backporting. See
https://wiki.ubuntu.com/UbuntuBackports for more information.
```


## Reported by someone not respecting the Code of Conduct

```none
Thank you for your bug report. To maintain a respectful atmosphere, please
follow the code of conduct - http://www.ubuntu.com/project/about-ubuntu/conduct.
Bug reports are handled by humans, the majority of whom are volunteers, so please
bear this in mind.
```


## A support request

Determining whether a bug report is actually a support request can be quite
challenging, but if you decide the bug *is* a support request you can convert it
to such by clicking {guilabel}`Convert to a question` at the top of the bug's
web page. This will mark the bug as *Invalid*, create a new question in the
answer tracker and link it to the bug. In the comment dialog that you receive,
post a comment to inform the reporter about your action, and advise them to use
the support tracker for any future problems.

```none
Thank you for taking the time to report this issue and helping to make Ubuntu
better. Examining the information you have given us, this does not appear to be
a bug report so we are closing it and converting it to a question in the support
tracker. We understand the difficulties you are facing, but it is better to
raise problems you are having in the support tracker at
https://answers.launchpad.net/ubuntu if you are uncertain if they are bugs. If
you would prefer live chat support, you can find an IRC support channel for your
flavor of Ubuntu here: https://wiki.ubuntu.com/IRC/ChannelList. You can also
find help with your problem in the support forum of your local Ubuntu community
http://loco.ubuntu.com/ or asking at https://askubuntu.com or
https://discourse.ubuntu.com/t/welcome-to-support-and-help/49951. For help on
reporting bugs, see https://help.ubuntu.com/community/ReportingBugs.
```

Chris Guiver provides an alternate wording (thanks, Chris!):

```none
Thank you for taking the time to report this bug and helping to make Ubuntu better.

Bug reporting is about finding & fixing problems thus preventing future users
from hitting the same bug.

I suspect a Support site would be more appropriate, e.g.
https://answers.launchpad.net/ubuntu. You can also find help with your problem
in the support forum of your local Ubuntu community http://loco.ubuntu.com/ or
asking at https://askubuntu.com or https://discourse.ubuntu.com/t/welcome-to-support-and-help/49951),
or for more support options please look at https://discourse.ubuntu.com/t/community-support/709.
```

It is also a good idea to change the source package beforehand if it's set
incorrectly, so that the question will be associated with the correct package in
the answer tracker, or edit the question afterwards and assign it to the correct
package. If it doesn't pertain to a specific package, change it to "Ubuntu".


## Not reported in English

This response is appropriate when a bug is not reported in English or some error
messages are not in English.

```none
Thank you for taking the time to report this issue and helping to make Ubuntu
better. We noticed that some of the sentences in this bug report are not in
English. If they were translated to English they would be more understandable to
triagers. Could you please translate them?
```


## Suspected bad ISO download

This response may be necessary when someone is having strange issues with the
Desktop ISO.

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. While we appreciate the difficulties you are facing, it would appear
that the image (ISO file) you downloaded could be corrupt. There is an easy way
to verify the integrity of the Ubuntu ISO files you download. Could you please
visit https://help.ubuntu.com/community/HowToMD5SUM follow the instructions and
report back as to whether or not the MD5SUM verified? Thanks in advance.
```


## A suggestion for changing default applications or preferences

This should only be used for bug reports where the scope of the change is quite
large or would affect a lot of users.

```none
Thank you for your suggestion. However, the changes you are requesting aren't
really a bug and require more discussion, which should be done on an appropriate
mailing list or forum. http://www.ubuntu.com/support/community/mailinglists might
be a good start for determining which mailing list to use.
```


## About an incorrect translation

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. Translations in Ubuntu are handled by the Ubuntu Translations project at
https://launchpad.net/ubuntu-translations, so we are going to move this bug
report over to that project.
```


## Incomplete package request

```none
Thank you for taking the time to request this package and helping to make Ubuntu
better. Unfortunately you have not provided enough information for a developer
to start packaging this application. Please make sure this bug meets the
guidelines at https://wiki.ubuntu.com/UbuntuDevelopment/NewPackages. An example
of a complete package request is available at
https://wiki.ubuntu.com/UbuntuDevelopment/NewPackages/ExamplePackageRequest).
```


## Triage successful

```none
Thanks for reporting this bug and any supporting documentation. Since this bug
has enough information provided for a developer to begin work, I'm going to mark
it as confirmed and let them handle it from here. Thanks for taking the time to
make Ubuntu better!
```


## Triage unsuccessful: Back to New/Incomplete Status

```none
Thanks for taking the time to report this bug and comment on it. However, I've
noticed that this bug has been Confirmed although there is not clear indication
as to how to recreate this bug [or version of software affected]. Subsequently,
I'm setting its status to Incomplete until that information is provided. You can
learn more about bug statuses at http://wiki.ubuntu.com/Bugs/Status. Thanks for
taking the time to make Ubuntu better!
```


## Release has reached End of Life (EOL)

If the specific release has reached End of Life (as per
[Releases](https://wiki.ubuntu.com/Releases) and there is not enough information
to work on the bug, then you can set to *Incomplete* and use the following
response (delete the lines that are not relevant):

```none
Thank you for reporting this bug to Ubuntu.

Ubuntu 24.10 (oracular) reached end-of-life on July 10, 2025
Ubuntu 23.04 (lunar) reached end-of-life on January 25, 2024
Ubuntu 23.10 (mantic) reached end-of-life on July 11, 2024
Ubuntu 23.04 (lunar) reached end-of-life on January 25, 2024
Ubuntu 22.10 (kinetic) reached end-of-life on July 20, 2023
Ubuntu 21.10 (impish) reached end-of-life on July 14, 2022
Ubuntu 21.04 (hirsute) reached end-of-life on January 20, 2022
Ubuntu 20.10 (groovy) reached end-of-life on July 22, 2021
Ubuntu 20.04 (focal) reached end-of-standard-support in May 2025
Ubuntu 19.10 (eoan) reached end-of-life on July 17, 2020
Ubuntu 19.04 (disco) reached end-of-life on January 23, 2020
Ubuntu 18.10 (cosmic) reached end-of-life on July 18, 2019
Ubuntu 18.04 (bionic) reached end-of-standard-support on May 31, 2023
Ubuntu 17.10 (artful) reached end-of-life on July 19, 2018
Ubuntu 17.04 (zesty) reached end-of-life on January 13, 2018
Ubuntu 16.10 (yakkety) reached end-of-life on July 20, 2017
Ubuntu 16.04 (xenial) reached end-of-standard-support on April 29, 2021
Ubuntu 15.10 (wily) reached end-of-life on July 28, 2016
Ubuntu 15.04 (vivid) reached end-of-life on February 4, 2016
Ubuntu 14.10 (utopic) reached end-of-life on July 23, 2015
Ubuntu 14.04 (trusty) reached end-of-standard-support on April 25, 2019
Ubuntu 13.10 (saucy) reached end-of-life on July 17, 2014
Ubuntu 13.04 (raring) reached end-of-life on January 27, 2014
Ubuntu 12.10 (quantal) reached end-of-life on May 16, 2014
Ubuntu 12.04 (precise) reached end-of-life on April 28, 2017
Ubuntu 11.10 (oneiric) reached end-of-life on May 9, 2013
Ubuntu 11.04 (natty) reached end-of-life on October 28, 2012
Ubuntu 10.10 (maverick) reached end-of-life on April 10, 2012
Ubuntu 10.04 (lucid) reached end-of-life on May 9, 2013
Ubuntu 9.10 (karmic) reached end-of-life on April 30, 2011
Ubuntu 9.04 (jaunty) reached end-of-life on October 23, 2010
Ubuntu 8.10 (intrepid) reached end-of-life on April 30, 2010
Ubuntu 8.04 (hardy) reached end-of-life on May 12, 2011
Ubuntu 7.10 (gutsy) reached end-of-life on April 18th, 2009
Ubuntu 7.04 (feisty) reached end-of-life on October 19, 2008
Ubuntu 6.10 (edgy) reached end-of-life on April 26, 2008

See this document for currently supported Ubuntu releases:
https://wiki.ubuntu.com/Releases

We appreciate that this bug may be old and you might not be interested in
discussing it anymore. But if you are then please upgrade to the latest Ubuntu
version and re-test. If you then find the bug is still present in the newer
Ubuntu version, please add a comment here telling us which new version it is in.
```


## Patch attachment not flagged as a patch

When reviewing bug attachments you might find an attachment
[that is a patch](https://wiki.ubuntu.com/Bugs/Patches), but is not flagged.
Let people know what a patch is!

```none
Looking at the attachments in this bug report, I noticed that an attachment was
not flagged as a patch. A patch contains changes to an Ubuntu package that will
resolve a bug and this attachment is one! Subsequently, I've checked the patch
flag for it. In the future when submitting patches please use the patch checkbox
as there are some Launchpad searches that use this feature. You can learn more
about the patch workflow at https://wiki.ubuntu.com/Bugs/Patches.
```


## Attachment incorrectly flagged as a patch

When reviewing bug attachments you might that someone flagged an attachment
[that is a patch](https://wiki.ubuntu.com/Bugs/Patches), but it really isn't one.
Let people know what a patch is!

```none
Looking at the attachments in this bug report, I noticed that one was flagged as
a patch incorrectly. A patch contains changes to an Ubuntu package that will
resolve a bug, since this was not one I've unchecked the patch flag for it. In
the future keep in mind the definition of a patch. You can learn more about what
qualifies as a patch at https://wiki.ubuntu.com/Bugs/Patches. Thanks!
```


## Package installation failure

If the problem looks like local file system corruption (e.g. {lpbug}`322714`),
which indicates broken/truncated `dpkg .list` files), it is most likely not
something we can fix in Ubuntu in general. Since we have a large number of such
bugs, it is probably best to close it as *Invalid* (or *Incomplete* if you want
to follow-up and subscribe) with this comment:

```none
Thank you for your report. This package failure looks like being caused by a
corrupted file system. Please start the "Memory check" from the boot menu. If
that runs successfully, please start the desktop ISO. Hold right-shift key after
the BIOS checks to get to the grub menu and run "Check disc for errors" option.
If the file system corruption is serious, the safest option would be to
reinstall your system.
```


## Security bugs

Please see the Ubuntu Security Team's
[bug triage](https://wiki.ubuntu.com/SecurityTeam/BugTriage) page.


## Added bug watch

```none
Thanks for taking the time to report this bug in the upstream bug tracking
system this is a tremendous help. Launchpad has the ability to watch lots of
upstream bug trackers and this can be done by following the procedure documented
at https://wiki.ubuntu.com/Bugs/Watches. I've added the bug watch for this bug
report.
```


## Hanging application or daemon

```none
Thanks for your interest in helping to resolve this issue. In order to get to
the bottom of this we need to figure out where the program is hanging. If you
can follow the steps on https://wiki.ubuntu.com/Backtrace#Already_running_programs
and attach the generated text file to this bug it would be of great help.
```


## User incorrectly subscribing a team to a bug

```none
Thanks for your interest in helping to resolve this issue. There is no need to
subscribe anyone to this bug, as it generates unnecessary emails and will not
resolve the issue any faster. Your bug will be looked at by a developer as time
permits.
```


## Bug reported against Firefox snap

Beginning in Ubuntu 22.04, Firefox is provided as a snap created and published
directly by Mozilla. Users, however, can still report against the Firefox package
directly in Launchpad. Apport still warns against this, but Launchpad does not.
Add this comment (a slight modification of the response from Apport) if the bug
mentions occurring in 22.04 (or later) and mark the bug as *Incomplete*. If the
user mentions the package as not being a snap, then it's *Invalid* as it came
from a source other than Ubuntu or the snap.

```none
Thank you for taking the time to report this bug and help make Ubuntu better.
Firefox is provided by a snap published by Mozilla, and they may not be aware
of this issue. Please contact them via
https://support.mozilla.org/kb/file-bug-report-or-feature-request-mozilla
and link the bug report here so it can be further tracked. Thank you!
```


## Bug reported from unofficial derivative (not official flavour)

Sometimes we receive bug reports from unofficial derivatives (such as Linux Mint),
which we cannot guarantee bugs can be fixed for or can support, so they need to
be closed as *Invalid* with this message:

```none
Thank you for taking the time to report this bug and helping to make Ubuntu
better. However, per your report, it seems as though you are not actually running
Ubuntu but a derivative distribution. Derivatives are not official flavours and
may have additional repositories that provide packages that conflict with our
official packages, so we cannot provide support or debug when things go wrong in
these distributions.

Official flavours of Ubuntu are listed here: https://ubuntu.com/desktop/flavours

Please seek support and bug reporting solutions from your distribution. Thank
you!
```


## Links

Other projects have standard responses as well:

* [GNOME](http://live.gnome.org/Bugsquad/TriageGuide/StockResponses)  
* [Mozilla Team](https://wiki.ubuntu.com/MozillaTeam/Bugs/Triage/Responses)



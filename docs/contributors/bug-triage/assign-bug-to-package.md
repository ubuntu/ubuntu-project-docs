(assign-bug-to-package)=
# Assign a bug to a package

To ensure the right people see a bug report, every report should identify the
software package related to the bug. When running `ubuntu-bug` (see
[Reporting Bugs](https://help.ubuntu.com/community/ReportingBugs)), one must
sometimes specify the package manually. This page explains how to identify the
related package.


## Common scenarios

In most situations, you can identify the problem package based on the scenario
in which the bug occurs. 


### Applications

Applications in released versions of Ubuntu no longer have a
{guilabel}`Report a Problem` menu item. Thus, you must first determine the
executable name for the application and then find the package the executable
belongs to.


#### Apport

Since Natty Narwhal (11.04) you can call `ubuntu-bug` with `--window` (or `-w`)
which enables you to click on the application window and Apport will identify
the package name by itself.


#### Determining the executable path

If you launched the application through the Main Menu, you can use the menu
editor to find which command it runs:

GNOME
: Launch System -> Preferences -> Main Menu

: Select the item for the application (e.g., System -> Preferences -> Display)

: Click {guilabel}`Properties` button

: Write down the "Command" value -- this is the executable name

: Open a Terminal (Applications -> Accessories -> Terminal)

: In the terminal, type `which [executable name]`

: Write down the value printed on the terminal -- this is the full executable path


KDE
: Open the Menu Editor by clicking on the {guilabel}`K` button (Kickoff
  Application Launcher) in the Desktop Panel with the right mouse button and
  selecting {guilabel}`Menu Editor`

: Select the item for the application (e.g., System -> Dolphin (File Manager))

: Write down the first value in the "Command" filed in the General tab -- this
  is the executable name (e.g., "dolphin")

: Open a Terminal with Konsole (K -> Applications -> System -> Terminal)

: In the terminal, type `which <executable name>` (e.g., `which dolphin`)

: Write down the value printed on the terminal -- this is the full executable
  path


Any other
: If you did not launch the application through the Main Menu or cannot use the
  Menu Editor, you can use `xprop` to find the related executable:

: Launch the application

: Open a Terminal:
  * GNOME: Applications -> Accessories -> Terminal
  * KDE: K -> Applications -> System -> Terminal

: In the terminal, type `xprop WM_CLASS` -- your mouse pointer should now turn
  to crosshairs

: Click anywhere in the application's window

: The terminal will now list a line like `WM_CLASS(STRING) = "deja-dup", "Deja-dup"`

: Write down the first value (e.g. `"deja-dup"`). 

: In the terminal, type `locate -b "\[executable name]"` (in this case,
  `locate -b "\deja-dup"`) -- the backslash (`\`) is important!

: Write down the line printed on the terminal -- this is the full executable
  path (if there are multiple lines, use the first one)


#### Find the package name

After you have found the executable path, you can find the package name by
running:

```none
dpkg -S [full executable path]
```

For example, `dpkg -S /usr/bin/gnome-display-properties` will print the package
name for `gnome-display-properties`.

Another useful tool when triaging bugs is `apt-file`:

```none
apt-file search terminator
```

This utility works like `dpkg -S` but searches all packages instead of only
those you have installed.


### When installing Ubuntu (or derivatives)

If you encounter a bug when installing Ubuntu, Kubuntu, Edubuntu, or other
derivatives, the bug is probably one of a small set of packages.

* If you find the bug when booting the Live CD (or alternative installer), file
  the bug against the kernel

* If you find the bug when installing Ubuntu from the Desktop CD), the package
  is `ubiquity` (see [Debugging Ubiquity/Attaching Logs](https://wiki.ubuntu.com/DebuggingUbiquity/AttachingLogs))

* If you find the bug when installing from the Alternate or Server CDs, the
  package is `debian-installer` 


### When upgrading Ubuntu (or derivatives)

If you encounter a bug while upgrading Ubuntu (for example, from 24.04 to 24.10),
the problem package is `ubuntu-release-upgrader`. Attach the log files found in
`/var/log/dist-upgrade/`.


### During boot

* If you encounter a bug with the boot splash screen (typically an Ubuntu logo
  displayed during boot), the package is `plymouth`.

* If the screen goes blank after the splash screen (about the time the login
  screen should come up), report the bug against `xorg`.

* If the boot errors or freezes even in "recovery mode", the bug should be
  reported against the kernel.


### At the login screen

If you encounter a bug at the login screen, the package is the display manager:

* In Ubuntu 11.10 to 17.04, it is `LightDM` -- in previous versions of Ubuntu
  and Edubuntu it was `gdm`.

* In Ubuntu 17.10 or above it is `gdm3`.

* In Xubuntu 11.10 or above, it is `LightDM` -- in previous versions of Xubuntu
  it was `gdm`.

* In Kubuntu 15.04 or above, it is `sddm` -- in previous versions of Kubuntu it
  was `kdm`.

* In Lubuntu 18.10 or above, it is `sddm` -- in Lubuntu 12.04 through 18.04 it
  was `LightDM`, and prior versions of Lubuntu it was `lxdm`.

* In Ubuntu GNOME it is `gdm3`.

* In Ubuntu MATE it is `LightDM`.

* In Ubuntu Unity it is `LightDM`.


### Graphical Environment

The Ubuntu graphical environment is provided by a combination of the Linux
kernel and the X Window System (aka `x.org`).

The following symptoms typically are due to GPU issues in the kernel DRM driver
(`linux` package):

* Blank or solid-colored screen instead of login screen, or immediately after
  login.

* System freezes completely.

* Wrong default screen resolution.

If you have any of the following symptoms, the issue is with X and the package
to report against is `xorg` (see [X/Troubleshooting](https://wiki.ubuntu.com/X/Troubleshooting)
if you want to pin-point the problem):

* The graphical session terminates and returns to the login screen.

* Fonts are extremely big or small.

If your problem is with the actual desktop (for example, with desktop icons):

* In Ubuntu and Edubuntu, the desktop is managed by the file browser, `nautilus`.

If your problem is with window management (for example, focus stealing):

* If you are using `compiz` (visual effects), the package is `compiz`.

* In Ubuntu and Edubuntu, the no-effects window manager is `metacity`.

* In Xubuntu, the window manager is `xfwm4`.

* In Kubuntu, the window manager is `kwin`.

If your problem is with the Administration authentication dialog (where you
enter your password), the package is:

* `gksu` in Ubuntu and Edubuntu.

* `kdesudo` in Kubuntu.

If your problem is with the Notification System, the package is:

* `notify-osd` in Ubuntu, Xubuntu and Edubuntu.

If your problem is with the lock screen itself, the package is `gnome-screensaver`
until 13.10 or `unity` from 14.04 onwards. For more info, check
[How screen locking works](https://wiki.ubuntu.com/DebuggingScreenLocking/HowScreenLockingWorks).


### Printing

All printing in Ubuntu is done via the Common UNIX Printing System (CUPS).
The package is `cups` (see also
[Debugging Printing Problems](https://wiki.ubuntu.com/DebuggingPrintingProblems)).


### Sound

See [Debugging Sound Problems](https://wiki.ubuntu.com/DebuggingSoundProblems)
for reporting/triage instructions for sound problems.

You might want to try [Sound Troubleshooting](https://help.ubuntu.com/community/SoundTroubleshooting)
first.


### Hardware Malfunctions

If a piece of hardware is malfunctioning, typically the problem package is the
kernel. However, if the problem is with a storage device (internal or external)
in 9.10 Karmic Koala or above, problems should be reported with
`ubuntu-bug storage`. If you are triaging, see the "Use Storage Symptom"
standard reply.


### Network

Usual candidate packages are the kernel (file bugs under the `linux` package)
and `network-manager`.


### Suspend and Hibernate

Suspend and hibernate are treated as two completely different issues, needing
one bug report for each. While there are many different packages responsible:

* The kernel implements the actual suspending and resuming and is generally the
  responsible package when there are hardware-related failures after resume.
  
  File all bugs against the package `linux` first, unless you know exactly the
  root cause commit in the code for the responsible package. The majority of
  suspend/hibernate bugs are due to outdated BIOS or buggy driver
  implementations, rather than userspace bugs.

* `gnome-power-manager` (in Ubuntu and Edubuntu) is responsible for setting
  policy on when the system should be suspended or resumed, and signaling the
  system to do so.

* `pm-utils` is responsible for getting the system into a state where it can be
  suspended or hibernated, and handling any cleanup after resume. 

If you are unsure which package is causing the problem, a safe bet is the kernel
(package: `linux`), but make sure the bug title includes "suspend" or "hibernate".


### Hotkeys

Hotkey handling, such as volume and suspend keys, involves multiple packages.
See [Hotkeys/Troubleshooting](https://wiki.ubuntu.com/Hotkeys/Troubleshooting)
for specific packages involved and for troubleshooting instructions. If a hotkey
does nothing or is mapped to the wrong function, the problematic package is
likely `udev`.


### Ubuntu mirror issues

Issues with Ubuntu {ref}`Mirrors <mirrors>` should be reported to
`mirrors@ubuntu.com` and not as a bug on Launchpad.


### Ubuntu Touch

See the [Ubuntu Touch guidelines](https://wiki.ubuntu.com/Touch/Contribute#How_to_report_bugs)


## Package-specific instructions

Some packages have changed names through versions of Ubuntu and others need
special care while reporting. This section lists those special cases.


### Filesystem problems

Usual suspects are the kernel, `gvfs` and `mountall`.


### Kernel

The correct package for bugs about the kernel is `linux`.

Please read [Kernel Team bug policies](https://wiki.ubuntu.com/KernelTeam/KernelTeamBugPolicies)
when reporting bugs against the kernel.


### MySQL

Put MySQL bugs in the appropriate package depending on the version of MySQL:

* `mysql-5.5` - the default version in Trusty (14.04)
* `mysql-5.6`
* `mysql-5.7`
* `mysql-8.0`

### Incorrectly reported packages

The following packages often receive bug reports in error.

| Incorrect package | Correct package                  |
| ----------------- | -------------------------------- |
| `chromium`        | `chromium-browser`               |
| `dash`            | `unity`                          |
| `discover`        | `plasma-discover`                |
| `epiphany`        | `epiphany-browser`               |
| `gnome`           | `gnome-shell` or `gnome-session` |
| `kernel-package`  | `linux`                          |
| `snap`            | `snapd`                          |
| `software-center` | `gnome software`[^1]             |
| `ubuntu-settings` | `gnome-control-center`           | 

[^1]: or the `snap-store-desktop` project (if relating to the snap version of 'GNOME Software')

Bug reports for these packages should be moved to the correct packages so
they reach those that can investigate and/or fix them.


## Find the source package

Many "binary packages" (that is, packages containing the software you run) may
be built from the same "source package" (developers' source code), so bug
reports are assigned to source packages and not binary packages. In rare cases,
you must manually identify the source package from a binary package.

Go to [Launchpad search](https://launchpad.net/ubuntu/+search) where you can
search for the source package from which the binary package is compiled. The
source package is the package you should select when filing a bug.

* For example: `gnome-control-center` belongs to the `gnome-system-tools` source
  package.

Alternatively, you can use `apt-cache show kdm` and look for the `Source:` line
to find the source package.


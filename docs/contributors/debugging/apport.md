Available languages:[Italiano](https://wiki.ubuntu.com/Apport_it),

<<TableOfContents>>


(what-is-this-all-about)=
## What is this all about?

Debugging program crashes without any automated tools has been pretty time consuming and hard for both developers and users. Many program crashes remain unreported or unfixed because:

* Many crashes are not easily reproducible.

* End users do not know how to prepare a report that is really useful for developers, like building a package with debug symbols, operating `gdb`, etc.

* A considerable part of bug triage is spent with collecting relevant information about the crash itself, package versions, hardware architecture, operating system version, etc.

* There is no easy frontend which allow users to submit detailed problem reports.

* Existing solutions like bug-buddy or krash are specific to a particular desktop environment, are nontrivial to adapt to the needs of a distribution developer, do not work for crashes of background servers (like a database or an email server), and do not integrate well with existing debug packages that a distribution might provide.

Apport is a system which:

* intercepts crashes right when they happen the first time,

* gathers potentially useful information about the crash and the OS environment,

* can be automatically invoked for unhandled exceptions in other programming languages (e. g. in Ubuntu this is done for Python),

* can be automatically invoked for other problems that can be automatically detected (e. g. Ubuntu automatically detects and reports package installation/upgrade failures from update-manager),

* presents a UI that informs the user about the crash and instructs them on how to proceed,

* and is able to file non-crash bug reports about software, so that developers still get information about package versions, OS version etc.

We are sure that this will lead to a much better level of quality assurance in the future.

If you want to make crash reports of your software even more useful when being reported through Apport, please see the [Apport developer how-to guide](https://wiki.ubuntu.com/Apport/DeveloperHowTo).

(what-does-it-look-like-for-users)=
## What does it look like for users?

The user side of apport is designed to be extremely simple and as unannoying as possible.

If any process in the system dies due to a signal that is commonly referred to as a 'crash' (segmentation violation, bus error, floating point exception, etc.), or e. g. a packaged Python application raises an uncaught exception, the apport backend is automatically invoked. It produces an initial crash report in a file in `/var/crash/` (the file name is composed from the name of the crashed executable and the user id). If the crashed process belongs to the user who is currently logged in, or it belongs to a system process and the user is an administrator, apport informs the user about the crash and offers to report the problem:

<!-- Image: apport_crash_nodetails.png -->

You can click on "Show Details..." to see what data it collected:

<!-- Image: apport_crash_details.png -->

If the user leaves the "Send error report" checkbox enabled, Apport uploads the collected information to the bug tracking system. After that it opens the packages' bug filing page with a sensible default bug title and leaves the rest of bug filing process to the web UI.


(why-is-apport-disabled-by-default)=
## Why is apport disabled by default?

Apport is not enabled by default in stable releases, even if it is installed. The automatic crash interception component of apport is disabled by default in stable releases for a number of reasons:

1. Apport collects potentially sensitive data, such as core dumps, stack traces, and log files. They can contain passwords, credit card numbers, serial numbers, and other private material.

This is mitigated by the fact that it presents you what will be sent to the bug tracker, and that all crash report bugs are private by default, limited to [the Ubuntu bug triaging team](https://launchpad.net/~ubuntu-crashes-universe). We can reasonably expect developers and technically savvy users, who run the development release, to be aware of this and judge whether it is appropriate to file a crash report. But we shouldn't assume that every Ubuntu user of stable releases is able to do so. In 12.04 and up this is transparently handled by whoopsie, see page on the [Error Tracker](https://wiki.ubuntu.com/ErrorTracker).

1. During the development release we already collect thousands of crash reports, much more than we can ever fix. Continuing to collect those for stable releases is not really useful, since

* The most important crashes have already been discovered in the development release.

* The less important ones are not suitable for getting fixed in stable releases (see [|SRU policy](https://wiki.ubuntu.com/StableReleaseUpdates)

* Asking users to send crash reports to us is insincere, since we can't possibly answer and deal with all of them.


1. Data collection from Apport takes a nontrivial amount of CPU and I/O resources, which slow down the computer and don't allow you to restart the crashed program for several seconds.

**Note** Apport does not trap SIGABRT signals. If you are getting such a signal, then please see the page on [debugging program crash](https://wiki.ubuntu.com/DebuggingProgramCrash).

(how-to-enable-apport)=
## How to enable apport

Apport itself is running at all times because it collects crash data for `whoopsie` (see page on the [Error Tracker](https://wiki.ubuntu.com/ErrorTracker)). However, the crash interception component is still disabled. To enable it permanently, do:

```none
sudo nano /etc/apport/crashdb.conf
```

... and **add a hash symbol # in the beginning** of the following line:

```none
        'problem_types': ['Bug', 'Package'],
```

To disable crash reporting just remove the hash symbol.


(im-a-developer-how-do-i-use-these-crash-reports)=
## I'm a developer. How do I use these crash reports?


(report-format)=
### Report format

apport internally uses the standard Debian control syntax for reports, i. e. keeps everything in a flat file that looks like this:

```none
DistroRelease: Ubuntu 12.04
ExecutablePath: /usr/bin/gcalctool
Package: gcalctool 5.8.24-0ubuntu2
ProcCmdline: gcalctool
ProcEnviron:
 SHELL=/bin/bash
 PATH=/usr/sbin:/usr/bin:/sbin:/bin:/usr/bin/X11:/usr/games
 LANG=de_DE.UTF-8
StackTrace:
 [...]
 #0  0x00002ae577bb37bf in poll () from /lib/libc.so.6
 No symbol table info available.
 #1  0x00002ae57786991e in g_main_context_check () from /usr/lib64/libglib-2.0.so.0
 No symbol table info available.
 [...]
CoreDump: base64
 eJzsXQmcFMXV7+XGA0dBREVoDxSPXQYEB...
```

Only a tiny subset of the available fields are shown here. Apport reports include a core dump in a compressed and encoded format, which is useful for post-mortem debugging and post-mortem generation of a symbolic stack trace.

However, when uploading the data to a bug tracking system, a different format can be used. e. g. when using [Launchpad](https://launchpad.net), the data is uploaded in Multipart/MIME format so that the small parts land directly in the bug summary and the big parts become separate bug attachments.


(fields)=
#### Fields

Some fields warrant further details:



* `SegvReason: reading NULL VMA` would mean that a NULL pointer was most likely dereferenced while reading a value.

* `SegvReason: writing unknown VMA` would mean that something was attempting to write to the destination of a pointer aimed outside of allocated memory.  (This is sometimes a security issue.)

* [SegvAnalysis](https://wiki.ubuntu.com/SegvAnalysis): when examining a Segmentation Fault (signal 11), Apport attempts to review the exact machine instruction that caused the fault, and checks the program counter, source, and destination addresses, looking for any virtual memory address (VMA) that is outside an allocated range (as reported in the [ProcMaps](https://wiki.ubuntu.com/ProcMaps) attachment).
* [SegvReason](https://wiki.ubuntu.com/SegvReason): a VMA can be read from, written to, or executed.  On a SegFault, one of these 3 CPU actions has taken place at a given VMA that either not allocated, or lacks permissions to perform the action.  For example:
* `SegvReason: executing writable VMA [stack]` would mean that something was causing code on the stack to be executed, but the stack (correctly) lacked execute permissions.  (This is almost always a security issue.)

(Tools)=


(tools)=
### Tools

There are several tools available for working with a crash report:

* **Ubuntu Bug Patterns**: [These](http://bazaar.launchpad.net/~ubuntu-bugcontrol/apport/ubuntu-bugpatterns/files) are patterns for packages (writable by Ubuntu Bug Control) that prevent bugs from being filed by apport.  Complete details are found in the [README](http://bazaar.launchpad.net/~ubuntu-bugcontrol/apport/ubuntu-bugpatterns/annotate/head%3A/README).

* **apport-unpack**: Unpack a report into single files (one per attribute). This is most useful for extracting the core dump. Please see the manpage for further details. This tool is not necessary when working with Launchpad, since it already splits the parts into separate attachments.

* **apport-retrace**: Regenerate stack traces of a report. If you supply the `-g` option, this tool will automatically download available debug symbol packages and use them to generate a symbolic stack trace. The manpage explains the functionality and all available options in detail.

* **python-problem-report**: This package ships a Python module `problem_report` which provides general dictionary access to a crash report and loading/saving methods (not specific to apport reports).

* **python-apport**: This ships a Python package `apport` which encapsulates core functionality of apport and is specific to crash and bug reports. You can use it to implement your own frontends and backends.

* **apport-collect**: This checks the source package(s) of an existing Launchpad bug, runs apport hooks for them, and uploads their collected information back to the bug report.


(how-does-it-work-internally)=
## How does it work internally?


(crash-interception)=
### Crash interception

Apport uses `/proc/sys/kernel/core_pattern` to directly pipe the core dump into
apport:

```none
$ cat /proc/sys/kernel/core_pattern
|/usr/share/apport/apport %p %s %c
$
```

Note that even if `ulimit` is set to disabled core files (by specyfing a core file size of zero using `ulimit -c 0`), apport will _still_ capture the crash.

For intercepting Python crashes it installs a `/etc/python*/sitecustomize.py` to call apport on unhandled exceptions.


(example)=
#### Example

Apport is even able to capture core files if PID 1 (Upstart) dies:

1. If Upstart detects an internal inconsistency, it raises the `SIGABRT` signal.

1. The Upstart crash handler is called on `SIGABRT`.

1. Upstart crash handler forks a child process.

1. The Upstart child process re-raises the signal which results in the child exiting abnormally.

1. The kernel detects the child process has exited abnormally and calls `apport`, piping the core file to apports standard input (due to `/proc/sys/kernel/core_pattern`).

1. `apport` writes the core file to disk in `/var/crash/`.

1. PID 1 waits for its child to terminate (which only happens once `apport` has finished writing the core file).

1. PID 1 exits.

1. kernel panics.

1. On next boot, Whoopsie will detect the crash file and process it.


(backend)=
### Backend

In order to keep the delay and CPU/IO impact as low as possible, `/usr/share/apport/apport` only collects data which has to be acquired while the crashed process still exists: information from `/proc/`_pid_, the core dump, the executable path, and the signal number. The report is written to `/var/crash/`_executable_path_`.`_uid_`.crash`.


(frontend-invocation)=
### Frontend invocation

In Gnome, `update-notifier` keeps an inotify watch on `/var/crash`. Whenever there is something new, it calls `/usr/share/apport/apport-checkreports`. If there are new reports, it calls `/usr/share/apport/apport-gtk`, which is the frontend shown in the screenshots above.

The frontend then collects additional information like package versions, package file checksums, or OS version, and calls all matching package hooks.

To disable this, you can run `gsettings set com.ubuntu.update-notifier show-apport-crashes false` (as your ordinary desktop user).


(launchpad-based-auto-retracer)=
## Launchpad-based auto-retracer

The Canonical data center runs a service which automatically retrace bugs with apport. By tagging the bugs according to architecture in Launchpad, a retrace will be done and the tag will be removed. Tags that are used are `need-i386-retrace` or `need-amd64-retrace`. See the [announcement](https://lists.ubuntu.com/archives/ubuntu-devel/2007-March/023440.html).


(per-package-apport-hooks)=
## Per-package Apport Hooks

It is possible for packages to specify information gathered from the system and included in the bug report.  These are done by apport hooks contained in packages.  For some useful examples see:

* source_xorg.py - adds additional log files and hardware details to bug reports

* usplash - ignores crashes in specific code paths

* source_totem.py - asks the reporter questions and gathers different information based on responses

in `/usr/share/apport/package-hooks`.  There is also a [list](http://wiki.ubuntu.com/Apport/PackageHooks) of packages providing apport hooks.


Please see the [Apport developer how-to guide](https://wiki.ubuntu.com/Apport/DeveloperHowTo) for further information.

If a crash or bug report is submitted through Apport, the relevant hooks will be run automatically. If you have an already reported bug that was filed without Apport, and you are interested in the information from those hooks, you can ask the bug reporter to use `apport-collect` _bugnumber_ (see [#Tools](https://help.ubuntu.com/community/#Tools)).

(use-the-source-luke)=
## Use the source, Luke!

* You can download the upstream tarball from the [Launchpad project page](https://launchpad.net/apport/+download), or the Ubuntu source tarball from the [Ubuntu archive](http://archive.ubuntu.com/ubuntu/pool/main/a/apport/).

* apport is developed with the [bazaar](http://bazaar-vcs.org) RCS on [Launchpad](https://code.launchpad.net/apport). If you want to contribute to it or develop your own system based on it, you can get your own branch with `bzr branch lp:apport` for trunk, or `debcheckout -a apport` for the Ubuntu packaging branch.

You can also [browse it online](http://bazaar.launchpad.net/~apport-hackers/apport/trunk).


(future-plans)=
## Future plans

* Various improvements to performance, better tools to work with reports, and integration of more languages (Mono/Python stack traces, assertion messages, etc.) See the relevant [specification](https://features.launchpad.net/distros/ubuntu/+spec/apport-improvements).


(further-links)=
## Further links

* The [report file data format specification](attachment:data-format.pdf).

* Original specifications: [apport design](https://wiki.ubuntu.com/AutomatedProblemReports), [User interface](https://wiki.ubuntu.com/CrashReporting)

* [Ubuntu apport bug patterns](http://bazaar.launchpad.net/~ubuntu-bugcontrol/apport/ubuntu-bugpatterns/files)


* [Whoopsie](https://wiki.ubuntu.com/ErrorTracker) is a newer Ubuntu crash submission system that doesn't require any input from the user and integrates with Apport
* Please do not hesitate to report bugs and feature requests to the [bug tracker](https://launchpad.net/apport/+bugs).

* See [Bugs/ApportRetraces](https://help.ubuntu.com/community/Bugs/ApportRetraces) for additional documentation for those triaging Apport-generated bug reports in LaunchPad, based on a [MOTU/School](https://help.ubuntu.com/community/MOTU/School) session by EmmetHikory .

* [Brian Murray](BrianMurray) gave a [class](https://wiki.ubuntu.com/MeetingLogs/devweek0909/ApportPkgHooks) at Ubuntu Developer week regarding writing package hooks.

* Integration using LaunchpadIntegration: [https://wiki.ubuntu.com/UbuntuDevelopment/Internationalisation/Coding#LPI](https://wiki.ubuntu.com/UbuntuDevelopment/Internationalisation/Coding#LPI)

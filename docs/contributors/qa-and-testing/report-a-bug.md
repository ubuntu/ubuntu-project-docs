(how-to-report-a-bug)=
# How to report a bug

```{note}
Once a bug is filed, be prepared to answer questions, provide additional details, and test fixes. Engaged reporters get bugs resolved faster. See [The Keys to Successful Bug Reporting](https://ubuntu.com/blog/the-keys-to-successful-bug-reporting).
```

## Quick start

1. **Confirm it's a bug** — not a support request, feature request, or an issue caused by unsupported software (PPAs, third-party packages, self-compiled software). See {ref}`determine-if-the-bug-is-really-a-bug`.
2. **Search for duplicates** — check the [release notes](https://documentation.ubuntu.com/release-notes/) and [Launchpad](https://bugs.launchpad.net/).
3. **Collect information** — run `ubuntu-bug <package>` (for .deb packages) or `snap report-issue <snap>` (for snaps).
4. **File the report** — provide a clear title, expected vs. actual behaviour, and reproduction steps.
5. **Stay engaged** — respond to questions from triagers and developers.

(getting-support)=
## Getting support

Not every problem is a bug. If you're unsure, or need help debugging, use:

* {ref}`Matrix channels <using-matrix>` — live chat with volunteers
* [Ubuntu Discourse](https://discourse.ubuntu.com/) — community forum
* {ref}`Community support resources <community-support>`

(how-to-report-bugs)=
## How to report bugs

Ubuntu uses {ref}`Launchpad <about-launchpad>` to track bugs. The primary tool for filing bug reports is `ubuntu-bug` (also called `apport-bug` or `apport-collect`), which collects system information and opens a report form in your browser.

For .deb packages:

```none
ubuntu-bug buggy-package-name
```

For snap packages:

```none
snap report-issue buggy-snap-name
```

Snap bug trackers are also listed on each package's page at [snapcraft.io](https://snapcraft.io/).

(create-a-launchpad-account)=
## Create a Launchpad account

You need a [Launchpad account](https://documentation.ubuntu.com/launchpad/user/YourAccount/NewAccount/) to file and comment on bugs.

(determine-if-the-bug-is-really-a-bug)=
## Determine if it's really a bug

Do **not** file a bug if you are:

* **Requesting new software** — see {ref}`New Packages <new-packages>`.
* **Requesting support** — see {ref}`community-support`.
* **Discussing features or policy** — use the [ubuntu-devel-discuss](https://lists.ubuntu.com/mailman/listinfo/ubuntu-devel-discuss) mailing list.
* **Using unsupported software** — software from PPAs, third-party packages, or self-compiled software is not supported by Ubuntu. Reproduce the issue with only supported software installed before filing a bug. If the problem only occurs with unsupported software, contact its maintainer directly. See {ref}`package-archive <package-archive>` for details on supported repositories.

(perform-a-survey-of-your-problem)=
## Check for existing reports

1. Check the [release notes](https://documentation.ubuntu.com/release-notes/) for known issues.
2. Search [Launchpad](https://bugs.launchpad.net/) for duplicate reports.

```{note}
For translation or spelling bugs, see {ref}`filing-a-translation-bug`.
```

(reporting-a-crash)=
## Reporting a crash

When an application crashes, {ref}`Apport <debugging-apport>` displays a window offering to collect information and file a report.

![Screenshot of Apport](apport-1.png)

```{note}
Install the [whoopsie](https://launchpad.net/ubuntu/+source/whoopsie) package to ensure crash reports are uploaded. It's installed by default on Ubuntu Desktop, but server users must install it manually: `sudo apt install whoopsie`.
```

(reporting-crash-in-the-development-release)=
### Development release

In the development release, Apport opens a browser window to file the report on Launchpad. The [Apport Retracing Service](https://help.ubuntu.com/community/ApportRetracingService) automatically processes the report to provide debugging information.

(reporting-a-crash-in-the-stable-release)=
### Stable release

By default, Apport uploads crash reports to the [Error Tracker](https://errors.ubuntu.com/), not Launchpad (see {lpbug}`994921`).

To file on Launchpad instead, edit `/etc/apport/crashdb.conf` and comment out:

```python
if _is_ubuntu_stable_release():
    databases["ubuntu"]["problem_types"] = ["Bug", "Package"]
```

Then file the crash report:

```none
ubuntu-bug /var/crash/FILENAME.crash
```

(reporting-a-crash-when-no-message-shows-up-and-crash-files-created)=
### Apport created a crash file but no prompt appeared

File the crash report manually:

```none
ubuntu-bug /var/crash/FILENAME.crash
```

To confirm it was uploaded to the Error Tracker, get the ID:

```none
sudo cat /var/lib/whoopsie/whoopsie-id
```

Then visit `https://errors.ubuntu.com/user/ID` (replacing `ID` with the value from the command above).

(reporting-a-crash-when-no-message-shows-up-and-crash-files-not-created)=
### Apport didn't create a crash file

Check that Apport is enabled in `/etc/default/apport`:

```none
enabled=1
```

If Apport is enabled but still not creating crash files:

* **LibreOffice crashes** — neither Apport nor LibreOffice's built-in reporter may capture these (see {lpbug}`1537566`).
* **System crashes** (freezes, lockups, logout) — see [Debugging System Crashes](https://help.ubuntu.com/community/DebuggingSystemCrash).
* **Application crashes** — see [Debugging Program Crashes](https://wiki.ubuntu.com/DebuggingProgramCrash).

(reporting-non-crash-hardware-and-desktop-application-bugs)=
## Reporting non-crash bugs

Use `ubuntu-bug` to collect information about the problematic package or process.

(collecting-information-from-a-specific-package)=
### From a specific package

Press Alt+F2, type `ubuntu-bug <package name>`, and press Enter.

![Filing a bug with the "Run Command" screen](gnome-ubuntu-bug-pkgname.png)

If you don't know which package is at fault, see [finding the right package](https://wiki.ubuntu.com/Bugs/FindRightPackage).

(collecting-information-from-a-currently-running-program)=
### From a running process

Open System Monitor, find the process ID, then run:

```none
ubuntu-bug <PID>
```

(filing-a-general-bug-against-no-particular-package)=
### When you don't know the package

First, {ref}`review potential package candidates <how-to-assign-a-bug-to-a-package>`. If you still can't identify the package, run `ubuntu-bug` without arguments — it will guide you through questions to help assign the bug.

(complete-the-bug-report-filing-process)=
## Completing the bug report

After `ubuntu-bug` collects information, a browser window opens on Launchpad.

1. **Title** — be succinct but descriptive. Example: "On noble, foo fails to launch when started from the application icon".

   ![Launchpad asking for a bug title](bug-title2.png)

2. **Check for duplicates** — Launchpad searches for similar reports. If one matches, click it and confirm. Otherwise, file a new report.

   ![Launchpad search results about the bug title](bug-search.png)

3. **Describe the bug** — include:
   * What you expected to happen
   * What actually happened
   * Minimal reproduction steps (starting with "start the program")

4. **Additional options:**
   * **Security vulnerability** — check only if the bug could be exploited to compromise security.
   * **Tags** — add relevant {ref}`tags <bug-tags>`. Leave predefined values as-is.
   * **Attachments** — screenshots, logs, or sample files that demonstrate the issue. For kernel bugs, `lspci` output is collected automatically — no need to attach it separately.

   ![Launchpad presenting extra options](extra-options2.png)

5. Click **Submit bug report**.

(tips-and-tricks)=
## Tips and tricks

(filing-bugs-when-offline-or-using-a-headless-setup)=
### Filing from an offline or headless system

**For crashes:** copy the `.crash` file from `/var/crash/` to a connected machine and run:

```none
ubuntu-bug FILENAME.crash
```

**For other bugs:** save the report on the problem machine:

```none
ubuntu-bug PACKAGENAME --save FILENAME.apport
```

Copy the file to a connected machine and file it:

```none
ubuntu-bug FILENAME.apport
```

Do not attach `.apport` or `.crash` files directly to a report — use the commands above so the data is processed correctly.

(filing-bugs-manually-at-launchpad-net)=
### Filing manually at Launchpad

If `ubuntu-bug` doesn't work, file directly at [bugs.launchpad.net/ubuntu/+filebug](https://bugs.launchpad.net/ubuntu/+filebug). This method is discouraged because the report may lack important system information. Use `ubuntu-bug` whenever possible.

You can also use a direct URL:

```none
https://bugs.launchpad.net/ubuntu/+source/PACKAGENAME/+filebug?no-redirect
```

(error-the-launchpadlib-python-module-is-not-installed)=
### Error: launchpadlib Python module not installed

Install the required package:

```none
sudo apt install python3-launchpadlib
```

(package-libreoffice-not-installed-and-no-hook-available-ignoring)=
### Error: Package libreoffice not installed and no hook available

Install LibreOffice:

```none
sudo apt install libreoffice
```

(non-crash-userspace-bugs)=
### Capturing non-crash issues

A screenshot or [screencast](https://help.ubuntu.com/community/Screencast) can help demonstrate the problem.

(translation)=
(filing-a-translation-bug)=
### Translation bugs

File translation bugs against the [Ubuntu Translations project](https://bugs.launchpad.net/ubuntu-translations) for:

* Wrong translations or spelling mistakes in non-English languages
* Spellchecker or language support errors
* Strings not available for translation in [Launchpad Translations](https://translations.launchpad.net/ubuntu)
* Translations not updated in Ubuntu language packs
* Duplicate translation templates

If unsure, [contact the Translations team](https://wiki.ubuntu.com/Translations/Contact).

(bug-reporting-etiquette)=
## Bug reporting etiquette

(all-bug-reports)=
### General guidelines

* **One issue per report.** Don't combine multiple problems (e.g. suspend and hibernate) into a single report.
* **Search before filing.** Check for existing reports, but don't speculate about duplicates — file a new report if you're unsure.
* **Include all requested information upfront.** See {ref}`how-to-debug-an-apport-crash`. Missing information is the top reason bugs don't get triaged.
* **Test the latest version.** Try the latest upstream release and the latest development release before filing.
* **No "me too" comments.** If you have the same bug, file a separate report with your own debugging information.
* **Don't post log URLs.** Paste the full content directly into the report — don't link to pastebin or similar services.
* **Don't compress attachments.** Launchpad accepts large attachments.
* **Don't reopen fixed bugs.** If a problem reoccurs in a newer version, file a new report.
* **Be objective.** Provide facts and technical impact, not opinions or complaints.
* **Respect triagers and developers.** Many are volunteers. If asked for information, provide it without arguing.
* **Don't run `apport-collect` on other people's reports** unless asked by a triager.

(hardware-bug-reports-linux-kernel-xorg-sound-etc)=
### Hardware bug reports

* **Update BIOS and firmware first.** Outdated firmware causes many hardware issues. See [BIOS Update](https://help.ubuntu.com/community/BIOSUpdate).
* **One report per hardware configuration.** Hardware bugs are specific to the combination of components.
* **Don't comment on others' hardware reports.** File your own report — even with similar hardware, the root cause may differ.

(getting-advice)=
## Getting advice

Still have questions? Ask in {matrix}`Matrix <discuss>`.

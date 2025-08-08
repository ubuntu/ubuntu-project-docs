(bug-types)=
# Bug types

## Apport reports

[Apport](https://wiki.ubuntu.com/Apport) reports are bugs reported via the
Apport bug reporting program. Reporting bugs using Apport is the preferred way
of reporting a bug since it gives the developers a lot of information about the
affected system. Some programs have hooks for Apport, which adds more information
when reporting a bug.

You can recognize Apport bugs by the added list of system information in their
description. This information can usually be found in the attachments.


(apport-crash-reports)=
### Apport crash reports

A considerable number of Apport bugs concern program crashes, which are reported
semi-automatically and get pre-processed automatically by bots in the Canonical
data center. These bots try to generate a fully symbolic stack trace and check
for duplicates.

In Feisty and early Gutsy, those bugs were public. However, this created a
privacy problem since core dumps and stack traces may contain sensitive
information. Also, crash reports generate a lot of bug mail noise. With the
automatic check for duplicates, a fair amount of reported bugs are redundant for
triagers.

Since Gutsy, these problems [have been mitigated](https://wiki.ubuntu.com/CrashReporting):
bugs are filed with the "private" flag enabled, i.e. only the reporter and
subscribers can see it. The reprocessing bots subscribe the
{ref}`bug-control-team` team without sending emails to the team members.

Crash bugs differ from other bugs in two important aspects: they need to be
checked for sensitive data, so there is no initial bug mail for them until they
become public. Triagers should check the following things:

* If the crash still has a `CoreDump.gz` attachment, then it was not possible
  to automatically get a fully symbolic stack trace and check for duplicates. In
  this case, the bug will be tagged with
  [`apport-failed-retrace`](https://bugs.launchpad.net/ubuntu/+bugs?field.tag=apport-failed-retrace).
  
  If the stack trace looks good enough, the `CoreDump.gz` attachment should be
  removed with the {guilabel}`edit` link in the attachment box.
  
  If the retrace failed completely, mark the bug as *Invalid* and ask the
  reporter to refile the bug if the crash can be reproduced.
  
  **Never mark a bug containing a `Coredump.gz` attachment as public.**

* If there is no `Stacktrace.txt` (retraced) attachment, it is likely the
  `CoreDump.gz` attachment is broken.

* Check if any stack trace attachments (original stack traces, `Stacktrace.txt`
  (retraced) and `ThreadStacktrace.txt` (retraced)) have anything that looks
  like sensitive data passed as function arguments. Examples are passwords,
  things that look like bank account numbers, CSS keys, user names, server
  names, etc. If you don't find anything, you may mark the bug as public ("This
  report is public/private" in the bug report). This is not *required* though,
  it is fine to keep the bug private throughout its lifetime.

Except for those privacy issues, crash reports should be handled like normal
bugs in terms of duplicate searching/marking, upstream forwarding, etc.


## Feature requests

If the bug report is actually a feature request, there are two possibilities.

1. If the requested enhancement is small and well-defined and/or the suggestion
   concerns an upstream project, the *Importance* of the bug should be set to
   *Wishlist*. When the report is complete, the status should be set to
   *Triaged*. Only the members of the
   [Ubuntu Bug Control](https://launchpad.net/~ubuntu-bugcontrol) team can do
   so. If you're not a member you need to ask someone who is to do it for you.
   Paste the bug number in the `#ubuntu-devel` Matrix channel and say you think
   the bug should be set to *Wishlist*. Someone will notice and set it for you,
   although not necessarily immediately.

   Bugs requesting a feature concerning upstream projects should be forwarded
   upstream. Forwarding upstream is explained at
   {ref}`forward-bug-upstream`.

1. If the request is abstract and/or suggesting a large change the bug should
   be closed as *Invalid* while posting a message pointing the user to the
   appropriate upstream or to the user forums.

A standard response you can use is:

```none
Thank you for taking the time to make Ubuntu better. Since what you submitted
is not a bug or a problem, but rather an idea to improve Ubuntu, you are invited
to discuss the idea with other Ubuntu community members in the many public
forums. Public discussion of ideas improves the likelihood of adoption. Thanks
for taking the time to share your opinion!
```


## Regressions

A regression is a bug introduced after an update. These bugs are especially
important because if something breaks that used to work it causes frustration
for software users. Rergressions can be more obvious and painful for users than
bugs. To track regressions we use tags. Make sure to use the tags when doing
triage!

`regression-release`
: A regression in a new stable release or a development release. This may be a
  bug in a single package or functionality lost when changing the default
  application.

`regression-update`
: A regression introduced by an updated package in the stable release.

`regression-proposed`
: A regression introduced by a package in `-proposed`.

`regression-retracer`
: Used by the retracer when it finds a bug that has a similar trace to a
  previously-closed bug.

Once tagged, the bugs will appear on the
[regression tracking page](http://qa.ubuntu.com/reports/regression/regression_tracker.html)
and will from there be escalated to the development teams. See
[QATeam/RegressionTracking](https://wiki.ubuntu.com/QATeam/RegressionTracking)
for more information.


## Bug reports not in English

Bug reports should be in English since that is the most commonly used language
by Ubuntu developers and bug triagers. If a bug report is not in English, ask
the reporter to translate their bug and any error messages into English.

If you are concerned that the bug report is critical and needs to be translated
quickly, e-mail the [Ubuntu translators mailing list](https://lists.ubuntu.com/mailman/listinfo/ubuntu-translators)
for help in getting the bug translated.


## Special types of bugs

Most bugs are code or packaging defects, but some groups within Ubuntu also use
bugs for other things. Careful attention must be paid to these bugs so as not
to disrupt team processes. These classes of bugs have special rules and
different meanings for the statuses. They may even have different meanings
depending on where Ubuntu is in its release cycle.

```{warning}
Unless you are familiar with the specific process in question, changes to these
bugs are likely to be problematic. If in doubt, don't change them!
```


### Developer Process Bugs

You should generally not change bugs of this type *unless* you are working with
a developer/packager.

Bugs in this category can have subjects like:  

* Please merge \<package\> from Debian unstable (main)  
* Please sync \<package\> from Debian unstable (main)  
* Please remove \<package\> from the Ubuntu archives  
* Please promote \<package\> to \<component\>  
* Please demote \<package\> to \<component\>  
* Main inclusion report (MIR)  

Bugs in this category will have **any** of the following teams subscribed:  

* [Ubuntu Sponsors](https://bugs.launchpad.net/~ubuntu-sponsors/)  
* [Ubuntu Package Archive Administrators](https://bugs.launchpad.net/~ubuntu-archive)  
* [MOTU Release Team](https://bugs.launchpad.net/~motu-release)  
* [Ubuntu Release Team](https://bugs.launchpad.net/~ubuntu-release)  
* [MIR team](https://bugs.launchpad.net/~ubuntu-mir)

For packages in `universe`/`multiverse`, see the
[Sponsors Queue](https://wiki.ubuntu.com/MOTU/Sponsorship/SponsorsQueue) page.


### needs-packaging bugs

A "needs-packaging" bug is a subset of the Developer Process bugs above: it is
not really a bug, but a request to add a new package to Ubuntu. You may find
them with a subject like: `[needs-packaging] <package>`, or with either the
description or summary requesting that a package be created. These bugs are
used to track software requested for inclusion in Ubuntu. For these bugs:

* Read and follow the instructions on [Sponsor Queue](https://wiki.ubuntu.com/MOTU/Sponsorship/SponsorsQueue).

* Check if it is already in Ubuntu via [`packages.ubuntu.com`](http://packages.ubuntu.com),
  or by running `rmadison <package>`.

  * If it **is** in the Archive, mark it as *Invalid*, and add a comment
    explaining your action.

  * If it **is not** in Ubuntu, then check Debian via [`packages.debian.org`](http://packages.debian.org),
    or by running `rmadison -u debian <package>`.
    
    * If it is in Debian, mark it as *Invalid*, and add a comment stating:

      ```none
      Packages for this software appear to exist in Debian already. Ubuntu has
      semi-automatic tools to sync new packages from Debian so it will most
      likely appear in the next Ubuntu release.
      ```

* Next, check [the Debian bug tracker](http://bugs.debian.org) or
  [Work-Needing and Prospective Packages](http://www.debian.org/devel/wnpp/)
  for an Intent To Package (ITP) or Request For Package (RFP) for this package.
  If you find such a request, add an upstream bug watch for it, and continue on.

* Check for the upstream licenses:

  * If license info and upstream URL are included, add a comment with the
    license types and the links to them upstream.
  * If this information is not included, or you cannot find it, add a request
    for the reporter to link the licenses in.

* Now you can add the tag "needs-packaging" and mark the bug as *Triaged*.

```{warning}
Not all package names are intuitive! You should also use the package description
to help guide you.
```

```{warning}
**Never** set these bugs to *Confirmed*, unless you are working with a package
maintainer and have been asked to do so.
```

```{warning}
The bug should remain on *New*, or *Incomplete* status until all prerequisites
are completed.
```

If you are unsure whether the bug you are looking at fits into one of these
categories, you can ask in `#ubuntu-bugs` or `#ubuntu-motu` on IRC.


### Security bugs

The [Security Team](https://wiki.ubuntu.com/SecurityTeam) uses a similar but
slightly different process for Triaging bugs. If you think a bug may be a
security issue or are triaging a bug flagged as a security issue, read
[Security Team/Bug Triage](https://wiki.ubuntu.com/SecurityTeam/BugTriage)
before you proceed.


### Translation bugs and Launchpad integration

The Ubuntu [Translations team](https://wiki.ubuntu.com/Translations) has a
separate Launchpad project for tracking translation bugs. Launchpad integration
is also tracked by this project.

All translation and Launchpad integration bugs should have a task against the
[`ubuntu-translations`](https://launchpad.net/ubuntu-translations) project. If a
translation bug doesn't have such a task, add one:

1. Click on the {guilabel}`Also affects project` link.

1. *If necessary*, click the {guilabel}`Choose another project` link between the
   parentheses (after the project name), when that project name is not "Ubuntu
   Translations".

1. Enter "ubuntu-translations" in the project name box and click {guilabel}`Continue`.

If the bug is a translation error, the {guilabel}`ubuntu-translations` task
should be assigned to the proper translation team; `ubuntu-l10n-LC`, where `LC`
is the language code according to the ISO 639-2 standard, or ISO 639-3 for
languages that are not in the previous standard.

The [Translations/Handling Bugs](https://wiki.ubuntu.com/Translations/KnowledgeBase/HandlingBugs)
wiki page contains a detailed overview of the
[Translation team bug policy](https://wiki.ubuntu.com/Translations).

Apart from opening the {guilabel}`ubuntu-translations` task to let the
[Translations team](https://wiki.ubuntu.com/Translations) know the bug exists,
the bug should be handled like any other bug. When its status in the `ubuntu`
project is {ref}`set to Triaged <bug-status>` they know the report is ready
for them to work on.


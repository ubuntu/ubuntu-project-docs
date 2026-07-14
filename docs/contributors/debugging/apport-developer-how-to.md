(apport-developer-how-to)=
# Apport developer how-to

```{admonition} Migrated content
This page has been migrated from the Ubuntu Wiki "as is".
It may contain inaccuracies, may not be up-to-date, and may require
formatting, language, or other corrections.
```



(how-to-use-apport-in-your-programs)=
## How to Use Apport in your Programs

By default, apport provides the following functionality for all programs in Ubuntu:

* When a program segfaults, apport stores a persistent crash report in `/var/crash` which can be later analyzed even if the bug cannot be reproduced by a developer

* Relevant information about the state of the system and installed software is automatically included in the report

* Apport can semi-automatically attach the crash report to a bug report in Launchpad

* For C and C++ programs, the [retracer](https://wiki.ubuntu.com/Bugs/ApportRetraces) will automatically decode the stack trace in the crash report and attach the decoded stack trace to the bug report. See [bug #252046](https://bugs.launchpad.net/ubuntu/+source/gvfs/+bug/252046) as an example what this looks like.


(package-hooks)=
### Package Hooks

In addition to the generic information apport collects, arbitrary package-specific data can be included in the report by adding package hooks.  For example:

* Relevant log files
* Configuration files
* Current system state

Hooks can also cause a crash to be ignored, or the report suppressed with an explanation.

Since Ubuntu 9.10 ("Karmic"), hooks can also ask interactive questions, to get further information from the reporter. Currently supported are "yes/no" questions, multiple choice questions, file selector, and an information message box.

To create a hook, have your package install a file `/usr/share/apport/package-hooks/<binarypackagename>.py` or `/usr/share/apport/package-hooks/source_<sourcepackagename>.py`.  The hook will be used whenever apport logs a report for the specified package.  Here's a simple example of a hook:

```python
from apport.hookutils import *

def add_info(report, ui=None):
    attach_file_if_exists(report, '/var/log/foo.log', key='FooLog')
    attach_related_packages(report, ['hello', 'hello-debhelper'])
    report['SuspiciousXErrors'] = xsession_errors(re.compile('CRITICAL.*assertion.*failed'))
    report['SecretMessage'] = 'my hook was here'
```

'report' is a Python dictionary which can be used to store arbitrary data using a string key (alphanumerical or dots (.), hyphens (-) and underscores (_)).

To test a package hook with a test package build, you can set APPORT_DISABLE_DISTRO_CHECK in your environment to force apport to create a report even though your package is not (yet) official.

For complete instructions, see `/usr/share/doc/apport/package-hooks.txt.gz` ([online version](http://bazaar.launchpad.net/%7Eapport-hackers/apport/trunk/annotate/head%3A/doc/package-hooks.txt)).

For a list of convenience functions, refer to the `apport.hookutils` module:

```bash
pydoc apport.hookutils

```

It provides ready made and safe functions for many standard situations,
such as getting a command's output, attaching a file's contents,
attaching hardware related information, etc.

Hooks can also perform interactive actions.  For this see the `apport.ui` module:

```bash
pydoc apport.ui

```

[Brian Murray](https://wiki.ubuntu.com/BrianMurray) gave a [class](https://wiki.ubuntu.com/MeetingLogs/devweek0909/ApportPkgHooks) at Ubuntu Developer week regarding writing package hooks.


(problemtype)=
#### ProblemType

By the time a package hooks `add_info()` function gets called,
apport will likely have already determined the _type_ of the problem
being reported. It does this by setting the `ProblemType` key in the
`report` dictionary passed to `add_info()`.

Possible values of `ProblemType`:

* `Bug`
   The user has run `ubuntu-bug` manually to report an issue.

* `Crash`
   Apport automatically detected a program crash.

* `Hang`
   Apport automatically detected a program has stopped responding.

* `Package`
   Apport automatically detected a program in a package failed to install/upgrade correctly.

* `KernelOops`
   Apport detected that the kernel encountered a situation that should not have arisen (non fatal).

* `KernelCrash`
   Apport detected that the kernel crashed (on a previous boot).

To check the value of `ProblemType`:

```python
  if report.get('ProblemType', '') == 'Crash':
      # handle crash scenario
  elif report.get('ProblemType', '') == 'Bug':
      # handle bug scenario
  else:
      # handle remaining scenarios
```


(notes)=
##### Notes

* `Crash` bug reports are private by default. All other `ProblemType`s are public by default.

* `Crash` bug reports are suppressed post-release (the apport configuration file is automatically modified to disable collection of `Crash` bugs).


(advice)=
##### Advice

* Only ask interactive questions if really necessary.

* Keep questions brief yet easy to understand.

* Provide sensible default values.

* If appropriate, provide a list of permissible values using apports ``ui.choice()`` facility.

* Test your hook thoroughly in all possible scenarios; apport _is_
   able to cope with a broken hook, but if your hook doesn't function
   correctly, it will not be able to gather the required information!

* Do not annoy the user with lots of questions if you want the problem to be reported!!


(general-hooks)=
### General Hooks

These are the same as package hooks, but apply to all packages.  They can be used, for example, to implement a 'taint check' which reports on whether certain problematic software is installed, regardless of which program is misbehaving.  They are installed in `/usr/share/apport/general-hooks/*.py`.

For complete instructions, see `/usr/share/doc/apport/package-hooks.txt`


(symptoms)=
### Symptoms

In some cases it is quite hard for a bug reporter to figure out which package
to file a bug against, especially for functionality which spans multiple
packages.  For example, sound problems are divided between the kernel, alsa,
pulseaudio, and gstreamer.

Apport supports an extension of the notion of package hooks to do an
interactive "symptom based" bug reporting. Calling the UI with just "-f" and
not specifying any package name shows the available symptoms, the user selects
the matching category, and the symptom scripts can do some question & answer
game to finally figure out which package to file it against and which
information to collect. Alternatively, the UIs can be invoked with "-s
symptom-name".

For instructions, see `/usr/share/doc/apport/symptoms.txt` ([online version](http://bazaar.launchpad.net/%7Eapport-hackers/apport/trunk/annotate/head%3A/doc/symptoms.txt)).

In Ubuntu, symptoms are shipped in the
[apport-symptoms](https://code.launchpad.net/~ubuntu-dev/apport/apport-symptoms)
package.


(bug-patterns)=
### Bug patterns

Apport can suppress reports for bugs which have already been reported. Sometimes a bug affects so many people that we get hundreds of duplicates in a matter of days, which both creates a lot of needless reporting, triaging, and retracing work. In those cases, and when the bug can be uniquely identified with regular expressions on the apport report keys or file attachments, a "bug pattern" should be created which will prevent Apport from reporting the bug in the first place, and instead guide the user to the already existing bug page.

To avoid inventing a new file format and to be able to extend the
functionality in the future (e. g. other operators than just regexp
matching) the bug patterns are stored in an XML file.

The general syntax is:

```text
 root element := <patterns>
 patterns := <pattern url="http://bug.url"> *
 pattern := <re key="report_key">regular expression*</re>
```

For example:

```xml
<?xml version="1.0"?>
 <patterns>
     <pattern url="https://launchpad.net/bugs/1">
         <re key="Foo">ba.*r</re>
     </pattern>
     <pattern url="https://launchpad.net/bugs/2">
         <re key="Foo">write_(hello|goodbye)</re>
         <re key="Package">^\S* 1-2$</re> <!-- test for a particular version -->
     </pattern>
 </patterns>
```

The bug patterns are publicly accessible at [http://people.canonical.com/~ubuntu-archive/bugpatterns/](http://people.canonical.com/~ubuntu-archive/bugpatterns/), where Apport (when running on the client side) will check for them. They are maintained in a [bzr branch](https://code.launchpad.net/~ubuntu-bugcontrol/apport/ubuntu-bugpatterns) accessible to the [Ubuntu bug control](https://launchpad.net/~ubuntu-bugcontrol/) team, and copied to people.canonical.com every 15 minutes.

The [bug patterns bzr branch](https://code.launchpad.net/~ubuntu-bugcontrol/apport/ubuntu-bugpatterns) also includes a tool, test-local, for testing bug patterns.  Using the above example you can use **test-local 2** and the Apport data from bug 2 will be downloaded and checked using your local copy of the bug patterns.  Additionally, duplicate bugs will be checked so you will know whether or not the pattern could use expanding.


(custom-invocation)=
### Custom Invocation

Apport needs to be "triggered" by something to create a report. For real
crashes, that is the kernel itself (`/proc/sys/kernel/core_pattern`), for Python
scripts this is a fallback exception handler in `/etc/python2.5/sitecustomize.py`.

For still greater flexibility, apport can be invoked explicitly under other
conditions, to trap and report on custom events, even if no signal-driven crash
(such as a segfault) has occurred.  For example, GCC can trap internal compiler
errors and calls `/usr/share/apport/gcc_ice_hook` if one happens; if apt sees
that a package fails to install, it calls `/usr/share/apport/package_hook`.

These scripts should ensure that apport is enabled (as it is turned off for stable releases) before executing.  This can be done by importing apport.packaging and using apport.packaging.enabled().
These scripts should create minimal `apport.Report()` object and set the
`Package` and `SourcePackage` fields correctly, so that any matching package
hook will be triggered as well. Finally, it should write the report to a file.

Additional information collection can either happen

* directly in the script, if it needs to be done synchronously when the script is called, or

* in a separate package hook, in which case the additional information collection will be done asynchronously when the user gets notified about the problem and decides to report it.

In general you should collect as much information as possible in package hooks, especially when they require expensive operations. That way, the calling program does not have to block very long, and information is not collected if the user does not want to report a bug at all.

For an asynchronous script, see `/usr/share/apport/kernel_hook` and the accompanying package hook `/usr/share/apport/package-hooks/source_linux.py`. For a synchronous script, see `/usr/share/apport/gcc_ice_hook` (this also shows how to read bulk data directly from stdin).


(third-party)=
(applications-not-included-in-ubuntus-repositories-but-hosted-on-launchpad)=
### Applications not included in Ubuntu's repositories but hosted on Launchpad

If you're using Launchpad as a bug tracker, you can install Apport hooks in your application even if your application is not included in Ubuntu repositories.

1. Create an Apport hook named `/usr/share/apport/package-hooks/<binarypackagename>.py` or `/usr/share/apport/package-hooks/source_<sourcepackagename>.py` as described previously. In the add_info function, add this code:

```python
if not apport.packaging.is_distro_package(report['Package'].split()[0]):
    report['CrashDB'] = '<packagename>'

```

1. Create a configuration file named `<packagename>`-crashdb.conf in /etc/apport/crashdb.conf.d/ with this content:

```python
<packagename> = {
 'impl' : 'launchpad',
 'project' : '<packagename>',
 'bug_pattern_base' : None,
 }

```

Obviously, you should replace `<packagename>` with the name of your package (without < and >).  **`<packagename>` cannot have any hyphen '-' characters in it.**  Replace them with underscores '_'.  It is also important that the `<packagename>` in the crashdb.conf file match the `<packagename>` in the Python file.

Once the package is included in Ubuntu's repositories, Apport will know to report bugs to Ubuntu's bug tracker. For an example of an implementation of this, see /usr/share/apport/package-hooks/source_ubuntuone-client.py and /etc/apport/crashdb.conf.d/ubuntuone-client-crashdb.conf


(interactive-feedback)=
### Interactive Feedback

Apport is able to prompt the user by asking them questions.


(yes-no-question)=
#### Yes/No Question

```python
def add_info(report, ui):

    attach_file = False

    if ui and ui.yesno('Attach some file?') == True:
        attach_file = True

    if attach_file == True:
        # user wants file to be attached
```


(choice-list)=
#### Choice List

The pseudo code below shows how to handle choices; if the response from
`ui.choice()` is not `None`, it will be the zero-based index into the
list passed as the second argument to `ui.choice()`:

```python
def add_info(report, ui):

    attach_file = False

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday' ]

    response = ui.choice('What day is it?', days)

    if response == None:
        # user cancelled
        pass
    elif 0 in response:
        # 'Monday' selected
    elif 1 in response:
        # 'Tuesday' selected
    ...
    elif 6 in response:
        # 'Sunday' selected
```


(skeleton-for-a-package-hook)=
### Skeleton for a Package Hook

```python
from apport.hookutils import *
import apport.packaging

msg = \
"""

The contents of file 'some-file' may help developers diagnose your bug
more quickly. However, if you have changed it, it may contain
sensitive information.

Do you want to include the files in your bug report?
(you will be able to review the data before it is sent)

"""

def add_info(report, ui):
    attach_files = False
    problem_type = report.get('ProblemType', '')

    if problem_type == 'Bug' and ui:
        # interactively ask the user a question and change behaviour based on their response.
        if ui.yesno(msg) == None:
            # user decided to cancel
            raise StopIteration

        # user is allowing files to be attached.
        attach_files = True

    elif problem_type == 'Crash':
        # crash bugs are private by default
        attach_files = True

    if attach_files == False:
        # do not attach any files
        return

    attach_file(report, '/etc/foo')
    attach_file_if_exists(report, '/var/foo.log')
```


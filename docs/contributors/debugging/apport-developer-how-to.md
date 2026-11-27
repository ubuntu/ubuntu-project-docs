(apport-developer-how-to)=
# Apport developer how-to


(how-to-use-apport-in-your-programs)=
## How to use Apport in your programs

By default, Apport provides the following functionality for all programs in Ubuntu:

* When a program segfaults, Apport stores a persistent crash report in `/var/crash`, which can be analyzed later even if a developer can't reproduce the bug.

* Relevant information about the state of the system and installed software is automatically included in the report.

* Apport can semi-automatically attach the crash report to a bug report in Launchpad.

* For C and C++ programs, the retracer automatically decodes the stack trace in the crash report and attaches the decoded stack trace to the bug report. See {lpbug}`252046` for an example of what this looks like.


(package-hooks)=
### Package hooks

In addition to the generic information Apport collects, package hooks can add arbitrary package-specific data to the report. For example:

* Relevant log files
* Configuration files
* Current system state

Hooks can also cause a crash to be ignored, or the report to be suppressed with an explanation.

Hooks can also ask interactive questions to get further information from the reporter. Apport supports yes/no questions, multiple choice questions, a file selector and an information message box.

To create a hook, have your package install a file `/usr/share/apport/package-hooks/<binarypackagename>.py` or `/usr/share/apport/package-hooks/source_<sourcepackagename>.py`. The hook is used whenever Apport logs a report for the specified package. Here's a simple example of a hook:

```python
import re

from apport.hookutils import *


def add_info(report, ui=None):
    attach_file_if_exists(report, '/var/log/foo.log', key='FooLog')
    attach_related_packages(report, ['hello', 'hello-debhelper'])
    report['SuspiciousXErrors'] = xsession_errors(re.compile('CRITICAL.*assertion.*failed'))
    report['SecretMessage'] = 'my hook was here'
```

`report` is a Python dictionary that stores arbitrary data under string keys. Keys can contain letters, numbers, dots (`.`), hyphens (`-`) and underscores (`_`).

To test a package hook with a test package build, set `APPORT_DISABLE_DISTRO_CHECK` in your environment. This forces Apport to create a report even though your package is not (yet) official.

For complete instructions, see [`package-hooks.md`](https://github.com/canonical/apport/blob/main/doc/package-hooks.md) in the Apport source.

For a list of convenience functions, refer to the `apport.hookutils` module:

```none
$ pydoc3 apport.hookutils
```

It provides ready-made and safe functions for many standard situations, such as getting a command's output, attaching a file's contents and attaching hardware-related information.

Hooks can also perform interactive actions. For this, see the `apport.hook_ui` module:

```none
$ pydoc3 apport.hook_ui
```


(problemtype)=
#### ProblemType

By the time a package hook's `add_info()` function gets called, Apport has likely already determined the *type* of the problem being reported. It does this by setting the `ProblemType` key in the `report` dictionary passed to `add_info()`.

Possible values of `ProblemType`:

* `Bug`: The user ran `ubuntu-bug` manually to report an issue.

* `Crash`: Apport automatically detected a program crash.

* `Hang`: Apport automatically detected that a program stopped responding.

* `Package`: Apport automatically detected that a package failed to install or upgrade correctly.

* `KernelOops`: Apport detected that the kernel encountered a situation that should not have arisen (non-fatal).

* `KernelCrash`: Apport detected that the kernel crashed (on a previous boot).

* `RecoverableProblem`: A program reported an error that it can recover from, through `/usr/share/apport/recoverable_problem`.

To check the value of `ProblemType`:

```python
if report.get('ProblemType', '') == 'Crash':
    ...  # handle the crash scenario
elif report.get('ProblemType', '') == 'Bug':
    ...  # handle the bug scenario
else:
    ...  # handle the remaining scenarios
```


(notes)=
##### Notes

* `Crash` bug reports are private by default. All other problem types are public by default.

* On stable releases, Apport doesn't file `Crash` reports on Launchpad. There, the `ubuntu` crash database in `/etc/apport/crashdb.conf` only accepts `Bug` and `Package` reports.


(advice)=
##### Advice

* Only ask interactive questions if really necessary.

* Keep questions brief yet easy to understand.

* Provide sensible default values.

* If appropriate, provide a list of permissible values using Apport's `ui.choice()` facility.

* Test your hook thoroughly in all possible scenarios. Apport *is* able to cope with a broken hook, but if your hook doesn't work correctly, it can't gather the required information.

* Don't ask so many questions that users give up on reporting the problem.


(general-hooks)=
### General hooks

These are the same as package hooks, but apply to all packages. They can be used, for example, to implement a "taint check" that reports whether certain problematic software is installed, regardless of which program is misbehaving. They are installed in `/usr/share/apport/general-hooks/*.py`.

For complete instructions, see [`package-hooks.md`](https://github.com/canonical/apport/blob/main/doc/package-hooks.md) in the Apport source.


(symptoms)=
### Symptoms

In some cases it is quite hard for a bug reporter to figure out which package to file a bug against, especially for functionality that spans multiple packages. For example, sound problems are divided between the kernel, ALSA, PipeWire and GStreamer.

Apport extends the notion of package hooks to interactive, "symptom based" bug reporting. Calling the UI with just `-f` and no package name shows the available symptoms. The user selects the matching category, and the symptom scripts can ask questions to figure out which package to file the bug against and which information to collect. Alternatively, the UIs can be invoked with `-s <symptom-name>`.

For instructions, see [`symptoms.md`](https://github.com/canonical/apport/blob/main/doc/symptoms.md) in the Apport source.

In Ubuntu, symptoms are shipped in the [apport-symptoms](https://git.launchpad.net/apport-symptoms) package.


(bug-patterns)=
### Bug patterns

Apport can suppress reports for bugs which have already been reported. Sometimes a bug affects so many people that we get hundreds of duplicates in a matter of days, which creates a lot of needless reporting, triaging and retracing work. In those cases, and when the bug can be uniquely identified with regular expressions on the Apport report keys or file attachments, create a "bug pattern". It prevents Apport from reporting the bug in the first place and instead guides the user to the existing bug page.

To avoid inventing a new file format and to be able to extend the functionality in the future (for example, other operators than just regular expression matching), the bug patterns are stored in an XML file.

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

The bug patterns are publicly accessible at <https://people.canonical.com/~ubuntu-archive/bugpatterns/>, where Apport (when running on the client side) checks for them. They are maintained in a [Git repository](https://git.launchpad.net/~ubuntu-bugcontrol/apport/+git/ubuntu-bugpatterns) accessible to the [Ubuntu Bug Control](https://launchpad.net/~ubuntu-bugcontrol/) team, and copied to people.canonical.com every 15 minutes.

The bug patterns repository also includes a tool, `test-local`, for testing bug patterns. Using the above example, you can run `test-local 2`, and the Apport data from bug 2 is downloaded and checked using your local copy of the bug patterns. Duplicate bugs are checked as well, so you know whether the pattern could use expanding.


(custom-invocation)=
### Custom invocation

Apport needs to be "triggered" by something to create a report. For real crashes, that is the kernel itself (`/proc/sys/kernel/core_pattern`). For Python programs, it is the `apport_python_hook` exception handler, which the system's `sitecustomize.py` installs.

For still greater flexibility, Apport can be invoked explicitly under other conditions, to trap and report on custom events, even if no signal-driven crash (such as a segfault) has occurred. For example, GCC can trap internal compiler errors and calls `/usr/share/apport/gcc_ice_hook` if one happens. If APT sees that a package fails to install, it calls `/usr/share/apport/package_hook`.

These scripts should ensure that Apport is enabled (as it is turned off for stable releases) before executing. Check this with `apport.packaging.enabled()`. The scripts should create a minimal `apport.Report()` object and set the `Package` and `SourcePackage` fields correctly, so that any matching package hook is triggered as well. Finally, they should write the report to a file.

Additional information collection can either happen:

* directly in the script, if it needs to be done synchronously when the script is called, or

* in a separate package hook, in which case the additional information collection is done asynchronously when the user gets notified about the problem and decides to report it.

In general, you should collect as much information as possible in package hooks, especially when it requires expensive operations. That way, the calling program does not have to block for long, and information is not collected if the user does not want to report a bug at all.

For an asynchronous script, see `/usr/share/apport/kernel_oops` and the accompanying package hook `/usr/share/apport/package-hooks/source_linux.py`. For a synchronous script, see `/usr/share/apport/gcc_ice_hook` (this also shows how to read bulk data directly from stdin).


(applications-not-included-in-ubuntus-repositories-but-hosted-on-launchpad)=
### Applications not included in Ubuntu's repositories but hosted on Launchpad

If you're using Launchpad as a bug tracker, you can install Apport hooks in your application even if your application is not included in Ubuntu repositories.

1. Create an Apport hook named `/usr/share/apport/package-hooks/<binarypackagename>.py` or `/usr/share/apport/package-hooks/source_<sourcepackagename>.py` as described previously. In the `add_info()` function, add this code:

   ```python
   if not apport.packaging.is_distro_package(report['Package'].split()[0]):
       report['CrashDB'] = '<packagename>'
   ```

1. Create a configuration file named `<packagename>-crashdb.conf` in `/etc/apport/crashdb.conf.d/` with this content:

   ```python
   <packagename> = {
       'impl': 'launchpad',
       'project': '<packagename>',
       'bug_pattern_url': None,
   }
   ```

Replace `<packagename>` with the name of your package. **`<packagename>` cannot contain hyphens (`-`).** Replace them with underscores (`_`). The `<packagename>` in the `crashdb.conf` file must match the `<packagename>` in the Python file.

Once the package is included in Ubuntu's repositories, Apport reports bugs to Ubuntu's bug tracker instead.


(interactive-feedback)=
### Interactive feedback

Apport can prompt the user by asking them questions.


(yes-no-question)=
#### Yes/no question

`ui.yesno()` returns `True` if the user selects {guilabel}`Yes`, `False` for {guilabel}`No`, and `None` if they cancel:

```python
def add_info(report, ui):
    attach_file = False

    if ui and ui.yesno('Attach some file?'):
        attach_file = True

    if attach_file:
        ...  # the user wants the file attached
```


(choice-list)=
#### Choice list

The pseudo-code below shows how to handle choices. If the response from `ui.choice()` is not `None`, it is a list of zero-based indexes into the list passed as the second argument to `ui.choice()`:

```python
def add_info(report, ui):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    response = ui.choice('What day is it?', days)

    if response is None:
        pass  # the user cancelled
    elif 0 in response:
        ...  # 'Monday' selected
    elif 1 in response:
        ...  # 'Tuesday' selected
    # [...]
    elif 6 in response:
        ...  # 'Sunday' selected
```


(skeleton-for-a-package-hook)=
### Skeleton for a package hook

```python
from apport.hookutils import *

MSG = """
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
        # ask the user and change behavior based on their answer
        answer = ui.yesno(MSG)
        if answer is None:
            # the user cancelled the report
            raise StopIteration
        attach_files = answer

    elif problem_type == 'Crash':
        # crash bugs are private by default
        attach_files = True

    if not attach_files:
        return

    attach_file(report, '/etc/foo')
    attach_file_if_exists(report, '/var/foo.log')
```

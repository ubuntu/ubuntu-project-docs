(triaging-bugs)=
# Triaging bugs

```{toctree}
:maxdepth: 1
:hidden:

bug-types
bug-status
bug-importance
bug-responses
Assign a bug to a package <assign-a-bug-to-a-package>
```

Ubuntu receives a huge number of bug reports every day. Triaging new bugs is a
great way to get started as an Ubuntu contributor, since you'll need to deal
with every aspect of a bug's lifecycle.

A bug triage review involves:

* Reading and assessing the bug
* Checking if enough information was provided
* Assigning the bug to the correct package
* Trying to reproduce the bug
* Checking for duplicates
* Marking the bug as *Triaged*

You might also need to send bugs upstream or cross-reference bugs from other
distributions.

If you are interested in triaging bugs, or need help getting started, you may
want to join the {ref}`bug-squad`.


## Prerequisites

Ubuntu uses Launchpad to track bugs and issues, so you need to create a
[Launchpad](https://launchpad.net/) account if you don't have one. When you do
so, you also need to read and sign the Ubuntu
{ref}`Code of Conduct <code-of-conduct>`.


## Find an untriaged bug

The most common way to find untriaged bugs is by using the Launchpad
[Bug Tracking System's](https://bugs.launchpad.net/)
search functionality to look up a package you're interested in. You can then use
the advanced search on that package's bugs page to look for:

* **Status:** New
* **Importance:** Undecided
* **Assigned to:** Nobody

Or you can [view all untriaged bugs](https://launchpad.net/ubuntu/+bugs?field.searchtext=&orderby=-datecreated&field.status%3Alist=Unconfirmed&field.importance%3Alist=Undecided&assignee_option=none&field.assignee=&field.owner=&field.component=1&field.component=2&field.component-empty-marker=1&field.omit_dupes.used=&field.omit_dupes=on&field.has_patch.used=&field.has_no_package.used=&search=Search).
Once a bug's status has changed from *New* it will no longer show up in this
search.


## Work on the bug

To get started, pick one of the recent new bugs and open the link in your
browser.

Try to pick bugs that affect software or parts of the system you are familiar
with, as this will help you decide how complete the report is, and make it
easier for you to reproduce the bug. If no one else has commented yet this bug
could be yours!

There are many different {ref}`types of bugs <bug-types>` you might encounter.
Try to identify the type of bug you have using that page, and then use the
following actions depending on what you have.

* {ref}`triage-assign-bug-to-package`
* {ref}`confirm-a-bug`
* {ref}`forward-bug-upstream`
* {ref}`mark-bug-as-duplicate`
* {ref}`improve-bug-report`
* {ref}`convert-bug-to-question`
* {ref}`invalidate-a-bug`
* {ref}`bug-status-and-importance`
* {ref}`check-on-your-bugs`

You don't need to do all of these, especially if you are just starting out --
trying to reproduce a reported bug by following the instructions the reporter
provides, and setting the status to "Confirmed" if you find the same issue is
already an excellent way to help. As you grow your knowledge and confidence you
can branch out into the other triager tasks.

The [Launchpad Greasemonkey scripts](https://launchpad.net/launchpad-gm-scripts)
can be a great time-saver while performing these actions.

```{warning}

Some teams have their own policies on triaging, such as:

* [Kernel/Bug Triage](https://wiki.ubuntu.com/Kernel/BugTriage)  
* [X/Triaging](https://wiki.ubuntu.com/X/Triaging)

and some packages have additional policies on triaging beyond the standard
processes:

* [Server Team/NGINX](https://wiki.ubuntu.com/ServerTeam/NGINX#BugTriage)
```


### Talking to reporters

Every bug report is a conversation with the reporter. The first contact any
reporter usually has with the Ubuntu community is through a bug triager, who
tries to put together a complete bug report. It's very important that we give a
good impression, so please be polite and follow the {ref}`code-of-conduct`.

If you need to ask for more information, update the reporter on the status
of their bug, or otherwise correspond with the reporter in some way, you may
find the standard texts on the {ref}`bug-responses` page helpful.


(triage-assign-bug-to-package)=
### Assign a bug to a package

Hundreds of bugs are filed without a package, either because the reporter did
not know the correct package, or did not know how to assign their bug to a
package.

If you can assign a package to a bug, you greatly increase the chances of it
being fixed. It is very easy for a new triager to start here and learn how to
navigate Launchpad while getting to know the community. Eventually you learn
what information is needed for common reports and can ask the reporters to
attach logs or confirm bug reports. This is a first step towards more advanced
triaging.

See the {ref}`how-to-assign-a-bug-to-a-package` for instructions on how to identify
the correct package and assign a bug to it.


(confirm-a-bug)=
### Confirm a bug

The *Confirmed* status is used when it is certain the bug exists. If the bug
adheres to **ANY** of the following criteria it can be considered confirmed:

* Are there enough log files and crash dumps, as outlined in
  [Debugging Procedures](https://wiki.ubuntu.com/DebuggingProcedures)?  

* Can you reproduce the bug yourself? (following the steps provided by the
  reporter)

* Does another distribution have a complete and confirmed bug?  

* Does the upstream author have a complete and confirmed bug?

* Is there a patch that claims to fix the bug? 

If **ANY** of these conditions are satisfied and *you are not the original
reporter*, you can *Confirm* the report. To do this:

* Change the {guilabel}`Status` field to *Confirmed*
* Assign the appropriate {ref}`importance <bug-importance>`  
* Click {guilabel}`Save changes`


### Mark a Confirmed bug as Triaged

The *Triaged* status is used to show you are done with triaging the bug and that
it is ready to be worked on by a developer. Before a confirmed bug can be fixed,
as well as being *Confirmed*, it must also adhere to the following criteria:

* Does the bug report describe a valid bug?  

* Does the bug report contain {ref}`enough details <improve-bug-report>`?  

* If the bug is trivial to fix, is it
  [marked as affecting](https://wiki.ubuntu.com/One%20Hundred%20Papercuts/Triage/Classify%20as%20a%20papercut)
  the "Hundred Papercuts" project?
  
* If bugs for the package are managed elsewhere, is the bug report
  {ref}`forwarded upstream <forward-bug-upstream>`?  

* Is the bug report ready to be worked on by a developer?

Only if **ALL** these conditions are satisfied, can you set the status of the
bug report to 'Triaged'. To do this:

* Change the {guilabel}`Status` field to *Triaged*

* If not done yet, assign the {ref}`appropriate importance <bug-importance>`  

* Click {guilabel}`Save changes`

To set bug statuses to *Triaged* you need to be a member of the
{ref}`bug-control-team` team. If you are not a Bug Control member, and you find
a bug you think is ready to be marked as *Triaged*, then join the `#ubuntu-bugs`
channel on IRC and provide a link to the report. A Bug Control member can then
examine the report and, if it is indeed ready, mark it as *Triaged* for you.


(forward-bug-upstream)=
### Forwarding upstream

Forwarding bugs upstream is an important part of being a triager. Without
telling them, upstream developers might never know about the bug you've been
triaging so studiously.

Bugs should be forward upstream when:

* the Ubuntu bug is *Confirmed* or *Triaged*, and  
* the issue is not due to packaging or a Debian/Ubuntu patch

Please keep in mind that you will be representing Ubuntu upstream. Try to leave
a good impression. Good practice is to mention the original reporter of the bug
and provide a link to the original bug report. It's often greatly appreciated
if you link to the most important attachments and explain what they are.

Before writing a whole new bug report you should look for the problem you're
reporting to prevent duplicates. If you find a duplicate leave a comment
mentioning the Ubuntu bug and link to it. When there are no duplicates to be
found, you can create a new one.

Now you should link the upstream bug to the Ubuntu bug in Launchpad so we can
keep track of its status. To do this:

* Click {guilabel}`Also affects project`  
* If necessary, search for and pick the right project  
* Choose the {guilabel}`I have the URL for the upstream bug:` option and paste
  the URL for the upstream bug in the correct field  
* Click {guilabel}`Add to Bug Report`

Launchpad tracks the upstream bug and warns subscribers to the Ubuntu bug when
the status upstream has been changed.

The page [Bugs/Upstream](https://wiki.ubuntu.com/Bugs/Upstream) provides more
details on how to report bugs in various upstream bug trackers.


#### Marking a bug as requiring forwarding

If you find a bug that needs forwarding, it is best to forward it immediately.
However, if you are running short on time, you can still mark the bug as needing
to be forwarded. To do this:

* Open an upstream task (you click on {guilabel}`Also affects project`), but do
  not assign a bug watch by selecting the option "I just want to register that
  it is upstream right now; I don't have any way to link it." and press
  {guilabel}`Add to Bug Report`. Mind the wording; there is a bug filed against
  {lpbug}`353097`.  
* This will mark the bug as "needs forwarding".
* You can search for those bugs in the {guilabel}`Advanced Search` by selecting
  the "Show only bugs that need to be forwarded to an upstream bugtracker"
  option.


(mark-bug-as-duplicate)=
### Mark bug as duplicate

Many bug reports filed against Ubuntu are actually duplicates. This can happen
after a high profile bug has been introduced into Ubuntu, causing a lot of users
to report it. Other times, reporters don't know how to check if the same bug has
already been filed, or it is hard for them to determine if their bug is the same
as another. Finding these duplicate bugs and aggregating information into one
bug report is a very valuable contribution.

Bugs are duplicates when they have the same root cause. Determining this is a
skill that you learn as you become more familiar with a particular package or
subsystem. Bugs are *not necessarily* duplicates if they have the same effects.
For example, many different bugs can cause X not to start. Determining which bug
a report refers to is part of triaging. If in doubt, ask for a second opinion.

It is probably also sensible to ask the reporter to take look at the possible
duplicate and to help with the decision. Reporters are normally interested in
helping with their own bug reports!

When you first look at a new bug, try to find an existing bug in the system that
describes the new one. Here's how:

* Click the {guilabel}`List open bugs` link at the bottom of the bug page **or**  
  click the {guilabel}`Bugs` tab at the top of the page. Both ways produce a
  list of bugs about the same package.

* Look for bugs with similar descriptions or related titles.  

* If they describe the same root cause, decide which report should be the
  primary one. This should be the one that easiest to understand and contains
  the most information, not necessarily the oldest (lowest numbered) bug.
  
* For the other report, add a comment like this and include a standard reply:

  **`Include: Nothing found for "^== A duplicate ==$"!`**

  (See the {ref}`bug-responses` page for standard responses, and instructions
  to access them as a Firefox extension)

* Then click the {guilabel}`Mark as Duplicate` link at the top right of the bug
  report page, and enter the number of the primary bug.

By default, searches in Launchpad and mentioned above will only look at *Open*
bugs. It may worthwhile to go through the list of *Invalid* and *Won't Fix* bugs,
which you can look for by using an {guilabel}`Advanced Search`. There is also a
standardized tag for bugs likely to have lots of duplicates --
[`metabug`](https://launchpad.net/ubuntu/+bugs?field.tag=metabug).

When marking a bug report as a duplicate of another (primary) bug report, please
also check whether the primary bug report is marked as private. If so, the
primary bug report might not be visible to the current bug reporter.

If the primary bug is marked as private please check why it is so. If it's only
private because Apport makes all bugs private by default, but the core dump has
been removed and none of the Apport attachments contain anything private, it may
be made public. If it does contain confidential information, the bug should
remain private and it is better to search for another bug that could be safely
marked as the primary bug. For any guidance regarding the private status of a
primary bug and marking another bug as a duplicate of it, please ask in the IRC
channel of the {ref}`Bug Squad <bug-squad>` (`#ubuntu-bugs`).

For more information on private Apport bugs, have a look at the
{ref}`apport-crash-reports` section.


(improve-bug-report)=
### Improve bug report

Only valid, well-described bugs can be processed efficiently and swiftly by
developers. Part of the triage process is ensuring the bug is in a good state
before being marked as *Triaged*. 

To be considered complete, a bug report should normally contain:

* The version of Ubuntu that the reporter is running
* The version of the package the reporter is using
* The actions taken to produce the problem
* Whether or not it is possible for the reporter to reproduce the bug
* The expected result of these actions
* The actual result of these actions 

Not every bug report contains this information though. As triagers, we should
ask for all of the above if they are missing. Sometimes a particular piece of
information may be clear from the rest of the report, or it may not be needed.

A good test is to see if you can reproduce the bug yourself on the basis of the
available information. If in doubt, it may be better to discuss with the
reporter before marking the bug as incomplete.

Additionally, certain classes of bugs and specific packages require more
detailed information like configuration and log files. The
[Debugging Procedures](https://wiki.ubuntu.com/DebuggingProcedures) page
contains a list of links to detailed information to gather.

Since most reports probably won't be complete, you'll have to start a
conversation with the bug reporter. Ask the reporter for more information by
doing the following:

* Click on the bug task name (usually the package name) in the yellow horizontal
  line

* Change the {guilabel}`Status` field to *Incomplete*.

* Ask for any missing information needed in the
  {guilabel}`Comment on this change` field

* Check the {guilabel}`E-mail me about changes to this bug report` check box
  to subscribe to the bug

* Click {guilabel}`Save changes` 

As a subscriber to the bug, you will be e-mailed when the reporter responds.

Even if the bug report is complete it could probably still use some improvement.
Is the bug's summary descriptive of the bug? This will help people find the bug
more easily.

As an example, consider the specific and descriptive:

* "no r5xx support in radeon driver (X1300, X1400, X1600, X1800, X1900, X1950)"

vs the vague and general:

* "update-manager"
* "Screen Saver Issues"
* "Buffer I/O Error" 


#### Incomplete bug expiration

Ubuntu doesn't have the resources to address every bug, so we want to focus our
resources on the bugs we really need to fix. Having tens of thousands of bug
reports in the system which we can't and won't get to is not constructive, and
it makes the bug fixing we CAN do less efficient. We focus our effort on bugs
introduced in the Ubuntu packaging process, or specific to the Ubuntu versions
of packages, and bugs which create very significant issues for many users.

We also focus attention on well-defined and complete bugs, because those are the
ones developers have the best chance of addressing in a reasonable time.

Many bugs are fixed from one Ubuntu Release to the next because they are fixed
in new upstream releases. It can be difficult to get the attention of the bug
reporter if they have upgraded to a new version where the fix has been applied.
However, it is important to try and establish if an incomplete bug has been
addressed in a new version.

Therefore, bugs which are marked *Incomplete* are eventually *Expired*, and
drop off the primary reporting lists for developer attention.

If a bug is not fully defined, set it to *Incomplete* and ask if it is still
valid. If a new release of Ubuntu has been made, it is also reasonable to ask
if the bug still appears in the new release and set the bug to *Incomplete*.
Unless the reporter resets the bug status the bug report will be set to expire. 


(convert-bug-to-question)=
### Convert bug to question

Some bug reporters aren't actually reporting a bug but rather are looking for
support with using Ubuntu. These bugs should be converted to questions so they
appear in the Launchpad answer tracker and can be answered there.

Telling whether or not a bug report is actually a support request is subjective,
but these guidelines may help you decide.

* Is the reporter looking for help to accomplish a task?  

  * Installing printer drivers for a printer is a good example of this  

* Is the reporter missing a package to accomplish a task?
 
  * Missing codecs to watch DVDs is a good example of this  

* Is the bug report in a foreign language?  

* Has the reporter misconfigured their system?  

  * Mangled lines in `/etc/apt/sources.list`


(invalidate-a-bug)=
### Invalidate a bug

You may need to invalidate a bug, e.g. if the problem is not reproducible, or if
the program was designed to behave a certain way.

If you are not waiting for a response from the reporter, the best thing to do is
politely decline the report while thanking the user for submitting it. There are
some useful {ref}`bug-responses` that you can use in these cases.

You *do not need* to reject bugs that are already marked as a duplicate of
another bug.

```{note}

Some bug reporters may never get back to you. If there is not enough information
for the bug to be worked on, you do not need to invalidate the bugs -- bugs in
*Incomplete* status without a response will be automatically expired in 60 days.
```


(bug-status-and-importance)=
## Status and importance

The default meanings of importances and statuses are explained at
{ref}`bug-importance` and {ref}`bug-status`. Make sure you've read these
pages thoroughly.

If in doubt, the maintainer (or the one working on the bug) should change the
Status and Importance. It usually reflects the status of this work or reflects
how the bug fits into their working time.


(check-on-your-bugs)=
## Check on your bugs

Perhaps you want to look at a list of bugs you are working on to see if anyone
has replied and to make sure you haven't forgotten one.

A good way to get a list of these bugs is to look at your related bugs. This
can be found in [your bugs page at Launchpad](https://bugs.launchpad.net/people/+me/)

You can see [your subscribed bugs](https://bugs.launchpad.net/~/+subscribedbugs),
or the [bugs you've commented on](https://bugs.launchpad.net/~/+commentedbugs).
Links to both are available at your main "Bugs" page.

You should go through your bugs about once a week, to make sure you haven't
missed anything. This includes bugs you have reported upstream. If there is an
important fact from an upstream bug you should add it to the Ubuntu bug report.



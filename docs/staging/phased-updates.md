(phased-updates)=

# Phased updates

Push out stable release updates to expanding subsets of the user base so that
serious regressions can be detected before updates are pushed to everyone, and
the process stopped. The aim is for regressions to affect a smaller proportion
of our user base.

## Current status

Once an update is released to `-updates`, the update is then phased so that the
update is gradually made available to expanding subsets of Ubuntu users. This
process allows us to automatically monitor for regressions and halt the update
process if any are found. Complete details about the process can be found in a
**blog post** by Brian Murray.

The Phased-Update-Percentage is initially set to 10%, and a job is run (every 6
hours) that checks for regressions and if none are found the phased update
percentage will be incremented by 10%. So an update will become fully phased
after 54 hours or about 2 days. In the event that a regression is detected the
Phased-Update-Percentage will be set to 0% thereby causing supported package
managers not to install the update.

The progress of phased updates is visible
[in a report](https://ubuntu-archive-team.ubuntu.com/phased-updates.html)
which is updated by the same job that does the phasing.

Up to Ubuntu 20.04 LTS (Focal), Update Manager is the only package manager that
supports phased updates
([reference](https://discourse.ubuntu.com/t/phased-updates-in-apt-in-21-04/20345?u=nteodosio)).
Any other update mechanism installs all updates regardless of the
Phased-Update-Percentage.

## Release note

[Stable Release Updates](https://wiki.ubuntu.com/StableReleaseUpdates) will no
longer appear in Update Manager at the same time for all machines. Instead a
subset of machines will be selected at random to receive the update first. The
update will only be made available to everyone if there are no serious
regressions encountered by the first set of users. There is still a testing
process completed by Ubuntu developers before any users receive the update.

## Rationale

Giving an entirely new version of any widely used software program to our
entire user base all at once is unnecessarily fraught with peril.

Instead, let's employ a phased update strategy wherein we provide the updated
software to an ever-expanding set of random users. This pool of users will be
grown as our confidence of that software update grows, fed by real-time
information from the crash database and other potential sources.

This process will be developed in tandem with the efforts to increase testing
of packages in `-proposed` so that we have more confidence in the updates we
are pushing out. This process will add to that the ability to pull an
update before a large number of users encounter it.

## User stories

**As an** Ubuntu User:
* **I want to** encounter regressions in stable release updates less frequently
* **so that** I can get my work done

**As an** Ubuntu developer:
* **I want to** get feedback about regressions before everyone installs the update
* **so that** I can reduce the number of affected users

**As an** Ubuntu pre-release tester:
* **I want to** install all updates immediately
* **so that** I can see breakage as quickly as possible

## update-manager

`update-manager` will treat an update available only when the computer is in
the current **testing set** for that update.

A computer is in the testing set if `Phased-Update-Percentage`
$\times 2^{128} \geq$ `md5` (*machine id* + *package name* + *package version*).

($2^{128}$ is the maximum number producible by the `md5` function.)

This algorithm requires only the package record and the machine ID to execute
and is fairly fast so shouldn't slow down the time to calculate the list of
available updates significantly.

It is deterministic so that it will always answer the same for a particular
package and version at a particular threshold. It does vary based on package
and version though, so that the same set of users aren't always the ones that
find the regressions.

### Unresolved questions

* Is the algorithm correct?
* What do we want to call the new field?
* What should update manager do if there is another version of the package available and the algorithm answers no for the latest? e.g. security update and newer package in -updates. If it won't install the -updates version, should it install the -security? Probably.
* If update manager pops up once a week does it make the phased updates rather useless?
  * Assuming that the default is one week, and there is a fairly uniform distribution on which day of the week that is, we will find that the actual percentage of people with the update installed lags the set number fairly significantly. How much depends on how promptly people install the updates. If everyone installs as soon as the popup happens the update will take about a week longer than the ideal curve to fully propagate, but a majority of people will have the update installed by the time it reaches 100% on the server side.
  * We can't know exactly what the current percentage is, only guess based on the phase of the update.
  * When pausing an update the phase should be bought down to 0 to prevent others installing it, and then increased back up, or jumped to the previous value.
  * Given that the phase doesn't control the percentage of machines with the update installed very strongly, and the "open weekly" default for non-security updates provides some sort of phasing, the main thing this scheme provides is the ability to pause an update without deleting it from -updates. Is that worth the effort?
  * Combining phased updates with an option in update-manager to still only show non-security updates (combined with a change to calculate that based on whether the updates will be shown for the particular machine) makes sense to balance our control in pushing out updates, with the users desire to not be bothered by update prompts every day.
* Given that it is machine based someone with multiple machines will see the updates at different times. Is that too confusing? Should there be a way to turn it off (opt in to testing)?

## Archive

On the server side the new `Phased-Update-Percentage` field needs to be
populated when we want to phase an update.

Launchpad will insert this into the package record. It therefore needs to know
what value to insert. Where should it be stored in Launchpad?

An API will be added to Launchpad to set the value, and it will be controlled
by `ubuntu-sru` (ubuntu-archive?).

  I think that this should be akin to component/section/priority overrides: that is, it should be a column on `BinaryPackagePublishingHistory` and it could most easily be set by adding another optional parameter to `BinaryPackagePublishingHistory.changeOverride`.  This will have the effect of creating a new publication for the package, so it will be beneficial not to change the value too often (perhaps once a day or so); but in order to get the LP archive publisher to generate a new Packages stanza a new publication is necessary anyway, so this is true regardless.  `BinaryPackagePublishingHistory.changeOverride` is restricted to ubuntu-archive. --`cjwatson`

A script will then be run to set these values. When a package is pushed into -updates
the script will start to increase the percentage over time, using some
to-be-defined function of the age of the package, and possibly the urgency.

There will be an override to that aging that will allow `ubuntu-sru` to pause the
script for a particular package that can be used when there are suspected
regressions. Once it has been decided what to do the package can either be
superseded in updates, in which case the process will start again for the new
version, or the roll-out will be continued.

## Opting out

Pre-release versions of Ubuntu should be opted out of phased updates by default.

[The "Updates" panel of the Contributor Console](https://wiki.ubuntu.com/ContributorConsole#updates)
should let testers opt out of phased updates post-release, or opt in to phased
updates pre-release (to test the phasing mechanism itself).

### Unresolved questions

* Where should the information be stored in Launchpad?
* Who should be allowed to change the value?
* How should the process be paused for a particular package?
* What should the roll-out curve look like?

## Further development

* An automatic link could be added from the error tracker to the roll-out script
so that it pauses propagation if there is a spike in crashes with the new
version.

Replace that heading with headings for each thing you’re changing or specifying.

Checklist:

1. Have you reviewed the bug reports for the relevant package? (Yes, this may
  take an hour or two. But you might be able to fix multiple bugs with a
  well-designed change.)

1. If any user interface is involved, is it fully described? Include any
  wire frames or mock-ups.

1. Have you had any new user interface, or new visible text, reviewed by a
  designer? (Or if you are a designer, have you had it peer-reviewed?)

1. Is the change accessible? (For example, have you specified accessible labels
  for any graphic-only elements?)

1. How will users learn the new way of doing things? Describe any help pages
  required, and any changes to the Ubuntu Web site or installer slideshow.

1. Is any migration of data or settings required?

1. How will the feature be tested? Work with the
  [Quality team](https://discourse.ubuntu.com/t/ubuntu-quality/39).

## Unresolved issues

(None)

## See Also

* [Error Tracker/Phased Updates](https://wiki.ubuntu.com/ErrorTracker/PhasedUpdates)
* [Ubuntu Archive team - phased updates](https://ubuntu-archive-team.ubuntu.com/phased-updates.html)

----

* **Launchpad entry**: [Phased updates of software packages](https://blueprints.launchpad.net/ubuntu/+spec/foundations-r-phased-updates)
* **Originally created**: 2012-05-14
* **Last updated**: 2023-06-09
* **Contributors**: `Evan Dandrea`, `James Westby`, `Colin Watson`, `Steve Langasek`, `Michael Vogt`, `Matthew Paul Thomas`, and others


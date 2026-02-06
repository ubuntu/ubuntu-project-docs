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
[blog post](https://web.archive.org/web/20210507035933/http://www.murraytwins.com/blog/?p=127) by Brian Murray.

The Phased-Update-Percentage is initially set to 10%, and a job is run (every 6
hours) that checks for regressions and if none are found the phased update
percentage will be incremented by 10%. So an update will become fully phased
after 54 hours or about 2 days. In the event that a regression is detected the
Phased-Update-Percentage will be set to 0% thereby causing supported package
managers not to install the update.

The progress of phased updates is visible [in a
report](https://ubuntu-archive-team.ubuntu.com/phased-updates.html) which is
updated by the same job that does the phasing. The script behind this whole mechanism is located [in the `ubuntu-archive-tools`](https://git.launchpad.net/ubuntu-archive-tools/tree/phased-updater).

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

## apt

`apt` will treat an update available only when the computer is in
the current **testing set** for that update.

A computer being in the testing set is determined as follows:
* Compute a random number based on the following seed: (*package name* + *package version* + *machine id*).
* Distribute uniformly that random number between 0 and 100.
* Check whether that number is below `Phased-Update-Percentage` and if yes, include the update.

This algorithm requires only the package record and the machine ID to execute
and is fairly fast so shouldn't slow down the time to calculate the list of
available updates significantly.

It is deterministic so that it will always answer the same for a particular
package and version at a particular threshold. It does vary based on package
and version though, so that the same set of users aren't always the ones that
find the regressions.


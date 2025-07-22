(freeze-exceptions)=
# Freeze exceptions

```{note}
This page will be moved to:
* how-ubuntu-is-made > concepts
```

Exceptions to the {ref}`feature-freeze` process must be approved by the Release
Management team for all packages in the Archive (i.e. `main`, `restricted`,
`universe` and `multiverse`).

Exceptions should be granted if the upload:

* Contributes to high-priority feature goals for the release

* Contains *only* bug fixes (which do not usually require explicit exceptions)

* Is warranted due to other exceptional circumstances, as judged by the release managers.

This page outlines some of the common scenarios where Feature Freeze exceptions
might be wanted. You should read this page before you
{ref}`request-a-freeze-exception`.


## Feature Freeze for bugfix-only updates

Up through RC, if a developer believes an upload of a new upstream release that
just has bug fixes in it is warranted, they may upload it. The developer should
explicitly document that this is a bugfix-only upload in the changelog or sync
request.

If you are not sure whether something qualifies, check with a member of
`ubuntu-release` (or subscribe `ubuntu-release` to the bug) and if one person
from `ubuntu-release` agrees it's a bug fix update, you're good for upload.


## Feature Freeze for new packages

New source packages in the Archive do not require Feature Freeze exceptions, as
they must be explicitly opted into by users. For NEW uploads which are not
syncs from Debian, make sure you have the agreement of a member of
the Archive Admin team to perform the necessary queue reviews before you
upload.

However, at the point where you integrate the new package into an existing one
(e.g. adding a dependency or turning on a feature) or add it to a seed, Feature
Freeze begins to apply and you must seek an exception. This is the point at
which risk is added for people who didn't explicitly choose it.

(ui-freeze-exceptions)=
## User Interface Freeze exceptions

{ref}`user-interface-freeze` exception request bugs need a justification for
why the User Interface (UI) needs to be changed at that point, and give a
rationale as to why the benefits of it are worth breaking existing documentation
and translations.

Refer to the {ref}`request-ui-freeze-exception` section for additional
instructions for your request bug.


(milestone-freeze-exceptions)=
## Milestone freeze exceptions (like Beta Freeze)

During milestone/final release freeze periods, extreme caution is exercised
when considering exceptions, as a regression could cause a deadline to be
missed, or a build to receive less testing than desired. A request for an
exception must demonstrate strong rationale and minimal risk for the update to
be considered.

Refer to the {ref}`request-milestone-freeze-exception` section for additional
instructions for your request bug.

(universe-multiverse-freeze-exceptions)=
## Exceptions for Universe/Multiverse

The Freeze Exception process is the same for `universe`/`multiverse` as for
`main`/`restricted`, except during the last week of development before the
release. During that time, all uploads need to get approved by the release team. 

Meeting where [this was decided](https://wiki.ubuntu.com/MOTU/Council/Meetings/2007-02-23).

Refer to the {ref}`request-universe-multiverse-exception` section for additional
instructions for your request bug.


## Packageset FFE delegations

From time to time the `ubuntu-release` team will delegate the responsibility of
reviewing Feature Freeze Exceptions (FFE) for a packageset to one or more
designated individuals who are not members of the Release Team.

Delegates are expected to be Ubuntu Developers with upload rights to the
packageset in question, who have a good working relationship with the Release
Team and have demonstrated a clear understanding of the freeze guidelines.

For the `kubuntu-desktop` packageset in Ubuntu 20.04, the Release Team delegates
FFE-granting authority to [`Rik Mills (~rikmills`)](https://launchpad.net/~rikmills)
and [`Simon Quigley (~tsimonq2`)](https://launchpad.net/~tsimonq2).


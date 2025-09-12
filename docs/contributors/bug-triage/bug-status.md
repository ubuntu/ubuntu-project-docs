(bug-status)=
# Bug status

A report's status is a reflection of the current development state of what is
being reported.

The status of a report can be changed by clicking on {guilabel}`current status`
in the yellow line, towards the top of the page. This reveals a sub-menu of
statuses to choose from. You can then set a new status via the drop down box.

Below is a list of report statuses, their meaning, and when to use them. If you
have any questions, contact the {ref}`bug-squad` via their mailing list.


*New*
: Reports are submitted with this status, and all *New* reports should be
  untriaged. They sometimes lack information.

: If the original reporter adds more information to an *Incomplete* report, they
  can set the status back to *New*.


*Incomplete*
: If you must ask the reporter questions, set the report to *Incomplete*.

: When you ask the reporter to provide any necessary information in a comment,
  subscribe yourself to the report so you will get any updates to it via e-mail.
  If anyone (including yourself) comments on it, the 60-day expiration clock is
  reset.

: For more on this, see {ref}`bug-responses`.


*Opinion*
: This is used when there is a difference of opinion around the report and
  people are free to continue the discussion, but the project or package
  maintainers are considering the issue closed so they can move onto other work.
  The idea is that reports can be marked as closed, so developers aren't spending
  time on them, but discussion can still be ongoing.

: This status is considered an experiment, and will be closely monitored. 


*Invalid*
: This status means the report is closed, and no further triaging or development
  will continue towards it. The *Invalid* status should be used when:

  * The report does not contain enough information to determine whether or not
    it is a bug, even if it is resolved for the reporter.

  * The reported problem is not a bug at all. For example, the reporter's lack
    of knowledge on how something works, hardware failure, or fixed after
    updating a buggy and outdated BIOS. 

: It should be used conservatively, since reports marked as *Invalid* no longer
  show up in default searches. Be sure to triple-check a report before you
  invalidate it!


*Expired*
: This status is similar to *Invalid*, but is meant specifically for reports
  that have been *Incomplete* for too long (see above).
: This status can only be set by using `launchpadlib` or the email interface.
: Like *Invalid* reports, *Expired* reports do not show up in default searches. 


*Confirmed*
: For all packages except for Linux (Ubuntu):

  * Another reporter has experienced the same issue. This can come in the form
    of a duplicate report or a comment.

  * Confirmed reports require confirmation from someone *other* than the original
    reporter. This ensures that the report is applicable to Ubuntu in general,
    and is not due to hardware failure, lack of knowledge, etc.

  * In general, please don't confirm your own bugs, unless there is a documented
    exception by the development group of the package. 

: Only for Linux (Ubuntu):

  * Confirmed means the original reporter has at least attached the minimum
    amount of information to begin triaging.

  * The original reporter has provided previously requested information. 


*Triaged*
: A member of {ref}`bug-control-team` thinks the report describes a genuine
  issue in enough detail that a developer could start working on a fix.

: Use this when you are confident the bug should be looked at by a developer and
  has enough information for them to fix it.

: While not a requirement, a report's Ubuntu task status should be set to *Triaged*
  before any upstream forwarding occurs.

: With reports about Linux: Triaged means that the original reporter has tested
  with the latest upstream mainline kernel they can technically test to.

: For process reports (e.g. {ref}`FFes <freeze-exceptions>` and
  {ref}`syncs`), *Triaged* means the action has been approved by
  the relevant developers. 


*In Progress*
: You have assigned the report to yourself, and you're going to address it right
  now by submitting a patch.

: This status is not for debugging (e.g. bisecting, testing out a patch provided
  by someone else, you have a work around, etc.). 

  ```{warning}
  Never assign a report to others.

  If there has been an assignee for more than six months without a fix or
  response, you can unassign them and revert the status. 
  ```


*Fix Committed*
: **Ubuntu task**: the changes are pending, and to be uploaded soon.

  * *Fix Committed* is also used when an updated package exists in a `-proposed`
    repository (i.e. `noble-proposed`).

  * *Fix Committed* is not to be used when a patch is attached to a report. 

: **Upstream task**: the fix is in `bzr/CVS/git/SVN`, or committed to some place. 


*Fix Released*
: **Ubuntu task**: fixed in the latest Ubuntu release, as a standard upgrade.

  * If the bug stills affects an older Ubuntu release, please nominate it for
    that series. Otherwise people won't know it isn't fixed there!

  * It is preferred, although not required, that one indicates which package
    version the fix was released in. 

: **Upstream task**: fix available in a tarball. 


*Won't Fix*
: This status is sometimes used when the fix is too controversial. It is most
  often used for a report with a release target that will not be fixed in that
  particular release but may be fixed later.

: It may also be used for feature requests that the developers do not want to
  implement. 


## Restricted status changes

The following status changes are restricted to members of {ref}`bug-control-team`
or package maintainers:

* Moving to *Triaged*
* Moving to *Won't Fix*
* Moving from *Won't Fix*
* Targeting to a specific Ubuntu release

If you need someone to change the status of a report that has enough information
to *Triaged*, paste the report number into the `#ubuntu-bugs` channel on IRC
and state that you think the report should be set to "Triaged" with the
appropriate {ref}`bug-importance` (wishlist, low, medium, high, or critical).


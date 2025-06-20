(mir-roles-and-steps)=
# MIR roles and steps

Getting a package promoted to `main` or `restricted` through the MIR process
generally follows this set of steps, where the progress of the bug is
{ref}`tracked in Launchpad <mir-process-states>` using bug states.


## Role overview

There are four roles typically involved in the MIR process, and their
participation follows the same order as the steps of the MIR process itself.

1. **Reporter** (`mir-reporter`) is the person who wants a package promoted,
   who will submit the MIR request through a Launchpad bug.

1. **Reviewer** (`mir-reviewer`) is the MIR team member who reviews the request.

1. **Security reviewer** (`mir-security-reviewer`) for packages where an
   additional security review is needed.

1. **Archive Admin** (`archive-admin`) who promotes the package after the
   reviews are completed.


(mir-step-1)=
## Reporter thinks about the package

The MIR request is submitted as a Launchpad bug by the **reporter**, who uses
the {ref}`mir-reporters-template`. The reporter is initially expected to:


### Process the template

Process the template and check that the package meets all the criteria there.
The {ref}`mir-how-to-use-templates` page can provide guidance.

While processing the template, if it turns out that the package has non-trivial
problems, it is not yet eligible for main inclusion, and those problems need to
be fixed first. In that case, the reporter should:

* Write down issues that violate the requirements and list them in the MIR bug.

* Write down all positive checks that were done (not only the issues).


### File a bug report

File a bug report about the package, titled "`[MIR] sourcepackagename`".

* **Answering each TODO** should include a positive or negative statement as
  confirmation that each requirement was checked carefully.

* **Rule violations** should have an explanation to justify why it should be OK
  for this case.

Subscribe [`ubuntu-mir`](https://launchpad.net/~ubuntu-mir) to the bug report.
Keep it in state "NEW" and do not assign it to anyone: this ensures that it
appears in the
[MIR bug list](https://bugs.launchpad.net/ubuntu/?field.searchtext=&orderby=-date_last_updated&field.status%3Alist=NEW&assignee_option=none&field.assignee=&field.subscriber=ubuntu-mir).


(mir-step-2)=
## Reviewers review the bug

The MIR bug report is reviewed *first* by the MIR team **reviewer**, and then
if necessary, also by the **security reviewer**. Reviewers use the
{ref}`mir-reviewers-template`.


### MIR team review

The MIR team **reviewer** reviews the bug report.

They might delegate portions of the review to other teams, (e.g. the security
team) by assigning it to them.

The outcome of the review is either an acknowledgment, or a set of tasks that
still need to be completed.


### Security review

* See [Security team/Auditing](https://wiki.ubuntu.com/SecurityTeam/Auditing)
  for details on requesting an audit.
* See the [security team Jira board](https://warthogs.atlassian.net/jira/software/c/projects/SEC/boards/594)
  (private board) for a prioritized list of MIR security reviews, or getting
  sign-off from particular team leads about maintenance commitments.


### Update the bug status

After reviewing, the bug status should be adjusted according to the outcome.
If there has been more than one review (e.g. by both MIR team and security
team reviewers), whoever does the last review shall be the one to adjust the
bug status.

For instance, if the MIR team says "OK", and then Security says "OK", the
Security team reviewer should mark the bug as `Fix Committed`.

For other statuses, see the {ref}`mir-process-states` page.


### Refer back to reporter
   
If, during the review process, tasks are identified that need to be completed,
the bug is set to `Incomplete`. This reflects that the onus is back on the
**reporter** to drive the completion of those tasks forward before more
progress can be made.
      
Common examples are "please add an automated test" or "this needs the new
version".


(mir-step-3)=
## Resolve issues

If the bug is set to `Incomplete`, the **reporter** needs to resolve the issues
and complete any tasks that are still outstanding. The MIR team checks updates
on any `Incomplete` bugs and thereby receives the **reporter**'s statement on
which issues have been handled. The **reviewer** checks and confirms -- once
the issues are indeed fully resolved, sets the bug state accordingly to move on
with the process.

Now, the **reporter** takes responsibility for adding the package to the seeds
as per {ref}`seed-management`, or adding a dependency to it from another
package that already is in main.

The package will not be moved to main automatically, but will show up in the
[`component-mismatches`](https://ubuntu-archive-team.ubuntu.com/component-mismatches.svg)
list, or if the dependency is only in proposed, the
[`component-mismatches-proposed`](https://ubuntu-archive-team.ubuntu.com/component-mismatches-proposed.svg)
list.

At this point, **Archive Admins** will promote approved packages to `main`.

## Additional notes

* MIR bugs should always be named for SOURCE packages, not binary packages.

* New binary packages from existing source packages, where the source package
  is already in main, do not require **new** MIR bugs.

* If a new source package contains *only* code which is already in main (e.g.
  a source package split or rename, or source packages with a version in the
  name), it may not need a full review.
  
  In such cases, submitting an MIR bug with an explanation (without the full
  template) **or** updating/extending an existing MIR bug for the package and
  re-opening it by setting it to "NEW" is sufficient.


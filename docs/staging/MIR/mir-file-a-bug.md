(mir-file-a-bug)=
# How to file an MIR bug

The steps of the MIR process require a **reporter** (the one who wants a package
promoted) an MIR team member (who does the review) and potentially a Security
team member (for an extra review).

The MIR bug **reporter** is expected to:

1. Thoroughly go through TODO/RULE entries in
   {ref}`Ubuntu Main Inclusion RULEs and TODOs <main-inclusion-requirements>`,
   check that the package meets all the points there.
   If the package has non-trivial problems, it is not eligible for main
   inclusion, and needs to be fixed first.

   1. Write down issues that violate the requirements and list them in the MIR bug.

   1. Write down all positive checks that you did as well (not only the issues).

1. File a bug report about the package, titled "`[MIR] sourcepackagename`".

   1. Use the template from
      {ref}`Ubuntu Main Inclusion RULEs and TODOs <main-inclusion-requirements>`.

   1. For each rule include a positive or negative statement as confirmation
      that you checked each requirement carefully.

   1. For any rule violations ensure to explain why it should be OK for this case.

1. Subscribe `ubuntu-mir` to the bug report (keep it in state "NEW" and do not
   assign it to anyone!), so that it appears in the
   [MIR bug list](https://bugs.launchpad.net/ubuntu/?field.searchtext=&orderby=-date_last_updated&field.status%3Alist=NEW&assignee_option=none&field.assignee=&field.subscriber=ubuntu-mir).

1. The [MIR team](https://launchpad.net/~ubuntu-mir) reviews the reports, and
   sets acceptable ones to *In Progress* or *Fix Committed*. They might also
   delegate portions of the review to other teams, by assigning it to them;
   common cases are getting a thorough security review from the
   [Security team](https://launchpad.net/~ubuntu-security) (please see
   [Security team/Auditing](https://wiki.ubuntu.com/SecurityTeam/Auditing) for
   details on requesting an audit and the
   [security team Jira board](https://warthogs.atlassian.net/jira/software/c/projects/SEC/boards/594)
   (private board) for a prioritized list of MIR security reviews), or getting a
   sign-off from particular team leads about maintenance commitments.
   
   1. In the case where an MIR needs a security review, a normal MIR review will
      happen by a member of the MIR team and the security review by a member of
      the security team. Among these team members, whoever does the last review
      shall adjust the bug status accordingly.
      
      For instance, if the MIR team says "OK", then Security says "OK", the
      Security team member should mark the bug as "Fix Committed" (see above
      for other statuses).

   1. In case the MIR team (or later, other reviewers) identify tasks that need
      to be done, the bug is set to "incomplete" to reflect that is back on the
      **reporter** to drive that forward before more progress can be made.
      
      Common examples are "please add an automated test" or "this needs the new
      version".

1. The **submitter** should then take responsibility for adding the package to
   the seeds as per {ref}`seed-management` or adding a dependency to it from
   another package that already is in main. The package will not be moved to
   main automatically, but will show up in the
   [`component-mismatches`](https://ubuntu-archive-team.ubuntu.com/component-mismatches.txt)
   list, or if the dependency is only in proposed, the
   [`component-mismatches-proposed`](https://ubuntu-archive-team.ubuntu.com/component-mismatches-proposed.txt)
   list.

   1. Archive administrators will review the `component-mismatches` output, and
      for each package waiting to move into main, look for a
      [corresponding bug](https://bugs.launchpad.net/~ubuntu-mir/+subscribedbugs).

   1. The archive administrators will promote approved packages to main if some
      other package or the seeds want it (see
      [`component-mismatches` output](https://ubuntu-archive-team.ubuntu.com/component-mismatches.txt))
      and the package in question has an owning team subscribed to it.

```{note}
MIR bugs should always be named for SOURCE packages, not binary packages.
```

```{note}
New binary packages from existing source packages, where the source package is
already in main, do not require MIR bugs.
```

```{note}
If a new source package contains only code which is already in main (e.g. the
result of a source package split or rename, or source packages with a version in
the name), it may not need a full review. Submitting an MIR bug with an
explanation (but without the full template) or updating/extending on the
existing old MIR bug and re-opening it by setting it to "NEW" is sufficient.
```


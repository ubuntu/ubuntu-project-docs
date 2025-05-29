(mir-helpers)=
# MIR-related helpers

## Tools

* `check-mir` can be run from a checked-out source and tell you which
  dependencies are in universe.
* `seeded-in-ubuntu PACKAGE` can tell you whether (and how) a given PACKAGE is
  seeded.
* `reverse-depends` can tell you reverse source or binary depends, per component
* The [component mismatches](https://ubuntu-archive-team.ubuntu.com/component-mismatches.svg)
  and [`proposed` component mismatches](https://ubuntu-archive-team.ubuntu.com/component-mismatches-proposed.svg)

## Making life easier for archive team members

To help prevent promotion of packages that cause component mismatches, we can
do two things:

1. Run `check-mir` and make sure that all dependencies have an MIR. We don't
   want to be surprised by a dependency after a package is promoted.
1. List all distinct binary packages that should be promoted. Often, a source
   package will have binary packages that aren't actually needed in main. Things
   like `-doc`, `-autopilot` or `-dbgsym`. These can stay in universe, and it is
   a kindness to list only the packages we need for the archive team member that
   does the promotion.
1. Recommend the owning team to add their corresponding team bug subscriber
   during the MIR process.

## Bug lists

* [All MIR bugs](https://bugs.launchpad.net/~ubuntu-mir)
* [All open MIR bugs](https://bugs.launchpad.net/~ubuntu-mir/+bugs?field.searchtext=&orderby=-importance&search=Search&field.status%3Alist=NEW&field.status%3Alist=CONFIRMED&field.status%3Alist=TRIAGED&field.status%3Alist=INPROGRESS&field.status%3Alist=INCOMPLETE_WITH_RESPONSE&field.status%3Alist=INCOMPLETE_WITHOUT_RESPONSE)
* [All open unclaimed MIR bugs](https://bugs.launchpad.net/ubuntu/?field.searchtext=&orderby=-date_last_updated&field.status%3Alist=NEW&field.status%3Alist=CONFIRMED&assignee_option=none&field.assignee=&field.subscriber=ubuntu-mir)
* [All incomplete MIR bugs](https://bugs.launchpad.net/ubuntu/?field.searchtext=&orderby=-importance&field.status%3Alist=INCOMPLETE_WITH_RESPONSE&field.status%3Alist=INCOMPLETE_WITHOUT_RESPONSE&assignee_option=any&field.assignee=&field.bug_reporter=&field.bug_commenter=&field.subscriber=ubuntu-mir&field.structural_subscriber=&field.component-empty-marker=1&field.tag=&field.tags_combinator=ANY&field.status_upstream-empty-marker=1)
* [All MIR bugs where the security team is assigned](https://bugs.launchpad.net/%7Eubuntu-mir/+bugs?field.searchtext=&orderby=-importance&search=Search&field.status%3Alist=NEW&field.status%3Alist=CONFIRMED&field.status%3Alist=TRIAGED&field.status%3Alist=INPROGRESS&field.status%3Alist=FIXCOMMITTED&field.status%3Alist=INCOMPLETE_WITH_RESPONSE&field.status%3Alist=INCOMPLETE_WITHOUT_RESPONSE&assignee_option=choose&field.assignee=ubuntu-security&field.bug_reporter=&field.bug_commenter=&field.subscriber=ubuntu-mir&field.structural_subscriber=&field.tag=&field.tags_combinator=ANY&field.status_upstream-empty-marker=1&field.has_cve.used=&field.omit_dupes.used=&field.omit_dupes=on&field.affects_me.used=&field.has_patch.used=&field.has_branches.used=&field.has_branches=on&field.has_no_branches.used=&field.has_no_branches=on&field.has_blueprints.used=&field.has_blueprints=on&field.has_no_blueprints.used=&field.has_no_blueprints=on)
* [Security team MIR Jira board](https://warthogs.atlassian.net/jira/software/c/projects/SEC/boards/594)

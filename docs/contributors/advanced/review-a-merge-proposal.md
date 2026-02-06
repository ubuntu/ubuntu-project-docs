(how-to-review-a-merge-proposal)=
# How to review a merge proposal

Establishing a review process before sponsoring or uploading content has helped to maintain consistently high quality. To do so, changes are proposed as {ref}`merge-proposals <how-to-submit-a-merge-proposal>` against {command}`git-ubuntu` branches.

:::{admonition} **Sponsorship** series
The article series provides guidance on requesting sponsorship and sponsoring.

Overview:
:   * {ref}`sponsorship`

For contributors:
:   * {ref}`how-to-find-a-sponsor`
    * {ref}`how-to-request-an-upload`
    * {ref}`how-to-request-a-sync`

For sponsors:
:   * {ref}`how-to-review-a-merge-proposal` (this article)
    * {ref}`how-to-sponsor-an-upload`
    * {ref}`how-to-sponsor-a-sync`
:::

MP reviews are conducted using a {ref}`checklist <review-checklist-template>`. The reviewer is asked to:

* Review formal content for issues.
* Ensure adherence to style guidelines.
* Identify common issues.
* Conduct further testing (when warranted).


## Appropriate level of scrutiny

There are two kinds of changes that require reviews:

Changes are complex or there is any kind of remaining uncertainty:
: Needs a full review as outlined below (the default).

Changes are trivial:
: The requester is not looking for a deep check and only wants to catch obvious and unintended lapses. The requester states **Trivial change** in the MP description.

   * The review can be free form and rather short.
   * Trivial do not require pre-building in PPA and pre-testing with {command}`autopkgtest`.
   * If the reviewer disagrees with that classification, they are entitled to do a full review.


## States for each checklist entry

The following states indicate reviewer feedback on each aspect we check.

{guilabel}`OK` (`+`)
: No concerns to be raised.

{guilabel}`Not OK` (`!`)
: Changes required in the proposed content.

{guilabel}`Question` (`?`)
: Something needs clarifying.

{guilabel}`Not applicable` (`N`)
: The check is not applicable to this case.

{guilabel}`Skipped` (`S`)
: The check is not mandatory for this case.


## Skipping whole sections

Not every change needs all the checks in the checklist. When all elements of a section would be marked `S` ({guilabel}`Skipped`), drop the whole section.

A common case for this are checks relating to "package merges", "new delta in `debian/`", or "new patches".


## Provide feedback

For all {guilabel}`Not OK` and {guilabel}`Question` states, the reviewer must provide details to allow the requester to understand and take action.

Feedback is optional for states {guilabel}`OK`, {guilabel}`Not applicable`, and, usually, {guilabel}`Skipped` states.

When providing feedback, follow the style of [conventional comments](https://conventionalcomments.org/). A prefix helps in many common cases, making it clear if things are blocking or optional.

Reviews do not need to be only critique. Remember the `praise:` label exists.


## What to review

The following is an overview of common things to check.


### New changelog stanza

* Contains a bug pointer in the format `LP: #12345678` for all associated cases.

* Correctly formatted entries according to the [changelog policy](https://www.debian.org/doc/debian-policy/ch-source.html#debian-changelog-debian-changelog) and {ref}`hints for merges <merge-fix-the-changelog>`.

* Lists all changes made -- the changelog is a complete representation.

* Proper version -- check against {ref}`version-strings`.

* Proper release -- often incorrect due to the {command}`dch` tool or a human error.

* Author name and email address.


### Documentation and release notes updates

* All significant developments that need mentioning in Ubuntu release notes should be queued in the document.

* If the update/merge has implications that need to be documented, ensure documentation is updated alongside the change. When things that require documentation arrive via a sync or upstream changes, create a backlog tracker for them.


### Indirect changes

* Some changes imply that the packaging needs to be adapted. Check the content and release notes for any changes like that.

* When merging from Debian or upstream, check if there are newer versions to incorporate. Also ensure the newer release hasn't been withdrawn or doesn't need an immediate fix due to breakage.

* Ensure that any changes in Debian do not imply the need to update the {term}`Ubuntu delta` (even if the delta applies cleanly).

* Ensure the {command}`update-maintainer` tool has been run.


### Old delta

* Ensure that everything dropped from the {term}`Ubuntu delta` really can be dropped.

* Ensure that everything that _can_ be dropped really is dropped (this often needs a test to verify, which is suggested to the owner of the MP and only rarely done by the reviewer).


### New delta

* Do the patches follow the {ref}`dep-3-patch-file-headers` format? (Use {command}`dep3changelog` to verify the headers and generate a changelog entry.)

* Does the patch content and name {ref}`follow our additional style choices <how-to-work-with-debian-patches>`? This is not a strict check, but consistency helps to maintain packages together.

* Do the patches match what is (proposed) upstream?

  * If a certain case asks for violating this rule, it's OK, but it should be a conscious decision and not an accident.

  * The intention is to avoid deviating the code we maintain too much from how the project continues to evolve (hard to maintain well over long periods).

* Are the patches applied the right way according to `debian/source/format`? (See also {ref}`patches`.)

* Are all changes:

  * Forwarded to Debian or upstream, so that everyone benefits, and a merge can one day become a sync again?

  * Or, if they are Ubuntu-only choices, are they marked like that, so the next packager is not wondering if Ubuntu wants to keep or submit it? (See {ref}`UD-forwarded for commits <write-the-commit-message>` and {ref}`Forwarded for patches <the-patchfile-header>`.)

    :::{note}
    If the old delta added in the past does not have such info, and you made an effort to check the history and reasoning to make good decisions, add the same info to that old delta.
    :::


### Git and maintenance

* Check that changes are logically split into separate commits (to ease future merges and cherry picking to other releases).


### Build and test

* If a PPA build is provided, check if the PPA source package is the same as the one being proposed in the merge. Otherwise, this could lead to false negatives (e.g., the proposed merge {term}`FTBFS`, but the PPA build succeeds).

* Verify that the PPA build is successful on all intended architectures.

* If this is an SRU, check that the SRU template in the bug is OK. Test instructions are often only understandable for the reporter, and we want them to be good before the SRU review.

* Where applicable, consider whether tests should be added, adapted, or extended to reflect the changes.

* Use {command}`autopkgtest` on the PPA builds to ensure confidence before Archive entry and avoid late discovery of issues that might lead to entanglement in other {term}`proposed migrations <proposed migration>`.

* New runtime dependencies might be added and could cause {ref}`component mismatches <main-universe-binary-mismatch>`. This would block proposed migration and may necessitate either filing a {ref}`MIR <main-inclusion-review>` for them or adapting the upload to avoid that dependency.

* Optional: Manually install packages from the PPA to verify the builds.

  * Automated testing ({command}`autopkgtest`) is preferred. Suggest adding {term}`DEP-8` test cases where it would make sense.

  * In some situations, manual verification of certain behaviors is necessary for additional assurance.


(review-checklist-template)=
## Review checklist template

Use this template for reviews; it includes all standard criteria as check boxes to avoid omissions.

```
Review Symbols:
+ = OK
! = Not OK
? = Question
N = Not applicable
S = Skipped

* Changelog:
  - [ ] Changelog entry has correct version and targeted codename
  - [ ] Correct formatting of changelog items
  - [ ] Bug references correct
  - [ ] Old content and logical tag match as expected (Package Merge)

* Release notes and Documentation
  - [ ] Added, updated, or enqueued relevant documentation.
  - [ ] Added, updated, or enqueued relevant release notes.

* Package Merge - indirect changes:
  - [ ] No upstream changes that need adapting due to Ubuntu's design
  - [ ] No further upstream version/changes to consider
  - [ ] Debian changes are compatible with the Ubuntu implementation
  - [ ] update-maintainer has been run

* Package Merge - old delta:
  - [ ] Dropped changes are OK to be dropped
  - [ ] Nothing else to drop
  - [ ] Old delta was forwarded to upstream/Debian or marked as Ubuntu-only

* New delta in debian/*:
  - [ ] New changes in debian/* are OK
  - [ ] New delta was forwarded to Debian or marked as Ubuntu-only

* New patches:
  - [ ] No new patches added
  - [ ] Patches match those proposed/committed upstream
  - [ ] Patches correctly included in debian/patches/series
  - [ ] Patches have correct DEP-3 metadata
  - [ ] Patches follow our style choices
  - [ ] New code not from upstream was forwarded or marked as Ubuntu-only

* Git/maintenance:
  - [ ] Commits are properly split (more important on -dev than on SRUs)

* Build/Test:
  - [ ] Build is OK
  - [ ] This is an SRU, the validation instructions are ok
  - [ ] Testcases added or adapted (N/A if not strictly required or already present)
  - [ ] autopkgtest against the PPA package passes (if possible, evidence was provided already)
  - [ ] Based on PPA builds and the build-log, no new component mismatch expected
  - [ ] Verified PPA package installs/uninstalls
  - [ ] Verified PPA source package matches Merge Proposal source package
  - [ ] Verified function manually
```

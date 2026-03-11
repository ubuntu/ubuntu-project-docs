(lifecycle-of-a-change)=
# Lifecycle of a change

Software in Ubuntu is delivered via packages and there might be various
reasons to change them. A change might appear as a fix to a bug, as an update
to a new version of a package or customizing the build and runtime configuration
to the needs of all Ubuntu users.

Getting such a change into Ubuntu involves various steps to enable worldwide
collaboration and to ensure the quality of an upload containing that change to
the Ubuntu Archive.

The diagrams here show the path a change takes, each stage then
refined in later sections, some with optional paths where applicable.

This overview of the involved mechanisms allows a contributor to know
what topic to study next and can be considered a different point of view
to the content aligned to the lifecycle of a change and its way into Ubuntu.

```{include} /how-ubuntu-is-made/processes/lifecycle-of-a-change.txt
```

(lc-bug-report-and-triage)=
## Bug reporting and triage

Almost every change begins with {ref}`filing a bug <how-to-report-a-bug>` on
[Launchpad](https://bugs.launchpad.net/ubuntu). A well-written report states
how to reproduce the problem, which package is affected, and what the expected
behaviour is. Ideally it includes references to related upstream changes or reports.
Once filed, the bug is {ref}`triaged <triaging-bugs>`: confirmed
as real, assigned the appropriate
{ref}`importance <bug-importance>`, given a {ref}`status <bug-status>`,
tagged (see {ref}`bug-tags` and {ref}`bug-types`), and routed to the right
package. The bug serves as the central record that links all subsequent
work (patch, merge proposal, upload).

```{include} /how-ubuntu-is-made/processes/lifecycle-1-report-triage.txt
```


(lc-prepare-fix)=
## Preparing and testing the change

The most common type of change is a **targeted patch**: the {ref}`fix <patching>`
is written, the `debian/changelog` entry is updated, and the change is
{ref}`proposed against a git-ubuntu branch <how-to-handle-git-ubuntu-uploads>`.

Other change types include {ref}`merges <merging>` from a
newer Debian version of the package ({ref}`merges-syncs`), syncs where the
Debian package is copied verbatim ({ref}`merges-syncs`), and
{ref}`new packages <new-packages>` — which, if destined for *main* or
*restricted*, must also pass a {ref}`Main Inclusion Review <main-inclusion-review>`.

Before proposing the change for review, it should be proven to build
correctly and not break existing functionality. The recommended approach is a
{ref}`PPA build <how-to-build-packages-in-a-ppa>` on Launchpad — the same
infrastructure that builds official Ubuntu packages. Once built, PPA packages
can be shared with the bug reporter for smoke-testing, and
{ref}`automated DEP-8 tests <how-to-run-package-tests>` can be run against
them — see {ref}`automatic-package-testing-autopkgtest` for how these tests
are defined and integrated into packages.
{ref}`Building locally with sbuild <how-to-build-packages-locally>`
is also an option for iterative debug cycles.

```{include} /how-ubuntu-is-made/processes/lifecycle-2-prepare-test.txt
```


(lc-review)=
## Proposing and reviewing

Once the fix builds and tests pass, it is
{ref}`submitted as a merge proposal (MP) <how-to-submit-a-merge-proposal>`
against the relevant `git-ubuntu` branch on Launchpad. The merge proposal
links the fix to the bug, describes what was done
and why, and refers to a PPA and test results as far as they already exist.
Reviewers leave comments, the contributor iterates until the merge proposal
is approved.

A reviewer (typically a developer with upload rights)
{ref}`checks the proposal <how-to-review-a-merge-proposal>` against a
{ref}`review checklist <review-checklist-template>`. This covers correctness
of the fix, packaging correctness (`debian/changelog`, version string,
copyright), DEP-3 patch headers, and adherence to Debian and Ubuntu policy.
Trivial or low-risk changes may receive a lighter-weight review.

```{include} /how-ubuntu-is-made/processes/lifecycle-3-propose-review.txt
```


(lc-upload)=
## Sponsorship and uploads

Once approved, the change must be
{ref}`uploaded to the Ubuntu Archive <uploading-to-the-archive>`.

Direct upload access is granted only after a developer has demonstrated consistent
packaging quality (see the {ref}`Uploader journey <uploaders-journey>`).

Until then, a contributor {ref}`finds a sponsor <how-to-find-a-sponsor>` — a
developer who reviews the change, signs the `.changes` file with their own
key, and runs `dput` on the contributor's behalf.

Ideally the uploader is the person who did the review of the {ref}`merge proposal <lc-review>`,
there is no need to be reviewed twice. Otherwise they might apply their own
{ref}`review <how-to-review-a-merge-proposal>` before signing and uploading.

If you want to apply for upload rights later, you should keep track of your work and who has were your sponsors, as sponsors become endorsers for your application.


```{include} /how-ubuntu-is-made/processes/lifecycle-4-upload-sponsor.txt
```


(lc-proposed-migration)=
## Proposed migration

All accepted uploads land in the {ref}`-proposed <proposed-migration>` pocket
(`[codename]-proposed`) first. From there, Launchpad builds binary packages
for every supported architecture. A series of automated quality gates must
then be passed before the package is allowed to *migrate* to the `-release`
or `-updates` pocket and thereby reach users.
Any regression must be investigated as it otherwise stays stuck in `-proposed`.

To migrate from the staging area, the update must:

- **{ref}`Build Successfully<failure-to-build-from-source-ftbfs>`**
  The source package must not fail to build from source (FTBFS) on any
  architecture. In case of failure, the uploader must investigate the build log
  and upload a corrected source package.
- **{ref}`Pass Autopkgtest <autopkgtest-regressions>` (DEP-8)**
  {ref}`Automated functional tests <automatic-package-testing-autopkgtest>`
  in `debian/tests/` inside the changed package and all its reverse-dependencies must pass.
- **{ref}`Pass Archive consistency check <issues-preventing-migration>`**
  The tooling then verifies that the new binaries are installable together
  with everything else in the archive, that all required dependencies are
  present at the right version, and that nothing else becomes
  uninstallable as a side-effect. Any findings are reported as
  {ref}`issues-preventing-migration`.

Progress for the current development release is visible on the
[update excuses page](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_excuses.html).

See {ref}`resolve-a-migration-issue` for practical guidance on tackling such blockers.

```{include} /how-ubuntu-is-made/processes/lifecycle-5-proposed-migration.txt
```


(lc-sru)=
## Stable release updates (SRU)

Updates for the current Ubuntu development version can directly be released.
But after publication of an Ubuntu release (such as `26.04`), its package archive is
frozen for updates.
Bug fixes, security patches, and important improvements can still be provided
for users through the {ref}`Stable Release Update <stable-release-updates-sru>`
(SRU) process — but only under {ref}`strict requirements <explanation-sru-requirements>`
designed to avoid regressions by an update.

A lot of the machinery is shared, an SRU upload passes through the same
{ref}`Proposed migration <lc-proposed-migration>` as any other. At the beginning
the {ref}`SRU team <sru-role>` reviews and accepts from the -unapproved queue,
and at the end the {ref}`SRU team <sru-role>` verifies the case to be ready
to then releases it to -updates.

See {ref}`SRU pipeline <explanation-sru-pipeline>` for the flow of these extra steps.

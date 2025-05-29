(mir-requirements)=
# Main Inclusion requirements

Use this template for the MIR bug report that you will file.

Usage follows {ref}`mir-templates-and-rules`.

The package must fulfill the following requirements.

```
[Availability]
TODO: The package TBDSRC is already in Ubuntu universe.
TODO: The package TBDSRC build for the architectures it is designed to work on.
TODO: It currently builds and works for architectures: TBD
TODO: Link to package https://launchpad.net/ubuntu/+source/TBDSRC

[Rationale]
RULE: There must be a certain level of demand for the package
TODO: - The package TBDSRC is required in Ubuntu main for TBD
TODO-A: - The package TBDSRC will generally be useful for a large part of
TODO-A:   our user base
TODO-B: - The package TBDSRC will not generally be useful for a large part of
TODO-B:   our user base, but is important/helpful still because TBD
TODO: - Additional reasons TBD
TODO: - Additionally new use-cases enabled by this are TBD
TODO: - Package TBDSRC covers the same use case as TBD, but is better
TODO:   because TBD, thereby we want to replace it.
TODO: - The package TBDSRC is a new runtime dependency of package TBD that
TODO:   we already support
RULE: Sometimes there are other/better ways, often are achieved by using a
RULE: library with similar functionality that is more commonly used and
RULE: thereby already in main or a better candidate to promote.
RULE: Reducing the set of supported software in Ubuntu helps to focus on the
RULE: right things, otherwise Ubuntu developers will be consumed by updating
RULE: many variations of the same - wasting valuable time that could be better
RULE: spent elsewhere.
RULE: If there are other packages in the archive that are close, but unable to
RULE: address the problem you might spend some time explaining what exists and
RULE: why it isn't a sufficient alternative.
TODO: - There is no other/better way to solve this that is already in main or
TODO:   should go universe->main instead of this.
RULE: You truly need to understand the difference between main and universe
RULE: in general and in the context of changed rules (build-depends) and
RULE: constraints (Ubuntu Pro made it less of a difference in many cases).
RULE: We have seen requests that were mostly based on old "I said supported (a
RULE: weakly defined term to begin with) in a contract, so it has to be in main"
RULE: feelings, but with sometimes no true reason - neither technically nor
RULE: helping the user base of Ubuntu. Hence we need to ask for that clearly.
TODO: - The binary packages TBD needs to be in main to achieve TBD
TODO-A: - All other binary packages built by TBDSRC should remain in universe
TODO-B: - All binary packages built by TBDSRC need to be in main to achieve TBD

RULE: Reviews will take some time. Also the potential extra work out of review
RULE: feedback from either MIR-team and/or security-team will take time.
RULE: For better prioritization it is quite helpful to clearly state the
RULE: target release and set a milestone to the bug task.
RULE: When doing so do not describe what you "wish" or "would like to have".
RULE: Only milestones that are sufficiently well-founded and related to
RULE: major releases will be considered
TODO-A: - The package TBDSRC is required in Ubuntu main no later than TBD
TODO-A:   due to TBD
TODO-B: - It would be great and useful to community/processes to have the
TODO-B:   package TBD in Ubuntu main, but there is no definitive deadline.

[Security]
RULE: The security history and the current state of security issues in the
RULE: package must allow us to support the package for at least 9 months (120
RULE: for LTS+ESM support) without exposing its users to an inappropriate level
RULE: of security risks. This requires checking of several things:
RULE:   - Search in the National Vulnerability Database using the PKG as keyword
RULE:     https://cve.mitre.org/cve/search_cve_list.html
RULE:   - check OSS security mailing list (feed into search engine
RULE:     'site:www.openwall.com/lists/oss-security <pkgname>')
RULE:   - Ubuntu CVE Tracker
RULE:     https://ubuntu.com/security/cve?package=<source-package-name>
RULE:   - Debian Security Tracker
RULE:     https://security-tracker.debian.org/tracker/source-package/<source-package-name>
TODO-A: - Had #TBD security issues in the past
TODO-A:   - TBD links to such security issues in trackers
TODO-A:   - TBD to any context that shows how these issues got handled in
TODO-A:     the past
TODO-B: - No CVEs/security issues in this software in the past

RULE: - Check for security relevant binaries, services and behavior.
RULE:   If any are present, this requires a more in-depth security review.
RULE:   Demonstrating that common isolation/risk-mitigation patterns are used
RULE:   will help to raise confidence. For example a service running as root
RULE:   open to the network will need to be considered very carefully. The same
RULE:   service dropping the root permissions after initial initialization,
RULE:   using various systemd isolation features and having a default active
RULE:   apparmor profile is much less concerning and can speed up acceptance.
RULE:   This helps Ubuntu, but you are encouraged to consider working with
RULE:   Debian and upstream to get those security features used at wide scale.
RULE: - It might be impossible for the submitting team to check this perfectly
RULE:   (the security team will), but you should be aware that deprecated
RULE:   security algorithms like 3DES or TLS/SSL 1.1 are not acceptable.
RULE:   If you think a package might do that it would be great to provide a
RULE:   hint for the security team like "Package may use deprecated crypto"
RULE:   and provide the details you have about that.
TODO: - no `suid` or `sgid` binaries
TODO-A: - no executables in `/sbin` and `/usr/sbin`
TODO-B: - Binary TBD in sbin is no problem because TBD
TODO-A: - Package does not install services, timers or recurring jobs
TODO-B: - Package does install services, timers or recurring jobs
TODO-B:   TBD (list services, timers, jobs)
TODO: - Security has been kept in mind and common isolation/risk-mitigation
TODO:   patterns are in place utilizing the following features:
TODO:   TBD (add details and links/examples about things like dropping
TODO:   permissions, using temporary environments, restricted users/groups,
TODO:   seccomp, systemd isolation features, apparmor, ...)
TODO-A: - Packages does not open privileged ports (ports < 1024).
TODO-B: - Packages open privileged ports (ports < 1024), but they have
TODO-B:   a reason to do so (TBD)
TODO-A: - Package does not expose any external endpoints
TODO-B: - Package does expose an external endpoint, it is
TODO-B:   TBD endpoint + TBD purpose
TODO: - Packages does not contain extensions to security-sensitive software
TODO:   (filters, scanners, plugins, UI skins, ...)

RULE: The package should not use deprecated security algorithms like 3DES or
RULE: TLS/SSL 1.1. The security team is the one responsible to check this,
RULE: but if you happen to spot something it helps to provide a hint.
RULE: Provide whatever made you suspicious as details along that statement.
RULE: Or remove the following lines entirely if you did not spot anything.
TODO: - I've spotted what I consider deprecated algorithms, the security team
TODO:   should have a more careful look please, details are:

[Quality assurance - function/usage]
RULE: - After installing the package it must be possible to make it working with
RULE:   a reasonable effort of configuration and documentation reading.
TODO-A: - The package works well right after install
TODO-B: - The package needs post install configuration or reading of
TODO-B:   documentation, there isn't a safe default because TBD

[Quality assurance - maintenance]
RULE: - To support a package, we must be reasonably convinced that upstream
RULE:   supports and cares for the package.
RULE: - The status of important bugs in Debian, Ubuntu and upstream's bug
RULE:   tracking systems must be evaluated. Important bugs must be pointed out
RULE:   and discussed in the MIR report.
TODO: - The package is maintained well in Debian/Ubuntu/Upstream and does
TODO:   not have too many, long-term & critical, open bugs
TODO:   - Ubuntu https://bugs.launchpad.net/ubuntu/+source/TBDSRC/+bug
TODO:   - Debian https://bugs.debian.org/cgi-bin/pkgreport.cgi?src=TBDSRC
TODO:   - Upstream's bug tracker, e.g., GitHub Issues
TODO: - The package has important open bugs, listing them: TBD
TODO-A: - The package does not deal with exotic hardware we cannot support
TODO-B: - The package does deal with exotic hardware, such hardware is available
TODO-B:   to the team for debugging, test, verification and development via:
RULE: This is about confidence to be able to maintain the package, therefore
RULE: any option (the examples or anything else you add) is "valid", but it
RULE: depends on the case if that is then considered sufficient.
RULE: The following examples are in descending order in regard to how "ok" they
RULE: likely will be.
TODO-B1:   - testflinger under the following queue(s): TBD
TODO-B2:   - (multiple) Canonical systems in the TBD computing center/lab
TODO-B3:   - an engineering sample in engineers home on TBD team, manager TBD
TODO-B4:   - (multiple) cloud providers as type: TBD
TODO-B5:   - hopefully somewhen getting it due to TBD

[Quality assurance - testing]
RULE: - The package must include a non-trivial test suite
RULE:   - it should run at package build and fail the build if broken
TODO-A: - The package runs a test suite on build time, if it fails
TODO-A:   it makes the build fail, link to build log TBD
TODO-B: - The package does not run a test at build time because TBD

RULE:   - The package should, but is not required to, also contain
RULE:     non-trivial autopkgtest(s).
TODO-A: - The package runs an autopkgtest, and is currently passing on
TODO-A:   this TBD list of architectures, link to test logs TBD
TODO-B: - The package does not run an autopkgtest because TBD

RULE: - existing but failing tests that shall be handled as "ok to fail"
RULE:   need to be explained along the test logs below
TODO-A: - The package does have not failing autopkgtests right now
TODO-B: - The package does have failing autopkgtests tests right now, but since
TODO-B:   they always failed they are handled as "ignored failure", this is
TODO-B:   ok because TBD

RULE: - If no build tests nor autopkgtests are included, and/or if the package
RULE:   requires specific hardware to perform testing, the subscribed team
RULE:   must provide a written test plan in a comment to the MIR bug, and
RULE:   commit to running that test either at each upload of the package or
RULE:   at least once each release cycle. In the comment to the MIR bug,
RULE:   please link to the codebase of these tests (scripts or doc of manual
RULE:   steps) and attach a full log of these test runs. This is meant to
RULE:   assess their validity (e.g. not just superficial).
RULE:   If possible such things should stay in universe. Sometimes that is
RULE:   impossible due to the way how features/plugins/dependencies work
RULE:   but if you are going to ask for promotion of something untestable
RULE:   please outline why it couldn't provide its value (e.g. by splitting
RULE:   binaries) to users from universe.
RULE:   This is a balance that is hard to strike well, the request is that all
RULE:   options have been exploited before giving up. Look for more details
RULE:   and backgrounds https://github.com/canonical/ubuntu-mir/issues/30
RULE:   Just like in the SRU process it is worth to understand what the
RULE:   consequences a regression (due to a test miss) would be. Therefore
RULE:   if being untestable we ask to outline what consequences this would
RULE:   have for the given package. And let us be honest, even if you can
RULE:   test you are never sure you will be able to catch all potential
RULE:   regressions. So this is mostly to force self-awareness of the owning
RULE:   team than to make a decision on.
TODO: - The package can not be well tested at build or autopkgtest time
TODO:   because TBD. To make up for that:
TODO-A:   - We have access to such hardware in the team
TODO-B:   - We have allocated budget to get this hardware, but it is not here
TODO-B:     yet
TODO-C:   - We have checked with solutions-qa and will use their hardware
TODO-C:     through testflinger
TODO-D:   - We have checked with other team TBD and will use their hardware
TODO-D:     through TBD (eg. MAAS)
TODO-E:   - We have checked and found a simulator which covers this case
TODO-E:     sufficiently for testing, our plan to use it is TBD
TODO-F:   - We have engaged with the upstream community and due to that
TODO-F:     can tests new package builds via TBD
TODO-G:   - We have engaged with our user community and due to that
TODO-G:     can tests new package builds via TBD
TODO-H:   - We have engaged with the hardware manufacturer and made an
TODO-H:     agreement to test new builds via TBD
TODO-A-H: - Based on that access outlined above, here are the details of the
TODO-A-H:   test plan/automation TBD (e.g. script or repo) and (if already
TODO-A-H:   possible) example output of a test run: TBD (logs).
TODO-A-H:   We will execute that test plan
TODO-A-H1:  on-uploads
TODO-A-H2:  regularly (TBD details like frequency: monthly, infra: jira-url)
TODO-X:   - We have exhausted all options, there really is no feasible way
TODO-X:     to test or recreate this. We are aware of the extra implications
TODO-X:     and duties this has for our team (= help SEG and security on
TODO-X:     servicing this package, but also more effort on any of your own
TODO-X:     bug triage and fixes).
TODO-X:     Due to TBD there also is no way to provide this to users from
TODO-X:     universe.
TODO-X:     Due to the nature, integration and use cases of the package the
TODO-X:     consequences of a regression that might slip through most likely
TODO-X:     would include
TODO-X:     - TBD
TODO-X:     - TBD
TODO-X:     - TBD

RULE: - In some cases a solution that is about to be promoted consists of
RULE:   several very small libraries and one actual application uniting them
RULE:   to achieve something useful. This is rather common in the go/rust space.
RULE:   In that case often these micro-libs on their own can and should only
RULE:   provide low level unit-tests. But more complex autopkgtests make no
RULE:   sense on that level. Therefore in those cases one might want to test on
RULE:   the solution level.
RULE:   - Process wise MIR-requesting teams can ask (on the bug) for this
RULE:     special case to apply for a given case, which reduces the test
RULE:     constraints on the micro libraries but in return increases the
RULE:     requirements for the test of the actual app/solution.
RULE:   - Since this might promote micro-lib packages to main with less than
RULE:     the common level of QA any further MIRed program using them will have
RULE:     to provide the same amount of increased testing.
TODO: - This package is minimal and will be tested in a more wide reaching
TODO:   solution context TBD, details about this testing are here TBD

[Quality assurance - packaging]
RULE: - The package uses a debian/watch file whenever possible. In cases where
RULE:   this is not possible (e.g. native packages), the package should either
RULE:   provide a debian/README.source file or a debian/watch file (with
RULE:   comments only) providing clear instructions on how to generate the
RULE:   source tar file.
TODO-A: - debian/watch is present and works
TODO-B: - debian/watch is not present, instead it has TBD
TODO-C: - debian/watch is not present because it is a native package

RULE: - The package should define the correct "Maintainer:" field in
RULE:   debian/control. This needs to be updated, using `update-maintainer`
RULE:   whenever any Ubuntu delta is applied to the package, as suggested by
RULE:   dpkg (LP: #1951988)
TODO: - debian/control defines a correct Maintainer field

RULE: - It is often useful to run `lintian --pedantic` on the package to spot
RULE:   the most common packaging issues in advance
RULE: - Non-obvious or non-properly commented lintian overrides should be
RULE:   explained
TODO: - This package does not yield massive lintian Warnings, Errors
TODO: - Please link to a recent build log of the package <TBD>
TODO: - Please attach the full output you have got from
TODO:   `lintian --pedantic` as an extra post to this bug.
TODO-A: - Lintian overrides are not present
TODO-B: - Lintian overrides are present, but ok because TBD

RULE: - The package should not rely on obsolete or about to be demoted packages.
RULE:   That currently includes package dependencies on Python2 (without
RULE:   providing Python3 packages), and packages depending on GTK2.
TODO: - This package does not rely on obsolete or about to be demoted packages.
TODO: - This package has no python2 or GTK2 dependencies

RULE: - Debconf questions should not bother the default user too much
TODO-A: - The package will be installed by default, but does not ask debconf
TODO-A:   questions higher than medium
TODO-B: - The package will not be installed by default

RULE:  - The source packaging (in debian/) should be reasonably easy to
RULE:   understand and maintain.
TODO-A: - Packaging and build is easy, link to debian/rules TBD
TODO-B: - Packaging is complex, but that is ok because TBD

[UI standards]
TODO-A: - Application is not end-user facing (does not need translation)
TODO-B: - Application is end-user facing, Translation is present, via standard
TODO-B:   intltool/gettext or similar build and runtime internationalization
TODO-B:   system see TBD

TODO-A: - End-user applications that ships a standard conformant desktop file,
TODO-A:   see TBD
TODO-B: - End-user applications without desktop file, not needed because TBD

[Dependencies]
RULE: - In case of alternative the preferred alternative must be in main.
RULE: - Build(-only) dependencies can be in universe
RULE: - If there are further dependencies they need a separate MIR discussion
RULE:   (this can be a separate bug or another task on the main MIR bug)
TODO-A: - No further depends or recommends dependencies that are not yet in main
TODO-B: - There are further dependencies that are not yet in main, MIR for them
TODO-B:   is at TBD
TODO-C: - There are further dependencies that are not yet in main, the MIR
TODO-C:   process for them is handled as part of this bug here.

[Standards compliance]
RULE: - Major violations should be documented and justified.
RULE:   - FHS: https://refspecs.linuxfoundation.org/fhs.shtml
RULE:   - Debian Policy: https://www.debian.org/doc/debian-policy/
TODO-A: - This package correctly follows FHS and Debian Policy
TODO-B: - This package violates FHS or Debian Policy, reasons for that are TBD

[Maintenance/Owner]
RULE: The package must have an acceptable level of maintenance corresponding
RULE: to its complexity:
RULE: - All packages must have a designated "owning" team, regardless of
RULE:   complexity.
RULE:   This requirement of an owning-team comes in two aspects:
RULE:   - A case needs to have a team essentially saying "yes we will own that"
RULE:     to enter the MIR process. Usually that is implied by team members
RULE:     filing MIR requests having the backup by their management for the
RULE:     long term commitment this implies.
RULE:     - A community driven MIR request might be filed to show the use case,
RULE:       but then, as a first step, needs to get a team agreeing to own
RULE:       it before the case can be processed further.
RULE:       If unsure which teams to consider have a look at the current mapping
RULE:       http://reqorts.qa.ubuntu.com/reports/m-r-package-team-mapping.html
RULE:       In that case (you are not a representative of the team who will
RULE:       gain the long term committment to this) please ask a representative
RULE:       of that team to comment on the bug acknowledging that they are ok to
RULE:       own it.
RULE:   - The package needs a bug subscriber before it can be promoted to main.
RULE:     Strictly speaking that subscription can therefore wait until the
RULE:     moment of the actual promotion by an archive admin. But it is
RULE:     strongly recommended to subscribe early, as the owning team will get
RULE      a preview of the to-be-expected incoming bugs later on.
RULE: - Simple packages (e.g. language bindings, simple Perl modules, small
RULE:   command-line programs, etc.) might not need very much maintenance
RULE:   effort, and if they are maintained well in Debian we can just keep them
RULE:   synced. They still need a subscribing team to handle bugs, FTBFS and
RULE:   tests
RULE: - More complex packages will usually need a developer or team of
RULE:   developers paying attention to their bugs, whether that be in Ubuntu
RULE:   or elsewhere (often Debian). Packages that deliver major new headline
RULE:   features in Ubuntu need to have commitment from Ubuntu developers
RULE:   willing to spend substantial time on them.
TODO-A: - The owning team will be TBD and I have their acknowledgement for
TODO-A:   that commitment
TODO-B: - I Suggest the owning team to be TBD
TODO-A: - The future owning team is already subscribed to the package
TODO-B: - The future owning team is not yet subscribed, but will subscribe to
TODO-B:   the package before promotion

RULE: - Responsibilities implied by static builds promoted to main, which is
RULE:   not a recommended but a common case with golang and rust packages.
RULE:   - the security team will track CVEs for all vendored/embedded sources in main
RULE:   - the security team will provide updates to main for all `golang-*-dev`
RULE:     packages
RULE:   - the security team will provide updates to main for non-vendored
RULE:     dependencies as per normal procedures (including e.g.,
RULE:     sponsoring/coordinating uploads from teams/upstream projects, etc)
RULE:   - the security team will perform no-change-rebuilds for all packages
RULE:     listing an CVE-fixed package as Built-Using and coordinate testing
RULE:     with the owning teams responsible for the rebuilt packages
RULE:   - for packages that build using any `golang-*-dev` packages:
RULE:     - the owning team must state their commitment to test
RULE:       no-change-rebuilds triggered by a dependent library/compiler and to
RULE:       fix any issues found for the lifetime of the release (including ESM
RULE:       when included)
RULE:     - the owning team must provide timely testing of no-change-rebuilds
RULE:       from the security team, fixing the rebuilt package as necessary
RULE:   - for packages that build with approved vendored code:
RULE:     - the owning team must state their commitment to provide updates to
RULE:       the security team for any affected vendored code for the lifetime of
RULE:       the release (including ESM when included)
RULE:     - the security team will alert the owning team of issues that may
RULE:       affect their vendored code
RULE:     - the owning team will provide timely, high quality updates for the
RULE:       security team to sponsor to fix issues in the affected vendored code
RULE:     - the owning team will use a minimal set of vendored code (e.g., Rust
RULE:       packages are unlikely to need `*_win` crates to build)
RULE:     - if subsequent uploads add new vendored components or dependencies
RULE:       these have to be reviewed and agreed by the security team.
RULE:     - Such updates in the project might be trivial, but imply that a
RULE:       dependency for e.g. a CVE fix will be moved to a new major version.
RULE:       Being vendored that does gladly at least not imply incompatibility
RULE:       issues with other packages or the SRU policy. But it might happen
RULE:       that this triggers either:
RULE:       a) The need to adapt the current version of the main package and/or
RULE:          other vendored dependencies to work with the new dependency
RULE:       b) The need to backport the fix in the dependency as the main
RULE:          package will functionally only work well with the older version
RULE:       c) The need to backport the fix in the dependency, as it would imply
RULE:          requiring a newer toolchain to be buildable that isn't available
RULE:          in the target release.
RULE: - The rust ecosystem currently isn't yet considered stable enough for
RULE:   classic lib dependencies and transitions in main; therefore the
RULE:   expectation for those packages is to vendor (and own/test) all
RULE:   dependencies (except those provided by the rust runtime itself).
RULE:   This implies that all the rules for vendored builds always
RULE:   apply to them. In addition:
RULE:   - The rules and checks for rust based packages are preliminary and might
RULE:     change over time as the ecosystem matures and while
RULE:     processing the first few rust based packages.
RULE:   - It is expected rust builds will use dh-cargo so that a later switch
RULE:     to non vendored dependencies isn't too complex (e.g. it is likely
RULE:     that over time more common libs shall become stable and then archive
RULE:     packages will be used to build).
RULE:   - The tooling to get a Cargo.lock that will include internal vendored
RULE:     dependencies is described at:
RULE:     https://github.com/canonical/ubuntu-mir/blob/main/vendoring/Rust.md
RULE:   - An example of how Rust dependency vendoring can be automated is
RULE:     "s390-tools", isolating crates in a .orig-vendor.tar.xz tarball:
RULE:     * https://git.launchpad.net/ubuntu/+source/s390-tools/tree/debian/rules
RULE:     Other examples include "authd" (for a native package, combined with
RULE:     Golang vendoring) and "gnome-snapshot" (using debian/missing-sources):
RULE:     * authd:
RULE:       https://github.com/ubuntu/authd/blob/main/debian/rules
RULE:     * gnome-snapshot:
RULE:       https://salsa.debian.org/ubuntu-dev-team/snapshot/-/blob/ubuntu/latest/debian/README.source

RULE: - All vendored dependencies (no matter what language) shall have a
RULE:   way to be refreshed
TODO-A: - This does not use static builds
TODO-B: - The team TBD is aware of the implications by a static build and
TODO-B:   commits to test no-change-rebuilds and to fix any issues found for the
TODO-B:   lifetime of the release (including ESM)

TODO-A: - This does not use vendored code
TODO-B: - The team TBD is aware of the implications of vendored code and (as
TODO-B:   alerted by the security team) commits to provide updates and backports
TODO-B:   to the security team for any affected vendored code for the lifetime
TODO-B:   of the release (including ESM).

TODO-A: - This does not use vendored code
TODO-B: - This package uses vendored go code tracked in go.sum as shipped in the
TODO-B:   package, refreshing that code is outlined in debian/README.source
TODO-C: - This package uses vendored rust code tracked in Cargo.lock as shipped,
TODO-C:   in the package (at /usr/share/doc/<pkgname>/Cargo.lock - might be
TODO-C:   compressed), refreshing that code is outlined in debian/README.source
TODO-D: - This package uses vendored code, refreshing that code is outlined
TODO-D:   in debian/README.source

TODO-A: - This package is not rust based
TODO-B: - This package is rust based and vendors all non language-runtime
TODO-B:   dependencies

RULE: - Some packages build and update often, in this case everyone can just
RULE:   check the recent build logs to ensure if it builds fine.
RULE:   But some other packages are rather stable and have not been rebuilt
RULE:   in a long time. There no one can be confident it would build on e.g.
RULE:   an urgent security fix. Hence we ask if there has been a recent build.
RULE:   That might be a recent build that has been done anyway as seen on
RULE:   https://launchpad.net/ubuntu/+source/<source>, a reference to a recent
RULE:   archive test rebuild (those are announced on the ubuntu-devel mailing
RULE:   list like https://lists.ubuntu.com/archives/ubuntu-devel-announce/2024-January/001342.html),
RULE:   or a build set up by the reporter in a PPA with all architectures
RULE:   enabled.
TODO-A: - The package has been built within the last 3 months in the archive
TODO-B: - The package has been built within the last 3 months as part
TODO-B:   of a test rebuild
TODO-C: - The package has been built within the last 3 months in PPA
TODO-D: - The package has been built within the last 3 months in sbuild as it
TODO-D:   can not be uploaded yet
RULE: - To make it easier for everyone, please provide a link to that build so
RULE:   everyone can follow up easily e.g. checking the various architectures.
RULE:   Example https://launchpad.net/ubuntu/+source/qemu/1:8.2.2+ds-0ubuntu1
TODO: - Build link on launchpad: TBD

[Background information]
RULE: - The package descriptions should explain the general purpose and context
RULE:   of the package. Additional explanations/justifications should be done in
RULE:   the MIR report.
RULE: - If the package was renamed recently, or has a different upstream name,
RULE:   this needs to be explained in the MIR report.
TODO: The Package description explains the package well
TODO: Upstream Name is TBD
TODO: Link to upstream project TBD
TODO: TBD (any further background that might be helpful
```

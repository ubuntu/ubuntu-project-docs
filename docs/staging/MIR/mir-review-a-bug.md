(mir-review-a-bug)=
# How to review an MIR bug

This section is a guideline for the review by the
[MIR team](https://launchpad.net/~ubuntu-mir).

Usage follows {ref}`mir-templates-and-rules`.

The intent is to answer the primary decision:
*Will this package be well maintained in main?*

By default, statements are in the *OK* section. Issues that need to be addressed
should go to the *Problem:* sections (and briefly the summary at the top).

```
RULE: Since we sometimes have many such posts on one bug, in case multiple
RULE: packages are associated, clearly state which one this is for.
TODO: Review for Source Package: TBDSRC

[Summary]
TODO: WRITE - TBD The essence of the review result from the MIR POV
TODO-A: MIR team ACK
TODO-B: MIR team NACK
TODO-C: MIR team ACK under the constraint to resolve the below listed
TODO-C: required TODOs and as much as possible having a look at the
TODO-C: recommended TODOs.
TODO-A: This does need a security review, so I'll assign ubuntu-security
TODO-B: This does not need a security review
TODO: List of specific binary packages to be promoted to main: TBD
TODO: Specific binary packages built, but NOT to be promoted to main: TBD

Notes:
TODO: - add todos, issues or special cases to discuss
Required TODOs:
TODO: - TBD (Please add them numbered for later reference)
Recommended TODOs:
RULE: - Does it have a team bug subscriber? (This is not a blocker for a MIR
RULE:   team ACK, but needs to be provided before the package can be promoted
RULE:   by an AA)
TODO: - The package should get a team bug subscriber before being promoted
TODO: - TBD (Please add them numbered for later reference)

[Rationale, Duplication and Ownership]
RULE: One easy way to avoid the burden of maintaining the package is to not
RULE: use it in the first place! If a package is pulling in some random jpeg
RULE: parsing library that needs a MIR, maybe it makes more sense to patch the
RULE: package to just use libjpeg instead. Keep an eye out for duplicated
RULE: functionality in main, since that makes bug fixing and security
RULE: reviewing that much harder.
RULE: Duplicates can be found by searching packages in "main", e.g. using:
RULE: $ apt list "?not(?section(/))" | grep <SEARCH_TERM>
RULE: and/or by checking for alternatives on https://www.libhunt.com/ or
RULE: similar databases.
RULE: Sometimes duplicates are not too obvious, but can often be found by
RULE: searching through full descriptions, provides and all that. If the above
RULE: check didn't already find a duplicate then this check can be done via the
RULE: following steps:
RULE:   $ apt-cache search  <SEARCH_TERM>
RULE: In the returned list pick anything that looks suspicious by name or
RULE: description and check if any of them is in main:
RULE:   $ rmadison -c main {all,packages,that,look,like,duplicates}
RULE: If any of them are reported to be in main check in detail if they cover
RULE: indeed the same use case as the package this MIR is about.
TODO: There is no other package in main providing the same functionality.
RULE: No matter how useful a rationale is and how unique a package might be
RULE: it will need an owning team that is willing and able to spend the time
RULE: to maintain it well for the benefit of all Ubuntu users and use cases.
RULE: If someone submitted an MIR on behalf of another team and suggested them
RULE: to own it, we expect someone representing that to be owning team to
RULE: comment on the bug and acknowledge that they are ok to own that package
RULE: (to avoid review and process effort being spent only to then
RULE: immediately be cancelled by a lack of ownership).
TODO: A team is committed to own long term maintenance of this package.
RULE: In the template to submit cases we ask the reporter to state a rationale
RULE: why this should be considered. But a MIR team member needs to
RULE: try to judge if this rationale is good for Ubuntu and its users.
RULE: We've also seen requests that thought they need to be in main, but that
RULE: was based on wrong assumptions, ensure the requester understands what and
RULE: why they request a main inclusion when judging if the rationale is valid.
TODO: The rationale given in the report seems valid and useful for Ubuntu
RULE: If any of the above checks in this section the MIR team can decide to
RULE: skip the rest of the check until these basic questions are resolved.

[Dependencies]
OK:
TODO: - no other Dependencies to MIR due to this
TODO:   - SRCPKG checked with `check-mir`
TODO:   - all dependencies can be found in `seeded-in-ubuntu` (already in main)
TODO:   - none of the (potentially auto-generated) dependencies (Depends
TODO:     and Recommends) that are present after build are not in main
TODO: - no -dev/-debug/-doc packages that need exclusion
TODO: - No dependencies in main that are only superficially tested requiring
TODO:   more tests now.

TODO-A: Problems:
TODO-A: - TBD
TODO-B: Problems: None

[Embedded sources and static linking]
RULE: - Embedding a library source increases the maintenance burden of a package
RULE:   since that source needs to be maintained separately from the source in
RULE:   the Ubuntu archive. If a source embeds another package, in general the
RULE:   embedded package should not be used and the packaging should be modified
RULE:   to use the Ubuntu archive version. When this is not possible, the
RULE:   security team must agree to using the embedded source.
RULE: - Similarly, when a binary from one source package statically links to
RULE:   libraries from another source package from the archive, when those
RULE:   libraries are updated the statically linked binaries must be rebuilt
RULE:   with the updated libraries to receive the fix, which increases the
RULE:   maintenance burden. For this reason, static linking in archive builds
RULE:   is discouraged unless static linking is required for the package in
RULE:   question to function correctly (e.g. an integrity scanner).
RULE: - If debian/control uses `Built-Using` or `Static-Built-Using:` it may
RULE:   indicate static linking
RULE:   which should be discouraged (except golang/rust, see below)
RULE:   - Rust - toolchain and dh tools are still changing a lot. Currently it
RULE:     is expected to only list the rust toolchain in `Built-Using`.
RULE:     the remaining (currently vendored) dependencies shall be tracked
RULE:     in a Cargo.lock file
RULE:   - Go - here `Built-Using` is expected to only contain the go
RULE:     toolchain used to build it. Additional packaged dependencies
RULE:     will be tracked in `Static-Built-Using:` automatically.
RULE:     The superset of packaged and vendored (if used) dependencies shall be
RULE:     tracked in a go.sum file (go.mod are direct dependencies, go.sum
RULE:     covers checksum content for direct and indirect dependencies. This
RULE:     should be present for reproducible builds already which involve
RULE:     having a go.sum.
RULE:     We have let go packages into main before this existed, so we have
RULE:     sub-optimal prior-art. But down the road - if vendoring is used - we
RULE:     want to switch to require that once the toolchain is ready to
RULE:     create it accordingly.

OK:
TODO: - no embedded source present
TODO: - no static linking
TODO: - does not have unexpected Built-Using entries

RULE: Golang
RULE: - golang 1.4 packages and earlier could only statically compile their
RULE:   binaries. golang 1.5 in Ubuntu 16.10 introduced `-buildmode=shared`
RULE:   to build shared libraries and `-linkshared` to dynamically link against
RULE:   shared libraries. In general, statically compiled binaries are not
RULE:   suitable for the Ubuntu archive because they increase the maintenance
RULE:   burden significantly. As such, from Ubuntu 16.10 and later, golang
RULE:   packages in main were expected to be built with shared
RULE:   libraries.
RULE: - Evaluating cost/benefits while considering the ABI instability of golang
RULE:   libraries during this period, the MIR team decided for 17.10 and later
RULE:   to allow static builds of golang packages in main, so long as the number
RULE:   of these packages remains low and they follow the guidelines below:
RULE:   - golang applications in main are expected:
RULE:       1. to build using `golang-*-dev` packages from the Ubuntu archive
RULE:          creating `Built-Using` in debian/control. This requirement ensures
RULE:          that the security team is able to track security issues for all
RULE:          affected static binary packages
RULE:       2. not to build any vendored (i.e. embedded) code in the source
RULE:          package whose binaries appear in the archive (e.g. test code is
RULE:          ok) without clear justification from the requesting team and
RULE:          approval from the security team. This requirement ensures that
RULE:          the security team is able to track security issues for all
RULE:          affected source packages.
RULE:       3. only build against approved vendored sources (when applicable).
RULE:          If new versions add new components or dependencies in subsequent
RULE:          Ubuntu uploads this will need re-evaluation by the security
RULE:          team. This requirement ensures that the security team is able
RULE:          to track security issues for all affected source packages.
RULE: - The intended outcomes from the above requirements (if not vendored) are
RULE:   for packages in main to standardize on particular versions of
RULE:   `golang-*-dev` packages (when possible) with the requesting team
RULE:    adjusting their packaging as necessary, all teams responsible for
RULE:    golang packages coordinating on transitions and the requesting team
RULE:    occasionally creating new `golang-*-dev` packages as agreed to in the
RULE:    MIR bug (upstreaming to Debian whenever possible).
RULE: - As a practical matter, golang/rust source packages in main are not
RULE:   required to remove unused embedded code copies.
RULE: - If based on the above options it's a statically compiled golang package:
RULE:   - Does the package use dh-golang (if not, suggest dh-make-golang to
RULE:     create the package)?
RULE:   - Does debian/control use `Built-Using: ${misc:Built-Using}` for each
RULE:     non'-dev' binary package (importantly, golang-*-dev packages only
RULE:     ship source files so don't need Built-Using)?
RULE:   - Does the package follow Debian Go packaging guidelines?
RULE:     (See: https://go-team.pages.debian.net/packaging.html)
RULE: - When it is infeasible to comply with this policy, the justification,
RULE:   discussion and approval should all be clearly represented in the bug.

OK:
TODO-A: - not a go package, no extra constraints to consider in that regard
TODO-B: - Go Package that follows the Debian Go packaging guidelines

TODO-A:   - vendoring is used, but the reasoning is sufficiently explained
TODO-B:   - No vendoring used, all Built-Using are in main

TODO-A:   - golang: shared builds
TODO-B:   - golang: static builds are used, the team confirmed their commitment
TODO-B:     to the additional responsibilities implied by static builds.

TODO-A: - not a rust package, no extra constraints to consider in that regard
TODO-B: - Rust package that has all dependencies vendored. It does neither
TODO-B:   have *Built-Using (after build). Nor does the build log indicate
TODO-B:   built-in sources that are missed to be reported as Built-Using.

TODO: - rust package using dh_cargo (dh ... --buildsystem cargo)

TODO-A: - Includes vendored code, the package has documented how to refresh this
TODO-A:   code at <TBD>
TODO-B: - Does not include vendored code

TODO-A: Problems:
TODO-A: - TBD
TODO-B: Problems: None

[Security]
RULE: - Determine if the package may have security implications or history.
RULE:   Err on the side of caution.
RULE: - If the package is security sensitive, you should review as much as you
RULE:   can and then assign to the ubuntu-security team. The bug will then be
RULE:   added to the prioritized list of MIR security reviews.
RULE: - We do not block on, but want to recommend using enhanced isolation
RULE:   features, things like systemd isolation, apparmor and such shall at
RULE:   least have gotten a thought if they would help to mitigate risks in
RULE:   this case. If we spot a case where we think it should be either easy or
RULE:   very beneficial to use such features we should add them to recommended
RULE:   tasks.

OK:
TODO: - history of CVEs does not look concerning
TODO: - does not run a daemon as root
TODO: - does not use webkit1,2
TODO: - does not use lib*v8 directly
TODO: - does not parse data formats (files [images, video, audio,
TODO:   xml, json, asn.1], network packets, structures, ...) from
TODO:   an untrusted source.
TODO: - does not expose any external endpoint (port/socket/... or similar)
TODO: - does not process arbitrary web content
TODO: - does not use centralized online accounts
TODO: - does not integrate arbitrary javascript into the desktop
TODO: - does not deal with system authentication (eg, pam), etc)
TODO: - does not deal with security attestation (secure boot, tpm, signatures)
TODO: - does not deal with cryptography (en-/decryption, certificates,
TODO:   signing, ...)
TODO: - this makes appropriate (for its exposure) use of established risk
TODO:   mitigation features (dropping permissions, using temporary environments,
TODO:   restricted users/groups, seccomp, systemd isolation features,
TODO:   apparmor, ...)

TODO-A: Problems:
TODO-A: - TBD
TODO-B: Problems: None

[Common blockers]
RULE: - There are plenty of testing requirements, hopefully already resolved
RULE:   by the reporter upfront, see "Quality assurance - testing" section of
RULE:   the Main Inclusion requirements
RULE: - The MIR process shall ensure quality and maintainability, due to that
RULE:   the expectations to that are quite high, but especially in cases where
RULE:   special HW is needed that can be a hard to achieve which bloats the
RULE:   options below, it is a balance or compromise we need to strike between
RULE:   giving such cases a pass too easily and making them impossible.
RULE:   Please read (to keep this short) for more background:
RULE:   https://github.com/canonical/ubuntu-mir/issues/30

OK:
TODO: - does not FTBFS currently
TODO: - does have a test suite that runs at build time
TODO:   - test suite fails will fail the build upon error.
TODO: - does have a non-trivial test suite that runs as autopkgtest
TODO-A: - This does seem to need special HW for build or test so it can't be
TODO-A:   automatic at build or autopkgtest time. But as outlined
TODO-A:   by the requester in [Quality assurance - testing] there:
TODO-A1:   - is hardware and a test plan or code
TODO-A2:   - are partner engagements and a test plan or code
TODO-A3:   - is community support to test this for Ubuntu
TODO-A4:   - a simulator and a test plan or code
TODO-A5:   - is upstream support to test this for Ubuntu
TODO-A6:   - an agreement with the manufacturer to test this for Ubuntu
TODO-A7:   - an agreement with solutions-qa to be able to test this for Ubuntu
TODO-A8:   - an agreement with another team to be able to test this for Ubuntu
TODO-B: - This does not need special HW for build or test
TODO-C: - This does need special HW for thorough testing, but all options to
TODO-C:   get this covered have been exhausted and based on demonstration of
TODO-C:   enough investigation and proof of why there is currently no other
TODO-C:   option it is accepted as-is as a compromise.
TODO-C:   The owning team is committed and aware of the implications for
TODO-C:   ongoing maintenance.
TODO: - if a non-trivial test on this level does not make sense (the lib alone
TODO:   is only doing rather simple things), is the overall solution (app+libs)
TODO:   extensively covered i.e. via end to end autopkgtest ?
TODO: - no new python2 dependency
TODO: - Python package, but using dh_python
TODO: - Go package, but using dh-golang

TODO-A: Problems:
TODO-A: - TBD
TODO-B: Problems: None

[Packaging red flags]
RULE: - Does Ubuntu carry a non necessary delta?
RULE: - If it's a library, does it either have a symbols file or use an empty
RULE:   argument to dh_makeshlibs -V? (pass such a patch on to Debian, but
RULE:   don't block on it).
RULE:   Note that for C++, see https://wiki.ubuntu.com/DailyRelease/FAQ
RULE:   for a method to demangle C++ symbols files.
RULE: - Does it have a watch file? (If relevant, e.g. non-native)
RULE: - Is its update history slow or sporadic?
RULE: - Is the current release packaged?
RULE: - Will entering main make it harder for the people currently keeping it
RULE:   up to date? (i.e. are they only MOTUs?)
RULE: - Lintian warnings
RULE: - Is debian/rules a mess? Ideally it uses dh and overrides to make it as
RULE:   tiny as possible.
RULE: - If a package shall be promoted it should NOT be on the lto-disabled
RULE:   list, but the fix, or the workaround should be directly in the package
RULE:   to enforce maintainer awareness and make it more visible to anyone
RULE:   looking at the package - see https://wiki.ubuntu.com/ToolChain/LTO.

OK:
TODO-A: - Ubuntu does not carry a delta
TODO-B: - Ubuntu does carry a delta, but it is reasonable and maintenance under
TODO-B:   control
TODO-A: - symbols tracking is in place.
TODO-B: - For c++ libraries - symbols tracking isn't in place but the owning
TODO-B:   team tried to set it up and came back with a reasonable rationale
TODO-B:   of why it isn't practical to do for the package.
TODO-B:   If symbols tracking isn't used then it's recommended to investigate
TODO-B:   using an alternative like abigail or abi-compliance-check in CI
TODO-B:   or bumping SOVER with every package update.
TODO-C: - symbols tracking not applicable for this kind of code.
TODO-A: - debian/watch is present and looks ok (if needed, e.g. non-native)
TODO-B: - debian/watch is not present but also not needed (e.g. native)
TODO: - Upstream update history is (good/slow/sporadic)
TODO: - Debian/Ubuntu update history is (good/slow/sporadic)
TODO: - the current release is packaged
TODO: - promoting this does not seem to cause issues for MOTUs that so far
TODO:   maintained the package
TODO: - no massive Lintian warnings
TODO: - debian/rules is rather clean
TODO: - It is not on the lto-disabled list
RULE:   (fix, or the workaround should be directly in the package,
RULE:    see https://launchpad.net/ubuntu/+source/lto-disabled-list)

TODO-A: Problems:
TODO-A: - TBD
TODO-B: Problems: None

[Upstream red flags]
RULE: flag common issues:
RULE: - if you see anything else odd, speak up and ask for clarification

OK:
TODO: - no Errors/warnings during the build
TODO-A: - no incautious use of malloc/sprintf (as far as we can check it)
TODO-B: - no incautious use of malloc/sprintf (the language has no direct MM)
TODO: - no use of sudo, gksu, pkexec, or LD_LIBRARY_PATH (usage is OK inside
TODO:   tests)
TODO: - no use of user nobody
RULE:   (consider at least `grep -Hrn nobody` for it
RULE:    and run `find . -user nobody` in source and built binaries)
TODO: - no use of setuid / setgid
RULE:   (consider at least `grep -Hrn -e setuid -e setgid` for it
RULE:    and run `find . \( -perm -4000 -o -perm -2000 \)` in source and
RULE:    built binaries)
TODO: - use of setuid, but ok because TBD (prefer systemd to set those
TODO:   for services)
TODO: - no important open bugs (crashers, etc) in Debian or Ubuntu
RULE: Old dependencies, partially even still in main we want to get rid of over
RULE: time. While they may be still there, we'd not want to add new
RULE: dependencies. webkit = Web content engine library for GTK,
RULE: qtwebkit = Web content engine library for Qt, libseed = GObject JavaScript
RULE: bindings for the webkit engine
TODO: - no dependency on webkit, qtwebkit or libseed
TODO-A: - not part of the UI for extra checks
TODO-B: - part of the UI, desktop file is ok
TODO-A: - no translation present, but none needed for this case (user visible)?
TODO-B: - translation present

TODO-A: Problems:
TODO-A: - TBD
TODO-B: Problems: None
```

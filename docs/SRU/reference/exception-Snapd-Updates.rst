.. _reference-exception-snapdupdates:

Snapd Updates
=============

.. include:: /SRU/_sru-series-exception.rst

Introduction
------------

This page is the SRU exception for the ``snapd`` source package in supported
Ubuntu releases. It states the deviations from the standard SRU criteria that
the SRU team applies, and what the SRU team reviews and verifies.

The exception covers SnapD on Classic and Hybrid Classic systems. It does not
grant exceptions for the development series, feature or beta freezes, or point
releases. Those belong to the Release Team. Sponsoring is also outside this
exception. Pointers for that context are in the appendix.

Summary
-------

SnapD is maintained through a tailored SRU process that reflects its release
and update requirements. The deviations granted by this exception are:

- **Rolling release model.** Each SRU delivers a full upstream release,
  typically 150-250 pull requests, about half of which are test-related.

- **Re-execution model.** If a newer SnapD snap is present, the SnapD deb
  re-executes into it. Rollback of the running SnapD is then the snap revert,
  not a revert of the deb alone.

- **Delegated responsibility for ongoing stability.** Because of re-execution
  and snap refresh, the SRU team delegates to the SnapD team the responsibility
  for ensuring that SnapD updates delivered as debs or snaps continue to meet
  Ubuntu release stability expectations throughout the lifetime of each
  supported Ubuntu release.

- **Regression mitigation.** The SRU team retains authority to require that
  regressions affecting supported Ubuntu releases be addressed. The SnapD team
  chooses the mitigation, implements it, and communicates it.

- **Technical Board review before invasive Classic changes.** Changes that
  significantly alter SnapD behavior on Classic systems, or that affect
  backward compatibility, are reviewed by the Technical Board before they are
  introduced.

Risky features are gated and tested before an SRU is requested. The upstream
checklist for that work is in the appendix.

Background
----------

`SnapD <https://github.com/canonical/snapd>`_ is the background service that
manages installed snaps. On Classic Ubuntu (desktop, server, cloud, and Ubuntu
WSL) and on Hybrid Classic, updates are released as a deb and a snap. This
exception covers those deb updates.

Hybrid Classic uses a kernel snap and therefore requires SnapD. It is available
from 26.04. For this exception it is treated as Classic, including where SnapD
is part of TPM-backed full disk encryption.

Ubuntu Core is snap-only. The SRU process does not apply to it.

Package behavior
----------------

The SnapD deb installs the systemd units and service integration that
bootstrap SnapD on Classic. The snap contains equivalent service integration,
which is used on Ubuntu Core.

When the first snap is installed through the SnapD deb, the SnapD snap is
installed as well, and the deb then re-executes into it. The snap is kept up
to date by auto-refresh. Reverting the deb alone does not revert the running
SnapD if a newer or equal snap revision is still installed.

- **Automatic installation of the SnapD snap.** SnapD deb version 2.40 or
  newer installs the latest stable SnapD snap together with any non-essential
  snap (not core, base, gadget, kernel, or snapd) that does not itself require
  the core snap (`PR 6778 <https://github.com/canonical/snapd/pull/6778>`_).
  SnapD deb version 2.66.1 or newer does this for any non-essential snap
  (`PR 14173 <https://github.com/canonical/snapd/pull/14173>`_).

- **Re-execution.** If the SnapD snap version is greater than or equal to the
  SnapD deb version, the deb re-executes into the snap. A deb version such as
  ``2.66.1+ubuntu24.04`` is higher than snap version ``2.66.1``, so
  re-execution does not happen for that pair. If no SnapD snap is installed
  and the core snap is installed, the deb re-executes into the SnapD embedded
  in the core snap when that embedded version is greater than or equal to the
  deb version.

- **Automatic refresh.** An installed SnapD snap refreshes to the latest
  available version on the auto-refresh schedule.

Exceptions
----------

Categorization
^^^^^^^^^^^^^^

SnapD falls into the following overlapping :ref:`special types of SRU
<reference-special-types-of-sru>`:

- **Package-specific non-standard process:**

  This process deviates from the standard guidelines to accommodate its goal to
  always keep systems up-to-date with the latest bug fixes and features.

- **New bugfix-only upstream release:**

  Updates to SnapD may involve minor upstream releases (dot releases) that focus
  exclusively on fixing bugs.

- **New upstream release that adds features without breaking existing
  behaviour:**

  SnapD updates may also include upstream releases that introduce new features.
  These major updates are :ref:`carefully designed <ref_design>` to ensure
  backward compatibility. It is possible to gate new features using
  :ref:`experimental flags <ref_experimental>` that require user opt-in to be
  enabled. This is used when deemed necessary by the SnapD architect.

- **Creator support:**

  `Interfaces <https://snapcraft.io/docs/interfaces>`_ enable controlled access to
  a specific set of system resources and other snaps. It regularly happens that
  new interfaces or extensions are necessary to empower creators with the system
  resources they need to develop and enhance their applications.

All SnapD releases, regardless of the exact category, are required to comply
with the same thorough QA process.

Deviations requiring sign-off
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SnapD requires the following deviations from :ref:`what is acceptable to SRU
<reference-what-is-acceptable-to-sru>` to support its goal of always keeping
systems up-to-date and enable creators to access not-yet-supported system
resources.

Process
~~~~~~~

- Regular major releases, typically every eight weeks, are delivered as a single
  SRU bug. Each SRU aligns with a full upstream release - often encompassing 100+
  pull requests, approximately half of which are dedicated to test
  additions and maintenance - and introduces complete or partial features
  alongside bug fixes and interface extensions.
- Regular minor releases, as required to fix bugs and low risk interface
  extensions.
- The SRU will be done with a single process bug, instead of individual bug
  reports for individual bug fixes.
- Sponsors, the Ubuntu Release Team, and the SRU Team are not required to review
  all source changes, only those related to packaging and systemd/service
  integration. These changes must be clearly identified in the SRU bug.
- The SRU team delegates to the SnapD team responsibility for ensuring that SnapD
  updates delivered as debs or snaps, together with re-execution, automatic
  installation, and refresh behavior, continue to meet Ubuntu release stability
  expectations throughout the lifetime of each supported Ubuntu release. As part
  of this responsibility, the SnapD team may determine the optimal release order
  of SnapD deb and snap updates for each release, since this can affect which
  SnapD version is executed on a system.
- If a regression affecting Classic systems occurs, the SRU team may require a
  high-priority fix from the SnapD team. The SnapD team will select the most
  appropriate mitigation, such as a snapd deb-only update, a store-based snap
  revert, or a snap update, and is responsible for timely implementation and
  internal and public communication. Launchpad must be used as the primary
  means of communication and coordination.
- The SnapD team is responsible for identifying invasive changes affecting
  Classic systems, including changes to documented re-execution or update
  behaviour, or changes that impact backward compatibility, and must bring such
  changes to the Technical Board for review before they are introduced.

Quality Assurance
-----------------

.. _ref_design:

- **Design:**

  - Complicated or risky changes/features requires a specification for approval
    by at least the product architect.
  - Compatibility mindset - any SnapD version should run on any classic Ubuntu
    release and be able to:

    - Upgrade to any new version without breaking existing behavior.
    - Downgrade to any version without breaking behavior that also exists on the earlier
      version.

.. _ref_development:

- **Development:**

  - Each change must follow `conduct
    <https://github.com/canonical/snapd/blob/master/CODE_OF_CONDUCT.md>`_,
    `contribution <https://github.com/canonical/snapd/blob/master/CONTRIBUTING.md>`_
    and `coding guidelines <https://github.com/canonical/snapd/blob/master/CODING.md>`_
  - Each change must clearly indicate which support tickets it addresses. This
    includes Salesforce Support, Launchpad Bugs and Snapcraft Forum reports.
  - Each change must be approved by at least 2 members of the
    `SnapD team <https://github.com/orgs/canonical/teams/snapd>`_.
  - Each change must be fully tested at unit level.
  - Each feature must have up-to-date integration test.
  - Each change must pass required static analysis checks.
  - Each change must pass the required unit test for amd64 and arm64 on all
    supported classic Ubuntu releases for all corresponding versions of the Go
    toolchain.
  - Each change must pass required integration tests on all supported classic
    Ubuntu and Ubuntu Core releases. This includes:

    - Re-execution of SnapD deb to SnapD snap.
    - Upgrade/downgrade from/to previous to candidate version.

  - Tests that cannot be automated are documented and manually executed when
    there are changes in the code that can affect the feature.

.. _ref_experimental:

- **Experimental flags:**

  Features that are actively under development and carry uncertainty in terms
  of direction or risk must leverage the experimental flag system. This system
  ensures users must explicitly opt-in to activate and test such functionality. The
  SnapD architect is responsible for determining which features should be gated by
  experimental flags and for defining the duration of their experimental status.
  Existing experimental features must be  documented.

.. _ref_release:

- **Release:**

  Refer to the `SnapD release testing diagram <https://drive.google.com/file/d/1Rbs2l0YBaYQSxS4NgvzsoY8fL4gjBnu_/view?usp=sharing>`_
  for the full validation flow that also covers the SnapD snap. This section focuses
  on the SnapD deb part. The diagram serves as a guideline and may change as required.

  - **Release notes:**

    `Release notes <https://docs.google.com/document/d/1do2TFwRIAzuOjLmteVuD0CRoJNO5vVcdUIwTHo4bYO4/edit?usp=sharing>`_
    comments must represent  all PRs, excluding test and non-functional changes, and
    reference all the relevant Launchpad Bugs.

  .. _ref-release-testing:

  - **Release testing:**

    The release PR must pass required  static checks, unit tests
    (amd64, arm64) and integration tests (amd64, arm64) on all supported classic
    Ubuntu releases.

  - **QA testing on SnapD PPA:**

    SnapD debs must be staged  to *ppa:snappy-dev/image* and pass required static
    checks, unit tests (amd64, arm64) and integration tests (amd64, arm64) on all
    supported classic Ubuntu releases. Apart from QA spread based unit tests, unit
    tests will also be run at package build time, thereby covering all architectures.

  - **QA testing on `-proposed`:**

    SnapD debs must be staged  to *-proposed* and must pass required static checks,
    unit tests (amd64, arm64) and integration tests (amd64, arm64) similar to
    development on all supported classic Ubuntu releases. Apart from QA spread based
    unit tests, unit tests will also be run at package build time, thereby covering
    all architectures.

  - **Autopkgtest on `-proposed`:**

    SnapD debs must undergo  autopkgtest testing (all architectures) for all supported
    classic Ubuntu releases.

  - **Launchpad Bug testing on `-proposed`:**

    Each LP bug, relevant  to Ubuntu (excludes e.g. other distros and snaps), should
    implement the :ref:`SRU Bug template <reference-sru-bug-template>`, most importantly
    the *Impact* and *Test  Plan* and the rest as applicable. Each LP bug must be
    independently verified on all the targeted Ubuntu versions.

  - **SnapD snap testing:**

    The tests required as part of  the SnapD snap release validation must pass, with
    the exception of failures not applicable to the deb packages.

.. _ref_revert:

- **Revert:**

If a serious regression impacting Classic Ubuntu is reported or discovered, and
confirmed by a member of the SnapD team, the team is responsible for determining
the most appropriate mitigation, which may include a SnapD deb-only update, a
store-based snap revert, or a snap update.

Release Targets
---------------

- All supported interim releases in standard support.
- All LTS releases in standard support.

Releases for the different targets must share the same source tree, with the
only difference being the additional "backport" entry at the top of
debian/changelog. See
`SnapD versioning <https://github.com/cpaelzer/ubuntu-maintainers-handbook/blob/d380ce51da109f8e27db5c6606f43f253b3bcd92/VersionStrings.md#version-almost-native-packages>`_.

Key Integrations and Interactions
---------------------------------

- **kernel:** support for apparmor, seccomp, module loader, u-events, fuse
  module, etc.
- **systemd:** snap services, cgroups, mounting.
- **udev, libudev1 :** mediate device access.
- **dbus-x11, dbus-user-session:** mediate bus access.
- **policykit-1:** polkit policy.
- **apparmor:** apparmor profiles.
- **squashfs-tools:** packing of snaps.
- **squashfuse, fuse3, libfuse3-3:** to mount squashfs in virtual environments.
- **mount:** mounting and unmounting.
- **passwd, libc-bin:** user creation and lookup.
- **openssh-client:** device key generation.
- **ca-certificates:** secure communications.
- **xdg-desktop-portals:** portal support.
- **prompting-client, desktop-security-center:** apparmor prompting support.
- **snapd-desktop-integration:** SnapD notifications.
- **snap-store:** app-center.

Refer to `SnapD Key Integrations/Interactions on Classic Systems
<https://docs.google.com/document/d/1hNrDXVLJHD1igUSb3UNkhpVA3nx88cQzfIzs4LipwaY/edit?usp=sharing>`_
for more details.

Upload Process
--------------

The SRU should be done with a single process bug, instead of individual bug
reports for individual bug fixes. Individual bugs should be referenced in the
changelog, and each bug needs to be independently verified and commented on for
the SRU to be considered complete. Refer to the :ref:`SRU template
<ref_sru_template>` for details about the required documentation.

Workflow and responsibilities
-----------------------------

**Interim and LTS releases:**

- SRU Team reviews *-unapproved*.
- SRU Team promotes to *-proposed* and applies blocks *block-proposed-<series>*.
- SRU Team reviews *-proposed*.
- SnapD Team provides test results for *-proposed*.
- SnapD Team address autopkgtest failures if any (excuses) or re-trigger tests as
  required.
- SRU Team reviews test results and removes *block-proposed-<series>*.

Review
------

A review should cover at least the following:

- Review that required documentation has been provided as per the SRU template.
- Compare uploaded code to that of the respective release tag to confirm the
  only significant difference is the additional Go and C vendoring code in the
  package.
- Review the `release notes
  <https://docs.google.com/document/d/1do2TFwRIAzuOjLmteVuD0CRoJNO5vVcdUIwTHo4bYO4/edit?usp=sharing>`_.
- Review the related Launchpad bugs indicated in the release notes. Each LP bug,
  relevant to Ubuntu (excludes e.g. other distros and snaps), should implement
  the :ref:`SRU Bug template <reference-sru-bug-template>` , most importantly
  the *Impact* and *Test Plan* and the rest as applicable. Each LP bug must be
  independently verified in *-proposed*.
- Review packaging and systemd/service integration changes.
- Review results of all :ref:`required release testing <ref-release-testing>`.
- For all source packages for the different target releases:

  - Ensure builds for all architectures succeeded.
  - Source tarballs match.
  - Vendored dependencies match.
  - Changelogs for all targeted releases match the release notes and each other.

.. _ref_sru_template:

SRU Template
------------

Sponsoring Request
^^^^^^^^^^^^^^^^^^

This refers to the "single process bug" that links to to one or more Launchpad
bugs associated with the release.

.. code-block::

 This is a new SnapD release.
 SnapD [bugfix only] release 2.XX[.X] should be released to:
 - [Development Release]
 - [Latest LTS]
 - ... -
 - [Oldest LTS]

 The SnapD package deviates from the standard SRU process. The following special
 SRU process was followed:
 https://documentation.ubuntu.com/sru/en/latest/reference/exception-Snapd-Updates

 Release preparation: <Github release PR URL> Release preparation test results:
 <Github release PR test results URL>

 Release notes: < Changelogs commit URL > Launchpad bugs addressed:
 <URL(filter)>

 Packaging and systemd/service integration changes:
  - [Packaging changes]
  - [Systemd/service integration changes]

 Content overview:
  - [Features]
  - [Bug fixes]
  - [Creator support changes]
  - [Other]

 Areas of potential regressions:
  - <Potential regression | <URLs to relevant PR(s)>

 Source packages on `ppa:snappy-dev/image` for upload to `-proposed`:
  - <Development Release URL>
  - <Interim release URL>
  - <Latest LTS URL>
  - ...
  - <Oldest LTS URL>

 Validation already completed:
  - Release PR test results: <URL to relevant PR>
  - QA beta validation: <JIRA URL>
  - SnapD deb testing on `ppa:snappy-dev/image`: <JIRA URL>

 Validation required before release:
  - Autopkgtests on `-proposed` for all targeted releases
  - SnapD deb testing on `-proposed`
  - SnapD snap testing

Sponsoring Request Final Test Feedback
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following updates from the SnapD team is required before considering
releasing to *-updates*:

.. code-block::

 - Autopkgtests on `-proposed` for all targeted releases: <RESULT>
 - SnapD deb testing on `-proposed`: <RESULT>
 - SnapD snap testing: <RESULT>

Associated Launchpad Bugs
^^^^^^^^^^^^^^^^^^^^^^^^^

This refers to the linked LP bugs in "Launchpad bugs addressed" in the
above Sponsoring Request template. This should be added in the bug description
above the original comment.

In the case where the issue is covered by automated testing, this should be
explicitly mentioned with links to:
 - link to the relevant test
 - link to the Release PR where it was exercised
 - still include manual verification steps as well

Ubuntu Core only Launchpad bugs does not require Launchpad bug verification.
Clearly indicate if a Launchpadbug is Ubuntu Core only.

.. code-block::

 [SRU <version>](https://bugs.launchpad.net/ubuntu/+source/snapd/+bug/<URL>)

 [ Impact ]

 [ Test Plan ]

  1. Reproduce on reported snapd version <reported snapd version>

   [steps]

  2. Confirm fix on <candidate snapd version>

   [steps]

 [ Where problems could occur ]

 [ Other Info ]

 --- original ---

Related SRU Interest Team
-------------------------

SnapD has a :ref:`SRU Interest Team <reference-sru-interest-team>`,
please subscribe the
`Interest group <https://launchpad.net/~sru-verification-interest-group-snapd>`_
to the SRU bug early on.

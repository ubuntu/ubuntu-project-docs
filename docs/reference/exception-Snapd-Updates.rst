.. _reference-exception-snapdupdates:

SnapD Updates
=============

Introduction
------------

This document explains how SnapD updates deviate from the standard SRU policy,
outlining the background, deviations, and the responsibilities of the SnapD,
sponsor, and SRU teams in managing quality and risk.

Summary
-------

SnapD, Ubuntu’s service for delivering and updating snaps, is maintained
through a tailored SRU process that reflects its unique release and update
requirements.

Key deviations from the standard SRU model include:

- **Rolling release model:**

  Each SRU delivers a full upstream release, typically 150-250 pull requests,
  about half of which are test-related.

- **Re-execution model:**

  If a newer SnapD snap is present, the SnapD deb will re-execute into it,
  ensuring the SnapD runtime is kept up to date with snaps as they are refreshed,
  but shifting rollback control to the snap store.

- **Flexible timing:**

  Updates may land outside normal freeze windows to maintain security and feature
  currency.

- **Delegated responsibility for ongoing stability:**

  With re-execution and snap refresh behavior, the SRU team delegates
  responsibility to the snapd team for ensuring that snapd updates delivered as
  debs or snaps continue to meet Ubuntu release stability expectations
  throughout the lifetime of each supported Ubuntu release.

- **Regression mitigation:**

  The SRU team retains authority to require that regressions affecting supported
  Ubuntu releases be addressed. Responsibility for determining the appropriate
  mitigation is delegated to the SnapD team. The SnapD team is responsible for
  the timely implementation of the selected mitigation and communication.

- **Technical Board oversight for invasive changes:**

  Changes that significantly alter snapd behavior on Classic systems or impact
  backward compatibility must be reviewed by the Technical Board before they are
  introduced.

These deviations are necessary to keep Ubuntu systems secure, up-to-date, and
consistent across distributions, while enabling developers to use new system
capabilities without delay.

Risks are tightly managed through:

- A multi-layered QA process.
- The use of experimental feature flags for higher-risk or multi-stage feature
  development.
- Snap revert mechanism for urgent rollbacks.

This process ensures SnapD delivers at the pace required by its role, while
maintaining the stability and trust expected of Ubuntu releases.

Background
----------

`SnapD <https://github.com/canonical/snapd>`_ is a background service that
manages and maintains installed snaps. It is used on classic Ubuntu (and other
distributions) as well as on Ubuntu Core. From the perspective of the SnapD
team, a release usually involves both a deb and snap package to serve the needs
of desktop, server, cloud and IOT use cases.

An important goal of the SnapD project is to always keep systems up-to-date with
the latest security fixes, bug fixes and the latest features, while also
enabling developers to access system resources that are initially restricted by
interfaces but may be opened in a controlled manner to support new solutions.

The SnapD value proposition is to allow installing robust software that can move
at a different pace than distributions, in a rolling release model. In order to
fulfill this, it needs to provide a security-maintained, consistent and
up-to-date runtime environment for them across distributions and distribution
versions. See :ref:`design <ref_design>`, :ref:`development
<ref_development>` and :ref:`release <ref_release>` processes have been designed
to minimize the risks associated with maintaining this level of
"up-to-dateness".

Overview of SnapD usage across Ubuntu variants
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are different Ubuntu OS variants that depend on SnapD to different degrees.

These variants include:

- **Classic:** Desktop, Server, Cloud & Ubuntu WSL.
- **Hybrid Classic:** Similar to Classic systems, but use Kernel snap and therefore
  requires SnapD. Available from 26.04.
- **Ubuntu Core:** A strictly confined, immutable Ubuntu variant optimized for
  edge and IoT devices. It uses only snaps and therefore requires SnapD.

Variants and composition of installers and installed images may change in the future.

Classic systems
~~~~~~~~~~~~~~~

- SnapD is used during both installation and normal system operation.
- Installer LiveCD images are seeded with both SnapD deb and snap packages and
  installs are seeded with the SnapD deb package.
- Ubuntu supports and enables :ref:`re-execution <ref_reexecution>` during both
  installation and normal system operation.
- Due to re-execution, reverting the deb package alone does not necessarily
  revert the running SnapD version if a newer or equal snap revision is still
  installed. For this reason, SnapD reverts may be performed using the
  store-based snap revert mechanism described :ref:`here <ref_revert>`, rather
  than through the standard SRU process for deb packages.
- Updates are released as deb and snap packages; the order of release may vary.
- The SnapD deb package installs the systemd units and
  service integration that bootstrap SnapD. The SnapD snap also contains
  equivalent service integration, but this is only used on Ubuntu Core systems.
- SRU release targets all `Ubuntu Releases
  <https://ubuntu.com/about/release-cycle>`_ in Standard Support (not ESM or
  Legacy Support).

Hybrid Classic systems
~~~~~~~~~~~~~~~~~~~~~~

Hybrid Classic systems behave the same as Classic systems except for the following:

- SnapD is more deeply integrated into Hybrid Classic systems that use
  TPM-backed Full Disk Encryption (FDE).
- Currently LiveCD images and installs are seeded with both SnapD deb and snap
  packages.

Ubuntu Core systems
~~~~~~~~~~~~~~~~~~~

- Ubuntu Core images are seeded with the snap package.
- Updates are released as a snap package, therefore the SRU process is not
  relevant to this product.

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
- Flexibility during the development cycle (LTS or otherwise) to release major
  or minor releases between feature freeze and BETA freeze. In general SnapD
  releases may land in stable Ubuntu releases at any time which makes strictly
  adhering to the feature freeze counterproductive.
- Flexibility with `LTS point releases
  <https://wiki.ubuntu.com/PointReleaseProcess>`_ to release up to the release
  date minus 14 days.
- The SRU will be done with a single process bug, instead of individual bug
  reports for individual bug fixes.
- Sponsors must review the SnapD source package and resulting deb packages in the
  SnapD Team owned *ppa:snappy-dev/image* and sponsors upload to *-unapproved*
  queue from where the SRU team takes over, including further reviews.
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

Package behavior
~~~~~~~~~~~~~~~~

When the first snap is installed through the snapd deb, the snapd snap itself is
also installed, and the deb then re-executes into it. The snapd snap is kept up
to date through auto-refresh, ensuring that snapd always runs with the latest
features and fixes, and maintains consistency across Ubuntu releases regardless
of the host distribution’s update cadence.

- **Automatic installation of SnapD snap once other snaps are installed:**

  - SnapD deb version >= *2.40* will automatically install the latest stable SnapD
    snap along with any non-essential (not: core, base, gadget, kernel or snapd)
    snap that does not itself require the Core snap. This ensures an up-to-date
    runtime and additionally enables the use of interfaces (`PR-6778
    <https://github.com/canonical/snapd/pull/6778>`_).

  - SnapD deb version >= *2.66.1* will automatically install the latest stable SnapD
    snap along with any non-essential (not: core, base, gadget, kernel or snapd)
    snap. This is required to systematically remove the core snap upgrade path
    (`PR-14173 <https://github.com/canonical/snapd/pull/14173>`_).

.. _ref_reexecution:

- **Re-execution from SnapD deb to SnapD snap:**

  If the SnapD snap version is greater than or equal to the SnapD deb version,
  the SnapD deb will re-execute to run the SnapD snap. Note that in the case of
  the same counterpart versions, where SnapD deb version is *2.66.1+ubuntu24.04*
  and SnapD snap version is *2.66.1*, re-execution will not happen because the
  postfix *+ubuntu24.04* makes the deb version the higher version. With no SnapD
  snap installed and Core snap installed, if the version of SnapD embedded in
  the Core snap is greater than or equal to the SnapD deb version, the SnapD deb
  will re-execute to the SnapD embedded in the Core snap.

- **Automatic refresh of SnapD snap:**

  If SnapD snap is installed it will automatically refresh to the latest
  available version according to the auto-refresh schedule.

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

- Development release (for LTS and interim).
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

Review/Sponsoring
-----------------

The SnapD team requires the help of at least one dedicated Ubuntu Team member
(core-dev) to copy the applicable source packages available in
*ppa:snappy-dev/image* to -unapproved for all targeted Ubuntu releases. This
activity must be explicitly requested by the SnapD team as shown in the SRU bug
template. In the future when SnapD Team member(s) qualify as sponsors, this
dependency may fall away.

Workflow and responsibilities
-----------------------------

**Preparation:**

- SnapD Team uploads source packages to *ppa:snappy-dev/image*.
- SnapD Team provides test results for *ppa:snappy-dev/image*.
- SnapD Team provides autopkgtest results for packages in
  *ppa:snappy-dev/image*.
- Sponsor reviews release candidates in *ppa:snappy-dev/image* and test results.

**Development release:**

- Sponsor uploads to Development release *-proposed*.
- SnapD Team provides test results for *-proposed*.
- SnapD Team address autopkgtest failures if any (excuses) or retrigger tests as
  required.

**Interim and LTS releases:**

- Sponsor (core-dev) uploads to Interim/Stable release -unapproved.
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

Final Test Feedback
^^^^^^^^^^^^^^^^^^^

The following updates from the SnapD team is required before considering
releasing to *-updates*:

.. code-block::

 - Autopkgtests on `-proposed` for all targeted releases: <RESULT>
 - SnapD deb testing on `-proposed`: <RESULT>
 - SnapD snap testing: <RESULT>

Related SRU Interest Team
-------------------------

SnapD has a :ref:`SRU Interest Team <reference-sru-interest-team>`,
please subscribe the
`Interest group <https://launchpad.net/~sru-verification-interest-group-snapd>`_
to the SRU bug early on.
snapd team is responsible for determining the most appropriate mitigation, which may include a snapd deb-only update, a store-based snap revert, or a snap update

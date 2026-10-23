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

Special SRU categories
----------------------

SnapD falls under these overlapping categories in
:ref:`special types of SRU <reference-special-types-of-sru>`:

- **Package-specific non-standard process,** so that systems stay up to date
  with current bug fixes and features.
- **New bugfix-only upstream release,** for minor (dot) releases that only fix
  bugs.
- **New upstream release that adds features without breaking existing
  behaviour.** Major updates are expected to stay backward compatible. Where
  the SnapD architect decides a feature is not ready to be on by default, it
  is gated by an experimental flag that requires the user to opt in.
- **Creator support.** New interfaces or extensions are sometimes required so
  that creators can use system resources that were previously closed.

Granted deviations
------------------

This page is the approved exception. SnapD requires the following deviations
from :ref:`what is acceptable to SRU <reference-what-is-acceptable-to-sru>`.

- Regular major releases, typically every eight weeks, are delivered as one
  SRU. Each SRU matches a full upstream release, often 100 or more pull
  requests, about half of them tests, and may include complete or partial
  features, bug fixes, and interface extensions.
- Minor releases that fix bugs, and low-risk interface extensions, are
  delivered as SRUs when required.
- An SRU may use a single process bug. Every bug named in the changelog still
  has the :ref:`standard SRU template <reference-sru-bug-template>` and is
  verified in the normal way.
- The SRU team reviews packaging and systemd/service integration, as
  identified in the process bug. The SRU team does not review every upstream
  commit.
- The SRU team delegates to the SnapD team responsibility for ensuring that
  SnapD updates delivered as debs or snaps, together with re-execution,
  automatic installation, and refresh, continue to meet Ubuntu release
  stability expectations for the lifetime of each supported release. The SnapD
  team may choose the release order of the deb and the snap for each release,
  because that order can change which SnapD version runs.
- If a regression affects Classic systems, the SRU team may require a
  high-priority fix. The SnapD team selects the mitigation, such as a deb-only
  update, a store-based snap revert, or a snap update, and is responsible for
  implementing it and for internal and public communication. Launchpad is the
  primary place for that coordination.
- The SnapD team identifies invasive Classic changes, including changes to
  documented re-execution or update behaviour, or changes that affect backward
  compatibility, and brings them to the Technical Board before they are
  introduced.

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

Release targets
---------------

An SRU under this exception targets:

- supported interim releases in standard support
- LTS releases in standard support

The development release is not an SRU target.

Uploads for these targets share the same source tree. The only difference is
the additional backport entry at the top of ``debian/changelog``. See
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

Stable release workflow
-----------------------

SRU review starts when the upload is in the ``-unapproved`` queue. From there
the steps are the usual ones in :ref:`Perform a standard SRU <howto-perform-standard-sru>`:

- The SRU team reviews the upload in ``-unapproved``.
- The SRU team accepts it into ``-proposed`` and applies
  ``block-proposed-<series>``.
- The SnapD team posts the verification described in the process-bug test
  plan, and addresses autopkgtest failures or retriggers tests.
- The SRU team reviews that verification and removes
  ``block-proposed-<series>``, which releases the package to ``-updates``.

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

Process bug template
--------------------

Use one process bug for the SRU. Post verification results as comments on that
bug before the package is released to ``-updates``.

.. code-block:: none

   [ Impact ]

   This is a new SnapD release.
   SnapD [bugfix only] release 2.XX[.X] should be released to:
   - [Latest LTS]
   - ...
   - [Oldest LTS]

   The SnapD package follows this special SRU process:
   https://ubuntu.com/project/docs/SRU/reference/exception-Snapd-Updates/#reference-exception-snapdupdates

   [ Test Plan ]

   The SRU team should expect the following, posted on this bug:

   - Autopkgtests on -proposed for all targeted releases: <result and URL>
   - SnapD deb testing on -proposed: <result and URL>
   - SnapD snap testing: <result and URL>
   - Each bug named in the changelog verified on -proposed, using the
     standard SRU template: <links to those bugs and their verification>

   Packaging and systemd/service integration changes, which are the changes
   the SRU team reviews:
   - [Packaging changes]
   - [Systemd/service integration changes]

   [ Where problems could occur ]

   - <Potential regression, with URLs to the relevant pull requests>
   - Interactions called out for this upload. The standing list of Classic
     integrations is in the appendix.

   [ Other Info ]

   - Release preparation: <GitHub release pull request URL>
   - Release preparation test results: <URL>
   - Release notes: <changelog commit URL>
   - Launchpad bugs addressed: <URL>
   - Content overview: features, bug fixes, creator-support changes, other

Associated bugs
---------------

Add the following to the description of each bug named in the changelog, above
the original comment. If automated testing covers the issue, link the test and
the release pull request where it was exercised, and still include manual
verification steps.

Ubuntu Core-only Launchpad bugs do not require Launchpad bug verification.
State clearly when a bug is Ubuntu Core only.

.. code-block:: none

   [SRU <version>](https://bugs.launchpad.net/ubuntu/+source/snapd/+bug/<number>)

   [ Impact ]

   [ Test Plan ]

    1. Reproduce on reported snapd version <reported snapd version>

     [steps]

    2. Confirm fix on <candidate snapd version>

     [steps]

   [ Where problems could occur ]

   [ Other Info ]

   --- original ---

Related SRU interest team
-------------------------

SnapD has an :ref:`SRU interest team <reference-sru-interest-team>`. Subscribe
the `interest group <https://launchpad.net/~sru-verification-interest-group-snapd>`_
to the SRU bug early.

Appendix
--------

The topics below are not part of this exception. Public documentation is
linked first. The SnapD team's full statement, including development-cycle
practice, point-release timing, the sponsoring checklist, and the upstream
quality checklist, is the internal page
`SnapD updates in Ubuntu <https://documentation.ubuntu.com/canonical-snapd-lore/processes/snapd-updates-in-ubuntu/>`_.

Development cycle and freezes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SnapD updates during the development series, including between feature freeze
and beta freeze, are not granted here. The SRU team does not grant a standing
freeze exception.

The development series follows the :ref:`release cycle <release-cycle>`.
Freeze points, including :ref:`feature freeze <feature-freeze>` and
:ref:`beta freeze <beta-freeze>`, are described in :ref:`Freezes <freezes>`.
Exceptions are requested from the Release Team. See
:ref:`freeze exceptions <freeze-exceptions>` and
:ref:`request a freeze exception <request-a-freeze-exception>`.

Point releases
~~~~~~~~~~~~~~

Whether a SnapD update is included in an LTS point release, including any
cutoff such as the release date minus 14 days, is a Release Team decision.
This page does not grant it.

Point releases are described in :ref:`Ubuntu releases <ubuntu-releases>`
(:ref:`point releases <point-releases>`).

Sponsoring
~~~~~~~~~~

The SRU team takes the upload from ``-unapproved``. Copying it there is
sponsoring, not part of this exception.

A core developer copies the prepared source package from
``ppa:snappy-dev/image`` into ``-unapproved`` for each targeted stable
release, after the SnapD team requests that copy. Preparation of that PPA
upload, its test results, and the separate development-release upload to
``-proposed`` are described in the internal statement linked above.

General sponsoring practice is in :ref:`Sponsoring <sponsoring>`.

Upstream quality practice
~~~~~~~~~~~~~~~~~~~~~~~~~

Design approval, development rules, and experimental flags are how the SnapD
team gates risky work before an SRU. They are not a second SRU test plan. The
test plan in the process bug is what the SRU team verifies.

The release-testing diagram, which also covers the SnapD snap, is
`SnapD release testing <https://drive.google.com/file/d/1Rbs2l0YBaYQSxS4NgvzsoY8fL4gjBnu_/view?usp=sharing>`_.
The detailed checklist is in the internal statement linked above.

Key integrations
~~~~~~~~~~~~~~~~

The process bug's "Where problems could occur" section names the risk for
that upload. The standing list of Classic packages and subsystems SnapD
interacts with is
`SnapD key integrations <https://docs.google.com/document/d/1hNrDXVLJHD1igUSb3UNkhpVA3nx88cQzfIzs4LipwaY/edit>`_.

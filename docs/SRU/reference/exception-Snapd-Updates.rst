.. _reference-exception-snapdupdates:

SnapD Updates
=============

.. include:: /SRU/_sru-series-exception.rst

Introduction
------------

This document explains how SnapD updates deviate from the standard SRU policy,
outlining the background, deviations, and the responsibilities of the SnapD,
sponsor, and SRU teams in managing quality and risk.

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

Package behavior
~~~~~~~~~~~~~~~~

When the first snap is installed through the snapd deb, the snapd snap itself is
also installed, and the deb then re-executes into it. The snapd snap is kept up
to date through auto-refresh, ensuring that snapd always runs with the latest
features and fixes, and maintains consistency across Ubuntu releases regardless
of the host distribution’s update cadence.

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

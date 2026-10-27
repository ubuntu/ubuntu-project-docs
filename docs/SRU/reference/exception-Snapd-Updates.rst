.. _reference-exception-snapdupdates:

snapd Updates
=============

.. include:: /SRU/_sru-series-exception.rst

Introduction
------------

This document explains how snapd updates deviate from the standard SRU policy,
outlining the background, exceptions, and the responsibilities of the snapd,
sponsor, and SRU teams in managing quality and risk.

Background
----------

`snapd <https://github.com/canonical/snapd>`_ is a background service that
manages and maintains installed snaps. It is used on classic Ubuntu (and other
distributions) as well as on Ubuntu Core. From the perspective of the snapd
team, a release usually involves both a deb and snap package to serve the needs
of desktop, server, cloud and IOT use cases.

An important goal of the snapd project is to always keep systems up-to-date with
the latest security fixes, bug fixes and the latest features, while also
enabling developers to access system resources that are initially restricted by
interfaces but may be opened in a controlled manner to support new solutions.

The snapd value proposition is to allow installing robust software that can move
at a different pace than distributions, in a rolling release model. In order to
fulfill this, it needs to provide a security-maintained, consistent and
up-to-date runtime environment for them across distributions and distribution
versions. The design, development, and release processes limit the risk of
keeping that runtime up to date. They are described in the Quality Assurance
section of `snapd updates in Ubuntu
<https://documentation.ubuntu.com/canonical-snapd-lore/processes/snapd-updates-in-ubuntu/>`_.

snapd behaviour on Classic Ubuntu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- snapd is used during both installation and normal system operation.
- Installer LiveCD images are seeded with both snapd deb and snap packages and
  installs are seeded with the snapd deb package.
- Ubuntu supports and enables :ref:`re-execution <ref_reexecution>` during both
  installation and normal system operation.
- Due to re-execution, reverting the deb package alone does not necessarily
  revert the running snapd version if a newer or equal snap revision is still
  installed. For this reason, the snapd team chooses the mitigation
  :ref:`here <ref_revert>`, rather than through the standard SRU process for
  deb packages.
- Updates are released as deb and snap packages; the order of release may vary.
- The snapd deb package installs the systemd units and
  service integration that bootstrap snapd. The snapd snap also contains
  equivalent service integration, but this is only used on Ubuntu Core systems.
- Classic Ubuntu with TPM-backed full disk encryption, available from 26.04,
  requires a kernel snap, a base snap, and snapd for correct operation.

Exceptions
----------

snapd falls into the following overlapping :ref:`special types of SRU
<reference-special-types-of-sru>`. All snapd releases, regardless of the exact
category, are required to comply with the same thorough QA process, described
in the Quality Assurance section of `snapd updates in Ubuntu
<https://documentation.ubuntu.com/canonical-snapd-lore/processes/snapd-updates-in-ubuntu/>`_.

Package-specific non-standard process
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following exceptions to :ref:`what is acceptable to SRU
<reference-what-is-acceptable-to-sru>` apply to every snapd upload:

- The SRU will be done with a single process bug, instead of individual bug
  reports for individual bug fixes. This covers all supported interim releases
  in standard support and all LTS releases in standard support. Releases for
  the different targets must share the same source tree, with the only
  difference being the additional "backport" entry at the top of
  debian/changelog. See
  `snapd versioning <https://github.com/cpaelzer/ubuntu-maintainers-handbook/blob/d380ce51da109f8e27db5c6606f43f253b3bcd92/VersionStrings.md#version-almost-native-packages>`_.
- Individual bugs should be referenced in the changelog, and each bug needs to
  be independently verified and commented on for the SRU to be considered
  complete. Refer to the :ref:`SRU bug template <reference-sru-bug-template>`
  for details about the required documentation.
- Sponsors, the Ubuntu Release Team, and the SRU Team are not required to review
  all source changes, only those related to packaging and systemd/service
  integration. These changes must be clearly identified in the SRU bug.
- The SRU team delegates to the snapd team responsibility for ensuring that snapd
  updates delivered as debs or snaps, together with re-execution, automatic
  installation, and refresh behaviour, continue to meet Ubuntu release stability
  expectations throughout the lifetime of each supported Ubuntu release. As part
  of this responsibility, the snapd team may determine the optimal release order
  of snapd deb and snap updates for each release, since this can affect which
  snapd version is executed on a system.
- When the SRU team accepts an upload into *-proposed*, it applies
  *block-proposed-<series>* so the upload is not promoted to *-updates* on its
  own. The SRU team removes the block when the snapd team is ready to release.

.. _ref_revert:

- If a regression affecting Classic systems occurs, the SRU team may require a
  high-priority fix from the snapd team. The snapd team will select the most
  appropriate mitigation, such as a snapd deb-only update, a store-based snap
  revert, or a snap update, and is responsible for timely implementation and
  internal and public communication. Launchpad must be used as the primary
  means of communication and coordination.
- The snapd team is responsible for identifying invasive changes affecting
  Classic systems, including changes to documented re-execution or update
  behaviour, or changes that impact backward compatibility, and must bring such
  changes to the Technical Board for review before they are introduced.

New bugfix-only upstream release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Regular minor releases, as required to fix bugs.

New upstream release that adds features without breaking existing behaviour
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These updates are designed so existing behaviour does not
break. A feature that is not ready to be on by default stays behind an
experimental flag until the snapd architect enables
it.

- Regular major releases align with a full upstream release, typically 150-250
  pull requests, about half of which are test-related, and introduce complete
  or partial features alongside bug fixes and interface extensions.
- Regular minor releases may include low risk interface extensions that do not
  expose new hardware.

Hardware enablement
^^^^^^^^^^^^^^^^^^^

Some new interfaces give snaps access to hardware they could not use before.
That is :ref:`hardware enablement <reference-criteria-hardware>`: it must not
affect systems that already work. The same kind of interface change also
opens access to files, content, and other resources. Those additions are
unused until a snap is connected to them, so existing behaviour stays as it
is.

Non-standard package behaviour
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _ref_reexecution:

- When the first snap is installed through the snapd deb, the snapd snap itself is
  also installed, and the deb then re-executes into it. The snapd snap is kept up
  to date through auto-refresh, ensuring that snapd always runs with the latest
  features and fixes, and maintains consistency across Ubuntu releases regardless
  of the host distribution’s update cadence.
- Because the deb re-executes into an equal or newer snap, reverting or
  downgrading the deb leaves that snap running.

Review
------

The SRU team does not review the upstream changes. It confirms that the upload
matches the release tag except for the additional Go and C vendoring, and it
reviews the packaging and systemd/service integration changes identified in the
SRU bug.

Across the targeted releases, the source tarballs and vendored dependencies
match, and the changelogs differ only by the backport entry.

Each Launchpad bug that is relevant to Ubuntu uses the :ref:`SRU bug template
<reference-sru-bug-template>` and is verified in *-proposed*. The SRU team
checks that the release testing listed in the :ref:`SRU template
<ref_sru_template>` passed. On acceptance into *-proposed*, the SRU team
applies *block-proposed-<series>* and removes it when the snapd team is ready
to release.

.. _ref_sru_template:

SRU Template
------------

Sponsoring Request
^^^^^^^^^^^^^^^^^^

This refers to the "single process bug" that links to one or more Launchpad
bugs associated with the release.

.. code-block::

 This is a new snapd release.
 snapd [bugfix only] release 2.XX[.X] should be released to:
 - [Development Release]
 - [Latest LTS]
 - ... -
 - [Oldest LTS]

 The snapd package deviates from the standard SRU process. The following special
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
  - [Hardware enablement]
  - [Other interface extensions]
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
  - snapd deb testing on `ppa:snappy-dev/image`: <JIRA URL>

 Validation required before release:
  - Autopkgtests on `-proposed` for all targeted releases
  - snapd deb testing on `-proposed`
  - snapd snap testing

Sponsoring Request Final Test Feedback
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following updates from the snapd team are required before considering
releasing to *-updates*:

.. code-block::

 - Autopkgtests on `-proposed` for all targeted releases: <RESULT>
 - snapd deb testing on `-proposed`: <RESULT>
 - snapd snap testing: <RESULT>

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

Ubuntu Core only Launchpad bugs do not require Launchpad bug verification.
Clearly indicate if a Launchpad bug is Ubuntu Core only.

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

snapd has a :ref:`SRU Interest Team <reference-sru-interest-team>`,
please subscribe the
`Interest group <https://launchpad.net/~sru-verification-interest-group-snapd>`_
to the SRU bug early on.

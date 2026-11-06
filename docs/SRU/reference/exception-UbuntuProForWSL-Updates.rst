.. _reference-exception-UbuntuProForWSLUpdates:

Ubuntu Pro For WSL Updates
==================================================

.. include:: /SRU/_sru-series-exception.rst

Background
----------------

Ubuntu Pro is a suite of additional services provided by Canonical on
top of Ubuntu. It is an essential part of the Ubuntu ecosystem: as well
as providing services often required by commercial Ubuntu users, it also
provides a mechanism to fund Ubuntu development itself.

Ubuntu Pro for WSL extends Ubuntu Pro services specific to the WSL platform. It
offers compliance services tailored for WSL instances and manages these
instances by automatically attaching to Pro and registering them in Landscape.

In a large organisation, numerous repetitive steps are necessary to maintain
compliance. Ubuntu Pro for Windows streamlines this process by automating these
tasks across the entire enterprise landscape.

Ubuntu Pro for Windows is beneficial for corporate security teams, system
administrators, and desktop users, who would otherwise have to individually and
manually manage instances.

The project is made of 2 components:

- A Windows agent installed from the Microsoft Store and WinGet
- An Ubuntu service installed from the archive (``wsl-pro-service``).

For context only LTS releases are published to the WSL distributions catalog.
The scope of the SRU is the ``wsl-pro-service`` package on LTS releases back to
20.04.

Exceptions
----------------

Ubuntu Pro for WSL, being an extension of the Ubuntu Pro suite,
:doc:`adheres to similar exceptions <exception-UbuntuAdvantageTools-Updates>`.
In particular, we
maintain the facilities that enable access to Ubuntu Pro in the main Ubuntu
archive itself. This includes feature updates to these facilities as services
provided by Ubuntu Pro for WSL change over time and as tooling is improved,
including in stable Ubuntu releases during their lifetimes.

We do not generally accept changes in the main Ubuntu archive after an
Ubuntu release has reached End of Standard Support, but we make an
exception for Ubuntu Pro facilitation since Ubuntu Pro services include
support in the time period between End of Standard Support and End of
Life, and significant updates to facilitation tooling are often required
in this period.

The key package enabling Ubuntu Pro on WSL is ``wsl-pro-service``, which
relies solely on ``ubuntu-pro-client``, already an exception. In cases
where frequent updates to ``wsl-pro-service`` are needed, we have
established specific policies and processes to manage these exceptional
updates efficiently, minimising review iterations and changes.

Given that these updates may occur in stable releases at any time,
adhering strictly to the feature freeze during development cycles would
be impractical, as it would delay necessary changes until after release.
Therefore, feature freeze rules do not apply to changes covered in this
document. However, starting from the beta freeze, uploads of this
package will undergo the same rigorous review by the Release Team as any
other package.

.. _pro_for_wsl_summary_of_exceptions:

Summary of exceptions
---------------------

These specific exceptions require approval by the team indicated.

#. [TB] Facilities that enable access to Ubuntu Pro for WSL may be added to the
   main Ubuntu archive and installed by default. 

#. [SRU] Feature updates are permitted subject to SRU team review on a
   case-by-case basis, and for the ubuntu-advantage-tools package
   according to the policies, processes and limitations specified by the
   SRU team and documented below.

#. [TB/SRU] Updates shall be permitted as usual for SRUs and additionally after
   EoSS.

#. [Release team] Feature freeze in the development release shall not apply.

.. _pro_for_wsl_updating_the_wsl_pro_service_package:

Updating the wsl-pro-service package
------------------------------------

.. _pro_for_wsl_integrations_and_interactions:

Integrations and Interactions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``wsl-pro-service`` package has key interactions with the following
system components:

- ubuntu-pro-client
- landscape-client

.. _pro_for_wsl_mitigating_risk:

Mitigating Risk
---------------

Even though the service itself is opt-in and requires a subscription,
this package is installed on all Ubuntu WSL systems, and therefore we
have to be very careful that all reasonable use cases, not just Pro use
cases, will remain unaffected by any changes made to this package.

Sometimes this extends beyond what we might consider to be supportable
configurations; we try to stretch so that no user who appears to have an
otherwise functional system is affected by this package or by changes to
it.

This includes:

- Regressions caused by the introduction of new dependencies conflicting
  with existing deployments; for this reason the introduction of new
  dependencies will generally not be acceptable.
- Performance regression, for example in boot speed.
- Users who have taken efforts to remove or disable Ubuntu Pro or
  wsl-pro-service somehow, such as modifications and removals of
  configuration files in /etc, disabling or masking of systemd services,
  disabling or restricting Windows interoperability or any other
  generally supported mechanism. In this case, the instance will stop
  being managed by Ubuntu Pro for WSL. It may still be registered in
  Landscape though.
- Users running air-gapped or with limited Internet connectivity, and
  with related system configurations such as proxies and local mirrors.

In general we should avoid taking any additional action unless a user
has specifically opted in to Ubuntu Pro services, such as
interoperability settings, general WSL settings, Internet access, steps
during boot that would take additional time, or enabling system services
or timers. Where default system configuration is affected, we should
leave a documentation trail starting at any point a user might observe
it that will give non-Pro users confidence as to why their system will
not be affected.


.. _pro_for_wsl_maintaining_upgrade_paths:

Maintaining upgrade paths
-------------------------

As the Pro for WSL service evolves, new versions implement upgrade paths
to seamlessly move Pro users to updated and supported Pro system
configurations. For example, wsl-pro-service.postinst must contain
upgrade path code that moves or otherwise migrates files that contain
state, and the latest WSL Pro Service depends on the updated state
formats and locations.

This has the consequence that upgrade paths need to be maintained nearly
forever. For example, within a single release, a user might not be
installing updates for years whether with or without Pro enabled, then
upgrades everything. Upgrading from the release pocket version of the
WSL Pro service all the way up to the latest version must therefore be
supported. For us, this effectively means that we have to support
upgrading from any version that the user could have installed all the
way up to the latest version.

We do have the rule that prior to a release upgrade, users are expected
to be fully up-to-date, and that we do not support upgrading further
than an LTS at once. This does set an upper bound and allow us to
discard code supporting very old upgrade paths, but you'll note that
since the WSL Pro service is maintained as a single source tree that
applies to all releases, the code base going into the development
release still has to carry all the old baggage going all the way back to
the oldest non-EOL release at that time.


Requirements
------------

- Interim releases are not produced nor supported for WSL. If an update
  targets one stable release, it must also target all subsequent LTS
  releases and the development release.

- Wsl-pro-service will be uploaded to non-LTS interim releases for
  consistency. However, since we do not publicize WSL images for non-LTS
  interim releases, its reachability is limited to those who have performed the
  extra steps needed to install an interim release.

- All releases shall share the same source tree, with the only
  difference being the additional "backport" entry at the top of
  debian/changelog. This is to make the process simpler, and so the
  process documented here assumes this.

.. _pro_for_wsl_upstream_qa:

Upstream QA
-----------

The QA process is detailed in `upstream QA documentation <https://ubuntu.com/wsl/docs/en/latest/reference/09-qa-process-reference/>`_.
The `Ubuntu Pro for WSL repo <https://github.com/canonical/ubuntu-pro-for-wsl/actions/workflows/qa.yaml>`_
has a suite of automated integration tests that cover WSL in
Azure and on real hardware. It exercises the bulk of features
functionality delivered on all supported releases, i.e. LTS releases
both active or ESM from 20.04 onwards, as well as the development
release.

CI runs both tip of main against daily `images
<https://cdimages.ubuntu.com/ubuntu-wsl/>`_ and against any `pull requests
<https://github.com/canonical/ubuntu-pro-for-wsl/pulls>`_ before merging.

Updates to tip of `main
<https://github.com/canonical/ubuntu-pro-for-wsl/tree/main|ubuntu-pro-for-wsl>`_
go through the following process:

- Reviewed and approved by a member of the development team (Canonical
  Ubuntu WSL team only)

- Daily integration tests on tip

- Successful run of security scanning, unit tests, style and integration tests
  based on the branch

- Branch manually set to the merged state by the approving development
  member with commit access.

- Upgrades to interim releases are not supported and will not be tested.

.. _pro_for_wsl_upload_process:

Upload Process
--------------

Documentation
-------------

The change log will contain a reference to the SRU process bug, as well
as all pre-existing Launchpad issues and
`GitHub issues <https://github.com/canonical/ubuntu-pro-for-wsl/issues>`_
that are fixed; however, not all changes will be represented by an
individual bug tracker's bug.

Major changes must be called out, especially where changed behaviour is
not backward compatible.

Any packaging changes (e.g. a dependency change) need to be stated, and
appropriate separate test cases provided.

Any architecture-specific fixes need to be noted and
architecture-specific test cases provided.

The following types of changes must be called out for explicit SRU
review:

#. How the tool interacts with systemd.
#. How the tool interacts with ubuntu-pro-client.
#. Anything that changes Windows interoperability.
#. Anything that changes WSL default behaviour.
#. Anything that changes network traffic patterns, including anything that might
   "phone home".
#. Anything that changes the use of persistent processes or scheduled jobs.
#. Changes that affect what part of the namespace in PATH we consume.
#. Actions that take place without an explicit user opt-in (running the
   CLI to perform a specific task counts as opt-in for that task).

Normally SRUs are expected to be well tested upstream or in the
development release to gain confidence in correctness. In this case we
don't get wide exposure since the nature of the package is that it is
widely used in LTS only. However it is still worth testing on non-WSL
system that the service doesn't start.

Review/Sponsoring
-----------------

Using the normal process would mean that if something is asked to be
changed in SRU review, the change has already been uploaded to the
development release, and to keep things aligned the development release
then has to change again, or we have to diverge causing development and
review pain.

Instead, once upstream are ready, all reviewing for the subsequent
Ubuntu uploads are done from either a single merge proposal on Launchpad
or a single pull request on GitHub (hereinafter "MP"):

#. A person who has permission to upload the package to the development
   release performs a review **but does not upload** and iterates with
   upstream as required.

#. The SRU team then also reviews the proposed upload as they would for
   a normal SRU review but **prior to upload** and iterates on code
   changes and SRU documentation as required. This is done from the MP
   rather than the Unapproved queue. To minimise the effort involved in
   handling the many required uploads to stable releases, the SRU team
   expects to review just this one MP for the development release, and
   expects that the subsequent uploads to the stable releases will be
   identical to what was reviewed except for the straight backport
   package version and changelog changes.

#. Currently, the SRU review includes:

   -  a. A commit by commit review as presented by upstream, looking for the types of issues :ref:`described above <mitigating_risk>`. This is because that list is not exhaustive, and we have caught multiple issues this way either at this step or later on that have needed fixing.

   -  b. The usual SRU review checks, such as that all changes made appear to fit within the definition of the exception, that the version numbers are sensible, the Test Plan is reasonable given the specific changes being made, and so forth.

#. During review, areas warranting additional testing may be identified,
   and these will be added to the Test Plan for manual testing, or
   automated testing added, for testing at SRU review time.

#. After both the uploader and an SRU team member has approved, the
   uploader uploads the package to the development release, and also
   uploads to all stable releases as straight backports.

#. The SRU team member who approved the MP verifies that all SRU uploads
   are identical to what they reviewed, and then accepts the stable
   uploads from Unapproved.

Verification
------------

For each Ubuntu release that is targeted by the SRU, successful results
of integration testing of the -proposed package for at least the
following platforms must be provided.

- Azure Windows 10+ VM with WSL LTS releases targeted by the SRU.
- Real hardware with Windows 11 and WSL LTS releases targeted by the SRU.
- LTS to LTS upgrade test of attached machine for all affected LTS.
- LTS to LTS upgrade test of unattached machine for all affected LTS.

If the Test Plan calls for any additional manual testing, such testing
and its results must be documented, usually in the associated bugs
linked from the changelog.


.. _pro_for_wsl_sru_bug_template:

SRU Bug Template
----------------------

::

   [ Impact ]

   This release brings both bug-fixes and new features for the Ubuntu Pro for WSL service, and we would
   like to make sure all of our supported customers have access to these improvements on all releases.

   The most important changes are:

   <create a list with the spotlight fixes and features>

   See the changelog entry below for a full list of changes and bugs.

   [ Test Plan ]

   The following development and SRU process was followed:

   <https://wiki.ubuntu.com/UbuntuProForWSLUpdates>

   The Ubuntu Pro for WSL developers will be in charge of attaching the artefacts of the appropriate
   test runs to the bug, and will not mark 'verification-done' until this has happened.

   Besides the full integration test runs, manual tests were executed to verify bugs:

   <list bugs which required manual testing>

   [ Where problems could occur ]

   In order to mitigate the regression potential of the changes in this version, the results of the
   integration tests suite runs are attached to this bug.

   Other considerations not covered by the integration test suite are:

   * Think about what the upload changes in the software. Imagine the change is wrong or breaks
   something else: how would this show up?

   * This must '''never''' be "None" or "Low", or entirely an argument as to why your upload
   is low risk.

   * This both shows the SRU team that the risks have been considered, and provides guidance to
   testers in regression-testing the SRU.

   [ Other Info ]

   * Anything else you think is useful to include

   * Anticipate questions from users, SRU, +1 maintenance, security teams and the Technical Board and
   address these questions in advance

   [ Changelog ]

   <insert changelog entry>

Related SRU Interest Team
-------------------------

Ubuntu Pro Client has a :ref:`SRU Interest Team <reference-sru-interest-team>`. 
Members of the WSL team working on Ubuntu Pro for WSL are subscribers of the
`Pro Client Interest group
<https://launchpad.net/~sru-verification-interest-group-ubuntu-pro-client>`_.
to be early notified of changes that may affect the integration with WSL.


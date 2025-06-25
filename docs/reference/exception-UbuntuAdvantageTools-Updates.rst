.. _reference-exception-UbuntuAdvantageToolsUpdates:

Ubuntu-Advantage-Tools / Ubuntu-Pro-Client Updates
==================================================

U-A-T Background
----------------

Ubuntu Pro is a suite of additional services provided by Canonical on
top of Ubuntu. It is an essential part of the Ubuntu ecosystem: as well
as providing services often required by commercial Ubuntu users, it also
provides a mechanism to fund Ubuntu development itself.

Ubuntu Pro provides packages outside Ubuntu's main archive, so it is
often necessary to enable extra apt repositories to receive Ubuntu Pro
services. In many cases, further system configuration changes are also
required.

Ubuntu Pro provides tooling to make these configuration changes easy for
users. However, this results in a circular UX problem: if this tooling
were shipped in the additional Ubuntu Pro apt archives, then users would
face complexity in the form of multiple steps to fully configure their
systems for Ubuntu Pro services.

U-A-T Exceptions
----------------

Since we want to make access to Ubuntu Pro easy for Ubuntu users, we
resolve the circular UX problem by making the exception that we will
place and maintain the facilities that enable access to Ubuntu Pro in
the main Ubuntu archive itself. This includes feature updates to these
facilities as services provided by Ubuntu Pro change over time and as
tooling is improved, including in stable Ubuntu releases during their
lifetimes.

We do not generally accept changes in the main Ubuntu archive after an
Ubuntu release has reached End of Standard Support, but we make an
exception for Ubuntu Pro facilitation since Ubuntu Pro services include
support in the time period between End of Standard Support and End of
Life, and significant updates to facilitation tooling are often required
in this period.

The primary package providing Ubuntu Pro facilitation is
ubuntu-advantage-tools. Other packages are also involved and exceptions
for those will be handled by the SRU team on a case-by-case basis.
Updates to ubuntu-advantage-tools are required more frequently, so below
we define specific policy and process and requirements for handling
these exceptional uploads to ubuntu-advantage-tools, in order to reduce
review iteration and changes for these updates.

Since these feature changes may land in stable releases at any time,
adhering to feature freeze during the development cycle would be
counterproductive as those changes would be forced to land after release
instead. Therefore, feature freeze will not apply when the changes are
in scope of this document. However, from beta freeze on uploads of this
package will be subject to the same additional scrutiny by the Release
Team as any other package.

.. _summary_of_exceptions:

Summary of exceptions
---------------------

These specific exceptions have been approved by the team indicated.

#. Facilities that enable access to Ubuntu Pro may be added to the main
   Ubuntu archive and installed by default. `Signed off by the Technical
   Board on
   2023-10-10 <https://irclogs.ubuntu.com/2023/10/10/%23ubuntu-meeting.html#t19:18>`__.

#. Feature updates are permitted subject to SRU team review on a
   case-by-case basis, and for the ubuntu-advantage-tools package
   according to the policies, processes and limitations specified by the
   SRU team and documented below. `Signed off by Robie Basak on behalf
   of the SRU team on
   2023-10-04 <https://lists.ubuntu.com/archives/ubuntu-release/2023-October/005810.html>`__.

#. Updates shall be permitted as usual for SRUs and additionally after
   EoSS. `Signed off by the Technical Board on
   2023-10-10 <https://irclogs.ubuntu.com/2023/10/10/%23ubuntu-meeting.html#t19:18>`__.

#. Feature freeze in the development release shall not apply. `Signed
   off by Lukasz Zemczak on behalf of the Release Team on
   2023-11-27 <https://lists.ubuntu.com/archives/ubuntu-release/2023-November/005844.html>`__.

.. _updating_the_ubuntu_advantage_tools_package:

Updating the ubuntu-advantage-tools package
-------------------------------------------

.. _integrations_and_interactions:

Integrations and Interactions
-----------------------------

The ubuntu-advantage-tools package has key interactions with the
following system components:

-  apt and snapd
-  update-manager, update-notifier and unattended-upgrades

.. _mitigating_risk:

Mitigating Risk
---------------

Even though Pro itself is opt-in, this package that provides it is
installed on all Ubuntu systems (see LP: #1950692), and therefore we
have to be very careful that all reasonable use cases, not just Pro use
cases, will remain unaffected by any changes made to this package.

Sometimes this extends beyond what we might consider to be supportable
configurations; we try to stretch so that no user who appears to have an
otherwise functional system is affected by this package or by changes to
it.

This includes:

-  Regressions caused by the introduction of new dependencies
   conflicting with existing deployments; for this reason the
   introduction of new dependencies will generally not be acceptable.

-  Performance regression, for example in boot speed.

-  Users who have modified their system Python installations.

-  Users who have taken efforts to remove or disable Pro somehow, such
   as modifications and removals of configuration files in /etc,
   disabling or masking of systemd services, or any other generally
   supported mechanism.

-  Users running air-gapped or with limited Internet connectivity, and
   with related system configurations such as proxies and local mirrors.

In general we should avoid taking any additional action unless a user
has specifically opted in to Ubuntu Pro services, such as Internet
access, steps during boot that would take additional time, or enabling
system services or timers. Where default system configuration is
affected, we should leave a documentation trail starting at any point a
user might observe it that will give non-Pro users confidence as to why
their system will not be affected.

For example, in previous updates we have done the following:

#. We limited the scope of auto-attach checks by only checking for this
   on clouds that support the feature, since cloud-init already knows
   what cloud we're on. This makes auto-attach detection have zero side
   effects on the majority of Ubuntu systems.

#. We mark files that we drop in /etc with appropriate documentation for
   non-Pro users.

.. _maintaining_upgrade_paths:

Maintaining upgrade paths
-------------------------

As the Pro service evolves, new versions of the Pro client implement
upgrade paths to seamlessly move Pro users to updated and supported Pro
system configurations. For example, ubuntu-advantage-tools.postinst
contains upgrade path code that moves or otherwise migrates files that
contain state, and the latest Pro client depends on the updated state
formats and locations.

This has the consequence that upgrade paths need to be maintained nearly
forever. For example, within a single release, a user might not be
installing updates for years whether with or without Pro enabled, then
upgrades everything. Upgrading from the release pocket version of the
Pro client all the way up to the latest version must therefore be
supported. For us, this effectively means that we have to support
upgrading from any version that the user could have installed all the
way up to the latest version.

We do have the rule that prior to a release upgrade, users are expected
to be fully up-to-date, and that we do not support upgrading further
than an LTS at once. This does set an upper bound and allow us to
discard code supporting very old upgrade paths, but you’ll note that
since the Pro client is maintained as a single source tree that applies
to all releases, the code base going into the development release still
has to carry all the old baggage going all the way back to the oldest
non-EOL release at that time.

This is a considerable burden and should be considered when designing
components that require state, or in deciding upon making changes to
state schema.

Requirements
------------

-  If an update targets one stable release, it must also target all
   subsequent releases (whether interim or LTS) and the development
   release.

-  All releases shall share the same source tree, with the only
   difference being the additional “backport” entry at the top of
   debian/changelog. This is to make the process simpler, and so the
   process documented here assumes this.

.. _upstream_qa:

Upstream QA
-----------

ubuntu-advantage-client repo has a suite of automated integration tests
that cover AWS Pro, LXD container and KVM images and exercises the bulk
of features functionality delivered on all supported releases, i.e. LTS
releases both active or ESM, and the active interim releases. . CI runs
both tip of main against daily cloud-images and against any
https://github.com/canonical/ubuntu-advantage-client/pulls before
merging.

Updates to tip of
`ubuntu-advantage-tools:main <https://github.com/canonical/ubuntu-advantage-client/tree/main>`__
go through the following process:

-  Reviewed and approved by a member of the development team (Canonical
   Ubuntu server team only)

-  Daily integration tests on tip

-  Successful run of unit tests, style and integration tests based on
   the branch

-  Branch manually set to the merged state by the approving development
   member with commit access.

Further details to the upstream release process are documented in the
`“how to release
guide” <https://github.com/canonical/ubuntu-pro-client/blob/docs/dev-docs/howtoguides/release_a_new_version.md>`__.

.. _upload_process:

Upload Process
--------------

Documentation
-------------

The change log will contain a reference to the SRU process bug, as well
as all pre-existing Launchpad and GitHub bugs that are fixed; however,
not all changes will be represented by an individual Launchpad bug.

Major changes must be called out, especially where changed behavior is
not backward compatible.

Any packaging changes (e.g. a dependency change) need to be stated, and
appropriate separate test cases provided.

Any architecture-specific fixes need to be noted and
architecture-specific test cases provided.

The following types of changes must be called out for explicit SRU
review:

#. How the tool interacts with apt.

#. How the tool interacts with systemd.

#. Anything that changes network traffic patterns, including anything
   that might "phone home".

#. Anything that changes the use of persistent processes or scheduled
   jobs.

#. Changes that affect what part of the namespace in PATH we consume.

#. Actions that take place without an explicit user opt-in (running the
   CLI to perform a specific task counts as opt-in for that task).

Normally SRUs are expected to be well tested upstream or in the
development release to gain confidence in correctness. In this case we
don't get wide exposure since the nature of the package is that it is
widely used in LTSes only.

Review/Sponsoring
-----------------

Using the normal process would mean that if something is asked to be
changed in SRU review, the change has already been uploaded to the
development release, and to keep things aligned the development release
then has to change again, or we have to diverge causing development and
review pain.

Instead, once upstream are ready, all reviewing for the subsequent
Ubuntu uploads are done from either a single merge proposal on Launchpad
or a single pull request on !GitHub (hereinafter "MP"):

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

-  LXD VM and container of all LTS and interim releases targeted by the
   SRU.
-  EC2 Ubuntu Pro images and standard Ubuntu cloud images on all LTS
   releases
-  Azure Ubuntu Pro images and standard Ubuntu cloud images on all LTS
   releases
-  GCP Ubuntu Pro images and standard Ubuntu cloud images on all LTS
   releases
-  Once https://wiki.ubuntu.com/UbuntuProForWSLUpdates is approved and
   active we'll run the applicable subset of the integration test on
   that virtual substrate on all supported LTS releases. In addition we
   will run the related tests of the WSL team.
-  LTS to LTS upgrade test of attached machine for all affected LTS
-  LTS to LTS upgrade test of unattached machine for all affected LTS

If the Test Plan calls for any additional manual testing, such testing
and its results must be documented, usually in the associated bugs
linked from the changelog.

.. _sru_bug_template:

U-A-T SRU Bug Template
----------------------

::

   [ Impact ]

   This release brings both bug-fixes and new features for the Pro Client, and we would like to make sure all of our supported customers have access to these improvements on all releases.

   The most important changes are:
   <create a list with the spotlight fixes and features>

   See the changelog entry below for a full list of changes and bugs.

   [ Test Plan ]

   The following development and SRU process was followed:
   https://documentation.ubuntu.com/sru/en/latest/reference/exception-UbuntuAdvantageTools-Updates

   The Pro Client developers will be in charge of attaching the artifacts of the appropriate test runs to the bug, and will not mark ‘verification-done’ until this has happened.

   Besides the full integration test runs, manual tests were executed to verify bugs: 
   <list bugs which required manual testing>

   [ Where problems could occur ]

   In order to mitigate the regression potential of the changes in this version, the results of the integration tests suite runs are attached to this bug.

   Other considerations not covered by the integration test suite are:

   * Think about what the upload changes in the software. Imagine the change is wrong or breaks something else: how would this show up?

   * This must '''never''' be "None" or "Low", or entirely an argument as to why your upload is low risk.

   * This both shows the SRU team that the risks have been considered, and provides guidance to testers in regression-testing the SRU.

   [ Other Info ]

   * Anything else you think is useful to include

   * Anticipate questions from users, SRU, +1 maintenance, security teams and the Technical Board and address these questions in advance

   [ Changelog ]

   <insert changelog entry>

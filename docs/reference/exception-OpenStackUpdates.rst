#. 

   #. page was renamed from OpenStack/SRUs
   #. page was renamed from ServerTeam/OpenStackStableReleaseUpdates

.. _stable_release_updates_for_openstack_and_the_ubuntu_cloud_archive:

Stable Release Updates for OpenStack and the Ubuntu Cloud Archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SRU process for !OpenStack and the Ubuntu Cloud Archive (UCA)
follows the same process as `Ubuntu Stable Release
Updates <https://wiki.ubuntu.com/StableReleaseUpdates>`__. This page
summarises the process for the cloud archive and adds some points that
apply specifically to it.

**NOTE**: This process is followed for !OpenStack packages and
supporting dependencies such as Open vSwitch and Ceph.

.. _package_list:

Package List
------------

.. _openstack_packages:

OpenStack packages
~~~~~~~~~~~~~~~~~~

-  

   -  aodh
   -  barbican
   -  ceilometer
   -  cinder
   -  designate
   -  glance
   -  gnocchi
   -  heat
   -  horizon
   -  keystone
   -  neutron
   -  neutron-lbaas
   -  neutron-fwaas
   -  neutron-vpnaas
   -  nova
   -  octavia
   -  placement
   -  swift

.. _supporting_packages:

Supporting packages
~~~~~~~~~~~~~~~~~~~

-  

   -  ceph
   -  openvswitch
   -  ovn

.. _sru_expectations:

SRU Expectations
----------------

-  

   -  Users of official releases expect a high degree of stability.
   -  It is critically important to treat SRUs with great caution.
   -  SRUs must be accompanied by a strong rationale and must present a
      low risk of regression.
   -  Minimizing risk tends to be well-correlated with minimizing the
      size of the change. As such, the same bug may need to be fixed in
      different ways in stable and development releases.
   -  Stable release updates will, in general, only be issued in order
      to fix:

| ``   * New upstream stable point releases for !OpenStack core packages which group several bug fixes together.``
| ``   * High-impact bugs (e.g. security vulnerabilities, severe regressions, loss of user data).``
| ``   * Bugs that are not high-impact, but have an obviously safe patch.``

-  

   -  An SRU must have an accompanying bug, and that uses a prescribed
      format (see the `template below <#sru-template>`__). It must
      contain details as described in the `Ubuntu Stable Release Updates
      procedure <https://wiki.ubuntu.com/StableReleaseUpdates#Procedure>`__.
   -  Bugs must be fixed in the following order, when possible:

| ``   1. Upstream in the latest !OpenStack release [1]``
| ``   1. The corresponding Ubuntu release [2]``
| ``   1. The corresponding UCA release``
| ``   1. The bug can then be fixed in the same order for the prior !OpenStack release:``
| ``      1. upstream stable``
| ``      1. corresponding Ubuntu release``
| ``      1. corresponding UCA release``

| ``[1] /!\ Landing a fix upstream may not always be possible, for example once the upstream branch is in critical-fix or security-fix only mode, or once it has reached EOL.  See the ``\ ```OpenStack upstream stable branch policy`` <http://docs.openstack.org/project-team-guide/stable-branches.html>`__\ ``, which specifies the various phases of support for stable branches, which are typically supported for 12 to 18 months.  The case where a bug can't be fixed upstream first must be handled with extreme caution, since fixes would be released directly to the corresponding Ubuntu release without having landed upstream first.``
| ``[2] /!\ Landing a fix in a corresponding Ubuntu release may not always be possible, for example once the Ubuntu release has reached EOL and the UCA is still supported.  This case must be handled with extreme caution, since fixes would be released directly to the corresponding UCA without having first landed in the corresponding Ubuntu release, and possibly also without having first landed in the upstream !OpenStack release.``

.. _qa_process:

QA Process
----------

Once stable package updates have been accepted by the ubuntu-sru (or
Cloud Archive) team into -proposed pockets, the following SRU
verification process is followed:

-  

   -  Deployment and base configuration using `OpenStack Charm
      Testing <https://github.com/openstack-charmers/openstack-charm-testing>`__
      bundles and charms, using the current set of stable charms
      configured to consume packages from the proposed pocket of the
      archive.

-  

   -  Testing of the deployed Cloud using the
      `Tempest <https://github.com/openstack/tempest>`__ (the !OpenStack
      functional test project) smoke test target; this is approximately
      100 tests from the full Tempest upstream function test suite that
      cover all core functions of the cloud. The deployed cloud is
      expected to pass all smoke tests.

For updates where there is risk of regression as a result of the package
upgrade process, the same testing process is followed as above,
deploying from archive excluding proposed, testing using Tempest,
upgrading the deployed cloud to proposed and then re-verifying the cloud
using Tempest.

This testing process is automated by the `Ubuntu OpenStack CI
system <https://launchpad.net/ubuntu-openstack-ci>`__.

Additionally, any specific test cases covered in SRU bug reports should
be explicitly tested as well.

<<Anchor(sru-template)>>

.. _sru_template:

SRU Template
------------

::

   == Begin SRU Template ==
   [Impact]
   This release sports mostly bug-fixes and we would like to make sure all of our
   users have access to these improvements.

   The update contains the following package updates:

   *** <TODO: Create list with package names and versions>

   [Test Case]
   The following SRU process was followed:
   https://wiki.ubuntu.com/OpenStack/StableReleaseUpdates

   In order to avoid regression of existing consumers, the OpenStack team will
   run their continuous integration test against the packages that are in
   -proposed.  A successful run of all available tests will be required before the
   proposed packages can be let into -updates.

   The OpenStack team will be in charge of attaching the output summary of the
   executed tests. The OpenStack team members will not mark ‘verification-done’ until
   this has happened.

   [Regression Potential]
   In order to mitigate the regression potential, the results of the
   aforementioned tests are attached to this bug.

   [Discussion]
   <TODO: other background>

   == End SRU Template ==

.. _nominating_a_bug_for_a_series:

Nominating a Bug for a Series
-----------------------------

A sponsor can be asked to nominate a bug for a particular series. You
can find the following sponsors in #ubuntu-server on freenode:

-  To target an Ubuntu series: coreycb, jamespage
-  To target an Ubuntu Cloud Archive series: coreycb, jamespage,
   dosaboy, wolsen

Getting permission to target a bug for a series:

-  To gain permission to target a bug for an Ubuntu series you must be a
   member of: https://launchpad.net/~ubuntu-bugcontrol
-  To gain permission to target a bug for an Ubuntu Cloud Archive series
   you must be a member of:
   https://launchpad.net/~ubuntu-cloud-archive-bugs

.. _getting_package_source:

Getting Package Source
----------------------

Depending on the package and the release, there are different ways to
download the package source:

-  Core !OpenStack packages are `maintained in git on
   Launchpad <https://code.launchpad.net/~ubuntu-server-dev/+git>`__.
   See `OpenStack Core
   Packages <https://wiki.ubuntu.com/OpenStack/CorePackages>`__ for
   information on how to work with these repositories.

-  Packages can be retrieved from Launchpad with the \`pull-lp-source\`
   tool:

   -  

      -  \`pull-lp-source [release|version]\` (e.g. \`pull-lp-source
         python-oslo.messaging bionic\`)

-  Packages can be retrieved from the UCA with the pull-uca-source tool:

   -  

      -  \`pull-uca-source [release|version]\` (e.g. \`pull-uca-source
         python-oslo.messaging queens\`)

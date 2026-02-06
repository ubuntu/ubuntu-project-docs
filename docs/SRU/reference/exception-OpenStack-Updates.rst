.. _reference-exception-OpenStackUpdates:

Stable Release Updates for OpenStack and the Ubuntu Cloud Archive
=================================================================

The SRU process for !OpenStack and the Ubuntu Cloud Archive (UCA)
follows the same process as `Ubuntu Stable Release
Updates </howto/standard>`__. This page
summarises the process for the cloud archive and adds some points that
apply specifically to it.

**NOTE**: This process is followed for !OpenStack packages and
supporting dependencies such as Open vSwitch and Ceph.


Package List
------------

.. _openstack_packages:

OpenStack packages
------------------

-  aodh
-  barbican
-  ceilometer
-  cinder
-  designate
-  glance
-  gnocchi
-  heat
-  heat-dashboard
-  horizon
-  keystone
-  magnum
-  magnum-ui
-  manila
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
-------------------

-  ceph
-  openvswitch
-  ovn

.. _openstack_sru_expectations:

SRU Expectations
----------------

-  Users of official releases expect a high degree of stability.
-  It is critically important to treat SRUs with great caution.
-  SRUs must be accompanied by a strong rationale and must present a
   low risk of regression.
-  Minimizing risk tends to be well-correlated with minimizing the
   size of the change. As such, the same bug may need to be fixed in
   different ways in stable and development releases.
-  Stable release updates will, in general, only be issued in order
   to fix:

   -  New upstream stable point releases for OpenStack core packages which group several bug fixes together.
   -  High-impact bugs (e.g. security vulnerabilities, severe regressions, loss of user data).
   -  Bugs that are not high-impact, but have an obviously safe patch.

-  An SRU must have an accompanying bug, and that uses a prescribed
   format (see the :ref:`template below <openstack_sru_template>`). It must
   contain details as described in the :ref:`Stable Release Updates <howto-perform-standard-sru>`.
-  Bugs must be fixed in the following order, when possible:

   #.  Upstream in the latest !OpenStack release [1]
   #.  The corresponding Ubuntu release [2]
   #.  The corresponding UCA release
   #.  The bug can then be fixed in the same order for the prior !OpenStack release:
       #.  upstream stable
       #.  corresponding Ubuntu release
       #.  corresponding UCA release

.. warning::
    [1] Landing a fix upstream may not always be possible, for example once the upstream branch is in critical-fix or security-fix only mode, or once it has reached EOL.  See the `OpenStack upstream stable branch policy <http://docs.openstack.org/project-team-guide/stable-branches.html>`__, which specifies the various phases of support for stable branches, which are typically supported for 12 to 18 months.  The case where a bug can't be fixed upstream first must be handled with extreme caution, since fixes would be released directly to the corresponding Ubuntu release without having landed upstream first.

.. warning::
    [2] Landing a fix in a corresponding Ubuntu release may not always be possible, for example once the Ubuntu release has reached EOL and the UCA is still supported.  This case must be handled with extreme caution, since fixes would be released directly to the corresponding UCA without having first landed in the corresponding Ubuntu release, and possibly also without having first landed in the upstream OpenStack release.


OpenStack QA Process
--------------------

Once stable package updates have been accepted by the ubuntu-sru (or
Cloud Archive) team into -proposed pockets, the following SRU
verification process is followed:


-  Deployment and base configuration using `OpenStack Charm
   Testing <https://github.com/openstack-charmers/openstack-charm-testing>`__
   bundles and charms, using the current set of stable charms
   configured to consume packages from the proposed pocket of the
   archive.

-  Testing of the deployed Cloud using the
   `Tempest <https://github.com/openstack/tempest>`__ (the OpenStack
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

.. _openstack_sru_template:

OpenStack SRU Template
----------------------

::

   == Begin SRU Template ==
   [Impact]
   This release sports mostly bug-fixes and we would like to make sure all of our users have access to these improvements.

   The update contains the following package updates:

   *** <TODO: Create list with package names and versions>

   [Test Case]
   The following SRU process was followed:
   https://documentation.ubuntu.com/sru/en/latest/reference/exception-OpenStack-Updates

   In order to avoid regression of existing consumers, the OpenStack team will run their continuous integration test against the packages that are in -proposed.  A successful run of all available tests will be required before the
   proposed packages can be let into -updates.

   The OpenStack team will be in charge of attaching the output summary of the executed tests. The OpenStack team members will not mark ‘verification-done’ until this has happened.

   [Regression Potential]
   In order to mitigate the regression potential, the results of the aforementioned tests are attached to this bug.

   [Discussion]
   <TODO: other background>

   == End SRU Template ==

.. _nominating_a_bug_for_a_series:

Nominating a Bug for a Series
-----------------------------

A sponsor can be asked to nominate a bug for a particular series. You
can find the following sponsors in #ubuntu-server on freenode:

-  To target an Ubuntu series: coreycb, jamespage, icey
-  To target an Ubuntu Cloud Archive series: coreycb, jamespage, icey,
   dosaboy, wolsen

Getting permission to target a bug for a series:

-  To gain permission to target a bug for an Ubuntu series you must be a
   member of: https://launchpad.net/~ubuntu-bugcontrol
-  To gain permission to target a bug for an Ubuntu Cloud Archive series
   you must be a member of:
   https://launchpad.net/~ubuntu-cloud-archive-bugs

.. _nominating_a_new_package_for_an_sru_exception:

Nominating a new package for an SRU Exception
---------------------------------------------

To propose adding a new package to this exception, you should send an
email to ubuntu-release@lists.ubuntu.com that requests inclusion for the
named package, as well as a justification of why it can be included. For
example:

::

   == Begin Exception Template ==
   Subject: Request New OpenStack SRU Exception for Heat

   Hello SRU Team,

   I'd like to request that Heat be included in the OpenStack SRU Exception list at https://documentation.ubuntu.com/sru/en/latest/reference/exception-OpenStack-Updates

   Heat is the orchestration project in OpenStack.

   Heat is already included in our regression testing and is validated via Tempest smoke tests.

   Thanks,
   Me

   == End Exception Template ==

.. _getting_package_source:

Getting Package Source
----------------------

Depending on the package and the release, there are different ways to
download the package source:

-  Core OpenStack packages are `maintained in git on
   Launchpad <https://code.launchpad.net/~ubuntu-openstack-dev/+git>`__.
   See `OpenStack Core
   Packages <https://wiki.ubuntu.com/OpenStack/CorePackages>`__ for
   information on how to work with these repositories.

-  Packages can be retrieved from Launchpad with the \`pull-lp-source\`
   tool:

   -  ``pull-lp-source [release|version]`` (e.g. ``pull-lp-source python-oslo.messaging bionic``)

-  Packages can be retrieved from the UCA with the pull-uca-source tool:

   -  ``pull-uca-source [release|version]`` (e.g. ``pull-uca-source python-oslo.messaging queens``)

Related SRU Interest Team
-------------------------

OpenStack has a :ref:`SRU Interest Team <reference-sru-interest-team>`.
Please subscribe the
`Interest group <https://launchpad.net/~sru-verification-interest-group-openstack>`__
to the SRU bug early on.

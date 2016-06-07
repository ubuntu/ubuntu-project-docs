#. 

   #. page was renamed from ServerTeam/OpenStackStableReleaseUpdates

.. _stable_release_updates_for_openstack_and_the_ubuntu_cloud_archive:

Stable Release Updates for OpenStack and the Ubuntu Cloud Archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SRU process for !OpenStack and the Ubuntu Cloud Archive follows the
same process as `Ubuntu Stable Release
Updates <https://wiki.ubuntu.com/StableReleaseUpdates>`__. Most of the
points that are highlighted here are covered in further detail in the
previous link, and are condensed and reiterated here with some additions
that are specific to the Ubuntu Cloud Archive.

.. _sru_expectations:

SRU Expectations
~~~~~~~~~~~~~~~~

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

   -  SRUs must have an accompanying bug with well-documented sections
      for [Impact], [Test Case], and [Regression Potential]. These
      sections must contain details as described in the `Ubuntu Stable
      Release Updates
      procedure <https://wiki.ubuntu.com/StableReleaseUpdates#Procedure>`__.
   -  Bugs must be fixed in the following order, when possible:

| ``   1. Upstream in the latest !OpenStack release [1]``
| ``   1. Then in the corresponding Ubuntu release [2]``
| ``   1. Then in the corresponding UCA release``
| ``   1. Then the bug can be fixed in the same order for the prior !OpenStack release (upstream stable first, corresponding Ubuntu release second, and corresponding UCA release third).``
| ``[1] Landing a fix upstream may not always be possible, for example once the upstream branch is in critical-fix or security-fix only mode, or once it has reached EOL.  See the ``\ ```OpenStack upstream stable branch policy`` <http://docs.openstack.org/project-team-guide/stable-branches.html>`__\ ``, which specifies the various phases of support for stable branches, which are typically supported for 12 to 18 months.  The case where a bug can't be fixed upstream first must be handled with extreme caution, since fixes would be released directly to the corresponding Ubuntu release without having landed upstream first.``
| ``[2] Landing a fix in a corresponding Ubuntu release may not always be possible, for example once the Ubuntu release has reached EOL and the UCA is still supported.  This case must be handled with extreme caution, since fixes would be released directly to the corresponding UCA without having first landed in the corresponding Ubuntu release, and possibly also without having first landed in the upstream !OpenStack release.``

.. _nominating_a_bug_for_a_series:

Nominating a Bug for a Series
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~

Depending on the package and the release, there are different ways to
download the package source:

-  

   -  Core !OpenStack packages for Liberty+ are `maintained in git on
      Launchpad <https://code.launchpad.net/~ubuntu-server-dev/+git>`__.
      The process for working with these repositories is documented
      `here <https://wiki.ubuntu.com/ServerTeam/OpenStackPackaging>`__.

-  

   -  Core !OpenStack packages prior to Liberty can be found `maintained
      in Bazaar on
      Launchpad <https://code.launchpad.net/~ubuntu-server-dev>`__. The
      process for working with these branches is documented
      `here <https://wiki.ubuntu.com/ServerTeam/OpenStack>`__.

-  

   -  UCA packages that correspond to a supported Ubuntu release can be
      retrieved with the pull-lp-source tool:

``   * pull-lp-source ``\ \ `` [release|version] (e.g. pull-lp-source python-oslo.messaging xenial)``

-  

   -  UCA packages that correspond to an unsupported (EOL) Ubuntu
      release can be retrieved from the corresponding UCA staging PPA:

``   * For example, see the ``\ ```Mitaka staging PPA`` <https://launchpad.net/~ubuntu-cloud-archive/+archive/ubuntu/mitaka-staging/+packages>`__\ ``.``

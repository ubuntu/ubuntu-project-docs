#. 

   #. page was copied from LandscapeUpdates

This document describes the policy for updating sosreport package in a
stable supported distro, including LTS. It is also the aim of this
document to provide an example for any upstream project that wants to
push updates to an Ubuntu stable release.

Sosreport is an extensible, portable, support data collection tool
primarily aimed at Linux distributions and other UNIX-like operating
systems. This tool **is mission critical for Canonical to support UA
(Ubuntu Advantage) customer, partners and community**. Sosreport is also
widely used by other third party vendors.

-  Upstream reference:

   -  https://sos.readthedocs.io/en/latest/
   -  http://github.com/sosreport/sos

Therefore, in addition to bug fixes, new features are allowed in an
update **as long as the conditions outlined below are met**.

Process
-------

This is the mandatory process that the proposed packages have to pass.
The following requirements must be met:

-  Sosreport needs to be tested

   -  By a reasonable amount of Canonical Support team members with
      positive and detailed feedbacks (documented in an LP bug)
   -  On physical hardware, container and virtual machine.
   -  Under various UA customer similar environment and context (for LTS
      version only, no UA customer has such setup using non-LTS):

      -  Cloud, Ceph, Landscape, MAAS, JuJu managed environment, ....

   -  On as much architecture as available to the testers.
   -  For commonly used parameters : -a, --all-logs, --upload, --batch,
      ...

.. _sos_report___collect_and_package_diagnostic_and_support_data:

sos report - Collect and package diagnostic and support data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

sos report is now used to generate sosreport tarballs

-  

   -  Make sure sosreport generates an archive under **/tmp**\ [0] in
      the form of **sosreport--2020-06-19-ogwtrgb.tar.xz** with its
      accompanied sha256 checksum
      **sosreport--2020-06-19-ogwtrgb.tar.xz.sha256** (Note that the
      naming pattern may vary depending on the options and versions
      used.)

-  

   -  Extract the archive

      -  Validate its content and make sure it is sane and accurate.
      -  Validate that sosreport obfuscates sensible information for
         plugins instructed to do so such as:

| ``   * landscape plugin, should obfuscate password(s) and secret-token from config file.``
| ``   * or any plugins (sos/plugins/) exercising the ``\ **``do_file_sub()``**\ `` method.``

-  

   -  Inspect for 0 size file(s) within the archive and use common sense
      if legit or not (e.g. "command is not found" can be avoided for
      instance)

``   * find /path_to_sosreport_archive/ -type f -size 0``

-  

   -  Look under "sos_reports" for full report.
   -  Look under "sos_logs" for WARN and/or ERROR

| ``   * grep -v "INFO:" sos_logs/sos.log``
| ``   * Look under "sos_logs" for error files (e.g. sos_logs/systemd-plugin-errors.txt).``

-  Run "simple.sh": An upstream port of the Travis tests to bash.
   Generating various type of sosreport collections (which is part of
   the autopkgtest (d/test/simple.sh)) now.

   -  https://github.com/sosreport/sos/blob/master/tests/simple.sh

[0] Debian/Ubuntu systemd implementation doesn't have a tmpfiles-clean
directive to clean /var/tmp (/var/tmp being the default location for sos
upstream.

Debian systemd (tmpfiles.d/tmp.conf):

::

    # Clear tmp directories separately, to make them easier to override
    D /tmp 1777 root root -
    #q /var/tmp 1777 root root 30d

For that reasons, Debian/Ubuntu intentionally differ to /tmp in order to
have tmpfiles-clean directive under /tmp and prevent to full /var/tmp.
This could be re-evaluated if Debian changes the directive in the future
`debbugs#966621 <https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=966621>`__

.. _sos_clean___obfuscate_sensitive_data_from_one_or_more_sosreports:

sos clean - Obfuscate sensitive data from one or more sosreports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

sos clean, also available as sos mask, is a newly added sub-command in
this release and is an implementation of the standalone soscleaner
project.

$ sos clean

It can obfuscate: keywords, username, hostname, domain, ip & mac
addresses.

-  Make sure it generates a default_mapping file inside
   /etc/sos/cleaner/ (at first run)

-  Make sure it produces the following files:

   -  Tarball with sensitive information obfuscated (e.g. Ready to share
      with 3rd party vendor):

      -  sosreport-host0-2020-08-26-eywxccq-obfuscated.tar.xz

   -  Tarball accompanied sha256 checksum:

      -  sosreport-host0-2020-08-26-eywxccq-obfuscated.tar.xz.sha256

   -  Private mapping file (Not to share, keep it private):

      -  sosreport-host0-2020-08-26-eywxccq-private_map

   -  sos clean execution logs (Not to share, keep it private):

      -  sosreport--2020-08-26-eywxccq-obfuscation.log

.. _sos_collect___collect_sosreports_from_multiple_cluster_nodes:

sos collect - Collect sosreports from multiple (cluster) nodes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

sos collect is a new sub command in this release, and is an integration
of the standalone sos-collector project, with the aim being to collect
sosreports from multiple systems simultaneously.

.. _previous_sosreport_updates_bugs:

Previous sosreport updates bugs
-------------------------------

-  v4.1 `(LP: #1917894) <https://bugs.launchpad.net/bugs/1917894>`__
-  v4.0 `(LP: #1892275) <https://bugs.launchpad.net/bugs/1892275>`__
-  v3.9.1 `(LP: #1884293) <https://bugs.launchpad.net/bugs/1884293>`__
-  v3.9 `(LP: #1862830) <https://bugs.launchpad.net/bugs/1862830>`__
-  v3.6 `(LP: #1775195) <https://bugs.launchpad.net/bugs/1775195>`__

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be requested as usual
(`StableReleaseUpdates <StableReleaseUpdates>`__) with the additional
note about having the above steps being completed.

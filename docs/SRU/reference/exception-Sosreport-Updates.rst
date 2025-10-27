.. _reference-exception-SosreportUpdates:

Sos / SosReport Updates
=======================

This document describes the policy for updating sosreport & sos package
in a stable supported distro, including LTS. It is also the aim of this
document to provide an example for any upstream project that wants to
push updates to an Ubuntu stable release.

sos is an extensible, portable, support data collection tool primarily
aimed at Linux distributions and other UNIX-like operating systems. This
tool **is mission critical for Canonical to support UPro (Ubuntu Pro)
customer, partners and community**. sos is also widely used by other
third party vendors.

-  Upstream reference:

   -  https://sos.readthedocs.io/en/main/
   -  http://github.com/sosreport/sos

Therefore, in addition to bug fixes, new features are allowed in an
update **as long as the conditions outlined below are met**.

Process
-------

This is the mandatory process that the proposed packages have to pass.
The following requirements must be met:

-  sos needs to be tested

   -  By a reasonable amount of Canonical Support team members with
      positive and detailed feedback (documented in an LP bug)
   -  Should be tested with Canonical internal tooling such as:

      - `hostos <https://github.com/canonical/hotsos>`__

   -  On physical hardware, container and virtual machine.
   -  Under various UPro customer similar environment and context (for
      LTS version only, no UPro customer has such setup using non-LTS):

      -  Cloud, Ceph, Landscape, MAAS, sunbeam, juju managed
         environment, ....

   -  On as much architecture as available to the testers.
   -  For commonly used parameters : ``-a``, ``--all-logs``, ``--upload``,
      ``--batch``, ...

.. _sos_report___collect_and_package_diagnostic_and_support_data:

sos report - Collect and package diagnostic and support data
------------------------------------------------------------

sos report is now used to generate sos report tarballs

-  Make sure sos report generates an archive under ``/tmp`` in the
   form of ``sosreport--2020-06-19-ogwtrgb.tar.xz`` with its
   accompanied sha256 checksum
   ``sosreport--2020-06-19-ogwtrgb.tar.xz.sha256`` (Note that the
   naming pattern may vary depending on the options and versions
   used.)

-  Extract the archive

   -  Validate its content and make sure it is sane and accurate.

   -  Validate that sos report obfuscates sensible information for
      plugins instructed to do so such as:

      -  landscape plugin, should obfuscate password(s) and secret-token from config file.

      -  or any plugins (``sos/plugins/``) exercising the ``do_file_sub()`` method.

   -  Inspect for 0 size file(s) within the archive and use common sense
      if legit or not (e.g. "command is not found" can be avoided for
      instance)::

      $ find /path_to_sosreport_archive/ -type f -size 0

   -  Look under ``sos_reports`` for full report.

   -  Look under ``sos_logs`` for WARN and/or ERROR::

      $ grep -v "INFO:" sos_logs/sos.log

      - Look under ``sos_logs`` for error files (e.g. ``sos_logs/systemd-plugin-errors.txt``).

.. _sos_clean___obfuscate_sensitive_data_from_one_or_more_sosreports:

sos clean - Obfuscate sensitive data from one or more sosreports
----------------------------------------------------------------

sos clean, also available as sos mask, is a newly added sub-command in
this release and is an implementation of the standalone soscleaner
project.::

  $ sos clean <path_to_sosreport>

It can obfuscate: keywords, username, hostname, domain, ip & mac
addresses.

-  Make sure it generates a default_mapping file inside
   ``/etc/sos/cleaner/`` (at first run)

-  Make sure it produces the following files:

   -  Tarball with sensitive information obfuscated (e.g. Ready to share
      with 3rd party vendor):

      -  ``sosreport-host0-2020-08-26-eywxccq-obfuscated.tar.xz``

   -  Tarball accompanied sha256 checksum:

      -  ``sosreport-host0-2020-08-26-eywxccq-obfuscated.tar.xz.sha256``

   -  Private mapping file (Not to share, keep it private):

      -  ``sosreport-host0-2020-08-26-eywxccq-private_map``

   -  sos clean execution logs (Not to share, keep it private):

      -  ``sosreport--2020-08-26-eywxccq-obfuscation.log``

.. _sos_collect___collect_sosreports_from_multiple_cluster_nodes:

sos collect - Collect sosreports from multiple (cluster) nodes
--------------------------------------------------------------

sos collect is a new sub command in this release, and is an integration
of the standalone sos-collector project, with the aim being to collect
sosreports from multiple systems simultaneously.

.. _sos_upload__upload_sosreports_or_files_to_vendor:

sos upload - Upload sosreports or files to Vendor
-------------------------------------------------

sos upload is a new sub command in 4.9.0. This allows to upload a sos or a file
to Canonical, this can be achieved by running the following command.::

  $ sos upload <filename>

The filename should have the case id, so that the automation can take place. We
should check the command with multiple files

* A sosreport that was originally created.
* a file that is not a sos, but a file that is needed for support purposes.

The utility will detect automatically that you're running on Ubuntu, and hence
will upload to Canonical file server.

.. _previous_sosreport_updates_bugs:

Previous sosreport updates bugs
-------------------------------

-  v4.9.2 `(LP: #2114840) <https://bugs.launchpad.net/bugs/2114840>`__
-  v4.8.2 `(LP: #2091858) <https://bugs.launchpad.net/bugs/2091858>`__
-  v4.7.2 `(LP: #2054395) <https://bugs.launchpad.net/bugs/2054395>`__
-  v4.5.6 `(LP: #2028327) <https://bugs.launchpad.net/bugs/2028327>`__
-  v4.4 `(LP: #1986611) <https://bugs.launchpad.net/bugs/1986611>`__
-  v4.3 `(LP: #1960996) <https://bugs.launchpad.net/bugs/1960996>`__
-  v4.2 `(LP: #1941745) <https://bugs.launchpad.net/bugs/1941745>`__
-  v4.1 `(LP: #1917894) <https://bugs.launchpad.net/bugs/1917894>`__
-  v4.0 `(LP: #1892275) <https://bugs.launchpad.net/bugs/1892275>`__
-  v3.9.1 `(LP: #1884293) <https://bugs.launchpad.net/bugs/1884293>`__
-  v3.9 `(LP: #1862830) <https://bugs.launchpad.net/bugs/1862830>`__
-  v3.6 `(LP: #1775195) <https://bugs.launchpad.net/bugs/1775195>`__


Sosreport Requesting the SRU
----------------------------

The SRU should be requested as usual
(:ref:`StableReleaseUpdates <howto-perform-standard-sru>`) with the additional
note about having the above steps being completed.

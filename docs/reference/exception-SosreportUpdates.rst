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
   -  Under various UA customer similar environment and context: Cloud,
      Landscape, MAAS, juju, ....
   -  On as much architecture as available to the testers.
   -  For commonly used parameters : -a, --all-logs, --upload, --batch,
      ...

-  For each test above

   -  Make sure sosreport generates an archive under **/tmp** in the
      form of **sosreport--2020-06-19-ogwtrgb.tar.xz** with its
      accompanied md5 checksum
      **sosreport--2020-06-19-ogwtrgb.tar.xz.md5** (The naming pattern
      may vary depending on the options and versions used)
   -  Extract the archive

      -  Validate its content and make sure it is sane and accurate.
      -  Validate that sosreport obfuscates sensible information for
         plugins instructed to do so

``    (e.g. landscape plugin: should obfuscate password(s) and secret-token from config file and any plugins using do_file_sub() function)``

-  

   -  Check for 0 size file(s) (and use common sense if legit or not)
   -  Look under "sos_reports" for full report.
   -  Look under "sos_logs" for WARN and/or ERROR

| ``   * $ grep -v "INFO:" sos_logs/sos.log``
| ``   * Look under "sos_logs" for error files (e.g. sos_logs/systemd-plugin-errors.txt).``

-  Run "simple.sh": An upstream port of the Travis tests to bash.
   Generating various type of sosreport collections (which is part of
   the autopkgtest (d/test/simple.sh)) now.

   -  https://github.com/sosreport/sos/blob/master/tests/simple.sh

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be requested as usual
(`StableReleaseUpdates <StableReleaseUpdates>`__) with the additional
note about having the above steps being completed.

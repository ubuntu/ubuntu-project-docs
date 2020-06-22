#. 

   #. page was copied from LandscapeUpdates

This document describes the policy for updating sosreport package in a
stable supported distro, including LTS. It is also the aim of this
document to provide an example for any upstream project that wants to
push updates to an Ubuntu stable release.

Sos is an extensible, portable, support data collection tool primarily
aimed at Linux distributions and other UNIX-like operating systems. This
tool is mission critical for Canonical to support UA (Ubuntu Advantage)
customer, partners and community. Sosreport is also widely used by other
third party vendors.

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

   -  Make sure sosreport generated an archive under /tmp.
   -  Extract the archive

      -  Validate its content and make sure it is sane
      -  Validate that sosreport obfuscates for plugins instructed doing
         so (e.g. landscape plugin: substitution of password(s) and
         secret-token from config file)
      -  Check for 0 size file(s) (and use common sense if legit or not)

   -  Look under "sos_reports" for full report.
   -  Look under "sos_logs" for WARN and/or ERROR

      -  $ grep -v "INFO:" sos_logs/sos.log
      -  Look under "sos_logs" for error files
         (sos_logs/systemd-plugin-errors.txt).

-  Run "simple.sh": An upstream port of the travis tests to bash.
   Generating various type of sosreport collections (which is part of
   the autopkgtest (d/test/simple.sh)) now.

   -  https://github.com/sosreport/sos/blob/master/tests/simple.sh

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be requested as usual
(`StableReleaseUpdates <StableReleaseUpdates>`__) with the additional
note about having the above steps being completed.

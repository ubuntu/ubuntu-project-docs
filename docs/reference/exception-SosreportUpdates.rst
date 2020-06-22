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

https://sos.readthedocs.io/en/latest/

http://github.com/sosreport/sos

Therefore, in addition to bug fixes, new features are allowed in an
update **as long as the conditions outlined below are met**.

Process
-------

This is the mandatory process that the proposed packages have to pass.
The following requirements must be met:

-  Sosreport needs to be tested by a reasonnable amount of Canonical
   Support team members with positive and detailed feedbacks.
-  Sosreport needs to be tested on physical hardware, container and
   Virtual Machine.
-  Sosreport needs to be tested under various UA customer similar
   environment and context: Cloud, Landscape, MAAS, JuJu, ....
-  Sosreport needs to be tested on as much architecture as available to
   the testers.
-  Sosreport needs to be test for commonly used parameters : -a,
   --all-logs, --upload, ...

-  For each test above

   -  Make sure sosreport generated an archive under /tmp.
   -  Extract the archive

      -  Check at its content and make sure it is sane.
      -  Check for 0 size file(s) (and use common sense if legit or not)

   -  Look under "sos_reports" for full report.
   -  Look under "sos_logs" for WARN and/or ERROR

      -  $ grep -v "INFO:" sos_logs/sos.log
      -  Look under "sos_logs" for error files
         (sos_logs/systemd-plugin-errors.txt).

-  Run "simple.sh": An upstream port of the travis tests to bash.
   Generating various type of sosreport collections (which is part of
   the autopkgtest (d/test/simple.sh) now.

   -  https://github.com/sosreport/sos/blob/master/tests/simple.sh

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be requested as usual
(`StableReleaseUpdates <StableReleaseUpdates>`__) with the additional
note about having the above steps being completed.

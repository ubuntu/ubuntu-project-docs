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

-  Sosreport need to be tested by various team members of Canonical
   Support team with positive feedbacks.
-  Sosreport need to be tested on physical hardware, container and
   Virtual Machine
-  Sosreport need to be tested in different context: cloud, MAAS, JuJu
   managed,
-  "simple.sh" (A port of the travis tests to bash) need to report no
   failures.

   -  https://github.com/sosreport/sos/blob/master/tests/simple.sh

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be requested as usual
(`StableReleaseUpdates <StableReleaseUpdates>`__) with the additional
note about having the above steps being completed.

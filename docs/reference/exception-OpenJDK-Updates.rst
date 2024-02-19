This document describes the policy for updating the openjdk-N packages,
and to introduce new openjdk-N packages in Ubuntu LTS versions. OpenJDK
upstream has long supported LTS releases (11, 17, 21), which are
normally maintained in the distro. OpenJDK versions in between OpenJDK
LTS version are only supported for around six months. Having such a
version in an Ubuntu non-LTS release make sense, because the support
time frame is around the same for both.

We want to ship the short term support OpenJDK version to get those
exposed to users and developers, but want to drop them again when they
become unsupported. Therefore we are not shipping any short term OpenJDK
version in an Ubuntu LTS release, and only providing the package in the
updates pocket.

.. _qa_process:

QA Process
----------

A new OpenJDK short term support version has to be uploaded to the
current development series first, then to the most recent Ubuntu LTS
release. At most two OpenJDK short term support versions can be found in
an Ubuntu LTS release.

These versions are not used by default, minimizing the risk to affect
other packages in the archive. The test results run during the build
should look reasonably well. The autopkg tests are also run for these
uploads, however they not meaningful at all, because they are run
against the default Java version of the Ubuntu LTS release.

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be done with a single process bug for this stable release
exception, instead of individual bug reports for individual bug fixes.
However, individual bugs may be referenced in the from the changelog but
each of those bugs will need to independently verified and commented on
for the SRU to be considered complete.

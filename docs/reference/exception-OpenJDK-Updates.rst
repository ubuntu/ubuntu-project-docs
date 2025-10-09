.. _reference-exception-OpenJDK-Updates:

OpenJDK Updates
===============

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


OpenJDK QA Process
------------------

A new OpenJDK short term support version has to be uploaded to the
current development series first, then to the most recent Ubuntu LTS
release. At most two OpenJDK short term support versions can be found in
an Ubuntu LTS release.

These versions are not used by default, minimizing the risk to affect
other packages in the archive. The test results run during the build
should look reasonably well. The autopkg tests are also run for these
uploads, however they not meaningful at all, because they are run
against the default Java version of the Ubuntu LTS release.


OpenJDK Requesting the SRU
--------------------------

The SRU should be done with a single process bug for this stable release
exception, instead of individual bug reports for individual bug fixes.
However, individual bugs may be referenced in the from the changelog but
each of those bugs will need to independently verified and commented on
for the SRU to be considered complete.

The LTS OpenJDK release is built in ppa:openjdk-private/bootstrap[1].
This PPA contains all OpenJDK release builds for the supported stable
releases. LTS OpenJDK release is published during the Ubuntu Freeze (Mid
September).

Toolchain team:

-  Requests FFe for OpenJDK LTS release (FFe bug) in advance and uploads
   to the development release once release is available. Note: Make all
   necessary fixes for stable releases in the development release.
-  Prepares builds for the stable releases in
   `ppa:openjdk-private/bootstrap` and updates FFe bug according to the
   SRU template. The testing section must contain results of JTREG build
   time and autopkgtests.
   Note: Ensure that build dependencies specify the latest openjdk
   release first if the intermediate release, such as openjdk-24 is
   present in the archive:
   `openjdk-25-jdk-headless:native | openjdk-24-jdk-headless:native,`
-  Performs a no-change rebuild to validate bootstraping works in a
   public ppa in `openjdk-r` team, e.g. `ppa:openjdk-r/openjdk-25`.
-  Binary-copies the update packages to unapproved queue for the target
   releases:

   .. code-block::

        suite=noble \
        copy-package -b -s ${suite} --to-suite ${suite}-proposed \
          --from ppa:openjdk-r/ubuntu/openjdk-25 --to ubuntu openjdk-25
-  Messages @ubuntu-sru on #sru:ubuntu.com that OpenJDK updates are
   ready


[1]
https://launchpad.net/~openjdk-private/+archive/ubuntu/bootstrap/+packages

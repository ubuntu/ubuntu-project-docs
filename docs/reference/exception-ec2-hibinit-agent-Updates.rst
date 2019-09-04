This document describes the policy for updating the ec2-hibinit-agent
package to new upstream versions in a stable, supported distro
(including LTS releases). This is an exception to the standard SRU
process.

ec2-hibinit-agent is provided by Amazon for installation within guests
that run on Amazon Web Services Elastic Compute Cloud (EC2). The package
consists of scripts to act on an ACPI hibernation event specific to the
EC2 environment to enable VM hibernation to disk.

Cloud platforms evolve at a rate that can't be handled in six-month
increments, and they will often develop features that they would like to
be available to customers who don't want to upgrade from earlier Ubuntu
releases. As such, updating ec2-hibinit-agent releases is required
within all Ubuntu releases, so they continue to function properly in
their environment.

New versions of ec2-hibinit-agent can be SRU'd in to older releases
provided the following process is followed.

.. _qa_process:

QA Process
----------

When a new version of ec2-hibinit-agent is uploaded to -proposed, the
following will be done:

-  an image based on -proposed will be built for EC2 and published as a
   test image
-  the CPC team will write new automated tests to cover new testable
   functionality (if any) in the new package
-  the automated testing that the CPC team normally runs against EC2
   images before they are published will be run against the -proposed
   image, testing of the image must include:

   -  VM stop/terminate testing via API or EC2 console to avoid
      regression of `LP:
      #1840909 <https://bugs.launchpad.net/ubuntu/+source/ec2-hibinit-agent/+bug/1840909>`__;
      the instance must be responsive to the ACPI powerbutton event and
      shut down as a result, and
   -  instance types that include both the XEN and KVM hypervisors for
      all tests to cover the different underlying platform
      implementations.

If all the testing indicates that the image containing the new package
is acceptable, verification will be considered to be done and the the
package can be released from -proposed.

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be done with a single process bug for this stable release
exception, instead of individual bug reports for individual bug fixes.
However, individual bugs may be referenced in the from the changelog but
each of those bugs will need to independently verified and commented on
for the SRU to be considered complete.

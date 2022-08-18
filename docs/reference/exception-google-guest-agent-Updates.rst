This document describes the policy for updating the
google-compute-engine-oslogin package to new upstream versions in a
stable, supported distro (including LTS releases). This is an exception
to the standard SRU process.

google-compute-engine-oslogin is provided by Google for installation
within guests that run on Google Compute Engine. It is a collection of
tools and daemons, packaged as google-compute-engine-oslogin, that
ensure that the Ubuntu images published to GCE run properly on their
platform.

Cloud platforms evolve at a rate that can't be handled in six-month
increments, and they will often develop features that they would like to
be available to customers who don't want to upgrade from earlier Ubuntu
releases. As such, updating google-compute-engine-oslogin to more recent
upstream releases is required within all Ubuntu releases, so they
continue to function properly in their environment.

New versions of google-compute-engine-oslogin can be SRU'd in to older
releases provided the following process is followed.

.. _qa_process:

QA Process
----------

When a new version of google-compute-engine-oslogin is uploaded to
-proposed, the following will be done:

-  an image based on -proposed will be built for GCE and published to
   the ubuntu-os-cloud-devel project
-  the CPC team will write new automated tests to cover new testable
   functionality (if any) in the new package
-  the automated testing that the CPC team normally runs against GCE
   images before they are published will be run against the -proposed
   image
-  the GCE team will be asked to validate

   -  that the new package addresses the issues it is expected to
      address, and
   -  that the image passes their internal image validation.

If all the testing indicates that the image containing the new package
is acceptable, verification will be considered to be done and the the
package can be released from -proposed without waiting for its age reach
the default SRU aging requirement.

The rationale behind
`lifting <https://lists.ubuntu.com/archives/ubuntu-release/2018-August/004553.html>`__
the aging requirement is that no one is expected to test the package
apart from the uploader, the GCE team and the CPC team, and they all
test the package in the verification process. Verification also includes
preparing custom-built images for testing first-booting instances which
can't be easily done by others.

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be done with a single process bug for this stable release
exception, instead of individual bug reports for individual bug fixes.
However, individual bugs may be referenced in the from the changelog but
each of those bugs will need to independently verified and commented on
for the SRU to be considered complete.

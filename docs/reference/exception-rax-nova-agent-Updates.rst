.. _this_document_is_a_proposal_and_is_not_yet_accepted_as_an_sru_exception:

This document is a proposal and is not yet accepted as an SRU exception!
------------------------------------------------------------------------

This document describes the policy for updating the rax-nova-agent
package to new upstream versions in a stable, supported distro
(including LTS releases). This is an exception to the standard SRU
process.

Nova-agent is provided by Rackspace for installation on servers that run
in Rackspace Cloud. It is a collection of tools and daemons, packaged as
rax-nova-agent, that ensure that the Ubuntu images published to
Rackspace Cloud run properly on their platform.

Cloud platforms evolve at a rate that can't be handled in six-month
increments, and they will often develop features that they would like to
be available to customers who don't want to upgrade from earlier Ubuntu
releases. As such, updating rax-nova-agent to more recent upstream
releases is required within all Ubuntu releases, so they continue to
function properly in their environment.

New versions of rax-nova-agent can be SRU'd in to older releases
provided the following process is followed.

.. _qa_process:

QA Process
----------

When a new version of rax-nova-agent is uploaded to -proposed, the
following will be done:

-  an image including the package from -proposed will be built for
   Rackspace to be tested in Rackspace Cloud
-  the CPC team will write new automated tests to cover new testable
   functionality (if any) in the new package
-  the automated testing that the CPC team normally runs against
   Rackspace Cloud images before they are published will be run against
   the -proposed image
-  Rackspace's team will be asked to validate

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
apart from the uploader, Rackspace's team and the CPC team, and they all
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

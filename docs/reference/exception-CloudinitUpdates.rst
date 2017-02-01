**DRAFT DRAFT DRAFT**

This document describes the policy for updating Cloud-init in a stable
supported distro, including LTS.

Cloud-init is...

.. _qa_process:

QA Process
----------

.. _merge_qa:

Merge QA
~~~~~~~~

This is the mandatory QA process that the proposed packages have to
pass. The following requirements must be met:

-  

   -  Every change needs to be covered by a Launchpad bug to track all
      changes
   -  Every bug must have:

| ``     * A bzr branch attached with the fix + changes covered by unit tests``
| ``     * Link to successful run of integration tests based on the bzr branch``
| ``     * Reviewed and approved by a member of the development team``
| ``     * Branch set to the committed state``

-  

   -  All unit tests and style tests ran and passed successfully
   -  Code coverage of changes or code coverage % either no change or
      increased(?)

.. _packaging_qa:

Packaging QA
~~~~~~~~~~~~

TBD

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be requested per the StableReleaseUpdates documented
process.

The SRU should be done with a single process bug for this stable release
exception, instead of individual bug reports for individual bug fixes.
Individual bugs may be referenced in the change log, but in that case
each of those bugs will need to be independently verified and commented
on for the SRU to be considered complete.

The description of the bug should contain links to automatic testing
results (e.g. Jenkins test runs) so that anyone can verify the testing
that occurred and the results. Additionally, the SRU bug should be
verbose in documenting any manual testing that occurs. See `LP#
1588052 <https://bugs.launchpad.net/ubuntu/+source/snapd/+bug/1588052>`__
as an example

.. _sru_template:

SRU Template
~~~~~~~~~~~~

TBD

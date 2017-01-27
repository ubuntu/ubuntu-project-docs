**DRAFT DRAFT DRAFT**

This document describes the policy for updating Curtin in a stable
supported distro, including LTS.

Curtin (the curt installer) is a "fast path" installer designed to
install Ubuntu quickly. It is blunt, brief, snappish, snippety and
unceremonious. Periodically Curtin needs to be updated in order to take
advantage of new features and bug fixes. Therefore, in addition to bug
fixes, new features are allowed in an update as long as the conditions
outlined below are met.

.. _qa_process:

QA Process
----------

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

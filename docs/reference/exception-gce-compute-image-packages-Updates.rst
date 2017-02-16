This document describes the policy for updating the
gce-compute-image-packages package in a stable, supported distro
(including LTS releases).

compute-image-packages is provided by Google for installation within
guests that run on Google Compute Engine. It is a collection of tools
and daemons, packaged as gce-compute-image-packages, that ensure that
the Ubuntu images published to GCE run properly on their platform.

Cloud platforms evolve at a rate that can't be handled in six-month
increments, and they will often develop features that they would like to
be available to customers who don't want to upgrade from earlier Ubuntu
releases. As such, updating gce-compute-image-packages to more recent
upstream releases is required within all Ubuntu releases, so they
continue to function properly in their environment.

New versions of gce-compute-image-packages can be SRU'd in to older
releases provided the following process is followed.

.. _qa_process:

QA Process
----------

.. _requesting_the_sru:

Requesting the SRU
------------------

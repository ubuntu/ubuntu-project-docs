.. _apt_python_apt_upstream_versioning_scheme_lts_srus:

apt, python-apt: Upstream versioning scheme LTS SRUs
====================================================

The APT developers (https://launchpad.net/~deity) maintain upstream
stable branches for LTS releases of Ubuntu. These will be uploaded to
LTS releases using **upstream version numbers** and no ubuntu downstream
version components. These branches are shared with other downstreams
like OpenEmbedded, however they are not influenced by other downstream
needs.

The APT release management ensures that there is no conflict in
versioning between Debian and Ubuntu uploads. There is only one
versioned branch with one designated target release.

.. _qa_process:

QA process
----------

In addition to normal Ubuntu QA process after the upload, each upstream
release (each push to the git branch really) undergoes a dedicated CI
pipeline that runs the test suite as both root and a normal user whereas
the autopkgtests only cover the root portion.

.. _requesting_the_sru:

Requesting the SRU
------------------

SRUs will follow the normal SRU procedure but may use upstream versions
if uploaded by the https://launchpad.net/~deity team.

Other developers are strongly recommended to deliver patches to the
upstream APT project and get an upstream APT release instead of
releasing uploads themselves to ensure validation by APT developers and
the CI. Please ping juliank if you need a patch!

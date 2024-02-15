.. _upstream_versioning_scheme_lts_srus:

Upstream versioning scheme LTS SRUs
===================================

The APT developers (https://launchpad.net/~deity) maintain upstream
stable branches for LTS releases of Ubuntu. These will be uploaded to
LTS releases using **upstream version numbers** and no ubuntu downstream
version components. These branches are shared with other downstreams
like OpenEmbedded, however they are not influenced by other downstream
needs.

The APT release management ensures that there is no conflict in
versioning between Debian and Ubuntu uploads. There is only one
versioned branch with one designated target release.

Each upstream release undergoes a dedicated CI pipeline that runs the
test suite as both root and a normal user whereas the autopkgtests only
cover the root portion.

.. _requesting_the_sru:

Requesting the SRU
------------------

Apart from upstream versioning by uploads from
https://launchpad.net/~deity team, we otherwise follow normal SRU
procedure.

This document describes the policy for updating the docker.io group of
packages (docker.io, containerd, runc) in a stable supported distro, in
particular LTS releases.

Basically docker is a sufficiently fast-moving project that we provide
more value to our users by delivering an "upstream" experience rather
than worrying over-much about backward compatibility or regressions.

The Technical Board approved such an approach in the meeting on
2016-XX-XX.

Process
-------

The aim is to backport the .1 release of a major version to the current
LTS as soon as possible after it has been released.

To do this we will, once the .0 release is out:

#. File (or find, our users are quite proactive about wanting this) a
   bug to cover the upgrade.

| ``2. Upload the .0 release to the current development series of Ubuntu but use a block-proposed tag on the update bug to prevent it migrating to release, so we can sort out any new build or packaging or autopkgtest problems.``
| ``3. Once .1 is released, this can be uploaded to the devel series (and the block-proposed tag be removed) where it should quickly migrate to release.  ``
| ``4. Once it has migrated, it  can then be uploaded with minimal necessary changes to the SRU queue of the most recent LTS.``

We will reuse the upgrade bug for the SRU but this need not include
detailed test case or regression potential sections (it should link to
this page for the sake of the SRU team member doing the review!).

QA
--

As hinted above, we will not do amazingly extensive QA. The package has
a basic autopkgtest which catches gross breakages and in practice has
caught most packaging issues so far (the only problem I am aware of it
missing is a problem in containerd on arm64 because we do not run
autopkgtests on arm64).

The other test that should be carried out as part of SRU verification is
the "docker in lxd" test as described in
https://insights.ubuntu.com/2016/04/13/stephane-graber-lxd-2-0-docker-in-lxd-712/
.

As of docker 1.12 there is an autopkgtest in the tree for this that does
not run on production infrastructure but can be run on a developers
machine by downloading the package and running

::

   $ suite=target-suite ./debian/tests/docker-in-lxd

This QA should happen both for the -proposed -> -release migration in
the devel series and again as part of the SRU verification.

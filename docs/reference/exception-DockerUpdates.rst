This document describes the policy for updating the docker.io group of
packages (docker.io-app, containerd-app, runc-app, docker-buildx,
docker-compose-v2) in a stable supported distro, in particular LTS
releases.

Basically docker is a sufficiently fast-moving project that we provide
more value to our users by delivering an "upstream" experience rather
than worrying over-much about backward compatibility or regressions.

Process
-------

The aim is to backport stable and compatible releases across all the
packages that are part of this stack
(runc-app/containerd-app/docker.io-app/docker-buildx/docker-compose-v2)
to all supported releases.

To do this we will:

#. File (or find, our users are quite proactive about wanting this) a
   bug to cover the upgrade.

| ``2. Upload the latest upstream version of the packages to the current development series of Ubuntu. Make sure all the versions are compatible among them.``
| ``3. Once they have migrated, they can then be uploaded with minimal necessary changes to the SRU queue of the supported Ubuntu releases. For docker.io-app, docker-buildx and docker-compose-v2, .0 releases will not be backported; for containerd-app and runc-app, .0 releases are eligible for backporting.``

We will reuse the upgrade bug for the SRU but this does not include
detailed test case or regression potential sections (it should link to
this page for the sake of the SRU team member doing the review!).

QA
--

As hinted above, we will not do amazingly extensive QA. The package has
a basic autopkgtest which catches gross breakages and in practice has
caught most packaging issues so far (the only problem I am aware of it
missing is a problem in containerd on arm64 because we did not run
autopkgtests on arm64 at the time).

There is also an autopkgtest that exercises "docker in lxd" as described
in
https://insights.ubuntu.com/2016/04/13/stephane-graber-lxd-2-0-docker-in-lxd-712/
. on autopkgtests.

This QA should happen both for the -proposed -> -release migration in
the devel series and again as part of the SRU verification.

.. _record_of_regressions:

Record of regressions
---------------------

According to `LP:
#1939106 <https://bugs.launchpad.net/ubuntu/+source/docker.io/+bug/1939106>`__,
upstream removed support for the aufs storage driver. This broke users
in August 2021, but this breakage was explicitly permitted by this
policy as it was written at the time. The deprecation notice was stated
in Docker Engine 18.09 see
https://docs.docker.com/engine/release-notes/18.09/#deprecation-notices
(2019-09-03).

In `LP:
#1968035 <https://bugs.launchpad.net/ubuntu/+source/docker-buildx/+bug/1968035>`__,
upstream has changed the requirements to run the new buildsystem
\`DOCKER_BUILDKIT=1 docker build .\`. In the new version, the new
buildsystem requires \`docker-buildx\` which was not included in the
SRU.

`LP:
#2098106 <https://bugs.launchpad.net/ubuntu/+source/docker.io-app/+bug/2098106>`__
Potential regression afecting Launchpad OCI builds. Still being
investigated.

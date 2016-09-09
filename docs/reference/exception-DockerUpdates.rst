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
LTS as soon as possible after it has been released. To do this we will
upload the .0 release to the -proposed pocket but use a block-proposed
tag on the update bug to prevent it migrating to release, so we can sort
out any new build or packaging or autopkgtest problems. Once .1 is
released, this should then quickly migrate to release and can then be
uploaded with minimal necessary changes to the SRU queue of the most
recent LTS. We will reuse the upgrade bug for the SRU but this need not
include detailed test case or regression potential sections (it should
link to this page for the sake of the SRU team member doing the
review!).

QA
--

As hinted above, we will not do amazingly extensive QA. The package has
a basic autopkgtest which catches gross breakages and in practice has
caught most packaging issues so far. The other test that should be
carried out as part of SRU verification is the "docker in lxd" test as
described in
https://insights.ubuntu.com/2016/04/13/stephane-graber-lxd-2-0-docker-in-lxd-712/
. (As of docker 1.12 there is an autopkgtest in the tree for this that
does not run on production infrastructure but can be run on a developers
machine). This QA should happen both for the -proposed -> -release
migration in the devel series and again as part of the SRU verification.

.. _reference-exception-PostfixUpdates:

This document describes the policy for updating the Postfix package in a
stable supported distro, in particular LTS releases.

Quoting the `Technical Board meeting minutes
(2011-10-06) <https://lists.ubuntu.com/archives/ubuntu-devel-announce/2011-October/000902.html>`__:

"Upstream has tight requirements for what goes into stable
microreleases, QAs them with regression tests, and has a good history of
not breaking anything. Known breakage so far was in the packaging. Our
QA regression testing repository has an `existing integration test
script <http://bazaar.launchpad.net/~ubuntu-bugcontrol/qa-regression-testing/master/view/head:/scripts/test-postfix.py>`__
which should be run on the proposed packages for checking for general
mis-builds, packaging errors, etc."

The mentioned `integration test
script <https://salsa.debian.org/postfix-team/postfix-dev/-/blob/debian/master/debian/tests/test-postfix.py>`__
is already included in the Postfix source package.

`Here <https://lists.ubuntu.com/archives/technical-board/2012-May/001266.html>`__
Postfix exception was added to the old
*StableReleaseUpdates/MicroReleaseExceptions* wiki page.

Process
-------

The aim is to be able to include upstream patch level microreleases in
supported stable releases, specially LTS ones. Those microreleases
include bug fixes reported by users which should improve the quality of
the package and overall user experience.

To do this we will, once the need to include an upstream microrelease in
a stable release comes up:

#. File (or find) a bug to cover the upgrade. This bug might be related
   to one of the bugs fixed in the proposed microrelease, or a bug
   dedicated to the microrelease update.

| ``2. Fix all the bugs tackled in the microrelease in the current development series of Ubuntu.``
| ``3. Once the package containing the bug fixes migrates to the release pocket of the current development series, the microrelease can be uploaded to the SRU queue.``

We will use the bug mentioned in *1* for the SRU but this need not
include detailed test case or regression potential sections (it should
link to this page for the sake of the SRU team member doing the
review!).

QA
--

As hinted above, we will not do amazingly extensive QA, upstream does
that already. And the package also has a good regression test executed
by autopkgtest which can catch breakages.

This QA should happen both for the -proposed -> -release migration in
the devel series and again as part of the SRU verification.

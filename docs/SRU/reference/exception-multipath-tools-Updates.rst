.. _reference-exception-multipath-tools-updates:

multipath-tools Updates
=======================

This document describes the policy for doing microrelease updates of the multipath-tools package in Ubuntu LTS releases, including interim releases where required by SRU policy.

.. _about_multipath-tools:

About multipath-tools
---------------------

`Linux Multipath <https://en.wikipedia.org/wiki/Linux_DM_Multipath>`__ allows to access to the same storage devices over multiple alternative connections, including active-active or active-passive operating modes (load-balancing, fallback).
It's implemented through device mapping in Linux, and can be controlled with `multipath-tools <https://github.com/opensvc/multipath-tools>`__.


Upstream release policy
-----------------------

Beginning with version 0.10, upstream releases stable updates on `stable-0.x.y` branches on `GitHub <https://github.com/opensvc/multipath-tools>`__.
These contain small bug fixes with low regression risk that are cherry-picked from the staging area from `openSUSE <https://github.com/openSUSE/multipath-tools/tree/queue>`__.
The stable branches are maintained by the `multipath-tools` maintainers on a best-effort basis.
From time to time, `minor releases <https://github.com/opensvc/multipath-tools/tags>`__ are made on these branches [#multipath-tools_readme]_.

.. [#multipath-tools_readme] https://github.com/opensvc/multipath-tools/blob/1234eed0022f904f660745de07e8bca072380926/README.md


.. _ubuntu_and_multipath-tools_releases_affected_by_this_mre:

Ubuntu [and multipath-tools] releases affected by this MRE
----------------------------------------------------------

All supported **Ubuntu LTS releases** shiping ``multipath-tools >= 0.10`` are affected by this policy.

``multipath-tools >= 0.10.0`` with version ``a.b.x`` get stable upstream updates on ``x`` from branch ``stable-a.b.x``.

Note this will include non-LTS releases of Ubuntu as needed to satisfy the :ref:`"newer releases" criteria <explanation-newer-releases>`.

Once upstream drafts a new ``a.b`` version, we expect it to have a stable branch.


QA
--

Upstream tests
^^^^^^^^^^^^^^

`multipath-tools` contains an integrated testsuite that is executed by their CI action and during our build through `make test`.

Pipelines
^^^^^^^^^

Upstream also makes use of `GitHub Actions <https://github.com/opensvc/multipath-tools/actions>`__ in order to automate the testing of new commits.
At the time of this writing, these are the `available pipelines <https://github.com/opensvc/multipath-tools/tree/master/.github/workflows>`__:

- ``multiarch test for rolling distros``
- ``multiarch test for stable distros``
- ``compile and unit test on native arch``
- ``compile and unit test on foreign arch``
- ``basic-build-and-ci``

All of them are relevant for us, since they test multiple architectures and execute the unit tests.
Another very important fact is that these pipelines also use Debian (sid and stable) as their base OS, which makes the results much more reliable for direct Ubuntu integration.

Autopkgtests
^^^^^^^^^^^^

The Debian/Ubuntu packages also carry autopkgtests, which check if a multipath devicemapping actually works.
Especially the test ``tgtbasedmpaths`` validates multipath usage over iSCSI.

multipath-tools Update Process
------------------------------

.. _multipath-tools_preparing_for_the_sru:

Preparing the SRU
^^^^^^^^^^^^^^^^^

Before filing an SRU/MRE bug and kickoff the process officially, we need to perform the following actions:

#. Commit the latest ``multipath-tools`` stable microrelease into our existing package, rebasing whatever delta the package may contain.

#. Upload the resulting package to a PPA (with all target release architectures + proposed enabled), making sure that the build succeeds **and** that there are no autopkgtest regressions introduced.

When everything looks OK, we are ready to start the SRU process:

#. File an MRE bug including the rationale for the upgrade.
   This MRE bug will contain references to previous MREs bugs, as well as a list of changes present in the new microrelease.
   The engineer driving the SRU must inspect all changes and highlight if these are important changes (should be kept), backward incompatible changes (should not be kept), or behavior changes (then it depends).
   See the SRU template below for more details on how this bug will look like.

#. Once everything is OK, upload the package to the proposed pocket (if it's a non-security upload). Then, after approval, check the proposed migration state, and do the SRU verification.

.. _multipath-tools_testing_and_verification:

Testing and verification
^^^^^^^^^^^^^^^^^^^^^^^^

As explained above, the testing/verification will be done in ``-proposed``, where the functional tests are run as autopkgtests.

We will also provide a link to upstream's GitHub workflows that were executed when the release was cut.

.. _multipath-tools_sru_template:

multipath-tools SRU template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

   [ Impact ]

   This bug tracks the following MRE updates for the multipath-tools package:

   * a.b on $ubuntu_release_name: $current_version -> a.b.x.
   * ...

   These updates only include bug fixes, following the SRU policy exception defined at https://documentation.ubuntu.com/sru/en/latest/reference/exception-multipath-tools-Updates/

   [ Major Changes ]

   TODO: List the major changes if any, with link to https://github.com/opensvc/multipath-tools/blob/<stable-branch-name>/NEWS.md

   [ Test Plan ]

   See https://documentation.ubuntu.com/sru/en/latest/reference/exception-multipath-tools-Updates/#qa

   #. Upstream GitHub workflow results: TODO link for tag/release on https://github.com/opensvc/multipath-tools/tags and its commit workflow runs.

   #. As specified in the MRE page for multipath-tools, the test plan is to build the package in "-proposed" and make sure that
      (a) all build-time tests pass and
      (b) all autopkgtest runs (incl reverse dependencies) also pass.

   * Build log confirming that the build-time testsuite has been performed and completed successfully:
     - TODO link to build log(s)

   * Test results:
     - TODO autopkgtest results and discussion

   [ Where problems could occur ]

   Upstream tests are always executed during build-time.
   Autopkgtests validate real-world functionality and test for regressions.
   Nevertheless, there is always a risk for something to break since we are dealing with a microrelease upgrade.
   Whenever a test failure is detected, we will analyze and make sure it doesn't affect existing users.

   TODO: consider any other regression potential specific to the version being updated and list if any.

   [ Other Info ]

   This is a recurring effort. For reference, here are previous multipath-tools SRU backports:

   * TODO: bug links to more recent cases of SRU backports for this package

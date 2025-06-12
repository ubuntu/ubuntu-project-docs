.. _reference-exception-PostgreSQLUpdates:

PostgreSQL Updates
==================

This document describes the policy for doing microrelease updates of the
PostgreSQL package in Ubuntu LTS releases.

.. _about_postgresql:

About PostgreSQL
----------------

`PostgreSQL <https://www.postgresql.org>`__ is a powerful, open source
object-relational database system with over 35 years of active
development that has earned it a strong reputation for reliability,
feature robustness, and performance.


PostgreSQL Upstream release policy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Upstream is very active and conscious about their releases. They have a
well established `release
policy <https://www.postgresql.org/support/versioning/>`__ and are on
top of security fixes and improvements. Their major releases receive 5
years of Long Term Support, which fits really well into Ubuntu's 5 year
standard support term for LTS releases.

.. _history_track_record:

PostgreSQL History & Track record
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Server team has been doing MREs for PostgreSQL for several years
now, but due to historical reasons there never was an official wiki page
documenting the process. However, as can be seen from the list below,
these releases have always been properly prepared, tested and uploaded
to the right pockets (sometimes to ``-security`` , sometimes to ``-updates``):

-  https://pad.lv/1637236
-  https://pad.lv/1664478
-  https://pad.lv/1690730
-  https://pad.lv/1713979
-  https://pad.lv/1730661
-  https://pad.lv/1747676
-  https://pad.lv/1752271
-  https://pad.lv/1786938
-  https://pad.lv/1815665
-  https://pad.lv/1828012
-  https://pad.lv/1833211
-  https://pad.lv/1839058
-  https://pad.lv/1863108
-  https://pad.lv/1892335
-  https://pad.lv/1915254
-  https://pad.lv/1928773
-  https://pad.lv/1939396
-  https://pad.lv/1950268
-  https://pad.lv/1961127
-  https://pad.lv/1973627
-  https://pad.lv/1978249
-  https://pad.lv/1984012
-  https://pad.lv/1996770
-  https://pad.lv/2006406
-  https://pad.lv/2019214
-  https://pad.lv/2028426
-  https://pad.lv/2040469


PostgreSQL Upstream tests
^^^^^^^^^^^^^^^^^^^^^^^^^

The PostgreSQL software contains an extensive testsuite that is executed
during build time on all supported architectures.

.. _debian_support:

Debian support
--------------

Myon, the Debian Developer who maintains the PostgreSQL package on
Debian, is also very active in building and testing the upstream
releases (even when they are not present in Debian anymore). He
`maintains several Jenkins nodes <https://pgdgbuild.dus.dg-i.net/>`__
that perform builds and tests, and that have been useful when comparing
results against the Ubuntu MRE builds.

Autopkgtests
------------

The Debian/Ubuntu packages also carry autopkgtests. They run the
build-time tests inside an autopkgtest environment.

As part of the process of preparing the MRE, we also try to run
autopkgtests from as many reverse dependencies as we are able to. This
is an important step especially when the upload will go to the ``-security``
pocket, since no autopkgtests are executed there.

PostgreSQL Update Process
-------------------------

.. _preparing_for_the_sru:

Preparing for the PostgreSQL SRU
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before filing an MRE bug and kickoff the process officially, we need to
perform the following actions:

#. Confirm that the new minor release does **not** contain any
   breaking changes that might put users' data in jeopardy (e.g.,
   requiring a ``pg_dump/pg_restore``
   cycle is dangerous and should never happen in a minor release).

#. Merge the latest PostgreSQL LTS microrelease into our existing package, rebasing whatever delta the package may contain.

   #. Update the contents of the ``debian/NEWS`` file to reflect manual operations that might need to be performed by the user after upgrading the package.

#. Upload the resulting package to a PPA, making sure that the build succeeds **and** that there are no autopkgtest regressions introduced.

When everything looks OK, we are ready to start the SRU process.


PostgreSQL Requesting the SRU
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As with regular MREs, the aim here is to offer bugfixes and security
fixes to all supported releases. The SRU will be done using a single bug
instead of individual bug reports for each fix.

We will:



#. File an MRE bug including the rationale for the upgrade. This MRE
   bug will contain references to previous MREs bugs, as well as a
   summary of the important bugfixes present in the new microrelease.
   See the SRU template below for more details on how this bug will
   look like.

#. If there are no known CVEs being addressed by the update (if there is one, the CVE ID will be explicitly mentioned in the upstream changelog),

   #. We will upload the package to the proposed pocket. Once approved, we will monitor the excuses page and address any DEP8 failures.


   #. If instead there are CVEs being addressed by the update, we will ensure there are no regressions by running autopkgtests for the updated package and its reverse dependencies. Then, contact the security team so they can take over the release to the security pocket.

.. _testing_and_verification:

Testing and verification
^^^^^^^^^^^^^^^^^^^^^^^^

As explained above, the testing will be done primarily using a PPA. When
needed (i.e., when uploading to the ``-security`` pocket), we will also run autopkgtests for all of the reverse
dependencies as well as upstream's testsuite during the package build.
Otherwise, we will upload directly to ``-updates`` pocket and monitor the excuses page.


PostgreSQL SRU template
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   [Impact]

   * MRE for latest stable fixes of Postgres XX, YY, and ZZ released on Month Year.

   [Test Case]

   * The Postgres MREs traditionally rely on the large set of autopkgtests
      to run for verification. In a PPA, those are all already pre-checked to
      be good for this upload.

   [Regression Potential]

   * Upstream tests are usually great and in addition in the Archive there
      are plenty of autopkgtests that in the past caught issues before being
      released.
      But nevertheless there always is a risk for something to break. Since
      these are general stable releases I can't pinpoint them to a most-likely area.
      - usually this works smoothly except a few test hiccups (flaky) that need to be clarified to be sure. Pre-checks will catch those to be discussed upfront (as last time)

   [Other Info]

   * This is a reoccurring MRE, see below and all the references
   * CVEs addressed by this MRE:
     - <List CVEs if needed>


   Current versions in supported releases that got updates:
    postgresql-XX | XX.AA-0ubuntu0.20.04.1 | focal-updates | source, amd64, arm64, armhf, i386, ppc64el, riscv64, s390x
    postgresql-YY | YY.B-0ubuntu0.22.04.1 | jammy-updates | source, amd64, arm64, armhf, i386, ppc64el, riscv64, s390x
    postgresql-ZZ | ZZ.C-0ubuntu0.23.04.1 | lunar-updates | source, amd64, arm64, armhf, i386, ppc64el, riscv64, s390x
    postgresql-ZZ | ZZ.C-1ubuntu1 | mantic | source, amd64, arm64, armhf, i386, ppc64el, riscv64, s390x

   Special cases:

   - <Describe special cases here.>

   Standing MRE - Consider last updates as template:
   - pad.lv/1637236
   - pad.lv/1664478
   - pad.lv/1690730
   - pad.lv/1713979
   - pad.lv/1730661
   - pad.lv/1747676
   - pad.lv/1752271
   - pad.lv/1786938
   - pad.lv/1815665
   - pad.lv/1828012
   - pad.lv/1833211
   - pad.lv/1839058
   - pad.lv/1863108
   - pad.lv/1892335
   - pad.lv/1915254
   - pad.lv/1928773
   - pad.lv/1939396
   - pad.lv/1950268
   - pad.lv/1961127
   - pad.lv/1973627
   - pad.lv/1978249
   - pad.lv/1984012
   - pad.lv/1996770
   - pad.lv/2006406
   - pad.lv/2019214
   - pad.lv/2028426

   As usual we test and prep from the PPA and then push through SRU/Security as applicable.

   Once ready, the test packages should be available at https://launchpad.net/~canonical-server/+archive/ubuntu/postgresql-sru-preparation/+packages

SRU team approval by RAOF 2024/01/31

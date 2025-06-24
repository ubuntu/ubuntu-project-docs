.. _reference-exception-DPDKUpdates:

DPDK Updates
============

This page describes the policy for updating the src:dpdk package in
regard to upstream LTS stable releases. This is an exception to the
standard SRU process under the banner of the SRU "New upstream
microreleases" exception.

.. _background_on_dpdk:

Background on DPDK
------------------

This outlines details of the project and the current state of their
verification to prove that the LTS releases can be considered for an MRE
exception.

.. _the_dpdk_project:

The DPDK Project
----------------

DPDK was included in Ubuntu main during the 16.04 release cycle; since
then upstream DPDK have started maintaining LTS releases of DPDK; At
least for our LTS releases we try to base on DPDK LTS releases The first
one was 16.11 which shipped in Zesty, and the next DPDK LTS will be
17.11 which is our target for Ubuntu 18.04 Bionic Beaver.

DPDK is a set of libraries and userspace drivers for fast packet
processing. It is designed to run on any processors. The first supported
CPU was Intel x86 and it is now extended to IBM POWER and ARM. It runs
mostly in Linux userland.

Having a MRE for DPDK will ensure that users of DPDK receive timely
critical updates to this software.

.. _upstream_change_and_release_policy:

Upstream Change and Release Policy
----------------------------------

Upstream have a
`policy <http://dpdk.org/doc/guides/contributing/stable.html>`__ for
accepting changes into the LTS release branches which includes:

-  Back-porting of any critical bug fixes (crashes, data loss, etc)
-  Minor usability items that are very low risk
-  Only changes are backported that are part of the last main release
   (This ensures more test coverage on those changes)

There is a section on backporting features as well, but the constraints
limit it to something that is IMHO sane to SRU:

-  There is a justifiable use case (for example a new PMD).
-  The change is non-invasive.
-  There is support within the community.

This so far happened very rarely and In addition those features (mostly
PMDs to support more HW) are only added in stable releases being not
built by default. For packaging that means this is a no-op as we won't
enable it so nothing changes.

Commits are peer reviewed as part of the normal development process and
are signed to signify both the developer and review (see
`contrib <http://dpdk.org/doc/guides/contributing/patches.html>`__ for
the doc on this).

LTS release updates are made after some time has passed (to allow
testing) and usually follow the new master release which happens more or
less every 3 months (see the the current
`road-map <http://dpdk.org/dev/roadmap>`__).

Updates to LTS releases are numbered with a minor point release

::

      16.11: 16.11.1, 16.11.2, ...
      17.11: 17.11.1, 17.11.2, ...

I watched the DPDK 16.11.x LTS release as it was the first of its kind
and it was great. Due to the fast pace of DPDK development with 3 month
release cycles a stable release is very important to carry the stability
needed by Distribution LTS releases. Therefore I now plan to:

-  release Ubuntu 18.04 with the first stable release 17.11.1
-  Ask for this MRE to keep up with further stable releases

.. _upstream_regression_testing:

Upstream Regression Testing
---------------------------

The upstream DPDK regression suite is a mix of comprehensive functional
tests (API coverage, etc.) and stress workloads via packet generators.
The full set is defined at the `DTS
suite <http://dpdk.org/doc/dts/gsg/intro.html>`__.

The QA suite is run against the branches regularly to hunt for
low-frequency problems. Everything should be tested regularly, and all
but the most recent patches have been tested over and extended period of
time.

Results are published via email to the dpdk-test-report mailing list
(see an
`examples <http://dpdk.org/ml/archives/test-report/2017-May/020337.html>`__).

In addition there is a smaller set of integration tests that runs
pre-checks. This is integrated into patchwork to directly augment the
patch review. Those checks were run by Intel so far but are currently
extended to be a Hardware vendor opt-in to gain even more coverage - see
`CI <http://dpdk.org/browse/tools/dpdk-ci/tree/README>`__ efforts for
details on this growing part of the project that will provide even more
coverage.

.. _ubuntu_dpdk_testing:

Ubuntu DPDK Testing
-------------------

DPDK has very high constraints on the environment (a lot of memory, huge
pages, certain CPU features) as well as the Hardware (limited to a set
of cards that have PMDs).

Therefore we have a
`test <https://code.launchpad.net/~ubuntu-server/ubuntu/+source/dpdk-testing/+git/dpdk-testing>`__
set outside of autopkgtest that tries to cover the basic use case we
know users have in mind (you can use DPDK for way more, but we want and
can only test what is in the archive).

In particular this sets up a set of KVM guests and runs a few test tools
to finally set up a dpdk enabled Open vSwitch between them. On this dpdk
enabled Open vSwitch it then runs some benchmarks to ensure no
significant performance loss (compared manually for now) and some
endurance tests via re-attaching devices or re-starting guests (all
those based on lessons learned by past issues we identified).

In addition, we set up
`autopkgtests <http://autopkgtest.ubuntu.com/packages/dpdk>`__ as well
for those components that can be tested. Those are mostly the extra
packaging bits that would not be covered by the upstream testing: -
testing the init scrips - testing dkms modules work withing Ubuntu -
testing the correct linking of builds against dpdk

Note: We also test the dpdk autotests in autopkgtests but for the
constraints mentioned before they are not reliable in the environment
they run in and thereby not yet gating.

.. _proposed_sru_approach:

Proposed SRU Approach
---------------------

=== only DPDK LTS releases for Ubuntu LTs releases ==

SRU updates for DPDK in Ubuntu will be aligned to the associated LTS
release of DPDK and only taken care for Ubuntu LTS releases:

::

    18.04 -> DPDK 17.11.x 20.04 -> DPDK 19.11.x (if releases still align) [...]

Ubuntu will only use the released version of updates and will not pull
directly from the upstream VCS. That is important as on the release of a
DPDK LTS there is another test/verification loop that we want to see
passed.

.. _testing_and_verification:

Testing and verification
------------------------

In addition to all the verification done by upstream prior to be
releases the proposed packages will be prepared, uploaded and tested
both standalone and in-conjunction with Open vSwitch (following the
methodology detail above) as part of the standard SRU verification
process for packages with MRE's.

An upload for an SRU shall be acompanied by a log of running the
`internal
test <https://code.launchpad.net/~ubuntu-server/ubuntu/+source/dpdk-testing/+git/dpdk-testing>`__.
All tests in this log shall be passed or explained in the Template why
not passing is to be considered ok in this case.


DPDK Requesting the SRU
-----------------------

The SRU should be done with a single process bug, instead of individual
bug reports for individual bug fixes. The one bug should have the
following:

-  The SRU should be requested "normally" per the StableReleaseUpdates
   documented process.
-  The template at the end of this document should be used and all
   ‘TODO’ filled out.
-  Major changes should be called out in the SRU template, especially
   where changed behavior is not backwards compatible.
-  Changelog should contain a link to the stable releases announcement
   (`example <http://dpdk.org/ml/archives/announce/2017-December/000163.html>`__)


DPDK SRU Template
-----------------

::

   This bug tracks an update for the DPDK packages, version TODO.

   This update includes bugfixes only following the SRU policy exception defined at
   https://documentation.ubuntu.com/sru/en/latest/reference/exception-DPDK-Updates
   [TODO: check to be true (ensure features stay disabled by default) or discuss new features on the SRU in detail if they are applying to "other safe" category (https://documentation.ubuntu.com/sru/en/latest/reference/requirements/#other-safe-cases)]

   [Impact]

   Stable release update so not directly applicable; see the exception policy document.

   [Major Changes]

   TODO: List the major changes
   TODO: list to the announce mail containing all changes

   [Test Plan]

   See https://documentation.ubuntu.com/sru/en/latest/reference/exception-DPDK-Updates/#testing-and-verification
   TODO: attach a log of executing said tests from a ppa with the upload
   TODO: if there are any non passing tests - explain why that is ok in this case.

   [Regression Potential]

   Upstream performs extensive testing before release, giving us a high degree of confidence in the general case. There problems are most likely to manifest in Ubuntu-specific integrations, such as in relation to the versions of dependencies available and other packaging-specific matters.

   TODO: consider any other regression potential specific to the version being updated and list if any or list N/A.

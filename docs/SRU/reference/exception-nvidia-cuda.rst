.. _reference-exception-nvidia-cuda:

#####################
 Nvidia CUDA updates
#####################

**************
 Introduction
**************

This document describes the policy, process and criteria for updating NVIDIA
CUDA libraries in a stable supported distro, including LTS.

NVIDIA CUDA is broadly used by developers for GPU compute activities, for
example for AI/ML. Ubuntu has a redistribution agreement with NVIDIA to
redistribute the CUDA libraries in the Ubuntu archive. Per the agreement, Ubuntu
must deliver the prebuilt binaries from NVIDIA without modifications, and follow
the same schedule than NVIDIA.

CUDA represents ~37 new source packages for every minor version. Minor versions
are released on average every 3 months. Each minor version usually get one or
two patch versions, which will be candidates for SRUs. Given the nature of
CUDA, these SRUs are not compliant with the usual SRU policy.

As of the time of writing, CUDA packages are under an allowed exception to install
files under /usr/local. The exception is temporary. Any SRU request that is patching 
a CUDA version relying on the exception is expected to keep installing files under /usr/local.

.. _requesting_sru:

********************************
 NVIDIA CUDA Requesting the SRU
********************************

The SRU should be done with a single process bug, instead of individual bug
reports for individual bug fixes. The one bug should have the following:

- The SRU should be requested per the :ref:`StableReleaseUpdates
  <howto-perform-standard-sru>` documented process
- The template at the end of this document should be used and all ‘TODO’ filled
  out
- The changelog will contain a reference to the single SRU process bug, not all
  bugs fixed by the SRU. However, if there are very important bugs that are
  deemed worthy of reference they too should be included in the changelog.
- Major changes should be called out in the SRU template, especially where
  changed behavior is not backward compatible.
- For each release that is proposed to be updated by the SRU a link to the
  results of the automated tests so that anyone can verify that they have been
  executed successfully.
- Additionally, the SRU bug should be verbose in documenting any manual testing
  that occurred.
- Any architecture specific fixes need to be noted and architecture specific
  test results included.
- Any packaging changes (e.g. a dependency change) need to be stated

.. _packaging_qa:

**************************
 NVIDIA CUDA Packaging QA
**************************

The objective of the QA is to test:

- Package installation from scratch
- Package upgrades
- Compliancy with NVIDIA's own releases

This QA is implemented as an autopkgtest within each source package. The result
of the tests will be attached to the SRU bug. The package upgrade must be
attempted manually, from a fresh installation.

.. _integration_tests:

*******************
 Integration tests
*******************

- `Certification test suite
  <https://github.com/canonical/checkbox/blob/main/providers/gpgpu/units/cuda.pxu>`__
  must pass on a range of hardware, with the same result as with NVIDIA's
  provided packages.

.. _sru_template:

**************************
 NVIDIA CUDA SRU Template
**************************

::

    [Impact]
    This patch provides both bug fixes and we would like to
    make sure all of our users have access to these improvements.

    The patched packages are:

    *** <TODO: Provide a list of updated packages, by comparing https://developer.download.nvidia.com/compute/cuda/redist/redistrib_${MAJOR}.${MINOR}.${PATCH}.json for the current and target versions  >

    [Test Plan]
    The following development and SRU process was followed:
    https://documentation.ubuntu.com/sru/en/latest/reference/exception-nvidia-cuda/

    <TODO Document any QA done, automated and manual>

    The QA team that executed the tests will be in charge of attaching the artifacts and
    console output of the appropriate run to the bug. NVIDIACUDA maintainers team members
    will not mark ‘verification-done’ until this has happened.

    [Where problems could occur]
    NVIDIA could be delivering a not-so-minor change that could cause regressions. The pre-built nature of CUDA
    prevent us to detect that. It could not install anymore due to a missing newly added package, for example.
    The installation test, the autopkgtests and the integration tests should be able to detect that.

    <TODO: attach test artifacts for every SRU release, not a link as links expire>

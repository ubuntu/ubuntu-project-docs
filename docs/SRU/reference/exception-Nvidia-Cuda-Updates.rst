.. _reference-exception-Nvidia-Cuda-Updates:

Nvidia CUDA updates
===================

Introduction
-------------

This document describes the policy, process and criteria for updating NVIDIA
CUDA libraries in a stable supported distro, including LTS.

NVIDIA CUDA is broadly used by developers for GPU compute activities, for
example for AI/ML. Canonical has a redistribution agreement with NVIDIA to
redistribute the CUDA libraries in the Ubuntu archive. Per the agreement, Canonical
must deliver the prebuilt binaries from NVIDIA without modifications.

CUDA consists of about 37 new source packages for every minor version. Minor versions
are released on average every 3 months. Each minor version usually receives one or
two patch versions, which will be candidates for SRUs. Since our redistribution 
agreement requires us to match NVIDIA's changes exactly within a given CUDA release,
and since CUDA consists primarily of precompiled binaries, our CUDA packages must all
roll forward in tandem on each upstream update. As a result, CUDA SRUs are not 
compliant with the standard SRU policy.

As of the time of writing, CUDA 13.x packages are under an allowed exception to
install files under /usr/local. The exception is temporary, and we are working on a
plan to remove it with CUDA 14.x. Any SRU request that is patching a CUDA version
relying on the exception is expected to keep installing files under /usr/local.

.. _release_versions:

Released versions
------------------

**Minor versions**:

CUDA packages are released in the multiverse pocket.
CUDA's minor versions are meant to be available and installable in parallel, and
therefore e.g. 13.2 does not replace 13.1 in Ubuntu. Minor versions are always a
new set of source packages, suffixed with MAJOR.MINOR, e.g. cuda-13-2.

CUDA's minor version package sets are meant to be broadly SRU'd to
compatible releases that are supported, starting with 26.04. For example, when
the currently hypothetical 14.1.0 version is released for 28.04, it will be
SRU'd to 27.10 and 26.04.

A few binary package have the same name between two minor versions:
-  cuda
-  cuda-toolkit and cuda-toolkit-<MAJOR>

Users expect these binary packages to be rolling. They can use
cuda-<MAJOR>-<MINOR> and cuda-toolkit-<MAJOR>-<MINOR> to be sure to stay on
the same minor version. NVIDIA recommends the installation of minor-tight
CUDA versions in their own documentation.

**Patch versions**:

Patch versions do replace the corresponding existing version so e.g. 13.2.1 will
replace 13.2.0.

CUDA's patch version package sets are also meant to be broadly SRU'd to
compatible releases that are supported. For example, 26.04 was released with
13.1.1 and when 13.1.2 is available in devel it will be SRU'd up until 26.04.

In the past, a patch version of nsight-compute could change the name of a
binary package. For example, 13.2.0 had `nsight-compute-2026.1.0` while
13.2.1 had `nsight-compute-2026.1.1`. In such cases, the new package, this
SRU exception allows the patch version to be SRU'd only if there is a
transitional package from the old name to the new name.

Internal dependencies
---------------------

CUDA packages have internal dependencies illustrated in the following graph:

.. mermaid::

flowchart TD
    n0["cccl-13-4"]
    n1["cuda-crt-13-4"]
    n2["cuda-ctadvisor-13-4"]
    n3["cuda-cudart-13-4"]
    n4["cuda-culibos-13-4"]
    n5["cuda-cuobjdump-13-4"]
    n6["cuda-cupti-13-4"]
    n7["cuda-cuxxfilt-13-4"]
    n8["cuda-documentation-13-4"]
    n9["cuda-gdb-13-4"]
    n10["cuda-nvcc-13-4"]
    n11["cuda-nvdisasm-13-4"]
    n12["cuda-nvml-dev-13-4"]
    n13["cuda-nvprune-13-4"]
    n14["cuda-nvrtc-13-4"]
    n15["cuda-nvtx-13-4"]
    n16["cuda-opencl-13-4"]
    n17["cuda-profiler-api-13-4"]
    n18["cuda-sandbox-dev-13-4"]
    n19["cuda-sanitizer-api-13-4"]
    n20["cuda-tileiras-13-4"]
    n21["libcublas-13-4"]
    n22["libcudla-13-4"]
    n23["libcufft-13-4"]
    n24["libcufile-13-4"]
    n25["libcuobjclient-13-4"]
    n26["libcurand-13-4"]
    n27["libcusolver-13-4"]
    n28["libcusparse-13-4"]
    n29["libnpp-13-4"]
    n30["libnvfatbin-13-4"]
    n31["libnvjitlink-13-4"]
    n32["libnvjpeg-13-4"]
    n33["libnvptxcompiler-13-4"]
    n34["libnvvm-13-4"]
    n35["nsight-compute-13-4"]
    n36["nsight-systems-13-4"]
    n1 --> n3
    n3 --> n0
    n3 --> n4
    n9 --> n5
    n9 --> n11
    n10 --> n1
    n10 --> n3
    n10 --> n33
    n10 --> n34
    n16 --> n3
    n20 --> n10
    n20 --> n31
    n21 --> n3
    n21 --> n4
    n23 --> n3
    n23 --> n4
    n24 --> n3
    n25 --> n3
    n26 --> n3
    n26 --> n4
    n27 --> n3
    n27 --> n4
    n28 --> n3
    n28 --> n4
    n29 --> n3
    n29 --> n4
    n30 --> n3
    n31 --> n3
    n32 --> n3
    n32 --> n4
    n34 --> n3

Sponsors should ideally respect this uploading order:
1. cuda-cuobjdump, cuda-nvdisasm, libcudla, cuda-sandbox-dev, cuda-ctadvisor, 
cuda-nvml-dev, cuda-documentation, cuda-nvprune, cuda-cuxxfilt,
cuda-sanitizer-api, cuda-nvtx, cuda-nvrtc, cuda-profiler-api, sight-compute,
nsight-systems, cccl, culibos
2. cudart, cuda-gdb
3. cuda-opencl, libnvfatbin, libcufile, libcuobjclient, libnjpeg, libcufft,
libcurand, libcublas, libcusolver, libcusparse, libnpp, cuda-crt, libnvvm,
libnvjitlink
4. cuda-nvcc
5. cuda-tileiras
6. cuda-meta
Since these packages are not build from source, dependencies are only resolved
through the package manager. Most of the packages can build without their
theoretical build-depends.

The specificity of cuda-meta
----------------------------

`cuda-meta` is the source package that contains all the metapackages
distributing CUDA. Just like every other source package, it is tight to it
minor version, eg CUDA 13.2 contains a cuda-meta-13-2 source package.

cuda-meta-X-Y contains
- cuda
- cuda-X-Y
- cuda-toolkit
- cuda-toolkit-X
- cuda-toolkit-X-Y
And a few others that are less problematic.
The problem with cuda, cuda-toolkit and cuda-toolkit-X is that the same binary
package is shipped again in other versions (cuda-meta-X-(Y+1) for example).

The archive won't complain. For users, if they had install one of these meta
from a cuda-meta-X-Y source package, they will automatically be rolled forward
to the newer version provided by cuda-meta-X-(Y+1).

It's trickier for SRUs. If we SRU, for example, cuda-meta-13-1 (13.1.2) in
26.04 and cuda-meta-13-2 (13.2.0) is in 26.04 already, then we are trying to
upload binary packages that are **already** superseded. In that case, we chose
to comment these binary packages in the control file.

.. _requesting_sru:

NVIDIA CUDA Requesting the SRU
-------------------------------

The SRU should be done with a single process bug appropriately named
`cuda-X-Y`, instead of individual bug
reports for individual bug fixes. The one bug should have the following:

- The SRU should be requested per the :ref:`StableReleaseUpdates
  <howto-perform-standard-sru>` documented process
- The template at the end of this document should be used and all ‘TODO’ items
  filled out
- This SRU exception applies to only the multiverse archive component.
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


NVIDIA CUDA Packaging QA
-------------------------

The objective of the QA is to test:

-  Package installation from scratch
-  Package upgrades
-  Compliance with NVIDIA's own releases

   -  Making sure that we deliver the right binary in the right packages with
      the right license and dependencies
   -  Making sure the CUDA installation is working as expected (integration
      tests with cuda samples).
-  Compatibility with NVIDIA's own releases and repos

   -  Making sure that NVIDIA's packages supersede ours, and that users adding
      the NVIDIA repo don't end up with a mix of our packages and NVIDIA's packages

This QA is implemented as an autopkgtest within each source package. The result
of the tests will be attached to the SRU bug. The package upgrade must be
attempted manually, from a fresh installation.

.. _integration_tests:


Integration tests
------------------

- `Certification test suite
  <https://github.com/canonical/checkbox/blob/main/providers/gpgpu/units/cuda.pxu>`__
  must pass on a range of hardware, including at least one workstation and one
  server GPU, with the same result as with NVIDIA's provided packages.

.. _sru_template:


NVIDIA CUDA SRU Template
-------------------------

::

    [Impact]
    This patch provides both bug fixes and improvements and we would like to
    make sure all of our users have access to these improvements.

    The patched packages are:

    *** <TODO: Provide a list of updated packages, by comparing https://developer.download.nvidia.com/compute/cuda/redist/redistrib_${MAJOR}.${MINOR}.${PATCH}.json for the current and target versions >

    [Test Plan]
    The following development and SRU process was followed:
    https://documentation.ubuntu.com/sru/en/latest/reference/exception-Nvidia-Cuda-Updates/

    <TODO Document any QA done, automated and manual>

    The QA team that executed the tests will be in charge of attaching the artifacts and
    console output of the appropriate run to the bug. NVIDIACUDA maintainers team members
    will not mark ‘verification-done’ until this has happened.

    [Where problems could occur]
    NVIDIA could deliver a not-so-minor change that could cause regressions. The pre-built nature of CUDA
    prevents us from detecting that. It might fail to install due to a newly added missing package, for example.
    The installation test, the autopkgtests and the integration tests will to detect that.

    <TODO: attach test artifacts for every SRU release, not a link as links expire>

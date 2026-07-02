.. _reference-exception-AMD-ROCm-Updates:

AMD ROCm updates
================

Introduction
------------

This document describes the policy, process and criteria for updating the AMD
ROCm open-source GPU compute stack in a stable supported distro, including LTS.

ROCm (Radeon Open Compute) is AMD's open-source GPU compute platform, broadly
used by developers for AI/ML, HPC and scientific computing on AMD GPUs.
Canonical packages and ships ROCm libraries in the Ubuntu multiverse archive.

ROCm consists of approximately 32 source packages that form a tightly coupled
stack. All packages in the stack must be updated atomically: cross-version
combinations are neither tested by AMD nor expected to be functional, because
the ABI, API, CMake find-package configs and GPU device-library ABIs are all
versioned together. As a result, ROCm SRUs are not fully compliant with the
standard SRU policy in the following respects:

- A single SRU covers all ~32 source packages simultaneously (coordinated
  update), rather than one source package per SRU bug.

- Several packages in the stack ship pre-compiled GPU kernel code objects (HSA
  Code Objects, the GPU equivalent of machine code) for each supported AMD GPU
  architecture. The most prominent example is ``hipblaslt``, whose Tensile
  library embeds pre-compiled GEMM kernels for gfxNNN targets. These binaries
  are redistributed as-is from AMD upstream; Canonical does not recompile them.

- Individual bug fixes cannot be cherry-picked from an upstream patch release
  without taking the full coordinated release, because AMD issues patch versions
  as atomic snapshots of the entire stack rather than as per-repository patches.

- The Launchpad SRU process bug covers the entire coordinated package set rather
  than individual per-package fixes. Important individual bugs may additionally
  be referenced in per-package changelogs.

As of the time of writing, ROCm packages are shipped in the multiverse archive
component and are subject to multiverse SRU rules.

.. _rocm_released_versions:

Released versions
-----------------

**Versioning scheme**:

ROCm follows a MAJOR.MINOR.PATCH scheme. The Ubuntu archive ships a single
active minor-version series at any given time; a new minor version **replaces**
the previous one (unlike NVIDIA CUDA's parallel-installation model). For
example, ROCm 7.2.x replaces 7.1.x in the archive; both cannot be installed
simultaneously.

**Minor versions (e.g. 7.1 → 7.2)**:

Minor versions are released by AMD approximately every three to four months.
Each minor release may add support for new AMD GPU architectures (identified by
their gfxNNN GFX IP code), introduce new public APIs, and carry large
refactors. Minor-version updates are not SRU'd to stable releases while a
newer minor version is still under active development; they land in devel first
and are then evaluated for SRU. When a minor version becomes stable and the
next minor version has landed in the devel series, the stable minor version
will be SRU'd to all compatible supported Ubuntu releases.

**Patch versions (e.g. 7.2.0 → 7.2.4)**:

Patch versions are issued by AMD within a minor-version series to deliver bug
fixes, correctness patches, and performance improvements. AMD typically releases
two to four patch versions per minor version. Patch versions are the primary
SRU vehicle: when a new patch version lands in the devel series it is evaluated
against this exception policy and, if approved, SRU'd to all supported Ubuntu
releases that carry the same minor version, starting with resolute (26.04 LTS).
For example, when 7.2.4 is released for the devel series it will be SRU'd to
resolute (26.04) and any other supported release that ships ROCm 7.2.x.

SOVERSIONs do not change between patch releases within a minor version series.
No reverse-dependency rebuilds are required for a patch-version SRU.

**Package list**:

The following source packages form the ROCm stack and are updated together in
each coordinated SRU:

Core runtime and toolchain:

- ``rocm-core``
- ``rocm-cmake``
- ``rocr-runtime``
- ``rocm-hipamd`` (provides libamdhip64, libhiprtc, rocm-opencl-icd)
- ``rocm-llvm`` (provides rocm-device-libs and clang-based toolchain wrappers)
- ``llvm-toolchain-rocm``
- ``rocm-smi-lib``
- ``rocminfo``
- ``rocm`` (meta-package)

Debugger support:

- ``rocdbgapi``
- ``roctracer``

Math and compute libraries:

- ``rocblas``
- ``rocfft``
- ``rocrand``
- ``rocprim``
- ``rocthrust``
- ``rocwmma``
- ``hipcub``
- ``rocalution``
- ``rocsparse``
- ``rocsolver``
- ``miopen``
- ``rccl``

HIP interface libraries:

- ``hipblas-common``
- ``hipblas``
- ``hipblaslt``
- ``hipfft``
- ``hiprand``
- ``hipsparse``
- ``hipsolver``

Tooling:

- ``hipify``

``amdsmi`` (AMD System Management Interface) is also part of the ROCm stack
and follows the same MAJOR.MINOR.PATCH version numbering. It is included in
the coordinated SRU. However, because its release cadence sometimes diverges
slightly from the rest of the stack (e.g. a patch release may land earlier or
later than the main set), it may be uploaded separately to -proposed as long
as the process bug is the same and the final -updates migration is coordinated.

.. _rocm_requesting_sru:

AMD ROCm Requesting the SRU
-----------------------------

The SRU for each target stable release (e.g. resolute 26.04) must be tracked
under a single process Launchpad bug named after the coordinated release, e.g.
``rocm-7.2.4``. Individual package uploads reference this bug in their
changelogs. The SRU process must follow the :ref:`StableReleaseUpdates
<howto-perform-standard-sru>` documented process, with the following additions
mandated by this exception:

- **One process bug per target release**: all source packages for a given
  ``MAJOR.MINOR.PATCH`` bump to a given stable series share a single process
  bug. Per-package upload bugs may be filed but must be cross-referenced from
  the process bug.

- **The SRU template** at the end of this document must be completed. All
  ``TODO`` items must be filled in before the upload is submitted for review.

- **This SRU exception applies to the multiverse archive component only.**

- **Changelogs**: each source package changelog must reference the process bug.
  Where a patch release fixes a particularly important user-visible bug, that
  bug may also be referenced explicitly.

- **All packages must upload to -proposed simultaneously** (or as close to
  simultaneously as feasible). Individual packages must not migrate to -updates
  while other packages in the coordinated set are still pending in -proposed.

- **Architecture-specific notes**: ROCm targets amd64 as the primary
  architecture. Any arm64 or other architecture-specific build results must be
  noted in the SRU template.

- **Packaging changes** (dependency additions or removals, new binary packages,
  changed install paths) must be explicitly documented in the SRU template.

- **ABI verification**: for each source package that ships a shared library,
  the SRU template must state the result of either ``dpkg-gensymbols`` (with
  ``DPKG_GENSYMBOLS_CHECK_LEVEL=4``) or ``abidiff`` comparing the old and new
  binaries. SONAME changes are not permitted in patch-version SRUs; any SONAME
  change escalates the upload to a new-minor-version SRU with a full review.

.. _rocm_packaging_qa:

AMD ROCm Packaging QA
----------------------

The objective of the QA is to verify:

- **Fresh installation** of the full package set from the -proposed pocket on a
  clean resolute (or target release) system.

- **Upgrade** from the currently published archive version to the -proposed
  version on a system with the old ROCm stack installed.

- **ABI compliance**: SOVERSIONs unchanged; ``dpkg-gensymbols`` or ``abidiff``
  reports no removed or changed public symbols for each shared library.

- **Autopkgtest pass**: the autopkgtest suite for each source package that
  ships a ``debian/tests/control`` must pass. For packages that require a GPU
  (the majority), tests must be executed on a host with a supported AMD GPU
  using the ``rocm-gpu`` LXD profile. Results must be attached to the SRU
  process bug.

- **GPU device-code correctness** (integration tests, see below): the GEMM,
  FFT, BLAS and related compute kernels must produce numerically correct output
  on a representative set of AMD GPU architectures.

- **NVIDIA/other hardware**: ROCm installs should not interfere with non-AMD
  GPU configurations. This check is out of scope for the autopkgtests but
  should be noted if affected.

The package upgrade must be verified manually starting from a fresh installation
of the currently published version. Autopkgtest results alone are not sufficient
to satisfy the upgrade requirement.

.. _rocm_integration_tests:

Integration tests
-----------------

The following integration tests must pass before the SRU is approved:

- The autopkgtest suite for every source package in the coordinated set must
  pass on a real AMD GPU testbed (``rocmtest`` host or equivalent, amd64,
  Ubuntu resolute, LXD ``rocm-gpu`` profile).

- All autopkgtests must be run on at least one supported AMD GPU. The GPU
  model used (identified by its gfxNNN architecture code) must be stated in
  the SRU process bug, along with the full autopkgtest log. Expanded coverage
  across additional GPU architectures is encouraged but not required.

- For ``hipblaslt``, which ships pre-compiled Tensile GPU kernels: results
  from the ``libhipblaslt1-tests`` autopkgtest must confirm that the embedded
  kernels execute correctly on the GPU architectures present in the test fleet.

- For ``rocfft`` and ``hipfft``, which include a large accuracy test suite:
  out-of-memory skips due to GPU VRAM limits are acceptable (they do not
  constitute failures) provided the same test passed in a targeted re-run with
  sufficient available VRAM. Non-OOM failures require investigation and must be
  cleared before the SRU is approved.

.. _rocm_sru_template:

AMD ROCm SRU Template
----------------------

The following template must be used for the process bug description. One
``[Package]`` section is required per source package in the coordinated set.
All ``TODO`` items must be completed before submission for SRU review.

::

    [Process bug]
    This is the SRU process bug for the coordinated ROCm MAJOR.MINOR.PATCH
    stack update to Ubuntu RELEASE (TARGET_RELEASE LTS).

    All source packages listed below are updated atomically per the ROCm SRU
    exception:
    https://documentation.ubuntu.com/sru/en/latest/reference/exception-AMD-ROCm-Updates/

    The SRU process followed is documented at:
    https://documentation.ubuntu.com/sru/en/latest/reference/exception-AMD-ROCm-Updates/

    [Affected packages]
    *** <TODO: List all source packages and the old → new version for each,
               e.g.:
               rocm-core        7.1.0-0ubuntu1   → 7.2.4-0ubuntu1
               rocr-runtime     7.1.0+dfsg-0ubuntu6 → 7.2.4+dfsg-0ubuntu1
               ...>

    [Impact]
    *** <TODO: Summarise the key changes in this patch release that affect
               Ubuntu users: correctness fixes, performance improvements,
               new GPU architecture support, notable packaging changes.
               Identify which changes are upstream library changes vs
               Debian/Ubuntu packaging fixes.>

    This update is part of the coordinated ROCm MAJOR.MINOR.PATCH stack
    release for Ubuntu TARGET_RELEASE.

    [Test Plan]
    The following development and SRU process was followed:
    https://documentation.ubuntu.com/sru/en/latest/reference/exception-AMD-ROCm-Updates/

    For each source package below, the results of the autopkgtest suite are
    listed. All tests were run on a real AMD GPU testbed (rocmtest host,
    ubuntu-daily:TARGET_RELEASE, lxd --profile=rocm-gpu, amd64) unless
    otherwise stated.

    *** <TODO: For each source package that ships debian/tests/control,
               paste the relevant section of the autopkgtest summary output
               (the @@@@@@@@@@@@@@@@@@ summary block). Indicate the GPU model
               used and the date of the run. Attach full logs to this bug.>

    [ABI verification]
    *** <TODO: For each source package that ships a shared library, state the
               result of DPKG_GENSYMBOLS_CHECK_LEVEL=4 or abidiff.
               Confirm SOVERSIONs are unchanged.
               E.g.:
               librocblas5:   DPKG_GENSYMBOLS_CHECK_LEVEL=4 — no symbols
                              added/removed/changed. SONAME librocblas.so.5
                              unchanged.
               libhipfft0:    abidiff 7.1.1 → 7.2.4: exit 0, no output.
                              SONAME libhipfft.so.0 unchanged.
               libhipfftw0:   6 symbols added (additive-only). SONAME
                              libhipfftw.so.0 unchanged.>

    [Where problems could occur]
    - If a package in the coordinated set fails to build or install, it may
      prevent the rest of the stack from being installable. Symptom: apt
      dependency resolution failure when installing any ROCm meta-package.
    - Pre-compiled GPU kernels in hipblaslt (Tensile) may produce incorrect
      results on GPU architectures not present in the AMD test matrix. Symptom:
      GEMM accuracy failures on an unlisted gfxNNN target.
    - Packaging changes (new dependencies, renamed binary packages) could break
      upgrade paths. Symptom: apt reports unresolvable conflicts or missing
      packages during upgrade from the old version.
    *** <TODO: Document any additional package-specific risks identified during
               testing.>

    [Other info]
    *** <TODO: Include PPA links for each package, upstream comparison URLs
               (github.com/ROCm/<repo>/compare/rocm-OLD...rocm-NEW), and any
               known pre-existing build failures (armhf, s390x, etc.) that
               are out of scope for this SRU.>

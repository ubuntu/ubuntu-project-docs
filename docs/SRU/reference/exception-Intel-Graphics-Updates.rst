.. _reference-exception-Intel-Graphics-Updates:

Intel Graphics Stack Updates
============================

This document describes the policy for doing updates of the Intel graphics
stack packages in Ubuntu releases.

.. _about_intel_graphics:

About the Intel graphics stack
------------------------------

The Intel graphics stack is a multi-package recipe for GPU-based functionality 
in Intel hardware in Ubuntu. The following packages are currently included in 
this group:

#. intel-gmmlib
#. libva
#. libva-utils
#. intel-media-driver
#. intel-media-driver-non-free
#. level-zero
#. level-zero-gpu-raytracing
#. intel-compute-runtime
#. intel-graphics-compiler
#. onetbb
#. libvpl
#. libvpl-tools
#. onevpl-intel-gpu
#. intel-vc-intrinsics

Whenever new Intel graphics hardware is introduced, support for that hardware 
must be added in the kernel as well as in these userspace packages. Without 
these efforts, baseline functionalities like hardware encode/decode would not 
work on new hardware.

Since users often prefer LTS releases, these packages need periodic backporting
to ensure prompt support for their new hardware at time of launch.

This update work will often be closely related to Mesa updates for HWE

.. _upstream_release_policy:

Upstream release policies
^^^^^^^^^^^^^^^^^^^^^^^^^

Most projects use semantic versioning:

* intel-gmmlib (22.8.1, 22.8.0, 22.7.3, 22.7.2, 22.7.1)
* libva and libva-utils (2.22.0, 2.21.0, 2.20.0, 2.19.0)
* intel-media-driver and intel-media-driver-non-free (25.3.3, 25.3.2, 25.3.1)
* level-zero (1.24.2, 1.24.1, 1.24.0, 1.23.2, 1.23.1)
* level-zero-gpu-raytracing (1.0.0, 1.1.0)
* intel-graphics-compiler (2.16.0, 2.14.1, 2.12.5)
* onetbb (2022.2.0, 2022.1.0, 2022.0.0, 2021.13.0)

  * Calendar versioning converted to semantic versioning

* libvpl (2.15.0, 2.14.0, 2.13.0)
* libvpl-tools (1.4.0, 1.3.0, 1.2.0)
* intel-vc-intrinsics (0.23.2, 0.23.1, 0.23.0, 0.22.1)

Two still use date-based versioning and should not be understood to contain
API-breaking changes if the leftmost version changes:

* intel-compute-runtime (25.31.34666.3, 25.27.34303.5, 25.22.33944.8)
* onevpl-intel-gpu (25.2.6, 25.1.4, 24.4.4)

Additionally, Intel has support guarantees merged into nearly all listed
packages:

* Media Driver (free and non-free)

  * https://github.com/intel/media-driver?tab=readme-ov-file#backward-compatibility

* IGC

  * https://github.com/intel/intel-graphics-compiler?tab=readme-ov-file#supported-platforms

* Compute Runtime

  * https://github.com/intel/compute-runtime?tab=readme-ov-file#supported-platforms

* vpl-gpu-rt (onevpl-intel-gpu)

  * https://github.com/intel/vpl-gpu-rt?tab=readme-ov-file#backward-compatibility

* level zero raytracing support

  * https://github.com/intel/level-zero-raytracing-support?tab=readme-ov-file#supported-platforms

* gmmlib

  * https://github.com/intel/gmmlib?tab=readme-ov-file#supported-platforms

* vc-intrinsics

  * https://github.com/intel/vc-intrinsics?tab=readme-ov-file#supported-platforms

* onetbb

  * https://github.com/uxlfoundation/oneTBB/pull/1797/files

* level-zero

  * This is not a HW driver

  * Uses semver, which contains the builtin assumption that API-breaking
    changes will result in a semver major version change.

  * https://github.com/oneapi-src/level-zero/blob/master/CONTRIBUTING.md#code-review

* libvpl

  * https://github.com/intel/libvpl?tab=readme-ov-file#backward-compatibility

* libvpl-tools

  * Is not a HW driver, is a support library for libvpl dispatcher

* libva

  * https://github.com/intel/libva/pull/855

* libva-utils

  * Is not a HW driver, uses what libva loads

.. _ubuntu_releases_affected:

Ubuntu releases affected by this exception
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We will only SRU hardware enablement version bumps back to the latest LTS, which is Noble at
this time.

.. _intel_gfx_history_track_record:

History and track record
^^^^^^^^^^^^^^^^^^^^^^^^^

Intel has a strong track record in these packages. We rarely need to backport 
fixes to the source itself, and our PPA for hardware enablement has been
active for over a year with no issues relating to source updates causing
regression.

.. _quality_assurance:

Quality assurance
-----------------

The process for integrating updates into Ubuntu involves several
layers of quality assurance testing to ensure stability and compatibility.

Upstream tests
^^^^^^^^^^^^^^

Each of these stacks undergoes substantial testing at Intel, both automated and
QA. Before any SRU is submitted, that work is already done. Our partners at
Intel typically test our integrations before we release them, and this is likely to
continue in the case of an SRU.

Ubuntu tests
^^^^^^^^^^^^

We have developed extensive testing for the Intel graphics stack by
integrating conformance tests into Checkbox providers here:

* https://github.com/canonical/checkbox-gfx

* https://github.com/canonical/checkbox-media

These tests are in the process of merging into checkbox/contrib:
https://github.com/canonical/checkbox/tree/main/contrib/checkbox-gfx

The following test suites are run:

* OpenCL conformance test suite from Khronos
* OpenGL conformance test suite from Khronos
* Vulkan conformance test suite from Khronos
* Crucible 
* Level Zero unit tests
* Level Zero Raytracing unit tests
* Libvpl unit tests

The following test categories were developed for media:

* Gstreamer
* FFmpeg
* Firefox
* GuC and HuC
* Totem (default video player)

Gstreamer and FFmpeg testing covers the following cases:

* Hardware encode (VP9, H264 @ 4K, 1080p)
* Hardware (HW) decode (AV1, VP9, H264, MJPEG, VP8, MPEG2 @ 4K, 1080p, 720p,
  480p, 360p, 180p)

Firefox testing covers:

* Hardware decode (AV1, VP9, H264, MJPEG, VP8 @ 4K, 1080p, 720p, 480p, 360p,
  180p)

GuC and HuC testing:

* checks to make sure that GuC and HuC have loaded

Totem testing covers:

* Hardware Decode (AV1, VP9, H264, MJPEG, VP8, MPEG2 @ 4K, 1080p, 720p, 480p,
  360p, 180p)

Hardware decode and hardware encode are confirmed using libva traces to ensure
that the correct entrypoint and libva profiles are used for the intended
operation. In plainer terms, we confirm that the GPU activity is due to VP9 HW
decode and not a hypothetical H264 HW encode operation happening
simultaneously.

Hardware Support
^^^^^^^^^^^^^^^^

SRUs should not regress hardware support. In this case, we should break down
support by top-level component. Supported hardware for each component can be
found here:

**Media Driver**: https://github.com/intel/media-driver?tab=readme-ov-file#supported-platforms

**Compute Runtime**: https://github.com/intel/compute-runtime?tab=readme-ov-file#supported-platforms

**Level Zero Raytracing**: https://github.com/intel/level-zero-raytracing-support?tab=readme-ov-file#supported-platforms

These lists should be compared between the current and proposed versions, and
any differences should be disclosed in the SRU to ensure that no generations
have been intentionally dropped from support. Additionally, release notes for
all packages will be checked for removal of API or hardware support.

To ensure that hardware support has not regressed unintentionally, the
previously-stated test plans will be run on a reasonable subset of the supported
generations.

.. csv-table::
   :header: "Generation", "Will Test", "Notes"
   :widths: 20, 10, 40

   "Broadwell (BDW)","Yes",""
   "Skylake (SKL)","Yes",""
   "Broxton (BXT)","No","Cancelled program"
   "Apollo Lake (APL)","Yes",""
   "Gemini Lake (GLK)","Yes",""
   "Kaby Lake (KBL)","Yes",""
   "Coffee Lake (CFL)","Yes",""
   "Whiskey Lake (WHL)","Yes",""
   "Comet Lake (CML)","Yes",""
   "Amber Lake (AML)","No","Low distribution, only a handful left online fully intact"
   "Ice Lake (ICL)","Yes",""
   "Jasper Lake (JSL)","Yes",""
   "Elkhart Lake (EHL)","Yes",""
   "Tiger Lake (TGL)","Yes",""
   "Rocket Lake (RKL)","Yes",""
   "Alder Lake (ADL)","Yes",""
   "Raptor Lake (RPL)","Yes",""
   "DG1/SG1","No","Low distribution, very similar to TGL"
   "DG2/DG2-ATSM","Yes",""
   "Meteor Lake (MTL)","Yes",""
   "Arrow Lake (ARL)","Yes",""
   "Lunar Lake (LNL)","Yes",""
   "Battlemage (BMG)","Yes",""
   "Panther Lake (PTL)","Yes",""

Test results will be compared between the current and proposed updates and will
be available for review. Any regressions will be highlighted in the SRU.

Since libva is also part of the AMD stack, the ffmpeg test plan will be run 
on an AMD device, and any regressions will be reported in the SRU.

**Caveats**

* In the event of difficulties with a device, the SRU team has full discretion
  on whether or not the test devices provide sufficient coverage.

* If an unlisted, newer generation is supported by any component, it should be
  added to the support list and tested.

* The addition of new functional components must be accompanied by new tests.

.. _security_uploads:

Security uploads
^^^^^^^^^^^^^^^^

CVEs are uncommon in these packages. Here is an exhaustive list of all CVEs
pertaining to packages in the Intel graphics stack:

* libva: https://ubuntu.com/security/CVE-2023-39929

  * Not a regression

* onevpl-intel-gpu: https://ubuntu.com/security/CVE-2024-28051

  * Not a regression, only before 24.1.4

* onevpl-intel-gpu: https://ubuntu.com/security/CVE-2024-28030

  * Not a regression, only before 24.1.4

* onevpl-intel-gpu: https://ubuntu.com/security/CVE-2024-21808

  * Not a regression, only before 24.1.4

* onevpl-intel-gpu: https://ubuntu.com/security/CVE-2024-21783

  * Not a regression, only before 24.1.4

.. _process:

Process
-------

Graphics HWE package versions will be worked out with Intel for new hardware
support. Partner Engineering's Intel squad will submit an SRU bug for tracking
the backport to these versions.

Verification
^^^^^^^^^^^^

Each major component of the stack (Compute Runtime, Media Driver, Mesa) will
have test results from Partner Engineering to show that no regression happens
during the version bump. Some dependencies such as level-zero also have tests.

Additionally, Intel and Canonical will run their own independent validation
cycles to ensure that the new stack does not introduce regressions.

Requesting the SRU
^^^^^^^^^^^^^^^^^^

The SRU should be done with a single process bug, instead of individual bug
reports for each package. 

* The template at the end of this document should be used and all $variables filled out. 
* Major changes should be called out in the SRU template, especially where changed behavior is not backwards compatible. 
* Any packaging changes (e.g. a dependency changes) need to be stated. 
* If any manual testing occurs it should also be documented. 
* If backwards compatibility is to be broken, this should be clearly written at
  the top of the bug description for the SRU, as well as in the package list 
  with "[breaks-compat]" for the offending package. Furthermore, an email to 
  ubuntu-release will be sent to point the release / SRU teams to the bug in
  order to get approval before uploading to the release's upload queue.
 
.. _sru_template:

SRU template
^^^^^^^^^^^^

::

    Title: Backport Intel Graphics stack to enable $intelPlatform on $release

    [ Impact ]

    Without backporting these versions, the graphics stack in Ubuntu would not
    run on $intelPlatform. This is not backporting a single fix, nor an MRE,
    but backporting a later version of each package for platform enablement.
    See the Intel Graphics SRU exception here for more details:

    https://documentation.ubuntu.com/sru/en/latest/reference/package-specific/#defined-exceptions

    [ Test Plan ]

    In order to track intentional hardware retiring, we will compare
    these lists in the current stable and proposed versions:
    * https://github.com/intel/media-driver?tab=readme-ov-file#supported-platforms
    * https://github.com/intel/compute-runtime?tab=readme-ov-file#supported-platforms
    * https://github.com/intel/intel-graphics-compiler?tab=readme-ov-file#supported-platforms
    * https://github.com/intel/level-zero-raytracing-support?tab=readme-ov-file#supported-platforms
    * https://github.com/intel/gmmlib?tab=readme-ov-file#supported-platforms
    * https://github.com/intel/vc-intrinsics?tab=readme-ov-file#supported-platforms
    * https://github.com/uxlfoundation/oneTBB/blob/master/SYSTEM_REQUIREMENTS.md#supported-hardware
    * https://github.com/intel/libvpl?tab=readme-ov-file#dispatcher-behavior-when-targeting-intel-gpus

    To mitigate unintentional hardware regressions, Intel's and Canonical's
    validation teams will install all proposed packages and test that the
    graphics stack is working as expected. Partner Engineering will run tests
    developed to confirm successful integration of each component and its
    dependencies. These tests will include at least:
    * Vulkan, OpenGL, and OpenCL conformance testing
    * Level Zero unit testing
    * Level Zero Raytracing unit testing
    * Libvpl unit tests
    * Crucible
    * Gstreamer testing
    * FFmpeg testing
    * Firefox testing
    * GuC and HuC testing
    * Totem (default video player) testing

    To run these tests, use the following commands:
    sudo snap install --classic snapcraft
    sudo snap install checkbox24
    lxd init --auto
    git clone https://github.com/canonical/checkbox-gfx
    cd checkbox-gfx
    snapcraft
    sudo snap install --dangerous --classic ./checkbox-gfx_1.0_<arch>.snap

    # These may need to be split up and run one-by-one with their respective
    # test scripts. Otherwise, they take up significant disk space
    checkbox-gfx.install-crucible
    checkbox-gfx.install-lvl-zero
    checkbox-gfx.install-lvl-zero-rt
    checkbox-gfx.install-opengl
    checkbox-gfx.install-opencl
    checkbox-gfx.install-vulkan

    checkbox-gfx.test-crucible
    checkbox-gfx.test-lvl-zero
    checkbox-gfx.test-lvl-zero-rt
    checkbox-gfx.test-opencl
    checkbox-gfx.test-opengl
    checkbox-gfx.test-vulkan

    # Remove all installed test material
    checkbox-gfx.remove

    sudo snap install --classic snapcraft
    sudo snap install checkbox24
    lxd init --auto
    git clone https://github.com/canonical/checkbox-media
    cd checkbox-media
    snapcraft
    sudo snap install --dangerous --classic ./checkbox-media_1.0_amd64.snap

    checkbox-media.install
    checkbox-media.install-gstreamer
    checkbox-media.install-video-players

    checkbox-media.test
    checkbox-media.test-gstreamer
    checkbox-media.test-browsers
    checkbox-media.test-intel
    checkbox-media.test-video-players

    We will then compare the initial test output (before the HWE update) with
    the new stack to ensure that there have been no regressions.

    The following describes which generations we will test to mitigate
    unintentional hardware regressions:
    https://documentation.ubuntu.com/sru/en/latest/reference/exception-Intel-Graphics-Updates/#hardware-support

    [ Where problems could occur ]

    An HWE update contains a lot of new changes. On an LTS, it is
    likely that the version will not change between HWE updates, which means
    there will be substantial diffs, especially on projects as active as the
    media driver and compute runtime. With the bugfixes, refactors, and new
    features introduced in the meantime, we may be trading known issues for
    new issues. When dealing with packages like these, we could see serious
    bugs, but we have to balance that knowledge with the knowledge that
    we will only promote well-tested configurations.

    [ Other Info ]

    Packages to update:

    $packagename version $version to $release

    $packagename2 version $version2 to $release

    $packagename3 version $version3 to $release

    Any known test regressions should be listed below:

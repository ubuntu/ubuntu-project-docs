.. _crash_and_makedumpfile_sru_exception:

Crash and Makedumpfile SRU Exception
====================================

This document describes the policy for introducing new upstream- and
micro- releases of the crash and makedumpfile packages into Ubuntu
releases. Crash typically has two releases per calendar year, around
April and November. This can include minor (8.0.4 -> 8.0.5) and major
version updates (7.3.0 -> 8.0.0), and both scenarios should be covered
under the testing plan detailed in this page. Makedumpfile also follows
similar release cadence.

.. _about_makedumpfile:

About makedumpfile
------------------

Makedumpfile is a user space tool which is run by kdump-tools inside the
kdump kernel to compress the kernel dump. This compressed dump can be
read by tools such as crash.

Upstream resources:

- `Porject page <https://github.com/makedumpfile/makedumpfile>`_
- `Mailing List Archive <https://lists.infradead.org/pipermail/kexec/>`_

.. _about_crash:

About crash
-----------

Crash is a self-contained tool that can be used to analyze kernel memory
dumps (e.g. created by makedumpfile). It's also able to investigate live
systems through e.g. /proc/kcore.

Upstream resources:

- `Project page <https://crash-utility.github.io/>`_
- `Upstream changelog <https://crash-utility.github.io/crash.changelog.html>`_
- `Extensions modules <https://crash-utility.github.io/extensions.html>`_
- `Contribution Guidelines <https://github.com/crash-utility/crash/wiki>`_

.. _rationale_for_the_exception:

Rationale for the exception
---------------------------

Crash is extremely helpful for analysis and RCA of kernel issues.
Particularly for HWE kernels, new features could be introduced that
change the memory structures being parsed by crash. Keeping crash
updated to latest stable versions keeps compatibility for older kernels,
while allowing LTS releases to work with kernel dumps from newer Ubuntu
versions.

Makedumpfile is responsible for generating the compressed memory dump
from /proc/vmcore which can be consumed by tools such as crash[1]. The
kdump-tools package uses makedumpfile by default[2]. Since the structure
and layout of /proc/vmcore is dependent on the kernel, updates to
makedumpfile are necessary to ensure proper functionality.

Furthermore, the release of both of these projects are disconnected from
upstream and the Ubuntu release cycles. It is possible the the upstream
projects have the right support for a new kernel release, but there may
not be a release for some time. In such situations, SRU of specific
patches from the upstream crash and makedumpfile projects may be
required.

.. _upstream_policy_enforces_backwards_compatibility:

Upstream policy enforces backwards compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Although crash and makedumpfile do not seem to have a formal release
policy documented, upstream maintainers take extensive care so that
these tools always remain backwards-compatible. This ensures minimal
breakage and greater stability of these tools. Updates include bug fixes
and patches to ensure the tool can continue analyzing memory structures
of newer kernels. For crash, is documented in the `Contribution
Guidelines <https://github.com/crash-utility/crash/wiki>`_.
Makedumpfile maintains a support matrix of the package against previous
kernel versions as documented in the `upstream
repository <https://github.com/makedumpfile/makedumpfile>`_.

.. _microreleases_are_not_restricted_to_bug_fixes:

Microreleases are not restricted to bug fixes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As there doesn't seem to be a formal release policy documented, there's
no criteria of what can be included in upstream releases. Historically,
this has involved compatibility patches to new kernels and
architectures, regression fixes, cleanup commits, as well as minor
quality-of-life features. Considering a new release is not necessarily
restricted to bug fixes only, we can't always push an upstream release
to Ubuntu as per the `New upstream
microreleases <https://canonical-sru-docs.readthedocs-hosted.com/en/latest/reference/requirements/#new-upstream-microreleases>`_
section of the SRU docs. The upstream project also doesn't seem to have
a formal testing procedure documented, which we hope to cover for Ubuntu
more extensively through the test plans below.

.. _sru_process:

SRU Process
-----------

For new releases of the crash utility, the following criteria need to be
validated and documented in a public Launchpad bug:

-  Crash must be able to correctly open a makedumpfile compressed image of the system
-  Crash must be able to correctly execute against the generic and HWE kernel

Kernel crash dumps should be captured with default parameters for a
given Ubuntu release, as this will cover the more general scenario for
the tool. Alternatively and with appropriate justification from the SRU
requester, crash can be validated against a live system image as well.

The SRU should ensure all the supported architectures are working
correctly with a new crash version. Likewise, we're only concerned that
crash is able to open and parse kernel dumps correctly, extensions or
specific crash commands **are not going to be covered** with this test.

The following steps can be followed to test a new version of crash and/or
makedumpfile package:

1. Install the kernel's debug symbols packages
2. Install the updated crash/makedumpfile packages as well as `kdump-tools` and `kexec-tools` packages
3. Ensure the system is ready to capture the dump using `sudo kdump-config show`. Reboot if necessary.
4. Trigger kernel crash (i.e `echo c | sudo tee /proc/sysrq-trigger`)
5. Once the machine reboots, see if crash is able to load the dumpfile against kernel's debug symbols file (i.e `crash <DEBUG_SYM_FILE> <DUMP_FILE>`.

.. _regression_testing:

Regression Testing
~~~~~~~~~~~~~~~~~~

The targets above should cover most of the crash users, but it does
leave out specific flavors and other derivative kernels like
*linux-aws*, *linux-azure*, etc. Kernel team has integrated kdump
testing within their SRU Regression Testing suite and hence would be
running this test against all of the prepared kernel once per kernel SRU
cycle. This testing is comprehensive and includes all the supported
architectures.

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be requested following the regular SRU process, with
additional notes about the validation steps described above. A suggested
template for new releases covered under the SRU exception can be found
below.

Template
~~~~~~~~

New Upstream release for *crash* and/or *makedumpfile*

[Impact]

This new release contains important bug fixes and compatibility patches
for [...].

[Upstream Changes]

TODO: link to upstream changelog, making note of any significant
commits like compatibility to new kernel versions or new architectures

[Test Plan]

The test plan from
`CrashMakedumpfileUpdates <https://github.com/ubuntu/ubuntu-project-docs/blob/main/docs/SRU/reference/exception-CrashMakedumpfile-Updates.rst>`_
was followed. Attached are console logs for each covered kernel version
and architecture.

[Where problems could occur]

TODO: document any potential issues or risky patches, as per regular
SRU process

[Other Info]

TODO: fill out any relevant information to the test plan or the new
release

Checklist
~~~~~~~~~
-  Ensure crash can open dumps for the GA kernel on supported architectures
-  Ensure crash can open dumps for the HWE kernel on supported architectures
-  Attach or link to logs confirming above tests
-  Update the list of previous crash updates under this SRU Exception below

.. _previous_crash_updates_bugs:

Previous crash updates bugs
---------------------------

- 

References
----------

[1]
https://manpages.debian.org/unstable/makedumpfile/makedumpfile.8.en.html

[2]
https://manpages.debian.org/unstable/kdump-tools/kdump-tools.5.en.html

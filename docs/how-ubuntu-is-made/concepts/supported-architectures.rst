.. _supported-architectures:

Supported architectures
=======================

Packages are typically built for each of several :term:`architectures <Architecture>`.
These are officially supported and maintained by the Ubuntu project.
:term:`Canonical` provides server resources to build, store and distribute packages and installation media for them, and the core development team is responsible for their upkeep.

Build failures on these architectures are considered serious bugs.
Each official Ubuntu release and update includes appropriate support for these architectures.

.. list-table::
    :header-rows: 1

    * - Identifier
      - Alternative Architecture Names
      - Endianness
    * - ``amd64``
      - x86-64, x86_64, x64, AMD64, Intel 64
      - :term:`Little-Endian`
    * - ``arm64``
      - ARM64, ARMv8, AArch64
      - :term:`Little-Endian`
    * - ``armhf``
      - ARM32, ARMv7, AArch32, ARM Hard Float
      - :term:`Little-Endian`
    * - ``ppc64el``
      - PowerPC64 Little-Endian
      - :term:`Little-Endian`
    * - ``s390x``
      - IBM System z, S/390, S390X
      - :term:`Big-Endian`
    * - ``riscv64``
      - RISC-V (64-bit)
      - :term:`Little-Endian`

The ``i386`` partial port
-------------------------

A small number of packages are built for the ``i386`` architecture
(i.e. using 32-bit Intel / AMD or ``IA32`` instructions).  There is no
kernel, installer or bootloader for ``i386`` so these packages can
only be installed on an ``amd64`` host as a multi-arch supplementary
architecture. The main reason these are provided is to run old legacy
binaries that cannot be rebuilt as ``amd64`` native applications
(mostly games).

Architecture baselines
----------------------

For each architecture above, there is a *baseline* which is the oldest or least capable CPU that can be used to run Ubuntu of that architecture:

.. list-table::
    :header-rows: 1

    * - Architecture
      - Baseline
    * - ``amd64``
      - No extensions beyond the original 64-bit AMD / Intel CPUs
    * - ``arm64``
      - ARMv8-A with no optional extensions. VFPv4 and NEON are assumed but ARMv8.1-A are not.
    * - ``armhf``
      - ARMv7 with VFPv3-D16 floating point. NEON is not guaranteed.
    * - ``ppc64el``
      - Ubuntu 16.04 through 21.10 assumed a POWER8 or newer CPU.
        Ubuntu 22.04 and newer assume POWER9 or newer.
    * - ``s390x``
      - Ubuntu 16.04 through 19.10 assumed zEC12 or newer.
      - Ubuntu 20.04 thought 25.10 assumed z13 or newer.
        Ubuntu 26.04 and newer assume z15.
    * - ``riscv64``
      - RISC-V (64-bit)
      - Ubuntu 20.04 through 25.04 assumed the RVA20 profile.
        Ubuntu 25.10 and newer assume the RVA23 profile.

Architecture variants
---------------------

To be able to assume features of more modern CPUs without dropping support for older machines, Ubuntu 25.10 introduced the concept of :term:`Architecture Variant`. This allows packages to be built for given :term:`architecture <Architecture>` (remember, architecture really means :term:`ABI`) multiple times, each build assuming different CPU features.

The only variant supported in Ubuntu so far is ``amd64v3`` which assumes the ``x86-64-v3`` microarchiture level. This assumes a number of instructions that have been added in the years since the first amd64 CPUs, including AVX2, FMA, BMI2 and others. Most amd64-compatible processors produced since about 2013 support this.


Further reading
---------------

- `Statement on 32-bit i386 packages for Ubuntu 19.10 and 20.04 LTS <https://canonical.com/blog/statement-on-32-bit-i386-packages-for-ubuntu-19-10-and-20-04-lts>`_
- `Ubuntu Downloads <https://ubuntu.com/download>`_
- `Endianness <https://en.wikipedia.org/wiki/Endianness>`_

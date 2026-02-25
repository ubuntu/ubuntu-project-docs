.. _supported-architectures:

Supported architectures
=======================

Packages are typically built for each of several architectures.
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


Other architectures
-------------------

:term:`Ubuntu` doesn't currently support any other :term:`architectures <Architecture>`. This doesn't mean that Ubuntu won't run on other architectures -- in fact it is entirely possible for it to install without a problem, because Ubuntu is based on the :term:`Debian` distribution, which has support for eight additional architectures (see `Debian Supported Architectures <https://wiki.debian.org/SupportedArchitectures>`_).

However, if you run into problems, the Ubuntu community may not be able to help you.


Further reading
---------------

- `Statement on 32-bit i386 packages for Ubuntu 19.10 and 20.04 LTS <https://canonical.com/blog/statement-on-32-bit-i386-packages-for-ubuntu-19-10-and-20-04-lts>`_
- `Ubuntu Downloads <https://ubuntu.com/download>`_
- `Endianness <https://en.wikipedia.org/wiki/Endianness>`_

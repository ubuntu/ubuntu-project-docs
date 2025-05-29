(mir-exceptions-oem)=
# OEM exceptions

Starting in 20.04, Ubuntu Desktop ISOs will support installing hardware-specific
meta-packages if the machine being installed on has a corresponding enablement
package available.

Ubiquity will use `ubuntu-drivers` to discover if an enablement package exists.
The user will then be asked if they want to install the package, and it will be
installed if they say "yes".

Installing the package implies that it is on the ISO image. Packages on the ISO
image must be in main. We expect there to be several of these at any given
moment. Going through the full formal MIR process for each package is likely to
be too much of a burden on the OEM / Desktop / MIR teams, and so here we
propose a streamlined process.

**These packages enable an additional APT archive.**

This is the subject of a
[discussion with the Technical Board](https://lists.ubuntu.com/archives/technical-board/2020-January/002478.html).
See [OEM Archive](https://wiki.ubuntu.com/OEMArchive) for further details.

## Process

If packages meet the subscriber, naming and content requirements defined below,
they may be promoted or *NEW*-ed directly into main without recourse to the MIR
team. No future update may cause the package to not follow the requirements.

Since these uploads usually target active releases it is an SRU process to
handle them, but it also requires {term}`AA` privileges for the NEW queue
handling. Which means it can either only be processed by members being in the
intersection of [SRU members](https://launchpad.net/~ubuntu-sru/+members) and
[Archive Admin members](https://launchpad.net/~ubuntu-archive/+members).
Or, following the joint processing as mentioned in
[SRU uploads hitting the new queue](https://documentation.ubuntu.com/sru/en/latest/howto/special/#sru-uploads-hitting-the-new-queue).

When uploaded to `-unapproved` the SRU team will see it, but only those that
also are Archive Admins can process it. For awareness, the uploader is
encouraged to subscribe `ubuntu-sru`, but not `ubuntu-archive` to the related bug.

The Archive Admins being also SRU members can then use the
`oem-metapackage-mir-check` script from `lp:ubuntu-archive-tools` to view a
debdiff against a reference package in the Ubuntu archive. If any of the
differences are not covered in this document or trivially understandable, go
back to the uploader.

## Subscriber

As the packages are going to be in main, they need to have an "owning" team
that is subscribed to the bugs for the package in Launchpad. The team
[~canonical-mainstream](https://launchpad.net/~canonical-mainstream) must be
subscribed to the package before it is promoted.

## Naming

The source and binary packages must follow the form `oem-<product name>-meta`.

## Content

The packages must follow the following structure. They must be otherwise empty.

```
.
├── oem-foo-meta.list
└── debian
        ├── changelog
        ├── control
        ├── copyright
        ├── install
        ├── modaliases
        ├── rules
        └── source
            └── format
```

`oem-foo-meta.list` is installed into `/etc/apt/sources.list.d/` and enables
the OEM archive. **No other files may be installed by the metapackage itself.**
If there is a case for installing other files, the package loses this MIR
exception and must go through the normal process. The control file should look
similar to:

```
Source: oem-foo-meta
Section: misc
Priority: optional
Maintainer: Commercial Engineering <commercial-engineering@canonical.com>
Build-Depends: debhelper-compat (= 12), dh-modaliases
Standards-Version: 4.5.0

Package: oem-foo-meta
Architecture: all
Depends: ${misc:Depends},
        ubuntu-oem-keyring,
        fwupd,
        xserver-xorg-hwe-20.04,
XB-Modaliases: ${modaliases}
Description: hardware support for foo
 This is a metapackage for foo. It installs packages needed to support this
 hardware fully.
```

The list of dependencies may vary slightly. As usual, since they will be on the
ISO these meta-packages may depend on **packages in main only**. It is intended
that the OEM archive offers upgrades to the metapackage itself if it needs to
pull in other packages that can’t be on the ISO (this is the subject of the TB
discussion).

The control file can optionally specify a field `XB-Ubuntu-OEM-Kernel-Flavour`
to select a different kernel. Acceptable values are `default` (use the
distribution's default kernel, i.e. generic or HWE) and `oem`. If this field
isn't specified, `oem` is assumed.

The rules file should be minimal:

```
%:
    dh $@ --with modaliases
```

so that the package is auditable. It must use `dh-modalias` to fill in the
`XB-Modalias` field.

`debian/{oem-foo-meta.,}modaliases` contains the modaliases that will eventually
end up in `XB-Modaliases` and represents the hardware set that this metapackage
is designed to work with.

## Known modaliases matching patterns

More information about modaliases in OEM meta packages.

Matching types:

```
- Matching by PCI ID
  - Modalias convention
    - pci:*sv0000${OEM_ID}sd0000${BIOS_ID}bc0Csc05*
    - OEM_ID
      - PCI Vendor ID of OEM (4 hexadecimal ASCII characters).
    - BIOS_ID
      - The unique ID of OEM System ID (4 hexadecimal ASCII characters).
    - bc0Csc05
      - bc (base class) 0C and sc (sub class) 05, matching SMBus (System Management Bus).
      - The purpose of comparing the SMBus is to avoid some add-on cards with incorrect subsystem IDs, which can cause the system to install unexpected platform meta-packages. E.g. A thunderbolt card which has subsystem ID “0739”, it makes the system installed an unexpected platform meta package for BIOS_ID “0739”.
  - Example of modaliases
    - E.g. “pci:*sv00001028sd0000084Abc0Csc05*”
    - sv 00001028 (subvendor)
    - sd 0000084A (subdevice)
  - OEM platforms using this matching type
    - Dell, HP
- Matching by DMI string
  - Modaliase convention
    - dmi:*bvn${OEM_NAME}:bvr${BIOS_ID}:pvr${PRODUCT_NAME}*
    - OEM_NAME:
      - DMI_BIOS_VENDOR
    - BIOS_ID:
      - DMI_BIOS_VERSION
      - The unique ID of the OEM platforms.
    - PRODUCT_NAME:
      - DMI_PRODUCT_VERSION
  - Example of modaliases
    - dmi:*bvnLENOVO:bvrR29*:pvrThinkPad*
  - OEM platform using this matching type
    - Lenovo
```

## Known issue

* [LP#1869867](https://bugs.launchpad.net/ubuntu/+source/oem-qemu-meta/+bug/1869867) gives
  `package-installs-apt-sources` lintian error


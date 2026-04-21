(openjdk-packaging)=
# `openjdk` packaging

How to update, package, and maintain versions of {pkg}`openjdk` in Ubuntu.

## Introduction

The [upstream OpenJDK project](https://openjdk.org/) follows a strict [release cadence](https://openjdk.org/projects/jdk-release-cadence/): a new feature release is published every six months, with quarterly Critical Patch Updates (CPU) for security and stability.

In Ubuntu, we currently maintain the following versions:
* **Long Term Support (LTS):** 11, 17, 21, and 25.
* **Interim:** The current latest feature release.

### Maintenance

OpenJDK packaging is generally maintained as a shared effort with Debian on [Salsa](https://salsa.debian.org/openjdk-team/openjdk). A notable exception is OpenJDK 11, which is maintained in Ubuntu through the `openjdk-lts` package.

### Help and Communication

If you need assistance or want to participate in toolchain-related discussions, you can reach out in the [Ubuntu Toolchains](https://matrix.to/#/!gsGkkvuHZNBLerIqwJ:ubuntu.com?via=ubuntu.com&via=matrix.org) Matrix channel.

```{toctree}
:maxdepth: 1

Debian Repository <openjdk-debian-repository>
Update OpenJDK <update-openjdk>
Patch OpenJDK <patch-openjdk>
Build OpenJDK <build-openjdk>
Test OpenJDK <test-openjdk>
Backport OpenJDK <backport-openjdk>
Version Strings <openjdk-version-strings>

```
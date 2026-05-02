(openjdk-debian-repository)=
# OpenJDK Debian repository

OpenJDK packaging code is maintained on [Salsa](https://salsa.debian.org/openjdk-team/openjdk).

## Repository Access

To contribute to OpenJDK packaging, clone the repository from Salsa:

```bash
$ git clone https://salsa.debian.org/openjdk-team/openjdk.git
```

## Branches

The repository maintains separate branches for each OpenJDK release. Branches are named using the `openjdk-<version>` pattern:

*   **`openjdk-11`, `openjdk-17`, `openjdk-21`, `openjdk-25`**: Track the respective Long Term Support (LTS) releases.
*   **`master`**: Tracks the mainline [openjdk/jdk](https://github.com/openjdk/jdk) repository and is used for the current development version.

Please tag your merge requests with the intended branches, e.g., `[openjdk-11, ..., master]`, to indicate if a change should be applied across multiple supported versions.


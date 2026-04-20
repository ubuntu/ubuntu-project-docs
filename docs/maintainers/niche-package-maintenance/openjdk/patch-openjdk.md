(patch-openjdk)=
# Patch OpenJDK

All patches applied to OpenJDK should follow the naming convention:
- Upstream patches: `jdk-<bug-number>[-proposed].diff`. Use `-proposed` suffix for patches that are not yet applied in the upstream repository, e.g. not backported yet.
- Debian and Ubuntu-specific patches: `<name>.diff`

All new patches should have DEP-3 headers.

Ensure that every patch that updates the upstream source tree is submitted upstream.

## OpenJDK developer guide

Please use the [OpenJDK developer guide](https://openjdk.org/guide/) when working with the upstream source tree.

## OpenJDK tests

OpenJDK uses the [jtreg](https://openjdk.org/jtreg/) testing framework. See {ref}`test-openjdk` for details on
running the test suite against both a locally built source tree and an installed package.

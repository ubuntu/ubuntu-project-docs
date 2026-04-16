(patch-openjdk)=
# Patch OpenJDK

All patches applied to OpenJDK should follow the naming convention:
- Upstream patches: `jdk-<bug-number>[-proposed].diff`. Use `-proposed` suffix for patches that are not yet applied in the upstream repository, e.g. not backported yet.
- Debian and Ubuntu-specific patches: `<name>.diff`

All new patches should have DEP-3 headers.

Ensure that every patch that updates upstream source tree is submitted upstream.

## OpenJDK developer guide

Please use OpenJDK developer guide[1] when working with upstream source tree.

## OpenJDK tests

OpenJDK uses jtreg[2] testing framework.

[1] https://openjdk.org/guide/
[2] https://openjdk.org/jtreg/



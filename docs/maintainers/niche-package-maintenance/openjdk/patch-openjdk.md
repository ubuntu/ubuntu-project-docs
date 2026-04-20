(patch-openjdk)=
# Patch OpenJDK

All patches applied to OpenJDK should follow the naming convention:
- Upstream patches: `jdk-<bug-number>[-proposed].diff`. Use `-proposed` suffix for patches that are not yet applied in the upstream repository, e.g. not backported yet.
- Debian and Ubuntu-specific patches: `<name>.diff`

All new patches should have DEP-3 headers.

Ensure that every patch that updates the upstream source tree is submitted upstream.

## OpenJDK developer guide

Please use the [OpenJDK developer guide](https://openjdk.org/guide/) when working with the upstream source tree.

## Example: adding an upstream patch

This example walks through the process of backporting an upstream fix into the
Debian/Ubuntu package.

### 1. File or find the bug report

All upstream OpenJDK bugs are tracked in the
[JDK Bug System](https://bugs.openjdk.org/). Search for an existing report or
file a new one. Note the bug ID (e.g. `JDK-8312488`).

### 2. Find or create the fix

Fixes are submitted as pull requests against the
[openjdk/jdk](https://github.com/openjdk/jdk/) repository.

### 3. Extract the patch

Download the commit as a patch. For example:

```bash
$ wget -O debian/patches/jdk-8312488.patch \
    https://github.com/openjdk/jdk/commit/78a8a99d990dcc0b77c096bb2ca2c1bb86462e3f.patch
```

The file name must follow the naming convention:
`jdk-<bug-number>.patch` for merged fixes, or `jdk-<bug-number>-proposed.patch`
for fixes not yet merged upstream.

### 4. Add DEP-3 headers

Add the required [DEP-3](https://dep-team.pages.debian.net/deps/dep3/) headers
at the top of the patch file:

```
Description: tools/jpackage/share/AppLauncherEnvTest.java fails with dynamically linked libstdc++
 The generated image contains libjpackageapplauncheraux.so that
 contains a destructor function dcon(). It calls already disposed
 logger, causing a crash.
Author:  Vladimir Petko <vpetko@openjdk.org>
Origin: upstream, https://github.com/openjdk/jdk/commit/78a8a99d990dcc0b77c096bb2ca2c1bb86462e3f
Bug: https://bugs.openjdk.org/browse/JDK-8312488
Reviewed-By: asemenyuk, almatvee
Last-Update: 2024-07-18
---
```

The key fields are:

| Field | Description |
| :--- | :--- |
| `Description` | Short summary on the first line, followed by an indented longer explanation. |
| `Author` | The commit author. |
| `Origin` | `upstream, <commit-url>` for merged fixes, or `other, <pr-url>` for proposed fixes. |
| `Bug` | Link to the JDK Bug System entry. |
| `Last-Update` | Date in `YYYY-MM-DD` format. |

### 5. Add the patch to the series

Append the patch file name to `debian/patches/series`:

```bash
$ echo jdk-8312488.patch >> debian/patches/series
```

Then verify that the patch applies cleanly:

```bash
$ quilt push -a
```

## OpenJDK tests

OpenJDK uses the [jtreg](https://openjdk.org/jtreg/) testing framework. See {ref}`test-openjdk` for details on
running the test suite against both a locally built source tree and an installed package.

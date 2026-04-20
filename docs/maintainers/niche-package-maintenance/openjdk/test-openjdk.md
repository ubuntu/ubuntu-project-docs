(test-openjdk)=
# Test OpenJDK

OpenJDK uses the [jtreg](https://openjdk.org/jtreg/) testing framework for its comprehensive test suite.
The tests are integrated into the Debian/Ubuntu package autopkgtest via wrapper
scripts in `debian/tests/`.

## Prerequisites

Install `jtregN` before running any tests, e.g. for OpenJDK 21 and later:

```bash
$ sudo apt install jtreg8
```

OpenJDK 11 and 17 use `jtreg7`.

The test scripts require the following environment variables to be set:

| Variable | Description |
| :--- | :--- |
| `AUTOPKGTEST_TMP` | Writable directory used as a working area (e.g. for problem lists and JTwork output). |
| `AUTOPKGTEST_ARTIFACTS` | Directory where test reports and artifacts are saved. |
| `JDK_TO_TEST` | Path to the JDK image under test. Defaults to the installed JDK (e.g. `/usr/lib/jvm/java-21-openjdk-amd64`). |
| `BOOTJDK_HOME` | Path to the boot JDK. Defaults to `JDK_TO_TEST` if not set. |

## Testing the locally built source tree

After building the source tree (e.g. with `dpkg-buildpackage -b`), use the
per-subsystem wrapper scripts from the root of the source tree. Each script
runs tier1 and tier2 tests for its subsystem, excluding known-failing tests.

Set up the environment first:

```bash
export AUTOPKGTEST_TMP=$(mktemp -d)
export AUTOPKGTEST_ARTIFACTS=$(mktemp -d)
export JDK_TO_TEST=$(pwd)/build/images/jdk
```

Then run one or more of the following:

```bash
# HotSpot VM tests
debian/tests/hotspot

# Core JDK library tests (requires a virtual display; Xvfb is started automatically)
debian/tests/jdk

# JAXP (XML processing) tests
debian/tests/jaxp

# Langtools (javac, javadoc, etc.) tests
debian/tests/langtools
```

Each script:

- Generates a combined exclusion list from the upstream `ProblemList.txt` and the
  Debian-specific `debian/tests/problems.csv` via `write-problems.sh`.
- Invokes `debian/tests/jtreg-autopkgtest.sh` with `-dir:test/<subsystem>` and
  the pre-built native test binaries from `build/images/test/<subsystem>/jtreg/native`.
- Retries failed or errored tests up to three times to distinguish genuine failures
  from flaky tests.
- Saves `.jtr` result files and any `hs_err_pid` crash logs to `AUTOPKGTEST_ARTIFACTS`.

```{note}
The `jdk` script starts `Xvfb` automatically via `debian/tests/start-xvfb.sh` to
provide a graphical display for tests that require one.
```

## Testing the installed package

Use the `-autopkgtest.sh` variants to test the JDK installed from the package
rather than a locally built image. These scripts resolve the JDK path automatically
from `/usr/lib/jvm/` and use the native test binaries shipped in the
`openjdk-<N>-jdk` testsuite directory.

```bash
export AUTOPKGTEST_TMP=$(mktemp -d)
export AUTOPKGTEST_ARTIFACTS=$(mktemp -d)

# Run HotSpot tests against the installed JDK (tier1 only by default)
debian/tests/hotspot-autopkgtest.sh

# Run JDK tests against the installed JDK (tier1 only by default; starts Xvfb)
debian/tests/jdk-autopkgtest.sh
```

Both scripts skip tests listed in `debian/tests/skip-large-autopkgtest.txt` in
addition to the standard problem list, to avoid tests that exceed typical
autopkgtest resource limits.

You can pass additional `jtreg` arguments to override the defaults:

```bash
# Run only a single test
debian/tests/hotspot-autopkgtest.sh -dir:test/hotspot/jtreg Test.java
```

```{note}
Tests are skipped (exit code 77) on architectures that use the Zero interpreter,
since Hotspot-specific tests are not meaningful there.
```

[1] https://openjdk.org/jtreg/

(test-openjdk)=
# Test OpenJDK

OpenJDK uses the `jtreg` testing framework for its comprehensive suite of tests. In the Ubuntu package, these tests are integrated into the package autopkgtest.

The scripts are generated from `debian/tests/*.in` files.
Unpack the openjdk source tree and run `make -f debian-rules update-control-files` to regenerate.

## Core Scripts

- **`jtreg-autopkgtest.sh`**: The primary wrapper for `jtreg`. It handles the execution logic, including retrying failed tests to identify flakiness and collecting diagnostic artifacts (like `.jtr` files and `hs_err` logs) into the `AUTOPKGTEST_ARTIFACTS` directory.
- **`jdk-autopkgtest.sh`**: Runs the core JDK library tests (located in `test/jdk`). It sets up the test environment, including a virtual display for GUI tests.
- **`hotspot-autopkgtest.sh`**: Runs the Hotspot virtual machine tests (located in `test/hotspot`).
- **`start-xvfb.sh`**: A helper script that starts `Xvfb` and `xfwm4` to provide a graphical environment for tests that require a `DISPLAY`.

### Managing Failing Tests

Because OpenJDK has a massive testsuite, some tests may fail due to environment limitations or known bugs.

- **`problems.csv`**: A Debian-specific database of tests that should be skipped on certain architectures or Ubuntu releases.
- **`write-problems.sh`**: This script combines upstream `ProblemList.txt` files with the local `problems.csv` to generate a unified exclusion list passed to `jtreg` via the `-exclude` option.
- **`skip-large-autopkgtest.txt`**: A list of tests that are known to be too large or time-consuming for the standard autopkgtest infrastructure.

## Running Tests Locally

You can run these tests locally using the `autopkgtest` tool. For example, to run the JDK tests:

```bash
$ autopkgtest openjdk/ -- qemu <path-to-image>
```

To run a specific test case using the wrapper scripts manually (assuming you are in the source tree and have the package installed):

```bash
$ export AUTOPKGTEST_TMP=$(mktemp -d)
$ export AUTOPKGTEST_ARTIFACTS=$(mktemp -d)
$ debian/tests/jdk-autopkgtest.sh <test-name>
```

.. _automatic-package-testing-autopkgtest:

Automatic package testing: autopkgtest
======================================

The :term:`DEP-8` specification defines how to integrate automatic testing into packages. To integrate a test into a package, add the following files:

:file:`debian/tests/control`
: Specifies the requirements for the testbed.

:file:`debian/tests/`
: The tests.


Testbed requirements
--------------------

In ``debian/tests/control`` you specify what to expect from the testbed. So 
for example you list all the required packages for the tests, if the testbed
gets broken during the build or if ``root`` permissions are required. The 
DEP 8 specification lists all available options.

Below we are having a look at the ``glib2.0`` source package. In a very 
simple case the file would look like this::

        Tests: build
        Depends: libglib2.0-dev, build-essential

For the test in ``debian/tests/build`` this would ensure that the packages 
``libglib2.0-dev`` and ``build-essential`` are installed.

.. note:: You can use ``@`` in the ``Depends`` line to indicate that you want
        all the packages installed which are built by the source package in
        question.


The actual tests
----------------

The accompanying test for the example above might be:

.. code-block:: sh

        #!/bin/sh
        # autopkgtest check: Build and run a program against glib, to verify that the
        # headers and pkg-config file are installed correctly
        # (C) 2012 Canonical Ltd.
        # Author: Martin Pitt <martin.pitt@ubuntu.com>

        set -e

        WORKDIR=$(mktemp -d)
        trap "rm -rf $WORKDIR" 0 INT QUIT ABRT PIPE TERM
        cd $WORKDIR
        cat <<EOF > glibtest.c
        #include <glib.h>

        int main()
        {
            g_assert_cmpint (g_strcmp0 (NULL, "hello"), ==, -1);
            g_assert_cmpstr (g_find_program_in_path ("bash"), ==, "/bin/bash");
            return 0;
        }
        EOF

        gcc -o glibtest glibtest.c `pkg-config --cflags --libs glib-2.0`
        echo "build: OK"
        [ -x glibtest ]
        ./glibtest
        echo "run: OK"

Here a very simple piece of C code is written to a temporary directory. Then 
this is compiled with system libraries (using flags and library paths as 
provided by `pkg-config`). Then the compiled binary, which just exercises some
parts of core glib functionality, is run.

While this test is very small and simple, it covers quite a lot: that your -dev
package has all necessary dependencies, that your package installs working
pkg-config files, headers and libraries are put into the right place, or that
the compiler and linker work. This helps to uncover critical issues early on.


Executing the test
------------------

While the test script can be easily executed on its own, it is strongly
recommended to actually use ``autopkgtest`` from the ``autopkgtest`` package for
verifying that your test works; otherwise, if it fails in the Ubuntu Continuous
Integration (CI) system, it will not land in Ubuntu.  This also avoids cluttering
your workstation with test packages or test configuration if the test does
something more intrusive than the simple example above.

The `README.running-tests <running_tests_>`_ documentation explains all
available testbeds (schroot, LXD, QEMU, etc.) and the most common scenarios how
to run your tests with ``autopkgtest``, e. g. with locally built binaries, locally
modified tests, etc.

The Ubuntu CI system uses the QEMU runner and runs the tests from the packages
in the archive, with ``-proposed`` enabled. To reproduce the exact same
environment, first install the necessary packages::

        sudo apt install autopkgtest qemu-system qemu-utils autodep8

Now build a testbed with::

        autopkgtest-buildvm-ubuntu-cloud -v

(Please see its manpage and ``--help`` output for selecting different releases,
architectures, output directory, or using proxies). This will build e. g.
``adt-trusty-amd64-cloud.img``.

Then run the tests of a source package like ``libpng`` in that QEMU image::

        autopkgtest libpng -- qemu adt-trusty-amd64-cloud.img

The Ubuntu CI system runs packages with only selected packages from
``-proposed`` available (the package which caused the test to be run); to
enable that, run::

        autopkgtest libpng -U --apt-pocket=proposed=src:foo -- qemu adt-release-amd64-cloud.img

or to run with all packages from ``-proposed``::

        autopkgtest libpng -U --apt-pocket=proposed -- qemu adt-release-amd64-cloud.img

The ``autopkgtest`` manpage has a lot more valuable information on other
testing options.


Further examples
----------------

This list is not comprehensive, but might help you get a better idea of how
automated tests are implemented and used in Ubuntu.

* The `libxml2 tests <libxml2_>`_ are very similar. They also run a test-build of a 
  simple piece of C code and execute it.
* The `gtk+3.0 tests <gtk3_>`_ also do a compile/link/run check in the "build" test. 
  There is an additional "python3-gi" test which verifies that the GTK 
  library can also be used through introspection.
* In the `ubiquity tests <ubiquity_>`_ the upstream test-suite is executed.
* The `gvfs tests <gvfs_>`_ have comprehensive testing of their functionality and
  are very interesting because they emulate usage of CDs, Samba, DAV and
  other bits.


Ubuntu infrastructure
---------------------


Packages which have ``autopkgtest`` enabled will have their tests run whenever
they get uploaded or any of their dependencies change. The output of
`automatically run autopkgtest tests <jenkins_>`_ can be viewed on the web and is 
regularly updated.

Debian also uses ``autopkgtest`` to run package tests, although currently only
in schroots, so results may vary a bit. Results and logs can be seen on
http://ci.debian.net. So please submit any test fixes or new tests to Debian as
well.


Getting the test into Ubuntu
----------------------------

The process of submitting an autopkgtest for a package is similar to :ref:`fixing a bug in Ubuntu <how-to-fix-a-bug-in-a-package>`:

#. Run ``bzr branch ubuntu:<packagename>``,
#. Edit ``debian/control`` to enable the tests,
#. Add the ``debian/tests`` directory,
#. Write the ``debian/tests/control`` based on the :term:`DEP-8` specification,
#. Add your test case(s) to ``debian/tests``,
#. Commit your changes, push them to Launchpad, propose a merge, and get it reviewed like any other improvement in a source package.


What you can do
---------------

The Ubuntu Engineering team maintains a `list of required test-cases <requiredtests_>`_ with packages that need tests in different categories. Use it to find examples of tests and assign them to yourself.

For help with resolving problems, join the `<#devel:ubuntu.com_>`_ Matrix channel to get in touch with developers.


Further reading
---------------

* `Autopkgtest - Defining tests for Debian packages <https://salsa.debian.org/ci-team/autopkgtest/blob/master/doc/README.package-tests.rst>`_

.. wokeignore:rule=master
.. _libxml2: https://git.launchpad.net/ubuntu/+source/libxml2/tree/debian/tests
.. _gvfs: https://git.launchpad.net/ubuntu/+source/gvfs/tree/debian/tests
.. _gtk3: https://git.launchpad.net/ubuntu/+source/gtk+3.0/tree/debian/tests
.. _ubiquity: https://git.launchpad.net/ubiquity/tree/debian/tests
.. _jenkins: http://autopkgtest.ubuntu.com/
.. wokeignore:rule=master
.. _running_tests: https://salsa.debian.org/ci-team/autopkgtest/blob/master/doc/README.running-tests.rst
.. _requiredtests: https://wiki.ubuntu.com/QATeam/RequiredTests

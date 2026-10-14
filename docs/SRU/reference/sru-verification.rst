.. _reference-sru-verification:

SRU verification
----------------

SRU verification is part of the QA process for an SRU, and is required for each bug associated with the SRU.

Perform the test plan
^^^^^^^^^^^^^^^^^^^^^

1. Access your testing environment (virtual machine, container, etc.).
2. :ref:`Enable the proposed pocket<reference-enable-proposed>`.
3. Install the new package from ``-proposed``:

.. code:: bash

    sudo apt install -t <series>-proposed <package>

3. Confirm that the version from ``-proposed`` is now installed:

.. code:: bash

    apt policy <package>

4. Perform the test plan described in the ``[Test Plan]`` section of the bug description.

Share test results
^^^^^^^^^^^^^^^^^^

1. Leave a comment on the bug with the result of your test, noting the package version you tested. Preferably, share the output of ``apt policy`` from the test environment.
2. Update the bug tags. If the test was successful, change the ``verification-needed-<series>`` tag to ``verification-done-<series>``. If the test was not successful, change the tag to ``verification-failed-<series>``.

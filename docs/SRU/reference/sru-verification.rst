.. _reference-sru-verification:

SRU verification
----------------

.. include:: /SRU/_sru-series.rst

SRU verification is part of the QA process for an SRU, and is required for each bug associated with the SRU.


.. _reference-enable-proposed:

Enable the -proposed pocket
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Enable the ``-proposed`` pocket in order to test new packages before they are released to ``-updates``.

On Ubuntu 24.04 LTS and newer
""""""""""""""""""""""""""""""

Enable ``-proposed`` with a new apt sources configuration:

.. tabs::

   .. tab:: amd64

         .. code:: bash

             cat << EOF | sudo tee /etc/apt/sources.list.d/proposed.sources
             Types: deb
             URIs: http://archive.ubuntu.com/ubuntu
             Suites: $(. /etc/os-release && echo $VERSION_CODENAME)-proposed
             Components: main restricted universe multiverse
             Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
             EOF
             sudo apt update

   .. tab:: ports

         .. code:: bash

             cat << EOF | sudo tee /etc/apt/sources.list.d/proposed.sources
             Types: deb
             URIs: http://ports.ubuntu.com/ubuntu-ports
             Suites: $(. /etc/os-release && echo $VERSION_CODENAME)-proposed
             Components: main restricted universe multiverse
             Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
             EOF
             sudo apt update

To install a package from ``-proposed``:

.. code:: bash

    sudo apt install -t <series>-proposed <package>


On Ubuntu 22.04 LTS and older
""""""""""""""""""""""""""""""

Enable ``-proposed`` with a new apt sources configuration:

.. tabs::

   .. tab:: amd64

         .. code:: bash

             echo "deb http://archive.ubuntu.com/ubuntu/ $(. /etc/os-release && echo $VERSION_CODENAME)-proposed restricted main multiverse universe" | sudo tee /etc/apt/sources.list.d/proposed.list
             sudo apt update

   .. tab:: ports

         .. code:: bash

             echo "deb http://ports.ubuntu.com/ubuntu-ports/ $(. /etc/os-release && echo $VERSION_CODENAME)-proposed restricted main multiverse universe" | sudo tee /etc/apt/sources.list.d/proposed.list
             sudo apt update

Prior to Ubuntu 24.04 LTS, it is recommended to add additional configuration to enable selective package upgrades from ``-proposed``:

.. code:: bash

    cat << EOF | sudo tee /etc/apt/preferences.d/proposed
    Package: *
    Pin: release a=$(. /etc/os-release && echo $VERSION_CODENAME)-proposed
    Pin-Priority: 100
    EOF

To install a package from ``-proposed``:

.. code:: bash

    sudo apt install -t <series>-proposed <package>


Perform the test plan
^^^^^^^^^^^^^^^^^^^^^

1. Access your testing environment (virtual machine, container, etc.).
2. Enable the ``-proposed`` pocket as described :ref:`above <reference-enable-proposed>`.
3. Install the new package from ``-proposed``:

.. code:: bash

    sudo apt install -t <series>-proposed <package>

4. Confirm that the version from ``-proposed`` is now installed:

.. code:: bash

    apt policy <package>

5. Perform the test plan described in the ``[Test Plan]`` section of the bug description.


Share test results
^^^^^^^^^^^^^^^^^^

1. Leave a comment on the bug with the result of your test, noting the package version you tested. Preferably, share the output of ``apt policy`` from the test environment.
2. Update the bug tags. If the test was successful, change the ``verification-needed-<series>`` tag to ``verification-done-<series>``. If the test was not successful, change the tag to ``verification-failed-<series>``.

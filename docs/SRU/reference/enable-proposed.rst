.. _reference-enable-proposed:

Enable proposed
---------------

Enable the ``-proposed`` pocket in order to test new packages before they are released to ``-updates``.

On Ubuntu 24.04 LTS and newer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

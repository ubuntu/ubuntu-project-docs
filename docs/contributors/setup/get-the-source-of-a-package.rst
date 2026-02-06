.. _how-to-get-the-source-of-a-package:

How to get the source of a package
==================================

Before you can work on a :term:`source package`, you need to get the :term:`source code` of that package. This article presents four ways to achieve this:

- :command:`git-ubuntu`
- :command:`pull-pkg`
- :command:`apt-get source`
- :command:`dget`


git-ubuntu
----------

``git-ubuntu`` is the modern way of working with :term:`Ubuntu` source packages.

.. warning::

    ``git-ubuntu`` is still in active development and these instructions will likely change over time. While ``git-ubuntu`` will become the default packaging method, for now you may encounter rough edges or unsupported edge cases. Ask for help in the ``#ubuntu-devel`` channel or `open a bug report <GitUbuntuBugs_>`_ on :term:`Launchpad`. Bug reports are very welcome!


Install
~~~~~~~

To install ``git-ubuntu``:

.. code-block:: bash

    sudo snap install --classic --edge git-ubuntu 


Basic use
~~~~~~~~~

To clone a source package Git repository to a directory:

.. code-block:: bash

    git-ubuntu clone PACKAGE [DIRECTORY]


To generate the :term:`orig tarballs <orig tarball>` for a given source package:

.. code-block:: bash

    git-ubuntu export-orig


Example
~~~~~~~

.. code-block:: bash

    git-ubuntu clone hello 
    cd hello
    git-ubuntu export-orig


pull-pkg
--------

The :command:`pull-pkg` command is part of the ``ubuntu-dev-tools`` package and downloads a specific version of a source package, or the latest version from a specified release.


Install
~~~~~~~

To install ``ubtuntu-dev-tools``, which includes :command:`pull-pkg`:

.. code-block:: bash

    sudo apt install ubuntu-dev-tools


Basic use
~~~~~~~~~

.. code-block:: none

    pull-pkg [OPTIONS] PACKAGE-NAME [SERIES|VERSION]

Further information in the manual page :manpage:`pull-pkg(1)`.


Examples
~~~~~~~~

There are convenience scripts that follow a similar syntax and set the ``OPTIONS`` for pull type and :term:`distribution` appropriately. Here are three examples:


:command:`pull-lp-source`
^^^^^^^^^^^^^^^^^^^^^^^^^

* To download the latest version of the ``hello`` source package for the :term:`Current Release in Development` from Launchpad:

  .. code-block:: bash

      pull-lp-source hello

* To download the latest version of the ``hello`` source package for the Ubuntu ``mantic`` release from Launchpad:

  .. code-block:: bash

      pull-lp-source hello mantic

* To download version ``2.10-3`` of the ``hello`` source package from Launchpad:

  .. code-block:: bash

      pull-lp-source hello 2.10-3


:command:`pull-ppa-source`
^^^^^^^^^^^^^^^^^^^^^^^^^^

* To download the latest version of the ``hello`` source package from the Launchpad :term:`Personal Package Archive` (PPA), also called ``hello``, of the user ``dviererbe``:

  .. code-block:: bash

      pull-ppa-source --ppa 'dviererbe/hello' 'hello'

* To download the latest version of the ``hello`` source package for the ``mantic`` release from the same Launchpad PPA:

  .. code-block:: bash

      pull-ppa-source --ppa 'dviererbe/hello' 'hello' 'mantic'

* To download version ``2.10-3`` of the ``hello`` source package for the ``mantic`` release from the same Launchpad PPA:

  .. code-block:: bash

      pull-ppa-source --ppa 'dviererbe/hello' 'hello' '2.10-3'


:command:`pull-debian-source`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* To download the latest version of the ``hello`` source package from :term:`Debian`:

  .. code-block:: bash

      pull-debian-source 'hello'

* To download the latest version of the ``hello`` source package for the ``sid`` release from Debian:

  .. code-block:: bash

      pull-debian-source 'hello' 'sid'

* To download the version ``2.10-3`` of the ``hello`` source package from Debian:

  .. code-block:: bash

      pull-debian-source 'hello' '2.10-3'


:command:`apt-get source`
-------------------------

The :term:`APT` package manager can also fetch source packages.

.. important::

   Source packages are tracked separately from :term:`binary packages <Binary Package>` via ``deb-src`` lines in the :manpage:`sources.list(5)` files. This means you need to add such a line for each :term:`repository` you want to get source packages from; otherwise you get either the wrong (too old or too new) source package versions -- or none at all.


Basic use
~~~~~~~~~

.. tabs::

    .. group-tab:: apt

        .. code-block:: none

            apt source PACKAGE-NAME

        Further information in the manual page :manpage:`apt(8)`.

    .. group-tab:: apt-get

        .. code-block:: none

            apt-get source PACKAGE-NAME

        Further information in the manual page :manpage:`apt-get(8)`.


Example
~~~~~~~

.. tabs::

    .. code-tab:: none apt

        apt source 'hello'

    .. code-tab:: none apt-get

        apt-get source 'hello'


``dget``
--------

The :command:`dget` command is part of the ``devscripts`` package. If you call it with the URL of a ``.dsc`` or ``.changes`` file it acts as a source package-aware :manpage:`wget(1)` and downloads all associated files that are listed in the ``.dsc`` or ``.changes`` file (Debian tarball, :term:`orig tarballs <orig tarball>`, :term:`upstream` :term:`signatures <Signature>`).


Install
~~~~~~~

.. code-block:: bash

    sudo apt install devscripts


Basic use
~~~~~~~~~

.. code-block:: bash

    dget URL


Example
~~~~~~~

#. Go to Launchpad and select the package to download (in this example, the latest version of the ``hello`` source package).

#. Copy the download link of the ``.dsc`` file:

#. Call ``dget`` with the copied URL:

   .. code-block:: bash

       dget https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/hello/2.10-3/hello_2.10-3.dsc

This works for links from Debian and Launchpad PPAs, too.

Further information in the manual page :manpage:`dget(1)`.

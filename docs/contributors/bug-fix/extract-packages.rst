.. _extract-packages:

Extract packages
================

This article demonstrates how to extract the contents of Debian packages.

See also the article :ref:`package-model` for a deeper understanding of package formats.


.. _extract-a-source-package:

Extract a source package
------------------------

This section demonstrates how to extract the content of a source package.

.. note::

    A source package archive has the file extension `.dsc`. See also the manual page :manpage:`dsc(5)` for further information.

.. important::

    Make sure you have the :pkg:`dpkg-dev` package installed. To install it:

    .. code-block:: none

        sudo apt update && sudo apt install dpkg-dev

Run the following command in a terminal:

.. code-block:: none

    dpkg-source --extract SOURCE-PACKAGE.dsc [OUTPUT-DIRECTORY]

``SOURCE-PACKAGE.dsc``
    The path to the source package control file.

``OUTPUT-DIRECTORY`` (optional)
    The path to the directory where to extract the content of the source package to. This directory **must not** exist. If no output directory is specified, the content is extracted into a directory named ``NAME-VERSION`` (where ``NAME`` is the name of the source package and ``VERSION`` its version) under the current working directory.

See the manual page :manpage:`dpkg-source(1)` for further information.


.. _extract-a-binary-package:

Extract a binary package
------------------------

This section demonstrates how to extract the content a binary package.

.. note::

    A binary package archive has the file extension `.deb`. See the manual page :manpage:`deb(5)` for further information.

Run:

.. code-block:: none

    dpkg-deb --extract <BINARY-PACKAGE>.deb <OUTPUT-DIRECTORY>

``BINARY-PACKAGE.deb``
    The path to the binary package control file.

``OUTPUT-DIRECTORY``
    The path to the directory where to extract the content of the binary package. In comparison to :ref:`extract-a-source-package`, this directory can already exist and even contain files.

See the manual page :manpage:`dpkg-deb(1)` for further information.

.. tip::

    Using ``--vextract`` instead of ``--extract`` also outputs a list of the extracted files to :term:`standard output`.

    To just list the files that the package contains, use the ``--contents`` option:

    .. code-block:: none

        dpkg-deb --contents BINARY-PACKAGE.deb

.. tip::

    You can also replace ``dpkg-deb`` with ``dpkg`` for the examples shown here. ``dpkg`` forwards the options to ``dpkg-deb``. See the manual page :manpage:`dpkg(1)` for further information.

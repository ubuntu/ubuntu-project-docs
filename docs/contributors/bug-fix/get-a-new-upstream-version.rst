.. _how-to-get-a-new-upstream-version:

How to get a new upstream version
=================================

Download a new :term:`upstream <Upstream>` release or checking if a newer upstream release exists is usually needed when:

- Fixing a bug to rule out that a more recent version may have already fixed the bug.
- (As a :term:`source package <Source Package>` :term:`maintainer <Maintainer>`) to check for, download, and package a newer upstream release.

Most of the source packages contain a ``watch`` file in the ``debian`` directory. This is a configuration file for the :manpage:`uscan(1)` utility, which allows you to automatically search HTTP or FTP sites or :manpage:`git(1)` repositories for newly available updates of the upstream project.

.. note::
    If the source package does not contain a :file:`debian/watch` file, there may be
    an explanation and instructions in the :file:`debain/README.source` or
    :file:`debian/README.debian` file (if available) that tell you how to proceed.

Best practices
--------------

Download upstream file(s) manually only if there is no automatic download mechanism and you can't find any download instructions.

Packages may get distributed to hundreds of thousands of users. Humans are the weakest link in this distribution chain because we may accidentally miss or skip a verification step, misspell a :term:`URL`, copy the wrong URL or copy a URL only partially, etc.

When downloading upstream file(s) manually, make sure to verify :term:`cryptographic signatures <Cryptographic Signature>` (if available). The :term:`signing key` of the upstream project should be stored in the source package as :file:`debian/upstream/signing-key.asc` (if the upstream project has a signing key).

:manpage:`uscan(1)` verifies downloads against this signing key automatically (if available).

Download new upstream version (if available)
--------------------------------------------

Running :manpage:`uscan(1)` from the :term:`root` of the :term:`source tree` checks if a newer upstream version exists and downloads it:

.. code-block:: bash

    uscan

If :manpage:`uscan(1)` cannot find a newer upstream version, it returns exit code `1` and prints nothing to the :term:`standard output`.

:manpage:`uscan(1)` reads the first entry in :file:`debian/changelog` to determine the name and version of the source package.

Add the ``--verbose`` flag to see more information (e.g., which version :manpage:`uscan(1)` found):

.. code-block:: bash

    uscan --verbose

Check for new upstream version (no download)
--------------------------------------------

To check if a new update is available without downloading anything, run the :manpage:`uscan(1)` command with the ``--safe`` flag from the :term:`root` of the source tree:

.. code-block:: bash

    uscan --safe

Force the download
------------------

Use the ``--force-download`` flag to download an upstream release from the upstream project, even if the upstream release is up-to-date with the source package:

.. code-block:: bash

    uscan --force-download

Download the source of older versions from the upstream project
---------------------------------------------------------------

To download the source of a specific version from the upstream project, use the ``--download-version`` flag.

Basic syntax:

.. code-block:: none

    uscan --download-version VERSION

For example:

.. code-block:: bash

    uscan --download-version '1.0'

To download the source for the current version of the source package from the upstream project, use the ``--download-current-version`` flag instead, which parses the version to download from the first entry in the :file:`debian/changelog` file:

.. code:: bash

    uscan --download-current-version

.. note::

    The ``--download-version`` and ``--download-current-version`` flags are both a :term:`best-effort` features of :manpage:`uscan(1)`.

    There are special cases where they do not work for technical reasons.


Further reading
---------------

- Manual page -- :manpage:`uscan(1)`
- Debian wiki -- `debian/watch <https://wiki.debian.org/debian/watch>`_
- Debian policy ``4.6.2.0`` -- `Upstream source location: debian/watch <https://www.debian.org/doc/debian-policy/ch-source.html#upstream-source-location-debian-watch>`_

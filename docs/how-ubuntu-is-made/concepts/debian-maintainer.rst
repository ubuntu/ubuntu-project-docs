.. _debian-maintainer:

The Maintainer field
=======================

In the :file:`debian/control` file, the ``Maintainer`` field indicates the person or team responsible for the maintenance of the package. Since Ubuntu derives from Debian, and many of Ubuntu's packages are unchanged from the upstream Debian package, it is common to find a Debian maintainer listed in this field within the source package.

For example, here is the top of :file:`debian/control` from the ``groff`` package, version 1.22.4-10 shipped with Ubuntu 23.04:

.. code-block:: control
    :emphasize-lines: 4

    Source: groff
    Section: text
    Priority: important
    Maintainer: Colin Watson <cjwatson@debian.org>
    Standards-Version: 3.9.8
    Build-Depends: bison,
                   debhelper-compat (= 13),
                   ghostscript,
                   ...

This is acceptable when Ubuntu has made no changes to the package. However, in the event that Ubuntu ships a package with *any* changes at all, this field must be updated to reflect the fact that Debian are not responsible for (and should not be contacted about) these changes. This requirement was introduced after discussion with, and polling of, the Debian community to determine the most appropriate way to handle the ``Maintainer`` field in distributions derived from Debian.


The :command:`update-maintainer` command
------------------------------------------

When a package has Ubuntu-specific changes, or has been re-built against Ubuntu-specific sources (a :term:`no-change rebuild <NCR>`) the following changes must be made:

* The original ``Maintainer`` field is renamed to ``XBSC-Original-Maintainer``

* A new ``Maintainer`` field with an ``ubuntu.com`` address is added

The :command:`update-maintainer` script, found in the :pkg:`ubuntu-dev-tools` package can be used to accomplish this easily, but be aware that it will refuse to do so unless :file:`debian/changelog` indicates that the package targets Ubuntu (the top entry has a series other than "unstable", "testing", etc).

For example, after defining a new version targeting "lunar" in :file:`debian/changelog`, running :command:`update-maintainer` leaves the following at the top of :file:`debian/control`:

.. code-block:: control
    :emphasize-lines: 4-5

    Source: groff
    Section: text
    Priority: important
    Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
    XSBC-Original-Maintainer: Colin Watson <cjwatson@debian.org>
    Standards-Version: 3.9.8
    Build-Depends: bison,
                   debhelper-compat (= 13),
                   ghostscript,
                   ...

Typically, the address ``ubuntu-devel-discuss@lists.ubuntu.com`` is used as any package in Ubuntu may be uploaded by anyone with the appropriate rights, which are governed by Launchpad rather than the ``Maintainer`` and ``Uploader`` fields in the source package. However, any ``ubuntu.com`` address may be used, if a specific maintainer is more appropriate.

The Ubuntu version of the package building tools ensure that, if the package's version number indicates Ubuntu modifications, they will refuse to build unless the ``Maintainer`` field includes an ``ubuntu.com`` address.


Binary packages
---------------

Even when the *source* package is unchanged from Debian, and contains a Debian maintainer, *binary* packages built by Launchpad will still have the ``ubuntu-devel-discuss@lists.ubuntu.com`` address in their ``Maintainer`` field. This is because Launchpad automatically updates this field in a post-build step.

.. _debian-policy:

Debian policy
=============

The Debian policy defines the requirements and guidelines for packages in the Debian distribution. It governs how packages should behave, how they interact with each other, and how they fit into the system as a whole.

The policy specifies:

- the structure and contents of the Debian archive
- mandatory technical requirements for inclusion in the distribution
- package formatting and control files
- filesystem layout
- :term:`operating system` design principles
- maintainer scripts
- inter-package relationships
- shared library handling

See the `Debian Policy Manual <https://www.debian.org/doc/debian-policy/index.html>`_ for the latest version of the Debian policy.


Policy conformance
------------------

It's recommended but not mandatory that every :term:`source package` should conform to the latest version of the Debian policy available at the time of the package’s last update.

The ``Standards-Version`` field in the :file:`debian/control` file of the source package must be filled out to indicate the version of the Debian policy that the package complies with. Also, package maintainers must review policy changes before updating this field.


:file:`debian/control` file
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :file:`debian/control` file defines key metadata for source packages and :term:`binary packages <Binary Package>`. It resides in the root of the source package directory and is required for all source packages.

This file consists of stanzas, which are sections of fields separated by empty lines. The first stanza defines the source package. Each following stanza describes a binary package built from that source package.

Here are the required fields in the first stanza of the :file:`debian/control` file of the source package:

``Source``
    The name of the source package, which must be unique within the Debian archive.

``Maintainer``
    Name and email of the primary maintainer. This field is crucial for contacting the maintainer regarding issues, updates, or questions related to the package.

``Standards-Version``
    The version of the Standard the package complies with.

Recommended fields in the first stanza of the :file:`debian/control` file include ``Section`` and ``Priority``.

For more information on :file:`debian/control` files and their fields, see `Control files and their fields <https://www.debian.org/doc/debian-policy/ch-controlfields.html>`_.


``Standards-Version`` field
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``Standards-Version`` field in the :file:`debian/control` file indicates which version of the Debian policy the package has been reviewed against. The field must appear in the first stanza of the :file:`debian/control` file.

The value of the field, which is the Debian policy version number, has four components:

.. code-block:: text

    Standards-Version: <major>.<minor>.<patch>.<subpatch>

Here is a breakdown of the components:

* **Major version** (``<major>``): Incremented for significant policy changes requiring widespread updates.
* **Minor version** (``<minor>``): Changed for substantial but less disruptive updates.
* **Major patch level** (``<patch>``): Updated for any normative binding changes.
* **Minor patch level** (``<subpatch>``): Used for non-functional fixes like typos and clarifications.

Only the first three components are significant. You may include or omit the fourth.

When updating an existing package, only update the ``Standards-Version`` field after reviewing the differences between the old and new policy versions and updating the package if necessary.


Upgrading checklist
~~~~~~~~~~~~~~~~~~~

Before updating the ``Standards-Version`` field, follow these steps to ensure compliance:

1. Check the ``Standards-Version`` value in :file:`debian/control`.
#. Review the changes introduced in newer versions. Refer to the `Upgrading checklist <https://www.debian.org/doc/debian-policy/upgrading-checklist.html>`_ section of the *Debian Policy Manual* for a summary of the changes made in each version.
#. Review relevant sections of the policy based on listed changes and apply updates only when necessary.
#. Test the package to confirm that it builds and behaves correctly with the new standard.
#. Update the ``Standards-Version`` field in :file:`debian/control` file to the new version.


Further reading
---------------

- `Debian Policy Manual <https://www.debian.org/doc/debian-policy/index.html>`_

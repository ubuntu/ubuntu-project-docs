.. _patch-management:

Patch management
================

This article demonstrates how to manage the :term:`patches <Patch>` of a :term:`source package <Source package>` in the ``3.0 (quilt)`` format.

See the :ref:`patches` for more background information about patches in the context of :term:`Ubuntu`.

.. note::

    If the format is ``3.0 (native)``, this article is not of interest for you and simply write your changes to the files. There is no need to explicitly create and track a patch for :term:`native packages <native package>`. See the :ref:`package-model` article for more information about package formats.

As the source package format implies, we use the :manpage:`quilt(1)` tool to manage the patches of a source package. Quilt manages patches like a :term:`stack`. It maintains a list of patches (also called "series") that get applied one after another from top to bottom in the order they are listed in :file:`debian/patches/series`, excluding lines starting with ``#``.

.. important::

    Quilt creates a ``.pc/`` directory at the source package root directory. This is the location where Quilt stores control files similar to the ``.git/`` folder of a :term:`Git` repository.

    Before you commit any changes (e.g., with :term:`git-ubuntu`) or attempt to build the source package, **do not forget to unapply all patches and delete the directory:**

    .. code-block:: none

        quilt pop -a && rm -r .pc

    To avoid having to remove ``.pc``, add it to the :file:`.gitignore`.


Prerequisites
-------------

If you haven't already, install :manpage:`quilt(1)`:

.. code:: none

    sudo apt install quilt

The following sample :manpage:`quilt(1)` configuration file sets recommended useful defaults. It also instructs :command:`quilt` to look for patches in the ``debian/patches/`` directory if the ``quilt`` command is invoked within a :term:`source package` directory. Save it as :file:`~/.quiltrc`.

.. literalinclude:: configure.bash
   :language: bash

.. note::

    To undo this configuration, delete :file:`~/.quiltrc`.


List patches
------------

List all available patches:

.. code-block:: none

    quilt series

This also color-codes the output based on patch status:

- applied (green)
- latest applied patch (yellow)
- unapplied (white)

List applied patches:

.. code-block:: none

    quilt applied

Display the topmost applied patch:

.. code-block:: none

    quilt top

List unapplied patches:

.. code-block:: none

    quilt unapplied

.. note::

    Quilt patches are applied from top to bottom in the order they are listed.


.. _apply-patches:

Apply patches
-------------

Apply the next patch:

.. code-block:: none

    quilt push

Apply all patches:

.. code-block:: none

    quilt push -a

Apply the next ``N`` patches

.. code-block:: none

    quilt push N

Apply all patches until (including) a specific patch:

.. code-block:: none

    quilt push PATCH-NAME

This can also be the path of the patch (allowing for auto-completion):

.. code-block:: none

    quilt push debian/series/PATCH-NAME


Unapply patches
---------------

This works similar to applying patches.

Unapply the patch on top:

.. code-block:: none

    quilt pop

Unapply all patches:

.. code-block:: none

    quilt pop -a

Unapply the ``N`` topmost applied patches

.. code-block:: none

    quilt pop N

Unapply all patches until (excluding) a specific patch:

.. code-block:: none

    quilt pop PATCH-NAME

This can also be the path of the patch (allowing for auto-completion):

.. code-block:: none

    quilt pop debian/series/PATCH-NAME


.. _verify-patches:

Verify patches
--------------

Now that you know how to apply and unapply patches you can verify if all patches apply and unapply cleanly. This is useful when you merge changes from Debian into an Ubuntu package and want to check if everything is still in order.

1. Verify that all patches apply cleanly:

   .. code-block:: none

       quilt push -a

2. Verify that all patches unapply cleanly:

   .. code-block:: none

       quilt pop -a

3. (optional) Remove the Quilt control file directory:

   .. code-block:: none

       rm -r .pc


Show details about a patch file
-------------------------------

Print the header of the topmost applied or specified patch:

.. code-block:: none

    quilt header [PATCH-NAME]

Print the list of files that the topmost applied or specified patch changes:

.. code-block:: none

    quilt files [PATCH-NAME]

Print the changes by the topmost applied or specified patch to the specified file(s) in a diff format. If no files are specified, all files that are changes are included.

.. code-block:: none

    quilt diff [-P PATCH-NAME] [FILE-PATH ...]


Rename a patch file
-------------------

Rename the topmost applied or specified patch:

.. code-block:: none

    quilt rename [-P PATCH-NAME] NEW-PATCH-NAME


Remove a patch file
-------------------

Remove the topmost applied or specified patch from the :file:`debian/patches/series` file. Use the ``-r`` option to also delete the patch file from the :file:`debian/patches` directory:

.. code-block:: none

    quilt delete [-r] [PATCH-NAME]


Generate a patch file
---------------------

1. Create a new patch after the topmost applied patch:

   .. code-block:: none

       quilt new PATCH-NAME

   .. note::

       It is best practice to read the existing patch filenames in :file:`debian/patches` and ensure your new patch name is consistent with the existing ones.

2. Edit files outside the :file:`debian/` directory by following the same steps as outlined by the :ref:`edit-a-patch-file` section.


.. _edit-a-patch-file:

Edit a patch file
-----------------

1. Apply all patches until the patch we want to edit:

   .. code-block:: none

       quilt push PATCH-NAME

2. There are multiple approaches how to edit the patch file:

   - Edit the patch header:

     .. code-block:: none

         quilt header -e

     .. tip::

         Use the ``--dep3`` flag to insert a :term:`DEP 3` patch header template:

        .. code-block:: none

            quilt header --dep3 -e

        .. tip::

         See :ref:`dep-3-patch-file-headers`, which lists and briefly explains standard DEP 3 compliant fields and shows sample DEP 3 compliant headers.

   - Edit specific file(s) with a text editor after adding the changes to the patch file:

     .. code-block:: none

         quilt edit FILE-PATH ...

     .. note::

         Opens the files in ``$EDITOR`` -- this is usually your default terminal editor.

   - Edit specific file(s) manually (without immediately opening an editor):

     a. Check which files are already changed by the patch file:

        .. code-block:: none

            quilt files 

     b. To edit file(s) that the patch currently does NOT change, add these files to the patch before editing them:

        .. code-block:: none

            quilt add FILE-PATH ...

        .. note::

            You can directly edit files that are already changed by the patch.

        .. tip::

            To see the changes of the patch file to a specific file:

            .. code-block:: none

             quilt diff FILE-PATH

            To see the changes you made of the patch file:

            .. code-block:: none

             quilt diff -z

     c. Save the changes to the patch file:

        .. code-block:: none

            quilt refresh

   - Delete the changes of a patch to specific file(s):

     .. code-block:: none

         quilt remove FILE-PATH ...

3. (recommended) If there are patches after the patch you have edited,
   :ref:`verify that all patches still apply cleanly <verify-patches>`.


Import a patch file
-------------------

Insert patch files following the current topmost applied patch: 

.. code-block:: none

    quilt import PATCH-FILE-PATH ...

.. important::

    The patch files have to be outside the :file:`debian/patches/` directory.

.. note::

    The imported patches do not get applied automatically. You must :ref:`apply the patches <apply-patches>` after importing them.


Further reading
---------------

- :ref:`dep-3-patch-file-headers`
- :ref:`patches`
- manual page :manpage:`quilt(1)`
- `Debian wiki -- Using quilt in Debian source packages <https://wiki.debian.org/UsingQuilt>`_

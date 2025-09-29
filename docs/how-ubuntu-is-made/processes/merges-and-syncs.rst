.. _merges-syncs:

Merges & syncs
==============

This article explains how and why Ubuntu imports changes from :term:`Debian`.


.. admonition:: **Merging** series

    The article series provides guidance on performing package merges.

    Process overview:
      - :ref:`merges-syncs` (this article)

    .. raw:: html

        <span style="font-size:0.1px"></span>

    :ref:`How to do a merge <merging>`:
      #. :ref:`merge-preliminary-steps`
      #. :ref:`merge-process`
      #. :ref:`merge-fix-the-changelog`
      #. :ref:`merge-upload-a-ppa`
      #. :ref:`merge-test-the-new-build`
      #. :ref:`merge-git-ubuntu-merge-proposal`

    Extra:
      - :ref:`merge-manually`
      - :ref:`merge-cheat-sheet`


Importing changes from Debian
-----------------------------

Because Ubuntu is derived from Debian and uses the same package management system (:term:`APT`), most changes made to Debian can also be applied to Ubuntu.

**Syncs** and **merges** are the two processes through which Ubuntu developers integrate updates and improvements from Debian into the :ref:`package-archive`.

.. list-table:: Syncs and merges
   :header-rows: 1

   * - Sync
     - Merge
   * - Ubuntu package carries no delta (no changes are applied by Ubuntu on top of the Debian package)
     - Ubuntu package carries a delta (patches are applied by Ubuntu to the Debian package)


.. _syncs:

Syncs
~~~~~

Sync (synchronization with Debian) is the automatic copying of new packages from Debian unstable (:term:`code name` "Sid") to the Ubuntu Archive. This includes packages that have not been in the distribution before and packages with higher version identifiers than the corresponding Ubuntu packages. Corresponding Ubuntu packages that carry :term:`Ubuntu delta` are excluded from the sync.

The sync process runs from the opening of the Ubuntu Archive for a new :term:`release <Ubuntu release>` until the :ref:`debian-import-freeze`.

On request (via a :term:`Launchpad` ticket), :term:`archive admins <Archive admin>` can sync a package from Debian even if the Ubuntu package carries an Ubuntu delta. In this case, the Ubuntu delta is dropped. A good example is when Ubuntu-specific changes have been merged into the Debian package or the :term:`upstream` project and are no longer needed. See :ref:`how-to-request-a-sync`.

.. admonition:: Getting packages from Debian to Ubuntu outside of the sync process

    After the Debian Import Freeze and before the :ref:`final-release`, you must request the respective :ref:`freeze exception <freeze-exceptions>`.

    After the Final Release, you must follow the :ref:`stable-release-updates` process. For additional details about the freezes, see the :ref:`release-cycle` article.


.. _merges:

Merges
~~~~~~

When importing a newer Debian package into Ubuntu, a merge must be performed if the corresponding Ubuntu package carries an Ubuntu delta that needs to be partially or fully applied to the Debian package.

The Ubuntu Merge-o-Matic (MoM) service automatically performs merges and publishes the reports on `merges.ubuntu.com <https://merges.ubuntu.com/>`_. See the lists of outstanding merges for:

* `main <https://merges.ubuntu.com/main.html>`_
* `universe <https://merges.ubuntu.com/universe.html>`_
* `restricted <https://merges.ubuntu.com/restricted.html>`_
* `multiverse <https://merges.ubuntu.com/multiverse.html>`_

To complete a merge, interaction and supervision by Ubuntu maintainers are required. See :ref:`merging` for details on performing a merge.

When Debian or upstream incorporate our logical changes before we merge them, meaning that there is essentially no difference between the Ubuntu and Debian versions, proceeding with merge would be merging an :ref:`empty commit <merge-empty-commits>` (i.e., adding a commit where nothing has changed). In this situation, it is better to sync the new version of the Debian package back to Ubuntu than to manually perform an empty merge. See :ref:`how-to-request-a-sync`.

See the section :ref:`archive-components` in the article that explains the Ubuntu package archive for an explanation of ``main``, ``universe``, ``restricted``, and ``multiverse``.


Why does Ubuntu import changes from Debian
------------------------------------------

Ubuntu incorporates changes from Debian through merging and syncing to leverage the extensive work and improvements made by the Debian community. Debian provides a stable foundation and a vast repository of packages. By integrating changes from Debian, Ubuntu can focus on refining the :term:`user experience`. At the same time, the consistency between Ubuntu and Debian allows for sharing resources (e.g., testing and bug fixing) and contributing back to the open-source ecosystem, ultimately benefiting both :term:`distributions <distribution>` and their users.

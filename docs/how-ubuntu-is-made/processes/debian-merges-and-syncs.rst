.. _importing-changes-from-debian-merges-syncs:

Importing changes from Debian (merges & syncs)
==============================================

This article explains how and why changes from :term:`Debian` are imported into Ubuntu.


How does Ubuntu import changes from Debian
------------------------------------------

Because Ubuntu is derived from Debian and uses the same package management system (:term:`APT`), most changes made to Debian can also be applied to Ubuntu.

**Syncs** and **merges** are the two processes through which Ubuntu developers integrate updates and improvements from Debian into the :ref:`ubuntu-package-archive`.


Sync
~~~~

Beginning with the archive opening for a new Ubuntu release until the :ref:`debian-import-freeze`, new :term:`packages <Package>` and packages with higher version identifiers than the corresponding Ubuntu packages are automatically copied from Debian unstable (also known as :term:`Code name` "Sid") into the Ubuntu package archive if the corresponding Ubuntu packages do not carry :term:`Ubuntu Delta`. This process is called "synchronization with Debian", or "sync" for short.

On request (via a :term:`Launchpad` bug-ticket), :term:`Archive Admins <Archive Admin>` can sync a package from Debian even if the Ubuntu package carries Ubuntu Delta. In this case, the Ubuntu Delta will be dropped. A good example is when Ubuntu-specific changes have been merged into the Debian package or :term:`Upstream` project and are no longer needed.

.. note::
    The :ref:`feature-freeze-ff` is often scheduled for the same day as the :ref:`debian-import-freeze`.

    After the Debian Import Freeze and before the :ref:`final-release`, you must also request the respective freeze exception.

    After the Final Release, you must follow the :ref:`SRU <sru-overview>` process. For additional details about the freezes, see the :ref:`ubuntu-development-process` article.


Merges
~~~~~~

When importing a newer Debian package into Ubuntu, a merge must be performed if the corresponding Ubuntu package carries Ubuntu Delta that needs to be partially or fully applied to the Debian package.

The Ubuntu Merge-o-Matic (MoM) automatically performs merges and publishes the reports on `merges.ubuntu.com <https://merges.ubuntu.com/>`_. See the lists of outstanding merges for:

* `main <https://merges.ubuntu.com/main.html>`_
* `universe <https://merges.ubuntu.com/universe.html>`_
* `restricted <https://merges.ubuntu.com/restricted.html>`_
* `multiverse <https://merges.ubuntu.com/multiverse.html>`_

.. TODO merging link

To complete a merge, interaction and supervision by Ubuntu maintainers are required. See TODO for details on performing a merge.

See the section :ref:`archive-components` in the article that explains the Ubuntu package archive for an explanation of ``main``, ``universe``, ``restricted``, and ``multiverse``.


Why does Ubuntu import changes from Debian
------------------------------------------

Ubuntu incorporates changes from Debian through merging and syncing to leverage the extensive work and improvements made by the Debian community. Debian provides a stable foundation and a vast repository of packages. By integrating changes from Debian, Ubuntu can focus on refining the :term:`user experience`. At the same time, the consistency between Ubuntu and Debian allows for sharing resources (e.g., testing and bug fixing) and contributing back to the open-source ecosystem, ultimately benefiting both :term:`distributions <distribution>` and their users.

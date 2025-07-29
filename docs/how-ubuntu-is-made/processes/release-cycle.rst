.. _release-cycle:

Release cycle
=============

Each release cycle follows the same general pattern with a number of major phases. Ubuntu contributors are expected to follow this process closely to ensure that their work is aligned with that of others. Because of the time-based release cycle, Ubuntu contributors must coordinate well to produce an on-time release.

See also the article :ref:`ubuntu-releases` for more details about the release cadence.


Beginning a new release
-----------------------

The Ubuntu infrastructure is prepared for a new development branch at the beginning of each cycle. The package build system is set up, the toolchain is organized, :term:`seeds` are branched, and many other pieces are made ready before development can properly begin. Once these preparations are made, the new branch is officially announced on the `ubuntu-devel-announce mailing list <https://lists.ubuntu.com/mailman/listinfo/ubuntu-devel-announce>`_ and opened for uploads to the :ref:`package-archive`.

.. note::
    See the `Ubuntu 24.04 LTS (Noble Numbat) Archive opening announcement email <https://lists.ubuntu.com/archives/ubuntu-devel-announce/2023-October/001341.html>`_ as an example.


Planning
--------

Ubuntu contributors discuss the targeted features for each release cycle via the various channels (IRC, Matrix, Discourse, Launchpad). Some of these come from strategic priorities for the distribution as a whole, and some are proposed by individual developers.

The broader open-source community gets together at the :term:`Ubuntu Summit` (similar but different to the past :term:`Ubuntu Developer Summits <Ubuntu Developer Summit>`) to share experiences and ideas and to inspire future projects covering development as well as design, writing, and community leadership with a wide range of technical skill levels.


Merging with upstream and feature development
---------------------------------------------

The first phase of the release cycle is characterized by bringing new releases of :term:`upstream` components into Ubuntu, either directly or via :ref:`merges-syncs`. The development of planned projects for the release often begins while merging is still underway, and the development accelerates once the Package Archive is reasonably consistent and usable.

The automatic import of new package versions from Debian ends at the :ref:`debian-import-freeze`.


Stabilization and milestones (freezes)
--------------------------------------

Developers should increasingly exercise caution in making changes to Ubuntu to ensure a stable state is reached in time for the final release date. Archive Admins incrementally restrict modifications to the Ubuntu Package Archive, effectively freezing it. The milestones when these restrictions get enabled are called "freezes". During freezes, developers must request :ref:`freeze-exceptions` to approve changes (see also :ref:`request-a-freeze-exception`). The release team posts the current Release Schedule as a Discourse article under the `"Release" topic <https://discourse.ubuntu.com/c/project/release>`_. It shows the typical order and length of the various freezes.

See :ref:`freezes` for an overview of the individual stabilization milestones.


Finalization
------------

As the final release approaches, the focus narrows to fixing "showstopper" bugs and thoroughly validating the installation images. Every image is tested to ensure that the installation methods work as advertised. Low-impact bugs and other issues are deprioritized to focus developers on this effort.

This phase is vital, as severe bugs that affect the experience of booting or installing the images must be fixed before the final release. In contrast, ordinary bugs affecting the installed system can be fixed with Stable Release Updates.


.. _final-release:

Final Release
-------------

Once the release team declares the :ref:`release-candidate` ISO stable and names it the "Final Release", a representative of the team announces it on the `ubuntu-announce mailing list <https://lists.ubuntu.com/archives/ubuntu-announce/>`_.

.. note::
    See, for example, the `Ubuntu 24.04 LTS (Noble Numbat) release announcement <https://lists.ubuntu.com/archives/ubuntu-announce/2024-April/000301.html>`_.

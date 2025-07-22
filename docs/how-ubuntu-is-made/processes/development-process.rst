.. _ubuntu-development-process:

Ubuntu development process
==========================

Each release cycle follows the same general pattern, with the following major phases. Ubuntu contributors are expected to follow this process closely to ensure that their work is aligned with that of others. Because of the time-based release cycle, Ubuntu contributors must coordinate well to produce an on-time release.

See also the article :ref:`ubuntu-releases` for more details about the release cadence.


Beginning a new release
-----------------------

The Ubuntu infrastructure is prepared for a new development branch at the beginning of each cycle. The package build system is set up, the toolchain is organized, :term:`seeds` are branched, and many other pieces are made ready before development can properly begin. Once these preparations are made, the new branch is officially announced on the `ubuntu-devel-announce mailing list <https://lists.ubuntu.com/mailman/listinfo/ubuntu-devel-announce>`_ and opened for uploads to the :ref:`ubuntu-package-archive`.

.. note::
    See the `Ubuntu 24.04 LTS (Noble Numbat) archive opening announcement email <https://lists.ubuntu.com/archives/ubuntu-devel-announce/2023-October/001341.html>`_ as an example.


Planning
--------

Ubuntu contributors discuss the targeted features for each release cycle via the various channels (e.g., IRC, Matrix, Discourse, Launchpad). Some of these come from strategic priorities for the distribution as a whole, and some are proposed by individual developers.

The broader open-source community gets together at the :term:`Ubuntu Summit` (similar but different to the past :term:`Ubuntu Developer Summits <Ubuntu Developer Summit>`) to share experiences and ideas and to inspire future projects covering development as well as design, writing, and community leadership with a wide range of technical skill levels.


Merging with upstream and feature development
---------------------------------------------

The first phase of the release cycle is characterized by bringing new releases of :term:`upstream` components into Ubuntu, either directly or via :ref:`importing-changes-from-debian-merges-syncs`. The development of planned projects for the release often begins while merging is still underway, and the development accelerates once the package archive is reasonably consistent and usable.

The automatic import of new package versions from Debian ends at the :ref:`debian-import-freeze`.


Stabilization and milestones (freezes)
--------------------------------------

Developers should increasingly exercise caution in making changes to Ubuntu to ensure a stable state is reached in time for the final release date. Archive admins incrementally restrict modifications to the Ubuntu package archive, effectively freezing the state of the Ubuntu package archive. The milestones when these restrictions get enabled are called "freezes". During freezes, developers must request exceptions to approve changes. See :ref:`request-a-freeze-exception`. The release team usually posts the current Release Schedule as a Discourse article under the `"Release" topic <https://discourse.ubuntu.com/c/project/release>`_. It shows the typical order and length of the various freezes.

.. note::
    In the past, the Release Schedule was published in the Ubuntu Wiki. See, for example, the `release schedule of Ubuntu 20.04 LTS (Focal Fossa) <https://wiki.ubuntu.com/FocalFossa/ReleaseSchedule>`_.


.. _testing-weeks:

Testing weeks
~~~~~~~~~~~~~

During a release's development phase, the release team organize testing weeks to focus the Ubuntu community's efforts on testing Ubuntu's latest daily :term:`ISO images <Image>` and its :term:`flavors <Ubuntu flavors>`. These weeks are crucial for discovering bugs and getting early feedback about new features.

.. note::
    The testing weeks replaced the older practice of alpha and beta milestones. For example, Ubuntu 14.04 LTS (Trusty Tahr) had Alpha 1, Alpha 2, Beta 1, and Beta 2 milestones.

    See `the email <https://lists.ubuntu.com/archives/ubuntu-release/2018-April/004434.html>`_ that announced the process change.


.. _debian-import-freeze:

Debian Import Freeze
~~~~~~~~~~~~~~~~~~~~

Archive admins disable the automatic import of new packages and versions of existing packages from Debian. The import of a new package or version of an existing package from Debian has to be requested.

.. note::

    The general development activity is still unrestricted until the Feature Freeze; however, the Feature Freeze is often scheduled for the same day.


.. _feature-freeze-ff:

Feature Freeze (FF)
~~~~~~~~~~~~~~~~~~~

At this point, Ubuntu developers should stop introducing new features, packages, and :term:`API`/:term:`ABI` changes, and instead concentrate on fixing bugs in the current release in development.


.. _user-interface-freeze-uif:

User Interface Freeze (UIF)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user interface should be finalized to allow documentation writers and translators to work on a consistent target that doesn't render screenshots or documentation obsolete.

After the user interface freeze, the following things are not allowed to change without a freeze exception:

* User interface of individual applications that are installed by default
* Appearance of the desktop
* Distribution-specific artwork
* All user-visible strings in the desktop and applications that are installed by default


.. _documentation-string-freeze:

Documentation String Freeze
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Documentation strings should no longer be created or modified. This freeze ensures that the documentation can be accurately translated.

Exceptions to this rule may be considered before the release for significant and glaring errors or exceptional circumstances.


.. _kernel-feature-freeze:

Kernel Feature Freeze
~~~~~~~~~~~~~~~~~~~~~

The :term:`kernel` feature development should end at this point, and the kernels can be considered feature-complete for the release. From now on, only bug-fix changes are expected.

.. note::
    The Kernel Feature Freeze occurs after the :ref:`feature-freeze-ff` because the Linux Kernel is typically released upstream after the Feature Freeze. Additionally, the Kernel Feature Freeze is deliberately scheduled so that the Beta images have a fully featured kernel suitable for testing.


.. _hardware-enablement-freeze:

Hardware Enablement Freeze
~~~~~~~~~~~~~~~~~~~~~~~~~~

All new hardware enablement tasks for devices targeting the given release should be finished, and all the respective packages should be in the Ubuntu package archive. The release team no longer accepts changes in the Ubuntu package archive related to supporting new image types or platforms. This freeze ensures that any new platforms are already available for testing of the beta images and in the weeks leading to the :ref:`final-freeze`.

.. note::
    The Hardware Enablement Freeze is usually scheduled for the same day as the Beta Freeze.


.. _beta-freeze:

Beta Freeze
~~~~~~~~~~~

In preparation for the beta release, all uploads are queued and subject to manual approval by the release team. Changes to packages that affect beta release images (flavours included) require the release team's approval before uploading. Uploads for packages that do not affect images are generally accepted as time permits.

.. tip::
    Use the :manpage:`seeded-in-ubuntu(1)` tool, provided by the ``ubuntu-dev-tools`` package, to list all the current daily images containing a specified package or to determine whether the specified package is part of the supported seed.

    If the list output is empty, uploading it during a freeze should be safe.

The freeze allows Archive Admins to fix package inconsistencies or critical bugs quickly and in an isolated manner. Once the beta release is shipped, the Beta Freeze restrictions no longer apply.


.. _kernel-freeze:

Kernel Freeze
~~~~~~~~~~~~~

The Kernel Freeze is the final date for kernel updates because they require several lockstep actions that must be folded into the image-building process.

Exceptional circumstances may justify exemptions to the freeze at the discretion of the release managers.


.. _non-language-pack-translation-deadline:

Non-language-pack translation deadline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some translation data cannot currently be updated via the language pack mechanism. Because these items require more disruptive integration work, they are subject to an earlier deadline to give time to developers to manually export translations from Launchpad and integrate them into the package.

This marks the date after which translations for such packages are not guaranteed to be included in the final release. Depending on the package and its maintainers workflow, they may be exported later.

Other packages can still be translated until the :ref:`language-pack-translation-deadline`.


.. _final-freeze:

Final Freeze
~~~~~~~~~~~~

This freeze marks an **extremely** high-caution period until the :ref:`final-release`. Only bug fixes for release-critical, security-critical or otherwise exceptional circumstantial bugs are included in the Final Release, which the release team and relevant section teams must confirm.


Unseeded packages
^^^^^^^^^^^^^^^^^

Packages in :ref:`archive-components-universe` that aren't seeded in any of the Ubuntu flavours remain in :ref:`feature-freeze-ff` because they do not affect the release; however, when the Ubuntu package archive is frozen, fixes must be manually reviewed and accepted by the release team members.

When the Final Release is close (~1.5 days out), developers should consider uploading to the :ref:`proposed pocket <archive-pockets-proposed>`, from which the release team cherry-picks into the :ref:`release pocket <archive-pockets-release>` if circumstances allow. All packages uploaded to the proposed pocket that do not make it into the release pocket until the Final Release become candidates for :ref:`sru-overview`. Therefore, uploads to the proposed pocket during Final Freeze should meet the requirements of Stable Release Updates if the upload is not accepted into the release pocket. In particular, the upload must reference at least one bug, which is used to track the stable update.

.. note::
    If you are sure that your upload will be accepted during Final Freeze, you can upload directly to the release pocket, but be aware that you have to re-upload after Final Release if the upload gets rejected.


.. _release-candidate:

Release Candidate
~~~~~~~~~~~~~~~~~

The images produced during the week before the :ref:`final-release` are considered "release candidates". In an ideal world, the first release candidate would end up being the Final Release; however, we don't live in a perfect world, and this week is used to get rid of the last release-critical bugs and do as much testing as possible. Until the Final Release, changes are only permitted at the release team's discretion and will only be allowed for high-priority bugs that might justify delaying the release.


.. _language-pack-translation-deadline:

Language pack translation deadline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Translations done up until this date are included in the final release's language packs.


Finalization
------------

As the final release approaches, the focus narrows to fixing "showstopper" bugs and thoroughly validating the installation images. Every image is tested to ensure that the installation methods work as advertised. Low-impact bugs and other issues are deprioritized to focus developers on this effort.

This phase is vital, as severe bugs that affect the experience of booting or installing the images must be fixed before the final release. In contrast, ordinary bugs affecting the installed system can be fixed with Stable Release Updates.


.. _final-release:

Final Release
-------------

Once the release team declares the :ref:`ReleaseCandidate` ISO stable and names it the "Final Release", a representative of the team announces it on the `ubuntu-announce mailing list <https://lists.ubuntu.com/archives/ubuntu-announce/>`_.

.. note::
    See, for example, the `Ubuntu 24.04 LTS (Noble Numbat) release announcement <https://lists.ubuntu.com/archives/ubuntu-announce/2024-April/000301.html>`_.

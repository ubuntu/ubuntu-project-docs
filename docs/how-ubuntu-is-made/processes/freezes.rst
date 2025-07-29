.. _freezes:

Freezes
=======

This article provides an overview of the stabilization milestones that lead to the release of a new version of Ubuntu. The series of milestones (freezes) means the gradual introduction of restrictions on modifications in certain areas, so that the distribution can stabilize as it nears the final release.

See :ref:`release-cycle` for an overview of the entire release process.


.. _testing-weeks:

Testing weeks
-------------

During a release's development phase, the release team organize testing weeks to focus the Ubuntu community's efforts on testing Ubuntu's latest daily :term:`ISO images <Image>` and its :term:`flavors <Ubuntu flavors>`. These weeks are crucial for discovering bugs and getting early feedback about new features.

.. note::
    The testing weeks replaced the older practice of alpha and beta milestones. For example, Ubuntu 14.04 LTS (Trusty Tahr) had Alpha 1, Alpha 2, Beta 1, and Beta 2 milestones.

    See `the email <https://lists.ubuntu.com/archives/ubuntu-release/2018-April/004434.html>`_ that announced the process change.


.. _debian-import-freeze:

Debian Import Freeze
--------------------

Archive admins disable the automatic import of new packages and versions of existing packages from Debian. The import of a new package or version of an existing package from Debian has to be requested.

.. note::

    The general development activity is still unrestricted until the Feature Freeze; however, the Feature Freeze is often scheduled for the same day.


.. _feature-freeze-ff:

Feature Freeze (FF)
-------------------

At this point, Ubuntu developers should stop introducing new features, packages, and :term:`API`/:term:`ABI` changes, and instead concentrate on fixing bugs in the current release in development.


.. _user-interface-freeze-uif:

User Interface Freeze (UIF)
---------------------------

The user interface should be finalized to allow documentation writers and translators to work on a consistent target that doesn't render screenshots or documentation obsolete.

After the user interface freeze, the following things are not allowed to change without a freeze exception:

* User interface of individual applications that are installed by default
* Appearance of the desktop
* Distribution-specific artwork
* All user-visible strings in the desktop and applications that are installed by default


.. _documentation-string-freeze:

Documentation String Freeze
---------------------------

Documentation strings should no longer be created or modified. This freeze ensures that the documentation can be accurately translated.

Exceptions to this rule may be considered before the release for significant and glaring errors or exceptional circumstances.


.. _kernel-feature-freeze:

Kernel Feature Freeze
---------------------

The :term:`kernel` feature development should end at this point, and the kernels can be considered feature-complete for the release. From now on, only bug-fix changes are expected.

.. note::
    The Kernel Feature Freeze occurs after the :ref:`feature-freeze-ff` because the Linux Kernel is typically released upstream after the Feature Freeze. Additionally, the Kernel Feature Freeze is deliberately scheduled so that the Beta images have a fully featured kernel suitable for testing.


.. _hardware-enablement-freeze:

Hardware Enablement Freeze
--------------------------

All new hardware enablement tasks for devices targeting the given release should be finished, and all the respective packages should be in the Ubuntu package archive. The release team no longer accepts changes in the Ubuntu package archive related to supporting new image types or platforms. This freeze ensures that any new platforms are already available for testing of the beta images and in the weeks leading to the :ref:`final-freeze`.

.. note::
    The Hardware Enablement Freeze is usually scheduled for the same day as the Beta Freeze.


.. _beta-freeze:

Beta Freeze
-----------

In preparation for the beta release, all uploads are queued and subject to manual approval by the release team. Changes to packages that affect beta release images (flavours included) require the release team's approval before uploading. Uploads for packages that do not affect images are generally accepted as time permits.

.. tip::
    Use the :manpage:`seeded-in-ubuntu(1)` tool, provided by the ``ubuntu-dev-tools`` package, to list all the current daily images containing a specified package or to determine whether the specified package is part of the supported seed.

    If the list output is empty, uploading it during a freeze should be safe.

The freeze allows Archive Admins to fix package inconsistencies or critical bugs quickly and in an isolated manner. Once the beta release is shipped, the Beta Freeze restrictions no longer apply.


.. _kernel-freeze:

Kernel Freeze
-------------

The Kernel Freeze is the final date for kernel updates because they require several lockstep actions that must be folded into the image-building process.

Exceptional circumstances may justify exemptions to the freeze at the discretion of the release managers.


.. _non-language-pack-translation-deadline:

Non-language-pack translation deadline
--------------------------------------

Some translation data cannot currently be updated via the language pack mechanism. Because these items require more disruptive integration work, they are subject to an earlier deadline to give time to developers to manually export translations from Launchpad and integrate them into the package.

This marks the date after which translations for such packages are not guaranteed to be included in the final release. Depending on the package and its maintainers workflow, they may be exported later.

Other packages can still be translated until the :ref:`language-pack-translation-deadline`.


.. _final-freeze:

Final Freeze
------------

This freeze marks an **extremely** high-caution period until the :ref:`final-release`. Only bug fixes for release-critical, security-critical or otherwise exceptional circumstantial bugs are included in the Final Release, which the release team and relevant section teams must confirm.


Unseeded packages
~~~~~~~~~~~~~~~~~

Packages in :ref:`archive-components-universe` that aren't seeded in any of the Ubuntu flavours remain in :ref:`feature-freeze-ff` because they do not affect the release; however, when the Ubuntu package archive is frozen, fixes must be manually reviewed and accepted by the release team members.

When the Final Release is close (~1.5 days out), developers should consider uploading to the :ref:`proposed pocket <archive-pockets-proposed>`, from which the release team cherry-picks into the :ref:`release pocket <archive-pockets-release>` if circumstances allow. All packages uploaded to the proposed pocket that do not make it into the release pocket until the Final Release become candidates for :ref:`stable-release-updates`. Therefore, uploads to the proposed pocket during Final Freeze should meet the requirements of Stable Release Updates if the upload is not accepted into the release pocket. In particular, the upload must reference at least one bug, which is used to track the stable update.

.. note::
    If you are sure that your upload will be accepted during Final Freeze, you can upload directly to the release pocket, but be aware that you have to re-upload after Final Release if the upload gets rejected.


.. _release-candidate:

Release Candidate
-----------------

The images produced during the week before the :ref:`final-release` are considered "release candidates". In an ideal world, the first release candidate would end up being the Final Release; however, we don't live in a perfect world, and this week is used to get rid of the last release-critical bugs and do as much testing as possible. Until the Final Release, changes are only permitted at the release team's discretion and will only be allowed for high-priority bugs that might justify delaying the release.


.. _language-pack-translation-deadline:

Language pack translation deadline
----------------------------------

Translations done up until this date are included in the final release's language packs.


.. _further-reading:

Further reading
---------------

- :ref:`freeze-exceptions`
- :ref:`request-a-freeze-exception`

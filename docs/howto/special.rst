Special types of SRU
--------------------

This section is for the special types of SRU listed at
:ref:`Reference → Special types of SRU <reference-special-types-of-sru>`.

.. _howto-request-package-specific-non-standard-process:

Request a package-specific non-standard process
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This hasn't been transferred into the new documentation yet. See
https://wiki.ubuntu.com/StableReleaseUpdates#Documentation_for_Special_Cases
for now.

.. _howto-stage-upload:

Stage an upload
~~~~~~~~~~~~~~~

See also: :ref:`Explanation → Special types of SRU → Staging low priority
uploads <explanation-staged-uploads>`

1. Follow the usual process but additionally add a
   block-proposed-<series> tag to at least one of the SRU bugs together
   with a comment explaining the reason for the staging. Staging can
   also be added retrospectively simply by adding the tag; this can be
   done at any time before an SRU is released. If you do so, please make
   sure that you add a bug comment that explains the reason.
2. Ensure that you perform SRU verification as normal as soon as the
   package is accepted into proposed.

Land an upload blocked by staging
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See also: :ref:`Explanation → Special types of SRU → Staging low priority
uploads <explanation-staged-uploads>`

In principle the block-proposed-<series> tag should be removed by an SRU
team member when accepting a newer upload not planned for further
staging. But if they overlook this, it's appropriate for whoever notices
it (SRU team, or uploader) to remove the block-proposed-<series> tag
with a suitable comment when it no longer applies.

.. _howto-remove-package:

Remove a package
~~~~~~~~~~~~~~~~

See also:

-  :ref:`Explanation → Special types of SRU → Removals <explanation-removals>`
-  :ref:`Reference → Historical removals <reference-historical-removals>`

Steps for the uploader
^^^^^^^^^^^^^^^^^^^^^^

1. If appropriate depending on the reason for the removal, ensure that
   the package is also removed in the development release and any
   releases subsequent to the release being targetted.
2. Construct an essentially empty package with an appropriate
   explanation in NEWS and a corresponding critical debconf note. Follow
   the pattern used previously (see :ref:`the list of historical
   removals <reference-historical-removals>`).
3. Create an SRU tracking but with an appropriate explanation.
4. `Write to the technical
   board <https://lists.ubuntu.com/mailman/listinfo/technical-board>`__
   for approval.
5. Upload as normal

Steps for the SRU reviewer:
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Check the above list has been performed correctly, and that the
   Technical Board has approved
2. Document in the :ref:`list of historical removals
   <reference-historical-removals>`.
3. Process the SRU as normal.

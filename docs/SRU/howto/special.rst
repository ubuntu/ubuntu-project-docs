Special types of SRU
--------------------

This section is for the special types of SRU listed at
:ref:`Reference → Special types of SRU <reference-special-types-of-sru>`.

.. _howto-request-package-specific-non-standard-process:

Request a package-specific non-standard process
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See :ref:`package-specific notes <reference-package-specific-notes>`
for existing package specific exceptions. To add a new one please provide a
pull request against the repository of this documentation, adding a new
exception following the same pattern established by the others.
See the footer on each page to find the source of it in the version
control system.

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

.. _howto-new-queue:

SRU uploads hitting the NEW queue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See also: :ref:`Explanation → Special types of SRU → NEW queue in the SRU context <explanation-new-queue>`

Some steps of the normal :ref:`SRU pipeline <explanation-sru-pipeline>` are
different in these cases.

New binary
^^^^^^^^^^

#. Step 3 of the :ref:`SRU pipeline <explanation-sru-pipeline>` changes in
   regard to the binary not immediately making it to the -proposed pocket after
   being built.
#. Communicating on the bug is important, but the SRU member shall not yet ask
   for verification in -proposed as it is not yet available there.
#. Once evaluated and accepted by an Archive Admin the new binary will be in
   -proposed and the usual SRU flow can continue asking for verification.

New source
^^^^^^^^^^

#. Step 2 of the :ref:`SRU pipeline <explanation-sru-pipeline>` changes as the
   upload first shows up in the NEW queue. But once an Archive Admin would
   accept from the NEW queue it would directly move to -proposed implying the
   need for pre-coordination between the two roles.
#. Ensure there is a tracking bug, it will help to coordinate the approvals,
   later allow to audit why things were done, and allow the late part of this
   process to follow the normal SRU steps people are used to.
#. The archive admin evaluates the case and states the confirmation to be
   approved in regard to the NEW queue processing on the bug.
#. The SRU member evaluates the case and states the confirmation to be approved
   in regard to the SRU rules on the bug.
#. Once both agree the Archive admin will accept from the new queue.
#. The source package will appear in -proposed and start to build.
#. Built binaries then show up in the NEW queue and are accepted from there
   again landing in -proposed
#. Form here on we are back in the normal path at the end of step 3 of the
   :ref:`SRU pipeline <explanation-sru-pipeline>`. The SRU member can do the
   normal communication and status updates on the bug as if it would have been
   accepted from -unapproved.

   #. To do so the following command line can be used to add the standard
      "package accepted" comment to the bug, and adjust the verification tags:
      :code:`sru-accept -s <release>-proposed -p <source-pkg> -v <version> <bug-number>`.
      The script can be found in the `ubuntu-archive-tools git repository
      <https://code.launchpad.net/~ubuntu-archive/ubuntu-archive-tools/+git/ubuntu-archive-tools>`_.

.. _howto-unblock-staging:

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
   releases subsequent to the release being targeted.
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

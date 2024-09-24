Non-standard Processes
----------------------

.. _explanation-package-specific-non-standard-processes:

Package-specific non-standard processes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a package or set of packages requires deviation from our standard
process, but we expect to routinely deviate in the same way for
subsequent updates to the same packages, we document these deviations
under :ref:`package-specific notes <reference-package-specific-notes>`.
This allows us to be consistent in our approaches to review, QA and
release. If the package-specific note has been approved by one member of
the SRU team, other SRU team members will try to honour that previous
approval when reviewing.

.. _explanation-staged-uploads:

Staging low priority uploads
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SRUs for bugs which do not affect users at runtime are inappropriate to
force users to apply. There is a cost to our users (and our mirror
network) for downloading updates of packages, which should be balanced
against the utility of the update to the user downloading it.

However, if such an update otherwise complies with SRU policy, it can be
staged to be bundled with a future SRU or security update.

It is essential to carry out SRU verification on all related bugs as
usual as soon as the upload enters the proposed pocket. We do not want
to burden a future SRUer with verification of your low priority bug. If
timely verification is not performed, then as usual the staged upload is
a candidate for deletion, and a future SRUer is quite entitled to base
their upload on the version prior to your staged upload instead. If this
happens, the future SRU will not include your changes, effectively
cancelling the staging.

Since we try to avoid regressing users on upgrade to a new release, it
is essential to carry out this SRU verification for every affected bug
series task. If you skip verification of one series then staged uploads
in all series are candidates for deletion or overriding as above at the
discretion of the SRU team.

See also:

- :ref:`How-to → Stage an upload <howto-stage-upload>`
- :ref:`How-to → Land an upload blocked by staging <howto-unblock-staging>`

.. _explanation-new-queue:

NEW queue in the SRU context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SRU policy does not forbid uploading a new source or binary to active
releases. But if that happens it needs double approval. One of an archive-admin
for the aspect of `NEW queue processing
<https://wiki.ubuntu.com/ArchiveAdministration#NEW_Processing>`__ and that of a
SRU member for the regression evaluation.

While that can be done as a single step by the few people wearing both roles at
once, that is not always possible. Hence the process is defined as cooperation
between members of both teams.

This case can come in two variants:

- new binary: An upload has been evaluated by the SRU member and was accepted
  from the Unapproved queue. But that upload now builds a new binary which will
  hit the NEW queue of the respective release.
- new source: An upload of a new source hits the NEW queue of an active release.

See also:

- :ref:`How-to → Process the NEW queue in the SRU context <howto-new-queue>`

.. _explanation-removals:

Removals
~~~~~~~~

While it is always preferable to fix a package, rather than drop it,
there are rare cases when a universe package becomes actively
detrimental in stable releases: If it is unmaintained in Ubuntu and has
unfixed security issues or has been broken because of changing network
protocols/APIs, it is better to stop offering it in Ubuntu altogether
rather than continuing to encourage users to install it.

It is not technically possible to remove a package from a stable
release, but this can be approximated by SRUing an essentially empty
package with an appropriate explanation in NEWS and a corresponding
critical debconf note.

When a package is removed in this way from a stable release, it may need
similar removal from the devel release as well, depending on the
justification for removal.

See also:

-  :ref:`How-to → Remove a package <howto-remove-package>`
-  :ref:`Reference → Historical removals <reference-historical-removals>`

.. _explanation-security:

Security updates
~~~~~~~~~~~~~~~~

Since some users choose to receive security updates but not SRUs, if a
proposed SRU appears to fix security issues, it should be considered for
the `security update process
<https://wiki.ubuntu.com/SecurityTeam/UpdateProcedures>`__ first
instead.

Sometimes an issue being fixed may or may not be a security issue
depending on opinion, or the security team may otherwise consider it not
appropriate for the -security pocket. In this case, the SRU process may
be used to fix the issue if the change being made otherwise meets
:ref:`SRU criteria <reference-what-is-acceptable-to-sru>`.

Freezes and release opening
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  After final freeze, the release team may decline to accept changes,
   so uploaders should assume that they will become SRUs and include bug
   references. They must provide SRU documentation if they become SRUs.
   See the freeze announcement from the release team for details.
-  After release, the development release will not yet have opened, but
   uploaders may need SRUs regardless.

   -  *How to do this*
   -  [this section needs cleaning up]

-  The release team will do a copy-forward-en-masse and then hand queue
   management of the just-released updates pocket to the SRU team. From
   this point on, uploaders should upload to the new development
   Unapproved queue when needed for SRU process, even though it hasn't
   yet opened.

Removal of languishing updates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a bug fixed by an update does not get any testing or verification
feedback for 90 days an automated call for testing comment will be made
on the bug report. In the event that there is still no testing after an
additional 15 days (a total of 105 days without any testing), the Stable
Release Managers will remove the package from -proposed and usually
close the bug task as "Won't Fix", due to lack of interest. Removal will
happen immediately if a package update in -proposed is found to
introduce a nontrivial regression.

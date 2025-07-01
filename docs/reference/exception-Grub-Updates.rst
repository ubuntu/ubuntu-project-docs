.. _reference-exception-GrubUpdates:

.. _process_for_sruing_grub:

Process for SRUing GRUB
=======================

There is no SRU "exception" for GRUB. Criteria for acceptance remains
the same as normal under our usual policies. However, GRUB requires
special handling to actually build and release it, due to our EFI
signing pipeline as follows. This isn't yet fully documented, but this
should do as a stopgap to avoid a bottleneck on release.

Scope: the grub2, grub2-unsigned and grub2-signed source packages (?is
this correct?)

-  An Archive Admin is required to do the initial review and accept and
   must not do this unless they have received training. This involves
   verifying that the package was built correctly in the appropriate
   special purpose archive that has the appropriate signing keys
   attached, been copied over to the archive unapproved queue, etc.

-  Any SRU team member can release these packages but only when:

   -  They verify that it was an Archive Admin that originally
      accepted it.

   -  The Launchpad ``Done`` queue should list who accepted the upload; for example: `<https://launchpad.net/ubuntu/jammy/+queue?queue_state=3&queue_text=grub2>`__
   -  `List <https://launchpad.net/~ubuntu-archive/+members#active>`__ of active members of the Ubuntu Packge Archive Administrators team.

-  They have check for correct verification as for a normal SRU.

-  They release them together as required (which sru-release also
   enforces; don't override it!)

Related SRU Interest Team
-------------------------

Grub has a :ref:`SRU Interest Team <reference-sru-interest-team>`,
please subscribe the
`Interest group <https://launchpad.net/~sru-verification-interest-group-grub>`__
to the SRU bug early on.

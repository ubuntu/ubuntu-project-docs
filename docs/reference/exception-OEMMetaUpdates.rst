PROPOSAL
========

NOT APPROVED YET, BEING DRAFTED.

Introduction
============

These packages exist to hint parts of the installer / upgrade tooling
that the running hardware is certified, and should have certain packages
installed.

They follow the naming scheme \`oem-\*-meta\`.

Possible situation that need update meta package and then SRU it.

-  kernel flavour change
-  add modaliases per customer request.
-  modification due to spec change. (the way installer need it, etc)

.. _sru_bug_template:

SRU Bug template
================

[ Background ]

Why are we making this update?

[ Impact ]

#. Upgrade path: Users will be upgrading from a package in the
   associated OEM archive, not the Ubuntu archive.

| ``2. The background and impact of the situation for this change, and it's``
| ``   impact. ``

[ Testing ]

#. Test that \`ubuntu-drivers list-oem\` lists the meta-package on the
   relevant hardware

| ``2. Test that fully installing the meta-package (upgrading to the OEM archive if relevant) works properly on the  hardware``
| ``3. Do an offline install. Boot the system. Run update-manager. Check that an upgrade to the OEM package is offered and that it completes successfully and the hardware works properly.``

[ Regression Potential ]

Most potential regressions will live in the package set that will be
installed via dependency of this package, which live in OEM archive
(outside of Ubuntu) and control by OEM team. OEM team and other
corresponding team need take responsibility of those dependency
installed.

[When switching kernel flavour] Check that the new kernel flavour works
on the target platform.

Procedure
=========

There is `an existing MIR exception <MIRTeam/Exceptions/OEM>`__,
allowing these packages to be accepted directly into main. As long as
the package complies with the template required for the MIR exception to
apply, it can be similarly accepted into \`-proposed\` without further
review. SRU team members can use the script
\`oem-metapackage-mir-check\` from \`lp:ubuntu-archive-tools\` to
satisfy themselves that this is the case.

Canonical's Commercial Engineering team are expected to perform the
required testing as outlined in the template above. This must be done on
the package \*as it exists in the Ubuntu archive\*, so after acceptance
into \`-proposed\`. Providing this is done, the 10-day aging period does
not apply.

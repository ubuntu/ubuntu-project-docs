Handle a regression
-------------------

.. _howto-report-regression:

Report a regression
~~~~~~~~~~~~~~~~~~~

If a package update introduces a regression which already made it
through the verification process to -updates, please **immediately**
ensure that a separate bug exists for the issue by filing one as needed,
and add the tag regression-update to the bug.

If the regression *only* applies to the package in -proposed, please
follow up to the bug with a detailed explanation, and tag the bug with
regression-proposed. To ensure that the package doesn't accidentally get
released, add a comment to an existing bug and change the appropriate
tag to verification-<series>-failed.

.. _howto-handle-regression-report:

Handle a regression report
~~~~~~~~~~~~~~~~~~~~~~~~~~

See also: :ref:`Explanation → Standard Processes → Regressions
<explanation-regressions>`

This is the playbook to follow when there is a concern about a
regression that has taken place in the updates pocket, such that a user
receiving the recommended updates within a stable release is regressed
somehow. Regressions that have taken place elsewhere (e.g. during a
release upgrade, in the security pocket, in the proposed pocket or in
Pro-specific repositories) are out of scope.

Uncertainty phase
^^^^^^^^^^^^^^^^^

Actions to take
'''''''''''''''

-  All: ensure that a separate bug report exists and that it is tagged
   regression-update.
-  All: ensure that the most relevant bug related to the update has a
   comment stating that a regression is suspected, linking to the
   regression bug.
-  Ubuntu developers: if you think the situation warrants moving to the
   alert phase, contact an SRU team member.

Examples of why we may be stuck in this phase:

-  Reports may not have all the necessary information
-  We are not confident in the reliability of the information available
   to us
-  The regression can not be reproduced (in by itself, this is not
   enough reason to doubt it, though)

Alert phase
^^^^^^^^^^^

Roles
'''''

-  An SRU team member should be nominated to drive decision-making.
-  It is expected that further technical investigation is carried out by
   the Ubuntu developer who uploaded the update in question, by a
   sponsoree under their supervision, or by some other Ubuntu developer
   delegated by them or their team. However, in their absence, anyone
   may assume this role. Please coordinate with the nominated SRU team
   member.

Actions to take
'''''''''''''''

-  Nominate an SRU team member who will coordinate and ensure that they
   are available and their name is communicated.
-  Nominate the technical investigator, ensure that they are available
   and that their name is communicated.
-  If phasing is still in progress then `find an
   AA <https://launchpad.net/~ubuntu-archive/+members#active>`__ to stop
   phasing, since this is considered easy and risk-free.

Examples of why we may be stuck in this phase:

-  The source package that caused the regression has not been
   confidently identified.

Action phase
^^^^^^^^^^^^

Roles
'''''

-  An SRU team member should be nominated to drive decision-making.
-  It is expected that preparation of the reverting upload and
   subsequent SRU verification is carried out by the Ubuntu developer
   who uploaded the regressing update in question, by a sponsoree under
   their supervision, or by some other Ubuntu developer delegated by
   them or their team. However, in their absence, anyone may assume this
   role. Please coordinate with the nominated SRU team member.

Actions to take
'''''''''''''''

-  Verify that there is no reason to think that an exact revert won't
   exacerbate the issue. For example, if it's a postinst failure due to
   an upgrade path problem, or some other latent bug triggered by the
   action of updating itself, then an exact revert is probably not
   appropriate. In this case, these instructions end and you will need
   to solve the problem according to your best judgement. See also:
   :ref:`Explanation → Standard Processes → Regressions → Exceptions
   that justify pushing ahead <explanation-regressions-pushing-ahead>`.
-  Otherwise, upload an exact revert of the regressing update for
   immediate release to updates as soon as appropriate QA is completed,
   bypassing the usual ageing period. If possible, one SRU team member
   and one other Ubuntu developer should work together (or one reviewing
   the other) to minimise the risk of mistakes or unforeseen
   consequences. However, if nobody is available, the SRU team member
   may release their own work alone.

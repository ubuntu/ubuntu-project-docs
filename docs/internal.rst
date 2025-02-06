Internal SRU team docs
======================

Decision making
---------------

-  Act for the team if you're confident that the team would concur
-  If unsure, ask, and if you need to follow up, add to the SRU team
   meeting agenda where we can make a team decision

Reviewing procedure and tools
-----------------------------

If you are a member of the `SRU reviewing team <https://launchpad.net/~ubuntu-sru>`__,
you should check out the `ubuntu-archive-tools <https://launchpad.net/ubuntu-archive-tools>`__
scripts with

.. code::

   git clone https://git.launchpad.net/ubuntu-archive-tools

which greatly simplifies the reviewing procedure. You should symlink
``sru-review`` and ``sru-accept`` somewhere to your ``~/bin/`` directory for easy
access, or put the checkout into your ``$PATH``.

The following review procedure is recommended:

-  Open the unapproved queue for a particular release, e.g.
   `Upload queue <https://launchpad.net/ubuntu/precise/+queue?queue_state=1>`__
   for noble. This shows the list of SRU uploads which have to be
   reviewed, commented on, and approved/accepted/rejected.
-  For each package, generate the debdiff to the current version in the
   archive and open the corresponding bugs:

   .. code::

      sru-review -s noble gnash

   This opens all the bugs which are mentioned in the .changes file in
   the browser, and will generate a debdiff between the current archive
   and the unapproved upload (unless the ``orig.tar.gz`` changes this will
   only download the two ``diff.gz``, so it is reasonably fast).

   -  In case the SRU is a package sync instead of a standard upload,
      the ``sru-review`` tool will not be able to fetch the debdiff for you
      and will exit with an error. You will have to review the changes
      manually and then re-run the tool with an additional argument of
      ``--no-diff``.

-  Review the bugs for complete description, justification, check that
   they have a stable release task, conform to SRU rules, etc,
   and comment accordingly.
-  Scrutinise the debdiff for matching the changes in the bugs, not
   having unrelated changes, etc. If you have doubts, comment on the
   bug.
-  *If you are in the ubuntu-sru team:*

   -  Exit the tool you are using to review the debdiff
   -  If the bugs and debdiff are okay, accept the package by pressing :kbd:`y`
      at the "Accept the package into -proposed?" prompt.
      This will tag the bug(s) with verification-needed,
      verification-needed-$RELEASE, subscribe ubuntu-sru, and add a
      general "please test and give feedback"-like comment.
   -  If the upload is broken or unsuitable for an SRU, reject it by
      pressing N at the "Accept the package into -proposed?" prompt and
      pressing y at the "REJECT the package from -proposed?" prompt.

-  *If you are not in the ubuntu-sru team:* Send a follow up comment to
   the bugs:

   -  If all is okay: send an "ubuntu-sru approved and reviewed" comment
      and set the task to "In Progress"
   -  If something is wrong: send the feedback to the bug and set the
      task to "Incomplete"

The `pending SRUs <http://people.canonical.com/~ubuntu-archive/pending-sru>`__ should
also be reviewed to see whether or not there are any to be released or
removed from the archive. The process for dealing with these follows:

Packages in -proposed can be moved to -updates once they are approved by
someone from sru-verification, and have passed the minimum ageing period
of **7 days**. Use the ``sru-release`` script from ubuntu-archive-tools for
this:

.. code::

   $ ./sru-release noble kdebase

Please see ``--help``, you can also use this tool to copy packages to
-security and to the current development release. N.B. before copying a
package to -security ping a member of the
`ubuntu-security <https://launchpad.net/~ubuntu-security/+members>`__
team.

-  `Currently pending SRUs <http://people.canonical.com/~ubuntu-archive/pending-sru.html>`__

If a package should be removed from -proposed, use the ``remove-package``
tool (from ``ubuntu-archive-tools``). e.g., to remove source and binaries
for the ``libreoffice`` package currently in ``xenial-proposed``:

.. code::

   $ ./remove-package -m "SRU abandoned (verification-failed)" \
     -s noble-proposed libreoffice

.. _internal-override-phasing:

Override phasing
----------------

*Overriding phasing can only be performed by a member of the SRU team.*

Overriding halted phasing is done in a similar way to overriding
autopkgtest failures. The phased update machinery looks at
`phased-update-overrides.txt <https://bazaar.launchpad.net/~ubuntu-sru/ubuntu-archive-tools/phased-update-overrides/view/head:/phased-updates-overrides.txt>`__,
which is a simple CSV file containing lines of the form

.. code::

   *source package*, *version*, *THING_TO_IGNORE*

where ``*THING_TO_IGNORE*`` can either be an
errors.ubuntu.com problem URL to ignore or *increased-rate*.

If there are multiple errors to ignore, just repeat the line with the same source package name, version, and then the other error to ignore.

To make a change, please create a bzr merge proposal against lp:~ubuntu-sru/ubuntu-archive-tools/phased-update-overrides.

Adding members to the team
--------------------------

Onboarding
~~~~~~~~~~

-  Existing SRU team members identify when new team members are needed.
   Suggestions can be made, but ultimately the SRU team members will privately
   identify and acknowledge candidates.

-  To join the team a candidate first becomes an SRU Assistant (formerly
   sometimes called trainee). This requires the usual full time committment,
   but not yet any privileges.

-  In that state one existing team member will onboard a given new assistant,
   "sponsoring" privileged SRU actions such as review accept and release.

-  After an inital training session this is usually done by fully shadowing
   and assisting in the shift of that existing team member being their mentor.

-  This mentor will confer with the other existing team members if and when
   they consider the assistant to be ready for full membership:

   - One existing team member will study a candidate's recent SRU activity,
     assess them against our criteria and write a summary.

   - The team will then decide whether the candidate is suitable.

- Once agreed the assitant will be given equivalent privileges, stop shadowing,
  and get assigned their own shift.


Criteria for new SRU team members
---------------------------------

Hard requirements
~~~~~~~~~~~~~~~~~

-  Must be able to upload all SRUs they expect to review; i.e. Ubuntu
   Core Developer or SRU Developer. A member of the SRU team who is an
   SRU Developer is expected to be in the process of applying to be an
   Ubuntu Core Developer: the role involves exercising judgement about
   whether a change in the development series is **good**, and therefore
   someone in this role should be formally trusted by the project to
   make such decisions for the development series as well.

-  Recent track record of good quality SRUs.

-  Recent uploads (whether sponsored or not) either met our expectations
   or successfully anticipated concerns that could reasonably have been
   predicted by existing SRU team members.

-  Few recent poor quality SRUs (nice to have: none). This includes
   uploads for issues that are unsuitable for SRU, as well as missing
   SRU information, missing bug references, poorly completed SRU
   information, etc. Exception: if an omission or concern is called out
   by the uploader and the upload was for the purpose of asking the SRU
   team about it.

-  Can they say no?

Nice to haves
~~~~~~~~~~~~~

-  Demonstrated familiarity **across** existing SRU policies and
   procedures (rather than just having correctly submitted good SRUs
   that might be limited in parts of SRU policy and procedure that they
   exercise)

-  What about SRUs they've sponsored: do they successfully raise the
   quality of SRU submissions to our expected level before they sponsor
   them? If so, then this might be a good indicator that they'll be able
   to do similar at SRU review time.

-  Do they have a track record of spotting issues before they occur? How
   broadly do they look when determining "Where problems could occur"?
   Do they then make sure the Test Plan covers identified risks?

-  Do they seek to change general policy when appropriate, rather than
   ignoring it? Can they identify the difference between individual
   exceptions and the general case?

-  Previous activity as an SRU representative helps a lot to pick up most of
   these aspects ahead of time as well as building a better general
   understanding and a personal relationship with the existing SRU team.

.. _stable-release-updates:

Stable Release Updates
======================

To fix newly discovered bugs and make updates after the publication of an :term:`Ubuntu Stable Release`, use the **Stable Release Update (SRU)** process.

The SRU process ensures that any changes made to a stable release are thoroughly vetted and tested before being made available to users. This is because many users rely on the stability of the stable release.

.. TODO SRU link

This section provides a brief introduction to the SRU process. See the dedicated SRU documentation for more details about this process.


When is SRU necessary
~~~~~~~~~~~~~~~~~~~~~

SRU requires caution because it's automatically recommended to a large number of users. So, when you propose an update, there should be a strong rationale for it. Also, the update should present a low risk of :ref:`regressions`.

You can propose an SRU in the following cases:

- To fix high-impact bugs, including those that may directly cause security vulnerabilities, severe regressions from the previous release, or bugs that may directly cause loss of user data.
- To adjust to changes in the environment, server protocols, or web services. This ensures that Ubuntu remains compatible with evolving technologies.
- For safe cases with low regression potential but high user experience improvement.
- To introduce new features in :term:`LTS releases <LTS>`, usually under strict conditions.
- To update commercial software in the :term:`Canonical partner archive`.
- To fix :term:`Failed to build from Source` issues.
- To fix :term:`autopkgtest` failures, usually in conjunction with other high-priority fixes.


Overview
~~~~~~~~

A typical SRU is performed like this:

1. Ensure the bug is fixed in the :term:`current development release <Current Release in Development>` and all subsequent supported releases to ensure consistency across different Ubuntu versions, especially preventing regressions when users upgrade to newer releases.
#. Update the **existing** bug report detailing the Impact of the Bug, the Test Plan to verify that the bug was fixed and highlight where problems could occur.
#. Get the package with the SRU patch into the upload queue.
#. The SRU team then reviews from the unapproved queue. When the upload is ready, the SRU team accepts the upload into the proposed pocket.
#. Once the builds are ready, autopkgtest are triggered. Test the binaries in the :term:`Ubuntu Archive` and follow up in the bug report with your verification results.
#. The Ubuntu SRU Team evaluates the testing feedback and moves the package into :ref:`updates <archive-pockets-updates>` after it passes a minimum aging period of 7 days without regressions.


Verification
^^^^^^^^^^^^

Once the SRU team accepts the SRU into the proposed pocket, the SRU has to be verified by the reporter or affected users of the SRU bug in a software environment that closely resembles the state after the SRU team copies the package to the updates pocket. Generally, this is with a system that's up to date with the release, security, and updates pockets. It shouldn't include other packages from the proposed or backports pocket, except commonly-installed packages built from the affected source package.


SRU phasing
^^^^^^^^^^^

Once a package is released to the updates pocket, the update is then phased, so it is gradually made available to expanding subsets of Ubuntu users.


.. _regressions:

Regressions
^^^^^^^^^^^

Regressions are unintended negative consequences that updates introduce. They appear as new bugs or failures in previously well-functioning aspects of an Ubuntu release.


Updates removal
^^^^^^^^^^^^^^^

If a bug fixed by an update doesn't get any testing or verification feedback for 90 days, an automated "call for testing" comment is made on the bug report. If no testing occurs within an additional 15 days, totaling 105 days without any testing, the :term:`Stable Release Managers` removes the package from proposed and close the bug task as **Won't Fix**.

Also, updates are removed from proposed if they introduce a non-trivial regression.


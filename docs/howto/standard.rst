.. _howto-perform-standard-sru:

Perform a standard SRU
----------------------

This how-to is for standard SRUs, where straightforward bugs are fixed
using minimal cherry-picks. For other types of SRUs, see :ref:`How-to →
Prepare a special type of SRU <howto-prepare-special-sru>` instead.

1.  Check that the upload complies with :ref:`Reference → Requirements →
    What is acceptable to SRU <reference-what-is-acceptable-to-sru>`.
2.  If this is not a straightforward set of bugs being fixed by minimal
    cherry-picks, see :ref:`How-to → Prepare a special type of SRU
    <howto-prepare-special-sru>` first.
3.  Check for compliance against :ref:`Reference →
    General requirements for all SRUs <reference-general-requirements>`
4.  Document the SRU, starting with the :ref:`SRU Bug Template
    <reference-sru-bug-template>` and following and ensuring compliance
    against the :ref:`documentation requirements
    <reference-documentation-requirements>`
5.  Prepare the upload, ensuring compliance against :ref:`Reference →
    Requirements → Upload. <reference-upload-requirements>` If you do
    not have access to upload to the Ubuntu package archive yourself,
    you may prepare this in the form of a debdiff or a git-ubuntu
    branch.
6.  If you:

    1. have a debdiff, then `request
       sponsorship <https://wiki.ubuntu.com/SponsorshipProcess>`__ by
       attaching the debdiff and subscribing 'ubuntu-sponsors' to one
       bug.
    2. have a git-ubuntu branch, then request sponsorship by filing a
       merge proposal and ensuring that the ubuntu-sponsors team has
       been requested to review it.
    3. have access to upload to the Ubuntu package archive directly,
       then go ahead and upload, and set the relevant bug task status to
       In Progress.
    4. are sponsoring an upload for someone else, then check that the
       above steps have been performed correctly, iterate or fix up as
       necessary, ensure that you are subscribed to all referenced bugs,
       upload, and set the relevant bug task statuses to In Progress.

7.  Wait for review, following any instructions you are given. If you
    wish, you can follow progress through the :ref:`SRU pipeline
    <explanation-sru-pipeline>` using the various :ref:`status pages
    <reference-status-pages>`.
8.  After the package is accepted into -proposed, you will be asked to
    execute your Test Plan against the built packages. Please do so,
    using bug comments to report your results. Once done, change the bug
    tags according to the instructions given.
9.  Subscribe yourself to bugmail for the package in Launchpad, if you
    haven't done so already, and monitor Launchpad for bug reports
    relating to the update for at least one week following release of
    the package.
10. If you find a regression, follow :ref:`Howto → Report a regression
    <howto-report-regression>`. If someone else reports a regression,
    please also follow :ref:`Howto → Report a regression
    <howto-report-regression>` and ensure that all steps documented
    there have been performed correctly.

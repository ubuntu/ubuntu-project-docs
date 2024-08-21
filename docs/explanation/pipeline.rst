.. _explanation-sru-pipeline:

Overview of the SRU pipeline
----------------------------

1. An SRU driver prepares the relevant bugs with the necessary
   documentation and makes an SRU upload available.
2. When an SRU is uploaded by a developer with upload access to the
   Ubuntu package archive, it enters the "Unapproved" queue, which you
   can see here: https://launchpad.net/ubuntu/jammy/+queue?queue_state=1
   (modify for different series as needed).
3. The SRU team will then review from the Unapproved queue,
   communicating in the bug as necessary. When ready, the upload is
   *accepted* into the -proposed pocket, and then built. Once accepted
   into -proposed, its status appears in the `Pending SRU
   Report <https://ubuntu-archive-team.ubuntu.com/pending-sru.html>`__
   when the report is next generated.
4. Once builds are ready, the agreed QA steps are performed on the
   package build using the -proposed pocket, with results being posted
   to the relevant bugs as comments. The `Pending SRU
   Report <https://ubuntu-archive-team.ubuntu.com/pending-sru.html>`__
   tracks progress on this, as well as any other blockers detected, such
   as build or test failures.
5. Once the `Pending SRU
   Report <https://ubuntu-archive-team.ubuntu.com/pending-sru.html>`__
   displays all outstanding tasks as reported to be resolved, the SRU is
   ready to be released. The SRU team regularly reviews the report. For
   packages marked as ready, they review the corresponding bug comments,
   ensure that all agreed QA steps have been performed satisfactorily
   and that there are no outstanding blockers. If satisfied, they
   *release* packages into the -updates pocket.
6. The SRU is now complete. If a regression is found, see :ref:`How-to →
   Handling regressions <howto-handle-regression-report>` for next steps.

See also: :ref:`Reference → Status Pages <reference-status-pages>`

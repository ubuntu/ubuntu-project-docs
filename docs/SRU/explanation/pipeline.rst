.. _explanation-sru-pipeline:

Overview of the SRU pipeline
----------------------------

1. An SRU driver prepares the relevant bugs with the necessary
   documentation, using the :ref:`reference-sru-bug-template`,
   and makes an SRU upload available.
2. When an SRU is uploaded by a developer with upload access to the
   Ubuntu package archive, it enters the "Unapproved" queue, which you
   can see here: `Upload queue <https://launchpad.net/ubuntu/jammy/+queue?queue_state=1>`__
   (modify for different series as needed).
3. The SRU team will then review both the upload in the Unapproved queue,
   *and* the SRU documentation on each bug. As necessary, the SRU team
   will leave comments about the upload or SRU documentation on the relevant
   bug. When ready, the upload is *accepted* into the -proposed pocket, and
   then built. Once accepted into -proposed, its status appears in the
   `Pending SRU Report <https://ubuntu-archive-team.ubuntu.com/pending-sru.html>`__
   when the report is next generated.
4. Once builds are ready, the agreed QA steps are performed on the
   package build using the -proposed pocket, with results being posted
   to the relevant bugs as comments. The `Pending SRU Report <https://ubuntu-archive-team.ubuntu.com/pending-sru.html>`__
   tracks progress on this, as well as any other blockers detected, such
   as build or test failures.
5. Once the `Pending SRU Report <https://ubuntu-archive-team.ubuntu.com/pending-sru.html>`__
   displays all outstanding tasks as reported to be resolved, the SRU is
   ready to be released. The SRU team regularly reviews the report. For
   packages marked as ready, they review the corresponding bug comments,
   ensure that all agreed QA steps have been performed satisfactorily
   and that there are no outstanding blockers. If satisfied, they
   *release* packages into the -updates pocket.
6. The SRU is now complete. If a regression is found, see
   :ref:`How-to → Handling regressions <howto-handle-regression-report>` for next steps.

The following diagram illustrates this pipeline:

.. mermaid::
   :align: center

   %%{init: {'themeVariables': {
                'fontSize': '20px',
                'fontFamily': 'Ubuntu'}}}%%
   flowchart TD
       prepare_package["Prepare the bug fix, and the SRU template"]
       unapproved["Upload the package to the unapproved queue"]
       review{"Does the SRU team accept the changes and documentation?"}
       proposed["Package builds in<br>-proposed"]
       build{"Does the package build on all architectures?"}
       verification{"Does the package pass the SRU test plan?"}
       autopkgtest{"Are there autopkgtest regressions triggered by the upload?"}
       age["Package ages in<br>-proposed for minimum 7 days"]
       released(["Package is released<br>to -updates"])
       troubleshoot(["Refer to SRU documentation, or ask SRU team for guidance."])

       prepare_package --> unapproved
       unapproved --> review
       review -- Yes --> proposed
       proposed --> build
       build -- Yes --> verification
       verification -- Yes --> autopkgtest
       autopkgtest -- No --> age
       age --> released

       review -- No --> troubleshoot
       build -- No --> troubleshoot
       verification -- No --> troubleshoot
       autopkgtest -- Yes --> troubleshoot

See also: :ref:`Reference → Status Pages <reference-status-pages>`

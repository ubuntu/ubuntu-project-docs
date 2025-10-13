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

.. graphviz::
   :align: center

   digraph {
        center=true;
        node [
            fontname = "Ubuntu";
            fontsize = "10";
            fixedsize = true;
            height = 1.3;
            width = 2.3;
        ];
        edge [
            fontname = "Ubuntu";
            fontsize = "10";
        ];

        prepare_package [
            label = "Prepare the bug fix,\nand the SRU template";
            shape = rect;
        ];
        unapproved [
            label = "Upload the package to\nthe unapproved queue";
            shape = rect;
        ];
        review [
            label = "Does the SRU team\naccept the changes\nand documentation?";
            shape = diamond;
        ];
        proposed [
            label = "Package builds in -proposed";
            shape = rect;
        ];
        build [
            label = "Does the package build\non all architectures?";
            shape = diamond;
        ];
        verification [
            label = "Does the package pass\nthe SRU test plan?";
            shape = diamond;
        ];
        autopkgtest [
            label = "Are there autopkgtest\nregressions triggered\nby the upload?";
            shape = diamond;
        ];
        age [
            label = "Package ages in -proposed\nfor minimum 7 days";
            shape = rect;
        ];
        released [
            label = "Package is released\nto -updates";
            shape = oval;
        ];
        troubleshoot [
            label = "Refer to SRU documentation,\nor ask SRU team for guidance."
            shape = oval;
        ];

        {
            rank=same;
            review; proposed;
        }
        {
            rank=same;
            troubleshoot; released;
        }

        prepare_package -> unapproved;

        unapproved -> review;

        proposed -> review [ label = "Yes"; dir=back ];
        proposed:s -> build:n;

        build:s -> verification:n [ label = " Yes" ];
        build2 [ shape=point, height=0.01, width=0.01 ];
        {
            rank=same;
            build; build2;
        }
        build -> build2 [ dir=none, label="                   No                   " ];
        review:s -> build2:n [ dir=none, label="\n\n\n  No" ];

        verification:s -> autopkgtest:n [ label = " Yes" ];
        verification2 [ shape=point, height=0.01, width=0.01 ];
        {
            rank=same;
            verification; verification2;
        }
        verification -> verification2 [ dir=none, label="                   No                   "];
        build2 -> verification2[ dir=none ];

        autopkgtest:s -> age:n [ label = " No" ];
        autopkgtest2 [ shape=point, height=0.01, width=0.01 ];
        {
            rank=same;
            autopkgtest; autopkgtest2;
        }
        autopkgtest -> autopkgtest2 [ dir=none, label="                   Yes                  "];
        verification2 -> autopkgtest2 [ dir=none];

        autopkgtest2 -> troubleshoot:n;

        age:s -> released:n;
   }

See also: :ref:`Reference → Status Pages <reference-status-pages>`

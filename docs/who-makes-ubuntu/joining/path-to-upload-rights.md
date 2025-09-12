(path-to-upload-rights)=
# Path to upload rights

```{note}
The links shown on this page are subject to sudden changes over the next
few months as more of the documentation it refers to is migrated here. Please
expect inconsistencies -- and feel welcome to correct any links you believe are
incorrect.
```

This interactive chart shows the skills needed to obtain permissions for
uploading changes to the Ubuntu Package Archive. It can be used as a guide
to help build your applications for upload rights on:

* {ref}`Package Sets <membership-in-packageset>`
* {ref}`MOTU <membership-in-motu>`, 
* {ref}`Core Developer <membership-in-core-dev>`

(upload-path-basics)=
## Basics

These topics will get you started with a good foundation for your future work.

```{mermaid}
block-beta
columns 2
    block
        InitialStudies("Initial studies")
        columns 1
        Concepts{{"<a href=https://github.com/canonical/ubuntu-maintainers-handbook>Concepts</a>"}}
        GitUbuntu{{"git-ubuntu"}}
        DebianPolicy{{"<a href=https://www.debian.org/doc/debian-policy/>Debian Policy</a>"}}
    end

    block
        InitialTasks("Initial tasks")
        columns 1
        BugTriage["Bug triage"]
        BiteSizedBugs["Bite-sized bugs"]
        TrivialPackgeMerges["Trivial package merges"]
    end

    InitialStudies --> InitialTasks

    style InitialStudies fill: #FFDAB9, stroke:#F4A460
    style InitialTasks fill:#FFDAB9, stroke:#F4A460
```

Once your team and/or mentor says you are ready for more, you can move onto the
intermediate tasks.


(upload-path-intermediate)=
## Intermediate

This set of topics and tasks will prepare you to apply for single-package or
package set uploads.

```{mermaid}
block-beta
    columns 2

    block
        IntermediateStudies("Intermediate studies")
        columns 1
        UnderstandDep8{{"<a href=https://salsa.debian.org/ci-team/autopkgtest/blob/master/doc/README.package-tests.rst>Understand DEP8</a>"}}
        ComplexPackageMerges{{"Complex package merges"}}
        SRU{{"<a href=https://canonical-sru-docs.readthedocs-hosted.com/>Study SRU</a>"}}
    end
   
    block
        IntermediateTasks("Intermediate tasks")
        columns 1
        AddAUTOPKGTESTS["<a href=https://canonical-ubuntu-project.readthedocs-hosted.com/contributors/bug-fix/package-tests/>Add Autopkgtest</a>"]
        ProposeMigration["<a href=https://canonical-ubuntu-project.readthedocs-hosted.com/how-ubuntu-is-made/processes/proposed-migration/>Proposed Migration</a>"]
        DoSRUS["Do SRUS"]
    end
    
    %% Transitions
    UnderstandDep8 --> AddAUTOPKGTESTS
    ComplexPackageMerges --> ProposeMigration
    SRU --> DoSRUS

    style IntermediateStudies fill: #FFDAB9, stroke:#F4A460
    style IntermediateTasks fill:#FFDAB9, stroke:#F4A460
```

Once you have done enough of these tasks that your team/mentor says you are
ready to move onto the Advanced topics, you should be ready to apply for PPU
or Package Set. 


(upload-path-advanced)=
## Advanced

```{mermaid}
block-beta
    columns 2

    block
        AdvancedStudies("Advanced studies")
        columns 1

        BlockA(" ")
        BlockB(" ")
        BlockC(" ")

        StudyFFE{{"<a href=https://canonical-ubuntu-project.readthedocs-hosted.com/staging/release-team/freeze-exceptions/>Study FFE</a>"}}
        PlusOne{{"<a href=https://canonical-ubuntu-project.readthedocs-hosted.com/contributors/advanced/plus-one-maintenance/>Study +1</a>"}}
    end

    block
        AdvancedTasks("Advanced tasks")
        columns 1
        UpstreamSubmissionFixes["Upstream submission fixes/features"]
        UpstreamSubmissionDelta["Upstream submission of delta"]
        MilestonesAndExceptions["Milestones and exceptions"]
        DoAnFFE["Do An FFE"]
        PlusOneShadowing["+1 Shadowing"]
    end

    StudyFFE-->DoAnFFE
    PlusOne-->PlusOneShadowing

    style AdvancedStudies fill: #FFDAB9, stroke:#F4A460;
    style AdvancedTasks fill:#FFDAB9, stroke:#F4A460;
    style BlockA fill:transparent,stroke:transparent;
    style BlockB fill:transparent,stroke:transparent;
    style BlockC fill:transparent,stroke:transparent;

```


### (Optional) Activities in Debian

At this point, while you are applying for MOTU, you may also want to branch out
and contribute more to Debian.

```{mermaid}
flowchart LR
    Contribute(("<a href=https://www.debian.org/doc/manuals/maint-guide/>Contribute</a>"))
    DM[["<a href=https://wiki.debian.org/DebianMaintainer>Debian Maintainer</a>"]]
    DD[["<a href=https://wiki.debian.org/DebianDeveloper>Debian Developer</a>"]]

    Contribute --> DM
    DM --> DD
```


(upload-path-expert)=
## Expert 

Once you are a member of MOTU, the following tasks and topics will guide you
towards becoming a Core Developer. Keep doing enough of these tasks until you
have the experience you need to apply for Core Dev.

```{mermaid}
block-beta
    columns 2
    
    block 
        columns 1
        ExpertStudies("Expert studies")

        StudyLibaryTransitions{{"<a href=https://wiki.debian.org/Teams/ReleaseTeam/Transitions>Study Libary Transitions</a>"}}
        StudyPackageTransitions{{"<a href=https://wiki.debian.org/PackageTransition>Study Package Transitions</a>"}}
        BlockA(" ")
        StudyMIR{{"<a href=https://canonical-ubuntu-project.readthedocs-hosted.com/MIR/main-inclusion-review/>Study MIR</a>"}}
    end

    block
        columns 1
        ExpertTasks("Expert tasks")

        DoLibaryTransitions["Do Libary Transitions"]
        DoPackageTransitions["Do Package Transitions"]
        DoMIR["Do a MIR"]
        SeedChange["Seed Change"]
    end

        StudyLibaryTransitions-->DoLibaryTransitions
        StudyPackageTransitions-->DoPackageTransitions
        StudyMIR-->DoMIR
        StudyMIR-->SeedChange

    style ExpertStudies fill: #FFDAB9, stroke:#F4A460;
    style ExpertTasks fill:#FFDAB9, stroke:#F4A460;
    style BlockA fill:transparent,stroke:transparent;
```



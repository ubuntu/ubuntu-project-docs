(path-to-upload-rights)=
# Path to upload rights

This interactive chart shows the skills needed to obtain permissions for
uploading changes to the Ubuntu Package Archive. It can be used as a guide
to help build your applications for upload rights on:

* Package Sets
* [MOTU](https://wiki.ubuntu.com/MOTU), 
* [Core Developer](https://wiki.ubuntu.com/UbuntuDevelopers#Ubuntu_Core_Developers) 


## Basics

These topics will get you started with a good foundation for your future work.

```{mermaid}
%% mermaid flowcharts documentation: https://mermaid.js.org/syntax/flowchart.html
%%{ init: { 'flowchart': { 'curve': 'catmullRom' } } }%%
flowchart TD
    direction TB
    subgraph InitialStudies["Topics for study"]
        direction BT
        Concepts{{"<a href=https://github.com/canonical/ubuntu-maintainers-handbook>Concepts</a>"}}
        Git-Ubuntu{{"git-ubuntu"}}
        Debian-Policy{{"<a href=https://www.debian.org/doc/debian-policy/>Debian Policy</a>"}}
    end

    subgraph InitialTasks["Initial tasks"]
        direction BT
        BiteSizedBugs["Bite-sized bugs"]
        TrivialPackgeMerges["Trivial package merges"]
    end

    InitialStudies --> InitialTasks
```

Once your team and/or mentor says you are ready for more, you can move onto the
intermediate tasks.


## Intermediate

This set of topics and tasks will prepare you to apply for single-package or
package set uploads.

```{mermaid}
%% mermaid flowcharts documentation: https://mermaid.js.org/syntax/flowchart.html
%%{ init: { 'flowchart': { 'curve': 'catmullRom' } } }%%
flowchart TD
    direction TB
    subgraph IntermediateStudies[" "]
        direction BT
        UnderstandDep8{{"<a href=https://salsa.debian.org/ci-team/autopkgtest/blob/master/doc/README.package-tests.rst>Understand DEP8</a>"}}
        ComplexPackageMerges{{"Complex package merges"}}
        SRU{{"<a href=https://canonical-sru-docs.readthedocs-hosted.com/>Study SRU</a>"}}

    end
    
    subgraph IntermediateTasks[" "]
        AddAUTOPKGTESTS["<a href=https://github.com/canonical/ubuntu-maintainers-handbook/blob/main/PackageTests.md>Add Autopkgtest</a>"]
        ProposeMigration["<a href=https://canonical-ubuntu-project.readthedocs-hosted.com/how-ubuntu-is-made/processes/proposed-migration/>Proposed Migration</a>"]
        DoSRUS["Do SRUS"]
    end
    
    %% Transitions
    UnderstandDep8 --> AddAUTOPKGTESTS
    ComplexPackageMerges --> ProposeMigration
    SRU --> DoSRUS
```

Once you have done enough of these tasks that your team/mentor says you are
ready to move onto the Advanced topics, you should be ready to apply for PPU
or Package Set. 


## Advanced

```{mermaid}
%% mermaid flowcharts documentation: https://mermaid.js.org/syntax/flowchart.html
%%{ init: { 'flowchart': { 'curve': 'catmullRom' } } }%%
flowchart TD
    subgraph AdvancedStudies[" "]
        direction TB
        
    end

    subgraph AdvancedTasks[" "]
        direction TB
        %% States
        UpstreamSubmissionFixes(("Upstream submission<br>fixes/features"))
        UpstreamSubmissionDelta(("Upstream submission<br>of delta"))
        MilestonesAndExceptions(("Milestones<br>and exceptions"))
        StudyFFE{{"<a href=https://wiki.ubuntu.com/FreezeExceptionProcess>Study FFE</a>"}}
        DoAnFFE(("Do An FFE"))
        PlusOne{{"<a href=https://wiki.ubuntu.com/PlusOneMaintenanceTeam>Study +1</a>"}}
        PlusOneShadowing(("+1 Shadowing"))

        %% Transitions
        StudyFFE-->DoAnFFE
        PlusOne-->PlusOneShadowing
    end
```


### (Optional) Activities in Debian

At this point, while you are applying for MOTU, you may also want to branch out
and contribute more to Debian.

```{mermaid}
%% mermaid flowcharts documentation: https://mermaid.js.org/syntax/flowchart.html
%%{ init: { 'flowchart': { 'curve': 'catmullRom' } } }%%
flowchart TD
    subgraph optionalDebian[Optional activites in Debian]
        %% States
        Contribute(("<a href=https://www.debian.org/doc/manuals/maint-guide/>Contribute</a>"))
        DM[["<a href=https://wiki.debian.org/DebianMaintainer>Debian Maintainer</a>"]]
        DD[["<a href=https://wiki.debian.org/DebianDeveloper>Debian Developer</a>"]]

        %% Transitions
        Contribute --> DM
        DM --> DD
    end
```


## Expert 

Once you are a member of MOTU, the following tasks and topics will guide you
towards becoming a Core Developer. Keep doing enough of these tasks until you
have the experience you need to apply for Core Dev.

```{mermaid}
%% mermaid flowcharts documentation: https://mermaid.js.org/syntax/flowchart.html
%%{ init: { 'flowchart': { 'curve': 'catmullRom' } } }%%
flowchart TD
    direction LR
    subgraph ExpertTasks["Expert tasks"]
        direction TB

        %% States
        StudyLibaryTransitions{{"<a href=https://wiki.debian.org/Teams/ReleaseTeam/Transitions>Study Libary Transitions</a>"}}
        DoLibaryTransitions(("Do Libary Transitions"))
        StudyPackageTransitions{{"<a href=https://wiki.debian.org/PackageTransition>Study Package Transitions</a>"}}
        DoPackageTransitions(("Do Package Transitions"))
        StudyMIR{{"<a href=https://github.com/canonical/ubuntu-mir/edit/main/README.md>Study MIR</a>"}}
        DoMIR(("Do a MIR"))
        SeedChange(("Seed Change"))

        %% Transitions
        StudyLibaryTransitions-->DoLibaryTransitions
        StudyPackageTransitions-->DoPackageTransitions
        StudyMIR-->DoMIR
        StudyMIR-->SeedChange
    end
```



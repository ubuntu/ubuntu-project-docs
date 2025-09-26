(path-to-upload-rights)=
# Path to upload rights

```{note}
The links shown on this page are subject to sudden changes over the next
few months as more of the documentation it refers to is migrated here. Please
expect inconsistencies -- and feel welcome to correct any links you find that
are incorrect.
```

These interactive charts show the skills needed to obtain permissions for
uploading changes to the Ubuntu Package Archive. They can be used as a guide
to help build your applications for upload rights on:

* {ref}`Package Sets <membership-in-packageset>`
* {ref}`MOTU <membership-in-motu>`, 
* {ref}`Core Developer <membership-in-core-dev>`


## The overall journey

Since Ubuntu is based on Debian, they share a similar technical skillset. This
means that as a contributor, you may want to contribute to Debian as well as
Ubuntu, or just focus on one (as you prefer).

This diagram shows the overall expected progression paths you can take as a
contributor. Click any of the nodes to learn more.


:::{mermaid}
block-beta
  columns 6

%% Column 1
  block:col1
  columns 2
    space:5
    Ubuntu{{"<b>Ubuntu<br>path</br>"}}
    Start(("Start"))
    space:2
    Debian{{"<b>Debian<br>path</b>"}}
  end

  Start --> Ubuntu
  Start --> Debian

%% Column 2
  block:col2
  columns 2
    space:4
    Basics("<a href='#upload-path-basics'>Basics</a>")
    id1((" "))
    space:2
    Contributor("<a href="https://www.debian.org/doc/manuals/maint-guide/">Contributor</a>")
    space
  end

%% Column 3
  block:col3
  columns 2
    UploadRights{{"<b>Upload<br>rights</b>"}}
    PPU["<a href='https://canonical-ubuntu-project.readthedocs-hosted.com/who-makes-ubuntu/joining/membership-in-packageset/'>PPU*</a>"]
    space:2
    Intermediate("<a href='#upload-path-intermediate'>Intermediate</a>")
    id2((" "))
    space:2
    Maintainer("<a href='https://wiki.debian.org/DebianMaintainer'>Maintainer</a>")
    space
  end

%% Column 4
  block:col4
  columns 2
    space
    PackageSet["<a href='https://canonical-ubuntu-project.readthedocs-hosted.com/who-makes-ubuntu/joining/membership-in-packageset/'>PPU*<br>PackageSet</a>"]
    space:2
    Advanced("<a href='#upload-path-advanced'>Advanced</a>")
    id3((" "))
    space:2
    Developer("<a href='https://wiki.debian.org/DebianDeveloper'>Developer</a>")
    space
  end

%% Column 5
  block:col5
  columns 2
    space
    MOTU["<a href='https://canonical-ubuntu-project.readthedocs-hosted.com/who-makes-ubuntu/joining/membership-in-MOTU/'>MOTU</a>"]
    space:2
    Expert("<a href='#upload-path-expert'>Expert</a>")
    id4((" "))
    space:4
  end

%% Column 6
  block:col6
    columns 2
    space
    CoreDev["<a href='https://canonical-ubuntu-project.readthedocs-hosted.com/who-makes-ubuntu/joining/membership-in-core-dev/'>Core Dev</a>"]
    space:2
    Main("<a href='#upload-path-expert'>Expert<br>in main</a>")
    id5((" "))
    space:4
  end


%% Connections
Basics --> Intermediate
Intermediate --> Advanced
Advanced --> Expert
Expert --> Main

id2 --> PPU
id3 --> PackageSet
id4 --> MOTU
Main --- id5
id5 --> CoreDev

Contributor --> Maintainer
Maintainer --> Developer

%% Styling
classDef debianStyle fill: #F8A3C0, stroke: #DD1155
  class Debian,Contributor,Maintainer,Developer debianStyle

classDef ubuntuStyle fill: #FFDAB9, stroke: #E95420,stroke-width:1px;
  class Ubuntu,Basics,Intermediate,Advanced,Expert,Main ubuntuStyle

classDef uploaderStyle fill: #FFDF7E, stroke: #FBAB13
  class UploadRights,PPU,PackageSet,MOTU,CoreDev uploaderStyle

classDef invisible fill: transparent, stroke: transparent
  class id1,col1,col2,col3,col4,col5,col6,col7 invisible

classDef solid fill: #000, stroke: transparent
  class id2,id3,id4,id5 solid
:::


(upload-path-basics)=
## Basics

These topics will get you started with a good foundation for your future
contributions to Ubuntu.

:::{mermaid}
block-beta
columns 2
  block:left
    InitialStudies("Initial studies")
    columns 1
    Concepts{{"<a href=https://github.com/canonical/ubuntu-maintainers-handbook>Concepts</a>"}}
    GitUbuntu{{"git-ubuntu"}}
    DebianPolicy{{"<a href=https://www.debian.org/doc/debian-policy/>Debian Policy</a>"}}
  end

  block:right
    InitialTasks("Initial tasks")
    columns 1
    BugTriage["<a href='https://canonical-ubuntu-project.readthedocs-hosted.com/contributors/bug-triage/'>Bug triage</a>"]
    BiteSizedBugs["Bite-sized bugs"]
    TrivialPackgeMerges["Trivial package merges"]
  end

  InitialStudies --> InitialTasks

  classDef Studies fill: #FFDAB9, stroke:#F4A460;
    class InitialStudies,InitialTasks Studies
  classDef invisible fill:transparent,stroke:transparent;
    class left,right invisible
:::

Once your team and/or mentor says you are ready for more, you can move onto the
Intermediate-level tasks.


(upload-path-intermediate)=
## Intermediate

This set of topics are more in-depth, as well as being quite hands-on.
Completing the tasks in this set will prepare you for Advanced-level work.

:::{mermaid}
block-beta
  columns 3

  block:left
    columns 1
    IntermediateStudies("Intermediate studies")
    UnderstandDep8{{"<a href=https://salsa.debian.org/ci-team/autopkgtest/blob/master/doc/README.package-tests.rst>Understand DEP8</a>"}}
    ComplexPackageMerges{{"Complex package merges"}}
    SRU{{"<a href=https://canonical-sru-docs.readthedocs-hosted.com/>Study SRU</a>"}}
    space:1
  end
   
  block:middle
    columns 1
    IntermediateTasks("Intermediate tasks")
    AddAUTOPKGTESTS["<a href=https://canonical-ubuntu-project.readthedocs-hosted.com/contributors/bug-fix/package-tests/>Add Autopkgtest</a>"]
    ProposeMigration["<a href=https://canonical-ubuntu-project.readthedocs-hosted.com/how-ubuntu-is-made/processes/proposed-migration/>Proposed Migration</a>"]
    DoSRUS["Do SRUS"]
    WorkOnBugs["Work on packaging bugs/features"]
  end

  block:right
    columns 2
    space
    PPU["<a href='https://canonical-ubuntu-project.readthedocs-hosted.com/who-makes-ubuntu/joining/membership-in-packageset/'>PPU*</a>"]
    space:8
  end

  UnderstandDep8 --> AddAUTOPKGTESTS
  ComplexPackageMerges --> ProposeMigration
  SRU --> DoSRUS
  IntermediateTasks --> PPU

  classDef Studies fill: #FFDAB9, stroke:#F4A460;
    class IntermediateStudies,IntermediateTasks Studies
  classDef invisible fill:transparent,stroke:transparent;
    class left,middle,right invisible
:::

Once you have done enough of these tasks that your team/mentor says you are
ready to continue your journey, you can move onto the Advanced topics.

At this time, you may also be ready to apply for Per-Package Upload (PPU) rights.
This will depend very much on the package you are interested in gaining upload
rights for. Some packages will need you to complete the Advanced path first.


(upload-path-advanced)=
## Advanced

:::{mermaid}
block-beta
  columns 3

  block:left
    AdvancedStudies("Advanced studies")
    columns 1
    space:3
    StudyFFE{{"<a href=https://canonical-ubuntu-project.readthedocs-hosted.com/staging/release-team/freeze-exceptions/>Study FFE</a>"}}
    PlusOne{{"<a href=https://canonical-ubuntu-project.readthedocs-hosted.com/contributors/advanced/plus-one-maintenance/>Study +1</a>"}}
  end

  block:middle
    AdvancedTasks("Advanced tasks")
    columns 1
    UpstreamSubmissionFixes["Upstream submission fixes/features"]
    UpstreamSubmissionDelta["Upstream submission of delta"]
    MilestonesAndExceptions["Milestones and exceptions"]
    DoAnFFE["Do An FFE"]
    PlusOneShadowing["+1 Shadowing"]
  end

  block:right
    columns 2
    space
    PPU["<a href='https://canonical-ubuntu-project.readthedocs-hosted.com/who-makes-ubuntu/joining/membership-in-packageset/'>PPU*</a>"]
    space
    PackageSet["<a href='https://canonical-ubuntu-project.readthedocs-hosted.com/who-makes-ubuntu/joining/membership-in-packageset/'>PackageSet</a>"]
    space:8
  end

  AdvancedTasks --> PPU
  AdvancedTasks --> PackageSet
  StudyFFE --> DoAnFFE
  PlusOne --> PlusOneShadowing

  classDef Studies fill: #FFDAB9, stroke:#F4A460;
    class AdvancedStudies,AdvancedTasks Studies
  classDef invisible fill:transparent,stroke:transparent;
    class left,middle,right invisible
:::

With enough of these tasks under your belt to demonstrate your skills and
experience, you can move onto the Expert topics.

At this point, you are likely to be ready to apply for Per-Package Upload (PPU)
rights, or if there is a set of packages you are interested in working on, you
can apply for Package Set instead.


(upload-path-expert)=
## Expert 

The Expert-level studies will prepare you for becoming a member of MOTU, where
you will help to maintain packages in `universe`.

If you want to, you can continue your Expert-level studies by further
specializing in `main` -- you need to do this if you want to apply for
the Core Developer role.

:::{mermaid}
block-beta
  columns 3

  block:topleft 
    columns 1
    ExpertStudies("Expert studies")
    StudyLibaryTransitions{{"<a href=https://wiki.debian.org/Teams/ReleaseTeam/Transitions>Study libary transitions</a>"}}
    StudyPackageTransitions{{"<a href=https://wiki.debian.org/PackageTransition>Study package transitions</a>"}}
    id1((" "))
  end

  block:topright
    columns 1
    ExpertTasks("Expert tasks")
    DoLibaryTransitions["Do libary transitions"]
    DoPackageTransitions["Do package transitions"]
    space:1
  end

  block:motu
    columns 2
    id2((" "))
    MOTU["<a href='https://canonical-ubuntu-project.readthedocs-hosted.com/who-makes-ubuntu/joining/membership-in-MOTU/'>MOTU</a>"]
    space:4
    id3((" "))
    space
  end

  ExpertTasks --> MOTU

  block:lowerleft
    columns 1
    ExpertinMainStudies("Expert in <code>main</code> studies")
    space
    StudyMIR{{"<a href=https://canonical-ubuntu-project.readthedocs-hosted.com/MIR/main-inclusion-review/>Study MIR</a>"}}
    space:1
  end

  block:lowerright
    columns 1
    ExpertinMainTasks("Expert in <code>main</code> tasks")
    DoMIR["Do an MIR"]
    space
    SeedChange["Seed change"]
  end

  block:coredev
    columns 2
    space
    CoreDev["<a href='https://canonical-ubuntu-project.readthedocs-hosted.com/who-makes-ubuntu/joining/membership-in-core-dev/'>Core Dev</a>"]
    space:6
  end
 
  ExpertinMainTasks --> CoreDev

  id1 --> ExpertinMainStudies
  id2 --- id3
  id3 --- id1

  StudyLibaryTransitions-->DoLibaryTransitions
  StudyPackageTransitions-->DoPackageTransitions
  StudyMIR-->DoMIR
  StudyMIR-->SeedChange

  classDef Studies fill: #FFDAB9, stroke:#F4A460;
    class ExpertStudies,ExpertTasks,ExpertinMainStudies,ExpertinMainTasks Studies

  classDef invisible fill: transparent, stroke: transparent
    class topleft,topright,lowerleft,lowerright,motu,coredev invisible

  classDef solid fill: #000, stroke: transparent
    class id1,id2,id3 solid
:::



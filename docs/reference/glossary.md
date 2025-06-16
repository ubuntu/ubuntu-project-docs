(glossary)=

# Glossary

We are currently compiling and defining terms for this glossary. If you would
like to help, please visit our {ref}`contributions page <contribute>` for
details on how to get involved.


:::{glossary}

80x86
    See {term}`i386`

AArch32
    See {term}`armhf`

AArch64
    See {term}`arm64`

amd64
    {term}`CPU` {term}`Architecture` identifier for the `AMD64` (also known
    as {term}`x64`, {term}`x86-64`, {term}`x86_64`, and {term}`Intel 64`)
    architecture; a 64-bit version of the {term}`i386` instruction set.

    See also: [X86-64 (Wikipedia)](https://en.wikipedia.org/wiki/X86-64)

ANAIS
Architecture Not Allowed In Source
    *Work in Progress*

ABI
Application Binary Interface
    Defines how two binary applications interface each other, like calling
    conventions, data type sizes, and system call interfaces, ensuring
    compatibility and proper communication between different parts of a
    software system, such as libraries, executables, and the
    {term}`Operating System`. **Application Binary Interfaces**
    are crucial for software components compiled on different systems
    to work together seamlessly.

    See also:
    * [Kernel ABI (Ubuntu Wiki)](https://wiki.ubuntu.com/KernelTeam/BuildSystem/ABI)
    * [Application binary interface (Wikipedia)](https://en.wikipedia.org/wiki/Application_binary_interface)

    ```{warning}
    Do not confuse with {term}`Application Programming Interface` ({term}`API`)!
    ```

API
Application Programming Interface
    An **Application Programming Interface** (API), is a set of rules that
    allows different software applications to communicate with each other. It
    defines the methods and data formats that applications can use to request
    and exchange information, perform specific tasks, or access the
    functionality of another software component, such as an
    {term}`Operating System`, library, or online service.
    
    **APIs** enable developers to build upon existing software and create
    new applications by providing a standardized way to interact with external
    systems, services, or libraries without needing to understand their internal
    workings.

    ```{warning}
    Do not confuse with {term}`Application Binary Interface` ({term}`ABI`)!
    ```

APT
Advanced Packaging Tool
    This is a common package manager used in Ubuntu.
    
    See also:
    * [Package management (Ubuntu Server documentation)](https://documentation.ubuntu.com/server/how-to/software/package-management/)

Architecture
    Within the context of {term}`Ubuntu`, this refers to the system architecture
    (more specifically, the CPU architecture and its instruction set) an
    application is designed for.

    See also:
    * [Supported architectures](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/reference/architectures/)
    * [Computer Architecture (Wikipedia)](https://en.wikipedia.org/wiki/Computer_architecture)

AA
Archive Admin
    An administrator that is responsible for maintenance tasks of the
    {term}`Ubuntu Package Archive <Ubuntu Archive>`, including processing of new
    {term}`Packages <Package>`, migration of packages between
    {term}`Components <Component>`, and other administrative matters.

    See also:
    * ["Ubuntu Package Archive Administrators" team on Launchpad](https://launchpad.net/~ubuntu-archive)

Archive Mirror
    A {term}`Mirror` of the {term}`Ubuntu Archive`.

    See the section [Mirrors](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivemirrors) for more details.

ARM
    *ARM* (formerly an acronym for *Advanced RISC Machines* and originally
    *Acorn RISC Machine*) is a widely used family of {term}`RISC` {term}`CPU`
    {term}`Architectures <Architecture>` known for their efficiency,
    low power consumption, and versatility, which are widely used in
    {term}`Embedded Systems` and mobile devices.

    Notable examples are {term}`arm64` and {term}`armhf`.

    See also:
    * [ARM architecture family (Wikipedia)](https://en.wikipedia.org/wiki/ARM_architecture_family)

arm64
ARMv8
    {term}`CPU` {term}`Architecture` identifier (also known as ARM64,
    {term}`ARMv8`, and {term}`AArch64`) for a 64-bit {term}`ARM` {term}`Architecture`
    variant.

    See also:
    * [AArch64 (Wikipedia)](https://en.wikipedia.org/wiki/AArch64)

armhf
ARM Hard Float
ARMv7
    {term}`CPU` {term}`Architecture` identifier (also known as ARM32,
    {term}`ARMv7`, {term}`AArch32`, and {term}`ARM Hard Float`) for a 32-bit
    {term}`ARM` {term}`Architecture` variant.

    See also:
    * [AArch64 (Wikipedia)](https://en.wikipedia.org/wiki/AArch64)

autopkgtest
    {manpage}`autopkgtest(1)` is a software that interprets and executes tests
    found in {term}`source packages <Source Package>` that follow the {term}`DEP-8`
    specification.

    See also:
    * [autopkgtest.ubuntu.com](https://autopkgtest.ubuntu.com/)

autopkgtest Cloud
    The {term}`Ubuntu project <Ubuntu>` operates a testing infrastructure used
    to execute automated tests for Ubuntu {term}`source packages <Source Package>`.
    It is an implementation of the {term}`DEP-8` specification, enabling large-scale
    testing across a variety of architectures and environments.

BZR
Bazaar
    A distributed {term}`Version Control System` to collaborate on software
    development, developed by {term}`Canonical` and part of the {term}`GNU`
    system.

    **Bazaar** as a Canonical project is discontinued. Development has been
    carried forward in the community as {term}`Breezy`.

    See also:
    * [Bazaar (Launchpad)](https://launchpad.net/bzr)

    ```{note}
    **Bazaar** is replaced in favor of a {term}`git`-based workflow as the
    main Version Control System within Ubuntu. There are some projects that
    still use it, but be aware that documents referencing Bazaar as an actively
    used Version Control System within Ubuntu are most likely outdated.

    See also: {term}`git-ubuntu`
    ```

Big-Endian
    *Work in Progress*

    See also: {term}`Endianness`

Binary Package
    A {term}`Debian` **binary package** is a standardized format with the file
    extension `.deb` that the {term}`Package Manager` ({manpage}`dpkg(1)` or
    {manpage}`apt(8)`) can understand to install and uninstall software on a
    target machine to simplify distributing software to a target machine and
    managing software on a target machine.

    See also: 
    * [Binary Packages (explanation)](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/package-model/#binarypackages)

Blank space
    **Blank space** characters refer to characters in a text (especially
    {term}`Source Code`) used for formatting and spacing but that do not
    produce visible marks or symbols when rendered. Common *blank space*
    characters include spaces, tabs and newline characters.

Branch
    *Work in Progress*

Breezy
    A {term}`Fork` of the {term}`Bazaar` {term}`Version Control System`.

    See also:
    * [Breezy (Launchpad)](https://launchpad.net/brz)

Bug
    In software development a **bug** refers to unintended or unexpected
    behavior of a computer program or system that produce incorrect results, or
    crashes.
    
    Bugs can occur due to programming mistakes, design issues, or unexpected
    interactions between different parts of the software.
    
    Identifying and fixing bugs is a fundamental part of the software
    development process to ensure that the software functions as intended and
    is free of errors.

    See also:
    * [Software bug (Wikipedia)](https://en.wikipedia.org/wiki/Software_bug)

BTS
Bug Tracking System
    A platform used by software development teams to manage and monitor the
    progress of reported issues or {term}`Bugs <Bug>` within a software project.
    It provides a centralized platform for users to report problems, assign
    tasks to developers, track the status of issues, prioritize fixes, and
    maintain a comprehensive record of software defects and their resolutions.

    This system helps streamline the debugging process and enhances
    communication among team members, ultimately leading to improved
    software quality.

    {term}`Launchpad` is the **Bug Tracking System** for Ubuntu packages.

    See also:
    * [Bug tracking system (Wikipedia)](https://en.wikipedia.org/wiki/Bug_tracking_system)

Canonical
    **Canonical Ltd.** is a UK-based private company that is devoted to the
    {term}`Free and Open Source Software` philosophy and has created several
    notable software projects, including {term}`Ubuntu`. Canonical offers
    commercial support for Ubuntu and related services and is responsible
    for delivering six-monthly milestone releases and regular {term}`LTS`
    releases for enterprise production use, as well as security updates,
    support and the entire online infrastructure for community interaction.

    Find out more on [the Canonical website](https://canonical.com/).

Canonical Discourse
    A {term}`Discourse` instance for internal/Canonical-wide discussions. 
    The discussions here are only accessible to Canonical employees.

    See also:
    * [Canonical Discourse](https://discourse.canonical.com)

CD Mirror
    A {term}`Mirror` of the {term}`Ubuntu` [Image archive](https://cdimage.ubuntu.com/).

    See also:
    * [The complete list of officially recognized Ubuntu image archive mirrors](https://launchpad.net/ubuntu/+cdmirrors).

CPU
Central Processing Unit
    The main component of a computer, which is responsible for executing the
    instructions of a computer program, such as arithmetic, logic, and
    input/output (I/O) operations.

CUE
Certified Ubuntu Engineer
    Develop and certify your skills on the world's most popular {term}`Linux`
    {term}`OS`.
    
    See also: 
    * [Ubuntu credentials](https://ubuntu.com/credentials)

Changelog
    The `debian/changelog` file in a {term}`Source Package`.

    See also:
    * [Basic overview of the `debian/` directory](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/reference/debian-dir-overview/)
    * [Section 4.4 Debian changelog (Debian Policy Manual v4.6.2.0)](https://www.debian.org/doc/debian-policy/ch-source.html#debian-changelog-debian-changelog)

CoF
Circle of Friends
    The {term}`Ubuntu` logo is called **Circle of Friends**, because it is
    derived from a picture that shows three friends extending their arms,
    overlapping in the shape of a circle. It should represent the
    [core values of Ubuntu](https://design.ubuntu.com/brand):
    *Freedom*, *Reliable*, *Precise* and *Collaborative*.

    ```{image} ../images/glossary-CoF-Square.png
    :width: 200
    :height: 200
    :alt: Circle of Friends (Ubuntu Logo)
    ```

    ```{image} ../images/glossary-Old-Ubuntu-Login-Background.jpg
    :height: 200
    :alt: Old Ubuntu-Login background showing three people in a circle holding hands.
    ```

Closed Source Software
    *Work in Progress*

Code name
    *Work in Progress*

CoC
Code of Conduct
    *Work in Progress*

    See also: {term}`Ubuntu Code of Conduct`

Code Review
    *Work in Progress*

CLI
Command Line Interface
    *Work in Progress*

CVE
Common Vulnerabilities and Exposures
    *Work in Progress*

CISC
Complex Instruction Set Computer
    A {term}`CPU` {term}`Architecture` featuring a rich and diverse set of
    instructions, often capable of performing complex operations in a single
    instruction. {term}`CISC` processors aim to minimize the number of
    instructions needed to complete a task, potentially sacrificing execution
    speed for instruction richness.

    See also:
    * [Complex instruction set computer (Wikipedia)](https://en.wikipedia.org/wiki/Complex_instruction_set_computer)

Component
    **Components** are logical subdivisions or namespaces of the {term}`Packages <Package>`
    in a [Suite](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivesuite).
    The {term}`APT` {term}`Package Manager` can individually subscribe to the
    components of a [suite](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivesuite).

    The packages of an {term}`Ubuntu` [Ubuntu series](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/reference/glossary/#term-Ubuntu) are categorized
    if they are {term}`Open Source Software` and part of the Base Packages
    for a given Ubuntu series and sorted into the **components**;
    [Main](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivecomponents-main),
    [Restricted](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivecomponents-restricted),
    [Universe](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivecomponents-universe), or
    [Multiverse](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivecomponents-multiverse), as shown in the following table:

    |                          | Open Source Software | Closed Source Software |
    | --- | --- | --- |
    | **Ubuntu Base Packages** | Main                 | Restricted             |
    | **Community Packages**   | Universe             | Multiverse             |

    See also: [Components (explanation)](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivecomponents)

CD
Continuous Delivery
    *Work in Progress*

    See also:
    * [Continuous delivery (Wikipedia)](https://en.wikipedia.org/wiki/Continuous_delivery)

CI
Continuous Integration
    *Work in Progress*

    See also:
    * [Continuous integration (Wikipedia)](https://en.wikipedia.org/wiki/Continuous_integration)

CLA
Contributor Licence Agreement
    *Work in Progress*

Control File
    The `debian/control` file in a {term}`Source Package`.

    This can also refer to a {term}`Debian` source control file (`.dsc` file)
    or the control file in a {term}`Binary Package` (`.deb` file).

    See also:
    * [Basic overview of the `debian/` directory](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/reference/debian-dir-overview/)
    * [Chapter 5. Control files and their fields (Debian Policy Manual v4.6.2.0)](https://www.debian.org/doc/debian-policy/ch-controlfields.html)

Coordinated Release Date
    The date at which the details of a {term}`CVE` are to be publicly disclosed.
    
    Disambiguation: The acronym CRD could also refer to {term}`Current Release in Development`

Copyleft
    Licenses which implement copyleft grant certain freedoms to their works, under
    the condition that these freedoms are preserved in all derivative works.

    One famous example of copyleft is the {term}`GNU` {term}`General Public License`,
    which gives its users {term}`Free Software` rights as long as equivalent
    rights are maintained in modified distributions of said software.

Copyright
    *Work in Progress*

Copyright File
    The `debian/copyright` file in a {term}`Source Package`.

    See also:
    * [Basic overview of the `debian/` directory](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/reference/debian-dir-overview/)
    * [Section 4.5. Copyright (Debian Policy Manual v4.6.2.0)](https://www.debian.org/doc/debian-policy/ch-source.html#copyright-debian-copyright)

Cryptographic Signature
    *Work in Progress*

Current Release in Development
    {term}`Ubuntu` follows a strict time-based release cycle. Every six months a
    new Ubuntu version is released.

    The "Current Release in Development" is the Ubuntu version in development
    for the next release at any given time. It is also often referred
    to as "devel".

    Disambiguation: The acronym CRD could also refer to {term}`Coordinated Release Date`
    See also:
    * [Ubuntu Releases (explanation)](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/releases/)

Debian
    **Debian** is a widely-used community-driven
    {term}`Free and Open Source <Free and Open Source Software>`
    {term}`Operating System` known for its stability and extensive software
    {term}`Repository`.
    
    It follows a strict commitment to Free and Open Source Software principles
    and serves as the basis for various {term}`Linux`
    {term}`Distributions <distribution>`
    (including {term}`Ubuntu`). Debian's {term}`Package Manager`, {term}`APT`,
    simplifies software installation and updates, making it a popular choice
    for servers and desktops.

    See also:
    * [Official Debian website](https://www.debian.org/)

DEP
Debian Enhancement Proposal
    A Debian Enhancement Proposal ({term}`DEP`) is a formal document that outlines
    proposed changes, enhancements, or new processes within the
    {term}`Debian project <Debian>`. DEPs provide a structured way for contributors
    to suggest, discuss, and document improvements to Debian' software, policies,
    or workflows.

    See also:
    * [Official DEP team page](https://dep-team.pages.debian.net/)

DSA
Debian System Administration
    *Work in Progress*

debs
    `.deb` is the file extension of a {term}`Debian` {term}`Binary Package`.
    Such files are commonly referred to as "debs".

DEP-8
    {term}`DEP-8` is a specification from the {term}`Debian project <Debian>`
    that defines a standardized framework for automated testing of
    {term}`source <Source Package>` and {term}`binary packages <Binary Package>`.

    See also:
    * [Current DEP-8 Specification](https://dep-team.pages.debian.net/deps/dep8/)

Detached Signature
    A detached signature is a {term}`Digital Signature <Signature>` that is separated
    from the data it signs. In contrast to an embedded signature, which is included
    within the data it signs, a detached signature is kept as a separate file
    or entity. 

Devel
    Shorthand term for the {term}`Current Release in Development`.

DMB
Developer Membership Board
    *Work in Progress*

    See also:
    * [Developer Membership Board (Ubuntu Wiki)](https://wiki.ubuntu.com/DeveloperMembershipBoard)

diff
    A text format that shows the difference between files that are compared.
    A file that contains text in this format usually has the file extension `.diff`.
    This file format does not work well for comparing files in a non-text encoded
    format (e.g. `.bin`, `.png`, `.jpg`).

    See also:
    * {manpage}`diff(1)`
    * {manpage}`git-diff(1)`

Discourse
    An {term}`open-source <Open Source Software>` forum software that is used 
    by {term}`Ubuntu` and {term}`Canonical`.

    See also:
    * {term}`Ubuntu Discourse`
    * {term}`Canonical Discourse`
    * [Discourse Project Homepage](https://www.discourse.org/)

Distribution
distro
    In general, a software **distribution** (also called a **distro**) is a set of
    software components that is distributed as a whole to users.

    Usually people think specifically of {term}`Linux` distributions. A Linux
    distribution (or distro), is a complete {term}`Operating System` based on the
    Linux {term}`Kernel`. It includes essential system components, software
    applications, and {term}`Package Management Tools <Package Manager>`, tailored
    to a specific purpose or user preferences. Linux distributions vary
    in features, desktop environments, and software {term}`Repositories <Repository>`,
    allowing users to choose the one that best suits their needs.

    See also:
    * [Linux distribution (Wikipedia)](https://en.wikipedia.org/wiki/Linux_distribution)

DNS
Domain Name System
    *Work in Progress*

Downstream
    A software project(s) (and associated entities) that depend on
    another software project directly or indirectly.

    See also:
    * [Downstream (explanation)](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/upstream-and-downstream/#downstream)

dsc
    `.dsc` is the file extension of a {term}`Debian` source control file.
    
    See also:
    * [Chapter 5. Control files and their fields (Debian Policy Manual v4.6.2.0)](https://www.debian.org/doc/debian-policy/ch-controlfields.html)

End of Life
    Refers to the {term}`End of Support` (Life) for a product/software.

End of Line
    The end of a line of {term}`encoded text <Text Encoding>` is indicated by
    a control character or sequence of control characters. This is relevant for
    text parser which often parse text line by line.

    The most common examples for control character(s) that indicate a *end of line* are:

    | {term}`Operating System`                   | Abbreviation* | `hex` value(s)* | `dec` value(s)* | Escape sequence* |
    |--------------------------------------------|---------------|-----------------|-----------------|------------------|
    | {term}`Unix` and {term}`Unix`-like systems | `LF`          | `0A`            | `10`            | `\n`             |
    | Windows systems                            | `CR` `LF`     | `0D` `0A`       | `13` `10`       | `\r` `\n`        |


    \* for the character encoding `ASCII`

EoSS
End of Standard Support
    *Work in Progress*

EoS
End of Support
    *Work in Progress*

EULA
End-user license agreement
    *Work in Progress*

Embedded Systems
    *Work in Progress*

Endianness
    *Work in Progress*

    See also:
    * {term}`Little-Endian`
    * {term}`Big-Endian`
    * [Endianness (Wikipedia)](https://en.wikipedia.org/wiki/Endianness)

ESM
Expanded Security Maintenance
    *Work in Progress*
    
    See also:
    * [Expanded Security Maintenance (homepage)](https://ubuntu.com/security/esm)

FTBFS
Failed to build from Source
    *Work in Progress*

FTI
Failed to install
    *Work in Progress*

FFE
Feature Freeze Exception
    *Work in Progress*
    
    See also:
    * [Freeze Exception Process](https://wiki.ubuntu.com/FreezeExceptionProcess)

FR
Feature Request
    *Work in Progress*

FIPS
Federal Information Processing Standards
    A set of standards and guidelines of the United States federal government
    developed by {term}`National Institute of Standards and Technology` ({term}`NIST`)
    to ensure the security and interoperability of computer systems and software
    used by non-military federal agencies and its contractors.
        
    See also:
    * [Federal Information Processing Standards (Wikipedia)](https://en.wikipedia.org/wiki/Federal_Information_Processing_Standards)

Fork
    In the context of {term}`Open Source Software` development, a **fork** refers
    to the process of creating a new, independent version of a software project by
    copying its {term}`Source Code` to evolve separately, potentially with different
    goals, features, or contributors.

FOSS
Free and Open Source Software
    The term "Free and Open Source Software" encompasses both {term}`Free Software`
    and {term}`Open Source Software`. In short, free and open-source software not
    only makes its {term}`Source Code` publicly available, but also allows users to
    use, distribute, modify, and distribute modified copies of the software free of
    charge.

    See also:
    * [Free and open-source software (Wikipedia)](https://en.wikipedia.org/wiki/Free_and_open-source_software)

Free Software
    A common definition of Free Software is any software which guarantees the Free
    Software Foundation's four essential freedoms:

    - The freedom to run the program as you wish, for any purpose (freedom 0).
    - The freedom to study how the program works, and change it so it does your
      computing as you wish (freedom 1). This requires access to the source code.
    - The freedom to redistribute copies of the original software program
      (freedom 2).
    - The freedom to distribute copies of your modified versions to others (freedom 3).
      This also requires access to the source code.

    The definition of free software has significant overlap with
    {term}`Open Source Software`, so the two categories are often collectively
    referred to as {term}`Free and Open Source Software`.

    See also:
    * [Free software (Wikipedia)](https://en.wikipedia.org/wiki/Free_software)
    * [FSF Four Freedoms](https://static.fsf.org/nosvn/posters/handout-four-freedoms.pdf)

GA
General Availability
    *Work in Progress*

GPL
General Public License
    The {term}`GNU` General Public Licenses (GPL) are a set of {term}`Free Software`
    licenses. They grant users the ability to use, study, modify, and distribute
    the software and source code. Additionally, the GPLs are {term}`Copyleft`, so
    any derivative works must be distributed with the same or equivalent freedoms.

    Prominent projects which use a version of the GPL include {term}`git` and
    {term}`Linux`.

git
    *Work in Progress*

git-ubuntu
    *Work in Progress*

GNU
    **GNU** is a recursive acronym for "GNU's Not Unix!". It is a collection
    of {term}`Free and Open Source Software` that can be used as an {term}`Operating System`
    and aims to respect its users' freedom. The collection of
    Free and Open Source Software is often used with {term}`Unix`-like
    kernels like {term}`Linux` (these {term}`Distributions <Distribution>` are
    commonly referred to as **GNU/Linux**).

    For example, {term}`Debian` and {term}`Ubuntu` are GNU/Linux
    {term}`Distributions <Distribution>`.

    Most of the GNU software is licensed under the GNU {term}`General Public License` ({term}`GPL`).

    See also:
    * [GNU (Wikipedia)](https://en.wikipedia.org/wiki/GNU)
    * [Official GNU website](https://www.gnu.org)

GUI
    Abbreviation for Graphical {term}`User Interface`.

i386
    {term}`CPU` {term}`Architecture` identifier (also known as {term}`Intel x86`,
    {term}`80x86`, and {term}`x86`), that was originally released as 80386; a
    32-Bit Microprocessor by Intel.

    See also:
    * [i386 (Wikipedia)](https://en.wikipedia.org/wiki/I386)

IBM
    Abbreviation for *International Business Machines*

    See also:
    * [IBM website](https://www.ibm.com/).

Image
    Within the context of {term}`Ubuntu` development, an **Image** refers to an
    `.iso` file that contains a bootable Ubuntu installer that can be
    burned to a CD to make installation disks.

    See also:
    * [releases.ubuntu.com](https://www.releases.ubuntu.com/)
    * [Optical disc image (Wikipedia)](https://en.wikipedia.org/wiki/Optical_disc_image)

IC
Individual Contributor
    *Work in Progress*

IEEE
Institute of Electrical and Electronics Engineers
    *Work in Progress*
    
    See also:
    * [IEEE website](https://www.ieee.org/)

Intel 64
    See {term}`arm64`

Intel x86
    See {term}`i386`

ITP
Intent to Package
    *Work in Progress* (see https://wiki.debian.org/ITP)

ICE
Internal Compiler Error
    *Work in Progress*

IRC
Internet Relay Chat
    Internet Relay Chat ({term}`IRC`)

ISO
    *Work in Progress*

Kernel
    *Work in Progress*

Keyring
    *Work in Progress*

LP
Launchpad
    The general development platform where {term}`Ubuntu` itself and most of
    Ubuntu related software projects live.

    See also:
    * [Launchpad (explanation article)](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/launchpad/)

Linux
    **Linux** is an {term}`Open Source <Open Source Software>` {term}`Operating System`
    {term}`Kernel` originally created by Linus Torvalds in 1991. It forms the
    core of various Linux {term}`Distributions <Distribution>`, such as {term}`Debian`
    and {term}`Ubuntu`. Linux is known for its stability, security, and flexibility,
    making it a popular choice for servers, desktops, and embedded systems.

    See also:
    * [Linux (Wikipedia)](https://en.wikipedia.org/wiki/Linux)

LinuxONE
    *Work in Progress*

LXC
Linux Containers
    *Work in Progress*

    See also:
    * [Official LXC documentation](https://linuxcontainers.org/lxc/introduction/)

Little-Endian
    *Work in Progress*

    See also:
    * {term}`Endianness`

LTS
Long Term Support
    *Work in Progress*

LXD
    LXD is system container manager.
    
    See also:
    * [Official LXD documentation](https://documentation.ubuntu.com/lxd/latest/)

Main
    A {term}`Component` of every {term}`Ubuntu` [Series](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archiveseries) in the
    {term}`Ubuntu Archive` that contains {term}`Open Source <Open Source Software>`
    {term}`Packages <Package>` which are supported and maintained by {term}`Canonical`.

    See also:
    * [Components](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivecomponents)

Makefile
    A Makefile declares a set of tasks to be automatically executed. Makefiles are
    most commonly used to describe how a program is compiled, installed, cleaned,
    and uninstalled. The actions the Makefile performs in order to achieve these
    tasks consist of {term}`Shell` commands.

    See also:
    * [GNU Make Documentation](https://www.gnu.org/software/make/manual/make.html#Introduction)


MIR
Main Inclusion Review
    The review process when a {term}`Package` in {term}`Universe` or {term}`Multiverse`
    gets requested to be promoted to {term}`Main` or {term}`Restricted`.

    See also:
    * {ref}`Main Inclusion Review (explanation article) <main-inclusion-review>`

Mailing List
    *Work in Progress*

Maintainer
    *Work in Progress*

MOTU
Masters of the Universe
    *Work in Progress*

Merge
    *Work in Progress*

Merge Conflict
    *Work in Progress*

MP
Merge Proposal
    *Work in Progress*

MRE
Micro Release Exception
    See also:
    * [Micro Release Exception](https://wiki.ubuntu.com/StableReleaseUpdates/MicroReleaseExceptions)

MIR Team
    The {term}`Ubuntu` team that reviews requests to promote {term}`Packages <Package>`
    in {term}`Universe` or {term}`Multiverse` to {term}`Main` or {term}`Restricted`.

    See also:
    * {ref}`Main Inclusion Review (explanation article) <main-inclusion-review>`

Mirror
    A server that **mirrors** (replicates and keeps in sync) the content of another
    server to distribute network traffic, reduce latency, and provide redundancy,
    ensuring high availability and fault tolerance.

    See also:
    * {term}`Archive Mirror`
    * {term}`CD Mirror`

Multiverse
    A {term}`Component` of every {term}`Ubuntu`
    [Series](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archiveseries) in the
    {term}`Ubuntu Archive` that contains {term}`Packages <Package>` of
    {term}`Closed Source Software` or {term}`Open Source Software` restricted by
    copyright or legal issues. These packages are maintained and supported by
    the Ubuntu community.

    See also:
    * [Components](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivecomponents)

Namespace
    A concept in computer science and software development that defines a scope
    or context in which identifiers (such as variable names, functions, or classes)
    are unique and distinct.

    It helps prevent naming conflicts and organizes code elements into separate
    compartments. Namespaces are commonly used in programming languages to group
    and categorize code, making it more manageable and maintainable.

    They play a crucial role in encapsulation and modularity,
    allowing developers to create reusable and organized code structures.
    Namespaces are particularly important in larger software projects where
    numerous components and libraries need to coexist without clashing with
    each other's names.

NIST
National Institute of Standards and Technology
    *Work in Progress*

Native Package
    **Native source packages** are {term}`Source Packages <Source Package>` that
    are their own {term}`Upstream`, therefore they do not have an
    {term}`orig tarball`.

    See also:
    * [Native Source Packages (explanation)](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/package-model/#nativesourcepackages)

NBS
Not built from Source
    *Work in Progress*

NPOASR
Never Part Of A Stable Release
    *Work in Progress*

NVIU
Newer Version in Unstable
    *Work in Progress*

OSS
Open Source Software
    Open source software is any software with a license that guarantees a certain
    set of rights to users of the software: the rights to use, study, modify, and
    distribute both the software and its source code for any purpose.

    The definition of open source software has significant overlap with
    {term}`Free Software`, so the two categories are often collectively
    referred to as {term}`Free and Open Source Software`.

    See also:
    * [The Open Source Initiative's standard definition of Open Source](https://opensource.org/osd)

OS
Operating System
    An **operating system** (OS) is essential system software that manages computer
    hardware and software resources. It provides crucial services for computer
    programs, including hardware control, task scheduling, memory management,
    file operations, and user interfaces, simplifying program development and
    execution.

    See also:
    * [Operating system (Wikipedia)](https://en.wikipedia.org/wiki/Operating_system)

orig tarball
    Also known as "original tarball". The `.orig.tar.ext` and
    `.orig-component.tar.ext` (where `ext` can be `gz`, `bz2`, `lzma` and `xz`
    and `component` can contain alphanumeric characters (`a-zA-Z0-9`) and
    hyphens `-`) {manpage}`tar(5)` archive files of a {term}`Debian`
    {term}`Source Package` that contains the original {term}`Source`
    of the {term}`Upstream` project.

    See also:
    * {manpage}`dpkg-source(1)`
    * {term}`tarball`

Package
    *Work in Progress*

Package Manager
    *Work in Progress*

Patch
    A **patch** is a (often small) piece of code or a software update designed
    to fix or improve a computer program or system. It is typically applied
    to address {term}`Security Vulnerabilities <Common Vulnerabilities and Exposures>`,
    {term}`Bugs <Bug>`, or enhance functionality, ensuring the software remains
    up-to-date and reliable. Patches are essential for maintaining software
    integrity and security.

    See also:
    * [Patch (Wikipedia)](https://en.wikipedia.org/wiki/Patch_(computing))

PCRE
Perl Compatible Regular Expressions
    *Work in Progress*
    
    See also: [PCRE (Reference Implementation)](https://www.pcre.org/)

PPA
Personal Package Archive
    *Work in Progress*

Pocket
    A **pocket** is a {term}`Package` sub-{term}`repository <Repository>` within
    the Ubuntu Archive. Every Ubuntu {term}`Series` has the following pockets:
    * [Release](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivepockets-release)
    * [Security](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivepockets-security)
    * [Updates](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivepockets-updates)
    * [Proposed](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivepockets-proposed)
    * [Backports](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivepockets-backports)

    See also:
    * [Pockets (explanation)](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivepockets)

POSIX
    Abbreviation for **Portable Operating System Interface**: A family of
    standards specified by the {term}`IEEE` Computer Society for maintaining
    compatibility between {term}`Operating Systems <Operating System>`. POSIX
    defines the {term}`API`, along with command line shells and utility
    interfaces, for software compatibility with variants of Unix and other
    {term}`Operating Systems <Operating System>`.

PowerPC
    *Work in Progress*

ppc64el
    *Work in Progress* (PowerPC64 Little-Endian)

PKCS
Public Key Cryptography Standards
    *Work in Progress*

    See also:
    * [PKCS (Wikipedia)](https://en.wikipedia.org/wiki/PKCS)

Pull
    *Work in Progress*

PR
Pull Request
    *Work in Progress*

Push
    *Work in Progress*

RTOS
Real Time Operating System
    *Work in Progress*

Rebase
    *Work in Progress*

RISC
Reduced Instruction Set Computer
    a {term}`CPU`  characterized by a simplified and streamlined
    set of instructions, optimized for efficient and fast execution of basic operations.
    {term}`RISC` processors typically prioritize speed over complexity.

    Examples of {term}`RISC` {term}`Architectures <Architecture>` are {term}`arm64`,
    {term}`armhf`, {term}`RISC-V`, {term}`ppc64el`, and {term}`PowerPC`.

    See also:
    * [Reduced instruction set computer (Wikipedia)](https://en.wikipedia.org/wiki/Reduced_instruction_set_computer)

RegEx
Regular Expression
    A sequence of characters that specifies a text-matching pattern. String-search
    algorithms usually use these patterns for input validation or find (and replace)
    operations on strings.

    While this general term stems from theoretical computer science and formal language
    theory, people usually think of {term}`Perl Compatible Regular Expressions` ({term}`PCRE`).

Repository
Repo
    *Work in Progress*

RFC
Request for Comments
    *Work in Progress*

    See also:
    * [Request for Comments (Wikipedia)](https://en.wikipedia.org/wiki/Request_for_Comments)

RoM
Request of Maintainer
    *Work in Progress*

RoP
Request of Porter
    *Work in Progress*

RoQA
Requested by the QA team
    *Work in Progress*

RoST
Request of Security Team
    *Work in Progress*

RoSRM
Request of Stable Release Manager
    *Work in Progress*

Restricted
    A {term}`Component` of every {term}`Ubuntu` [Series](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archiveseries) in the
    {term}`Ubuntu Archive` that contains {term}`Closed Source <Closed Source Software>`
    {term}`Packages <Package>` which are supported and maintained by {term}`Canonical`.

    See also:
    * [Components](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivecomponents)

RISC-V
    *Work in Progress*

riscv64
    *Work in Progress*

Root
    *Work in Progress*

Rules File
    The `debian/rules` file in a {term}`Source Package`.

    See also:
    * [Basic overview of the `debian/` directory](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/reference/debian-dir-overview/)
    * [Section 4.9. Main building script (Debian Policy Manual v4.6.2.0)](https://www.debian.org/doc/debian-policy/ch-source.html#main-building-script-debian-rules)

s390x
    *Work in Progress*

Seeds
    Seeds are lists of packages that define which packages go into the
    {term}`Main` component of the {term}`Ubuntu Archive` and which packages
    go into the distribution {term}`images <Image>`.

Series
    A **series** refers to the {term}`Packages <Package>` in the {term}`Ubuntu Archive`
    that target a specific Ubuntu version. A series is usually referred
    to by its {term}`Code name`.

    See also:
    * [Series (explanation)](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archiveseries)

SLA
Service-level Agreement
    *Work in Progress*

Shell
    *Work in Progress*

Signature
    A digital signature is a cryptographic record that verifies the authenticity
    and integrity of data.

    Every {term}`Package` in the {term}`Ubuntu Archive` is digitally signed,
    enabling users to detect data corruption during the download or unwanted/malicious
    modifications. Furthermore, some {term}`Upstream` projects sign their releases,
    which lets Ubuntu {term}`Maintainers <Maintainer>` and users of the corresponding
    packages verify that the {term}`Source Code` is from the developers of the
    upstream project.

    The tool {manpage}`gpg(1)` is commonly used to create and modify digital
    signatures. Further information can be found in the
    [GNU Privacy Handbook](https://www.gnupg.org/gph/en/manual.html#AEN136).

Signing Key
    *Work in Progress*

Source
    *Work in Progress*

Source Code
    The source code of a program is a set of human-readable instructions written in
    a programming language. Those instructions are later converted to machine code
    to be directly executed by a computer. Generally, programmers study and modify
    software by reading and editing the source code.

Source Package
    A {term}`Debian` **source package** contains the {term}`Source` material used
    to build one or more {term}`Binary Packages <Binary Package>`.

    See also:
    * [Source Packages (explanation)](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/package-model/#sourcepackages)

Source Tree
    *Work in Progress*

Sponsor
    *Work in Progress*

SRU Verification Team
    *Work in Progress*

Stable Release Managers
    *Work in Progress*

SRU
Stable Release Update
    *Work in Progress*

Stack
    In computer science, a **Stack** is a data-structure that can store a
    collection of elements linearly with two primary operations:

    - "Push": adds an element to the collection
    - "Pop": removes the most recently added element in the collection

    Stack implementations also often have a "Peak" operation to see the most
    recently added element in the collection without removing it.

    The name **Stack** stems from the analogy of items "stacked" on top of
    each other like a stack of plates, where you have to remove the plates
    above to access the plates below.

    See also:
    * [Stack (abstract data type)](https://en.wikipedia.org/wiki/Stack_(abstract_data_type))

Staging Environment
    *Work in Progress*

Standard Output
    *Work in Progress*

tarball
    A file in the {manpage}`tar(5)` archive format, which collects any number of
    files, directories, and other file system objects (symbolic links, device nodes, etc.)
    into a single stream of bytes. The format was originally designed to be used with
    tape drives, but nowadays it is widely used as a general packaging mechanism.

    See also: {term}`orig tarball`

Text Encoding
    **Text encoding** refers to the method or schema used to represent and store
    text characters in a digital format. It involves assigning numerical codes
    (typically binary) to each character in a character set, which allows computers
    to process and display text. 

    For example, `ASCII` and `UTF-8` are commonly used text encoding formats.

    The choice of a text encoding format is essential for ensuring proper character
    representation, especially when dealing with different languages and special
    characters.

TLS
Transport Layer Security
    *Work in Progress*

TPM
Trusted Platform Module
    *Work in Progress*

TUI
    Abbreviation for text-based {term}`User Interface`.

Ubuntu
    The word "**ubuntu**" is derived from the pronunciation of an an ancient
    African word **`oǒ’boǒntoō`** meaning **"humanity to others"**. It is often
    described as reminding us that **"I am what I am because of who we all are"**.

    The Ubuntu {term}`Operating System` tries to bring that spirit to the world of
    computers and software. The Ubuntu {term}`Distribution` is a {term}`Debian`-based
    {term}`Linux` distribution and aims to represent the best of what the world's
    software community has shared with the world.

    See also:
    * [The story of Ubuntu](https://ubuntu.com/about)
    * [Ubuntu ethos](https://ubuntu.com/community/ethos)
    * [Ubuntu Project Governance](https://ubuntu.com/community/governance)

Ubuntu Archive
Archive
    The **Ubuntu Package Archive** is an {term}`APT` {term}`Repository` that is
    pre-configured by default on Ubuntu installations. It hosts {term}`Debian`
    {term}`Binary Packages <Binary Package>` (`.deb` files) and
    {term}`Source Packages <Source Package>` (`.dsc` files).

    See also:
    * [Ubuntu Package Archive (explanation)](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/)

Ubuntu autopkgtest Cloud
    *Work in Progress*

    See also:
    * [autopkgtest.ubuntu.com](https://autopkgtest.ubuntu.com/)

Ubuntu Base Packages
    {term}`Packages <Package>` that are in the {term}`Main` or {term}`Restricted`
    {term}`Component`. These are packages maintained by {term}`Canonical`,
    because they are fundamental for {term}`Ubuntu`.

    See also: {term}`Main Inclusion Review`

UCA
Ubuntu Cloud Archive
    *Work in Progress* 
    
    See also:
    * [Cloud Archive (Ubuntu Wiki)](https://wiki.ubuntu.com/OpenStack/CloudArchive)

Ubuntu Code of Conduct
    *Work in Progress*

    See also: 
    * [Ubuntu Code of Conduct](https://ubuntu.com/community/ethos/code-of-conduct)

UCT
Ubuntu CVE Tracker
    *Work in Progress*
    
    See also:
    * [Launchpad CVE tracker](https://launchpad.net/ubuntu-cve-tracker)
    * [Ubuntu CVEs](https://ubuntu.com/security/cves)

Ubuntu Delta
    A modification to an {term}`Ubuntu` {term}`Package` that is derived from a {term}`Debian`
    Package.

    See also:
    * [Upstream & Downstream (explanation)](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/upstream-and-downstream/)

Ubuntu Desktop
    *Work in Progress*

UDS
Ubuntu Developer Summit
    Between 2004 and 2012, Ubuntu releases were planned during regularly scheduled
    summits, where the wider Ubuntu community would come together for planning
    and hacking sessions. This event occurred two times a year, each one
    running for a week. The discussions were highly technical and heavily
    influenced the direction of the subsequent Ubuntu release.

    These events were called the "Ubuntu Developer Summit" (UDS).

    Since November 2022, these events were continued as the "Ubuntu Summit" (US)
    to include the broader Ubuntu community and not only developers.
    
    See also:
    * [Ubuntu Developer Summit is now Ubuntu Summit (Ubuntu Blog)](https://ubuntu.com/blog/uds-is-now-ubuntu-summit),
    * [Developer Summit (Ubuntu Wiki)](https://wiki.ubuntu.com/DeveloperSummit)

Ubuntu Discourse
    A {term}`Discourse` instance about general Ubuntu development that
    is accessible to the general public, where you can find discussions,
    announcements, team updates, documentation and much more.

    Feel free [to introduce yourself](https://discourse.ubuntu.com/c/intro/101).

    See also:
    * [Ubuntu Discourse](https://discourse.ubuntu.com)

Ubuntu ESM Team
    *Work in Progress*

    See also:
    * [Ubuntu ESM Team](https://launchpad.net/~ubuntu-esm-team)

Ubuntu flavors
    **Ubuntu flavors** are {term}`Distributions <Distribution>` of the default Ubuntu
    releases, which choose their own default applications and settings. Ubuntu flavors are
    owned and developed by members of the Ubuntu community and backed by the full
    {term}`Ubuntu Archive` for {term}`Packages <Package>` and updates.

    Officially recognized flavors are:

    - [Edubuntu](https://www.edubuntu.org/)
    - [Kubuntu](https://kubuntu.org/)
    - [Lubuntu](https://lubuntu.me/)
    - [Ubuntu Budgie](https://ubuntubudgie.org/)
    - [Ubuntu Cinnamon](https://ubuntucinnamon.org/)
    - [Ubuntu Kylin](https://www.ubuntukylin.com/index-en.html)
    - [Ubuntu MATE](https://ubuntu-mate.org/)
    - [Ubuntu Studio](https://ubuntustudio.org/)
    - [Ubuntu Unity](https://ubuntuunity.org/)
    - [Xubuntu](https://xubuntu.org/)

IRCC
Ubuntu IRC Council
    *Work in Progress*

    See also:
    * [IRC Council (Ubuntu Wiki)](https://wiki.ubuntu.com/IRC/IrcCouncil)

Ubuntu Keyserver
    *Work in Progress*

Ubuntu Pro
    *Work in Progress*

    See also:
    * [Ubuntu Pro (homepage)](https://ubuntu.com/pro)

Ubuntu Server
    *Work in Progress*

Ubuntu SRU Team
    *Work in Progress*

    See also:
    * [Ubuntu SRU Team](https://wiki.ubuntu.com/StableReleaseUpdates#Contacting_the_SRU_team)

Ubuntu Sponsors
    *Work in Progress*

    See also:
    * [Ubuntu Sponsors](https://launchpad.net/~ubuntu-sponsors)

Ubuntu Security Sponsors
    *Work in Progress*

    See also:
    * [Ubuntu Security Sponsors Team](https://launchpad.net/~ubuntu-security-sponsors)

Ubuntu Stable Release
    Ubuntu stable releases are officially-published versions of Ubuntu
    and their {term}`packages <Package>`.

US
Ubuntu Summit
    The *Ubuntu Summit* (US) is a continuation of the {term}`Ubuntu Developer Summit`
    since November 2022. The change in name aims to broaden the scope, which
    opens the event up to additional audiences.

    While the {term}`Ubuntu Developer Summit` was focused on technical development,
    the talks and workshops of the **Ubuntu Summit** will cover development as well
    as design, writing, and community leadership with a wide range of technical
    skill levels.
    
    The name also results in a nifty new acronym, **US**, or more appropriately,
    simply "Us". This fits very nicely with the meaning of {term}`Ubuntu`,
    *"I am what I am because of who we all are"*.

    If you have any question feel free to send an email at
    [summit@ubuntu.com](mailto:summit@ubuntu.com).

    Also, check out the [Ubuntu Summit mailing list](https://lists.ubuntu.com/mailman/listinfo/summit-news).

    You can find more information at the [Ubuntu Summit page](https://ubuntu.com/summit).

URI
Uniform Resource Identifier
    *Work in Progress*

    See also:
    * [Uniform Resource Identifier (Wikipedia)](https://en.wikipedia.org/wiki/Uniform_Resource_Identifier)

URL
Uniform Resource Locator
    *Work in Progress*

    See also:
    * [URL (Wikipedia)](https://en.wikipedia.org/wiki/URL)

Universe
    A {term}`Component` of every Ubuntu
    [Series](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archiveseries)
    in the {term}`Ubuntu Archive` that contains {term}`Open Source <Open Source Software>`
    {term}`Packages <Package>` which are supported and maintained by the Ubuntu
    community.

    See also: 
    * [Components](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/archive/#archivecomponents)

Unix
    **Unix** is an {term}`Operating System` whose development started in the
    late 1960s at AT&T Bell Labs. It is characterized by its multi-user and
    multi-tasking capabilities, hierarchical file system, and a suite of
    {term}`Command Line <Command Line Interface>` utilities.
    Unix has been influential in shaping modern Operating Systems and remains
    the basis for various Unix-like systems, including {term}`Linux` and macOS.

    See also:
    * [Unix (Wikipedia)](https://en.wikipedia.org/wiki/Unix)

Upstream
    A software project (and associated entities), another software project
    depends on directly or indirectly.

    See [Upstream (explanation)](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/upstream-and-downstream/#upstream)

UX
User Experience
    The overall experience and satisfaction a user has while interacting with
    a product or system. It considers usability, accessibility, user flow, and
    the emotional response of users to ensure a positive and efficient interaction
    with the {term}`User Interface` and the product as a whole.

UI
User Interface
    Refers to the visual elements and design of a digital product or application
    that users interact with. It includes components like buttons, menus, icons,
    and layout, focusing on how information is presented and how users navigate
    through the interface.

UIFe
User Interface Freeze Exception
    *Work in Progress*

    See also:
    * [Ubuntu development process](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/explanation/development-process/)

VCS
Version Control System
    A software tool or system that enables developers to track and manage changes
    to their {term}`Source Code` and collaborate with others effectively. It maintains
    a history of Source Code revisions, allowing users to revert to previous
    versions, track modifications, and work on different {term}`Branches <Branch>`
    of Source Code simultaneously. **Version Control Systems** are crucial
    for Source Code management and collaboration in {term}`Open Source Software`
    development projects.

WoU
Waiting on Upstream
    *Work in Progress*

    See also: {term}`Upstream`

Watch File
    The `debian/watch` file in a {term}`Source Package`.

    See also:
    * [Basic overview of the `debian/` directory](https://canonical-ubuntu-packaging-guide.readthedocs-hosted.com/en/latest/reference/debian-dir-overview/)
    * {manpage}`uscan(1)`
    * [Section 4.11. Upstream source location (Debian Policy Manual v4.6.2.0)](https://www.debian.org/doc/debian-policy/ch-source.html#upstream-source-location-debian-watch)

x64
    See {term}`amd64`

x86
    See {term}`i386`

x86-64
    See {term}`amd64`

x86_64
    See {term}`amd64`

:::

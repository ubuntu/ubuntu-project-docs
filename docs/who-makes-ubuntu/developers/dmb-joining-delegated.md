(dmb-joining-delegated)=
# Delegated Developers

Delegated Developers are members of a [delegated development group](https://wiki.ubuntu.com/UbuntuDevelopers/TeamDelegation) in Launchpad.
They are collectively responsible for the maintenance of a subset of packages in Ubuntu.
This role is similar to the {ref}`dmb-joining-ppu` and {ref}`dmb-joining-packageset` roles, except that the package set is governed by a delegated team.

The Delegated Developer answers questions of other developers to expand their understanding of packaging work and provides guidance for prospective Ubuntu developers regarding technical issues.


## Sponsorship

Delegated Developers understand packaging concepts, having substantial experience of uploading packages through a sponsor.
Within their own Package Set, they can apply their knowledge by uploading new packages, and updating existing packages, in their area of expertise.

They are considered as {ref}`dmb-joining-contributing` when working outside their delegated subset of packages, but they can contribute to other areas of Ubuntu in cooperation with another developer.


## Current delegated teams

Delegated teams admitting their own members:
: * [Ubuntu Desktop Developers](https://wiki.ubuntu.com/DesktopTeam/Developers) (Launchpad: [`~ubuntu-desktop`](https://launchpad.net/~ubuntu-desktop))
: * [Mythbuntu Developers](http://www.mythbuntu.org/development/policy) (Launchpad: [`~mythbuntu-dev`](https://launchpad.net/~mythbuntu-dev))
: * [Kubuntu Developers](https://wiki.ubuntu.com/Kubuntu/KubuntuDevelopers) (Launchpad: [`~kubuntu-dev`](https://launchpad.net/~kubuntu-dev))
: * [Edubuntu Developers](https://wiki.ubuntu.com/Edubuntu/Documentation/Developers) (Launchpad: [`~edubuntu-dev`](https://launchpad.net/~edubuntu-dev))
: * [Ubuntu Kernel Uploaders](https://wiki.ubuntu.com/Kernel/Dev/UploadRights) (Launchpad: [`~ubuntu-kernel-uploaders`](https://launchpad.net/~ubuntu-kernel-uploaders))
: This delegation includes individual per-package upload privileges for packages in the corresponding team package set.


Delegated teams whose prospective members apply to the {ref}`Developer Membership Board <dmb>`:
: * [Ubuntu Kylin](https://wiki.ubuntu.com/UbuntuKylin) Developers (Launchpad: [`~ubuntukylin-dev`](https://launchpad.net/~ubuntukylin-dev))
: * Ubuntu GNOME Developers (Launchpad: [`~ubuntu-gnome-dev`](https://launchpad.net/~ubuntu-gnome-dev))
: * Ubuntu Bazaar Uploaders (Launchpad: [`~ubuntu-bzr-dev`](https://launchpad.net/~ubuntu-bzr-dev))
: * Ubuntu CLI/Mono Uploaders (Launchpad: [`~ubuntu-cli-mono-dev`](https://launchpad.net/~ubuntu-cli-mono-dev))
: * Ubuntu Desktop Extra Uploaders (Launchpad: [`~ubuntu-desktop-extra-dev`](https://launchpad.net/~ubuntu-desktop-extra-dev))
: * Ubuntu Input Methods Uploaders (Launchpad: [`~ubuntu-input-methods-dev`](https://launchpad.net/~ubuntu-input-methods-dev))
: * Ubuntu Mozilla Uploaders (Launchpad: [`~ubuntu-mozilla-uploaders`](https://launchpad.net/~ubuntu-mozilla-uploaders))
: * Ubuntu OIF uploaders (Launchpad: [`~ubuntu-oif-dev`](https://launchpad.net/~ubuntu-oif-dev))
: * Ubuntu Qt5 Uploaders (Launchpad: [`~ubuntu-qt5-dev`](https://launchpad.net/~ubuntu-qt5-dev))
: * Ubuntu Schooltool Uploaders (Launchpad: [`~ubuntu-schooltool-dev`](https://launchpad.net/~ubuntu-schooltool-dev))
: * Ubuntu Sugar Uploaders (Launchpad: [`~ubuntu-sugar-dev`](https://launchpad.net/~ubuntu-sugar-dev))
: * Ubuntu Server Developers (Launchpad: [`~ubuntu-server-dev`](https://launchpad.net/~ubuntu-server-dev))
: * Ubuntu Studio Uploaders (Launchpad: [`~ubuntu-studio-uploaders`](https://launchpad.net/~ubuntu-studio-uploaders))
: * Ubuntu Ubuntu One Uploaders (Launchpad: [`~ubuntu-ubuntuone-dev`](https://launchpad.net/~ubuntu-ubuntuone-dev))
: * Ubuntu Xorg uploaders (Launchpad: [`~ubuntu-xorg-dev`](https://launchpad.net/~ubuntu-xorg-dev))
: * Ubuntu Zentyal Uploaders (Launchpad: [`~ubuntu-zentyal-dev`](https://launchpad.net/~ubuntu-zentyal-dev))
: * Ubuntu Zope Uploaders (Launchpad: [`~ubuntu-zope-dev`](https://launchpad.net/~ubuntu-zope-dev))

Package sets with no owning team:
: * `lubuntu`
: * `xubuntu`
: * `ubuntu-mate`


(form-a-delegated-team)=
## Form a delegated team

Email `devel-permissions@lists.ubuntu.com` with:

* A description of your set of packages. The {ref}`dmb` will use this description to verify which packages should belong to the set.
  This description should contain a name for the Package Set, and set out criteria against which packages can be tested for membership.

* An initial list of packages.

* An initial list of members (with their Launchpad IDs).

The DMB, at its next meeting (providing this is more than 7 days after the application), will discuss the Package Set with the applicants and then vote on its creation.
When applying for a set, please be prepared to attend a DMB meeting.

The Developer Membership Board will take care of creating the Package Set and ensuring that the requested permissions are granted.


## Requesting changes to delegated teams

Email `devel-permissions@lists.ubuntu.com` with the proposed change(s) and the Package Set to which the change applies.
  
A DMB member will review the request and either make the change or ask for further clarification if it us unclear that the package falls under the delegation granted when the team was created.


## Voting

As with {ref}`dmb-joining-ppu` and {ref}`dmb-joining-packageset`, members through Delegated teams are granted a vote when the {ref}`dmb` or Technical Board are polling Ubuntu Developers.


## Join a delegated team

Check the general requirements for {ref}`ubuntu-membership`.

Review the requirements for the specific team of interest. If the team is one that admits its own members, apply to that team for membership via their own process.
Otherwise, apply via the DMB using the {ref}`usual application process <dmb-application>`.


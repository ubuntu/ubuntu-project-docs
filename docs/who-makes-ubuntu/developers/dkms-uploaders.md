(dkms-uploaders)=
# Ubuntu Kernel DKMS Uploaders

The [Ubuntu Kernel DKMS Uploaders team](https://launchpad.net/~ubuntu-kernel-dkms-uploaders)
maintains the kernel-dkms package set, which provides out-of-tree kernel modules.

These packages require specialised knowledge of kernel internals, module compilation, ABI
compatibility and DKMS framework mechanics.

The maintenance of these packages includes tasks such as:

* Verifying that all DKMS packages continue to function correctly whenever a new kernel is
  released upstream
* Ensuring compatibility with stable kernel upstream updates across all supported Ubuntu
  releases
* Addressing build failures caused by kernel ABI changes
* Testing DKMS packages on real hardware or in emulated environments to ensure proper
  module loading, functionality and system stability

Members of this team are inducted only after a careful application and screening process.
The sections below describe the general member profile of the ubuntu-kernel-dkms-uploaders team
and the application and screening process.


(dkms-member-profile)=
## Member profile

Members of the delegate team must have demonstrated proficiency in the following areas.


(dkms-upstream-downstream-knowledge)=
### Upstream/downstream knowledge

Members must understand the derivative distribution model and how packages flow from
upstream through Debian to Ubuntu. This includes knowledge of how deltas are added and
managed, when adding a delta is appropriate, and the maintenance burden that comes with
carrying Ubuntu-specific changes.

Members must also be familiar with the Ubuntu and Launchpad packaging data model,
including the various pockets and components of each series, source-only uploads and how
the build process works.


(dkms-ubuntu-development-knowledge)=
### Ubuntu development knowledge

Members must understand the Ubuntu development process, in particular knowledge of the
Ubuntu development cycle milestones and freezes and what their purpose is.

Members must demonstrate the ability to create high quality patches as well as the ability to
merge and sync packages from Debian to Ubuntu, understanding when automatic syncs occur
and when manual intervention is required. In doing so members must also demonstrate the
knowledge and capability to communicate and track package changes using Launchpad bugs.

Additionally members must have a thorough understanding of the SRU process, and a history
of preparing and shepherding SRU uploads for DKMS packages through the verification and
release process.


(dkms-quality-assurance)=
### Quality assurance

Members must understand that uploading a package is not the end of the process. They
should be proficient in monitoring the proposed pocket migration queue and resolving issues
that prevent migration, including build failures and autopkgtest regressions.

Members must be capable of writing new autopkgtest for DKMS packages and running them
locally to validate changes before upload.


(dkms-specific-knowledge)=
### DKMS-specific knowledge

Members must possess deep knowledge of the DKMS framework, including how it builds,
installs, upgrades, and removes kernel modules across multiple installed kernels.

They must understand kernel ABI stability, how upstream kernel changes can break
out-of-tree modules, and techniques for adapting modules to new kernel versions, without
breaking compatibility with older ones.

Members must understand both the upstream kernel release schedule and the Ubuntu kernel
release schedule and how it drives the timing and urgency of DKMS package updates.


(dkms-member-responsibilities)=
## Member responsibilities

Members of the team will be collectively responsible for the maintenance of all packages in
the kernel-dkms package set across all supported Ubuntu releases as well as the development
release.

When appropriate, members should contribute fixes and improvements back to the upstream
project and to Debian, thus reducing the delta Ubuntu carries and benefiting the broader
open source community.

They are expected to stay informed about upcoming kernel changes and their impact on
DKMS packages, and to coordinate with other team members on maintenance activities.

Members must exercise great care in their work, understanding that their efforts have a
direct impact on every Ubuntu user who relies on out-of-tree kernel modules, the Ubuntu
release team and the SRU team.


(dkms-application-requirements)=
## Application requirements

Prospective members of the team must have a history of substantial and direct contribution
to the distribution, and in particular to DKMS packages, over a period of at least six months.

Given that DKMS work requires a deep understanding of both kernel code and kernel release
cadence, candidates must already possess [Kernel Package Upload Rights](https://wiki.ubuntu.com/Kernel/Dev/UploadRights)
as a prerequisite for application.

Candidates must demonstrate practical experience and proficiency through the following
minimum requirements:

* At least 10 good-quality SRU uploads for DKMS packages, demonstrating not only the
  ability to work on the package code itself, but also a detailed understanding of the SRU
  process specifics and the skills and knowledge needed to successfully shepherd packages
  through the verification process and ensure correct transition from the proposed pocket to
  updates.

* At least 10 good-quality uploads of DKMS packages to the development series,
  demonstrating not only the ability to work on the package code itself, but also showing an
  understanding of and ability to contribute fixes back to upstream and/or Debian, thereby
  minimising the Ubuntu delta needed.

* At least 5 package syncs or merges of DKMS packages from Debian, demonstrating an
  understanding of how Merge-o-Matic works and why it is critical to sync and merge packages
  as early as possible in the development cycle to reduce the delta between Ubuntu and
  Debian/upstream.

It is important to emphasise that these thresholds refer to good-quality uploads, that is,
uploads that were well-prepared as proposed and did not require significant rework, fixups or
corrections. It is expected that candidates will go through an initial learning phase guided by
mentors and sponsors; uploads made during that phase that required substantial revision do
not count toward these minimums.

Moreover, applicants must possess the knowledge highlighted in the
{ref}`member profile <dkms-member-profile>` section.


(dkms-application-process)=
## Application process

An applicant who is ready to apply must prepare their application, following the
{ref}`DMB general guidelines for a good application <dmb-aspects-of-a-good-application>`,
and seek endorsements from their sponsors. At least two different endorsements must be
obtained from existing members of the team, who can confirm they have worked with the
applicant sufficiently to judge their skills and that the application meets the criteria outlined
above. Once endorsements are secured, the application should be submitted via email to the
Ubuntu kernel-team mailing list (kernel-team@lists.ubuntu.com) for review.

The applicant will be notified of a scheduled Matrix meeting ({matrix}`kernel`) where they
will be interviewed, covering:

* A brief self introduction
* A review of the applicant's contribution history
* Technical questions related to DKMS maintenance and Ubuntu development process
* Discussion of any concerns raised during the application interview

Only existing members of the team will be allowed to vote on new applicants. An applicant
must receive a majority of ACKs from the voting members, with a minimum of 3 ACKs, to be
added to the team. If a majority of voting members provides NACKs, the application is
rejected. In that case, the voting members must provide the applicant with clear and
actionable suggestions on the areas that need improvement. These suggestions will be
verified during the next voting session when the applicant re-applies.

Upon successful completion of the application process, an announcement will be made to
both the Ubuntu kernel-team mailing list and the devel-permissions@lists.ubuntu.com mailing
list, and the applicant will be added to the DKMS team by a team administrator.

Meeting logs for each voting session will be saved in a publicly visible repository on
Launchpad.


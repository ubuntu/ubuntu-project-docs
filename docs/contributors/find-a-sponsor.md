(find-a-sponsor)=
# How to find a sponsor


The ability to upload directly to the Archive is carefully managed to ensure
the stability and security of Ubuntu. New contributors don't have upload rights
immediately -- instead they must request {ref}`sponsorship` from someone who
*does* have upload rights whenever they...

- Make changes to existing packages or incremental updates
- Submit security updates or bug fixes
- Introduce new packages to Ubuntu


## Preparation

If you follow the {ref}`guidance for contributors <how-to-contribute>`, your
changes should be properly prepared for sponsorship. In general, try to remember
that someone else needs to understand what you've done -- so "show your working"
as they say.

For any non-trivial change, it can be good practice to discuss your plans with
a potential sponsor *after* you think you know what needs done, but *before*
you've actually done it. Often, an experienced developer can offer
alternative approaches that may save you time or provide better results.


## Seeking sponsorship

There are three ways to find a sponsor: two formal, and one informal.


### Via a merge proposal

The first formal way is by filing a {ref}`Merge Proposal (MP) <merge-proposals>`
with `canonical-<your-team>` (e.g. `canonical-server-reporter` for Ubuntu Server
team members) set as a reviewer. Make sure to mention in your MP comments that 
you're also in need of sponsorship. If the reviewer has upload rights they can
take care of sponsoring the upload as well.


### Via a Launchpad bug

The second formal (and more traditional) approach is to
[file a bug report in Launchpad](https://bugs.launchpad.net/ubuntu/+filebug),
attach your changes as a {manpage}`debdiff(1)`, and then subscribe
`ubuntu-sponsors` (or `ubuntu-security-sponsors` for security issues). This
approach is generally used only if a package is not in `git-ubuntu` or if an MP
can't be generated for some reason.

To request sponsorship, follow these steps:

1. [File an Ubuntu bug in Launchpad](https://bugs.launchpad.net/ubuntu/+filebug)
   or follow up on an existing one

1. Add the necessary files, such as patches or `.diff.gz` files, according to
   the package's requirements
   
   * If the change is a patch, follow the patch tagging guidelines
   
   * For security updates, follow the
     [security update packaging guidelines](https://wiki.ubuntu.com/SecurityTeam/UpdatePreparation#Packaging)

1. Link your changes to the bug; see
   [Seeking Sponsorship](https://wiki.ubuntu.com/DistributedDevelopment/Documentation/SeekingSponsorship)

1. Subscribe `ubuntu-sponsors` or `ubuntu-security-sponsors` to the bug.


### Via chat

Informally, you can also try approaching possible sponsors via chat or email
and directly asking them for sponsorship.

This can be helpful in the case of urgent issues, or if you want to find
sponsors outside your usual circle.

Canonical employees typically have ready sponsors from their team mates.
However, sponsors can also be found elsewhere in Canonical or in the wider
community. Having a diversity of sponsors can be useful when
{ref}`applying <path-to-upload-rights>` for {ref}`MOTU <membership-in-MOTU>`
and {ref}`Core Dev <membership-in-core-dev>`,
since it will demonstrate breadth of your experience and trustworthiness.


## Responding to feedback from sponsors

If a sponsor reviews your changes and requests further changes, make the
changes to the branch you were working on, then commit them by running:

```none
$ bzr commit
```

Now, push your changes to {term}`Launchpad`. Since `bzr` remembers the previous
push location, you can run:

```none
$ bzr push
```

After pushing your changes, reply to the sponsor's request explaining the
changes you made, and request a re-review. You can also respond directly on the
merge proposal page in Launchpad.


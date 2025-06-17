(sponsorship-process)=
# Sponsorship process

```{note}
This content comes [from the wiki](https://wiki.ubuntu.com/SponsorshipProcess)
It has not yet been reviewed for currency or accuracy.
Last updated: 2023
```

The sponsorship process is designed to allow prospective developers to have
packages reviewed and uploaded. Sponsorship provides a means of learning about
Ubuntu development and lowers the entry barrier for contribution.

The process outlined here is aimed at dealing with incremental changes to
existing packages within Ubuntu. For mentoring on the creation of entirely new
packages, please see the
{ref}`New Packages process <new-packages>`.

## Requesting Sponsorship

To make use of Ubuntu merge proposals, follow these steps:

* [set up the tools](http://packaging.ubuntu.com/html/getting-set-up.html)
* [get the source](http://packaging.ubuntu.com/html/udd-intro.html)
* [work on the package](http://packaging.ubuntu.com/html/fixing-a-bug.html#work-on-a-fix)
* [seek sponsorship](https://wiki.ubuntu.com/DistributedDevelopment/Documentation/SeekingSponsorship)

```{admonition} Incorrect redirects
:class: important
The first three links in this list point to the old packaging guide, which
automatically redirects to the new packaging guide, but the content in the new
packaging guide hasn't been brought over from the old one?
```

The traditional process involves:

* [File an Ubuntu bug in Launchpad](https://bugs.launchpad.net/ubuntu/+filebug)
  or follow up on an existing one. If you think this might be a security update,
  please review the security team's
  "[Issues that warrant a security update](https://wiki.ubuntu.com/SecurityTeam/UpdateProcedures#Issues.2520that.2520warrant.2520a.2520security.2520update)".

* Attach your work:

  * In the case of a patch (using the same upstream version), attach your
    suggested patch (["Submitting the fix"](https://packaging.ubuntu.com/html/fixing-a-bug.html#submitting-the-fix-and-getting-it-included)).
    For security updates, please see the [security update packaging guidelines](https://wiki.ubuntu.com/SecurityTeam/UpdatePreparation#Packaging).

  * If the package uses a patch system (run `what-patch` in the source tree to
    find out), use `edit-patch` to comply with the choice of patch system, then
    make sure to follow the [patch tagging guidelines](https://wiki.ubuntu.com/UbuntuDevelopment/PatchTaggingGuidelines).
    Package-specific patch tags may be documented in `debian/README.source`.

  * Review [our general patch guidelines](https://wiki.ubuntu.com/UbuntuDevelopment/Patches)
    that give tips on how to get the patch included upstream as well.

  * In the case of a upstream version update attach the `.diff.gz` file (and
    link to the new upstream source if necessary.

* Subscribe `ubuntu-sponsors` or `ubuntu-security-sponsors` as appropriate
  (details below).

### Packages maintained on Launchpad Code Hosting

Special attention is required if packages are maintained on Launchpad's Code
Hosting. You might run into a message like this, when getting the source
package:

```
$ apt-get source ubuntu-artwork
Reading package lists... Done
Building dependency tree       
Reading state information... Done
NOTICE: 'ubuntu-artwork' packaging is maintained in the 'Bzr' version control system at:
https://code.launchpad.net/~ubuntu-art-pkg/ubuntu-artwork/ubuntu
Please use:
bzr get https://code.launchpad.net/~ubuntu-art-pkg/ubuntu-artwork/ubuntu
to retrieve the latest (possible unreleased) updates to the package.
[...]
$ 
```

In these cases please consider registering a
[merge proposal](https://help.launchpad.net/BranchMergeProposals). It will make
the life of the maintainers a lot easier.

### Forwarding patches upstream

Review [Debian/Bugs](https://wiki.ubuntu.com/Debian/Bugs) for more information.

### New packages

The process for getting NEW packages (packages which are not in Ubuntu at all
yet) reviewed is explained at {ref}`new-packages`.

## Getting help

If you are unsure how to get a package sponsored, would like to add a new
package or submit a patch, or have questions getting your package upstream
into Debian, the Ubuntu Patch Pilots can help.

To find out how to get in touch, please check the
[program documentation](https://ubuntu.com/community/contribute/ubuntu-development/ubuntu-patch-pilots|program documentation).

Generally asking for help in `#ubuntu-motu` or `#ubuntu-devel` is definitely on
topic too. :-)

## Sponsoring

**To review Ubuntu merge proposals, check out
[these UDD instructions](http://packaging.ubuntu.com/html/udd-uploading.html)**.

Sponsorship is organized into two teams:

* [Ubuntu Sponsors](https://launchpad.net/~ubuntu-sponsors)

* [Ubuntu Security sponsors](https://launchpad.net/~ubuntu-security-sponsors)

Do not assign a bug to anyone if it needs sponsorship.

Any Ubuntu developer who is interested in acting as a sponsor is welcome to
apply for membership in the appropriate team.

You can see the currently pending requests at:

* `https://bugs.launchpad.net/ubuntu/+bugs?field.subscriber=ubuntu-sponsors`

* `https://bugs.launchpad.net/ubuntu/+bugs?field.subscriber=ubuntu-sponsors&field.component=3&field.component=4`

* `https://bugs.launchpad.net/~ubuntu-security-sponsors/+subscribedbugs`

Or combined at:

* **[Sponsoring reports](http://sponsoring-reports.ubuntu.com/)**

```{note}
Occasionally it may be useful to check if there are non-ubuntu bugs that fail
to be noticed: `https://bugs.launchpad.net/bugs/+bugs?field.subscriber=ubuntu-sponsors`
```

The `ubuntu-sponsors` team handles general sponsorship of packages in Ubuntu.
The `ubuntu-security-sponsors` team handles sponsorship of packages in the
`security` pocket for all components.

## Workflow for review and sponsorship

If you are processing the universe sponsorship queue, please review the
[Code reviews](https://wiki.ubuntu.com/UbuntuDevelopment/CodeReviews),
[MOTU Sponsorship procedure documentation](https://wiki.ubuntu.com/MOTU/Sponsorship/SponsorsQueue),
or
[Security team sponsors queue](https://wiki.ubuntu.com/SecurityTeam/SponsorsQueue).





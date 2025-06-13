(archive-administration)=
# Archive Administration

- What *is* archive admin?

-----

> From wiki
> This page details the processes for the
> [Ubuntu Package Archive Administrators](https://launchpad.net/~ubuntu-archive)
> team, and hopefully provides a decent guide for new members of the team.

> Bugs should be filed against the appropriate packages, and the team
> **subscribed** (*not assigned*) to the bug.

> The requests can be found at
> [subscribed bugs](https://launchpad.net/~ubuntu-archive/+subscribedbugs). This
> sometimes fails to load, if in doubt
> [this page](https://bugs.launchpad.net/~ubuntu-archive/+bugs?orderby=-date_last_updated&start=0)
> also includes assigned bugs but works more reliably.

> Team members may assign bugs to themselves and mark them *In Progress* if
> they're working on them, or discussing them; to act as a lock on that request.

> ## Client-side tools

> We are transitioning towards client-side administration as the necessary
> facilities become available via the Launchpad API. To get hold of
> [these tools](https://code.launchpad.net/+branch/ubuntu-archive-tools):

> ```bash
> $ git clone lp:ubuntu-archive-tools
> ```
-----


## Archive Administrators

- define the team involved
- Processes the team is responsible for:

  For each process:
  - Explain what the process is, what it's for, and how to do it
- how does one become an archive admin?

## AA team responsibilities

The main tasks the Archive Admin team is responsible for are:

* {ref}`aa-new-review`
* {ref}`aa-package-removal`
* {ref}`aa-package-overrides`

Less commonly, they are asked to do the following tasks. These are explained in
more depth in the {ref}`aa-secondary-tasks` page.

* Priority mismatches
* Signing bootloaders
* Phasing on delivering SRU updates
* i386 whitelist updates

The following list of Archive-related services needs to be updated with details
of the charmed hosted services as they are migrated.

- {ref}`aa-archive-related-services` 


## Communication

How to get in touch with the AA team?

## Museum

* {ref}`aa-museum`

## Not AA content anymore

* {ref}`not-AA`


```{toctree}
:titlesonly:

aa-new-review
wiki-new-review
aa-package-removal
wiki-package-removal
aa-package-overrides
wiki-package-overrides
aa-secondary-tasks
aa-archive-related-services
not-AA
aa-museum
```






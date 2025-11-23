(ubuntu-developers)=
# Ubuntu Developers

```{toctree}
:titlesonly:
:hidden:

dmb-joining-prospective
dmb-joining-contributing
dmb-joining-ppu
dmb-joining-packageset
dmb-joining-delegated
dmb-joining-MOTU
dmb-joining-sru-dev
dmb-joining-core-dev
dmb-application
```

Ubuntu Developers represent an important part of the creation of Ubuntu. They
have a direct influence on the software included in Ubuntu and whether it meets
the needs of end users. They are responsible for ensuring that Ubuntu works, and
works as well as it can with the resources available.

Everybody is welcome to work on any package they want to improve and we value
these contributions. If you don't have upload rights yet,
{ref}`sponsors <sponsorship>` can review your work and upload it for you.

If you wanted to categorize the different kinds of involvement and upload rights
in Ubuntu, it would look like this:

* {ref}`dmb-joining-prospective` who probably just started contributing
  to Ubuntu.

* {ref}`dmb-joining-contributing`, who were recognized with
  {ref}`ubuntu-membership`.

* {ref}`Per-Package Uploaders (PPU) <dmb-joining-ppu>`,
  who can upload specific packages.

* {ref}`Package Set uploaders <dmb-joining-packageset>`

* {ref}`Ubuntu Developers (from delegated teams) <dmb-joining-delegated>`,
  who can upload to a specific [Package Set](https://wiki.ubuntu.com/ArchiveReorganisation/Permissions).

* {ref}`MOTU <dmb-joining-motu>`, who can upload to
  {ref}`universe and multiverse <archive-components>`.

* {ref}`SRU developers <dmb-joining-sru-dev>`, who can upload any package but
  only to stable releases.

* {ref}`Ubuntu Core Developers (core-dev) <dmb-joining-core-dev>`,
  who can upload to all areas of Ubuntu.

See {ref}`path-to-upload-rights` below for a visual guide.


(ubuntu-developer-membership)=
## Ubuntu Developer membership

Ubuntu Developers get all the {ref}`benefits of Ubuntu Membership <member-perks>`.
They also get:

* Voting privileges to confirm Ubuntu [Technical Board](https://wiki.ubuntu.com/TechnicalBoard) and {ref}`dmb` nominations.

* The opportunity to be nominated for the Developer Membership Board.

* Access to all [Valve-produced games for Steam](https://lists.ubuntu.com/archives/ubuntu-devel-announce/2014-February/001079.html).

```{note}
A few Per-Package Uploaders are not members of [`ubuntu-dev`](https://launchpad.net/~ubuntu-dev) and are not eligible for these benefits.
One way to check this is to run `bin/lp-check-membership` from the `lptools` package.
```


(path-to-upload-rights)=
## Path to upload rights

```{note}
The links shown on this page are subject to sudden changes over the next
few months as more of the documentation it refers to is migrated here. Please
expect inconsistencies -- and feel welcome to correct any links you find that
are incorrect.
```

These interactive charts show the skills needed to obtain permissions for
uploading changes to the Ubuntu Package Archive. They can be used as a guide
to help build your applications for upload rights on:

* {ref}`PPU <dmb-joining-ppu>` and {ref}`Package Sets <dmb-joining-packageset>`
* {ref}`MOTU <dmb-joining-motu>`, 
* {ref}`Core Developer <dmb-joining-core-dev>`


(uploaders-journey)=
### The uploader's journey

Since Ubuntu is based on Debian, they share a similar technical skill set. This
means that as a contributor, you may want to contribute to Debian as well as
Ubuntu, or just focus on one (as you prefer).

This diagram shows the overall expected progression paths you can take as a
contributor. Click any of the nodes to learn more.


```{include} /who-makes-ubuntu/developers/diagrams/overall-path.txt
```


(upload-path-basics)=
### Basics

As a {ref}`Prospective Developer <dmb-joining-prospective>` you should start your learning here.
These topics will get you started with a good foundation for your future contributions to Ubuntu.
As you complete tasks that build your confidence and skills, you can apply for Ubuntu Developer Membership as a {ref}`Contributing Developer <dmb-joining-contributing>`.

```{include} /who-makes-ubuntu/developers/diagrams/basics.txt
```

Once your team and/or mentor says you are ready for more, you can move onto the Intermediate-level tasks.


(upload-path-intermediate)=
### Intermediate

This set of topics are more in-depth, as well as being quite hands-on.
Completing the tasks in this set will prepare you for Advanced-level work.

```{include} /who-makes-ubuntu/developers/diagrams/intermediate.txt
```

Once you have done enough of these tasks that your team/mentor says you are
ready to continue your journey, you can move onto the Advanced topics.

At this time, you may also be ready to apply for Per-Package Upload (PPU) rights.
This will depend very much on the package you are interested in gaining upload rights for.
Some of the more complex packages will need you to complete the Advanced path first.


(upload-path-advanced)=
### Advanced

```{include} /who-makes-ubuntu/developers/diagrams/advanced.txt
```

With enough of these tasks under your belt to demonstrate your skills and
experience, you can move onto the Expert topics.

At this point, you are likely to be ready to apply for Per-Package Upload (PPU)
rights, or if there is a set of packages you are interested in working on, you
can apply for Package Set instead.


(upload-path-expert)=
### Expert 

The Expert-level studies will prepare you for becoming a member of MOTU, where
you will help to maintain packages in `universe`.

If you want to, you can continue your Expert-level studies by further
specializing in `main` -- you need to do this if you want to apply for
the Core Developer role.

```{include} /who-makes-ubuntu/developers/diagrams/expert.txt
```



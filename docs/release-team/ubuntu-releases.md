(ubuntu-releases)=
# Ubuntu releases

## Release cadence

Ubuntu follows a strict time-based release cycle. Every six months since 2004,
Canonical publishes a new Ubuntu version ({term}`series`) and its set of
{term}`packages <Package>` are declared stable (production-quality).

Simultaneously, a new version begins development; it is given its own
{term}`Code name`, but is also referred to as the "Current Release in
Development" or "{term}`Devel`" for short.

Every Ubuntu series receives the same production-grade support quality,
but different types of release receive support for different lengths of time.


(lts-releases)=
### LTS releases

Since 2006, every fourth release, made every two years in April, receives
Long Term Support ({term}`LTS`). An estimated 95% of all Ubuntu installations
are LTS releases.

LTS releases receive five years of standard security maintenance for all
packages in the `main` {ref}`component <archive-components>`. An
[Ubuntu Pro](https://ubuntu.com/pro) subscription provides access to
[Expanded Security Maintenance](https://ubuntu.com/security/esm) (ESM),
which includes security fixes for packages in the `universe` component,
and covers both `main` and `universe` beyond the five years of standard support.

```{note}
Due to the strict time-based six-monthly release cycle, LTS releases only happen
in even-numbered years (e.g. `20`, `22`, `24`) in April (`04`). The only
exception to this rule was Ubuntu 6.06 LTS (Dapper Drake).
```


(point-releases)=
### Point releases

To ensure that a fresh install of an {ref}`LTS release <lts-releases>` works on
newer hardware and does not require a large download of additional updates,
Canonical publishes **point releases** that include all the updates made so far.

The first point release of an LTS is published three months after the initial
release, and repeated approximately every six months at least until the next LTS
is published. In practice, Canonical may publish even more point releases for an
LTS series, if it turns out to be popular.

For example, the Ubuntu 16.04.7 LTS (Xenial Xerus) point release was published
more than four years after the initial release of Ubuntu 16.04 LTS.


(interim-releases)=
### Interim releases

In the years between LTS releases, Canonical also produces **interim releases**,
sometimes also called "regular releases".

Many developers use interim releases because they provide newer compilers or
access to newer {term}`kernels <Kernel>` and newer libraries. They are often
used inside rapid DevOps processes like {term}`CI`/{term}`CD` pipelines where
the lifespan of an artifact is likely to be shorter than the support period of
the interim release.

Interim releases are production-quality and supported for nine months, with
enough time provided for users to update -- but these releases do not receive
the long-term commitment of LTS releases.


### Why does Ubuntu use time-based releases?

Ubuntu releases represent an aggregation of the work of thousands of independent
software projects. The time-based release process provides users with the best
balance of the latest software, tight integration, and excellent overall
quality.


## Ubuntu version format

```none
YY.MM[.POINT-RELEASE] [LTS]
```

Ubuntu version identifier as used for Ubuntu releases consist of four
components, which are:

`YY`
: The 2-digit year number of the initial release.

`MM`
: The 2-digit month number of the initial release.

`POINT-RELEASE`
: The {ref}`point release <point-releases>` number starts at `1` and increments
  with every additional point release.

  This component is omitted for the initial release, in which case zero is
  assumed.

`LTS`
: Any Ubuntu release that receives Long Term Support is marked with `LTS`.

  Any Ubuntu release that does not receive long term support omits this
  component.


A full list of all the current releases, their codenames, release notes, and
supported lifetimes can be found on the {ref}`list-of-releases` page.


## Editions

Ubuntu Desktop provides a Graphical User Interface ({term}`GUI`) for everyday
computing tasks, making it suitable for personal computers and laptops.
{term}`Ubuntu Server`, on the other hand, provides a Text-based User Interface
({term}`TUI`), optimized for server environments, which allows machines on the
server to be run headless, focusing on server-related services and applications,
making it ideal for hosting web services, databases, and other server functions.

Additionally, each release of Ubuntu is available in minimal configurations,
which have the fewest possible packages installed: available in the installer
for Ubuntu Server, Ubuntu Desktop, and as separate cloud images.

Ubuntu is also available for the Windows Subsystem for Linux ({term}`WSL`).
Ubuntu on WSL provides a full terminal-based development environment on Windows
that is less resource-intensive than a traditional VM or dual-boot setup. Since
Ubuntu 24.04.2 LTS (Noble Numbat), LTS releases of Ubuntu are made available as
tar-based images, which can be installed without the Microsoft Store.

Canonical publishes Ubuntu on all major public clouds, and the
[latest image](https://cloud-images.ubuntu.com/) for each LTS version will
always include any security updates provided since the LTS release date, until
two weeks prior to the image creation date.


## Ubuntu flavors

Ubuntu flavors are {term}`distributions <Distribution>` of the default Ubuntu
releases that choose their own default applications and settings. Ubuntu
flavours are owned and developed by members of the Ubuntu community and backed
by the full {term}`Ubuntu Archive` for packages and updates.

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

In addition to the officially recognized flavors, dozens of other {term}`Linux`
distributions take Ubuntu as a base for their own distinctive ideas and
approaches.

Flavors generally support their releases for 3 years in LTS versions (although
there can be exceptions).


## Further reading

- [The Ubuntu life cycle and release cadence](https://ubuntu.com/about/release-cycle)
- [Ubuntu flavors](https://ubuntu.com/desktop/flavors)
- [Ubuntu releases](https://releases.ubuntu.com/)
- [Ask a bug supervisor](https://answers.launchpad.net/launchpad/+question/140509)

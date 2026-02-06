(release-cycle)=
# Release cycle

Each {ref}`Ubuntu release <ubuntu-releases>` cycle follows the same general
pattern with a number of major phases. Ubuntu contributors are expected to
follow this process closely to ensure their work is aligned with that of others.

Because of the time-based release cycle, Ubuntu contributors must coordinate
well to produce an on-time release. For every release, key dates are set out in
the release schedule (
[the 24.04 LTS (Noble Numbat) release schedule](https://discourse.ubuntu.com/t/noble-numbat-release-schedule/35649)
provides an example).


## Beginning a new release

The Ubuntu infrastructure is prepared for a new development branch at the start
of each cycle. The package build system is set up, the toolchain is organized,
{term}`seeds` are branched, and many other pieces are made ready before
development can properly begin. Once these preparations are made, the new
development release is officially announced on the
[`ubuntu-devel-announce`](https://lists.ubuntu.com/mailman/listinfo/ubuntu-devel-announce)
mailing list and opened for uploads to the
{ref}`Package Archive <package-archive>`.

```{note}
See the Ubuntu 24.04 LTS (Noble Numbat)
[Archive opening announcement email](https://lists.ubuntu.com/archives/ubuntu-devel-announce/2023-October/001341.html)
as an example.
```


## Planning

Ubuntu contributors discuss the targeted features for each release cycle via the
various channels (Matrix, Discourse, Launchpad). Some of these come from
strategic priorities for the distribution as a whole, and some are proposed by
individual developers.

The broader open-source community gets together at the {term}`Ubuntu Summit`
(similar but different to the past
{term}`Ubuntu Developer Summits <Ubuntu Developer Summit>`) to share experiences
and ideas, and to inspire future projects covering development as well as
design, writing, and community leadership with a wide range of technical skill
levels.


## Merging with upstream and feature development

The first phase of the release cycle is characterized by bringing new releases
of {term}`upstream` components into Ubuntu, either directly or via
{ref}`merges-syncs`. The development of planned projects for the release often
begins while merging is still underway, and the development accelerates once the
Package Archive is reasonably consistent and usable.

The automatic import of new package versions from Debian ends at the
{ref}`debian-import-freeze`.


(monthly-snapshots)=
## Monthly snapshots

During a release's development phase, the
[Canonical Release Management](https://launchpad.net/~canonical-ubuntu-qa) team
organizes
[monthly snapshot releases](https://discourse.ubuntu.com/t/supercharging-ubuntu-releases-monthly-snapshots-automation/61876).
These releases are not intended to be used in production, but rather are
curated, testable milestones that can be used to detect failure modes during the
development cycle.


## Stabilization and Freezes

Developers should increasingly exercise caution in making changes to Ubuntu to
ensure a stable state is reached in time for the final release date. The Release
Team incrementally restricts modifications to the Ubuntu Package Archive. The
dates when these restrictions get enabled are called "Freezes".

During freezes, developers must request {ref}`freeze-exceptions` to approve
changes. The Release Team posts the current Release Schedule as a Discourse
article under the
["Release" topic](https://discourse.ubuntu.com/c/project/release/38). It shows the
typical order and length of the various Freezes.

See {ref}`freezes` for an overview of the individual stabilization Freezes.


## Finalization

As the {ref}`final-release` approaches, the focus narrows to fixing
"showstopper" bugs and thoroughly validating the installation images. Every
image is tested to ensure the installation methods work as advertised.
Low-impact bugs and other issues are deprioritized to focus developers on this
effort.

This phase is vital, as severe bugs that affect the experience of booting or
installing the images must be fixed before the Final Release. By contrast,
ordinary bugs affecting the installed system can be fixed with
{ref}`stable-release-updates`.


(final-release)=
## Final Release

Once the Release Team declares the {ref}`release-candidate` ISO stable and names
it the "Final Release", a representative of the team announces it on the
[`ubuntu-announce`](https://lists.ubuntu.com/archives/ubuntu-announce/) mailing
list.

```{note}
See, for example, the Ubuntu 24.04 LTS (Noble Numbat)
[release announcement](https://lists.ubuntu.com/archives/ubuntu-announce/2024-April/000301.html).
```


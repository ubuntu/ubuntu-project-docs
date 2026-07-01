(for-ubuntu-developers)=
# For Ubuntu developers

> "Ubuntu benefits from a strong Debian, and Debian benefits from a strong Ubuntu." — *Mark Shuttleworth*
>
> "Every Debian developer is also an Ubuntu developer, because one way to contribute to Ubuntu is to contribute to Debian." — *Mark Shuttleworth*
>
> "We incorporate Debian changes regularly, because that introduces the latest work, the latest upstream code, and the newest packaging efforts from a huge and competent open source community. Without Debian, Ubuntu would not be possible." — *Mark Shuttleworth*

This page is for Ubuntu developers who are thinking about contributing to Debian. It gives the current "best practice" with regard to collaboration with another distribution. This is not a requirement, but it can make everybody's life much easier to keep other distributions and upstream on the same page.

## Why should I care about Debian?
* Ubuntu is [Debian-based](https://ubuntu.com/community/docs/governance/debian).
* Debian supports more [hardware architectures](https://www.debian.org/ports/), so if you want to run something like Ubuntu in your (not so) new mips machine it will be really useful.
* Debian project has more volunteers than Ubuntu. Ubuntu community as a whole can benefit from it.
* Debian project is heavily committed to free software; its [free software guidelines](https://en.wikipedia.org/wiki/Debian_Free_Software_Guidelines) and [legal mailing list](https://lists.debian.org/debian-legal/) are well recognized by the community.

## What's stable, testing, unstable?
The **“stable”** distribution contains the latest officially released distribution of Debian. The **“testing”** distribution contains packages that haven't been accepted into a “stable” release yet. The **“unstable”** (codenamed **sid**) distribution is where active development occurs.

Information about Debian releases, like [how "testing" becomes "stable"](https://www.debian.org/doc/manuals/debian-faq/ftparchives.en.html#frozen) and [release codenames](https://www.debian.org/doc/manuals/debian-faq/ftparchives.en.html#codenames), can be found at: [**Debian Releases**](https://www.debian.org/releases/).

## I'm a Ubuntu user and I want to install Debian
The Debian project develops **d-i**, the Debian installer. It is used by both Debian and Ubuntu. If you feel comfortable installing Ubuntu, you will have a similar experience with Debian.

Note that Ubuntu (by default) installs GNOME. Debian will ask you which sets of packages you want to install. You can read the [Debian Stable Release Installation Guide](https://www.debian.org/releases/stable/installmanual) for more details.

## Why contribute to another distribution?
Ubuntu regularly takes updates from Debian. Packages that are newer in Debian are merged or synced in Ubuntu. It would be impossible to manage universe without Debian, as Ubuntu has far less manpower.

Contributing to Debian makes everyone's life simpler because Ubuntu syncs its packages from there. Fewer Ubuntu-specific changes mean less work in the long run.

## Forwarding bug reports
When you find or fix a bug in Ubuntu, check if it applies to Debian. If so, report it in the [Debian Bug Tracking System](https://bugs.debian.org/).
* Always mention you are running Ubuntu.
* Only forward bugs you have verified apply to Debian.
* Be careful with severity levels.

## Getting new software in Debian
### Why would I get my work in Debian?
* **Reviewer time:** Getting packages through Debian provides more specialized mentorship.
* **Visibility:** Your package reaches a massive user base and gets better bug reports.
* **Avoid duplication:** Prevents a Debian developer from packaging the same software differently.

### How do I do it?
Refer to [Getting help with Debian and Ubuntu collaboration](https://wiki.debian.org/DerivativesFrontDesk).

#### Required packaging changes
* **debian/changelog:** The version should end in `-1` (the Debian revision). Target `unstable` instead of an Ubuntu release.
* **debian/control:** Update the `Maintainer` field with your info. Remove `XSBC-Original-Maintainer`.
* **Section:** Remove Ubuntu-specific prefixes (e.g., change `universe/sound` to `sound`).

#### Notifying Debian
If you just want to notify Debian, **file an RFP** (Request For Package). Mention your Ubuntu package and provide a link to the source.

#### Maintain the package yourself
If you want to maintain it in Debian:
1. **File an ITP** (Intent To Package).
2. **Find a sponsor** (Reviewer) via `#debian-mentors` on OFTC or the [Mentoring FAQ](https://wiki.debian.org/DebianMentorsFaq).
3. **Use pbuilder** to build against Debian unstable.

## See Also
* [About Debian](https://www.debian.org/intro/about)
* [Debian Social Contract](https://www.debian.org/social_contract)
* [A Brief History of Debian](https://www.debian.org/doc/manuals/project-history)

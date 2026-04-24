(for-ubuntu-developers)=
# For Ubuntu developers

[Ubuntu](https://www.ubuntu.com) is based on [Debian](https://www.debian.org/). This page covers how Ubuntu developers can contribute to Debian.

## Why contribute to Debian?

- Ubuntu regularly incorporates changes from Debian — packages newer in Debian are merged or synced in Ubuntu
- Contributing to Debian reduces Ubuntu-specific changes, meaning less work to maintain
- Debian has more volunteers and specialized mentorship available
- Your package reaches more users through Debian

## Debian releases

Debian has three main releases:

- **stable** — The latest officially released distribution
- **testing** — Packages that haven't been accepted into stable yet
- **unstable** (sid) — Where active development occurs

See [Debian Releases](https://www.debian.org/releases/) for more information.

## Forwarding bug reports

When you find or fix a bug in Ubuntu, check if it applies to Debian too. If so, report it in the [Debian Bugtracking System](https://bugs.debian.org/).

Tips:

- Always mention you are running Ubuntu, not Debian
- If unsure whether Debian is affected, don't file the bug — ask a Debian user to reproduce it first
- Read [How to Report Bugs Effectively](https://www.chiark.greenend.org.uk/~sgtatham/bugs.html)

## Getting new software into Debian

### Option 1: File an RFP

File an **RFP** (Request For Package) to notify Debian your package exists. A Debian developer may adopt it and upload it to Debian. It will then return to Ubuntu through normal merges.

### Option 2: Maintain it yourself

To maintain the package in Debian yourself:

1. **File an ITP** (Intent To Package)
2. Find a sponsor to review and upload your package
3. Learn to use [pbuilder](https://wiki.debian.org/PbuilderHowto) to build against Debian unstable
4. Use the [#debian-mentors](irc://irc.oftc.net/debian-mentors) IRC channel for help

See the [Debian WNPP page](https://www.debian.org/devel/wnpp/) for the process.

### Required packaging changes

When preparing a package for Debian:

- **debian/changelog**: Remove `-0ubuntu1` from version; use `-1` instead
- **debian/control**: 
  - Set yourself as Maintainer (unless a team maintains it)
  - Remove `XSBC-Original-Maintainer` field
  - Remove Ubuntu component from Section (e.g., `sound` not `universe/sound`)

## See also

- [About Debian](https://www.debian.org/intro/about)
- [Debian Social Contract](https://www.debian.org/social_contract)
- [To Fork or Not To Fork: Lessons From Ubuntu and Debian](https://mako.cc/writing/to_fork_or_not_to_fork.html)
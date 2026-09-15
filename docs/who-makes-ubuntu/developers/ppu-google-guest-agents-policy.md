(ppu-google-guest-agents-policy)=
# PPU review boundaries for the Google "guest agent" packages

If you hold (or are applying for) {ref}`Per-Package Upload rights <dmb-joining-ppu>` for the Google guest agents,
then this page is for you! It covers the following packages:

* [`google-guest-agent`](https://launchpad.net/ubuntu/+source/google-guest-agent)
* [`google-osconfig-agent`](https://launchpad.net/ubuntu/+source/google-osconfig-agent)
* [`gce-compute-image-packages`](https://launchpad.net/ubuntu/+source/gce-compute-image-packages)
* [`google-compute-engine-oslogin`](https://launchpad.net/ubuntu/+source/google-compute-engine-oslogin)

PPU rights usually cover leaf packages, a happier place where a bad upload is more of an inconvenience to people who
installed that package (and usually nobody else). These four agent packages are a whole different beast; they might
only be seeded inside Google Compute Engine Ubuntu images, *but* inside those images they can:
* run as root
* start during boot
* decide who is allowed to log in

And that last point is probably the worst one. If we get it wrong we don't just get a bug report, we can effectively
"brick" VMs.

This page describes what you can upload "on your own" (i.e. in your capacity as a PPU uploader) and what warrants
a second pair of eyes from a core dev. This complements the general {ref}`PPU expectations <dmb-joining-ppu>` and the
[SRU exceptions](https://documentation.ubuntu.com/sru/) already documented for these packages.

## Why are these packages special?

In the beginning, these agents did simple instance bring up. They have since expanded and now do several things
that you wouldn't expect from an ordinary archive package in `main`. They:
* Run very early in boot
* Configure `sshd` and supply the `authorized_keys` that `OSLogin` relies on
* Ship `PAM` and `NSS` modules that sit directly in the auth path
* Use and can execute on metadata sent to them by the compute platform (and not necessarily by the VM owner)

Fortunately the blast radius is *relatively* small as they are only seeded in Google images and (almost) nothing depends
on them. But within that radius the failure modes can be catastrophic, hard/impossible to fix remotely and
fundamentally, bad for Ubuntu's image. So the bar here is much higher!

## What you can upload directly

No extra ceremony is required should the uploads be:
* New upstream code cuts that stay within the **existing** integration
* Packaging and build fixes (including per-arch build failures)
* Refreshing vendored dependency trees or toolchain bumps that don't change the shipped behaviour
* No change rebuilds
* `d/changelog`, `d/copyright`, `d/rules`, etc. and any documentation or test tidy ups (`d/control` may also be changed
  assuming the change doesn't include edits to any relationships, see `Relationships between packages` below)
* Writing and/or improving `autopkgtests` (do more of this!)

## What needs a second opinion

Get review from a Core Developer before uploading anything in the categories below. This applies whether you wrote the
change or inherited it from an upstream release (i.e. "upstream did it" is an explanation *not* a review).

Trust material
: Anything that installs, generates, renews or removes certificates/keys or other trust material, or anything that
  touches the trust store.

Authentication and authorisation
: Anything touching the `PAM` stack, `NSS` config, `sshd` config, `AuthorizedKeysCommand` handling, `sudoers` or how
  accounts and groups get created and/or removed.

Relationships between packages
: Any new or removed binary package, and any change to `Depends`, `Recommends`, `Breaks`, `Replaces`, `Conflicts` or
  `Provides`.

Files owned by other packages
: Any maintainer script or install rule that creates, edits or removes files outside the agents' own paths.

New functionality
: Updates that stay within the existing integration don't need extra approval, conversely **new** integrations should
  receive a review from a core dev.

If you're not sure, assume it should have a second review. Asking is better than an authentication regression!

## Getting a second review

1. Put the change up as a merge proposal against the package's git repository
2. Ask for a reviewer in the {matrix}`ubuntu-devel` Matrix channel and subscribe
   [`~ubuntu-sponsors`](https://launchpad.net/~ubuntu-sponsors) to the bug
3. Note who reviewed it and their `ack` in the bug before you upload
4. If nobody's available (and it's genuinely urgent), upload the part that doesn't need review and upload the rest
   separately. Splitting an upload up might be annoying, but it's much less annoying than the alternative

## Bugs and SRUs

All these packages have documented SRU exceptions, however two of those rules are worth repeating:

* Track each stable release update with **a single process bug**, not a separate bug per individual fix
* If a pinned or vendored dependency moves, record each one in the SRU bug along with the versions it moved **from** and
  **to** (yes, even when the vendor tree is enormous as it often is)

One more point which was learned the hard way: if a single problem spans more than one of these packages, file just
**one bug with a task per affected source package**, and title it after the symptom rather than the fix you have in
mind. Splitting one problem across several bugs hides its true form from reviewers, and tends to end with two sponsors
each holding half of it and neither of them seeing the whole.

(request-package-removal)=
# How to request a package removal

Packages that are removed from Debian are semi-automatically removed from
Ubuntu `universe` {ref}`on a regular basis <source-package-removals-via-debian>`
by the {ref}`Archive Admin team <archive-administration>`. However, packages are
not removed from Ubuntu `main` without an explicit request, and nor are packages
which originated elsewhere.


## The removal request

To request removal of a package, file a bug against the package. The bug must
have the following elements:

* The release to remove it from

* What source and binary packages you expect to be removed

* A rationale for {ref}`why they should be removed <justification-for-removal>`.
  Examples:

  * In Noble please remove `bin:foo-old-stuff` from `src:foo` as it blocks
    migration of the new version which is no more building it

  * In questing please remove `src:bar` and all of its binaries, they are
    dysfunctional in that release XX, because ...

  * In plucky please remove `src:foobar` and all of its binaries, they block
    the transition of `snafu` and `foobar` upstream is orphaned and won’t be
    updated to work with the new versions of the overall stack

  * Please remove `src:arrr` from noble, because all binaries it used to
    build have been taken over by `src:pirate` now

* Confirmation that the binary packages have no `reverse-depends` (no other
  package depends on them). To do so, check the instructions in
  {ref}`check-reverse-dependencies`.
  Copy and paste the output from whichever tool you use into the bug.

* Mention if the request is limited to a particular architecture

Once the bug is ready, as per the above list, subscribe the `ubuntu-archive`
team to the bugs.


## Getting help

If you need help deciding whether a package ought to be removed,
please discuss on the `ubuntu-devel` mailing list rather than asking the
Archive Administrators.



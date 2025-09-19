(transitions)=
# Transitions

Unlike an ordinary {ref}`package migration <proposed-migration>`, when a major
build dependency gets updated with a new version that includes
{term}`API`/{term}`ABI` changes, it can require rebuilding and re-testing all
the packages that need that build dependency.

The new dependency (and the ecosystem of packages dependent on it) are kept in
the `-proposed` pocket until this process is completed, at which point the
group of packages is then allowed to migrate into the `-release` pocket.

This process is referred to as a **Transition**.

Very large transitions require a concerted, organized effort, and that's what
we'll primarily focus on in this document. Smaller transitions often go through
automatically, or sometimes with a bit of manual assistance, as described in the
{ref}`proposed-migration` page, but some of the tips in this document may be of
use in sorting out complications.

A specific focus will be on transitions involving language runtimes, such as
PHP.


## General process

A transition will sequence through several phases, each involving a different
workflow:

- {ref}`transitions-pre-transition-preparation`

- {ref}`transitions-introduce-new-dependency`

- {ref}`transitions-update-default-version`

- {ref}`transitions-phased-rebuilds-of-ecosystem`

- {ref}`transitions-resolve-build-test-and-dependency-issues`

- {ref}`transitions-migrate-new-dependency`

- {ref}`transitions-remove-old-dependency`

- {ref}`transitions-stabilize-ecosystem`


(transitions-pre-transition-preparation)=
## Pre-transition preparation

Before starting a new transition, consider its status in Debian. It can be
an order of magnitude more work to go ahead of Debian with a transition, so it
pays to wait, or to help Debian to complete their transition before starting it
in Ubuntu.

In particular, even if the new version is present in Debian, if it is not yet
set as the default version then there may still be plenty of transition issues.

Sometimes, a transition will start prematurely via the auto-sync process. For
example, Debian may have completed a transition to a new major version that you
planned to wait on until the next release. To correct this issue, ask the
Archive Admins to remove the new language dependency, and then add it to the
blocklist. See [LP: #1907177](https://bugs.launchpad.net/bugs/1907177) as an
example.

To register a transition in the transition tracker, add a config file
[such as revision 871](https://launchpad.net/~ubuntu-transition-trackers/ubuntu-transition-tracker/configs).
If you don't have direct commit access to that repository or need guidance, ask
on the usual development channels (#ubuntu-devel on IRC, Matrix etc).


(transitions-introduce-new-dependency)=
## Introduce new dependency

When you're ready to start the transition, the first step is to upload the new
language dependency. In some cases, it may have already successfully synced into
`-proposed` from Debian, but even then, make sure to review whether the old
dependency has an Ubuntu delta that needs to be carried forward.

For example, Debian allows multiple versions of PHP to exist in their archive,
but in Ubuntu we permit only a single version per release. To support this, each
version has some *Breaks*/*Replaces* on the previous version; these need to be
re-applied for each new major version.

If the new dependency is available from Debian but has been blocklisted in
Ubuntu, you can ask the Archive Admins to un-blocklist it. See
[LP: #1927288](https://bugs.launchpad.net/bugs/1927288) as an example.

If you decide to go ahead of Debian, you may need to manually sync the package
in from Debian `-experimental` via `syncpackage`. If Debian has packaged it but
not yet released it to `-experimental`, checkout their git tree and build the
package yourself.

If Debian hasn't even packaged the new version yet, and you can't do the work
in Debian yourself, you'll need to follow their processes as closely as you can.
Be careful to avoid choosing revision numbers that may conflict with Debian
later, and be aware that if your orig tarball differs from Debian's you won't
be able to auto-sync updates.

The main complication you may run into during this phase are build failures. For
example, upstream may have introduced some new dependencies not yet in the
Ubuntu Archive. Resolving these issues can involve
{ref}`MIRs <main-inclusion-review>`, pulling patches from upstream, and other
{ref}`how-to-fix-a-bug-in-a-package` activities.


(transitions-update-default-version)=
## Update default version

Language runtimes like PHP or Ruby have `php-defaults` or `ruby-defaults`
meta-packages that, among other things, define the version to use in the Ubuntu
release.

If Debian has already done the transition, it may be possible to sync or merge
their changes from `-unstable`, `-experimental`, or their git repository, if
it hasn't synced in already. Otherwise, you will need to manually adjust things;
typically you can look at past git commits to see what changes need doing.

Once the `*-defaults` package is uploaded, the fun begins.


(transitions-phased-rebuilds-of-ecosystem)=
## Phased rebuilds of ecosystem

The Transition Tracker can be used to identify a list of packages that need to
be rebuilt against the new dependency. However, the Transition Tracker may not
catch every necessary rebuild; for PHP it has been useful to manually maintain
a list of things needing to be rebuilt.

A script is available to help update packages that need rebuilding:

```bash
$ pkg-nochange <package>
```

Some packages depend on other packages in the ecosystem, so it is important to
note that the order things are uploaded in matters. The Transition Tracker
organizes packages by their dependency level to allow this phased work.

Unfortunately, the tracker doesn't make it clear when enough of one phase has
been completed to be able to start the next, so it can help to be aware of the
specific dependencies of things at higher levels so you can start them as soon
as possible.


(transitions-resolve-build-test-and-dependency-issues)=
## Resolve build, test, and dependency issues

This phase of the transition process typically requires the most time and
attention. The work is essentially {ref}`proposed-migration` work, and requires
many of the same tricks and skills.

With transitions in particular, a good first thing to check is if the build log
shows the right version. For example, with a transition to PHP 8.1, if the build
or test logs show "`php8.0`" anywhere, then that is usually a clue that the
package or one of its dependencies needs a (usually "no-change") rebuild.

Another good tip when dealing with transition-related migration issues is to
review the upstream Release Notes for the new version and all intermediate
versions. Pay particular attention to any documentation about deprecated
features and API changes.


(transitions-migrate-new-dependency)=
## Migrate new dependency

Once all the migration issues are handled the new language runtime (or other
major piece) will move to the `-release` pocket. However, this piece is a NEW
package and as such it'll be in `universe` rather than `main`. So, the next
step is to move it into `main`.

It's a good idea to file a bug report for tracking this work. But to actually
perform the `universe` --> `main` move you'll need the attention of an Archive
Admin. This can often be achieved via IRC in the `#ubuntu-release` channel on
the [Libera Chat server](https://libera.chat/). Since Archive Admins tend to be
very busy, it's important to be both patient and well organized, particularly
if there are any still-open or in-progress packages, or issues listed on the
excuses page against the package.


(transitions-remove-old-dependency)=
## Remove old dependency

Once the new version of the dependency is in place, the old version can be
removed. This can be done via a Launchpad bug report with the Archive Admin team
subscribed. See [LP: #1927264](https://bugs.launchpad.net/ubuntu/+source/php8.0/+bug/1927264)
as an example.


(transitions-stabilize-ecosystem)=
## Stabilize ecosystem

Theoretically, this last step should not be necessary since all migration issues
need to be resolved prior to the migration.

However, in reality there is often follow up work to tend to before the
transition project can truly be considered finished:

1. Forward appropriate remaining Ubuntu delta to Debian

1. Migration issues that (for whatever reason) only showed up post-migration

1. Additional updates on the Debian side that become available post-migration

1. Bug reports filed against packages within the ecosystem relating to upgrade
   failures or other problems caused with the newly-introduced package

>>>>>>> 9d833bf (Add process pages)

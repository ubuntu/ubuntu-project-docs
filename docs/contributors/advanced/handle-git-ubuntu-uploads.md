(how-to-handle-git-ubuntu-uploads)=
# How to handle `git-ubuntu` uploads

git-ubuntu is tooling that provides unified git-based workflows for the development of Ubuntu source packages. Use git-ubuntu for inspecting, working on, or contributing to Ubuntu source packages.

See {ref}`how-to-set-up-for-ubuntu-development` for basic prerequisites.


## Handle contributions using git-ubuntu

The following is a typical workflow for handling a git-ubuntu-based
contribution:

1. Clone the source package's official git-ubuntu repository
1. Add the contributor's remote tracking branch branch to the checkout
1. Review the branch
1. Build the proposed source package
1. Run autopkgtests

These steps are described in the sections below.


## Checkout the source package's official git-ubuntu repo

```none
$ git ubuntu clone <package> [dir-name]
```

For example, for a contribution to dovecot, you might run:

```none
$ git ubuntu clone dovecot dovecot-gu
```


## Add remote tracking branches to a git-ubuntu checkout

In order to review the sponsoree's changes, you'll want to add their
Launchpad username to your local checkout:

```none
$ git ubuntu remote add <sponsoree>
$ git checkout "<sponsoree>/<branch_name>" -b "<branch_name>"
```


## View the current state of the package for a given release

By default the `git ubuntu clone` command will checkout a branch named
'ubuntu/devel' that corresponds to the current Ubuntu development
release.  If you wish to examine the version of the source package for a
different Ubuntu version, git-ubuntu provides branches tracking all
releases and pockets.  For example:

```none
$ git branch -av | grep pkg/ubuntu/jammy
remotes/pkg/ubuntu/jammy            17f59d728 1:2.3.16+dfsg1-3ubuntu2 (patches unapplied)
remotes/pkg/ubuntu/jammy-devel      f5217e4fc changelog
remotes/pkg/ubuntu/jammy-proposed   f5217e4fc changelog
remotes/pkg/ubuntu/jammy-security   20252305d 1:2.3.16+dfsg1-3ubuntu2.1 (patches unapplied)
remotes/pkg/ubuntu/jammy-updates    f5217e4fc changelog
```

Most commonly, it will be the -devel branch you're interested in for
patch piloting work, so in general for the current jammy version of the
package, you would typically want to run:

```none
$ git checkout pkg/ubuntu/jammy-devel -b jammy-devel
```

Be aware that the -devel branch will include any changes currently
staged in -proposed that haven't been released yet.  If the git hash
for -devel doesn't match with at least one of the release pockets, that
may indicate this discrepancy.  In that case, some additional action may
be needed before the new changes can be uploaded.


(convert-a-debdiff-contribution-into-a-git-ubuntu-branch)=
## Convert a debdiff contribution into a git-ubuntu branch

Traditional contributions to Patch Pilot are in debdiff form, and in
terms of policy may be fine to handle directly, without use of
git-ubuntu.  However, if you prefer to handle it through git-ubuntu, you
may find the following workflow useful.

```none
$ mkdir review-lp<num>
$ cd review-lp<num>
$ wget <url-debdiff>
$ git ubuntu clone <package> <package>-gu
$ cd <package>-gu
$ git checkout pkg/ubuntu/<release>-devel -b review-lp<num>-<release>
$ debdiff-apply < ../<debdiff>
$ git commit debian/changelog -m changelog
$ changes=$(dpkg-parsechangelog -S Changes | grep "^ ")
$ update-maintainer -r
Restoring original maintainer: ...
$ git commit -a -m "${changes}"
$ update-maintainer
$ git commit debian/control* -m "update-maintainer"
```

That should result in a reasonable facsimile of a git ubuntu style
branch.  Depending on the contribution you might want to improve the
commit message or split the changes up into several commits instead of
one.

Once you're happy, you can proceed with reviewing and building using the
techniques described elsewhere.

For more info about traditional debdiff-based contributing, see the
[Reviewer Team's Knowledge Base](https://wiki.ubuntu.com/ReviewersTeam/KnowledgeBase).


(restore-empty-directories)=
## Restore empty directories

The experimental `git-ubuntu.experimental-emptydirfixup` tool restores
the empty directories locally as a workaround to the {ref}`empty directory problem <empty-directories>`. It takes a non-merge commit and
examines its parent to examine what empty directories have been lost. It
provides an equivalent replacement commit.

Run it with `fix-head` to replace `HEAD` with a commit that has empty
directories restored.

Run it with `fix-many` and a parameter pointing to a base commit to run
`git-rebase` to fix a set of commits.

Note that in both cases, the parent must have the empty directories in order
for them to be copied down through the fixed up commits. In the common case
where this tool is needed, you'll be starting from an "official" git-ubuntu
import tag or branch, so this will be true in these cases. However, this does
mean that you need to use `fix-many` all the way back to the first commit
after such an "official" commit. If you have intermediary un-fixed commits and
then just try to apply `fix-head` to the end, then it won't work as the
empty directories won't get copied forward.

Example of use:

```none
$ git ubuntu clone apache2
$ cd apache2
$ git tag -f base
  <add commits>
$ git-ubuntu.experimental-emptydirfixup fix-many base
$ dpkg-buildpackage $(git ubuntu prepare-upload args) -S
```


## Build a git-ubuntu source package branch for uploading

Assuming you have the branch checked out that you want to build, and are
running inside an Ubuntu release matching the MP's release (e.g. in an
LXC container), here is one way to build the source package from the
branch:

```none
$ install-build-deps
$ git ubuntu export-orig [--for-merge]
$ upload_args=$(git ubuntu prepare-upload args)
$ debuild --no-lintian -S -uc -us ${upload_args}
```

Following this workflow, with use of prepare-upload, the rich history
in the git commit log will be preserved and shared with other packagers,
and the merge proposal will get marked merged automatically.

The `install-build-deps` script can be found in the ubuntu-helpers repository, or
you can download it directly from [install-build-deps](https://git.launchpad.net/~ubuntu-server/+git/ubuntu-helpers/plain/bryce/install-build-deps).

This calculates the build requirements using the debian/control file in
the current directory tree.  This is more reliable than using
`apt-get build-dep <package>` when the changes you're reviewing have
some package dependency changes, such as when merging a new upstream
package.


## Run autopkgtests against a git-ubuntu branch

Here's a workflow snippet to toss the changes into a PPA and run tests
on that:

```none
$ ppa="ppa:<username>/<package>-review-lp<num>"
$ ppa create ${ppa}
$ dput ${ppa} <source-changes-file>
$ ppa wait ${ppa}
$ ppa tests ${ppa}
```

The last command will print clickable links to trigger the corresponding
autopkgtests.  When triggering them, keep in mind not all architectures
may be available in the PPA build.

If someone has already provided a PPA with a successfully built package,
you can skip most of that and just run the last command.  If another
pilot has already run the tests, then that'll print the results.

Since autopkgtests can take a while to run, you may want to consider
triggering them and then handing off the remainder of the review to the
next patch pilot.


## Close someone's git-ubuntu MP

Ask for the the MP to be closed for you, with an
explanation as to why and whether it should be set to Merged or Rejected.

Canonical employees: in Mattermost on the "Patch Pilot v2" channel, mention
`git-ubuntu-help` to request this.

General public: use #ubuntu-devel on Libera.Chat, mentioning
`git-ubuntu-help`.

For example:

```none
git-ubuntu-help please mark
https://code.launchpad.net/~abc/ubuntu/+source/hello/+git/foo/+merge/123
as merged as it has been uploaded.
```


## Find out why a git-ubuntu package repository is not up-to-date

1. Check `https://git.launchpad.net/ubuntu/+source/<package>` to see when
   git-ubuntu last updated the package repository.
1. Check `https://launchpad.net/ubuntu/+source/<package>/+publishinghistory` to
   see when the package was last updated by Launchpad.
1. Ask an admin if it's pending or with an error in the queue.
1. If there are no other signs, then developer debug is probably necessary.


## Deal with a package version deleted from the Archive

See {lpbug}`1852389`.

* Base on what is appropriate; both the deleted version and the currently
  present version may be fine, depending on why the deletion was performed.
* Rich history import won't be affected; it just expects your changelog parent
  to match your rich history base, and that'll generally be true anyway.
* You can't upload the same version that was deleted, so you may need to "jump"
  past that version. Exception: in a stable release, ubuntu1 -> ubuntu2
  (deleted) -> ubuntu1.1 works.

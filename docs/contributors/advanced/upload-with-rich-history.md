(how-to-upload-with-rich-history)=
# How to upload with rich history

See the {ref}`rich history explanation <rich-history>` for context.

:::{admonition} Not retaining rich history
:class: note
This applies to all workflows described below

If you don't wish to retain your rich history branch in Launchpad, you must
wait for the importer to retrieve it before you delete it. To be sure of the
timing, wait until after the rich history has appeared in the official
repository.
:::


## Standard workflow

These instructions make the following assumptions:

1. You had originally used `git ubuntu clone` to clone your repository.
1. You have a local branch checked out and your working directory is clean.
1. A previous git-ubuntu commit is an ancestor of your current commit.
1. You are at the top level of your source tree that is ready to build.

Push your branch, create the source package and changes file and upload them as
follows:

```console
dpkg-buildpackage -S $your_options $(git ubuntu prepare-upload args)
dput ubuntu ../<package>_<version>_source.changes
```

`git ubuntu prepare-upload args` will push your branch to your namespace
on Launchpad with the same remote branch name, and then output the appropriate
arguments for `dpkg-buildpackage` to include the appropriate reference to
the rich history in the changes file. See
{ref}`changes-file-headers`.


## Manual workflow

These instructions make the following assumptions:

1. A previous git-ubuntu commit is an ancestor of your current commit.
1. You have made a branch available at a public git URL on Launchpad that
   contains the rich history that will match your upload.
1. You are at the top level of your source tree that is ready to build.

Identify three items:

1. The publicly available URL on Launchpad to the git repository that contains
   your commit. This **must** begin with `https://git.launchpad.net/`.
1. A ref under which your commit can be found. For example, if you have pushed
   to a branch called `my-feature`, the ref would be
   `refs/heads/my-feature`.
1. The full commit hash of your commit.

Call `dpkg-buildpackage` as follows:

```console
dpkg-buildpackage -S \
    $your_options \
    --changes-option=-DVcs-Git=$repourl \
    --changes-option=-DVcs-Git-Ref=$gitref \
    --changes-option=-DVcs-Git-Commit=$commithash
```

Upload as usual:

```console
dput ubuntu ../<package>_<version>_source.changes
```


## Mangle workflow

These instructions make the following assumptions:

1. You have already built your source package and have the changes file ready
   to upload, except that it doesn't contain a rich history reference.
1. You have a local branch checked out, the checkout is identical to the source
   package you have prepared, and your working directory is clean.
1. A previous git-ubuntu commit is an ancestor of your current commit.
1. You are at the top level of your source tree that is already built.

Push your branch, adjust your changes file, re-sign it and upload as follows::

```none
$ git ubuntu prepare-upload mangle ../<package>_<version>_source.changes
$ debsign ../<package>_<version>_source.changes
$ dput ubuntu ../<package>_<version>_source.changes
```

`git ubuntu prepare-upload mangle` will push your branch to your
namespace on Launchpad with the same remote branch name, and then modify your
changes file to add the appropriate reference to the rich history, stripping
out the now-invalidated signature if it was present. See
{ref}`changes-file-headers`.

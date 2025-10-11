(empty-directories)=
# Empty directories

git's frontend doesn't let you add an empty directory. Usually the workaround
is to create any necessary empty directory at build time, or failing that to
create a placeholder file like `.empty` and check that in.

Neither of these approaches work for git-ubuntu's importer in the general case.
A source package can ship an empty directory by nature of the source package
format. But the build system (ie. `debian/rules`) in the source package
expects the source exactly as packed. Just as some builds break if empty
directories are missing, other builds might break if empty directories are not
actually empty.

Internally, git supports empty directories just fine. Directories map to git
tree objects. An empty tree object is the obvious way of representing an empty
directory, and git seems to accept them if they are represented this way. It's
just the git index and front end that do not support them.

In git-ubuntu, we therefore import empty directories "correctly" and losslessly
by using empty tree objects as necessary. However when at the client end such a
tree is checked out, the empty directories disappear as they pass through the
index, and get lost. A subsequent commit made by a developer then gets created
from the index, so does not include the empty directories even if they haven't
been touched.

This becomes an issue if a such a commit is subsequently presented back to
git-ubuntu as rich history to be adopted against an upload. git-ubuntu finds
that the upload (with empty directories) doesn't match the rich history commit
(with missing empty directories).

```none
WARNING: empty directories exist but are not tracked by git:
These will silently disappear on commit, causing extraneous
unintended changes. See: LP: #1687057.
Use "git commit --no-verify ..." to ignore this problem.
```

Source packages can ship with empty directories, but git's frontend
doesn't allow adding empty directories.  This can cause some confusion
for git ubuntu.  For patch piloting this is worth being aware of, since
the workaround needs to be done at point of upload.

For a full explanation and steps on how to handle it, see
{ref}`restore-empty-directories`.

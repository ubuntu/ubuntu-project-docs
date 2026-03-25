## Apply the fix

Whether the bug fix originates from an upstream project or your own work,
changes must be managed via patches:
- `debian/patches/`: This directory, located at the root of the package repository, stores the patch files themselves.
- `debian/patches/series`: This file defines the specific order in which the patches should be applied.
- `debian/changelog`: This file tracks the history of changes made to the package over time.

In our workflow, we use `git-ubuntu` to manage and apply these changes to packages.

### Step 1: Assign the task to yourself

First, going back to our [example case](https://bugs.launchpad.net/ubuntu/+source/postfix/+bug/1753470)

Go to the task (row) that starts with "bionic" and assign the task to yourself.

Switch the status to "in progress" using the yellow pencil icons.


### Step 2: Clone the package (if you haven't already)

Find the repository name:

```none
$ apt-cache show postfix | grep Source:
```

In this case, there is no Source field, so we just use `postfix`.

```none
$ git ubuntu clone postfix postfix-gu
$ cd postfix-gu
```


### Step 3: Make a branch based on the appropriate Ubuntu branch

The affected version of `postfix` is in Bionic, so we branch from
`bionic-devel`. It helps to use a descriptive branch name.

```none
$ git checkout pkg/ubuntu/bionic-devel -b postfix-sru-lp1753470-segfault-bionic
```


### Step 4: Make a patch to fix the issue (maybe)

If the only changes you made are within the `debian/` sub-directory, you don't
need a patchfile, and can skip this step.

On the other hand, if you've made changes to the upstream code (anything
outside of the `debian/` directory), you'll need to generate a patch in
`debian/patches`.

For instructions, see {ref}`how-to-work-with-debian-patches`.


### Step 5: Commit the patch

See {ref}`how-to-commit-changes`.

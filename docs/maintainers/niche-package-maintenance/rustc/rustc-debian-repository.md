(rustc-debian-repository)=
# `rustc-debian` repository

Because `rustc` is a versioned package, we have a bunch of different `rustc` repositories floating around.
These repositories tend to have changes in common from Debian's `rustc`, including changes in the `debian/` directory.
[`rustc-debian`](https://code.launchpad.net/~rust-toolchain/ubuntu/+source/rustc-debian) is a centralized repository where the Rust toolchain team stores those common changes in the form of patches.

## Why `rustc-debian`?

Our `rustc` is different than Debian's, and therefore our `debian/` directory has many changes over Debian's.
For most Ubuntu packages, which are non-versioned, these changes stay in the Git history, and are carried through time with the normal merge process.
However, when porting another `rustc` version to another Ubuntu version, our workflow starts with cloning fresh from Debian.
This means we need to re-apply the patches.

Previously, when we needed to re-use an existing commit on a fresh `rustc` port, we would:
- Find another team member with a repository with that commit.
- Add their repository as a remote.
- Cherry-pick that commit.

As you may imagine, this was error-prone, led to lots of code duplication, and wasted lots of time trawling through Git repositories looking for the correct patch.

`rustc-debian` is a centralized place to put those patches.
Instead of having our patches float around in random Git trees, we use Git's [patch-based workflow](https://git-scm.com/docs/gitworkflows#_patch_workflow) to store commits as files, which we then track using Git as if they were any other file.
The patch-based workflow is based around two commands:

- {manpage}`git-format-patch(1)`, which lets you *export* commits as `.patch` files unbound to any repository.
- {manpage}`git-am(1)`, which lets you *apply* `.patch` files as new commits over your working tree.

We place patches that may be helpful across many versions of `rustc` in the `menu/` directory of `rustc-debian`, using `git format-patch`.
Then, when we need to port a new version of rustc, we pick the patches we want, as if we were ordering from a *menu*, and use `git am` to apply them.

```{note}
Git's patch-based workflow was originally designed to work over email; after creating a patch, it's generally assumed that you send it to a project's maintainers by email.
Git has some additional ergonomic features to automatically send and recieve patches by email, and you may see references to email in man pages and web searches about the patch-based workflow.
So, it's worth stating clearly that we don't use email in our workflow.
The way we share patches is by putting them in the rust-debian repository.
```

## Using `rustc-debian`

As a motivating example, Debian's `rustc` has a bug where it builds a few components twice.
Given that `rustc` has long enough build times already, we created a patch to fix the bug (which fortunately was rather simple).
It is exported as `prevent-duplicate-dh-auto-build.patch`.

<!-- TODO: pygment does not support .patch files. I am using .diff instead, which has slightly different
highlighting ...-->
```diff
From 4d6301da24f8e360414172bc169f6fe31705e35c Mon Sep 17 00:00:00 2001
From: Max Gilmour <max.gilmour@canonical.com>
Date: Tue, 18 Nov 2025 09:04:25 -0800
Subject: [PATCH] d/rules: Prevent duplicate call to dh_auto_build

Both the override_dh_auto_build-arch and override_dh_auto_build-indep
rules rely on the debian/dh_auto_build.stamp target, but this target
did not actually generate said file, meaning that the target would be
called twice.

This patch was incorporated into Rust 1.90.

Thanks to blkerby for spotting this error!

This patch is from rustc-debian.
https://git.launchpad.net/~rust-toolchain/ubuntu/+source/rustc-debian/?h=main
---
 debian/rules | 1 +
 1 file changed, 1 insertion(+)

diff --git a/debian/rules b/debian/rules
index 50df4fb388f..2fe19a3f9af 100755
--- a/debian/rules
+++ b/debian/rules
@@ -345,6 +345,7 @@ clean_generated:
 
 debian/dh_auto_build.stamp:
 	$(RUSTBUILD) build $(RUSTBUILD_FLAGS)
+	touch "$@"
 
 override_dh_auto_build-arch: debian/dh_auto_build.stamp
 ifeq (true,$(BUILD_WINDOWS))
-- 
2.43.0
```

```{note}
There are other, more complicated patches expressing more structural differences between our Rust and Debian's Rust.
However, this patch is nice and simple, so it serves as a good example.

In real life, our motivation to create `rustc-debian` was {lpbug}`2100266`.
It was a bug affecting many different versions of `rustc`, and the fix was non-trivial.
Putting the patch in a central location made it easy to apply over any bugged versions of `rustc` that we found in our care.

`rustc-debian` also was useful when testing `cargo-auditable` support, as we ended up testing it on many different versions of `rustc`.
```

Applying patches is simple:

- Make sure that your local clone of `rustc-debian` is up-to-date
- `git am path/to/rustc-debian/menu/prevent-duplicate-dh-auto-build.patch`

`git am` takes a .patch file and turns it back into a commit.

### Merge Conflicts

Git has slightly worse ergonomics for merge conflicts when done with patch-based workflow.
If you try to `git am` a patch with conflicts, it will simply refuse to try.
You must use `git am -3` to make it try and fix conflicts.

<!--TODO: in general am-ing conflicts is hacky, and I'll need to rewrite this section when I next
have to fix a merge conflict so that I can provide more accurate information --petrakat -->

## Contributing to `rustc-debian`

When you create a commit that may be useful in other versions of `rustc`, you can export it with `git format-patch`.

First, create your commit like any other commit.
Then, run `git format-patch -1`.
It will print the name of a patch file like `0001-first-line-of-your-commit-message.patch`, and create it in your working directory.

```{note}
`-1` tells git to only create a single patch.
Usually, the command expects a range of commits.
```

`mv` that file over to wherever you have cloned `rustc-debian`.
Then, create a commit in `rustc-debian` with a brief(er) description of the patch, and push it.

### How to Format a Nice Patch

Remember that people will see your commit as a file floating around by itself, with no helpful Git history for context.
Therefore, it's worth putting lots of detail about the history of the patch and why it is necessary in a long commit message.

Secondly, given that `rustc-debian` is a unique workflow and its repository is not easily discoverable, you should put this footer into your commit message:

```none
This patch is from rustc-debian.
https://git.launchpad.net/~rust-toolchain/ubuntu/+source/rustc-debian/?h=main
```

Thirdly, remember to remove the `0001-` prefix from the name of your patch file.
Git names the files like this to help keep things in order when exporting a range of patches, but our workflow works only with single files.
So, we would end up with a bunch of `.patch` files all starting with `0001-`, which is just noisy.

(We may revisit this policy later, if we end up having patch files that depend on each other.)

## Future Work

Currently, `rustc-debian` only has a `menu/` directory.
In the future, we hope to store other useful patches and scripts in this repository in other directories.
`rustc-debian` is for the benefit of us as the Rust toolchain squad, which means we get to decide the rules.
Feel free to suggest anything else you'd like to use the repository for!

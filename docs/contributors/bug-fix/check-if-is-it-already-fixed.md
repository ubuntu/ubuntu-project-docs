(check-if-is-it-already-fixed)=
# Check if it's already been fixed

Often we can save time by leveraging someone else's work, so it's always
worth doing some research up-front. Fixes for bugs can sometimes be found in
newer versions of Ubuntu, Debian, or upstream, and sometimes in external
forums or bug trackers.


## Was it fixed in a newer Ubuntu?

The easiest way to check is to review the package's status in Ubuntu:

```none
$ rmadison postfix
 postfix | 2.9.1-4           | precise         | source, amd64, armel, armhf, i386, powerpc
 postfix | 2.9.6-1~12.04.3   | precise-updates | source, amd64, armel, armhf, i386, powerpc
 postfix | 2.11.0-1          | trusty          | source, amd64, arm64, armhf, i386, powerpc, ppc64el
 postfix | 2.11.0-1ubuntu1.2 | trusty-updates  | source, amd64, arm64, armhf, i386, powerpc, ppc64el
 postfix | 3.1.0-3           | xenial          | source, amd64, arm64, armhf, i386, powerpc, ppc64el, s390x
 postfix | 3.1.0-3ubuntu0.3  | xenial-updates  | source, amd64, arm64, armhf, i386, powerpc, ppc64el, s390x
 postfix | 3.3.0-1           | bionic          | source, amd64, arm64, armhf, i386, ppc64el, s390x
 postfix | 3.3.0-1ubuntu1    | cosmic          | source, amd64, arm64, armhf, i386, ppc64el, s390x
```

Debian can also be worth checking:

```none
$ rmadison -u debian postfix
postfix    | 3.3.0-1          | testing        | source, amd64, arm64, armel, armhf, i386, mips64el, mipsel, ppc64el, s390x
postfix    | 3.3.0-1          | unstable       | source, amd64, arm64, armel, armhf, i386, mips64el, mipsel, ppc64el, s390x
...
```

We see from the first output that `3.3.0-1ubuntu1` exists under Cosmic, so
`postfix` has been modified there. Let's see what was changed.


### Clone the Package

Find the repository name:

```none
$ apt-cache show postfix | grep Source:
```

In this case, there is no "Source" field, so we just use "`postfix`".

```none
$ git ubuntu clone postfix postfix-gu
```

This will create a new git clone of the postfix repo named `postfix-gu`, with
a remote of `pkg`. The current branch will be `ubuntu-devel`, and the various
versions for each distribution version will be under `pkg/ubuntu/version`.

Notes:

* Due to {lpbug}`this bug <1761821>`, you may get:
  `fatal: could not read Username for 'https://git.launchpad.net': terminal prompts disabled.` 
  It's safe to ignore this.
 * The first time you run this command, a git-ubuntu entry will be added to
   `.gitignore`.
 * Sometimes it can be helpful to checkout the git repositories for the
   package maintained by Debian and/or upstream. These would be checked out
   to "`postfix-debian`" and "`postfix`" respectively.


### View the Commit Log

```none
$ git log -b pkg/ubuntu/cosmic
...
commit 73cb543efe06a340021cbf538d3ca88abfd96bd8 (tag: pkg/upload/3.3.0-1ubuntu1)
Author: Andreas Hasenack <andreas@canonical.com>
Date:   Wed May 9 10:14:49 2018 -0300

    changelog

commit d4cb4562480496f8a1b25ddc397cef45dd45d855
Author: Andreas Hasenack <andreas@canonical.com>
Date:   Wed May 9 09:51:20 2018 -0300

      * debian/patches/fix-postconf-segfault.diff: Fix a postconf segfault
        when map file cannot be read.  Thanks to Viktor Dukhovni <postfix-
        users@dukhovni.org>. (LP: #1753470)
```

`d4cb45` sure looks like a fix for this issue!

```none
$ git log -b -p pkg/ubuntu/cosmic
...
diff --git a/debian/patches/fix-postconf-segfault.diff b/debian/patches/fix-postconf-segfault.diff
new file mode 100644
index 00000000..f8eef6bf
--- /dev/null
+++ b/debian/patches/fix-postconf-segfault.diff
@@ -0,0 +1,25 @@
+Description: Fix a postconf segfault when map file cannot be read
+Author: Viktor Dukhovni <postfix-users@dukhovni.org>
+Origin: https://marc.info/?l=postfix-users&m=152578771531514&w=2
+Bug-Debian: https://bugs.debian.org/898271
+Bug-Ubuntu: https://launchpad.net/bugs/1753470
+Last-Update: 2018-05-09
+---
+This patch header follows DEP-3: http://dep.debian.net/deps/dep3/
+--- a/src/postconf/postconf_dbms.c
++++ b/src/postconf/postconf_dbms.c
+@@ -174,10 +174,10 @@
+        */
+       dict = dict_ht_open(dict_spec, O_CREAT | O_RDWR, 0);
+       dict_register(dict_spec, dict);
+-      if ((fp = vstream_fopen(cf_file, O_RDONLY, 0)) == 0
+-          && errno != EACCES) {
+-          msg_warn("open \"%s\" configuration \"%s\": %m",
+-                   dp->db_type, cf_file);
++      if ((fp = vstream_fopen(cf_file, O_RDONLY, 0)) == 0) {
++        if (errno != EACCES)
++              msg_warn("open \"%s\" configuration \"%s\": %m",
++                           dp->db_type, cf_file);
+           myfree(dict_spec);
+           return;
+       }
diff --git a/debian/patches/series b/debian/patches/series
index c2e47271..1f77ec0b 100644
--- a/debian/patches/series
+++ b/debian/patches/series
@@ -15,3 +15,4 @@
 50_LANG.diff
 70_postfix-check.diff
 tls_version.diff
+fix-postconf-segfault.diff
```

Here we see both the patch and the change to `debian/patches/series` to
include the patch. This is the fix we need!


## Was it fixed in Debian?

Sometimes the fix may have been updated in Debian instead of Ubuntu. There are
many ways to locate fixes from Debian. Debian maintains its own git
repository for many (but not all) of its packages, so having a clone of this
can be handy.

For example, let's assume for argument's sake that we had a problem with
`sshd` in Xenial, where it would fail to check config files before reloading
([as in this bug](https://bugs.launchpad.net/ubuntu/+source/openssh/+bug/1771340)).
From Debian's `openssh`
[source package page](https://packages.debian.org/source/stretch/openssh),
we find the git repository at `https://salsa.debian.org/ssh-team/openssh` and
can check it out:

```none
$ git clone https://salsa.debian.org/ssh-team/openssh.git openssh-debian
$ cd openssh-debian
$ git branch -av | cat
* master                               296562ba1 releasing package openssh version 1:8.2p1-4
  remotes/origin/HEAD                  -> origin/master
  remotes/origin/buster                6d9ca74c4 releasing package openssh version 1:7.9p1-10+deb10u2
  remotes/origin/etch                  851625c74 releasing version 1:4.3p2-9etch1
  remotes/origin/experimental          09a03c340 Update contact information for Natalie Amery
  remotes/origin/jessie                9da94db38 Merge branch 'jessie' into 'jessie'
  remotes/origin/master                296562ba1 releasing package openssh version 1:8.2p1-4
  remotes/origin/pristine-tar          5fdaf4d7d pristine-tar data for openssh_8.2p1.orig.tar.gz
  remotes/origin/sarge                 f297a6e07 debconf-updatepo
  remotes/origin/squeeze               faa0b9a59 releasing package openssh version 1:5.5p1-6+squeeze5
  remotes/origin/stretch               0ef21e4e2 Merge branch 'fix-923486-stretch' into 'stretch'
  remotes/origin/ubuntu/saucy          f8daff632 releasing package openssh version 1:6.2p2-6ubuntu0.5
  remotes/origin/ubuntu/trusty         f6ffa5954 releasing package openssh version 1:6.6p1-2ubuntu2
  remotes/origin/ubuntu/xenial         bd9cfb441 releasing package openssh version 1:7.2p2-4ubuntu1
  remotes/origin/upstream              f0de78bd4 Import openssh_8.2p1.orig.tar.gz
  remotes/origin/upstream-experimental 102062f82 Import openssh_8.0p1.orig.tar.gz
  remotes/origin/upstream-jessie       487bdb3a5 Import openssh_6.7p1.orig.tar.gz
  remotes/origin/upstream-stretch      971a76537 Import openssh_7.4p1.orig.tar.gz
  remotes/origin/wheezy                e345e2a5f releasing package openssh 1:6.0p1-4+deb7u3
  remotes/origin/wheezy-backports      1d95da812 Remove now-unnecessary backports-specific version changes.
```

That's a lot of branches, but the ones of most interest will be `master` and
sometimes `experimental`. `master` is already checked out, so lets peruse its
commit history. Doing this, we find:

```none
commit d4181e15b03171d1363cd9d7a50b209697a80b01
Author:     Colin Watson <cjwatson@debian.org>
AuthorDate: Mon Jun 26 10:18:26 2017 +0100
Commit:     Colin Watson <cjwatson@debian.org>
CommitDate: Mon Jun 26 10:18:26 2017 +0100

    Test configuration before starting or reloading sshd under systemd (closes: #865770).
```

Our issue would be the same as Debian bug #865770.

It's also possible to search for commits via Debian's web front-end for git,
[Salsa](https://salsa.debian.org/public). Doing so in this case would bring you to
[this commit](https://salsa.debian.org/ssh-team/openssh/-/commit/d4181e15b03171d1363cd9d7a50b209697a80b01)

Either way, you should also mention the Salsa link in the fixed-up bug report,
and you should also include it in your fix commit message.

Since we can't push new versions of packages to previous Ubuntu releases,
you'll need to backport the fix by copying what Debian did into a new commit
on Xenial.


## Was it fixed upstream?

For bugs that aren't already fixed in Ubuntu or Debian, sometimes the original
developers of the software have already found and fixed the issue, or at least
are aware of it and may have a proposed solution or workaround available.

From the unpacked package directory, a quick way to see if there's a newer
upstream release is via `uscan`:

```none
$ cd dovecot-gu/
$ uscan --safe
uscan: Newest version of dovecot on remote site is 2.3.10, local version is 2.3.7.2
uscan:    => Newer package available from
  https://dovecot.org/releases/2.3/dovecot-2.3.10.tar.gz
```

This only works if the package has a `debian/watches` file. If it doesn't,
look in the package's README or other documentation, and do the research
online manually.

Searching the upstream bug tracker, or generally Googling error messages or
symptoms can sometimes turn up a patch or bug report of relevance.


## Forwarding issues upstream

If there are no existing fixes for an issue, you can either develop one
yourself, or communicate the problem to Debian or the upstream developers.

Sometimes clues can be found "in the wild" via random forum posts or bug
trackers, but be aware these can span the full range from high quality to
dangerous - so treat them only as ideas and don't accept anything blindly.

Each upstream project has its own conventions and expectations for how they
can be communicated with. Check the source tree and the development section of
the upstream project's website for policies, or study other recent bug reports
and patch contributions for best practices to follow.

In general though, it is a good idea to make sure you are able to reliably
reproduce the issue yourself. Document the steps you took in a way that
non-Ubuntu users could follow. If there is a workload or test case, try to
simplify it down to the minimal set of commands needed to reproduce the issue.

When filing the bug report or pull request upstream, do identify yourself as
an Ubuntu developer, and your role in forwarding an issue reported against
the distribution.

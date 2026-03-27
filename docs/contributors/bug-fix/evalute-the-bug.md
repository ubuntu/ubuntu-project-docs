(evaluate-the-bug)=
# Evaluate the Bug

Let's look at an example:
[bug #1753470 report](https://bugs.launchpad.net/ubuntu/+source/postfix/+bug/1753470).


## Bug report description:

The original bug report was filed with just this description:

```none
Fresh install of 18.04 server. Every 5 minutes postconf segfaults:

Mar 5 14:30:05 hostname-here kernel: [ 672.082204] postconf[12975]: segfault at 40 ip 0000564d613ff053 sp 00007ffc39e19b90 error 4 in postconf[564d613e7000+25000]
Mar 5 14:30:06 hostname-here kernel: [ 672.303499] postconf[13004]: segfault at 40 ip 000055b29d0f8053 sp 00007fff72f4b740 error 4 in postconf[55b29d0e0000+25000]
```

According to the Apport log (which is automatically attached to the Launchpad
bug by Apport), the crash is caused by following command line:

```none
$ postconf -h queue_directory
```

Running the command in the shell, however, works as expected and lists the
default spool directory (`/var/spool/postfix`).

```none
ProblemType: Bug
DistroRelease: Ubuntu 18.04
Package: postfix 3.3.0-1
ProcVersionSignature: Ubuntu 4.15.0-10.11-generic 4.15.3
Uname: Linux 4.15.0-10-generic x86_64
ApportVersion: 2.20.8-0ubuntu10
Architecture: amd64
Date: Mon Mar 5 14:26:27 2018
SourcePackage: postfix
UpgradeStatus: No upgrade log present (probably fresh install)
```

Note that the metadata at the end of the description is what gets appended
when the bug report filing is automatically triggered, or if the user uses a
bug reporting assistant (such as Apport).

Sometimes these types of bug reports will also include an attached
"`something.crash`" file. This is created by the Apport process running on the
user's system at the time of segfault, and typically includes the core dump,
logs, and other relevant information. If the user has provided a `.crash`
file, you can examine the
{ref}`Apport Crash manually <how-to-debug-an-apport-crash>`
to get a useful stacktrace.


## Try to reproduce the issue

Not all bugs can be easily reproduced, and it's not always obvious how to
reproduce even reproducible bugs. In these cases, some bug work will be needed
to isolate the problem ourselves, or you'll need to work with bug reporters to
narrow the cause enough to identify a fix.

However, in our example case we're lucky. The bug triagers have identified a
way to reproduce the issue, in
[comment #12](https://bugs.launchpad.net/ubuntu/+source/postfix/+bug/1753470/comments/12):

```none
ubuntu@bionic-postfix:~$ postconf virtual_alias_map
Segmentation fault (core dumped)
ubuntu@bionic-postfix:~$ dpkg-query -W postfix
postfix 3.3.0-1
ubuntu@bionic-postfix:~$ ll /etc/postfix/valiases.cf
-rw-r----- 1 root root 169 May 7 14:08 /etc/postfix/valiases.cf
ubuntu@bionic-postfix:~$
```

Let's see if we can reproduce the issue as well, using these directions.

Before that, we need to set up an environment for doing the testing. There are
many options for where and how to do your testing, and different developers
have their own preferences. Here's a couple of options:


### Make a test environment

To make a container for testing:

```none
$ lxc launch ubuntu-daily:bionic tester
```

Alternatively, create a virtual machine (VM) for testing:

```none
$ lxc launch ubuntu-daily:bionic --vm tester
```

With both containers and VMs, you can use the `limits.memory` and `limits.cpu` options to configure available RAM or CPU cores.
For example, to limit the available memory to 2 GiB, and make 2 CPU cores available, add these parameters to the `lxc launch` command:

```none
-c limits.memory=2GiB -c limits.cpu=2
```

Log into the machine:

```none
$ lxc exec tester -- sudo -i -u ubuntu
```

```{note}
The "ubuntu" user's password is locked, but `sudo` can be run without password.
```


### Get up to date and install `postfix`

```none
ubuntu@tester:~$ sudo apt dist-upgrade
ubuntu@tester:~$ sudo apt install -y postfix
```


#### Tell `postfix` to use a map file

```none
ubuntu@tester:~$ echo "virtual_alias_maps = pgsql:/etc/postfix/valiases.cf" \
 | sudo tee -a /etc/postfix/main.cf
```


### To reproduce, the file must be unreadable by the current user

```none
ubuntu@tester:~$ sudo touch /etc/postfix/valiases.cf
ubuntu@tester:~$ sudo chmod 0600 /etc/postfix/valiases.cf
```


### Reproduce the issue

```none
ubuntu@tester:~$ /usr/sbin/postconf virtual_alias_map
Segmentation fault (core dumped)
```

Now we have confirmed the bug.

```none

Keep track of the commands you used to reproduce the bug. You'll need them
later.
```
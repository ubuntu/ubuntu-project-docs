(validate-the-fix)=
# Validate the fix


## Start a Bionic container and enter it:

We can name our LXC containers with any scheme we wish, such as 'tester'
earlier for a temporary one to test with. However, for bug fixes we'll often
need to keep the container around for reference as the bug fix goes through
the review, sponsorship, and SRU processes.

So, to keep things consistent let's reuse our git branch name, and just
prefix the package name:

```none
$ lxc launch ubuntu:bionic postfix-sru-lp1753470-segfault-bionic
Creating postfix-sru-lp1753470-segfault-bionic
Starting postfix-sru-lp1753470-segfault-bionic

$ lxc exec postfix-sru-lp1753470-segfault-bionic -- bash
root@postfix-sru-lp1753470-segfault-bionic:~# 
```


## Reproduce the bug

Record your steps as you go (you'll need them later):

```none
# apt dist-upgrade
# apt install -y postfix
# touch /etc/postfix/valiases.cf
# chmod 0600 /etc/postfix/valiases.cf
# echo "virtual_alias_maps = pgsql:/etc/postfix/valiases.cf" >> /etc/postfix/main.cf
# su - ubuntu
$ /usr/sbin/postconf virtual_alias_map
Segmentation fault (core dumped)
```


## Install the fixed package

In this case, I'm using a PPA. Alternatively, if you've built locally, you can
copy in the `.deb` file and install it manually.

```none
$ sudo add-apt-repository -ys ppa:kstenerud/postfix-sru-lp1753470-segfault
$ sudo apt update
$ sudo apt upgrade -y
```


## Test the bug again

```none
$ /usr/sbin/postconf virtual_alias_map
/usr/sbin/postconf: warning: virtual_alias_map: unknown parameter
```

The bug is fixed! Sweet!

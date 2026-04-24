(debian-bugs)=
# Reporting bugs in Debian

Learn how to report bugs in the Debian Bugtracking System (BTS) from an Ubuntu system.

## Using reportbug

The **`reportbug`** command line utility is installed on Ubuntu. To report a bug to Debian:

```bash
reportbug -B debian <package-name>
```

Before using reportbug for the first time, configure it:

```bash
reportbug --configure
```

This creates a `~/.reportbugrc` file with your settings.

## Using submittodebian

The **`submittodebian`** tool (from `ubuntu-dev-tools` package) is a convenient way to forward patches to Debian. It:

- Adds appropriate usertags for tracking
- Opens your editor to refine the patch
- Calls reportbug internally

Example workflow:

```bash
apt-get source <package>
cd <package>-<version>
# make your changes
dch -i 'description of change'
debuild -S
submittodebian
```

## When to report bugs in Debian

Consider reporting bugs to Debian when:

- The bug exists in both Ubuntu and Debian
- You have an improvement suggestion (file as wishlist)
- You have a patch that Debian should also have

## After reporting

Once the bug is filed in Debian:

- Link the Debian bug to the Ubuntu/Launchpad bug using "Also affects distribution"
- Set up a bug watch to track the Debian bug status

## See also

- [Debian BTS documentation](https://www.debian.org/Bugs/Reporting)
- [Debian BTS usertagging](https://wiki.ubuntu.com/Debian/Usertagging)
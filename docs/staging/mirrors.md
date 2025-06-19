(mirrors)=

# Mirrors

```{note}
This content comes [from the wiki](https://wiki.ubuntu.com/Mirrors).
It has not yet been reviewed for currency or accuracy.
Last updated: 2024
```

Looking for a list of Ubuntu {ref}`archive or CD image mirrors <existing-mirrors>`?

The distribution of Ubuntu CD images and packages can always be improved.
[There's a team](https://launchpad.net/~ubuntu-mirror-admins) working on
improving user experiences every day, making Ubuntu available to you. You can
help too, by creating a mirror of your own and provide people near you with a
reliable mirror.

These pages tell you what to expect, and what Ubuntu expects. You can also find
example scripts to sync, and guidelines on maintaining your mirror.

There are two types of mirrors:

* Country mirrors (e.g. `nl.archive.ubuntu.com`/`nl.releases.ubuntu.com`)
* Normal mirrors (reachable via their own hostname)

If you wish to create a new mirror, please read this page and its sub-pages.
If you want to apply for being a country mirror, please read {ref}`these requirements <country-mirror>`.

## Registration

If your mirror is meant to be used by others, please go and register it at
[Launchpad](https://launchpad.net/ubuntu/+newmirror). You may need to create a
Launchpad account first. When your registration is successful and approved, it
will show up on the mirror lists on Launchpad. It will also be checked by
Launchpad.

If you registered a CD mirror, and registration is successful and approved, it
will also show up on the [Ubuntu download pages](http://www.ubuntu.com/download).

## Mirror guidelines

To keep your mirror up to date and working, please follow these guidelines:

* **Be committed to being a mirror**

  Obviously, each offer to be an Ubuntu mirror is great and users appreciate it.
  However, it's in nobody's interest to go and change the `sources.list` every
  time a mirror disappears. So if you're not planning on creating a mirror for
  the long run, don't register it. People might get disappointed in you and/or
  Ubuntu.

* **Know what you're starting with**

  A mirror may cause a lot of traffic. If your server has insufficient
  bandwidth, users cannot download very well and your machine may become
  unreachable. If you pay for traffic, please note that traffic might increase,
  a lot.

* **Make sure you have enough disk space**

  The Ubuntu archive, as of `2024-04-09`, uses about:

  * **2.6TB** of disk space for the Ubuntu package archive
  * **32GB** for Ubuntu release CD images

  ... *and is slowly growing*. A full disk will get you out of sync and cause
  problems for your users. 

* **Keep up to date**

  Please try to mirror about four times a day (so every six hours) for
  archive mirrors. Since Ubuntu only releases every six months or so, a daily
  check on a releases mirror is sufficient.
  
  [Push mirroring](https://wiki.ubuntu.com/Mirrors/PushMirroring) is available
  as an alternative.

* **Monitor the output of your sync scripts**

  Sometimes, syncing of the mirrors fails. That's OK, but it is very important
  that you monitor that and correct faults. Missing packages are not very
  user-friendly, so try to avoid that.

* **Subscribe to the mirror mailing lists**

  There are two mailing lists for mirror admins. You have the
  [`ubuntu-mirrors` mailing list](https://lists.ubuntu.com/mailman/listinfo/ubuntu-mirrors)
  for discussion, tips and tricks about mirroring. There's also
  [`ubuntu-mirrors-announce`](https://lists.ubuntu.com/mailman/listinfo/ubuntu-mirrors-announce)
  which announces big updates and deletes on the mirrors.

(country-mirror)=
## Country mirror requirements

If you want to apply for being a country mirror, you **MUST** follow these
requirements:

* In case of an archive mirror:

  * update every six hours (four times a day)

  * use a {ref}`two-stage sync <mirror-scripts>`

* In case of a Releases mirror, update every 4 hours (six times a day) or have
  {ref}`push mirroring <push-mirroring>` set up.

* Provide the following services:

  * HTTP

  * Optional, but beneficial: `rsync` (modules '`ubuntu`' for archive and
    '`releases`' for releases).

* Keep your Launchpad account up to date, so we can reach you if needed.

* In case of an archive mirror, the archive must be available at the following
  URL:

  * `http://<country-code>.archive.ubuntu.com/ubuntu/`

* In case of a releases mirror, the releases must be available at the following
  URL:

  * `http://<country-code>.releases.ubuntu.com/`

* Subscribe to [`ubuntu-mirrors-announce`](https://lists.ubuntu.com/mailman/listinfo/ubuntu-mirrors-announce)
  which announces big updates and deletes on the mirrors.

```{note}
The way {term}`APT` works means that all of the hosts behind a given name
**must** be in sync.

If there is already a country mirror for that country, then you need to work
out with that country mirror which one is the better one going forward, since
there can only be one.

If there is more than one host, they should be on the same LAN and making sure
that they remain consistent in the view that they present to the users.
```

## Releases statistics

[Releases](https://wiki.ubuntu.com/Releases) approximately take up the following
number of *bytes* (as of `2019-03-27`):

| Release       | Size in bytes | Size in GB |
| ------------- | ------------- | ---------- |
| Precise       |  4625553121   |  4.3       |
| Trusty        |  3775672451   |  3.5       |
| Xenial        |  5324338074   |  5.0       |
| Bionic        |  2876699930   |  2.7       |
| Cosmic        |  2929092930   |  2.7       |
| ubuntu-core   |  1783731688   |  1.7       |
| **Total**     |  16589609199  |  20.0      |

(existing-mirrors)=
## Existing mirrors

You can find the list of currently registered mirrors on launchpad:

* [Archive Mirrors](https://launchpad.net/ubuntu/+archivemirrors)

* [CD image mirrors](https://launchpad.net/ubuntu/+cdmirrors)

To identify which country mirror you are connecting to, you can do a `CNAME`
lookup on the URL and cross reference the result with the relevant list above.
You can use the `dig` command on the terminal to do this, e.g. `dig nl.archive.ubuntu.com`.

(mirrors-communication)=
## Communication

If you want to get in touch with other mirror admins, feel free to join us at
`#ubuntu-mirrors` on `https://libera.chat`. Also, if you have questions or an
issue with a mirror, email us at `mirrors@ubuntu.com` to [open a ticket](https://rt.ubuntu.com).



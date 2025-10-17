(mirrors)=
# Mirrors

```{toctree}
:maxdepth: 1
:hidden:

mirror-scripts
push-mirroring
```

The distribution of Ubuntu CD images and packages can always be improved. The
[`ubuntu-mirror-admins`](https://launchpad.net/~ubuntu-mirror-admins) team works
to improve user experiences every day, making Ubuntu available. You can help
too, by creating a mirror of your own and providing people near you with a
reliable mirror.


```{admonition} **Mirrors** series

**Mirrors overview:**
: {ref}`About mirrors <mirrors>` (this page)

**Reference:**
: * {ref}`mirror-scripts`
: * {ref}`push-mirroring`
```


## Mirror types

There are two types of mirrors:

* Country mirrors (e.g. `nl.archive.ubuntu.com`/`nl.releases.ubuntu.com`)

* Normal mirrors (reachable via their own hostname)

If you want to create a new mirror, please read this page and its sub-pages.
To apply for being a country mirror, read
{ref}`these requirements <country-mirror>`.


## Registration

If your mirror is meant to be used by others,
[register it at Launchpad](https://launchpad.net/ubuntu/+newmirror/+login).
When your registration is successful and approved, it will show up on the mirror
lists on Launchpad. It will also be checked by Launchpad.

If you registered a CD mirror, and registration is successful and approved, your
mirror will be selected for nearby users when they click on the the download
button on the [Ubuntu download pages](https://ubuntu.com/download).


## Mirror guidelines

To keep your mirror up to date and working, follow these guidelines:

**Be committed to being a mirror**
: Obviously, each offer to be an Ubuntu mirror is great and users appreciate it.
  However, it's in nobody's interest to go and change the `sources.list` every
  time a mirror disappears. So if you're not planning on creating a mirror for
  the long run, don't register it. People might get disappointed in you and/or
  Ubuntu.

**Know what you're starting with**
: A mirror may cause a lot of traffic. If your server has insufficient
  bandwidth, users cannot download very well and your machine may become
  unreachable. If you pay for traffic, please note that traffic might increase
  (a lot).

**Make sure you have enough disk space**
: The Ubuntu archive, as of September 2025, uses about:

  * **2.6TB** of disk space for the Ubuntu Package Archive

  * **50GB** for Ubuntu release CD images

  ... *and it only grows larger*. A full disk will put you out of sync and
  cause problems for your users. 

**Keep up to date**
: Try to mirror about four times a day (every six hours) for Archive mirrors.
  Since Ubuntu only releases every six months or so, a daily check on a Releases
  mirror is sufficient.
  
  {ref}`push-mirroring` is available as an alternative.

**Monitor the output of your sync scripts**
: Sometimes, mirror syncing fails. That's OK, but it is important that you
  monitor and correct faults. Missing packages are not very user-friendly, so
  try to avoid that.

**Subscribe to the mirror mailing lists**
: There are two mailing lists for mirror admins. You have the
  [`ubuntu-mirrors` mailing list](https://lists.ubuntu.com/mailman/listinfo/ubuntu-mirrors)
  for discussion, tips and tricks about mirroring. There's also
  [`ubuntu-mirrors-announce`](https://lists.ubuntu.com/mailman/listinfo/ubuntu-mirrors-announce)
  which announces big updates and deletes on the mirrors.


(country-mirror)=
## Country mirror requirements

If you want to apply for being a country mirror, you **MUST** follow these
requirements:

Syncs
: For an Archive mirror:
  * Update every six hours (four times per day)
  * Use a {ref}`two-stage sync <mirror-scripts>`

: For a Releases mirror:
  * Update every 4 hours (six times per day)
  * or have {ref}`push mirroring <push-mirroring>` set up.

Provide the following services:
: * HTTP

: * Optional (but beneficial) `rsync` (modules '`ubuntu`' for Archive and
  '`releases`' for Releases).

Keep your Launchpad account up to date
: So we can reach you if needed.

  * For an Archive mirror, the Archive must be available at:
    `http://<country-code>.archive.ubuntu.com/ubuntu/`

  * For a Releases mirror, the Releases must be available at:
    `http://<country-code>.releases.ubuntu.com/`

Subscribe
: to [`ubuntu-mirrors-announce`](https://lists.ubuntu.com/mailman/listinfo/ubuntu-mirrors-announce)
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


(existing-mirrors)=
## Existing mirrors

You can find the list of currently registered mirrors on Launchpad:

* [Archive mirrors](https://launchpad.net/ubuntu/+archivemirrors)

* [CD image mirrors](https://launchpad.net/ubuntu/+cdmirrors)

To identify which country mirror you are connecting to, you can do a `CNAME`
lookup on the URL and cross reference the result with the relevant list above.
You can use the `dig` command on the terminal to do this, e.g.
`dig nl.archive.ubuntu.com`.


(mirrors-communication)=
## Communication

If you want to get in touch with other mirror admins, or you have questions or
issues with a mirror, email us at `mirrors@ubuntu.com` to
[open a ticket](https://rt.ubuntu.com).


# Debian packaging maintscripts

Debian binary packages may optionally contain a set of maintainer scripts (aka
"maintscripts"): `prerm` (pre-removal), `preinst` (pre-installation),
`postrm`, and `postinst`. We will not attempt to define these here as
[chapter 6] of the [Debian Policy Manual] does a very thorough job of this.
Rather, this document is concerned with two things:

* Detailing which maintainer scripts run, when they run, which version of them
  runs (particularly in upgrade scenarios), and what arguments they are passed
  in response to packaging actions.

* Showing where, under the different options to [dh\_installsystemd]
  services are stopped, started, or restarted.

The work on documenting this came about largely as a result of a wide-ranging
issue ([LP: #1959054]) affecting the restart of services in packages. As a
result of that, the behaviour of restarts handled by dh\_installsystemd was
changed in Ubuntu 22.04 (jammy). Thus, the following information applies
strictly to jammy or later versions. Earlier versions (in particular focal)
have a subtly different behaviour, but as that version is now out of standard
support, those details are omitted for the sake of clarity.


## Flow chart

The following chart documents the order of processing of maintscripts in
response to certain package actions. Given its size and complexity, you are
encouraged to view this in a form where you can move around a zoomed in version
(e.g. open the chart in a separate tab and use your browser's zoom function,
or print this in a large form).

```{image} ../images/maintscripts/current.*
:align: center
:alt: A large and complex flow-chart showing the order of maintscript processing in Debian packages
```

The key to the graph is given below:

```{image} ../images/maintscripts/key.*
:align: center
:alt: The key for the flow-chart above, showing the node shapes and colors, and the various edge styles indicating package operations, and success or failure of maintscripts
```

The orange lozenge nodes indicate the various states that a Debian package may
be in ("Not installed", "Installed", and so on). The purple box-shaped nodes
indicate actions that may be performed on a package ("Install", "Remove",
"Upgrade"). The gray boxes indicate where maintscripts are executed, and
finally the white boxes indicate other operations taken by the package
management system which provide some context.

The various lines are color-coded according to the operation in progress. Light
green is a new install, while darker green is a re-install. Blue is for upgrade
operations, and red is for removal operations (light red for remove, darker red
for purge).

Solid lines indicate success of the node (typically a maintscript) that they
lead from. Dotted lines indicate failure of the same node.


## Examples

It may be easiest to understand the chart by following some examples.


### Package installation

Start from the "Not installed" node at the bottom right. This is the typical
initial state of most non-essential packages on a new system. Follow the light
green line to the purple box labelled "Install", indicating the user has
requested to install the package. Continue following the green line and we
reach the first maintscript to be executed: "preinst install". This means that
the `preinst` script (if it exists) is executed with a single argument which
is literally the word `install`.

You may also note the header above this states "this-ver". This is largely
irrelevant for the installation procedure and can be ignored for now (this
header becomes more important in upgrade operations which we will cover later).

At this point, the preinst script may succeed or fail (exit with 0 or a
non-zero value respectively). If it succeeds, follow the solid light green line
onward, and if it fails, follow the dotted light green line. In this case, we
will assume the preinst script succeeded, and proceed to the white "Files are
unpacked" node. This simply gives context to what the package manager is doing
at this stage; not all actions taken by the package manager are included.

From here there are several lines leading away, but we need to follow the light
green one to continue on the "install" route. Next we reach the orange lozenge
node "Unpacked". This is another "state" a package can be in, indicating that
its files have been unpacked on the disk, but the package is not yet
"configured" (and thus not yet fully installed). However, this is not a
terminal state.

Once again, we continue on the light green line to reach another maintscript:
"postinst configure". This means the `postinst` script (if it exists) is
executed with a single argument, `configure`. Once more, the script may
succeed or fail, and you would follow the solid or dotted line as appropriate.

We will again assume the script succeeds (or does not exist), so we follow the
solid green line to the white "Services are started" box. This indicates that
services installed by the dh\_installsystemd utility (which are also enabled)
are started at this point.

Finally, we follow the light green arrow along to the "Installed" state. This
is the terminal state for this example.


### Package upgrade

Start from the orange lozenge node labelled "Installed" (where we left off the
prior example), roughly in the middle of the graph. We will be following the
blue lines for the upgrade route, so the next node is the purple box-shaped
"Upgrade" node indicating the user has requested the package is upgraded.

Next we come to the first maintscript node to be run: "**prior-ver**: prerm
upgrade *\<this-ver\>*". This tells us several things:

1. The `prerm` script will be executed, if it exists

1. It will be passed two arguments: `upgrade` and the *new* version number of
   the package ("*this-ver*")

1. The `prerm` script that is run will be the one shipped by the *currently
   installed* version of the package ("**prior-ver**")

For the sake of demonstration, let us assume this script fails. Follow the
dotted blue line to another maintscript node: "**this-ver**: prerm
failed-upgrade *\<prior-ver\>*". Given the example above this tells us that the
`prerm` script from the *new* version of the package will be executed, and
two arguments will be passed to it: `failed-upgrade` and the version number
of the *currently installed* version of the package.

In our example, this script succeeds (meaning the upgrade can proceed). Follow
the solid blue line to another maintscript node: "**this-ver**: preinst upgrade
*\<prior-ver\>*". By now, the meaning of this node should be clear.

From this node there are *two* blue lines leading away. Which one to follow
depends on the arguments passed to the dh\_installsystemd utility, indicating
when to restart services during an upgrade. There are three possibilities:

`--restart-after-upgrade` (default)
: This is the default behaviour which indicates that service(s) for this
  package should be restarted *after* the new version of the package has been
  installed. In other words, the service(s) should remain running while the
  package's files are upgraded on disk, then should be restarted in one
  operation after the upgrade is complete.

`--no-stop-on-upgrade` (also `--no-restart-on-upgrade`)
: This indicates that services should not be stopped or restarted by the
  upgrade procedure. Often this indicates that the restart procedure is more
  involved, and the package will handle this itself in the `postinst`
  maintscript, but other times it simply means that restart is manual and
  only done at the explicit request of the administrator.

`--no-restart-after-upgrade`
: This (extremely unfortunately named) option indicates that services *will*
  be restarted, but that they must not be running during the upgrade.
  Services will be stopped before files are unpacked, then started again
  after configuration is complete.

For the purposes of this example, we will assume the default behaviour.
Follow the solid blue line annotated with `--restart-after-upgrade` along to
the white "Files are unpacked" node. Then follow the next solid blue to the
next maintscript: "**prior-ver**: postrm upgrade *\<this-ver\>*". Note that,
although the new package's files are now unpacked on the disk, this maintscript
still comes from the *prior* version of the package.

Assume this maintscript suceeds, and proceed along the solid blue line to the
white "Old files are deleted" box. This cleans up files which existed in the
old version of the package but no longer exist in the new version. Follow the
solid blue line to the final maintscript for the upgrade: "**this-ver**:
postinst configure *\<prior-ver\>*".

As this script executes successfully, follow the solid blue line to the white
"Services are started or restarted" box. Then follow the final solid blue line
back to the orange "Installed" state. This concludes a successful upgrade
operation.


Resources
=========

- The [Debian Policy Manual]


[chapter 6]: https://www.debian.org/doc/debian-policy/ch-maintainerscripts.html
[dh\_installsystemd]: https://manpages.ubuntu.com/manpages/noble/en/man1/dh_installsystemd.1.html
[LP: #1959054]: https://bugs.launchpad.net/ubuntu/+source/debhelper/+bug/1959054
[Debian Policy Manual]: https://www.debian.org/doc/debian-policy/

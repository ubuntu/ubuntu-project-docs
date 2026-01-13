(seed-management)=
# Seed management

```{note}
* Page source: [wiki - Seed Management](https://wiki.ubuntu.com/SeedManagement)
* Page source: [wiki - Ubuntu Studio/seeds](https://wiki.ubuntu.com/UbuntuStudio/Seeds)

This page will be moved to:
* Contributors > advanced
```

```{admonition} **Seed management** series
The article series explains seeds and how they are used.

Seeds overview:
: {ref}`seeds`

Related topics:
: {ref}`germinate`

Practical guidance:
: {ref}`seed-management` (this article)
```


## Changing seeds

The general workflow to edit seeds is straightforward:

* Get the source
* Edit the source
* Commit your changes
* Push the changes back to the repository

If seeding the package would mean that it had to be in `main` (and it is not
currently) then you should go through the
{ref}`Main Inclusion Review (MIR) <main-inclusion-review>` process
for the package first. If the package is already in `main`, or seeding the
package wouldn't require it to be in `main` (e.g. seeding for a CD built from
`universe`) you can skip the MIR process.


### Get the source

Seeds are maintained in a
[Launchpad project](https://launchpad.net/ubuntu-seeds) whose git repositories
[are published here](https://code.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/).

You can obtain a copy of the seeds for editing using `git`:

```none
git clone https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/ubuntu
```


````{admonition} Is this step strictly necessary?
Make sure to set an appropriate user ID in git, like this:

```none
git config --global user.name 'Colin Watson'
git config --global user.email 'colin.watson@canonical.com'
```
````

```{admonition} Is this still true?
Some seeds have not yet been migrated to git. See [revision 73](https://wiki.ubuntu.com/SeedManagement?action=recall&rev=73) of this page for the old, bzr-based instructions.
```

Change to the new directory and locate the seed file you want to change:

```none
cd ubuntu
```


### Edit the source

You can find some documentation of the syntax of seeds files in the
{manpage}`germinate manual page <germinate(1)>`.

This is an example of a seed file (minimized version of a real seed file):

```none
Task-Section: user
Task-Description: 2D/3D creation and editing suite
Task-Key: ubuntustudio-graphics

 * agave  #This is a dependency
 * (blender)  #This is a recommend
 # * (openclipart-svg)  #Has been commented out, and will not be used

 * ubuntustudio-graphics # Metapackage for everything here.
```

Make sure you are in the correct branch for the release you want to modify. Most
of the time this will be the development release:


### Commit your changes

Then once the changes are made, you commit the changes with an explanatory
message:

```none
git commit -m "Drop X package (LP: #123456) in video seedfile"
```

It is always good to refer to the Launchpad bug number in the commit message.
If there isn't a bug yet, why not create one with a verbose description of the
reason for the change? It will help make clear why the change was made further
down the road.


### Push your changes

Push the changes back to the repository with `git push`.

Note that changing the seeds does not automatically move packages to a new
component in the Archive. See the
[MIR queue](https://bugs.launchpad.net/~ubuntu-mir/+subscribedbugs).

```{note}
If any of the `ubuntu-meta`, `kubuntu-meta`, `edubuntu-meta`, or `xubuntu-meta`
source packages build a metapackage for the seed you changed, run the `update`
script in the appropriate source package and upload it after your changes have
been effected in the seeds archive. You will need to wait about 20 minutes for
these changes to propagate to the public mirror.
```


## Debugging seed problems

````{admonition} Is this still needed/relevant?

**Why does package X get pulled onto the CD (or into the archive)?**

All the logs necessary to answer this kind of question are available, but they
do take some interpretation, and sometimes you need to run `germinate` locally
if you don't have access to all its output. Let's take a worked example, of
investigating why `exim4-base` and friends landed on the Ubuntu alternate
install CD (this happened on 2009-01-15):

* There are several packages involved, but they all start with `exim4`, so
  we'll just search for that.

* Look at the `germinate` output to find out which seed contains `exim4`
  (`grep -l ^exim4 *` in the appropriate directory, in this case
  `/srv/cdimage.ubuntu.com/scratch/ubuntu/daily/germinate/jaunty/i386` on
  `antimony`; had we not had direct access, running `germinate` by hand with
  some appropriate arguments usually produces a good approximation).

* This produces quite a lot of output. Cut down on some of `germinate`'s
  auxiliary output files:

  ```none
  $ grep -l ^exim4 * | fgrep -v . | xargs
  
  all all+extra d-i-requirements dvd provides server-ship supported-development supported-misc-servers supported-sysadmin-common
  ```

* `all`, `all+extra`, and `provides` are not real seeds, so ignore these. The
  only one of the rest on the alternate CD is `d-i-requirements`. You can look
  at the file itself, and the result is sometimes useful:

  ```none
  $ grep ^exim4 d-i-requirements | cut -d\| -f1-3

  exim4-base          | exim4            | exim4-daemon-heavy
  exim4-config        | exim4            | exim4-base
  exim4-daemon-heavy  | exim4            | mdadm (Recommends)
  ```

* Alternatively, you can look at `germinate`'s output, which sometimes provides
  rationale and supporting information (although in a rather terse form). In
  this case, the output is in
  [CD build logs](https://ubuntu-archive-team.ubuntu.com/cd-build-logs/). We
  know which seed was involved, so search for
  "`Resolving d-i-requirements dependencies`". Here's the output:

  ```none
  Resolving d-i-requirements dependencies ...
  * Chose libcurl4-openssl-dev out of libcurl3-dev to satisfy libxen3
  ! Promoted exim4-daemon-heavy from server-ship to d-i-requirements to satisfy mdadm
  ! Promoted exim4-base from server-ship to d-i-requirements to satisfy exim4-daemon-heavy
  * Chose cron to satisfy exim4-base
  ! Promoted exim4-config from server-ship to d-i-requirements to satisfy exim4-base
  * Chose exim4-config to satisfy exim4-base
  ! Promoted mailx from ship to d-i-requirements to satisfy exim4-base
  ! Promoted libmysqlclient15off from server-ship to d-i-requirements to satisfy exim4-daemon-heavy
  ! Promoted mysql-common from server-ship to d-i-requirements to satisfy libmysqlclient15off
  ! Promoted libpq5 from server-ship to d-i-requirements to satisfy exim4-daemon-heavy
  ```

* This confirms the earlier results: `mdadm` `Recommends: mail-transport-agent`,
  so `germinate` picked one. It tries seeds that strictly contain
  `d-i-requirements` first, so used `server-ship` and found (arbitrarily)
  `exim4-daemon-heavy`. The problem may be fixed by using
  `Recommends: postfix | mail-transport-agent` instead.

* Often, more than one dependency arc is involved, and `germinate` won't always
  list them all verbosely. You can look in the `rdepends` files for this, which
  are published at URLs of the form
  `http://people.canonical.com/~ubuntu-archive/germinate-output/<seedcollection>/rdepends/ALL/<packagename>'`,
  where `<seedcollection>` might be `ubuntu.jaunty` or `kubuntu.intrepid`, etc.
````



## Notes

```{caution}
These are probably obsolete, and need a technical review to see what's still
relevant

### Brain-dump notes


Launchpad does not manage seeds within its database. Instead we have an arch
branch on the super-mirror and tell the Launchpad about the branch. We then have
a tool which takes germinate output, interacts with launchpad (E.g. over XMLRPC)
and does the component changes. We can also integrate that into the appservers
so you can click a button, launchpad will check out the branch from the
super-mirror, germinate and let you manipulate things that way.

The pluses of this method are:

* Much less coding resource needed from the Launchpad team in the short term
  (don't need to design entire DB sections and pages for editing seeds) but in
  the long term we're still flexible for moving to more control in Launchpad.
* Ubuntu team gets their history, branching, merging, diffing, etc all for free
  from bazaar.
* Ubuntu team continues to get their direct low-level control of how seeds
  affect the components.
* Ubuntu team have slightly less to learn to move to Launchpad in the initial
  case.

The minuses of this method are:

* Less direct control in Launchpad
* Launchpad has to have access to the super-mirror
* Direct `pybaz` dependency will be introduced.

The Launchpad stuff:

* Launchpad gains a concept called a 'Flavour' which for now has an arch branch
  in a text field. Later we can always key seed tables off this table.
* Flavours do not inherit within the Launchpad because that'd be too confusing
  for the seed management people. They get inheritance by virtue of bazaar's
  branching and merging, ancestry etc and this seems a desirable level for them.
```

